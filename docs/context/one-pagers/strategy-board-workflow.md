# ONE-PAGER: Strategy Board-Driven Workflow

**Initiative**: Strategy Board-Driven Workflow  
**Category**: Context Sync Bridge  
**Status**: 🟡 Needs Decision  
**Priority Score**: ~76-78 (Highest Priority)  
**Date Created**: 2025-11-09  

---

# Project Brief

## **Background**

You're currently the manual bridge between three disconnected systems (Claude Chat for strategy, Claude Code for implementation, and Notion Strategy Board for prioritization). Every session requires 10-15 minutes of context reloading, repeated copy-paste of decisions, and manual status updates. With your baby arriving in January 2026, you need automated workflows that preserve decision context and eliminate cognitive overhead.

The Context Sync Bridge (Phase 1) established git hooks and MCP tools, but the workflow still has manual gaps: no automated Strategy Board integration, no structured one-pager creation process, unclear handoffs between agents, and no signal for when implementation is complete.

This initiative closes those gaps by making Strategy Board the source of truth, automating handoffs with structured prompts, and creating a seamless flow from strategic decision → PRD → implementation → completion.

## **Problem Statements**

### **Problem 1 (Your perspective - strategic work):**
I am **Dharan, a solo founder building Epic 2nd Brain and Legacy AI**. I am trying to **move from strategic decisions to implemented features efficiently**. But **I manually bridge between Strategy Board, Claude Chat, and Claude Code** because **there's no automated workflow connecting prioritization → planning → implementation** which makes me feel **frustrated and cognitively drained from repetitive context-loading and status updates**.

### **Problem 2 (Notion Strategy Board perspective - source of truth):**
I am **the Strategy Board database in Notion**. I am trying to **serve as the single source of truth for what should be worked on and its current status**. But **no one reads from me automatically, and status updates are manual** because **there's no integration with Claude Chat or the git workflow** which makes me feel **like a static dashboard instead of a living system that drives action**.

### **Problem 3 (Claude Chat perspective - strategic agent):**
I am **Claude (Chat), the strategy agent**. I am trying to **help Dharan make high-quality strategic decisions and create clear PRDs**. But **I don't know what's in the Strategy Board, and I have no formal handoff mechanism to Claude Code** because **there's no integration between Notion and the MCP tools** which makes me feel **like I'm working blind and creating friction instead of flow**.

### **Problem 4 (Claude Code perspective - implementation agent):**
I am **Claude Code, the implementation agent**. I am trying to **translate PRDs into working code efficiently**. But **I don't get clear context on what to build or why it's prioritized** because **handoffs are manual and context is scattered across chat history** which makes me feel **like I'm guessing rather than executing with confidence**.

## **Goals**

### **Goal 1: Automated Context Loading from Strategy Board**
- **What success looks like**: When I say "Start session," Claude automatically queries Strategy Board, identifies top 3 initiatives by Priority Score (excluding completed/blocked), and presents them for selection. Context loads in <10 seconds with zero manual Notion lookups.

### **Goal 2: Structured One-Pager Creation**
- **What success looks like**: For any chosen initiative, Claude walks me through the Project Brief template interactively (background, problems, goals, vision), writes the one-pager directly to the initiative's Notion page content, and we can iterate until it's solid before moving to PRD.

### **Goal 3: Seamless Agent Handoffs with Clear Prompts**
- **What success looks like**: When I approve a PRD, Claude generates a handoff prompt for Claude Code (includes goals, documents to reference, context, git commit command), updates Strategy Board status to "In Progress," and Claude Code knows exactly what to do next without me explaining.

### **Goal 4: Implementation Completion Signal**
- **What success looks like**: When Claude Code finishes implementation, I say "Coding complete" and Claude loads the latest session log, summarizes what shipped, and updates Strategy Board with completion status and high-signal notes (blockers, dependencies, metrics, learnings - max 10 sentences).

### **Non Goals**

