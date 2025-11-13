# One-Pager: Multi-Project Expansion

**Initiative**: Multi-Project Expansion  
**Category**: Context Sync Bridge  
**Owner**: Dharan Chandra Hasan  
**Created**: 2025-11-11  
**Status**: Ready to Build  
**Notion Initiative**: [Multi-Project Expansion](https://www.notion.so/Multi-Project-Expansion-2a68369c730581b5afc0fd2bb1486e39)

---

## Background

You built Context Sync Bridge for Epic 2nd Brain. It works beautifully - MCP tools load context in <3 minutes (down from 10-15), git hooks auto-sync to Notion, session logs preserve all decisions.

But you're not just building Epic 2nd Brain. You're simultaneously:
- Running **Legacy AI** (customer discovery: 5 of 30 interviews done)
- Planning a **home remodel** (quotes, timelines, design decisions)
- Exploring future ventures (contemplative technology, 100,000X workflows)

Right now, Context Sync Bridge only works for ONE project. Every PRD, session log, and roadmap item assumes "Epic 2nd Brain." Your customer discovery notes live in Notion PARA but aren't searchable through MCP tools. Your home remodel planning has no structure.

**The structural problem**: You built single-project infrastructure in a multi-project reality.

With your baby arriving January 2026 (7 weeks away), you need systems that scale across ALL your work - not just one project.

---

## Problem Statements

### From Your Perspective (Solo Founder)
You're context-switching between projects 3-5 times per day:
- Morning: Epic 2nd Brain (deep work)
- Midday: Legacy AI (customer calls)
- Evening: Home remodel (contractor coordination)

Each switch requires:
- **5-10 minutes** recalling project state ("where did we leave off?")
- **3-5 searches** through Notion, chat history, email
- **Mental overhead** keeping project boundaries clear

You're losing **30-60 minutes per day** to context switching overhead. That's **3.5-7 hours per week** - nearly a full workday.

### From the System Perspective (Context Sync Bridge)
Current architecture hardcodes "Epic 2nd Brain" assumptions:
- `start_session()` has no project parameter
- `docs/` folder structure assumes single project
- Notion sync targets one roadmap database
- MCP tools can't filter by project

The system works perfectly... for ONE project. Adding a second project would require duplicating the entire setup or polluting docs with mixed content.

### From Claude Chat's Perspective (Strategy Agent)
When you say "Start session," I don't know which project you're working on. I could load:
- Epic 2nd Brain context (wrong if you're doing Legacy AI)
- Legacy AI context (wrong if you're doing Epic 2nd Brain)
- Both (information overload, slows everything down)

I need explicit project scoping to load the RIGHT context, not ALL context.

### From Claude Code's Perspective (Implementation Agent)
When I receive a handoff prompt, I need to know:
- Which project's docs to read
- Which roadmap to update
- Which git branch conventions to follow
- Which Notion databases to sync with

Without project context, I'd mix Legacy AI customer insights into Epic 2nd Brain PRDs. That's chaos.

---

## Goals

**Must Have**:
1. **Project-scoped sessions** - "Start session for Legacy AI" loads ONLY Legacy AI context
2. **Multi-project docs structure** - Each project has its own PRDs, sessions, roadmap
3. **Filtered MCP tools** - `search_docs(project="Legacy AI")` returns only relevant results
4. **Project-aware Notion sync** - Git hooks update the correct Notion database per project
5. **Zero cross-contamination** - Epic 2nd Brain decisions never pollute Legacy AI context

**Success Metrics**:
- Context switch overhead: **30-60 min/day → <10 min/day** (80%+ reduction)
- Context loading accuracy: **100%** (zero cross-contamination)
- System scales to **5-10 active projects** without performance degradation
- Setup time for new project: **<30 minutes** (copy templates, configure Notion)

**Non-Goals**:
- Cross-project search (e.g., "show me all PRDs across all projects") - Deferred to Phase 2
- Automatic project detection from context (too error-prone) - Explicit is better
- Shared resources between projects (e.g., contact databases) - Each project is isolated for V1
- Unified priority scoring across projects - Each project has its own Strategy Board

---

## Hypothesis

**If** we extend Context Sync Bridge to support multiple projects with explicit scoping,  
**Then** Dharan can context-switch between Epic 2nd Brain, Legacy AI, and home remodel in <2 minutes per switch,  
**Because** the system loads ONLY relevant context (not everything), preserving mental clarity and reducing cognitive load.

**Size of Win**: 
- **Time saved**: 30-60 min/day → ~4-6 hours/week → **200-300 hours/year**
- **Cognitive leverage**: Enables parallel project development (not just sequential)
- **Baby deadline alignment**: System scales to handle reduced time availability (January 2026)
- **100,000X foundation**: Multi-project infrastructure is prerequisite for contemplative technology workflows

**Risk if we're wrong**: 
- Additional complexity might slow down single-project work (mitigation: project parameter is optional, defaults to Epic 2nd Brain)
- Setup overhead per project might be prohibitive (mitigation: templates + 30-min setup checklist)

---

## Vision Narrative

**Morning - 7:30am**

You sit down for deep work. Open Claude Desktop.

> "Start session for Epic 2nd Brain"

Claude responds in 8 seconds:
- Top 3 Strategy Board initiatives (Epic 2nd Brain only)
- Latest PRD: Multi-Project Expansion (this project!)
- Recent session: Strategy Board workflow implementation
- Zero mention of Legacy AI or home remodel

You dive into coding. No mental overhead. No "wait, which project am I on?" confusion.

**Midday - 12:30pm**

Customer discovery call just finished. You have 15 minutes before lunch to capture insights.

> "Start session for Legacy AI"

Claude responds in 6 seconds:
- Customer Interview #5 notes (from Notion PARA)
- Pain points identified so far (aggregated)
- Next interview scheduled (from project roadmap)
- Zero mention of Epic 2nd Brain infrastructure

You record voice notes about the interview. Voice-to-Notion pipeline automatically tags them "Project: Legacy AI" and routes to the correct database.

**Evening - 6pm**

Contractor just emailed updated kitchen quote. You need to decide by tomorrow.

> "Start session for Home Remodel"

Claude responds in 5 seconds:
- Previous quotes comparison (from project docs)
- Budget constraints (from one-pager)
- Timeline dependencies (kitchen → flooring → painting)
- Zero mention of Epic 2nd Brain or Legacy AI

You discuss trade-offs with Claude, make a decision, log it. Git hook syncs to "Home Remodel" Notion database.

**The Difference**:
- **Before**: 5-10 min per switch digging through Notion, chat history, email
- **After**: <10 seconds to load context, immediate mental clarity
- **Multiplied**: 3-5 switches/day × 5-10 min = **30-60 min/day saved**

---

## Rough Scoping & Timeline

### Phase 1: Architecture (Day 1-2, 4-6 hours)
**What**: Extend existing MCP tools + git hooks to support project parameter

**Changes**:
- `start_session(project_name)` - Add project parameter (default: "Epic 2nd Brain")
- `end_session(project_name)` - Add project parameter
- `search_docs(query, project_name)` - Filter by project
- Docs structure: `docs/projects/epic-2nd-brain/`, `docs/projects/legacy-ai/`
- Git hooks: Read project name from file path, sync to correct Notion database
- Config: `config/projects.yaml` - Map project names to Notion database IDs

**Validation**: 
- Start session for Epic 2nd Brain → loads Epic context only ✅
- Start session for Legacy AI → loads Legacy context only ✅
- Search "customer pain points" with project=Legacy AI → correct results ✅

---

### Phase 2: Legacy AI Integration (Day 3-4, 4-6 hours)
**What**: Migrate existing Legacy AI notes + create project structure

**Tasks**:
- Create `docs/projects/legacy-ai/` folder structure
- Migrate customer discovery notes from Notion PARA to new structure
- Create Legacy AI roadmap in `docs/projects/legacy-ai/roadmap.md`
- Configure Notion database for Legacy AI in `config/projects.yaml`
- Test full workflow: start session → create PRD → end session → Notion sync

**Validation**:
- Customer interview notes searchable via MCP tools ✅
- Legacy AI has its own Strategy Board view in Notion ✅
- Zero cross-contamination with Epic 2nd Brain ✅

---

### Phase 3: Home Remodel Setup (Day 5, 2-3 hours)
**What**: Prove system scales to non-software projects

**Tasks**:
- Create `docs/projects/home-remodel/` folder structure
- Document existing quotes, timelines, decisions as PRDs
- Create home remodel roadmap
- Configure Notion database
- Test voice-to-Notion routing ("Project: Home Remodel")

**Validation**:
- System handles 3 active projects without slowdown ✅
- Setup time for new project: <30 minutes ✅
- Non-technical projects work as smoothly as software projects ✅

---

### Phase 4: Documentation & Templates (Day 6, 2-3 hours)
**What**: Make it easy to add future projects

**Deliverables**:
- "New Project Setup" checklist (< 30 min per project)
- Project template structure (copy-paste ready)
- Updated README with multi-project examples
- Troubleshooting guide (common issues + fixes)

**Validation**:
- Someone (or you in 3 months) can add a new project in <30 minutes ✅

---

**Total Effort**: 12-18 hours across 6 days (2-3 hours per day)  
**Timeline**: November 12-17, 2025 (fits within baby deadline)  
**Payback Period**: 3-4 weeks (200-300 hours/year saved)

---

## Key Trade-Offs & Decisions

### Decision 1: Explicit Project Scoping (Not Automatic Detection)
**Options**:
- A: Infer project from context (chat history, file paths, keywords)
- B: Require explicit `project_name` parameter in every tool call
- C: Set "active project" at session start, carry through session

**Choice**: Option B (explicit parameter)

**Why**: 
- **Predictable**: No "wrong project detected" errors
- **Simple**: Clear mental model (you always know which project you're on)
- **Debuggable**: When things break, obvious where to look

**Trade-offs**: 
- Slightly more verbose (`start_session(project="Legacy AI")` vs `start_session()`)
- User must remember which project they're working on (but this is the point - mental clarity!)

---

### Decision 2: Isolated Project Structures (Not Shared Resources)
**Options**:
- A: Each project has its own docs, roadmap, Notion database (fully isolated)
- B: Shared resources (contacts, templates, research) across projects
- C: Hybrid (isolated docs, shared resources)

**Choice**: Option A (fully isolated)

**Why**:
- **Clean boundaries**: No ambiguity about what belongs where
- **Prevents contamination**: Epic 2nd Brain customer feedback never leaks into Legacy AI
- **Scales simply**: Adding project = copy template, no dependency mapping

**Trade-offs**:
- Duplicated templates per project (acceptable - disk is cheap)
- Can't easily search "all customer feedback across all projects" in V1 (deferred to Phase 2)

---

### Decision 3: Project Name in File Path (Not Metadata)
**Options**:
- A: Encode project in folder structure (`docs/projects/epic-2nd-brain/`)
- B: Add project metadata to frontmatter of every doc
- C: Store project mapping in separate database

**Choice**: Option A (folder structure)

**Why**:
- **Visual clarity**: File explorer shows project boundaries
- **Git-friendly**: Easy to see what changed per project in git diff
- **Tool-agnostic**: Works with `ls`, `grep`, any file browser (not just MCP tools)

**Trade-offs**:
- Deeper folder nesting (`docs/projects/epic-2nd-brain/prd/` vs `docs/prd/`)
- Moving docs between projects requires file path changes (rare operation)

---

### Decision 4: Per-Project Notion Databases (Not Views)
**Options**:
- A: One Notion database, filtered views per project
- B: Separate Notion database per project
- C: No Notion sync (repo only)

**Choice**: Option B (separate databases)

**Why**:
- **Clean Strategy Boards**: Each project has its own priority scoring
- **No filter maintenance**: Views don't break when you add new properties
- **Future collaboration**: Easier to share one project's Notion without exposing others

**Trade-offs**:
- More Notion setup per project (30 min vs 5 min for new view)
- Can't compare priorities across projects in single view (not a goal)

---

### Decision 5: Default Project = "Epic 2nd Brain" (Backward Compatible)
**Options**:
- A: Require project parameter (breaking change)
- B: Default to "Epic 2nd Brain" if not specified (backward compatible)
- C: Default to "last used project" (stateful)

**Choice**: Option B (default to Epic 2nd Brain)

**Why**:
- **Zero breaking changes**: Existing workflows continue working
- **Gradual adoption**: Can add project parameter as you adopt multi-project
- **Clear primary project**: Epic 2nd Brain is 80% of work, makes sense as default

**Trade-offs**:
- Could accidentally load Epic 2nd Brain context when you meant Legacy AI (user error, but explicit parameter makes it obvious)

---

## Success Validation

**Week 1 (November 12-17): Implementation + Dogfooding**
- [ ] Phase 1-4 complete (12-18 hours)
- [ ] Test with 3 real projects (Epic 2nd Brain, Legacy AI, Home Remodel)
- [ ] Measure context switch time: Target <10 min/day, <2 min per switch
- [ ] Measure setup time for Home Remodel: Target <30 min

**Week 2-3 (November 18-30): Validation**
- [ ] Use multi-project system for 2 weeks
- [ ] Track: Context switches per day, time saved, errors (wrong project loaded)
- [ ] Validate: Zero cross-contamination (no Epic 2nd Brain PRDs referencing Legacy AI)
- [ ] Confirm: System scales to 3-5 active projects without performance degradation

**Gate to Next Phase**:
- If context switch time not <10 min/day → Investigate bottlenecks before expanding
- If setup time for new project >30 min → Simplify templates before adding more projects
- If cross-contamination >0 → Fix isolation before relying on system for critical work

---

## Next Steps After This One-Pager

1. **Review & Approve** (you + Claude Chat)
   - Does this solve the right problem?
   - Are trade-offs acceptable?
   - Is timeline realistic (12-18 hours)?

2. **Create PRD** (Claude Chat)
   - Expand problem statement with user stories
   - Detail technical requirements for each phase
   - Define success criteria with measurements

3. **Handoff to Claude Code** (Claude Chat → Claude Code)
   - Create handoff prompt with implementation mode: Interactive
   - Claude Code asks clarifying questions before coding
   - Claude Code implements Phase 1-4 over 6 days

4. **Dogfood & Iterate** (you + both Claudes)
   - Test with real projects
   - Measure time savings
   - Refine based on friction points

---

**End of One-Pager**
