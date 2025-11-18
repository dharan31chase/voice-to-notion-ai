# Decision Framework for Context Engineering

**Purpose**: Vendor selection, cost-benefit analysis, and trade-off evaluation  
**Audience**: Business owner making architecture decisions  
**Last Updated**: November 18, 2025 (Architecture Clarified)  
**Critical Update**: Desktop-first (Tier 0-2), API optional (Tier 3+)

---

## 🎯 Core Architecture Decision: Desktop vs API

### **First Principle: Interface ≠ Business Logic**

```
┌────────────────────────────────────────┐
│ INTERFACE (How you interact)          │
│ • Tier 0-2: Claude Desktop (Max $100) │
│ • Tier 3+: API agents (optional)      │
├────────────────────────────────────────┤
│ BUSINESS LOGIC (How it works)         │
│ • Tier 0: Prompt caching              │
│ • Tier 1-2: Contextual RAG            │
│ • Same logic works for both!          │
└────────────────────────────────────────┘
```

**Key Insight**: You can use RAG in Claude Desktop (no API needed). API is only for autonomous agents.

---

## Decision Tree: Interface Selection

```
START: Do I need agents running WITHOUT me?
  ↓
  ├─ NO → Use Claude Desktop (Tier 0-2)
  │        Cost: $100-125/month (Max + optional DB)
  │        Interface: Interactive (you in conversation)
  │        Use Cases: All current workflows
  │
  └─ YES → Add API Wrapper (Tier 3+)
           Cost: +$40-60/month (API charges)
           Interface: Autonomous (agents run alone)
           Use Cases: Scheduled reports, background processing
```

### **Follow-Up: Corpus Size (Within Desktop Interface)**

```
Within Desktop, what context approach?
  ↓
Is corpus < 200k tokens?
  ├─ YES → Use Prompt Caching (Tier 0)
  │        Load full corpus into Desktop
  │        Covered by Max subscription
  │
  └─ NO → Use Contextual RAG (Tier 1-2)
          Smart retrieval → Desktop
          $0-25/month for vector DB
```

---

## Vendor Comparison Matrix

### **Embedding Models** (Tier 1+ Only)

| Provider | Model | Cost (per 1M tokens) | Performance | Your Context |
|----------|-------|----------------------|-------------|--------------|
| **Voyage AI** | voyage-2 | $0.06 | Best | Also has reranker (single vendor) |
| **Google Gemini** | text-embedding-004 | $0.025 | Best (tied) | Need Google Cloud setup |
| **OpenAI** | text-embedding-3-small | $0.02 | Good | Already using for voice pipeline |

**Recommendation**:
- **Tier 0**: N/A (not using embeddings, full-corpus caching)
- **Tier 1**: Voyage (embeddings + reranking in one package)
- **Alternative**: Gemini if optimizing for cost ($0.025 vs $0.06)

**Note**: One-time cost (~$0.70 for 689k corpus). Monthly cost is negligible (only new docs).

---

### **Vector Databases** (Tier 1+ Only)

| Provider | Free Tier | Paid Tier | Complexity | Your Context |
|----------|-----------|-----------|------------|--------------|
| **Chroma** | Free (local) | N/A | Low | No cloud costs, DIY setup |
| **Weaviate** | Self-hosted | $25/month cloud | Medium | Open source, good balance |
| **Pinecone** | 1M vectors | $70/month | Low | Easiest, but expensive |

**Recommendation**:
- **Development**: Chroma (free, fast iteration)
- **Production (Tier 1)**: Start with Chroma ($0), switch to Weaviate ($25) if needed
- **Scale (Tier 2+)**: Evaluate based on actual needs

**Why Start Local**: Your corpus (820k tokens) is small. Save $25/month until you need cloud scale.

---

### **Reranking Models** (Tier 1 Optional)

| Provider | Model | Cost (per 1M tokens) | Integration |
|----------|-------|----------------------|-------------|
| **Voyage** | rerank-lite-1 | $0.05 | Same vendor as embeddings |
| **Cohere** | rerank-english-v3.0 | $1.00 | Separate API |

**Recommendation**:
- **Tier 1**: Test without reranking first (hybrid BM25 + embeddings might be enough)
- **If failures >3%**: Add Voyage reranking (~$0.50/month for 10k queries)

**Decision Rule**: Don't optimize prematurely. Test, then add if needed.

---

## Cost-Benefit Analysis (CORRECTED)

### **Tier 0: Claude Desktop + Prompt Caching**

**Costs**:
- Development: 4-6 hours ($400-600 at $100/hr)
- **Claude Max**: $100/month (flat fee, unlimited)
- MCP Server: $0/month (local)
- **Total Year 1**: $1,600-1,800 (dev + $1,200 annual Max)