- **Full Notion PARA integration** - We're focusing on Strategy Board only, not searching across all Notion databases (deferred to later phase)
- **Multi-project filtering in Phase 1** - Start with Epic 2nd Brain only; add Legacy AI support after validation (will need project filter parameter)
- **RAG search** - Basic keyword search is sufficient for now; semantic search can wait
- **Calendar/email integration** - Not part of this workflow; deferred to separate initiatives
- **Custom mobile app** - Notion mobile is sufficient for viewing Strategy Board status

### **Hypothesis**

If we **automate Strategy Board → Claude Chat → Claude Code handoffs with structured one-pagers and clear prompts**, then **context loading drops from 10-15 min to <3 min, copy-paste events drop from 5-10 to <2 per session, and decision quality improves** leading to **70-120 min/week saved, zero "what changed?" moments, and foundation for multi-project expansion**.

**Size of win estimate**: 
- Time saved: 7-12 min per session × 10 sessions/week = **70-120 min/week** (1.2-2 hours)
- Cognitive load: **Massive reduction** - no more mental switching between systems
- Decision preservation: **100% of strategic decisions captured** in structured format
- Foundation value: **Enables all future initiatives** - this is Tier 0 infrastructure

## **Vision Narrative**

**Monday morning, 7:15 AM**. You grab coffee and open Claude Chat.

"Start session for Epic 2nd Brain."

Within seconds, I respond: "Good morning! I've queried your Strategy Board. Here are the top 3 initiatives by Priority Score:

1. **Strategy Board-Driven Workflow** (Priority: 76) - Status: Needs Decision
2. **Multi-Project Expansion** (Priority: 74.5) - Status: Ready to Build  
3. **Notion Command Center** (Priority: 65.3) - Status: Ready to Build

Which one should we tackle today?"

You reply: "Let's do Strategy Board-Driven Workflow."

I fetch the initiative page from Notion. It's blank - no one-pager exists yet. 

"This initiative doesn't have a one-pager yet. Let me walk you through creating one. First, let's establish the background..."

Over the next 20 minutes, we work through the Project Brief template together. I ask clarifying questions, you provide context, I draft sections, you refine them. The one-pager takes shape directly in the Notion page content - no copy-paste, no switching apps.

"Great! The one-pager is complete. Ready to move to PRD?"

"Yes."

I spend the next 30 minutes creating a comprehensive PRD, asking questions about trade-offs, documenting decisions, outlining phases. You review, we iterate, it's solid.

"I approve this PRD. Let's move to Claude Code."

Instantly, I:
- Create session log in `docs/sessions/claude-chat/2025-11-09-strategy-board-workflow.md`
- Generate handoff prompt in `docs/handoffs/2025-11-09-to-claude-code.md` with clear instructions, git commit command at top, context on what to build
- Update Strategy Board: "Strategy Board-Driven Workflow" status → "🚀 In Progress"

You see the confirmation: "Handoff complete. Strategy Board updated. Claude Code is ready - just paste the handoff prompt."

**Later that afternoon, 2:00 PM**. You open Claude Code.

You paste the handoff prompt. Claude Code responds:

"Got it! I can see we're building Strategy Board integration. I've read the PRD and have a few questions about the technical approach before I start coding:

1. For querying Strategy Board, should I use Notion Official MCP or build custom tools in ai-assistant MCP?
2. When writing one-pagers to Notion page content, what's the conflict resolution strategy if you edit manually?
3. For the handoff prompt format, should it be markdown in docs/handoffs/ or JSON with structured fields?

Let's align on these decisions first, then I'll create the technical requirements."

You discuss the approaches, Claude Code creates tech requirements, you approve, coding begins. 

**4:00 PM**. Claude Code finishes, runs tests, everything works.

Claude Code commits: `[STRATEGY-BOARD-WORKFLOW] [STATUS:Complete] Implemented Strategy Board integration - all tools working`

Git hook triggers → Notion updates session log.

**4:15 PM**. You come back to Claude Chat.

"Coding complete."

I immediately query for the latest Claude Code session log, parse it, and respond:

"Welcome back! Claude Code completed **Strategy Board-Driven Workflow** implementation. Here's what shipped:

**What Shipped:**
- 5 new MCP tools for Strategy Board integration
- One-pager workflow with interactive template filling  
- Handoff prompt generation system
- All tests passing

