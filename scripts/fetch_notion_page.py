#!/usr/bin/env python3
"""
CLI tool to fetch Notion pages as markdown.

Usage:
    python scripts/fetch_notion_page.py <page_id> [--output path]
    python scripts/fetch_notion_page.py 2a58369c73058079a356cbf2dd2d86bc
    python scripts/fetch_notion_page.py 2a58369c73058079a356cbf2dd2d86bc --output docs/roadmap.md
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Load environment variables
load_dotenv()

from scripts.notion.page_fetcher import NotionPageFetcher
from core.logging_utils import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch Notion page and convert to markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch page to docs/context/ (auto-named from title)
  python scripts/fetch_notion_page.py 2a58369c73058079a356cbf2dd2d86bc

  # Fetch page with custom output path
  python scripts/fetch_notion_page.py 2a58369c73058079a356cbf2dd2d86bc --output docs/roadmap.md

  # Fetch with custom output directory
  python scripts/fetch_notion_page.py 2a58369c73058079a356cbf2dd2d86bc --output-dir docs/plans
        """
    )

    parser.add_argument(
        'page_id',
        help='Notion page ID (with or without hyphens)'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Output file path (overrides --output-dir)'
    )

    parser.add_argument(
        '--output-dir',
        '-d',
        default='docs/context',
        help='Output directory (default: docs/context)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Set log level
    if args.verbose:
        from core.logging_utils import set_log_level
        set_log_level(logger, "DEBUG")

    try:
        # Create fetcher
        fetcher = NotionPageFetcher()

        # Fetch and save
        if args.output:
            # Custom output path provided
            output_path = Path(args.output)
            output_dir = str(output_path.parent)
            filename = output_path.name

            file_path = fetcher.save_page_as_markdown(
                args.page_id,
                output_dir=output_dir,
                filename=filename
            )
        else:
            # Use output directory with auto-generated filename
            file_path = fetcher.save_page_as_markdown(
                args.page_id,
                output_dir=args.output_dir
            )

        print(f"\n✅ Success! Markdown saved to: {file_path}\n")

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
