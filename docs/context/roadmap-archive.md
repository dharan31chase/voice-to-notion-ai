# Epic 2nd Brain: Tier 0 Roadmap

**ARCHIVED**: 2025-11-18
**Reason**: Replaced by unified `/ROADMAP.md` at repo root
**See**: [/ROADMAP.md](../../../ROADMAP.md) for current roadmap

---

**Timeline**: Nov 8-22, 2025 (2 weeks)
**Status**: Phase 3 - Multi-Project Expansion (✅ Complete) | Phase 4 - Notion Command Center (Next)
**Last Updated**: Nov 13, 2025

---

## 🎯 Mission: Context Sync Bridge

**The Problem**: You're the manual bridge between three disconnected systems (Claude chat, Claude Code, Notion), causing:
- Context loss between sessions (10-15 min/session spent reloading context)
- Repeated copy-paste of requirements/decisions (5-10 events/session)
- No single source of truth for project status
- Manual documentation updates that don't flow bidirectionally

**The Vision**: World-class product development framework at solo founder scale
- Claude (chat) = Strategic decisions, PRDs (write permission)
- Claude Code = Technical implementation, requirements (write permission)
- Notion = Command center with visual dashboard (read-only, synced from repo)
- Git/GitHub = Single source of truth (version controlled, cloud backed up)
- Automated handoffs via structured documentation

**The Leverage**: 70-120 min/week saved + cognitive load reduction + decision history preservation

---

## 📅 Phase Overview

### **Phase 1: MCP PoC + Templates** ✅ COMPLETE
**Completed**: Nov 8, 2025 (4 hours actual vs 6-8 estimated - ahead of schedule!)
**What Shipped**:
- MCP server with 5 core tools (read_file, write_file, start_session, end_session, search_docs)
- Template system (PRD, tech requirements, session logs, architecture diagrams)
- Proof of concept validated: Context loading works

**Tech Requirements**: [mcp-poc-and-templates.md](../tech-requirements/mcp-poc-and-templates.md)

---

### **Phase 2: Strategy Board Workflow** ✅ COMPLETE
**Completed**: Nov 11, 2025
**What Shipped**:
- 3 new MCP tools (query_strategy_board, update_initiative_status, write_to_page_content)
- 2 enhanced tools (start_session with Strategy Board query, end_session with status updates)
- Git hooks for automatic Notion sync
- Strategy Board-driven workflow validated

**Tech Requirements**: [strategy-board-workflow.md](../tech-requirements/strategy-board-workflow.md)
**Session Log**: [2025-11-11-completed-strategy-board-drive.md](../sessions/claude-chat/2025-11-11-completed-strategy-board-drive.md)

---

### **Phase 3: Multi-Project Expansion** ✅ COMPLETE
**Started**: Nov 11, 2025 (Session 2A)
**Completed**: Nov 13, 2025 (Session 2B)
**Actual Time**: 3.5-4.5 hours (under 6-8 hour estimate)

**What This Unlocked**:
- Legacy AI (business) gets same infrastructure as Epic 2nd Brain
- Clean IP separation (co-founder ready, investor ready)
- Professional repo structure from day 1
- Foundation for Life Admin, Baby Prep, Project Franklin, etc.

**Implementation Status**:
- ✅ Session 2A: PRD + Handoff + Test Suite complete (Nov 12)
- ✅ Session 2B: Implementation + Validation complete (Nov 13)
  - Multi-project MCP tools (read_file, search_docs, start_session)
  - Git hooks configured for both repos
  - Automated test suite (7/8 tests passed)
  - Performance: All operations < 5s (goal: < 10s)
  - Strategy Board filtered views verified
- ✅ All 5 success criteria met
- ✅ Session 2C: Task Title Generation Debug + Fix complete (Nov 13) - See Bug Fixes section
- ⬜ Session 3: Real Legacy AI usage (customer discovery) - Ready to start

**Detailed Roadmap**: See [roadmap-addendum-multi-project.md](roadmap-addendum-multi-project.md) for:
- Day-by-day execution plan (Phases 1-5)
- Deferred features (mobile access, specialized tools, etc.)
- Risk management
- Success milestones

