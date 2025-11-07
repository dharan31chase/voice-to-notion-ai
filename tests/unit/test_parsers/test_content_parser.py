"""Unit tests for ContentParser."""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root / "scripts"))

from parsers.content_parser import ContentParser


@pytest.mark.unit
class TestContentParser:
    """Test content parsing logic."""

    def test_detect_task_category(self):
        """Test task category detection."""
        parser = ContentParser()
        content = "Need to call the dentist tomorrow. Task."
        result = parser.parse(content)
        assert result["category"] == "task", f"Expected 'task', got '{result['category']}'"

    def test_detect_note_category(self):
        """Test note category detection."""
        parser = ContentParser()
        content = "I noticed that project management is improving. Note."
        result = parser.parse(content)
        assert result["category"] == "note", f"Expected 'note', got '{result['category']}'"

    def test_passive_content_defaults_to_note(self):
        """Test passive content defaults to note (Milestone 2.1 requirement)."""
        parser = ContentParser()
        content = "Some random observation about the weather."
        result = parser.parse(content)
        assert result["category"] == "note", \
            f"Passive content should default to 'note', got '{result['category']}'"

    def test_detect_unclear_category(self):
        """Test unclear category detection."""
        parser = ContentParser()
        content = "This is ambiguous content without clear markers."
        result = parser.parse(content)
        # Should either be 'note' (default) or 'unclear'
        assert result["category"] in ["note", "unclear"], \
            f"Expected 'note' or 'unclear', got '{result['category']}'"
