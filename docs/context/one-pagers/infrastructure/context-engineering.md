# One-Pager: Applied Context Engineering

**Status**: Active - Build Phase
**Project**: Infrastructure
**Owner**: Dharan Chandrahasan
**Created**: 2025-11-18
**Last Updated**: 2025-11-25

---

## 🎯 TL;DR

Build intelligent context management for Claude Chat through 4 integrated phases delivered in Week 1 (Nov 25-29): Tool Priority Fix (1 hour) eliminates 8-step spirals + Visibility & Control (6-8 hours) stops restart spirals + Smart Discovery (6-8 hours) enables instant file finding + Learning Loop (4-6 hours) auto-improves suggestions. Total investment: 17-23 hours for 100-140 min/week savings, foundation for multi-project scaling.

---

## 🔥 Why This Matters

### The 8-Step Spiral (Validated Nov 25, 2025)

**Test query**: "Read the meta-analysis from the Insights folder in Legacy AI"

**What happened**:
1. `read_file` (wrong path) → ❌
2. `bash ls` → ❌
3. `bash find` → ❌
4. `bash ls` again → ❌
5. `bash find` again → ❌
6. `search_docs` (wrong project) → ❌
7. `search_legacy_corpus` → ✅ FOUND IT
8. `read_source_document` → ✅ SUCCESS

**Time wasted**: 90-120 seconds

