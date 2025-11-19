"""
Document Chunker for Legacy AI RAG

Header-based chunking with overlap for markdown documents.
Preserves semantic structure and extracts rich metadata.
"""

import re
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import tiktoken


@dataclass
class ChunkMetadata:
    """Metadata for a document chunk."""
    # Source identification
    source_file: str
    document_title: str

    # Position in document
    section_header: str
    section_hierarchy: list[str]
    chunk_index: int

    # Content type
    content_type: str  # transcript, analysis, insight, guide
    customer_name: str

    # Timestamps
    file_modified: str
    indexed_at: str = ""

    # Technical
    token_count: int = 0
    char_count: int = 0
    has_overlap: bool = False
    content_hash: str = ""


@dataclass
class Chunk:
    """A document chunk with text and metadata."""
    id: str
    text: str
    metadata: ChunkMetadata

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "text": self.text,
            **{k: v for k, v in self.metadata.__dict__.items()}
        }


class DocumentChunker:
    """
    Chunk markdown documents by headers with overlap.

    Strategy:
    1. Split at header boundaries (##, ###)
    2. If chunk > max_tokens, split by paragraphs
    3. Add overlap from previous chunk
    4. Extract rich metadata
    """

    def __init__(
        self,
        max_chunk_tokens: int = 2000,
        min_chunk_tokens: int = 100,
        overlap_tokens: int = 200,
        header_levels: list[str] = None
    ):
        self.max_chunk_tokens = max_chunk_tokens
        self.min_chunk_tokens = min_chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.header_levels = header_levels or ["#", "##", "###"]
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))

    def chunk_document(self, file_path: str) -> list[Chunk]:
        """
        Chunk a document file into searchable chunks.

        Args:
            file_path: Path to markdown file

        Returns:
            List of Chunk objects with text and metadata
        """
        path = Path(file_path).expanduser()

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        # Read document
        content = path.read_text(encoding="utf-8")

        # Extract document-level metadata
        doc_title = self._extract_title(content, path)
        content_type = self._detect_content_type(str(path))
        customer_name = self._extract_customer_name(str(path), content)
        file_modified = path.stat().st_mtime

        # Split by headers
        sections = self._split_by_headers(content)

        # Process each section into chunks
        chunks = []
        previous_overlap = ""

        for section_idx, (header, section_text, hierarchy) in enumerate(sections):
            # Split large sections by paragraphs
            section_chunks = self._split_section(section_text, header)

            for chunk_idx, chunk_text in enumerate(section_chunks):
                # Add overlap from previous chunk
                if previous_overlap and chunk_idx == 0:
                    full_text = previous_overlap + "\n\n" + chunk_text
                    has_overlap = True
                else:
                    full_text = chunk_text
                    has_overlap = False

                # Skip tiny chunks
                token_count = self.count_tokens(full_text)
                if token_count < self.min_chunk_tokens and section_idx < len(sections) - 1:
                    # Merge with next section instead
                    previous_overlap = full_text
                    continue

                # Create chunk ID
                chunk_id = self._generate_chunk_id(str(path), section_idx, chunk_idx)

                # Create metadata
                metadata = ChunkMetadata(
                    source_file=str(path),
                    document_title=doc_title,
                    section_header=header,
                    section_hierarchy=hierarchy,
                    chunk_index=len(chunks),
                    content_type=content_type,
                    customer_name=customer_name,
                    file_modified=str(file_modified),
                    token_count=token_count,
                    char_count=len(full_text),
                    has_overlap=has_overlap,
                    content_hash=hashlib.sha256(full_text.encode()).hexdigest()[:16]
                )

                chunks.append(Chunk(
                    id=chunk_id,
                    text=full_text,
                    metadata=metadata
                ))

                # Prepare overlap for next chunk
                previous_overlap = self._get_overlap_text(chunk_text)

        return chunks

    def _split_by_headers(self, content: str) -> list[tuple[str, str, list[str]]]:
        """
        Split content by markdown headers.

        Returns:
            List of (header, text, hierarchy) tuples
        """
        # Build regex pattern for headers
        # Match ## or ### at start of line
        pattern = r'^(#{1,3})\s+(.+)$'

        sections = []
        current_header = ""
        current_text = []
        hierarchy = []

        lines = content.split('\n')

        for line in lines:
            match = re.match(pattern, line)

            if match:
                # Save previous section
                if current_text or current_header:
                    sections.append((
                        current_header,
                        '\n'.join(current_text).strip(),
                        hierarchy.copy()
                    ))

                # Start new section
                level = len(match.group(1))
                header_text = match.group(2).strip()
                current_header = f"{'#' * level} {header_text}"
                current_text = []

                # Update hierarchy
                if level == 1:
                    hierarchy = [header_text]
                elif level == 2:
                    hierarchy = hierarchy[:1] + [header_text] if hierarchy else [header_text]
                elif level == 3:
                    hierarchy = hierarchy[:2] + [header_text] if len(hierarchy) >= 2 else hierarchy + [header_text]
            else:
                current_text.append(line)

        # Don't forget last section
        if current_text or current_header:
            sections.append((
                current_header,
                '\n'.join(current_text).strip(),
                hierarchy.copy()
            ))

        # Handle documents with no headers
        if not sections:
            sections = [("", content.strip(), [])]

        return sections

    def _split_section(self, text: str, header: str) -> list[str]:
        """
        Split a section if it exceeds max tokens.

        Strategy:
        1. If under max, return as-is
        2. Split by paragraphs (double newline)
        3. Merge small paragraphs, split large ones
        """
        # Include header in first chunk
        full_text = f"{header}\n\n{text}" if header else text

        if self.count_tokens(full_text) <= self.max_chunk_tokens:
            return [full_text]

        # Split by paragraphs
        paragraphs = re.split(r'\n\n+', text)

        chunks = []
        current_chunk = header + "\n\n" if header else ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if adding this paragraph exceeds limit
            test_chunk = current_chunk + para + "\n\n"

            if self.count_tokens(test_chunk) > self.max_chunk_tokens:
                # Save current chunk if it has content
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Start new chunk with this paragraph
                if self.count_tokens(para) > self.max_chunk_tokens:
                    # Paragraph itself is too large, split by sentences
                    sentence_chunks = self._split_by_sentences(para)
                    chunks.extend(sentence_chunks[:-1])
                    current_chunk = sentence_chunks[-1] + "\n\n" if sentence_chunks else ""
                else:
                    current_chunk = para + "\n\n"
            else:
                current_chunk = test_chunk

        # Don't forget last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [full_text]

    def _split_by_sentences(self, text: str) -> list[str]:
        """Split text by sentences for very long paragraphs."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current = ""

        for sentence in sentences:
            test = current + " " + sentence if current else sentence

            if self.count_tokens(test) > self.max_chunk_tokens and current:
                chunks.append(current.strip())
                current = sentence
            else:
                current = test

        if current:
            chunks.append(current.strip())

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """Extract overlap text from end of chunk."""
        tokens = self.tokenizer.encode(text)

        if len(tokens) <= self.overlap_tokens:
            return text

        # Get last N tokens
        overlap_tokens = tokens[-self.overlap_tokens:]
        return self.tokenizer.decode(overlap_tokens)

    def _extract_title(self, content: str, path: Path) -> str:
        """Extract document title from content or filename."""
        # Try to find # Title
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Fall back to filename
        return path.stem.replace("-", " ").replace("_", " ")

    def _detect_content_type(self, file_path: str) -> str:
        """Detect content type from file path."""
        path_lower = file_path.lower()

        if "transcript" in path_lower:
            return "transcript"
        elif "analys" in path_lower:
            return "analysis"
        elif "insight" in path_lower:
            return "insight"
        elif "guide" in path_lower:
            return "guide"
        elif "template" in path_lower:
            return "template"
        else:
            return "other"

    def _extract_customer_name(self, file_path: str, content: str) -> str:
        """Extract customer name from filename or content."""
        path = Path(file_path)
        filename = path.stem

        # Pattern: "Interview Transcript Suzy Somers"
        match = re.search(r'Interview\s+Transcript\s+(.+)', filename, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Pattern: "2025-ripanshi" or "2025-suzy-somers"
        match = re.search(r'^\d{4}-(.+)$', filename)
        if match:
            name = match.group(1).replace("-", " ").replace("_", " ")
            return name.title()

        # Try to extract from content (first mention after "Interview with")
        match = re.search(r'Interview\s+with\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', content)
        if match:
            return match.group(1)

        return "Unknown"

    def _generate_chunk_id(self, file_path: str, section_idx: int, chunk_idx: int) -> str:
        """Generate unique chunk ID."""
        # Use file path hash + indices
        path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        return f"{path_hash}_{section_idx:03d}_{chunk_idx:03d}"


# Convenience function
def chunk_document(file_path: str, **kwargs) -> list[Chunk]:
    """Chunk a document with default settings."""
    chunker = DocumentChunker(**kwargs)
    return chunker.chunk_document(file_path)
