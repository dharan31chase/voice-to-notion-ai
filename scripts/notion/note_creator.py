"""
Note Creator Module - Phase 5.1

Responsibilities:
- Create Notion note entries
- Build note-specific properties
- Handle note-specific formatting and action items

Does NOT handle:
- Task creation (TaskCreator)
- Content formatting (ContentFormatter)
- Notion API calls (NotionClientWrapper)
"""

from typing import Dict, Optional, List
from datetime import datetime

# Import shared utilities
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger

logger = get_logger(__name__)


class NoteCreator:
    """Creates Notion note entries with intelligent organization."""

    def __init__(
        self,
        notion_wrapper,
        router,
        project_matcher,
        content_formatter,
        notes_db_id: str
    ):
        """
        Initialize note creator.

        Args:
            notion_wrapper: NotionClientWrapper instance
            router: IntelligentRouter instance
            project_matcher: ProjectMatcher instance
            content_formatter: ContentFormatter instance
            notes_db_id: Notion Notes database ID
        """
        self.notion = notion_wrapper
        self.router = router
        self.project_matcher = project_matcher
        self.formatter = content_formatter
        self.notes_db = notes_db_id

    def create_note(self, analysis: Dict) -> Optional[Dict]:
        """
        Create a note with intelligent organization and embedded action items.

        Args:
            analysis: Note analysis dictionary with content, title, etc.

        Returns:
            Created Notion page dictionary or None if failed
        """
        try:
            content = analysis.get("content", "")
            title = analysis.get("title", "")

            # Organize the content using AI (preserves voice)
            content_result = self.formatter.organize_note_content(content)
            organized_content = content_result["formatted_text"]

            # Add metadata to analysis (future Epic 2nd Brain Workflow)
            analysis["metadata"] = {
                "confidence_score": content_result["confidence_score"],
                "needs_review": content_result["needs_review"],
                "review_reasons": content_result["review_reasons"],
                "created_at": datetime.now().isoformat(),
                "source": "voice_recording"
            }

            # Build properties
            properties = self._build_note_properties(title, analysis)

            # Get icon for page-level setting
            icon = analysis.get("icon", "⁉️")

            # Split content into chunks for Notion's 2000 character limit
            content_chunks = self.formatter.chunk_content(organized_content)

            # Create content blocks from chunks
            content_blocks = self._create_content_blocks(content_chunks)

            # Add action items if any (embedded in note, not separate tasks)
            action_items = analysis.get("action_items", [])
            if action_items:
                content_blocks.extend(self._create_action_items_blocks(action_items))

            # Create the page with icon
            page = self.notion.create_page(
                database_id=self.notes_db,
                icon={"type": "emoji", "emoji": icon},
                properties=properties,
                children=content_blocks
            )

            if page:
                analysis_project = analysis.get("project", "")
                logger.info(f"✅ Created organized note: {title}")
                logger.info(f"   🎯 Project: {analysis_project}")
                logger.info(f"   📝 Action items: {len(action_items)}")
                logger.info(f"   📊 Confidence: {analysis['metadata']['confidence_score']}")
            else:
                logger.error(f"❌ Failed to create note in Notion")

            return page

        except Exception as e:
            logger.error(f"❌ Failed to create note: {e}")
            logger.error(f"   Content: {content[:100]}...")
            return None

    def _build_note_properties(self, title: str, analysis: Dict) -> Dict:
        """
        Build note properties dictionary for Notion.

        Args:
            title: Note title
            analysis: Full analysis dictionary

        Returns:
            Notion properties dictionary
        """
        properties = {
            "Name": {"title": [{"text": {"content": title}}]},
            "Created Date": {"date": {"start": datetime.now().isoformat()}}
        }

        # Add project assignment from analysis (fuzzy matching)
        analysis_project = analysis.get("project", "")
        if analysis_project and analysis_project != "Manual Review Required":
            # Get project ID from cache
            project_id = self.project_matcher.get_project_id_from_cache(analysis_project)
            if project_id:
                properties["Project"] = {"relation": [{"id": project_id}]}
                logger.info(f"   🎯 Project assigned: {analysis_project} (ID: {project_id[:8]}...)")
            else:
                logger.warning(f"   ⚠️ Project not found in cache: {analysis_project}")
        else:
            logger.info(f"   📝 No project assigned (Manual Review Required or empty)")

        # Handle manual review cases
        if analysis_project == "Manual Review Required":
            # Use Jessica's Input checkbox instead
            properties["Need Jessica's Input"] = {"checkbox": True}

        # Add confidence-based checkbox (future Epic 2nd Brain Workflow)
        if analysis.get("metadata", {}).get("needs_review", False):
            properties["Need Jessica's Input"] = {"checkbox": True}

        return properties

    def _create_content_blocks(self, content_chunks: List[str]) -> List[Dict]:
        """
        Create Notion content blocks from chunks.

        Args:
            content_chunks: List of content strings

        Returns:
            List of Notion block dictionaries
        """
        content_blocks = []
        for i, chunk in enumerate(content_chunks):
            content_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                }
            })

            # Add space between chunks (except last one)
            if i < len(content_chunks) - 1:
                content_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ""}}]
                    }
                })

        return content_blocks

    def _create_action_items_blocks(self, action_items: List[str]) -> List[Dict]:
        """
        Create Notion blocks for action items.

        Args:
            action_items: List of action item strings

        Returns:
            List of Notion block dictionaries
        """
        blocks = [
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "📋 Action Items"}}]
                }
            }
        ]

        for item in action_items:
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": item}}]
                }
            })

        return blocks
