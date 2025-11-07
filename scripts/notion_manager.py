"""
Notion Manager - Backward Compatibility Wrapper

This file maintains backward compatibility for code that imports from
scripts/notion_manager.py.

All functionality has been refactored into the scripts/notion/ package:
- scripts/notion/content_formatter.py
- scripts/notion/notion_client_wrapper.py
- scripts/notion/task_creator.py
- scripts/notion/note_creator.py
- scripts/notion/notion_manager.py (new modular implementation)

Usage:
    from scripts.notion_manager import AdvancedNotionManager  # Still works!
    from scripts.notion import NotionManager  # New recommended import
"""

# Import from new modular implementation
from scripts.notion import (
    NotionManager,
    AdvancedNotionManager,
    ContentFormatter,
    NotionClientWrapper,
    TaskCreator,
    NoteCreator
)

# Expose main function for backward compatibility
from scripts.notion.notion_manager import main

__all__ = [
    "NotionManager",
    "AdvancedNotionManager",
    "ContentFormatter",
    "NotionClientWrapper",
    "TaskCreator",
    "NoteCreator",
    "main"
]

if __name__ == "__main__":
    main()
