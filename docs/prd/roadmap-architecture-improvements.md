# PRD: Roadmap Architecture Improvements

**Status**: Complete
**Owner**: Dharan Chandrahasan
**Created**: 2025-11-18
**Completed**: 2025-11-18
**Work Stream**: Roadmap Prioritization

---

## 🎯 TL;DR

Restructure roadmap architecture from single-file chaos to three-layer system with **unified multi-project view**: high-signal priority table at repo root (`ROADMAP.md`) showing P0-P3 across Epic 2nd Brain AND Legacy AI, context-rich one-pagers linking to implementation details, and clear Notion sync strategy. This eliminates scattered updates across multiple files and creates single source of truth for all work.

**Key Decision**: Single unified roadmap (not separate per project) because you're one person, infrastructure serves both projects, and baby deadline requires ruthless cross-project prioritization.

**Time Investment**: 8-11 hours (template creation, migration, git hook enhancement, backlink updates)
**Leverage**: Clear prioritization across all work, reduced decision fatigue, mobile-accessible roadmap, foundation for multi-project scaling

---

## 🔥 Problem Statement

**Current Pain Points**:

1. **Multiple Implementation Plans Scattered**
   - `roadmap.md` in `docs/context/` (Epic 2nd Brain focused)
   - `roadmap-addendum-multi-project.md` (multi-project details)
   - `strategy-board-batch-2.md` (Legacy AI initiatives)
   - Various PRDs with their own roadmaps
   - No clear "what's THE roadmap?" answer

2. **Updates Happen Everywhere**
   - Notion Strategy Board (manual updates)
   - Markdown files (sometimes remembered)
   - Session logs (documented but not reflected in roadmap)
   - Result: Always asking "what's the latest status?"

3. **No High-Signal Priority View Across Projects**
   - Current roadmap is comprehensive but hard to scan
   - Need "what's P0 RIGHT NOW?" answer in 5 seconds
   - Can't compare "Epic 2nd Brain Phase 4" vs "Legacy AI customer interviews"
   - Too much detail mixed with high-level status

4. **New Work Streams Emerge Organically**
   - Like this one (Roadmap Prioritization work stream)
   - No clear place to track them
   - End up bolted onto existing docs

5. **Overload Risk in Layer 2**
   - PRDs, tech requirements, one-pagers, session logs all mixed
   - Hard to know "where should I link this?"
   - Want high-signal linking strategy (one-pagers as aggregation layer)

6. **Mobile Access Friction** (Critical)
   - Can't access roadmap/PRDs when not at computer
   - Need to review context before customer calls, during commutes
   - Current: Must wait until back at laptop

7. **Backlink Fragmentation** (Hidden Risk)
   - MCP tools reference old `docs/context/roadmap.md` path
   - Claude Chat/Code memory has old roadmap location
   - Documentation links point to wrong file
   - Risk: Update new `/ROADMAP.md`, but agents still read old file

**Why Now**:
- Baby deadline approaching (Jan 2026) - need clarity on what matters ACROSS all projects
- Two active projects (Epic 2nd Brain + Legacy AI) - need unified priority view
- 25+ customer interviews coming - need mobile access to context
- Peter potentially joining - need professional roadmap he can read independently
- Foundation for 100,000X workflows - roadmap must be clear to AI agents

---

## ✅ Success Criteria

**Must Have** (Launch Blockers):

1. **Single Source of Truth Across Projects**
   - One `ROADMAP.md` file at repo root with "Project" column
   - Shows P0-P3 across Epic 2nd Brain, Legacy AI, future projects
   - All status updates flow through this file
   - Both Claude Chat and Claude Code know to update it

2. **5-Second Cross-Project Priority Answer**
   - Opening repo shows immediate priority table
   - Clear P0/P1/P2 designation across all work
   - Can instantly compare "Is infrastructure or business more important today?"
   - Status visible at a glance (✅ 🚀 ⬜ 🔴)

3. **Mobile Access to Roadmap AND Docs** (Critical Friction Point)
   - `ROADMAP.md` syncs to Notion page automatically
   - Can check priorities on phone during morning ritual
   - PRDs, one-pagers accessible on mobile (Notion sync)
   - Strategy Board items reflect actuals after updates

4. **Clean Layer 2 Linking**
   - One-pagers aggregate related docs (PRDs, tech requirements, sessions)
   - `ROADMAP.md` links to one-pagers only (not 10 different doc types)
   - Clear information architecture

5. **Manual Update Flow Works for Both Agents**
   - At end of session: "Update roadmap"
   - **Both Claude Chat AND Claude Code know** to update `/ROADMAP.md` (not old file)
   - Git commit → hook triggers Notion sync
   - No broken workflow for first 2-3 weeks of usage

