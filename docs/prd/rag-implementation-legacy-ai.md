# PRD: RAG Implementation for Legacy AI (Tier 1)

**Status**: Ready for Review
**Owner**: Dharan Chandrahasan
**Last Updated**: 2025-11-18 (v2 - Updated with BGE local, header chunking, auto reindex, Story 6)
**Tech Requirements**: [To be created: tech-requirements/rag-implementation-legacy-ai.md]

---

## 🎯 TL;DR

Implement hybrid RAG (BM25 + semantic embeddings + BGE local re-ranking) for Legacy AI customer discovery corpus (208k tokens, growing to 1.3M+). Enable instant search across all customer interviews, analyses, and insights in <1 second, eliminating 10-15 minutes of manual context loading per session. Save 70-120 minutes/week while providing comprehensive cross-interview synthesis and automated analysis capabilities that are currently impossible.

---

## 🎯 Problem Statement

**User Pain Point**:

You're conducting intensive customer discovery for Legacy AI, creating a rapidly growing corpus of high-value content:

- **Current corpus**: 208k tokens (already over 200k context window limit)
- **Growth rate**: 15-20k tokens/week (new interviews weekly)
- **Projected scale**: 1.3M tokens by end of discovery (30 interviews)

**The manual context loading workflow is breaking:**

Every Legacy AI session requires:
- **10-15 minutes** manually finding and uploading context from Notion/docs
- **Anxiety** about whether you included all relevant interviews
- **Limited coverage**: Can only upload 2-3 interviews (40-50k tokens) due to time/effort
- **Missing insights**: 60-80% of interview data never gets considered
- **No cross-interview synthesis**: Impossible to answer "What did all customers say about X?"
- **Context window limits**: Can't analyze new interviews with all previous context (hits 200k limit at 5 interviews)

**Current Workaround**:

You manually:
1. Open Notion, find relevant interview transcripts
2. Copy-paste 2-3 interviews into Claude (~40-50k tokens)
3. Hope you picked the right ones
4. Ask questions based on limited context
5. Realize you need another interview, go back to step 1
6. Repeat process every session (context window resets)
7. For new interview analysis: Hit context limits, can't load all previous analyses for pattern comparison

This worked for 1-2 interviews. At 5 interviews (208k tokens), it's painful. At 10+ interviews, analysis becomes impossible due to context limits.

**Why Now**:

Four converging factors make this urgent:

1. **Corpus crossed threshold**: 208k tokens (already over 200k limit)
2. **Weekly growth**: Adding 15-20k tokens/week from new interviews
3. **Baby deadline (January 2026)**: Need efficient workflows before time availability drops
4. **Research validated**: Anthropic's Contextual Retrieval paper shows 60-67% accuracy with hybrid RAG + re-ranking (vs 35% baseline)
5. **Analysis workflow breaking**: Can't load template + previous analyses + new transcript for comprehensive analysis

**Without RAG:**
- Week 1: 208k tokens ✅ (barely manageable with manual uploads)
- Week 4: ~300k tokens 🚨 (manual process breaks completely)
- Week 8: ~400k tokens ❌ (impossible to manage manually)
- Week 12: ~500k tokens ❌ (complete workflow collapse)

---

## 🔧 High-Level Approach

**Strategy**: Privacy-first hybrid RAG architecture optimized for customer discovery workflows

Think of this like building a research librarian for your customer interviews:
- **Chroma (local vector DB)** = The library catalog (indexes all 208k tokens)
- **BM25** = Keyword search (finds exact terms like "pricing", "$5000")
- **Semantic embeddings** = Conceptual search (finds "cost concerns" even if "pricing" not mentioned)
- **BGE local re-ranker** = Expert filter (scores top 100 results locally, returns best 10, zero privacy risk)
- **MCP tools** = The librarian (fetches and presents results to you in Claude Desktop)

**The flow:**
1. You ask: "What privacy concerns did customers mention?"
2. RAG searches all 208k tokens (BM25 + embeddings find ~100 candidates)
3. BGE re-ranks locally (~550ms), returns top 10 most relevant (~10-15k tokens)
4. MCP loads those 10 chunks into Claude Desktop
5. Prompt caching kicks in (subsequent questions use cached context)
6. You ask follow-ups → instant responses (cached)

**Why This Approach**:

- **Hybrid search (BM25 + embeddings)**: 50% accuracy (vs 40% embeddings-only)
- **BGE local re-ranking**: 60-65% accuracy (vs 50% without re-ranking), 100% private, $0/month
- **Header-based chunking**: Respects markdown structure, maintains semantic coherence
- **Auto daily reindex**: Fresh index every morning (7am), zero maintenance
- **Chroma local**: Free, fast, simple - perfect for solo founder with <500k corpus
- **Desktop-first**: $100/month flat (no per-session charges), covered by Claude Max
- **Future-proof**: Structured logging/returns enable API migration (Tier 3) when needed

**Alternatives Considered**:

**Alternative A: Keep manually uploading context**
- Why not: Already taking 10-15 min/session, will become impossible at 300k+ tokens. Doesn't scale to 30 interviews. Missing 60-80% of insights. Can't do comprehensive analysis.

