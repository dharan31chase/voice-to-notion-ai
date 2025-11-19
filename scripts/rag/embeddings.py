"""
Embedding Generator for Legacy AI RAG

Generates OpenAI embeddings with batching, caching, and retry logic.
"""

import os
import asyncio
import hashlib
import json
from pathlib import Path
from typing import Optional
import logging
import structlog
from openai import OpenAI, RateLimitError, APIError, BadRequestError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = structlog.get_logger()
std_logger = logging.getLogger(__name__)


class EmbeddingCache:
    """
    Cache embeddings by content hash to avoid recomputation.

    Stores embeddings in a JSON file for persistence across runs.
    """

    def __init__(self, cache_dir: str = "~/.cache/legacy-ai-rag"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "embedding_cache.json"
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except json.JSONDecodeError:
                logger.warning("embedding_cache_corrupted", file=str(self.cache_file))
                return {}
        return {}

    def _save_cache(self):
        """Save cache to disk."""
        self.cache_file.write_text(json.dumps(self._cache))

    def get_hash(self, text: str) -> str:
        """Get hash for text content."""
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str) -> Optional[list[float]]:
        """Get cached embedding for text."""
        key = self.get_hash(text)
        return self._cache.get(key)

    def set(self, text: str, embedding: list[float]):
        """Cache embedding for text."""
        key = self.get_hash(text)
        self._cache[key] = embedding

    def save(self):
        """Persist cache to disk."""
        self._save_cache()
        logger.info("embedding_cache_saved", entries=len(self._cache))

    def clear(self):
        """Clear all cached embeddings."""
        self._cache = {}
        self._save_cache()

    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "file_size_kb": self.cache_file.stat().st_size / 1024 if self.cache_file.exists() else 0
        }


class EmbeddingGenerator:
    """
    Generate embeddings using OpenAI API.

    Features:
    - Batch processing for efficiency
    - Caching to avoid recomputation
    - Retry with exponential backoff
    - Async support
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        batch_size: int = 100,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        cache_dir: str = "~/.cache/legacy-ai-rag"
    ):
        self.model = model
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = OpenAI()
        self.cache = EmbeddingCache(cache_dir)

    def generate(self, texts: list[str], use_cache: bool = True) -> list[list[float]]:
        """
        Generate embeddings for texts.

        Args:
            texts: List of text strings to embed
            use_cache: Whether to use cached embeddings

        Returns:
            List of embedding vectors (1536 dimensions each)
        """
        if not texts:
            return []

        embeddings = [None] * len(texts)
        texts_to_embed = []
        indices_to_embed = []

        # Check cache first
        if use_cache:
            for i, text in enumerate(texts):
                cached = self.cache.get(text)
                if cached:
                    embeddings[i] = cached
                else:
                    texts_to_embed.append(text)
                    indices_to_embed.append(i)

            cache_hits = len(texts) - len(texts_to_embed)
            if cache_hits > 0:
                logger.info("embedding_cache_hits",
                    hits=cache_hits,
                    misses=len(texts_to_embed),
                    hit_rate=f"{cache_hits/len(texts)*100:.1f}%"
                )
        else:
            texts_to_embed = texts
            indices_to_embed = list(range(len(texts)))

        # Generate embeddings for uncached texts
        if texts_to_embed:
            new_embeddings = self._batch_embed(texts_to_embed)

            # Store in result and cache
            for idx, embedding in zip(indices_to_embed, new_embeddings):
                embeddings[idx] = embedding
                if use_cache:
                    self.cache.set(texts[idx], embedding)

            # Save cache periodically
            if use_cache and len(texts_to_embed) > 10:
                self.cache.save()

        return embeddings

    def _batch_embed(self, texts: list[str]) -> list[list[float]]:
        """
        Embed texts in batches with retry logic.

        Args:
            texts: Texts to embed

        Returns:
            Embeddings for all texts
        """
        all_embeddings = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]

            # Validate batch - filter empty texts and replace with placeholder
            validated_batch = []
            for text in batch:
                if text and text.strip():
                    validated_batch.append(text)
                else:
                    # Use placeholder for empty texts to maintain index alignment
                    validated_batch.append("[empty]")
                    logger.warning("empty_text_replaced", batch_index=i)
            batch = validated_batch
            batch_num = i // self.batch_size + 1
            total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

            logger.info("embedding_batch_start",
                batch=batch_num,
                total=total_batches,
                size=len(batch)
            )

            embeddings = self._embed_with_retry(batch)
            all_embeddings.extend(embeddings)

            logger.info("embedding_batch_complete",
                batch=batch_num,
                total=total_batches
            )

        return all_embeddings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((RateLimitError, APIError)),
        before_sleep=before_sleep_log(std_logger, logging.WARNING)
    )
    def _embed_with_retry(self, texts: list[str]) -> list[list[float]]:
        """
        Call OpenAI API with retry logic.

        Retries on:
        - Rate limit errors
        - API errors (transient)

        Fails fast on:
        - Authentication errors
        - Invalid requests
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        return [item.embedding for item in response.data]

    def generate_single(self, text: str, use_cache: bool = True) -> list[float]:
        """Generate embedding for single text."""
        embeddings = self.generate([text], use_cache=use_cache)
        return embeddings[0]

    def save_cache(self):
        """Persist embedding cache to disk."""
        self.cache.save()

    def clear_cache(self):
        """Clear embedding cache."""
        self.cache.clear()

    def cache_stats(self) -> dict:
        """Get cache statistics."""
        return self.cache.stats()


# Convenience functions
def generate_embeddings(texts: list[str], **kwargs) -> list[list[float]]:
    """Generate embeddings with default settings."""
    generator = EmbeddingGenerator(**kwargs)
    embeddings = generator.generate(texts)
    generator.save_cache()
    return embeddings


def generate_embedding(text: str, **kwargs) -> list[float]:
    """Generate single embedding."""
    return generate_embeddings([text], **kwargs)[0]
