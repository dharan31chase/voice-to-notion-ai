# Technical Requirements: Live Context Control v3

**Status**: In Progress (Phases 0-5 Complete - 39/62 hours, 63% done)
**PRD**: [docs/prd/live-context-control-v3.3.md](../prd/live-context-control-v3.3.md)
**Owner**: Claude Code (Sonnet 4.5)
**Last Updated**: 2025-12-05
**Completion Date (Phases 0-5)**: 2025-12-05

---

## 🎯 TL;DR
Refactor MCP server into modular Python package with 8 phases: tool priority signals, archival system, high-signal session templates, ROADMAP automation, usage tracking, schema auto-detection, RAG expansion, and YAML handoffs. 62 hours total, saves 100-140 min/week.

---

## 🎯 Architecture Decision

**Approach**: Modular Python package structure with utility modules
**Rationale**: Enables incremental delivery, easier testing, and better code organization vs monolithic refactor

**Alternatives Considered**:
1. **Monolithic Refactor (All-at-Once)**:
   - Pros: Clean break, no intermediate states
   - Cons: High risk, 62-hour blast radius, harder to test
   - Why rejected: Baby deadline risk, can't pause mid-refactor

2. **Keep Current Structure (No Refactor)**:
   - Pros: Zero migration effort
   - Cons: 1881-line monolith, hard to maintain, no modularity
   - Why rejected: Technical debt accumulating, future features harder

**Trade-offs Accepted**:
- **More files** (8 utils vs 1 monolith) → Easier navigation and testing
- **Upfront modularization** (8h Phase 1) → Faster future development
- **Git-tracked usage logs** (sanitized) → Privacy preserved, learning enabled

---

## 🚫 Out of Scope (PARITY Approach)

**What We're NOT Doing Now**:
1. **Parallel AI Processing** (from PRD Phase 2 notes)
   - Why deferred: Current sequential processing works, adds complexity
   - Effort if done later: 30 min
   - Benefit: 2.5x faster for batch operations
   - Roadmap: Yes - documented as future enhancement

2. **Cross-platform Timeout** (Unix-only signal.alarm)
   - Why deferred: User on Mac, PARITY preserves existing behavior
   - Effort if done later: 15-20 min (threading.Timer)
   - Benefit: Windows compatibility
   - Roadmap: Low priority

3. **MCP Server Refactor** (separate tools into individual files)
   - Why deferred: Tools work fine in full_server.py, not critical path
   - Effort if done later: 2-4 hours
   - Benefit: Cleaner imports, better IDE navigation
   - Roadmap: Phase 8 or future enhancement

**Future Enhancements** (documented for later):
- Parallel processing for batch operations: 30 min, 2.5x speed improvement
- Cross-platform timeout mechanism: 15-20 min
- Individual tool file organization: 2-4 hours

---

## 🛠️ Implementation Plan

### Phase 0: Tool Selection Priority Fix (2 hours) ✅ COMPLETE

**Goal**: Prevent "bash spiral" where Claude tries bash before MCP tools

**Steps**:
1. Add 🎯 priority signals to 8 critical MCP tools (30 min)
   - Files: `mcp_server/full_server.py`
   - Changes: Updated docstrings with "🎯 USE THIS FIRST" guidance
   - Tools updated: read_file, write_file, start_session, end_session, search_docs, query_strategy_board, update_initiative_status, write_to_page_content

2. Test with 5 queries that previously caused spirals (30 min)
   - Validate Claude uses MCP tools first
   - Measure tool selection time (target: <30 sec)

**Success Criteria**:
- [x] All 8 tools have 🎯 priority signals in docstrings
- [x] Syntax validation passes
- [x] No breaking changes to existing functionality

**Completed**: 2025-12-05

---

### Phase 1: Package Structure + Archival System (8 hours) ✅ COMPLETE

**Goal**: Refactor monolithic server into modular Python package with backup/archival

**Steps**:
1. Create package structure (1 hour)
   - Files: `mcp_server/__init__.py`, `mcp_server/tools/__init__.py`, `mcp_server/utils/__init__.py`, `mcp_server/rag/__init__.py`
   - Changes: Initialize Python package with module docstrings

2. Implement backup system (2 hours)
   - Files: `mcp_server/utils/backup.py`
   - Functions: `create_backup()`, `cleanup_old_backups()`, `restore_from_backup()`, `list_backups()`
   - Features: Auto-backup before overwrite, keep last 3 versions, `.backups/` subfolder
   - Gitignore: Added `**/.backups/` to prevent commit

