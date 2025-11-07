"""
Notion Package - Phase 5.1

Modular Notion integration with separate concerns:
- ContentFormatter: Format and clean content
- NotionClientWrapper: API calls with retry logic
- TaskCreator: Create task entries
- NoteCreator: Create note entries
- NotionManager: Thin facade coordinating all modules
"""

from .content_formatter import ContentFormatter
from .notion_client_wrapper import NotionClientWrapper
from .task_creator import TaskCreator
from .note_creator import NoteCreator
from .notion_manager import NotionManager, AdvancedNotionManager

__all__ = [
    "ContentFormatter",
    "NotionClientWrapper",
    "TaskCreator",
    "NoteCreator",
    "NotionManager",
    "AdvancedNotionManager",  # Legacy compatibility
]
