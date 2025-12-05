# CLI Usage Guide
## Command-Line Interface for AI Assistant Scripts

**Date**: October 7, 2025  
**Milestone**: 1.3 - CLI Foundation  
**Status**: ✅ Complete

---

## 📋 Overview

Both main scripts now support command-line arguments for flexible testing, debugging, and customization:
- `scripts/process_transcripts.py` - Transcript processing with AI analysis
- `scripts/recording_orchestrator.py` - End-to-end USB recorder workflow

**Key Benefits:**
- **20x faster testing** (dry-run mode)
- **No Notion cleanup needed** (simulate before executing)
- **Debug any component** (verbose logging)
- **Test in isolation** (skip steps, single files)

---

## 🎯 process_transcripts.py

### Basic Usage

```bash
# Process all files (default behavior - backwards compatible)
python scripts/process_transcripts.py

# Get help
python scripts/process_transcripts.py --help
```

### Available Flags

| Flag | Short | Description | Example |
|------|-------|-------------|---------|
| `--dry-run` | | Simulate without creating Notion entries or saving files | `--dry-run` |
| `--verbose` | `-v` | Enable debug-level logging | `-v` |
| `--file PATH` | | Process single file instead of all | `--file transcripts/test.txt` |
| `--config PATH` | | Use custom configuration file | `--config test.yaml` |
| `--input-dir PATH` | | Custom transcript folder | `--input-dir my_transcripts` |
| `--output-dir PATH` | | Custom output folder | `--output-dir my_output` |

### Common Workflows

#### **1. Test a Change (Dry-Run)**
```bash
# See what WOULD happen without creating anything
python scripts/process_transcripts.py --dry-run --file transcripts/test.txt

# Output shows:
# 🔍 DRY RUN: Would create Notion entry:
#    Title: Your Task Title
#    Project: Detected Project
#    Icon: 💡
# 🔍 DRY RUN: Would save to: processed/test_processed.json
```

#### **2. Debug Project Detection**
```bash
# Verbose output shows AI decision-making
python scripts/process_transcripts.py --dry-run --file test.txt --verbose

# Output shows:
# DEBUG - Extracting project from: 'Close HDFC account...'
# DEBUG - Trying word combination: 'HDFC'
# DEBUG - Fuzzy match result: 'Banking Tasks'
```

#### **3. Test Custom Config**
```bash
# Test new config without affecting production
python scripts/process_transcripts.py --config config/experimental.yaml --dry-run
```

#### **4. Process Single File (Real)**
```bash
# Actually create Notion entry for one file
python scripts/process_transcripts.py --file transcripts/important.txt
```

#### **5. Batch Process Custom Directory**
```bash
# Process files from different folder
python scripts/process_transcripts.py --input-dir test_transcripts --output-dir test_output
```

---

## 🎙️ recording_orchestrator.py

### Basic Usage

```bash
# Run full workflow (default behavior - backwards compatible)
python scripts/recording_orchestrator.py

# Get help
python scripts/recording_orchestrator.py --help
```

### Available Flags

| Flag | Short | Description | Example |
|------|-------|-------------|---------|
| `--dry-run` | | Simulate without file operations | `--dry-run` |
| `--verbose` | `-v` | Enable debug-level logging | `-v` |
| `--skip-steps STEPS` | | Skip specific steps (comma-separated) | `--skip-steps transcribe,archive` |
| `--config PATH` | | Custom config (placeholder for future) | `--config test.yaml` |

### Available Steps to Skip

| Step | What It Does | Why Skip It |
|------|--------------|-------------|
| `detect` | Find files on USB | Test with manual file list |
| `validate` | Check file sizes/formats | Assume all files valid |
| `transcribe` | Run Whisper (SLOW) | Use existing transcripts |
| `process` | AI analysis + Notion | Test file handling only |
| `archive` | Move files to archives | Keep files for re-testing |
| `cleanup` | Delete source files | Preserve originals |

### Common Workflows

#### **1. Test File Detection Only**
```bash
# See what files would be found without processing them
python scripts/recording_orchestrator.py --skip-steps transcribe,process,archive,cleanup --dry-run

# Output shows:
# ⏭️ Skipping steps: archive, cleanup, process, transcribe
# 🔍 Step 1: Monitor & Detect
# 📁 Found 11 .mp3 files
```

#### **2. Skip Slow Transcription (Test with Existing)**
```bash
# Transcription takes 10+ minutes - skip it to test other steps
python scripts/recording_orchestrator.py --skip-steps transcribe

# Uses existing transcripts in transcripts/ folder
# Continues with processing, archiving, cleanup
```

