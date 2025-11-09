# Problem Statement: Groq Cloud API File Size Limit

**Date**: November 8, 2025
**Context**: Phase II Enhancement for Groq Transcription Integration
**Status**: Validated in testing, needs product solution

---

## Problem Overview

Groq Cloud API has a **25MB file size limit** for audio transcription requests. Files exceeding this limit return a `413 Request Entity Too Large` error and must fall back to Local Whisper (130x slower).

---

## Current Behavior

### What Happens Now
1. ✅ Files ≤25MB → Groq Cloud API (1-2 seconds per file)
2. ❌ Files >25MB → Groq fails with 413 error → Local Whisper fallback (90-120 seconds per file)

### Test Results
- **Test Dataset**: 12 files from session_20251106_112341
- **Groq Success**: 11/12 files (91.7%)
- **Groq Failure**: 1 file (46MB) - fell back to Local Whisper

**The Problem**: Large files lose the 130x speed advantage

---

## Impact Assessment

### User Impact
- **Occasional users** (mostly short recordings): ✅ No impact
- **Power users** (long meetings, interviews, lectures): ❌ Significant impact

### Real-World Scenarios Affected

| Scenario | Typical File Size | Impact |
|----------|------------------|--------|
| Quick voice notes (1-3 min) | 1-3 MB | ✅ No impact |
| Daily reflections (5-10 min) | 5-10 MB | ✅ No impact |
| Meetings (30-60 min) | 30-60 MB | ❌ **Falls back to slow Local Whisper** |
| Interviews (60-90 min) | 60-90 MB | ❌ **Falls back to slow Local Whisper** |
| Lectures/workshops (2+ hours) | 120+ MB | ❌ **Falls back to slow Local Whisper** |

### Example from Test Data
- **46MB file** (251106_0851_session_20251106_112341.mp3)
  - Groq: Failed (413 error)
  - Fallback: Local Whisper (estimated 5-7 minutes)
  - **Lost opportunity**: Could have been 5-10 seconds with Groq

---

## Business Impact

### Current State
- **11/12 files** benefit from 130x speed improvement ✅
- **1/12 files** fall back to slow processing ❌
- **Success metric**: 91.7% of files get fast processing

### Future Concern
**What if user records longer content regularly?**
- Weekly team meetings (60 min) → 60MB → Always slow
- Monthly all-hands (90 min) → 90MB → Always slow
- Interview series (60-90 min each) → Always slow

**This limits the product's value proposition for power users**

---

## Technical Constraints

### Groq Cloud API Limits
- **Maximum file size**: ~25 MB
- **Error response**: `413 Request Entity Too Large`
- **No official chunking support**: API expects single file upload

### Audio File Characteristics
- **Format**: MP3
- **Typical bitrate**: 128-192 kbps
- **Size calculation**: ~1 MB per minute of audio
- **25MB limit = ~25 minutes of audio**

---

## Potential Solution Approaches

> **Note**: These are technical possibilities - product requirements should be defined based on user needs

### Option 1: Audio File Chunking (Pre-processing)
**How it works**:
1. Split large files into <20MB chunks before sending to Groq
2. Transcribe each chunk with Groq (still fast!)
3. Merge transcripts back together

**Pros**:
- ✅ Preserves Groq's 130x speed for large files
- ✅ Transparent to user (happens automatically)
- ✅ No loss of accuracy (2-3 second overlap prevents word cutoff)

**Cons**:
- ⚠️ Adds complexity (splitting, merging logic)
- ⚠️ Slightly longer total time (multiple API calls)
- ⚠️ Potential for merge artifacts if not done carefully

**Implementation effort**: 2-3 hours

### Option 2: Hybrid Approach (Smart Routing)
**How it works**:
1. Files ≤25MB → Groq (fast)
2. Files >25MB → Local Whisper (slow but reliable)
3. User notification: "Large file detected, using slower processing"

**Pros**:
- ✅ Simplest implementation (already working!)
- ✅ No risk of chunking artifacts
- ✅ Clear user expectation setting

**Cons**:
- ❌ Large files still slow (defeats purpose of Groq integration)
- ❌ Inconsistent user experience (sometimes fast, sometimes slow)

**Implementation effort**: 0 hours (current state)

### Option 3: User-Initiated Chunking
**How it works**:
1. Detect large files before processing
2. Ask user: "File is large. Split into smaller chunks for faster processing?"
3. User chooses: Fast (Groq, chunked) vs Reliable (Local, whole file)

**Pros**:
- ✅ User control over trade-offs
- ✅ Transparent decision-making
- ✅ Educational (users learn about system capabilities)

**Cons**:
- ⚠️ Adds friction to workflow
- ⚠️ Requires UI/notification system
- ⚠️ Users may not understand trade-offs

