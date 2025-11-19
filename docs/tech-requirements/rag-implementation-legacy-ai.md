# Tech Requirements: RAG Implementation for Legacy AI

**Status**: Ready for Review
**PRD**: [docs/prd/rag-implementation-legacy-ai.md](../prd/rag-implementation-legacy-ai.md)
**Owner**: Dharan Chandrahasan
**Last Updated**: 2025-11-18

---

## 1. Executive Summary

Implement a hybrid RAG system (BM25 + semantic embeddings + BGE local re-ranking) for Legacy AI's customer discovery corpus (208k tokens). The system enables instant search across all customer interviews in <1 second, eliminating 10-15 minutes of manual context loading per session.

**Key Technical Decisions** (from clarifying questions):
- Sensible defaults + overrides for tool configurability
- Retry with backoff for external APIs, fail-fast for local resources
- Real local dependencies, mock APIs for testing
- Implementation lives in `ai-assistant/scripts/rag/`
- Index full corpus (all 208k tokens) from start

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Desktop (MCP)                     │
├─────────────────────────────────────────────────────────────┤
│  MCP Tools: start_session, search, analyze_interview        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    RAG Pipeline                              │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Indexer    │   Searcher   │  Re-ranker   │   Storage      │
│  (chunking,  │  (BM25 +     │  (BGE local) │  (Chroma)      │
│  embeddings) │  semantic)   │              │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Legacy AI Corpus (208k tokens)                  │
│  ~/Documents/1. Projects/legacy-ai/research/                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

**Indexing Flow (Daily at 7am)**:
```
Documents → Header-based Chunking → Metadata Extraction →
OpenAI Embeddings → Chroma Storage + BM25 Index
```

**Query Flow (~550ms)**:
```
User Query → BM25 Search (50) + Semantic Search (50) →
Merge & Dedupe (80-100) → BGE Re-rank (top 10) →
Format Results → Return to Claude Desktop
```

---

## 3. Component Specifications

### 3.1 Document Chunker (`chunker.py`)

**Purpose**: Split markdown documents into semantically coherent chunks while preserving structure and metadata.

#### 3.1.1 Chunking Strategy (Header-Based with Overlap)

**Best Practice**: Chunks should overlap by 10-20% to prevent losing context at boundaries.

```python
class ChunkConfig:
    max_chunk_tokens: int = 2000      # Maximum tokens per chunk
    min_chunk_tokens: int = 100       # Minimum tokens (avoid tiny chunks)
    overlap_tokens: int = 200         # 10% overlap for context continuity
    header_levels: list = ['#', '##', '###']  # Split boundaries
```