**Root causes identified**:
- Tool selection priority (Claude tries bash/view before MCP)
- Path discovery (no way to find files without exact paths)
- Cross-project confusion (search tools don't work across projects)

---

### The Invisible Crisis (Your Pain Points)

> "A lot of the times, the files you suggest in the beginning are completely useless too and the mcp tool doesn't learn at all."

> "I usually pivot to a new chat to start and I forget halfway in which files are in context."

> "Today, it's so hard to add a file, I have to go to the folder and paste the path name exactly."

**The Cascading Failure:**
Bad suggestions (30% accuracy) → Work with wrong context → 20 min in, need different files → 90-120 sec tool spiral → Give up OR spend 5 min navigating → Start new chat → Lose 20 min work → Same bad suggestions → Repeat.

**Impact:**
- **Time cost**: 100-140 min/week in context management friction (1.7-2.3 hours/week)
- **Cognitive cost**: "Which files are loaded?" uncertainty breaks flow state
- **Scaling blocker**: With 3-5 projects, friction multiplies 3-5x (unbearable without fix)
- **Strategic importance**: Leverage Point #6 (Information Flows) - make invisible visible

---

## 📊 Current Status

**Phase**: Build - Week 1 Implementation (Nov 25-29)

**Progress**: 
- ✅ Phase 1 (Architecture): Complete
- 🎯 Phase 0-4 (Implementation): Starting Nov 25

**Timeline**: Nov 18 → Dec 2 (2 weeks total)
- Week 1: Architecture analysis → ✅ Complete
- Week 2: Full implementation (all 4 phases) → In Progress

---

## 🚀 Phase Breakdown

### ✅ Phase 1: Systems Architecture (Nov 18-24) - COMPLETE
**Time**: 4-6 hours

**What shipped:**
- Component inventory (50+ modules documented, 5 friction points analyzed)
- System context diagram (Level 1 - Executive view)
- Container architecture diagram (Level 2 - Builder view, complete system map)
- Leverage points analysis (Level 3 - Decision view, 8 interventions ranked)
- **Context management deep dive** (Level 4 - Component view, current vs proposed architecture with 3-phase progressive enhancement)

**What gets unlocked:**
- Clear understanding of current system structure
- Identification of high-leverage intervention points (8-step spiral validated as critical)
- Foundation for Phases 0-4 implementation
- Validated need for comprehensive Week 1 implementation (not spread over 3 weeks)

---

### 🎯 Phase 0: Tool Selection Priority Fix (Nov 25) - WEEK 1, DAY 1
**Time**: 1 hour

**Problem**: 8-step spiral validated (Claude tries bash/view/grep before MCP tools, wastes 30-90 sec per operation)

**Solution**:
- Optimize MCP tool descriptions for discoverability
- Add 🎯 priority signals ("PRIMARY TOOL", "use me FIRST")
- Add explicit "WHEN TO USE" and "DO NOT use bash" guidance
- Test with fresh Claude Chat to validate fix

**Key deliverables:**
- Zero tool selection spirals (from current 3-5 per session)
- Claude uses MCP tools on first attempt (not 8th attempt)
- New Phase 2-4 tools (`list_context`, `reload_context`, `search_repo`) used correctly from Day 1

**Time saved**: 15-45 min/week (eliminates 30-90 sec waste × 30-50 events/week)

**PRD**: [Live Context Control](../../prd/live-context-control.md)

---

### 🎯 Phase 2: Context Visibility + Control (Nov 25-26) - WEEK 1, DAY 1-2
**Time**: 6-8 hours

**Goals:**
- Make context visible: `list_context()` tool (shows loaded files with metadata)
- Enable mid-session adjustments: `reload_context(add, remove)` tool (swap files in <30 sec)
- Always-load core files: ROADMAP.md, one-pager (no manual loading, 100% availability)
- Track usage patterns (silent, privacy-preserving, foundation for Phase 4 learning)

**Key deliverables:**
- Zero restart spirals (from current 3-5 per week)
- Context adjustment time: 5 min → 30 sec (90% reduction)
- ROADMAP.md always available (no "hard to refer to midway")
- Session state tracking (files loaded, added, removed, referenced)
- Usage tracking (append-only log for Phase 4, NO conversation content)

**Time saved**: 45 min/week

**PRD**: [Live Context Control](../../prd/live-context-control.md)

---

### 🎯 Phase 3: Smart Discovery (Nov 27-28) - WEEK 1, DAY 3-4
**Time**: 6-8 hours

**Goals:**
- Eliminate 8-step spirals: Find files by content/name in <2 sec (not 90-120 sec)
- Semantic search: `search_repo(query, file_types, project)` tool
- Pattern browsing: `list_files(pattern, project)` tool
- Cross-project search that actually works (fix test failure)

**Technical Decision** (Made at Phase 3 Kickoff):
- Option A: Simple ripgrep keyword search (fast, simple, good for ~50k token corpus)
- Option B: Mini-RAG with ChromaDB (semantic, better relevance, more complex)
- **Recommendation**: Start with ripgrep (A), monitor Phase 2 usage, upgrade to RAG (B) if search quality insufficient
- **Rationale**: Test showed path discovery is main issue, not semantic understanding. Corpus might be too small (~50k tokens) to justify RAG overhead. Can always upgrade later.

**Key deliverables:**
- File discovery: 90-120 sec (spiral) → 2-4 sec (search) = **95-97% reduction**
- No more "go to folder, paste exact path" friction
- Cross-project search works: Legacy AI vs Epic 2nd Brain correctly routed
- Examples work: "Find PRDs about sessions", "Show me all architecture docs"

**Time saved**: 35-65 min/week

**PRD**: [Live Context Control](../../prd/live-context-control.md)

---

### 🎯 Phase 4: Learning Loop (Nov 29) - WEEK 1, DAY 5
**Time**: 4-6 hours

**Goals:**
- Analyze 2-3 weeks of usage data (accumulated from Phase 2 tracking during Phases 2-3 work)
- Auto-update context-profiles.json with learned patterns
- Improve suggestions: 30% → 80% accuracy (2.7x improvement)
- Make MCP finally learn (addresses "doesn't learn at all" pain)

**Learning Algorithm:**
- Score files based on: references in responses (+3), explicitly added (+2), loaded and kept (+1), explicitly removed (-5), loaded but never referenced (-1)
- Weight recent sessions higher (last 5 sessions = 2x weight)
- Rank files by score, top 3-6 become new suggestions
- Transparent reasoning: "Suggested because used in 8/10 recent sessions"

**Key deliverables:**
- Suggestions reflect actual usage patterns (not generic heuristics)
- System learns which files you use vs ignore
- Suggestion accuracy: 30% → 80% by Week 4
- Can see why files suggested, can reset if system learns wrong pattern

**Time saved**: 20-30 min/week

**PRD**: [Live Context Control](../../prd/live-context-control.md)

---

## 📈 Success Metrics

**Overall (All Phases):**
- **Total time saved**: 100-140 min/week (1.7-2.3 hours/week)
  - Phase 0: 15-45 min/week (faster tool selection)
  - Phase 2: 45 min/week (fewer restarts)
  - Phase 3: 35-65 min/week (faster file discovery)
  - Phase 4: 20-30 min/week (better suggestions)

**Investment vs Return:**
- Total time: 17-23 hours (all phases Week 1)
- Weekly savings: 100-140 min (1.7-2.3 hours)
- Payback period: **10-13 weeks**
- ROI after 1 year: **4.7-6.5x return** (88-120 hours saved for 17-23 invested)

**Performance Improvements:**
- Tool selection: 30-90 sec → 2-5 sec (**85-95% reduction**)
- Context adjustment: 5 min → 30 sec (**90% reduction**)
- File discovery: 90-120 sec → 2-4 sec (**95-97% reduction**)
- Suggestion accuracy: 30% → 80% (**2.7x improvement**)
- Restart spirals: 3-5 per week → 0 (**100% elimination**)

**Cognitive Benefits (Priceless):**
- No more 8-step tool selection spirals breaking flow
- No more "which files loaded?" uncertainty
- No more restart spirals losing 20 min of work
- No more navigation friction breaking concentration
- Confidence in context quality

**Scaling Benefits:**
- Prevents 3-5x friction multiplication as projects grow (2 → 5 projects)
- Foundation for cross-project context ("Show me decisions across all projects")
- Enables 100,000X workflows at scale

**2x Validation:**
- Target: 50% time reduction in context management by Week 2
- Measure: Time spent on context (adjustments + discovery) before vs after
- If not hitting 50% by Week 2, reassess approach

---

## 🔗 Key Artifacts

**PRDs:**
- [Live Context Control PRD](../../prd/live-context-control.md) - **NEW: Comprehensive rewrite with validation test, Phase 0, Week 1 plan**
- [Context Sync Bridge PRD](../../prd/context-sync-bridge.md) - Related foundation work

**Architecture:**
- [Context Management Architecture](../../architecture/context-management-current-vs-proposed.mermaid.md) - **NEW: Level 4 deep dive, current vs proposed with 3-phase progressive enhancement**
- [Interactive Visualization](../../architecture/visuals/context-management-architecture.html) - **NEW: 4-tab executive presentation with metrics and timeline**
- [Systems Leverage Points](../../architecture/leverage-points.mermaid.md) - Level 3 analysis (identified this opportunity)
- [Component Inventory](../../architecture/component-inventory.md) - 50+ modules documented

**Research:**
- [Context Engineering README](../../insights/context-engineering/README.md)
- [Next Steps](../../insights/context-engineering/next-steps.md)
- [Application to Epic 2nd Brain](../../insights/context-engineering/application-to-epic2b.md)

---

## 🎯 Key Decisions & Trade-offs

### Decision 1: Comprehensive Week 1 Implementation (Nov 25, 2025)
**Context**: Could spread over 3 weeks (6-8 hours each) or compress to 1 week (17-23 hours)
**Chosen**: All 4 phases in Week 1 (Nov 25-29)
**Rationale**: User requested comprehensive PRD for single handoff, baby deadline makes intensive burst better than slow build, Claude Code can tackle in 1-2 focused sessions
**Trade-offs**: More intensive week vs spread-out work, but all features operational by Week 2
**One-way door**: Can't easily split back to 3 weeks once started, but can pause between phases if needed

### Decision 2: Phase 0 as Blocker (Nov 25, 2025)
**Context**: Validation test showed 8-step spiral, wastes 30-90 sec per operation
**Chosen**: Fix tool selection priority FIRST (Phase 0), before building new tools (Phases 2-4)
**Rationale**: If we build new tools without fixing this, they'll suffer same 8-step spiral fate. Test proved this is real, not theoretical.
**Trade-offs**: Adds 1 hour to timeline, but prevents Phase 2-4 tools from being ignored
**One-way door**: Once tool descriptions optimized, hard to test "before" state, but low risk

### Decision 3: Track Usage from Phase 2 (Nov 25, 2025)
**Context**: Phase 4 needs usage data to learn patterns
**Chosen**: Start tracking in Phase 2 (silent, privacy-preserving, accumulates during Phases 2-3)
**Rationale**: Phase 4 starts with 2-3 weeks of real data (not theoretical), immediate improvements possible
**Trade-offs**: Slight Phase 2 complexity, but avoids rework and enables effective Phase 4
**One-way door**: Once tracking starts, hard to retrofit if we wait

### Decision 4: Mini-RAG Decision Deferred (Nov 25, 2025)
**Context**: Epic 2nd Brain corpus ~50k tokens, is RAG justified?
**Chosen**: Decide at Phase 3 kickoff (Day 3) based on Phase 2 usage patterns
**Options**:
- A: Simple ripgrep keyword search (fast, simple, ~100ms queries)
- B: Mini-RAG with ChromaDB (semantic, better relevance, ~800ms queries)
**Recommendation**: Start with ripgrep (A), monitor Phase 2, upgrade to RAG (B) if search quality insufficient
**Rationale**: Test showed path discovery is main issue, not semantic understanding. Corpus might be too small. Can always upgrade later (two-way door).
**Status**: Open - will decide Day 3 based on data

### Decision 5: Desktop-First (No API Yet) (Nov 25, 2025)
**Context**: Could build for API or Desktop
**Chosen**: Desktop-first (Claude Max $100/month flat fee, no API costs)
**Rationale**: Zero additional cost, covers all interactive work for Phases 0-4
**Trade-offs**: Can't build autonomous agents (defer to Tier 3 when needed), but not needed for context control
**Two-way door**: Can add API later if needed (Context Engineering has Tier 3 plan for API)

---

## 🚫 Out of Scope

**Not in this initiative:**
- **Auto-context pruning** (risky, needs extensive validation, Phase 5+ after learning proven 3+ months)
- **Real-time token release** (technical limitation - can't delete conversation history)
- **Cross-conversation memory** (different problem, requires persistent memory like Projects, Tier 2+)
- **Multi-agent context coordination** (technical limitation - no API for Claude Code prompt injection)
- **Voice commands for context** ("Claude, remove the architecture doc" - polish, not core value, Tier 2+)
- **Context presets** ("Load my 'deep work' context set" - learning loop should make unnecessary)
- **External tool integration** (VS Code, Cursor - MCP is Claude Desktop only, scope creep)
- **Advanced visualizations** (context usage graphs, timeline views - nice-to-have polish, Tier 2+)

**Scope protection:** With baby arriving January 2026, these non-goals actively rejected to protect Week 1 timeline and focus on high-ROI work.

---

## 📝 Change Log

| Date | Update | Author |
|------|--------|--------|
| 2025-11-18 | Created initiative from context engineering research | Claude Code |
| 2025-11-24 | Phase 1 complete, PRD created for Phases 2-4, timeline extended to Dec 13 | Claude (Sonnet 4.5) |
| 2025-11-25 | **Major update**: Validation test (8-step spiral), PRD comprehensive rewrite, Phase 0 added, Week 1 comprehensive implementation plan, Level 4 architecture diagrams, interactive visualization | Claude (Sonnet 4.5) |

---

**Related**: [ROADMAP.md](../../../ROADMAP.md) | [Live Context Control PRD](../../prd/live-context-control.md) | [Context Management Architecture](../../architecture/context-management-current-vs-proposed.mermaid.md)
