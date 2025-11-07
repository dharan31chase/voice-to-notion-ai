"""
Transcription Engine Module

Responsibilities:
- Audio-to-text transcription using Whisper
- Intelligent batch processing with work budget balancing
- System resource monitoring (disk, memory, CPU)
- Parallel transcription with ThreadPoolExecutor
- CPU throttling to prevent overload
- Smart retry policy (skip permission/short file errors)
- Duplicate transcript detection
- Transcription state management

Does NOT handle:
- File validation (FileValidator)
- USB operations (USBDetector)
- Staging management (StagingManager)
- Archive management (ArchiveManager)
"""

import os
import shutil
import subprocess
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger(__name__)


class TranscriptionEngine:
    """Handles audio-to-text transcription with batching and resource management."""

    def __init__(self, config, file_validator):
        """
        Initialize transcription engine.

        Args:
            config: ConfigLoader instance for transcription settings
            file_validator: FileValidator instance for dependency checks
        """
        self.config = config
        self.file_validator = file_validator
        logger.info("TranscriptionEngine initialized")

    def extract_file_metadata(self, file_path: Path) -> Dict:
        """
        Extract metadata from audio file.

        Uses file size to estimate duration (1MB H 1 minute).

        Args:
            file_path: Path to audio file

        Returns:
            Dict: Metadata with name, size_mb, timestamps, estimated_minutes
        """
        try:
            stat = file_path.stat()
            file_size_mb = stat.st_size / (1024 * 1024)  # Convert to MB

            # Estimate duration based on file size (rough approximation)
            # Assuming ~1MB per minute for typical voice recording
            estimated_minutes = int(file_size_mb)

            return {
                "name": file_path.name,
                "size_mb": round(file_size_mb, 1),
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "estimated_minutes": estimated_minutes,
                "path": str(file_path)
            }
        except Exception as e:
            logger.error(f"L Error extracting metadata for {file_path.name}: {e}")
            return {
                "name": file_path.name,
                "size_mb": 0,
                "created_time": None,
                "modified_time": None,
                "estimated_minutes": 0,
                "path": str(file_path),
                "error": str(e)
            }

    def check_system_resources(self, project_root: Path) -> Tuple[bool, Dict]:
        """
        Check if system has sufficient resources for transcription.

        Requirements:
        - Disk space: >500MB free
        - Memory: >1GB available (if psutil installed)

        Args:
            project_root: Project root directory to check space for

        Returns:
            Tuple[bool, Dict]: (resources_ok, resource_status)
        """
        try:
            # Check disk space
            total, used, free = shutil.disk_usage(project_root)
            free_gb = free / (1024**3)

            # Check available memory (rough estimate)
            try:
                import psutil
                memory = psutil.virtual_memory()
                available_gb = memory.available / (1024**3)
                memory_ok = available_gb > 1.0
                memory_available = round(available_gb, 2)
            except ImportError:
                logger.debug("psutil not available, skipping memory check")
                memory_ok = True  # Assume OK if we can't check
                memory_available = "Unknown"

            # Requirements: 500MB free disk, 1GB available memory
            disk_ok = free_gb > 0.5

            resource_status = {
                "disk_free_gb": round(free_gb, 2),
                "disk_ok": disk_ok,
                "memory_available_gb": memory_available,
                "memory_ok": memory_ok,
                "all_ok": disk_ok and memory_ok
            }

            if not resource_status["all_ok"]:
