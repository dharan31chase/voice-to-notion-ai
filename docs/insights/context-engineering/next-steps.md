# Next Steps: Action Items for Implementation

**Purpose**: Clear action items based on context engineering research  
**Priority Order**: Sorted by urgency, dependency, and interface (Desktop vs API)  
**Last Updated**: November 18, 2025 (Architecture Clarified)  
**Critical Update**: Desktop-first (Tier 0-2), API deferred (Tier 3+)

---

## 🎯 Core Principle: Build for Desktop, Design for API

Everything in Tier 0-2 uses **Claude Desktop** (covered by Max $100/month).  
API automation is **optional** (Tier 3+, add only if manual work >2 hours/month).

---

## Immediate Actions (This Week)

### **1. Update Context Sync Bridge PRD** ⚠️ **CRITICAL**

**What Changed**: Architecture is Desktop-first (not API-based), costs much lower

**Specific Updates Needed**:

```markdown
SECTION: Success Criteria

OLD: "Context loading time < 3 minutes (from current 10-15 min)"

NEW: "Context loading time < 1 minute (from current 10-15 min)
     Interface: Claude Desktop (no API needed)
     Cost: Covered by Max subscription ($100/month flat fee)"

---

SECTION: Phase 5 (Day 10-12)

OLD: Phase 5: RAG search implementation (6-8 hours)
     Decision: Simple keyword vs semantic embeddings

NEW: Phase 5: Prompt Caching in Desktop (4-6 hours)
     - Load full Epic 2nd Brain corpus (189k tokens) into Claude Desktop
     - Validate context loads in <1 min (covered by Max subscription)
     - Add structured logging (future-proofing for API)
     - Add session tracking (prevent runaway loops later)
     - Test with 5+ sessions, measure satisfaction
     
     Success Criteria:
     - Context loads in <1 min
     - Zero "can't find decision" moments
     - Covered by Max subscription (no additional costs)
     
     Deferred to Tier 1: RAG (when corpus >200k or adding Legacy AI)

---

NEW SECTION: Phase 7 (Tier 1 - Week 3-4)

Phase 7: Hybrid RAG for Multi-Project (6-8 hours)

Trigger: When corpus >200k tokens (adding Legacy AI)

Interface: Still Claude Desktop (no API needed)

Components:
1. Vector DB setup (Chroma local = $0, or Weaviate cloud = $25/month)
2. Contextual chunking ($0.70 one-time via API)
3. BM25 + semantic embeddings (local algorithms, free)
4. MCP integration (return results to Desktop)

Cost: $100-125/month (Max + optional cloud DB)

Success Criteria:
- Retrieval failure rate <3%
- Query latency <500ms (local search)
- Results displayed in Desktop (covered by Max)
- Scales to 1M+ tokens

---

NEW SECTION: Phase 9 (Tier 3 - Q2 2026, Optional)

Phase 9: API Automation (4-6 hours)

Trigger: When manual repetitive work >2 hours/month

Interface: Desktop + API (hybrid)

Components:
1. API wrapper around existing MCP tools (90% code reuse)
2. Autonomous agents (scheduled reports, background processing)
3. Cost controls (rate limiting, budget alerts)

Cost: +$40-60/month (Claude API charges)

Success Criteria:
- Agents run without human supervision
- Time saved >2 hours/month (ROI justifies cost)
- API costs stay within budget ($50/month)

Decision: Defer until proven need (data-driven)

---

SECTION: Cost Estimates (Update Throughout)

OLD: Various estimates assuming API charges

NEW: 

Tier 0 (Epic 2nd Brain only):
- Claude Max: $100/month (flat fee, unlimited)
- MCP Server: $0/month (runs locally)
- Total: $100/month

Tier 1 (Add Legacy AI):
- Claude Max: $100/month (same)
- Vector DB: $0-25/month (Chroma local = free, Weaviate = $25)
- Embeddings setup: $0.70 one-time
- Total: $100-125/month

Tier 3 (API automation - optional):
- Claude Max: $100/month (keep for interactive work)
- Claude API: $40-60/month (NEW - autonomous agents)
- Vector DB: $25/month (same)
- Total: $165-185/month

ROI: 4-12x return depending on tier
```

**Additional Sections to Add**:
1. Clarify Desktop vs API interface (User Story or Design Notes)
2. Link to `docs/insights/context-engineering/` folder
3. Decision log (why Desktop-first, when to add API)

