"""
Project Cache Module - Phase 5.2

Responsibilities:
- Cache project data with file persistence
- Manage cache freshness and expiration
- Provide fast lookup by name or alias
- Handle cache metadata

Does NOT handle:
- Fetching from Notion (NotionProjectFetcher)
- Fuzzy matching (FuzzyMatcher)
- Project detection (ProjectMatcher)
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

# Import shared utilities
import sys
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from core.config_loader import ConfigLoader

logger = get_logger(__name__)


class ProjectCache:
    """In-memory cache for project data with file persistence."""

    def __init__(self, cache_file: str = ".cache/projects.json", config: ConfigLoader = None):
        """
        Initialize project cache.

        Args:
            cache_file: Path to cache file
            config: Optional ConfigLoader instance
        """
        self.cache_file = Path(cache_file)
        self.config = config or ConfigLoader()

        self._cache = {
            "projects": {},  # project_name -> full_data
            "aliases": {},   # normalized_alias -> project_name
            "metadata": {
                "last_fetch": None,
                "cache_age_minutes": 0,
                "source": "none",
                "total_projects": 0,
                "fetch_duration_ms": 0,
                "last_successful_fetch": None,
                "failed_fetch_attempts": 0
            }
        }
        self._load_cache()

    def _load_cache(self):
        """Load cache from file if it exists."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self._cache = data
                    self._update_cache_age()
                    logger.info(
                        f"📋 Loaded {self._cache['metadata']['total_projects']} projects from cache "
                        f"({self._cache['metadata']['cache_age_minutes']}min old)"
                    )
        except Exception as e:
            logger.warning(f"⚠️ Failed to load cache: {e}")
            self._cache = {
                "projects": {},
                "aliases": {},
                "metadata": {
                    "last_fetch": None,
                    "cache_age_minutes": 0,
                    "source": "none",
                    "total_projects": 0,
                    "fetch_duration_ms": 0,
                    "last_successful_fetch": None,
                    "failed_fetch_attempts": 0
                }
            }

    def _save_cache(self):
        """Save cache to file."""
        try:
            # Create cache directory if it doesn't exist
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"⚠️ Failed to save cache: {e}")

    def _update_cache_age(self):
        """Update cache age based on last fetch time."""
        if self._cache["metadata"]["last_fetch"]:
            try:
                last_fetch = datetime.fromisoformat(self._cache["metadata"]["last_fetch"])
                age = datetime.now() - last_fetch
                self._cache["metadata"]["cache_age_minutes"] = int(age.total_seconds() / 60)
            except Exception:
                self._cache["metadata"]["cache_age_minutes"] = 999999  # Very old

    def _normalize_alias(self, alias: str) -> str:
        """Normalize alias for consistent matching."""
        return alias.lower().strip()

    def update_from_notion(self, projects_data: List[Dict[str, Any]], fetch_duration_ms: int = 0):
        """
        Update cache with data from Notion.

        Args:
            projects_data: List of project dictionaries from Notion
            fetch_duration_ms: Time taken to fetch from Notion
        """
        start_time = datetime.now()

        # Clear existing data
        self._cache["projects"] = {}
        self._cache["aliases"] = {}

        # Process each project
        for project in projects_data:
            name = project.get("name", "")
            if name:
                # Store project data
                self._cache["projects"][name] = project

                # Process aliases
                aliases = project.get("aliases", [])
                for alias in aliases:
                    normalized_alias = self._normalize_alias(alias)
                    if normalized_alias:
                        self._cache["aliases"][normalized_alias] = name

        # Update metadata
        self._cache["metadata"].update({
            "last_fetch": start_time.isoformat(),
            "cache_age_minutes": 0,
            "source": "notion",
            "total_projects": len(self._cache["projects"]),
            "fetch_duration_ms": fetch_duration_ms,
            "last_successful_fetch": start_time.isoformat(),
            "failed_fetch_attempts": 0
        })

        # Save to file
        self._save_cache()

        logger.info(
            f"✅ Updated cache with {len(self._cache['projects'])} projects "
            f"and {len(self._cache['aliases'])} aliases"
        )

    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get project by exact name match.

        Args:
            name: Project name to look up

        Returns:
            Project dictionary or None
        """
        return self._cache["projects"].get(name)

    def get_project_by_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """
        Get project by normalized alias.

        Args:
            alias: Project alias to look up

        Returns:
            Project dictionary or None
        """
        normalized_alias = self._normalize_alias(alias)
        project_name = self._cache["aliases"].get(normalized_alias)
        return self.get_project_by_name(project_name) if project_name else None

    def get_all_project_names(self) -> List[str]:
        """Get list of all project names (for backward compatibility)."""
        return list(self._cache["projects"].keys())

    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get list of all project data dictionaries."""
        return list(self._cache["projects"].values())

    def is_cache_fresh(self, max_age_minutes: Optional[int] = None) -> bool:
        """
        Check if cache is fresh enough to use.

        Args:
            max_age_minutes: Maximum age in minutes (from config if None)

        Returns:
            True if cache is fresh
        """
        if max_age_minutes is None:
            max_age_minutes = self.config.get("project_matching.cache_duration_minutes", 60)

        self._update_cache_age()
        return self._cache["metadata"]["cache_age_minutes"] < max_age_minutes

    def should_refresh_cache(self, max_age_minutes: Optional[int] = None) -> bool:
        """
        Determine if cache should be refreshed.

        Args:
            max_age_minutes: Maximum age in minutes (from config if None)

        Returns:
            True if cache should be refreshed
        """
        if max_age_minutes is None:
            max_age_minutes = self.config.get("project_matching.cache_duration_minutes", 60)

        cache_age = self._cache["metadata"]["cache_age_minutes"]
        total_projects = self._cache["metadata"]["total_projects"]

        # Always refresh if cache is empty
        if total_projects == 0:
            return True

        # Always refresh if cache is very old (>24 hours)
        if cache_age > 1440:  # 24 hours
            return True

        # Try to refresh if cache is moderately old (>max_age_minutes)
        if cache_age > max_age_minutes:
            return True

        # Use cached data if fresh
        return False

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache metadata for debugging."""
        self._update_cache_age()
        return self._cache["metadata"].copy()

    def clear_cache(self):
        """Clear cache and delete file."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            self._cache = {
                "projects": {},
                "aliases": {},
                "metadata": {
                    "last_fetch": None,
                    "cache_age_minutes": 0,
                    "source": "none",
                    "total_projects": 0,
                    "fetch_duration_ms": 0,
                    "last_successful_fetch": None,
                    "failed_fetch_attempts": 0
                }
            }
            logger.info("🗑️ Cache cleared")
        except Exception as e:
            logger.warning(f"⚠️ Failed to clear cache: {e}")
