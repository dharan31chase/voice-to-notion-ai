"""
Vector Storage for Legacy AI RAG

Chroma vector database wrapper for storing and querying embeddings.
"""

from pathlib import Path
from typing import Optional
import structlog
import chromadb
from chromadb.config import Settings

from .chunker import Chunk

logger = structlog.get_logger()


class VectorStore:
    """
    Chroma vector store for document embeddings.

    Features:
    - Persistent storage
    - Metadata filtering
    - Similarity search
    - Incremental updates
    """

    def __init__(
        self,
        persist_directory: str = "~/.cache/legacy-ai-rag/chroma",
        collection_name: str = "legacy_ai_interviews"
    ):
        self.persist_directory = Path(persist_directory).expanduser()
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name

        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        logger.info("vector_store_initialized",
            persist_dir=str(self.persist_directory),
            collection=collection_name,
            count=self.collection.count()
        )

    def add(self, chunks: list[Chunk], embeddings: list[list[float]]):
        """
        Add chunks with embeddings to the store.

        Args:
            chunks: Document chunks with metadata
            embeddings: Corresponding embedding vectors
        """
        if not chunks:
            return

        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) must match")

        # Prepare data for Chroma
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = []

        for chunk in chunks:
            # Convert metadata to dict, ensuring all values are strings/ints/floats
            meta = {
                "source_file": chunk.metadata.source_file,
                "document_title": chunk.metadata.document_title,
                "section_header": chunk.metadata.section_header,
                "section_hierarchy": "|".join(chunk.metadata.section_hierarchy),
                "chunk_index": chunk.metadata.chunk_index,
                "content_type": chunk.metadata.content_type,
                "customer_name": chunk.metadata.customer_name,
                "file_modified": chunk.metadata.file_modified,
                "indexed_at": chunk.metadata.indexed_at,
                "token_count": chunk.metadata.token_count,
                "char_count": chunk.metadata.char_count,
                "has_overlap": chunk.metadata.has_overlap,
                "content_hash": chunk.metadata.content_hash
            }
            metadatas.append(meta)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        logger.info("chunks_added",
            count=len(chunks),
            total=self.collection.count()
        )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 10,
        where: dict = None,
        include_embeddings: bool = False
    ) -> list[dict]:
        """
        Query for similar documents.

        Args:
            query_embedding: Query vector
            n_results: Number of results to return
            where: Metadata filter (e.g., {"content_type": "transcript"})
            include_embeddings: Whether to include embeddings in results

        Returns:
            List of result dicts with id, text, metadata, distance
        """
        includes = ["documents", "metadatas", "distances"]
        if include_embeddings:
            includes.append("embeddings")

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=includes
        )

        # Format results
        formatted = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                }
                if include_embeddings:
                    result["embedding"] = results["embeddings"][0][i]
                formatted.append(result)

        return formatted

    def get_by_id(self, chunk_id: str) -> Optional[dict]:
        """Get a specific chunk by ID."""
        result = self.collection.get(
            ids=[chunk_id],
            include=["documents", "metadatas"]
        )

        if result["ids"]:
            return {
                "id": result["ids"][0],
                "text": result["documents"][0],
                "metadata": result["metadatas"][0]
            }
        return None

    def get_by_ids(self, chunk_ids: list[str]) -> list[dict]:
        """Get multiple chunks by IDs."""
        result = self.collection.get(
            ids=chunk_ids,
            include=["documents", "metadatas"]
        )

        formatted = []
        for i in range(len(result["ids"])):
            formatted.append({
                "id": result["ids"][i],
                "text": result["documents"][i],
                "metadata": result["metadatas"][i]
            })
        return formatted

    def delete_by_source(self, source_file: str):
        """Delete all chunks from a source file."""
        # Get IDs to delete
        results = self.collection.get(
            where={"source_file": source_file},
            include=[]
        )

        if results["ids"]:
            self.collection.delete(ids=results["ids"])
            logger.info("chunks_deleted",
                source=source_file,
                count=len(results["ids"])
            )

    def delete_by_ids(self, chunk_ids: list[str]):
        """Delete chunks by IDs."""
        if chunk_ids:
            self.collection.delete(ids=chunk_ids)
            logger.info("chunks_deleted_by_id", count=len(chunk_ids))

    def get_all_chunks(self) -> list[dict]:
        """Get all chunks in the store."""
        result = self.collection.get(
            include=["documents", "metadatas"]
        )

        formatted = []
        for i in range(len(result["ids"])):
            formatted.append({
                "id": result["ids"][i],
                "text": result["documents"][i],
                "metadata": result["metadatas"][i]
            })
        return formatted

    def get_sources(self) -> list[str]:
        """Get list of all source files in the store."""
        all_chunks = self.collection.get(include=["metadatas"])
        sources = set()
        for meta in all_chunks["metadatas"]:
            sources.add(meta["source_file"])
        return sorted(list(sources))

    def count(self) -> int:
        """Get total number of chunks."""
        return self.collection.count()

    def clear(self):
        """Clear all data from the store."""
        # Delete and recreate collection
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("vector_store_cleared")

    def stats(self) -> dict:
        """Get store statistics."""
        all_chunks = self.collection.get(include=["metadatas"])

        sources = set()
        content_types = {}
        total_tokens = 0

        for meta in all_chunks["metadatas"]:
            sources.add(meta["source_file"])
            ct = meta.get("content_type", "other")
            content_types[ct] = content_types.get(ct, 0) + 1
            total_tokens += meta.get("token_count", 0)

        return {
            "total_chunks": self.collection.count(),
            "total_documents": len(sources),
            "total_tokens": total_tokens,
            "content_types": content_types
        }