**Algorithm**:
1. Parse markdown, identify header boundaries (##, ###)
2. Create chunks at header boundaries
3. If chunk > `max_chunk_tokens`: split by paragraphs (double newline)
4. If still > `max_chunk_tokens`: split by sentences with overlap
5. Add `overlap_tokens` from previous chunk to start of next chunk
6. Skip chunks < `min_chunk_tokens` (merge with adjacent)

**Why Overlap Matters**: Without overlap, a question about "pricing concerns" might miss context if "pricing" is at the end of chunk A and "concerns" is at the start of chunk B.

#### 3.1.2 Metadata Preservation

**Best Practice**: Rich metadata enables filtering, debugging, and source attribution.

```python
@dataclass
class ChunkMetadata:
    # Source identification
    source_file: str           # "research/customer-interviews/transcripts/Interview Transcript Suzy Somers.md"
    document_title: str        # "Interview Transcript Suzy Somers"

    # Position in document
    section_header: str        # "## Privacy Concerns"
    section_hierarchy: list    # ["Interview Transcript", "Privacy Concerns"]
    chunk_index: int           # 0, 1, 2... (order within document)

    # Content type
    content_type: str          # "transcript" | "analysis" | "insight" | "guide"
    customer_segment: str      # "storyteller" | "listener" | "unknown"
    customer_name: str         # "Suzy Somers" (extracted from filename)

    # Timestamps
    file_modified: str         # ISO timestamp for incremental indexing
    indexed_at: str            # When this chunk was indexed

    # Technical
    token_count: int           # Actual token count of chunk
    char_count: int            # Character count
    has_overlap: bool          # True if chunk starts with overlap from previous
```

**Content Type Detection**:
```python
def detect_content_type(file_path: str) -> str:
    if "transcripts/" in file_path:
        return "transcript"
    elif "analyses/" in file_path:
        return "analysis"
    elif "insights/" in file_path:
        return "insight"
    elif "interview-guides/" in file_path:
        return "guide"
    return "other"
```

**Customer Name Extraction**:
```python
def extract_customer_name(file_path: str) -> str:
    # "Interview Transcript Suzy Somers.md" → "Suzy Somers"
    # "2025-ripanshi.md" → "Ripanshi"
    filename = Path(file_path).stem
    # Pattern matching for different naming conventions
    ...
```

#### 3.1.3 Special Content Handling

**Best Practice**: Preserve semantic meaning of special markdown elements.

| Content Type | Handling | Rationale |
|--------------|----------|-----------|
| Code blocks | Keep intact, never split mid-block | Preserve syntax |
| Lists | Keep list items together when possible | Maintain enumeration context |
| Block quotes | Keep intact | Preserve attribution |
| Tables | Keep intact, split only if > max_tokens | Maintain data relationships |
| Links | Preserve full link syntax | Keep references |

```python
def is_atomic_block(text: str) -> bool:
    """Check if text contains atomic elements that shouldn't be split."""
    patterns = [
        r'```[\s\S]*?```',      # Code blocks
        r'\|.*\|.*\n',          # Table rows
        r'^>\s+',               # Block quotes
    ]
    ...
```

### 3.2 Embedding Generator (`embeddings.py`)

**Purpose**: Generate vector embeddings for semantic search using OpenAI's API.

#### 3.2.1 Configuration

```python
class EmbeddingConfig:
    model: str = "text-embedding-3-small"  # 1536 dimensions
    batch_size: int = 100                   # API batch limit
    max_retries: int = 3                    # Retry on failure
    retry_delay: float = 1.0                # Initial retry delay (seconds)
    retry_multiplier: float = 2.0           # Exponential backoff
    timeout: int = 30                       # Request timeout (seconds)
```

#### 3.2.2 Batch Processing

**Best Practice**: Batch embeddings for efficiency, but respect API limits.

```python
async def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """Generate embeddings in batches with retry logic."""
    embeddings = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        for attempt in range(max_retries):
            try:
                response = await openai.embeddings.create(
                    model=model,
                    input=batch
                )
                embeddings.extend([e.embedding for e in response.data])
                break
            except RateLimitError:
                delay = retry_delay * (retry_multiplier ** attempt)
                await asyncio.sleep(delay)
            except APIError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay)

    return embeddings
```

#### 3.2.3 Caching Strategy

**Best Practice**: Cache embeddings to avoid recomputation on reindex.

```python
class EmbeddingCache:
    """Cache embeddings by content hash to avoid recomputation."""

    def get_cache_key(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str) -> Optional[list[float]]:
        key = self.get_cache_key(text)
        # Check Chroma for existing embedding with same content hash
        ...

    def should_reembed(self, chunk: Chunk, stored_chunk: StoredChunk) -> bool:
        # Only reembed if content changed (not just metadata)
        return chunk.content_hash != stored_chunk.content_hash
```

**Cost Implications**:
- Initial indexing (208k tokens): ~$0.004
- Daily reindex (only new/changed): ~$0.0002 per new interview
- Cached chunks: $0 (skipped)

### 3.3 Vector Store (`storage.py`)

**Purpose**: Persist embeddings and metadata using Chroma local database.

#### 3.3.1 Configuration

```python
class StorageConfig:
    persist_directory: str = "~/.cache/legacy-ai-rag/chroma"
    collection_name: str = "legacy_ai_interviews"
    distance_metric: str = "cosine"  # Best for text similarity
```

#### 3.3.2 Schema Design

**Best Practice**: Store all metadata for flexible querying and debugging.

```python
# Chroma collection schema
collection = chroma_client.create_collection(
    name="legacy_ai_interviews",
    metadata={"hnsw:space": "cosine"}
)

# Document structure
collection.add(
    ids=["chunk_001", "chunk_002", ...],
    embeddings=[[0.1, 0.2, ...], ...],
    documents=["chunk text...", ...],
    metadatas=[
        {
            "source_file": "...",
            "section_header": "...",
            "content_type": "transcript",
            "customer_name": "Suzy Somers",
            "token_count": 450,
            "file_modified": "2025-11-18T10:30:00",
            "indexed_at": "2025-11-18T07:00:00",
            # ... all metadata fields
        },
        ...
    ]
)
```

#### 3.3.3 Incremental Updates

**Best Practice**: Only reindex changed documents to minimize cost and time.

```python
def get_documents_to_reindex(corpus_path: str) -> list[str]:
    """Detect new or modified documents since last index."""
    last_index_time = get_last_index_timestamp()

    documents_to_reindex = []
    for doc_path in glob(f"{corpus_path}/**/*.md", recursive=True):
        file_mtime = os.path.getmtime(doc_path)
        if file_mtime > last_index_time:
            documents_to_reindex.append(doc_path)

    return documents_to_reindex

def remove_stale_chunks(deleted_files: list[str]):
    """Remove chunks from documents that no longer exist."""
    for file_path in deleted_files:
        collection.delete(where={"source_file": file_path})
```

### 3.4 BM25 Index (`bm25_index.py`)

**Purpose**: Keyword-based search for exact term matching.

#### 3.4.1 Configuration

```python
class BM25Config:
    k1: float = 1.5      # Term frequency saturation
    b: float = 0.75      # Length normalization
    persist_path: str = "~/.cache/legacy-ai-rag/bm25_index.pkl"
```

#### 3.4.2 Implementation

**Best Practice**: Use rank-bm25 library for proven implementation.

```python
from rank_bm25 import BM25Okapi
import pickle

class BM25Index:
    def __init__(self, config: BM25Config):
        self.config = config
        self.bm25 = None
        self.documents = []
        self.doc_ids = []

    def build(self, chunks: list[Chunk]):
        """Build BM25 index from chunks."""
        tokenized = [self.tokenize(chunk.text) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized, k1=self.config.k1, b=self.config.b)
        self.documents = [chunk.text for chunk in chunks]
        self.doc_ids = [chunk.id for chunk in chunks]
        self.save()

    def search(self, query: str, top_k: int = 50) -> list[tuple[str, float]]:
        """Search and return (doc_id, score) pairs."""
        tokenized_query = self.tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = scores.argsort()[-top_k:][::-1]

        return [(self.doc_ids[i], scores[i]) for i in top_indices]

    def tokenize(self, text: str) -> list[str]:
        """Simple tokenization - lowercase, split on whitespace/punctuation."""
        return re.findall(r'\w+', text.lower())

    def save(self):
        with open(self.config.persist_path, 'wb') as f:
            pickle.dump((self.bm25, self.documents, self.doc_ids), f)

    def load(self):
        with open(self.config.persist_path, 'rb') as f:
            self.bm25, self.documents, self.doc_ids = pickle.load(f)
```

### 3.5 Hybrid Searcher (`searcher.py`)

**Purpose**: Combine BM25 and semantic search results using Reciprocal Rank Fusion.

#### 3.5.1 Configuration

```python
class SearchConfig:
    bm25_weight: float = 0.5          # Weight for BM25 scores
    semantic_weight: float = 0.5      # Weight for semantic scores
    bm25_candidates: int = 50         # BM25 results before merge
    semantic_candidates: int = 50     # Semantic results before merge
    rrf_k: int = 60                   # RRF constant (standard value)
```

#### 3.5.2 Reciprocal Rank Fusion

**Best Practice**: RRF is robust and doesn't require score normalization.

```python
def reciprocal_rank_fusion(
    results_lists: list[list[tuple[str, float]]],
    k: int = 60
) -> list[tuple[str, float]]:
    """
    Merge multiple ranked lists using RRF.

    RRF score = sum(1 / (k + rank_i)) for each list

    Why RRF:
    - Doesn't require score normalization (BM25 and cosine are different scales)
    - Robust to outliers
    - Simple and effective
    """
    fused_scores = {}

    for results in results_lists:
        for rank, (doc_id, _) in enumerate(results, 1):
            if doc_id not in fused_scores:
                fused_scores[doc_id] = 0
            fused_scores[doc_id] += 1 / (k + rank)

    # Sort by fused score
    sorted_results = sorted(
        fused_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return sorted_results
```

#### 3.5.3 Full Search Pipeline

```python
class HybridSearcher:
    def search(
        self,
        query: str,
        top_k: int = 10,
        rerank: bool = True,
        filters: dict = None
    ) -> list[SearchResult]:
        """
        Execute hybrid search with optional re-ranking.

        Args:
            query: User's search query
            top_k: Number of results to return
            rerank: Whether to apply BGE re-ranking
            filters: Metadata filters (e.g., {"content_type": "transcript"})

        Returns:
            List of SearchResult with text, metadata, and scores
        """
        # 1. BM25 search
        bm25_results = self.bm25_index.search(query, top_k=50)

        # 2. Semantic search
        query_embedding = self.get_query_embedding(query)
        semantic_results = self.chroma_collection.query(
            query_embeddings=[query_embedding],
            n_results=50,
            where=filters
        )

        # 3. Merge with RRF
        merged = reciprocal_rank_fusion([
            bm25_results,
            self.format_chroma_results(semantic_results)
        ])

        # 4. Get top candidates for re-ranking
        candidates = merged[:100]  # Top 100 for re-ranking

        # 5. Re-rank with BGE (if enabled)
        if rerank:
            reranked = self.reranker.rerank(query, candidates, top_k=top_k)
            return self.build_results(reranked)
        else:
            return self.build_results(candidates[:top_k])
```

### 3.6 BGE Re-ranker (`reranker.py`)

**Purpose**: Re-rank candidates using BGE cross-encoder for higher accuracy.

#### 3.6.1 Configuration

```python
class RerankerConfig:
    model_name: str = "BAAI/bge-reranker-base"  # 278M parameters, 1.3 GB
    device: str = "mps"                          # Apple Silicon GPU
    batch_size: int = 32                         # Process in batches
    max_length: int = 512                        # Max tokens per passage
```

#### 3.6.2 Implementation

**Best Practice**: Use cross-encoder for accurate relevance scoring.

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

class BGEReranker:
    def __init__(self, config: RerankerConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self._loaded = False

    def load(self):
        """Lazy load model (only when first search is executed)."""
        if self._loaded:
            return

        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.config.model_name
        )
        self.model.to(self.config.device)
        self.model.eval()
        self._loaded = True

    def rerank(
        self,
        query: str,
        candidates: list[tuple[str, str]],  # (doc_id, text)
        top_k: int = 10
    ) -> list[tuple[str, float]]:
        """
        Re-rank candidates by relevance to query.

        Returns:
            List of (doc_id, score) sorted by relevance
        """
        self.load()  # Lazy load

        scores = []

        # Process in batches
        for i in range(0, len(candidates), self.config.batch_size):
            batch = candidates[i:i + self.config.batch_size]

            # Prepare inputs: [query, passage] pairs
            pairs = [[query, text] for _, text in batch]

            # Tokenize
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                max_length=self.config.max_length,
                return_tensors="pt"
            ).to(self.config.device)

            # Score
            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_scores = outputs.logits.squeeze(-1).cpu().tolist()

            scores.extend(batch_scores)

        # Combine with doc_ids and sort
        scored = [(candidates[i][0], scores[i]) for i in range(len(candidates))]
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored[:top_k]
```

#### 3.6.3 Performance Characteristics

- **Model size**: 1.3 GB (0.37% of 350 GB available disk)
- **RAM usage**: 2-3 GB when loaded (only during searches)
- **Latency**: ~500ms for 100 candidates on Apple Silicon
- **Accuracy**: 60-65% top-10 relevance (vs 50% without re-ranking)

### 3.7 MCP Tools (`mcp_tools.py`)

**Purpose**: Expose RAG functionality to Claude Desktop via MCP protocol.

#### 3.7.1 Tool Definitions

```python
# Tool 1: Start Session
@mcp_tool
def start_legacy_ai_session() -> str:
    """
    Initialize RAG context for Legacy AI customer discovery.

    Returns:
        Status message with corpus size and last index time.
    """
    stats = get_corpus_stats()
    return f"""✅ Loaded Legacy AI context ({stats.total_tokens:,} tokens indexed)
    - {stats.document_count} documents
    - {stats.chunk_count} searchable chunks
    - Last indexed: {stats.last_indexed}
    Ready for customer discovery work."""

