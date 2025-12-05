**Status**: Approved - Ready to Build
**Owner**: Dharan Chandrahasan
**Created**: 2025-12-05
**Target Completion**: January 3, 2026 (4 weeks, 60 hours)
**One-Pager**: [Applied Context Engineering](../context/one-pagers/infrastructure/context-engineering.md)
**Current State Analysis**: [MCP Server Analysis](../architecture/mcp-server-current-state-analysis.md)
**Supersedes**: Live Context Control v2 PRD

---

## 🎯 Executive Summary

### TL;DR

Build state-of-the-art MCP server that eliminates 100-140 min/week of context loading friction through 8 integrated phases delivered over 4 weeks. Investment: 60 hours for foundation that scales to 5-10 projects without multiplying friction. Core innovation: Separate RAG architecture (Legacy AI in business repo, Epic 2nd Brain in personal repo) enables team scaling while preserving privacy.

### Problem Statement

**7 validated pain points waste 100-140 min/week:**

1. **Tool Selection Spiral**: Claude tries bash/view before MCP tools (8 steps, 90-120 sec waste)
2. **Repo Organization Hell**: Cluttered repo (orphaned folders, 290 processed files) makes files hard to find
3. **Useless Context Suggestions**: 30% accuracy, files you never use, no learning loop
4. **No In-Repo Search**: Can't find \"related PRDs\", leads to 8-step spiral or manual navigation
5. **Session Handoff Broken**: Notion database description empty, manual git commit copying
6. **End-Session Protocol Incomplete**: Roadmap not updated automatically
7. **No Handoff Auto-Detection**: Claude Code doesn't know what to work on at \"start session\"

**Root cause**: Current MCP server (1,881 lines, 9 tools) built iteratively without unified architecture.

### Solution Overview

**Refactor 70%, Rewrite 30%** through 8 phases:

- **Phase 0**: Tool Selection Priority Fix (2 hours) - Add 🎯 priority signals
- **Phase 0.5**: Enhanced File Editing Tools (2 hours) - Section-based editing
- **Phase 1**: Repo Organization Cleanup (4 hours) - Archive orphaned folders
- **Phase 2**: Session Handoff Fix (2 hours) - Populate Notion description
- **Phase 3**: End-Session Protocol (2 hours) - Auto-update roadmap
- **Phase 4**: Context Learning Loop (4 hours) - Track usage, improve suggestions
- **Phase 5**: Epic 2nd Brain RAG (12 hours) - Semantic search for personal docs
- **Phase 6**: Legacy AI RAG Migration (12 hours) - Move to separate repo for team scaling
- **Phase 7**: Handoff Auto-Detection (12 hours) - File-based handoffs Claude Code picks up
- **Phase 8**: Context Visibility & Control (4 hours) - `list_context()`, `reload_context()` tools

**Total**: 54 hours implementation + 6 hours testing = 60 hours over 4 weeks

### Success Criteria

**Performance improvements:**
- Tool selection: 90-120 sec → <5 sec (95% reduction)
- Context suggestions: 30% → 80% accuracy (2.7x improvement)
- File discovery: 90-120 sec → <5 sec (95% reduction)
- Session handoff: Manual → Automatic (100% elimination)

**Time saved**: 100-140 min/week (1.7-2.3 hours/week)

**Privacy**: Separate RAG repos enable team scaling without data leakage

**ROI**: 60 hours invested → 88-120 hours saved over 1 year (1.5-2x return)

### Timeline

**Week 1 (Dec 5-13)**: Quick Wins - Phases 0-4 (20 hours)
**Week 2-3 (Dec 16-27)**: Heavy Lifting - Phases 5-6 (24 hours)
**Week 4 (Dec 30-Jan 3)**: Polish - Phases 7-8 (16 hours)

**Critical constraint**: Baby due January 5, 2026 - all work must complete by January 3.

---

## 🌟 Vision: Perfect Session Flow

### Your Description (North Star)

> \"I go into a session and say, 'Hey, start this workstream. We're doing infrastructure development,' and it asks me, 'Great, which initiative are you working on?' I provide the initiative, which is mapped to the strategy board in Notion. Then, it goes and in the first month or two, I provide the context manually, but each of the contexts is captured in the database, and you start learning the context that I provide over time. Based on that learning, you start providing recommendations after you have a little bit of data. If that context is not there, I say, 'I'm able to search within Claude. You're calling the MCP tools to say, \"Now provide these other documents. Search for these kinds of documents,\"' and it's able to search for documents in the repo and give me a list of numbered documents that I can just say, 'One, two, or three,' and it loads those contexts. Basically, I just want intelligent context loading.\"

### Before vs After

**BEFORE (Current State)**:

```
You: \"Start session infrastructure\"
MCP: Suggests 6 files (30% accuracy, some useless)
You: Manually add files by pasting exact paths (5 min)
You: Mid-session, need another file
     Claude tries bash, fails (90 sec)
     You paste exact path again (2 min)
You: End session
     Notion description empty
     You manually copy git commit message (3 min)
     Roadmap not updated
You: Start new session in Claude Code
     Claude Code: \"What should I work on?\"
     You: Re-explain everything (5 min)

Total friction: 15+ minutes per session
```

**AFTER (Target State)**:

```
You: \"Start session infrastructure\"
MCP: \"Which initiative?\" (linked to Strategy Board)
You: \"Applied Context Engineering\"
MCP: Suggests 6 files (80% accuracy, learned from usage)
     + \"Want to search for more?\"
You: \"Yes, find PRDs about context\"
MCP: Semantic search returns 3 results
     1. live-context-control.md (95% relevant)
     2. context-sync-bridge.md (87% relevant)
     3. mobile-context-access.md (45% relevant)
You: \"Load 1 and 2\"
MCP: ✅ Context loaded (3 sec)
You: Mid-session, need file
     \"Find architecture docs\"
MCP: Returns 2 results, you select 1 (5 sec)
You: \"Drop mobile-context-access, not relevant\"
MCP: ✅ Removed from context (2 sec)
You: End session
     Notion description auto-populated
     Roadmap auto-updated
     Handoff file created in /docs/handoffs/
You: Start session in Claude Code
     \"Start session\"
Claude Code: Auto-detects handoff, loads context
     \"I see you approved the Live Context Control v3 PRD.
      I'll implement Phase 0 (Tool Priority Fix). Ready?\"

Total friction: <30 seconds per session
```

---

## 📊 Current State Analysis

**Full analysis**: [MCP Server Current State Analysis](../architecture/mcp-server-current-state-analysis.md)

### Key Findings

**Architecture**:
- 1 FastMCP server (1,881 lines) in `/src/ai_assistant/server.py`
- 9 MCP tools (4 working, 2 partial, 3 broken/missing)
- 3 projects supported (Epic 2nd Brain, Legacy AI, Lifeadmin)
- 102 markdown files in docs/ folder

**Status by Tool**:
- ✅ **Working**: `read_file`, `write_file`, `query_strategy_board`, `update_initiative_status` (4 tools)
- ⚠️ **Partial**: `start_session`, `search_docs` (2 tools)
- ❌ **Broken/Missing**: `end_session` (Notion description empty), handoff auto-detection, semantic search (3 gaps)