**Key Decisions:**
- Used Notion Official MCP for queries (faster than custom)
- One-pagers write directly to page content (no sync lag)
- Handoffs use markdown format (human-readable)

**Should I update Strategy Board to Complete with these notes?"

You review: "Yes, update it."

I update Strategy Board:
- Status: "✅ Complete"
- Completed Date: 2025-11-09
- Launch Notes: "Strategy Board integration working. Zero manual context loading. Handoffs automated. Ready for multi-project expansion."
- Decision Notes: "Notion Official MCP chosen for speed. Direct page content writes prevent sync issues."

"Done! Strategy Board updated. What's next - should we tackle Multi-Project Expansion now that this foundation is in place?"

**Total time spent on context management: <5 minutes across entire day**. The rest was pure strategic thinking and building.

## **Rough Scoping & Timeline**

### **V1 Scope (Phase 1: Foundation) - 6-8 hours**

**What's Included:**

1. **Strategy Board Integration** (2-3 hours)
   - Custom MCP tools: `query_strategy_board()`, `update_initiative_status()`, `write_to_page_content()`
   - Query logic: Filter by Status (exclude Complete/Blocked), sort by Priority Score DESC, return top 3
   - Update logic: Change status, write completion notes, update timestamps

2. **Updated `start_session()` Flow** (1 hour)
   - Remove tech requirements from context loading (not needed at session start)
   - Add Strategy Board query as first step
   - Present top 3 initiatives for user selection
   - Load roadmap + recent session logs for continuity

3. **One-Pager Workflow** (2-3 hours)
   - Interactive template filling (Project Brief sections)
   - Write directly to Notion initiative page content
   - Support for iterative refinement
   - Checkpoint before moving to PRD

4. **Handoff Automation** (1-2 hours)
   - Generate handoff prompt file: `docs/handoffs/[date]-to-claude-code.md`
   - Include: Goals, documents to reference, context, git commit command (first line)
   - Update Strategy Board status to "In Progress" via Notion API
   - Create session log in `docs/sessions/claude-chat/`

5. **Completion Workflow** (1 hour)
   - New tool or parameter: Load latest Claude Code session log
   - Parse: What Shipped, Decisions, Next Steps, Alerts
   - Update Strategy Board: Status → Complete, add Launch Notes + Decision Notes
   - Confirm with user before writing

**What's NOT Included in V1:**
- Multi-project support (filter by project) - add after validation with Epic 2nd Brain
- RAG search - basic search is sufficient
- Auto-commit from Claude Chat - git commit happens in Claude Code only
- Calendar/email integration - separate initiatives
- Full Notion PARA search - only Strategy Board for now

### **V2 Scope (Phase 2: Multi-Project) - 3-4 hours**

**What's Included:**
- Add `project_name` parameter to all tools
- Filter Strategy Board by project (Epic 2nd Brain vs Legacy AI)
- Support multiple roadmap files (`docs/context/roadmap-epic.md`, `docs/context/roadmap-legacy.md`)
- Cross-project initiative dependencies (if needed)

**Deferred to V2 because:**
- Need to validate V1 works smoothly with one project first
- Multi-project adds complexity (filtering, cross-references)
- You're primarily focused on Epic 2nd Brain in near term

### **V3+ Scope (Future Enhancements) - Tier 1+**

**What's Included:**
- RAG search across all docs (semantic, not just keyword)
- Notion PARA integration (search beyond Strategy Board)
- Calendar sync (meeting prep using context)
- Voice command integration ("Claude, what's blocking me?")
- Advanced visualizations (Gantt, timeline views)

### **Roll Out / Testing Plan**

#### **Phase 1: V1 Build & Test (Week 1)**

**Day 1-2: Strategy Board Integration (Claude Code)**
- Build 3 custom MCP tools
- Test with real Strategy Board database
- Validate query/update logic works
- **Validation**: Can query top 3, can update status

**Day 3: Start Session Flow (Claude Code)**  
- Modify existing `start_session()` tool
- Add Strategy Board query step
- Remove tech requirements loading
- **Validation**: Session starts with Strategy Board context in <10 sec

