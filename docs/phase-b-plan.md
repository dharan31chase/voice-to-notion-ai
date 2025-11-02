# Phase B: recording_orchestrator.py Refactoring Plan
**Date**: November 1, 2025
**Status**: Planning Phase
**Priority**: PRODUCTION-CRITICAL

---

## 🎯 Overview

**Current State**: recording_orchestrator.py is a 2,518-line monolith with 9+ responsibilities
**Target State**: ~300-line coordinator delegating to 8 specialized modules
**Estimated Effort**: 5-7 days (including comprehensive testing)
**Risk Level**: HIGH (production-critical code)

---

## 📊 Current Structure Analysis

### RecordingOrchestrator Class (2,347 lines)
**50+ methods organized into 10 functional areas:**

#### 1. **Detection & USB Management** (~300 lines)
- `_check_usb_connection()` - USB volume availability
- `_scan_mp3_files()` - Discover .mp3 files
- `_check_usb_file_permissions()` - Permission validation
- `step1_monitor_and_detect()` - Main detection workflow

#### 2. **File Validation** (~250 lines)
- `_validate_file_integrity()` - File corruption checks
- `_should_skip_short_file()` - Duration filtering
- `_validate_transcript_for_processing()` - Transcript validation
- `step2_validate_and_prepare()` - Main validation workflow
- `_check_whisper_installation()` - Dependency checks
- `_check_disk_space()` - Storage availability

#### 3. **Staging Management** (~200 lines)
- `_copy_files_to_staging()` - USB → Local copy
- `_cleanup_staging_files()` - Staging cleanup
- `_safe_delete_usb_file()` - Safe USB deletion

#### 4. **Transcription Engine** (~450 lines)
- `_transcribe_single_file()` - Whisper transcription
- `_should_transcribe_audio()` - Transcription filtering
- `_monitor_cpu_usage()` - Resource monitoring
- `step3_transcribe()` - Main transcription workflow
- `_create_balanced_batches()` - Duration-aware batching
- `_create_processing_batches()` - Batch creation
- `_estimate_processing_time()` - Time estimation
- `_check_system_resources()` - System health checks

#### 5. **AI Processing** (~300 lines)
- `_import_process_transcripts()` - Import processing logic
- `_process_single_transcript()` - Single file processing
- `_get_transcript_processing_status()` - Status checks
- `step4_stage_and_process()` - Main processing workflow

#### 6. **Notion Verification** (~200 lines)
- `_verify_notion_entry_exists()` - Single entry verification
- `_verify_notion_entries()` - Batch verification
- `_verify_session_success()` - Session validation

#### 7. **Archive Management** (~400 lines)
- `_create_archive_structure()` - Date-based folders
- `_archive_single_recording()` - Single file archiving
- `_archive_successful_recordings()` - Batch archiving
- `_ensure_archive_permissions()` - Permission management
- `step5_verify_and_archive()` - Main archiving workflow

#### 8. **Cleanup Operations** (~250 lines)
- `_cleanup_recorder_file()` - USB cleanup
- `_cleanup_successful_sources()` - Source cleanup
- `_run_automatic_cleanup()` - Scheduled cleanup
- `_cleanup_old_archives()` - Archive retention

#### 9. **State Management** (~300 lines)
- `_load_state()` - State loading from JSON
- `_save_state()` - State persistence
- `_update_archive_state_with_verification()` - Verified updates
- `_finalize_session_with_verification()` - Session finalization
- `_finalize_session()` - Legacy finalization

#### 10. **Utilities & Setup** (~200 lines)
- `__init__()` - Initialization
- `_setup_folders()` - Folder creation
- `_setup_notion_client()` - Notion setup
- `_extract_file_metadata()` - Metadata extraction
- `_generate_session_id()` - Session IDs
- `_get_unprocessed_files()` - File filtering
- `_move_failed_file()` - Failure handling
- `_move_failed_transcript()` - Transcript failures

#### 11. **Main Orchestration** (~100 lines)
- `run()` - Main workflow coordinator

---

## 🏗️ Target Architecture

