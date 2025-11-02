"""
File Validation Module

Responsibilities:
- Validate file integrity (corruption checks)
- Duration filtering (skip too-short files)
- Transcript validation
- Check dependencies (Whisper, ffmpeg)
- Check disk space availability

Does NOT handle:
- File operations (StagingManager)
- Transcription (Transcriber)
- USB operations (USBDetector)
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class FileValidator:
    """Validates files and system prerequisites for processing."""

    def __init__(self, config=None):
        """
        Initialize file validator.

        Args:
            config: Optional ConfigLoader instance for validation rules
        """
        self.config = config
        logger.info("FileValidator initialized")

    def validate_integrity(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate file integrity (check for corruption).

        Args:
            file_path: Path to audio file

        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        # TODO: Extract from _validate_file_integrity()
        # Should check:
        # - File exists
        # - File size > 0
        # - File is readable
        # - Basic MP3 header validation
        pass

    def validate_duration(self, file_path: Path) -> Tuple[bool, str]:
        """
        Check if file meets minimum duration requirements.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple[bool, str]: (should_process, reason)
                - (True, "") if should process
                - (False, reason) if should skip
        """
        # TODO: Extract from _should_skip_short_file()
        # Should:
        # - Check file size (estimate duration)
        # - Compare against minimum threshold
        # - Return skip reason if too short
        pass

    def validate_transcript(self, transcript_path: Path) -> bool:
        """
        Validate transcript file for AI processing.

        Args:
            transcript_path: Path to transcript text file

        Returns:
            bool: True if valid for processing
        """
        # TODO: Extract from _validate_transcript_for_processing()
        # Should check:
        # - File exists
        # - Not empty
        # - UTF-8 readable
        # - Minimum word count
        pass

    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Check if required dependencies are installed.

        Returns:
            Tuple[bool, List[str]]: (all_available, missing_dependencies)
        """
        # TODO: Extract from _check_whisper_installation()
        # Should check:
        # - whisper CLI available
        # - ffmpeg available
        # - Other required tools
        pass

    def check_disk_space(self, required_mb: float) -> Tuple[bool, float]:
        """
        Check if sufficient disk space is available.

        Args:
            required_mb: Required space in megabytes

        Returns:
            Tuple[bool, float]: (has_space, available_mb)
        """
        # TODO: Extract from _check_disk_space()
        # Should:
        # - Check available space on target drive
        # - Compare against required
        # - Return available space
        pass

    def get_processing_status(self, transcript_path: Path) -> str:
        """
        Get processing status of a transcript.

        Args:
            transcript_path: Path to transcript

        Returns:
            str: Status ("unprocessed", "processed", "failed", etc.)
        """
        # TODO: Extract from _get_transcript_processing_status()
        # Should check:
        # - Corresponding .json file exists
        # - State file for this transcript
        pass
