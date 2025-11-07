"""
Notion Client Wrapper Module - Phase 5.1

Responsibilities:
- Wrap Notion API calls with retry logic
- Handle rate limiting and errors gracefully
- Provide clean interface for page creation

Does NOT handle:
- Content formatting (ContentFormatter)
- Task/Note specific logic (TaskCreator/NoteCreator)
- Routing decisions (NotionManager)
"""

import time
from typing import Dict, List, Optional, Callable, Any

# Import shared utilities
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from core.config_loader import ConfigLoader

logger = get_logger(__name__)


class NotionClientWrapper:
    """Wraps Notion API with retry logic and error handling."""

    def __init__(self, notion_client, config: ConfigLoader = None):
        """
        Initialize Notion client wrapper.

        Args:
            notion_client: notion_client.Client instance
            config: Optional ConfigLoader instance
        """
        self.notion = notion_client
        self.config = config or ConfigLoader()

        # Get retry configuration
        self.retry_attempts = self.config.get("notion.retry_attempts", 3)
        self.retry_delay = self.config.get("notion.retry_delay_seconds", 2)

    def create_page(
        self,
        database_id: str,
        properties: Dict,
        children: Optional[List[Dict]] = None,
        icon: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Create a Notion page with retry logic.

        Args:
            database_id: Notion database ID
            properties: Page properties dictionary
            children: Optional list of content blocks
            icon: Optional icon dictionary (e.g., {"type": "emoji", "emoji": "📝"})

        Returns:
            Created page dictionary or None if failed
        """
        # Build page data
        page_data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }

        if icon:
            page_data["icon"] = icon

        if children:
            page_data["children"] = children

        # Create page with retry
        return self._retry_with_backoff(
            operation=lambda: self.notion.pages.create(**page_data),
            operation_name="create_page"
        )

    def _retry_with_backoff(
        self,
        operation: Callable,
        operation_name: str = "notion_operation"
    ) -> Optional[Any]:
        """
        Retry an operation with exponential backoff.

        Args:
            operation: Callable that performs the Notion API call
            operation_name: Name for logging purposes

        Returns:
            Operation result or None if all retries failed
        """
        last_error = None

        for attempt in range(1, self.retry_attempts + 1):
            try:
                result = operation()
                if attempt > 1:
                    logger.info(f"✅ {operation_name} succeeded on attempt {attempt}")
                return result

            except Exception as e:
                last_error = e
                error_msg = str(e)

                # Check if it's a rate limit error (429)
                if "429" in error_msg or "rate" in error_msg.lower():
                    logger.warning(f"⚠️ Rate limit hit on {operation_name}, attempt {attempt}/{self.retry_attempts}")
                    if attempt < self.retry_attempts:
                        # Longer delay for rate limits
                        delay = self.retry_delay * (2 ** (attempt - 1)) * 2
                        logger.info(f"   Waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue

                # Check if it's a network error
                elif "network" in error_msg.lower() or "timeout" in error_msg.lower():
                    logger.warning(f"⚠️ Network error on {operation_name}, attempt {attempt}/{self.retry_attempts}")
                    if attempt < self.retry_attempts:
                        delay = self.retry_delay * attempt
                        logger.info(f"   Waiting {delay}s before retry...")
                        time.sleep(delay)
                        continue

                # Other errors
                else:
                    logger.error(f"❌ Error on {operation_name}: {error_msg}")
                    if attempt < self.retry_attempts:
                        delay = self.retry_delay
                        logger.info(f"   Retrying in {delay}s...")
                        time.sleep(delay)
                        continue

        # All retries failed
        logger.error(f"❌ {operation_name} failed after {self.retry_attempts} attempts: {last_error}")
        return None

    def update_page(
        self,
        page_id: str,
        properties: Dict
    ) -> Optional[Dict]:
        """
        Update a Notion page with retry logic.

        Args:
            page_id: Notion page ID
            properties: Properties to update

        Returns:
            Updated page dictionary or None if failed
        """
        return self._retry_with_backoff(
            operation=lambda: self.notion.pages.update(
                page_id=page_id,
                properties=properties
            ),
            operation_name="update_page"
        )

    def retrieve_page(self, page_id: str) -> Optional[Dict]:
        """
        Retrieve a Notion page with retry logic.

        Args:
            page_id: Notion page ID

        Returns:
            Page dictionary or None if failed
        """
        return self._retry_with_backoff(
            operation=lambda: self.notion.pages.retrieve(page_id=page_id),
            operation_name="retrieve_page"
        )

    def query_database(
        self,
        database_id: str,
        filter_dict: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None
    ) -> Optional[Dict]:
        """
        Query a Notion database with retry logic.

        Args:
            database_id: Notion database ID
            filter_dict: Optional filter dictionary
            sorts: Optional list of sort dictionaries

        Returns:
            Query results dictionary or None if failed
        """
        query_params = {"database_id": database_id}
        if filter_dict:
            query_params["filter"] = filter_dict
        if sorts:
            query_params["sorts"] = sorts

        return self._retry_with_backoff(
            operation=lambda: self.notion.databases.query(**query_params),
            operation_name="query_database"
        )
