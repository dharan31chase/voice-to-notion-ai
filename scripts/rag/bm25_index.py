"""
BM25 Index for Legacy AI RAG

Keyword-based search using BM25 algorithm.
"""

import re
import pickle
from pathlib import Path
from typing import Optional
import structlog
from rank_bm25 import BM25Okapi

logger = structlog.get_logger()


class BM25Index:
    """
    BM25 keyword search index.

    Features:
    - Okapi BM25 algorithm
    - Simple tokenization
    - Persistent storage
    - Fast keyword matching
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        persist_path: str = "~/.cache/legacy-ai-rag/bm25_index.pkl"
    ):
        self.k1 = k1
        self.b = b
        self.persist_path = Path(persist_path).expanduser()
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)

        self.bm25: Optional[BM25Okapi] = None
        self.documents: list[str] = []
        self.doc_ids: list[str] = []

    def build(self, chunks: list[dict]):
        """
        Build BM25 index from chunks.

        Args:
            chunks: List of chunk dicts with 'id' and 'text' keys
        """
        if not chunks:
            logger.warning("bm25_build_empty")
            return

        # Extract texts and IDs
        self.documents = [chunk["text"] for chunk in chunks]
        self.doc_ids = [chunk["id"] for chunk in chunks]

        # Tokenize documents
        tokenized = [self.tokenize(doc) for doc in self.documents]

        # Build BM25 index
        self.bm25 = BM25Okapi(tokenized, k1=self.k1, b=self.b)

        logger.info("bm25_index_built",
            documents=len(self.documents),
            avg_tokens=sum(len(t) for t in tokenized) / len(tokenized)
        )

        # Save to disk
        self.save()

    def search(self, query: str, top_k: int = 50) -> list[tuple[str, float]]:
        """
        Search for documents matching query.

        Args:
            query: Search query string
            top_k: Number of results to return

        Returns:
            List of (doc_id, score) tuples sorted by score descending
        """
        if self.bm25 is None:
            logger.warning("bm25_search_no_index")
            return []

        # Tokenize query
        tokenized_query = self.tokenize(query)

        if not tokenized_query:
            return []

        # Get scores for all documents
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = scores.argsort()[-top_k:][::-1]

        # Return (doc_id, score) pairs
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include non-zero scores
                results.append((self.doc_ids[idx], float(scores[idx])))

        return results

    def tokenize(self, text: str) -> list[str]:
        """
        Simple tokenization for BM25.

        - Lowercase
        - Split on non-alphanumeric
        - Remove very short tokens
        """
        # Convert to lowercase and split on non-alphanumeric
        tokens = re.findall(r'\w+', text.lower())

        # Filter very short tokens (likely noise)
        tokens = [t for t in tokens if len(t) > 1]

        return tokens

    def save(self):
        """Save index to disk."""
        if self.bm25 is None:
            return

        data = {
            "bm25": self.bm25,
            "documents": self.documents,
            "doc_ids": self.doc_ids,
            "k1": self.k1,
            "b": self.b
        }

        with open(self.persist_path, "wb") as f:
            pickle.dump(data, f)

        logger.info("bm25_index_saved", path=str(self.persist_path))

    def load(self) -> bool:
        """
        Load index from disk.

        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.persist_path.exists():
            return False

        try:
            with open(self.persist_path, "rb") as f:
                data = pickle.load(f)

            self.bm25 = data["bm25"]
            self.documents = data["documents"]
            self.doc_ids = data["doc_ids"]
            self.k1 = data.get("k1", 1.5)
            self.b = data.get("b", 0.75)

            logger.info("bm25_index_loaded",
                path=str(self.persist_path),
                documents=len(self.documents)
            )
            return True

        except Exception as e:
            logger.error("bm25_index_load_failed", error=str(e))
            return False

    def get_document(self, doc_id: str) -> Optional[str]:
        """Get document text by ID."""
        try:
            idx = self.doc_ids.index(doc_id)
            return self.documents[idx]
        except ValueError:
            return None

    def count(self) -> int:
        """Get number of documents in index."""
        return len(self.documents)

    def clear(self):
        """Clear the index."""
        self.bm25 = None
        self.documents = []
        self.doc_ids = []

        if self.persist_path.exists():
            self.persist_path.unlink()

        logger.info("bm25_index_cleared")

    def stats(self) -> dict:
        """Get index statistics."""
        if not self.documents:
            return {"documents": 0, "avg_tokens": 0}

        tokenized = [self.tokenize(doc) for doc in self.documents]
        total_tokens = sum(len(t) for t in tokenized)

        return {
            "documents": len(self.documents),
            "total_tokens": total_tokens,
            "avg_tokens": total_tokens / len(self.documents) if self.documents else 0
        }