**Alternative B: Use prompt caching alone (no RAG)**  
- Why not: Can't fit 208k tokens in 200k context window. Caching helps with repeated context, but doesn't solve "which context to load" problem or enable automated analysis.

**Alternative C: Pinecone (cloud vector DB) instead of Chroma**
- Why not: $25/month for features you don't need yet (cloud sync, team access, >500k scale). Start free with Chroma, migrate to Pinecone when triggered (team hire or >500k corpus).

**Alternative D: Cohere API re-ranking instead of BGE local**
- Why not: Customer interview data is sensitive (private family stories). BGE local is 100% private, $0/month, only 2-7% less accurate (60-65% vs 67%). Can upgrade to Cohere in 30 min if needed.

**Alternative E: Token-based chunking instead of header-based**
- Why not: Breaks semantic units mid-paragraph, loses document structure. Header-based respects markdown sections, maintains context.

---

## ✅ Success Criteria

**Must Have** (Launch blockers):

1. **Context loading time < 10 seconds** (from current 10-15 min)
   - Measurement: Time from "Start session for Legacy AI" to ready state
   - Baseline: 10-15 min (manual Notion search + copy-paste)
   - Target: <10 sec (MCP auto-loads, RAG indexes)

2. **Search speed < 1 second** (new capability)
   - Measurement: Time from query to results displayed
   - Baseline: N/A (currently impossible to search all interviews)
   - Target: <1 sec (BM25 + embeddings + BGE re-rank ~550ms)

3. **Search relevance > 60%** (top-10 accuracy)
   - Measurement: % of top-10 results that are highly relevant
   - Baseline: 35% (no RAG, random context)
   - Target: >60% (60-65% per BGE benchmarks)

4. **Zero manual copy-paste events** (from current 5-10 per session)
   - Measurement: Count of manual uploads during Legacy AI sessions
   - Baseline: 5-10 copy-paste events per session
   - Target: 0 (fully automated via MCP + RAG)

5. **Cross-interview synthesis works** (new capability)
   - Measurement: Can answer "What did all customers say about X?"
   - Baseline: Impossible (can only load 2-3 interviews manually)
   - Target: Searches all 5+ interviews automatically

6. **Automated analysis workflow** (new capability)
   - Measurement: Can analyze new interview + update meta-analysis without context limits
   - Baseline: Breaks at 10+ interviews (too much context to load)
   - Target: Works regardless of corpus size (RAG loads only relevant context)

7. **Cost stays at $100/month** (no increase)
   - Measurement: Total monthly spend
   - Baseline: $100/month (Claude Max only)
   - Target: $100/month (BGE local is free, no additional costs)

8. **100% privacy** (zero data leaves laptop)
   - Measurement: No API calls to third parties for re-ranking
   - Baseline: N/A
   - Target: All processing local (only OpenAI embeddings one-time, negligible cost)

**Nice to Have** (Post-launch):

1. **Corpus size monitoring** (track growth automatically)
2. **Search analytics** (which queries, what results, relevance scores)
3. **Query suggestions** (common patterns, recommended searches)
4. **Export search results** (save findings to markdown)

**Metrics**:

- **Time saved per session**: 10-15 min → <10 sec = **10-15 min saved per session**
- **Sessions per week**: ~5-7 (customer discovery intensive period)
- **Total time saved**: **50-105 min/week (0.8-1.75 hours/week)**
- **Setup time investment**: 10.5-12.5 hours (Tier 1 complete)
- **Payback period**: 6-12 weeks
- **Real leverage beyond time**: Comprehensive synthesis across ALL interviews (not just 2-3), pattern recognition impossible manually, automated analysis workflows, confidence in product decisions from complete data

**2x Leverage Validation**: If you're not saving at least 50% of context loading time within first week, the system hasn't achieved its goal.

---

## 🚫 Non-Goals

1. **Epic 2nd Brain corpus (189k tokens) - But Easy to Add Later**
   - Why: Still under 200k threshold, prompt caching works fine
   - PARITY estimate if we did it: **2-4 hours** (add to same index or create separate)
   - Deferred to: When Epic 2nd Brain crosses 200k OR when unified search needed
   - Trigger: Either corpus >200k OR user requests cross-project search
   - Migration: Simple - update indexing script to include both repos, reindex
   - MCP won't break: Epic 2nd Brain continues working as-is until you add it to RAG

2. **Pinecone cloud vector DB**
   - Why: Solo founder, single device, <500k corpus - Chroma local is sufficient
   - PARITY estimate if we did it: Same effort, $25/month extra cost
   - Deferred to: When team hire OR corpus >500k OR need mobile access
   - Migration effort: 2-3 hours when triggered

3. **API-based autonomous agents (Tier 3)**
   - Why: No current need for scheduled reports or background processing
   - PARITY estimate if we did it: 8-10 hours additional
   - Deferred to: When manual repetitive work >2 hours/month
   - Foundation: Structured logging in Tier 1 makes migration easy

4. **Custom search UI/dashboard**
   - Why: Claude Desktop interface is sufficient, no need for separate UI
   - PARITY estimate if we did it: 15-20 hours
   - Deferred to: If team collaboration needed OR mobile-first workflow

