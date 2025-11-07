"""Shared test fixtures and configuration."""
import pytest
from pathlib import Path
from unittest.mock import Mock

# Test fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def test_config():
    """Load test configuration."""
    return {
        "openai": {"model": "gpt-3.5-turbo", "max_tokens": 100},
        "notion": {"timeout": 5},
        "processing": {"max_file_duration_minutes": 5}
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for tests."""
    mock = Mock()
    mock.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content='{"category": "task", "title": "Test Task"}'))]
    )
    return mock


@pytest.fixture
def mock_notion_client():
    """Mock Notion client for tests."""
    mock = Mock()
    mock.pages.create.return_value = {"id": "test_page_id"}
    mock.pages.retrieve.return_value = {"id": "test_page_id", "archived": False}
    return mock


@pytest.fixture
def sample_transcript():
    """Sample transcript for testing."""
    transcript_file = FIXTURES_DIR / "transcripts" / "task_samples.txt"
    if transcript_file.exists():
        return transcript_file.read_text()
    return "Call dentist tomorrow. Task. Life Admin HQ."


@pytest.fixture
def sample_audio():
    """Sample audio file path."""
    audio_file = FIXTURES_DIR / "audio" / "short_task.mp3"
    return audio_file if audio_file.exists() else None
