"""
Base RAG Implementation (Phase 6)

Privacy-first RAG with separate ChromaDB collections per project.

Architecture:
- Each project has its own ChromaDB collection
- Hybrid search: BM25 + semantic embeddings + BGE reranking
- Privacy isolation: No cross-project data leakage
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseRAG(ABC):
    """
    Base RAG class for project-specific document search.

    Each project subclass implements:
    - Project-specific document paths
    - Project-specific ChromaDB collection
    - Privacy-isolated search
    """

    def __init__(
        self,
        project_name: str,
        config_path: Optional[Path] = None
    ):
        """
        Initialize RAG for a specific project.

        Args:
            project_name: Project name (e.g., "Epic 2nd Brain", "Legacy AI")
            config_path: Optional path to rag-repos.json
        """
        self.project_name = project_name

        # Load configuration
        if config_path is None:
            config_path = Path.home() / "Documents/1. Projects/ai-assistant/docs/config/rag-repos.json"

        self.config = self._load_config(config_path)
        self.project_config = self.config["projects"].get(project_name, {})

        if not self.project_config:
            raise ValueError(f"Project '{project_name}' not found in RAG config")

        # Project settings
        self.enabled = self.project_config.get("enabled", False)
        self.chroma_collection = self.project_config.get("chroma_collection")
        self.index_paths = self.project_config.get("index_paths", [])
        self.exclude_patterns = self.project_config.get("exclude_patterns", [])
        self.embedding_model = self.project_config.get("embedding_model", "text-embedding-3-small")
        self.chunk_size = self.project_config.get("chunk_size", 1000)
        self.chunk_overlap = self.project_config.get("chunk_overlap", 200)

        # Reranking settings
        self.reranking_config = self.project_config.get("reranking", {})
        self.reranking_enabled = self.reranking_config.get("enabled", True)
        self.reranker_model = self.reranking_config.get("model", "BAAI/bge-reranker-base")
        self.top_k_rerank = self.reranking_config.get("top_k_rerank", 20)

        # Global settings
        self.global_config = self.config.get("global_settings", {})
        self.chroma_persist_dir = Path(self.global_config.get("chroma_persist_directory", ".chroma"))
        self.max_results = self.global_config.get("max_results_per_query", 10)

        # Initialize components (lazy load)
        self._chroma_client = None
        self._collection = None
        self._embeddings = None
        self._reranker = None

    def _load_config(self, config_path: Path) -> Dict:
        """Load RAG configuration from JSON."""
        if not config_path.exists():
            raise FileNotFoundError(f"RAG config not found: {config_path}")

        with open(config_path, 'r') as f:
            return json.load(f)

    @abstractmethod
    def get_repo_path(self) -> Path:
        """
        Get repository path for this project.

        Subclasses must implement this to return the correct repo path.

        Returns:
            Path to project repository
        """
        pass

    def is_enabled(self) -> bool:
        """Check if RAG is enabled for this project."""
        return self.enabled

    def get_index_paths(self) -> List[Path]:
        """
        Get full paths to index directories.

        Returns:
            List of absolute paths to index
        """
        repo_path = self.get_repo_path()
        return [repo_path / path for path in self.index_paths]

    def search(
        self,
        query: str,
        top_k: int = None,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search documents in this project's RAG index.

        Args:
            query: Search query
            top_k: Number of results to return (default: max_results)
            filter_metadata: Optional metadata filters

        Returns:
            List of dicts with:
                - content: Document chunk content
                - metadata: Document metadata (file_path, chunk_id, etc.)
                - score: Relevance score
                - source: File path

        Raises:
            NotImplementedError: If RAG not enabled or not indexed
        """
        if not self.is_enabled():
            raise NotImplementedError(f"RAG not enabled for project '{self.project_name}'")

        # Subclasses implement actual search logic
        raise NotImplementedError("Subclass must implement search()")

    def index_documents(self, force_reindex: bool = False) -> Dict[str, Any]:
        """
        Index all documents for this project.

        Args:
            force_reindex: Force re-indexing even if already indexed

        Returns:
            Dict with indexing stats

        Raises:
            NotImplementedError: Subclass must implement
        """
        raise NotImplementedError("Subclass must implement index_documents()")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG statistics for this project.

        Returns:
            Dict with:
                - total_chunks: Number of indexed chunks
                - total_documents: Number of indexed documents
                - collection_name: ChromaDB collection name
                - last_indexed: Timestamp of last index

        Raises:
            NotImplementedError: Subclass must implement
        """
        raise NotImplementedError("Subclass must implement get_stats()")

    def __repr__(self):
        """String representation of RAG instance."""
        enabled_status = "enabled" if self.enabled else "disabled"
        return f"<{self.__class__.__name__}: {self.project_name} ({enabled_status})>"
