#!/usr/bin/env python3
"""
Notion Sync Script

Syncs git commits to Notion databases:
1. Parse commit for roadmap item references
2. Update Roadmap database (status, last updated)
3. Create session log in Sessions database
4. Link to relevant PRD/tech docs

Usage:
    python3 sync_to_notion.py \
      --commit-msg "[ROADMAP-123] Implement feature" \
      --commit-hash "abc123" \
      --commit-author "Dharan" \
      --commit-date "2025-11-08 10:00:00" \
      --files "file1.py,file2.md"
"""

import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Notion client
try:
    from notion_client import Client
    from scripts.notion.notion_client_wrapper import NotionClientWrapper
    from core.config_loader import ConfigLoader
    from core.logging_utils import get_logger
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root and dependencies are installed.")
    sys.exit(1)

logger = get_logger(__name__)

# Notion database IDs (from environment)
ROADMAP_DB_ID = os.getenv("NOTION_ROADMAP_DB")
SESSIONS_DB_ID = os.getenv("NOTION_SESSIONS_DB")
GITHUB_USERNAME = "dharan31chase"  # From git remote


class NotionSyncEngine:
    """Syncs git commits to Notion databases"""

    def __init__(self):
        """Initialize Notion sync engine."""
        # Initialize Notion client
        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ValueError("NOTION_TOKEN not found in environment")

        self.notion_client = Client(auth=notion_token)
        self.wrapper = NotionClientWrapper(self.notion_client)
        self.config = ConfigLoader()

        # Validate database IDs
        if not ROADMAP_DB_ID:
            logger.warning("NOTION_ROADMAP_DB not set - roadmap updates will be skipped")
        if not SESSIONS_DB_ID:
            logger.warning("NOTION_SESSIONS_DB not set - session logging will be skipped")

    def extract_roadmap_refs(self, commit_msg: str) -> List[str]:
        """
        Extract roadmap item references from commit message.

        Format: [ROADMAP-123] or [roadmap-456]

        Args:
            commit_msg: Git commit message

        Returns:
            List of roadmap item IDs
        """
        pattern = r"\[ROADMAP-(\d+)\]"
        matches = re.findall(pattern, commit_msg, re.IGNORECASE)
        return matches

    def update_roadmap_status(
        self,
        item_id: str,
        commit_msg: str,
        commit_hash: str,
        status: str = "In Progress"
    ) -> bool:
        """
        Update roadmap item status in Notion.

        Args:
            item_id: Roadmap item ID (e.g., "123")
            commit_msg: Git commit message
            commit_hash: Git commit hash
            status: Status to set (default: "In Progress")

        Returns:
            True if successful, False otherwise
        """
        if not ROADMAP_DB_ID:
            logger.info("Skipping roadmap update (NOTION_ROADMAP_DB not set)")
            return False

        try:
            # Query for roadmap item with matching ID
            logger.info(f"Searching for ROADMAP-{item_id} in Notion...")

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

                # Update status and last updated date
                self.notion_client.pages.update(
                    page_id=page_id,
                    properties={
                        "Status": {
                            "select": {
                                "name": status
                            }
                        },
                        "Last Updated": {
                            "date": {
                                "start": datetime.now().isoformat()
                            }
                        }
                    }
                )
                logger.info(f"✓ Updated '{feature_name}' (ROADMAP-{item_id}) to '{status}'")
                return True
            else:
                logger.warning(f"✗ Roadmap item ROADMAP-{item_id} not found in Notion")
                logger.warning(f"  Make sure the 'Roadmap ID' property contains 'ROADMAP-{item_id}'")
                return False

        except Exception as e:
            logger.error(f"Error updating roadmap item {item_id}: {e}")
            return False

    def create_session_log(
        self,
        commit_msg: str,
        commit_hash: str,
        commit_author: str,
        commit_date: str,
        files_changed: str,
        agent: str = "Claude Code"
    ) -> Optional[Dict]:
        """
        Create session log entry in Notion.

        Args:
            commit_msg: Git commit message
            commit_hash: Git commit hash
            commit_author: Commit author name
            commit_date: Commit datetime (ISO format)
            files_changed: Comma-separated list of files
            agent: Agent name (default: "Claude Code")

        Returns:
            Dict with Notion page info or None if failed
        """
        if not SESSIONS_DB_ID:
            logger.info("Skipping session log (NOTION_SESSIONS_DB not set)")
            return None

        try:
            # Format title
            date_str = datetime.fromisoformat(commit_date.replace(" ", "T", 1)).strftime("%Y-%m-%d")
            title = f"Session: {date_str} - {agent}"

            # GitHub commit URL
            github_url = f"https://github.com/{GITHUB_USERNAME}/voice-to-notion-ai/commit/{commit_hash}"

            # Format files list for better readability
            files_list = files_changed.strip(",").replace(",", "\n") if files_changed else "No files changed"

            logger.info(f"Creating session log: '{title}'...")

            # Create page in Sessions database
            response = self.wrapper.create_page(
                database_id=SESSIONS_DB_ID,
                properties={
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    },
                    "Agent": {
                        "select": {
                            "name": agent
                        }
                    },
                    "What Shipped": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": commit_msg[:2000]  # Notion limit
                                }
                            }
                        ]
                    },
                    "Git Commit": {
                        "url": github_url
                    },
                    "Session Date": {
                        "date": {
                            "start": commit_date.split()[0]  # Extract date only (YYYY-MM-DD)
                        }
                    },
                    "Project": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": "Epic 2nd Brain Workflow"
                                }
                            }
                        ]
                    }
                }
            )

            if response:
                logger.info(f"✓ Created session log in Notion")
                logger.info(f"  URL: {response.get('url', 'N/A')}")
                return {
                    "url": response.get("url"),
                    "id": response.get("id")
                }
            else:
                logger.error("✗ Failed to create session log")
                return None

        except Exception as e:
            logger.error(f"Error creating session log: {e}")
            return None

    def sync_commit(
        self,
        commit_msg: str,
        commit_hash: str,
        commit_author: str,
        commit_date: str,
        files_changed: str
    ) -> Dict:
        """
        Main sync function - processes a git commit and syncs to Notion.

        Args:
            commit_msg: Git commit message
            commit_hash: Git commit hash
            commit_author: Commit author name
            commit_date: Commit datetime
            files_changed: Comma-separated list of files

        Returns:
            Dict with sync results
        """
        results = {
            "roadmap_updates": [],
            "session_log": None,
            "success": True
        }

        logger.info("=" * 60)
        logger.info("NOTION SYNC STARTED")
        logger.info("=" * 60)
        logger.info(f"Commit: {commit_hash}")
        logger.info(f"Message: {commit_msg}")
        logger.info(f"Author: {commit_author}")
        logger.info(f"Date: {commit_date}")
        logger.info(f"Files: {files_changed}")

        # Extract and update roadmap items
        roadmap_refs = self.extract_roadmap_refs(commit_msg)
        if roadmap_refs:
            logger.info(f"\nFound roadmap references: {roadmap_refs}")
            for item_id in roadmap_refs:
                success = self.update_roadmap_status(
                    item_id=item_id,
                    commit_msg=commit_msg,
                    commit_hash=commit_hash
                )
                results["roadmap_updates"].append({
                    "item_id": item_id,
                    "success": success
                })
        else:
            logger.info("\nNo roadmap references found in commit message")

        # Create session log
        logger.info("\nCreating session log...")
        session_log = self.create_session_log(
            commit_msg=commit_msg,
            commit_hash=commit_hash,
            commit_author=commit_author,
            commit_date=commit_date,
            files_changed=files_changed
        )
        results["session_log"] = session_log

        logger.info("\n" + "=" * 60)
        logger.info("NOTION SYNC COMPLETE")
        logger.info("=" * 60)

        return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Sync git commits to Notion")
    parser.add_argument("--commit-msg", required=True, help="Git commit message")
    parser.add_argument("--commit-hash", required=True, help="Git commit hash")
    parser.add_argument("--commit-author", required=True, help="Commit author name")
    parser.add_argument("--commit-date", required=True, help="Commit datetime")
    parser.add_argument("--files", required=True, help="Comma-separated list of files")

    args = parser.parse_args()

    try:
        engine = NotionSyncEngine()
        results = engine.sync_commit(
            commit_msg=args.commit_msg,
            commit_hash=args.commit_hash,
            commit_author=args.commit_author,
            commit_date=args.commit_date,
            files_changed=args.files
        )

        # Exit with success
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
