"""
BGE Reranker for Legacy AI RAG

Cross-encoder reranking for improved precision.
"""

from typing import Optional
import structlog
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

logger = structlog.get_logger()


class BGEReranker:
    """
    BGE cross-encoder reranker for improving search precision.

    Features:
    - Lazy model loading (only loads when first used)
    - GPU acceleration if available
    - Batch processing for efficiency
    - Score normalization
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        device: str = None,
        batch_size: int = 32
    ):
        """
        Initialize reranker.

        Args:
            model_name: HuggingFace model name
            device: Device to use (auto-detect if None)
            batch_size: Batch size for inference
        """
        self.model_name = model_name
        self.batch_size = batch_size

        # Determine device
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device

        # Lazy loading
        self._model = None
        self._tokenizer = None
        self._loaded = False

    def _load_model(self):
        """Load model and tokenizer (lazy loading)."""
        if self._loaded:
            return

        logger.info("reranker_loading",
            model=self.model_name,
            device=self.device
        )

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name
        )
        self._model.to(self.device)
        self._model.eval()

        self._loaded = True

        logger.info("reranker_loaded",
            model=self.model_name,
            device=self.device
        )

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: int = None
    ) -> list[dict]:
        """
        Rerank search results using BGE cross-encoder.

        Args:
            query: Original search query
            results: Search results with 'text' field
            top_k: Number of results to return (all if None)

        Returns:
            Reranked results with updated scores
        """
        if not results:
            return []

        # Load model if needed
        self._load_model()

        logger.info("reranking_start",
            query=query[:50],
            candidates=len(results)
        )

        # Prepare pairs for scoring
        pairs = [(query, result["text"]) for result in results]

        # Score in batches
        scores = []
        for i in range(0, len(pairs), self.batch_size):
            batch = pairs[i:i + self.batch_size]
            batch_scores = self._score_batch(batch)
            scores.extend(batch_scores)

        # Add rerank scores to results
        for result, score in zip(results, scores):
            result["rerank_score"] = score
            # Preserve original score
            if "score" in result:
                result["retrieval_score"] = result["score"]
            result["score"] = score

        # Sort by rerank score
        reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)

        # Apply top_k
        if top_k is not None:
            reranked = reranked[:top_k]

        logger.info("reranking_complete",
            query=query[:50],
            results=len(reranked)
        )

        return reranked

    def _score_batch(self, pairs: list[tuple[str, str]]) -> list[float]:
        """
        Score a batch of query-document pairs.

        Args:
            pairs: List of (query, document) tuples

        Returns:
            List of relevance scores
        """
        with torch.no_grad():
            # Tokenize
            inputs = self._tokenizer(
                pairs,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Forward pass
            outputs = self._model(**inputs)

            # Get scores (sigmoid for probability)
            scores = torch.sigmoid(outputs.logits.squeeze(-1))

            return scores.cpu().tolist()

    def score_single(self, query: str, document: str) -> float:
        """
        Score a single query-document pair.

        Args:
            query: Query string
            document: Document text

        Returns:
            Relevance score
        """
        self._load_model()
        scores = self._score_batch([(query, document)])
        return scores[0] if scores else 0.0

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._loaded

    def unload(self):
        """Unload model to free memory."""
        if self._loaded:
            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None
            self._loaded = False

            # Clear GPU cache
            if self.device == "cuda":
                torch.cuda.empty_cache()
            elif self.device == "mps":
                torch.mps.empty_cache()

            logger.info("reranker_unloaded")


class RerankerPipeline:
    """
    Complete reranking pipeline with search integration.

    Combines hybrid search + BGE reranking for best results.
    """

    def __init__(
        self,
        searcher,
        reranker: BGEReranker = None,
        rerank_candidates: int = 20,
        final_results: int = 5
    ):
        """
        Initialize pipeline.

        Args:
            searcher: HybridSearcher instance
            reranker: BGEReranker instance (creates default if None)
            rerank_candidates: Number of candidates to rerank
            final_results: Number of final results
        """
        self.searcher = searcher
        self.reranker = reranker or BGEReranker()
        self.rerank_candidates = rerank_candidates
        self.final_results = final_results

    def search(
        self,
        query: str,
        top_k: int = None,
        where: dict = None,
        skip_rerank: bool = False
    ) -> list[dict]:
        """
        Search with reranking.

        Args:
            query: Search query
            top_k: Final results (uses self.final_results if None)
            where: Metadata filter
            skip_rerank: Skip reranking (for speed/debugging)

        Returns:
            Reranked search results
        """
        if top_k is None:
            top_k = self.final_results

        # Get initial candidates
        candidates = self.searcher.search(
            query=query,
            top_k=self.rerank_candidates,
            where=where
        )

        if not candidates:
            return []

        # Skip reranking if requested
        if skip_rerank:
            return candidates[:top_k]

        # Rerank
        reranked = self.reranker.rerank(
            query=query,
            results=candidates,
            top_k=top_k
        )

        return reranked

    def search_graceful(
        self,
        query: str,
        top_k: int = None,
        where: dict = None
    ) -> list[dict]:
        """
        Search with graceful degradation.

        Falls back to hybrid search if reranking fails.

        Args:
            query: Search query
            top_k: Final results
            where: Metadata filter

        Returns:
            Search results (reranked or fallback)
        """
        if top_k is None:
            top_k = self.final_results

        try:
            return self.search(query, top_k, where)
        except Exception as e:
            logger.warning("reranking_failed_fallback",
                error=str(e),
                query=query[:50]
            )

            # Fallback to hybrid search without reranking
            return self.searcher.search(
                query=query,
                top_k=top_k,
                where=where
            )


def create_reranker(config: dict = None) -> BGEReranker:
    """
    Create a configured BGEReranker instance.

    Args:
        config: Configuration dict

    Returns:
        Configured BGEReranker
    """
    if config is None:
        config = {
            "model": "BAAI/bge-reranker-base",
            "batch_size": 32
        }

    return BGEReranker(
        model_name=config.get("model", "BAAI/bge-reranker-base"),
        batch_size=config.get("batch_size", 32)
    )