6. **Complete Backlink Migration** (Critical - Prevents Stale Data)
   - All MCP tools updated to reference `/ROADMAP.md` (not `docs/context/roadmap.md`)
   - Git hooks updated to watch correct file
   - Documentation (`docs/README.md`, templates) updated with new paths
   - Claude Chat and Claude Code memory updated with new roadmap location
   - **Test**: Ask "Load roadmap" → returns `/ROADMAP.md` content (not old file)
   - **Test**: Search codebase for `docs/context/roadmap` → 0 results (except archive file)

**Nice to Have** (Post-Launch):

1. **Automatic Status Detection**
   - MCP tool detects "initiative complete" and updates roadmap
   - Reduces manual step at end of session

2. **Project-Filtered Views**
   - Quick filter to "Infrastructure only" or "Legacy AI only"
   - Default shows all projects (cross-project prioritization)

3. **Historical Roadmap Snapshots**
   - Weekly snapshot of priorities for retrospectives
   - Track how priorities shift over time

**Metrics**:
- **Time to find priority**: Current unknown → Target <5 seconds
- **Roadmap staleness**: Current 1-3 days → Target <1 hour (after manual update + sync)
- **"Where does this link?" confusion**: Current 3-5 times/week → Target 0
- **Mobile doc access**: Current 0 (blocked) → Target 3-5 times/week
- **Backlink errors**: Target 0 (all tools point to correct file)

---

## 🚫 Non-Goals

1. **Automatic AI-Driven Roadmap Updates**
   - Why: Need to validate manual flow works first
   - Deferred to: Phase 2 (after 2-3 weeks of manual usage)

2. **Complex Gantt Charts / Timeline Views**
   - Why: Simple table view is sufficient for solo founder
   - Deferred to: When Peter joins (collaborative planning needed)

3. **Real-Time Notion Sync**
   - Why: Git hook sync (<5 seconds after commit) is fast enough
   - Deferred to: Never (unnecessary complexity)

4. **Separate Roadmaps Per Project**
   - Why: You're one person, need unified priority view across all work
   - Alternative: Single roadmap with "Project" column for filtering

5. **Historical Roadmap Versioning UI**
   - Why: Git history already provides this (rollback capability)
   - Deferred to: Never (Git is sufficient)

6. **Learning Note Formatter** (Removed from Scope)
   - Why: Not high leverage, defer to future
   - Context: GPT-4 post-processing for interviews/books - nice-to-have, not critical path

7. **Modifying Notion Roadmap Database** (CRITICAL - Do NOT Touch)
   - Why: Notion "Roadmap" database is Claude Code's write-only session tracker
   - This is the actual source of truth for implementation work
   - Even Dharan doesn't touch it - completely automated
   - **This PRD creates a NEW "Roadmap" PAGE, NOT a database**
   - Different databases:
     - `NOTION_ROADMAP_DB` (env var) = Claude Code session tracker (DO NOT TOUCH)
     - `STRATEGY_BOARD_DATABASE_ID` (env var) = Strategy Board (this PRD updates)
     - New Notion page = Unified roadmap view (this PRD creates)

---

## 🏗️ Proposed Architecture

### **Key Decision: Single Unified Roadmap**

**Rationale**:
- You're one person with one attention span (not a team with separate projects)
- Infrastructure (Context Sync Bridge, Voice-to-Notion) serves BOTH projects
- Baby deadline requires ruthless prioritization: "What's P0 across EVERYTHING?"
- Mobile workflow: One page to check, not two
- Shared infrastructure would be duplicated/confused in separate roadmaps

**Alternative Rejected**: Separate roadmaps per project
- Would require checking two files daily
- Can't compare "Epic 2nd Brain Phase 4" vs "Legacy AI interviews" directly
- Shared infrastructure (MCP tools, git hooks) unclear which roadmap tracks it

---

### **Three-Layer System**

#### **Layer 0: ROADMAP.md** (Repo Root - Unified Multi-Project)
**Location**: `/ROADMAP.md` (repo root, **not** `docs/context/roadmap.md`)
**Purpose**: High-signal priority table showing P0-P3 across ALL projects
**Updates**: Manually at end of session ("Update roadmap" → both agents know to update THIS file)
**Syncs To**: **NEW** Notion "Roadmap (All Projects)" page (you create manually, see Implementation section)

**Key Sections**:
- Active Work (P0-P1, Weeks 1-2) - **with "Project" column**
- Near-Term Backlog (P2-P3, Weeks 3-4) - **with "Project" column**
- Future Work (P4+, Weeks 5+) - **with "Project" column**
- Health Metrics (per project and overall)
- Recent Updates (last 3-5 entries)

