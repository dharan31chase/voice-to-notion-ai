# Tech Requirements - Second Brain Sync

**Project**: Second Brain Sync (Epic 2nd Brain Infrastructure)
**Status**: Day 2 - Tech Requirements Ready for Implementation
**Last Updated**: 2025-12-15
**Owner**: Dharan Chandra Hasan

---

## 📋 Overview

This folder contains detailed technical requirements for implementing the Second Brain Sync system across 6 phases. Each phase document provides step-by-step implementation guidance, testing requirements, rollback plans, and time estimates.

**Total Estimated Time**: 24-28 hours across 6 phases
**Critical Deadline**: Baby arrives Jan 5, 2026 (3 weeks)

---

## 🗂️ Phase Documents

### **Phase 1: PARA Restructure** (P0 - CRITICAL)
**File**: `phase-1-para-restructure.md`
**Estimated Time**: 6-8 hours
**Priority**: P0 (Everything depends on this)

**What**: Restructure both repos (ai-assistant + legacy-ai) to PARA format
**Why Critical**: MCP must work immediately after restructure, zero data loss tolerance
**Success Criteria**:
- ✅ All files moved to PARA structure (projects/areas/resources/archive/)
- ✅ Git history preserved (using git mv)
- ✅ MCP path-mappings.json created and validated
- ✅ MCP "start session" workflow still works (100% success)

**Deliverables**:
- PARA folder structure created
- path-mappings.json config file
- PathMapper module implemented
- All tests passing

---

### **Phase 2: Notion → Repo Sync** (P0)
**File**: `phase-2-notion-to-repo-sync.md`
**Estimated Time**: 6-8 hours
**Priority**: P0 (Core sync functionality)

**What**: Implement Notion → Git sync engine (capture work)
**Success Criteria**:
- ✅ Meeting notes, book notes, research sync from Notion → Git
- ✅ Correct PARA path routing (using routing_table.json)
- ✅ Frontmatter preserved (tags, title, created, last_synced)
- ✅ 95%+ sync success rate

**Deliverables**:
- Sync Engine Python scripts
- routing_table.json config
- sync_state.db schema
- Error handling + retry logic

---

### **Phase 3: Repo → Notion Sync** (P1)
**File**: `phase-3-repo-to-notion-sync.md`
**Estimated Time**: 4-6 hours
**Priority**: P1 (Dashboard visibility)

**What**: Implement Git → Notion sync engine (session work read-only)
**Success Criteria**:
- ✅ PRDs, session logs, tech-requirements sync to Notion (read-only)
- ✅ "View-only" indicator added to synced pages
- ✅ 95%+ sync success rate

**Deliverables**:
- Repo → Notion sync module
- Markdown → Notion blocks parser
- View-only indicator logic

---

### **Phase 4: RAG Reindex** (P1)
**File**: `phase-4-rag-reindex.md`
**Estimated Time**: 3-4 hours
**Priority**: P1 (Semantic search)

**What**: Full reindex of both RAG instances (Epic 2nd Brain + Legacy AI)
**Success Criteria**:
- ✅ Epic 2nd Brain RAG indexes ALL of ai-assistant repo
- ✅ Legacy AI RAG indexes legacy-ai + shared ai-assistant/resources/
- ✅ Cross-repo resource sharing works
- ✅ Search quality validated (spot-check queries)

**Deliverables**:
- Reindexed ChromaDB collections
- Cross-repo sharing configured
- Search quality tests passing

---

### **Phase 5: MCP Intelligence** (P2)
**File**: `phase-5-mcp-intelligence.md`
**Estimated Time**: 3-4 hours
**Priority**: P2 (Quality of life)

**What**: Enhance MCP with project-specific session filtering + work-stream updates
**Success Criteria**:
- ✅ work-stream-mappings.json updated to PARA paths
- ✅ Session filtering by project works (frontmatter.project)
- ✅ RAG integration works (search_rag tool)

