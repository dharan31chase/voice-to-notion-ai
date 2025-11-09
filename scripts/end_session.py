#!/usr/bin/env python3
"""
End Session Script

Updates the most recent Notion session with rich metadata that Claude Code
has from the conversation context.

Usage:
    # Interactive mode (asks questions)
    python3 scripts/end_session.py

    # With all parameters
    python3 scripts/end_session.py \
        --duration 120 \
        --decisions "Decided X, Chose Y approach" \
        --next-steps "Build Z, Test W" \
        --alerts "Bug in transcription" \
        --roadmap-updates "ROADMAP-1:P0:notes,ROADMAP-2:P1:notes"

Author: Claude Code
Created: 2025-11-09
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment
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


class SessionEnder:
    """Ends a session by enriching Notion with session metadata."""

    def __init__(self):
        """Initialize session ender."""
        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ValueError("NOTION_TOKEN not found in environment")

        self.notion_client = Client(auth=notion_token)

        if not SESSIONS_DB_ID:
            raise ValueError("NOTION_SESSIONS_DB must be set")

        logger.info("=" * 60)
        logger.info("END SESSION")
        logger.info("=" * 60)
        logger.info("")

    def get_most_recent_session(self) -> Optional[Dict]:
        """Get the most recent session from Notion."""
        logger.info("Fetching most recent session...")

        response = self.notion_client.databases.query(
            database_id=SESSIONS_DB_ID,
            sorts=[
                {
                    "property": "Session Date",
                    "direction": "descending"
                }
            ],
            page_size=1
        )

        if response["results"]:
            session = response["results"][0]
            session_title = session["properties"]["Title"]["title"][0]["text"]["content"]
            logger.info(f"✓ Found: '{session_title}'")
            return session
        else:
            logger.error("✗ No sessions found")
            return None

    def update_session_metadata(
        self,
        session_id: str,
        duration: Optional[int] = None,
        decisions: Optional[str] = None,
        next_steps: Optional[str] = None,
        alerts: Optional[str] = None
    ) -> bool:
        """Update session with rich metadata."""
        logger.info("Updating session metadata...")

        properties = {}

        if duration is not None:
            properties["Duration"] = {"number": duration}
            logger.info(f"  Duration: {duration} minutes")

        if decisions:
            properties["Decisions Made"] = {
                "rich_text": [{"text": {"content": decisions[:2000]}}]
            }
            logger.info(f"  Decisions: {decisions[:100]}...")

        if next_steps:
            properties["Next Steps"] = {
                "rich_text": [{"text": {"content": next_steps[:2000]}}]
            }
            logger.info(f"  Next Steps: {next_steps[:100]}...")

        if alerts:
            properties["Critical Alerts"] = {
                "rich_text": [{"text": {"content": alerts[:2000]}}]
            }
            logger.info(f"  Alerts: {alerts[:100]}...")

        if not properties:
            logger.warning("No metadata to update")
            return False

        try:
            self.notion_client.pages.update(
                page_id=session_id,
                properties=properties
            )
            logger.info("✓ Session updated successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Error updating session: {e}")
            return False

    def update_roadmap_item(
        self,
        roadmap_id: str,
        priority: Optional[str] = None,
        notes: Optional[str] = None,
        prd_link: Optional[str] = None,
        tech_req_link: Optional[str] = None
    ) -> bool:
        """Update a roadmap item with metadata."""
        logger.info(f"Updating ROADMAP-{roadmap_id}...")

        # Find the roadmap item
        try:
            query_response = self.notion_client.databases.query(
                database_id=ROADMAP_DB_ID,
                filter={
                    "property": "Roadmap ID",
                    "rich_text": {
                        "equals": f"ROADMAP-{roadmap_id}"
                    }
                }
            )

            if not query_response["results"]:
                logger.warning(f"  ROADMAP-{roadmap_id} not found")
                return False

            page_id = query_response["results"][0]["id"]
            feature_name = query_response["results"][0]["properties"]["Feature Name"]["title"][0]["text"]["content"]
            logger.info(f"  Found: '{feature_name}'")

            properties = {}

            if priority:
                properties["Priority"] = {"select": {"name": priority}}
                logger.info(f"    Priority: {priority}")

            if notes:
                properties["Notes"] = {
                    "rich_text": [{"text": {"content": notes[:2000]}}]
                }
                logger.info(f"    Notes: {notes[:100]}...")

            if prd_link:
                properties["PRD Link"] = {"url": prd_link}
                logger.info(f"    PRD Link: {prd_link}")

            if tech_req_link:
                properties["Tech Req Link"] = {"url": tech_req_link}
                logger.info(f"    Tech Req Link: {tech_req_link}")

            if not properties:
                logger.warning("  No updates for this roadmap item")
                return False

            self.notion_client.pages.update(
                page_id=page_id,
                properties=properties
            )
            logger.info(f"  ✓ Updated ROADMAP-{roadmap_id}")
            return True

        except Exception as e:
            logger.error(f"  ✗ Error updating ROADMAP-{roadmap_id}: {e}")
            return False

    def end_session(
        self,
        duration: Optional[int] = None,
        decisions: Optional[str] = None,
        next_steps: Optional[str] = None,
        alerts: Optional[str] = None,
        roadmap_updates: Optional[List[Dict]] = None
    ):
        """Main end session workflow."""
        # Get most recent session
        session = self.get_most_recent_session()
        if not session:
            logger.error("Cannot end session - no recent session found")
            return

        logger.info("")

        # Update session metadata
        session_updated = self.update_session_metadata(
            session_id=session["id"],
            duration=duration,
            decisions=decisions,
            next_steps=next_steps,
            alerts=alerts
        )

        logger.info("")

        # Update roadmap items
        if roadmap_updates:
            for update in roadmap_updates:
                self.update_roadmap_item(**update)
                logger.info("")

        logger.info("=" * 60)
        logger.info("SESSION ENDED SUCCESSFULLY")
        logger.info("=" * 60)


def parse_roadmap_updates(updates_str: str) -> List[Dict]:
    """
    Parse roadmap updates string.

    Format: ROADMAP-1:P0:notes,ROADMAP-2:P1:notes
    """
    if not updates_str:
        return []

    updates = []
    for item in updates_str.split(","):
        parts = item.strip().split(":")
        if len(parts) >= 2:
            roadmap_id = parts[0].replace("ROADMAP-", "")
            priority = parts[1] if len(parts) > 1 else None
            notes = parts[2] if len(parts) > 2 else None

            updates.append({
                "roadmap_id": roadmap_id,
                "priority": priority,
                "notes": notes
            })

    return updates


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="End session and update Notion")
    parser.add_argument("--duration", type=int, help="Session duration in minutes")
    parser.add_argument("--decisions", type=str, help="Key decisions made")
    parser.add_argument("--next-steps", type=str, help="Next steps")
    parser.add_argument("--alerts", type=str, help="Critical alerts")
    parser.add_argument("--roadmap-updates", type=str, help="Roadmap updates (format: ROADMAP-1:P0:notes,ROADMAP-2:P1:notes)")

    args = parser.parse_args()

    # Parse roadmap updates
    roadmap_updates = parse_roadmap_updates(args.roadmap_updates) if args.roadmap_updates else None

    try:
        ender = SessionEnder()
        ender.end_session(
            duration=args.duration,
            decisions=args.decisions,
            next_steps=args.next_steps,
            alerts=args.alerts,
            roadmap_updates=roadmap_updates
        )
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
