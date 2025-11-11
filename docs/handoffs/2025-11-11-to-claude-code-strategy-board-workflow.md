# Handoff to Claude Code: Strategy Board-Driven Workflow

**Date**: November 11, 2025  
**From**: Claude Chat (Sonnet 4.5)  
**To**: Claude Code  
**Project**: Epic 2nd Brain  
**Initiative**: Strategy Board-Driven Workflow

---

## 🚀 Git Commands - RUN THESE FIRST

```bash
# Navigate to repo
cd ~/Documents/1.\ Projects/ai-assistant/

# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/strategy-board-workflow

# Commit the PRD and session log
git add docs/prd/strategy-board-workflow.md
git add docs/sessions/claude-chat/2025-11-11-completed-strategy-board-drive.md
git add docs/handoffs/2025-11-11-to-claude-code-strategy-board-workflow.md
git commit -m "feat: Strategy Board-Driven Workflow PRD and handoff

- Complete PRD with interactive implementation mode
- Graceful degradation for Notion API failures
- Documentation update protocol
- Reviewed and refined with Dharan

Ref: Notion Strategy Board initiative"

# Push to remote
git push origin feature/strategy-board-workflow
```

---

## 🎯 Implementation Mode: INTERACTIVE

**CRITICAL**: This is an **interactive implementation**, not autonomous coding.

**Your protocol**:
1. Read the PRD thoroughly
2. Present **2-3 architectural options** for each major decision
3. **Wait for Dharan's choice** before proceeding
4. Only after alignment, create tech requirements
5. Only after tech requirements approved, start coding
6. After coding complete, **update documentation** (roadmap, tech req, implementation plan)

**Example dialogue we want**:
```
You: "For end_session query configuration, I see 3 options:
A) Hardcoded query in tool (simple, fast, inflexible)
B) Config file with query templates (flexible, needs file management)
C) Dynamic query builder based on parameters (most flexible, more complex)

Which approach aligns with your architecture vision?"

[Wait for Dharan's answer]

You: "Got it, Option A it is. For error handling when Notion API fails..."
```

---

## 📋 What to Build

**Goal**: Integrate Notion Strategy Board with Claude Chat and Claude Code, automating context loading, status updates, and handoff workflows.

**Success Criteria**:
- Context loading time < 10 seconds (from 10-15 min baseline)
- Zero manual Notion status updates
- Clear handoff prompts with git commands at top
- Graceful degradation when Notion API fails

**Timeline**: 6-8 hours implementation + 1 week dogfooding

---

## 📚 Documents to Reference

**Primary Documents**:
1. **PRD**: `docs/prd/strategy-board-workflow.md` (comprehensive spec with user stories)
2. **One-Pager**: Notion page at https://www.notion.so/2a68369c73058103be83c0d0f933f112 (currently blank - this is expected)
3. **Roadmap**: `docs/context/roadmap.md` (update this after implementation)

**Supporting Context**:
- **Notion Strategy Board Database**: https://www.notion.so/2a68369c7305802ebbe6c355a80d65e5
- **Context Sync Bridge PRD**: `docs/prd/context-sync-bridge.md` (Phase 1 foundation)
- **Existing MCP Server**: `mcp_server/server.py` (add 3 new tools here)
- **Git Hooks**: `scripts/sync_to_notion.py` (already working)

---

## 🔑 High-Level Context

**The Problem**:
Dharan manually bridges three disconnected systems:
1. Notion Strategy Board (priorities calculated, but no auto-query)
2. Claude Chat (strategy decisions, but no structured handoffs)
3. Claude Code (implementation, but no clear context on what/why to build)

This causes 10-15 min/session of manual context loading, 5-10 copy-paste events, and lost decisions.

**The Solution**:
Strategy Board becomes the automation driver:
- `start_session()` auto-queries Strategy Board → Top 3 initiatives
- Interactive one-pager creation (with Notion fallback to repo)
- PRD creation with links to repo files
- Handoff prompts with git commands at top
- Git hooks update Notion automatically
- Completion workflow parses session logs, updates Strategy Board

**Why This Matters**:
- Saves 70-120 min/week (7-12 min/session × 10 sessions/week)
- Baby arriving January 2026 (10 weeks to establish automation)
- Foundation for multi-project expansion (Legacy AI, future projects)

---

## 🛠️ Technical Components to Build

### **1. Three New MCP Tools** (add to `mcp_server/server.py`)

**Tool 1: `query_strategy_board()`**
- **Purpose**: Query Notion Strategy Board database, return top initiatives by Priority Score
- **Parameters**: 
  - `filter_status` (optional): exclude Complete/Blocked
  - `limit` (optional): default 3
  - `project_name` (optional): Epic 2nd Brain, Legacy AI (deferred to V2)
- **Returns**: List of initiatives with Name, Priority Score, Status, URL

**Tool 2: `update_initiative_status()`**
- **Purpose**: Update Status field and add notes to Decision Notes
- **Parameters**:
  - `page_id`: Notion page ID
  - `new_status`: one of ["🟡 Needs Decision", "🚀 In Progress", "✅ Complete", "🔴 Blocked"]
  - `decision_notes` (optional): append to existing notes
  - `launch_notes` (optional): summary of what shipped (for Complete status)
  - `completed_date` (optional): auto-set to today if Complete
- **Returns**: Confirmation of update

**Tool 3: `write_to_page_content()`**
- **Purpose**: Write markdown content to Notion page content (for one-pagers)
- **Parameters**:
  - `page_id`: Notion page ID
  - `content`: markdown string
  - `fallback_path` (optional): repo path to save if Notion fails
- **Returns**: Success confirmation OR fallback path if Notion failed
- **Error Handling**: Graceful degradation - try Notion first, save to repo if fails

