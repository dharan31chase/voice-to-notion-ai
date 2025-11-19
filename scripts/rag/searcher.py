"""
Hybrid Searcher for Legacy AI RAG

Combines BM25 keyword search with semantic vector search using RRF fusion.
"""

from typing import Optional
import structlog
from .embeddings import EmbeddingGenerator
from .storage import VectorStore
from .bm25_index import BM25Index

logger = structlog.get_logger()


class HybridSearcher:
    """
    Hybrid search combining BM25 and semantic similarity.

    Features:
    - BM25 for keyword matching
    - Semantic embeddings for meaning
    - Reciprocal Rank Fusion (RRF) for score combination
    - Metadata filtering
    - Configurable weights
    """

    def __init__(
        self,
        vector_store: VectorStore,
        bm25_index: BM25Index,
        embedding_generator: EmbeddingGenerator,
        bm25_weight: float = 0.3,
        semantic_weight: float = 0.7,
        rrf_k: int = 60
    ):
        """
        Initialize hybrid searcher.

        Args:
            vector_store: Chroma vector store
            bm25_index: BM25 keyword index
            embedding_generator: For query embedding
            bm25_weight: Weight for BM25 scores (0-1)
            semantic_weight: Weight for semantic scores (0-1)
            rrf_k: RRF constant (higher = smoother ranking)
        """
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.embedder = embedding_generator
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        self.rrf_k = rrf_k

        # Load BM25 index if not already loaded
        if not self.bm25_index.bm25:
            self.bm25_index.load()

    def search(
        self,
        query: str,
        top_k: int = 10,
        bm25_candidates: int = 50,
        semantic_candidates: int = 50,
        where: dict = None,
        include_scores: bool = True
    ) -> list[dict]:
        """
        Perform hybrid search.

        Args:
            query: Search query string
            top_k: Number of final results
            bm25_candidates: Number of BM25 candidates to fetch
            semantic_candidates: Number of semantic candidates to fetch
            where: Metadata filter for vector search
            include_scores: Whether to include individual scores

        Returns:
            List of result dicts sorted by combined score
        """
        logger.info("hybrid_search_start",
            query=query[:50],
            top_k=top_k,
            bm25_candidates=bm25_candidates,
            semantic_candidates=semantic_candidates
        )

        # 1. BM25 search
        bm25_results = self._bm25_search(query, bm25_candidates)

        # 2. Semantic search
        semantic_results = self._semantic_search(
            query, semantic_candidates, where
        )

        # 3. Combine with RRF
        combined = self._rrf_fusion(bm25_results, semantic_results)

        # 4. Get top_k results with full metadata
        results = self._fetch_results(combined[:top_k], include_scores)

        logger.info("hybrid_search_complete",
            query=query[:50],
            results=len(results),
            bm25_hits=len(bm25_results),
            semantic_hits=len(semantic_results)
        )

        return results

    def _bm25_search(self, query: str, top_k: int) -> list[tuple[str, float, int]]:
        """
        Perform BM25 keyword search.

        Returns:
            List of (doc_id, score, rank) tuples
        """
        results = self.bm25_index.search(query, top_k)

        # Add rank for RRF
        ranked = []
        for rank, (doc_id, score) in enumerate(results, 1):
            ranked.append((doc_id, score, rank))

        return ranked

    def _semantic_search(
        self,
        query: str,
        top_k: int,
        where: dict = None
    ) -> list[tuple[str, float, int]]:
        """
        Perform semantic similarity search.

        Returns:
            List of (doc_id, distance, rank) tuples
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_single(query)

        # Search vector store
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=top_k,
            where=where
        )

        # Convert to ranked tuples (lower distance = better)
        ranked = []
        for rank, result in enumerate(results, 1):
            # Convert distance to similarity (1 - distance for cosine)
            similarity = 1 - result["distance"]
            ranked.append((result["id"], similarity, rank))

        return ranked

    def _rrf_fusion(
        self,
        bm25_results: list[tuple[str, float, int]],
        semantic_results: list[tuple[str, float, int]]
    ) -> list[tuple[str, float, dict]]:
        """
        Combine results using Reciprocal Rank Fusion.

        RRF score = sum(1 / (k + rank))

        Args:
            bm25_results: BM25 results with ranks
            semantic_results: Semantic results with ranks

        Returns:
            Combined results sorted by RRF score, with score breakdown
        """
        # Build score maps
        scores = {}  # doc_id -> {rrf_score, bm25_score, semantic_score, bm25_rank, semantic_rank}

        # Process BM25 results
        for doc_id, score, rank in bm25_results:
            if doc_id not in scores:
                scores[doc_id] = {
                    "rrf_score": 0,
                    "bm25_score": 0,
                    "semantic_score": 0,
                    "bm25_rank": None,
                    "semantic_rank": None
                }

            rrf_contribution = self.bm25_weight / (self.rrf_k + rank)
            scores[doc_id]["rrf_score"] += rrf_contribution
            scores[doc_id]["bm25_score"] = score
            scores[doc_id]["bm25_rank"] = rank

        # Process semantic results
        for doc_id, similarity, rank in semantic_results:
            if doc_id not in scores:
                scores[doc_id] = {
                    "rrf_score": 0,
                    "bm25_score": 0,
                    "semantic_score": 0,
                    "bm25_rank": None,
                    "semantic_rank": None
                }

            rrf_contribution = self.semantic_weight / (self.rrf_k + rank)
            scores[doc_id]["rrf_score"] += rrf_contribution
            scores[doc_id]["semantic_score"] = similarity
            scores[doc_id]["semantic_rank"] = rank

        # Sort by RRF score
        sorted_results = sorted(
            scores.items(),
            key=lambda x: x[1]["rrf_score"],
            reverse=True
        )

        return [(doc_id, data["rrf_score"], data) for doc_id, data in sorted_results]

    def _fetch_results(
        self,
        scored_results: list[tuple[str, float, dict]],
        include_scores: bool
    ) -> list[dict]:
        """
        Fetch full document data for results.

        Args:
            scored_results: List of (doc_id, rrf_score, score_breakdown)
            include_scores: Whether to include score details

        Returns:
            List of result dicts with text, metadata, and optional scores
        """
        if not scored_results:
            return []

        # Get document IDs
        doc_ids = [doc_id for doc_id, _, _ in scored_results]

        # Fetch from vector store
        docs = self.vector_store.get_by_ids(doc_ids)

        # Build results with scores
        results = []
        doc_map = {doc["id"]: doc for doc in docs}

        for doc_id, rrf_score, score_breakdown in scored_results:
            if doc_id not in doc_map:
                continue

            doc = doc_map[doc_id]
            result = {
                "id": doc_id,
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": rrf_score
            }

            if include_scores:
                result["score_breakdown"] = {
                    "rrf": rrf_score,
                    "bm25": score_breakdown["bm25_score"],
                    "semantic": score_breakdown["semantic_score"],
                    "bm25_rank": score_breakdown["bm25_rank"],
                    "semantic_rank": score_breakdown["semantic_rank"]
                }

            results.append(result)

        return results

    def search_bm25_only(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Search using only BM25 (fallback mode).

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of results
        """
        results = self.bm25_index.search(query, top_k)

        if not results:
            return []

        doc_ids = [doc_id for doc_id, _ in results]
        docs = self.vector_store.get_by_ids(doc_ids)
        doc_map = {doc["id"]: doc for doc in docs}

        formatted = []
        for doc_id, score in results:
            if doc_id in doc_map:
                doc = doc_map[doc_id]
                formatted.append({
                    "id": doc_id,
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": score
                })

        return formatted

    def search_semantic_only(
        self,
        query: str,
        top_k: int = 10,
        where: dict = None
    ) -> list[dict]:
        """
        Search using only semantic similarity (fallback mode).

        Args:
            query: Search query
            top_k: Number of results
            where: Metadata filter

        Returns:
            List of results
        """
        query_embedding = self.embedder.generate_single(query)

        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=top_k,
            where=where
        )

        # Convert distance to score
        for result in results:
            result["score"] = 1 - result["distance"]
            del result["distance"]

        return results


