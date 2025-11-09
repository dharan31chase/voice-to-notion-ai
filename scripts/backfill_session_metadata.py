#!/usr/bin/env python3
"""
Backfill Session Metadata from Markdown Logs

Reads session log markdown files from docs/sessions/ and updates the corresponding
Notion session entries with rich metadata (decisions, next steps, alerts, etc.)

Usage:
    # Backfill all sessions
    python3 scripts/backfill_session_metadata.py

    # Backfill specific date
    python3 scripts/backfill_session_metadata.py --date 2025-11-08

    # Dry run
    python3 scripts/backfill_session_metadata.py --dry-run

Author: Claude Code
Created: 2025-11-09
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Optional, Dict, List
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


class SessionLogParser:
    """Parses session log markdown files to extract metadata."""

    def __init__(self, file_path: Path):
        """Initialize parser with session log file."""
        self.file_path = file_path
        self.content = file_path.read_text()
        self.metadata = self._parse()

    def _extract_section(self, heading: str, end_heading: Optional[str] = None) -> str:
        """Extract content between two headings."""
        # Match heading (e.g., "## 🚀 What Shipped")
        pattern = rf'^##\s+.*?{re.escape(heading)}.*?$'
        match = re.search(pattern, self.content, re.MULTILINE | re.IGNORECASE)

        if not match:
            return ""

        start = match.end()

        # Find next heading or end of file
        if end_heading:
            end_pattern = rf'^##\s+.*?{re.escape(end_heading)}.*?$'
            end_match = re.search(end_pattern, self.content[start:], re.MULTILINE | re.IGNORECASE)
            end = start + end_match.start() if end_match else len(self.content)
        else:
            # Find any next heading
            next_heading = re.search(r'^##\s+', self.content[start:], re.MULTILINE)
            end = start + next_heading.start() if next_heading else len(self.content)

        return self.content[start:end].strip()

    def _extract_duration(self) -> Optional[int]:
        """Extract duration from header metadata."""
        match = re.search(r'\*\*Duration\*\*:\s*(\d+)\s*hours?', self.content, re.IGNORECASE)
        if match:
            return int(match.group(1)) * 60  # Convert hours to minutes

        match = re.search(r'\*\*Duration\*\*:\s*(\d+)\s*min', self.content, re.IGNORECASE)
        if match:
            return int(match.group(1))

        return None

    def _extract_decisions(self) -> str:
        """Extract architecture decisions."""
        section = self._extract_section("Architecture Decisions")
        if not section:
            return ""

        # Extract decision summaries
        decisions = []
        decision_pattern = r'\*\*Decision \d+\*\*:\s*([^\n]+)'
        matches = re.findall(decision_pattern, section)

        for i, decision in enumerate(matches, 1):
            decisions.append(f"{i}. {decision}")

        return "\n".join(decisions) if decisions else section[:500]

    def _extract_next_steps(self) -> str:
        """Extract next steps section."""
        section = self._extract_section("Next Steps")
        if not section:
            section = self._extract_section("➡️ Next Steps")

        # Clean up and limit length
        return section[:1000] if section else ""

    def _extract_alerts(self) -> str:
        """Extract critical alerts."""
        section = self._extract_section("Critical Alerts")
        if not section:
            return "None"

        # Check for "None" or "No blockers"
        if re.search(r'(None|No blockers|No bugs)', section, re.IGNORECASE):
            return "None"

        return section[:1000]

    def _extract_what_shipped(self) -> str:
        """Extract what shipped summary."""
        section = self._extract_section("What Shipped")
        return section[:500] if section else ""

    def _extract_roadmap_refs(self) -> List[str]:
        """Extract ROADMAP-X references from the log."""
        pattern = r'ROADMAP-(\d+)'
        matches = re.findall(pattern, self.content)
        return list(set(matches))  # Unique IDs

    def _parse(self) -> Dict:
        """Parse all metadata from session log."""
        return {
            "duration": self._extract_duration(),
            "decisions": self._extract_decisions(),
            "next_steps": self._extract_next_steps(),
            "alerts": self._extract_alerts(),
            "what_shipped": self._extract_what_shipped(),
            "roadmap_refs": self._extract_roadmap_refs()
        }


class SessionMetadataBackfiller:
    """Backfills Notion sessions with metadata from markdown logs."""

    def __init__(self, dry_run: bool = False):
        """Initialize backfiller."""
        notion_token = os.getenv("NOTION_TOKEN")
        if not notion_token:
            raise ValueError("NOTION_TOKEN not found in environment")

        self.notion_client = Client(auth=notion_token)
        self.dry_run = dry_run

        if not SESSIONS_DB_ID:
            raise ValueError("NOTION_SESSIONS_DB must be set")

        logger.info("=" * 60)
        logger.info("BACKFILL SESSION METADATA")
        logger.info("=" * 60)
        logger.info(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will update Notion)'}")
        logger.info("")

    def find_session_logs(self, date_filter: Optional[str] = None) -> List[Path]:
        """Find all session log markdown files."""
        session_dirs = [
            project_root / "docs" / "sessions" / "claude-code",
            project_root / "docs" / "sessions" / "claude-chat"
        ]

        logs = []
        for session_dir in session_dirs:
            if not session_dir.exists():
                continue

            for log_file in session_dir.glob("*.md"):
                if log_file.name == "TEMPLATE.md":
                    continue

                # Filter by date if specified
                if date_filter and date_filter not in log_file.name:
                    continue

                logs.append(log_file)

        return sorted(logs)

    def find_notion_session(self, date: str, agent: str) -> Optional[Dict]:
        """Find Notion session by date and agent."""
        try:
            response = self.notion_client.databases.query(
                database_id=SESSIONS_DB_ID,
                filter={
                    "and": [
                        {
                            "property": "Session Date",
                            "date": {
                                "equals": date
                            }
                        },
                        {
                            "property": "Agent",
                            "select": {
                                "equals": agent
                            }
                        }
                    ]
                }
            )

            if response["results"]:
                # Return the first match (there might be multiple sessions same day)
                return response["results"][0]

            return None

        except Exception as e:
            logger.error(f"Error finding session: {e}")
            return None

    def update_session(self, session_id: str, metadata: Dict) -> bool:
        """Update Notion session with metadata."""
        properties = {}

        if metadata.get("duration"):
            properties["Duration"] = {"number": metadata["duration"]}

        if metadata.get("decisions"):
            properties["Decisions Made"] = {
                "rich_text": [{"text": {"content": metadata["decisions"][:2000]}}]
            }

        if metadata.get("next_steps"):
            properties["Next Steps"] = {
                "rich_text": [{"text": {"content": metadata["next_steps"][:2000]}}]
            }

        if metadata.get("alerts"):
            properties["Critical Alerts"] = {
                "rich_text": [{"text": {"content": metadata["alerts"][:2000]}}]
            }

        if not properties:
            return False

        if self.dry_run:
            logger.info(f"  [DRY RUN] Would update with: {list(properties.keys())}")
            return True

        try:
            self.notion_client.pages.update(
                page_id=session_id,
                properties=properties
            )
            return True
        except Exception as e:
            logger.error(f"  Error updating session: {e}")
            return False

    def process_log(self, log_path: Path) -> Dict:
        """Process a single session log file."""
        logger.info(f"📄 {log_path.name}")

        # Parse the log
        parser = SessionLogParser(log_path)
        metadata = parser.metadata

        # Extract date and agent from filename
        # Format: YYYY-MM-DD-description.md
        match = re.match(r'(\d{4}-\d{2}-\d{2})', log_path.name)
        if not match:
            logger.warning("  ⏭️  SKIP: Cannot parse date from filename")
            return {"status": "skipped", "reason": "invalid_filename"}

        date = match.group(1)

        # Determine agent from directory
        agent = "Claude Code" if "claude-code" in str(log_path.parent) else "Claude Chat"

        logger.info(f"  Date: {date}, Agent: {agent}")
        logger.info(f"  Extracted: Duration={metadata.get('duration')}min, Decisions={len(metadata.get('decisions', ''))>0}, Next Steps={len(metadata.get('next_steps', ''))>0}, Alerts={len(metadata.get('alerts', ''))>0}")

        # Find matching Notion session
        session = self.find_notion_session(date, agent)
        if not session:
            logger.warning(f"  ⚠️  WARNING: No matching Notion session found for {date} - {agent}")
            return {"status": "warning", "reason": "session_not_found"}

        session_title = session["properties"]["Title"]["title"][0]["text"]["content"]
        logger.info(f"  Found: '{session_title}'")

        # Check if already has metadata
        has_duration = session["properties"].get("Duration", {}).get("number") is not None
        has_decisions = bool(session["properties"].get("Decisions Made", {}).get("rich_text"))

        if has_duration and has_decisions:
            logger.info(f"  ⏭️  SKIP: Already has metadata")
            return {"status": "skipped", "reason": "already_populated"}

        # Update session
        success = self.update_session(session["id"], metadata)

        if success:
            logger.info(f"  ✅ Updated successfully")
            return {"status": "success" if not self.dry_run else "dry_run"}
        else:
            logger.error(f"  ❌ Update failed")
            return {"status": "error"}

    def backfill(self, date_filter: Optional[str] = None):
        """Run the backfill process."""
        logs = self.find_session_logs(date_filter)
        logger.info(f"Found {len(logs)} session log(s)\n")

        if not logs:
            logger.warning("No session logs found!")
            return

        results = {
            "total": len(logs),
            "success": 0,
            "skipped": 0,
            "warning": 0,
            "error": 0,
            "dry_run": 0
        }

        for log_path in logs:
            result = self.process_log(log_path)
            results[result["status"]] += 1
            logger.info("")

        # Print summary
        logger.info("=" * 60)
        logger.info("BACKFILL COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total logs: {results['total']}")
        logger.info(f"✅ Success: {results['success']}")
        logger.info(f"⏭️  Skipped: {results['skipped']}")
        logger.info(f"⚠️  Warnings: {results['warning']}")
        logger.info(f"❌ Errors: {results['error']}")
        if self.dry_run:
            logger.info(f"🔍 Dry run: {results['dry_run']}")
        logger.info("")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Backfill session metadata from markdown logs")
    parser.add_argument("--date", type=str, help="Only backfill sessions from this date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")

    args = parser.parse_args()

    try:
        backfiller = SessionMetadataBackfiller(dry_run=args.dry_run)
        backfiller.backfill(date_filter=args.date)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
