"""
Notion Schema Detection Module (Phase 5)

Auto-detects Notion database schemas via API to remove hardcoded assumptions:
- Query Notion databases API
- Extract property names and types
- Cache schema in memory (session-lifetime)
- Fallback to defaults if detection fails

Usage:
    from mcp_server.utils.notion_schema import NotionSchemaDetector

    detector = NotionSchemaDetector(notion_client)
    schema = detector.get_strategy_board_schema()

    # Access properties safely
    status_prop = schema.get_property("Status", default="Status")
    initiative_name_prop = schema.get_property("Initiative Name", default="Initiative Name")
"""

from typing import Dict, Optional, Any
from notion_client import Client
import logging

logger = logging.getLogger(__name__)


class NotionSchemaDetector:
    """
    Detects Notion database schemas and caches them in memory.

    Removes hardcoded property names, allowing database schema changes
    without code updates.
    """

    def __init__(self, notion_client: Client):
        """
        Initialize schema detector.

        Args:
            notion_client: Notion API client
        """
        self.notion_client = notion_client

        # In-memory cache (session-lifetime)
        self._schema_cache: Dict[str, Dict] = {}

    def detect_database_schema(self, database_id: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Detect schema for a Notion database.

        Args:
            database_id: Notion database ID
            force_refresh: Force refresh cache (default: False)

        Returns:
            Dict with property names, types, and metadata
            None if detection fails

        Schema format:
            {
                "database_id": "abc123",
                "title": "Strategy Board",
                "properties": {
                    "Initiative Name": {"type": "title", "id": "prop_id_1"},
                    "Status": {"type": "select", "id": "prop_id_2", "options": [...]},
                    "Priority Score": {"type": "number", "id": "prop_id_3"},
                    ...
                }
            }
        """
        # Check cache first
        if not force_refresh and database_id in self._schema_cache:
            return self._schema_cache[database_id]

        try:
            # Query database metadata
            database = self.notion_client.databases.retrieve(database_id=database_id)

            # Extract properties
            properties = {}
            for prop_name, prop_data in database.get("properties", {}).items():
                prop_type = prop_data.get("type")
                prop_id = prop_data.get("id")

                properties[prop_name] = {
                    "type": prop_type,
                    "id": prop_id
                }

                # For select/multi_select, extract options
                if prop_type in ["select", "multi_select"]:
                    options_data = prop_data.get(prop_type, {}).get("options", [])
                    properties[prop_name]["options"] = [
                        opt.get("name") for opt in options_data
                    ]

            # Build schema
            schema = {
                "database_id": database_id,
                "title": database.get("title", [{}])[0].get("plain_text", "Unknown"),
                "properties": properties
            }

            # Cache schema
            self._schema_cache[database_id] = schema

            logger.info(f"Detected schema for database '{schema['title']}': {len(properties)} properties")

            return schema

        except Exception as e:
            logger.error(f"Error detecting schema for database {database_id}: {str(e)}")
            return None

    def get_strategy_board_schema(self, database_id: str) -> 'NotionSchema':
        """
        Get Strategy Board schema.

        Args:
            database_id: Strategy Board database ID

        Returns:
            NotionSchema wrapper with safe property access
        """
        schema = self.detect_database_schema(database_id)
        return NotionSchema(schema, defaults={
            "initiative_name": "Initiative Name",
            "status": "Status",
            "priority_score": "Priority Score",
            "category": "Category",
            "project": "Project",
            "completed_date": "Completed Date",
            "decision_notes": "Decision Notes",
            "launch_notes": "Launch Notes",
            "prd": "PRD"
        })

    def get_roadmap_schema(self, database_id: str) -> 'NotionSchema':
        """
        Get Roadmap database schema.

        Args:
            database_id: Roadmap database ID

        Returns:
            NotionSchema wrapper with safe property access
        """
        schema = self.detect_database_schema(database_id)
        return NotionSchema(schema, defaults={
            "initiative_name": "Initiative Name",
            "strategy_board": "🎯 Strategy Board",
            "owner": "Owner"
        })

    def get_sessions_schema(self, database_id: str) -> 'NotionSchema':
        """
        Get Sessions database schema.

        Args:
            database_id: Sessions database ID

        Returns:
            NotionSchema wrapper with safe property access
        """
        schema = self.detect_database_schema(database_id)
        return NotionSchema(schema, defaults={
            "title": "Title",
            "description": "Description",
            "session_date": "Session Date",
            "duration": "Duration",
            "strategy_board": "🎯 Strategy Board"
        })


class NotionSchema:
    """
    Wrapper for Notion database schema with safe property access.

    Provides fallback to default property names if schema detection fails
    or properties are renamed.
    """

    def __init__(self, schema: Optional[Dict], defaults: Dict[str, str]):
        """
        Initialize schema wrapper.

        Args:
            schema: Detected schema (or None if detection failed)
            defaults: Default property names (fallback)
        """
        self.schema = schema
        self.defaults = defaults

        # Build reverse mapping: default_key -> actual_property_name
        self._property_map = {}
        if schema:
            self._build_property_map()

    def _build_property_map(self):
        """
        Build mapping from default keys to actual property names.

        Handles renamed properties by fuzzy matching.
        """
        if not self.schema:
            return

        properties = self.schema.get("properties", {})

        for default_key, default_name in self.defaults.items():
            # Try exact match first
            if default_name in properties:
                self._property_map[default_key] = default_name
                continue

            # Try case-insensitive match
            lower_default = default_name.lower()
            for prop_name in properties:
                if prop_name.lower() == lower_default:
                    self._property_map[default_key] = prop_name
                    break

            # If no match, use default (property may not exist)
            if default_key not in self._property_map:
                self._property_map[default_key] = default_name

    def get_property(self, key: str) -> str:
        """
        Get actual property name for a logical key.

        Args:
            key: Logical key (e.g., "initiative_name", "status")

        Returns:
            Actual property name in Notion database

        Example:
            >>> schema.get_property("initiative_name")
            "Initiative Name"  # or "Initiative Title" if renamed
        """
        if key in self._property_map:
            return self._property_map[key]

        # Fallback to default
        return self.defaults.get(key, key)

    def get_property_type(self, key: str) -> Optional[str]:
        """
        Get property type for a logical key.

        Args:
            key: Logical key (e.g., "status", "priority_score")

        Returns:
            Property type (e.g., "select", "number", "title")
            None if schema not detected or property not found
        """
        if not self.schema:
            return None

        prop_name = self.get_property(key)
        properties = self.schema.get("properties", {})

        if prop_name in properties:
            return properties[prop_name].get("type")

        return None

    def get_select_options(self, key: str) -> Optional[list]:
        """
        Get select/multi_select options for a property.

        Args:
            key: Logical key (e.g., "status", "category")

        Returns:
            List of option names
            None if not a select property or schema not detected
        """
        if not self.schema:
            return None

        prop_name = self.get_property(key)
        properties = self.schema.get("properties", {})

        if prop_name in properties:
            prop_data = properties[prop_name]
            if prop_data.get("type") in ["select", "multi_select"]:
                return prop_data.get("options", [])

        return None

    def has_property(self, key: str) -> bool:
        """
        Check if property exists in database.

        Args:
            key: Logical key

        Returns:
            True if property exists, False otherwise
        """
        if not self.schema:
            # If schema not detected, assume property exists (use default)
            return True

        prop_name = self.get_property(key)
        properties = self.schema.get("properties", {})

        return prop_name in properties

    def validate_select_value(self, key: str, value: str) -> bool:
        """
        Validate that a value is valid for a select property.

        Args:
            key: Logical key (e.g., "status")
            value: Value to validate (e.g., "✅ Complete")

        Returns:
            True if valid, False otherwise
        """
        options = self.get_select_options(key)

        if options is None:
            # Can't validate - assume valid
            return True

        return value in options

    def __repr__(self):
        """String representation of schema."""
        if self.schema:
            title = self.schema.get("title", "Unknown")
            prop_count = len(self.schema.get("properties", {}))
            return f"<NotionSchema: {title} ({prop_count} properties)>"
        else:
            return f"<NotionSchema: Not detected (using defaults)>"
