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

import os
import subprocess
import shutil
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
        Validate .mp3 file integrity.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                return False, "File does not exist"

            # Check file size (should be > 0 bytes)
            file_size = file_path.stat().st_size
            if file_size == 0:
                return False, "File is empty (0 bytes)"

            # Check if file is readable
            with open(file_path, 'rb') as f:
                f.read(1024)  # Read first 1KB to test access

            # Basic .mp3 validation (check file extension and size)
            if file_path.suffix.lower() != '.mp3':
                return False, "File is not .mp3 format"

            # Log file info
            logger.debug(f"✅ File validated: {file_path.name} ({file_size} bytes)")
            return True, "OK"

        except Exception as e:
            return False, f"Validation error: {e}"

    def validate_duration(self, file_path: Path) -> Tuple[bool, str]:
        """
        Check if file meets minimum duration requirements.

        Uses file size estimate: 1MB ≈ 1 minute, so 33KB ≈ 2 seconds

        Args:
            file_path: Path to audio file

        Returns:
            Tuple[bool, str]: (is_valid, reason)
                - (True, "") if duration is acceptable
                - (False, reason) if file is too short
        """
        try:
            skip_threshold_seconds = self.config.get("processing.skip_short_audio_seconds", 2) if self.config else 2
            skip_threshold_bytes = skip_threshold_seconds * 33 * 1024  # 33KB per 2 seconds

            file_size = file_path.stat().st_size

            if file_size < skip_threshold_bytes:
                estimated_seconds = file_size / (33 * 1024) * 2
                reason = f"File too short (~{estimated_seconds:.1f}s, minimum {skip_threshold_seconds}s)"
                return False, reason  # INVERTED: False = invalid/skip

            return True, ""  # INVERTED: True = valid/process

        except Exception as e:
            logger.error(f"❌ Error checking file size for {file_path.name}: {e}")
            return True, ""  # On error, allow processing (fail-open)

    def validate_transcript(self, transcript_path: Path, project_root: Path) -> bool:
        """
        Validate that a transcript is ready for AI processing.

        Args:
            transcript_path: Path to transcript text file
            project_root: Project root directory

        Returns:
            bool: True if valid for processing
        """
        try:
            if not transcript_path.exists():
                logger.warning(f"⚠️ Transcript file not found: {transcript_path}")
                return False

            # Check file size
            file_size = transcript_path.stat().st_size
            if file_size < 10:  # Less than 10 bytes
                logger.warning(f"⚠️ Transcript too small: {transcript_path} ({file_size} bytes)")
                return False

            # Check if already processed
            processed_file = project_root / "processed" / f"{transcript_path.stem}_processed.json"
            if processed_file.exists():
                logger.info(f"ℹ️ Transcript already processed: {transcript_path.stem}")
                return False

            # Read and validate content
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            if len(content) < 10:
                logger.warning(f"⚠️ Transcript content too short: {transcript_path}")
                return False

            logger.info(f"✅ Transcript validated: {transcript_path.name} ({file_size} bytes, {len(content)} chars)")
            return True

        except Exception as e:
            logger.error(f"❌ Error validating transcript {transcript_path}: {e}")
            return False

    def check_dependencies(self) -> bool:
        """
        Check if Whisper is installed and accessible.

        Returns:
            bool: True if Whisper is available
        """
        try:
            result = subprocess.run(['whisper', '--help'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ Whisper CLI found and accessible")
                return True
            else:
                logger.error("❌ Whisper CLI not working properly")
                return False

        except FileNotFoundError:
            logger.error("❌ Whisper CLI not found. Please install: pip install openai-whisper")
            return False

        except Exception as e:
            logger.error(f"❌ Error checking Whisper: {e}")
            return False

    def check_disk_space(self, project_root: Path, required_mb: float) -> bool:
        """
        Check if sufficient disk space is available.

        Args:
            project_root: Project root directory to check space for
            required_mb: Required space in megabytes

        Returns:
            bool: True if sufficient space available
        """
        try:
            total, used, free = shutil.disk_usage(project_root)
            free_mb = free / (1024 * 1024)

            if free_mb < required_mb:
                logger.error(f"❌ Insufficient disk space: {free_mb:.1f}MB available, {required_mb:.1f}MB required")
                return False

            logger.info(f"✅ Disk space OK: {free_mb:.1f}MB available, {required_mb:.1f}MB required")
            return True

        except Exception as e:
            logger.error(f"❌ Error checking disk space: {e}")
            return False
