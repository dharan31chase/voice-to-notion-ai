# Testing Roadmap - AI Assistant Project
**Created**: November 4, 2025
**Status**: Phase 1 (Minimal Setup) - In Progress
**Purpose**: Comprehensive testing strategy and implementation plan

---

## 📊 Executive Summary

This document outlines the testing strategy for the AI Assistant project, designed to:
1. **Prevent regressions** as refactoring continues (Phase B Step 7 in progress)
2. **Ensure data integrity** (top priority - prevent data loss)
3. **Maintain performance targets** (8-10 min transcription, 96%+ success rate)
4. **Enable confident development** through TDD (Test-Driven Development)
5. **Serve as reusable template** for future projects

---

## 🎯 Key Decisions Made (November 4, 2025)

### Priority Hierarchy
1. **Data Integrity** (P0) - Prevent data loss, ensure file safety
2. **Performance** (P1) - Maintain speed targets (8-10 min processing)
3. **Quality Output** (P2) - Ensure AI accuracy and Notion integration

### Testing Philosophy
- **Approach**: Minimal setup today → Expand weekly
- **TDD**: Write tests first, then code (reduces ambiguity, ensures alignment)
- **Time Investment**: 1 day/week on testing infrastructure
- **Risk Tolerance**: Balanced (production stability vs. rapid development)

### Infrastructure Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Test Accounts** | Separate test workspace/APIs | Industry standard, prevents production pollution |
| **Test Configuration** | Dedicated `config/test.yaml` | Clear separation, cheaper models for tests |
| **CI/CD Frequency** | Daily scheduled (9 AM) + main branch | Cost-effective, catches regressions without slowing dev |
| **Test Organization** | `tests/` with unit/integration/e2e | Standard pytest structure |
| **Test Data Source** | Copied from production | Real-world edge cases |
| **Coverage Target** | 70% (industry standard) | Balanced effort vs. value |
| **Test Requirements** | Required for new features/bugs | Enforced at session end |

---

## 📁 Test Structure (Final State)

```
tests/
├── __init__.py
├── conftest.py                  # Shared fixtures and configuration
├── pytest.ini                   # Pytest configuration
│
├── unit/                        # Fast, isolated tests (70% of tests)
│   ├── __init__.py
│   ├── test_parsers/
│   │   ├── test_content_parser.py
│   │   ├── test_project_extractor.py
│   │   └── test_transcript_validator.py
│   ├── test_analyzers/
│   │   ├── test_task_analyzer.py
│   │   └── test_note_analyzer.py
│   ├── test_routers/
│   │   ├── test_duration_estimator.py
│   │   ├── test_tag_detector.py
│   │   ├── test_icon_selector.py
│   │   └── test_project_detector.py
│   ├── test_orchestration/
│   │   ├── test_state_manager.py
│   │   ├── test_usb_detector.py
│   │   ├── test_file_validator.py
│   │   ├── test_staging_manager.py
│   │   ├── test_transcription_engine.py
│   │   ├── test_processing_engine.py
│   │   ├── test_archive_manager.py
│   │   └── test_cleanup_manager.py
│   └── test_validators/
│       └── test_notion_validator.py
│
├── integration/                 # Multi-component tests (20% of tests)
│   ├── __init__.py
│   ├── test_transcript_processing.py    # process_transcripts.py workflow
│   ├── test_notion_integration.py       # Notion API integration
│   ├── test_orchestrator_steps.py       # Step-by-step orchestrator
│   └── test_ai_pipeline.py             # OpenAI → Analysis → Notion
│
├── e2e/                         # Full workflow tests (10% of tests)
│   ├── __init__.py
│   ├── test_manual_workflow.py          # Manual transcription workflow
│   └── test_usb_workflow.py            # USB recorder end-to-end
│
├── fixtures/                    # Test data (version controlled)
│   ├── __init__.py
│   ├── audio/                   # Test audio files (copied from production)
│   │   ├── short_task.mp3       # <1 min, single task
│   │   ├── long_note.mp3        # 5+ min, long-form content
│   │   ├── multiple_tasks.mp3   # 2-3 min, multiple tasks
│   │   └── edge_cases/
│   │       ├── very_short.mp3   # <2 sec (should skip)
│   │       ├── corrupt.mp3      # Corrupted file
│   │       └── silent.mp3       # Silent audio
│   ├── transcripts/             # Sample transcripts
│   │   ├── task_samples.txt
│   │   ├── note_samples.txt
│   │   ├── multiple_tasks.txt
│   │   └── edge_cases/
│   │       ├── empty.txt
│   │       ├── malformed.txt
│   │       └── very_long.txt
│   ├── configs/                 # Test configurations
│   │   └── test.yaml            # Test-specific config
│   └── expected_outputs/        # Known good results
│       ├── task_analysis.json
│       └── note_analysis.json
│
├── utils/                       # Test utilities
│   ├── __init__.py
│   ├── mocks.py                # Mock objects (Notion, OpenAI clients)
│   ├── helpers.py              # Test helpers (assert functions)
│   └── performance.py          # Performance benchmarking utilities
│
└── reports/                     # Test reports (gitignored)
    ├── coverage/               # Coverage reports
    ├── performance/            # Performance benchmarks
    └── regression/             # Regression test results
```

---

## 🚀 Phase 1: Minimal Setup (Today - November 4, 2025)

**Goal**: Foundation for testing infrastructure
**Time**: 2-3 hours
**Scope**: Minimal viable testing setup

### Tasks

#### 1. Create Directory Structure ✅
```bash
mkdir -p logs
mkdir -p tests/{unit,integration,e2e,fixtures,utils,reports}
mkdir -p tests/fixtures/{audio,transcripts,configs,expected_outputs}
mkdir -p tests/unit/{test_parsers,test_analyzers,test_routers,test_orchestration,test_validators}
```

#### 2. Move Test Logs ✅
```bash
# Move existing test logs from /tmp/ to logs/
mv /tmp/orchestrator_*.log logs/ 2>/dev/null || true
mv /tmp/hotspot_test_run.log logs/ 2>/dev/null || true

# Create .gitignore for logs
echo "*.log" > logs/.gitignore
echo "!.gitignore" >> logs/.gitignore
```

#### 3. Organize Existing Test Scripts ✅
```bash
# Move test scripts to proper locations
mv scripts/test_step5.py tests/integration/test_orchestrator_steps.py
mv scripts/cleanup_test_entries.py tests/utils/cleanup_notion_entries.py
mv test_migration_comparison.py tests/integration/test_migration_comparison.py
```

#### 4. Install pytest Framework ✅
```bash
# Add to requirements.txt
echo "pytest==7.4.3" >> requirements.txt
echo "pytest-cov==4.1.0" >> requirements.txt
echo "pytest-mock==3.12.0" >> requirements.txt

# Install
pip install pytest pytest-cov pytest-mock
```

#### 5. Create pytest Configuration ✅
**File**: `tests/pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --color=yes
    --strict-markers
    --tb=short
    --cov=scripts
    --cov-report=term-missing
    --cov-report=html:tests/reports/coverage
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (multi-component)
    e2e: End-to-end tests (full workflow)
    slow: Tests that take >5 seconds
    requires_api: Tests that require API access
```

#### 6. Create Shared Test Configuration ✅
**File**: `tests/conftest.py`
```python
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
    return (FIXTURES_DIR / "transcripts" / "task_samples.txt").read_text()

@pytest.fixture
def sample_audio():
    """Sample audio file path."""
    return FIXTURES_DIR / "audio" / "short_task.mp3"
```

#### 7. Write Example Tests (Critical Paths) ✅

**File**: `tests/unit/test_parsers/test_content_parser.py`
```python
"""Unit tests for ContentParser."""
import pytest
from scripts.parsers.content_parser import ContentParser

@pytest.mark.unit
class TestContentParser:
    """Test content parsing logic."""

    def test_detect_task_category(self):
        """Test task category detection."""
        parser = ContentParser()
        content = "Need to call the dentist tomorrow. Task."
        result = parser.parse(content)
        assert result["category"] == "task"

    def test_detect_note_category(self):
        """Test note category detection."""
        parser = ContentParser()
        content = "I noticed that project management is improving. Note."
        result = parser.parse(content)
        assert result["category"] == "note"

    def test_passive_content_defaults_to_note(self):
        """Test passive content defaults to note (Milestone 2.1 requirement)."""
        parser = ContentParser()
        content = "Some random observation about the weather."
        result = parser.parse(content)
        assert result["category"] == "note"
```

**File**: `tests/integration/test_transcript_processing.py`
```python
"""Integration tests for transcript processing workflow."""
import pytest
from pathlib import Path
from scripts.process_transcripts import process_transcript_file

@pytest.mark.integration
class TestTranscriptProcessing:
    """Test full transcript processing pipeline."""

    def test_process_single_task(self, tmp_path, mock_openai_client, mock_notion_client):
        """Test processing single task transcript."""
        # Create test transcript
        transcript = tmp_path / "test.txt"
        transcript.write_text("Call dentist tomorrow. Task. Life Admin HQ.")

        # Process (with mocked APIs)
        result = process_transcript_file(
            transcript,
            dry_run=True,  # Don't actually create Notion entries
            openai_client=mock_openai_client,
            notion_client=mock_notion_client
        )

        # Verify
        assert result["category"] == "task"
        assert "dentist" in result["title"].lower()
```

**File**: `tests/unit/test_orchestration/test_transcription_engine.py`
```python
"""Unit tests for TranscriptionEngine (critical component)."""
import pytest
from pathlib import Path
from scripts.orchestration.transcription.transcription_engine import TranscriptionEngine

@pytest.mark.unit
class TestTranscriptionEngine:
    """Test transcription engine logic."""

    def test_calculate_dynamic_timeout(self):
        """Test dynamic timeout calculation (prevent timeout failures)."""
        engine = TranscriptionEngine(recorder_path=Path("/tmp"))

        # Short file (3 min) → 20 min timeout (minimum)
        timeout = engine._calculate_timeout(estimated_minutes=3)
        assert timeout == 1200  # 20 minutes

        # Long file (40 min) → 20 min timeout (0.5x duration)
        timeout = engine._calculate_timeout(estimated_minutes=40)
        assert timeout == 1200  # 20 minutes (0.5 * 40 = 20)

        # Very long file (100 min) → 50 min timeout
        timeout = engine._calculate_timeout(estimated_minutes=100)
        assert timeout == 3000  # 50 minutes (0.5 * 100)
```

#### 8. Create Test Data Samples ✅
**File**: `tests/fixtures/transcripts/task_samples.txt`
```
Call dentist tomorrow morning to schedule cleaning. Task. Life Admin HQ.
```

**File**: `tests/fixtures/transcripts/note_samples.txt`
```
I noticed that my productivity improves when I take breaks every hour. This is something I should remember. Note. Project Eudaimonia.
```

#### 9. Update README.md ✅
Add testing section:
```markdown
## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# End-to-end tests (slow)
pytest -m e2e
```

### Run with Coverage
```bash
pytest --cov=scripts --cov-report=html
open tests/reports/coverage/index.html
```

### Run Specific Test File
```bash
pytest tests/unit/test_parsers/test_content_parser.py -v
```

### Test-Driven Development Workflow
```bash
# 1. Write failing test first
pytest tests/unit/test_new_feature.py

# 2. Implement feature until test passes
# ... edit code ...

# 3. Verify test passes
pytest tests/unit/test_new_feature.py

# 4. Run full test suite
pytest
```
```

#### 10. Create Performance Benchmark Infrastructure ✅
**Time**: 30 minutes
**Priority**: P0 (reproducibility)

**Purpose**: Establish baseline for performance regression detection

**Tasks:**
```bash
# Create benchmark directory structure
mkdir -p logs/benchmarks

# Create golden baseline file (template)
cat > logs/benchmarks/golden.json <<EOF
{
  "run_id": "baseline-2025-11-02",
  "date": "2025-11-02",
  "commit": "88ff47a",
  "transcription_duration_sec": 480,
  "ai_processing_duration_sec": 45,
  "total_duration_sec": 525,
  "files_processed": 5,
  "success_count": 5,
  "failure_count": 0,
  "success_rate": 1.0,
  "notes": "Baseline from real-world test (5 files, 96% success rate)"
}
EOF
```

**Create Benchmark Utility**: `tests/utils/performance.py`
```python
"""Performance benchmarking utilities."""
import json
from datetime import datetime
from pathlib import Path

BENCHMARKS_DIR = Path("logs/benchmarks")

def save_benchmark(metrics: dict, run_id: str = None):
    """Save benchmark results to JSON file."""
    if run_id is None:
        run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    metrics["run_id"] = run_id
    metrics["date"] = datetime.now().strftime("%Y-%m-%d")

    output_file = BENCHMARKS_DIR / f"{run_id}.json"
    output_file.write_text(json.dumps(metrics, indent=2))
    return output_file

def load_golden_baseline():
    """Load golden baseline for comparison."""
    golden_file = BENCHMARKS_DIR / "golden.json"
    if not golden_file.exists():
        return None
    return json.loads(golden_file.read_text())

