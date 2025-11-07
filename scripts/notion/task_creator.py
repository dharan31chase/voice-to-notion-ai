"""
Task Creator Module - Phase 5.1

Responsibilities:
- Create Notion task entries
- Build task-specific properties
- Handle task-specific formatting and metadata

Does NOT handle:
- Note creation (NoteCreator)
- Content formatting (ContentFormatter)
- Notion API calls (NotionClientWrapper)
"""

from typing import Dict, Optional
from datetime import datetime

# Import shared utilities
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger

logger = get_logger(__name__)


class TaskCreator:
    """Creates Notion task entries with AI-powered routing."""

    def __init__(
        self,
        notion_wrapper,
        router,
        project_matcher,
        content_formatter,
        tasks_db_id: str
    ):
        """
        Initialize task creator.

        Args:
            notion_wrapper: NotionClientWrapper instance
            router: IntelligentRouter instance
            project_matcher: ProjectMatcher instance
            content_formatter: ContentFormatter instance
            tasks_db_id: Notion Tasks database ID
        """
        self.notion = notion_wrapper
        self.router = router
        self.project_matcher = project_matcher
        self.formatter = content_formatter
        self.tasks_db = tasks_db_id

    def _create_content_blocks(self, content_chunks: list) -> list:
        """
        Create Notion paragraph blocks from content chunks.

        Args:
            content_chunks: List of content strings (pre-chunked to <2000 chars)

        Returns:
            List of paragraph block dictionaries
        """
        blocks = []
        for chunk in content_chunks:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": chunk}}]
                }
            })
        return blocks

    def create_task(self, analysis: Dict) -> Optional[Dict]:
        """
        Create a task with AI-powered smart routing and clean formatting.

        Args:
            analysis: Task analysis dictionary with content, title, etc.

        Returns:
            Created Notion page dictionary or None if failed
        """
        try:
            content = analysis.get("content", "")
            title = analysis.get("title", "")

            # Extra safety check to remove any quotes
            title = title.strip('"').strip("'")

            # Clean and format the title with confidence scoring
            title_result = self.formatter.clean_task_title(title)
            cleaned_title = title_result["formatted_text"]

            # Clean the content to remove meta-commentary with confidence scoring
            content_result = self.formatter.organize_task_content(content)
            cleaned_content = content_result["formatted_text"]

            # Add metadata to analysis (future Epic 2nd Brain Workflow)
            analysis["metadata"] = {
                "confidence_score": min(
                    title_result["confidence_score"],
                    content_result["confidence_score"]
                ),
                "needs_review": (
                    title_result["needs_review"] or
                    content_result["needs_review"]
                ),
                "review_reasons": (
                    title_result["review_reasons"] +
                    content_result["review_reasons"]
                ),
                "created_at": datetime.now().isoformat(),
                "source": "voice_recording"
            }

            # Get AI recommendations
            project = self.router.detect_project(content)
            duration_info = self.router.estimate_duration_and_due_date(content)
            special_tags = self.router.detect_special_tags(content)

            # Build properties
            properties = self._build_task_properties(
                cleaned_title,
                duration_info,
                special_tags,
                analysis
            )

            # Get icon for page-level setting
            icon = analysis.get("icon", "⁉️")

            # Split content into chunks for Notion's 2000 character limit
            content_chunks = self.formatter.chunk_content(cleaned_content)

            # Create content blocks with CLEANED content (split if >2000 chars)
            content_blocks = self._create_content_blocks(content_chunks)

            # Add divider
            content_blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })

            # Add AI analysis metadata
            content_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "text": {
                            "content": (
                                f"🤖 AI Analysis:\n"
                                f"• Duration: {duration_info['duration_category']} "
                                f"({duration_info['estimated_minutes']} min)\n"
                                f"• Project: {project}\n"
                                f"• Tags: {', '.join(special_tags) if special_tags else 'None'}\n"
                                f"• Reasoning: {duration_info['reasoning']}\n"
                                f"• Confidence: {analysis['metadata']['confidence_score']}"
                            )
                        }
                    }]
                }
            })

            # Create the page with icon
            page = self.notion.create_page(
                database_id=self.tasks_db,
                icon={"type": "emoji", "emoji": icon},
                properties=properties,
                children=content_blocks
            )

            if page:
                logger.info(f"✅ Created intelligent task: {cleaned_title}")
                logger.info(f"   🎯 Project: {project}")
                logger.info(f"   ⏰ Due: {duration_info['due_date']} ({duration_info['duration_category']})")
                logger.info(f"   🏷️ Tags: {special_tags}")
                logger.info(f"   📊 Confidence: {analysis['metadata']['confidence_score']}")
            else:
                logger.error(f"❌ Failed to create task in Notion")

            return page

        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            logger.error(f"   Content: {content[:100]}...")
            return None

    def _build_task_properties(
        self,
        title: str,
        duration_info: Dict,
        special_tags: list,
        analysis: Dict
    ) -> Dict:
        """
        Build task properties dictionary for Notion.

        Args:
            title: Cleaned task title
            duration_info: Duration and due date information
            special_tags: List of special tags
            analysis: Full analysis dictionary

        Returns:
            Notion properties dictionary
        """
        properties = {
            "Task": {"title": [{"text": {"content": title}}]},
            "Done": {"status": {"name": "Not started"}},
            "Due Date": {"date": {"start": duration_info["due_date"]}}
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

        # Add manual review tag if needed
        if analysis.get("manual_review", False):
            special_tags.append("🏷️ Needs Manual Review")

        # Add confidence-based tag (future Epic 2nd Brain Workflow)
        if analysis.get("metadata", {}).get("needs_review", False):
            special_tags.append("🔍 Needs Review")

        # Add tags
        if special_tags:
            properties["Tags"] = {"multi_select": [{"name": tag} for tag in special_tags]}

        return properties
