# Technical Requirements: Groq Transcription Integration

**PRD**: `docs/prd/groq-transcription-integration.md`
**Status**: Implementation Ready
**Last Updated**: 2025-11-08
**Estimated Implementation**: 70 minutes

---

## 🎯 Technical Summary

Implement `TranscriptionService` abstraction layer with 2 pluggable backends (Groq, Local Whisper) to achieve 10-20x speed improvement while maintaining 100% backward compatibility and reliability.

---

## 🏗️ Architecture

### Component Diagram

```
scripts/orchestration/transcription/
├── transcription_engine.py           # EXISTING - High-level coordinator
│   ├── Uses: TranscriptionService    # NEW INTEGRATION
│   └── Public API: transcribe_batch()
│
├── transcription_service.py          # NEW - Abstraction layer
│   ├── Manages: Backend selection & fallback
│   ├── Public API: transcribe_file()
│   └── Returns: (success, transcript_text, error_msg)
│
└── backends/                          # NEW - Pluggable backends
    ├── __init__.py
    ├── base_backend.py                # Abstract base class
    │   └── Interface: transcribe(audio_path) → (success, text, error)
    │
    ├── groq_backend.py                # PRIMARY - Groq Cloud API
    │   ├── Model: whisper-large-v3
    │   ├── Speed: 1-5 sec per 3-min file
    │   └── Fallback: On error, delegates to local
    │
    └── local_whisper_backend.py       # FALLBACK - Local Whisper
        ├── Model: turbo (from config)
        ├── Speed: 90-120 sec per 3-min file
        └── Always succeeds (no fallback needed)
```

### Data Flow

```
┌─────────────────────┐
│ TranscriptionEngine │
│  (orchestrator)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ TranscriptionService│  <-- NEW abstraction layer
│  (backend manager)  │
└──────────┬──────────┘
           │
           ├──> Try GroqBackend (1-5 sec)
           │    ├─ Success? → Return transcript
           │    └─ Fail? → Try local backend
           │
           └──> Try LocalWhisperBackend (90-120 sec)
                └─ Always succeeds → Return transcript
```

---

## 📋 Implementation Tasks

### Task 1: Create Backend Abstraction (15 min)

**File**: `scripts/orchestration/transcription/backends/base_backend.py`

```python
"""Base class for transcription backends."""
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
            audio_file: Path to audio file (.mp3, .wav, etc.)

        Returns:
            Tuple[bool, str, str]: (success, transcript_text, error_message)
            - success: True if transcription succeeded
            - transcript_text: Transcribed text (empty string if failed)
            - error_message: Error description (empty string if succeeded)
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this backend is available (API key set, dependencies installed).

        Returns:
            bool: True if backend can be used
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get backend name for logging.

        Returns:
            str: Backend name (e.g., "Groq", "OpenAI", "Local Whisper")
        """
        pass
```

**File**: `scripts/orchestration/transcription/backends/__init__.py`

```python
"""Transcription backend modules."""

from .base_backend import BaseTranscriptionBackend
from .groq_backend import GroqBackend
from .openai_backend import OpenAIBackend
from .local_whisper_backend import LocalWhisperBackend

__all__ = [
    "BaseTranscriptionBackend",
    "GroqBackend",
    "OpenAIBackend",
    "LocalWhisperBackend",
]
```

---

### Task 2: Implement GroqBackend (15 min)

**File**: `scripts/orchestration/transcription/backends/groq_backend.py`

**Dependencies**: `pip install groq` (add to requirements.txt)

**Key Implementation Details**:
- Use Groq Python SDK
- Model: `whisper-large-v3`
- Timeout: 10 seconds (configurable)
- Error handling: Network errors, API errors, rate limits
- Return format: `(True, transcript_text, "")` on success, `(False, "", error_msg)` on failure

**API Call Example**:
```python
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
with open(audio_file, "rb") as f:
    transcription = client.audio.transcriptions.create(
        file=f,
        model="whisper-large-v3",
        response_format="text"
    )
```

---

### Task 3: Implement LocalWhisperBackend (10 min)

**File**: `scripts/orchestration/transcription/backends/local_whisper_backend.py`

