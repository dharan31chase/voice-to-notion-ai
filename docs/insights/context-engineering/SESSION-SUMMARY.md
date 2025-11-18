# Context Engineering Research: Session Summary

**Date**: November 18, 2025  
**Session Goal**: Deep-dive into Anthropic's contextual retrieval research and apply to Epic 2nd Brain  
**Status**: ✅ Complete - Documentation captured

---

## What We Created

A complete context engineering knowledge base in `docs/insights/context-engineering/`:

1. **README.md** - Navigation hub and learning path
2. **fundamentals.md** - Core concepts (chunking, BM25, embeddings, caching)
3. **anthropic-contextual-retrieval-insights.md** - Research findings and performance data
4. **application-to-epic2b.md** - Specific recommendations for your system
5. **decision-framework.md** - Vendor comparison and cost-benefit analysis
6. **next-steps.md** - Action items for next session
7. **testing-protocols.md** - Shell for future testing procedures
8. **migration-guides.md** - Shell for Tier 0→Tier 1 transition

---

## Key Insights Captured

### **1. You Don't Need RAG Yet**

**Finding**: Your corpus (189k tokens) is below 200k threshold → use prompt caching instead

**Impact**: 
- Saves 6-8 hours in Tier 0
- Simpler architecture
- Better accuracy (zero retrieval failures)
- Cheaper ($25-35/month vs $55-125)

**Action**: Update Context Sync Bridge PRD Phase 5

---

### **2. Contextual Embeddings = 49-67% Better Accuracy**

**Finding**: Adding context to chunks before embedding dramatically improves retrieval

**Performance**:
- Regular embeddings: 5.7% failure rate
- Contextual embeddings: 3.7% (35% better)
- + BM25: 2.9% (49% better)
- + Reranking: 1.9% (67% better)

**Action**: Plan for Tier 1 when corpus >200k tokens

---

### **3. Prompt Caching Makes It Economically Viable**

**Finding**: $1.02 per million tokens (vs $20-30 without caching)

**Your Cost**:
- Tier 0 (prompt caching): $20-35/month
- Tier 1 (RAG): $55-125/month
- But ROI is 8-34x regardless

**Action**: Test prompt caching in next session

---

### **4. Hybrid Search (BM25 + Embeddings) is Best**

**Finding**: Combining keyword and semantic search gives best results

**Why**: 
- BM25 finds exact terms ("MCP server")
- Embeddings find meaning ("context loading")
- Together = 49% better than embeddings alone

**Action**: Implement in Tier 1 (not Tier 0)

---

### **5. Track Corpus Size Automatically**

**Finding**: Need early warning when approaching 200k threshold

**Trigger Points**:
- 180k tokens: Start planning RAG
- 190k tokens: Alert - approaching limit
- 200k tokens: Must implement RAG

**Action**: Add to Phase 2 git hooks

---

## Major PRD Changes Required

### **Context Sync Bridge Updates**

**Phase 5 (OLD)**:
```
Phase 5 (Day 10-12): RAG search implementation (6-8 hours)
- Simple keyword matching vs semantic embeddings
- Decision: Which approach to use?
```

**Phase 5 (NEW)**:
```
Phase 5 (Day 10-12): Prompt Caching Optimization (4-6 hours)
- Implement full-corpus caching in MCP
- Add corpus size monitoring
- Test cache performance
- Document RAG transition criteria

Rationale: Corpus (189k) below 200k threshold - RAG premature
```

**New Phase 7 (Tier 1 - When Adding Legacy AI)**:
```
Phase 7: Contextual Retrieval RAG (6-8 hours)
- Contextual chunking + embedding
- Hybrid search (Voyage embeddings + BM25)
- Vector DB integration (Weaviate)
- Optional reranking if failure rate >3%

Trigger: Corpus exceeds 200k tokens (adding Legacy AI)
```

---

## Vendor Recommendations

