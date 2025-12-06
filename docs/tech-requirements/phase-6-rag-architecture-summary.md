# Phase 6: RAG Separate Repos - Architecture Summary

**Status**: Architecture Complete, Implementation Foundation Ready
**Branch**: `feature/rag-separate-repos`
**Date**: 2025-12-05

---

## ✅ What's Complete (Phase 6.1-6.2)

### 1. Feature Branch Created
- ✅ Branch: `feature/rag-separate-repos`
- ✅ Safe rollback capability for 16-hour risky change
- ✅ Phases 0-5 committed to `feature/strategy-board-workflow` first

### 2. RAG Architecture Designed

**Privacy Model**: Separate ChromaDB collections per project
- Epic 2nd Brain: `epic-2nd-brain` collection
- Legacy AI: `legacy-ai` collection
- **Zero cross-project data leakage**

**Configuration**: `docs/config/rag-repos.json`
```json
{
  "Epic 2nd Brain": {
    "chroma_collection": "epic-2nd-brain",
    "index_paths": ["docs/prd", "docs/tech-requirements", ...]
  },
  "Legacy AI": {
    "chroma_collection": "legacy-ai",
    "index_paths": ["research/customer-interviews", ...]
  }
}
```

**Search Architecture**:
- Hybrid: BM25 + semantic embeddings + BGE reranking
- Embeddings: OpenAI text-embedding-3-small (384 dimensions)
- Reranking: BGE reranker-base (local, privacy-first)
- Top-K: 20 results reranked → 10 returned

### 3. Base RAG Class Implemented

**File**: `mcp_server/rag/base_rag.py`

**Features**:
- Abstract base class for project-specific RAG
- Configuration loading from `rag-repos.json`
- Privacy isolation (separate collections)
- Extensible for future projects

**Interface**:
```python
class BaseRAG(ABC):
    def search(query: str, top_k: int) -> List[Dict]
    def index_documents(force_reindex: bool) -> Dict
    def get_stats() -> Dict
    def is_enabled() -> bool
```

---

## ⏳ What Remains (Phase 6.3-6.6)

### Phase 6.3: Implement Legacy AI RAG (6h)

**To Build**:
- `mcp_server/rag/legacy_ai_rag.py`
- Extends `BaseRAG`
- Index paths:
  - `research/customer-interviews/`
  - `research/analyses/`
  - `product/`
  - `business/`
  - `sessions/customer-discovery/`

**Implementation Tasks**:
1. ChromaDB client initialization
2. Document chunking (header-based, 1000 chars)
3. Embedding generation (OpenAI API)
4. Hybrid search (BM25 + semantic)
5. BGE reranking (local model)

**Estimated Time**: 6 hours

---

### Phase 6.4: Implement Epic 2nd Brain RAG (6h)

**To Build**:
- `mcp_server/rag/epic_2nd_brain_rag.py`
- Extends `BaseRAG`
- Index paths:
  - `docs/prd/`
  - `docs/tech-requirements/`
  - `docs/sessions/claude-code/`
  - `docs/sessions/claude-chat/`
  - `docs/context/one-pagers/`

**Implementation Tasks**: (Same as Legacy AI)

**Estimated Time**: 6 hours

---

### Phase 6.5: Add MCP Tools for RAG Search (1h)

**To Build in** `mcp_server/full_server.py`:

```python
@mcp.tool()
def search_legacy_ai(
    query: str,
    doc_types: Optional[List[str]] = None,
    top_k: int = 10
) -> List[Dict]:
    """
    Search Legacy AI documents (customer interviews, analyses, etc.)

    Args:
        query: Search query
        doc_types: Filter by types (interviews, analyses, product, business)
        top_k: Number of results

    Returns:
        List of ranked results with snippets
    """
    from mcp_server.rag.legacy_ai_rag import LegacyAIRAG

    rag = LegacyAIRAG()
    return rag.search(query, top_k=top_k)


@mcp.tool()
def search_epic_2nd_brain(
    query: str,
    doc_types: Optional[List[str]] = None,
    top_k: int = 10
) -> List[Dict]:
    """
    Search Epic 2nd Brain documents (PRDs, tech requirements, sessions)

    Args:
        query: Search query
        doc_types: Filter by types (prd, tech-req, sessions, one-pagers)
        top_k: Number of results

    Returns:
        List of ranked results with snippets
    """
    from mcp_server.rag.epic_2nd_brain_rag import Epic2ndBrainRAG

    rag = Epic2ndBrainRAG()
    return rag.search(query, top_k=top_k)
```

**Estimated Time**: 1 hour

---

### Phase 6.6: Test RAG Separation (1h)

**Test Cases**:

1. **Test A: Privacy Isolation**
   - Search Legacy AI for "customer interview"
   - Verify NO Epic 2nd Brain results returned
   - Search Epic 2nd Brain for "PRD"
   - Verify NO Legacy AI results returned

2. **Test B: Search Accuracy**
   - Known query: "What are the main customer pain points?"
   - Expected: Top 3 results from customer interviews
   - Validate: Relevance score >0.6

3. **Test C: Cross-Project Search**
   - Query both projects separately
   - Verify separate collections used
   - Validate no data leakage

**Test Script**: `test_rag_separation.py`

**Estimated Time**: 1 hour

---

## 🏗️ Architecture Decisions

### Why Separate Collections?

**Privacy**: Customer data (Legacy AI) isolated from infrastructure docs (Epic 2nd Brain)

**Performance**: Smaller collections → faster search

**Flexibility**: Can enable/disable per project

### Why ChromaDB?

**Local-first**: Privacy-preserved, no third-party uploads

**Hybrid search**: Supports both BM25 and semantic

**Lightweight**: No heavy infrastructure required

### Why BGE Reranking?

**Local model**: Privacy-preserved (runs locally)

**High quality**: State-of-the-art reranking

**Fast**: Reranks 20 → 10 results in <100ms

---

## 📊 Estimated Completion

| Phase | Estimated | Status |
|-------|-----------|--------|
| 6.1 | 15 min | ✅ Complete |
| 6.2 | 2h | ✅ Complete (architecture) |
| 6.3 | 6h | ⏳ Pending (Legacy AI RAG) |
| 6.4 | 6h | ⏳ Pending (Epic 2nd Brain RAG) |
| 6.5 | 1h | ⏳ Pending (MCP tools) |
| 6.6 | 1h | ⏳ Pending (testing) |
| **Total** | **16h** | **~2.25h complete (14%)** |

---

## 🚀 Next Steps

### Option A: Continue Implementation (14h remaining)
- Implement Legacy AI RAG (6h)
- Implement Epic 2nd Brain RAG (6h)
- Add MCP tools (1h)
- Test RAG separation (1h)

### Option B: Pause and Validate Architecture
- Review RAG config and base class
- Validate architecture decisions
- Plan implementation in next session

### Option C: Skip Phase 6, Proceed to Phase 7
- Phase 7: File-based handoffs (6h) is independent
- Can return to Phase 6 later
- Delivers handoff detection sooner

---

## 💡 Recommendation

**Pause Phase 6** and proceed to **Phase 7** (File-based handoffs) in next session.

**Rationale**:
1. **Context**: At 122k tokens, limited headroom for 14h more work
2. **Independence**: Phase 7 doesn't depend on Phase 6
3. **Value**: Handoff detection delivers immediate value
4. **Completeness**: Phase 6 architecture documented, easy to resume

**Total Progress**: 41/62 hours (66%) if we proceed to Phase 7

---

*Generated: 2025-12-05*
*Branch: feature/rag-separate-repos*
*Status: Architecture complete, implementation foundation ready*