def compare_to_baseline(current_metrics: dict, threshold: float = 0.20):
    """
    Compare current metrics to golden baseline.

    Args:
        current_metrics: Current benchmark results
        threshold: Alert if degradation > this % (default 20%)

    Returns:
        dict: Comparison results with alerts
    """
    baseline = load_golden_baseline()
    if not baseline:
        return {"status": "no_baseline", "alerts": []}

    alerts = []

    # Check transcription duration
    baseline_duration = baseline.get("transcription_duration_sec", 0)
    current_duration = current_metrics.get("transcription_duration_sec", 0)
    if baseline_duration > 0:
        degradation = (current_duration - baseline_duration) / baseline_duration
        if degradation > threshold:
            alerts.append(
                f"Transcription {degradation*100:.1f}% slower "
                f"({current_duration}s vs {baseline_duration}s baseline)"
            )

    # Check success rate
    baseline_rate = baseline.get("success_rate", 1.0)
    current_rate = current_metrics.get("success_rate", 1.0)
    if current_rate < baseline_rate - threshold:
        alerts.append(
            f"Success rate dropped {(baseline_rate-current_rate)*100:.1f}% "
            f"({current_rate*100:.0f}% vs {baseline_rate*100:.0f}% baseline)"
        )

    return {
        "status": "regression" if alerts else "ok",
        "alerts": alerts,
        "baseline": baseline,
        "current": current_metrics
    }
