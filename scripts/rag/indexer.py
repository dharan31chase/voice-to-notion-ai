"""
Indexing Pipeline for Legacy AI RAG

Orchestrates document chunking, embedding generation, and storage.
"""

import os
import glob
from pathlib import Path
from datetime import datetime
import structlog
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .chunker import DocumentChunker
from .embeddings import EmbeddingGenerator
from .storage import VectorStore
from .bm25_index import BM25Index

logger = structlog.get_logger()


class Indexer:
    """
    Full indexing pipeline for Legacy AI corpus.

    Orchestrates:
    1. Document discovery
    2. Chunking with headers and overlap
    3. Embedding generation with caching
    4. Vector store updates
    5. BM25 index rebuilding
    """

    def __init__(self, config_path: str = None):
        """
        Initialize indexer from config.

        Args:
            config_path: Path to rag_config.yaml
        """
        # Load config
        if config_path:
            config = self._load_config(config_path)
        else:
            config = self._default_config()

        # Initialize components
        self.corpus_path = Path(config["corpus"]["path"]).expanduser()
        self.include_patterns = config["corpus"]["include_patterns"]
        self.exclude_patterns = config["corpus"]["exclude_patterns"]

        self.chunker = DocumentChunker(
            max_chunk_tokens=config["chunking"]["max_chunk_tokens"],
            min_chunk_tokens=config["chunking"]["min_chunk_tokens"],
            overlap_tokens=config["chunking"]["overlap_tokens"],
            header_levels=config["chunking"]["header_levels"]
        )

        self.embedder = EmbeddingGenerator(
            model=config["embeddings"]["model"],
            batch_size=config["embeddings"]["batch_size"],
            max_retries=config["embeddings"]["max_retries"],
            cache_dir=config["storage"]["persist_directory"]
        )

        self.storage = VectorStore(
            persist_directory=config["storage"]["persist_directory"],
            collection_name=config["storage"]["collection_name"]
        )

        self.bm25 = BM25Index(
            k1=config["bm25"]["k1"],
            b=config["bm25"]["b"],
            persist_path=config["bm25"]["persist_path"]
        )

        # Index state
        self.state_file = Path(config["storage"]["persist_directory"]).expanduser() / "index_state.yaml"

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """Default configuration."""
        return {
            "corpus": {
                "path": "~/Documents/1. Projects/legacy-ai/research",
                "include_patterns": ["**/*.md", "**/*.txt"],
                "exclude_patterns": ["**/.*", "**/__pycache__"]
            },
            "chunking": {
                "max_chunk_tokens": 2000,
                "min_chunk_tokens": 100,
                "overlap_tokens": 200,
                "header_levels": ["#", "##", "###"]
            },
            "embeddings": {
                "model": "text-embedding-3-small",
                "batch_size": 100,
                "max_retries": 3
            },
            "storage": {
                "persist_directory": "~/.cache/legacy-ai-rag/chroma",
                "collection_name": "legacy_ai_interviews"
            },
            "bm25": {
                "k1": 1.5,
                "b": 0.75,
                "persist_path": "~/.cache/legacy-ai-rag/bm25_index.pkl"
            }
        }

    def index_corpus(self, incremental: bool = True):
        """
        Index the entire corpus.

        Args:
            incremental: If True, only reindex changed files
        """
        logger.info("indexing_started",
            corpus=str(self.corpus_path),
            incremental=incremental
        )

        # 1. Find documents
        if incremental:
            docs = self._get_documents_to_reindex()
            if not docs:
                logger.info("no_documents_changed")
                return
        else:
            docs = self._get_all_documents()
            # Clear existing data for full reindex
            self.storage.clear()

        logger.info("documents_to_index", count=len(docs))

        # 2. Chunk all documents
        all_chunks = []
        for doc_path in docs:
            try:
                chunks = self.chunker.chunk_document(doc_path)
                all_chunks.extend(chunks)
                logger.info("document_chunked",
                    path=doc_path,
                    chunks=len(chunks)
                )
            except Exception as e:
                logger.error("document_chunk_failed",
                    path=doc_path,
                    error=str(e)
                )

        if not all_chunks:
            logger.warning("no_chunks_created")
            return

        logger.info("chunking_complete",
            total_chunks=len(all_chunks),
            total_tokens=sum(c.metadata.token_count for c in all_chunks)
        )

        # 3. Set indexed_at timestamp
        indexed_at = datetime.now().isoformat()
        for chunk in all_chunks:
            chunk.metadata.indexed_at = indexed_at

        # 4. Generate embeddings
        texts = [chunk.text for chunk in all_chunks]
        embeddings = self.embedder.generate(texts)
        self.embedder.save_cache()

        logger.info("embeddings_generated", count=len(embeddings))

        # 5. Remove old chunks for reindexed documents (incremental only)
        if incremental:
            for doc_path in docs:
                self.storage.delete_by_source(doc_path)

        # 6. Store chunks and embeddings
        self.storage.add(all_chunks, embeddings)

        # 7. Rebuild BM25 index (always full rebuild - it's fast)
        all_stored = self.storage.get_all_chunks()
        self.bm25.build(all_stored)

        # 8. Save state
        self._save_state()

        # Log stats
        stats = self.storage.stats()
        logger.info("indexing_complete",
            chunks=stats["total_chunks"],
            documents=stats["total_documents"],
            tokens=stats["total_tokens"]
        )

    def _get_all_documents(self) -> list[str]:
        """Get all documents in corpus."""
        docs = []

        for pattern in self.include_patterns:
            full_pattern = str(self.corpus_path / pattern)
            matches = glob.glob(full_pattern, recursive=True)
            docs.extend(matches)

        # Filter excludes
        filtered = []
        for doc in docs:
            excluded = False
            for exclude in self.exclude_patterns:
                if glob.fnmatch.fnmatch(doc, f"*{exclude}*"):
                    excluded = True
                    break
            if not excluded:
                filtered.append(doc)

        return sorted(set(filtered))

    def _get_documents_to_reindex(self) -> list[str]:
        """Get documents that have changed since last index."""
        last_index_time = self._get_last_index_time()

        if last_index_time == 0:
            # No previous index, index everything
            return self._get_all_documents()

        all_docs = self._get_all_documents()
        changed = []

        for doc in all_docs:
            mtime = os.path.getmtime(doc)
            if mtime > last_index_time:
                changed.append(doc)

        # Also check for deleted documents
        stored_sources = set(self.storage.get_sources())
        current_sources = set(all_docs)
        deleted = stored_sources - current_sources

        if deleted:
            for source in deleted:
                self.storage.delete_by_source(source)
            logger.info("deleted_documents_removed", count=len(deleted))

        return changed

    def _get_last_index_time(self) -> float:
        """Get timestamp of last index operation."""
        if not self.state_file.exists():
            return 0

        try:
            with open(self.state_file) as f:
                state = yaml.safe_load(f)
            return state.get("last_index_time", 0)
        except Exception:
            return 0

    def _save_state(self):
        """Save index state."""
        state = {
            "last_index_time": datetime.now().timestamp(),
            "last_index_date": datetime.now().isoformat(),
            "corpus_path": str(self.corpus_path),
            "stats": self.storage.stats()
        }

        with open(self.state_file, "w") as f:
            yaml.dump(state, f)

        logger.info("index_state_saved", path=str(self.state_file))

    def get_stats(self) -> dict:
        """Get comprehensive index statistics."""
        storage_stats = self.storage.stats()
        bm25_stats = self.bm25.stats()
        cache_stats = self.embedder.cache_stats()

        return {
            "storage": storage_stats,
            "bm25": bm25_stats,
            "embedding_cache": cache_stats,
            "corpus_path": str(self.corpus_path)
        }


def main():
    """CLI entry point for indexing."""
    import argparse

    parser = argparse.ArgumentParser(description="Index Legacy AI corpus for RAG")
    parser.add_argument(
        "--config",
        default="config/rag_config.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full reindex (not incremental)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show index statistics only"
    )

    args = parser.parse_args()

    # Find config file
    config_path = Path(args.config)
    if not config_path.is_absolute():
        # Look relative to script location
        script_dir = Path(__file__).parent.parent.parent
        config_path = script_dir / args.config

    indexer = Indexer(str(config_path) if config_path.exists() else None)

    if args.stats:
        stats = indexer.get_stats()
        print(yaml.dump(stats, default_flow_style=False))
    else:
        indexer.index_corpus(incremental=not args.full)


if __name__ == "__main__":
    main()