**Location**: `docs/prd/context-sync-bridge.md`

**Time Estimate**: 45-60 minutes

**Why Critical**: Prevents building wrong architecture (API-first instead of Desktop-first)

---

### **2. Add Future-Proofing to MCP Server** ⚠️ **HIGH PRIORITY**

**Goal**: Build MCP tools so they work for BOTH Desktop (now) and API (later)

**What to Add**:

#### **2A: Structured Logging** (1 hour)

```python
# Add to all MCP tools
import structlog
logger = structlog.get_logger()

def start_session(project_name, workstream):
    logger.info("session_start", 
        project=project_name, 
        workstream=workstream,
        timestamp=datetime.now().isoformat()
    )
    
    docs = load_docs(project_name, workstream)
    
    logger.info("session_loaded",
        docs_count=len(docs),
        token_count=count_tokens(docs),
        elapsed_seconds=(datetime.now() - start_time).total_seconds()
    )
    
    return docs
```

**Why**: When you add API (Tier 3), you can't use print statements (agents run in background). Logs persist for debugging.

---

#### **2B: Structured Return Values** (1 hour)

```python
# CURRENT (probably):
def start_session(project, workstream):
    docs = load_docs(project, workstream)
    return docs  # Just the text

# FUTURE-PROOF:
def start_session(project, workstream):
    docs = load_docs(project, workstream)
    return {
        "project": project,
        "workstream": workstream,
        "docs": docs,
        "metadata": {
            "doc_count": len(docs),
            "token_count": count_tokens(docs),
            "timestamp": datetime.now().isoformat()
        }
    }
```

**Why**: API agents need structured data. Desktop can display either format.

---

#### **2C: Session Tracking** (30 min)

```python
# Simple counter to prevent runaway loops
class SessionTracker:
    def __init__(self):
        self.sessions_today = 0
        
    def track_session(self, project):
        self.sessions_today += 1
        logger.info("session_tracked", 
            count=self.sessions_today, 
            project=project
        )
        
        if self.sessions_today > 50:
            logger.warning("high_session_count", 
                count=self.sessions_today,
                message="Possible runaway loop or heavy usage"
            )

# Use in start_session
tracker.track_session(project_name)
```

**Why**: When API agents run, you want to catch loops (agent calling itself 1000x).

**Total Time**: 2.5 hours  
**Benefit**: 90% code reuse when adding API (saves 10+ hours later)

---

### **3. Test Prompt Caching in Desktop** ⚠️ **HIGH PRIORITY**

**Goal**: Validate that Desktop + caching works as expected

**Test Scenario**:
```
1. Open Claude Desktop
2. Say "Start session for Epic 2nd Brain"
3. MCP loads 189k tokens
4. Ask 5 questions within 5 minutes:
   - "What are my open questions?"
   - "What did we decide about MCP architecture?"
   - "Show me the latest session log"
   - "What's the roadmap status?"
   - "Any blockers?"
5. Measure: Time per question, user satisfaction
```

**Success Criteria**:
- First load: <10 seconds (context loads into Desktop)
- Questions 2-5: Instant (Desktop has context loaded)
- Zero "can't find decision" moments
- Cost: $0 additional (covered by Max subscription)

**How to Validate Cost**:
- Check Anthropic usage dashboard (should show 0 API calls)
- Desktop usage doesn't appear in API billing
- Confirm: Still paying only $100/month Max

**Deliverable**: Document results in `docs/sessions/claude-chat/`
- Actual vs expected performance
- Any issues encountered
- Go/no-go decision for Phase 5

**Time Estimate**: 1 hour (testing + documentation)

**Why Important**: Validates core Tier 0 approach before committing

---

## Secondary Actions (Next 1-2 Sessions)

### **4. Add Corpus Size Tracking** (1-2 hours)

**What to Build**:

```python
# scripts/track_corpus_size.py
import os
from pathlib import Path
from datetime import datetime

def count_tokens(text):
    # Rough estimate: 1 token per 4 characters
    return len(text) // 4

def check_project_health(project_name, repo_path):
    total_tokens = 0
    
    # Count all markdown files
    for md_file in Path(repo_path).rglob("*.md"):
        if ".git" in str(md_file):
            continue
        content = md_file.read_text()
        total_tokens += count_tokens(content)
    
    # Calculate percentage of threshold
    pct = total_tokens / 200_000
    
    # Report
    print(f"\n{project_name} Corpus Health:")
    print(f"├─ Total tokens: {total_tokens:,}")
    print(f"├─ Threshold: 200,000")
    print(f"└─ Capacity: {pct:.1%}")
    
    # Alerts
    if pct > 0.95:
        print(f"\n⚠️  WARNING: {project_name} at 95%+ capacity")
        print("→ Plan RAG implementation (Tier 1)")
    
    if pct > 1.0:
        print(f"\n🚨 CRITICAL: {project_name} exceeded threshold")
        print("→ MUST implement RAG immediately")
    
    # Log for tracking over time
    log_entry = {
        "project": project_name,
        "tokens": total_tokens,
        "percentage": pct,
        "timestamp": datetime.now().isoformat()
    }
    
    return log_entry

# Run weekly via cron + on every commit (git hook)
```

**Git Hook Integration**:
```bash
#!/bin/bash
# .git/hooks/post-commit

# Existing: Sync to Notion
python scripts/sync_to_notion.py

# NEW: Track corpus size
python scripts/track_corpus_size.py \
    --project "Epic 2nd Brain" \
    --repo-path "."

# If threshold exceeded, alert user
```

**Time Estimate**: 1-2 hours  
**Why Important**: Early warning for Tier 1 trigger (when to add RAG)

---

### **5. Update Notion Roadmap** (30 min)

**What to Update**:

**Notion Roadmap Link**: `https://www.notion.so/2a58369c73058079a356cbf2dd2d86bc`

Changes:
1. Update Phase 5 title: "RAG search" → "Prompt Caching in Desktop"
2. Add Phase 7: "Hybrid RAG for Multi-Project (Tier 1)"
3. Add Phase 9: "API Automation (Tier 3, optional)"
4. Update cost estimates (Desktop $100-125, not $165+)
5. Add decision log (why Desktop-first)
6. Link to `docs/insights/context-engineering/` folder

**Implementation Plan Link**: `https://www.notion.so/2a58369c7305801896cfc84da4a03f3d`

Changes:
1. Reflect revised Phase 5 approach
2. Add Tier 3 as optional (not default path)
3. Document trigger conditions (corpus size, manual work)

**Time Estimate**: 30 minutes  
**Why Important**: Keep Notion in sync with repo decisions

---

## Deferred Actions (Tier 1 - When Corpus >200k)

### **6. Implement Hybrid RAG** (6-8 hours, 2-3 days)

**Trigger**: Adding Legacy AI OR reaching 200k tokens

**Components**:

#### **6A: Vector DB Setup** (2-3 hours)
- Choose: Chroma (local, $0) or Weaviate (cloud, $25/month)
- Install and configure
- Test basic operations (add, search, delete)

#### **6B: Contextual Chunking** (1-2 hours)
- Write script to chunk docs by headers
- Add context to each chunk (using Claude API - $0.70 one-time)
- Store in structured format

#### **6C: Embedding Generation** (1 hour)
- Choose: Voyage ($0.06/M) or Gemini ($0.025/M)
- Generate embeddings for all chunks
- Store in vector DB

#### **6D: Hybrid Search** (2-3 hours)
- Build BM25 index (local, free)
- Implement Reciprocal Rank Fusion (merge BM25 + semantic)
- Test retrieval accuracy (target: <3% failures)

#### **6E: MCP Integration** (1 hour)
- Update start_session() to use hybrid search
- Return top 20 docs (~150k tokens) to Desktop
- Validate: Results displayed in Desktop (covered by Max)

**Interface**: Still Claude Desktop (no API)  
**Cost**: $100-125/month (Max + optional cloud DB)  
**Documentation**: Create separate tech requirement for this

---

### **7. Testing Protocols** (2-3 hours, after Phase 5)

**What to Build**:
- Test query dataset (20-30 representative questions)
- Accuracy measurement script
- Performance benchmarking suite

**Reference**: `docs/insights/context-engineering/testing-protocols.md` (to be created)

**Time Estimate**: 2-3 hours

---

## Far Future Actions (Tier 3 - Q2 2026, If Triggered)

### **8. Build API Wrapper** (4-6 hours)

**Trigger**: When manual repetitive work >2 hours/month

**What to Build**:

```python
# NEW FILE: api_server.py
from fastapi import FastAPI
from mcp_server import start_session, end_session  # Reuse 100%!

app = FastAPI()

@app.post("/start-session")
async def api_start_session(project: str, workstream: str):
    # Call EXISTING MCP tool (no rewrite!)
    result = start_session(project, workstream)
    
    # NEW: Call Claude API with docs
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        system=result["docs"],  # Structured return value pays off!
        messages=[{"role": "user", "content": workstream}]
    )
    
    return {"result": response.content}

# That's it! 90% code reuse
```

**Cost**: 4-6 hours development + $40-60/month API charges  
**ROI**: Only implement if saves >2 hours/month manual work

---

### **9. Build Autonomous Agents** (6-8 hours)

**Examples**:

**Agent 1: Monday Morning Report**
```python
@schedule(time="07:00", day="Monday")
async def weekly_report():
    # Scan all projects
    blockers = []
    for project in ["Epic 2nd Brain", "Legacy AI"]:
        result = start_session(project, "identify blockers")
        blockers.extend(result["blockers"])
    
    # Post to Slack/Notion
    post_summary(blockers)
```

**Agent 2: Voice Note Processor**
```python
@schedule(interval="1 hour")
async def process_voice_notes():
    # Check for new notes
    new_notes = fetch_unprocessed_notes()
    
    for note in new_notes:
        # Analyze and route
        analysis = analyze_note(note)
        route_to_notion(analysis)
```

**Cost**: 6-8 hours development + agent-specific API costs  
**Decision**: Build agents one at a time, validate ROI for each

---

## Open Questions to Resolve

### **Questions for Peter (Engineering Coach)**

**Topic**: Technical validation and architecture

**Questions**:
1. Chroma (local) vs Weaviate (cloud) for 820k corpus - which would you choose?
   - **Context**: Starting small, may scale to 2-3M tokens in 2 years
   - **Your preference**: Chroma (free, simple) or Weaviate (managed, $25)?

2. When to add API wrapper - proactively (Tier 1) or reactively (Tier 3)?
   - **Context**: No current need, but may have use cases in Q1 2026
   - **Your take**: Build it early or wait until triggered?

3. How to test retrieval accuracy without ground-truth dataset?
   - **Context**: Don't have labeled "correct answer" set
   - **Ideas**: Sample queries and manual validation?

**When**: After Tier 0 complete (late November)

---

### **Questions for Kevin Au (Business Coach)**

**Topic**: Prioritization and budget

**Questions**:
1. Is $2,000-2,800 reasonable Year 1 budget given 6-9x ROI?
   - **Context**: $1,000 dev + $1,200 Max + $0-600 DB/contingency
   - **Compare to**: Doing nothing = $20k/year wasted time

2. Should I delay Legacy AI integration to keep Epic 2nd Brain simple longer?
   - **Context**: Baby arriving January, limited time in Q1
   - **Trade-off**: Simpler (stay Tier 0) vs Leverage (multi-project)

3. When to hire engineering help - after Tier 0 or Tier 1?
   - **Context**: Peter joining later, but may need contractor sooner
   - **Question**: At what complexity does solo become bottleneck?

**When**: After Tier 0 complete (late November)

---

## Decision Log (Track Changes)

### **Decision 1: Desktop-First Architecture** ✅
- **Date**: November 18, 2025
- **Rationale**: Covers all current workflows, no API costs, simpler
- **Impact**: Tier 0-2 cost $100-125/month (not $165+)
- **Next Review**: After Tier 0 validation

