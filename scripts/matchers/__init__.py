"""
Matchers Package - Phase 5.2

Modular project matching with separate concerns:
- ProjectCache: Cache project data with file persistence
- NotionProjectFetcher: Fetch projects from Notion API
- FuzzyMatcher: Perform fuzzy matching with confidence scores
- ProjectMatcher: Thin facade coordinating all modules
"""

from .project_cache import ProjectCache
from .notion_project_fetcher import NotionProjectFetcher
from .fuzzy_matcher import FuzzyMatcher

__all__ = [
    "ProjectCache",
    "NotionProjectFetcher",
    "FuzzyMatcher",
]
