"""
USB Detection Module

Responsibilities:
- Detect USB recorder connection
- Scan for .mp3 files on USB device
- Check file permissions
- Filter unprocessed files

Does NOT handle:
- File validation (FileValidator's job)
- File copying (StagingManager's job)
- State management (StateManager's job)
"""

import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


class USBDetector:
    """Detects and scans USB recorder for audio files."""

    def __init__(self, recorder_path: Path):
        """
        Initialize USB detector.

        Args:
            recorder_path: Path to USB recorder mount point
                          (e.g., /Volumes/IC RECORDER/REC_FILE/FOLDER01)
        """
        self.recorder_path = recorder_path
        logger.info(f"USBDetector initialized for {recorder_path}")

    def check_connection(self) -> Tuple[bool, str]:
        """
        Check if USB recorder is connected and accessible.

        Returns:
            Tuple[bool, str]: (success, message)
                - (True, "USB connected") if accessible
                - (False, reason) if not accessible
        """
        # TODO: Extract from _check_usb_connection()
        # Should check:
        # - Path exists
        # - Path is readable
        # - Can list directory contents
        pass

    def scan_files(self) -> List[Path]:
        """
        Scan USB device for .mp3 files.

        Returns:
            List[Path]: Discovered .mp3 files (full paths)
        """
        # TODO: Extract from _scan_mp3_files()
        # Should:
        # - Recursively search for .mp3 files
        # - Return sorted list
        # - Handle permission errors gracefully
        pass

    def check_permissions(self, file_path: Path) -> Tuple[bool, str]:
        """
        Check if file has required read permissions.

        Args:
            file_path: Path to file to check

        Returns:
            Tuple[bool, str]: (has_permission, message)
        """
        # TODO: Extract from _check_usb_file_permissions()
        # Should check:
        # - File exists
        # - File is readable
        # - Not a directory
        pass

    def get_unprocessed_files(self, mp3_files: List[Path], processed_files: set) -> List[Path]:
        """
        Filter out already processed files.

        Args:
            mp3_files: List of discovered .mp3 files
            processed_files: Set of filenames already processed

        Returns:
            List[Path]: Unprocessed files only
        """
        # TODO: Extract from _get_unprocessed_files()
        # Should compare filenames (not full paths) against processed set
        pass
