#!/usr/bin/env python3
"""
Fetch Legacy AI documents from Notion for migration to legacy-ai repo.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client

# Load environment
load_dotenv()

# Initialize Notion client
notion = Client(auth=os.getenv("NOTION_TOKEN"))

# Documents to fetch (search by title)
DOCUMENTS_TO_FETCH = [
    "Customer Interview Analysis: Uncle Bob & Aunt Missy",
    "Carrie Esker Interview",
    "Interview Guide: Aunt Missy & Uncle Bob",
    "Legacy AI: Technical Feasibility Analysis 2024-2025",
    "Legacy AI Interview Question Bank",
    "Legacy AI – Customer Interview Analysis: [NAME]",
    "Requirements & Vision",
    "Legacy AI - Product Strategy"
]

def search_notion_page(query: str):
    """Search for a page by title."""
    try:
        response = notion.search(
            query=query,
            filter={"property": "object", "value": "page"},
            page_size=10
        )

        results = response.get("results", [])
        if results:
            for result in results:
                title_prop = result.get("properties", {}).get("title", {}) or result.get("properties", {}).get("Name", {})
                if title_prop:
                    if title_prop.get("type") == "title" and title_prop.get("title"):
                        title = title_prop["title"][0]["text"]["content"]
                        print(f"  Found: {title}")
                        print(f"    ID: {result['id']}")
                        print(f"    URL: {result['url']}")
                        return result
        return None
    except Exception as e:
        print(f"  Error searching: {e}")
        return None

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
        print(f"  Error fetching content: {e}")
        return []

def block_to_markdown(block):
    """Convert a Notion block to markdown."""
    block_type = block.get("type")

    if block_type == "paragraph":
        text = extract_rich_text(block["paragraph"].get("rich_text", []))
        return text + "\n\n"

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
        return f"- {text}\n"

    elif block_type == "numbered_list_item":
        text = extract_rich_text(block["numbered_list_item"].get("rich_text", []))
        return f"1. {text}\n"

    elif block_type == "code":
        text = extract_rich_text(block["code"].get("rich_text", []))
        language = block["code"].get("language", "")
        return f"```{language}\n{text}\n```\n\n"

    elif block_type == "quote":
        text = extract_rich_text(block["quote"].get("rich_text", []))
        return f"> {text}\n\n"

    elif block_type == "divider":
        return "---\n\n"

    else:
        # Unsupported block type - return empty
        return ""

def extract_rich_text(rich_text_array):
    """Extract plain text from rich text array."""
    return "".join([rt.get("plain_text", "") for rt in rich_text_array])

def main():
    print("Searching for Legacy AI documents in Notion...\n")

    found_docs = {}

    for doc_query in DOCUMENTS_TO_FETCH:
        print(f"Searching for: {doc_query}")
        result = search_notion_page(doc_query)

        if result:
            page_id = result["id"]
            title_prop = result.get("properties", {}).get("title", {}) or result.get("properties", {}).get("Name", {})
            if title_prop and title_prop.get("title"):
                title = title_prop["title"][0]["text"]["content"]
                found_docs[title] = {
                    "id": page_id,
                    "url": result["url"],
                    "query": doc_query
                }
        else:
            print(f"  ⚠️  Not found\n")
        print()

    print(f"\n{'='*60}")
    print(f"Found {len(found_docs)} out of {len(DOCUMENTS_TO_FETCH)} documents")
    print(f"{'='*60}\n")

    # Fetch content for each found document
    for title, info in found_docs.items():
        print(f"Fetching content for: {title}")
        blocks = get_page_content(info["id"])

        if blocks:
            # Convert to markdown
            markdown = f"# {title}\n\n"
            markdown += f"**Source**: {info['url']}\n\n"
            markdown += "---\n\n"

            for block in blocks:
                markdown += block_to_markdown(block)

            # Save to file for manual review
            output_file = Path.home() / "Desktop" / f"{title.replace('/', '-')}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            print(f"  ✓ Saved to: {output_file}")
        else:
            print(f"  ⚠️  No content found")
        print()

if __name__ == "__main__":
    main()