#### **3. Keep Files for Re-Testing**
```bash
# Don't archive or delete - keep everything in place
python scripts/recording_orchestrator.py --skip-steps archive,cleanup

# Files stay on USB and in transcripts/ folder
# Can re-run tests without re-recording
```

#### **4. Debug Full Workflow**
```bash
# See every detail of what's happening
python scripts/recording_orchestrator.py --verbose

# Shows:
# DEBUG - Checking file: 251007_0435.mp3
# DEBUG - File size: 0.3 MB
# DEBUG - Estimated duration: 0.3 minutes
```

#### **5. Full Dry-Run Simulation**
```bash
# See what WOULD happen without doing anything
python scripts/recording_orchestrator.py --dry-run

# Shows complete workflow without file operations
```

---

## 💡 Pro Tips

### Combining Flags

**Multiple flags work together:**
```bash
# Dry-run + verbose + skip transcription
python scripts/recording_orchestrator.py --dry-run --verbose --skip-steps transcribe

# Single file + dry-run + verbose
python scripts/process_transcripts.py --file test.txt --dry-run -v
```

### Rapid Iteration

**Old workflow (10 minutes per test):**
```bash
# Edit code
python scripts/process_transcripts.py
# → Wait 10 minutes
# → Check 27 Notion entries
# → Find bug
# → Delete 27 test entries
# → Repeat
```

**New workflow (30 seconds per test):**
```bash
# Edit code
python scripts/process_transcripts.py --dry-run --file test.txt
# → See results in 30 seconds
# → No Notion cleanup needed
# → Iterate 20x faster!
```

### Debugging Steps

**When something fails:**

1. **Run with verbose first:**
   ```bash
   python scripts/process_transcripts.py --file problem.txt --verbose
   ```

2. **Add dry-run to see analysis:**
   ```bash
   python scripts/process_transcripts.py --file problem.txt --verbose --dry-run
   ```

3. **Check logs for details:**
   ```bash
   tail -100 logs/ai-assistant.log
   ```

---

## 📊 Impact Comparison

### Before CLI Foundation

| Task | Time | Notion Cleanup |
|------|------|----------------|
| Test project detection | 10 min | 27 entries |
| Debug icon selection | 10 min | 27 entries |
| Test config change | 10 min | 27 entries |
| Test single file | 10 min | 1 entry |
| **Total for 4 tests** | **40 min** | **82 entries** |

### After CLI Foundation

| Task | Command | Time | Notion Cleanup |
|------|---------|------|----------------|
| Test project detection | `--dry-run --file test.txt -v` | 30 sec | 0 entries |
| Debug icon selection | `--dry-run --file test.txt -v` | 30 sec | 0 entries |
| Test config change | `--config new.yaml --dry-run` | 30 sec | 0 entries |
| Test single file | `--file test.txt --dry-run` | 30 sec | 0 entries |
| **Total for 4 tests** | | **2 min** | **0 entries** |

**Result: 20x faster testing, zero cleanup overhead!**

---

## 🚨 Important Notes

### Dry-Run Guarantees

**When `--dry-run` is used:**
- ✅ NO Notion entries created
- ✅ NO files saved to `processed/`
- ✅ NO files moved or archived
- ✅ NO files deleted
- ✅ Shows exactly what WOULD happen

**Safe to run as many times as you want!**

### Backwards Compatibility

**Running without flags works exactly like before:**
```bash
# This still works the same way
python scripts/process_transcripts.py

# Processes all files
# Creates Notion entries
# Saves JSON files
```

**No breaking changes!**

### Skip-Steps Behavior

**When steps are skipped:**
- Orchestrator assumes prerequisites are met
- Example: `--skip-steps transcribe` assumes transcripts already exist
- Use with care - skipping wrong steps may cause errors

---

## 🎯 Quick Reference

### Test Before Committing
```bash
# Always dry-run test first
python scripts/process_transcripts.py --dry-run --file new_feature_test.txt --verbose
```

### Debug Production Issues
```bash
# Verbose logs show everything
python scripts/process_transcripts.py --verbose --file failing_transcript.txt
```

### Fast Iteration During Development
```bash
# Edit code, test instantly
python scripts/process_transcripts.py --dry-run --file test.txt
```

### Safe Config Testing
```bash
# Test new configs without risk
python scripts/process_transcripts.py --config experimental.yaml --dry-run
```

---

*Last Updated: October 7, 2025 - Milestone 1.3 Complete*

