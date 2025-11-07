"""Unit tests for TranscriptionEngine (critical component)."""
import pytest

# TODO (Phase 3 - Week 4): Add comprehensive TranscriptionEngine tests
#
# Priority tests needed:
# 1. Test extract_file_metadata() - verify duration estimation (1MB ≈ 1 min)
# 2. Test dynamic timeout calculation (inline at line 316-317)
#    - Short files (3 min) → 20 min timeout (minimum)
#    - Long files (40 min) → 20 min timeout (0.5x duration)
#    - Very long files (100 min) → 50 min timeout
# 3. Test batch transcription with resource monitoring
# 4. Test duration-aware batch balancing
#
# Actual implementation requires:
# - TranscriptionEngine(config, file_validator)
# - extract_file_metadata(file_path) - public method (no underscore)
# - Timeout calculation is inline (max(1200, int(estimated_minutes * 60 * 0.5)))
#
# See docs/testing-roadmap.md Phase 3 for test implementation plan.


@pytest.mark.unit
@pytest.mark.skip(reason="TODO: Add TranscriptionEngine tests in Phase 3 (Week 4)")
class TestTranscriptionEngine:
    """Placeholder for TranscriptionEngine tests."""

    def test_placeholder(self):
        """Placeholder test - to be implemented in Phase 3."""
        pass