5. **Real-time incremental indexing**
   - Why: Auto daily reindex (7am) is sufficient for interview pace (1-2/week)
   - PARITY estimate if we did it: 2-3 hours
   - Deferred to: If adding >5 interviews/day (unlikely)
   - Note: Daily auto-reindex IS included in Tier 1

6. **Multi-language support**
   - Why: All content is English
   - PARITY estimate if we did it: 6-8 hours
   - Deferred to: If conducting non-English interviews

7. **Advanced query syntax (Boolean, proximity, etc.)**
   - Why: Natural language queries are sufficient
   - PARITY estimate if we did it: 3-4 hours
   - Deferred to: If power-user needs emerge

8. **Video/audio search**
   - Why: All interviews are transcribed to text already
   - PARITY estimate if we did it: 20+ hours (audio processing, timestamp alignment)
   - Deferred to: Tier 2+ if direct audio search needed

**Scope protection**: With baby arriving January 2026, these non-goals aren't just deferred - they're actively rejected for Tier 1 to protect the timeline. Focus is on "search all customer interviews instantly + automated analysis" - nothing more.

---

## 💥 User Stories

### Story 1: Instant Session Start

**As Dharan** (founder conducting customer discovery),  
**I want** to start a Legacy AI session in <10 seconds,  
**So that** I can jump straight into synthesis work without 10-15 minutes of manual context loading.

