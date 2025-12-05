# PRD: Live Context Control v3 - Comprehensive MCP Refactor

**Status**: Approved - Ready to Build
**Owner**: Dharan Chandrahasan  
**Created**: 2025-12-05
**Last Updated**: 2025-12-05 (v3.1 - Addressed archival strategy, session template, initiative detection)
**Target Completion**: January 3, 2026 (4 weeks, 62 hours)
**One-Pager**: [Applied Context Engineering](../context/one-pagers/infrastructure/context-engineering.md)
**Current State Analysis**: [MCP Server Analysis](../architecture/mcp-server-current-state-analysis.md)
**Supersedes**: Live Context Control v2 PRD

---

## 🎯 Executive Summary

### TL;DR

Build state-of-the-art MCP server that eliminates 100-140 min/week of context loading friction through 8 integrated phases delivered over 4 weeks. Investment: 62 hours for foundation that scales to 5-10 projects without multiplying friction. Core innovation: Separate RAG architecture (Legacy AI in business repo, Epic 2nd Brain in personal repo) enables team scaling while preserving privacy.

### Problem Statement

**7 validated pain points waste 100-140 min/week:**

1. **Tool Selection Spiral**: Claude tries bash/view before MCP tools (8 steps, 90-120 sec waste)
2. **Repo Organization Hell**: Cluttered repo (orphaned folders, 290 processed files) makes files hard to find, no archival strategy for 50+ completed PRDs
3. **Useless Context Suggestions**: 30% accuracy, files you never use, no learning loop
4. **No In-Repo Search**: Can't find "related PRDs", leads to 8-step spiral or manual navigation
5. **Session Handoff Broken**: Notion database description empty OR low-signal (meta-commentary), manual git commit copying
6. **End-Session Protocol Incomplete**: Roadmap not updated automatically, no initiative detection (what if initiative doesn't exist?)
7. **No Handoff Auto-Detection**: Claude Code doesn't know what to work on at "start session"

**Root cause**: Current MCP server (1,881 lines, 9 tools) built iteratively without unified architecture.

### Solution Overview

**Refactor 70%, Rewrite 30%** through 8 phases:

- **Phase 0**: Tool Selection Priority Fix (2 hours) - Add 🎯 priority signals
- **Phase 1**: Repo Organization Cleanup (5 hours) - Archive orphaned folders + active/archive structure
- **Phase 2**: Session Handoff Fix (3 hours) - High-signal template + initiative detection
- **Phase 3**: End-Session Protocol (2 hours) - Auto-update roadmap + initiative detection
- **Phase 4**: Context Learning Loop (4 hours) - Track usage, improve suggestions
- **Phase 5**: Epic 2nd Brain RAG (12 hours) - Semantic search for personal docs
- **Phase 6**: Legacy AI RAG Migration (12 hours) - Move to separate repo for team scaling
- **Phase 7**: Handoff Auto-Detection (12 hours) - File-based handoffs Claude Code picks up
- **Phase 8**: Context Visibility & Control (4 hours) - `list_context()`, `reload_context()` tools

**Total**: 56 hours implementation + 6 hours testing = 62 hours over 4 weeks

### Success Criteria

**Performance improvements:**
- Tool selection: 90-120 sec → <5 sec (95% reduction)
- Context suggestions: 30% → 80% accuracy (2.7x improvement)
- File discovery: 90-120 sec → <5 sec (95% reduction)
- Session handoff: Manual → Automatic (100% elimination)

**Time saved**: 100-140 min/week (1.7-2.3 hours/week)

**Privacy**: Separate RAG repos enable team scaling without data leakage

**ROI**: 62 hours invested → 88-120 hours saved over 1 year (1.4-1.9x return)

### Timeline

**Week 1 (Dec 5-13)**: Quick Wins - Phases 0-4 (22 hours)
**Week 2-3 (Dec 16-27)**: Heavy Lifting - Phases 5-6 (24 hours)
**Week 4 (Dec 30-Jan 3)**: Polish - Phases 7-8 (16 hours)

**Critical constraint**: Baby due January 5, 2026 - all work must complete by January 3.

---

[Content continues with all sections from previous version, with three key updates shown below...]

---

### Phase 1: Repo Organization Cleanup

**Goal**: Clean cluttered repo, establish organization framework with archival strategy

**Time**: 5 hours

**What Gets Built**:

1. **Archive Orphaned Folders** (2 hours)
   - Move `Failed/` to `archive/failed-experiments/`
   - Move `hold-for-later/` to `archive/hold-for-later/`
   - Move `insights/context-engineering/research/` (290 files) to `archive/context-engineering-research/`
   - Update any references to moved files

2. **Implement Active/Archive Structure** (1 hour)
   - Create `active/` subdirectories for PRDs, sessions, tech-req
   - Create `archive/YYYY/QQ/` structure for completed work
   - Define archival triggers (initiative status = "✅ Complete")

3. **Document Organization Framework** (1 hour)
   - Create `docs/README.md` with folder structure guide
   - Define naming conventions (dates, titles, status)
   - Define archival strategy (when to archive vs delete)
   - Document search behavior (active + archive)

4. **Validate Tool Compatibility** (1 hour)
   - Test `search_docs()` with new structure
   - Test `start_session()` context loading
   - Update paths in context-profiles.json if needed
   - Validate RAG indexes both active and archive

**Folder Structure** (After):

```
docs/
├── README.md (NEW - organization guide)
├── prd/
│   ├── active/              # NEW - in-progress PRDs only
│   │   ├── live-context-control-v3.md
│   │   └── prototype-validation.md
│   └── archive/             # NEW - completed PRDs by year/quarter
│       ├── 2025/
│       │   ├── Q4/
│       │   │   ├── context-sync-bridge.md
│       │   │   └── rag-implementation.md
│       │   └── Q3/
│       │       └── ...
│       └── README.md        # How to search archive
├── tech-req/
│   ├── active/              # NEW - current technical docs
│   └── archive/2025/QQ/     # NEW - completed tech docs
├── sessions/
│   ├── claude-chat/
│   │   ├── active/          # NEW - current month
│   │   └── archive/2025/QQ/ # NEW - by year/quarter
│   └── claude-code/
│       ├── active/
│       └── archive/2025/QQ/
├── context/
│   ├── one-pagers/
│   └── README.md
├── architecture/
├── handoffs/                # NEW - File-based handoffs (Phase 7)
└── archive/                 # Deprecated/experimental work
    ├── failed-experiments/
    ├── hold-for-later/
    └── context-engineering-research/
```

**Archival Logic** (integrated with end_session):

```python
# When initiative status = "✅ Complete"
if initiative_status == "✅ Complete":
    # Calculate archive path
    year = datetime.now().year
    quarter = (datetime.now().month - 1) // 3 + 1
    archive_path = f"docs/prd/archive/{year}/Q{quarter}/"
    
    # Move PRD to archive
    if prd_path and prd_path.startswith("docs/prd/active/"):
        archived_path = move_file(prd_path, archive_path)
        
        # Update Strategy Board with archive location
        update_initiative(
            initiative_id,
            properties={"PRD Location": archived_path}
        )
```

**Search Behavior**:
- `search_repo()` searches **both active + archive** by default
- Can exclude archive with `search_repo(query, exclude_archive=True)`
- Archive PRDs have lower priority in suggestions (not frequently accessed)
- RAG indexes both active and archive (same corpus, different metadata)

**Success Criteria**:
- ✅ Zero orphaned folders in main docs/ tree
- ✅ Active/Archive structure operational
- ✅ Organization framework documented in docs/README.md
- ✅ All MCP tools work with new structure (no broken paths)
- ✅ Archival logic integrated with end_session
- ✅ Search works across active + archive

**Dependencies**: Phase 0 (test tool priority first)

**Risk**: Low - mostly moving files, clear archival triggers

---

### Phase 2: Session Handoff Fix (Workflow A)

**Goal**: Auto-populate Notion database description with HIGH-SIGNAL content only

**Time**: 3 hours

**What Gets Built**:

1. **High-Signal Session Template** (1 hour)
   - Define template: What Shipped / Key Decisions / Next Steps / Blocking Issues / Context Loaded
   - Remove meta-commentary ("written with Claude Chat/Code")
   - Focus on concrete deliverables and actionable information

2. **Initiative Detection Logic** (1 hour)
   - Check if initiative exists in Strategy Board before writing
   - If not found: Interactive prompts (Create / Search / Proceed without linking)
   - Handle ad-hoc sessions gracefully

3. **Update `end_session()` Logic** (0.5 hours)
   - After creating Sessions database entry
   - Call `write_to_page_content()` with high-signal template
   - No git commit messages in Notion (user gets that separately if needed)

4. **Test Workflow A** (0.5 hours)
   - Run strategy session in Claude Chat
   - Call `end_session()` with and without existing initiative
   - Validate Notion description populated correctly

**High-Signal Template**:

```markdown
# What Shipped
[Concrete deliverables - PRD, code, decision, analysis]
- Live Context Control v3 PRD (62 hours, 8 phases)
- RAG Strategy: Separate repos for privacy

# Key Decisions
[What you decided + rationale + trade-offs]
**RAG Architecture**: Option C (Separate Repos)
- **Rationale**: Privacy-first for team scaling
- **Trade-off**: 7-11 hours vs 2-4 hours, but worth it

**Risk Tolerance**: Option B (roll back if breaks)
- **Rationale**: Baby deadline makes "push through" risky

# Next Steps
- [ ] Dharan reviews PRD (15-20 min)
- [ ] Claude Code implements Phase 0 (2 hours)

# Blocking Issues
None

# Context Loaded
- docs/prd/live-context-control-v3.md
- ROADMAP.md
```

**Initiative Detection Flow**:

```python
# In start_session() and end_session()
async def check_initiative_exists(initiative_name, project_name):
    """Check if initiative exists, prompt if not."""
    initiative = await query_strategy_board(
        query=initiative_name,
        project=project_name
    )
    
    if not initiative:
        return {
            "initiative_found": False,
            "message": f"Initiative '{initiative_name}' not found in Strategy Board.",
            "options": [
                "1. Create new initiative in Strategy Board",
                "2. Search for similar initiatives (maybe typo?)",
                "3. Proceed without linking to Strategy Board (ad-hoc session)"
            ],
            "action_required": "Choose option 1, 2, or 3"
        }
    
    return {"initiative_found": True, "initiative": initiative}

# Option 1: Create New Initiative
async def create_initiative_interactive():
    """Interactive prompts to create initiative."""
    name = prompt("Initiative name?")
    project = prompt("Project? (Epic 2nd Brain / Legacy AI / Lifeadmin)")
    priority = prompt("Priority? (P0 / P1 / P2 / P3)")
    target = prompt("Target date? (YYYY-MM-DD or 'TBD')")
    
    new_initiative = await create_initiative_in_strategy_board(
        title=name,
        project=project,
        priority=priority,
        status="🟡 Needs Decision",
        target_date=target
    )
    
    return new_initiative

# Option 2: Search Similar
async def search_similar_initiatives(initiative_name, project_name):
    """Fuzzy search for similar initiatives."""
    similar = await search_strategy_board(
        query=initiative_name,
        project=project_name,
        top_k=3
    )
    
    return {
        "message": "Found similar initiatives:",
        "results": similar,
        "action_required": "Which one? Or create new?"
    }

# Option 3: Proceed Without Linking
async def proceed_adhoc():
    """Ad-hoc session, no Strategy Board link."""
    return {
        "message": "Starting ad-hoc session (not linked to Strategy Board)",
        "note": "Session log will be created but not linked to any initiative"
    }
```

**Code Changes**:

```python
# BEFORE (line 528)
result = await notion_api.update_initiative_status(
    page_id=initiative_page_id,
    new_status=None,
    # Properties only, no description
)

# AFTER
# Step 1: Check initiative exists (NEW)
if initiative_name:
    check_result = await check_initiative_exists(initiative_name, project_name)
    
    if not check_result['initiative_found']:
        # Interactive prompt, user chooses option
        return check_result

# Step 2: Update properties
result = await notion_api.update_initiative_status(
    page_id=initiative_page_id,
    new_status=None,
)

# Step 3: Write high-signal description (NEW)
session_summary = format_high_signal_template(
    what_shipped=decisions,  # Concrete deliverables
    key_decisions=decisions,  # Decisions + rationale
    next_steps=next_steps,
    blocking_issues=[],  # User can add if needed
    context_loaded=loaded_files
)

await notion_api.write_to_page_content(
    page_id=sessions_db_entry_id,
    content=session_summary
)
```

**Success Criteria**:
- ✅ Notion Sessions database description populated automatically
- ✅ HIGH-SIGNAL only (no meta-commentary about Claude Chat/Code)
- ✅ Template includes: What Shipped / Key Decisions / Next Steps / Blocking Issues / Context
- ✅ Initiative detection prompts if initiative not found
- ✅ Can create new initiative, search similar, or proceed ad-hoc
- ✅ Zero manual git commit message copying

**Dependencies**: Phase 0 (tool priority might affect end_session calls)

**Risk**: Low - `write_to_page_content()` already exists, template is just formatting

---

### Phase 3: End-Session Protocol Enhancement

**Goal**: Auto-update ROADMAP.md and Strategy Board at session end, with initiative detection

**Time**: 2 hours

**What Gets Built**:

1. **Add Roadmap Update Logic** (1 hour)
   - After Sessions database entry created
   - Parse initiative status from Strategy Board
   - Update corresponding row in ROADMAP.md
   - Mark as complete if status = "✅ Complete"
   - Archive PRD if complete (from Phase 1 logic)

2. **Initiative Detection** (0.5 hours)
   - Reuse logic from Phase 2
   - If initiative not found: Prompt to create/search/proceed

3. **Test Workflow** (0.5 hours)
   - Run session that completes an initiative
   - Validate ROADMAP.md updated automatically
   - Validate Strategy Board synced
   - Test with missing initiative

**Code Changes**:

```python
# In end_session(), after Notion updates:

# Step 1: Check initiative exists (reuse Phase 2 logic)
if initiative_page_id:
    check_result = await check_initiative_exists(initiative_name, project_name)
    
    if not check_result['initiative_found']:
        # Interactive prompt
        return check_result
    
    # Step 2: Get initiative status from Strategy Board
    initiative = await query_strategy_board(
        page_id=initiative_page_id
    )
    
    # Step 3: Update ROADMAP.md (NEW)
    roadmap_path = f"{project_root}/ROADMAP.md"
    roadmap_content = read_file(roadmap_path)
    
    # Find initiative row, update status
    updated_roadmap = update_roadmap_row(
        content=roadmap_content,
        initiative_name=initiative['title'],
        new_status=initiative['status'],
        completion_date=datetime.now() if status == "✅ Complete" else None
    )
    
    write_file(roadmap_path, updated_roadmap)
    
    # Step 4: Archive PRD if complete (NEW from Phase 1)
    if initiative['status'] == "✅ Complete" and prd_path:
        archive_prd(prd_path, initiative_page_id)
```

**Success Criteria**:
- ✅ ROADMAP.md updated automatically at session end
- ✅ Initiative status synced with Strategy Board
- ✅ Completion dates populated for completed initiatives
- ✅ PRDs archived automatically when initiative complete
- ✅ Initiative detection prompts if initiative not found
- ✅ Zero manual roadmap updates needed

**Dependencies**: Phase 1 (archival logic), Phase 2 (initiative detection logic)

**Risk**: Low - updates existing file, reuses Phase 2 logic

---

[All other phases remain the same as previous version...]

---

## 📅 Implementation Plan

### Week 1: Quick Wins (Dec 5-13)

**Day 1 (Dec 5)** - 7 hours
- ✅ Phase 0: Tool Selection Priority Fix (2 hours)
  - Update tool descriptions with 🎯 priority signals
  - Test with 5 queries that previously caused spirals
- ✅ Phase 1: Repo Organization Cleanup (5 hours)
  - Archive orphaned folders (2 hours)
  - Implement active/archive structure (1 hour)
  - Create docs/README.md organization guide (1 hour)
  - Validate tool compatibility + RAG indexing (1 hour)

**Day 2 (Dec 9)** - 7 hours
- ✅ Phase 2: Session Handoff Fix (3 hours)
  - Define high-signal template (1 hour)
  - Implement initiative detection (1 hour)
  - Update `end_session()`, test (1 hour)
- ✅ Phase 3: End-Session Protocol (2 hours)
  - Add roadmap update logic (1 hour)
  - Integrate initiative detection (0.5 hours)
  - Test auto-update flow (0.5 hours)
- ✅ Phase 4: Context Learning Loop - Part 1 (2 hours)
  - Implement usage tracking (log file loads, adds, removes, references)
  - Start collecting data

**Day 3 (Dec 11)** - 4 hours
- ✅ Phase 4: Context Learning Loop - Part 2 (4 hours)
  - Implement learning algorithm (scoring, ranking)
  - Update context-profiles.json with learned patterns
  - Test: Run 3 sessions, validate suggestions improve

**Day 4 (Dec 13)** - 4 hours
- ✅ Validation & Testing (4 hours)
  - Test all Phase 0-4 changes end-to-end
  - Test archival flow (complete an initiative, verify PRD archived)
  - Test initiative detection (missing initiative, create/search/proceed)
  - Measure time savings (before vs after)
  - Document any issues or edge cases

**Week 1 Total**: 22 hours
**Deliverables**: 4 phases shipped, archival operational, learning loop collecting data

---

### Week 2-3: Heavy Lifting (Dec 16-27)

[Same as previous version - 24 hours total]

---

### Week 4: Polish (Dec 30-Jan 3)

[Same as previous version - 16 hours total]

---

### Timeline Summary

| Week | Days | Hours | Phases | Key Deliverables |
|------|------|-------|--------|------------------|
| 1 (Dec 5-13) | 4 | 22 | 0-4 | Quick wins, archival operational, learning loop collecting data |
| 2-3 (Dec 16-27) | 4 | 24 | 5-6 | Semantic search, RAG separated for privacy |
| 4 (Dec 30-Jan 3) | 5 | 16 | 7-8 | Handoffs, context control, final validation |
| **Total** | **13** | **62** | **8** | **State-of-the-art MCP server** |

**Critical dates**:
- Dec 25 (Christmas): No work scheduled
- Jan 3: Final validation complete
- Jan 5: Baby due (all work finished)

---

## 📝 Change Log

| Date | Update | Author |
|------|--------|--------|
| 2025-12-05 | Created comprehensive PRD v3 (supersedes v2) | Claude (Sonnet 4.5) |
| 2025-12-05 | **v3.1 UPDATE**: Added archival strategy (active/archive/YYYY/QQ) | Claude (Sonnet 4.5) |
| 2025-12-05 | **v3.1 UPDATE**: Fixed session template (high-signal only) | Claude (Sonnet 4.5) |
| 2025-12-05 | **v3.1 UPDATE**: Added initiative detection (create/search/proceed) | Claude (Sonnet 4.5) |
| 2025-12-05 | **v3.1 UPDATE**: Updated timeline (60 hours → 62 hours) | Claude (Sonnet 4.5) |
| 2025-12-05 | **v3.2 UPDATE**: Added Phase 0.5 (Enhanced File Editing) - 64 hours total | Claude (Sonnet 4.5) |
| 2025-12-05 | **v3.2 UPDATE**: Added Phase 0.5 (Enhanced File Editing + Data Loss Prevention) - 65 hours total | Claude (Sonnet 4.5) |

---

**Related Documents**:
- [Applied Context Engineering One-Pager](../context/one-pagers/infrastructure/context-engineering.md)
- [MCP Server Current State Analysis](../architecture/mcp-server-current-state-analysis.md)
- [ROADMAP.md](../../ROADMAP.md)

---

**Status**: ✅ Ready for Claude Code Implementation

**Next Steps**: Hand this PRD to Claude Code to begin Phase 0 (Tool Selection Priority Fix) - 2 hours, quick win!