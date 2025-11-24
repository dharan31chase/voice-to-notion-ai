# One-Pager: Applied Context Engineering

**Status**: Active
**Project**: Infrastructure
**Owner**: Dharan Chandrahasan
**Created**: 2025-11-18
**Last Updated**: 2025-11-24

---

## 🎯 TL;DR

Build context intelligence for Claude Chat workflows through progressive enhancement: (1) systems architecture understanding, (2) mid-session context control, (3) intelligent file discovery, (4) automatic learning from usage. Saves 100-140 min/week while enabling multi-project scaling and preventing context management nightmare as projects grow from 2 → 5+.

---

## 🔥 Why This Matters

**The Invisible Crisis** (Your Words):
> "A lot of the times, the files you suggest in the beginning are completely useless too and the mcp tool doesn't learn at all."

> "I usually pivot to a new chat to start and I forget halfway in which files are in context."

> "Today, it's so hard to add a file, I have to go to the folder and paste the path name exactly."

**The Cascading Failure:**
Bad suggestions → Work with wrong context → 20 min in, need different files → Can't find path → Give up OR spend 5 min navigating → Start new chat → Lose 20 min of work → Same bad suggestions → Repeat.

**Impact:**
- **Time cost**: 45-140 min/week in context management friction (0.75-2.3 hours/week)
- **Cognitive cost**: "Which files are loaded?" uncertainty breaks flow state
- **Scaling blocker**: With 3-5 projects, friction multiplies 3-5x (unbearable without fix)
- **Strategic importance**: Leverage Point #6 (Information Flows) - make invisible visible

---

## 📊 Current Status

**Phase**: Build

**Progress**: 40% (Phase 1 complete)

**Timeline**: Nov 18 → Dec 13 (4 weeks)

---

## 🚀 Phase Breakdown

### ✅ Phase 1: Systems Architecture (Nov 18-24) - COMPLETE
**Time**: 4-6 hours

**What shipped:**
- Component inventory (50+ modules documented, 5 friction points analyzed)
- System context diagram (Level 1 - Executive view)
- Container architecture diagram (Level 2 - Builder view, complete system map)
- Leverage points analysis (Level 3 - Decision view, 8 interventions ranked)

**What gets unlocked:**
- Clear understanding of current system structure
- Identification of high-leverage intervention points
- Foundation for Phases 2-4 implementation
- Level 4 (component deep dives) will iterate over time as needed

---

### 🎯 Phase 2: Context Visibility + Control (Nov 25-29) - NEXT
**Time**: 6-8 hours

**Goals:**
- Make context visible: `list_context()` tool
- Enable mid-session adjustments: `reload_context(add, remove)` tool
- Always-load core files: ROADMAP.md, one-pager (no manual loading)
- Track usage patterns (silent, foundation for Phase 4 learning)

**Key deliverables:**
- Zero restart spirals (from current 3-5 per week)
- Context adjustment time: 5 min → 30 sec (90% reduction)
- ROADMAP.md 100% available in all sessions

**Time saved**: 45 min/week

**PRD**: [Live Context Control](../../prd/live-context-control.md)

---

### 🎯 Phase 3: Smart Discovery (Dec 2-6)
**Time**: 6-8 hours

**Goals:**
- Semantic search: `search_repo(query)` tool (find files by content)
- Pattern browsing: `list_files(pattern)` tool (explore by glob)
- Eliminate manual path hunting (from 5 min → 10 sec per file)

**Key deliverables:**
- File discovery: 5 min navigation → 2 sec search (97% reduction)
- No more "go to folder, paste exact path" friction
- Examples: "Find PRDs about sessions", "Show me all architecture docs"

**Time saved**: 35-65 min/week

**PRD**: [Live Context Control](../../prd/live-context-control.md)

---

### 🎯 Phase 4: Learning Loop (Dec 9-13)
**Time**: 4-6 hours

**Goals:**
- Analyze 2-3 weeks of usage data (from Phase 2 tracking)
- Auto-update context-profiles.json with learned patterns
- Improve suggestions: 30% → 80% accuracy (2.7x improvement)

