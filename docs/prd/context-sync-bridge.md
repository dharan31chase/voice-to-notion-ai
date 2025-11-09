# PRD: Context Sync Bridge - Epic 2nd Brain Tier 0

**Status**: Approved
**Owner**: Dharan Chandra Hasan
**Last Updated**: 2025-11-08
**Tech Requirements**: [Link to tech-requirements/context-sync-bridge-*.md (will be created per phase)]

---

## 🎯 TL;DR

Build an automated context sync system that eliminates the 10-15 minutes per session you currently spend manually bridging between Claude (strategy), Claude Code (implementation), and Notion (dashboard), saving 70-120 minutes per week while preserving decision context and preventing rework - **designed to scale across multiple projects** (Epic 2nd Brain, Legacy AI, and future work).

---

## 🎯 Problem Statement

**User Pain Point**:

You're currently the manual bridge between three disconnected systems, causing massive cognitive drain and time loss:

- **Claude (chat)**: Where you make strategic decisions and write PRDs
- **Claude Code**: Where technical implementation happens
- **Notion**: Where you track project status and review work

Every session requires:
- 10-15 minutes reloading context (reading past conversations, checking Notion, finding decisions)
- 5-10 copy-paste events per session (requirements, decisions, status updates)
- 3-5 "What changed?" moments per week (losing track of what was decided)
- 1-3 day lag in documentation updates (manual Notion updates you keep forgetting)

**The structural problem:** No single source of truth. Information exists in three places, none of them synchronized. You're spending cognitive energy on **translation** instead of **creation**.

**Current Workaround**:

You manually:
1. Read previous Claude chat conversations to reload context
2. Copy-paste requirements from Claude to Claude Code
3. Copy-paste what shipped from Claude Code to Notion
4. Search through chat history to find "when did we decide X?"
5. Update Notion roadmap manually (when you remember)

This works, but it's painful. And with your baby arriving January 2026, you won't have time for this manual overhead.

**Why Now**:

Three converging factors make this the right time:

1. **Baby deadline (January 2026)**: You have 10 weeks to establish foundational systems before your available time plummets. This is a **Tier 0 leverage point** - everything else depends on it working.

2. **MCP just became available**: Anthropic's Model Context Protocol launched in 2024, making automated context loading technically feasible. You validated it works on Day 1.

3. **Voice-to-Notion pipeline success**: You've already proven you can build automation that amplifies (not replaces) your authentic voice. You saved 15-30 min/day there - this is the next system.

---

## 🔧 High-Level Approach

**Strategy**: Hybrid architecture with Git/GitHub as single source of truth

Think of this like organizing a shared kitchen:
- **Git/GitHub** = The pantry (source of truth, everything stored here)
- **Notion** = The menu board (visual dashboard that reads FROM the pantry)
- **MCP** = The chef's assistant (automatically grabs ingredients when you start cooking)
- **Git hooks** = The inventory system (automatically updates the menu board when pantry changes)

**The flow:**
1. You (via Claude) write strategic decisions in markdown files → saved to Git
2. Claude Code writes technical implementations in markdown files → saved to Git  
3. Every commit automatically pushes to GitHub (cloud backup, survives coffee spills)
4. Git hooks automatically update Notion dashboard (you see status without manual updates)
5. MCP tools automatically load context when you start a session (no more 10-15 min reload time)

**Why This Approach**:

- **Git/GitHub as source of truth**: Version-controlled docs with rollback capability. If you break something, revert to last working state. If your laptop dies, everything's in the cloud.
  
- **Notion as dashboard (not source)**: Your PARA system mixes personal life + IP-sensitive work content. Keeping project docs separate in Git means you can share with future collaborators without exposing personal notes. Notion becomes a read-only view for visual status and mobile access.

- **MCP for automation**: Proven on Day 1 - Claude can now read files directly from your repo. This eliminates copy-paste and enables auto-context loading.

**Alternatives Considered**:

**Alternative A: Pure Notion (everything in Notion databases)**
- Why not: Notion isn't built for developer workflows. No version control means no rollback if you break something. Mixing IP-sensitive docs with personal PARA creates collaboration friction. Would require rebuilding your entire voice-to-Notion pipeline.

