"""
Groq Cloud API backend for transcription.

Uses Groq's whisper-large-v3 model via their cloud API.
Fastest backend: 1-5 seconds per 3-minute file.
"""

import os
from pathlib import Path
from typing import Tuple
from .base_backend import BaseTranscriptionBackend
from core.logging_utils import get_logger

logger = get_logger(__name__)


class GroqBackend(BaseTranscriptionBackend):
    """
    Groq Cloud API transcription backend.

    Uses whisper-large-v3 model via Groq's cloud API.

    Performance: ~1-5 seconds per 3-minute file (10-20x faster than local)
    Accuracy: ~95-97% (whisper-large-v3)
    Requires: GROQ_API_KEY environment variable
    """

    def __init__(self, config_loader, api_key: str = None):
        """
        Initialize Groq backend.

        Args:
            config_loader: ConfigLoader instance for reading settings
            api_key: Groq API key (if None, reads from GROQ_API_KEY env var)
        """
        self.config = config_loader
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.groq_client = None

        # Initialize Groq client if API key is available
        if self.api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.api_key)
                logger.debug("Groq client initialized successfully")
            except ImportError:
                logger.warning("groq package not installed - run: pip install groq")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")

    def transcribe(self, audio_file: Path) -> Tuple[bool, str, str]:
        """
        Transcribe audio file using Groq Cloud API.

        Args:
            audio_file: Path to audio file

        Returns:
            Tuple[bool, str, str]: (success, transcript_text, error_message)
        """
        if not self.groq_client:
            return (False, "", "Groq client not initialized (API key missing or groq package not installed)")

        try:
            # Get Groq settings from config
            model = self.config.get("transcription.groq.model", "whisper-large-v3")
            timeout = self.config.get("transcription.groq.timeout_seconds", 30)

            logger.debug(f"Transcribing with Groq: {audio_file.name} (model: {model}, timeout: {timeout}s)")

            # Open audio file and send to Groq API
            with open(audio_file, "rb") as f:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(audio_file.name, f.read()),
                    model=model,
                    response_format="text",
                    timeout=timeout
                )

            # Groq returns text directly (not JSON)
            transcript_text = transcription.strip() if isinstance(transcription, str) else str(transcription).strip()

            if len(transcript_text) > 10:  # Basic validation
                logger.info(f"Groq succeeded: {audio_file.name} ({len(transcript_text)} chars)")
                return (True, transcript_text, "")
            else:
                logger.warning(f"Groq transcript too short: {audio_file.name}")
                return (False, "", "Transcript too short (< 10 characters)")

        except ImportError:
            return (False, "", "groq package not installed - run: pip install groq")
        except TimeoutError:
            logger.error(f"Groq timeout: {audio_file.name}")
            return (False, "", "Groq API timeout")
        except Exception as e:
            # Catch all API errors (rate limits, network issues, etc.)
            error_msg = str(e)
            logger.error(f"Groq API error: {audio_file.name} - {error_msg}")
            return (False, "", f"Groq API error: {error_msg}")

    def is_available(self) -> bool:
        """
        Check if Groq backend is available (API key set, package installed).

        Returns:
            bool: True if Groq can be used
        """
        if not self.api_key:
            logger.debug("Groq API key not set (GROQ_API_KEY env var)")
            return False

        if not self.groq_client:
            logger.debug("Groq client not initialized")
            return False

        return True

    def get_name(self) -> str:
        """
        Get backend name for logging.

        Returns:
            str: "Groq Cloud API"
        """
        return "Groq Cloud API"