**Key Implementation Details**:
- **Extract existing logic** from `transcription_engine.py` method `transcribe_single_file()`
- Model: From config (`whisper.model`, default "turbo")
- Uses CLI: `whisper <file> --model turbo --language en --output_format txt`
- Timeout: Dynamic based on file duration (existing logic)
- **Always succeeds** (subprocess errors converted to error tuple, not exceptions)
- Return format: Same as GroqBackend

---

### Task 4: Create TranscriptionService (15 min)

**File**: `scripts/orchestration/transcription/transcription_service.py`

**Responsibilities**:
1. **Backend management**: Initialize available backends based on config/API keys
2. **Fallback chain**: Try backends in order (Groq → OpenAI → Local)
3. **Logging**: Log which backend succeeded/failed
4. **Configuration**: Read backend preferences from `config/settings.yaml`

**Public API**:
```python
class TranscriptionService:
    def __init__(self, config_loader):
        """Initialize with available backends based on config and API keys."""
        pass

    def transcribe_file(self, audio_file: Path) -> Tuple[bool, str, str]:
        """
        Transcribe file using best available backend with automatic fallback.

        Returns:
            Tuple[bool, str, str]: (success, transcript_text, error_message)
        """
        pass

    def get_active_backend(self) -> str:
        """Get name of currently active backend (for logging)."""
        pass
```

**Fallback Logic**:
```python
def transcribe_file(self, audio_file):
    for backend in self.backends:
        if not backend.is_available():
            logger.debug(f"{backend.get_name()} not available, skipping")
            continue

        logger.info(f"Trying {backend.get_name()}...")
        success, transcript, error = backend.transcribe(audio_file)

        if success:
            logger.info(f"✓ {backend.get_name()} succeeded")
            return (True, transcript, "")
        else:
            logger.warning(f"✗ {backend.get_name()} failed: {error}")
            # Try next backend

    # All backends failed
    return (False, "", "All transcription backends failed")
```

---

### Task 5: Update TranscriptionEngine (10 min)

**File**: `scripts/orchestration/transcription/transcription_engine.py`

**Changes**:
1. **Add TranscriptionService initialization** in `__init__()`
2. **Update `transcribe_single_file()`** to delegate to TranscriptionService
3. **Preserve existing method signature** (100% backward compatible)
4. **Add fallback to old logic** if TranscriptionService fails (safety net)

**Implementation Approach**:
```python
# In __init__:
from .transcription_service import TranscriptionService
self.transcription_service = TranscriptionService(self.config)

# In transcribe_single_file:
def transcribe_single_file(self, file_path, transcripts_folder, batch_num=1, file_num=1):
    # Try new TranscriptionService first
    success, transcript_text, error = self.transcription_service.transcribe_file(file_path)

    if success:
        # Save transcript to file
        output_path = transcripts_folder / f"{file_path.stem}.txt"
        with open(output_path, 'w') as f:
            f.write(transcript_text)
        return (True, output_path, "")
    else:
        # Fallback to old local Whisper logic (safety net)
        logger.warning(f"TranscriptionService failed: {error}, falling back to legacy local Whisper")
        return self._legacy_transcribe_single_file(file_path, transcripts_folder, batch_num, file_num)
```

---

### Task 6: Add Configuration Support (5 min)

**File**: `config/settings.yaml`

**New Section**:
```yaml
# Transcription Configuration
transcription:
  # Backend selection: auto, groq, local
  # - auto: Try Groq → Local (recommended)
  # - groq: Groq only (fails if unavailable)
  # - local: Local Whisper only (always works)
  backend: auto

  # Groq Cloud API settings
  groq:
    model: whisper-large-v3
    timeout_seconds: 30

# Keep existing whisper: section for backward compatibility
whisper:
  model: turbo
  language: en
  output_format: txt
```

**Environment Variables** (`.env`):
```bash
# GROQ_API_KEY already exists (user confirmed)
GROQ_API_KEY=your_groq_api_key_here
```

---

### Task 7: Update Dependencies (5 min)

**File**: `requirements.txt`

**Add**:
```
groq==0.4.0  # Groq Python SDK
```

**Install**:
```bash
pip install groq==0.4.0
```

---

## ✅ Success Criteria Validation

### Performance Testing