**Alternative B: Pure Git (no Notion, CLI-only)**  
- Why not: You've invested heavily in Notion PARA. The visual dashboard and mobile access are valuable for morning ritual and on-the-go status checks. Git alone has no visual status board.

**Alternative C: Separate wikis/tools per project**
- Why not: Context fragmentation gets worse, not better. You'd have even MORE places to check and sync.

---

## ✅ Success Criteria

**Must Have** (Launch blockers):

1. **Context loading time < 3 minutes** (from current 10-15 min)
   - Measurement: Time from "start session" to "ready to work"
   - Baseline: 10-15 min (manual reading of past chats)
   - Target: <3 min (MCP auto-loads context)

2. **Copy-paste events < 2 per session** (from current 5-10)
   - Measurement: Manual count during sessions
   - Baseline: 5-10 copy-paste events
   - Target: <2 (only edge cases)

3. **"What changed?" moments = 0 per week** (from current 3-5)
   - Measurement: Self-reported confusion about decisions
   - Baseline: 3-5 times/week asking "wait, what did we decide?"
   - Target: 0 (full decision history searchable)

4. **Documentation lag < 1 hour** (from current 1-3 days)
   - Measurement: Time between commit and Notion update
   - Baseline: 1-3 days (manual updates when you remember)
   - Target: <1 hour (automated sync via git hooks)

**Nice to Have** (Post-launch):

1. **Mobile access to roadmap status** (Notion mobile app)
2. **Search across all project docs in <2 seconds** (RAG search)
3. **Session logs automatically created** (no manual documentation)

**Metrics**:

- **Time saved per session**: 10-15 min → 3 min = **7-12 min saved per session**
- **Sessions per week**: ~10 
- **Total time saved**: **70-120 min/week (1.2-2 hours/week)**
- **Setup time investment**: 30-40 hours (Tier 0 complete)
- **Payback period**: 15-30 weeks
- **Real leverage beyond time**: Reduced cognitive load (priceless), preserved decision context (prevents rework), foundation for 100,000X workflows

**2x Leverage Validation**: If you're not saving at least 50% of context loading time by Week 2, the system hasn't achieved its goal.

---

## 🚫 Non-Goals

1. **Notion PARA integration (full workspace search)**
   - Why: 90% of queries are about current project, not old notes from your PARA archive
   - PARITY estimate if we did it: 15-20 hours (semantic search across all Notion)
   - Deferred to: Tier 1 (Weeks 3-4)

2. **Calendar sync (meetings → session blocks)**
   - Why: Not critical path for context sync, adds complexity
   - PARITY estimate if we did it: 12-16 hours
   - Deferred to: Tier 2 (Weeks 5-8)

3. **Email pipeline (feedback → roadmap items)**
   - Why: Email isn't primary input for your workflow
   - PARITY estimate if we did it: 10-12 hours
   - Deferred to: Tier 2 (Weeks 5-8)

4. **Voice command integration** ("Claude, what's blocking me?")
   - Why: Voice-to-Notion already handles voice input, this is polish
   - PARITY estimate if we did it: 8-10 hours
   - Deferred to: Tier 2 (Weeks 5-8)

5. **Multi-user collaboration features**
   - Why: You're solo founder, hiring isn't imminent
   - PARITY estimate if we did it: 40+ hours (permissions, roles, etc.)
   - Deferred to: Tier 3 (Weeks 9-12)

6. **Custom mobile app**
   - Why: Notion mobile is sufficient for dashboard access
   - PARITY estimate if we did it: 40-60 hours (native app development)
   - Deferred to: Tier 3+ (not planned)

7. **Advanced visualizations (Gantt charts, timeline views)**
   - Why: Simple board/table views are sufficient for Tier 0
   - PARITY estimate if we did it: 8-12 hours
   - Deferred to: Tier 1 (Weeks 3-4)

8. **Legacy AI-specific features in Tier 0**
   - Why: Focus on proving the infrastructure works for ONE project first (Epic 2nd Brain)
   - Customer discovery notes in Notion will be accessible in Tier 1 (Notion PARA integration)
   - PARITY estimate if we did it now: Would delay Tier 0 by 1-2 weeks
   - Approach: Build infrastructure for Epic 2nd Brain, expand to Legacy AI in Tier 1