# Tool 2: Search
@mcp_tool
def search_interviews(
    query: str,
    top_k: int = 10,
    content_type: str = None,
    customer_name: str = None,
    include_scores: bool = False
) -> str:
    """
    Search across all customer interviews and analyses.

    Args:
        query: Natural language search query
        top_k: Number of results (default: 10)
        content_type: Filter by type (transcript/analysis/insight)
        customer_name: Filter by customer (e.g., "Suzy Somers")
        include_scores: Include relevance scores in output

    Returns:
        Formatted search results with quotes and context.
    """
    filters = {}
    if content_type:
        filters["content_type"] = content_type
    if customer_name:
        filters["customer_name"] = customer_name

    results = searcher.search(query, top_k=top_k, filters=filters)

    return format_results(results, include_scores)

# Tool 3: Analyze Interview
@mcp_tool
def analyze_new_interview(
    transcript_path: str,
    update_meta_analysis: bool = True
) -> str:
    """
    Analyze a new interview transcript using RAG-loaded context.

    Automatically loads:
    - Analysis template
    - Similar previous analyses
    - Meta-analysis patterns

    Args:
        transcript_path: Path to new transcript file
        update_meta_analysis: Whether to update cross-interview patterns

    Returns:
        Analysis context ready for Claude to process.
    """
    # Load new transcript
    transcript = load_document(transcript_path)

    # RAG search for relevant context
    template = search_interviews("customer interview analysis template", top_k=1)
    similar = search_interviews(
        f"customer segment analysis {extract_segment(transcript)}",
        top_k=3
    )
    meta = search_interviews("meta-analysis patterns themes", top_k=2)

    return f"""## New Interview Analysis Context

### Transcript to Analyze
{transcript}

### Analysis Template
{template}

### Similar Previous Analyses
{similar}

### Meta-Analysis Patterns
{meta}

Please analyze this interview following the template structure and update
the meta-analysis with any new patterns."""
```

#### 3.7.2 Result Formatting

**Best Practice**: Format results for readability with clear source attribution.

```python
def format_results(results: list[SearchResult], include_scores: bool) -> str:
    """Format search results for Claude Desktop display."""
    formatted = []

    for i, result in enumerate(results, 1):
        # Header with source info
        header = f"### Result {i}: {result.metadata['document_title']}"
        if result.metadata.get('section_header'):
            header += f" > {result.metadata['section_header']}"

        # Score (if requested)
        score_line = ""
        if include_scores:
            score_line = f"\n*Relevance: {result.score:.3f}*\n"

        # Content with quote formatting
        content = f"> {result.text}"

        # Metadata footer
        footer = f"\n*Source: {result.metadata['source_file']}*"
        if result.metadata.get('customer_name'):
            footer += f" | *Customer: {result.metadata['customer_name']}*"

        formatted.append(f"{header}{score_line}\n{content}{footer}")

    return "\n\n---\n\n".join(formatted)