**Documentation**:
- PRD: [multi-project-expansion.md](../prd/multi-project-expansion.md)
- Test Results: [multi-project-test-results.md](test-scenarios/multi-project-test-results.md)
- Session Logs:
  - [2025-11-12-completed-session-2a-multi-pr.md](../sessions/claude-chat/2025-11-12-completed-session-2a-multi-pr.md) (Session 2A)
  - [2025-11-13-multi-project-expansion-validation.md](../sessions/claude-code/2025-11-13-multi-project-expansion-validation.md) (Session 2B)

---

### **Phase 4: Notion Command Center Dashboard** ⬜ NOT STARTED
**Target**: Week 2 (Nov 15-22)
**Estimated**: 6-8 hours
**Dependencies**: Phase 3 complete, real usage validated

**What This Builds**:
- Visual dashboard in Notion (board/table/timeline views)
- Mobile-accessible roadmap and project status
- Integration with existing PARA system
- Quick health checks (what's blocked? what's next?)

**Deferred Decisions**:
- Dashboard structure (after real multi-project usage)
- Which views are most valuable (after Session 3)

**Tech Requirements**: [To be created after Phase 3]

---

### **Phase 5: Enhanced Capabilities** ⬜ NOT STARTED
**Target**: Week 2-3 (Nov 15-29)
**Estimated**: 8-12 hours total
**Dependencies**: Phase 3 validated, usage patterns clear

**Sub-Phases**:

#### **5A: Mobile Doc Access** (6-8 hours)
**What**: Markdown → Notion sync for PRDs, Vision docs, Roadmaps
**Why**: Review docs on phone during interviews, commutes, etc.
**Priority**: High (immediate friction point identified in Session 2A)
**Implementation**: Git hook enhancement (selective sync, not all docs)

#### **5B: Template Enhancements** (3-4 hours)
**What**: Add frameworks to Customer Interview Analysis template
**When**: After 10-15 interviews (pattern emerges)
**Frameworks**: 7 Powers, Michael Porter 5 Forces, Value Prop Canvas
**Priority**: Medium (current template works, this makes it better)

#### **5C: Specialized MCP Tools** (4-6 hours)
**What**: Legacy AI-specific automation
**Tools**:
- `analyze_interview()` - Auto-extract Jobs-to-be-done insights
- `compare_interviews()` - Cross-interview pattern detection
- `generate_validation_questions()` - For prototype testing
**Priority**: Medium (nice-to-have, not blocking)

**Tech Requirements**: [To be created after Phase 3 usage patterns emerge]

#### **5D: Refactor MCP Server to Modular Architecture** (2-3 hours)
**What**: Extract context loading, session management, and project management into separate modules following Single Responsibility Principle (SRP)
**Target Structure**:
```
mcp_server/
  full_server.py              # Main entry point (routing only)
  tools/
    __init__.py
    session_manager.py        # start_session, end_session
    context_loader.py         # Profile management
    project_manager.py        # Project path mapping
  utils/
    file_discovery.py         # Folder scanning
    profile_storage.py        # JSON persistence
    input_parser.py           # User input parsing
  config/
    project_paths.json
```
**Why**: Current Phase 1 implementation in `full_server.py` is fast to ship but will become unmaintainable as MCP server grows. Modular architecture enables adding 10+ tools without bloat.
**Triggers**:
- When `full_server.py` exceeds 1000 lines, OR
- When adding 3rd MCP tool, OR
- When adding cross-tool shared utilities
**Priority**: Medium (critical for long-term maintainability, not immediate)
**Dependencies**: Context Profile Optimization (Phase 1 complete)

**Tech Requirements**: Documented in [context-profile-optimization.md](../tech-requirements/context-profile-optimization.md)

---

### **Phase 6: Testing & Documentation** ⬜ NOT STARTED
**Target**: Week 2 end (Nov 20-22)
**Estimated**: 3-4 hours
**Dependencies**: Phases 3-5 complete

**What This Covers**:
- Comprehensive test suite (already drafted in Phase 3)
- Documentation polish (README updates, CONTRIBUTING guides)
- Performance validation (all metrics under target)
- Handoff prep for future collaborators

