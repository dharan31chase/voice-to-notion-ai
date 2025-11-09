"""
Base class for transcription backends.

Provides abstract interface that all transcription backends must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple


class BaseTranscriptionBackend(ABC):
    """Abstract base class for transcription backends."""

    @abstractmethod
    def transcribe(self, audio_file: Path) -> Tuple[bool, str, str]:
        """
        Transcribe audio file to text.

        Args:
            audio_file: Path to audio file (.mp3, .wav, .m4a, etc.)

        Returns:
            Tuple[bool, str, str]: (success, transcript_text, error_message)
            - success (bool): True if transcription succeeded
            - transcript_text (str): Transcribed text (empty string if failed)
            - error_message (str): Error description (empty string if succeeded)

        Example:
            >>> backend = SomeBackend()
            >>> success, text, error = backend.transcribe(Path("audio.mp3"))
            >>> if success:
            ...     print(f"Transcript: {text}")
            ... else:
            ...     print(f"Error: {error}")
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this backend is available (API key set, dependencies installed).

        Returns:
            bool: True if backend can be used, False otherwise

        Example:
            >>> backend = GroqBackend(api_key=None)
            >>> backend.is_available()
            False
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get backend name for logging.

        Returns:
            str: Backend name (e.g., "Groq Cloud API", "OpenAI Whisper", "Local Whisper")

        Example:
            >>> backend = GroqBackend()
            >>> backend.get_name()
            'Groq Cloud API'
        """
        pass
