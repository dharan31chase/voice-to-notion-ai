# One-Pager: RAG Implementation for Legacy AI

**Status**: In Progress
**Project**: Infrastructure
**Owner**: Dharan Chandrahasan
**Created**: 2025-11-18
**Last Updated**: 2025-11-18

---

## TL;DR

Implement hybrid RAG (BM25 + semantic embeddings + BGE local re-ranking) for Legacy AI customer discovery corpus (208k tokens). Enable instant search across all customer interviews in <1 second, eliminating 10-15 minutes of manual context loading per session. Privacy-first architecture with 100% local processing.

---

## Why This Matters

**Problem**: Legacy AI corpus crossed 208k tokens (over 200k context limit), causing:
- 10-15 minutes manually loading context every session
- 60-80% of interview data never gets considered
- Impossible to answer "What did all customers say about X?"
- Analysis workflow breaks at 10+ interviews (can't fit in context)

**Opportunity**: Instant search across entire corpus enables comprehensive synthesis impossible manually. Automated analysis workflows that scale to 30+ interviews.

**Impact**:
- 70-120 min/week saved (context loading + synthesis)
- Cross-interview patterns become visible
- Evidence-based product decisions (search all data instantly)
- Analysis workflows that work at any corpus size
- Privacy-first: 100% local processing (BGE local, no third-party APIs)

---

## Current Status

**Phase**: Build (Phase 1 - Core Implementation)

**Progress**: Day 1 of 4

**Timeline**:
- Day 1 (Nov 18): Setup (Chroma, BGE, OpenAI API) - **Today**
- Day 2 (Nov 19): Indexing pipeline (header-based chunking, auto daily reindex)
- Day 3 (Nov 20): Search implementation (BM25, semantic, BGE re-rank, MCP tools)
- Day 4 (Nov 21): Testing & validation (accuracy >60%, Story 6 workflow)
- Phase 2 (Nov 25-29): Real usage validation

**Blockers**:
- None currently

**Next Steps**:
1. Approve tech requirements (in review)
2. Set up development environment
3. Download BGE model (1.3 GB)
4. Create project structure

---

## Key Decisions Made

1. **BGE Local Re-ranking** (not Cohere): 100% private, $0/month, 60-65% accuracy
2. **Header-based Chunking** (not token-based): Respects markdown structure
3. **Auto Daily Reindex** (7am cron): Zero maintenance
4. **Chroma Local** (not Pinecone): Free, sufficient for <500k corpus
5. **Desktop-First**: $100/month (no API costs), Claude Max covers it

---

## Success Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| Context loading | <10 sec | Time `start_session` |
| Search speed | <1 sec | Time `search_interviews` |
| Search relevance | >60% | Review top-10 results |
| Manual copy-paste | 0 events | User confirmation |
| Cross-interview synthesis | Works | Test query |
| Automated analysis | Works | Story 6 workflow |
| Cost | $100/month | No new costs |
| Privacy | 100% local | Audit API calls |

---

## Implementation Artifacts

**PRD**:
- [RAG Implementation PRD](../../../prd/rag-implementation-legacy-ai.md)

**Tech Requirements**:
- [RAG Implementation Tech Requirements](../../../tech-requirements/rag-implementation-legacy-ai.md)

**Architecture**: (to be created)
- `docs/architecture/rag-architecture.md`

**Implementation**:
- `ai-assistant/scripts/rag/` (in progress)

---

## Effort Estimate

**Phase 1 (This Week)**: 10.5-12.5 hours
- Setup: 2-3 hours
- Indexing: 3-4 hours
- Search: 3-4 hours
- Testing: 2-3 hours

**Phase 2 (Next Week)**: 2-3 hours
- Real usage validation
- Optimization if needed

**Total**: 12.5-15.5 hours

---

## Related Initiatives

- **Context Sync Bridge** (complete): Foundation MCP infrastructure
- **Applied Context Engineering** (in progress): Research that informed this PRD
- **RAG Expansion to Epic 2nd Brain** (future): 2-4 hours when triggered

---

## Notes

This is Tier 1 of the RAG architecture. Future tiers:
- Tier 2: Pinecone cloud (when team scales or >500k corpus)
- Tier 3: API automation (when autonomous agents needed)

Privacy is paramount - customer interview data contains sensitive family stories. BGE local ensures no data leaves your laptop.

---

**Strategy Board**: [Notion Link](https://www.notion.so/2aa8369c7305805cb2dded2bb3ca7c56)