**Success Criteria**:
- All 5 test scenarios pass (see Phase 3 test suite)
- Peter can onboard from docs alone (no 1:1 briefing needed)
- Context loading <10 seconds for all projects
- Git hooks sync in <5 seconds

**Tech Requirements**: [To be created in Week 2]

---

## 📋 PRD Backlog (Approved, Not Yet Started)

**Purpose**: Track PRDs from conception through completion. Both Claude agents update status.

| PRD | Status | Priority | Effort | Dependencies | Notes |
|-----|--------|----------|--------|--------------|-------|
| [Context Profile Optimization](../prd/context-profile-optimization.md) | 🚀 In Progress | High | 6-7h | None | Implementation complete, validating with real usage |

**Status Definitions**:
- `Draft` - Claude (chat) creating PRD
- `Ready for Tech Requirements` - PRD approved, needs technical spec
- `Approved for Implementation` - Tech requirements approved, ready to build
- `In Progress` - Claude Code actively implementing
- `Complete` - Feature shipped, documented, tested

**How to Use**:
- Claude (chat): Creates PRD → marks "Ready for Tech Requirements" → marks "Approved for Implementation"
- Claude Code: Marks "In Progress" when starting → marks "Complete" when done
- User: Reviews at start of each session to decide what to work on

---

## 🎯 Success Metrics (Overall Tier 0)

### **Time Savings**:
- **Baseline**: 10-15 min/session context loading + 5-10 copy-paste events
- **Target**: <3 min context loading + <2 copy-paste events
- **Actual** (to be measured in Session 3): ___

### **Context Quality**:
- **Baseline**: 3-5 "What changed?" moments per week
- **Target**: 0 per week (full decision history searchable)
- **Actual** (to be measured after Week 1): ___

### **Documentation Lag**:
- **Baseline**: 1-3 days between work done and Notion updated
- **Target**: <1 hour (automated sync)
- **Actual** (Phase 2 complete): <5 seconds ✅

### **Scalability**:
- **Target**: System works for 5-10 projects without degradation
- **Actual** (Phase 3 in progress): Testing with 2 projects

---

## 🚧 Known Blockers & Risks

### **Active Blockers**:
1. ⬜ **Session 2B Implementation** - 6-8 hours of work needed
   - **Impact**: Blocks real Legacy AI usage (Session 3)
   - **Resolution**: Starting today (Nov 12)

### **Upcoming Risks**:
1. **Baby arrives early** (Low probability, High impact)
   - **Mitigation**: Front-load Phase 3 this week
   - **Contingency**: Phases 4-6 can be deferred

2. **MCP tools break existing workflow** (Low probability, High impact)
   - **Mitigation**: Comprehensive test suite in Phase 3
   - **Contingency**: Git rollback (all changes versioned)

3. **Customer discovery takes longer than expected** (Medium probability, Medium impact)
   - **Mitigation**: Focus on template quality, not automation
   - **Contingency**: Peter can help synthesize insights when he joins

---

## 🐛 Bug Fixes & Maintenance

### **Task Title Generation Quality** ✅ FIXED (Nov 13, 2025)
**Problem**: AI generating useless task titles like "Identify Key Phrases in Text Analysis Project" instead of describing the actual task

**Root Causes**:
1. Only using first 200 chars (often transcription garbage: K1-X markers, foreign language)
2. No explicit examples of good vs bad titles in prompt
3. No anti-patterns to avoid meta-descriptions
4. Generic "Verb + Object + Context" pattern without examples

**Solution Implemented**:
- Increased excerpt from 200→600 chars (3x more context)
- Added `_clean_excerpt_for_title()` to remove transcription garbage
- Added explicit GOOD/BAD examples in prompt
- Added anti-patterns (avoid meta-talk like "Identify...", "Verify...")
- Lowered temperature from default to 0.3 for consistency
- Added 3 helper methods: `_clean_excerpt_for_title()`, `_is_likely_garbage()`, `_has_english_content()`

**Test Results**: 2/3 test cases excellent (67%), 1/3 acceptable (33%)
- Before: All 3 test cases had problematic titles
- After: 2 perfect titles, 1 acceptable (picked secondary topic in multi-topic transcript)

