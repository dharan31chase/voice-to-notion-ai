"""
RAG Implementation for Legacy AI Customer Discovery

Hybrid RAG system with BM25 + semantic embeddings + BGE local re-ranking.
Enables instant search across all customer interviews in <1 second.

Modules:
    - chunker: Document chunking with header-based splitting
    - embeddings: OpenAI embedding generation with caching
    - storage: Chroma vector store wrapper
    - bm25_index: BM25 keyword search index
    - searcher: Hybrid search with Reciprocal Rank Fusion
    - reranker: BGE local re-ranking
    - indexer: Full indexing pipeline orchestration
    - mcp_tools: MCP tool wrappers for Claude Desktop
"""

__version__ = "0.1.0"