### New Module Structure
```
scripts/
├── orchestration/
│   ├── __init__.py
│   ├── orchestrator.py              # ~300 lines (coordinator only)
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   ├── usb_detector.py          # ~250 lines (USB connection, scan, permissions)
│   │   └── file_validator.py        # ~300 lines (integrity, duration, dependencies)
│   │
│   ├── staging/
│   │   ├── __init__.py
│   │   └── staging_manager.py       # ~250 lines (copy, cleanup, safe delete)
│   │
│   ├── transcription/
│   │   ├── __init__.py
│   │   ├── transcriber.py           # ~200 lines (single file transcription)
│   │   ├── batch_manager.py         # ~150 lines (batching, time estimation)
│   │   └── resource_monitor.py      # ~100 lines (CPU, disk, system health)
│   │
│   ├── processing/
│   │   ├── __init__.py
│   │   └── ai_processor.py          # ~300 lines (transcript processing)
│   │
│   ├── verification/
│   │   ├── __init__.py
│   │   └── notion_verifier.py       # ~200 lines (Notion entry verification)
│   │
│   ├── archiving/
│   │   ├── __init__.py
│   │   ├── archive_manager.py       # ~300 lines (archive structure, file archiving)
│   │   └── cleanup_manager.py       # ~250 lines (cleanup operations, retention)
│   │
│   └── state/
│       ├── __init__.py
│       └── state_manager.py         # ~400 lines (state load/save, session management)
```

### Module Responsibilities

#### 1. **orchestrator.py** (Coordinator)
**Responsibility**: High-level workflow coordination ONLY
**Lines**: ~300
**Methods**:
- `run()` - Main workflow
- `_step1_detect()` - Delegates to USBDetector
- `_step2_validate()` - Delegates to FileValidator
- `_step3_transcribe()` - Delegates to Transcriber + BatchManager
- `_step4_process()` - Delegates to AIProcessor
- `_step5_archive()` - Delegates to ArchiveManager
- Error handling and logging only

#### 2. **usb_detector.py** (Detection)
**Responsibility**: USB device detection and file discovery
**Lines**: ~250
**Methods**:
- `check_connection()` - USB availability
- `scan_files()` - Discover .mp3 files
- `check_permissions()` - File access validation
- `get_unprocessed_files()` - Filter already processed

#### 3. **file_validator.py** (Validation)
**Responsibility**: File integrity and prerequisite validation
**Lines**: ~300
**Methods**:
- `validate_integrity()` - Corruption checks
- `validate_duration()` - Duration filtering
- `validate_transcript()` - Transcript validation
- `check_dependencies()` - Whisper, ffmpeg, etc.
- `check_disk_space()` - Storage availability

#### 4. **staging_manager.py** (Staging)
**Responsibility**: Local staging for USB files
**Lines**: ~250
**Methods**:
- `copy_to_staging()` - USB → Local copy
- `cleanup_staging()` - Staging cleanup
- `safe_delete_usb()` - Safe USB deletion
- `get_staged_files()` - List staged files

#### 5. **transcriber.py** (Transcription)
**Responsibility**: Single file transcription via Whisper
**Lines**: ~200
**Methods**:
- `transcribe()` - Single file transcription
- `should_transcribe()` - Transcription filtering
- `extract_metadata()` - File metadata

#### 6. **batch_manager.py** (Batching)
**Responsibility**: Batch creation and time estimation
**Lines**: ~150
**Methods**:
- `create_balanced_batches()` - Duration-aware batching
- `estimate_processing_time()` - Time estimation
- `create_batches()` - Fixed-size batches

#### 7. **resource_monitor.py** (Monitoring)
**Responsibility**: System resource monitoring
**Lines**: ~100
**Methods**:
- `check_cpu_usage()` - CPU monitoring
- `check_system_resources()` - Overall health
- `should_throttle()` - Throttling decisions

#### 8. **ai_processor.py** (Processing)
**Responsibility**: Transcript AI processing
**Lines**: ~300
**Methods**:
- `process_transcript()` - Single transcript processing
- `get_processing_status()` - Status checks
- `import_process_function()` - Import processing logic
- Error handling and retry logic

#### 9. **notion_verifier.py** (Verification)
**Responsibility**: Notion entry verification
**Lines**: ~200
**Methods**:
- `verify_entry_exists()` - Single entry verification
- `verify_entries_batch()` - Batch verification
- `verify_session_success()` - Session validation

#### 10. **archive_manager.py** (Archiving)
**Responsibility**: Archive structure and file archiving
**Lines**: ~300
**Methods**:
- `create_structure()` - Date-based folders
- `archive_recording()` - Single file archiving
- `archive_batch()` - Batch archiving
- `ensure_permissions()` - Permission management

#### 11. **cleanup_manager.py** (Cleanup)
**Responsibility**: Cleanup operations and retention
**Lines**: ~250
**Methods**:
- `cleanup_usb_file()` - USB cleanup
- `cleanup_source_files()` - Source cleanup
- `cleanup_old_archives()` - Archive retention
- `run_automatic_cleanup()` - Scheduled cleanup