### **Tier 0 (Prompt Caching)**
- **Primary**: Claude API only (no additional vendors)
- **Cost**: $20-35/month

### **Tier 1 (RAG)**
- **Embeddings**: Voyage AI ($0.06/M tokens)
  - Alternative: Google Gemini ($0.025/M tokens) if cost-sensitive
- **Vector DB**: Weaviate Cloud ($25/month)
  - Alternative: Pinecone ($70/month) if need scale
- **Reranking**: Voyage rerank-lite ($0.05/M tokens)
  - Alternative: Cohere ($1/M tokens) if need performance
- **Total Cost**: $55-125/month

---

## Immediate Next Steps

**Priority 1: Update PRD** (30-45 min)
- Revise Phase 5 description
- Add Phase 7 (Tier 1) outline
- Link to context-engineering docs
- Location: `docs/prd/context-sync-bridge.md`

**Priority 2: Test Prompt Caching** (1-2 hours)
- Validate approach with real test
- Measure latency, cost, cache hit rate
- Document results in session log
- Go/no-go decision for Phase 5

**Priority 3: Add Corpus Tracking** (1-2 hours)
- Script to count tokens
- Git hook integration
- Alert at 190k tokens

**Priority 4: Update Roadmap** (30 min)
- Notion roadmap reflects Phase 5 change
- Add Tier 1 trigger conditions
- Link to context-engineering folder

---

## Open Questions

**For Peter (Engineering)**:
1. Any risk with full-corpus caching at 189k tokens?
2. How to maximize cache hits across sessions?
3. Token counting accuracy - better than word count × 0.75?

**For Kevin (Business)**:
1. Is $1,720 Year 1 budget reasonable?
2. Accelerate Tier 1 planning even if corpus <200k?
3. Balance Epic 2nd Brain vs Legacy AI priority?

---

## Success Metrics

**Tier 0 Targets**:
- Context loading: <30 seconds (warm cache)
- Cache hit rate: >80%
- Cost per session: <$0.10
- Retrieval failures: 0%

**Tier 1 Targets** (future):
- Retrieval failure rate: <3%
- Query latency: <500ms
- Cost per query: <$0.01

---

## How to Use This Documentation

### **For Learning**:
1. Start with README.md (navigation)
2. Read fundamentals.md (understand concepts)
3. Read anthropic-contextual-retrieval-insights.md (see research)
4. Read application-to-epic2b.md (specific recommendations)

### **For Decision-Making**:
1. Review decision-framework.md (vendor comparisons, cost-benefit)
2. Check next-steps.md (immediate actions)
3. Consult with coaches (questions prepared)

### **For Implementation**:
1. Follow next-steps.md action items
2. Use fundamentals.md as technical reference
3. Fill in testing-protocols.md during Phase 5
4. Complete migration-guides.md before Tier 1

---

## ROI Summary

**Investment**:
- Tier 0 development: $400-600 (4-6 hours)
- Tier 0 infrastructure: $240-420/year (Claude API)
- **Total Year 1**: $640-1020

**Return**:
- Time saved: 70-120 min/week = $6,000-10,000/year
- Avoided rework: ~$12,000/year (missed decisions)
- **Total Value**: $18,000-22,000/year

**ROI**: 18-34x return on investment

---

## What Makes This Different

Traditional RAG guides tell you to build RAG. This research shows:

1. **Know when NOT to build**: <200k tokens = prompt caching is better
2. **Build incrementally**: Tier 0 → Tier 1 → Tier 2 as needs grow
3. **Context is everything**: Contextual embeddings (49-67% better) vs regular RAG
4. **Economics matter**: Prompt caching changed the game ($1.02 vs $20/M tokens)
5. **Hybrid beats pure**: BM25 + embeddings better than either alone

---

**Next Session Goal**: Test prompt caching and update PRD

**Location of All Docs**: `docs/insights/context-engineering/`

**Status**: Ready for learning and implementation
