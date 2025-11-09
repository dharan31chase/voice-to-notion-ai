"""
Notion Page Fetcher Module

Responsibilities:
- Fetch Notion pages by ID
- Convert Notion blocks to markdown
- Save pages as markdown files

Single purpose: READ operations with markdown conversion
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from notion_client import Client

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger

logger = get_logger(__name__)


class NotionPageFetcher:
    """Fetches Notion pages and converts to markdown."""

    def __init__(self, notion_client: Optional[Client] = None):
        """
        Initialize page fetcher.

        Args:
            notion_client: Optional Notion client (creates new if not provided)
        """
        if notion_client:
            self.client = notion_client
        else:
            # Create new client from environment
            token = os.getenv('NOTION_TOKEN')
            if not token:
                raise ValueError("NOTION_TOKEN not found in environment")
            self.client = Client(auth=token)

        logger.debug("NotionPageFetcher initialized")

    def fetch_page(self, page_id: str) -> Dict:
        """
        Fetch page metadata and all blocks.

        Args:
            page_id: Notion page ID (with or without hyphens)

        Returns:
            Dict with page metadata and blocks
        """
        # Clean page ID (remove hyphens if present)
        clean_id = page_id.replace('-', '')

        logger.info(f"Fetching page: {clean_id}")

        try:
            # Get page metadata
            page = self.client.pages.retrieve(page_id=clean_id)

            # Get all blocks (children)
            blocks = self._fetch_blocks_recursive(clean_id)

            # Extract title
            title = self._extract_title(page)

            logger.info(f"✅ Fetched page: '{title}' ({len(blocks)} blocks)")

            return {
                "id": clean_id,
                "title": title,
                "page": page,
                "blocks": blocks
            }

        except Exception as e:
            logger.error(f"❌ Failed to fetch page {clean_id}: {e}")
            raise

    def _fetch_blocks_recursive(self, block_id: str, level: int = 0) -> List[Dict]:
        """
        Recursively fetch all blocks and their children.

        Args:
            block_id: Block or page ID
            level: Current nesting level (for logging)

        Returns:
            List of block dictionaries with nested children
        """
        blocks = []
        has_more = True
        start_cursor = None

        while has_more:
            response = self.client.blocks.children.list(
                block_id=block_id,
                start_cursor=start_cursor,
                page_size=100
            )

            for block in response['results']:
                # Check if block has children
                if block.get('has_children', False):
                    # Recursively fetch children
                    block['children'] = self._fetch_blocks_recursive(
                        block['id'],
                        level + 1
                    )

                blocks.append(block)

            has_more = response.get('has_more', False)
            start_cursor = response.get('next_cursor')

        logger.debug(f"  {'  ' * level}Fetched {len(blocks)} blocks at level {level}")
        return blocks

    def _extract_title(self, page: Dict) -> str:
        """
        Extract page title from page metadata.

        Args:
            page: Page metadata dict

        Returns:
            Page title string
        """
        try:
            # Try to get title from properties
            properties = page.get('properties', {})

            # Look for title property (could be 'Name' or 'title')
            for prop_name, prop_value in properties.items():
                if prop_value.get('type') == 'title':
                    title_array = prop_value.get('title', [])
                    if title_array:
                        return title_array[0].get('plain_text', 'Untitled')

            # Fallback to page ID if no title found
            return f"Page {page['id'][:8]}"

        except Exception as e:
            logger.warning(f"Failed to extract title: {e}")
            return "Untitled"

    def blocks_to_markdown(self, blocks: List[Dict], level: int = 0) -> str:
        """
        Convert Notion blocks to markdown.

        Args:
            blocks: List of Notion block dictionaries
            level: Current nesting level (for indentation)

        Returns:
            Markdown string
        """
        markdown = []

        for block in blocks:
            block_type = block.get('type')

            if block_type == 'heading_1':
                text = self._extract_rich_text(block['heading_1'])
                markdown.append(f"# {text}\n")

            elif block_type == 'heading_2':
                text = self._extract_rich_text(block['heading_2'])
                markdown.append(f"## {text}\n")

            elif block_type == 'heading_3':
                text = self._extract_rich_text(block['heading_3'])
                markdown.append(f"### {text}\n")

            elif block_type == 'paragraph':
                text = self._extract_rich_text(block['paragraph'])
                if text:  # Only add non-empty paragraphs
                    markdown.append(f"{text}\n")

            elif block_type == 'bulleted_list_item':
                text = self._extract_rich_text(block['bulleted_list_item'])
                indent = "  " * level
                markdown.append(f"{indent}- {text}\n")

                # Handle nested children
                if 'children' in block:
                    child_md = self.blocks_to_markdown(block['children'], level + 1)
                    markdown.append(child_md)

            elif block_type == 'numbered_list_item':
                text = self._extract_rich_text(block['numbered_list_item'])
                indent = "  " * level
                markdown.append(f"{indent}1. {text}\n")

                # Handle nested children
                if 'children' in block:
                    child_md = self.blocks_to_markdown(block['children'], level + 1)
                    markdown.append(child_md)

            elif block_type == 'code':
                code_data = block['code']
                language = code_data.get('language', '')
                code_text = self._extract_rich_text(code_data)
                markdown.append(f"```{language}\n{code_text}\n```\n")

            elif block_type == 'callout':
                text = self._extract_rich_text(block['callout'])
                markdown.append(f"> {text}\n")

            elif block_type == 'quote':
                text = self._extract_rich_text(block['quote'])
                markdown.append(f"> {text}\n")

            elif block_type == 'divider':
                markdown.append("---\n")

            else:
                # Log unsupported block types but don't fail
                logger.debug(f"Unsupported block type: {block_type}")

        return '\n'.join(markdown)

    def _extract_rich_text(self, block_content: Dict) -> str:
        """
        Extract plain text from Notion rich text array.

        Args:
            block_content: Block content dict with rich_text array

        Returns:
            Plain text string
        """
        rich_text_array = block_content.get('rich_text', [])
        return ''.join([rt.get('plain_text', '') for rt in rich_text_array])

    def save_page_as_markdown(
        self,
        page_id: str,
        output_dir: str = "docs/context",
        filename: Optional[str] = None
    ) -> str:
        """
        Fetch page and save as markdown file.

        Args:
            page_id: Notion page ID
            output_dir: Output directory (default: docs/context)
            filename: Optional filename (uses page title if not provided)

        Returns:
            Path to saved markdown file
        """
        # Fetch page
        page_data = self.fetch_page(page_id)

        # Convert to markdown
        markdown = f"# {page_data['title']}\n\n"
        markdown += self.blocks_to_markdown(page_data['blocks'])

        # Determine filename
        if not filename:
            # Sanitize title for filename
            safe_title = "".join(c for c in page_data['title'] if c.isalnum() or c in (' ', '-', '_'))
            safe_title = safe_title.replace(' ', '-').lower()
            filename = f"{safe_title}.md"

        # Ensure output directory exists
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Write markdown file
        file_path = output_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        logger.info(f"✅ Saved markdown: {file_path}")
        return str(file_path)


def get_page_fetcher(notion_client: Optional[Client] = None) -> NotionPageFetcher:
    """
    Factory function to create NotionPageFetcher.

    Args:
        notion_client: Optional Notion client instance

    Returns:
        NotionPageFetcher instance
    """
    return NotionPageFetcher(notion_client)
