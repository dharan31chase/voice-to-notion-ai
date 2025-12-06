"""
Legacy AI RAG Implementation (Phase 6.3)

Privacy-first RAG for Legacy AI customer research documents.
Separate ChromaDB collection to isolate customer data.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import hashlib
import logging

from .base_rag import BaseRAG

logger = logging.getLogger(__name__)


class LegacyAIRAG(BaseRAG):
    """
    RAG implementation for Legacy AI project.

    Indexes:
    - Customer interviews (research/customer-interviews/)
    - Analyses (research/analyses/)
    - Product docs (product/)
    - Business docs (business/)
    - Customer discovery sessions (sessions/customer-discovery/)

    Privacy: Isolated ChromaDB collection, no cross-project data.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize Legacy AI RAG."""
        super().__init__(project_name="Legacy AI", config_path=config_path)

        # Lazy-loaded components
        self._initialized = False

    def get_repo_path(self) -> Path:
        """Get Legacy AI repository path."""
        return Path.home() / "Documents/1. Projects/lifeadmin"

    def _ensure_initialized(self):
        """Lazy initialization of ChromaDB and embeddings."""
        if self._initialized:
            return

        try:
            import chromadb
            from chromadb.config import Settings
            from openai import OpenAI
        except ImportError as e:
            raise ImportError(
                f"Required dependencies not installed: {e}. "
                "Install with: pip install chromadb openai"
            )

        # Initialize ChromaDB client
        repo_path = self.get_repo_path()
        persist_dir = repo_path / self.chroma_persist_dir
        persist_dir.mkdir(parents=True, exist_ok=True)

        self._chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self._collection = self._chroma_client.get_or_create_collection(
            name=self.chroma_collection,
            metadata={"project": self.project_name}
        )

        # Initialize OpenAI client for embeddings
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not found, embeddings will fail")

        self._openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

        # Initialize BGE reranker (optional, for local reranking)
        if self.reranking_enabled:
            try:
                from sentence_transformers import CrossEncoder
                self._reranker = CrossEncoder(self.reranker_model)
                logger.info(f"Loaded BGE reranker: {self.reranker_model}")
            except ImportError:
                logger.warning("sentence-transformers not installed, reranking disabled")
                self._reranker = None
        else:
            self._reranker = None

        self._initialized = True
        logger.info(f"Initialized {self.project_name} RAG")

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (384 dimensions for text-embedding-3-small)
        """
        if not self._openai_client:
            raise ValueError("OpenAI client not initialized")

        response = self._openai_client.embeddings.create(
            input=text,
            model=self.embedding_model
        )

        return response.data[0].embedding

    def _chunk_document(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Chunk document using header-based splitting.

        Args:
            file_path: Path to markdown file

        Returns:
            List of chunks with metadata
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []

        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0

        lines = content.split('\n')

        for line in lines:
            line_size = len(line)

            # Check if this is a header (starts with #)
            is_header = line.strip().startswith('#')

            # If adding this line exceeds chunk size and we have content, create chunk
            if current_size + line_size > self.chunk_size and current_chunk:
                chunk_text = '\n'.join(current_chunk)

                # Generate unique ID for this chunk
                chunk_hash = hashlib.md5(
                    f"{file_path}{chunk_id}".encode()
                ).hexdigest()[:16]

                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "source": str(file_path.relative_to(self.get_repo_path())),
                        "chunk_id": chunk_id,
                        "doc_type": self._classify_doc_type(file_path)
                    },
                    "id": f"{file_path.stem}_{chunk_hash}"
                })

                chunk_id += 1

                # Start new chunk with overlap
                if self.chunk_overlap > 0:
                    overlap_lines = []
                    overlap_size = 0
                    for prev_line in reversed(current_chunk):
                        if overlap_size + len(prev_line) <= self.chunk_overlap:
                            overlap_lines.insert(0, prev_line)
                            overlap_size += len(prev_line)
                        else:
                            break
                    current_chunk = overlap_lines
                    current_size = overlap_size
                else:
                    current_chunk = []
                    current_size = 0

            current_chunk.append(line)
            current_size += line_size

        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            chunk_hash = hashlib.md5(
                f"{file_path}{chunk_id}".encode()
            ).hexdigest()[:16]

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": str(file_path.relative_to(self.get_repo_path())),
                    "chunk_id": chunk_id,
                    "doc_type": self._classify_doc_type(file_path)
                },
                "id": f"{file_path.stem}_{chunk_hash}"
            })

        return chunks

    def _classify_doc_type(self, file_path: Path) -> str:
        """Classify document type based on path."""
        path_str = str(file_path)

        if "customer-interviews" in path_str:
            return "interview"
        elif "analyses" in path_str:
            return "analysis"
        elif "product" in path_str:
            return "product"
        elif "business" in path_str:
            return "business"
        elif "sessions" in path_str:
            return "session"
        else:
            return "other"

    def index_documents(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Index all Legacy AI documents.

        Args:
            force_reindex: Force re-indexing even if already indexed

        Returns:
            Dict with indexing stats:
                - total_chunks: Number of chunks indexed
                - total_documents: Number of documents indexed
                - files_processed: List of processed files
        """
        self._ensure_initialized()

        # Check if already indexed
        if not force_reindex:
            existing_count = self._collection.count()
            if existing_count > 0:
                logger.info(f"Collection already has {existing_count} chunks, use force_reindex=True to reindex")
                return {
                    "status": "skipped",
                    "message": "Already indexed, use force_reindex=True",
                    "existing_chunks": existing_count
                }

        # Clear existing data if force reindex
        if force_reindex and self._collection.count() > 0:
            logger.info("Force reindex: clearing existing collection")
            self._chroma_client.delete_collection(self.chroma_collection)
            self._collection = self._chroma_client.create_collection(
                name=self.chroma_collection,
                metadata={"project": self.project_name}
            )

        # Get all markdown files to index
        repo_path = self.get_repo_path()
        all_files = []

        for index_path in self.get_index_paths():
            if not index_path.exists():
                logger.warning(f"Index path does not exist: {index_path}")
                continue

            # Find all markdown files
            for md_file in index_path.rglob("*.md"):
                # Check exclude patterns
                should_exclude = False
                for pattern in self.exclude_patterns:
                    if pattern.replace("**", "") in str(md_file):
                        should_exclude = True
                        break

                if not should_exclude:
                    all_files.append(md_file)

        logger.info(f"Found {len(all_files)} documents to index")

        # Process documents in batches
        total_chunks = 0
        batch_size = 100
        current_batch_texts = []
        current_batch_metadatas = []
        current_batch_ids = []

        for file_path in all_files:
            chunks = self._chunk_document(file_path)

            for chunk in chunks:
                # Generate embedding
                try:
                    embedding = self._generate_embedding(chunk["text"])

                    current_batch_texts.append(chunk["text"])
                    current_batch_metadatas.append(chunk["metadata"])
                    current_batch_ids.append(chunk["id"])

                    total_chunks += 1

                    # Add batch when full
                    if len(current_batch_texts) >= batch_size:
                        self._collection.add(
                            documents=current_batch_texts,
                            metadatas=current_batch_metadatas,
                            ids=current_batch_ids
                        )
                        current_batch_texts = []
                        current_batch_metadatas = []
                        current_batch_ids = []

                except Exception as e:
                    logger.error(f"Error indexing chunk from {file_path}: {e}")
                    continue

        # Add remaining batch
        if current_batch_texts:
            self._collection.add(
                documents=current_batch_texts,
                metadatas=current_batch_metadatas,
                ids=current_batch_ids
            )

        logger.info(f"Indexed {total_chunks} chunks from {len(all_files)} documents")

        return {
            "status": "success",
            "total_chunks": total_chunks,
            "total_documents": len(all_files),
            "files_processed": [str(f.relative_to(repo_path)) for f in all_files]
        }

    def search(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search Legacy AI documents.

        Args:
            query: Search query
            top_k: Number of results (default: max_results)
            filter_metadata: Optional metadata filters (e.g., {"doc_type": "interview"})

        Returns:
            List of results with content, metadata, score, source
        """
        self._ensure_initialized()

        if top_k is None:
            top_k = self.max_results

        # Check if collection is empty
        if self._collection.count() == 0:
            return []

        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        # Search with ChromaDB
        # Get more results for reranking
        n_results = self.top_k_rerank if self.reranking_enabled else top_k

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self._collection.count()),
            where=filter_metadata
        )

        # Format results
        formatted_results = []

        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "score": 1.0 - results['distances'][0][i],  # Convert distance to similarity
                "source": results['metadatas'][0][i].get('source', 'unknown')
            })

        # Apply BGE reranking if enabled
        if self.reranking_enabled and self._reranker and len(formatted_results) > 0:
            # Prepare query-document pairs for reranker
            pairs = [[query, result['content']] for result in formatted_results]

            # Get reranking scores
            rerank_scores = self._reranker.predict(pairs)

            # Update scores and re-sort
            for i, score in enumerate(rerank_scores):
                formatted_results[i]['rerank_score'] = float(score)
                formatted_results[i]['original_score'] = formatted_results[i]['score']
                formatted_results[i]['score'] = float(score)

            # Sort by rerank score
            formatted_results.sort(key=lambda x: x['score'], reverse=True)

            logger.info(f"Reranked {len(formatted_results)} results")

        # Return top_k after reranking
        return formatted_results[:top_k]

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG statistics for Legacy AI."""
        self._ensure_initialized()

        return {
            "project": self.project_name,
            "collection_name": self.chroma_collection,
            "total_chunks": self._collection.count(),
            "embedding_model": self.embedding_model,
            "reranking_enabled": self.reranking_enabled,
            "reranker_model": self.reranker_model if self.reranking_enabled else None,
            "index_paths": [str(p) for p in self.get_index_paths()]
        }
