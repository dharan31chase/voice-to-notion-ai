#!/usr/bin/env python3
"""
Fetch a specific Notion page by URL and convert to markdown.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
import re

# Load environment
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def extract_page_id_from_url(url: str) -> str:
    """Extract page ID from Notion URL."""
    # Notion URLs format: https://www.notion.so/Page-Title-27d8369c73058050be08e48a21c629b7
    match = re.search(r'([a-f0-9]{32})', url)
    if match:
        raw_id = match.group(1)
        # Format with hyphens: 8-4-4-4-12
        return f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"
    return url

def get_page_title(page_id: str) -> str:
    """Get page title."""
    try:
        page = notion.pages.retrieve(page_id=page_id)
        props = page.get("properties", {})

        # Try different title property names
        for prop_name in ["title", "Name", "Title"]:
            if prop_name in props:
                title_prop = props[prop_name]
                if title_prop.get("type") == "title" and title_prop.get("title"):
                    return title_prop["title"][0]["text"]["content"]

        return "Untitled"
    except Exception as e:
        print(f"Error getting title: {e}")
        return "Untitled"

def get_page_content(page_id: str):
    """Fetch page content (blocks)."""
    try:
        blocks = []
        has_more = True
        start_cursor = None

        while has_more:
            response = notion.blocks.children.list(
                block_id=page_id,
                start_cursor=start_cursor,
                page_size=100
            )
            blocks.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return blocks
    except Exception as e:
        print(f"Error fetching content: {e}")
        return []

def extract_rich_text(rich_text_array):
    """Extract plain text from rich text array."""
    if not rich_text_array:
        return ""
    return "".join([rt.get("plain_text", "") for rt in rich_text_array])

def block_to_markdown(block, indent_level=0):
    """Convert a Notion block to markdown."""
    block_type = block.get("type")
    indent = "  " * indent_level

    if block_type == "paragraph":
        text = extract_rich_text(block["paragraph"].get("rich_text", []))
        return f"{text}\n\n" if text else ""

    elif block_type == "heading_1":
        text = extract_rich_text(block["heading_1"].get("rich_text", []))
        return f"# {text}\n\n"

    elif block_type == "heading_2":
        text = extract_rich_text(block["heading_2"].get("rich_text", []))
        return f"## {text}\n\n"

    elif block_type == "heading_3":
        text = extract_rich_text(block["heading_3"].get("rich_text", []))
        return f"### {text}\n\n"

    elif block_type == "bulleted_list_item":
        text = extract_rich_text(block["bulleted_list_item"].get("rich_text", []))
        return f"{indent}- {text}\n"

    elif block_type == "numbered_list_item":
        text = extract_rich_text(block["numbered_list_item"].get("rich_text", []))
        return f"{indent}1. {text}\n"

    elif block_type == "code":
        text = extract_rich_text(block["code"].get("rich_text", []))
        language = block["code"].get("language", "")
        return f"```{language}\n{text}\n```\n\n"

    elif block_type == "quote":
        text = extract_rich_text(block["quote"].get("rich_text", []))
        return f"> {text}\n\n"

    elif block_type == "divider":
        return "---\n\n"

    elif block_type == "callout":
        text = extract_rich_text(block["callout"].get("rich_text", []))
        return f"> {text}\n\n"

    elif block_type == "toggle":
        text = extract_rich_text(block["toggle"].get("rich_text", []))
        return f"**{text}**\n\n"

    else:
        return ""

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetch_notion_page.py <notion_url>")
        sys.exit(1)

    url = sys.argv[1]
    page_id = extract_page_id_from_url(url)

    print(f"Fetching page: {page_id}")
    title = get_page_title(page_id)
    print(f"Title: {title}")

    blocks = get_page_content(page_id)
    print(f"Found {len(blocks)} blocks")

    if blocks:
        markdown = f"# {title}\n\n**Source**: {url}\n\n---\n\n"
        for block in blocks:
            markdown += block_to_markdown(block)

        print(markdown)

if __name__ == "__main__":
    main()
