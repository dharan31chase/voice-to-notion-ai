"""
Unit tests for Context Profile Optimization

Tests core functions:
- parse_user_selection
- classify_file_type
- find_project
- Profile saving/loading
"""

import pytest
import sys
from pathlib import Path

# Add mcp_server to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "mcp_server"))

from full_server import (
    parse_user_selection,
    classify_file_type,
    find_project,
    save_profile,
    load_profile
)


class TestParseUserSelection:
    """Test user input parsing for file selection."""

    def test_parse_comma_separated(self):
        """Test parsing '1,2,3' format."""
        options = [{"path": "file1.md"}, {"path": "file2.md"}, {"path": "file3.md"}]
        result = parse_user_selection("1,2,3", options)
        assert result == [0, 1, 2]

    def test_parse_all(self):
        """Test parsing 'all' keyword."""
        options = [{"path": "file1.md"}, {"path": "file2.md"}, {"path": "file3.md"}]
        result = parse_user_selection("all", options)
        assert result == [0, 1, 2]

    def test_parse_empty(self):
        """Test parsing empty string (confirm learned profile)."""
        options = [{"path": "file1.md"}, {"path": "file2.md"}]
        result = parse_user_selection("", options)
        assert result == [0, 1]

    def test_parse_subset(self):
        """Test parsing subset '1,3'."""
        options = [{"path": "file1.md"}, {"path": "file2.md"}, {"path": "file3.md"}]
        result = parse_user_selection("1,3", options)
        assert result == [0, 2]

    def test_parse_invalid_index(self):
        """Test invalid index raises ValueError."""
        options = [{"path": "file1.md"}, {"path": "file2.md"}]
        with pytest.raises(ValueError, match="out of range"):
            parse_user_selection("1,5", options)

    def test_parse_invalid_format(self):
        """Test invalid format raises ValueError."""
        options = [{"path": "file1.md"}]
        with pytest.raises(ValueError, match="Invalid selection"):
            parse_user_selection("abc", options)


class TestClassifyFileType:
    """Test file type classification."""

    def test_classify_always(self):
        """Test 'always' type files."""
        assert classify_file_type("requirements-vision.md") == "always"
        assert classify_file_type("docs/roadmap.md") == "always"
        assert classify_file_type("product-strategy.md") == "always"

    def test_classify_exemplar(self):
        """Test 'exemplar' type files."""
        assert classify_file_type("interview-guide-exemplar.md") == "exemplar"
        assert classify_file_type("analyses/bob-missy-exemplar.md") == "exemplar"
        assert classify_file_type("reference-template.md") == "exemplar"

    def test_classify_synthesis(self):
        """Test 'synthesis' type files."""
        assert classify_file_type("segment-meta-analysis.md") == "synthesis"
        assert classify_file_type("comparison-report.md") == "synthesis"
        assert classify_file_type("validation-study.md") == "synthesis"

    def test_classify_optional(self):
        """Test 'optional' type (default)."""
        assert classify_file_type("random-notes.md") == "optional"
        assert classify_file_type("meeting-log.md") == "optional"


class TestFindProject:
    """Test project finding with aliases and fuzzy matching."""

    def test_exact_match(self):
        """Test exact project name match."""
        project = find_project("Legacy AI")
        assert project is not None
        assert project["name"] == "Legacy AI"

    def test_alias_match(self):
        """Test alias matching."""
        project = find_project("customer discovery")
        assert project is not None
        assert project["name"] == "Legacy AI"

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        project = find_project("legacy ai")
        assert project is not None
        assert project["name"] == "Legacy AI"

    def test_fuzzy_match(self):
        """Test substring matching."""
        project = find_project("legacy")
        assert project is not None
        assert project["name"] == "Legacy AI"

    def test_not_found(self):
        """Test project not found returns None."""
        project = find_project("Nonexistent Project")
        assert project is None


class TestProfileSaveLoad:
    """Test profile persistence."""

    def test_save_and_load_profile(self):
        """Test saving and loading a profile."""
        # Save a test profile
        test_files = [
            {"path": "file1.md", "type": "always"},
            {"path": "file2.md", "type": "latest"}
        ]

        save_profile("Test Project", "test-workstream", test_files)

        # Load it back
        profile = load_profile("Test Project", "test-workstream")

        assert profile is not None
        assert profile["usage_count"] == 1
        assert len(profile["files"]) == 2
        assert profile["files"][0]["path"] == "file1.md"
        assert profile["files"][1]["path"] == "file2.md"

    def test_update_existing_profile(self):
        """Test updating existing profile increments usage_count."""
        test_files = [{"path": "file1.md", "type": "always"}]

        # Save twice
        save_profile("Test Project 2", "test-workstream", test_files)
        save_profile("Test Project 2", "test-workstream", test_files)

        # Load and check usage_count
        profile = load_profile("Test Project 2", "test-workstream")
        assert profile["usage_count"] == 2

    def test_load_nonexistent_profile(self):
        """Test loading non-existent profile returns None."""
        profile = load_profile("Nonexistent Project", "nonexistent-workstream")
        assert profile is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