**Scope protection**: With baby arriving January 2026, these non-goals aren't just deferred - they're actively rejected for Tier 0 to protect the 2-week timeline.

---

## 👥 User Stories

### Story 1: Fast Context Reload (Multi-Project)

**As Dharan** (founder),  
**I want** Claude to automatically load all relevant project context when I start a session **for any project I'm working on**,  
**So that** I can jump straight into strategic thinking for Epic 2nd Brain, Legacy AI, or future projects without spending 10-15 minutes reconstructing context.

**Acceptance Criteria**:
- [ ] Saying "Start session for Epic 2nd Brain" loads: latest PRD, tech requirements, session logs, roadmap, alerts **for that project**
- [ ] Saying "Start session for Legacy AI" loads: customer discovery notes, design frameworks, prototype status **for that project**
- [ ] Context loading completes in <10 seconds regardless of project
- [ ] Claude can answer "What did we decide about X?" filtered by project
- [ ] System scales to 5-10 active projects without degrading performance

---

### Story 2: Seamless Agent Handoffs

**As Claude** (strategy agent),  
**I want** to write strategic decisions to structured docs that Claude Code can automatically read,  
**So that** implementation begins from correct requirements without manual copy-paste.

**Acceptance Criteria**:
- [ ] When I write a PRD, it's saved to `docs/prd/[feature].md`
- [ ] Claude Code can read the PRD directly (no copy-paste by Dharan)
- [ ] My strategic decisions are preserved in version control for future reference
- [ ] I can update PRDs and Claude Code sees the changes immediately

---

### Story 3: Automated Session Documentation

**As Claude Code** (implementation agent),  
**I want** to log what I shipped, decisions made, and next steps in a structured format,  
**So that** Dharan and Claude (chat) have complete context for the next session.

**Acceptance Criteria**:
- [ ] When I finish work, I create a session log at `docs/sessions/claude-code/[date]-[topic].md`
- [ ] Session log includes: what shipped, architecture decisions, roadmap updates, next steps, critical alerts
- [ ] Log is automatically pushed to GitHub (cloud backup)
- [ ] Log is automatically synced to Notion (Dharan sees it in dashboard)

---

### Story 4: No More "What Changed?" Moments (Multi-Project)

**As Dharan** (founder),  
**I want** to search across all project docs **across multiple projects** to find decisions instantly,  
**So that** I never lose track of "when did we decide X?" whether it's about Epic 2nd Brain architecture, Legacy AI customer feedback, or any other project.

**Acceptance Criteria**:
- [ ] I can ask Claude "What did we decide about MCP server architecture?" (Epic 2nd Brain context)
- [ ] I can ask Claude "What pain points did customers mention in interviews?" (Legacy AI context)
- [ ] I can ask Claude "Show me all open questions across all projects" (cross-project query)
- [ ] Search completes in <2 seconds even with multiple projects
- [ ] Results show which project the info came from

---

### Story 5: Real-Time Roadmap Visibility

**As Dharan** (founder),  
**I want** Notion roadmap to automatically update when work is committed,  
**So that** my morning ritual shows accurate project status without manual updates.

**Acceptance Criteria**:
- [ ] When Claude Code commits work, Notion roadmap item status updates automatically
- [ ] When a phase completes, roadmap shows "✅ Complete" without me changing it
- [ ] I can check project health on my phone (Notion mobile) during the day
- [ ] Last updated timestamps reflect actual work, not when I remembered to update Notion

---

## 🎨 Design Notes

**UI/UX Considerations**:

This is infrastructure, not UI. The "user interface" is:
- **For Dharan (chat)**: Claude conversation interface (already familiar)
- **For Dharan (mobile)**: Notion app dashboard (already familiar)  
- **For Claude Code**: Terminal + text editor (already familiar)

No new interfaces to learn.

**Visual Design**:

- **Architecture diagrams**: Mermaid diagrams showing system flow (will be created in Phase 1B, reference `docs/architecture/context-sync-bridge.mermaid.md`)
- **Notion dashboard**: Simple board view (by Status) + table view (all properties) + timeline view (by deadline)

