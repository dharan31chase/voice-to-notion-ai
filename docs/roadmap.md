# AI Assistant - Product Roadmap
**Last Updated**: October 9, 2025  
**Status**: Active Development - Phase 2 In Progress

---

## 📊 Roadmap Overview

This document consolidates all planned work across the AI Assistant project, organized by strategic initiative. Items marked with 🔍 need clarification.

### Quick Navigation
- [🏗️ Architecture Refactoring](#-architecture-refactoring-initiative) (Current Focus)
- [🎙️ Recording & Transcription](#-recording--transcription-initiative)
- [🤖 AI & Content Analysis](#-ai--content-analysis-initiative)
- [📝 Notion Integration](#-notion-integration-initiative)
- [⚡ Performance & Scale](#-performance--scale-initiative)
- [🔧 Configuration & Tools](#-configuration--tools-initiative)
- [📈 Quality & Reliability](#-quality--reliability-initiative)

---

## 🏗️ Architecture Refactoring Initiative
**Goal**: Improve maintainability through Single Responsibility Principle and separation of concerns

### ✅ Completed (Phase 1)
- [x] **Milestone 1.1**: Configuration System - YAML-based config with env overrides
- [x] **Milestone 1.2**: Shared Utilities - OpenAI client, file utils, logging (87% code reduction)
- [x] **Milestone 1.3**: CLI Foundation - argparse with dry-run, verbose, skip-steps

### 🚀 In Progress (Phase 2)
- [x] **Milestone 2.1**: Extract Parsing Logic - Smart heuristics, 95%+ category detection
- [x] **Milestone 2.2**: Extract AI Analysis Logic - TaskAnalyzer, NoteAnalyzer with content preservation
- [ ] **Milestone 2.3**: Refactor Main Script - Pure coordinator pattern

### 📋 Planned

#### Phase 3: Refactor `intelligent_router.py` (Week 3)
- [ ] **Milestone 3.1**: Extract Project Detection
  - Create `routers/project_detector.py`
  - Move few-shot learning logic
  - Fuzzy matching improvements
- [ ] **Milestone 3.2**: Extract Duration Estimation
  - Create `routers/duration_estimator.py`
  - Configuration-driven duration rules
- [ ] **Milestone 3.3**: Extract Icon Selection
  - Already has `icon_manager.py`, integrate better
  - Move remaining logic from router

#### Phase 4: Refactor `recording_orchestrator.py` (Week 4) ⚠️ PRODUCTION-CRITICAL
- [ ] **Milestone 4.1**: Extract Step Modules
  - Create `orchestrator/steps/` directory
  - Separate: detect, validate, transcribe, process, archive
- [ ] **Milestone 4.2**: Extract State Management
  - Create `orchestrator/state_manager.py`
  - JSON serialization, session tracking
- [ ] **Milestone 4.3**: Refactor Main Orchestrator
  - Coordinator pattern (like process_transcripts.py)
  - Dependency injection for testability

#### Phase 5: Refactor Remaining Scripts (Week 5)
- [ ] **Milestone 5.1**: Refactor `notion_manager.py`
  - Extract task creation logic
  - Extract note creation logic
  - Content chunking as utility
- [ ] **Milestone 5.2**: Refactor `project_matcher.py`
  - Extract caching logic
  - Extract fuzzy matching logic

#### Phase 6: Polish & Documentation (Week 6)
- [ ] **Milestone 6.1**: Comprehensive Testing
  - Unit tests for all modules
  - Integration tests for workflows
- [ ] **Milestone 6.2**: Documentation
  - API documentation
  - Architecture diagrams
  - Developer onboarding guide

---

## 🎙️ Recording & Transcription Initiative
**Goal**: Improve recording workflow, transcription quality, and processing efficiency

### ✅ Completed
- [x] USB recorder integration (5-step workflow)
- [x] Parallel transcription with CPU monitoring
- [x] Duplicate detection and smart cleanup
- [x] Date-based archive organization
- [x] Basic duration filter (hardcoded 10 min)

### 🚀 High Priority

#### **🎯 Configurable Duration Filter** (NEW - Oct 9, 2025)
**User Need**: "I want to specify which files to transcribe by duration"

**Scope**:
- [ ] Add `duration_filter` config to `settings.yaml`
  - `min_duration_minutes`: Minimum duration (0 = no min)
  - `max_duration_minutes`: Maximum duration (0 = no max)
  - `enabled`: Toggle filter on/off
- [ ] Add CLI flags
  - `--min-duration N`: Filter minimum
  - `--max-duration N`: Filter maximum  
  - `--no-duration-filter`: Disable filtering
- [ ] Implement filtering logic in orchestrator
- [ ] Enhanced logging (show filtered files with reasons)

**Effort**: ~1 hour  
**Value**: High - enables selective processing based on available time

**Examples**:
```bash
# Quick daily processing
python recording_orchestrator.py --max-duration 5

# Weekend batch (all files)
python recording_orchestrator.py --no-duration-filter

# Medium-length content only
python recording_orchestrator.py --min-duration 2 --max-duration 20
```

#### **🎯 Learning Note Formatter** (NEW - Oct 9, 2025 - CLARIFIED)
**User Need**: "Format long-form learning notes (books/talks/lectures) into structured, reusable Notion pages"

**Problem**: Raw transcripts from learning sessions lack structure and need manual cleanup

**Solution**: GPT-4 post-processing pipeline for long-form learning content

**Workflow**:
```
Recording → Whisper → Raw Transcript → [GPT Formatter] → Structured Notion Page
                                           ↑ NEW STEP
```

**Scope**:
- [ ] **Detection Logic**
  - Trigger: Duration ≥10 min + learning keywords (book/author/lecture/talk/podcast)
  - Configurable keywords and min duration
  - Manual override via CLI flag: `--format-as-learning`

- [ ] **Formatter Module** (`formatters/learning_note_formatter.py`)
  - Extract metadata (title, author/speaker)
  - Generate executive summary (3-5 sentences)
  - Organize content with clean Markdown headings (##, ###)
  - Extract action items/questions → "Open Items" section
  - Fix grammar, improve flow, preserve intent
  - Output Notion-ready `.md` format

- [ ] **Configuration** (`config/settings.yaml`)
  ```yaml
  formatters:
    learning_note:
      enabled: true
      min_duration_minutes: 10
      model: "gpt-4"  # Quality over cost for learning
      keywords: [book, author, lecture, talk, podcast, chapter]
      prompt_template: "config/prompts/learning_note_format.txt"
  ```

- [ ] **Prompt Template** (`config/prompts/learning_note_format.txt`)
  - User-provided formatting instructions
  - Metadata extraction rules
  - Summary generation guidelines
  - Open items format specification
  - Easy to iterate without code changes

- [ ] **Notion Integration**
  - Create formatted learning note pages
  - Preserve rich structure (headings, lists, checkboxes)
  - Tag with source type (book/talk/lecture)
  - Link to original project

**Output Format**:
```markdown
# {Title} – {Author}

{Executive Summary: 3-5 sentences capturing core purpose and key takeaways}

## Core Concepts

### Main Section
...

## Open Items

**Action Items:**
- [ ] Research X
- [ ] Follow up on Y

**Questions:**
- How does Z relate to...?

**Bookmarks/References:**
- Page 42: Key quote about...
```

**Model Choice**: GPT-4 (superior formatting quality for learning content)

**Effort**: ~3-4 hours
- 1 hour: Formatter module + detection logic
- 1 hour: Configuration + prompt template setup
- 1 hour: Notion integration for formatted notes
- 1 hour: Testing + prompt refinement

**Value**: High - transforms raw learning transcripts into valuable, reusable knowledge base entries

**Priority**: Medium-High - High value for learning workflow, add after Milestone 2.3

### 📋 Future Enhancements
- [ ] **Actual Audio Duration Detection** (via ffprobe)
  - Replace file size estimation with real duration
  - More accurate than current 1MB ≈ 1 min assumption
- [ ] **Process Skipped Files Later**
  - Track skipped files in state
  - `--only-skipped` flag to process previously filtered files
  - Useful for "quick pass now, long files later" workflow
- [ ] **Speaker Diarization** (who said what)
  - Identify different speakers
  - Useful for meeting/interview recordings
- [ ] **Custom Whisper Prompts per Project**
  - Project-specific vocabulary/context
  - Better accuracy for domain-specific content

---

## 🤖 AI & Content Analysis Initiative
**Goal**: Improve AI-powered analysis, categorization, and content understanding

### ✅ Completed
- [x] Smart parsing with 5-tier heuristics (95%+ accuracy)
- [x] Content preservation for long notes (>800 words)
- [x] Modular analyzers (TaskAnalyzer, NoteAnalyzer)
- [x] Project extraction with fuzzy matching
- [x] AI-powered icon selection (43 content patterns)

### 🚀 In Progress
- [ ] **Milestone 2.3**: Coordinator pattern for analysis pipeline

### 📋 Future Enhancements

#### **Multi-Category Support** (Deferred from Milestone 2.1)
- [ ] Calendar event detection
  - Keywords: "block", "schedule", "meeting", "appointment"
  - Route to Google Calendar workflow
- [ ] New project creation detection
  - Keywords: "new project", "start project"
  - Route to Notion Projects database
- [ ] Resource/reference detection
  - Keywords: "resource", "reference", "documentation"
  - Route to Notion Resources database

#### **Advanced Analysis Features**
- [ ] Sentiment analysis (positive/negative/neutral tasks)
- [ ] Priority detection (urgent/high/medium/low)
- [ ] Deadline extraction from natural language
  - "by Friday" → set due date
  - "next week" → calculate date
- [ ] Relationship detection (task dependencies)
- [ ] Tag auto-generation from content

#### **Learning & Improvement**
- [ ] Feedback loop for category detection
  - Track user corrections (task → note, etc.)
  - Improve detection rules based on patterns
- [ ] Custom rules per user
  - "For me, 'I noticed' means note, not task"
  - Personalized heuristics

---

## 📝 Notion Integration Initiative
**Goal**: Enhanced Notion integration with better features and reliability

### ✅ Completed
- [x] Task and Note creation
- [x] Project relation mapping
- [x] Content chunking (2000 char blocks)
- [x] Emoji icon assignment
- [x] Manual review tags

### 📋 Future Enhancements
- [ ] **Bi-directional Sync**
  - Pull tasks from Notion → update via voice
  - "Mark task X as complete" → update Notion status
- [ ] **Template Support**
  - Project-specific templates
  - Different properties per project type
- [ ] **Batch Updates**
  - Update multiple entries at once
  - Reduce API calls
- [ ] **Rich Content**
  - Embed images/links in notes
  - Code block formatting
  - Tables and lists
- [ ] **Notion Databases Beyond Tasks/Notes**
  - Journal entries
  - Meeting notes
  - Book summaries
  - Workout logs

---

## ⚡ Performance & Scale Initiative
**Goal**: Faster processing, better resource usage, scale to more files

### 🔍 Known Issues (NEEDS INVESTIGATION)
- 🔍 **Slow Transcription** - User reports "kinda really slow"
  - Current: Whisper small model, parallel batches
  - Question: Is it Whisper itself or API calls?
  - Question: Which files are slowest? (long files only or all?)

### 📋 Planned Improvements

#### **Transcription Performance**
- [ ] **Model Selection Strategy**
  - Tiny model for quick reminders (< 1 min)
  - Small model for normal recordings (1-10 min)
  - Medium model only when needed (10-30 min)
  - Cache model in memory (avoid reload)
- [ ] **Parallel Processing Optimization**
  - Current: 4 files per batch
  - Experiment: Dynamic batch size based on CPU/memory
  - Smart batching: Group similar-duration files
- [ ] **GPU Acceleration** (if available)
  - Detect CUDA/Metal support
  - Use GPU for Whisper if present
  - Fallback to CPU gracefully

#### **AI Analysis Performance**
- [ ] **Caching & Reuse**
  - Cache project detection results
  - Reuse icon patterns across files
  - Batch API calls where possible
- [ ] **Smarter API Usage**
  - Use GPT-3.5-turbo for simple tasks
  - Reserve GPT-4 for complex analysis
  - Parallel API calls (multiple files at once)

#### **System Optimization**
- [ ] **Async/Await Pattern**
  - Replace threads with async for I/O
  - Better resource utilization
- [ ] **Progress Streaming**
  - Show real-time progress (not just batch summaries)
  - ETA calculation
  - Cancellable operations

---

## 🔧 Configuration & Tools Initiative
**Goal**: Flexible configuration, powerful CLI, better developer experience

### ✅ Completed
- [x] YAML-based configuration system
- [x] Environment variable overrides
- [x] CLI with dry-run, verbose, skip-steps
- [x] Icon mapping configuration
- [x] Parsing rules configuration

### 📋 Future Enhancements
- [ ] **Configuration Validation**
  - Schema validation for YAML files
  - Clear error messages for invalid config
  - Default value fallbacks
- [ ] **Configuration Profiles**
  - `config/profiles/quick.yaml` - fast, short files only
  - `config/profiles/comprehensive.yaml` - all files, max quality
  - `config/profiles/testing.yaml` - dry-run defaults
  - `--profile quick` CLI flag
- [ ] **Interactive Setup Wizard**
  - First-time configuration helper
  - API key setup
  - Notion database selection
  - Test connection validation
- [ ] **Web UI** (Stretch Goal)
  - Dashboard for processing status
  - Configuration editor
  - File queue management
  - Analytics/statistics

---

## 📈 Quality & Reliability Initiative
**Goal**: Improve success rates, error handling, and user confidence

### ✅ Completed
- [x] Graceful error handling at all stages
- [x] Failed file tracking and logging
- [x] Duplicate detection
- [x] State management for recovery
- [x] Retry logic with exponential backoff

### 📋 Current Challenges (from Project State)
- **Success Rate**: Currently 82% (goal: 95%+)
- **Network Issues**: Notion API timeouts on home network
- **Manual Review**: Too many files flagged for review

### 📋 Planned Improvements

#### **Error Recovery**
- [ ] **Automatic Retry with Backoff**
  - Already implemented for API calls
  - Extend to file operations
  - Configurable retry attempts
- [ ] **Failure Analysis**
  - Categorize failures (network, validation, AI, etc.)
  - Suggest fixes automatically
  - "3 files failed due to network - retry?"
- [ ] **Partial Success Handling**
  - Continue on non-critical failures
  - Report summary at end
  - "15/17 succeeded, 2 need retry"

#### **Validation & Testing**
- [ ] **Pre-flight Checks**
  - Verify API keys before processing
  - Check disk space proactively
  - Validate configuration on startup
- [ ] **Integration Tests**
  - End-to-end workflow tests
  - Mock external services (Notion, OpenAI)
  - Automated regression testing
- [ ] **Monitoring & Alerts**
  - Success rate tracking over time
  - Alert when success rate drops
  - Performance metrics dashboard

---

## 🗓️ Prioritization & Timeline

### 🔥 **Immediate (This Week)**
1. ✅ Complete Milestone 2.2 (Analyzers) - DONE
2. ⏳ Complete Milestone 2.3 (Coordinator) - IN PROGRESS
3. 🎯 Add Configurable Duration Filter (~1 hour)

### 📅 **Short-term (Next 2 Weeks)**
1. Phase 3: Refactor intelligent_router.py
2. Investigate & fix transcription performance issues 🔍
3. Experiment with transcription quality improvements 🔍

### 📅 **Medium-term (Next Month)**
1. Phase 4: Refactor recording_orchestrator.py (production-critical)
2. Implement multi-category support (calendar, projects, resources)
3. Advanced analysis features (priority, deadlines, tags)

### 📅 **Long-term (Next Quarter)**
1. Phases 5-6: Complete refactoring initiative
2. Web UI for configuration and monitoring
3. Performance optimization (async, GPU, caching)
4. Advanced Notion integration (bi-directional sync, templates)

---

## 📊 Success Metrics

### Current Baseline (Oct 2025)
- **Success Rate**: 82% (goal: 95%+)
- **Processing Speed**: 1.47 files/minute
- **Code Quality**: 87% reduction in duplication (7,160 lines removed)
- **Notion Integration**: 100% success rate
- **Manual Review Rate**: ~15-20% of files

### Target Metrics (Q1 2026)
- **Success Rate**: 95%+ end-to-end
- **Processing Speed**: 3+ files/minute (2x improvement)
- **Code Maintainability**: 90%+ test coverage
- **Notion Integration**: <1% failure rate
- **Manual Review Rate**: <5% of files
- **Transcription Quality**: User satisfaction > 90%

---

## 🔍 Items Needing Clarification

These items are tagged for follow-up discussion:

1. ~~**Transcription Quality Improvements**~~ → **✅ CLARIFIED** as "Learning Note Formatter" (Oct 9, 2025)
   - GPT-4 post-processing for long-form learning content
   - See Recording & Transcription Initiative for full spec

2. **Performance Issues** (Performance & Scale Initiative)
   - Which part is slow: Whisper, AI analysis, or Notion?
   - Is slowness consistent or only for long files?
   - Hardware constraints (CPU, GPU availability)?

3. **Multi-Category Support** (AI & Content Analysis Initiative)
   - Priority order: Calendar → Projects → Resources?
   - Google Calendar integration scope (read/write)?
   - New database schema needed?

---

## 📝 Notes

### How to Use This Roadmap
1. **Current work**: Check "In Progress" sections
2. **Plan next sprint**: Review "High Priority" items
3. **Long-term planning**: Browse all initiatives
4. **Clarification needed**: Search for 🔍 tags

### Relationship to Other Docs
- **`refactoring-plan.md`**: Detailed Phase 1-6 technical plan (subset of this roadmap)
- **`project-state.md`**: Current status, decisions, lessons learned
- **`technical-requirements.md`**: System architecture and specifications

### Contributing to Roadmap
- New ideas → Add to appropriate initiative with 🔍 tag
- Completed items → Move to ✅ Completed section
- Clarified items → Remove 🔍 tag, update description
- Change priorities → Update prioritization section

---

*Last Updated: October 9, 2025*  
*Next Review: After Milestone 2.3 completion*