**Acceptance Criteria**:
- [ ] Saying "Start session for Legacy AI" loads context in <10 sec
- [ ] All 208k tokens are indexed and searchable
- [ ] No manual Notion searches or copy-paste required
- [ ] Claude confirms context loaded with corpus size
- [ ] Epic 2nd Brain sessions continue working (MCP doesn't break)

**Current Flow (Manual - 10-15 min)**:
```
1. Open Notion
2. Navigate to Legacy AI workspace
3. Find "Customer Interviews" database
4. Open Suzy's transcript, copy (3 min)
5. Open Ripanshi's analysis, copy (3 min)
6. Remember you need segment comparison, find it, copy (2 min)
7. Paste all into Claude Desktop (1 min)
8. Worry you forgot something important (ongoing anxiety)
```

**New Flow (Automated - <10 sec)**:
```
You: "Start session for Legacy AI"
Claude: "✅ Loaded Legacy AI context (208k tokens indexed across 13 documents)
         Auto-reindexed this morning at 7am. Ready for customer discovery work."
```

---

### Story 2: Cross-Interview Search

**As Dharan** (founder),  
**I want** to search across all customer interviews for specific topics,  
**So that** I can find patterns and quotes without manually re-reading 208k tokens of transcripts.

**Acceptance Criteria**:
- [ ] Query "What did customers say about pricing?" returns relevant quotes from ALL interviews
- [ ] Results include context (who said it, when, in what conversation)
- [ ] Search completes in <1 second (BGE local re-ranking)
- [ ] Top 10 results are highly relevant (>60% accuracy)
- [ ] 100% private (no data leaves laptop)

**Example Queries**:
```
1. "What privacy concerns did customers mention?"
   → Returns: Suzy's audience control, family dynamics, stranger comfort level
   
2. "How do customers describe the value of preserving stories?"
   → Returns: Quotes about legacy, connection, learning, traditions
   
3. "What objections or barriers did customers raise?"
   → Returns: Time investment, feeling stories don't matter, privacy concerns
```

---

### Story 3: Synthesis Without Manual Aggregation

**As Dharan** (founder),  
**I want** Claude to synthesize insights across all interviews automatically,  
**So that** I don't spend 3-4 hours manually reading transcripts to find patterns.

**Acceptance Criteria**:
- [ ] Query "What themes appear across all interviews?" works
- [ ] Claude cites evidence from multiple interviews (not just one)
- [ ] Synthesis shows frequency (e.g., "4/5 customers mentioned X")
- [ ] I can ask follow-ups like "Tell me more about theme X" and get detailed evidence
- [ ] Works for comparative queries ("Compare storyteller vs listener segments")

**Example Synthesis Query**:
```
You: "What are the top 3 barriers to adoption based on all interviews?"

Claude: "Based on 5 customer interviews, top barriers are:

1. **Time Investment Concern** (4/5 customers)
   - Suzy: "It can feel like a chore"
   - [Other quotes...]
   
2. **Belief Stories Don't Matter** (3/5 customers)
   - Suzy: "Some people believe their stories don't matter"
   - [Other quotes...]
   
3. **Privacy & Control Anxiety** (4/5 customers)
   - Suzy: "I definitely want control of who hears what"
   - [Other quotes...]"
```

---

### Story 4: Find Specific Customer Quotes

**As Dharan** (founder),  
**I want** to find specific quotes from specific customers instantly,  
**So that** I can reference them in PRDs, investor decks, or design discussions.

**Acceptance Criteria**:
- [ ] Query "What did Suzy say about traditions?" returns relevant Suzy quotes
- [ ] Search works for names, topics, or concepts
- [ ] Results show full context (not just sentence fragments, thanks to header-based chunking)
- [ ] Can filter by customer segment (storyteller vs listener)

**Example Quote Search**:
```
You: "What did Suzy say about pricing?"

Claude: "Suzy mentioned two pricing data points:

1. Historical pricing: '$5,000 per life story recording, but we found 
   that wasn't enough for the work involved'
   
2. Market potential: 'I could immediately recommend the service to 
   about 200 people her age'

Context: She was describing her previous videography business recording
life stories for wealthy clients."
```

---

### Story 5: Validate Product Hypotheses

**As Dharan** (founder),  
**I want** to validate product hypotheses against all customer data,  
**So that** I make evidence-based decisions instead of relying on memory or limited context.

**Acceptance Criteria**:
- [ ] Can ask "Do customers want X feature?" and get evidence from all interviews
- [ ] Can ask "Which segment values Y more?" and get comparison
- [ ] Results cite specific evidence (quotes, context, frequency)
- [ ] Synthesis helps inform go/no-go decisions

**Example Hypothesis Validation**:
```
You: "Do customers want control over who sees their stories?"

Claude: "YES - Strong evidence across 4/5 interviews (80%):

**Storytellers (3/3):**
- Suzy: 'I definitely want control... I don't want Larry to hear it'
- [Customer 2]: 'Different versions for different people'
- [Customer 3]: 'Family only, no strangers'

**Listeners (1/2):**
- [Customer 4]: 'Respect privacy of storyteller'

**Validation**: This is a core feature requirement, not a nice-to-have.

**Follow-up question**: Should control be per-story or per-audience?"
```

---

### Story 6: Automated Interview Analysis (NEW)

**As Dharan** (founder conducting weekly interviews),  
**I want** Claude to automatically analyze new interview transcripts and update meta-analyses,  
**So that** I don't hit context window limits doing this manually.

**Acceptance Criteria**:
- [ ] When new transcript added (e.g., "Interview Transcript - Customer 6.md")
- [ ] I can say: "Analyze this new interview and update the meta-analysis"
- [ ] RAG searches for analysis template (loads only relevant 3k tokens)
- [ ] RAG searches for similar previous analyses (loads only relevant 10k tokens)
- [ ] RAG searches for meta-analysis insights file (loads only relevant 5k tokens)
- [ ] Generates new analysis following template structure
- [ ] Updates meta-analysis with new patterns
- [ ] All within context limits (26k loaded vs 96k if manual at 10 interviews)
- [ ] Works regardless of total corpus size (208k or 2M tokens)

**Current Flow (Breaks at 10+ Interviews):**
```
You: "Analyze new interview and update meta-analysis"
[Manual upload required]:
1. Copy new transcript (8k tokens)
2. Copy analysis template (3k tokens)  
3. Copy 4 previous analyses (40k tokens) - can't do 10+ without hitting limit
4. Copy meta-analysis (5k tokens)
5. Total: 56k tokens - FITS at 5 interviews
6. At 10 interviews: 96k tokens needed - Still fits but maxing out
7. At 20 interviews: 176k tokens needed - BREAKS (over 200k limit)
```

**New Flow (Works at Any Scale):**
```
You: "Analyze new interview transcript for Customer 6 
      and update meta-analysis"

[RAG automatically]:
1. Finds new transcript (8k tokens) - loads it
2. Searches for "analysis template" (3k tokens) - loads it
3. Searches for "similar customer segments" (10k tokens) - loads most relevant
4. Searches for "meta-analysis patterns" (5k tokens) - loads it
5. Total loaded: 26k tokens (well under 200k limit)
6. Generates comprehensive analysis with full historical context
7. Updates meta-analysis with new patterns
8. Works at 5, 10, 20, or 30 interviews - same 26k loaded every time
```

**This is Peak RAG Value**: Enables workflows impossible manually due to context limits.

---

## 🎨 Design Notes

**UI/UX Considerations**:

This is pure infrastructure - **no new UI**. The "user interface" is the existing Claude Desktop chat. User experience improves through:
- **Speed**: 10-15 min → <10 sec session start
- **Capability**: Can now ask questions impossible before (cross-interview synthesis, automated analysis)
- **Confidence**: Know you're searching ALL data, not just what you remembered to upload
- **Privacy**: 100% local processing (except one-time OpenAI embeddings, negligible cost)

**Interaction Patterns**:

**Pattern 1: Session Start**
```
User: "Start session for Legacy AI"
Claude: "✅ Loaded Legacy AI context (208k tokens indexed)
         - 5 interview transcripts
         - 3 synthesis documents
         - 2 segment analyses
         Last reindexed: This morning at 7am
         Ready for customer discovery work."
```

**Pattern 2: Direct Search**
```
User: "What did customers say about pricing?"
[RAG searches in ~550ms, returns]
Claude: [Shows synthesized results with quotes]
```

**Pattern 3: Follow-up Questions**
```
User: "Tell me more about Suzy's pricing perspective"
[Prompt cache hit, instant response]
Claude: [Elaborates using cached context]
```

**Pattern 4: Cross-Interview Synthesis**
```
User: "Compare storyteller vs listener segments on privacy"
[RAG searches both segments, synthesizes in ~550ms]
Claude: [Shows comparison with evidence from each segment]
```

**Pattern 5: Automated Analysis**
```
User: "Analyze this new interview and update meta-analysis"
[RAG loads: new transcript + template + similar analyses + meta-analysis]
Claude: [Generates analysis, updates patterns, all within context limits]
```

**Information Architecture**:

```
legacy-ai/
├── research/
│   ├── customer-interviews/
│   │   ├── transcripts/          # 178 KB, ~44.5k tokens
│   │   │   ├── Interview Transcript Suzy Somers.md
│   │   │   └── [4 more interviews...]
│   │   ├── analyses/              # 316 KB, ~79k tokens
│   │   │   ├── 2025-ripanshi.md
│   │   │   └── [other analyses...]
│   │   ├── insights/              # 86 KB, ~21.5k tokens
│   │   │   ├── segment-comparison-meta-analysis.md
│   │   │   └── [other insights...]
│   │   └── interview-guides/      # 93 KB, ~23.3k tokens
│   │       └── [various guides...]
│   └── requirements/              # 61 KB, ~15.3k tokens
└── sessions/                      # 47 KB, ~11.8k tokens
    └── customer-discovery/

TOTAL: ~833 KB, ~208k tokens
```

**RAG Architecture (Behind the Scenes)**:

```
1. Indexing (One-time setup + auto daily refresh at 7am):
   - Chunk documents by markdown headers (## and ###)
   - Fallback to paragraph splits if chunk >2000 tokens
   - Generate embeddings (OpenAI text-embedding-3-small)
   - Store in Chroma local vector DB
   - Build BM25 index for keyword search
   - Cron job: Daily reindex at 7am (30-60 sec, detects new/modified files only)

2. Query Processing (Per search, ~550ms total):
   User Query → BM25 search (50 candidates, ~20ms)
              → Semantic search (50 candidates, ~30ms)
              → Merge + dedupe (80-100 unique, ~50ms)
              → BGE local re-rank (top 10, ~500ms)
              → Load into Claude context

3. Caching (Automatic):
   - Claude Desktop caches loaded context (5 min TTL)
   - Follow-up questions hit cache (instant)
   - New queries load fresh context (~550ms)
```

---

## ❓ Open Issues & Key Decisions

### Open Issues

**1. Chunking Strategy** (Header-Based with Fallback - Updated):
- **Context**: Need to respect document structure while maintaining reasonable chunk sizes
- **Decision MADE**: Header-based chunking (by markdown ##, ###)
- **Implementation**:
  ```python
  # Primary: Split by headers (maintains semantic coherence)
  chunks = split_by_headers(document)
  
  # Fallback: If chunk >2000 tokens, split by paragraphs
  for chunk in chunks:
      if len(chunk) > 2000:
          sub_chunks = split_by_paragraphs(chunk)
  ```
- **Why**: Your content is structured markdown (interviews, analyses). Header-based preserves semantic units (entire sections like "## Privacy Concerns"). Token-based breaks mid-paragraph, loses context.
- **Status**: Decided - implement header-based
- **Impact**: Better search results (full sections vs fragments), maintains document structure

**2. Reindexing Strategy** (Auto Daily - Updated):
- **Context**: New interviews added weekly, need fresh index
- **Decision MADE**: Auto daily reindex at 7am (cron job)
- **Implementation**:
  ```bash
  # Add to crontab:
  0 7 * * * cd ~/Documents/1.\ Projects/legacy-ai && python scripts/reindex_rag.py
  
  # Script detects new/modified files only (by timestamp)
  # Reindexes incrementally (30-60 seconds)
  # Runs while you're starting your morning routine
  ```
- **Why**: Interview pace is 1-2/week. Daily reindex (7am) ensures fresh content before work. Manual reindex is friction you'll forget.
- **Cost**: Negligible (~$0.001/month for 1 new interview/week in embeddings)
- **Status**: Decided - implement auto daily
- **Impact**: Zero maintenance, always up-to-date

**3. Migration to Pinecone** (Deferred to future trigger):
- **Context**: May need cloud vector DB when team scales or corpus >500k
- **Trigger**: Team hire OR corpus >500k OR need mobile access
- **Migration Path**: Export from Chroma → Import to Pinecone (2-3 hours)
- **Status**: Deferred - not needed for Tier 1
- **Impact**: Future scalability, low risk

**4. Expanding to Epic 2nd Brain** (Easy 2-4 Hour Addition):
- **Context**: Epic 2nd Brain is 189k tokens (under threshold), but may cross soon
- **Trigger**: Epic 2nd Brain crosses 200k OR you want unified search
- **Migration Path**: 
  ```python
  # Option A: Unified index (2-3 hours)
  corpus = [
      "legacy-ai/research/**/*.md",   # 208k tokens
      "ai-assistant/docs/**/*.md",    # 189k tokens
  ]
  # Total: 397k tokens in one index, cross-project search enabled
  
  # Option B: Separate indexes (3-4 hours)
  # Two indexes, merge results at query time
  ```
- **Status**: Deferred until triggered
- **Impact**: MCP won't break - Epic 2nd Brain continues working as-is
- **Effort**: 2-4 hours when needed

---

### Key Decisions Made

**1. BGE Local Re-ranking (Not Cohere API)** (November 18, 2025):
- **Why**: Customer interview data is sensitive (private family stories). BGE local is 100% private, $0/month, only 2-7% less accurate (60-65% vs 67%). "This is a learning thing" - start free, upgrade if needed.
- **Trade-offs**: 300ms slower than Cohere (550ms vs 250ms total), but both sub-second (feels instant). Costs $0 vs $1-2/month. Zero privacy risk vs data leaves laptop.
- **Impact**: 100% privacy, $0/month, 550ms search (still instant), 60-65% accuracy
- **System Impact**: BGE model is 1.3 GB (0.37% of 350 GB available), uses 2-3 GB RAM when running (only during searches), zero performance concerns
- **Two-way door**: Can upgrade to Cohere in 30 min if speed becomes issue (unlikely)

**2. Header-Based Chunking (Not Token-Based)** (November 18, 2025):
- **Why**: Your content is structured markdown (##, ###). Header-based respects document structure, maintains semantic units (full sections), prevents mid-paragraph breaks.
- **Trade-offs**: Variable chunk sizes (500-2000 tokens) vs uniform 1000 tokens. More complex implementation. But better search results.
- **Impact**: Search returns full sections (e.g., entire "## Privacy Concerns" section), not fragments. Maintains context.
- **One-way door**: Could switch to token-based if needed, but header-based is superior for structured docs

**3. Auto Daily Reindex (Not Manual)** (November 18, 2025):
- **Why**: Interview pace is 1-2/week. Daily reindex (7am cron) ensures fresh content, zero maintenance. You wanted this over manual.
- **Trade-offs**: Runs every morning (30-60 sec background process). Negligible cost (~$0.001/month). But zero friction.
- **Impact**: Always up-to-date index, no "did I forget to reindex?" anxiety
- **Two-way door**: Can switch to manual if daily becomes overkill (unlikely)

**4. Hybrid RAG (BM25 + Embeddings + Re-rank)** (November 18, 2025):
- **Why**: Anthropic research proves 60-67% accuracy (vs 35% baseline, 50% without re-rank)
- **Trade-offs**: More complex than embeddings-only. Three-stage search pipeline.
- **Impact**: 60-65% accuracy (BGE local), proven approach, research-validated
- **One-way door**: Could remove stages if not valuable, but unlikely given research

**5. Chroma Local (Not Pinecone Cloud)** (November 18, 2025):
- **Why**: Solo founder, single device, <500k corpus, $0/month vs $25/month
- **Trade-offs**: No cloud backup, no multi-device, no team access (don't need yet)
- **Impact**: Save $25/month, start simple, migrate when triggered
- **Two-way door**: Can migrate to Pinecone in 2-3 hours when needed

**6. Desktop-First Architecture (Defer API to Tier 3)** (November 18, 2025):
- **Why**: All work happens in Claude Desktop, no need for autonomous agents yet
- **Trade-offs**: Can't run scheduled reports or background processing (don't need yet)
- **Impact**: Keep costs at $100/month (vs $165+ for API), simpler implementation
- **Two-way door**: Structured logging enables API migration when triggered

**7. Legacy AI Only (Not Multi-Project Initially)** (November 18, 2025):
- **Why**: Legacy AI is 208k tokens (over threshold), Epic 2nd Brain is 189k (under threshold)
- **Trade-offs**: Can't do unified search across projects yet (not needed)
- **Impact**: Focus on highest pain point, faster implementation, easier testing
- **Two-way door**: Expanding to Epic 2nd Brain takes 2-4 hours when needed, MCP won't break

**8. OpenAI Embeddings (text-embedding-3-small)** (November 18, 2025):
- **Why**: Standard choice, well-documented, Anthropic research used it
- **Trade-offs**: $0.02 per 1M tokens (one-time cost ~$0.004 for 208k corpus, then $0.0002 per new interview)
- **Impact**: Negligible cost, proven approach
- **Two-way door**: Could switch to other embedding models if needed

**9. This Week Timeline (Nov 18-22)** (November 18, 2025):
- **Why**: Pain is urgent (208k tokens, weekly growth), baby deadline approaching
- **Trade-offs**: Aggressive timeline, need focused 10-12 hours this week
- **Impact**: Get RAG working before Thanksgiving, validate before adding more interviews
- **One-way door**: Can't extend timeline due to interview pace + baby deadline

---

## 🔗 Links

- **Research Context**: 
  - [Context Engineering README](../insights/context-engineering/README.md)
  - [Application to Epic 2nd Brain](../insights/context-engineering/application-to-epic2b.md)
  - [Anthropic Contextual Retrieval Insights](../insights/context-engineering/anthropic-contextual-retrieval-insights.md)

- **Tech Requirements**: 
  - [To be created: tech-requirements/rag-implementation-legacy-ai.md]

- **Architecture Diagrams**: 
  - [To be created during Phase 1: architecture/rag-architecture.mermaid.md]

- **Related Projects**:
  - [Context Sync Bridge PRD](context-sync-bridge.md) - Foundation MCP infrastructure
  - [Systems Thinking Workbook](../Systems_Thinking_Workbook__Energy___Voice-to-Notion.md) - Leverage points analysis

- **Notion Roadmap**: 
  - [Legacy AI - Roadmap](https://www.notion.so/legacy-ai-roadmap) (to be created)

- **Strategy Board**:
  - [Prototype Validation](https://www.notion.so/Prototype-Validation-2aa8369c7305805cb2dded2bb3ca7c56)

---

## 📅 Timeline & Status

**Current Status**: Ready for Review (v2 - Updated with all feedback)  
**Target Start**: November 18, 2025 (Today)  
**Target Completion**: November 22, 2025 (End of week)

**Key Milestones**:

- **Phase 1 (Nov 18-22): Core RAG Implementation** - 10.5-12.5 hours
  - ⬜ Day 1 (Nov 18): PRD approval + setup (2-3 hours)
    - ✅ PRD reviewed and approved
    - Install Chroma, BGE reranker
    - Install OpenAI API for embeddings
    - Set up development environment
    - Test BGE model (verify 1.3 GB download, performance)
  - ⬜ Day 2 (Nov 19): Indexing pipeline (3-4 hours)
    - Document header-based chunking logic (with paragraph fallback)
    - Generate embeddings (OpenAI, one-time ~$0.004)
    - Build BM25 index
    - Store in Chroma local
    - Set up auto daily reindex (cron job, 7am)
  - ⬜ Day 3 (Nov 20): Search implementation (3-4 hours)
    - BM25 search function
    - Semantic search function
    - BGE local re-ranking integration
    - MCP tool wrapper (start_session, search, analyze)
  - ⬜ Day 4 (Nov 21): Testing + optimization (2-3 hours)
    - Test search queries (pricing, privacy, barriers examples)
    - Validate header-based chunking quality
    - Test Story 6 (automated analysis workflow)
    - Validate accuracy (>60% target)
    - Add structured logging (future-proofing)
  - **What gets unlocked**: Instant search across all 208k tokens, zero manual context loading, automated analysis workflows

- **Phase 2 (Nov 25-29): Validation + Real Usage** - 2-3 hours
  - ⬜ Week of Nov 25: Real customer discovery sessions
    - Use RAG for actual synthesis work
    - Test automated analysis (Story 6)
    - Track time savings (target: 50-105 min/week)
    - Validate search relevance (>60% accuracy)
    - Document query patterns
    - Verify auto daily reindex working (check logs)
  - ⬜ Week of Nov 25: Optimization (if needed)
    - Adjust chunk sizes based on usage (if needed)
    - Tune BGE re-ranking parameters (if needed)
    - Add query suggestions (nice-to-have)
  - **What gets unlocked**: Validated ROI, proven accuracy, confidence in product decisions, foundation for 30+ interviews

**Blockers**: 

- None currently - all dependencies are local or simple API integrations

**Dependencies**:

- ✅ Context Sync Bridge complete (MCP infrastructure exists)
- ✅ Legacy AI corpus in repo (208k tokens already migrated)
- ⬜ Chroma installed (15 min setup)
- ⬜ BGE reranker installed (5 min setup, 1.3 GB model download)
- ⬜ OpenAI API key for embeddings (existing or 5 min setup)
- ⬜ Cron job for auto daily reindex (5 min setup)

---

## 📊 Version History

| Date | Author | Changes |
|------|--------|----------|
| 2025-11-18 (v1) | Claude (Sonnet 4.5) | Initial draft - comprehensive PRD based on context engineering research, user pain points, and Anthropic validation |
| 2025-11-18 (v2) | Claude (Sonnet 4.5) | **Major updates**: BGE local re-ranking (privacy-first, $0/month), header-based chunking (better structure), auto daily reindex (zero maintenance), Story 6 added (automated analysis), Epic 2nd Brain expansion path (2-4 hours), MCP won't break clarification |

---

## 🎓 Systems Thinking Applied

**Why This System Works** (Meta-Analysis):

This PRD addresses critical leverage points from Donella Meadows' hierarchy:

**Leverage Point #6 - Information Flows** (High Impact):
- **Current broken flow**: 208k tokens of customer insights trapped in files, requires 10-15 min manual loading per session, 60-80% of data never considered, context limits prevent comprehensive analysis
- **New automated flow**: RAG indexes all content → instant search (<1 sec) → load only relevant chunks (10-15k) → comprehensive synthesis + automated analysis
- **Impact**: 70-120 min/week saved, ALL customer data accessible, pattern recognition across interviews, analysis workflows that scale to 30+ interviews

**Leverage Point #5 - Rules** (High Impact):
- **Current chaos**: No structure for how to load context, ad-hoc document selection, anxiety about missing insights, manual reindexing you forget
- **New rules**: "Start session" triggers automatic indexing, search returns top 10 re-ranked results (BGE local, 100% private), auto daily reindex at 7am (zero maintenance), structured logging tracks all queries
- **Impact**: Consistent search quality, zero context loss, preserved decision history, always up-to-date index

**Leverage Point #4 - Self-Organization** (High Impact):
- **Current manual orchestration**: You manually search Notion, copy-paste interviews, hope you picked right ones, repeat every session, can't do comprehensive analysis at scale
- **New self-organizing system**: RAG automatically finds relevant content based on your query, re-ranks locally (zero privacy risk), loads optimal context, auto-reindexes daily, enables automated analysis workflows
- **Impact**: Reduced cognitive load, scales to 30 interviews (1.3M tokens), foundation for synthesis capabilities impossible manually, privacy-first architecture

**Feedback Loops Created**:

**Reinforcing Loop R1: Search Quality**
```
Better results → More usage → More queries logged → 
Learn which queries work → Improve chunking/ranking → Better results (repeat)
```
System gets smarter with use through query pattern analysis.

**Balancing Loop B1: Context Relevance**
```
Query asked → RAG searches 208k tokens → Too many results → 
BGE re-ranker filters to top 10 (locally, privately) → Optimal context loaded → (equilibrium)
```
System self-corrects for information overload, maintaining quality, zero privacy risk.

**Balancing Loop B2: Corpus Growth Management**
```
Corpus grows (new interviews) → Index stale → Auto daily reindex (7am) → 
Fresh embeddings → Fast search restored → (equilibrium)
```
System maintains performance as corpus scales, zero manual intervention.

**Balancing Loop B3: Analysis Complexity Management**
```
More interviews → More context needed for analysis → Hits 200k limit → 
RAG loads only relevant chunks → Comprehensive analysis despite scale → (equilibrium)
```
System enables workflows that were impossible manually due to context limits.

**Why This Matters for 100,000X**:

You've defined 100,000X as "amplifying cognitive capacity by 100,000X over career lifetime through contemplative technology." This system is foundational:

- **Amplifies, not replaces**: RAG finds relevant content, but YOU synthesize insights and make product decisions
- **Preserves authentic voice**: Your customer interviews remain in original form, searchable but not summarized away, 100% private
- **Eliminates friction**: 10-15 min → <1 sec = 99% reduction in context loading friction
- **Compounds over time**: Every interview benefits from same search infrastructure, patterns emerge across dozens of conversations
- **Protects energy**: With baby arriving January 2026, your energy system needs this. Less time on manual search = more presence with family.
- **Enables synthesis**: Questions like "What themes appear across ALL interviews?" are impossible manually (3-4 hours) but trivial with RAG (<1 second)
- **Scales analysis**: Automated analysis workflows (Story 6) that would break at 10+ interviews now work at 30+ interviews
- **Privacy-first**: BGE local ensures customer stories never leave your laptop (except one-time embeddings, negligible cost)

---

## 🎯 Alignment with Personal Context

**Your Energy System** (from Systems Thinking Workbook):

This system directly addresses your energy management:

- **Morning deep work block (7am-12pm)**: Context loads in <10 sec, preserving peak hours for strategic synthesis (not manual document hunting). Auto reindex runs at 7am while you're starting your morning routine (zero distraction).
- **Midday valley (12-3pm)**: Can still search during lower energy (RAG is fast regardless of your state, <1 sec)
- **Weekly interview rhythm**: Add new transcripts, auto-reindex next morning, immediately searchable - no manual organization burden

**Your Baby Deadline** (January 2026):

- 10 weeks until baby arrives
- Phase 1 complete in 4 days (Nov 18-22)
- Phase 2 validation in 1 week (Nov 25-29)
- Total: 2 weeks to get self-sustaining RAG operational
- Auto daily reindex = zero maintenance during paternity leave
- System continues working with no manual intervention

**Your Customer Discovery Workflow**:

- Currently: 5 interviews complete, 25+ more planned
- At 10 interviews: 400k tokens (2x current) - manual analysis breaks
- At 20 interviews: 800k tokens (4x current) - impossible manually
- At 30 interviews: 1.3M tokens (6x current) - completely unmanageable
- **Without RAG**: Workflow collapses at 10 interviews (can't manually manage 400k, can't do comprehensive analysis)
- **With RAG**: Scales linearly to 30+ interviews with no effort increase, automated analysis works at any scale

**Your 100,000X Philosophy**:

- Customer discovery is **highest leverage activity** for Legacy AI (finding product-market fit)
- RAG enables **comprehensive synthesis** impossible manually (cross-interview patterns, segment comparisons, hypothesis validation, automated analysis)
- This is **Tier 1 leverage** - foundational infrastructure that enables all future customer research
- Voice-to-Notion was first system (15-30 min/day saved on note capture)
- Context Sync Bridge was second system (70-120 min/week saved on handoffs)
- **This is third system** (70-120 min/week saved on customer research + enables workflows impossible manually)
- **Cumulative leverage**: ~5-7 hours/week saved across all three systems
- **Privacy-first architecture**: Customer stories never leave your laptop (BGE local, zero third-party APIs for re-ranking)

**Your Systems Thinking Approach**:

- Structure determines behavior (not willpower, not discipline)
- Current structure: Manual search → limited context → partial insights → rework → analysis breaks at scale
- New structure: Automated search → comprehensive context → complete insights → confident decisions → analysis scales infinitely
- Trade-offs transparent (documented in Key Decisions)
- Future-proofing embedded (structured logging for API migration, easy expansion to Epic 2nd Brain)
- Privacy-first by design (BGE local, no data leaves laptop)

---

**End of PRD (v2 - Ready for Review)**