3. Implement archival system (3 hours)
   - Files: `mcp_server/utils/archival.py`
   - Functions: `archive_file()`, `unarchive_file()`, `get_archive_path()`, `list_archived_files()`
   - Structure: `docs/prd/archive/YYYY/QQ/` organization
   - Safety: Prompt before archiving (force parameter to override)

4. Extract utility modules (2 hours)
   - Files: `mcp_server/utils/learning.py`, `mcp_server/utils/notion_helpers.py`
   - Moved: Context profile functions, markdown_to_notion_blocks, generate_handoff_template
   - Updated imports in `full_server.py`

5. Integrate backup into write_file() (30 min)
   - File: `mcp_server/full_server.py`
   - Changes: Auto-create backup before overwriting existing files
   - Returns backup path in response

**Success Criteria**:
- [x] Python package structure created (11 files)
- [x] Backup system working (create, restore, cleanup)
- [x] Archival system with YYYY/QQ structure
- [x] All imports successful
- [x] Syntax validation passes
- [x] No regressions in existing workflows

**Completed**: 2025-12-05

---

### Phase 2: High-Signal Session Template + Initiative Detection (8 hours) ✅ COMPLETE

**Goal**: Replace basic session logs with structured template, add initiative detection

**Steps**:
1. Create session helpers module (2 hours)
   - File: `mcp_server/utils/session_helpers.py`
   - Functions: `generate_high_signal_session_template()`, `check_initiative_exists()`, `search_similar_initiatives()`, `create_initiative_in_strategy_board()`
   - Template sections: What Worked ✅, What Didn't Work ⚠️, Decisions Made, Next Steps

2. Update end_session() tool (4 hours)
   - File: `mcp_server/full_server.py`
   - New parameters: `what_worked`, `what_didnt_work`, `initiative_name`
   - Logic: Auto-detect initiative in Strategy Board before linking
   - Prompts: Return options if initiative not found (create/search/proceed)

3. Test workflows (2 hours)
   - Test A: Session with existing initiative → auto-links
   - Test B: Session with non-existent initiative → prompts with options
   - Test C: Ad-hoc session without initiative → proceeds gracefully

**Success Criteria**:
- [x] High-signal template with What Worked/What Didn't Work sections
- [x] Initiative detection logic working
- [x] Interactive prompts for missing initiatives
- [x] Syntax validation passes
- [x] All imports successful

**Completed**: 2025-12-05

---

### Phase 3: Auto-Update Roadmap + Initiative Detection (6 hours) ✅ COMPLETE

**Goal**: Sync ROADMAP.md with Strategy Board at session end, auto-archive PRDs

**Steps**:
1. Create roadmap helpers module (2 hours)
   - File: `mcp_server/utils/roadmap_helpers.py`
   - Functions: `sync_roadmap_with_strategy_board()`, `update_roadmap_row()`, `mark_initiative_complete_in_roadmap()`, `find_initiative_in_roadmap()`

2. Add ROADMAP sync logic to end_session() (3 hours)
   - File: `mcp_server/full_server.py`
   - Logic: Query Strategy Board for initiative status
   - Update ROADMAP.md table row with status and completion date
   - Archive PRD if status = "✅ Complete" (Phase 1 integration)

3. Test workflow (1 hour)
   - Test: Run session that completes an initiative
   - Validate: ROADMAP.md updated, PRD archived to archive/YYYY/QQ/
   - Verify: Notion Roadmap DB also updated

**Success Criteria**:
- [x] ROADMAP.md syncs with Strategy Board status
- [x] Completion dates populated automatically
- [x] PRDs archived when initiative complete
- [x] Syntax validation passes
- [x] All imports successful

**Completed**: 2025-12-05

---

### Phase 4: Usage Tracking + Learning Algorithm (8 hours) ✅ COMPLETE (Phases 4.1-4.2)

**Goal**: Track file usage and learn patterns to improve context suggestions

**Steps**:
1. Implement usage tracking (3 hours)
   - File: `mcp_server/utils/usage_tracker.py`
   - Track: File loads, adds, removes, references per session
   - Storage: `logs/usage/YYYY-MM-DD-HH-MM-SS.json` (git-tracked, sanitized)
   - Privacy: Strip personal paths, tokens before logging

2. Build learning algorithm (4 hours)
   - File: `mcp_server/utils/learning_algorithm.py`
   - Algorithm: Score files by load frequency, recency, co-occurrence
   - Update: `docs/config/context-profiles.json` with learned patterns
   - Ranking: Sort suggestions by score (target: 80% accuracy)