```

### 3.8 Indexing Pipeline (`indexer.py`)

**Purpose**: Orchestrate the full indexing workflow.

#### 3.8.1 Main Indexing Flow

```python
class Indexer:
    def __init__(self, config: IndexerConfig):
        self.chunker = DocumentChunker(config.chunk_config)
        self.embedder = EmbeddingGenerator(config.embedding_config)
        self.storage = VectorStore(config.storage_config)
        self.bm25 = BM25Index(config.bm25_config)

    async def index_corpus(self, corpus_path: str, incremental: bool = True):
        """
        Index the entire corpus or just changed documents.

        Args:
            corpus_path: Path to legacy-ai/research/
            incremental: If True, only reindex changed files
        """
        # 1. Detect documents to index
        if incremental:
            docs = self.get_documents_to_reindex(corpus_path)
            if not docs:
                logger.info("No documents changed since last index")
                return
            logger.info(f"Reindexing {len(docs)} changed documents")
        else:
            docs = self.get_all_documents(corpus_path)
            logger.info(f"Full reindex of {len(docs)} documents")

        # 2. Chunk documents
        all_chunks = []
        for doc_path in docs:
            chunks = self.chunker.chunk_document(doc_path)
            all_chunks.extend(chunks)

        logger.info(f"Created {len(all_chunks)} chunks")

        # 3. Generate embeddings (with caching)
        texts = [chunk.text for chunk in all_chunks]
        embeddings = await self.embedder.generate_embeddings(texts)

        # 4. Store in Chroma
        if incremental:
            # Remove old chunks for reindexed documents
            for doc_path in docs:
                self.storage.delete_by_source(doc_path)

        self.storage.add(all_chunks, embeddings)

        # 5. Rebuild BM25 index (always full rebuild - it's fast)
        all_chunks_for_bm25 = self.storage.get_all_chunks()
        self.bm25.build(all_chunks_for_bm25)

        # 6. Update index timestamp
        self.save_index_timestamp()

        logger.info(f"Indexing complete. Total chunks: {len(all_chunks_for_bm25)}")
