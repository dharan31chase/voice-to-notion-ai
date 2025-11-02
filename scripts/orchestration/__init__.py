"""
Voice Recording Orchestration Package

Modular orchestration system for processing voice recordings from USB to Notion.
Follows Single Responsibility Principle with specialized modules.

Architecture:
- detection/: USB detection and file validation
- staging/: Local staging for USB files
- transcription/: Whisper transcription with batching and resource monitoring
- processing/: AI-powered transcript processing
- verification/: Notion entry verification
- archiving/: Archive management and file organization
- state/: State persistence and session management
"""

__version__ = "2.0.0"  # Phase B refactoring

# Expose main classes for easy importing
from .state import StateManager
from .detection import USBDetector, FileValidator

__all__ = [
    "StateManager",
    "USBDetector",
    "FileValidator",
]