#### 12. **state_manager.py** (State)
**Responsibility**: State persistence and session management
**Lines**: ~400
**Methods**:
- `load_state()` - State loading from JSON
- `save_state()` - State persistence
- `update_archive_state()` - State updates
- `finalize_session()` - Session finalization
- `generate_session_id()` - Session ID generation
- JSON serialization helpers

---

## 📋 Phased Implementation Plan

### **Step 1: Create Module Infrastructure** (Day 1 - Morning)
**Effort**: 2-3 hours
**Risk**: LOW

**Tasks**:
- [x] Commit Phase A work ✅
- [ ] Create `scripts/orchestration/` package structure
- [ ] Create all `__init__.py` files
- [ ] Create empty module files with docstrings
- [ ] Add base classes/interfaces if needed
- [ ] Update imports in existing files

**Testing**: Import new modules, verify no import errors

**Success Criteria**:
- All new directories created
- All `__init__.py` files present
- No import errors
- Git commit: "refactor: Create orchestration package structure"

---

### **Step 2: Extract State Management** (Day 1 - Afternoon)
**Effort**: 3-4 hours
**Risk**: MEDIUM (state is critical)

**Tasks**:
- [ ] Create `orchestration/state/state_manager.py`
- [ ] Extract state methods:
  - `_load_state()` → `load_state()`
  - `_save_state()` → `save_state()`
  - `_generate_session_id()` → `generate_session_id()`
  - `_update_archive_state_with_verification()` → `update_archive_state()`
  - `_finalize_session_with_verification()` → `finalize_session()`
  - `_finalize_session()` → `_finalize_session_legacy()` (keep for backward compatibility)
- [ ] Add comprehensive error handling
- [ ] Add state validation
- [ ] Update `RecordingOrchestrator.__init__()` to use StateManager

**Testing**:
- Unit tests for state loading/saving
- Test with existing state files (backward compatibility)
- Test session finalization
- Verify JSON serialization works correctly

**Success Criteria**:
- StateManager works independently
- Existing state files load correctly
- No data loss
- Git commit: "refactor: Extract state management to StateManager"

---

### **Step 3: Extract Detection & Validation** (Day 2 - Morning)
**Effort**: 3-4 hours
**Risk**: MEDIUM

**Tasks**:
- [ ] Create `orchestration/detection/usb_detector.py`
  - Extract USB detection methods
  - Extract file scanning methods
  - Extract permission checks
- [ ] Create `orchestration/detection/file_validator.py`
  - Extract validation methods
  - Extract dependency checks
  - Extract disk space checks
- [ ] Update `step1_monitor_and_detect()` to use new modules
- [ ] Update `step2_validate_and_prepare()` to use new modules

**Testing**:
- Test USB detection with/without USB connected
- Test file scanning with various scenarios
- Test validation with valid/invalid files
- Test dependency checks

**Success Criteria**:
- USBDetector and FileValidator work independently
- Step 1 and Step 2 produce same results as before
- Git commit: "refactor: Extract detection and validation modules"

---

### **Step 4: Extract Staging Management** (Day 2 - Afternoon)
**Effort**: 2-3 hours
**Risk**: MEDIUM (file operations)

**Tasks**:
- [ ] Create `orchestration/staging/staging_manager.py`
  - Extract staging methods
  - Extract cleanup methods
  - Extract safe delete logic
- [ ] Update methods that use staging to use StagingManager

**Testing**:
- Test copy to staging (USB → Local)
- Test staging cleanup
- Test safe USB delete
- Test with dry-run mode

**Success Criteria**:
- StagingManager works independently
- No file loss during staging
- Safe delete prevents data loss
- Git commit: "refactor: Extract staging management module"

---

### **Step 5: Extract Transcription Engine** (Day 3 - Morning)
**Effort**: 4-5 hours
**Risk**: HIGH (core functionality)

**Tasks**:
- [ ] Create `orchestration/transcription/transcriber.py`
  - Extract transcription methods
  - Extract filtering logic
- [ ] Create `orchestration/transcription/batch_manager.py`
  - Extract batching logic
  - Extract time estimation
- [ ] Create `orchestration/transcription/resource_monitor.py`
  - Extract CPU monitoring
  - Extract system health checks
- [ ] Update `step3_transcribe()` to use new modules

**Testing**:
- Test single file transcription
- Test batch creation (balanced batches)
- Test CPU monitoring and throttling
- Test with various file counts
- Test parallel transcription

