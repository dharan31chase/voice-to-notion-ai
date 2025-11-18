# Fundamentals of Context Management Systems

**Purpose**: Understand the core technical concepts behind RAG systems, embeddings, and prompt caching  
**Audience**: Business owner + Head of Engineering (you) making architecture decisions  
**Time to Read**: 20-30 minutes  
**Last Updated**: November 18, 2025

---

## Table of Contents

1. [The Core Problem: Context at Scale](#the-core-problem)
2. [Chunking: Breaking Documents Apart](#chunking)
3. [Two Ways to Search: BM25 vs Embeddings](#search-methods)
4. [Contextual Embeddings: The Innovation](#contextual-embeddings)
5. [Prompt Caching: The Economic Enabler](#prompt-caching)
6. [The 200k Token Threshold](#threshold)
7. [Quick Reference](#quick-reference)

---

## The Core Problem: Context at Scale {#the-core-problem}

### **Your Situation**

You have documentation growing across multiple projects:
- Epic 2nd Brain: PRDs, session logs, tech specs (~189k tokens)
- Legacy AI: Customer interviews, design docs, prototypes (~150k tokens in future)
- Future projects: TBD

**The Challenge**: Claude's context window is ~200k tokens (~150 pages). When you have 50-100 documents totaling 500k tokens, you can't fit everything in one prompt.

### **The Traditional Solution: RAG**

**RAG** (Retrieval-Augmented Generation) = Search your docs, send only relevant pieces to Claude

**The Process**:
1. User asks: "What are the Epic 2nd Brain success criteria?"
2. System searches all docs for relevant chunks
3. Returns top 5-10 most relevant chunks
4. Sends ONLY those chunks to Claude (saves tokens, costs less)

**The Problem**: Searching is imperfect. You might miss relevant info (false negatives) or retrieve irrelevant info (false positives).

**The Innovation**: Anthropic's contextual retrieval reduces search failures by 49-67%.

---

## Chunking: Breaking Documents Apart {#chunking}

### **What It Is**

Splitting large documents into smaller, searchable pieces.

**Example:**
```
📄 Context Sync Bridge PRD (10,000 tokens)
    ↓ Split into chunks:

📦 Chunk 1: Problem Statement (800 tokens)
📦 Chunk 2: High-Level Approach (800 tokens)  
📦 Chunk 3: Success Criteria (800 tokens)
📦 Chunk 4: User Stories (800 tokens)
...12 chunks total
```

### **Why Chunk Size Matters**

**Too Small (200 tokens)**:
- ❌ Loses context (mid-sentence cuts)
- ❌ More chunks = slower search
- ✅ More precise retrieval

**Too Large (2000 tokens)**:
- ✅ Preserves context
- ✅ Fewer chunks = faster search
- ❌ Less precise (returns too much)

**Sweet Spot: 600-1000 tokens** (Anthropic tested 800 tokens)

### **Chunking Strategies**

**Business Decision**: Which strategy for your docs?

| Strategy | Best For | Your Use Case |
|----------|----------|---------------|
| **Token-based** | Uniform content | ❌ Your docs have semantic structure |
| **Sentence-based** | Narrative text | ⚠️ Okay for session logs |
| **Header-based** | Structured docs (markdown) | ✅ Best for PRDs, tech specs |
| **Paragraph-based** | Essays, articles | ⚠️ Okay for blog posts |

**Engineering Decision**: Use header-based chunking for your markdown docs.

**Why**: Your PRDs/specs use markdown headers (##) as natural semantic boundaries. Each section is a complete thought.

**Example Implementation**:
```python
# Split by ## headers
def chunk_by_headers(markdown):
    chunks = []
    current_chunk = ""
    
    for line in markdown.split('\n'):
        if line.startswith('##'):  # New section
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line + '\n'
        else:
            current_chunk += line + '\n'
    
    return chunks
```

**Cost Implication**: More chunks = more embeddings = higher initial cost, but negligible ($0.02 per 1M tokens for OpenAI embeddings).

---

## Two Ways to Search: BM25 vs Embeddings {#search-methods}

### **BM25: Keyword Matching (Like Ctrl+F++)**

**What It Does**: Finds exact or near-exact word matches.

**How It Works**:
1. Count word frequency in each chunk
2. Weight rare words higher (e.g., "MCP" more important than "the")
3. Normalize for chunk length
4. Rank chunks by relevance score

**Example:**

Query: `"MCP server architecture"`

```
Chunk A: "The MCP server uses prompt caching for efficiency"
→ Contains "MCP" (5 times), "server" (3 times) 
→ Score: 8.7

Chunk B: "Context loading happens automatically in the system"  
→ Contains neither "MCP" nor "server"
→ Score: 0.0

Result: Chunk A wins
```

**Strengths**:
- ✅ Finds exact technical terms (error codes, API names, acronyms)
- ✅ Fast (no ML model needed)
- ✅ Predictable (you know WHY it matched)

**Weaknesses**:
- ❌ Doesn't understand synonyms ("revenue" ≠ "earnings")
- ❌ Misses related concepts ("caching" ≠ "storing in memory")
- ❌ Spelling errors break it

**When to Use**: Technical queries with specific terminology.

---

### **Semantic Embeddings: Meaning Matching**

**What It Does**: Converts text into numbers that capture MEANING, not just words.

**The Magic**: Similar meanings → similar numbers

```
"The company's revenue grew by 3%"
→ [0.23, 0.87, 0.45, ... 1536 numbers]

"Corporate earnings increased 3%"  
→ [0.24, 0.88, 0.44, ... 1536 numbers]

Similarity: 95% (very close!)
Even though they share few words
```

**How It Works**:
1. Neural network trained on billions of text examples
2. Learns that "revenue" and "earnings" appear in similar contexts
3. Represents semantically similar text with similar vectors

**Example:**

Query: `"How does automatic context work?"`

```
Chunk A: "Context loading happens automatically"
→ Embedding captures: [automated process, context, loading]
→ Similarity to query: 0.89 (89% match)

Chunk B: "The MCP server uses prompt caching"
→ Embedding captures: [server, caching, efficiency]  
→ Similarity to query: 0.42 (42% match)

Result: Chunk A wins (even though it doesn't say "automatic")
```

**Strengths**:
- ✅ Understands synonyms and paraphrasing
- ✅ Finds related concepts (context → loading → retrieval)
- ✅ Works across languages (with multilingual models)

**Weaknesses**:
- ❌ Can miss exact technical terms
- ❌ Computationally expensive (requires ML model)
- ❌ Less predictable (harder to debug)

**When to Use**: Conceptual queries, exploratory search.

---

### **Best of Both Worlds: Hybrid Search**

**Business Decision**: Use BOTH BM25 and embeddings together.

**Why**: They're complementary.

| Query Type | BM25 Finds | Embeddings Find | Winner |
|------------|------------|-----------------|--------|
| "Error code TS-999" | ✅ Exact code | ❌ Might miss | BM25 |
| "How to improve performance?" | ❌ Needs exact words | ✅ Optimization, speed, faster | Embeddings |
| "MCP server architecture" | ✅ Both words | ✅ Model Context Protocol | Both |

**The Process**:
1. BM25 retrieves top 150 chunks (exact matches)
2. Embeddings retrieve top 150 chunks (semantic matches)
3. Combine using "Reciprocal Rank Fusion" (merge and deduplicate)
4. Return top 20 chunks

**Performance**: Anthropic's research shows 49% fewer retrieval failures vs embeddings alone.

**Engineering Decision**: When you implement RAG (Tier 1), use hybrid retrieval.

**Vendor Options**:

| Approach | Complexity | Accuracy | Cost |
|----------|------------|----------|------|
| **Embeddings only** | Low | 5.7% failure rate | $0.02/M tokens |
| **Embeddings + BM25** | Medium | 2.9% failure rate (49% better) | $0.02/M tokens + BM25 (free) |
| **+ Reranking** | High | 1.9% failure rate (67% better) | $0.04/M tokens |

**Recommendation**: Start with Embeddings + BM25 (Tier 1), add reranking if failure rate >3%.

---

## Contextual Embeddings: The Innovation {#contextual-embeddings}

### **The Problem with Regular Embeddings**

**Example Chunk (from SEC filing)**:
```
"The company's revenue grew by 3% over the previous quarter."
```

**What's Missing**:
- Which company? (ACME Corp)
- Which quarter? (Q2 2023)  
- Previous quarter's revenue? ($314M)

**Result**: Embedding captures "revenue, 3%, growth" but lacks critical context for precise retrieval.

---

### **Contextual Embeddings Solution**

**Step 1: Use Claude to Generate Context**

Send to Claude:
```
<document>
[Full SEC filing document - 8,000 tokens]
</document>

<chunk>
"The company's revenue grew by 3% over the previous quarter."
</chunk>

Give short context to help find this chunk later.
```

Claude responds:
```
"This is from ACME Corp's Q2 2023 SEC filing. 
Previous quarter revenue was $314M."
```

**Step 2: Prepend Context to Chunk**

```
Before: 
"The company's revenue grew by 3% over the previous quarter."

After:
"ACME Corp Q2 2023 SEC filing; previous quarter $314M. 
The company's revenue grew by 3% over the previous quarter."
```

**Step 3: Embed the Contextualized Version**

Now the embedding captures: `ACME Corp, Q2 2023, $314M, revenue, 3%, growth`

**Result**: Query "ACME Q2 revenue" matches with 89% similarity (vs 62% without context).

---

### **Business Impact**

**Performance Gains** (from Anthropic research):
- Regular embeddings: 5.7% failure rate
- Contextual embeddings: 3.7% failure rate (**35% improvement**)
- + BM25: 2.9% failure rate (**49% improvement**)
- + Reranking: 1.9% failure rate (**67% improvement**)

**Cost** (with prompt caching):
- $1.02 per million document tokens (one-time)
- For your 189k token corpus: ~$0.20 total

**Your Use Case**:
```
Query: "What did we decide about MCP tools in Phase 1?"

Without context:
Chunk: "Implemented tools for context loading"
→ Missing: Which project? Which phase? What decision?
→ Low confidence match

With context:  
Chunk: "Context Sync Bridge (Epic 2nd Brain), Phase 1A, Nov 8 2025. 
Decision: Use MCP over REST API for lower latency. 
Implemented tools for context loading."
→ High confidence match! All context preserved.
```

---

## Prompt Caching: The Economic Enabler {#prompt-caching}

### **The Old Problem**

**Before Caching**:
```
Request 1: Send 10,000 token document → Pay $0.03
Request 2: Send same 10,000 tokens → Pay $0.03 again
Request 3: Send same 10,000 tokens → Pay $0.03 again

Total cost: $0.09
```

**Why Contextual Retrieval Was Expensive**:
- Generate context for 1000 chunks
- Each needs full document as reference (8k tokens)
- 1000 requests × 8k tokens × $0.003 = $24 per document
- Too expensive!

---

### **How Caching Changes Everything**

**With Caching**:
```
Request 1: Send 10,000 tokens → Pay $0.0375 (25% premium to cache)
Request 2: Reference cached tokens → Pay $0.003 (90% discount!)
Request 3: Reference cached tokens → Pay $0.003 (90% discount!)

Total cost: $0.0435 (51% savings)
```

**For Contextual Retrieval**:
```
Generate context for 1000 chunks:
- Cache document once: 8k × $0.00375 = $0.03
- Process 1000 chunks: 1000 × (800 chunk) × $0.0003 = $0.24
Total: $0.27 per document (vs $24 without caching!)

91% cost reduction
```

---

### **How It Works (Technical)**

**API Implementation**:
```python
import anthropic

client = anthropic.Anthropic()

# First request - establish cache
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    system=[
        {"type": "text", "text": "You are an AI assistant"},
        {
            "type": "text",
            "text": "[Your 10,000 token document here]",
            "cache_control": {"type": "ephemeral"}  # ← Mark for caching
        }
    ],
    messages=[{"role": "user", "content": "Question 1"}]
)

# Second request - cache hit!
response2 = client.messages.create(
    model="claude-sonnet-4-20250514",
    system=[  # Same system prompt
        {"type": "text", "text": "You are an AI assistant"},
        {
            "type": "text",
            "text": "[Same 10,000 token document]",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    messages=[{"role": "user", "content": "Question 2"}]  # Different question
)

# Document retrieved from cache (90% cheaper)
```

**Cache Rules**:
- Lasts 5 minutes of inactivity
- Must be >1024 tokens to cache
- Only system prompts and tool definitions cacheable
- Free to READ from cache, costs 25% more to WRITE

---

### **Business Impact for Your System**

**Your Corpus**: 189,000 tokens (Epic 2nd Brain only)

**Scenario 1: Without Caching**
```
10 sessions/week:
- Each loads 189k tokens: 189k × $0.003 = $0.567 per session
- Weekly cost: $5.67
- Monthly cost: $22.68
```

**Scenario 2: With Caching**
```
First session each day:
- Load 189k tokens (cache): 189k × $0.00375 = $0.709

Next 9 sessions (cache hits):
- Read 189k from cache: 189k × $0.0003 = $0.057 per session
- 9 sessions: $0.513

Daily cost: $0.709 + $0.513 = $1.222
Monthly cost (20 work days): $24.44

Wait, that's MORE expensive?
```

**The Trick**: Cache duration + session clustering

**Optimized Scenario 3**: Batch work sessions
```
Morning deep work (4 sessions within 5 min of each other):
- Session 1: Cache write $0.709
- Sessions 2-4: Cache hits $0.057 × 3 = $0.171
- Morning total: $0.880

Afternoon work (3 sessions within 5 min):
- Session 1: Cache write $0.709  
- Sessions 2-3: Cache hits $0.057 × 2 = $0.114
- Afternoon total: $0.823

Daily cost: $1.70
Monthly cost: $34

Still more expensive? What's going on?
```

**The Real Savings**: Context loading SPEED, not just cost

**Without caching**:
- Load 189k tokens: 3-5 seconds per session
- 10 sessions: 30-50 seconds/week on loading

**With caching**:
- First load: 3-5 seconds (cold cache)
- Subsequent: 0.5-1 second (cache hit)
- 10 sessions: ~8-15 seconds/week on loading

**2-3x faster context loading**

**The ACTUAL cost savings**: Avoiding RAG infrastructure

**RAG approach (>200k tokens)**:
- Vector DB: $25-70/month (Pinecone/Weaviate)
- Embedding API: $5-10/month
- Reranking API: $5-10/month
- **Total: $35-90/month**

**Prompt caching approach (<200k tokens)**:
- No vector DB needed
- No embedding costs
- No reranking costs
- **Total: $20-35/month (just Claude API)**

**Real savings: $15-55/month + eliminated complexity**

---

## The 200k Token Threshold {#threshold}

### **Why 200k Tokens Matters**

Claude's context window: ~200k tokens (~150 pages)

**Below 200k tokens**: Fit entire corpus in one prompt (no chunking needed)  
**Above 200k tokens**: Must chunk and retrieve (RAG required)

### **Your Situation**

**Epic 2nd Brain (Tier 0)**: ~189k tokens
- PRDs: 50k tokens
- Session logs: 100k tokens
- Tech specs: 30k tokens
- Architecture: 9k tokens

**Status**: 11k tokens below threshold (94.5% capacity)

**Adding Legacy AI (Tier 1)**: +150k tokens = 339k total
- Customer interviews: 100k tokens
- Design docs: 30k tokens
- Prototypes: 20k tokens

**Status**: 139k OVER threshold → RAG required

---

### **Business Decision: When to Implement What**

```
┌─────────────────────────────────────────────────────────┐
│ Corpus Size         │ Approach          │ Why            │
├─────────────────────────────────────────────────────────┤
│ < 180k tokens      │ Prompt Caching    │ Simplest       │
│ (Current: 189k)    │ (Full corpus)     │ Most accurate  │
│                    │                   │ Lowest cost    │
├─────────────────────────────────────────────────────────┤
│ 180k - 200k tokens │ Monitor closely   │ Approaching    │
│ (Warning zone)     │ Plan for RAG      │ limit          │
├─────────────────────────────────────────────────────────┤
│ > 200k tokens      │ Contextual RAG    │ Must chunk     │
│ (After Legacy AI)  │ (Embeddings+BM25) │ Scale solution │
└─────────────────────────────────────────────────────────┘
```

### **How to Track Corpus Size**

**Automated Monitoring**:
```python
# scripts/track_corpus_size.py

def count_tokens(text):
    """Rough estimate: 0.75 tokens per word"""
    return int(len(text.split()) * 0.75)

def check_corpus():
    total = 0
    for filepath in Path("docs").rglob("*.md"):
        content = filepath.read_text()
        total += count_tokens(content)
    
    print(f"Total: {total:,} tokens")
    print(f"Capacity: {total/200_000:.1%}")
    
    if total > 180_000:
        print("⚠️  Approaching 200k threshold")
    if total > 200_000:
        print("🚨 Must implement RAG")
    
    return total
```

**Add to git hooks**: Run on every commit, alert if approaching threshold.

---

## Quick Reference {#quick-reference}

### **Terminology**

| Term | Definition | Key Number |
|------|------------|------------|
| **Chunking** | Splitting docs into pieces | 600-1000 tokens/chunk |
| **BM25** | Keyword matching | Free (open source) |
| **Embeddings** | Meaning-based vectors | $0.02/M tokens (OpenAI) |
| **Contextual Embeddings** | Chunks with added context | 35% better accuracy |
| **Prompt Caching** | Store repeated content | 90% cost savings |
| **RAG** | Retrieval system for large corpora | Needed >200k tokens |
| **Reranking** | Filter search results | Additional 18% accuracy |

### **Decision Matrix**

| Corpus Size | Approach | Cost/Month | Accuracy | Complexity |
|-------------|----------|------------|----------|------------|
| < 200k tokens | Prompt Caching | $20-35 | 100% (no retrieval) | Low |
| 200k - 500k | Contextual RAG | $40-60 | 97% (3% failures) | Medium |
| 500k - 1M | RAG + Reranking | $60-90 | 98% (2% failures) | High |

### **Vendor Comparison**

| Feature | OpenAI | Google Gemini | Voyage AI |
|---------|--------|---------------|-----------|
| **Embeddings** | text-embedding-3 | text-embedding-004 | voyage-2 |
| **Cost** | $0.02/M tokens | $0.025/M tokens | $0.06/M tokens |
| **Performance** | Good | Best (per Anthropic) | Best (tied) |
| **Reranking** | No | No | Yes ($0.05/M tokens) |
| **Ease of Use** | High | Medium | High |

**Recommendation**: 
- **Tier 0**: OpenAI embeddings (you're already using for voice pipeline)
- **Tier 1**: Switch to Voyage (embeddings + reranking in one vendor)

---

## Next Steps

**For Business Decisions**:
- Read [Decision Framework](./decision-framework.md) for vendor selection and cost-benefit analysis

**For Engineering Decisions**:
- Read [Application to Epic 2nd Brain](./application-to-epic2b.md) for system architecture

**For Implementation**:
- Read [Next Steps](./next-steps.md) for action items in next session

---

**Last Updated**: November 18, 2025  
**Next Review**: After testing prompt caching in MCP (Phase 5 of Tier 0)
