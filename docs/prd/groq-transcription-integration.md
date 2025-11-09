# PRD: Groq Transcription Integration

**Status**: Draft  
**Owner**: Dharan Chandra Hasan  
**Last Updated**: 2025-11-08  
**Tech Requirements**: [To be created by Claude Code]

---

## 🎯 TL;DR

Integrate Groq Cloud API (whisper-large-v3) into the voice-to-Notion pipeline's transcription engine to achieve **10-20x speed improvement** (8 minutes → 30 seconds for 6 files), unlocking the ability to process customer discovery interviews (30+ minute recordings) that currently time out or take too long.

---

## 🎯 Problem Statement

**User Pain Point**:

The voice-to-Notion pipeline currently uses local Whisper transcription, which creates a critical bottleneck:

- **Current performance**: 8 minutes to process 5 files (after Phase 1 optimization)
- **Blocking use case**: Customer discovery interviews (30+ minutes) are **unprocessed** because they take too long
- **Daily friction**: Can't quickly process recordings - need to wait 8+ minutes even for short batches
- **Scalability issue**: As recording volume increases, processing time becomes prohibitive

**Current Workaround**:

Skip processing long-form recordings, or batch them for "later" processing that never happens. This means valuable customer insights from interviews are lost or delayed.

**Why Now**:

1. **Customer discovery active**: Currently conducting interviews for Legacy AI, need fast turnaround
2. **Groq API proven**: whisper-large-v3 available, 95-97% accuracy, 1-5 seconds per 3-minute file
3. **Phase 1 optimization complete**: Local improvements maxed out (4.2x faster, but still not fast enough)
4. **Baby deadline approaching**: January 2026 - need faster workflows before time availability drops

---

## 🔧 High-Level Approach

**Strategy**: Create TranscriptionService abstraction with simple fallback

**Architecture**:
```
TranscriptionService (abstraction layer)
├── GroqBackend (primary) - Cloud API, 1-5 sec/file
└── LocalWhisperBackend (fallback) - Local, always works offline
```

**The flow**:
1. User runs recording orchestrator
2. TranscriptionService tries Groq first (fastest)
3. If Groq fails (offline, API down, rate limit) → fall back to local Whisper
4. **Result**: System never fails, always uses fastest available method

**Why This Approach**:

- **Speed**: Groq is 10-20x faster than local (30 sec vs 8 min for 6 files)
- **Reliability**: Fallback ensures 100% uptime (local Whisper always works)
- **Accuracy**: whisper-large-v3 model maintains 95-97% accuracy
- **Zero setup**: No model downloads, works immediately with API key
- **Cost**: Free tier covers 14,400 sec/day (240 minutes of audio)
- **Simplicity**: Two backends only - no unnecessary complexity

**Alternatives Considered**:

**Alternative A: Pure Groq (no fallback)**
- Why not: Single point of failure, breaks when offline or API down

**Alternative B: Keep local Whisper only**
- Why not: Still too slow, doesn't unlock customer interviews

**Alternative C: Add OpenAI Whisper API as middle fallback**
- Why not: Unnecessary complexity, local Whisper already provides reliable fallback

---

## ✅ Success Criteria

**Must Have** (Launch blockers):

1. **Speed**: Process 6 files in <30 seconds (vs. current 8 minutes)
   - Measurement: End-to-end time from orchestrator start to transcripts ready
   - Baseline: 8 minutes for 5 files (current)
   - Target: 30 seconds for 6 files (10-20x improvement)

2. **Accuracy**: ≥95% transcription accuracy (match or exceed local Whisper)
   - Measurement: Manual review of 10 sample transcripts
   - Baseline: ~95% with local Whisper
   - Target: 95-97% with Groq whisper-large-v3

3. **Reliability**: 100% success rate with fallback
   - Measurement: No failed transcriptions even when Groq is down
   - Test: Disable Groq API key, verify local fallback works seamlessly

4. **Zero breaking changes**: Existing workflow still works
   - Measurement: Process recordings with no code changes needed
   - Backward compatibility: Can still use local-only mode if desired

**Nice to Have** (Post-launch):

1. **Automatic mode selection** (defer to Phase 3 - Auto-Switching)
2. **Cost tracking** (Groq API usage monitoring)
3. **Performance analytics** (track speed improvements over time)

**Metrics**:

- **Time saved per batch**: 8 min → 30 sec = **7.5 minutes saved per 6 files**
- **Customer interviews unlocked**: Can now process 30+ min recordings in <2 minutes (vs. 30+ min before)
- **Daily throughput increase**: 10-20x more recordings can be processed in same time
- **Setup time**: 0 minutes (just add API key, no model downloads)

**2x Leverage Validation**: If we're not processing at least 5x faster, the integration hasn't achieved its goal.

---

## 🚫 Non-Goals

1. **Multi-cloud redundancy** (Groq + AssemblyAI + Deepgram + OpenAI)
   - Why: Single cloud provider (Groq) + local fallback is sufficient for Tier 0
   - PARITY estimate if we did it: 6-8 hours (multiple API integrations)
   - Deferred to: Tier 1 (if Groq proves unreliable)

2. **Real-time streaming transcription**
   - Why: Batch processing is sufficient for current workflow
   - PARITY estimate if we did it: 10-12 hours (WebSocket integration)
   - Deferred to: Tier 2 (if live transcription becomes needed)

3. **Custom fine-tuned models**
   - Why: whisper-large-v3 already achieves 95-97% accuracy
   - PARITY estimate if we did it: 20+ hours (training data collection, fine-tuning)
   - Deferred to: Tier 2 (if accuracy becomes issue)

4. **Speaker diarization** (who said what in multi-person recordings)
   - Why: Most recordings are solo voice notes
   - PARITY estimate if we did it: 8-10 hours
   - Deferred to: Tier 2 (if meeting transcription becomes primary use case)

5. **Automatic language detection**
   - Why: All recordings are English
   - PARITY estimate if we did it: 2-3 hours
   - Deferred to: Tier 2 (if multilingual support needed)

**Scope protection**: With baby arriving January 2026, these non-goals aren't just deferred - they're actively rejected for this integration to keep the 70-minute timeline.

---

## 👥 User Stories

### Story 1: Fast Customer Interview Processing

**As Dharan** (founder doing customer discovery),  
**I want** customer interview transcripts ready within 2 minutes of ending a call,  
**So that** I can review insights immediately while the conversation is fresh in my mind.

**Acceptance Criteria**:
- [ ] Process 30-minute interview in <2 minutes (vs. 30+ minutes currently)
- [ ] Accuracy ≥95% for technical product discussions
- [ ] Works even when offline (falls back to local)
- [ ] No manual configuration needed (automatic backend selection)

---

### Story 2: Quick Daily Batch Processing

**As Dharan** (daily voice note user),  
**I want** my morning batch of 6 recordings processed in <30 seconds,  
**So that** I can review and organize notes during my 15-minute morning ritual instead of waiting 8 minutes.

**Acceptance Criteria**:
- [ ] Complete batch processing in <30 seconds
- [ ] See progress in real-time (not just batch summary)
- [ ] Zero failures with fallback reliability
- [ ] Works immediately after API key setup

---

### Story 3: Reliable Offline Fallback

**As Dharan** (sometimes working offline),  
**I want** transcription to still work when internet is unavailable,  
**So that** my workflow isn't blocked by connectivity issues.

**Acceptance Criteria**:
- [ ] Auto-detect offline mode
- [ ] Fall back to local Whisper seamlessly
- [ ] User informed which backend was used (logged)
- [ ] No errors or failures, just slower processing

---

## 🎨 Design Notes

**UI/UX Considerations**:

This is infrastructure, not UI. The "user interface" is:
- **For Dharan**: Same command-line workflow (`python recording_orchestrator.py`)
- **Feedback**: Console logs show which backend is being used
- **Progress**: Real-time progress updates during transcription

No new interfaces to learn. Seamless drop-in replacement.

**Configuration**:

New environment variables in `.env`:
```bash
GROQ_API_KEY=your_groq_api_key_here
TRANSCRIPTION_BACKEND=auto  # Options: auto, groq, local
```

New config in `config/settings.yaml`:
```yaml
transcription:
  backend: auto  # auto-detect best available
  groq:
    model: whisper-large-v3
    timeout: 10  # seconds
  local:
    model: turbo
```

**Information Architecture**:

```
scripts/
├── orchestration/
│   └── transcription/
│       ├── transcription_engine.py       # Existing
│       ├── transcription_service.py      # NEW - Abstraction layer
│       ├── backends/
│       │   ├── __init__.py               # NEW
│       │   ├── base_backend.py           # NEW - Interface
│       │   ├── groq_backend.py           # NEW - Groq implementation
│       │   └── local_whisper_backend.py  # NEW - Existing logic extracted
│       └── transcription_engine.py       # UPDATED - Use TranscriptionService
```

---

## ❓ Open Issues & Key Decisions

### Key Decisions Made

**1. Groq as Primary Backend** (November 8, 2025):
- **Why**: Fastest available (1-5 sec per file), high accuracy (95-97%), generous free tier
- **Trade-offs**: Cutting-edge service (could change pricing/limits), cloud dependency
- **Impact**: 10-20x speed improvement enables customer interview processing
- **Two-way door**: Can switch to different provider if Groq becomes unreliable

**2. Simple Two-Backend Fallback** (November 8, 2025):
- **Why**: Local Whisper already proven reliable - no need for OpenAI middle layer
- **Trade-offs**: Less redundancy, but simpler implementation and zero additional dependencies
- **Impact**: 100% uptime (local always works) with minimal complexity
- **Two-way door**: Can add more cloud providers if Groq proves unreliable

**3. TranscriptionService Abstraction** (November 8, 2025):
- **Why**: Clean separation allows easy backend swapping, testing, and future enhancements
- **Trade-offs**: Slightly more code, but much better architecture
- **Impact**: Can add new backends (AssemblyAI, Deepgram, OpenAI) without touching orchestrator
- **One-way door**: Once abstracted, should never go back to hardcoded backends

**4. Auto-Detection Deferred to Phase 3** (November 8, 2025):
- **Why**: Keep Phase 2 scope tight (70 minutes), auto-switching is 30-minute add-on
- **Trade-offs**: Manual backend selection initially, but user can set TRANSCRIPTION_BACKEND=auto
- **Impact**: Phased delivery - speed first (Phase 2), intelligence second (Phase 3)
- **Two-way door**: Can add auto-detection after proving core integration works

---

## 🔗 Links

- **Tech Requirements**: [To be created by Claude Code]
- **Related Roadmap**: `docs/roadmap.md` - Phase 2: Groq Cloud Migration
- **Architecture Context**: `docs/refactoring-plan.md` - Phase B Step 5 (TranscriptionEngine)
- **Groq API Docs**: https://console.groq.com/docs/quickstart

---

## 📅 Timeline & Status

**Current Status**: Draft PRD  
**Target Completion**: November 8, 2025 (70 minutes estimated)  

**Timeline**:
- **Phase 2 (This PRD)**: 70 minutes - Groq integration + fallback to local
- **Phase 3 (Next PRD)**: 30 minutes - Auto-switching intelligence (defer until Phase 2 validated)

**Key Milestones**:
- PRD approval: November 8, 2025
- Implementation: 70 minutes (Claude Code session)
- Testing: 10 minutes (process real customer interview)
- Validation: Measure speed improvement, accuracy, fallback reliability

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|----------|
| 2025-11-08 | Claude (Sonnet 4.5) | Initial draft - Groq transcription integration for 10-20x speed improvement |
| 2025-11-08 | Claude (Sonnet 4.5) | Simplified to two-backend architecture (removed OpenAI, keeping Groq + Local only) |

---

## 🎓 Systems Thinking Applied

**Leverage Point #6 - Information Flows** (High Impact):
- **Current broken flow**: Slow transcription → batch delay → insights lost/delayed
- **New automated flow**: Groq API (fast) → immediate transcripts → timely insights
- **Impact**: Unlocks customer interview processing, enables same-day insight capture

**Reinforcing Loop R1: Speed Enables Usage**
```
Fast transcription → More recordings processed → More insights captured → 
Higher value → More usage → (repeat)
```

**Balancing Loop B1: Fallback Reliability**
```
Cloud service down → Auto-fallback triggered → Local processing → 
System stays operational → (equilibrium)
```

**Why This Matters for 100,000X**:

- **Amplifies, not replaces**: API speeds up transcription, but YOU still do the insight work
- **Eliminates friction**: 8 min → 30 sec = 15.7x reduction in processing time
- **Compounds over time**: Every customer interview benefits, every daily batch benefits
- **Protects against failure**: Fallback ensures workflow never breaks
- **Simplicity enables sustainability**: Two backends easier to maintain than three

---

**End of PRD**