### **2. Modify Existing `start_session()` Tool**

**Current behavior**: Loads PRDs, tech req, recent sessions, roadmap
**New behavior**: ALSO query Strategy Board first, present top 3 initiatives

**Changes needed**:
1. Call `query_strategy_board()` at start
2. Format results: "Top 3 Initiatives by Priority:\n1. [Name] (Score: X, Status: Y)\n2. ..."
3. Keep existing loading of PRDs/sessions/roadmap

### **3. Modify Existing `end_session()` Tool**

**Current behavior**: Creates session log
**New behavior**: ALSO create handoff prompt in `docs/handoffs/`

**Handoff prompt structure**:
```markdown
# Handoff to Claude Code: [Initiative Name]

## 🚀 Git Commands - RUN THESE FIRST
[git commands]

## 🎯 Implementation Mode: INTERACTIVE

## 📋 What to Build
[goals, success criteria]

## 📚 Documents to Reference
[PRD path, one-pager location (Notion URL or repo path)]

## 🔑 High-Level Context
[why this matters]

## ❓ Clarifying Questions Before You Code
[3-5 questions about architecture, error handling, testing]
```

### **4. Create Instruction File** (first handoff only)

**File**: `docs/instructions/claude-code-workflow.md`

**Content sources**: 
- Your existing rules/memory about git workflow
- Your existing rules/memory about testing strategy
- Your existing rules/memory about documentation updates
- This specific workflow's end-session protocol

**Sections to include**:
1. Git workflow (branch naming, commit message format)
2. Testing strategy (when to test, what to test)
3. Documentation updates (roadmap, tech req, implementation plan)
4. End-session protocol (commit → update docs → create session log)

---

## ❓ Clarifying Questions Before You Code

**Before creating tech requirements, ask Dharan these questions:**

### **1. Tool Configurability**
**Question**: "For `query_strategy_board()`, should the query filters be:
- A) Hardcoded (e.g., always exclude Complete/Blocked, always top 3)
- B) Configurable via parameters (more flexible, but more complex API)
- C) Mix: Hardcoded defaults, but parameters can override

Which aligns with your vision for this system?"

**Why this matters**: Affects tool complexity, testing surface area, and future extensibility.

---

### **2. Notion API Error Handling Strategy**
**Question**: "When Notion API fails (for any of the 3 tools), should I:
- A) Retry with exponential backoff (standard practice, adds complexity)
- B) Fail immediately with clear error message (simple, predictable)
- C) Graceful degradation where possible (e.g., write_to_page_content falls back to repo)

For tools where fallback isn't possible (query, update), A or B?"

**Why this matters**: Affects reliability vs simplicity trade-off, impacts user experience during failures.

---

### **3. Testing Strategy**
**Question**: "For testing these Notion tools, should I:
- A) Test with real Notion Strategy Board (requires Notion token in tests, slower)
- B) Mock Notion API responses (faster, but doesn't catch real API issues)
- C) Mix: Unit tests with mocks, integration tests with real Notion (flag for manual runs)

Which approach do you prefer?"

**Why this matters**: Affects test reliability, execution speed, and CI/CD pipeline design.

---

### **4. Git Hook Dependencies**
**Question**: "The PRD assumes git hooks (`scripts/sync_to_notion.py`) already update Notion after commits. Should I:
- A) Assume hooks work perfectly, no additional sync logic needed
- B) Add explicit sync verification in tools (e.g., read-after-write checks)
- C) Build tool-based sync independent of hooks (redundant, but more reliable)

Which assumption is safer for V1?"

**Why this matters**: Affects separation of concerns, debugging complexity, and system reliability.

---

### **5. One-Pager Location Tracking**
**Question**: "When one-pager fallback to repo happens, how should I track the location for handoff prompt:
- A) Store in tool response, Claude Chat remembers during session
- B) Write location to a metadata file (e.g., `.one-pager-locations.json`)
- C) Always check both locations (Notion + repo) and use whichever exists

Which approach is simplest and most reliable?"

**Why this matters**: Affects session state management and error recovery.

---

### **6. Documentation Update Timing**
**Question**: "For documentation updates (roadmap, tech req, implementation plan), should I update:
- A) Before commit (ensures git contains latest state)
- B) After commit (commit triggers hooks first, then update docs)
- C) Separate commit just for docs (cleaner git history)

Which timing aligns with your git workflow preferences?"

**Why this matters**: Affects commit atomicity and git history clarity.

---

## 🎯 After You Answer These Questions

1. I'll create comprehensive tech requirements document
2. You review/approve tech requirements
3. I implement the 3 new tools + modifications to existing tools
4. I update documentation (roadmap, tech req, implementation plan)
5. I commit changes with proper git message
6. Git hooks auto-update Notion Strategy Board
7. I create session log documenting what shipped

---

## 📝 Notes from Claude Chat

**Key Architectural Decisions Made**:
1. Strategy Board is source of truth for priorities (not repo)
2. One-pagers in Notion page content with graceful degradation to repo
3. PRDs in repo (version controlled)
4. Handoff prompts in repo (historical record)
5. Interactive implementation mode (not autonomous)
6. Documentation updates are Claude Code's responsibility

**Open Issues**:
1. Notion Page Content API reliability - test during implementation, measure failure rate

**Success Metrics**:
- Context loading < 10 sec
- Copy-paste events < 2 per session
- Zero manual Notion updates
- 100% decision preservation

---

## 🚦 Ready When You Are

Once you've run the git commands at the top and asked your clarifying questions, we'll align on the technical approach and get started!

**Remember**: Interactive mode means presenting options and waiting for Dharan's choice. Don't make architectural decisions autonomously.

Good luck! 🚀

---

**End of Handoff Prompt**