**Key deliverables:**
- System learns which files you actually use (vs suggested)
- Suggestions reflect last 5 sessions, not all-time
- MCP finally learns (addresses "doesn't learn at all" pain)

**Time saved**: 20-30 min/week

**PRD**: [Live Context Control](../../prd/live-context-control.md)

---

## 📈 Success Metrics

**Overall (All Phases):**
- Time saved: 100-140 min/week (1.7-2.3 hours/week)
- Context adjustment: 5 min → 30 sec (90% reduction)
- File discovery: 5 min → 10 sec (97% reduction)
- Suggestion accuracy: 30% → 80% (2.7x improvement)
- Restart spirals: 3-5 per week → 0

**Cognitive Benefits (Priceless):**
- No more "which files loaded?" uncertainty
- No more restart spirals losing work
- No more navigation friction breaking flow
- Confidence in context quality

**Scaling Benefits:**
- Prevents 3-5x friction multiplication as projects grow
- Foundation for cross-project context
- Enables 100,000X workflows at scale

**2x Validation:**
- Target: 50% time reduction in context management by Week 2 (Phase 3 complete)
- Measure: Time spent on context (adjustments + discovery) before vs after

---

## 🔗 Key Artifacts

**PRDs:**
- [Live Context Control PRD](../../prd/live-context-control.md) - Phases 2-4 detailed
- [Context Sync Bridge PRD](../../prd/context-sync-bridge.md) - Related foundation work

**Architecture:**
- [Systems Architecture Diagrams](../../architecture/leverage-points.mermaid.md) - Level 1-3 complete
- [Component Inventory](../../architecture/component-inventory.md) - 50+ modules documented

**Research:**
- [Context Engineering README](../../insights/context-engineering/README.md)
- [Next Steps](../../insights/context-engineering/next-steps.md)
- [Application to Epic 2nd Brain](../../insights/context-engineering/application-to-epic2b.md)

---

## 🎯 Key Decisions & Trade-offs

### Decision 1: Four-Phase Progressive Enhancement
**Context**: Could build all-at-once or phase it
**Chosen**: Phase 1 (architecture) → Phase 2 (visibility) → Phase 3 (discovery) → Phase 4 (learning)
**Rationale**: Each phase delivers independent value, lower risk if priorities shift
**Trade-offs**: 4 weeks vs 2 weeks if rushed, but higher quality and flexibility

### Decision 2: Track Usage from Phase 2
**Context**: Phase 4 needs usage data to learn
**Chosen**: Start tracking in Phase 2 (silent, accumulates during Phases 2-3)
**Rationale**: Phase 4 starts with 2-3 weeks of real data, immediate improvements
**Trade-offs**: Slight Phase 2 complexity, but avoids rework

### Decision 3: Desktop-First (No API)
**Context**: Could build for API or Desktop
**Chosen**: Desktop-first (Claude Max $100/month flat fee)
**Rationale**: Zero additional cost, covers all interactive work
**Trade-offs**: Can't build autonomous agents (defer to Tier 3 when needed)

### Decision 4: Separate PRD from Context Sync Bridge
**Context**: Related but different scope
**Chosen**: New PRD for Live Context Control
**Rationale**: Context Sync Bridge = session start, this = mid-session control
**Trade-offs**: More docs to maintain, but clearer ownership and focus

---

## 🚫 Out of Scope

**Not in this initiative:**
- Cross-conversation memory (different problem, Tier 2+)
- Auto-context pruning (risky, Phase 5+ after learning proven)
- Multi-agent context coordination (technical limitation)
- Real-time token release (technical limitation)
- Voice commands (polish, Tier 2+)
- Context presets (learning loop should make unnecessary)
- External tool integration (scope creep)

---

## 📝 Change Log

| Date | Update | Author |
|------|--------|--------|
| 2025-11-18 | Created initiative from context engineering research | Claude Code |
| 2025-11-24 | Phase 1 complete, PRD created for Phases 2-4, timeline extended to Dec 13 | Claude (Sonnet 4.5) |

---

**Related**: [ROADMAP.md](../../../ROADMAP.md) | [Live Context Control PRD](../../prd/live-context-control.md)
