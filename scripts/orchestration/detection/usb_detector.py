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

import os
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

    def check_connection(self) -> bool:
        """
        Check if USB recorder is connected and accessible.

        Returns:
            bool: True if USB is connected and readable
        """
        try:
            if not self.recorder_path.exists():
                logger.error(f"❌ USB recorder not found at: {self.recorder_path}")
                return False

            # Test if we can read the directory
            os.listdir(self.recorder_path)
            logger.info(f"✅ USB recorder connected: {self.recorder_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Cannot access USB recorder: {e}")
            return False

    def scan_files(self) -> List[Path]:
        """
        Scan USB device for .mp3 files, excluding macOS hidden files.

        Returns:
            List[Path]: Discovered .mp3 files (full paths)
        """
        try:
            all_mp3_files = list(self.recorder_path.glob("*.mp3"))

            # Filter out macOS hidden files (._* prefix)
            mp3_files = [f for f in all_mp3_files if not f.name.startswith('._')]

            hidden_count = len(all_mp3_files) - len(mp3_files)
            if hidden_count > 0:
                logger.debug(f"⏭️ Filtered out {hidden_count} macOS hidden files (._* prefix)")

            logger.info(f"📁 Found {len(mp3_files)} .mp3 files in {self.recorder_path}")
            return mp3_files

        except Exception as e:
            logger.error(f"❌ Error scanning for .mp3 files: {e}")
            return []

    def check_permissions(self, mp3_file: Path) -> bool:
        """
        Check if USB recorder file has proper permissions for reading.

        Args:
            mp3_file: Path to MP3 file to check

        Returns:
            bool: True if file has proper read permissions
        """
        try:
            if not mp3_file.exists():
                logger.error(f"❌ USB file not found: {mp3_file}")
                return False

            # Check if file is readable
            if not os.access(mp3_file, os.R_OK):
                logger.warning(f"⚠️ USB file not readable: {mp3_file}")
                logger.info(f"💡 File permissions: {oct(mp3_file.stat().st_mode)[-3:]}")
                logger.info(f"💡 Try: chmod 644 '{mp3_file}'")
                return False

            # Check file size
            file_size = mp3_file.stat().st_size
            if file_size == 0:
                logger.error(f"❌ USB file is empty: {mp3_file}")
                return False

            logger.info(f"✅ USB file permissions OK: {mp3_file.name} ({file_size} bytes)")
            return True

        except Exception as e:
            logger.error(f"❌ Error checking USB file permissions: {e}")
            return False

    def get_unprocessed_files(self, mp3_files: List[Path], processed_files: set) -> List[Path]:
        """
        Filter out already processed files.

        Args:
            mp3_files: List of discovered .mp3 files
            processed_files: Set of filenames already processed

        Returns:
            List[Path]: Unprocessed files only
        """
        # Filter out already processed files (compare by filename)
        unprocessed = [f for f in mp3_files if f.name not in processed_files]

        logger.info(f"🔍 Already processed: {len(processed_files)}")
        logger.info(f"📋 New files to process: {len(unprocessed)}")

        return unprocessed