**Day 4-5: One-Pager Workflow (Claude Chat + Claude Code)**
- Implement interactive template filling (Claude Chat behavior)
- Build `write_to_page_content()` tool (Claude Code)
- Test with new initiative
- **Validation**: Can create one-pager in Notion page content

**Day 6: Handoff Automation (Claude Chat + Claude Code)**
- Build handoff prompt generation (Claude Chat)
- Build `update_initiative_status()` integration (Claude Code)
- Test full handoff flow
- **Validation**: PRD approval → Notion updated → prompt generated

**Day 7: Completion Workflow (Claude Chat + Claude Code)**
- Build session log parsing (Claude Chat)
- Build Strategy Board completion update (Claude Code)
- Test end-to-end
- **Validation**: "Coding complete" → summary → Notion updated

#### **Phase 2: Dogfooding (Week 2)**

**Use the system to build itself!**
- Use Strategy Board Workflow to prioritize next 3 initiatives
- Create one-pagers for those initiatives
- Track: Time saved, copy-paste events, "what changed?" moments
- Iterate on any friction points

**Success Metrics:**
- Context loading: <10 seconds (vs 10-15 min baseline)
- Copy-paste events: <2 per session (vs 5-10 baseline)
- Manual Notion updates: 0 (vs 3-5 per day baseline)
- Decision preservation: 100% captured in structured format

#### **Phase 3: Multi-Project Expansion (Week 3)**

**After V1 validation:**
- Add project filtering
- Test with Legacy AI initiatives
- Validate cross-project doesn't cause confusion

### **Platform Considerations**

**Mobile:**
- Strategy Board viewable via Notion mobile app ✅
- One-pagers readable in Notion mobile ✅
- PRDs readable in GitHub mobile or Notion sync ✅
- **No mobile-specific development needed**

**Entry Points:**
- Primary: Claude Desktop (for MCP tools)
- Secondary: Notion mobile (view-only)
- Tertiary: GitHub web (view PRDs/docs)

**Internationalization:**
- N/A - solo founder, English only

**User Onboarding:**
- Document workflow in README
- Create example one-pager as template
- Record video walkthrough (5 min) showing full flow
- **Onboarding effort: 1 hour**

### **Timeline Summary**

| Phase | Duration | What Gets Built | Who Builds |
|-------|----------|----------------|------------|
| **V1 Foundation** | 6-8 hours | Strategy Board integration, one-pager workflow, handoffs | Claude Code (tools), Claude Chat (behavior) |
| **Dogfooding** | 1 week | Use it to build next 3 initiatives, iterate on friction | You + Claude Chat + Claude Code |
| **V2 Multi-Project** | 3-4 hours | Project filtering, multiple roadmaps | Claude Code |
| **V3+ Future** | Tier 1+ | RAG search, PARA integration, calendar sync | TBD based on leverage |

**Total V1 Investment:** 6-8 hours  
**Expected Payback:** 70-120 min/week saved = **payback in 3-4 weeks**  
**Real Value:** Foundation for all future initiatives + preserved decision context

## **Key Trade-Offs & Decisions**

### **Decision 1: Strategy Board as Source of Truth (vs PRDs in Repo)**

**Context:** We need a single place that determines "what should we work on next?"