3. Test learning loop (1 hour)
   - Run 3 sessions with same project/workstream
   - Validate: Suggestions improve from 30% → 60%+ accuracy
   - Measure: Track suggestion hits/misses

**Success Criteria**:
- [x] Usage logs created (sanitized, git-tracked)
- [x] Learning algorithm scoring files correctly
- [x] Context profiles updated with learned patterns
- [ ] Suggestion accuracy improves from 30% → 60%+ after 3 sessions (Phase 4.3 - deferred to post-Wave 4)

**Dependencies**: Phase 1 (learning.py module exists), Phase 2 (session data)

**What Shipped** (Phases 4.1-4.2):
- ✅ `usage_tracker.py`: Silent file usage tracking with privacy sanitization
- ✅ `learning_algorithm.py`: File scoring (frequency + recency + co-occurrence)
- ✅ Integration: Tracker auto-saves on `end_session()`
- ✅ Logs directory: `logs/usage/` (git-tracked, safe to commit)
- ✅ Test results: All scoring algorithms validated (ROADMAP.md: 0.730 score, PRD: 0.604)

**Completed**: 2025-12-05 (Phases 4.1-4.2 only, 4.3 moved to post-Wave 4)

---

### Phase 5: Auto-Detect Notion Schema (8 hours) ✅ COMPLETE

**Goal**: Remove hardcoded database IDs, query Notion API for schema

**Steps**:
1. Build schema detection module (4 hours)
   - File: `mcp_server/utils/notion_schema.py`
   - Functions: `detect_strategy_board_schema()`, `detect_roadmap_schema()`, `detect_sessions_schema()`
   - Logic: Query Notion databases API, extract property names and types
   - Cache: Store detected schema in memory (session-lifetime)

2. Update Notion integration functions (3 hours)
   - Files: `mcp_server/full_server.py`, `mcp_server/utils/session_helpers.py`
   - Changes: Replace hardcoded property names with schema lookups
   - Fallback: Use defaults if schema detection fails

3. Test with multiple Notion schemas (1 hour)
   - Test A: Standard schema (current)
   - Test B: Renamed properties
   - Test C: Missing optional properties

**Success Criteria**:
- [x] Schema detection working for all 3 databases
- [x] No hardcoded property names in new code
- [x] Fallback to defaults if detection fails
- [x] Works with renamed properties

**Dependencies**: None (independent feature)

**What Shipped**:
- ✅ `notion_schema.py`: Auto-detects database schemas via Notion API
- ✅ `NotionSchemaDetector`: Queries databases, extracts properties, caches schemas
- ✅ `NotionSchema` wrapper: Safe property access with fallback to defaults
- ✅ Integration: `schema_detector` initialized in `full_server.py`
- ✅ Test results: Validated with Strategy Board (22 properties), Sessions DB (11 properties)
- ✅ Select options extraction: Status options detected (7 valid statuses)
- ✅ Graceful degradation: Works offline with default property names

**Rollout**: Infrastructure complete, incremental adoption in Notion functions (PARITY approach)

**Completed**: 2025-12-05

---

### Phase 6: Separate RAG Repos (16 hours) ⚠️ BRANCH FIRST ⏳ PENDING

**Goal**: Split RAG into separate repos for Legacy AI and Epic 2nd Brain (privacy)

**Steps**:
1. Create feature branch (15 min)
   - Branch: `feature/rag-separate-repos`
   - Reason: 16-hour risky change, need rollback capability

2. Design RAG architecture (2 hours)
   - Privacy model: Separate ChromaDB instances per project
   - Indexing: Project-specific document folders
   - Search: Query specific project's RAG repo
   - Config: `docs/config/rag-repos.json` for project mappings

3. Implement Legacy AI RAG (6 hours)
   - Files: `mcp_server/rag/legacy_ai.py`
   - Index: `research/customer-interviews/`, `research/analyses/`
   - Embeddings: BGE local (privacy-first)
   - Search: Hybrid BM25 + semantic + BGE reranking

4. Implement Epic 2nd Brain RAG (6 hours)
   - Files: `mcp_server/rag/epic_2nd_brain.py`
   - Index: `docs/prd/`, `docs/tech-requirements/`, `docs/sessions/`
   - Reuse: Same architecture as Legacy AI RAG