**Benefits**:
- Time saved: 70-120 min/week = 60-100 hours/year
- Value: $6,000-10,000/year (at $100/hr)
- Avoided rework: ~5 "what did we decide?" moments/month = 10 hours/month = $12,000/year
- **Total Value**: $18,000-22,000/year

**ROI**: 10-14x return

**Risk**: Corpus growth beyond 200k (mitigated by monitoring)

---

### **Tier 1: Claude Desktop + Contextual RAG**

**Costs**:
- Development: 6-8 hours ($600-800)
- Setup: $0.70 (contextualizing 689k corpus via API - one-time)
- **Claude Max**: $100/month (same flat fee)
- **Vector DB**: $0-25/month (Chroma local = free, Weaviate cloud = $25)
- Embeddings: ~$1/month (incremental updates)
- **Total Year 1**: $1,800-2,100 (dev + $1,200 Max + $0-300 DB)

**Benefits**:
- Time saved: Same as Tier 0 (70-120 min/week)
- Accuracy: 97-98% (vs 100% in Tier 0, but enables multi-project)
- Scalability: Supports 1M+ tokens
- **Total Value**: $18,000-22,000/year

**ROI**: 8-12x return

**Trigger**: When corpus >200k tokens (adding Legacy AI)

---

### **Tier 3: Add API Automation** (Optional)

**Costs**:
- Development: 4-6 hours ($400-600) for API wrapper
- **Claude Max**: $100/month (keep for interactive work)
- **Claude API**: $40-60/month (NEW - for autonomous agents)
- Vector DB: $25/month (same, already using Weaviate)
- **Total Year 1**: $2,600-3,100 (dev + $1,200 Max + $480-720 API + $300 DB)

**Benefits**:
- Time saved (Tier 0-2): 70-120 min/week (baseline)
- Time saved (automation): +120-240 min/month (NEW)
- Background processing: Voice notes → insights while you sleep
- Scheduled reports: Monday morning summaries without manual work
- **Total Value**: $20,000-28,000/year

**ROI**: 6-10x return

**Trigger**: When manual repetitive work >2 hours/month

---

### **Doing Nothing (Baseline)**

**Costs**:
- Time wasted: 10-15 min/session × 10 sessions/week = 100-150 min/week
- Annual: 87-130 hours = $8,700-13,000/year
- Rework from missed decisions: ~$12,000/year
- **Total Cost**: $20,700-25,000/year

**Benefits**: $0

**"ROI"**: -100% (pure cost, no benefit)

---

## Trade-Off Analysis

### **Simplicity vs Scalability**

| Approach | Simplicity | Scalability | Interface | Monthly Cost |
|----------|------------|-------------|-----------|--------------|
| **Prompt Caching** | ✅✅✅ Simplest | ⚠️ <200k tokens | Desktop | $100 |
| **Contextual RAG** | ⚠️ Medium | ✅✅ 200k-1M tokens | Desktop | $100-125 |
| **RAG + API** | ❌ Complex | ✅✅✅ 1M+ tokens + automation | Desktop + API | $165-185 |

**Your Path**: 
- Tier 0 (now): Simplicity wins
- Tier 1 (2-3 weeks): Scalability needed (stay in Desktop)
- Tier 3 (Q2 2026): Automation if ROI justifies

---

### **Desktop vs API Interface**

| Interface | Use Case | Cost | Human Involvement |
|-----------|----------|------|-------------------|
| **Claude Desktop** | Interactive work | $100/month (Max) | Always in loop |
| **Claude API** | Autonomous agents | +$40-60/month | Optional supervision |

**When Desktop Works**:
- ✅ You start sessions manually
- ✅ You review results and decide next steps
- ✅ Creative/strategic work (needs human judgment)
- ✅ Back-and-forth iteration

