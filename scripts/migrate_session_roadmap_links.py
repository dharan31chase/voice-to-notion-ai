#!/usr/bin/env python3
"""
One-time migration script: Link existing sessions to roadmap items

This script retroactively adds Roadmap relations to Sessions that were created
before the linking feature was implemented.

Usage:
    python3 scripts/migrate_session_roadmap_links.py [--dry-run] [--since YYYY-MM-DD]
"""

import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from notion_client import Client
from core.logging_utils import get_logger

logger = get_logger(__name__)

# Notion database IDs
ROADMAP_DB_ID = os.getenv("NOTION_ROADMAP_DB")
SESSIONS_DB_ID = os.getenv("NOTION_SESSIONS_DB")


class SessionRoadmapMigrator:
    """Migrates existing sessions to link to roadmap items."""

    def __init__(self, dry_run: bool = False):
        """Initialize migrator."""
        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ValueError("NOTION_TOKEN not found in environment")

        self.notion_client = Client(auth=notion_token)
        self.dry_run = dry_run

        if not ROADMAP_DB_ID or not SESSIONS_DB_ID:
            raise ValueError("NOTION_ROADMAP_DB and NOTION_SESSIONS_DB must be set")

        logger.info("=" * 60)
        logger.info("SESSION → ROADMAP MIGRATION")
        logger.info("=" * 60)
        logger.info(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will update Notion)'}")
        logger.info("")

    def extract_roadmap_refs(self, text: str) -> list[str]:
        """Extract [ROADMAP-X] references from text."""
        pattern = r"\[ROADMAP-(\d+)\]"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches

    def find_roadmap_page_id(self, item_id: str) -> str | None:
        """Find Notion page ID for a roadmap item."""
        try:
            query_response = self.notion_client.databases.query(
                database_id=ROADMAP_DB_ID,
                filter={
                    "property": "Roadmap ID",
                    "rich_text": {
                        "equals": f"ROADMAP-{item_id}"
                    }
                }
            )

            if query_response["results"]:
                page_id = query_response["results"][0]["id"]
                feature_name = query_response["results"][0]["properties"]["Feature Name"]["title"][0]["text"]["content"]
                logger.info(f"  Found: ROADMAP-{item_id} = '{feature_name}'")
                return page_id
            else:
                logger.warning(f"  Not found: ROADMAP-{item_id}")
                return None

        except Exception as e:
            logger.error(f"  Error finding ROADMAP-{item_id}: {e}")
            return None

    def get_sessions_to_migrate(self, since_date: str | None = None) -> list[dict]:
        """Get all sessions that need migration."""
        logger.info("Fetching sessions from Notion...")

        filters = []
        if since_date:
            filters.append({
                "property": "Session Date",
                "date": {
                    "on_or_after": since_date
                }
            })

        query_params = {"database_id": SESSIONS_DB_ID}
        if filters:
            query_params["filter"] = {"and": filters} if len(filters) > 1 else filters[0]

        sessions = []
        has_more = True
        next_cursor = None

        while has_more:
            if next_cursor:
                query_params["start_cursor"] = next_cursor

            response = self.notion_client.databases.query(**query_params)
            sessions.extend(response["results"])
            has_more = response["has_more"]
            next_cursor = response.get("next_cursor")

        logger.info(f"Found {len(sessions)} sessions\n")
        return sessions

    def migrate_session(self, session: dict) -> dict:
        """Migrate a single session to link to roadmap items."""
        session_id = session["id"]
        session_title = session["properties"]["Title"]["title"][0]["text"]["content"] if session["properties"]["Title"]["title"] else "Untitled"

        # Get "What Shipped" content
        what_shipped_prop = session["properties"].get("What Shipped", {})
        what_shipped_text = ""
        if what_shipped_prop.get("rich_text"):
            what_shipped_text = what_shipped_prop["rich_text"][0]["text"]["content"]

        # Check if already has Roadmap relation
        existing_relations = session["properties"].get("Roadmap", {}).get("relation", [])
        if existing_relations:
            logger.info(f"⏭️  SKIP: '{session_title}' (already has {len(existing_relations)} relation(s))")
            return {
                "session_id": session_id,
                "session_title": session_title,
                "status": "skipped",
                "reason": "already_linked"
            }

        # Extract roadmap references
        roadmap_refs = self.extract_roadmap_refs(what_shipped_text)
        if not roadmap_refs:
            logger.info(f"⏭️  SKIP: '{session_title}' (no ROADMAP references)")
            return {
                "session_id": session_id,
                "session_title": session_title,
                "status": "skipped",
                "reason": "no_roadmap_refs"
            }

        logger.info(f"📝 '{session_title}'")
        logger.info(f"  Found references: {roadmap_refs}")

        # Find roadmap page IDs
        roadmap_page_ids = []
        for item_id in roadmap_refs:
            page_id = self.find_roadmap_page_id(item_id)
            if page_id:
                roadmap_page_ids.append(page_id)

        if not roadmap_page_ids:
            logger.warning(f"⚠️  WARNING: No valid roadmap items found for '{session_title}'")
            return {
                "session_id": session_id,
                "session_title": session_title,
                "status": "warning",
                "reason": "roadmap_items_not_found"
            }

        # Update session with roadmap relations
        if self.dry_run:
            logger.info(f"  [DRY RUN] Would link to {len(roadmap_page_ids)} roadmap item(s)")
            return {
                "session_id": session_id,
                "session_title": session_title,
                "status": "dry_run",
                "roadmap_ids": roadmap_refs
            }
        else:
            try:
                self.notion_client.pages.update(
                    page_id=session_id,
                    properties={
                        "Roadmap": {
                            "relation": [{"id": page_id} for page_id in roadmap_page_ids]
                        }
                    }
                )
                logger.info(f"  ✅ Linked to {len(roadmap_page_ids)} roadmap item(s)")
                return {
                    "session_id": session_id,
                    "session_title": session_title,
                    "status": "success",
                    "roadmap_ids": roadmap_refs
                }
            except Exception as e:
                logger.error(f"  ❌ Error updating: {e}")
                return {
                    "session_id": session_id,
                    "session_title": session_title,
                    "status": "error",
                    "error": str(e)
                }

    def run_migration(self, since_date: str | None = None):
        """Run the full migration."""
        sessions = self.get_sessions_to_migrate(since_date)

        results = {
            "total": len(sessions),
            "success": 0,
            "skipped": 0,
            "warning": 0,
            "error": 0,
            "dry_run": 0
        }

        for session in sessions:
            result = self.migrate_session(session)
            results[result["status"]] += 1
            logger.info("")  # Blank line between sessions

        # Print summary
        logger.info("=" * 60)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total sessions: {results['total']}")
        logger.info(f"✅ Success: {results['success']}")
        logger.info(f"⏭️  Skipped: {results['skipped']}")
        logger.info(f"⚠️  Warnings: {results['warning']}")
        logger.info(f"❌ Errors: {results['error']}")
        if self.dry_run:
            logger.info(f"🔍 Dry run: {results['dry_run']}")
        logger.info("")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Migrate sessions to link to roadmap items")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--since",
        type=str,
        help="Only migrate sessions since this date (YYYY-MM-DD)"
    )

    args = parser.parse_args()

    try:
        migrator = SessionRoadmapMigrator(dry_run=args.dry_run)
        migrator.run_migration(since_date=args.since)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