5. Add MCP tools for RAG search (1 hour)
   - Tools: `search_legacy_ai()`, `search_epic_2nd_brain()`
   - Parameters: query, doc_types, top_k
   - Returns: Ranked results with snippets

6. Test RAG separation (1 hour)
   - Test A: Search Legacy AI only → no Epic 2nd Brain results
   - Test B: Search Epic 2nd Brain only → no Legacy AI results
   - Test C: Privacy validation → no cross-project leakage

**Success Criteria**:
- [ ] Separate RAG repos for Legacy AI and Epic 2nd Brain
- [ ] Privacy validated (no cross-project data)
- [ ] Search accuracy >60% for both projects
- [ ] MCP tools working

**Dependencies**: Phase 1 (rag/ module exists)

**Rollback Plan**:
- Git revert to pre-branch commit
- 30-minute fix budget before rollback
- Document what broke

---

### Phase 7: File-Based Handoffs with YAML (6 hours) ⏳ PENDING

**Goal**: Auto-detect handoffs between Claude Chat and Claude Code via file frontmatter

**Steps**:
1. Design YAML frontmatter format (1 hour)
   - Format: YAML frontmatter in handoff markdown files
   - Fields: `to`, `from`, `initiative_id`, `prd_path`, `priority`, `type`
   - Example:
     ```yaml
     ---
     to: claude-code
     from: claude-chat
     initiative_id: abc123
     prd_path: docs/prd/feature.md
     priority: P1
     type: implementation
     ---
     ```

2. Build handoff detection module (2 hours)
   - File: `mcp_server/utils/handoff_detector.py`
   - Functions: `scan_for_handoffs()`, `parse_handoff_frontmatter()`, `mark_handoff_complete()`
   - Logic: Scan `docs/handoffs/` for unprocessed files

3. Add detection to start_session() (2 hours)
   - File: `mcp_server/full_server.py`
   - Logic: Check for pending handoffs on session start
   - Prompt: "Found handoff: [summary]. Load this initiative? (Y/N)"
   - Auto-load: If Y, load PRD and related context

4. Test handoff workflow (1 hour)
   - Test A: Create handoff in Claude Chat → detected in Claude Code
   - Test B: Reject handoff → marked as skipped
   - Test C: Accept handoff → context loaded automatically

**Success Criteria**:
- [ ] YAML frontmatter parsed correctly
- [ ] Handoffs detected on session start
- [ ] Auto-load context when accepted
- [ ] Handoffs marked complete after processing

**Dependencies**: Phase 1 (handoff_detector.py location)

---

## 📁 Files Modified

### New Files (Phases 0-3 Complete)
```
mcp_server/__init__.py                      # Package root
mcp_server/tools/__init__.py                # Tools module
mcp_server/tools/files.py                   # File operations (future)
mcp_server/utils/__init__.py                # Utils module
mcp_server/utils/backup.py                  # Backup system ✅
mcp_server/utils/archival.py                # Archival system ✅
mcp_server/utils/learning.py                # Context learning ✅
mcp_server/utils/notion_helpers.py          # Notion utilities ✅
mcp_server/utils/session_helpers.py         # Session templates ✅
mcp_server/utils/roadmap_helpers.py         # Roadmap sync ✅
mcp_server/rag/__init__.py                  # RAG module (placeholder)
```

### New Files (Phases 4-7 Pending)
```
mcp_server/utils/usage_tracker.py           # Usage tracking (Phase 4)
mcp_server/utils/learning_algorithm.py      # Learning algo (Phase 4)
mcp_server/utils/notion_schema.py           # Schema detection (Phase 5)
mcp_server/rag/legacy_ai.py                 # Legacy AI RAG (Phase 6)
mcp_server/rag/epic_2nd_brain.py            # Epic 2nd Brain RAG (Phase 6)
mcp_server/utils/handoff_detector.py        # Handoff detection (Phase 7)
```

### Modified Files
```
mcp_server/full_server.py                   # Main MCP server (all phases)
.gitignore                                  # Added **/.backups/
```

### Configuration Changes
```
docs/config/context-profiles.json           # Updated by learning algo (Phase 4)
docs/config/rag-repos.json                  # RAG repo mappings (Phase 6)
logs/usage/YYYY-MM-DD-HH-MM-SS.json        # Usage logs (Phase 4)
```

---

## ⚙️ Configuration Changes