```

**Update `.gitignore`:**
```
logs/benchmarks/*.json
!logs/benchmarks/golden.json
```

---

#### 11. Create Structured Logging Standards ✅
**Time**: 20 minutes
**Priority**: P0 (debugging, CI artifacts)

**Purpose**: Date-stamped logs with run IDs for traceability

**Tasks:**
```bash
# Create dated log directories
mkdir -p logs/$(date +%Y-%m-%d)

# Create logging config template
```

**File**: `scripts/utils/logging_config.py`
```python
"""Centralized logging configuration."""
import logging
from datetime import datetime
from pathlib import Path

def setup_logging(run_id: str = None, level: str = "INFO"):
    """
    Configure structured logging with run IDs.

    Args:
        run_id: Unique identifier for this run (auto-generated if None)
        level: Log level (INFO, DEBUG, WARNING, ERROR)
    """
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create dated directory
    log_dir = Path("logs") / datetime.now().strftime("%Y-%m-%d")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Log file path
    log_file = log_dir / f"run_{run_id}.log"

    # Configure logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=f'%(asctime)s [{run_id}] %(levelname)s %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )

    return run_id, log_file
```

**Usage Example**:
```python
from scripts.utils.logging_config import setup_logging

# In your scripts
run_id, log_file = setup_logging(level="INFO")
logger = logging.getLogger(__name__)

logger.info("Starting transcription")
# Output: 2025-11-04 14:30:00 [20251104_143000] INFO __main__: Starting transcription
```

---

#### 12. Create Golden Test Dataset ✅
**Time**: 30 minutes
**Priority**: P0 (deterministic tests)

**Purpose**: Canonical test files with expected outputs for reproducible tests

**Tasks:**
```bash
# Create golden dataset directory
mkdir -p tests/fixtures/golden/{inputs,expected_outputs}
```

**File**: `tests/fixtures/golden/README.md`
```markdown
# Golden Test Dataset

This directory contains canonical test data for reproducible testing.

## Structure
- `inputs/` - Test input files (audio, transcripts)
- `expected_outputs/` - Expected results for each input

## Three-Tier Dataset

### 1. Short Task (short_task.mp3)
- **Duration**: <1 minute
- **Content**: Single actionable task
- **Expected Category**: task
- **Expected Processing**: <30 seconds

### 2. Long Note (long_note.mp3)
- **Duration**: 5+ minutes
- **Content**: Long-form reflection
- **Expected Category**: note
- **Expected Processing**: ~2 minutes

### 3. Multiple Tasks (multiple_tasks.mp3)
- **Duration**: 2-3 minutes
- **Content**: 3 distinct tasks
- **Expected Category**: task (or split into 3 tasks)
- **Expected Processing**: ~1 minute

## Usage
Copy production files that represent each tier:
```bash
# Copy from Recording Archives to golden dataset
cp "Recording Archives/2025-11-02/short_task.mp3" tests/fixtures/golden/inputs/
```

## Expected Outputs Format
For each input, store expected results:
- `short_task_transcript.txt` - Expected Whisper output
- `short_task_analysis.json` - Expected AI analysis
- `short_task_notion.json` - Expected Notion entry format
```

**Update `.gitignore`**:
```
# Keep golden dataset in git (small, canonical files)
!tests/fixtures/golden/inputs/*.mp3
!tests/fixtures/golden/expected_outputs/*.json
```

**Note**: Copy 3 representative files from your `Recording Archives` that match the three tiers (short/medium/long) and document their expected outputs.

---

## 📅 Phase 2: Test Account Setup (Week 1)

**Goal**: Separate test environment for safe testing
**Time**: 1-2 hours (one-time setup)
**Prerequisites**: None (can do anytime)

### Step 1: Create Notion Test Workspace

1. **Create New Notion Account** (or use separate workspace)
   - Go to https://www.notion.com/signup
   - Use test email: `your.email+notion-test@gmail.com`
   - Verify email and create workspace
   - Workspace name: "AI Assistant Test Workspace"

2. **Duplicate Database Structure**
   - Create Tasks database (duplicate production structure)
     - Properties: Title, Status, Project (relation), Tags (multi-select), Due Date
   - Create Notes database
     - Properties: Title, Type, Project (relation), Created Date
   - Create Projects database
     - Properties: Name, Status, Aliases (text)

3. **Create Notion Integration**
   - Go to https://www.notion.so/my-integrations
   - Click "New integration"
   - Name: "AI Assistant Tests"
   - Select test workspace
   - Copy integration token → save as `NOTION_TEST_TOKEN`

4. **Share Databases with Integration**
   - Open each database → Click "..." → "Connections" → Add integration
   - Share Tasks, Notes, Projects databases

5. **Get Database IDs**
   - Open each database in browser
   - Copy database ID from URL
   - Format: `https://notion.so/{database_id}?v=...`
   - Save as `TEST_TASKS_DATABASE_ID`, `TEST_NOTES_DATABASE_ID`, `TEST_PROJECTS_DATABASE_ID`

### Step 2: Create OpenAI Test API Key

1. **Optional**: Create separate OpenAI project for testing
   - Go to https://platform.openai.com/settings/organization/projects
   - Create "AI Assistant Tests" project
   - Get API key → save as `OPENAI_TEST_API_KEY`

2. **Or**: Use same API key (just track costs separately via logs)

### Step 3: Set Up Test Environment Variables

**File**: `.env.test` (add to .gitignore)
```bash
# Test Notion Configuration
NOTION_TEST_TOKEN=secret_test_token_here
TEST_TASKS_DATABASE_ID=test_tasks_db_id_here
TEST_NOTES_DATABASE_ID=test_notes_db_id_here
TEST_PROJECTS_DATABASE_ID=test_projects_db_id_here

# Test OpenAI Configuration (optional)
OPENAI_TEST_API_KEY=test_api_key_here

# Test recorder path (local test folder)
TEST_RECORDER_PATH=/tmp/test_recorder
```

**Update `.gitignore`**:
```
.env.test
tests/reports/
```

### Step 4: Create Test Configuration File

**File**: `config/test.yaml`
```yaml
# Test Configuration (overrides settings.yaml during tests)

openai:
  model: "gpt-3.5-turbo"  # Cheaper for tests
  max_tokens: 100         # Shorter responses
  timeout: 10             # Faster timeout

notion:
  timeout: 5              # Faster timeout
  retry_attempts: 1       # Fewer retries

processing:
  max_file_duration_minutes: 5     # Shorter files for tests
  warn_duration_threshold_minutes: 3
  cpu_usage_limit_percent: 50

transcription:
  parallel_workers: 2     # Fewer workers for tests
  timeout_seconds: 60     # Shorter timeout

archive:
  retention_days: 1       # Clean up test archives quickly
```

### Step 5: Update Test Fixtures to Load Test Config

**Update**: `tests/conftest.py`
```python
import os
from dotenv import load_dotenv

@pytest.fixture(scope="session", autouse=True)
def load_test_env():
    """Load test environment variables."""
    load_dotenv(".env.test")

@pytest.fixture
def test_notion_client():
    """Real Notion client for test workspace."""
    from notion_client import Client
    return Client(auth=os.getenv("NOTION_TEST_TOKEN"))
```

---

## 📅 Phase 3: Core Test Coverage (Weeks 2-4)

**Goal**: Test critical components (70% coverage target)
**Time**: 1 day/week for 3 weeks
**Focus**: Unit tests for refactored modules

### Week 2: Parser & Analyzer Tests

**Files to test**:
- `scripts/parsers/content_parser.py`
- `scripts/parsers/project_extractor.py`
- `scripts/parsers/transcript_validator.py`
- `scripts/analyzers/task_analyzer.py`
- `scripts/analyzers/note_analyzer.py`

**Test cases** (20+ tests):
- Category detection (task, note, unclear)
- Project extraction patterns
- Content validation (file size, encoding, length)
- Task analysis (single, multiple)
- Note analysis (short, long >800 words)
- Edge cases (empty, malformed, very long)

### Week 3: Router Tests

**Files to test**:
- `scripts/routers/duration_estimator.py`
- `scripts/routers/tag_detector.py`
- `scripts/routers/icon_selector.py`
- `scripts/routers/project_detector.py`

**Test cases** (15+ tests):
- Duration estimation (QUICK, MEDIUM, LONG)
- Tag detection (Communications, Jessica Input)
- Icon selection (keyword matching, fallback)
- Project detection (AI + fuzzy matching)

### Week 4: Orchestration Tests (Critical!)

**Files to test** (Priority: TranscriptionEngine, ProcessingEngine):
- `scripts/orchestration/state/state_manager.py`
- `scripts/orchestration/detection/usb_detector.py`
- `scripts/orchestration/detection/file_validator.py`
- `scripts/orchestration/staging/staging_manager.py`
- `scripts/orchestration/transcription/transcription_engine.py` ⭐
- `scripts/orchestration/processing/processing_engine.py` ⭐
- `scripts/orchestration/archiving/archive_manager.py`
- `scripts/orchestration/archiving/cleanup_manager.py`

**Test cases** (25+ tests):
- State management (load, save, sessions)
- USB detection and validation
- Staging operations (copy, cleanup)
- Transcription engine (dynamic timeout, batching) ⭐
- Processing engine (AI analysis, verification) ⭐
- Archive management (structure, integrity)
- Cleanup operations (safe deletion)

---

## 📅 Phase 4: Integration & E2E Tests (Weeks 5-6)

**Goal**: Test workflows and component interactions
**Time**: 1 day/week for 2 weeks

### Week 5: Integration Tests

**Test workflows**:
1. **Manual Workflow**: Transcript → Parser → Analyzer → Router → Notion
2. **Notion Integration**: Verify entry creation, project linking, icon assignment
3. **AI Pipeline**: OpenAI → Analysis → Validation → Notion
4. **Orchestrator Steps**: Each step in isolation (mocked dependencies)

**Test cases** (10+ tests):
- End-to-end transcript processing
- Notion entry creation and verification
- Project detection with real project cache
- Error handling and retry logic

### Week 6: End-to-End Tests

**Test full workflows**:
1. **USB Workflow**: Detection → Staging → Transcription → Processing → Archive → Cleanup
2. **Manual Workflow**: Transcript → Processing → Notion → JSON save

**Test cases** (5+ tests):
- Full USB recorder workflow (with test audio files)
- Duplicate detection and cleanup
- Performance benchmarks (8-10 min target)
- Error recovery and state management

---

## 📅 Phase 5: CI/CD Setup (Week 7)

**Goal**: Automated testing on GitHub Actions
**Time**: 4 hours

### Step 1: Create GitHub Actions Workflow

**File**: `.github/workflows/test.yml`
```yaml
name: Test Suite

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 9 * * *'  # 9 AM daily
  workflow_dispatch:  # Manual trigger

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run unit tests
      run: pytest -m unit --cov=scripts --cov-report=xml
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_TEST_API_KEY }}
        NOTION_TOKEN: ${{ secrets.NOTION_TEST_TOKEN }}

    - name: Run integration tests
      run: pytest -m integration
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_TEST_API_KEY }}
        NOTION_TOKEN: ${{ secrets.NOTION_TEST_TOKEN }}

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

    - name: Run benchmark tests
      run: |
        pytest tests/performance/test_benchmarks.py --verbose
        # Benchmark results saved to logs/benchmarks/

    - name: Upload test artifacts
      if: always()  # Upload even if tests fail
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ github.run_number }}
        path: |
          logs/
          tests/reports/
          logs/benchmarks/*.json
        retention-days: 30
```

**Note**: Artifacts are kept for 30 days and allow you to:
- Download logs when CI fails
- Compare benchmark results over time
- Debug flaky tests

### Step 2: Add Secrets to GitHub

1. Go to repository → Settings → Secrets and variables → Actions
2. Add secrets:
   - `OPENAI_TEST_API_KEY`
   - `NOTION_TEST_TOKEN`
   - `TEST_TASKS_DATABASE_ID`
   - `TEST_NOTES_DATABASE_ID`
   - `TEST_PROJECTS_DATABASE_ID`

### Step 3: Add Status Badge to README

```markdown
[![Tests](https://github.com/your-username/ai-assistant/actions/workflows/test.yml/badge.svg)](https://github.com/your-username/ai-assistant/actions/workflows/test.yml)
```

---

## 📅 Phase 6: Performance Testing (Week 8)

**Goal**: Regression testing for performance
**Time**: 2-3 hours

### Performance Benchmarks with Regression Detection

**File**: `tests/performance/test_benchmarks.py`
```python
"""Performance benchmarks with baseline comparison."""
import pytest
import time
from pathlib import Path
from tests.utils.performance import save_benchmark, compare_to_baseline

@pytest.mark.slow
class TestPerformanceBenchmarks:
    """Test performance targets with regression detection."""

    def test_transcription_speed(self):
        """Verify transcription meets 8-10 min target for 5 files."""
        # Load golden dataset (3 test files from Phase 1 Task 12)
        audio_files = list(Path("tests/fixtures/golden/inputs").glob("*.mp3"))
        assert len(audio_files) >= 3, "Need at least 3 golden test files"

        # Measure transcription
        start = time.time()
        # ... run transcription on audio_files ...
        transcription_duration = time.time() - start

        # Measure AI processing
        start = time.time()
        # ... run AI analysis on transcripts ...
        ai_duration = time.time() - start

        # Build metrics
        metrics = {
            "transcription_duration_sec": transcription_duration,
            "ai_processing_duration_sec": ai_duration,
            "total_duration_sec": transcription_duration + ai_duration,
            "files_processed": len(audio_files),
            "success_count": len(audio_files),  # Update if any failed
            "failure_count": 0,
            "success_rate": 1.0
        }

        # Save benchmark results
        save_benchmark(metrics)

        # Compare to baseline (20% threshold)
        comparison = compare_to_baseline(metrics, threshold=0.20)

        # Assert no regressions
        if comparison["status"] == "regression":
            alerts = "\n".join(comparison["alerts"])
            pytest.fail(f"Performance regression detected:\n{alerts}")

        # Assert absolute targets
        assert transcription_duration < 600, \
            f"Transcription took {transcription_duration}s (target: <600s)"
```

**Usage**:
```bash
# Run benchmarks
pytest tests/performance/test_benchmarks.py -v

# Results saved to logs/benchmarks/YYYY-MM-DD_HH-MM-SS.json
# Compare to logs/benchmarks/golden.json (20% threshold)

# View benchmark results
cat logs/benchmarks/2025-11-04_14-30-00.json
```

**Track performance over time**:
- **Baseline**: 8 min for 5 files (established November 2, 2025)
- **Alert Threshold**: >20% performance degradation
- **Storage**: `logs/benchmarks/YYYY-MM-DD_HH-MM-SS.json`
- **Golden Baseline**: `logs/benchmarks/golden.json` (checked into git)

**Regression Detection**:
- Automatically compares current run to golden baseline
- Fails test if transcription >20% slower
- Fails test if success rate drops >20%
- CI uploads benchmark JSON as artifacts for historical tracking

---

## 🎓 Future Integration Testing (Roadmap)

### Gmail Integration Tests (Future)
**When**: When email intelligence system is implemented

**Test Account Setup**:
1. Create Gmail test account: `ai.assistant.test@gmail.com`
2. Enable Gmail API, get test credentials
3. Add to `.env.test`: `GMAIL_TEST_CREDENTIALS`

**Test cases**:
- Email fetching and parsing
- Newsletter detection
- Task extraction from emails

### Google Calendar Integration Tests (Future)
**When**: When calendar integration is implemented

**Test Account Setup**:
1. Use same Gmail test account
2. Enable Calendar API
3. Create test calendar: "AI Assistant Tests"

**Test cases**:
- Event creation from tasks
- Deadline detection
- Calendar blocking

---

## 📊 Success Metrics

### Coverage Targets
- **Unit Tests**: 70% code coverage (industry standard)
- **Integration Tests**: All critical workflows covered
- **E2E Tests**: 2+ full workflow tests

### Quality Targets
- **Test Pass Rate**: 95%+ (failing tests indicate regressions)
- **Test Speed**: Unit tests <30s, Integration <2 min, E2E <10 min
- **CI/CD Success Rate**: 90%+ (green builds)

### Performance Targets (Regression Testing)
- **Transcription**: 5 files in 8-10 min (baseline: November 2, 2025)
- **AI Processing**: <60s for 5 transcripts
- **Success Rate**: 96%+ end-to-end (baseline: November 2, 2025)

---

## 🔄 Test-Driven Development (TDD) Workflow

### Standard TDD Cycle

```
1. Write failing test
   ↓
2. Run test (verify it fails)
   ↓
3. Write minimal code to pass
   ↓
4. Run test (verify it passes)
   ↓
5. Refactor if needed
   ↓
6. Run full test suite
```

### Example: Adding New Router

**Step 1: Write test first**
```python
# tests/unit/test_routers/test_priority_detector.py
def test_detect_urgent_priority():
    """Test urgent priority detection."""
    detector = PriorityDetector()
    content = "URGENT: Need to respond to client by EOD"
    priority = detector.detect(content)
    assert priority == "urgent"
```

**Step 2: Run test (fails - module doesn't exist yet)**
```bash
pytest tests/unit/test_routers/test_priority_detector.py
# FAILED: ModuleNotFoundError: No module named 'priority_detector'
```

**Step 3: Implement minimal code**
```python
# scripts/routers/priority_detector.py
class PriorityDetector:
    def detect(self, content):
        if "URGENT" in content.upper():
            return "urgent"
        return "normal"
```

**Step 4: Run test (passes)**
```bash
pytest tests/unit/test_routers/test_priority_detector.py
# PASSED
```

**Step 5: Add more test cases, refactor**

**Step 6: Run full suite**
```bash
pytest
```

---

## 🎯 Template for Future Projects

### Quick Start Checklist

When starting a new project, use this template:

- [ ] **Create test structure** (copy from ai-assistant/tests/)
- [ ] **Install pytest** (`pip install pytest pytest-cov pytest-mock`)
- [ ] **Set up test accounts** (separate workspace/APIs)
- [ ] **Create test config** (`config/test.yaml`)
- [ ] **Write first test** (TDD from day 1)
- [ ] **Set up CI/CD** (daily runs on GitHub Actions)
- [ ] **Define coverage target** (70% for new projects)
- [ ] **Document test running** (add to README)

### Reusable Files

Copy these files to new projects:
1. `tests/pytest.ini` (pytest configuration)
2. `tests/conftest.py` (shared fixtures - adapt for new project)
3. `.github/workflows/test.yml` (CI/CD workflow - adapt for new project)
4. `docs/testing-roadmap.md` (this document - adapt phases)

---

## 📝 Notes & Decisions

### Why Daily CI/CD (Not Per-Commit)?
- Solo developer, not team (less risk of breaking main)
- Cost-effective (fewer API calls to OpenAI/Notion)
- Catch regressions without slowing development
- Can still run tests locally before committing

### Why Separate Test Accounts?
- Prevent production data pollution
- Safe to delete all test data
- Track test costs separately
- Industry standard for any production system

### Why 70% Coverage Target?
- Industry standard (not 100% - diminishing returns)
- Focus on critical paths (parsers, engines, routers)
- Balanced effort vs. value
- Allow for some untested edge cases

### Why TDD?
- Reduces ambiguity (test defines expected behavior)
- Ensures alignment (user and AI agree on outcome)
- Prevents regressions (existing tests catch breaks)
- Faster debugging (failing test pinpoints issue)

---

## 🔗 Related Documents

- [Refactoring Plan](refactoring-plan.md) - Architecture improvements in progress
- [Project State](project-state.md) - Current status and decisions
- [Technical Requirements](technical-requirements.md) - System architecture
- [Roadmap](roadmap.md) - Future enhancements

---

## 📝 Peter's Recommendations Integration (November 4, 2025)

**Added to Phase 1:**
- Task 10: Performance benchmark infrastructure (JSON metrics, golden baseline)
- Task 11: Structured logging standards (date-stamped, run IDs)
- Task 12: Golden test dataset (3-tier with expected outputs)

**Enhanced Phase 5:**
- CI artifact publishing (logs, reports, benchmarks)

**Enhanced Phase 6:**
- Regression detection (20% threshold)
- Baseline comparison automation

**Total Additional Effort**: ~2 hours (Phase 1 tasks)

---

*Last Updated: November 4, 2025 (Peter's recommendations integrated)*
*Next Review: After Phase 1 completion*