**Information Architecture**:

```
ai-assistant/
├── docs/                           # NEW - All project docs
│   ├── prd/                        # Claude writes
│   │   ├── TEMPLATE.md
│   │   └── context-sync-bridge.md # This PRD
│   ├── tech-requirements/          # Claude Code writes
│   │   ├── TEMPLATE.md
│   │   └── [feature].md
│   ├── sessions/                   # Both write
│   │   ├── TEMPLATE.md
│   │   ├── claude-chat/
│   │   └── claude-code/
│   ├── architecture/               # Both write
│   │   ├── TEMPLATE.mermaid.md
│   │   └── context-sync-bridge.mermaid.md
│   └── README.md                   # Documentation index
├── mcp_server/                     # NEW - MCP tools
│   └── simple_server.py (→ full_server.py in Phase 3)
├── scripts/
│   └── sync_to_notion.py           # NEW - Git hook script
└── .git/hooks/
    └── post-commit                 # NEW - Auto-sync trigger
```

**How this fits into existing structure**: 

- Your voice-to-Notion pipeline remains unchanged in `src/`
- This adds a parallel documentation system in `docs/`
- Both systems coexist - one for voice notes, one for project docs
- Future integration possible: Voice notes could reference project docs

---

## ❓ Open Issues & Key Decisions

### Open Issues

