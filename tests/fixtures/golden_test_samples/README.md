# Golden Test Samples

This directory contains real MP3 recordings used for golden tests and manual review validation.

## Purpose
These samples represent actual voice recordings processed by the system, allowing us to:
1. Verify system behavior remains consistent over time (golden tests)
2. Test improvements against real-world data
3. Manually review processing accuracy
4. Debug category detection, project matching, and icon selection

## Structure

### session_20251106_112341/
**Date**: November 6, 2025
**Files**: 12 MP3 recordings
**Session Success Rate**: 95% (56/59 files)
**Processing Time**: 29.6 minutes

**Contents**:
- 251103_1719.mp3 - Baby room task (🛒 Welcoming our baby)
- 251104_0806.mp3 - Interview prep task (📋 No project - NEEDS REVIEW)
- 251104_1646.mp3 - Mental health note (🍎 No project)
- 251104_1708.mp3 - Relationship note (🛒 No project)
- 251104_1937.mp3 - Baby room layout (👶 Welcoming our baby)
- 251105_1251.mp3 - [pending analysis]
- 251105_1543.mp3 - [pending analysis]
- 251105_1847.mp3 - [pending analysis]
- 251105_1848.mp3 - [pending analysis]
- 251106_0748.mp3 - Mental health task (FAILED - content length)
- 251106_0851.mp3 - Mastery exploration (FAILED - content length)
- 251106_1003.mp3 - [pending analysis]

**Test Coverage**:
- ✅ Task detection
- ✅ Note detection
- ✅ Project matching (successful & failed)
- ✅ Icon selection (various contexts)
- ✅ Content length edge cases
- ✅ Multi-task bundling
- ✅ Personal vs work content

## Usage

### Golden Tests
```python
import pytest
from pathlib import Path

GOLDEN_SAMPLES = Path("tests/fixtures/golden_test_samples/session_20251106_112341")

@pytest.mark.parametrize("mp3_file", GOLDEN_SAMPLES.glob("*.mp3"))
def test_processing_consistency(mp3_file):
    """Verify processing produces consistent results"""
    # Transcribe
    transcript = transcribe_audio(mp3_file)

    # Process
    analysis = process_transcript(transcript)

    # Compare against expected results
    expected = load_expected_results(mp3_file.stem)
    assert_analysis_matches(analysis, expected)
```

### Manual Review
See `docs/manual-review-queue.md` for detailed review process.

## Maintenance

### Adding New Samples
```bash
# Copy from session archive
cp "Recording Archives/YYYY-MM-DD/session_*/file.mp3" \
   "tests/fixtures/golden_test_samples/session_YYYYMMDD_HHMMSS/"

# Update this README with file details
```

### Removing Samples
Only remove samples that are:
- No longer representative of system behavior
- Duplicate coverage of same scenario
- Contain sensitive/private information that should not be in tests

**Important**: Never remove samples that represent edge cases or known failure modes.

## Privacy Note

These files contain personal voice recordings. They are:
- ✅ Stored locally only (not in git)
- ✅ Used only for testing and development
- ❌ Never uploaded to cloud services
- ❌ Never shared outside the development team

`.gitignore` is configured to exclude `*.mp3` files from version control.

---

*Last Updated: November 6, 2025*
*Session: 20251106_112341*