```

#### 3.8.2 Cron Job Setup

```bash
# Add to crontab (crontab -e)
0 7 * * * cd ~/Documents/1.\ Projects/ai-assistant && \
    python scripts/rag/reindex.py >> ~/.cache/legacy-ai-rag/reindex.log 2>&1
```

**reindex.py**:
```python
#!/usr/bin/env python3
"""Daily reindex script for Legacy AI RAG."""

import asyncio
from indexer import Indexer, IndexerConfig

async def main():
    config = IndexerConfig.from_yaml("config/rag_config.yaml")
    indexer = Indexer(config)

    corpus_path = "~/Documents/1. Projects/legacy-ai/research"
    await indexer.index_corpus(corpus_path, incremental=True)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. Error Handling Strategy

### 4.1 Error Categories

| Category | Behavior | Example |
|----------|----------|---------|
| **External API** | Retry 3x with exponential backoff | OpenAI embeddings timeout |
| **Local Resource** | Fail-fast with clear message | BGE model file corrupted |
| **User Input** | Validate and provide helpful feedback | Invalid filter value |
| **Data Issues** | Log warning, continue with fallback | Empty document skipped |

### 4.2 Implementation

```python
class RAGError(Exception):
    """Base exception for RAG system."""
    pass

class EmbeddingError(RAGError):
    """Failed to generate embeddings after retries."""
    pass

class IndexError(RAGError):
    """Failed to index documents."""
    pass

class SearchError(RAGError):
    """Search operation failed."""
    pass

# Retry decorator for external APIs
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(RateLimitError),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
async def call_openai_embeddings(texts: list[str]) -> list[list[float]]:
    ...

# Fail-fast for local resources
def load_bge_model(model_path: str):
    if not os.path.exists(model_path):
        raise RAGError(
            f"BGE model not found at {model_path}. "
            f"Run: python -c \"from transformers import AutoModel; "
            f"AutoModel.from_pretrained('BAAI/bge-reranker-base')\""
        )
    ...
```

