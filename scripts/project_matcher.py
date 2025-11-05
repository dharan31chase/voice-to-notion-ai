#!/usr/bin/env python3
"""
Project Matcher - Phase 5.2 Refactored

Thin facade that coordinates ProjectCache, NotionProjectFetcher, and FuzzyMatcher.

Responsibilities:
- Coordinate cache refresh and fallback logic
- Provide simple API for external callers
- Maintain backward compatibility

Does NOT handle:
- Caching logic (ProjectCache)
- Fetching from Notion (NotionProjectFetcher)
- Fuzzy matching (FuzzyMatcher)
"""

import os
import sys
from typing import List, Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables first
load_dotenv()

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import Notion client
try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    Client = None

# Import Phase 5.2 modules
from scripts.matchers.project_cache import ProjectCache
from scripts.matchers.notion_project_fetcher import NotionProjectFetcher
from scripts.matchers.fuzzy_matcher import FuzzyMatcher

# Import shared utilities
from core.logging_utils import get_logger
from core.config_loader import ConfigLoader

logger = get_logger(__name__)


class ProjectMatcher:
    """
    Thin facade for project matching operations.

    Coordinates between ProjectCache, NotionProjectFetcher, and FuzzyMatcher.
    """

    def __init__(self, config: ConfigLoader = None):
        """
        Initialize project matcher.

        Args:
            config: Optional ConfigLoader instance
        """
        self.config = config or ConfigLoader()

        # Initialize ProjectCache
        self._cache = ProjectCache(config=self.config)

        # Initialize Notion client and fetcher
        self._notion_client = None
        self._fetcher = None
        self._projects_db_id = os.getenv("PROJECTS_DATABASE_ID")

        if NOTION_AVAILABLE:
            notion_token = os.getenv("NOTION_TOKEN")
            if notion_token and self._projects_db_id:
                try:
                    self._notion_client = Client(auth=notion_token)
                    self._fetcher = NotionProjectFetcher(
                        self._notion_client,
                        self._projects_db_id,
                        self.config
                    )
                    logger.info("✅ Notion project fetcher initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize Notion client: {e}")
        else:
            logger.warning("⚠️ Notion client not available - install notion-client")

        # Initialize FuzzyMatcher
        self._matcher = FuzzyMatcher(self._cache, self.config)

        logger.info("✅ ProjectMatcher initialized")

    def get_project_list(self) -> List[str]:
        """
        Get the current project list.

        Tries Notion first, falls back to cached data or hardcoded list.

        Returns:
            List of project names
        """
        # Check if we should refresh cache
        if self._cache.should_refresh_cache():
            if self._fetcher:
                projects, fetch_duration = self._fetcher.fetch_projects()

                if projects:
                    # Update cache with Notion data
                    self._cache.update_from_notion(projects, fetch_duration)
                    return self._cache.get_all_project_names()
                else:
                    # Notion failed, check if we have cached data
                    if self._cache._cache["metadata"]["total_projects"] > 0:
                        cache_age = self._cache._cache["metadata"]["cache_age_minutes"]
                        logger.warning(f"⚠️ Using {cache_age}min old cached data (Notion unavailable)")
                        return self._cache.get_all_project_names()
            else:
                logger.warning("⚠️ Notion fetcher not available")

        # Use cached data if fresh
        if self._cache._cache["metadata"]["total_projects"] > 0:
            return self._cache.get_all_project_names()

        # Fallback to hardcoded list
        if self._fetcher:
            return self._fetcher.get_fallback_projects()
        else:
            # Inline fallback if fetcher not available
            logger.warning("📋 Using inline hardcoded projects (fallback)")
            return [
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

    def fuzzy_match_project(self, extracted_project_name: str) -> str:
        """
        Enhanced fuzzy match extracted project name against actual project list and aliases.

        Delegates to FuzzyMatcher.

        Args:
            extracted_project_name: Project name extracted from transcript

        Returns:
            Matched project name from actual list, or "Manual Review Required" if no match
        """
        # Get available projects (ensures cache is fresh)
        available_projects = self.get_project_list()

        # Delegate to FuzzyMatcher
        return self._matcher.match_project(extracted_project_name, available_projects)

    def get_project_id_from_cache(self, project_name: str) -> Optional[str]:
        """
        Get project ID from cache for Notion relation assignment.

        Delegates to ProjectCache.

        Args:
            project_name: Project name to look up

        Returns:
            Project ID or None if not found
        """
        project_data = self._cache.get_project_by_name(project_name)
        return project_data.get("id") if project_data else None

    def set_similarity_threshold(self, threshold: float):
        """
        Set the similarity threshold for fuzzy matching.

        Delegates to FuzzyMatcher.

        Args:
            threshold: Threshold value (0.0 to 1.0)

        Raises:
            ValueError: If threshold is not between 0.0 and 1.0
        """
        self._matcher.set_threshold(threshold)

    def refresh_project_list(self):
        """
        Force refresh of project list from Notion.

        Clears cache and fetches fresh data.
        """
        logger.info("🔄 Forcing project list refresh...")

        if self._fetcher:
            projects, fetch_duration = self._fetcher.fetch_projects()

            if projects:
                self._cache.update_from_notion(projects, fetch_duration)
                logger.info(f"✅ Refreshed {len(projects)} projects")
            else:
                logger.error("❌ Failed to refresh project list")
        else:
            logger.error("❌ Notion fetcher not available for refresh")


# Global instance for easy access (backward compatibility)
project_matcher = ProjectMatcher()


def fuzzy_match_project(extracted_project_name: str) -> str:
    """
    Convenience function for fuzzy project matching.

    Args:
        extracted_project_name: Project name extracted from transcript

    Returns:
        Matched project name or "Manual Review Required"
    """
    return project_matcher.fuzzy_match_project(extracted_project_name)


def test_project_matching():
    """Test the fuzzy matching functionality"""
    logger.info("🧪 Testing Project Matching")
    logger.info("=" * 50)

    test_cases = [
        # Exact matches
        ("Life Admin HQ", "Life Admin HQ"),
        ("Green Card Application", "Green Card Application"),

        # Fuzzy matches
        ("Product Craftsman", "Project 2035 - Zen Product Craftsman"),
        ("Product Sense", "Improve my Product Sense & Taste"),
        ("Second Brain", "Epic 2nd Brain Workflow in Notion"),
        ("Eudaimonia", "Project Eudaimonia: Focus. Flow. Fulfillment."),
        ("Baby", "Welcoming our Baby"),
        ("Home", "Home Remodel"),

        # No matches
        ("Email plumber", "Manual Review Required"),
        ("Random project", "Manual Review Required"),
        ("", "Manual Review Required"),
    ]

    results = []

    for input_name, expected in test_cases:
        result = fuzzy_match_project(input_name)
        success = result == expected
        results.append(success)

        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status}: '{input_name}' → '{result}' (expected: '{expected}')")

    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100

    logger.info(f"\n📊 Results: {passed}/{total} ({success_rate:.1f}%)")

    if success_rate >= 90:
        logger.info("🎉 Excellent fuzzy matching!")
        return True
    else:
        logger.warning("⚠️ Some issues to address")
        return False


if __name__ == "__main__":
    test_project_matching()
