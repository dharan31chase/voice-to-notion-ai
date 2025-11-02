"""
Staging Management Module

Responsibilities:
- Copy files from USB to local staging area
- Manage staging directory cleanup
- Safe USB file deletion
- Track staged files

Does NOT handle:
- USB detection (USBDetector)
- Transcription (Transcriber)
- Archiving (ArchiveManager)
"""

import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


class StagingManager:
    """Manages local staging area for USB files."""

    def __init__(self, staging_folder: Path):
        """
        Initialize staging manager.

        Args:
            staging_folder: Path to local staging directory
        """
        self.staging_folder = staging_folder
        self.staging_folder.mkdir(exist_ok=True)
        logger.info(f"StagingManager initialized with folder: {staging_folder}")

    def copy_to_staging(self, files: List[Path]) -> Tuple[List[Path], List[Tuple[Path, str]]]:
        """
        Copy files from USB to local staging area.

        Args:
            files: List of USB file paths to copy

        Returns:
            Tuple[List[Path], List[Tuple[Path, str]]]:
                - List of successfully staged files (local paths)
                - List of (failed_file, error_reason) tuples
        """
        # TODO: Extract from _copy_files_to_staging()
        # Should:
        # - Copy each file to staging folder
        # - Preserve filename
        # - Track successes and failures
        # - Return local staging paths
        pass

    def cleanup_staging(self) -> int:
        """
        Clean up staging directory (remove all files).

        Returns:
            int: Number of files cleaned up
        """
        # TODO: Extract from _cleanup_staging_files()
        # Should:
        # - Remove all files in staging folder
        # - Keep the folder itself
        # - Handle permission errors
        # - Return count of cleaned files
        pass

    def safe_delete_usb(self, usb_file: Path) -> Tuple[bool, str]:
        """
        Safely delete file from USB (after staging complete).

        Args:
            usb_file: Path to USB file to delete

        Returns:
            Tuple[bool, str]: (success, message)
        """
        # TODO: Extract from _safe_delete_usb_file()
        # Should:
        # - Verify file is on USB (not local)
        # - Check permissions
        # - Attempt deletion
        # - Handle failures gracefully
        # - Never delete local files!
        pass

    def get_staged_files(self) -> List[Path]:
        """
        Get list of files currently in staging.

        Returns:
            List[Path]: Files in staging folder
        """
        # TODO: Helper method to list staged files
        pass

    def is_staged(self, filename: str) -> bool:
        """
        Check if file is already in staging.

        Args:
            filename: Filename to check

        Returns:
            bool: True if file exists in staging
        """
        # TODO: Helper to avoid duplicate staging
        pass