**Project Column Values**:
- "Infrastructure" = Epic 2nd Brain (serves all projects)
- "Legacy AI" = Business-specific work
- "Life Admin" = Future (baby prep, home remodel, etc.)

**Why Repo Root?**
- First thing visible when opening repo (GitHub, VS Code, Terminal)
- Signals "this is the source of truth for ALL work"
- Convention: `README.md` = about the repo, `ROADMAP.md` = about the work

---

#### **Layer 1: One-Pagers** 
**Location**: `docs/context/one-pagers/[project]/[initiative-name].md`
**Purpose**: Context + why + status + links to implementation details
**Updates**: Updated when initiative status changes materially
**Syncs To**: Notion (Phase 2 - for mobile doc access)

**Project-Specific Organization**:
```
ai-assistant/docs/context/one-pagers/
├── infrastructure/
│   ├── context-sync-bridge.md
│   ├── mobile-doc-access.md
│   ├── roadmap-architecture-improvements.md (THIS PRD's one-pager, created when approved)
│   └── context-profile-optimization.md
└── TEMPLATE.md

legacy-ai/docs/context/one-pagers/
├── customer-interview-analysis.md
├── template-enhancements.md
└── TEMPLATE.md
```

**CRITICAL**: Legacy AI one-pagers live in `legacy-ai/` repo (separate repo), NOT in `ai-assistant/` repo. This maintains clean separation for when Peter joins.

**One-Pager Creation Workflow**:
1. **Trigger**: Initiative approved and moving to implementation (P0-P2)
2. **Claude Chat**: Writes PRD → Gets approval
3. **Claude Chat**: Creates one-pager in `docs/context/one-pagers/[project]/[initiative].md`
   - Links to PRD (Layer 1 → Layer 2)
   - Includes TL;DR, Why This Matters, Current Status
4. **Claude Chat**: Adds initiative to `/ROADMAP.md` with one-pager link
5. **Claude Code**: Reads one-pager → Creates tech requirements → Implements
6. **Both agents**: Update one-pager status as work progresses

**Example (This PRD)**:
- ✅ PRD created: `docs/prd/roadmap-architecture-improvements.md`
- ⬜ One-pager next: `docs/context/one-pagers/infrastructure/roadmap-architecture-improvements.md` (when approved)
- ⬜ ROADMAP.md entry next: Links to one-pager

**Key Sections**:
- TL;DR (2-3 sentences)
- Why This Matters (problem + opportunity)
- Current Status (phase, progress, blockers, next steps)
- Implementation Artifacts (links to PRDs, tech requirements, sessions)
- Key Decisions & Trade-offs
- Metrics & Validation
- Change Log

**Why Project Subfolders in ai-assistant, Separate Repo for legacy-ai?**
- Infrastructure one-pagers in `ai-assistant/` (they belong to the infrastructure project)
- Legacy AI one-pagers in `legacy-ai/` (clean separation when Peter joins)
- Easy to find context: "Where's the Legacy AI customer analysis one-pager?" → legacy-ai/ repo
- Scales to future projects (Life Admin, Project Franklin, etc.)

---

#### **Layer 2: Implementation Details** (Existing)
**Locations**:
- `docs/prd/` - Strategic requirements (Claude Chat writes)
- `docs/tech-requirements/` - Technical specs (Claude Code writes)
- `docs/sessions/` - What happened each session (both write)
- `docs/architecture/` - System diagrams (both write)

**No Changes**: Already well-structured, just link from one-pagers

---

### **Notion Sync Strategy**

**CRITICAL DISTINCTION - Three Separate Notion Entities**:

1. **Notion "Roadmap" Database** (`NOTION_ROADMAP_DB` env var)
   - **Purpose**: Claude Code's write-only session tracker
   - **Usage**: Tracks what Claude Code shipped each session
   - **Access**: Automated only, even Dharan doesn't touch it
   - **THIS PRD DOES NOT MODIFY THIS** ❌

2. **Strategy Board Database** (`STRATEGY_BOARD_DATABASE_ID` env var)
   - **Purpose**: High-level initiative tracking
   - **Usage**: Manual + automated updates from roadmap changes
   - **Access**: Dharan updates manually, git hooks update automatically
   - **This PRD updates this** ✅ (when `/ROADMAP.md` initiative status changes)

3. **NEW: "Roadmap (All Projects)" Page** (you create manually)
   - **Purpose**: Mobile-accessible unified roadmap view
   - **Usage**: Syncs from `/ROADMAP.md` for mobile access
   - **Access**: Read-only for Dharan (git hook updates it)
   - **This PRD creates this** ✅