**Implementation effort**: 3-4 hours

### Option 4: Parallel Chunking (Advanced)
**How it works**:
1. Split file into chunks
2. Send all chunks to Groq **in parallel** (3-5 workers)
3. Merge transcripts in order

**Pros**:
- ✅ Even faster than sequential chunking (2-3x improvement)
- ✅ Maximizes Groq's speed advantage
- ✅ Scales to arbitrarily large files

**Cons**:
- ⚠️ More complex implementation
- ⚠️ Higher API concurrency (may hit rate limits)
- ⚠️ Requires careful merge logic

**Implementation effort**: 4-5 hours

---

## Key Questions for Product Requirements

### User Experience
1. **Should chunking be automatic or user-controlled?**
   - Automatic = seamless but less control
   - User-controlled = transparent but adds friction

2. **How should we communicate chunking to users?**
   - Silent (just works)
   - Progress indicator ("Processing chunk 3 of 5...")
   - Post-processing notification ("This file was split for faster processing")

3. **What's the acceptable chunk size?**
   - Smaller chunks = more API calls, more merge points
   - Larger chunks = fewer calls, less merge complexity
   - Recommendation: 20MB chunks (leaves 5MB buffer for safety)

4. **How should we handle merge artifacts?**
   - Use overlap (2-3 seconds) to prevent word cutoff
   - Smart boundary detection (pause points in speech)
   - User review option for chunked transcripts?

### Quality vs Speed Trade-offs
5. **Is chunking acceptable if it introduces merge artifacts?**
   - Example: "...and the project was completed on time. On time, we also..."
   - How critical is perfect transcript continuity?

6. **Should users be able to force Local Whisper for large files?**
   - Some users may prefer slow + whole file vs fast + chunked

### Future Scalability
7. **What's the maximum file size we should support?**
   - 46MB (current test case)
   - 100MB (2-hour meetings)
   - Unlimited (full-day recordings)

8. **Should chunking apply to ALL files or just large ones?**
   - Threshold: >25MB only
   - Always chunk (consistent behavior)

---

## Success Criteria for Phase II Solution

### Must Have
- ✅ Files >25MB benefit from Groq speed (no fallback to Local Whisper)
- ✅ Accuracy remains ≥95% after chunking/merging
- ✅ User experience is seamless (minimal friction)

### Should Have
- ✅ Clear communication to users about chunking
- ✅ Configurable chunk size (power user option)
- ✅ Error handling for failed chunks (partial fallback)

### Nice to Have
- ✅ Parallel chunking for 2-3x additional speed
- ✅ Smart boundary detection (split at pauses)
- ✅ User review queue for chunked transcripts

---

## Recommended Next Steps

1. **Claude Chat**: Define Phase II PRD based on this problem statement
   - Decide on chunking approach (automatic vs user-controlled)
   - Define UX for chunked transcripts
   - Set quality acceptance criteria

2. **Technical Implementation**: After PRD approval
   - Implement chunking logic (pydub or ffmpeg)
   - Implement merge logic with overlap handling
   - Add configuration settings

3. **Testing & Validation**
   - Test with 46MB file from current dataset
   - Test with artificially large files (60MB, 100MB, 120MB)
   - Validate merge quality (listen to chunk boundaries)

---

## Appendix: Technical Details

### Current Error Log
```
2025-11-08 21:33:56 - ERROR - Groq API error: 251106_0851_session_20251106_112341.mp3
Error code: 413 - {'error': {'message': 'Request Entity Too Large',
'type': 'invalid_request_error', 'code': 'request_too_large'}}

2025-11-08 21:33:56 - WARNING - ✗ Groq Cloud API failed
2025-11-08 21:33:56 - INFO - Trying Local Whisper...
```

### File Size Distribution (Test Dataset)
- **<1MB**: 4 files (36%)
- **1-5MB**: 5 files (45%)
- **5-25MB**: 1 file (9%)
- **>25MB**: 1 file (9%) ← **Problem case**

### Chunking Pseudocode
```python
def transcribe_with_chunking(audio_file: Path, chunk_size_mb: int = 20):
    file_size_mb = audio_file.stat().st_size / (1024 * 1024)

    if file_size_mb <= 25:
        # Small file: direct Groq transcription
        return groq.transcribe(audio_file)

    # Large file: chunk + transcribe + merge
    chunks = split_audio(audio_file, chunk_size_mb, overlap_sec=2)
    transcripts = [groq.transcribe(chunk) for chunk in chunks]

    # Remove overlap text when merging
    merged = merge_with_overlap_removal(transcripts, overlap_sec=2)
    return merged
```

---

**For Claude Chat**: Use this problem statement to create a Phase II PRD that addresses the 25MB file size limit. Focus on user experience, quality trade-offs, and product requirements rather than technical implementation.