**When API Needed**:
- ⚠️ Agents run on schedule (daily reports)
- ⚠️ Background processing (while you're away)
- ⚠️ Event-driven actions (new data → auto-process)
- ⚠️ Multi-agent orchestration (agents collaborate)

**Your Current Workflows**: 100% Desktop-compatible (no API needed)

---

### **Cost vs Accuracy**

| Approach | Monthly Cost | Accuracy | Interface |
|----------|--------------|----------|-----------|
| **Prompt Caching** | $100 | 100% (no retrieval) | Desktop |
| **RAG (embeddings)** | $100-125 | 94.3% (5.7% failures) | Desktop |
| **Contextual RAG** | $100-125 | 97.1% (2.9% failures) | Desktop |
| **+ Reranking** | $100-125 | 98.1% (1.9% failures) | Desktop |

**Insight**: RAG adds $0-25/month (just vector DB), not $60+ (no API charges in Desktop).

---

### **Speed vs Accuracy (Tier 1 Only)**

| Configuration | Latency | Accuracy | Use Case |
|---------------|---------|----------|----------|
| **Embeddings only** | 50-100ms | 94.3% | Speed-critical |
| **Embeddings + BM25** | 100-150ms | 97.1% | Balanced (your case) |
| **+ Reranking** | 200-300ms | 98.1% | Accuracy-critical |

**Your Workflow**: Not real-time → Optimize for accuracy (use reranking if failures >3%)

**All Work in Desktop**: Search happens locally, results displayed in Desktop (covered by Max)

---

## Timeline Implications

### **Critical Path for Tier 0**

```
Week 1 (Nov 8-15): Foundation
├─ Day 1-2: MCP PoC + Templates ✅ DONE
├─ Day 3-4: Template validation + MCP expansion
└─ Day 5-6: Git hooks + Notion sync

Week 2 (Nov 15-22): Desktop Optimization
├─ Day 7-9: Notion Command Center
├─ Day 10-11: Prompt caching in Desktop (NEW)
│             Add structured logging (future-proofing)
└─ Day 12-14: Testing + validation

Tier 0 Complete: Nov 22 (on track)
```

**Interface**: Claude Desktop (you in conversation)  
**Cost**: $100/month (Max subscription)  
**Risk**: Low (simple architecture, well-documented)

---

### **Critical Path for Tier 1**

```
Trigger: When corpus >200k tokens (adding Legacy AI)

Week 1: RAG Setup (Still in Desktop)
├─ Day 1-2: Vector DB setup (Chroma local, free)
├─ Day 3-4: Contextual chunking + embedding ($0.70 one-time)
└─ Day 5-6: Build hybrid search (BM25 + embeddings)

Week 2: Integration + Validation
├─ Day 7-9: Integrate search with MCP
│            Results displayed in Desktop (covered by Max)
├─ Day 10-11: Test retrieval accuracy
└─ Day 12-14: Add reranking if failures >3%

Tier 1 Complete: 2 weeks after trigger
```

**Interface**: Still Claude Desktop (no API)  
**Cost**: $100-125/month (Max + optional cloud DB)  
**Risk**: Medium (more moving parts, but proven approach)

---

### **Critical Path for Tier 3** (Optional, Future)

```
Trigger: When manual work >2 hours/month

Week 1: API Wrapper
├─ Day 1-2: FastAPI server setup
├─ Day 3-4: Integrate with existing MCP tools (90% reuse)
└─ Day 5-6: Test API calls, validate billing

Week 2: Autonomous Agents
├─ Day 7-9: Build scheduled report agent
├─ Day 10-11: Build background processing agent
└─ Day 12-14: Monitoring + cost controls

Tier 3 Complete: 2 weeks after trigger
```

**Interface**: Desktop + API (hybrid)  
**Cost**: $165-185/month (Max + API + DB)  
**Risk**: Medium-High (new architecture, API billing complexity)

---

## Budget Allocation (CORRECTED)

### **Year 1 Budget (Tier 0 - Epic 2nd Brain Only)**

| Category | Amount | Rationale |
|----------|--------|-----------|
| **Development** | $600 | 6 hours (Tier 0 implementation + future-proofing) |
| **Claude Max** | $1,200 | $100/month × 12 months (already paying) |
| **Contingency** | $200 | Unexpected issues, testing |
| **Total** | $2,000 | |

**Expected Value**: $18,000-22,000/year  
**ROI**: 9-11x

---

### **Year 1 Budget (Tier 1 - Add Legacy AI)**

| Category | Amount | Rationale |
|----------|--------|-----------|
| **Development** | $1,000 | +$400 for RAG implementation |
| **Claude Max** | $1,200 | $100/month × 12 months (same) |
| **Vector DB** | $0-300 | Chroma = $0, Weaviate = $25/month |
| **Setup** | $1 | Embeddings + contextualizing (one-time) |
| **Contingency** | $300 | Testing, iteration |
| **Total** | $2,500-2,800 | |

**Expected Value**: $18,000-22,000/year (same leverage, multi-project)  
**ROI**: 6-9x

---

### **Year 1 Budget (Tier 3 - Add API Automation)** (Optional)

| Category | Amount | Rationale |
|----------|--------|-----------|
| **Development** | $1,600 | +$600 for API wrapper |
| **Claude Max** | $1,200 | $100/month × 12 months (keep) |
| **Claude API** | $480-720 | $40-60/month × 12 months (NEW) |
| **Vector DB** | $300 | $25/month × 12 months (Weaviate) |
| **Contingency** | $400 | API billing surprises |
| **Total** | $3,980-4,220 | |

**Expected Value**: $20,000-28,000/year (baseline + automation)  
**ROI**: 5-7x

**Decision**: Only implement if manual work >2 hours/month (ROI threshold)

---

## Open Questions for Coaches

### **For Peter (Engineering Coach)**

1. **Vector DB Choice**: Chroma (local, free) vs Weaviate (cloud, $25/month)?
   - **Context**: 820k corpus, 1-10 projects, not scaling aggressively
   - **Your rec**: Start with Chroma (free), switch if needed

2. **Chunking Strategy**: Header-based (simple) vs semantic (complex)?
   - **Context**: Markdown docs with clear section headers
   - **Your rec**: Header-based (KISS principle)

3. **API Timing**: Build API wrapper in Tier 1 "just in case" or wait until Tier 3?
   - **Context**: No current need for autonomous agents
   - **Your rec**: Wait (YAGNI), add when triggered

### **For Kevin Au (Business Coach)**

1. **Budget Allocation**: Is $2,000-2,800 reasonable for Tier 0-1 given 6-9x ROI?
   - **Context**: Solo founder, baby arriving January
   - **Your rec**: Yes (high ROI, foundational investment)

2. **Tier 1 Trigger**: Start RAG at 180k (proactive) or 200k (reactive)?
   - **Context**: Epic 2nd Brain at 189k, adding Legacy AI soon
   - **Your rec**: Wait until 200k (don't over-engineer)

3. **API Timing**: Build in Q1 2026 (pre-baby) or Q2 2026 (post-baby)?
   - **Context**: Limited time in Q1, but may have use cases
   - **Your rec**: Defer to Q2 (validate need first)

---

## Recommended Decision Path

### **Immediate (This Week)**

✅ **Decision 1**: Use Claude Desktop for Tier 0-2 (defer API to Tier 3)  
**Rationale**: Covers all current workflows, no API costs, simpler architecture  
**Confidence**: High (backed by your actual usage patterns)

✅ **Decision 2**: Implement prompt caching in Desktop (Phase 5)  
**Rationale**: Simplest approach for <200k corpus, covered by Max  
**Confidence**: High (well-documented, proven approach)

✅ **Decision 3**: Add future-proofing (logging, structured returns)  
**Rationale**: 3-4 hours now saves 10+ hours later when adding API  
**Confidence**: High (low cost, clear upside)

---

### **Next Session (After Tier 0 Test)**

⏳ **Decision 4**: Choose vector DB for Tier 1 (Chroma vs Weaviate)  
**Rationale**: Need to understand retrieval patterns first  
**Confidence**: Medium (depends on usage data)

⏳ **Decision 5**: Embedding vendor (Voyage vs Gemini)  
**Rationale**: Both work well, comes down to cost vs convenience  
**Confidence**: Medium (marginal difference)

---

### **Tier 1 (When Adding Legacy AI)**

⏳ **Decision 6**: Reranking threshold (add if failures >3%)  
**Rationale**: Need real retrieval data to decide  
**Confidence**: Low (defer until testing)

⏳ **Decision 7**: Cross-project queries (scoped vs unified)  
**Rationale**: Depends on actual query patterns  
**Confidence**: Low (need usage data)

---

### **Tier 3 (Q2 2026, Optional)**

⏳ **Decision 8**: Build API wrapper (if manual work >2 hours/month)  
**Rationale**: Data-driven trigger, not speculative  
**Confidence**: Low (too far out, many unknowns)

⏳ **Decision 9**: Which agents to automate first (reports, processing, etc.)  
**Rationale**: Depends on which tasks are most repetitive  
**Confidence**: Low (need Tier 0-2 data first)

---

## Decision Framework Summary

### **Interface Decision Tree**

```
Do I need agents running WITHOUT me?
├─ NO → Claude Desktop (Tier 0-2)
│        Cost: $100-125/month
│        Timeline: Now - Q1 2026
│        Risk: Low
│
└─ YES → Add API (Tier 3)
         Cost: +$40-60/month
         Timeline: Q2 2026 (if triggered)
         Risk: Medium
```

### **Context Approach (Within Desktop)**

```
What's my corpus size?
├─ <200k → Prompt Caching (Tier 0)
│           Cost: $0 extra (covered by Max)
│           Timeline: 1 hour to implement
│
└─ >200k → Contextual RAG (Tier 1)
            Cost: $0-25/month (vector DB)
            Timeline: 6-8 hours to implement
```

### **Key Principle**

**Build for Desktop (Tier 0-2), design for API (Tier 3+).**

- Interface layer changes (Desktop → API)
- Business logic stays same (RAG, BM25, embeddings)
- 90% code reuse when adding API
- No premature optimization

---

**Last Updated**: November 18, 2025 (Architecture Clarified)  
**Next Review**: After Tier 0 validation  
**Owner**: Dharan Chandra Hasan

**Next**: See [Next Steps](./next-steps.md) for immediate action items.
