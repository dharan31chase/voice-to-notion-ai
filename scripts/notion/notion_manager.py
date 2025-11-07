"""
Notion Manager - Phase 5.1 Refactored

Thin facade that coordinates TaskCreator, NoteCreator, ContentFormatter,
and NotionClientWrapper.

Responsibilities:
- Route analysis to appropriate creator (task vs note)
- Coordinate between modules
- Provide simple API for external callers

Does NOT handle:
- Content formatting (ContentFormatter)
- Notion API calls (NotionClientWrapper)
- Task/Note specific logic (TaskCreator/NoteCreator)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import Notion client
try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    Client = None

# Import project modules
from scripts.intelligent_router import IntelligentRouter
from scripts.project_matcher import ProjectMatcher

# Import new Notion modules (Phase 5.1)
from scripts.notion.content_formatter import ContentFormatter
from scripts.notion.notion_client_wrapper import NotionClientWrapper
from scripts.notion.task_creator import TaskCreator
from scripts.notion.note_creator import NoteCreator

# Import shared utilities
from core.logging_utils import get_logger
from core.config_loader import ConfigLoader

logger = get_logger(__name__)

# Initialize Notion client
if NOTION_AVAILABLE:
    notion = Client(auth=os.getenv("NOTION_TOKEN"))
else:
    notion = None
    logger.warning("⚠️ Notion client not available - install notion-client")


class NotionManager:
    """
    Thin facade for Notion operations.

    Coordinates between ContentFormatter, NotionClientWrapper,
    TaskCreator, and NoteCreator.
    """

    def __init__(self, config: ConfigLoader = None, review_mode: bool = False):
        """
        Initialize Notion manager.

        Args:
            config: Optional ConfigLoader instance
            review_mode: If True, holds low-confidence items for review
                        (Future: Epic 2nd Brain Workflow)
        """
        self.config = config or ConfigLoader()
        self.review_mode = review_mode

        # Get database IDs from environment
        self.tasks_db = os.getenv("TASKS_DATABASE_ID")
        self.notes_db = os.getenv("NOTES_DATABASE_ID")
        self.projects_db = os.getenv("PROJECTS_DATABASE_ID")
        self.areas_db = os.getenv("AREAS_DATABASE_ID")

        if not NOTION_AVAILABLE:
            raise ImportError("notion-client not installed. Run: pip install notion-client")

        if not self.tasks_db or not self.notes_db:
            raise ValueError("TASKS_DATABASE_ID and NOTES_DATABASE_ID must be set in environment")

        # Initialize dependencies
        self.router = IntelligentRouter()
        self.project_matcher = ProjectMatcher()

        # Initialize Phase 5.1 modules
        self.formatter = ContentFormatter()
        self.notion_wrapper = NotionClientWrapper(notion, self.config)
        self.task_creator = TaskCreator(
            self.notion_wrapper,
            self.router,
            self.project_matcher,
            self.formatter,
            self.tasks_db
        )
        self.note_creator = NoteCreator(
            self.notion_wrapper,
            self.router,
            self.project_matcher,
            self.formatter,
            self.notes_db
        )

        logger.info("✅ NotionManager initialized")

    def create_intelligent_task(self, analysis: Dict) -> Optional[Dict]:
        """
        Create a task with AI-powered smart routing and clean formatting.

        Delegates to TaskCreator.

        Args:
            analysis: Task analysis dictionary

        Returns:
            Created Notion page or None
        """
        return self.task_creator.create_task(analysis)

    def create_organized_note(self, analysis: Dict) -> Optional[Dict]:
        """
        Create a note with intelligent organization and embedded action items.

        Delegates to NoteCreator.

        Args:
            analysis: Note analysis dictionary

        Returns:
            Created Notion page or None
        """
        return self.note_creator.create_note(analysis)

    def route_content(self, analysis) -> Dict:
        """
        Handle both single analysis and list of analyses with structured results.

        Args:
            analysis: Single analysis dict or list of analysis dicts

        Returns:
            Dict with successful, failed, and summary keys
        """
        # Check if it's a list (multiple tasks) or single object
        if isinstance(analysis, list):
            # Multiple tasks - process each one
            successful_tasks = []
            failed_tasks = []

            for i, task_analysis in enumerate(analysis, 1):
                try:
                    result = self.create_intelligent_task(task_analysis)
                    if result:
                        successful_tasks.append(result)
                        logger.info(f"✅ Task {i} created successfully")
                    else:
                        failed_tasks.append({
                            "task": task_analysis,
                            "error": "Failed to create task in Notion"
                        })
                        logger.error(f"❌ Task {i} failed to create")
                except Exception as e:
                    failed_tasks.append({
                        "task": task_analysis,
                        "error": str(e)
                    })
                    logger.error(f"❌ Task {i} failed with error: {e}")

            logger.info(f"📊 Multiple tasks summary: {len(successful_tasks)} successful, {len(failed_tasks)} failed")

            return {
                "successful": successful_tasks,
                "failed": failed_tasks,
                "summary": {
                    "total": len(analysis),
                    "successful": len(successful_tasks),
                    "failed": len(failed_tasks)
                }
            }

        else:
            # Single analysis - use structured format for consistency
            try:
                category = analysis.get("category", "").lower()

                if category == "task":
                    result = self.create_intelligent_task(analysis)
                elif category in ["note", "research"]:
                    result = self.create_organized_note(analysis)
                else:
                    logger.warning(f"⚠️ Unknown category: {category}, creating as note with manual review flag")
                    result = self.create_organized_note(analysis)

                if result:
                    return {
                        "successful": [result],
                        "failed": [],
                        "summary": {
                            "total": 1,
                            "successful": 1,
                            "failed": 0
                        }
                    }
                else:
                    return {
                        "successful": [],
                        "failed": [{
                            "task": analysis,
                            "error": "Failed to create content in Notion"
                        }],
                        "summary": {
                            "total": 1,
                            "successful": 0,
                            "failed": 1
                        }
                    }

            except Exception as e:
                return {
                    "successful": [],
                    "failed": [{
                        "task": analysis,
                        "error": str(e)
                    }],
                    "summary": {
                        "total": 1,
                        "successful": 0,
                        "failed": 1
                    }
                }


# Legacy class name for backward compatibility
class AdvancedNotionManager(NotionManager):
    """Legacy class name - use NotionManager instead."""
    pass


def main():
    """Test the Notion manager with processed transcripts."""
    manager = NotionManager()

    # Look for processed files
    from pathlib import Path
    import json

    processed_files = list(Path("processed").glob("*.json"))

    if not processed_files:
        print("No processed files found. Run process_transcripts.py first!")
        return

    print(f"Found {len(processed_files)} processed transcript files")

    for file_path in processed_files:
        print(f"\n{'='*60}")
        print(f"Processing: {file_path.name}")
        print(f"{'='*60}")

        with open(file_path, 'r') as f:
            data = json.load(f)

        result = manager.route_content(data)
        print(f"\n✅ Results: {result['summary']}")


if __name__ == "__main__":
    main()
