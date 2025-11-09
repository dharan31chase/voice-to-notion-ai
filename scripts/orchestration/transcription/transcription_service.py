"""
TranscriptionService - Abstraction layer for transcription backends.

Manages backend selection and automatic fallback chain:
Groq Cloud API → Local Whisper

This service ensures 100% uptime by always falling back to local Whisper
if cloud services are unavailable.
"""

from pathlib import Path
from typing import Tuple, List
from .backends import GroqBackend, LocalWhisperBackend
from core.logging_utils import get_logger

logger = get_logger(__name__)


class TranscriptionService:
    """
    Transcription service with automatic backend selection and fallback.

    Manages multiple transcription backends and automatically falls back
    if the primary backend fails.

    Backend priority:
    1. Groq Cloud API (fastest: 1-5 sec/file)
    2. Local Whisper (slowest but reliable: 90-120 sec/file)
    """

    def __init__(self, config_loader):
        """
        Initialize TranscriptionService with available backends.

        Args:
            config_loader: ConfigLoader instance for reading settings
        """
        self.config = config_loader
        self.backends: List = []
        self.active_backend_name = None

        # Initialize backends based on config
        backend_mode = self.config.get("transcription.backend", "auto")

        logger.info(f"Initializing TranscriptionService (mode: {backend_mode})")

        if backend_mode == "auto":
            # Auto mode: Try Groq first, then Local
            self._init_auto_mode()
        elif backend_mode == "groq":
            # Groq only mode
            self._init_groq_only()
        elif backend_mode == "local":
            # Local only mode
            self._init_local_only()
        else:
            logger.warning(f"Unknown backend mode '{backend_mode}', defaulting to auto")
            self._init_auto_mode()

        # Log available backends
        available_backends = [b.get_name() for b in self.backends if b.is_available()]
        if available_backends:
            logger.info(f"Available backends: {', '.join(available_backends)}")
        else:
            logger.error("No transcription backends available!")

    def _init_auto_mode(self):
        """Initialize backends for auto mode (Groq → Local)."""
        # Try Groq first
        groq = GroqBackend(self.config)
        if groq.is_available():
            self.backends.append(groq)
            logger.debug("Groq backend available")
        else:
            logger.debug("Groq backend not available (API key missing or package not installed)")

        # Always add Local as fallback
        local = LocalWhisperBackend(self.config)
        if local.is_available():
            self.backends.append(local)
            logger.debug("Local Whisper backend available")
        else:
            logger.warning("Local Whisper backend not available (whisper CLI not installed)")

    def _init_groq_only(self):
        """Initialize Groq backend only."""
        groq = GroqBackend(self.config)
        if groq.is_available():
            self.backends.append(groq)
            logger.debug("Groq-only mode activated")
        else:
            logger.error("Groq-only mode but Groq not available!")

    def _init_local_only(self):
        """Initialize Local Whisper backend only."""
        local = LocalWhisperBackend(self.config)
        if local.is_available():
            self.backends.append(local)
            logger.debug("Local-only mode activated")
        else:
            logger.error("Local-only mode but Local Whisper not available!")

    def transcribe_file(self, audio_file: Path) -> Tuple[bool, str, str]:
        """
        Transcribe audio file using best available backend with automatic fallback.

        Args:
            audio_file: Path to audio file

        Returns:
            Tuple[bool, str, str]: (success, transcript_text, error_message)
            - success (bool): True if transcription succeeded
            - transcript_text (str): Transcribed text (empty if failed)
            - error_message (str): Error description (empty if succeeded)

        Example:
            >>> service = TranscriptionService(config)
            >>> success, text, error = service.transcribe_file(Path("audio.mp3"))
            >>> if success:
            ...     print(f"Transcript: {text}")
        """
        if not self.backends:
            error_msg = "No transcription backends available"
            logger.error(error_msg)
            return (False, "", error_msg)

        # Try each backend in order
        for backend in self.backends:
            if not backend.is_available():
                logger.debug(f"{backend.get_name()} not available, skipping")
                continue

            logger.info(f"Trying {backend.get_name()}...")
            success, transcript, error = backend.transcribe(audio_file)

            if success:
                logger.info(f"✓ {backend.get_name()} succeeded ({len(transcript)} chars)")
                self.active_backend_name = backend.get_name()
                return (True, transcript, "")
            else:
                logger.warning(f"✗ {backend.get_name()} failed: {error}")
                # Continue to next backend

        # All backends failed
        error_msg = "All transcription backends failed"
        logger.error(error_msg)
        return (False, "", error_msg)

    def get_active_backend(self) -> str:
        """
        Get name of last successfully used backend.

        Returns:
            str: Backend name (e.g., "Groq Cloud API", "Local Whisper")
                 or "None" if no backend has succeeded yet
        """
        return self.active_backend_name or "None"

    def get_available_backends(self) -> List[str]:
        """
        Get list of available backend names.

        Returns:
            List[str]: Names of backends that are currently available
        """
        return [b.get_name() for b in self.backends if b.is_available()]
