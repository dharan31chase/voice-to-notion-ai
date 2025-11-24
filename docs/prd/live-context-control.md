# PRD: Live Context Control - Epic 2nd Brain

**Status**: Approved
**Owner**: Dharan Chandrahasan
**Created**: 2025-11-24
**Last Updated**: 2025-11-24
**One-Pager**: [Applied Context Engineering](../context/one-pagers/infrastructure/context-engineering.md)
**Related**: [Context Sync Bridge PRD](context-sync-bridge.md)

---

## 🎯 TL;DR

Build context visibility and control tools for Claude Chat sessions, eliminating the "restart spiral" and manual file hunting that currently waste 10-40 minutes per week. Enable mid-session context adjustments, intelligent file discovery, and automatic learning from usage patterns - saving 25-45 min/week while enabling multi-project scaling.

---

## 🎯 Problem Statement

### The Invisible Friction (Your Words)

**Direct quotes from session:**
> "A lot of the times, the files you suggest in the beginning are completely useless too and the mcp tool doesn't learn at all."

> "I usually pivot to a new chat to start and I forget halfway in which files are in context."

> "Today, it's so hard to add a file, I have to go to the folder and paste the path name exactly for you to even know which file I want to add because the suggestions aren't great now."

> "If I want to refer to roadmap file midway, it's hard. I want to change that."

### The Cascading Failure Pattern

```
Bad suggestions at start
  ↓
Start working with wrong files
  ↓
20 min in, realize you need different context
  ↓
Try to add file manually → can't find path → give up OR spend 5 min navigating
  ↓
Start new chat → lose 20 min of work
  ↓
New chat → same bad suggestions → repeat
```

### Three Core Problems

**Problem 1: Useless Suggestions at Session Start**
- **Current**: MCP suggests 3-6 files based on workstream config or generic heuristics
- **Reality**: Suggestions are often irrelevant ("completely useless")
- **Root cause**: No learning loop - system doesn't track which files you actually use
- **Frequency**: Every session start (5-10 times per week)
- **Cost**: 2-5 min manually requesting correct files OR working with wrong context

**Problem 2: Invisible Context Mid-Session**
- **Current**: No way to see which files are loaded
- **Reality**: "I forget halfway in which files are in context"
- **Root cause**: MCP loads files but doesn't track or display what's loaded
- **Frequency**: 3-5 times per long session (when topic pivots)
- **Cost**: Uncertainty → restart conversation → lose 20 min of work

**Problem 3: Manual File Hell**
- **Current**: To add file mid-session, must navigate folders, copy exact path, paste to Claude
- **Reality**: "So hard to add a file... have to go to the folder and paste the path name exactly"
- **Root cause**: No search/discovery tools in MCP
- **Frequency**: 2-4 times per session when context needs adjustment
- **Cost**: 1-2 min per file × 2-4 files = 2-8 min per session of pure navigation friction

### The Compounding Effect

**High frequency pain:**
- 10 Claude Chat sessions per week
- 3-5 context adjustments per session
- 30-50 friction events per week

**Time cost:**
- Problem 1 (bad suggestions): 2-5 min per session × 10 = 20-50 min/week
- Problem 2 (invisible context): Restart cost ~4 min × occasional = 5-10 min/week
- Problem 3 (manual file hell): 2-8 min per session × 10 = 20-80 min/week
- **Total: 45-140 min/week** (0.75-2.3 hours/week)

**Cognitive cost (harder to measure but real):**
- "Which files are loaded?" uncertainty breaks flow state
- Navigation friction pulls you out of strategic thinking
- Restart spiral loses conversational context and momentum
- Defensive behavior: "I should reference that PRD, but... I'll just work from memory"

### Why Now

**Convergence of factors:**

1. **Scaling pressure**: With Legacy AI + Epic 2nd Brain (2 projects now, 3-5 soon), context management friction will multiply
2. **Architecture work complete**: We just mapped the system (Diagram C) - now we know where to intervene
3. **Foundation exists**: MCP infrastructure from Context Sync Bridge is operational - this builds on it
4. **Baby deadline (Jan 2026)**: Need this solved before time availability drops