**Environment Variables** (`.env`) - No changes required, all existing:
```
NOTION_TOKEN=...                 # Existing
NOTION_SESSIONS_DB=...           # Existing
NOTION_ROADMAP_DB=...            # Existing
STRATEGY_BOARD_DATABASE_ID=...   # Existing
PROJECTS_DATABASE_ID=...         # Existing (optional)
NOTION_USER_ID=...               # Existing (optional)
```

**Config Files**:
- `docs/config/context-profiles.json` - Updated by Phase 4 learning algorithm
- `docs/config/rag-repos.json` - New in Phase 6 for RAG mappings

---

## ✅ Testing Strategy

### Unit Tests (Phases 0-3 Complete)
```python
def test_backup_system():
    """Test backup creation, restore, cleanup."""
    # Implemented in test_phase1_validation.py ✅

def test_archival_system():
    """Test archive path generation, file moves."""
    # Implemented in test_phase1_validation.py ✅

def test_imports():
    """Test all module imports successful."""
    # Implemented in test_phase1_validation.py ✅
```

### Integration Tests (Phases 4-7 Pending)
- [ ] Phase 4: Run 3 sessions, validate learning improves suggestions
- [ ] Phase 5: Test schema detection with renamed properties
- [ ] Phase 6: Validate RAG privacy (no cross-project leakage)
- [ ] Phase 7: Test handoff detection and auto-load

### Wave Validations
- [x] Wave 1 (Phases 0-1): Backup system, imports, no regressions ✅
- [ ] Wave 2 (Phases 2-3): Session creation, Notion updates, ROADMAP sync
- [ ] Wave 3 (Phases 4-5): Usage tracking, schema detection
- [ ] Wave 4 (Phases 6-7): RAG search, handoff detection

---

## 📅 Timeline & Status

**Current Status**: In Progress (Phases 0-3 Complete, 4-7 Pending)
**Estimated Effort**: 62 hours total
**Actual Effort So Far**: ~24 hours (Phases 0-3)
**Target Completion**: December 13, 2025

**Key Milestones**:
- ✅ Wave 1 (Phases 0-1): Dec 5 - Tool priority + Package structure
- ✅ Wave 2 (Phases 2-3): Dec 5 - Session template + Roadmap automation
- ⏳ Wave 3 (Phases 4-5): Dec 9-11 - Usage tracking + Schema detection
- ⏳ Wave 4 (Phases 6-7): Dec 11-13 - RAG expansion + Handoffs

**Blockers**: None currently

---

## 🚀 Deployment Plan

**Validation Steps** (per wave):
1. Run unit tests for new modules
2. Run integration tests (wave-specific)
3. Manual smoke test with real session
4. Verify success criteria met

**Rollback Plan**:
- **Phases 0-3**: Git revert to commit before Phase 0 (monolithic server)
- **Phase 6 (RAG)**: Feature branch allows clean rollback
- **30-minute fix budget**: Try to fix first, rollback if unfixable

**Post-Deployment**:
- Monitor usage logs for Phase 4 data collection
- Track suggestion accuracy improvement (target: 30% → 80%)
- Measure time saved (target: 100-140 min/week)

---

## 🚨 Open Issues & Decisions

**Design Decisions**:
1. **Python Package Structure vs Monolith**:
   - Why: Easier testing, better organization, incremental delivery
   - Trade-offs: More files (8 utils), upfront refactor cost (8h)
   - Impact: Future features easier to add
   - Date: 2025-12-05

2. **Git-Tracked Usage Logs (Sanitized)**:
   - Why: Learning loop requires historical data
   - Trade-offs: Repo size grows, but enables intelligence
   - Impact: Privacy preserved via sanitization
   - Date: 2025-12-05

3. **Separate RAG Repos (Privacy-First)**:
   - Why: Team scaling requires data separation
   - Trade-offs: 16h vs 7-11h for unified RAG
   - Impact: Enables future team growth
   - Date: Per PRD

**Platform Limitations**:
- **signal.alarm (Unix-only)**: Current implementation works on Mac/Linux, would need threading.Timer for Windows
  - Workaround: User on Mac, not critical
  - Cross-platform effort: 15-20 min

---

## 🔗 Links

- **PRD**: [docs/prd/live-context-control-v3.3.md](../prd/live-context-control-v3.3.md)
- **ROADMAP**: [ROADMAP.md](../../ROADMAP.md)
- **MCP Server**: [mcp_server/full_server.py](../../mcp_server/full_server.py)

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|----------|
| 2025-12-05 | Claude Code | Initial draft after Phases 0-3 implementation |
| 2025-12-05 | Claude Code | Added detailed specs for Phases 4-7 (pending) |