**Test 1: Speed Benchmark** (Target: <30 sec for 6 files)
```bash
# Measure time
time python scripts/recording_orchestrator.py --skip-steps process,archive,cleanup

# Expected output:
# - With Groq: ~30 seconds for 6 files (5 sec/file)
# - With Local: ~8 minutes for 6 files (80 sec/file)
```

**Test 2: Fallback Chain** (Target: 100% reliability)
```bash
# Disable Groq, verify local fallback
GROQ_API_KEY="" python scripts/recording_orchestrator.py
```

**Test 3: Accuracy Check** (Target: ≥95%)
- Process 3 sample files with Groq
- Manually review transcripts for accuracy
- Compare with known-good local Whisper output

### Backward Compatibility Testing

```bash
# Test 1: Default workflow (should use Groq automatically)
python scripts/recording_orchestrator.py

# Test 2: Force local-only mode (config override)
# Set transcription.backend: local in settings.yaml
python scripts/recording_orchestrator.py

# Test 3: Existing scripts still work
python scripts/process_transcripts.py
```

---

## 🚨 Risk Mitigation

### Risk 1: Groq API Unreliable
**Mitigation**: Automatic fallback to Local Whisper

### Risk 2: Breaking Changes to Existing Workflow
**Mitigation**:
- Preserve existing method signatures
- Add fallback to legacy local Whisper logic
- Config option to force local-only mode

### Risk 3: API Key Not Set
**Mitigation**:
- Backends check `is_available()` before use
- Skip unavailable backends silently
- Always have local Whisper as final fallback

### Risk 4: Groq API Cost Explosion
**Mitigation**:
- Free tier: 14,400 sec/day (240 minutes)
- User processes ~30 min/day max
- Well within free tier limits
- Can fallback to local if needed

---

## 📊 Performance Targets

| Metric | Baseline (Local) | Target (Groq) | Measurement |
|--------|------------------|---------------|-------------|
| 6 files | 8 minutes | <30 seconds | End-to-end time |
| 30-min interview | 30+ minutes | <2 minutes | Single long file |
| Accuracy | ~95% | ≥95% | Manual review |
| Fallback success | 100% | 100% | Disable API keys test |

---

## 🔗 Dependencies

**Python Packages**:
- `groq==0.4.0` (NEW)
- `openai` (EXISTING)
- `pyyaml` (EXISTING)

**Environment Variables**:
- `GROQ_API_KEY` (EXISTING - user confirmed)
- `OPENAI_API_KEY` (EXISTING)

**Configuration**:
- `config/settings.yaml` (UPDATE)
- `.env` (NO CHANGES - keys already set)

---

## 📝 Testing Checklist

### Unit Tests (Deferred to Phase 3)
- [ ] GroqBackend.transcribe() success case
- [ ] GroqBackend.transcribe() failure case
- [ ] OpenAIBackend.transcribe() success case
- [ ] LocalWhisperBackend.transcribe() success case
- [ ] TranscriptionService fallback chain

### Integration Tests (This Phase)
- [ ] Process 6 real files with Groq (<30 sec)
- [ ] Disable Groq, verify OpenAI fallback works
- [ ] Disable Groq+OpenAI, verify local fallback works
- [ ] Manual accuracy check on 3 sample transcripts
- [ ] Existing orchestrator workflow unchanged

---

## 🎯 Implementation Order

1. **Create directory structure** (2 min)
2. **Implement BaseTranscriptionBackend** (5 min)
3. **Implement LocalWhisperBackend** (extract existing logic, 10 min)
4. **Implement GroqBackend** (15 min)
5. **Implement OpenAIBackend** (10 min)
6. **Implement TranscriptionService** (15 min)
7. **Update TranscriptionEngine** (10 min)
8. **Add config support** (5 min)
9. **Install dependencies** (3 min)
10. **Test with real files** (10 min)

**Total**: 70 minutes

---

## 📅 Rollout Plan

### Phase 2 (This Implementation): Core Integration
- Groq + Local backends
- Automatic fallback chain (Groq → Local)
- Config-based backend selection

### Phase 3 (Future - Deferred): Auto-Switching Intelligence
- Detect file duration → choose backend
- Cost optimization (use local for short files, Groq for long)
- Performance analytics

---

*End of Technical Requirements*