**Root Causes Identified**:
1. **Notion Description Empty** → `end_session()` only sets properties, missing `children` blocks (line 528)
2. **Claude Uses Bash First** → Tool descriptions lack priority signals (no \"🎯 PRIMARY TOOL\")
3. **No Semantic Search** → `search_docs` uses keyword matching only (lines 709-732)
4. **Cluttered Repo** → Orphaned folders (Failed/, hold-for-later/), 290 processed files

**Recommendation**: **70% Refactor, 30% Rewrite** (54 hours total)

---

## 🔥 Problems & Root Causes

### Problem 0: Tool Selection Spiral

**Pain Point**:
> \"Unless I specifically state 'use MCP tool,' more than half the times it calls other tools and fails and looks at the mount directory instead of the repo\"

**Validated Example** (Nov 25, 2025):
- Query: \"Read the meta-analysis from the Insights folder in Legacy AI\"
- 8 steps: `read_file` (wrong path) → `bash ls` → `bash find` → `bash ls` → `bash find` → `search_docs` (wrong project) → `search_legacy_corpus` → `read_source_document` → SUCCESS
- **Time wasted**: 90-120 seconds

**Root Cause** (from analysis):
- Tool descriptions lack priority signals (\"🎯 PRIMARY TOOL\", \"Use me FIRST\")
- Claude defaults to bash/view before trying MCP tools
- No explicit \"DO NOT use bash\" guidance in tool descriptions

**Impact**:
- Time cost: 15-45 min/week (30-90 sec × 10-30 events/week)
- Cognitive cost: Flow state interrupted by spiral
- Workaround: Say \"use MCP tool\" explicitly (additional friction)

**Fix**: Phase 0 (Tool Selection Priority Fix)

---

### Problem 1: Repo Organization Hell

**Pain Point**:
> \"My repo gets cluttered, which makes it hard for it to manage. I need a good framework to clearly organize my repo as we start scaling. I don't know how people do this!\"

**Current State** (from analysis):
- Orphaned folders: `Failed/`, `hold-for-later/`, `insights/context-engineering/research/` (290 processed files)
- Inconsistent naming: Some files have dates, some don't
- No clear hierarchy: PRDs, one-pagers, architecture docs mixed

**Root Cause**:
- No documented organization framework
- Iterative building without cleanup
- No archival strategy for deprecated docs

**Impact**:
- Time cost: 10-20 min/week (searching through clutter)
- Cognitive cost: Uncertainty about where to put new docs
- Scaling blocker: With 5 projects, clutter multiplies 5x

**Fix**: Phase 1 (Repo Organization Cleanup)

---

### Problem 2: Useless Context Suggestions

**Pain Point**:
> \"A lot of the times, the files you suggest in the beginning are completely useless too and the MCP tool doesn't learn at all.\"

**Current Behavior**:
- `start_session()` suggests 3-6 files based on hard-coded heuristics
- No learning loop: System doesn't track which files you actually use
- Accuracy: ~30% (you keep 2/6 files, ignore 4/6)

**Root Cause** (from analysis):
- `use_intelligent_loading=False` by default (line 142)
- Context profiles use heuristics, not learned patterns
- No usage tracking (no data to learn from)

**Impact**:
- Time cost: 20-30 min/week (loading wrong context, restarting)
- Cognitive cost: \"Do I trust the suggestions?\" uncertainty
- Workaround: Manually provide context every time

**Fix**: Phase 4 (Context Learning Loop)

---

### Problem 3: No In-Repo Search

**Pain Point**:
> \"I am NOT able to easily search in the repo. It says 'no other PRDs associated with this.' I want to quickly search and say 'hey, look through my repo and say are there anything else that's related to this?'\"

**Current State**:
- `search_docs()` uses keyword matching only (lines 709-732)
- No semantic search: Can't find \"related PRDs\" by meaning
- Cross-project search broken: Legacy AI vs Epic 2nd Brain confused

**Root Cause** (from analysis):
- No RAG implementation for Epic 2nd Brain (50k tokens)
- Legacy AI RAG exists but in wrong repo (privacy risk for team scaling)
- Simple keyword search insufficient for \"find related docs\"

**Impact**:
- Time cost: 35-65 min/week (90-120 sec per file discovery × 20-30 events/week)
- Cognitive cost: \"What else is relevant?\" uncertainty
- Workaround: Navigate to folder, paste exact path (additional 2-5 min)

**Fix**: Phase 5 (Epic 2nd Brain RAG) + Phase 6 (Legacy AI RAG Migration)

---

### Problem 4: Session Handoff Broken (Workflow A)

**Pain Point**:
> \"At the end of this session, the handoff created in Notion doesn't have any information on the description. It doesn't state what shipped.\"

**Current Behavior**:
- `end_session()` creates entry in Sessions database
- Properties populated (Title, Date, Duration)
- Description field empty (see screenshot provided)

**Root Cause** (from analysis):
- `end_session()` calls Notion API to set properties only (line 528)
- Does NOT call `write_to_page_content()` to write description
- Missing: Session summary, decisions made, what shipped

**Impact**:
- Time cost: 3-5 min/session (manual git commit message copying)
- Data loss: Decisions not captured in Notion
- Workaround: Ask for git commit message, paste manually

**Workflow affected**: Strategy/Decision sessions (Claude Chat → Notion)

**Fix**: Phase 2 (Session Handoff Fix)

---

### Problem 5: End-Session Protocol Incomplete

**Pain Point**:
> \"Claude Code at the end-session protocol sometimes does not update the roadmap and other associated files unless I specifically ask it to.\"

**Current Behavior**:
- `end_session()` creates Sessions database entry
- Does NOT update ROADMAP.md automatically
- Does NOT update Strategy Board automatically

**Root Cause**:
- `end_session()` missing logic to update roadmap (not implemented)
- Unclear if this is MCP tool problem or prompt/rules problem
- No explicit \"update roadmap\" step in end_session flow

**Impact**:
- Time cost: 2-3 min/session (manual roadmap updates)
- Data drift: ROADMAP.md out of sync with Sessions database
- Workaround: Manually ask Claude Code to update

**Fix**: Phase 3 (End-Session Protocol)

---

### Problem 6: No Handoff Auto-Detection (Workflow B)

**Pain Point**:
> \"I approve a PRD in Claude Chat, take it to Claude Code, and Claude Code doesn't know what to work on when I say 'start session'\"

**Current Behavior**:
- No handoff mechanism between Claude Chat and Claude Code
- You manually re-explain what needs to be built
- Claude Code has no context from approval session

**Root Cause**:
- No file-based handoff system
- Claude Code `start_session()` doesn't check for pending handoffs
- No standardized handoff format

**Impact**:
- Time cost: 5-10 min/session (re-explaining context)
- Data loss: Nuance from approval session lost
- Cognitive cost: \"Did I remember to mention everything?\"

**Workflow affected**: Implementation sessions (Claude Chat → Claude Code)

**Fix**: Phase 7 (Handoff Auto-Detection)

---

### Problem 7: No Mid-Session Context Control

**Pain Point**:
> \"I usually pivot to a new chat to start and I forget halfway in which files are in context.\"

**Current Behavior**:
- No way to see which files are loaded
- No way to add/remove files mid-session without restarting
- Leads to restart spirals (lose 20 min of work)

**Root Cause**:
- No `list_context()` tool (visibility)
- No `reload_context()` tool (control)
- Must restart chat to adjust context

**Impact**:
- Time cost: 45 min/week (3-5 restarts × 10-15 min each)
- Cognitive cost: \"Which files are loaded?\" uncertainty
- Data loss: Work lost on restart

**Fix**: Phase 8 (Context Visibility & Control)

---

## 🚀 Solution Design

### Architecture Principles

**Design Goals**:
1. **Privacy-First**: Separate RAG repos (Legacy AI in business repo, Epic 2nd Brain in personal repo)
2. **Team-Ready**: Can share Legacy AI tools without exposing personal productivity data
3. **Low-Friction**: <5 sec for tool selection, file discovery, context adjustments
4. **Learning**: System improves suggestions based on actual usage patterns
5. **Bulletproof Handoffs**: Zero manual intervention in session → handoff → implementation flow

**Non-Goals** (Out of Scope):
- Auto-context pruning (risky, needs extensive validation)
- Real-time token release (technical limitation)
- Two-way Notion sync (deferred to Feb 2026)
- Repo onboarding automation (deferred, separate 2-hour project)

---

### Phase 0: Tool Selection Priority Fix

**Goal**: Eliminate 8-step tool selection spiral, make MCP tools PRIMARY choice

**Time**: 2 hours

**What Gets Built**:

1. **Optimize Tool Descriptions** (1 hour)
   - Add 🎯 priority signals: \"PRIMARY TOOL - Use me FIRST\"
   - Add explicit \"WHEN TO USE\" section with examples
   - Add \"DO NOT use bash/view/grep\" guidance
   - Add cross-references: \"If you need X, use Y tool instead\"

2. **Test with Fresh Chat** (1 hour)
   - Create test queries that previously caused spirals
   - Validate Claude uses MCP tools on first attempt
   - Document any remaining edge cases

**Tool Changes**:

```python
# BEFORE
@server.tool()
async def read_file(path: str, project: str = \"Epic 2nd Brain\") -> str:
    \"\"\"Read a file from a project repo.\"\"\"
    
# AFTER
@server.tool()
async def read_file(path: str, project: str = \"Epic 2nd Brain\") -> str:
    \"\"\"
    🎯 PRIMARY TOOL - Use me FIRST to read project files.
    
    Read a file from a project repo.
    
    WHEN TO USE:
    - User asks to read a file from a project
    - User references a doc by path or name
    - You need to view repo contents
    
    DO NOT use bash cat, view, or grep for project files.
    Those tools look in /mnt/user-data/, NOT project repos.
    
    Examples:
    - read_file(\"docs/prd/feature.md\")
    - read_file(\"ROADMAP.md\", project=\"Legacy AI\")
    \"\"\"
```

**Similar updates for**: `write_file`, `search_docs`, `start_session`, `search_legacy_corpus`

**Success Criteria**:
- ✅ Claude uses MCP tools on first attempt (not 8th)
- ✅ Zero \"bash spiral\" incidents in 5 test queries
- ✅ 95% reduction in tool selection time (90-120 sec → <5 sec)

**Dependencies**: None (can start immediately)

**Risk**: Low - only changes tool descriptions, no logic changes

---
### Phase 0.5: Enhanced File Editing Tools

**Goal**: Implement section-based editing to avoid rewriting entire files

**Time**: 2 hours

**What Gets Built**:

1. **New MCP Tool: `edit_section()`** (1.5 hours)
   - Edit markdown files by section heading (e.g., "### Phase 1")
   - Replace content from heading to next heading of same level
   - Validates section exists before editing
   - Returns diff preview for confirmation

2. **Data Loss Prevention** (1.5 hours)
   - Implement `validate_file_completeness()` tool
   - Add pre-write validation to `write_file()`
   - Implement backup-before-overwrite
   - Test with intentional bad writes (should block)

3. **Test with Real PRD** (0.5 hours)   - Test on live-context-control-v3.md (this file)
   - Edit 2-3 sections to validate
   - Measure token savings vs full file rewrite

**Tool Spec**:
```python
@server.tool()
async def edit_section(
    path: str,
    section_marker: str,
    new_content: str,
    project: str = "Epic 2nd Brain",
    description: str = ""
) -> dict:
    """
    🎯 PRIMARY TOOL - Use me to edit sections of markdown files.
    
    Edit a specific section of a markdown file without rewriting the entire file.
    
    Args:
        path: Relative path to file (e.g., "docs/prd/feature.md")
        section_marker: Markdown heading to find (e.g., "### Phase 1: Repo Cleanup")
        new_content: New content for that section (from heading to next same-level heading)
        project: Project name
        description: Why you're making this edit
    
    Returns:
        {
            "status": "success",
            "section_found": True,
            "old_length": 1250,  # characters
            "new_length": 1580,
            "diff_preview": "Added 330 characters",
            "tokens_saved": 50000  # vs rewriting entire file
        }
    
    How it works:
    1. Parse markdown file to find section_marker heading
    2. Find content from that heading to next heading of same level (or EOF)
    3. Replace that content with new_content
    4. Write file with surgical edit only
    
    Examples:
    - edit_section("docs/prd/feature.md", "### Phase 1", "Updated Phase 1 content...")
    - edit_section("ROADMAP.md", "## Active Work", "Updated active work table...")
    
    DO NOT use this tool for:
    - Non-markdown files (use str_replace instead)
    - Files without clear section headings (use write_file instead)
    - When you want to edit multiple sections (call tool multiple times)
    """
```

**Implementation Notes**:

- Uses markdown parser (e.g., `markdown-it-py` or custom regex)
- Heading levels: `##` = level 2, `###` = level 3, etc.
- Finds section by exact heading match (case-sensitive)
- Replaces from heading start to next same-level heading (or EOF)
- Preserves formatting, whitespace, other sections unchanged

**CRITICAL: Data Loss Prevention**:

1. **Pre-Write Validation** (prevents shortcuts)
   - Before ANY file write, validate content completeness
   - Check: Does new content have fewer sections than old content?
   - Check: Does new content contain placeholders like "refer to previous version", "[Content continues...]", "...", etc.?
   - If YES to either: BLOCK write with error message
   
2. **Backup Before Overwrite**
   - Before overwriting any file, create `.backup` copy with timestamp
   - Example: `live-context-control-v3.md.backup.2025-12-05-15-30-00`
   - Keep last 3 backups, auto-delete older ones
   - User can restore from backup if needed

3. **Diff Preview Before Commit**
   - Show user what's changing (sections added/removed/modified)
   - Require explicit confirmation for destructive changes (section removal)
   - Example: "Warning: This will REMOVE sections X, Y, Z. Confirm? (yes/no)"

4. **New Tool: `validate_file_completeness()`**
```python
   @server.tool()
   async def validate_file_completeness(
       old_path: str,
       new_content: str,
       project: str = "Epic 2nd Brain"
   ) -> dict:
       """
       Validate that new content is complete (no data loss).
       
       Checks:
       1. New content has >= same number of sections as old
       2. No placeholder text like "refer to previous version"
       3. No truncation markers like "..." or "[Content continues...]"
       
       Returns:
           {
               "is_complete": True/False,
               "issues_found": ["Missing section X", "Contains placeholder Y"],
               "safe_to_write": True/False
           }
       """
```

**Validation Logic**:
```python
FORBIDDEN_PLACEHOLDERS = [
    "refer to previous version",
    "refer to the previous version", 
    "[Content continues",
    "Content continues with all sections from previous version",
    "All sections from previous version",
    "...",  # Ellipsis suggesting truncation
    "[Full content in previous version]",
    "See above for",
    "Same as previous",
]

async def validate_file_completeness(old_path, new_content, project):
    """Prevent data loss from incomplete writes."""
    
    # Read old file
    old_content = await read_file(old_path, project)
    
    # Count sections (markdown headings)
    old_sections = count_markdown_headings(old_content)
    new_sections = count_markdown_headings(new_content)
    
    issues = []
    
    # Check 1: Section count
    if new_sections < old_sections:
        issues.append(
            f"Section count decreased: {old_sections} → {new_sections}. "
            f"Potential data loss!"
        )
    
    # Check 2: Forbidden placeholders
    for placeholder in FORBIDDEN_PLACEHOLDERS:
        if placeholder.lower() in new_content.lower():
            issues.append(
                f"Contains placeholder text: '{placeholder}'. "
                f"This suggests incomplete content!"
            )
    
    # Check 3: Length sanity check
    # If new content is <50% of old content, likely truncated
    if len(new_content) < (len(old_content) * 0.5):
        issues.append(
            f"New content is {len(new_content)} chars vs old {len(old_content)} chars. "
            f"Possible truncation!"
        )
    
    return {
        "is_complete": len(issues) == 0,
        "issues_found": issues,
        "safe_to_write": len(issues) == 0
    }
```

**Integration with write_file**:
```python
# BEFORE (current behavior - UNSAFE)
async def write_file(path, content, project):
    # Just write, no validation
    with open(full_path, 'w') as f:
        f.write(content)

# AFTER (with safety rails - SAFE)
async def write_file(path, content, project):
    # Step 1: Validate completeness
    if os.path.exists(full_path):
        validation = await validate_file_completeness(path, content, project)
        
        if not validation['safe_to_write']:
            return {
                "status": "blocked",
                "reason": "Data loss prevention",
                "issues": validation['issues_found'],
                "action_required": "Fix issues before writing, or use force=True"
            }
    
    # Step 2: Backup before overwrite
    if os.path.exists(full_path):
        backup_path = f"{full_path}.backup.{timestamp()}"
        shutil.copy(full_path, backup_path)
        cleanup_old_backups(full_path)  # Keep last 3 only
    
    # Step 3: Write file
    with open(full_path, 'w') as f:
        f.write(content)
    
    return {
        "status": "success",
        "backup_created": backup_path if existed else None
    }
```

**Success Criteria**:
- ✅ Can edit 1 section of live-context-control-v3.md without rewriting entire file
- ✅ Token savings: 50,000+ tokens vs full rewrite (60% reduction)
- ✅ Edit time: <10 sec vs 2-3 min for full rewrite (95% faster)
- ✅ Validation: Shows diff preview before editing
- ✅ Error handling: Clear error if section not found

**Benefits**:
- **Token efficiency**: Edit 1 section = ~2,000 tokens vs 133,000 tokens for full rewrite (98.5% savings)
- **Speed**: 10 sec vs 2-3 min (95% faster)
- **Precision**: Only changes what you intend to change
- **Pays for itself**: Saves time on all future PRD/doc edits throughout 64-hour project

**Dependencies**: None (can implement immediately)

**Risk**: Low - simple tool, clear use case, validates section exists before editing

---
### Phase 1: Repo Organization Cleanup

**Goal**: Clean cluttered repo, establish organization framework

**Time**: 4 hours

**What Gets Built**:

1. **Archive Orphaned Folders** (2 hours)
   - Move `Failed/` to `archive/failed-experiments/`
   - Move `hold-for-later/` to `archive/hold-for-later/`
   - Move `insights/context-engineering/research/` (290 files) to `archive/context-engineering-research/`
   - Update any references to moved files

2. **Document Organization Framework** (1 hour)
   - Create `docs/README.md` with folder structure guide
   - Define naming conventions (dates, titles, status)
   - Define archival strategy (when to archive vs delete)

3. **Validate Tool Compatibility** (1 hour)
   - Test `search_docs()` with new structure
   - Test `start_session()` context loading
   - Update paths in context-profiles.json if needed

**Folder Structure** (After):

```
docs/
├── README.md (NEW - organization guide)
├── prd/                    # Product Requirements Documents
├── tech-req/               # Technical Requirements
├── sessions/               # Session logs
│   ├── claude-chat/        # Strategy sessions
│   └── claude-code/        # Implementation sessions
├── context/                # Context documents
│   ├── one-pagers/         # Initiative one-pagers
│   └── README.md           # How to use context docs
├── architecture/           # System architecture diagrams
├── handoffs/               # NEW - File-based handoffs (Phase 7)
└── archive/                # Deprecated/experimental work
    ├── failed-experiments/
    ├── hold-for-later/
    └── context-engineering-research/
```

**Success Criteria**:
- ✅ Zero orphaned folders in main docs/ tree
- ✅ Organization framework documented in docs/README.md
- ✅ All MCP tools work with new structure (no broken paths)

**Dependencies**: Phase 0 (test tool priority first)

**Risk**: Low - mostly moving files, no logic changes

---

### Phase 2: Session Handoff Fix (Workflow A)

**Goal**: Auto-populate Notion database description at end of strategy sessions

**Time**: 2 hours

**What Gets Built**:

1. **Update `end_session()` Logic** (1.5 hours)
   - After creating Sessions database entry (line 528)
   - Call `write_to_page_content()` with session summary
   - Summary includes: decisions made, next steps, context used

2. **Test Workflow A** (0.5 hours)
   - Run strategy session in Claude Chat
   - Call `end_session()`
   - Validate Notion description populated

**Code Changes**:

```python
# BEFORE (line 528)
result = await notion_api.update_initiative_status(
    page_id=initiative_page_id,
    new_status=None,  # Don't change status
    # Properties only, no description
)

# AFTER
# Step 1: Update properties
result = await notion_api.update_initiative_status(
    page_id=initiative_page_id,
    new_status=None,
)

# Step 2: Write description (NEW)
session_summary = f\"\"\"
# Session Summary

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Duration**: {session_duration_hours} hours
**Project**: {project_name}

## Decisions Made
{format_decisions(decisions)}

## Next Steps
{format_next_steps(next_steps)}

## Context Used
{format_context(loaded_files)}
\"\"\"

await notion_api.write_to_page_content(
    page_id=sessions_db_entry_id,  # NEW entry, not initiative
    content=session_summary
)
```

**Success Criteria**:
- ✅ Notion Sessions database description populated automatically
- ✅ Zero manual git commit message copying
- ✅ Session summary includes decisions, next steps, context

**Dependencies**: Phase 0 (tool priority might affect end_session calls)

**Risk**: Low - `write_to_page_content()` already exists and works

---

### Phase 3: End-Session Protocol Enhancement

**Goal**: Auto-update ROADMAP.md and Strategy Board at session end

**Time**: 2 hours

**What Gets Built**:

1. **Add Roadmap Update Logic** (1.5 hours)
   - After Sessions database entry created
   - Parse initiative status from Strategy Board
   - Update corresponding row in ROADMAP.md
   - Mark as complete if status = \"✅ Complete\"

2. **Test Workflow** (0.5 hours)
   - Run session that completes an initiative
   - Validate ROADMAP.md updated automatically
   - Validate Strategy Board synced

**Code Changes**:

```python
# In end_session(), after Notion updates:

# Step 3: Update ROADMAP.md (NEW)
if initiative_page_id:
    # Get initiative status from Strategy Board
    initiative = await query_strategy_board(
        page_id=initiative_page_id
    )
    
    # Update ROADMAP.md
    roadmap_path = f\"{project_root}/ROADMAP.md\"
    roadmap_content = read_file(roadmap_path)
    
    # Find initiative row, update status
    updated_roadmap = update_roadmap_row(
        content=roadmap_content,
        initiative_name=initiative['title'],
        new_status=initiative['status'],
        completion_date=datetime.now() if status == \"✅ Complete\" else None
    )
    
    write_file(roadmap_path, updated_roadmap)
```

**Success Criteria**:
- ✅ ROADMAP.md updated automatically at session end
- ✅ Initiative status synced with Strategy Board
- ✅ Completion dates populated for completed initiatives

**Dependencies**: Phase 2 (builds on end_session changes)

**Risk**: Low - updates existing file, no API calls

---

### Phase 4: Context Learning Loop

**Goal**: Track usage patterns, improve suggestion accuracy from 30% → 80%

**Time**: 4 hours

**What Gets Built**:

1. **Usage Tracking** (2 hours)
   - Track files loaded in `start_session()`
   - Track files explicitly added via `reload_context()`
   - Track files referenced in Claude responses
   - Track files explicitly removed
   - Store in `usage-log.jsonl` (append-only, privacy-preserving)

2. **Learning Algorithm** (1.5 hours)
   - Score files: referenced (+3), added (+2), loaded and kept (+1), removed (-5), loaded but not referenced (-1)
   - Weight recent sessions higher (last 5 sessions = 2x weight)
   - Rank files by score, top 3-6 become new suggestions
   - Update context-profiles.json with learned patterns

3. **Test Learning** (0.5 hours)
   - Run 3 sessions with same work stream
   - Validate suggestions improve (track accuracy)

**Data Model**:

```json
// usage-log.jsonl (append-only)
{\"timestamp\": \"2025-12-05T10:30:00Z\", \"project\": \"Epic 2nd Brain\", \"work_stream\": \"infrastructure\", \"event\": \"file_loaded\", \"file\": \"docs/prd/live-context-control-v3.md\", \"source\": \"suggestion\"}
{\"timestamp\": \"2025-12-05T10:35:00Z\", \"project\": \"Epic 2nd Brain\", \"work_stream\": \"infrastructure\", \"event\": \"file_referenced\", \"file\": \"docs/prd/live-context-control-v3.md\", \"reference_count\": 5}
{\"timestamp\": \"2025-12-05T10:40:00Z\", \"project\": \"Epic 2nd Brain\", \"work_stream\": \"infrastructure\", \"event\": \"file_removed\", \"file\": \"docs/context/testing-roadmap.md\", \"reason\": \"not_relevant\"}

// context-profiles.json (updated by learning)
{
  \"Epic 2nd Brain\": {
    \"infrastructure\": {
      \"suggested_files\": [
        {
          \"path\": \"docs/prd/live-context-control-v3.md\",
          \"score\": 45,
          \"reason\": \"Referenced in 8/10 recent sessions\"
        },
        {
          \"path\": \"ROADMAP.md\",
          \"score\": 40,
          \"reason\": \"Loaded and kept in 10/10 sessions\"
        }
      ],
      \"last_updated\": \"2025-12-05T10:45:00Z\",
      \"sessions_analyzed\": 10
    }
  }
}
```

**Code Changes**:

```python
# In start_session(), track what gets loaded:
async def start_session(...):
    # ... existing logic ...
    
    # NEW: Track file loads
    for file in suggested_files:
        log_usage_event(
            project=project_name,
            work_stream=work_stream,
            event=\"file_loaded\",
            file=file['path'],
            source=\"suggestion\"
        )
    
    return {...}

# NEW: Background job (runs nightly)
async def update_context_profiles():
    \"\"\"Analyze usage log, update profiles.\"\"\"
    log = load_usage_log()
    
    for (project, work_stream) in unique_combinations(log):
        scores = calculate_scores(log, project, work_stream)
        top_files = sorted(scores, key=lambda x: x['score'], reverse=True)[:6]
        
        update_profile(project, work_stream, top_files)
```

**Success Criteria**:
- ✅ Usage tracking operational (all events logged)
- ✅ Learning algorithm updates profiles based on real data
- ✅ Suggestion accuracy: 30% → 60% after 1 week, 80% after 2 weeks
- ✅ Can explain why files suggested (\"Used in 8/10 sessions\")

**Dependencies**: Phase 0-1 (clean repo makes tracking easier)

**Risk**: Medium - algorithm might learn wrong patterns initially (can reset profiles)

---

### Phase 5: Epic 2nd Brain RAG - Semantic Search

**Goal**: Build semantic search for Epic 2nd Brain (50k tokens, 102 files)

**Time**: 12 hours

**What Gets Built**:

1. **RAG Infrastructure** (4 hours)
   - Copy RAG code from Legacy AI implementation
   - Set up ChromaDB for Epic 2nd Brain corpus
   - Configure BGE embeddings (local, privacy-first)
   - Set up hybrid search (BM25 + semantic)

2. **Indexing Pipeline** (4 hours)
   - Header-based chunking (preserve document structure)
   - Index all markdown files in `docs/`
   - Metadata: file path, type (prd, one-pager, session), last modified
   - Auto-reindex nightly (cron job)

3. **MCP Tools** (3 hours)
   - `search_repo(query, file_types, project)` - Semantic search
   - `list_files(pattern, project)` - Browse by pattern
   - Integrate with `reload_context()` for easy loading

4. **Testing** (1 hour)
   - Test queries: \"Find PRDs about context\", \"Show architecture docs\"
   - Validate relevance (manual review of top 5 results)
   - Validate speed (<2 sec per search)

**Architecture**:

```
ai-assistant/ (Epic 2nd Brain repo)
├── src/ai_assistant/
│   ├── server.py (main MCP server)
│   └── rag/
│       ├── epic_2b_rag/           # NEW
│       │   ├── indexer.py         # Index docs/ folder
│       │   ├── search.py          # Hybrid search
│       │   └── config.py          # Corpus path, chunk size
│       └── shared/                # Shared utilities
│           ├── embeddings.py      # BGE local
│           └── chunking.py        # Header-based chunking
└── .chroma/
    └── epic-2b/                    # NEW - Vector DB for Epic 2nd Brain
        ├── chroma.sqlite3
        └── embeddings/
```

**Tool Spec**:

```python
@server.tool()
async def search_repo(
    query: str,
    file_types: list[str] = None,  # [\"prd\", \"one-pager\", \"session\"]
    project: str = \"Epic 2nd Brain\",
    top_k: int = 5
) -> dict:
    \"\"\"
    🎯 PRIMARY TOOL - Use me to find related documents.
    
    Semantic search across project documentation.
    
    Args:
        query: Natural language query (e.g., \"Find PRDs about context management\")
        file_types: Filter by type (optional)
        project: Project name
        top_k: Number of results (default 5)
    
    Returns:
        {
            \"results\": [
                {
                    \"path\": \"docs/prd/live-context-control-v3.md\",
                    \"type\": \"prd\",
                    \"relevance\": 0.95,
                    \"snippet\": \"...context loading friction...\",
                    \"last_modified\": \"2025-12-05\"
                }
            ],
            \"query\": \"Find PRDs about context management\",
            \"total_results\": 3
        }
    
    Example usage:
    - search_repo(\"Find architecture diagrams\")
    - search_repo(\"PRDs about sessions\", file_types=[\"prd\"])
    \"\"\"
```

**Success Criteria**:
- ✅ Can find \"related PRDs\" in <2 seconds
- ✅ Search quality > keyword matching (manual validation)
- ✅ 95% reduction in file discovery time (90-120 sec → <5 sec)
- ✅ Supports numbered selection: \"Load results 1, 2, and 4\"

**Dependencies**: Phase 0-1 (clean repo, clear organization)

**Risk**: Low - reusing proven architecture from Legacy AI RAG

---

### Phase 6: Legacy AI RAG Migration

**Goal**: Move Legacy AI RAG to separate repo for team scaling, preserve privacy

**Time**: 12 hours

**What Gets Built**:

1. **Create Legacy AI MCP Server** (4 hours)
   - New file: `legacy-ai/src/legacy_ai/mcp_server.py`
   - Copy core MCP logic from `ai-assistant/src/ai_assistant/server.py`
   - Keep only Legacy AI specific tools (customer discovery, RAG)

2. **Move RAG Code** (4 hours)
   - Copy `ai-assistant/src/ai_assistant/rag/` to `legacy-ai/src/legacy_ai/rag/`
   - Update imports, paths
   - Move `.chroma/` vector DB to `legacy-ai/.chroma/`
   - Test: Validate search quality unchanged

3. **Update Epic 2nd Brain MCP** (2 hours)
   - Remove Legacy AI RAG references
   - Update `search_legacy_corpus()` to call Legacy AI MCP server (if running)
   - Add fallback: If Legacy AI MCP not running, show helpful error

4. **Testing** (2 hours)
   - Test customer discovery workflows (Story 6 from RAG implementation)
   - Validate no Epic 2nd Brain data in Legacy AI RAG
   - Validate no Legacy AI data in Epic 2nd Brain RAG

**Architecture** (After):

```
# BEFORE (privacy risk)
ai-assistant/
└── .chroma/
    ├── legacy-ai/        # ⚠️ Risk: Peter could access this
    └── epic-2b/          # ⚠️ Risk: Peter could access this

# AFTER (privacy-safe)
legacy-ai/ (business repo)
├── src/legacy_ai/
│   ├── mcp_server.py     # Separate MCP server
│   └── rag/              # Only Legacy AI RAG
└── .chroma/              # Only Legacy AI data

ai-assistant/ (personal repo)
├── src/ai_assistant/
│   ├── server.py         # Separate MCP server
│   └── rag/
│       └── epic_2b_rag/  # Only Epic 2nd Brain RAG
└── .chroma/              # Only Epic 2nd Brain data
```

**Success Criteria**:
- ✅ Two separate MCP servers running independently
- ✅ Complete privacy isolation (Peter can install Legacy AI MCP without seeing Epic 2nd Brain data)
- ✅ Legacy AI RAG quality unchanged (8 test cases still passing)
- ✅ Customer discovery workflow (Story 6) still works

**Dependencies**: Phase 5 (Epic 2nd Brain RAG working)

**Risk**: Medium - migration could break existing workflows
- **Mitigation**: Option B (roll back if breaks), extensive testing before cutover

---

### Phase 7: Handoff Auto-Detection (Workflow B)

**Goal**: File-based handoffs that Claude Code auto-detects on \"start session\"

**Time**: 12 hours

**What Gets Built**:

1. **Handoff Data Model** (2 hours)
   - Define handoff schema (JSON + markdown)
   - Location: `/docs/handoffs/{date}-{initiative}.md`
   - Contains: Initiative link, PRD path, approval notes, context to load

2. **Create Handoff Tool** (4 hours)
   - NEW: `create_handoff()` called at end of approval session
   - Generates handoff file with all necessary context
   - Links to Strategy Board initiative, PRD, one-pager

3. **Auto-Detection Logic** (4 hours)
   - Update `start_session()` in Claude Code
   - Check `/docs/handoffs/` for pending handoffs (status: \"pending\")
   - If found: Auto-load context, summarize task
   - Mark handoff as \"in_progress\"

4. **Testing** (2 hours)
   - Test Workflow B: Approve PRD in Chat → Start session in Code
   - Validate Claude Code knows what to work on
   - Validate no manual re-explaining needed

**Handoff Schema**:

```yaml
# docs/handoffs/2025-12-05-live-context-control-v3.md

---
status: pending            # pending | in_progress | complete
created: 2025-12-05T11:30:00Z
initiative_id: page_12345
initiative_name: Applied Context Engineering
project: Epic 2nd Brain
work_stream: infrastructure
approved_by: Dharan Chandrahasan
---

# Handoff: Live Context Control v3

## What Was Approved
Comprehensive MCP refactor to eliminate 100-140 min/week of context loading friction.

## Context to Load
- docs/prd/live-context-control-v3.md (PRIMARY - this PRD)
- docs/context/one-pagers/infrastructure/context-engineering.md
- docs/architecture/mcp-server-current-state-analysis.md
- ROADMAP.md

## Task
Implement 8 phases over 4 weeks (60 hours):
- Phase 0: Tool Selection Priority Fix (2 hours)
- Phase 1: Repo Organization Cleanup (4 hours)
- ... (full breakdown in PRD)

## Success Criteria
- Tool selection: 90-120 sec → <5 sec (95% reduction)
- Context suggestions: 30% → 80% accuracy
- File discovery: 90-120 sec → <5 sec
- Session handoff: Manual → Automatic

## Next Steps
Start with Phase 0 (Tool Selection Priority Fix) - 2 hours, quick win.

## Approval Notes
- Baby due January 5, 2026 - all work must complete by January 3
- Risk tolerance: Option B (roll back if breaks)
- RAG strategy: Separate repos for privacy (Option C)
```

**Code Changes**:

```python
# NEW tool in Claude Chat MCP
@server.tool()
async def create_handoff(
    initiative_id: str,
    initiative_name: str,
    project: str,
    work_stream: str,
    prd_path: str,
    task_summary: str,
    context_files: list[str],
    success_criteria: list[str],
    approval_notes: str = \"\"
) -> dict:
    \"\"\"
    Create a handoff file for Claude Code to pick up.
    
    Called at end of approval session (Workflow B).
    \"\"\"
    handoff_path = f\"docs/handoffs/{date.today()}-{slugify(initiative_name)}.md\"
    
    handoff_content = generate_handoff_markdown(...)
    
    write_file(handoff_path, handoff_content, project=project)
    
    return {
        \"handoff_created\": handoff_path,
        \"status\": \"pending\",
        \"message\": \"Handoff ready for Claude Code\"
    }

# Updated tool in Claude Code MCP
@server.tool()
async def start_session(
    project_name: str = \"Epic 2nd Brain\",
    work_stream: str = None
) -> dict:
    \"\"\"Start a session with intelligent context loading.\"\"\"
    
    # NEW: Check for pending handoffs
    handoffs = list_handoffs(project_name, status=\"pending\")
    
    if handoffs:
        # Auto-load handoff
        handoff = handoffs[0]  # Most recent
        context_files = handoff['context_files']
        
        # Load all context files
        load_context(context_files)
        
        # Mark as in_progress
        update_handoff_status(handoff['path'], \"in_progress\")
        
        return {
            \"message\": f\"Auto-detected handoff: {handoff['initiative_name']}\",
            \"task\": handoff['task_summary'],
            \"context_loaded\": context_files,
            \"next_steps\": handoff['next_steps']
        }
    
    # ... existing start_session logic if no handoff ...
```

**Success Criteria**:
- ✅ Handoff files created automatically at approval
- ✅ Claude Code auto-detects handoffs on \"start session\"
- ✅ Zero manual re-explaining (5-10 min saved per session)
- ✅ Handoff contains all necessary context (PRD, one-pager, initiative link)

**Dependencies**: Phase 0-4 (all quick wins shipped)

**Risk**: Medium - new data model, could have edge cases
- **Mitigation**: Extensive testing with real workflows before launch

---

### Phase 8: Context Visibility & Control

**Goal**: See loaded files, add/remove mid-session without restarting

**Time**: 4 hours

**What Gets Built**:

1. **List Context Tool** (1.5 hours)
   - NEW: `list_context()` - Shows all loaded files with metadata
   - Metadata: path, load time, referenced count, size

2. **Reload Context Tool** (2 hours)
   - NEW: `reload_context(add, remove)` - Adjust context mid-session
   - Add files by path or search result number
   - Remove files by path or list number
   - Validate: No duplicates, files exist

3. **Testing** (0.5 hours)
   - Test: Load context, list files, add file, remove file
   - Validate: No restart needed, changes take effect immediately

**Tool Specs**:

```python
@server.tool()
async def list_context() -> dict:
    \"\"\"
    Show all files currently loaded in context.
    
    Returns:
        {
            \"files\": [
                {
                    \"number\": 1,
                    \"path\": \"docs/prd/live-context-control-v3.md\",
                    \"loaded_at\": \"2025-12-05T10:30:00Z\",
                    \"referenced\": 5,  # Times referenced in responses
                    \"size_kb\": 42
                }
            ],
            \"total_files\": 6,
            \"total_size_kb\": 180
        }
    \"\"\"

@server.tool()
async def reload_context(
    add: list[str] = None,
    remove: list[str] = None
) -> dict:
    \"\"\"
    Add or remove files from context mid-session.
    
    Args:
        add: List of file paths or search result numbers
        remove: List of file paths or list numbers
    
    Examples:
        reload_context(add=[\"docs/prd/feature.md\"])
        reload_context(add=[\"1\", \"2\"])  # From search results
        reload_context(remove=[\"3\"])    # From list_context
        reload_context(remove=[\"docs/old.md\"])
    
    Returns:
        {
            \"added\": [\"docs/prd/feature.md\"],
            \"removed\": [\"docs/old.md\"],
            \"current_files\": 5,
            \"message\": \"Context updated\"
        }
    \"\"\"
```

**Success Criteria**:
- ✅ Can see which files are loaded (no more \"I forget which files are in context\")
- ✅ Can add/remove files in <30 sec (vs 5 min restart)
- ✅ Zero restart spirals (3-5 per week → 0)
- ✅ Context adjustment time: 5 min → 30 sec (90% reduction)

**Dependencies**: Phase 5 (semantic search enables easy file discovery)

**Risk**: Low - simple CRUD operations on context list

---

## 🏗️ System Architecture

### Current Architecture (Before)

```
┌─────────────────────────────────────────────────────┐
│  Claude Chat / Claude Code                          │
│  (User interfaces)                                  │
└────────────┬────────────────────────────────────────┘
             │
             │ MCP Protocol
             │
┌────────────▼────────────────────────────────────────┐
│  ai-assistant MCP Server (1,881 lines)              │
│  /src/ai_assistant/server.py                        │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Tools (9 total)                              │  │
│  │ ✅ read_file, write_file (working)          │  │
│  │ ⚠️  start_session (partial - bad suggestions)│  │
│  │ ⚠️  search_docs (partial - keyword only)     │  │
│  │ ❌ end_session (broken - Notion desc empty)  │  │
│  │ ❌ No list_context, reload_context           │  │
│  │ ❌ No search_repo (semantic search)          │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Data Stores                                  │  │
│  │ • context-profiles.json (heuristics)         │  │
│  │ • NO usage tracking                          │  │
│  │ • NO handoff files                           │  │
│  └──────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────────┘
             │
             │ File System + Notion API
             │
┌────────────▼────────────────────────────────────────┐
│  Repos + Databases                                  │
│                                                      │
│  • /ai-assistant/docs/ (102 files, cluttered)      │
│  • /legacy-ai/research/ (208k tokens)              │
│  • /.chroma/ (Legacy AI RAG - privacy risk!)       │
│  • Notion Strategy Board                           │
│  • Notion Sessions DB (descriptions empty)         │
└─────────────────────────────────────────────────────┘
```

**Key Problems**:
- 🔴 **Privacy Risk**: Legacy AI RAG in personal repo (team can't scale)
- 🔴 **No Learning**: Suggestions based on heuristics, not usage
- 🔴 **No Visibility**: Can't see loaded files, leads to restart spirals
- 🔴 **Tool Priority**: Claude tries bash before MCP tools
- 🔴 **Keyword Search**: Can't find \"related docs\" by meaning

---

### Proposed Architecture (After)

```
┌─────────────────────────────────────────────────────┐
│  Claude Chat (Strategy Sessions)                    │
└────────────┬────────────────────────────────────────┘
             │ MCP Protocol
             │
┌────────────▼────────────────────────────────────────┐
│  ai-assistant MCP Server (REFACTORED)               │
│  Epic 2nd Brain Productivity System                 │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Core Tools (Phase 0)                         │  │
│  │ 🎯 read_file, write_file (priority signals)  │  │
│  │ 🎯 search_repo (semantic - Phase 5)          │  │
│  │ 🎯 list_context, reload_context (Phase 8)    │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Session Management (Phases 2-4, 7)           │  │
│  │ ✅ start_session (learning loop - Phase 4)   │  │
│  │ ✅ end_session (Notion desc - Phase 2)       │  │
│  │ ✅ create_handoff (Phase 7)                  │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Epic 2nd Brain RAG (Phase 5)                 │  │
│  │ • 50k tokens, 102 files                      │  │
│  │ • ChromaDB + BGE (local, privacy-first)      │  │
│  │ • Hybrid search (BM25 + semantic)            │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Data Stores                                  │  │
│  │ • context-profiles.json (learned patterns)   │  │
│  │ • usage-log.jsonl (privacy-preserving)       │  │
│  │ • /docs/handoffs/ (file-based)               │  │
│  └──────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────────┘
             │ File System + Notion API
             │
┌────────────▼────────────────────────────────────────┐
│  ai-assistant Repo (CLEANED - Phase 1)              │
│  • /docs/ (organized, no orphaned folders)         │
│  • /.chroma/epic-2b/ (ONLY Epic 2nd Brain data)    │
│  • Notion Sessions DB (descriptions populated)     │
└─────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────┐
│  Claude Code (Implementation Sessions)               │
└────────────┬────────────────────────────────────────┘
             │ MCP Protocol
             │
┌────────────▼────────────────────────────────────────┐
│  legacy-ai MCP Server (NEW - Phase 6)               │
│  Customer Discovery System                          │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Customer Discovery Tools                     │  │
│  │ • search_legacy_corpus                       │  │
│  │ • get_customer_info                          │  │
│  │ • read_source_document                       │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ Legacy AI RAG (MIGRATED)                     │  │
│  │ • 208k tokens, 896 chunks                    │  │
│  │ • ChromaDB + BGE (local)                     │  │
│  │ • Hybrid search (proven, 8 tests passing)    │  │
│  └──────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────────┘
             │ File System
             │
┌────────────▼────────────────────────────────────────┐
│  legacy-ai Repo (BUSINESS REPO - Phase 6)           │
│  • /research/customer-discovery/ (208k tokens)     │
│  • /.chroma/ (ONLY Legacy AI data)                 │
│  • Team-ready (Peter can install without privacy  │
│    risk to Epic 2nd Brain data)                    │
└─────────────────────────────────────────────────────┘
```

**Key Improvements**:
- ✅ **Privacy Safe**: Separate repos, Peter can join Legacy AI without seeing Epic 2nd Brain
- ✅ **Learning Loop**: Suggestions based on actual usage (Phase 4)
- ✅ **Full Visibility**: `list_context()`, `reload_context()` (Phase 8)
- ✅ **Tool Priority**: 🎯 signals make MCP tools PRIMARY (Phase 0)
- ✅ **Semantic Search**: Find \"related docs\" by meaning (Phases 5-6)
- ✅ **Bulletproof Handoffs**: File-based, auto-detected (Phase 7)

---

### Data Models

**context-profiles.json** (Phase 4 - Learning Loop):

```json
{
  \"Epic 2nd Brain\": {
    \"infrastructure\": {
      \"suggested_files\": [
        {
          \"path\": \"docs/prd/live-context-control-v3.md\",
          \"score\": 45,
          \"reason\": \"Referenced in 8/10 recent sessions\",
          \"last_used\": \"2025-12-05T11:30:00Z\"
        },
        {
          \"path\": \"ROADMAP.md\",
          \"score\": 40,
          \"reason\": \"Loaded and kept in 10/10 sessions\",
          \"last_used\": \"2025-12-05T11:25:00Z\"
        },
        {
          \"path\": \"docs/architecture/mcp-server-current-state-analysis.md\",
          \"score\": 35,
          \"reason\": \"Explicitly added in 6/10 sessions\",
          \"last_used\": \"2025-12-03T14:20:00Z\"
        }
      ],
      \"always_load\": [
        \"ROADMAP.md\"
      ],
      \"last_updated\": \"2025-12-05T11:45:00Z\",
      \"sessions_analyzed\": 10,
      \"accuracy\": 0.75
    }
  },
  \"Legacy AI\": {
    \"customer-discovery\": {
      \"suggested_files\": [
        {
          \"path\": \"research/customer-discovery/meta-analysis.md\",
          \"score\": 50,
          \"reason\": \"Referenced in 9/10 recent sessions\",
          \"last_used\": \"2025-12-04T09:15:00Z\"
        }
      ],
      \"always_load\": [
        \"research/customer-discovery/interview-guide.md\"
      ],
      \"last_updated\": \"2025-12-04T09:30:00Z\",
      \"sessions_analyzed\": 10,
      \"accuracy\": 0.80
    }
  }
}
```

**usage-log.jsonl** (Phase 4 - Append-only, privacy-preserving):

```jsonl
{\"timestamp\": \"2025-12-05T10:30:00Z\", \"project\": \"Epic 2nd Brain\", \"work_stream\": \"infrastructure\", \"event\": \"file_loaded\", \"file\": \"docs/prd/live-context-control-v3.md\", \"source\": \"suggestion\"}
{\"timestamp\": \"2025-12-05T10:35:00Z\", \"project\": \"Epic 2nd Brain\", \"work_stream\": \"infrastructure\", \"event\": \"file_referenced\", \"file\": \"docs/prd/live-context-control-v3.md\", \"reference_count\": 5}
{\"timestamp\": \"2025-12-05T10:40:00Z\", \"project\": \"Epic 2nd Brain\", \"work_stream\": \"infrastructure\", \"event\": \"file_removed\", \"file\": \"docs/context/testing-roadmap.md\", \"reason\": \"not_relevant\"}
{\"timestamp\": \"2025-12-05T10:42:00Z\", \"project\": \"Epic 2nd Brain\", \"work_stream\": \"infrastructure\", \"event\": \"file_added\", \"file\": \"docs/architecture/mcp-server-current-state-analysis.md\", \"source\": \"search\"}
{\"timestamp\": \"2025-12-05T11:00:00Z\", \"project\": \"Epic 2nd Brain\", \"work_stream\": \"infrastructure\", \"event\": \"session_end\", \"duration_hours\": 1.5, \"files_loaded\": 6, \"files_referenced\": 4}
```

**Note**: Usage log contains NO conversation content, only file paths and actions (privacy-preserving).

**Handoff File** (Phase 7 - File-based handoffs):

```markdown
---
status: pending
created: 2025-12-05T11:30:00Z
initiative_id: page_abc123
initiative_name: Applied Context Engineering
project: Epic 2nd Brain
work_stream: infrastructure
approved_by: Dharan Chandrahasan
---

# Handoff: Live Context Control v3

## What Was Approved
Comprehensive MCP refactor to eliminate 100-140 min/week of context loading friction.

## Context to Load
- docs/prd/live-context-control-v3.md (PRIMARY)
- docs/context/one-pagers/infrastructure/context-engineering.md
- docs/architecture/mcp-server-current-state-analysis.md
- ROADMAP.md

## Task
Implement 8 phases over 4 weeks (60 hours).

## Success Criteria
- Tool selection: 90-120 sec → <5 sec (95% reduction)
- Context suggestions: 30% → 80% accuracy
- File discovery: 90-120 sec → <5 sec
- Session handoff: Manual → Automatic

## Next Steps
Start with Phase 0 (Tool Selection Priority Fix) - 2 hours.
```

---

## 📅 Implementation Plan

### Week 1: Quick Wins (Dec 5-13)

**Day 1 (Dec 5)** - 6 hours
**Day 1 (Dec 5)** - 9 hours
- ✅ Phase 0: Tool Selection Priority Fix (2 hours)
  - Update tool descriptions with 🎯 priority signals
  - Test with 5 queries that previously caused spirals
- ✅ Phase 0.5: Enhanced File Editing Tools (2 hours)
  - Implement edit_section() MCP tool
  - Test on this PRD file
- ✅ Phase 1: Repo Organization Cleanup (4 hours)
  - Archive orphaned folders (Failed/, hold-for-later/, research/)
  - Create docs/README.md organization guide
  - Validate tool compatibility

**Day 2 (Dec 9)** - 6 hours
- ✅ Phase 2: Session Handoff Fix (2 hours)
  - Update `end_session()` to call `write_to_page_content()`
  - Test Workflow A (strategy session)
- ✅ Phase 3: End-Session Protocol (2 hours)
  - Add roadmap update logic to `end_session()`
  - Test auto-update flow
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
  - Measure time savings (before vs after)
  - Document any issues or edge cases

**Week 1 Total**: 20 hours
**Deliverables**: 4 phases shipped, learning loop collecting data

---

### Week 2-3: Heavy Lifting (Dec 16-27)

**Day 5-6 (Dec 16-17)** - 12 hours
- ✅ Phase 5: Epic 2nd Brain RAG (12 hours)
  - Day 5 (6 hours): RAG infrastructure setup
    - Copy RAG code from Legacy AI
    - Set up ChromaDB for Epic 2nd Brain corpus
    - Configure BGE embeddings (local)
  - Day 6 (6 hours): Indexing + MCP tools
    - Build indexing pipeline (header-based chunking)
    - Implement `search_repo()` and `list_files()` tools
    - Test semantic search quality

**Day 7-9 (Dec 18-20)** - 12 hours
- ✅ Phase 6: Legacy AI RAG Migration (12 hours)
  - Day 7 (4 hours): Create Legacy AI MCP server
    - New file: `legacy-ai/src/legacy_ai/mcp_server.py`
    - Copy core MCP logic, keep only Legacy AI tools
  - Day 8 (4 hours): Move RAG code
    - Copy `rag/` folder to Legacy AI repo
    - Update imports, paths
    - Move `.chroma/` vector DB
  - Day 9 (4 hours): Testing & validation
    - Test customer discovery workflows (Story 6)
    - Validate privacy isolation (no Epic 2nd Brain data in Legacy AI RAG)
    - Validate search quality unchanged

**Week 2-3 Total**: 24 hours
**Deliverables**: Semantic search operational, RAG separated for privacy

---

### Week 4: Polish (Dec 30-Jan 3)

**Day 10-12 (Dec 30-Jan 1)** - 12 hours
- ✅ Phase 7: Handoff Auto-Detection (12 hours)
  - Day 10 (4 hours): Handoff data model + schema
    - Define handoff JSON + markdown format
    - Create `/docs/handoffs/` folder structure
  - Day 11 (4 hours): Create handoff tool
    - Implement `create_handoff()` in Claude Chat MCP
    - Test handoff file generation
  - Day 12 (4 hours): Auto-detection logic
    - Update `start_session()` in Claude Code MCP
    - Test Workflow B (approve PRD → start session in Code)

**Day 13 (Jan 2)** - 4 hours
- ✅ Phase 8: Context Visibility & Control (4 hours)
  - Implement `list_context()` tool (1.5 hours)
  - Implement `reload_context()` tool (2 hours)
  - Test mid-session context adjustments (0.5 hours)

**Day 14 (Jan 3)** - 4 hours
- ✅ Final Validation & Documentation (4 hours)
  - End-to-end testing (all 8 phases)
  - Measure final metrics (time saved, accuracy)
  - Update ROADMAP.md (mark initiative complete)
  - Write session log

**Week 4 Total**: 20 hours
**Deliverables**: Full system operational, validated, documented

---

### Timeline Summary

| Week | Days | Hours | Phases | Key Deliverables |
|------|------|-------|--------|------------------|
| 1 (Dec 5-13) | 4 | 20 | 0-4 | Quick wins, learning loop collecting data |
| 2-3 (Dec 16-27) | 4 | 24 | 5-6 | Semantic search, RAG separated for privacy |
| 4 (Dec 30-Jan 3) | 5 | 16 | 7-8 | Handoffs, context control, final validation |
| **Total** | **13** | **60** | **8** | **State-of-the-art MCP server** |

**Critical dates**:
- Dec 25 (Christmas): No work scheduled
- Jan 3: Final validation complete
- Jan 5: Baby due (all work finished)

---

## 📊 Success Metrics & Acceptance Criteria

### Overall Success Criteria

**Performance Improvements**:
- ✅ Tool selection: 90-120 sec → <5 sec (95% reduction)
- ✅ Context suggestions: 30% → 80% accuracy (2.7x improvement)
- ✅ File discovery: 90-120 sec → <5 sec (95% reduction)
- ✅ Session handoff: Manual → Automatic (100% elimination)
- ✅ Context adjustment: 5 min → 30 sec (90% reduction)

**Time Saved**:
- ✅ Week 1: 15-45 min/week (Phase 0: tool priority)
- ✅ Week 1: 45 min/week (Phases 2-4: handoffs, learning)
- ✅ Week 2-3: 35-65 min/week (Phases 5-6: semantic search)
- ✅ Week 4: Eliminated restart spirals (additional 15-30 min/week)
- ✅ **Total: 100-140 min/week saved** (1.7-2.3 hours/week)

**ROI**:
- Investment: 60 hours
- Weekly savings: 100-140 min (1.7-2.3 hours)
- Payback period: 26-35 weeks (6-8 months)
- 1-year return: 88-120 hours saved for 60 invested (1.5-2x ROI)

**Privacy**:
- ✅ Legacy AI and Epic 2nd Brain RAGs completely separated
- ✅ Peter can install Legacy AI MCP without seeing Epic 2nd Brain data
- ✅ Team-ready architecture (can scale to 5-10 people without privacy risk)

---

### Per-Phase Acceptance Criteria

**Phase 0: Tool Selection Priority Fix**

You'll know it works when:
- [ ] Claude uses MCP tools on first attempt (not 8th)
- [ ] Zero \"bash spiral\" incidents in 5 test queries
- [ ] Tool selection time: <5 sec (vs 90-120 sec before)
- [ ] No longer need to say \"use MCP tool\" explicitly

**Phase 1: Repo Organization Cleanup**

You'll know it works when:
- [ ] Zero orphaned folders in main docs/ tree
- [ ] Organization framework documented in docs/README.md
- [ ] All MCP tools work with new structure (no broken paths)
- [ ] File discovery easier (less clutter)

**Phase 2: Session Handoff Fix**

You'll know it works when:
- [ ] Notion Sessions database description populated automatically
- [ ] Description includes: decisions, next steps, context used
- [ ] Zero manual git commit message copying
- [ ] Session summary visible in Notion immediately after end_session

**Phase 3: End-Session Protocol**

You'll know it works when:
- [ ] ROADMAP.md updated automatically at session end
- [ ] Initiative status synced with Strategy Board
- [ ] Completion dates populated for completed initiatives
- [ ] Zero manual roadmap updates needed

**Phase 4: Context Learning Loop**

You'll know it works when:
- [ ] Usage tracking operational (all events logged in usage-log.jsonl)
- [ ] Learning algorithm updates context-profiles.json based on real data
- [ ] Suggestion accuracy: 30% → 60% after 1 week, 80% after 2 weeks
- [ ] Can explain why files suggested (\"Used in 8/10 sessions\")
- [ ] Can reset profiles if system learns wrong pattern

**Phase 5: Epic 2nd Brain RAG**

You'll know it works when:
- [ ] Can find \"related PRDs\" in <2 seconds
- [ ] Search quality better than keyword matching (manual validation)
- [ ] File discovery time: <5 sec (vs 90-120 sec before)
- [ ] Supports numbered selection: \"Load results 1, 2, and 4\"
- [ ] Cross-project search works (Epic 2nd Brain vs Legacy AI correctly routed)

**Phase 6: Legacy AI RAG Migration**

You'll know it works when:
- [ ] Two separate MCP servers running independently
- [ ] Complete privacy isolation (can share Legacy AI MCP without exposing Epic 2nd Brain data)
- [ ] Legacy AI RAG quality unchanged (8 test cases still passing)
- [ ] Customer discovery workflow (Story 6) still works
- [ ] No Epic 2nd Brain data in Legacy AI vector DB (validated with spot checks)

**Phase 7: Handoff Auto-Detection**

You'll know it works when:
- [ ] Handoff files created automatically at approval in Claude Chat
- [ ] Claude Code auto-detects handoffs on \"start session\"
- [ ] Zero manual re-explaining (5-10 min saved per session)
- [ ] Handoff contains all necessary context (PRD, one-pager, initiative link)
- [ ] Workflow B seamless: Approve in Chat → Start in Code → Context loaded

**Phase 8: Context Visibility & Control**

You'll know it works when:
- [ ] Can see which files are loaded (no more \"I forget which files\")
- [ ] Can add/remove files in <30 sec (vs 5 min restart)
- [ ] Zero restart spirals (3-5 per week → 0)
- [ ] Context adjustment time: 5 min → 30 sec (90% reduction)
- [ ] `list_context()` shows metadata (load time, referenced count, size)

---

## ⚠️ Risks & Mitigations

### High-Risk Phases

**Phase 6: Legacy AI RAG Migration**

**Risks**:
- Could break existing customer discovery workflow (Story 6)
- Data loss if migration fails mid-process
- Performance regression (slower search)

**Mitigations**:
- **Option B (Roll Back)**: If migration breaks, roll back to current state
- **Backup first**: Copy `.chroma/` before migration
- **Extensive testing**: Validate all 8 test cases pass before cutover
- **Parallel run**: Keep both MCP servers running during validation period

**Contingency Plan**:
- If breaks: Roll back, mark Phase 6 as \"deferred\"
- Ship Phases 0-5, 7-8 (still get 80% of value)
- Revisit migration in Feb 2026 (after parental leave)

---

**Phase 7: Handoff Auto-Detection**

**Risks**:
- New data model could have edge cases
- Claude Code might not detect handoffs correctly
- Handoff files could become stale/orphaned

**Mitigations**:
- **Extensive testing**: Test Workflow B with 5 different PRDs
- **Status tracking**: Handoffs have status (pending/in_progress/complete)
- **Manual override**: Can always start session without handoff if needed

**Contingency Plan**:
- If buggy: Fall back to manual handoffs (current state)
- Still get value from Phases 0-6, 8
- Polish Phase 7 in Jan (post-baby, lower pressure)

---

### Medium-Risk Phases

**Phase 4: Context Learning Loop**

**Risks**:
- Algorithm might learn wrong patterns (bias toward recent files)
- Could suggest irrelevant files if not enough data
- Privacy concern: Usage log could contain sensitive paths

**Mitigations**:
- **Weight recent sessions**: Last 5 sessions = 2x weight (balances recency with stability)
- **Minimum data threshold**: Need 5+ sessions before learning kicks in
- **Reset mechanism**: Can manually reset profiles if learning goes wrong
- **Privacy-preserving log**: Only stores paths and actions, NO conversation content

**Contingency Plan**:
- If learning poor: Disable learning, fall back to heuristics (current state)
- Still get value from Phases 0-3, 5-8

---

**Phase 5: Epic 2nd Brain RAG**

**Risks**:
- Corpus might be too small (50k tokens) for RAG to be better than keyword search
- ChromaDB might be overkill (performance overhead)
- BGE embeddings might not work well for technical docs

**Mitigations**:
- **Benchmark first**: Compare RAG vs keyword search on 10 test queries
- **Hybrid search**: Combine BM25 + semantic (get best of both)
- **Incremental rollout**: Test with personal use before recommending widely

**Contingency Plan**:
- If RAG not better: Fall back to improved keyword search (regex + fuzzy matching)
- Still get value from Phases 0-4, 6-8

---

### Low-Risk Phases

**Phases 0-3, 8**: Low risk (simple refactors, no new systems)

**Mitigation**: Even if something breaks, easy to roll back

---

## 🚫 Out of Scope (v3)

These are explicitly OUT of scope for v3 (can be v4, v5, etc.):

### Deferred to Future Versions

❌ **Auto-context pruning** (risky, needs extensive validation)
- Why deferred: Could remove files user needs, hard to detect
- When to revisit: v4, after learning loop proven for 3+ months

❌ **Real-time token release** (technical limitation)
- Why deferred: Can't delete conversation history in Claude API
- When to revisit: If/when Anthropic adds this capability

❌ **Cross-conversation memory** (different problem)
- Why deferred: Requires persistent memory like Projects, out of MCP scope
- When to revisit: v5, if Projects API becomes available

❌ **Multi-agent context coordination** (technical limitation)
- Why deferred: No API for Claude Code prompt injection
- When to revisit: If/when Anthropic adds agent-to-agent communication

❌ **Voice commands for context** (\"Claude, remove the architecture doc\")
- Why deferred: Polish, not core value
- When to revisit: v4, after core features proven

❌ **Context presets** (\"Load my 'deep work' context set\")
- Why deferred: Learning loop should make presets unnecessary
- When to revisit: v5, if users request after trying learning loop

❌ **External tool integration** (VS Code, Cursor)
- Why deferred: MCP is Claude Desktop only, scope creep
- When to revisit: v6, if demand warrants

❌ **Advanced visualizations** (context usage graphs, timeline views)
- Why deferred: Nice-to-have polish, not core value
- When to revisit: v4, after core features stable

### Explicitly Rejected (Scope Protection)

❌ **Two-way Notion sync** (deferred to Feb 2026)
- Why rejected: Different problem (mobile access), high complexity (80-120 hours)
- When to revisit: Feb 2026, after parental leave

❌ **Repo onboarding automation** (deferred, separate 2-hour project)
- Why rejected: One-time setup, not continuous workflow friction
- When to revisit: When adding 3rd+ project (Life Admin, etc.)

---

## 📝 Change Log

| Date | Update | Author |
|------|--------|--------|
| 2025-12-05 | Created comprehensive PRD v3 (supersedes v2) | Claude (Sonnet 4.5) |
| 2025-12-05 | Added 7 validated pain points with root causes | Claude (Sonnet 4.5) |
| 2025-12-05 | Added 8-phase solution design with detailed specs | Claude (Sonnet 4.5) |
| 2025-12-05 | Added before/after architecture diagrams | Claude (Sonnet 4.5) |
| 2025-12-05 | Added 4-week implementation plan (60 hours) | Claude (Sonnet 4.5) |
| 2025-12-05 | Added per-phase success metrics & acceptance criteria | Claude (Sonnet 4.5) |
| 2025-12-05 | Added risk analysis & mitigation strategies | Claude (Sonnet 4.5) |
| 2025-12-05 | Confirmed RAG Strategy: Option C (Separate Repos) | Claude (Sonnet 4.5) |

---

**Related Documents**:
- [Applied Context Engineering One-Pager](../context/one-pagers/infrastructure/context-engineering.md)
- [MCP Server Current State Analysis](../architecture/mcp-server-current-state-analysis.md)
- [ROADMAP.md](../../ROADMAP.md)

---

**Status**: ✅ Ready for Claude Code Implementation

**Next Steps**: Hand this PRD to Claude Code to begin Phase 0 (Tool Selection Priority Fix) - 2 hours, quick win!`,
  `project`: `Epic 2nd Brain`
}