**Options Considered:**
- **Option A: Strategy Board in Notion (CHOSEN)**
  - ✅ Pro: Visual prioritization with calculated Priority Score
  - ✅ Pro: Mobile access for quick status checks
  - ✅ Pro: Already established and actively maintained
  - ✅ Pro: Rich properties (Impact, Urgency, Leverage, Time)
  - ❌ Con: Requires Notion API integration (adds complexity)
  - ❌ Con: Not version controlled (can't rollback priority changes)

- **Option B: Prioritization in Repo (markdown file)**
  - ✅ Pro: Version controlled
  - ❌ Con: No visual board view, no mobile access, would need to rebuild priority scoring

- **Option C: Dual system (Notion + Repo)**
  - ✅ Pro: Best of both worlds
  - ❌ Con: Sync complexity, defeats "single source of truth"

**Decision: Option A (Strategy Board in Notion)**

**Rationale:** You've already invested in Strategy Board with rich scoring system. Visual prioritization helps with morning ritual. Mobile access valuable. Notion API integration is one-time cost. Trade-off of no version control on priorities is acceptable - we care more about current state than historical priority changes.

**Impact:** All tools will query/update Strategy Board. Repo remains source of truth for *content* (PRDs, docs), but Notion is source of truth for *prioritization*.

### **Decision 2: One-Pager Location (Notion Page Content vs Repo)**

**Context:** Where should the one-pager live?

**Options Considered:**
- **Option A: Notion Page Content (CHOSEN)**
  - ✅ Pro: Keeps strategy docs with prioritization
  - ✅ Pro: You can edit directly in Notion
  - ✅ Pro: Mobile accessible
  - ❌ Con: Not version controlled

- **Option B: Repo (docs/one-pagers/) with sync to Notion**
  - ✅ Pro: Version controlled
  - ❌ Con: Sync complexity, risk of conflicts

- **Option C: Repo only (no Notion)**
  - ✅ Pro: Simple, version controlled
  - ❌ Con: Breaks "Strategy Board as source of truth" model

**Decision: Option A (Notion Page Content)**

**Rationale:** One-pagers are strategic documents that live upstream of PRDs. Keeping them in Notion maintains the flow: Strategy Board → One-Pager → PRD (repo). You already navigate Notion daily. Version control less critical for one-pagers (they stabilize quickly).

**Impact:** Claude writes one-pagers directly to Notion page content. PRDs still go to repo. Clear boundary: Strategy (Notion) vs Specification (Repo).

### **Decision 3: Handoff Mechanism (File vs Notion Comment vs Memory)**

**Context:** How does Claude Code know what to build?

**Options Considered:**
- **Option A: Handoff File in Repo (CHOSEN)**
  - ✅ Pro: Structured, version controlled, human-readable
  - ✅ Pro: Git commit command at top
  - ❌ Con: Requires manual paste to Claude Code

- **Option B: Notion Comment**
  - ✅ Pro: Keeps everything in Notion
  - ❌ Con: Not version controlled, hard to find later

- **Option C: Memory/Instructions File**
  - ✅ Pro: No manual handoff
  - ❌ Con: Limited memory, no approval checkpoint

- **Option D: Fully Automated**
  - ✅ Pro: Zero manual steps
  - ❌ Con: Not technically feasible, you lose control

**Decision: Option A (Handoff File)**

**Rationale:** Explicit handoff gives you control. Version controlled means you can see what was communicated. Git commit command at top ensures sync. Human-readable format means you can edit if needed. One paste action is acceptable friction.

**Impact:** `docs/handoffs/[date]-to-claude-code.md` files will accumulate as historical record of handoffs.

### **Decision 4: Strategy Board Update Timing (Before vs After Git Commit)**

**Context:** When should we update Strategy Board status to "In Progress"?

**Options Considered:**
- **Option A: Before Git Commit (CHOSEN)**
  - ✅ Pro: Strategy Board reflects intent immediately
  - ✅ Pro: Separates strategy update (Claude Chat) from implementation (Claude Code)
  - ❌ Con: If you abandon work, status stuck at "In Progress"

- **Option B: After Git Commit**
  - ✅ Pro: Status only changes when work begins
  - ❌ Con: Gap between PRD approval and status update

- **Option C: Manual**
  - ❌ Con: Defeats automation purpose

**Decision: Option A (Before Git Commit)**

**Rationale:** PRD approval IS the commitment to work on something. Strategy Board should reflect your intentions. If work is abandoned, you can manually revert (acceptable edge case). Keeps Claude Chat in charge of Strategy Board.

**Impact:** When you approve PRD, Strategy Board updates immediately.

### **Decision 5: Multi-Project Support Timing (V1 vs V2)**

**Context:** You have multiple projects. When should we add project filtering?

**Options Considered:**
- **Option A: Defer to V2 (CHOSEN)**
  - ✅ Pro: Simpler V1, faster to validate
  - ✅ Pro: Epic 2nd Brain is current focus
  - ❌ Con: Can't use system for Legacy AI in Week 1-2

- **Option B: Build in V1**
  - ✅ Pro: Future-proof from start
  - ❌ Con: Adds 2-3 hours to timeline, increases testing surface

- **Option C: Never (single project only)**
  - ❌ Con: Doesn't scale

**Decision: Option A (Defer to V2)**

**Rationale:** Epic 2nd Brain is 80% of current focus. Better to validate core workflow works smoothly before adding project dimension. 3-4 hour V2 investment is reasonable after V1 proven.

**Impact:** V1 will show ALL initiatives from Strategy Board (mixed projects). After V2, you'll be able to say "Start session for Legacy AI" and see only Legacy AI initiatives.

### **Decision 6: Claude Code Start Protocol (Explicit Instructions vs Memory)**

**Context:** How does Claude Code know to read handoff prompts?

**Options Considered:**
- **Option A: Explicit Instruction File (CHOSEN)**
  - ✅ Pro: Version controlled, can iterate on protocol
  - ✅ Pro: Serves as documentation
  - ❌ Con: Claude Code must remember to read it

- **Option B: Memory Only**
  - ✅ Pro: No extra files
  - ❌ Con: Memory might drift, not visible

- **Option C: Hybrid**
  - ✅ Pro: Redundancy
  - ❌ Con: Maintenance burden

**Decision: Option A with Memory Pointer (Hybrid Light)**

**Rationale:** Create `docs/instructions/claude-code-workflow.md` with clear protocol. Add to Claude Code memory: "Always read docs/instructions/claude-code-workflow.md when starting a session." Best practice: explicit runbooks > tribal knowledge.

**Impact:** New file to create, but minimal maintenance. Claude Code becomes more reliable and auditable.

### **Summary Table: Key Decisions**

| Decision | Chosen Approach | Key Trade-Off Accepted |
|----------|----------------|----------------------|
| Source of Truth | Strategy Board (Notion) | No version control on priorities |
| One-Pager Location | Notion page content | No version control on one-pagers |
| Handoff Mechanism | File in repo | Manual paste to Claude Code |
| Status Update Timing | Before git commit | Might show "In Progress" for paused work |
| Multi-Project Support | Defer to V2 | V1 shows all projects mixed |
| Claude Code Protocol | Instruction file + memory | Must maintain instruction file |

## **Concept Mocks**

### **Mock 1: Session Start Flow**

```
┌─────────────────────────────────────────────┐
│  YOU: "Start session for Epic 2nd Brain"   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  CLAUDE CHAT:                                │
│  1. Query Strategy Board                    │
│  2. Filter: NOT Complete, NOT Blocked       │
│  3. Sort by Priority Score DESC             │
│  4. Return top 3                            │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  CLAUDE presents top 3 initiatives          │
│  YOU selects one                            │
│  CLAUDE checks for one-pager                │
└─────────────────────────────────────────────┘
```

### **Mock 2: One-Pager Creation**

```
┌─────────────────────────────────────────────┐
│  CLAUDE walks through template:             │
│  - Background                               │
│  - Problem Statements (4 perspectives)      │
│  - Goals & Non-Goals                        │
│  - Vision Narrative                         │
│  - Scoping & Timeline                       │
│  - Trade-Offs & Decisions                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  CLAUDE writes to Notion page content       │
│  Checkpoint: "Ready for PRD?"               │
└─────────────────────────────────────────────┘
```

### **Mock 3: Handoff Flow**

```
┌─────────────────────────────────────────────┐
│  YOU: "I approve PRD"                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  CLAUDE creates:                             │
│  - Session log                              │
│  - Handoff prompt (with git commands)       │
│  - Updates Strategy Board → In Progress     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  YOU pastes handoff to Claude Code          │
└─────────────────────────────────────────────┘
```

### **Mock 4: Completion Flow**

```
┌─────────────────────────────────────────────┐
│  YOU: "Coding complete"                     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  CLAUDE loads Claude Code session log       │
│  CLAUDE presents summary                    │
│  CLAUDE updates Strategy Board → Complete   │
└─────────────────────────────────────────────┘
```

---

**One-Pager Status:** ✅ Complete  
**Next Step:** Create comprehensive PRD  
**Notion Page:** [Strategy Board-Driven Workflow](https://www.notion.so/2a68369c73058103be83c0d0f933f112)
