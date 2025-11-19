"""
MCP Tools for Legacy AI RAG

Provides Claude Code integration via MCP protocol.
"""

import json
import yaml
from pathlib import Path
from typing import Optional
import structlog
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .searcher import HybridSearcher, create_searcher
from .reranker import BGEReranker, RerankerPipeline
from .storage import VectorStore
from .bm25_index import BM25Index
from .embeddings import EmbeddingGenerator

logger = structlog.get_logger()


class LegacyAIRAG:
    """
    Main RAG interface for Legacy AI corpus.

    Provides simple methods for searching and retrieving
    customer interview content.
    """

    def __init__(self, config_path: str = None):
        """
        Initialize RAG system.

        Args:
            config_path: Path to rag_config.yaml
        """
        # Load config
        if config_path:
            config = self._load_config(config_path)
        else:
            config = self._default_config()

        self._config = config

        # Lazy initialization
        self._searcher = None
        self._reranker = None
        self._pipeline = None

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file."""
        with open(config_path) as f:
            return yaml.safe_load(f)

    def _default_config(self) -> dict:
        """Default configuration."""
        return {
            "corpus": {
                "path": "~/Documents/1. Projects/legacy-ai/research"
            },
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
                "rrf_k": 60,
                "default_top_k": 5,
                "rerank_candidates": 20
            },
            "reranker": {
                "model": "BAAI/bge-reranker-base",
                "batch_size": 32,
                "enabled": True
            }
        }

    def _get_searcher(self) -> HybridSearcher:
        """Get or create searcher (lazy initialization)."""
        if self._searcher is None:
            self._searcher = create_searcher(self._config)
        return self._searcher

    def _get_pipeline(self) -> RerankerPipeline:
        """Get or create reranker pipeline (lazy initialization)."""
        if self._pipeline is None:
            searcher = self._get_searcher()

            if self._config["reranker"]["enabled"]:
                self._reranker = BGEReranker(
                    model_name=self._config["reranker"]["model"],
                    batch_size=self._config["reranker"]["batch_size"]
                )
            else:
                self._reranker = None

            self._pipeline = RerankerPipeline(
                searcher=searcher,
                reranker=self._reranker,
                rerank_candidates=self._config["search"]["rerank_candidates"],
                final_results=self._config["search"]["default_top_k"]
            )

        return self._pipeline

    def search(
        self,
        query: str,
        top_k: int = None,
        content_type: str = None,
        customer_name: str = None,
        use_reranker: bool = True
    ) -> list[dict]:
        """
        Search the Legacy AI corpus.

        Args:
            query: Natural language search query
            top_k: Number of results to return
            content_type: Filter by type (transcript, analysis, insight, guide)
            customer_name: Filter by customer name
            use_reranker: Whether to use BGE reranker

        Returns:
            List of relevant chunks with metadata
        """
        if top_k is None:
            top_k = self._config["search"]["default_top_k"]

        # Build metadata filter
        where = {}
        if content_type:
            where["content_type"] = content_type
        if customer_name:
            where["customer_name"] = customer_name

        where = where if where else None

        # Get pipeline
        pipeline = self._get_pipeline()

        # Search
        if use_reranker and self._config["reranker"]["enabled"]:
            results = pipeline.search_graceful(
                query=query,
                top_k=top_k,
                where=where
            )
        else:
            results = pipeline.searcher.search(
                query=query,
                top_k=top_k,
                where=where
            )

        return results

    def search_formatted(
        self,
        query: str,
        top_k: int = None,
        content_type: str = None,
        customer_name: str = None,
        use_reranker: bool = True
    ) -> str:
        """
        Search and return formatted results for Claude.

        Args:
            query: Natural language search query
            top_k: Number of results to return
            content_type: Filter by type
            customer_name: Filter by customer name
            use_reranker: Whether to use BGE reranker

        Returns:
            Formatted string with search results
        """
        results = self.search(
            query=query,
            top_k=top_k,
            content_type=content_type,
            customer_name=customer_name,
            use_reranker=use_reranker
        )

        if not results:
            return f"No results found for query: '{query}'"

        # Format results
        output = [f"## Search Results for: '{query}'\n"]
        output.append(f"Found {len(results)} relevant chunks:\n")

        for i, result in enumerate(results, 1):
            meta = result["metadata"]

            output.append(f"### Result {i}")
            output.append(f"**Source**: {meta['document_title']}")
            output.append(f"**Customer**: {meta['customer_name']}")
            output.append(f"**Type**: {meta['content_type']}")
            output.append(f"**Section**: {meta['section_header']}")

            if "score" in result:
                output.append(f"**Score**: {result['score']:.4f}")

            output.append(f"\n{result['text']}\n")
            output.append("---\n")

        return "\n".join(output)

    def get_customer_context(self, customer_name: str, top_k: int = 10) -> str:
        """
        Get all relevant context for a specific customer.

        Args:
            customer_name: Customer name to search for
            top_k: Maximum chunks to return

        Returns:
            Formatted context about the customer
        """
        # Search with customer name as query and filter
        results = self.search(
            query=f"{customer_name} interview insights",
            top_k=top_k,
            customer_name=customer_name,
            use_reranker=False  # Already filtered
        )

        if not results:
            return f"No information found for customer: {customer_name}"

        # Format
        output = [f"## Customer Context: {customer_name}\n"]

        for result in results:
            meta = result["metadata"]
            output.append(f"### {meta['section_header'] or 'Content'}")
            output.append(f"*From {meta['content_type']}*\n")
            output.append(result["text"])
            output.append("\n---\n")

        return "\n".join(output)

    def list_customers(self) -> list[str]:
        """
        List all customers in the corpus.

        Returns:
            List of unique customer names
        """
        store = VectorStore(
            persist_directory=self._config["storage"]["persist_directory"],
            collection_name=self._config["storage"]["collection_name"]
        )

        all_chunks = store.get_all_chunks()
        customers = set()

        for chunk in all_chunks:
            name = chunk["metadata"].get("customer_name", "Unknown")
            if name and name != "Unknown":
                customers.add(name)

        return sorted(list(customers))

    def list_documents(self) -> list[dict]:
        """
        List all documents in the corpus.

        Returns:
            List of document info dicts
        """
        store = VectorStore(
            persist_directory=self._config["storage"]["persist_directory"],
            collection_name=self._config["storage"]["collection_name"]
        )

        sources = store.get_sources()

        docs = []
        for source in sources:
            path = Path(source)
            docs.append({
                "path": source,
                "filename": path.name,
                "title": path.stem.replace("-", " ").replace("_", " ")
            })

        return docs

    def stats(self) -> dict:
        """
        Get corpus statistics.

        Returns:
            Dict with corpus stats
        """
        store = VectorStore(
            persist_directory=self._config["storage"]["persist_directory"],
            collection_name=self._config["storage"]["collection_name"]
        )

        return store.stats()


# Global instance for MCP tools
_rag_instance = None


def get_rag() -> LegacyAIRAG:
    """Get or create global RAG instance."""
    global _rag_instance
    if _rag_instance is None:
        # Find config file
        config_path = Path(__file__).parent.parent.parent / "config" / "rag_config.yaml"
        if config_path.exists():
            _rag_instance = LegacyAIRAG(str(config_path))
        else:
            _rag_instance = LegacyAIRAG()
    return _rag_instance


# MCP Tool Functions
def search_legacy_corpus(
    query: str,
    top_k: int = 5,
    content_type: str = None,
    customer_name: str = None
) -> str:
    """
    Search the Legacy AI customer discovery corpus.

    This tool searches through customer interviews, analyses,
    and insights to find relevant information.

    Args:
        query: Natural language search query (e.g., "What pain points do customers have with photo organization?")
        top_k: Number of results to return (default: 5)
        content_type: Filter by content type: 'transcript', 'analysis', 'insight', 'guide'
        customer_name: Filter by customer name

    Returns:
        Formatted search results with relevant chunks
    """
    rag = get_rag()
    return rag.search_formatted(
        query=query,
        top_k=top_k,
        content_type=content_type,
        customer_name=customer_name
    )


def get_customer_info(customer_name: str) -> str:
    """
    Get comprehensive information about a specific customer.

    Retrieves all relevant context including interview transcripts,
    analysis, and insights for the specified customer.

    Args:
        customer_name: Name of the customer (e.g., "Ripanshi", "Rob Halpern")

    Returns:
        Formatted customer context
    """
    rag = get_rag()
    return rag.get_customer_context(customer_name)


def list_interview_customers() -> str:
    """
    List all customers who have been interviewed.

    Returns:
        Formatted list of customer names
    """
    rag = get_rag()
    customers = rag.list_customers()

    if not customers:
        return "No customers found in the corpus."

    output = ["## Interviewed Customers\n"]
    for customer in customers:
        output.append(f"- {customer}")

    return "\n".join(output)


def get_corpus_stats() -> str:
    """
    Get statistics about the Legacy AI corpus.

    Returns:
        Formatted corpus statistics
    """
    rag = get_rag()
    stats = rag.stats()

    output = [
        "## Legacy AI Corpus Statistics\n",
        f"- **Total Chunks**: {stats['total_chunks']}",
        f"- **Total Documents**: {stats['total_documents']}",
        f"- **Total Tokens**: {stats['total_tokens']:,}",
        "\n### Content Types:"
    ]

    for ct, count in stats.get("content_types", {}).items():
        output.append(f"- {ct}: {count} chunks")

    return "\n".join(output)


# CLI for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Legacy AI RAG Tools")
    parser.add_argument("command", choices=["search", "customer", "list", "stats"])
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--customer", "-c", help="Customer name")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of results")
    parser.add_argument("--type", "-t", help="Content type filter")

    args = parser.parse_args()

    if args.command == "search":
        if not args.query:
            print("Error: --query required for search")
            exit(1)
        print(search_legacy_corpus(
            query=args.query,
            top_k=args.top_k,
            content_type=args.type,
            customer_name=args.customer
        ))

    elif args.command == "customer":
        if not args.customer:
            print("Error: --customer required")
            exit(1)
        print(get_customer_info(args.customer))

    elif args.command == "list":
        print(list_interview_customers())

    elif args.command == "stats":
        print(get_corpus_stats())