### 4.3 Graceful Degradation

```python
def search_with_fallback(query: str, top_k: int = 10) -> list[SearchResult]:
    """Search with fallback if components fail."""
    try:
        # Full hybrid search with re-ranking
        return hybrid_searcher.search(query, top_k=top_k, rerank=True)
    except RerankerError as e:
        logger.warning(f"Re-ranker failed, falling back to hybrid only: {e}")
        return hybrid_searcher.search(query, top_k=top_k, rerank=False)
    except EmbeddingError as e:
        logger.warning(f"Embeddings failed, falling back to BM25 only: {e}")
        return bm25_index.search(query, top_k=top_k)
```

---

## 5. Configuration

### 5.1 Configuration File (`config/rag_config.yaml`)

```yaml
# RAG Configuration for Legacy AI
# Location: ai-assistant/config/rag_config.yaml

corpus:
  path: "~/Documents/1. Projects/legacy-ai/research"
  include_patterns:
    - "**/*.md"
    - "**/*.txt"
  exclude_patterns:
    - "**/.*"           # Hidden files
    - "**/__pycache__"

chunking:
  max_chunk_tokens: 2000
  min_chunk_tokens: 100
  overlap_tokens: 200
  header_levels: ["#", "##", "###"]

embeddings:
  model: "text-embedding-3-small"
  batch_size: 100
  max_retries: 3
  retry_delay: 1.0

storage:
  persist_directory: "~/.cache/legacy-ai-rag/chroma"
  collection_name: "legacy_ai_interviews"

bm25:
  k1: 1.5
  b: 0.75
  persist_path: "~/.cache/legacy-ai-rag/bm25_index.pkl"

reranker:
  model_name: "BAAI/bge-reranker-base"
  device: "mps"  # Apple Silicon
  batch_size: 32

search:
  default_top_k: 10
  bm25_candidates: 50
  semantic_candidates: 50
  rrf_k: 60

logging:
  level: "INFO"
  file: "~/.cache/legacy-ai-rag/rag.log"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### 5.2 Environment Variables

```bash
# .env (ai-assistant repo)
OPENAI_API_KEY=sk-...              # For embeddings
RAG_LOG_LEVEL=INFO                  # Override log level
RAG_DEVICE=mps                      # Override device (cpu/mps/cuda)
```

---

## 6. Logging & Observability

### 6.1 Structured Logging

**Best Practice**: Log all operations for debugging and future optimization.

```python
import structlog

logger = structlog.get_logger()

# Indexing logs
logger.info("indexing_started",
    corpus_path=corpus_path,
    incremental=incremental,
    documents_count=len(docs)
)

logger.info("chunking_complete",
    document=doc_path,
    chunks_created=len(chunks),
    total_tokens=sum(c.token_count for c in chunks)
)

logger.info("embedding_generated",
    batch_number=i,
    batch_size=len(batch),
    latency_ms=elapsed_ms
)

# Search logs
logger.info("search_executed",
    query=query,
    top_k=top_k,
    filters=filters,
    bm25_results=len(bm25_results),
    semantic_results=len(semantic_results),
    final_results=len(results),
    latency_ms=elapsed_ms
)

logger.info("rerank_executed",
    query=query,
    candidates=len(candidates),
    top_k=top_k,
    latency_ms=elapsed_ms
)
```

### 6.2 Metrics to Track

| Metric | Purpose | Target |
|--------|---------|--------|
| `search_latency_ms` | Performance monitoring | <1000ms |
| `rerank_latency_ms` | BGE performance | <600ms |
| `embedding_latency_ms` | OpenAI API performance | <500ms |
| `chunks_indexed` | Corpus growth | Track over time |
| `search_result_count` | Query effectiveness | 5-10 per query |
| `cache_hit_rate` | Embedding cache efficiency | >80% on reindex |

---

## 7. Testing Strategy

### 7.1 Test Structure

```
tests/
├── unit/
│   ├── test_chunker.py          # Chunking logic
│   ├── test_bm25.py              # BM25 indexing/search
│   ├── test_rrf.py               # Reciprocal rank fusion
│   └── test_result_formatter.py  # Output formatting
├── integration/
│   ├── test_indexer.py           # Full indexing pipeline
│   ├── test_searcher.py          # Hybrid search
│   └── test_reranker.py          # BGE re-ranking
└── fixtures/
    ├── sample_transcript.md      # Test document
    ├── sample_analysis.md        # Test document
    └── mock_embeddings.json      # Cached embeddings for tests