**Deliverables**:
- Updated work-stream-mappings.json
- Session filtering logic
- RAG integration in MCP tools

---

### **Phase 6: Testing & Validation** (P0)
**File**: `phase-6-testing-validation.md`
**Estimated Time**: 2-3 hours
**Priority**: P0 (Quality assurance)

**What**: End-to-end testing of entire system
**Success Criteria**:
- ✅ All unit tests passing (70% coverage minimum)
- ✅ Integration tests passing (sync flows, MCP context loading)
- ✅ E2E test passing (mobile capture → desktop access workflow)
- ✅ 95%+ test pass rate

**Deliverables**:
- Test suite (unit + integration + E2E)
- Golden dataset (3 test files)
- Test report

---

## 📊 Phase Dependencies

```
Phase 1: PARA Restructure (MUST complete first)
    ↓
    ├─→ Phase 2: Notion → Repo Sync (can start after Phase 1)
    │       ↓
    ├─→ Phase 3: Repo → Notion Sync (can start after Phase 1)
    │       ↓
    └─→ Phase 4: RAG Reindex (can start after Phase 1)
            ↓
        Phase 5: MCP Intelligence (can start after Phase 4)
            ↓
        Phase 6: Testing & Validation (LAST - validates everything)
```

**Parallel Execution**:
- Phases 2, 3, 4 can run in parallel (after Phase 1 complete)
- Phase 5 requires Phase 4 complete (RAG integration)
- Phase 6 runs last (validates all previous phases)

---

## ⏱️ Time Estimates Breakdown

| Phase | Optimistic | Realistic | Pessimistic | Priority |
|-------|------------|-----------|-------------|----------|
| Phase 1: PARA Restructure | 6h | 7h | 8h | P0 |
| Phase 2: Notion → Repo Sync | 6h | 7h | 8h | P0 |
| Phase 3: Repo → Notion Sync | 4h | 5h | 6h | P1 |
| Phase 4: RAG Reindex | 3h | 3.5h | 4h | P1 |
| Phase 5: MCP Intelligence | 3h | 3.5h | 4h | P2 |
| Phase 6: Testing & Validation | 2h | 2.5h | 3h | P0 |
| **TOTAL** | **24h** | **28.5h** | **33h** | |

**Working Schedule** (if working 4 hours/day):
- Day 3: Phase 1 (PARA Restructure) - 7 hours
- Day 4: Phase 2 (Notion → Repo Sync) - 7 hours
- Day 5: Phase 3 (Repo → Notion Sync) + Phase 4 start - 5 + 1.5 hours
- Day 6: Phase 4 complete + Phase 5 - 2 + 3.5 hours
- Day 7: Phase 6 (Testing) - 2.5 hours

**Buffer**: 1-2 days for unexpected issues

---

## 🚨 Critical Risks

### **Risk 1: PARA Restructure Breaks MCP** (P0)
**Probability**: Medium
**Impact**: CATASTROPHIC (workflow broken, 10-15 min context loading)

**Mitigation**:
- Create path-mappings.json BEFORE restructure
- Test PathMapper with current paths BEFORE restructure
- Run MCP validation tests IMMEDIATELY after restructure
- Keep fallback enabled during transition
- Rollback plan: Revert git commits, restore old paths

**Covered in**: Phase 1 tech-req (detailed migration strategy)

---

### **Risk 2: Data Loss During Restructure** (P0)
**Probability**: Low (if following plan)
**Impact**: CATASTROPHIC (loss of work, broken Git history)

**Mitigation**:
- Pre-migration file inventory (count all files)
- Use git mv (preserves history), NOT mv
- Post-migration verification (count files, compare to inventory)
- Tests MUST verify: File count matches, Git log intact
- Rollback plan: Git branch protection, revert commits

**Covered in**: Phase 1 tech-req (zero data loss constraints)

---