def create_searcher(config: dict = None) -> HybridSearcher:
    """
    Create a configured HybridSearcher instance.

    Args:
        config: Configuration dict (uses defaults if None)

    Returns:
        Configured HybridSearcher
    """
    if config is None:
        config = {
            "storage": {
                "persist_directory": "~/.cache/legacy-ai-rag/chroma",
                "collection_name": "legacy_ai_interviews"
            },
            "embeddings": {
                "model": "text-embedding-3-small",
                "batch_size": 100,
                "max_retries": 3
            },
            "bm25": {
                "k1": 1.5,
                "b": 0.75,
                "persist_path": "~/.cache/legacy-ai-rag/bm25_index.pkl"
            },
            "search": {
                "bm25_weight": 0.3,
                "semantic_weight": 0.7,
                "rrf_k": 60
            }
        }

    # Initialize components
    vector_store = VectorStore(
        persist_directory=config["storage"]["persist_directory"],
        collection_name=config["storage"]["collection_name"]
    )

    bm25_index = BM25Index(
        k1=config["bm25"]["k1"],
        b=config["bm25"]["b"],
        persist_path=config["bm25"]["persist_path"]
    )

    embedder = EmbeddingGenerator(
        model=config["embeddings"]["model"],
        batch_size=config["embeddings"]["batch_size"],
        max_retries=config["embeddings"]["max_retries"],
        cache_dir=config["storage"]["persist_directory"]
    )

    return HybridSearcher(
        vector_store=vector_store,
        bm25_index=bm25_index,
        embedding_generator=embedder,
        bm25_weight=config["search"]["bm25_weight"],
        semantic_weight=config["search"]["semantic_weight"],
        rrf_k=config["search"]["rrf_k"]
    )