```

### 7.2 Key Test Cases

#### Chunking Tests
```python
def test_header_based_chunking():
    """Verify chunks split at headers."""
    doc = "# Title\n\nParagraph 1\n\n## Section\n\nParagraph 2"
    chunks = chunker.chunk(doc)
    assert len(chunks) == 2
    assert "# Title" in chunks[0].text
    assert "## Section" in chunks[1].text

def test_chunk_overlap():
    """Verify overlap between chunks."""
    # Long document that requires splitting
    doc = "## Section 1\n\n" + "word " * 2500 + "\n\n## Section 2\n\n" + "word " * 500
    chunks = chunker.chunk(doc)
    # Check overlap exists
    assert chunks[1].text.startswith(chunks[0].text[-200:])

def test_metadata_extraction():
    """Verify metadata correctly extracted."""
    chunks = chunker.chunk_document("transcripts/Interview Transcript Suzy Somers.md")
    assert chunks[0].metadata["content_type"] == "transcript"
    assert chunks[0].metadata["customer_name"] == "Suzy Somers"
```

#### Search Tests
```python
def test_hybrid_search_combines_results():
    """Verify BM25 and semantic results are merged."""
    # BM25 finds "pricing" keyword
    # Semantic finds "cost concerns" concept
    results = searcher.search("pricing concerns")
    # Should include both keyword matches and semantic matches
    assert any("pricing" in r.text.lower() for r in results)
    assert any("cost" in r.text.lower() for r in results)

def test_metadata_filtering():
    """Verify filters work correctly."""
    results = searcher.search(
        "privacy",
        filters={"content_type": "transcript"}
    )
    assert all(r.metadata["content_type"] == "transcript" for r in results)

def test_search_latency():
    """Verify search completes within target."""
    import time
    start = time.time()
    results = searcher.search("customer privacy concerns")
    elapsed = (time.time() - start) * 1000
    assert elapsed < 1000, f"Search took {elapsed}ms, expected <1000ms"
```

#### Accuracy Tests
```python
def test_search_relevance():
    """Verify >60% of results are relevant."""
    # Known relevant queries with expected matches
    test_cases = [
        {
            "query": "What did Suzy say about pricing?",
            "expected_sources": ["Interview Transcript Suzy Somers.md"],
            "expected_keywords": ["$5000", "pricing", "wealthy"]
        },
        {
            "query": "privacy concerns across interviews",
            "expected_keywords": ["control", "who hears", "strangers"]
        }
    ]

    for case in test_cases:
        results = searcher.search(case["query"], top_k=10)

        # Check source matches
        if "expected_sources" in case:
            sources = [r.metadata["source_file"] for r in results]
            assert any(exp in src for src in sources for exp in case["expected_sources"])

        # Check keyword presence
        if "expected_keywords" in case:
            all_text = " ".join(r.text.lower() for r in results)
            matches = sum(1 for kw in case["expected_keywords"] if kw.lower() in all_text)
            assert matches / len(case["expected_keywords"]) >= 0.6
```

### 7.3 Mock Strategy

```python
# Mock OpenAI embeddings for tests
@pytest.fixture
def mock_openai_embeddings(mocker):
    """Return deterministic embeddings for testing."""
    def fake_embeddings(texts):
        # Return consistent embeddings based on text hash
        return [
            [hash(text) % 1000 / 1000 for _ in range(1536)]
            for text in texts
        ]

    mocker.patch(
        "openai.embeddings.create",
        side_effect=lambda **kwargs: MockResponse(fake_embeddings(kwargs["input"]))
    )
```

---

## 8. File Structure

```
ai-assistant/
├── scripts/
│   └── rag/
│       ├── __init__.py
│       ├── chunker.py           # Document chunking
│       ├── embeddings.py        # OpenAI embedding generation
│       ├── storage.py           # Chroma vector store
│       ├── bm25_index.py        # BM25 keyword index
│       ├── searcher.py          # Hybrid search + RRF
│       ├── reranker.py          # BGE re-ranking
│       ├── indexer.py           # Indexing pipeline orchestration
│       ├── mcp_tools.py         # MCP tool wrappers
│       ├── reindex.py           # Cron job script
│       └── cli.py               # Command-line interface
├── config/
│   └── rag_config.yaml          # RAG configuration
├── tests/
│   └── rag/
│       ├── unit/
│       ├── integration/
│       └── fixtures/
└── docs/
    └── tech-requirements/
        └── rag-implementation-legacy-ai.md  # This document