---

**Primary Sync**: `/ROADMAP.md` → **NEW** Notion "Roadmap (All Projects)" page
- Git hook watches `/ROADMAP.md`
- On commit: Updates **NEW** Notion page (NOT the Roadmap database)
- Mobile access for morning ritual, quick status checks
- **Includes "Project" column** for filtering in Notion

**Setup** (Implementation Phase - Dharan Creates Page):
1. Create new page in Notion under "Epic 2nd Brain"
2. Title: "Roadmap (All Projects)"
3. Get page ID from URL
4. Add to `.env`: `NOTION_UNIFIED_ROADMAP_PAGE=<page-id>`
5. Git hook syncs markdown content to this page

**Secondary Sync**: `/ROADMAP.md` → Strategy Board Database (`STRATEGY_BOARD_DATABASE_ID`)
- When `/ROADMAP.md` changes initiative status (e.g., ⬜ → 🚀 → ✅)
- Git hook updates corresponding Strategy Board item
- Keeps Strategy Board accurate without manual updates
- Uses **existing** `STRATEGY_BOARD_DATABASE_ID` env var

**Phase 2 (Mobile Doc Access)**: One-pagers → Notion pages
- Priority: High (critical friction point - can't access docs on phone)
- Implementation: Git hook enhancement (selective sync, not all docs)
- Use case: Review customer interview context before calls, during commutes

---

## 📋 Migration Plan

### **Step 1: Create Templates**

**Files to Create**:
1. `/ROADMAP.md` (new, at repo root - **with Project column**)
2. `docs/context/one-pagers/TEMPLATE.md` (new template)
3. `docs/context/one-pagers/infrastructure/` (new folder in ai-assistant/)
4. Update: `scripts/sync_to_notion.py` (add ROADMAP.md sync logic)

**What Stays**:
- `docs/context/roadmap.md` (rename to `roadmap-archive.md`)
- All existing PRDs, tech requirements, sessions (no changes)

---

### **Step 2: Update Backlinks (CRITICAL - Prevents Stale Data)**

**Files to Update**:
1. **MCP Server** (`mcp_server/full_server.py`):
   - Search for: `docs/context/roadmap.md`
   - Replace with: `ROADMAP.md`
   - Update `start_session()` tool to load from new path

2. **Git Hooks** (`scripts/sync_to_notion.py`):
   - Add watch for `/ROADMAP.md`
   - Remove watch for `docs/context/roadmap.md` (if exists)

3. **Documentation** (`docs/README.md`):
   - Update all references to roadmap location
   - Add note: "Old roadmap archived at `docs/context/roadmap-archive.md`"

4. **Templates** (`docs/sessions/TEMPLATE.md`, `docs/prd/TEMPLATE.md`):
   - Update example links from `docs/context/roadmap.md` → `ROADMAP.md`

5. **Memory Updates** (Manual - Dharan to confirm):
   - Claude Chat: "The roadmap is now at /ROADMAP.md at repo root"
   - Claude Code: "The roadmap is now at /ROADMAP.md at repo root"

**Validation**:
- Search codebase: `rg "docs/context/roadmap"` → Should only find archive file
- Test MCP: Ask Claude "Load roadmap" → Should return `/ROADMAP.md` content
- Test both agents: "Update roadmap" → Should update `/ROADMAP.md` (not old file)

---

### **Step 3: Consolidate Multi-Project Context**

**Current State**:
- `docs/context/roadmap.md` (Epic 2nd Brain focused)
- `docs/strategy-board-batch-2.md` (Legacy AI initiatives)
- `docs/roadmap-addendum-multi-project.md` (multi-project details)
- Multiple scattered initiative docs

**Target State**:
- Single `/ROADMAP.md` with "Project" column
- All initiatives visible in one priority table
- Clear P0-P3 ranking across projects

**Migration Steps**:
1. Extract active initiatives from current `roadmap.md`
2. Extract Legacy AI initiatives from `strategy-board-batch-2.md`:
   - Customer Interview Analysis (P0)
   - Mobile Doc Access (P1)
   - Template Enhancements (P2)
3. Add "Project" column:
   - "Infrastructure" for Epic 2nd Brain items
   - "Legacy AI" for business items
4. Sort by Priority Score (highest first)
5. Archive old files:
   - `roadmap.md` → `roadmap-archive.md`
   - `strategy-board-batch-2.md` → `strategy-board-batch-2-archive.md`

---

### **Step 4: Extract Content**

**From** `docs/context/roadmap.md`:
- **To** `/ROADMAP.md`: High-level phase status, priority table, health metrics (**add Project column**)
- **To** `docs/context/one-pagers/infrastructure/context-sync-bridge.md`: Detailed context, decisions, timeline

**From** `docs/strategy-board-batch-2.md`:
- **To** `/ROADMAP.md`: Legacy AI initiatives in priority table (**with Project: Legacy AI**)
- **To** `legacy-ai/docs/context/one-pagers/customer-interview-analysis.md`: Full initiative context (in legacy-ai repo)
- **To** `legacy-ai/docs/context/one-pagers/mobile-doc-access.md`: Mobile access context (if customer-facing, else infrastructure folder)

**Result**: 
- `/ROADMAP.md` = scannable in 30 seconds, shows ALL work
- Archive files = detailed reference (keep for git history)
- One-pagers = comprehensive context per initiative (read in 5 minutes)

---

### **Step 5: Notion Setup (Dharan Creates Page)**

**What Dharan Creates**:
1. New page in Notion under "Epic 2nd Brain" project
2. Title: "Roadmap (All Projects)"
3. Leave empty (git hook will populate markdown content)
4. Copy page ID from URL (the long UUID in browser address bar)
5. Add to `.env` file:
   ```bash
   NOTION_UNIFIED_ROADMAP_PAGE=<paste-page-id-here>
   ```
6. Verify existing env vars are correct:
   ```bash
   STRATEGY_BOARD_DATABASE_ID=<existing-id>  # This is correct
   NOTION_ROADMAP_DB=<existing-id>           # Claude Code session tracker (DO NOT modify)
   ```

**When This Happens**: During Phase 3 implementation, Claude Code will prompt you

---

### **Step 6: Enhance Git Hooks**

**Current**: `scripts/sync_to_notion.py` syncs session logs to `NOTION_ROADMAP_DB` (Claude Code tracker)

**Add** (without touching existing functionality):
- Watch `/ROADMAP.md` for changes
- Sync to **NEW** `NOTION_UNIFIED_ROADMAP_PAGE` (the page you created)
- Parse initiative status changes → update `STRATEGY_BOARD_DATABASE_ID` items
- (Phase 2) Selective one-pager sync for mobile doc access

**Test**: 
1. Update `/ROADMAP.md` manually (change status, add Legacy AI item)
2. Git commit
3. Verify **NEW** Notion "Roadmap (All Projects)" page updated (not the database)
4. Verify Strategy Board (`STRATEGY_BOARD_DATABASE_ID`) status updated
5. Verify `NOTION_ROADMAP_DB` (Claude Code tracker) untouched ✅

---

### **Step 7: Validate Workflow**

**Test Scenarios**:
1. **End of session update (Infrastructure)**: "Update roadmap" → Claude updates Context Sync Bridge status → commit → Notion syncs
2. **End of session update (Legacy AI)**: "Update roadmap" → Claude updates Customer Interview Analysis → commit → Notion syncs
3. **Mobile access (roadmap)**: Check Notion on phone, see latest priorities across all projects
4. **Mobile access (docs - Phase 2)**: Check Notion on phone, read customer interview one-pager before call
5. **New initiative**: Add Legacy AI item to `/ROADMAP.md` → one-pager created in `legacy-ai/` folder → links to PRD
6. **Status change**: Move P2 Infrastructure → P1, verify Notion reflects change
7. **Cross-project prioritization**: Compare P0 Infrastructure vs P0 Legacy AI - clear which is more urgent
8. **Backlink test**: Ask both agents "Load roadmap" → both return `/ROADMAP.md` content
9. **Claude Code session tracker**: Verify `NOTION_ROADMAP_DB` still receiving Claude Code sessions (untouched)

**Success**: Manual workflow works smoothly for 2-3 weeks before considering automation

---

## 🎨 Design Notes

### **ROADMAP.md Format** (High-Signal Multi-Project Table)

```markdown
# Dharan's Roadmap: All Projects

**Last Updated**: 2025-11-18
**Current Focus**: Legacy AI Customer Discovery + Infrastructure Mobile Access

---

## 🎯 Active Work (P0-P1, This Week)

| Priority | Initiative | Project | Status | Owner | Target | One-Pager |
|----------|-----------|---------|--------|-------|--------|-----------|
| P0 | Customer Interview Analysis | Legacy AI | 🚀 Active | Dharan | Nov 25 | [Link](https://github.com/yourusername/legacy-ai/blob/main/docs/context/one-pagers/customer-interview-analysis.md) |
| P1 | Mobile Doc Access | Infrastructure | ⬜ Next | Dharan | Nov 29 | [Link](docs/context/one-pagers/infrastructure/mobile-doc-access.md) |
| P1 | Context Profile Optimization | Infrastructure | 🚀 Active | Dharan | Nov 22 | [Link](docs/context/one-pagers/infrastructure/context-profile-optimization.md) |

## 📅 Near-Term Backlog (P2-P3, Weeks 3-4)

| Priority | Initiative | Project | Status | Owner | Target | One-Pager |
|----------|-----------|---------|--------|-------|--------|-----------|
| P2 | Template Enhancements | Legacy AI | ⬜ Ready | Dharan | Dec 6 | [Link](https://github.com/yourusername/legacy-ai/blob/main/docs/context/one-pagers/template-enhancements.md) |
| P3 | Notion Command Center | Infrastructure | ⬜ Ready | Dharan | Dec 13 | [Link](docs/context/one-pagers/infrastructure/notion-command-center.md) |

## 🔮 Future Work (P4+, Weeks 5+)

| Priority | Initiative | Project | Status | Owner | Target | One-Pager |
|----------|-----------|---------|--------|-------|--------|-----------|
| P4 | RAG Search | Infrastructure | ⬜ Not Started | Dharan | Dec 20 | [Link](docs/context/one-pagers/infrastructure/rag-search.md) |

---

## 📊 Health Metrics

**Infrastructure (Epic 2nd Brain)**:
- Time Saved: 70-120 min/week (target met ✅)
- Context Load Time: 3 min (target: <3 min ✅)
- Projects Supported: 2 (Epic 2nd Brain, Legacy AI)

**Legacy AI (Business)**:
- Interviews Complete: 5 / 30 target
- Customer Insights Documented: 5 interviews analyzed
- Prototype Decision: On track for Dec 15

---

## 🔄 Recent Updates

- **2025-11-18**: Started Roadmap Architecture Improvements (unified multi-project view)
- **2025-11-18**: Added Mobile Doc Access as P1 (critical friction point)
- **2025-11-13**: Phase 3 Session 2C complete (task title generation fixed)
- **2025-11-12**: Phase 3 Session 2B complete (multi-project implementation)
```

**Note**: Legacy AI links use full GitHub URLs (not relative paths) since they're in separate repo.

---

### **Notion View Strategy**

**Primary View (Default)**: All Projects
- Shows full roadmap with Project column visible
- Sort by Priority (P0 first)
- Use case: Morning ritual - "What's P0 across everything?"

**Filter Views** (Optional):
- "Infrastructure Only" - Filter: Project = Infrastructure
- "Legacy AI Only" - Filter: Project = Legacy AI
- "This Week" - Filter: Target < 7 days from now

---

## 🔄 Update Flow (Manual)

```
End of session:
1. Dharan: "Update roadmap with today's progress"
2. Claude Chat/Code (BOTH know to update /ROADMAP.md):
   a. Updates relevant one-pager status (in correct project folder/repo)
   b. Updates /ROADMAP.md priority table (with Project column)
   c. Git commit with clear message: "Roadmap: [Project] - [Initiative] moved to [Status]"
3. Git hook (post-commit):
   a. Push to GitHub (cloud backup)
   b. Sync /ROADMAP.md → NEW Notion "Roadmap (All Projects)" page (preserve Project column)
   c. Update Strategy Board items in STRATEGY_BOARD_DATABASE_ID (if status changed)
   d. NOTION_ROADMAP_DB untouched (Claude Code session tracker)
   e. (Phase 2) Sync updated one-pagers → Notion (for mobile doc access)
4. Dharan sees latest:
   - In repo: /ROADMAP.md (all projects, one table)
   - On mobile: NEW Notion "Roadmap (All Projects)" page (filter by project if needed)
   - (Phase 2) On mobile: Notion one-pager pages (customer interview context, etc.)
   - On Strategy Board: Updated status
   - Claude Code session tracker: Continues working independently ✅
```

---

## ❓ Open Questions

### ✅ Question 1: Notion Page Structure (DECIDED)
**Decision**: Option A - Single page with markdown tables
**Rationale**: Simplest approach, mirrors file exactly, includes Project column

---

### ✅ Question 2: Strategy Board Update Logic (DECIDED)
**Decision**: Option B - Store Notion page ID in one-pager frontmatter
**Rationale**: Most reliable, scales to multi-project, survives name changes

---

### ✅ Question 3: Archived Roadmap Files (DECIDED)
**Decision**: Option B - Rename to `*-archive.md`
**Files to Rename**:
- `roadmap.md` → `roadmap-archive.md`
- `strategy-board-batch-2.md` → `strategy-board-batch-2-archive.md`

---

### ✅ Question 4: Mobile Doc Access Priority (DECIDED)
**Decision**: Part of roadmap as Phase 2 (after migration complete)
**Rationale**: Critical friction point, but validate architecture first

---

## 📊 Implementation Phases

### **Phase 1: Templates & Backlink Updates** (2-3 hours)
**Deliverables**:
- `/ROADMAP.md` template created (**with Project column**)
- `docs/context/one-pagers/TEMPLATE.md` created
- `docs/context/one-pagers/infrastructure/` folder created
- **All MCP tools updated** to reference `/ROADMAP.md`
- **All documentation updated** with new paths
- **Git hooks updated** to watch new file
- **Memory updates confirmed** (both agents know new location)

**Validation**: 
- Templates reviewed and approved
- Search `rg "docs/context/roadmap"` → only archive file
- Test: Ask agents "Load roadmap" → returns `/ROADMAP.md`

---

### **Phase 2: Content Migration** (2-3 hours)
**Deliverables**:
- `/ROADMAP.md` populated from:
  - Current `roadmap.md` (Infrastructure items)
  - `strategy-board-batch-2.md` (Legacy AI items)
  - **Project column added to all rows**
- First one-pagers created:
  - `infrastructure/context-sync-bridge.md`
  - `infrastructure/mobile-doc-access.md`
  - `infrastructure/roadmap-architecture-improvements.md` (this PRD's one-pager)
- Old files renamed:
  - `roadmap.md` → `roadmap-archive.md`
  - `strategy-board-batch-2.md` → `strategy-board-batch-2-archive.md`

**Validation**: New structure makes sense, nothing lost, priorities clear across projects

---

### **Phase 3: Notion Setup & Git Hook Enhancement** (2-3 hours)
**Deliverables**:
- **Dharan creates**: New Notion "Roadmap (All Projects)" page
- **Dharan adds**: `NOTION_UNIFIED_ROADMAP_PAGE` to `.env`
- `scripts/sync_to_notion.py` updated:
  - Watches `/ROADMAP.md`
  - Syncs to NEW page (`NOTION_UNIFIED_ROADMAP_PAGE`)
  - Updates Strategy Board (`STRATEGY_BOARD_DATABASE_ID`)
  - **Does NOT touch** `NOTION_ROADMAP_DB` (Claude Code tracker)
- Test: Update Legacy AI item, verify Notion reflects change
- Test: Verify Claude Code session tracker still works

**Validation**: Test scenarios pass (commit → Notion updates both projects, session tracker untouched)

---

### **Phase 4: Mobile Doc Access (Phase 2)** (2-3 hours)
**Deliverables**:
- Git hook enhancement: Selective one-pager sync
- Customer-facing one-pagers sync to Notion
- Test: Check one-pager on phone before customer call

**Validation**: Mobile doc access working, friction point resolved

---

### **Phase 5: Workflow Validation** (1-2 weeks)
**Deliverables**:
- Manual updates for 2-3 weeks
- Test cross-project prioritization decisions
- Friction points documented
- Iteration on templates based on usage

**Validation**: Workflow feels natural, no broken steps, clear P0 across all work

---

## 🎓 Systems Thinking Applied

**Leverage Point #6 - Information Flow**:
- **Current**: Information scattered (Infrastructure in roadmap.md, Legacy AI in strategy-board-batch-2.md)
- **New**: Unified hierarchy (ROADMAP.md with Project column → one-pagers → implementation details)
- **Impact**: Reduced cognitive load, faster cross-project decision-making

**Leverage Point #5 - Rules**:
- **Current**: No standard for where updates happen (Infrastructure? Legacy AI? Both?)
- **New**: Rule: "All status updates flow through /ROADMAP.md, tagged with Project"
- **Impact**: Consistency, no "which file do I update?" questions

**Leverage Point #4 - Self-Organization**:
- **Current**: Manual separation (you decide which project to focus on)
- **New**: System self-organizes priorities (P0 is P0 regardless of project)
- **Impact**: Objective prioritization, less decision fatigue

**Feedback Loop - Cross-Project Clarity**:
```
Unified roadmap → Clear P0 across projects → Focus on highest leverage → Better outcomes → Stronger conviction → Unified roadmap
```

**Balancing Loop - Roadmap Staleness**:
```
Stale roadmap → Manual update prompt → Git commit → Notion sync (both projects) → Fresh roadmap → (equilibrium)
```

---

## 📝 Dependencies

**Requires**:
- Phase 2 complete (git hooks + Notion sync operational)
- `scripts/sync_to_notion.py` exists and works for session logs
- Multi-project infrastructure validated (Context Sync Bridge Phase 3 complete)
- `.env` file with correct database IDs:
  - `STRATEGY_BOARD_DATABASE_ID` (exists, correct)
  - `NOTION_ROADMAP_DB` (exists, Claude Code tracker - do not modify)
  - `NOTION_UNIFIED_ROADMAP_PAGE` (will add in Phase 3)

**Enables**:
- Clearer prioritization across Infrastructure AND Business work
- Foundation for Peter onboarding (clear roadmap showing both projects)
- Scalable structure for Life Admin, Baby Prep, Project Franklin roadmaps
- Mobile doc access (Phase 2) for customer call prep

**Blocks Nothing**: Can be done in parallel with other work streams

---

## 🔗 Related Documents

**Context**:
- [Context Sync Bridge PRD](context-sync-bridge.md) - Parent initiative
- [Multi-Project Expansion PRD](multi-project-expansion.md) - Validated multi-project infrastructure
- [Strategy Board Batch 2](../strategy-board-batch-2.md) - Legacy AI initiatives to consolidate

**Implementation**:
- [Strategy Board Workflow Tech Requirements](../tech-requirements/strategy-board-workflow.md) - Git hook foundation
- [Session Log Template](../sessions/TEMPLATE.md) - Similar manual update workflow

---

## 📅 Timeline

**Target Completion**: Nov 22-25, 2025 (Week 2-3)
**Estimated Effort**: 8-11 hours total (includes backlink updates + mobile doc access)
**Urgency**: High (mobile doc access is blocking customer call prep)

**Phases**:
- Week 2 (Nov 18-22): Phase 1-2 (templates + backlinks + migration, 4-6 hours)
- Week 3 (Nov 25-29): Phase 3 (Notion setup + git hooks, 2-3 hours)
- Week 3 (Nov 25-29): Phase 4 (mobile doc access, 2-3 hours)
- Week 3-4 (Nov 25 - Dec 6): Phase 5 (workflow validation, ongoing)

---

## 📊 Success Metrics

**Quantitative**:
- Time to find priority: <5 seconds (opening repo shows unified table)
- Roadmap staleness: <1 hour (after manual update)
- Mobile roadmap checks: 3-5 times/week (Notion access)
- Mobile doc access: 3-5 times/week (one-pagers on phone)
- Cross-project priority decisions: <10 seconds (P0 visible immediately)
- Backlink errors: 0 (all tools point to /ROADMAP.md)

**Qualitative**:
- No more "where's the latest roadmap?" confusion
- No more "which project should I focus on today?" paralysis
- Claude agents know exactly where to update status (regardless of project)
- Both agents update correct file when asked "Update roadmap"
- Peter can read unified roadmap independently (when he joins)
- Can prep for customer calls on-the-go (mobile one-pager access)
- Claude Code session tracker continues working independently

**2x Validation**: If roadmap doesn't reduce "where do I update this?" questions by 80%, structure needs iteration

---

## 🎯 Alignment with Personal Context

**Baby Deadline (Jan 2026)**:
- Clear priorities visible in 5 seconds = faster decision-making across ALL work
- Unified view = easy to pause low-priority items when time drops
- Mobile access = check status during walks, commutes, low-energy moments
- Foundation for "maintenance mode" when baby arrives (clear P0-P1 cutline)

**Legacy AI $5k MRR Goal (June 2026)**:
- Customer interview analysis visible in unified roadmap (not hidden in separate file)
- Can compare "Is infrastructure or customer discovery more important?" objectively
- Mobile doc access unblocks customer call prep (25+ interviews coming)

**100,000X Philosophy**:
- Roadmap clarity = less cognitive load per decision
- Unified view = system decides priority (not manual comparison)
- Manual workflow first = validate before automating
- Templates = structure thinking, don't replace it

**Systems Thinking**:
- Current structure (separate files per project) → manual integration overhead
- New structure (unified table with Project column) → self-organizing prioritization
- Trade-offs transparent (manual updates upfront, automation later)

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-18 | Claude (Sonnet 4.5) | Initial draft based on Roadmap Prioritization work stream kickoff |
| 2025-11-18 | Claude (Sonnet 4.5) | Updated with unified multi-project decision, added mobile doc access as P1 critical friction point, consolidated Legacy AI initiatives |
| 2025-11-18 | Claude (Sonnet 4.5) | Added Success Criteria #6 (backlink migration), one-pager creation workflow, Notion database protection (DO NOT touch NOTION_ROADMAP_DB), correct env vars (STRATEGY_BOARD_DATABASE_ID), Notion setup instructions (Dharan creates page), Legacy AI one-pagers in separate repo |

---

**Status**: Complete
**What Shipped**:
- Phases 1-3 complete (templates, migration, Notion sync)
- Strategy Board aligned with ROADMAP.md
- Mobile Doc Access deferred to separate P2 initiative