### **Risk 3: Notion API Rate Limits** (P1)
**Probability**: Medium (during large syncs)
**Impact**: Partial sync failure, some notes not synced

**Mitigation**:
- Exponential backoff on 429 errors
- Batch operations (query 100 notes at once)
- Respect 3 req/s limit (add delays)
- Error queue for retry on next sync
- Tests simulate rate limit scenarios

**Covered in**: Phase 2 & 3 tech-req (error handling)

---

### **Risk 4: Sync Fails Silently** (P1)
**Probability**: Medium
**Impact**: Context gaps, manual copy-paste workaround

**Mitigation**:
- Sync logs written on every run
- Error queue captures failed syncs
- Weekly manual review of sync logs (spot-check)
- Tests verify sync logs exist and contain expected data

**Covered in**: Phase 2 & 3 tech-req (logging requirements)

---

## 📝 Document Format (Standardized)

Each phase document follows this structure:

```markdown
# Tech Requirements: [Phase Name]

**Phase**: X of 6
**Estimated Time**: X hours
**Priority**: [P0 | P1 | P2]
**Dependencies**: [What must be complete before this]

## Goal
[One sentence: What does this phase accomplish?]

## Success Criteria
- [ ] Measurable outcome 1
- [ ] Measurable outcome 2

## Technical Approach
[Step-by-step implementation plan]

## Data Structures
[Config files, frontmatter schemas, etc.]

## API Calls
[Notion API, GitHub API endpoints needed]

## Error Handling
[What could go wrong, how to handle it]

## Testing Requirements
- Unit tests: [What to test]
- Integration tests: [What to test]
- E2E tests: [What to test]

## Rollback Plan
[If this phase fails, how to revert]

## Files Changed
[List of files that will be created/modified]

## Time Estimate Breakdown
- Setup: X hours
- Implementation: X hours
- Testing: X hours
- Documentation: X hours
```

---

## 🔗 Related Documentation

**Project Documentation**:
- `../prd.md` - Product requirements (all decisions locked)
- `../vision.md` - 5-year architectural strategy
- `../architecture/` - System architecture (Day 2 deliverable)

**Reference Materials**:
- `../Building_a_Second_Brain___Tiago_Forte.md` - PARA methodology
- `../Systems_Thinking_Workbook__Energy___Voice-to-Notion.md` - Systems thinking
- `../handoff-to-claude-code-day-2.md` - Day 2 mission brief

---

## ✅ Implementation Readiness Checklist

**Before Starting Phase 1**:
- [x] Architecture documentation complete
- [x] Tech requirements reviewed with Dharan
- [ ] All blockers resolved (standard structure, tag routing, Notion schema)
- [ ] Development environment ready (Python 3.11+, Git, API keys)

**After Each Phase**:
- [ ] All tests passing for that phase
- [ ] Documentation updated
- [ ] Rollback plan tested (at least for P0 phases)
- [ ] Next phase dependencies satisfied

**Before Marking Project Complete**:
- [ ] All 6 phases complete
- [ ] End-to-end workflow tested (mobile capture → desktop access)
- [ ] 2X leverage validated (context load <3 min vs 10-15 min)
- [ ] Ready for daily use (1am/1pm syncs operational)

---

## 📞 Support & Questions

**If blocked during implementation**:
1. Check architecture docs (`../architecture/`) for design decisions
2. Check PRD (`../prd.md`) for product requirements
3. Review handoff document (`../handoff-to-claude-code-day-2.md`) for context
4. Document assumption, proceed with best judgment, flag for Dharan review

**Communication**:
- Document questions in session logs
- Provide options with recommendations
- Default to PRD decisions (don't relitigate)

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-15 | Claude Code (Sonnet 4.5) | Initial tech requirements overview |

---

**Status**: ✅ Tech requirements structure complete

**Next Step**: Review individual phase documents for implementation guidance

**Ready for Day 3**: Begin Phase 1 implementation (PARA Restructure)