**Success Criteria**:
- Transcription produces same results
- Batching logic preserved
- CPU monitoring works
- Performance matches baseline (8 min for 5 files)
- Git commit: "refactor: Extract transcription engine modules"

---

### **Step 6: Extract Processing & Verification** (Day 3 - Afternoon)
**Effort**: 3-4 hours
**Risk**: MEDIUM

**Tasks**:
- [ ] Create `orchestration/processing/ai_processor.py`
  - Extract AI processing methods
  - Extract status checks
  - Extract import logic
- [ ] Create `orchestration/verification/notion_verifier.py`
  - Extract Notion verification methods
  - Extract session validation
- [ ] Update `step4_stage_and_process()` to use new modules

**Testing**:
- Test transcript processing
- Test Notion verification
- Test with/without Notion entries
- Test error handling

**Success Criteria**:
- Processing produces same results
- Verification prevents data loss
- Git commit: "refactor: Extract processing and verification modules"

---

### **Step 7: Extract Archiving & Cleanup** (Day 4 - Morning)
**Effort**: 4-5 hours
**Risk**: HIGH (data preservation)

**Tasks**:
- [ ] Create `orchestration/archiving/archive_manager.py`
  - Extract archive structure creation
  - Extract file archiving methods
  - Extract permission management
- [ ] Create `orchestration/archiving/cleanup_manager.py`
  - Extract cleanup methods
  - Extract retention policy
  - Extract automatic cleanup
- [ ] Update `step5_verify_and_archive()` to use new modules

**Testing**:
- Test archive creation
- Test file archiving
- Test cleanup operations
- Test retention policy (7-day)
- Test with dry-run mode
- **CRITICAL**: Verify no files are deleted incorrectly

**Success Criteria**:
- Archiving preserves all files
- Cleanup respects retention policy
- No data loss
- Git commit: "refactor: Extract archiving and cleanup modules"

---

### **Step 8: Refactor Main Orchestrator** (Day 4 - Afternoon)
**Effort**: 3-4 hours
**Risk**: MEDIUM

**Tasks**:
- [ ] Rewrite `orchestrator.py` as clean coordinator
  - Remove all extracted methods
  - Keep only workflow coordination
  - Delegate to specialized modules
  - Target: ~300 lines
- [ ] Add comprehensive error handling
- [ ] Add detailed logging
- [ ] Update CLI integration

**Testing**:
- Test complete end-to-end workflow
- Compare with baseline behavior
- Test all CLI flags (dry-run, skip-steps, etc.)

**Success Criteria**:
- orchestrator.py is ~300 lines
- All functionality preserved
- Clean delegation pattern
- Git commit: "refactor: Simplify main orchestrator to coordinator pattern"

---

### **Step 9: Parallel Testing & Validation** (Day 5-6)
**Effort**: 2 full days
**Risk**: CRITICAL (production validation)

**Strategy**: Run both old and new in "shadow mode"

**Tasks**:
- [ ] **Day 5 Morning**: Create test scenarios
  - New files only
  - Duplicate files only
  - Mixed scenarios
  - Error conditions (missing USB, corrupt files, Notion failures)
  - Edge cases (very short files, very long files)

- [ ] **Day 5 Afternoon**: Dry-run testing
  - Run with `--dry-run` flag
  - Verify no file operations
  - Check logging output
  - Validate state updates

- [ ] **Day 6 Morning**: Real file testing (non-production)
  - Use test USB recordings
  - Verify transcription quality
  - Verify Notion entries created
  - Verify archiving works
  - Verify cleanup works

- [ ] **Day 6 Afternoon**: Production monitoring
  - Run on actual production files
  - Monitor for errors
  - Compare processing times
  - Verify success rate

**Testing Checklist**:
- [ ] End-to-end workflow completes successfully
- [ ] All 5 steps execute correctly
- [ ] Transcription quality matches baseline
- [ ] Notion entries created correctly
- [ ] Files archived properly
- [ ] State management works
- [ ] Cleanup respects retention
- [ ] Error handling works (network issues, API failures, etc.)
- [ ] Performance matches baseline (8 min for 5 files)
- [ ] Dry-run mode works
- [ ] Skip-steps works
- [ ] All CLI flags work

**Success Criteria**:
- 100% feature parity with old code
- Zero data loss
- Performance matches baseline
- All edge cases handled
- Git commit: "test: Validate Phase B refactoring with production scenarios"

---

### **Step 10: Documentation & Cleanup** (Day 7)
**Effort**: Full day
**Risk**: LOW