**Files Changed**:
- `parsers/content_parser.py` (+164, -57)
- `scripts/notion/task_creator.py` (-20) - Removed AI analysis metadata clutter

**Git Commits**: 80656c7, c8f374d
**Session Log**: [2025-11-13-improved-task-title-generation.md](../sessions/claude-code/2025-11-13-improved-task-title-generation.md)

---

### **Notion Sync Character Limit** ✅ FIXED (Nov 13, 2025)
**Problem**: Detailed commit messages (>2000 chars) failing to sync to Notion Sessions DB due to "What Shipped" property limit

**Root Cause**: Hard 2000 char limit on Notion rich text properties

**Solution Implemented**:
- Smart truncation preserving structure: title + body summary + GitHub link footer
- Cuts at line boundaries (cleaner than mid-sentence)
- Default max 1950 chars (50 char buffer for safety)
- Method: `_truncate_commit_message()` in `scripts/sync_to_notion.py`

**Test Results**:
- Short messages (<1950 chars): Pass through unchanged ✅
- Long messages (2117 chars): Truncated to 1921 chars ✅
- This commit itself synced successfully (proof it works!) ✅

**Files Changed**:
- `scripts/sync_to_notion.py` (+36, -1)

**Git Commit**: c8f374d
**Session Log**: Same as above

---

## 🗺️ Next Phases (Post-Tier 0)

### **Tier 1: Expansion & Polish** (Weeks 3-4)
- Notion PARA integration (full workspace search)
- Calendar intelligence (meetings → session blocks)
- Advanced visualizations (Gantt charts, timeline views)

### **Tier 2: Automation & Scale** (Weeks 5-8)
- Email pipeline (feedback → roadmap items)
- Voice command integration ("Claude, what's blocking me?")
- Automated interview transcription at scale

### **Tier 3: Team & Collaboration** (Weeks 9-12)
- Multi-user collaboration features (when Peter joins + future hires)
- Permissions and roles
- Review workflows

---

## 📊 Phase 3 Detailed Timeline (Current Focus)

For detailed day-by-day execution plan, see: [roadmap-addendum-multi-project.md](roadmap-addendum-multi-project.md)

**Quick Summary**:
- **Phase 3.1**: Foundation (Session 2B - 6-8 hours)
  - Create legacy-ai/ repo, update MCP tools, migrate 5 docs
- **Phase 3.2**: Real Usage Validation (Session 3 - Week of Nov 11)
  - Uncle Bob interview analysis, end-to-end workflow test
- **Phase 3.3**: Template Enhancement (Week 3-4)
  - Add frameworks after 10-15 interviews
- **Phase 3.4**: Specialized Tools (Week 2-4)
  - Build Legacy AI-specific MCP tools
- **Phase 3.5**: Collaboration Prep (Week 4-6)
  - Peter onboarding, legal setup, engineering work stream

---

## 🎓 Meta-Learning: Systems Thinking Applied

**This roadmap demonstrates leverage point #9 (Delays):**
- Phases 1-2: Tight feedback loop (implementation → usage immediately)
- Phase 3: Intentional delay (wait for real usage before optimization)
- Phases 4-6: Data-driven iteration (build what's needed, not what's cool)

**Feedback loops designed in:**
- **R1**: Template Improvement (better template → better insights → better interviews)
- **B1**: Time Management (baby deadline → ruthless prioritization → sufficient capability)
- **B2**: Context Freshness (staleness → session start → fetch latest → updated context)

**This is systems thinking in practice**: Structure determines behavior, not willpower.

---

## 📝 Change Log

| Date | Change | Impact |
|------|--------|--------|
| 2025-11-08 | Phase 1 complete (4 hours, ahead of schedule) | Context loading validated |
| 2025-11-11 | Phase 2 complete (Strategy Board workflow) | Git hooks + Notion sync operational |
| 2025-11-11 | Phase 3 Session 2A complete (PRD + handoff) | Ready for implementation |
| 2025-11-12 | Added roadmap addendum link for Phase 3 details | Clarified relationship between main roadmap and initiative-specific roadmaps |

---

**Last Updated**: 2025-11-12
**Next Update**: After Phase 3 Session 2B complete (implementation)
**Owner**: Dharan Chandra Hasan