**Strategic importance:**
- This is **Leverage Point #6** (Information Flows) - make invisible visible
- Amplifies existing Context Learning Loop (Loop #1 from architecture analysis)
- Foundation for multi-project workflows

---

## 🔧 High-Level Approach

### Three-Phase Solution

**Phase 2: Context Visibility + Control** (Week of Nov 25)
- **Problem**: "I forget which files are in context"
- **Solution**: Make context visible and adjustable mid-session
- **Tools**: `list_context()`, `reload_context(add, remove)`
- **Foundation**: Track usage patterns (silent, for Phase 4 learning)

**Phase 3: Smart Discovery** (Week of Dec 2)
- **Problem**: "So hard to add a file... have to paste the path name exactly"
- **Solution**: Intelligent file search and discovery
- **Tools**: `search_repo(query)`, `list_files(pattern)`
- **Benefit**: "Find PRDs about sessions" → instant results, no path hunting

**Phase 4: Learning Loop** (Week of Dec 9)
- **Problem**: "Suggestions are useless... MCP doesn't learn at all"
- **Solution**: Use accumulated usage data to improve suggestions
- **Mechanism**: Track which files you reference, adjust, add/remove → auto-update profiles
- **Benefit**: Suggestions get better over time (virtuous cycle)

### Why This Approach

**Progressive enhancement:**
- Phase 2 gives immediate relief (visibility + control)
- Phase 3 eliminates manual friction (search + discovery)
- Phase 4 creates long-term improvement (learning)

**Data-driven learning:**
- Tracking starts in Phase 2 (accumulates data during Phases 2-3)
- Phase 4 uses real usage data (2-3 weeks of behavior)
- System learns from actual patterns, not theoretical preferences

**Builds on existing foundation:**
- Context Sync Bridge created MCP infrastructure
- This extends it with new tools
- No architectural changes needed

---

## ✅ Success Criteria

### Phase 2: Context Visibility + Control

**Must Have:**
1. **List context in <5 seconds** (from current "no way to see")
   - Tool: `list_context()`
   - Shows: File paths, load time, token count, reason for inclusion
   - Target: Full context inventory in <5 sec

2. **Adjust context in <30 seconds** (from current ~5 min restart)
   - Tool: `reload_context(add=[], remove=[])`
   - Swaps files without conversation restart
   - Target: Add/remove files in <30 sec

3. **ROADMAP.md always available** (from current "hard to refer to midway")
   - Always-loaded files: ROADMAP.md, one-pager-vision.md
   - No manual loading needed
   - Target: 100% availability in all sessions

4. **Zero restart spirals per week** (from current 3-5 restarts)
   - Metric: Number of conversation restarts due to context issues
   - Target: 0 restarts (all adjustments handled mid-session)

**Usage Tracking (Silent):**
- Track which files actually referenced in responses
- Track which files added/removed mid-session
- Track session duration, project, workstream
- Storage: `~/.cache/epic-2nd-brain/context-usage.jsonl`

**Metrics:**
- Context adjustment time: Restart (5 min) → Reload (30 sec) = **90% reduction**
- Sessions per week: ~10
- **Time saved: 45 min/week** (5 min × 10 sessions = 50 min → 5 min total)

---

### Phase 3: Smart Discovery

**Must Have:**
1. **Find files by content in <2 seconds** (from current "go to folder, paste exact path")
   - Tool: `search_repo(query, file_types, project)`
   - Semantic search over repo (mini-RAG for Epic 2nd Brain docs)
   - Examples:
     - "Find PRDs about sessions" → context-sync-bridge.md
     - "Show me work on MCP" → sessions mentioning MCP
     - "What did we decide about git hooks?" → search across all docs
   - Target: <2 sec for search results

2. **Browse files by pattern** (from current "have to know exact path")
   - Tool: `list_files(pattern, project)`
   - Examples:
     - "Show me all PRDs" → lists docs/prd/*.md
     - "Show me recent sessions" → lists docs/sessions/*/2024-11-*.md
   - Target: Instant listing

3. **Suggest files when topic shifts** (from current "no suggestions")
   - Detect when conversation references unfamiliar terms
   - Auto-suggest: "You mentioned X, should I load Y?"
   - Target: 80% suggestion accuracy (relevant file offered)

**Metrics:**
- File discovery time: 5 min (manual navigation) → 10 sec (search) = **97% reduction**
- Frequency: 2-4 times per session × 10 sessions = 20-40 events/week
- **Time saved: 35-65 min/week** (5 min × 7-13 events saved)

---

### Phase 4: Learning Loop

**Must Have:**
1. **Suggestions improve over time** (from current "completely useless")
   - Analyze 2-3 weeks of usage data (from Phase 2 tracking)
   - Identify patterns: "For systems-architecture, Dharan always needs PRD + roadmap, never component-inventory"
   - Auto-update context-profiles.json
   - Target: 80% suggestion accuracy by Week 4 (from current ~30%)

2. **Learning from explicit signals** (from current "doesn't learn at all")
   - Track which files removed (negative signal)
   - Track which files added (positive signal)
   - Weight recent sessions higher (recency bias)
   - Target: Suggestions reflect last 5 sessions, not all-time average

3. **Implicit learning from references** (from current "no tracking")
   - Which files actually cited in responses (high value signal)
   - Files loaded but never referenced (low value, candidates for removal)
   - Target: Files I reference appear in future suggestions

**Metrics:**
- Suggestion accuracy: 30% → 80% = **2.7x improvement**
- Bad suggestions per session: 3-4 → 0-1
- **Time saved: 20-30 min/week** (2-3 min per session × 10 sessions)

---

### Overall Success (All Phases)

**Total time saved: 100-140 min/week** (1.7-2.3 hours/week)
- Phase 2: 45 min/week (fewer restarts)
- Phase 3: 35-65 min/week (faster file discovery)
- Phase 4: 20-30 min/week (better suggestions)

**Cognitive benefits (priceless):**
- No more "which files are loaded?" uncertainty
- No more restart spirals losing work
- No more navigation friction breaking flow
- Confidence in context quality

**Scaling benefits:**
- Enables multi-project workflows (3-5 projects without 3-5x friction)
- Foundation for cross-project context ("Show me decisions across all projects")
- Prevents nightmare scenario: More projects = exponentially worse context management

**2x Leverage Validation:**
- Target: Save 50% of context management time by Week 2
- Measure: Compare time spent on context (adjustments + discovery) before vs after
- If not hitting 50% by Week 2 (Phase 3 complete), reassess approach

---

## 🚫 Non-Goals

**Not in scope for this PRD:**

1. **Cross-conversation memory** (remembering context across days/weeks)
   - Why: Different problem (requires persistent memory system)
   - When: Defer to Tier 2+ (if needed)

2. **Auto-context pruning** (automatically removing unused files)
   - Why: Could be dangerous (remove important file by mistake)
   - When: Phase 5+ (after learning loop proven)

3. **Multi-agent context coordination** (Claude Chat + Claude Code sharing live context)
   - Why: Technical limitation (no API for Claude Code prompt injection)
   - When: Defer until Anthropic provides mechanism

4. **Real-time token release** (freeing tokens by removing files)
   - Why: Technical limitation (context window = conversation history, can't delete past)
   - Workaround: Can offer "context 85% full, start fresh?" prompt

5. **Voice commands for context control** ("Claude, remove the architecture doc")
   - Why: Voice-to-Notion already handles voice input, this is polish
   - When: Tier 2+ (after core tools proven)

6. **Context presets** ("Load my 'deep work' context set")
   - Why: Learning loop should make this unnecessary (auto-suggests right files)
   - When: Only if users request after Phase 4

7. **Integration with external tools** (VS Code, Cursor, etc.)
   - Why: MCP is Claude Desktop only, scope creep
   - When: Defer indefinitely

**Scope protection:** With baby arriving January 2026, these non-goals aren't just deferred - they're actively rejected to protect timeline and focus on high-ROI work.

---

## 👥 User Stories

### Story 1: Context Transparency

**As Dharan** (founder),
**I want** to see which files Claude has loaded at any point in the conversation,
**So that** I know what context I'm working with and can make informed decisions about adjustments.

**Acceptance Criteria:**
- [ ] Saying "What's in context?" shows list of loaded files
- [ ] Each file shows: path, load time, token count, reason for inclusion
- [ ] Shows total context usage (e.g., "45k tokens, 30% of window")
- [ ] Works at any point in conversation (not just session start)
- [ ] Takes <5 seconds to display

**Current Pain:**
> "I forget halfway in which files are in context."

---

### Story 2: Mid-Session Context Adjustment

**As Dharan** (founder),
**I want** to add or remove files mid-conversation without restarting,
**So that** I can pivot topics seamlessly without losing 20 minutes of work.

**Acceptance Criteria:**
- [ ] Can add files: `reload_context(add=["path1", "path2"])`
- [ ] Can remove files: `reload_context(remove=["path3"])`
- [ ] Can swap files: `reload_context(add=[...], remove=[...])`
- [ ] Adjustment completes in <30 seconds
- [ ] Conversation continues seamlessly (no restart needed)
- [ ] I'm informed what changed: "Loaded X, removed Y, now working with Z"

**Current Pain:**
> "I usually pivot to a new chat to start and I forget halfway in which files are in context."

---

### Story 3: Intelligent File Discovery

**As Dharan** (founder),
**I want** to search for files by content or pattern instead of exact path,
**So that** I don't waste 5 minutes navigating folders and copying paths.

**Acceptance Criteria:**
- [ ] Can search by content: "Find PRDs about sessions" → results in <2 sec
- [ ] Can browse by pattern: "Show me all PRDs" → instant list
- [ ] Can search within project: "Find MCP work in Epic 2nd Brain"
- [ ] Search works across file types (PRDs, sessions, tech-req, etc.)
- [ ] Results show preview snippet (why it matched)
- [ ] Can load directly from results: "Load result #1"

**Current Pain:**
> "Today, it's so hard to add a file, I have to go to the folder and paste the path name exactly for you to even know which file I want to add because the suggestions aren't great now."

---

### Story 4: Always-Available Core Files

**As Dharan** (founder),
**I want** ROADMAP.md and key docs always loaded at session start,
**So that** I can reference them anytime without manual loading.

**Acceptance Criteria:**
- [ ] ROADMAP.md loaded in every session (regardless of workstream)
- [ ] One-pager vision doc loaded in every session
- [ ] No manual "read ROADMAP.md" commands needed
- [ ] Can reference anytime: "What's next on roadmap?" just works
- [ ] Configurable: Can add other always-loaded files per project

**Current Pain:**
> "If I want to refer to roadmap file midway, it's hard. I want to change that."

---

### Story 5: Learning from Usage

**As Dharan** (founder),
**I want** the system to learn from which files I actually use,
**So that** suggestions improve over time instead of being "completely useless."

**Acceptance Criteria:**
- [ ] System tracks which files I reference in conversation (implicit signal)
- [ ] System tracks which files I add/remove mid-session (explicit signal)
- [ ] After 2-3 weeks, suggestions reflect learned patterns
- [ ] For each workstream, system knows: "Dharan usually needs X, Y, Z (not A, B, C)"
- [ ] Suggestions accuracy: 30% → 80% by Week 4
- [ ] Learning is transparent: Can see why files were suggested

**Current Pain:**
> "A lot of the times, the files you suggest in the beginning are completely useless too and the mcp tool doesn't learn at all."

---

## 🎨 Design Notes

### Phase 2: Tools Design

**Tool 1: `list_context()`**

```python
# Returns currently loaded files with metadata
{
  "loaded_files": [
    {
      "path": "docs/architecture/leverage-points.mermaid.md",
      "loaded_at": "2024-11-24T10:15:00Z",
      "size_tokens": 8500,
      "reason": "workstream=systems-architecture, type=synthesis",
      "referenced": true  # Was cited in responses
    },
    {
      "path": "ROADMAP.md",
      "loaded_at": "2024-11-24T10:15:00Z",
      "size_tokens": 2000,
      "reason": "always-loaded",
      "referenced": false
    }
  ],
  "total_tokens": 45000,
  "context_window_used": "30%",
  "max_tokens": 150000
}
```

**Tool 2: `reload_context(add=[], remove=[])`**

```python
# Adds and removes files atomically
reload_context(
  add=["docs/prd/context-sync-bridge.md", "mcp_server/full_server.py"],
  remove=["docs/architecture/component-inventory.md"]
)

# Returns confirmation
{
  "status": "success",
  "added": [
    {"path": "docs/prd/context-sync-bridge.md", "tokens": 6200},
    {"path": "mcp_server/full_server.py", "tokens": 3800}
  ],
  "removed": [
    {"path": "docs/architecture/component-inventory.md", "tokens": 12500}
  ],
  "new_total_tokens": 42500,
  "context_window_used": "28%"
}
```

**Tool 3: Always-loaded files config**

```python
# In project-paths.json, add per-project:
{
  "projects": [
    {
      "name": "Epic 2nd Brain",
      "always_files": [
        "ROADMAP.md",
        "docs/context/one-pager-vision.md"
      ]
    }
  ]
}
```

---

### Phase 3: Smart Discovery Design

**Tool 1: `search_repo(query, file_types=[], project)`**

Uses semantic search (mini-RAG) over repo:
- Chunk markdown files (header-aware, like Legacy AI RAG)
- Generate embeddings (OpenAI text-embedding-3-small)
- Store in ChromaDB (local, lightweight)
- BM25 + semantic hybrid search
- Local BGE reranking (privacy-preserving)

```python
# Example: Search for PRDs about sessions
search_repo(
  query="PRDs about session management",
  file_types=["prd"],
  project="Epic 2nd Brain"
)

# Returns ranked results
{
  "results": [
    {
      "path": "docs/prd/context-sync-bridge.md",
      "score": 0.89,
      "snippet": "...session start triggers context loading...",
      "chunk_id": "abc123"
    },
    {
      "path": "docs/prd/live-context-control.md",
      "score": 0.76,
      "snippet": "...mid-session context adjustment...",
      "chunk_id": "def456"
    }
  ],
  "query_time": "0.8s"
}
```

**Tool 2: `list_files(pattern, project)`**

Simple file listing by glob pattern:

```python
# Example: List all PRDs
list_files(pattern="docs/prd/*.md", project="Epic 2nd Brain")

# Returns
{
  "files": [
    {"path": "docs/prd/context-sync-bridge.md", "modified": "2025-11-08"},
    {"path": "docs/prd/live-context-control.md", "modified": "2025-11-24"}
  ]
}
```

---

### Phase 4: Learning Mechanism Design

**Tracking (starts in Phase 2, used in Phase 4):**

```jsonl
// ~/.cache/epic-2nd-brain/context-usage.jsonl (append-only)
{"session_id": "uuid1", "project": "Epic 2nd Brain", "workstream": "systems-architecture", "timestamp": "2025-11-25T10:00:00Z", "files_suggested": ["component-inventory.md", "roadmap.md"], "files_loaded": ["roadmap.md"], "files_removed": ["component-inventory.md"], "files_added": ["prd/context-sync-bridge.md"], "files_referenced": ["roadmap.md", "prd/context-sync-bridge.md"]}
{"session_id": "uuid2", "project": "Epic 2nd Brain", "workstream": "systems-architecture", "timestamp": "2025-11-26T11:00:00Z", "files_suggested": ["component-inventory.md", "roadmap.md"], "files_loaded": ["roadmap.md"], "files_removed": ["component-inventory.md"], "files_added": ["architecture/leverage-points.mermaid.md"], "files_referenced": ["leverage-points.mermaid.md"]}
```

**Analysis (Phase 4):**

```python
# Analyze last N sessions for workstream
analyze_usage(project="Epic 2nd Brain", workstream="systems-architecture", last_n=10)

# Identifies patterns:
{
  "always_useful": ["ROADMAP.md", "docs/prd/*.md"],  # Referenced in 80%+ sessions
  "never_useful": ["component-inventory.md"],  # Suggested 10 times, removed 9 times
  "sometimes_useful": ["architecture/*.md"],  # Context-dependent
  "temporal_pattern": "PRDs at start, architecture docs added mid-session"
}
```

**Profile update:**

```json
// context-profiles.json (updated automatically)
{
  "profiles": {
    "Epic 2nd Brain": {
      "systems-architecture": {
        "always_files": ["ROADMAP.md", "docs/context/one-pager-vision.md"],
        "suggested_files": [
          {"path": "docs/prd/*", "priority": "high"},
          {"path": "docs/architecture/leverage-points.mermaid.md", "priority": "medium"}
        ],
        "excluded_files": ["docs/architecture/component-inventory.md"],
        "usage_count": 12,
        "last_updated": "2025-12-13"
      }
    }
  }
}
```

---

## ❓ Open Issues & Key Decisions

### Open Issues

**1. Mini-RAG Performance** (Phase 3):
- **Context**: Need semantic search over Epic 2nd Brain docs
- **Question**: Is corpus large enough to justify RAG overhead?
- **Current size**: ~50k tokens (Epic 2nd Brain docs only)
- **Options**:
  - A: Build mini-RAG anyway (consistent with Legacy AI approach)
  - B: Start with simple keyword search, upgrade to RAG later
- **Recommendation**: Start with simple keyword (ripgrep), monitor usage, upgrade to RAG if needed
- **Status**: Open - decide at Phase 3 kickoff based on Phase 2 usage patterns

**2. Tracking Granularity** (Phase 2):
- **Context**: Need to track file usage without being creepy
- **Question**: How much to track?
- **Options**:
  - A: Track everything (every file mentioned in responses)
  - B: Track only explicit signals (files added/removed)
  - C: Track both, but only use explicit signals for learning (privacy-preserving)
- **Recommendation**: Option C - track both, transparent to user, can show what's tracked
- **Status**: Open - needs user confirmation

---

### Key Decisions Made

**1. Three-Phase Approach** (November 24, 2025):
- **Why**: Progressive enhancement - each phase delivers value independently
- **Trade-offs**: Could build all-at-once faster (2 weeks vs 3 weeks), but higher risk if priorities shift
- **Impact**: Phase 2 gives immediate relief, creates foundation for Phases 3-4
- **Two-way door**: Can compress timeline if needed, phases can be reordered

**2. Track Usage from Phase 2** (November 24, 2025):
- **Why**: Accumulate data during Phases 2-3 so Phase 4 starts with real usage patterns
- **Trade-offs**: Slight upfront complexity in Phase 2, but saves rework
- **Impact**: Phase 4 ships with immediate improvements (not "start collecting data")
- **One-way door**: Once tracking starts, hard to retrofit if we wait

**3. Always-Load Core Files** (November 24, 2025):
- **Why**: Specific pain point ("roadmap file midway, it's hard")
- **Trade-offs**: Uses some context window always, but ROADMAP.md is small (~2k tokens)
- **Impact**: 100% availability of most-referenced files, zero manual loading
- **Two-way door**: Can adjust which files are always-loaded based on usage

**4. Separate PRD from Context Sync Bridge** (November 24, 2025):
- **Why**: Different scope (session start vs mid-session), different timeline
- **Trade-offs**: More docs to maintain, but clearer ownership
- **Impact**: Context Sync Bridge can be "complete" while this work continues
- **Two-way door**: Could merge PRDs later if they converge

**5. Desktop-First (No API for Phase 2-4)** (November 24, 2025):
- **Why**: Claude Max subscription ($100/month) covers all interactive work
- **Trade-offs**: Can't build autonomous agents (defer to Tier 3)
- **Impact**: Zero additional cost for Phases 2-4
- **Two-way door**: Can add API later if needed (future-proofing already done in Context Engineering Tier 0)

---

## 🔗 Links

**Context:**
- [Applied Context Engineering One-Pager](../context/one-pagers/infrastructure/context-engineering.md)
- [Context Sync Bridge PRD](context-sync-bridge.md) - Related but separate work
- [Systems Architecture Diagrams](../architecture/leverage-points.mermaid.md) - Identified this opportunity

**Implementation:**
- Tech requirements (to be created per phase)
- Session logs (to be created as work progresses)

**Related Work:**
- Legacy AI RAG Implementation (similar search approach)
- Voice-to-Notion pipeline (proven automation success)

---

## 📅 Timeline & Status

**Current Status**: Approved - Ready to Build
**Phase 1 (Architecture)**: ✅ Complete (November 24, 2025)
**Target Completion**: December 13, 2025 (3 weeks from Nov 24)

**Key Milestones:**

### Week 1: Nov 25-29 (Phase 2: Visibility + Control)
**Time: 6-8 hours**

- [ ] Day 1 (Nov 25): Session state tracking infrastructure (2 hours)
  - Track which files loaded when
  - Track file usage (references, adds, removes)
  - Storage: `~/.cache/epic-2nd-brain/context-usage.jsonl`

- [ ] Day 2 (Nov 26): `list_context()` tool (2 hours)
  - Show loaded files with metadata
  - Display token usage and context window percentage
  - Test with various session states

- [ ] Day 3 (Nov 27): `reload_context()` tool (2 hours)
  - Add/remove files mid-session
  - Atomic swaps (add + remove in one operation)
  - Confirmation messages

- [ ] Day 4 (Nov 28): Always-loaded files (1 hour)
  - Add ROADMAP.md, one-pager to always-files config
  - Test across different workstreams
  - Validate 100% availability

- [ ] Day 5 (Nov 29): Testing + validation (1 hour)
  - End-to-end workflow testing
  - Measure context adjustment time (target: <30 sec)
  - User acceptance testing

**What gets unlocked**: No more restart spirals, context transparency, ROADMAP.md always available

---

### Week 2: Dec 2-6 (Phase 3: Smart Discovery)
**Time: 6-8 hours**

- [ ] Day 1 (Dec 2): RAG decision + implementation plan (1 hour)
  - Review Phase 2 usage patterns
  - Decide: Simple keyword search vs mini-RAG
  - Create implementation plan based on decision

- [ ] Day 2-3 (Dec 3-4): `search_repo()` tool (4-5 hours)
  - Option A: Simple ripgrep-based keyword search (if corpus small)
  - Option B: Mini-RAG with ChromaDB (if usage justifies)
  - Test with realistic queries ("Find PRDs about sessions")

- [ ] Day 4 (Dec 5): `list_files()` tool (1 hour)
  - Glob pattern matching
  - Project-aware file listing
  - Test with various patterns

- [ ] Day 5 (Dec 6): Testing + validation (1 hour)
  - Measure file discovery time (target: <2 sec)
  - End-to-end workflow testing
  - User acceptance testing

**What gets unlocked**: No more manual path hunting, instant file discovery, semantic search

---

### Week 3: Dec 9-13 (Phase 4: Learning Loop)
**Time: 4-6 hours**

- [ ] Day 1 (Dec 9): Usage data analysis (2 hours)
  - Analyze 2-3 weeks of context-usage.jsonl
  - Identify patterns per project+workstream
  - Generate learned profiles

- [ ] Day 2 (Dec 10): Profile auto-update logic (1-2 hours)
  - Algorithm: Weight recent sessions, identify always/never/sometimes useful files
  - Update context-profiles.json automatically
  - Transparent reasoning (can explain why suggested)

- [ ] Day 3 (Dec 11): Integration with `start_session()` (1 hour)
  - Use learned profiles for suggestions
  - Fall back to heuristics if no learned profile
  - A/B test: old suggestions vs learned suggestions

- [ ] Day 4 (Dec 12): Testing + validation (1 hour)
  - Measure suggestion accuracy (target: 80%)
  - Compare to baseline (30%)
  - User acceptance testing

- [ ] Day 5 (Dec 13): Documentation + handoff (1 hour)
  - Update one-pager with results
  - Document learned patterns
  - Mark initiative complete

**What gets unlocked**: System learns and improves, suggestions become useful, virtuous learning cycle

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|----------|
| 2025-11-24 | Claude (Sonnet 4.5) | Initial draft based on architecture analysis session and user pain points |

---

## 🎓 Systems Thinking Applied

### Leverage Point Analysis

**This PRD targets Leverage Point #6: Information Flows** (from Meadows' hierarchy)

**Current broken flow:**
- Context is invisible (loaded files unknown)
- Adjustments require restart (5 min restart spiral)
- Discovery is manual (5 min path hunting)
- Learning is absent (same bad suggestions every time)

**New automated flow:**
- Context is visible (`list_context()` shows what's loaded)
- Adjustments are instant (`reload_context()` swaps files in <30 sec)
- Discovery is intelligent (`search_repo()` finds files in <2 sec)
- Learning is automatic (system improves from usage patterns)

**Impact:**
- 100-140 min/week saved (direct time)
- Cognitive load reduction (priceless)
- Enables multi-project scaling (prevents 3-5x friction)
- Foundation for 100,000X workflows

---

### Feedback Loop: Context Learning (Reinforcing)

**Structure:**
```
User selects files → Track usage → Learn patterns → Better suggestions → 
More trust → More usage → Better data → (repeat)
```

**Current state:** Loop is WEAK
- Suggestions don't improve (no learning)
- User doesn't trust suggestions (restart instead)
- No data accumulation (no tracking)

**After Phase 4:** Loop is STRONG
- Tracking captures real usage (Phase 2)
- Learning updates profiles (Phase 4)
- Suggestions improve over time (virtuous cycle)
- User trusts system → uses more → system learns more

**Why this matters:**
- Reinforcing loops compound over time
- Small initial improvement → accelerating returns
- Eventually: System suggests exactly what you need, zero manual adjustment

---

### Amplification Effect

**This work amplifies existing Context Sync Bridge:**
- Context Sync Bridge: Load context at session start
- Live Context Control: Adjust context mid-session
- Combined: Seamless context management throughout entire session

**This work enables multi-project scaling:**
- With 1 project: Context friction is annoying
- With 3 projects: Context friction is 3x worse (restart spiral across projects)
- With 5 projects: Context friction is unbearable without this system
- **Prevention beats cure:** Build this now before scaling pain hits

---

### Alignment with 100,000X Philosophy

You've defined 100,000X as "amplifying cognitive capacity through contemplative technology."

**This system amplifies:**
- **Reduces cognitive load:** No more "which files loaded?" uncertainty
- **Preserves flow state:** No more restart spirals breaking momentum
- **Enables deep work:** Less time managing context = more time creating
- **Compounds over time:** Learning loop means system gets better with use

**This system preserves authenticity:**
- Doesn't replace thinking, amplifies it
- You still make strategic decisions, system just provides right context
- Transparent: Can see why files suggested, what's tracked, what's learned

---

**End of PRD**
