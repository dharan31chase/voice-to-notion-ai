"""
NotionProjectFetcher Module - Phase 5.2

Responsibilities:
- Fetch projects from Notion API with filtering
- Enrich project data with aliases
- Handle API errors and fallbacks
- Track fetch metrics (duration, errors)

Does NOT handle:
- Caching (ProjectCache)
- Fuzzy matching (FuzzyMatcher)
- Project detection (ProjectMatcher)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

# Import shared utilities
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from core.config_loader import ConfigLoader

logger = get_logger(__name__)


class NotionProjectFetcher:
    """Fetches and enriches project data from Notion Projects database."""

    def __init__(
        self,
        notion_client,
        projects_db_id: str,
        config: ConfigLoader = None
    ):
        """
        Initialize Notion project fetcher.

        Args:
            notion_client: Notion client instance
            projects_db_id: Notion Projects database ID
            config: Optional ConfigLoader instance
        """
        self.notion = notion_client
        self.projects_db_id = projects_db_id
        self.config = config or ConfigLoader()

    def fetch_projects(self) -> tuple[List[Dict[str, Any]], int]:
        """
        Query Notion Projects database and return active projects.

        Returns:
            Tuple of (projects_list, fetch_duration_ms)
            Projects list contains dicts with name, id, status, and aliases
        """
        if not self.notion or not self.projects_db_id:
            logger.error("❌ Notion client or Projects database ID not available")
            return [], 0

        start_time = datetime.now()

        try:
            # Build filter for active projects
            filter_params = self._build_filter_params()

            # Query the database
            response = self.notion.databases.query(
                database_id=self.projects_db_id,
                filter=filter_params
            )

            # Parse and enrich projects
            projects = []
            for page in response["results"]:
                project_data = self._parse_project_data(page)
                if project_data:
                    projects.append(project_data)

            # Calculate fetch duration
            fetch_duration = int((datetime.now() - start_time).total_seconds() * 1000)

            logger.info(f"✅ Fetched {len(projects)} active projects from Notion ({fetch_duration}ms)")

            return projects, fetch_duration

        except Exception as e:
            logger.error(f"❌ Notion query failed: {e}")
            return [], 0

    def _build_filter_params(self) -> Dict:
        """
        Build Notion filter parameters for active projects.

        Filters for:
        - Status in ["In progress", "Ongoing", "Backlog", "On Hold"]
        - Archives = False (not archived)

        Returns:
            Notion filter dictionary
        """
        return {
            "and": [
                {
                    "or": [
                        {
                            "property": "Status",
                            "status": {
                                "equals": "In progress"
                            }
                        },
                        {
                            "property": "Status",
                            "status": {
                                "equals": "Ongoing"
                            }
                        },
                        {
                            "property": "Status",
                            "status": {
                                "equals": "Backlog"
                            }
                        },
                        {
                            "property": "Status",
                            "status": {
                                "equals": "On Hold"
                            }
                        }
                    ]
                },
                {
                    "property": "Archives",
                    "checkbox": {
                        "equals": False
                    }
                }
            ]
        }

    def _parse_project_data(self, page: Dict) -> Optional[Dict[str, Any]]:
        """
        Parse project data from Notion page.

        Extracts:
        - name (from title field)
        - id (page ID)
        - status (from status field)
        - aliases (from text field, comma-separated)

        Args:
            page: Notion page dictionary

        Returns:
            Project dictionary or None if invalid
        """
        properties = page["properties"]

        # Extract project name (title field)
        name_property = properties.get("Name", {})
        name = ""
        if name_property.get("title") and len(name_property["title"]) > 0:
            name = name_property["title"][0]["text"]["content"]

        # Extract status (status type)
        status_property = properties.get("Status", {})
        status = status_property.get("status", {}).get("name", "")

        # Extract aliases (text field)
        aliases_property = properties.get("Aliases", {})
        aliases_text = ""
        if aliases_property.get("rich_text") and len(aliases_property["rich_text"]) > 0:
            aliases_text = aliases_property["rich_text"][0]["text"]["content"]

        # Parse aliases (split by comma, strip whitespace)
        aliases = []
        if aliases_text:
            aliases = [alias.strip() for alias in aliases_text.split(",") if alias.strip()]

        # Only return projects with names
        if not name:
            return None

        return {
            "name": name,
            "id": page["id"],
            "status": status,
            "aliases": aliases,
            "archived": False
        }

    def get_fallback_projects(self) -> List[str]:
        """
        Get hardcoded fallback project list.

        Used when Notion is unavailable or cache is empty.

        Returns:
            List of hardcoded project names
        """
        hardcoded_projects = [
            "Green Card Application",
            "Welcoming our Baby",
            "Project 2035 - Zen Product Craftsman",
            "Home Remodel",
            "AI Ethics / Sci Author Extraordinaire",
            "Legendary Seed-stage Investor",
            "Tinker with Claude",
            "Nutrition & Morning Routine",
            "India Wedding Planning",
            "Epic 2nd Brain Workflow in Notion",
            "Lume Coaching Notes & Meetings",
            "Project Eudaimonia: Focus. Flow. Fulfillment.",
            "Life Admin HQ",
            "Improve my Product Sense & Taste",
            "Woodworking Projects"
        ]
        logger.info(f"📋 Using {len(hardcoded_projects)} hardcoded projects (fallback)")
        return hardcoded_projects