### **Decision 2: Prompt Caching for Tier 0** ✅
- **Date**: November 18, 2025
- **Rationale**: Corpus (189k) below 200k threshold
- **Alternative Considered**: Build RAG anyway (rejected as premature)
- **Next Review**: After prompt caching test (action item #3)

### **Decision 3: Defer API to Tier 3** ✅
- **Date**: November 18, 2025
- **Rationale**: No current need for autonomous agents
- **Trigger**: When manual work >2 hours/month
- **Next Review**: Monthly (track manual work time)

### **Decision 4: Add Future-Proofing (Logging, Tracking)** ✅
- **Date**: November 18, 2025
- **Rationale**: 2.5 hours now saves 10+ hours later
- **Components**: Structured logging, return values, session tracking
- **Next Review**: During Tier 0 implementation

### **Decision 5: Corpus Size Monitoring** ✅
- **Date**: November 18, 2025
- **Rationale**: Early warning for Tier 1 trigger
- **Implementation**: Git hook + weekly report
- **Next Review**: Weekly (automated)

---

## Success Metrics

### **Phase 5 Success (Prompt Caching in Desktop)**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Context loading time | <1 min | User perception |
| "Can't find decision" moments | 0/week | User feedback |
| Cost | $100/month | Max subscription only |
| User satisfaction | >90% | Self-assessment |

**Review Date**: End of Phase 5 (Nov 20)

---

### **Tier 1 Success (RAG in Desktop)**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Retrieval failure rate | <3% | Test query results |
| Query latency | <500ms | Performance logs |
| Monthly cost | $100-125 | Max + DB |
| User satisfaction | >90% | Self-assessment |

**Review Date**: 2 weeks after Tier 1 launch

---

### **Tier 3 Success (API Automation)** - Optional

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time saved | >2 hours/month | Manual tracking |
| API cost | <$60/month | Usage dashboard |
| Agent reliability | >95% | Error logs |
| ROI | >2x | Time saved × $100/hr ÷ cost |

**Review Date**: 1 month after Tier 3 launch

---

## Next Session Agenda (Suggested)

**Session Goal**: Validate Desktop approach and update PRD

**Time**: 90-120 minutes

**Agenda**:

1. **Update Context Sync Bridge PRD** (45-60 min)
   - Desktop vs API architecture
   - Phase 5 revised (prompt caching)
   - Add Phase 7 (Tier 1 RAG)
   - Add Phase 9 (Tier 3 API, optional)
   - Update cost estimates throughout
   - Link to context-engineering docs

2. **Add Future-Proofing to MCP** (2.5 hours - Claude Code)
   - Structured logging (1 hour)
   - Structured return values (1 hour)
   - Session tracking (30 min)

3. **Test Prompt Caching** (1 hour)
   - Run 5-question test in Desktop
   - Validate: fast, accurate, covered by Max
   - Document results

4. **Plan Corpus Size Tracking** (30 min)
   - Design script structure
   - Decide: implement now or next session?
   - Schedule if yes

**Deliverables**:
- Updated PRD (Desktop-first, clear cost breakdown)
- Future-proof MCP tools (90% reusable for API)
- Test results (validation of approach)
- Decision: corpus tracking now or later

---

## Resource Links

**Documentation Created**:
- [README](./README.md) - Overview (updated for Desktop-first)
- [Fundamentals](./fundamentals.md) - Core concepts
- [Anthropic Insights](./anthropic-contextual-retrieval-insights.md) - Research
- [Application to Epic 2B](./application-to-epic2b.md) - Recommendations (updated)
- [Decision Framework](./decision-framework.md) - Vendors and costs (updated)
- **This File** - Action items (updated)

**External Resources**:
- [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [MCP Documentation](https://docs.anthropic.com/en/docs/build-with-claude/mcp)

**Project Documentation**:
- [Context Sync Bridge PRD](../../prd/context-sync-bridge.md) - Needs updates
- [Roadmap](../../context/roadmap.md) - Current status
- [Systems Thinking Workbook](../../Systems_Thinking_Workbook__Energy___Voice-to-Notion.md)

---

## Key Takeaways

1. **Architecture is Desktop-First** (Tier 0-2)
   - No API costs for interactive work
   - Covered by Max $100/month
   - API optional in Tier 3 (when triggered)

2. **Costs Much Lower Than Expected**
   - Tier 0: $100/month (not $40)
   - Tier 1: $100-125/month (not $165)
   - Tier 3: $165-185/month (if/when needed)

3. **Future-Proofing is Cheap** (2.5 hours now)
   - Structured logging, returns, tracking
   - 90% code reuse for API later
   - Saves 10+ hours when migrating

4. **Testing is Critical** (validate assumptions)
   - Don't assume prompt caching works
   - Test in real Desktop environment
   - Measure time, cost, satisfaction

5. **Decision-Driven, Not Speculative**
   - Build Tier 0 (proven need)
   - Build Tier 1 when triggered (corpus >200k)
   - Build Tier 3 only if ROI justifies (manual work >2hr/mo)

---

**Last Updated**: November 18, 2025 (Architecture Clarified)  
**Next Review**: After Tier 0 PRD update and testing  
**Owner**: Dharan Chandra Hasan

**Priority**: Focus on action items #1-3 this week (PRD update, future-proofing, testing).