```

---

## 9. Dependencies

### 9.1 Python Packages

```python
# requirements-rag.txt
chromadb>=0.4.0              # Vector store
openai>=1.0.0                 # Embeddings API
rank-bm25>=0.2.2              # BM25 implementation
transformers>=4.35.0          # BGE model loading
torch>=2.0.0                  # PyTorch for BGE
sentence-transformers>=2.2.0  # Embedding utilities
tiktoken>=0.5.0               # Token counting
pyyaml>=6.0                   # Config loading
structlog>=23.0.0             # Structured logging
tenacity>=8.0.0               # Retry logic
pytest>=7.0.0                 # Testing
pytest-asyncio>=0.21.0        # Async test support
```

### 9.2 System Requirements

- **Python**: 3.11+
- **Disk**: ~2 GB (BGE model 1.3 GB + Chroma DB + indices)
- **RAM**: 4 GB minimum (BGE uses 2-3 GB when loaded)
- **Device**: Apple Silicon (MPS) or CPU

---

## 10. Implementation Timeline

### Day 1 (Nov 18): Setup - 2-3 hours

- [ ] Create project structure (`scripts/rag/`)
- [ ] Install dependencies (`pip install -r requirements-rag.txt`)
- [ ] Download BGE model (1.3 GB)
- [ ] Verify OpenAI API key works
- [ ] Create config file (`rag_config.yaml`)
- [ ] Write basic tests for chunker
- [ ] Test BGE model loading and performance

### Day 2 (Nov 19): Indexing Pipeline - 3-4 hours

- [ ] Implement `chunker.py` (header-based + overlap)
- [ ] Implement `embeddings.py` (batch + cache)
- [ ] Implement `storage.py` (Chroma wrapper)
- [ ] Implement `bm25_index.py`
- [ ] Implement `indexer.py` (orchestration)
- [ ] Index full corpus (208k tokens)
- [ ] Set up cron job for daily reindex
- [ ] Write tests for indexing pipeline

### Day 3 (Nov 20): Search Implementation - 3-4 hours

- [ ] Implement `searcher.py` (hybrid + RRF)
- [ ] Implement `reranker.py` (BGE integration)
- [ ] Implement `mcp_tools.py` (3 tools)
- [ ] Register MCP tools with Claude Desktop
- [ ] Test end-to-end search flow
- [ ] Write tests for search + reranking

### Day 4 (Nov 21): Testing & Validation - 2-3 hours

- [ ] Run full test suite
- [ ] Test PRD query examples (pricing, privacy, barriers)
- [ ] Validate accuracy (>60% target)
- [ ] Test Story 6 workflow (automated analysis)
- [ ] Performance benchmarking (<1 sec search)
- [ ] Add structured logging
- [ ] Document any issues/learnings

---

## 11. Success Criteria Validation

| Criterion | Target | Validation Method |
|-----------|--------|-------------------|
| Context loading time | <10 sec | Time `start_legacy_ai_session()` |
| Search speed | <1 sec | Time `search_interviews()` with logging |
| Search relevance | >60% | Manual review of top-10 for test queries |
| Zero manual copy-paste | 0 events | User confirmation during Phase 2 |
| Cross-interview synthesis | Works | Test "What did all customers say about X?" |
| Automated analysis | Works | Test Story 6 workflow end-to-end |
| Cost | $100/month | Verify no new recurring costs |
| Privacy | 100% local | Audit API calls (only OpenAI embeddings) |

---

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| BGE model too slow | Search >1 sec | Use Apple Silicon MPS; fallback to CPU with smaller model |
| Chunking breaks semantic units | Poor search quality | Extensive testing with real queries; adjust overlap |
| OpenAI API rate limits | Indexing fails | Batch + retry + backoff; cache embeddings |
| Chroma performance at scale | Slow queries | Monitor; migrate to Pinecone if >500k tokens |
| Cron job fails silently | Stale index | Log to file; add health check |

---

## 13. Future Enhancements (Post-Tier 1)

- **Query suggestions**: Recommend common patterns based on history
- **Search analytics**: Track queries, results, user feedback
- **Export results**: Save findings to markdown for documentation
- **Epic 2nd Brain expansion**: Add second corpus (2-4 hours)
- **Cohere upgrade**: Switch to Cohere re-ranking if speed critical (30 min)

---

**End of Tech Requirements Document**

*Ready for review. After approval, Day 1 implementation begins.*
