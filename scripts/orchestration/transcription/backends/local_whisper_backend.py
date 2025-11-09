"""
Local Whisper backend for transcription.

Uses the local Whisper CLI (installed via `pip install openai-whisper`).
This backend always works offline and serves as the ultimate fallback.
"""

import subprocess
import os
from pathlib import Path
from typing import Tuple
from .base_backend import BaseTranscriptionBackend
from core.logging_utils import get_logger

logger = get_logger(__name__)


class LocalWhisperBackend(BaseTranscriptionBackend):
    """
    Local Whisper transcription backend.

    Uses local Whisper CLI installation. Slowest but most reliable backend
    (always works, even offline).

    Performance: ~90-120 seconds per 3-minute file
    Accuracy: ~95% (depends on model used)
    """

    def __init__(self, config_loader):
        """
        Initialize Local Whisper backend.

        Args:
            config_loader: ConfigLoader instance for reading whisper settings
        """
        self.config = config_loader

    def transcribe(self, audio_file: Path) -> Tuple[bool, str, str]:
        """
        Transcribe audio file using local Whisper CLI.

        Args:
            audio_file: Path to audio file

        Returns:
            Tuple[bool, str, str]: (success, transcript_text, error_message)
        """
        try:
            # Get Whisper settings from config
            whisper_model = self.config.get("whisper.model", "turbo")
            whisper_language = self.config.get("whisper.language", "en")
            whisper_output_format = self.config.get("whisper.output_format", "txt")

            # Create temporary output directory (same directory as audio file)
            output_dir = audio_file.parent
            output_filename = f"{audio_file.stem}.txt"
            output_path = output_dir / output_filename

            # Whisper command
            cmd = [
                'whisper',
                str(audio_file),
                '--model', whisper_model,
                '--language', whisper_language,
                '--output_dir', str(output_dir),
                '--output_format', whisper_output_format
            ]

            logger.debug(f"Local Whisper command: {' '.join(cmd)}")

            # Calculate dynamic timeout based on file size estimate
            # Whisper takes ~0.27x real-time, use 0.5x for safety margin with 20-minute minimum
            file_size_mb = audio_file.stat().st_size / (1024 * 1024)
            estimated_minutes = max(1, file_size_mb)  # Rough estimate: 1 MB ~= 1 minute
            dynamic_timeout = max(1200, int(estimated_minutes * 60 * 0.5))  # 0.5x duration, min 20 min

            logger.debug(f"Using dynamic timeout: {dynamic_timeout}s for {estimated_minutes}-minute estimated file")

            # Run Whisper with dynamic timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=dynamic_timeout)

            if result.returncode == 0 and output_path.exists():
                # Read transcript
                with open(output_path, 'r', encoding='utf-8') as f:
                    transcript_text = f.read().strip()

                if len(transcript_text) > 10:  # Basic validation
                    logger.info(f"Local Whisper succeeded: {audio_file.name}")
                    return (True, transcript_text, "")
                else:
                    logger.warning(f"Local Whisper transcript too short: {audio_file.name}")
                    return (False, "", "Transcript too short (< 10 characters)")
            else:
                error_msg = result.stderr if result.stderr else "Unknown Whisper CLI error"
                logger.error(f"Local Whisper failed: {audio_file.name} - {error_msg}")
                return (False, "", error_msg)

        except subprocess.TimeoutExpired:
            logger.error(f"Local Whisper timeout: {audio_file.name}")
            return (False, "", "Transcription timeout")
        except FileNotFoundError:
            logger.error("Whisper CLI not found - is openai-whisper installed?")
            return (False, "", "Whisper CLI not installed (pip install openai-whisper)")
        except Exception as e:
            logger.error(f"Local Whisper error: {audio_file.name} - {e}")
            return (False, "", str(e))

    def is_available(self) -> bool:
        """
        Check if local Whisper is available (CLI installed).

        Returns:
            bool: True if `whisper` command is available
        """
        try:
            # Check if whisper command exists
            result = subprocess.run(
                ['which', 'whisper'],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.returncode == 0
            if not available:
                logger.debug("Local Whisper CLI not found in PATH")
            return available
        except Exception as e:
            logger.debug(f"Error checking Local Whisper availability: {e}")
            return False

    def get_name(self) -> str:
        """
        Get backend name for logging.

        Returns:
            str: "Local Whisper"
        """
        return "Local Whisper"