**Tasks**:
- [ ] Update `docs/refactoring-plan.md` (mark Phase B complete)
- [ ] Update `docs/project-state.md` (add Phase B achievements)
- [ ] Update `docs/roadmap.md` (update progress)
- [ ] Create architecture diagram (before/after)
- [ ] Write migration guide for developers
- [ ] Add module-level docstrings
- [ ] Add method docstrings with examples
- [ ] Create developer guide: "How to add a new orchestration step"
- [ ] Remove old code comments if any
- [ ] Final cleanup commit

**Success Criteria**:
- All documentation updated
- Clear developer guide
- Professional docstrings
- Git commit: "docs: Complete Phase B documentation"

---

## 🎯 Success Metrics

### Before Refactoring (Baseline)
- **Lines**: 2,518 (RecordingOrchestrator class)
- **Methods**: 50+ methods in one class
- **Responsibilities**: 9+ concerns mixed
- **Testability**: Difficult (need full orchestrator)
- **Extensibility**: Hard (modify 2,518-line file)
- **Time to understand**: Hours (need to read entire file)

### After Refactoring (Target)
- **Lines**: ~300 (orchestrator.py) + ~2,350 (8 modules)
- **Methods**: ~5-10 per module
- **Responsibilities**: 1 per module (SRP)
- **Testability**: Easy (test modules independently)
- **Extensibility**: Easy (modify specific module)
- **Time to understand**: Minutes (read specific module)

### Performance Targets
- **Processing time**: Match baseline (8 min for 5 files)
- **Success rate**: 100% (no regressions)
- **Data loss**: Zero (critical)
- **Test coverage**: 80%+ for new modules

---

## 🚨 Risk Mitigation Strategy

### Risk 1: Breaking Production Workflow
**Likelihood**: MEDIUM
**Impact**: CRITICAL

**Mitigation**:
- Extensive testing with real files before production
- Dry-run mode for all testing
- Parallel testing (shadow mode)
- Rollback plan ready (Git revert)
- Keep old code in Git history
- Feature flag for gradual rollout

### Risk 2: Data Loss During Refactoring
**Likelihood**: LOW (we have P0 hotfix)
**Impact**: CRITICAL

**Mitigation**:
- Always verify before delete
- Archive before cleanup
- Test with dry-run first
- Comprehensive logging
- State tracking for audit trail

### Risk 3: Performance Regression
**Likelihood**: LOW
**Impact**: MEDIUM

**Mitigation**:
- Benchmark before/after
- Performance tracking during testing
- Resource monitoring
- Load testing with multiple files

### Risk 4: Scope Creep
**Likelihood**: MEDIUM
**Impact**: MEDIUM

**Mitigation**:
- Strict "parity + infrastructure" approach
- No "fixes" during refactoring (separate PRs)
- Time-box each step
- Clear success criteria

### Risk 5: Integration Issues
**Likelihood**: MEDIUM
**Impact**: MEDIUM

**Mitigation**:
- Step-by-step integration
- Test after each extraction
- Maintain backward compatibility
- Comprehensive integration tests

---

## 🔄 Rollback Plan

### If Things Go Wrong
1. **Immediate**: Stop refactoring, assess issue
2. **Quick fix possible?**: Fix and test
3. **Complex issue?**: Git revert to last stable commit
4. **Production broken?**: Emergency rollback to pre-Phase-B commit

### Git Strategy
- Create branch: `feature/phase-b-orchestrator-refactoring`
- Commit after each step
- Tag stable points: `phase-b-step-1-stable`, etc.
- Keep `main` branch stable (merge only when complete)

---

## 📝 Next Steps

### Immediate (This Session)
1. Review this plan with user
2. Create orchestration package structure
3. Begin Step 1: Module infrastructure

### Short-term (Next Week)
1. Complete Steps 1-8 (extraction)
2. Begin Step 9 (testing)

### Long-term (After Phase B)
1. Future enhancements enabled by refactoring
2. Move to Phase 5-6 (other scripts)
3. Performance optimization (Groq integration)

---

## 💡 Key Principles

1. **Single Responsibility**: Each module does ONE thing well
2. **Parity First**: Exact behavior match, no "improvements"
3. **Test Everything**: Each extraction must be tested
4. **Safety First**: Production stability > refactoring speed
5. **Gradual Migration**: Step-by-step, not big-bang
6. **Documentation**: Clear docs for future developers

---

**Last Updated**: November 1, 2025
**Status**: Ready to begin
**Estimated Completion**: November 8, 2025 (7 days)
