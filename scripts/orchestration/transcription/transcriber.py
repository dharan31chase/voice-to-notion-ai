"""
Transcription Module

Responsibilities:
- Single file transcription via Whisper CLI
- Transcription filtering logic
- File metadata extraction
- Error handling for transcription failures

Does NOT handle:
- Batching (BatchManager)
- Resource monitoring (ResourceMonitor)
- File validation (FileValidator)
"""

import logging
from pathlib import Path
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class Transcriber:
    """Handles audio-to-text transcription using Whisper."""

    def __init__(self, transcripts_folder: Path, config=None):
        """
        Initialize transcriber.

        Args:
            transcripts_folder: Output folder for transcript files
            config: Optional ConfigLoader for transcription settings
        """
        self.transcripts_folder = transcripts_folder
        self.config = config
        self.transcripts_folder.mkdir(exist_ok=True)
        logger.info(f"Transcriber initialized with output: {transcripts_folder}")

    def transcribe(self, audio_file: Path, batch_num: int = 1, file_num: int = 1) -> Tuple[bool, Path, str]:
        """
        Transcribe single audio file using Whisper.

        Args:
            audio_file: Path to audio file (.mp3)
            batch_num: Batch number (for logging)
            file_num: File number within batch (for logging)

        Returns:
            Tuple[bool, Path, str]:
                - success: True if transcription succeeded
                - transcript_path: Path to generated transcript
                - error_message: Error message if failed
        """
        # TODO: Extract from _transcribe_single_file()
        # Should:
        # - Run whisper CLI command
        # - Capture output
        # - Save to transcript file
        # - Handle errors (permission, timeout, etc.)
        # - Return transcript path
        pass

    def should_transcribe(self, audio_file: Path) -> Tuple[bool, str]:
        """
        Determine if audio file should be transcribed.

        Args:
            audio_file: Path to audio file

        Returns:
            Tuple[bool, str]: (should_transcribe, reason_if_skip)
        """
        # TODO: Extract from _should_transcribe_audio()
        # Should check:
        # - Transcript already exists?
        # - File too short?
        # - File corrupted?
        pass

    def extract_metadata(self, file_path: Path) -> Dict:
        """
        Extract metadata from audio file.

        Args:
            file_path: Path to audio file

        Returns:
            Dict: Metadata (duration, size, timestamp, etc.)
        """
        # TODO: Extract from _extract_file_metadata()
        # Should extract:
        # - File size
        # - Creation timestamp
        # - Estimated duration
        pass