**1. RAG Search Implementation** (Phase 5 - Day 10-12):
- **Context**: Need to search across project docs instantly (Success Criteria #4)
- **Options**:
  - A: Simple keyword matching (fast, good for small corpus, easy to implement)
  - B: Semantic embeddings (better relevance, requires vector DB, more complex)
- **Recommendation**: Defer decision to Phase 5 kickoff after researching RAG frameworks with Peter (engineering coach)
- **Status**: Open - requires deeper technical understanding before deciding
- **Impact**: Doesn't block Phases 1-4, can start with simple and upgrade later if needed

---

### Key Decisions Made

**1. Git/GitHub as Source of Truth** (November 8, 2025):
- **Why**: Version control enables rollback if something breaks. Cloud backup survives laptop death. Separation from Notion PARA makes future collaboration cleaner.
- **Trade-offs**: Git has learning curve (but Claude Code handles it). Adds complexity vs pure Notion. Requires internet for GitHub sync.
- **Impact**: All documentation flows through Git first, Notion syncs FROM it (not bidirectional)
- **One-way door**: Switching to different architecture later would require migration, but risk is low given MCP proof-of-concept success

**2. MCP for Context Loading** (November 8, 2025):
- **Why**: Anthropic official SDK, proven working on Day 1 (100% test success rate). Eliminates copy-paste, enables auto-context loading.
- **Trade-offs**: Mac-only (can't use MCP from web/phone). Cutting-edge tech (potential breaking changes). Requires Claude Desktop app.
- **Impact**: Context loading time drops from 10-15 min to <3 min (80%+ time savings)
- **Two-way door**: If MCP fails, fallback to manual file reading (still better than status quo)

**3. Hybrid Architecture (Repo + Notion)** (November 8, 2025):
- **Why**: Best of both worlds - Git's version control + Notion's visual dashboard. Keeps IP-sensitive docs separate from personal PARA. Leverages existing Notion investment.
- **Trade-offs**: More complex than pure Notion or pure Git. Requires keeping systems in sync. Two places to check (but Notion is read-only dashboard).
- **Impact**: Enables collaboration in future without exposing personal Notion. Protects against vendor lock-in (Git is portable).
- **Two-way door**: Can simplify to pure Git later if Notion becomes burden

**4. Templates-First Approach** (November 8, 2025):
- **Why**: Standardized formats reduce decision fatigue. Both agents can read/write in same structure. Foundation for automation (git hooks can parse structured docs).
- **Trade-offs**: Upfront investment in templates (4-6 hours). Templates need maintenance as workflows evolve. Could feel bureaucratic if over-engineered.
- **Impact**: Validated on Day 1 - templates enhanced with PARITY principles, TL;DR sections, explicit non-goals. Ready for use.
- **Two-way door**: Templates can be simplified or enhanced based on usage data

**5. 2-Week Timeline (Tier 0 Only)** (November 8, 2025):
- **Why**: Baby arrives January 2026 - need foundational system operational before time availability drops. Focus on core value (context sync), defer polish.
- **Trade-offs**: Some nice-to-haves deferred to Tier 1+ (Notion PARA search, calendar sync, etc.). Risk of technical debt if rushing. No room for scope creep.
- **Impact**: Aggressive but achievable. Day 1 ahead of schedule (Phase 1A + 1B in 4 hours vs 6-8 estimated). Remaining phases well-scoped.
- **One-way door**: Can't extend timeline due to baby deadline, but can defer lower-priority phases to Tier 1

**6. Backup on Every Commit** (November 8, 2025):
- **Why**: Already committing at end of every session. Claude Code already pushes to GitHub. Zero additional work. Maximum protection against data loss.
- **Trade-offs**: Requires internet connection for GitHub push. More frequent GitHub API calls (but well under rate limits).
- **Impact**: Full project history preserved. Can rollback to any previous state. Cloud backup survives laptop failure.
- **Two-way door**: Can switch to daily backups if commit frequency becomes issue (unlikely)

---

## 🔗 Links

- **Tech Requirements**: 
  - Phase 1: [mcp-poc-and-templates.md](tech-requirements/mcp-poc-and-templates.md) (Phase 1A + 1B) - ✅ Complete
  - Phase 2: [git-hooks-notion-sync.md](tech-requirements/git-hooks-notion-sync.md) (to be created)
  - Phase 3: [mcp-server-expansion.md](tech-requirements/mcp-server-expansion.md) (to be created)
  - Phase 4: [notion-command-center.md](tech-requirements/notion-command-center.md) (to be created)
  - Phase 5: [rag-search.md](tech-requirements/rag-search.md) (to be created)
  - Phase 6: [testing-validation.md](tech-requirements/testing-validation.md) (to be created)

- **Architecture Diagrams**: [docs/architecture/context-sync-bridge.mermaid.md](architecture/context-sync-bridge.mermaid.md) (to be created in Phase 3)

- **Notion Roadmap**: [Epic 2nd Brain - Tier 0 Roadmap](https://www.notion.so/2a58369c73058079a356cbf2dd2d86bc)

- **Implementation Plan**: [Detailed Implementation Plan](https://www.notion.so/2a58369c7305801896cfc84da4a03f3d)

- **Systems Thinking Context**: Project file `Systems_Thinking_Workbook__Energy___Voice-to-Notion.md`

---

## 📅 Timeline & Status

**Current Status**: In Development  
**Phase 1 Complete**: November 8, 2025 (MCP PoC + Templates)  
**Target Completion**: November 22, 2025 (14 days from kickoff)

**Key Milestones**:

- **Week 1 (Nov 8-15): Foundation** - 15-20 hours
  - ✅ Day 1-2 (Nov 8): MCP PoC + Templates (4 hours actual, ahead of 6-8 estimate)
  - 🟡 Day 3-4 (Nov 9-10): Template validation + MCP expansion (6-8 hours)
  - ⬜ Day 5-6 (Nov 11-12): Git hooks + Notion sync OR continue MCP (depends on Day 3-4 results)
  - **What gets unlocked**: Auto-context loading working, session logs automated, basic sync operational

- **Week 2 (Nov 15-22): Polish + Validation** - 15-20 hours
  - ⬜ Day 7-9 (Nov 13-15): Notion Command Center dashboard (6-8 hours)
  - ⬜ Day 10-12 (Nov 16-18): RAG search implementation (6-8 hours)
  - ⬜ Day 13-14 (Nov 19-20): Testing + validation (3-4 hours)
  - **What gets unlocked**: Full system operational, 2x leverage validated, ready for daily use

**Blockers**: 

- None currently
- Potential blocker: RAG search decision (simple vs semantic) - to be resolved in Phase 5 kickoff

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|----------|
| 2025-11-08 | Claude (Sonnet 4.5) | Initial draft - comprehensive PRD based on roadmap, implementation plan, and systems thinking workbook |
| 2025-11-08 | Claude (Sonnet 4.5) | Updated to Approved status with multi-project scalability (Stories 1 & 4), Legacy AI in non-goals, 100,000X section enhanced |

---

## 🎓 Systems Thinking Applied

**Why This System Works** (Meta-Analysis):

This PRD addresses three critical leverage points from Donella Meadows' hierarchy:

**Leverage Point #6 - Information Flows** (High Impact):
- **Current broken flow**: Context trapped in three disconnected systems (Claude chat, Claude Code terminal, Notion dashboard)
- **New automated flow**: Git → GitHub → Notion (one-way sync), MCP → Claude (auto-context loading)
- **Impact**: 70-120 min/week saved, eliminates translation overhead

**Leverage Point #5 - Rules** (High Impact):
- **Current chaos**: No structure for how agents communicate, ad-hoc handoffs, forgotten documentation
- **New rules**: Templates define structure, git hooks enforce sync, MCP tools standardize context loading
- **Impact**: Consistent handoffs, zero context loss, preserved decision history

**Leverage Point #4 - Self-Organization** (High Impact):
- **Current manual orchestration**: You manually copy-paste, update Notion, reload context every session
- **New self-organizing system**: Commits trigger Notion updates, session starts trigger context loading, system maintains itself
- **Impact**: Reduced cognitive load, scales to multiple projects, foundation for 100,000X workflows

**Feedback Loops Created**:

**Reinforcing Loop R1: Documentation Value**
```
Good docs → Easy context loading → More usage → Better docs → (repeat)
```
As docs become more useful, you use them more. As you use them more, you refine them. This creates a virtuous cycle where the system gets better with use.

**Balancing Loop B1: Context Freshness**
```
Context staleness → Session start → Fetch latest → Updated context → (equilibrium)
```
System self-corrects for stale context. Every session start pulls latest docs, preventing drift.

**Balancing Loop B2: Roadmap Accuracy**
```
Roadmap drift → Git commit → Auto-update → Accurate roadmap → (equilibrium)
```
Manual Notion updates are unreliable (you forget). Git hooks make updates automatic, keeping dashboard accurate.

**Why This Matters for 100,000X**:

You've defined 100,000X as "amplifying cognitive capacity by 100,000X over career lifetime through contemplative technology." This system is foundational:

- **Amplifies, not replaces**: MCP loads context, but YOU make strategic decisions
- **Preserves authentic voice**: Templates structure thinking, don't replace it
- **Eliminates friction**: 10-15 min → 3 min = 80% reduction in startup friction
- **Compounds over time**: Every project benefits from same system (Voice-to-Notion next, then others)
- **Protects energy**: With baby arriving January 2026, your energy system needs this. Less time on manual admin = more presence with family.
- **Scales to all projects**: This system isn't just for Epic 2nd Brain. Your customer discovery for Legacy AI, your home remodel planning, your voice-to-Notion improvements - all benefit from the same infrastructure. Build the context sync bridge once, apply it forever. This is **systems thinking at scale** - the leverage compounds with every project added.

---

## 🎯 Alignment with Personal Context

**Your Energy System** (from Systems Thinking Workbook):

This system directly addresses your energy management:

- **Morning deep work block (7am-12pm)**: Context loads in <3 min, preserving your natural peak for creative work (not admin)
- **Midday valley (12-3pm)**: Session logs auto-created, no manual documentation during low-energy period
- **Evening family time**: No "I need to update Notion" guilt - it's automatic

**Your Baby Deadline** (January 2026):

- 10 weeks to establish Tier 0
- Phases 1-6 designed for 30-40 hours total
- Week 1 already ahead of schedule (4 hours actual vs 6-8 estimated)
- System must be self-sustaining before time availability drops

**Your 100,000X Philosophy**:

- Context sync is **Tier 0 leverage** - unlocks everything else
- Voice-to-Notion was first system (15-30 min/day saved)
- This is second system (70-120 min/week saved)
- Future systems build on these foundations (calendar, email, etc.)

**Your Systems Thinking Approach**:

- Structure determines behavior (not willpower, not discipline)
- Current structure: Manual bridges → oscillating context quality
- New structure: Automated flows → stable, reliable context
- Trade-offs transparent (documented in Key Decisions)

---

**End of PRD**
