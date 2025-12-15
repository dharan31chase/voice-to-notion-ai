# Technical Requirements: Live Context Control v3 - Testing Issues & Fixes

**Status**: Testing Phase (Phases 0-6 Complete, Validating Implementations)
**Related PRD**: [live-context-control-v3.3.md](../prd/live-context-control-v3.3.md)
**Related Tech Req**: [live-context-control-v3.md](live-context-control-v3.md)
**Owner**: Dharan Chandrahasan + Claude Code
**Created**: 2025-12-09
**Last Updated**: 2025-12-09

---

## 🎯 Purpose

Document all testing issues discovered during Phase 0-6 validation, root cause analysis, and proposed solutions. This enables batch implementation of fixes rather than incremental changes.

**Workflow**:
1. User tests each phase
2. Documents failures here with root cause
3. Proposes 2-3 solution options
4. After all testing complete → batch implement fixes

---

## 🎉 Wins (What's Working)

### Phase 2: High-Signal Session Template - 100% Complete ✅

**All 6 tests passed!** This phase demonstrates what "done" looks like.

**What Works**:
- ✅ `end_session()` creates high-signal Notion entries automatically
- ✅ Template includes: What Worked ✅ / What Didn't Work ⚠️ / Key Decisions / Next Steps
- ✅ NO meta-commentary (no "written with Claude Chat/Code" noise)
- ✅ NO git commit messages polluting Notion
- ✅ Initiative detection: Auto-links if exists, prompts if missing (Create/Search/Proceed)
- ✅ Ad-hoc sessions: Works without initiative link
- ✅ Multi-project: Works for Legacy AI and Epic 2nd Brain

**Why Phase 2 Succeeded** (vs Phase 1 failure):
1. **End-to-end testing**: Actually ran the tool and verified Notion output
2. **Clear validation**: Observable output (can check Notion Sessions DB)
3. **Integration completed**: Notion API calls working, templates rendering correctly
4. **No infrastructure needed**: Uses existing Notion databases

**User Value Delivered**:
- ⏱️ **Time saved**: Auto-populates session descriptions (previously manual)
- 📊 **Better tracking**: High-signal content enables quick decision review
- 🎯 **Initiative linking**: Auto-detects and links to Strategy Board
- 🚀 **Zero friction**: Works for both ad-hoc and initiative-linked sessions

**Lesson Learned**: Phase 2 shows the right approach - build code, test integration, validate output, verify user value.

### Phase 4: Usage Tracking + Learning - 100% Complete ✅

**All 4 tests passed!** Learning loop working, suggestions improving over time.

**What Works**:
- ✅ Usage logs created in `logs/usage/` directory with sanitized data
- ✅ No sensitive data leakage (privacy preserved)
- ✅ Learning algorithm scoring files correctly based on frequency + recency + co-occurrence
- ✅ Suggestions relevant and accurate for repeat workstreams
- ✅ Suggestion quality improves from Session 1 → Session 5 (observable improvement)
- ✅ `docs/config/context-profiles.json` updated automatically after sessions
- ✅ Learned patterns persisted and reused across sessions

**Why Phase 4 Succeeded**:
1. **Privacy-first design**: Logs sanitized, no personal data leaked
2. **Observable improvement**: User can see suggestions getting better
3. **Integration complete**: Tracker + algorithm + profile storage all working
4. **Testing over time**: Validated improvement across multiple sessions (Session 1 vs 5)

**User Value Delivered**:
- 🎯 **Smarter context loading**: Suggestions improve with each session
- ⏱️ **Time saved**: Relevant files surfaced automatically
- 🔒 **Privacy preserved**: No sensitive data in logs
- 📈 **Continuous improvement**: Learning loop works without manual tuning

**Lesson Learned**: Phase 4 shows the value of testing over time (Session 1 vs Session 5) rather than single-shot tests.

---

### Phase 3: Auto-Update Roadmap - ⚠️ Partially Working (67% - 2/3 tests)

**ROADMAP.md sync works, but PRD archival broken** (Issue #7 discovered by user).

**What Works**:
- ✅ `end_session()` automatically syncs ROADMAP.md with Strategy Board status
- ✅ Completion dates populated automatically when initiative marked complete
- ✅ Mid-project status changes (🟡 → 🚀 → ✅) reflected in ROADMAP.md
- ✅ Perfect sync: All initiatives match between Strategy Board and ROADMAP.md

**What's Broken** (Issue #7):
- ❌ PRDs NOT auto-archived when initiative complete
- ❌ `prd_path` extraction fails (only works if Notion PRD property contains "docs/prd/" in URL)
- ❌ Archival logic skipped when `prd_path = None`
- ❌ Strategy Board "PRD Location" field never updated
- ❌ Archive folders never created (archival.py would auto-create them, but never gets called)

**Why Partial Success**:
1. **ROADMAP sync works**: Status and completion dates update correctly ✓
2. **Archival broken**: PRD path extraction logic fails for most URL formats ✗
3. **Code exists but never runs**: archival.py has correct logic, but `prd_path=None` bypasses it

**User Value Delivered**:
- ⏱️ **Partial automation**: ROADMAP.md auto-updated, but PRDs require manual archival
- 📊 **Sync works**: Strategy Board → ROADMAP.md sync reliable
- 📁 **Archival broken**: Completed PRDs stay in docs/prd/ folder (Issue #7)

**Critical Discovery** (by user):
- User marked "Live Context Control v3" as complete
- PRD file still at `docs/prd/live-context-control-v3.md` (NOT archived)
- Correctly identified my testing error (I claimed Test 3.1 passed without verifying archival)
- Root cause: `prd_path` extraction logic only handles specific URL format

---

## 📋 Testing Issues

### Issue #1: RAG Tools Not Used for Document Discovery

**Test Case**: Test 0.1 - "Read the one-pager vision doc"

**Expected Behavior**:
```
1. search_epic_2nd_brain("one-pager vision")
2. read_file("docs/context/one-pagers/epic-2nd-brain-overview.md")
```

**Actual Behavior**:
```
1. search_docs("one-pager vision") ❌ Used legacy tool
2. Bash grep commands ❌ Used manual search
3. Notion API calls ❌ Wrong approach
4. Never called search_epic_2nd_brain ❌ Ignored RAG tool
```

**Root Cause**:
- **Competing priority signals**: Both `search_docs` (line 995) and `search_epic_2nd_brain` (line 1180) have "🎯 USE THIS FIRST" in descriptions
- **No clear hierarchy**: Claude doesn't know which tool to prefer
- **Legacy tool pollution**: `search_docs` is older, appears first in file, may be preferred by model
- **Unclear use cases**: Descriptions don't explain WHEN to use each tool

**Impact**:
- **Time waste**: 90-120 seconds spiral (bash → search_docs → Notion API)
- **User frustration**: RAG tools built but never used
- **Phase 6 ROI at risk**: 16 hours invested in RAG, but not being utilized

**Solution Options**:

#### Option A: Strengthen RAG Tool Descriptions (Low Risk, Low Effort)
**What**: Update tool descriptions with clearer hierarchy and use cases
**Changes**:
```python
# search_epic_2nd_brain
"""
🎯🎯🎯 USE THIS FIRST TO FIND DOCUMENTS IN EPIC 2ND BRAIN 🎯🎯🎯

**WHEN TO USE THIS TOOL:**
- User asks to "read/find/search for a document" in Epic 2nd Brain
- You need PRDs, tech requirements, session logs, one-pagers
- You DON'T know the exact file path
- Examples: "read the one-pager vision doc"

**DO NOT use bash grep/find or search_docs - Use THIS instead!**
...
"""

# search_docs
"""
⚠️ LEGACY TOOL - Use RAG tools (search_epic_2nd_brain, search_legacy_ai) instead!

Only use this if:
- RAG tools are unavailable (error/not indexed)
- You need to search file names (not content)

This tool is deprecated in favor of hybrid RAG search.
...
"""
```
**Pros**: Quick fix (15 min), low risk, no code changes
**Cons**: Not guaranteed to work (model behavior is probabilistic)
**Validation**: Run 10 test queries, measure RAG-first usage rate

#### Option B: Deprecate search_docs Entirely (Medium Risk, Low Effort)
**What**: Remove or disable `search_docs` tool
**Changes**:
```python
# Comment out or delete search_docs tool
# @mcp.tool()
# def search_docs(...):
#     ...
```
**Pros**: Forces RAG tool usage, clear solution
**Cons**: No fallback if RAG fails, breaks existing workflows
**Validation**: Test RAG tools handle all search scenarios

#### Option C: Create Document Router Tool (Low Risk, Medium Effort)
**What**: Single `find_document(query, project)` tool that routes to correct RAG
**Changes**:
```python
@mcp.tool()
def find_document(query: str, project: str = "Epic 2nd Brain") -> list:
    """
    🎯 USE THIS FIRST: Find any document across all projects.

    Automatically routes to the correct RAG search:
    - Epic 2nd Brain → search_epic_2nd_brain
    - Legacy AI → search_legacy_ai

    This is your ONE tool for finding documents.
    """
    if project == "Epic 2nd Brain":
        return search_epic_2nd_brain(query)
    elif project == "Legacy AI":
        return search_legacy_ai(query)
    else:
        return [{"error": f"Unknown project: {project}"}]
```
**Pros**: Clear single entry point, easier for model to choose
**Cons**: Extra abstraction layer, 30-60 min to implement
**Validation**: All document queries use `find_document` first

**Recommendation**: Try Option A first (15 min), if <80% success rate → implement Option C (60 min)

**Status**: ⏳ Pending - waiting for more testing issues before implementation

---

### Issue #2: Phase 6 RAG Collections Never Indexed

**Test Case**: Test 0.2 / 6.4 - "Read the meta-analysis from Insights folder"

**Expected Behavior**:
```
1. search_legacy_ai("meta-analysis insights")
2. Returns relevant documents with scores
3. read_file("research/customer-interviews/insights/segment-comparison-meta-analysis.md")
```

**Actual Behavior**:
```
1. search_legacy_ai("meta-analysis insights")
   → Returns: "No documents indexed yet" ❌

2. search_docs("meta-analysis")
   → No output, no error (poor UX) ❌

3. read_file("insights/...")
   → "File not found" (wrong path guessed) ❌

4. search_legacy_corpus("meta-analysis")
   → SUCCESS ✅ (old RAG system, already indexed)
```

**Root Cause**:
- **Phase 6 incomplete**: Built RAG classes + MCP tools + indexing script, but **NEVER RAN INDEXING**
- **Two RAG systems exist**:
  - **OLD RAG** (`scripts/rag/`) → Already indexed, works via `search_legacy_corpus` (old MCP tool)
  - **NEW RAG** (`mcp_server/rag/`) → Code exists but ChromaDB collections empty
- **Missing step**: `python scripts/index_rag.py` was never executed
- **No validation**: Phase 6 marked complete without verifying collections populated

**Impact**:
- **16 hours wasted**: Phase 6 effort (RAG separation) not usable
- **Tool fragmentation**: 4 failed attempts before finding old working tool
- **User confusion**: "Why build new RAG if old one works?"
- **Privacy goal blocked**: Can't separate repos if new RAG not functional

**Discovery**:
```bash
# OLD RAG (Working)
Location: scripts/rag/
Storage: ~/.cache/legacy-ai-rag/chroma
Collection: legacy_ai_interviews
Status: ✅ Indexed & operational

# NEW RAG (Not Working)
Location: mcp_server/rag/
Collections: "legacy-ai", "epic-2nd-brain" (ChromaDB)
Status: ❌ Code exists, collections empty
```

**Solution Options**:

#### Option A: Run Indexing Script Immediately (Quick Fix)
**What**: Execute indexing script to populate ChromaDB collections
**Changes**:
```bash
cd /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant
python scripts/index_rag.py  # Index both Legacy AI + Epic 2nd Brain
```
**Pros**: 5-10 min fix, enables Phase 6 RAG tools immediately
**Cons**: Manual step, not automated, could forget to re-run after doc changes
**Validation**:
```python
# Test search_legacy_ai works
search_legacy_ai("customer pain points")  # Should return results

# Test search_epic_2nd_brain works
search_epic_2nd_brain("MCP server architecture")  # Should return results
```

#### Option B: Add Auto-Indexing Check to MCP Tools (Robust)
**What**: Add logic to RAG tools to auto-index if collections empty
**Changes**:
```python
# In search_legacy_ai() and search_epic_2nd_brain()
def search_legacy_ai(query: str, ...):
    rag = LegacyAIRAG()

    # Check if indexed
    stats = rag.get_stats()
    if stats.get("total_chunks", 0) == 0:
        # Auto-index on first use
        print("First-time use: Indexing Legacy AI documents...")
        rag.index_documents()

    return rag.search(query, ...)
```
**Pros**: Self-healing, no manual steps, works on first use
**Cons**: 2-5 min delay on first search, complexity, might surprise user
**Validation**: Delete ChromaDB, run search, verify auto-indexes

#### Option C: Add Indexing to start_session (Proactive)
**What**: Check RAG collections on session start, prompt to index if empty
**Changes**:
```python
# In start_session()
def start_session(...):
    # ... existing code ...

    # Check RAG collections
    legacy_rag = LegacyAIRAG()
    epic_rag = Epic2ndBrainRAG()

    if legacy_rag.get_stats().get("total_chunks", 0) == 0:
        return {
            "warning": "Legacy AI RAG not indexed",
            "action": "Run: python scripts/index_rag.py --legacy-ai",
            "impact": "search_legacy_ai() will not work until indexed"
        }

    # Same for epic_rag
    # ... continue session ...
```
**Pros**: User awareness, explicit action, no surprises
**Cons**: Adds noise to session start, still manual step
**Validation**: Start session with empty collections, verify warning shown

#### Option D: Deprecate Old RAG, Use New RAG (Clean Slate)
**What**: Remove old RAG system, only use Phase 6 RAG after indexing
**Changes**:
- Delete `scripts/rag/` (old system)
- Remove `search_legacy_corpus` tool
- Index new RAG: `python scripts/index_rag.py`
- Update all references to use new tools only
**Pros**: Single source of truth, cleaner architecture, privacy separation works
**Cons**: Breaking change, 1-2 hour effort, need to verify no regressions
**Validation**: All RAG searches work with new tools only

**Recommendation**:
1. **Immediate**: Option A (run indexing script now - 5 min)
2. **Short-term**: Option D (deprecate old RAG, clean up - 1-2 hours)
3. **Long-term**: Option B (auto-indexing - if re-indexing is common)

**Status**: ⏳ Pending - Need to run `python scripts/index_rag.py` first

---

### Issue #3: search_docs() Keyword Matching Too Literal (Needs Semantic Search)

**Test Case**: Test 0.3 - "Find PRDs about context engineering"

**Expected Behavior**:
```
1. search_docs("context engineering PRD") or search_epic_2nd_brain("context engineering PRD")
2. Returns "Live Context Control v3" PRD (semantically related to "context engineering")
3. User gets result in <30 seconds
```

**Actual Behavior**:
```
Attempt 1: search_docs("context engineering PRD")
   → Empty results (no keyword match) ❌

Attempt 2: read_file("docs/prd/")
   → Error: It's a directory, can't read ❌

Attempt 3: view directory listing
   → Path not found error ❌

Attempt 4: bash find command
   → Directory doesn't exist in container ❌

Attempt 5: Check uploaded files
   → No matches ❌

Attempt 6: search_epic_2nd_brain("context engineering")
   → "No documents indexed yet" ❌ (Issue #2)

Attempt 7: search_docs("context engineering") [broader query]
   → ✅ SUCCESS (found "Applied Context Engineering" one-pager)
```

**Time Waste**: 90-120 seconds for 7 attempts

**Root Cause**:
- **Keyword mismatch**: Searched "context engineering PRD" but actual title is "Live Context Control v3"
- **search_docs() limitations**: Basic string matching, no semantic understanding
  - Doesn't know "context engineering" ≈ "Live Context Control"
  - Doesn't know "context engineering" ≈ "Applied Context Engineering"
  - Literal substring match only
- **RAG not available**: Epic 2nd Brain RAG (which WOULD find semantic matches) not indexed (Issue #2)
- **No fuzzy matching**: Exact keyword required, no tolerance for synonyms/related terms

**Impact**:
- **Phase 6 ROI blocked**: This test case demonstrates EXACTLY why hybrid RAG was built
  - Semantic embeddings: "context engineering" → "Live Context Control" (cosine similarity)
  - BM25 + reranking: Would rank "Live Context Control v3 PRD" higher than one-pager
- **User frustration**: 7 attempts to find a document that exists
- **Tool chaos**: Tried 7 different approaches before finding answer
- **Time waste**: 90-120 sec per query like this

**Why This Matters**:
This is the **poster child for Phase 6 value**:
- **Without RAG**: "context engineering" → no match → 7 failed attempts
- **With RAG (indexed)**: "context engineering" → semantic embedding → finds "Live Context Control" immediately

**Solution Options**:

#### Option A: Index RAG Collections (Immediate - Solves Issue #2 + #3)
**What**: Run indexing script to enable semantic search
**Changes**:
```bash
python scripts/index_rag.py
```
**Expected Result**:
```python
search_epic_2nd_brain("context engineering")
# Returns:
# 1. "Live Context Control v3 PRD" (score: 0.89)
# 2. "Applied Context Engineering one-pager" (score: 0.85)
# 3. "Context Management Architecture" (score: 0.78)
```
**Pros**: Fixes both Issue #2 and #3, demonstrates Phase 6 value
**Cons**: Still need to fix Issue #1 (tool selection)
**Validation**:
- Search "context engineering" → finds "Live Context Control"
- Search "git hooks" → finds relevant tech-req docs
- Search "session handoffs" → finds handoff PRD

#### Option B: Improve search_docs() with Fuzzy Matching (Fallback)
**What**: Add fuzzy string matching to search_docs()
**Changes**:
```python
from fuzzywuzzy import fuzz

def search_docs(query: str, ...):
    # ... existing code ...

    # Add fuzzy matching
    results_with_scores = []
    for file, content in files:
        # Exact match
        if query.lower() in content.lower():
            score = 1.0
        # Fuzzy match on title
        elif fuzz.partial_ratio(query.lower(), file.stem.lower()) > 70:
            score = 0.7
        else:
            continue

        results_with_scores.append((file, content, score))

    # Sort by score
    results_with_scores.sort(key=lambda x: x[2], reverse=True)
```
**Pros**: Improves search_docs() without RAG dependency
**Cons**: Still not as good as semantic embeddings, 30-60 min effort
**Validation**: "context engineering" matches "Live Context Control" (fuzzy match on filename)

#### Option C: Add Synonym/Alias Mapping (Quick Hack)
**What**: Map common search terms to actual document titles
**Changes**:
```python
# docs/config/search-aliases.json
{
  "context engineering": ["Live Context Control", "Applied Context Engineering"],
  "git hooks": ["Git Hooks Implementation", "Context Sync Bridge"],
  "session handoffs": ["Handoff YAML Spec", "Session Handoff Fix"]
}

# In search_docs()
def search_docs(query: str, ...):
    # Expand query with aliases
    aliases = load_search_aliases()
    expanded_terms = [query] + aliases.get(query.lower(), [])

    # Search for any matching term
    for term in expanded_terms:
        results = search_for_term(term)
        if results:
            return results
```
**Pros**: 15-30 min quick fix, handles common queries
**Cons**: Manual maintenance, doesn't scale, brittle
**Validation**: Alias mapping works for common terms

**Recommendation**:
1. **Immediate**: Option A (index RAG - fixes Issue #2 + #3)
2. **If RAG fails**: Option B (fuzzy matching - 60 min fallback)
3. **Skip**: Option C (alias mapping is too brittle)

**Why Option A is Best**:
- **Solves root cause**: Semantic search is the right solution for "find related docs"
- **Phase 6 value**: Demonstrates why 16 hours was invested in RAG
- **Low effort**: Just run indexing script (5-10 min)
- **High impact**: Transforms search from literal → intelligent

**Status**: ⏳ Pending - Blocked by Issue #2 (need to index RAG first)

---

### Issue #4: Archival System Not Integrated with Search (Phase 1 Incomplete)

**Test Case**: Test 1.1 - "Search for completed PRDs from Q4 2025"

**Expected Behavior**:
```
1. search_docs("completed PRDs Q4 2025", filters={status: "complete", date_range: "Q4 2025"})
   OR
   search_epic_2nd_brain("completed PRDs Q4 2025", doc_types=["prd"], filters=...)
2. Returns archived PRDs from docs/prd/archive/2025/Q4/
3. Shows both active and archived results (archive=lower priority)
```

**Actual Behavior**:
```
1. search_docs("completed PRDs Q4 2025")
   → No results (keyword mismatch + doesn't search archive folder) ❌

2. search_epic_2nd_brain("completed PRDs Q4 2025")
   → "No documents indexed yet" ❌ (Issue #2)

3. Bash commands (ls, find)
   → Can't find repo directories (MCP abstraction layer) ❌

4. Checked uploads
   → Empty ❌

5. No way to browse archive/YYYY/QQ/ structure
   → Missing tool for file listing ❌
```

**Root Causes**:

#### 1. Archive Folders Not Indexed
- **Phase 1 spec** (line 169-172 in PRD): "search_repo() searches **both active + archive** by default"
- **Reality**: search_docs() doesn't know about archive folders
- **Missing**: Archive paths not in folder_map, not in RAG index paths

#### 2. No Metadata Tracking
- **Phase 1 spec**: "Archive PRDs have lower priority in suggestions (not frequently accessed)"
- **Reality**: No metadata for:
  - Document status (Draft / In Progress / Complete)
  - Completion date
  - Archive date
  - Quarter/year tags
- **Missing**: Frontmatter, database, or config file tracking metadata

#### 3. No Date-Based Filtering
- **Query**: "Q4 2025" (Oct-Dec 2025)
- **Reality**: No way to filter by date range
- **Missing**: Date parsing + filtering in search_docs()

#### 4. No File Listing Tool
- **Need**: Browse archive structure (list_files, list_archive)
- **Reality**: Can't discover what's in archive/2025/Q4/ without guessing paths
- **Missing**: Tool to list files with metadata

#### 5. MCP Path Abstraction Breaks Exploration
- **Good**: read_file() abstracts paths ("Epic 2nd Brain" → actual repo path)
- **Bad**: Can't browse/explore when you don't know exact paths
- **Missing**: Discovery tool (like ls but for projects)

**Impact**:
- **Phase 1 archival system useless**: Can archive files but can't find them later
- **User workflow broken**: "Find that PRD I completed last quarter" → impossible
- **Search degradation**: Archived docs invisible to search
- **ROI lost**: Phase 1 effort (8 hours) not delivering value

**Discovery - What's Actually Missing**:

```python
# Phase 1 PRD said this should work (line 169):
search_repo(query, exclude_archive=False)  # Search both active + archive

# Reality: This tool doesn't exist
# We have:
search_docs(query, doc_types, project_name)  # No archive awareness
search_epic_2nd_brain(query, doc_types, top_k)  # No archive indexing

# We need:
search_docs(query, include_archive=True, filters={status: "complete", date_range: "Q4 2025"})
```

**Solution Options**:

#### Option A: Add Archive Folders to search_docs() (Quick Fix - 30 min)
**What**: Update search_docs() to include archive/ folders in search paths
**Changes**:
```python
# In search_docs() - Update folder_map
folder_map = {
    "prd": [
        repo_path / "docs" / "prd",           # Active
        repo_path / "docs" / "prd" / "archive"  # Archive (recursive)
    ],
    "tech-req": [
        repo_path / "docs" / "tech-requirements",
        repo_path / "docs" / "tech-requirements" / "archive"
    ],
    # ... etc
}

# Search all paths, tag results with source
for path in folder_paths:
    results = search_in_folder(path)
    for result in results:
        result["source"] = "archive" if "archive" in str(path) else "active"
        result["priority"] = 0.5 if "archive" else 1.0
```
**Pros**: 30 min fix, search finds archive docs immediately
**Cons**: Still no date filtering, no metadata, no semantic search
**Validation**: Search "PRD" returns both active + archived docs

#### Option B: Add Archive Paths to RAG Indexing (Robust - 1 hour)
**What**: Update Phase 6 RAG to index archive folders with metadata
**Changes**:
```python
# In mcp_server/rag/epic_2nd_brain_rag.py
def get_index_paths(self):
    return [
        self.base_path / "docs" / "prd",           # Active
        self.base_path / "docs" / "prd" / "archive",  # Archive
        self.base_path / "docs" / "tech-requirements",
        self.base_path / "docs" / "tech-requirements" / "archive",
        # ...
    ]

# Add metadata during indexing
def index_documents(self):
    for file in files:
        metadata = {
            "source": "archive" if "archive" in str(file) else "active",
            "doc_type": infer_doc_type(file),
            "year": extract_year_from_path(file),  # From archive/2025/Q4/
            "quarter": extract_quarter_from_path(file)
        }
        # Index with metadata
```
**Pros**: Semantic search + metadata filtering, archive docs findable, proper solution
**Cons**: 1 hour effort, requires re-indexing
**Validation**:
- `search_epic_2nd_brain("PRD", filter_metadata={"source": "archive"})`
- `search_epic_2nd_brain("PRD", filter_metadata={"year": "2025", "quarter": "Q4"})`

#### Option C: Add list_files() Tool (Discovery - 30 min)
**What**: New MCP tool to browse project folders with metadata
**Changes**:
```python
@mcp.tool()
def list_files(
    project: str = "Epic 2nd Brain",
    folder: str = "docs/prd",
    include_archive: bool = True
) -> list:
    """
    List files in a project folder with metadata.

    Returns:
        List of files with metadata (status, date, size, source)
    """
    repo_path = PROJECT_CONFIG[project]["repo_path"]
    folder_path = repo_path / folder

    results = []
    for file in folder_path.rglob("*.md"):
        metadata = {
            "path": str(file.relative_to(repo_path)),
            "name": file.name,
            "source": "archive" if "archive" in str(file) else "active",
            "size": file.stat().st_size,
            "modified": file.stat().st_mtime,
            # Extract from frontmatter if exists
            "status": extract_frontmatter(file).get("status"),
            "date": extract_frontmatter(file).get("date")
        }
        results.append(metadata)

    return results
```
**Pros**: Discovery tool, browse archive, see metadata
**Cons**: Doesn't solve search problem, just adds browsing
**Validation**: `list_files("Epic 2nd Brain", "docs/prd/archive/2025/Q4")`

#### Option D: Add Document Frontmatter Metadata (Complete - 2 hours)
**What**: Add YAML frontmatter to all PRDs with status, dates
**Changes**:
```yaml
# At top of each PRD
---
status: Complete
created: 2025-11-01
completed: 2025-12-05
quarter: Q4 2025
initiative_id: abc123
project: Epic 2nd Brain
---
# PRD Title
...
```
**Pros**: Metadata source of truth, enables all filtering
**Cons**: 2 hours to add frontmatter to existing docs, ongoing maintenance
**Validation**: Parse frontmatter, filter by status/date

**Recommendation**:
1. **Immediate**: Option A (add archive to search_docs - 30 min) + Option C (list_files tool - 30 min) = 1 hour
2. **After indexing RAG**: Option B (index archive with metadata - 1 hour)
3. **Long-term**: Option D (frontmatter metadata - 2 hours, do incrementally)

**Why This Order**:
- **Quick win**: Options A+C make archive browsable/searchable in 1 hour
- **Proper solution**: Option B (after Issue #2 fixed) enables semantic search with metadata
- **Complete solution**: Option D enables rich filtering but takes time

**Status**: ⏳ Pending - Multiple fixes needed (1-4 hours depending on scope)

**Phase 1 Gap Analysis**:
- ✅ Built: Archive system (move files to archive/YYYY/QQ/)
- ✅ Built: Archival logic (archive PRDs when initiative complete)
- ❌ **Missing**: Archive search integration
- ❌ **Missing**: Metadata tracking (status, dates)
- ❌ **Missing**: File listing/discovery tool
- ❌ **Missing**: Date-based filtering

**Actual Phase 1 Completion**: ~50% (built infrastructure, didn't integrate with search)

---

### Issue #5: No Directory Listing Tool (Can't Browse Project Structure)

**Test Case**: Test 1.2 - "Check if orphaned folders cleaned up"

**Expected Behavior**:
```
1. list_files("Epic 2nd Brain", "docs/", recursive=True)
   → Shows directory tree
2. Verify docs/Failed/, docs/hold-for-later/ no longer exist
3. Quick visual confirmation in <30 seconds
```

**Actual Behavior** (9-step trial-and-error process):
```
Attempt 1: search_docs("Failed hold-for-later") → No results ❌
Attempt 2: search_epic_2nd_brain() → Not indexed ❌
Attempt 3-4: Bash find/ls commands → Repos not mounted in container ❌
Attempt 5: Notion search → Skipped (wrong approach)
Attempt 6: Check mount points → No project mounts ❌
Attempt 7: read_file("ROADMAP.md") → SUCCESS ✅ (discovered MCP works)
Attempt 8: read_file("docs/context/one-pagers/...") → SUCCESS ✅ (confirmed access)
Attempt 9: Try reading orphaned folders directly:
   - read_file("docs/Failed/README.md") → File not found ✅
   - read_file("docs/hold-for-later/README.md") → File not found ✅
   - read_file("docs/insights/context-engineering/research/README.md") → File not found ✅

CONCLUSION: Folders ARE cleaned up (not found = archived) ✅
BUT: Took 9 attempts to verify this simple fact ❌
```

**Time Waste**: 5-7 minutes for a 30-second task

**Root Cause**:
- **No directory listing tool**: Can't browse project structure without guessing paths
- **read_file() limitations**: Can read files but can't list directories
- **Error message ambiguity**: "File not found" could mean:
  - File doesn't exist (good - archived)
  - Folder doesn't exist (good - archived)
  - File path typo (bad - need to retry)
  - Parent folder exists but file missing (unclear)
- **Trial-and-error discovery**: Had to guess paths and infer from errors
- **No search by path**: search_docs() searches content, not paths/filenames

**Impact**:
- **Simple verification takes 5-7 min**: Should be <30 sec
- **User frustration**: "Why can't I just see what folders exist?"
- **Testing friction**: Every test requiring folder verification is slow
- **Workflow broken**: Can't explore project structure organically

**What's Missing**:

```python
# Need this:
list_files(project="Epic 2nd Brain", path="docs/", recursive=False)
# Returns:
[
  {"name": "prd", "type": "directory", "file_count": 12},
  {"name": "tech-requirements", "type": "directory", "file_count": 8},
  {"name": "sessions", "type": "directory", "file_count": 45},
  {"name": "context", "type": "directory", "file_count": 6},
  {"name": "archive", "type": "directory", "file_count": 23}
]

# Or this:
get_directory_tree(project="Epic 2nd Brain", path="docs/", depth=2)
# Returns:
"""
docs/
├── prd/ (12 files)
├── tech-requirements/ (8 files)
├── sessions/
│   ├── claude-chat/ (30 files)
│   └── claude-code/ (15 files)
├── context/
│   └── one-pagers/ (6 files)
└── archive/
    └── 2025/
        └── Q4/ (23 files)
"""
```

**Solution Options**:

#### Option A: Add list_files() MCP Tool (Essential - 30 min)
**What**: New tool to list directories and files with metadata
**Changes**:
```python
@mcp.tool()
def list_files(
    project: str = "Epic 2nd Brain",
    path: str = "docs/",
    recursive: bool = False,
    file_pattern: str = "*.md"
) -> list:
    """
    🎯 USE THIS: List files and folders in a project directory.

    IMPORTANT: Use this instead of bash ls/find commands. This tool
    provides structured directory listings with metadata.

    Args:
        project: Project name ("Epic 2nd Brain", "Legacy AI", "Lifeadmin")
        path: Relative path from repo root (default: "docs/")
        recursive: Include subdirectories (default: False)
        file_pattern: File filter (default: "*.md")

    Returns:
        List of files/folders with metadata

    Examples:
        - list_files("Epic 2nd Brain", "docs/")  # Top-level folders
        - list_files("Epic 2nd Brain", "docs/prd/", recursive=True)  # All PRDs
        - list_files("Legacy AI", "research/")  # Legacy AI folders
    """
    repo_path = PROJECT_CONFIG[project]["repo_path"]
    target_path = repo_path / path

    if not target_path.exists():
        return [{"error": f"Path not found: {path}"}]

    results = []

    if recursive:
        # Recursive listing
        for item in target_path.rglob(file_pattern):
            results.append({
                "path": str(item.relative_to(repo_path)),
                "name": item.name,
                "type": "file" if item.is_file() else "directory",
                "size": item.stat().st_size if item.is_file() else None,
                "modified": item.stat().st_mtime
            })
    else:
        # Shallow listing (directories + matching files)
        for item in target_path.iterdir():
            if item.is_dir():
                file_count = len(list(item.glob("*.md")))
                results.append({
                    "path": str(item.relative_to(repo_path)),
                    "name": item.name,
                    "type": "directory",
                    "file_count": file_count
                })
            elif item.match(file_pattern):
                results.append({
                    "path": str(item.relative_to(repo_path)),
                    "name": item.name,
                    "type": "file",
                    "size": item.stat().st_size,
                    "modified": item.stat().st_mtime
                })

    return sorted(results, key=lambda x: (x["type"] != "directory", x["name"]))
```
**Pros**: 30 min fix, enables all folder exploration, solves Issue #4 discovery too
**Cons**: Adds another tool (but essential one)
**Validation**:
- `list_files("Epic 2nd Brain", "docs/")` shows folders, no Failed/ or hold-for-later/
- `list_files("Epic 2nd Brain", "docs/archive/2025/Q4/", recursive=True)` shows archived PRDs

#### Option B: Add get_directory_tree() Tool (Visual - 45 min)
**What**: Tree-like visualization of directory structure
**Changes**:
```python
@mcp.tool()
def get_directory_tree(
    project: str = "Epic 2nd Brain",
    path: str = "docs/",
    depth: int = 2
) -> str:
    """
    Get directory tree visualization.

    Returns:
        Tree-style string showing folder structure
    """
    repo_path = PROJECT_CONFIG[project]["repo_path"]
    target_path = repo_path / path

    def build_tree(current_path, current_depth, prefix=""):
        if current_depth > depth:
            return ""

        tree = ""
        items = sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for i, item in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "

            if item.is_dir():
                file_count = len(list(item.glob("*.md")))
                tree += f"{prefix}{connector}{item.name}/ ({file_count} files)\n"

                if current_depth < depth:
                    extension = "    " if is_last else "│   "
                    tree += build_tree(item, current_depth + 1, prefix + extension)
            else:
                tree += f"{prefix}{connector}{item.name}\n"

        return tree

    return build_tree(target_path, 0)
```
**Pros**: Beautiful visualization, easy to scan
**Cons**: 45 min effort, text output (harder to parse programmatically)
**Validation**: Visual inspection of tree shows clean structure

#### Option C: Enhance read_file() Error Messages (Quick - 15 min)
**What**: Better error messages to distinguish file vs folder issues
**Changes**:
```python
def read_file(path: str, project: str = "Epic 2nd Brain") -> str:
    # ... existing code ...

    if not full_path.exists():
        # Check if parent directory exists
        parent = full_path.parent
        if not parent.exists():
            return f"Error: Directory not found: {parent.relative_to(repo_path)}/"
        else:
            return f"Error: File '{full_path.name}' not found in {parent.relative_to(repo_path)}/"

    if full_path.is_dir():
        # List directory contents instead of error
        files = list(full_path.glob("*.md"))
        return f"Error: Path is a directory. Contains {len(files)} files. Use list_files() to browse."
```
**Pros**: 15 min fix, helps with existing tools
**Cons**: Doesn't solve core problem (still can't list directories)
**Validation**: read_file("docs/Failed/") gives helpful error

**Recommendation**:
1. **Immediate**: Option A (list_files tool - 30 min) - **Essential for all testing**
2. **Nice-to-have**: Option B (tree visualization - 45 min) - Good UX but not critical
3. **Quick win**: Option C (better errors - 15 min) - Do this regardless

**Why Option A is Essential**:
- **Solves Issue #4 too**: Can browse archive folders
- **Testing requirement**: Every test needs to verify folder states
- **User workflow**: "What folders exist?" is a fundamental question
- **30 min investment**: Saves hours in testing time

**Status**: ⏳ Pending - Option A is critical path for all future testing

**Test 1.2 Result**: ✅ **PASSED** (folders are archived, but took 9 attempts to verify)

---

### Issue #6: Active/Archive Directory Structure Never Created (Phase 1 ~25% Complete)

**Test Case**: Test 1.3 - "Active/archive structure operational"

**Expected Behavior**:
```
1. list_files("Epic 2nd Brain", "docs/prd/") shows:
   - active/ directory (in-progress PRDs)
   - archive/ directory with 2025/Q4/ subdirectories
2. PRDs organized by status (active vs completed)
3. Structure matches Phase 1 spec (lines 109-145 in PRD)
```

**Actual Behavior**:
```
Attempt 1: bash ls -la /Users/.../ai-assistant/docs/prd/
   → No such file or directory ❌

Attempt 2: read_file("docs/prd/active", project="Epic 2nd Brain")
   → Error: File not found at .../ai-assistant/docs/prd/active ❌
   → Revealed actual repo path (helpful!)

Attempt 3: read_file("README.md", project="Epic 2nd Brain")
   → SUCCESS ✅ (confirmed MCP tool works, repo accessible)

Attempt 4: Python script to check directories
   → os.path.exists(repo_path + "/docs/prd") = False ❌
   → os.path.exists(repo_path + "/docs") = False ❌

CONCLUSION: No docs/ directory exists at all! ❌
```

**Root Cause**:
- **Phase 1 incomplete**: Wrote `archival.py` code but **NEVER created actual folder structure**
- **Missing setup step**: No mkdir commands run, no initialization script
- **Code vs infrastructure gap**: Functions exist to archive files, but target directories don't exist
- **No validation**: Phase 1 marked complete without verifying folder structure created

**What's Missing**:

```bash
# Expected structure from Phase 1 PRD (lines 109-145):
ai-assistant/
├── docs/
│   ├── README.md                    # ❌ Doesn't exist
│   ├── prd/
│   │   ├── active/                  # ❌ Doesn't exist
│   │   │   ├── live-context-control-v3.md
│   │   │   └── prototype-validation.md
│   │   └── archive/                 # ❌ Doesn't exist
│   │       ├── 2025/
│   │       │   └── Q4/
│   │       │       ├── context-sync-bridge.md
│   │       │       └── rag-implementation.md
│   │       └── README.md
│   ├── tech-requirements/
│   │   ├── active/                  # ❌ Doesn't exist
│   │   └── archive/2025/Q4/         # ❌ Doesn't exist
│   ├── sessions/
│   │   ├── claude-chat/
│   │   │   ├── active/              # ❌ Doesn't exist
│   │   │   └── archive/2025/Q4/     # ❌ Doesn't exist
│   │   └── claude-code/
│   │       ├── active/              # ❌ Doesn't exist
│   │       └── archive/2025/Q4/     # ❌ Doesn't exist
│   └── archive/                     # ❌ Doesn't exist
│       ├── failed-experiments/
│       ├── hold-for-later/
│       └── context-engineering-research/

# Current reality:
ai-assistant/
├── (no docs/ directory at all!)
```

**Impact**:
- **Phase 1 archival.py useless**: Can't archive files if target folders don't exist
- **Archive function will fail**: `archive_file()` will crash when trying to move files
- **Search integration impossible**: Can't search archive if it doesn't exist (compounds Issue #4)
- **ROI completely lost**: Phase 1 effort (8 hours) delivered 0% value

**Phase 1 Actual Completion Revised**:
- ✅ Built: `archival.py` module with functions (2 hours)
- ✅ Built: `backup.py` module (2 hours)
- ✅ Built: Package structure (1 hour)
- ❌ **Never did**: Create actual folder structure (0 hours)
- ❌ **Never did**: Integrate with search (0 hours, Issue #4)
- ❌ **Never did**: Migrate existing PRDs to active/archive (0 hours)
- ❌ **Never did**: Test end-to-end archival workflow (0 hours)

**Actual Phase 1 Completion**: ~25% (built code modules, never created infrastructure or tested)

**Discovery - What Actually Exists**:
```bash
# Run this to see what's actually there:
cd /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant
tree -L 2 docs/  # Likely returns "docs/: No such file or directory"

# What Phase 1 SHOULD have done:
mkdir -p docs/{prd,tech-requirements,sessions/claude-{chat,code},context,archive}/{active,archive/2025/Q4}
```

**Solution Options**:

#### Option A: Create Directory Structure Now (Quick Fix - 5 min)
**What**: Run mkdir commands to create all missing folders
**Changes**:
```bash
cd /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant

# Create full structure from Phase 1 spec
mkdir -p docs/prd/active
mkdir -p docs/prd/archive/2025/{Q1,Q2,Q3,Q4}
mkdir -p docs/tech-requirements/active
mkdir -p docs/tech-requirements/archive/2025/{Q1,Q2,Q3,Q4}
mkdir -p docs/sessions/claude-chat/active
mkdir -p docs/sessions/claude-chat/archive/2025/{Q1,Q2,Q3,Q4}
mkdir -p docs/sessions/claude-code/active
mkdir -p docs/sessions/claude-code/archive/2025/{Q1,Q2,Q3,Q4}
mkdir -p docs/context/one-pagers
mkdir -p docs/archive/{failed-experiments,hold-for-later,context-engineering-research}

# Create README files
cat > docs/README.md << 'EOF'
# Documentation Organization

See Phase 1 spec for details on active/archive structure.

## Structure
- active/ - In-progress documents
- archive/YYYY/QQ/ - Completed documents by quarter

## Archival Logic
Documents are auto-archived when initiative status = "✅ Complete"
EOF

cat > docs/prd/archive/README.md << 'EOF'
# Archived PRDs

Search works across both active + archive (lower priority for archive).
Use search_epic_2nd_brain() for semantic search.
EOF
```
**Pros**: 5 min fix, enables archival system immediately
**Cons**: Manual one-time setup, doesn't prevent future missing folders
**Validation**:
- `list_files("Epic 2nd Brain", "docs/prd/")` shows active/ and archive/
- `archive_file()` function works without errors

#### Option B: Add Initialization Script (Robust - 30 min)
**What**: Create `scripts/init_repo_structure.py` that sets up all folders
**Changes**:
```python
#!/usr/bin/env python3
"""
Initialize repository structure for Phase 1 active/archive system.
Run this once to set up all required folders.
"""

from pathlib import Path

def init_repo_structure(repo_path: Path):
    """Create all folders from Phase 1 spec."""

    # Define structure
    structure = {
        "docs/prd": ["active", "archive/2025/Q1", "archive/2025/Q2", "archive/2025/Q3", "archive/2025/Q4"],
        "docs/tech-requirements": ["active", "archive/2025/Q1", "archive/2025/Q2", "archive/2025/Q3", "archive/2025/Q4"],
        "docs/sessions/claude-chat": ["active", "archive/2025/Q1", "archive/2025/Q2", "archive/2025/Q3", "archive/2025/Q4"],
        "docs/sessions/claude-code": ["active", "archive/2025/Q1", "archive/2025/Q2", "archive/2025/Q3", "archive/2025/Q4"],
        "docs/context": ["one-pagers/infrastructure", "one-pagers/legacy-ai"],
        "docs/archive": ["failed-experiments", "hold-for-later", "context-engineering-research"]
    }

    # Create all folders
    for base_path, subdirs in structure.items():
        for subdir in subdirs:
            folder = repo_path / base_path / subdir
            folder.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {folder.relative_to(repo_path)}")

    # Create README files
    create_readme_files(repo_path)

    print("\n🎉 Repository structure initialized!")

if __name__ == "__main__":
    repo_path = Path.home() / "Documents" / "1. Projects" / "ai-assistant"
    init_repo_structure(repo_path)
```
**Pros**: Repeatable, can re-run if folders deleted, self-documenting
**Cons**: 30 min to write, user must remember to run it
**Validation**: Run script, verify all folders created

#### Option C: Add Initialization to MCP start_session (Proactive - 45 min)
**What**: Check folder structure on session start, auto-create if missing
**Changes**:
```python
# In start_session() MCP tool
def start_session(...):
    # ... existing code ...

    # Check repository structure (Phase 1)
    repo_path = PROJECT_CONFIG[project]["repo_path"]
    required_folders = [
        "docs/prd/active",
        "docs/prd/archive/2025/Q4",
        "docs/tech-requirements/active",
        # ... etc
    ]

    missing_folders = []
    for folder in required_folders:
        if not (repo_path / folder).exists():
            missing_folders.append(folder)

    if missing_folders:
        # Auto-create or warn user
        for folder in missing_folders:
            (repo_path / folder).mkdir(parents=True, exist_ok=True)

        return {
            "warning": "Repository structure was incomplete",
            "action": "Auto-created missing folders",
            "folders_created": missing_folders
        }

    # ... continue session ...
```
**Pros**: Self-healing, no manual setup required, works on first use
**Cons**: 45 min effort, adds complexity to start_session
**Validation**: Delete folders, start session, verify auto-created

#### Option D: Migrate Existing PRDs to Active/Archive (Complete - 1-2 hours)
**What**: Move existing PRD files into active/ or archive/ based on status
**Changes**:
```bash
# After Option A creates folders:

# Move in-progress PRDs to active/
mv docs/prd/live-context-control-v3.md docs/prd/active/
mv docs/prd/prototype-validation.md docs/prd/active/

# Move completed PRDs to archive/2025/Q4/
mv docs/prd/context-sync-bridge.md docs/prd/archive/2025/Q4/
mv docs/prd/rag-implementation.md docs/prd/archive/2025/Q4/

# Update references in code/configs
```
**Pros**: Full implementation of Phase 1 spec
**Cons**: 1-2 hours, need to determine status of each PRD, might break existing paths
**Validation**: All PRDs in correct locations, search still works

**Recommendation**:
1. **Immediate**: Option A (create folders manually - 5 min) - **Unblocks archival system**
2. **Short-term**: Option B (init script - 30 min) - **Repeatable setup**
3. **Medium-term**: Option C (auto-init on session start - 45 min) - **Self-healing**
4. **Long-term**: Option D (migrate existing PRDs - 1-2 hours) - **Full Phase 1 implementation**

**Why This Order**:
- **Quick win**: Option A unblocks archival.py functions immediately (5 min)
- **Robustness**: Option B makes setup repeatable for other developers/machines
- **User experience**: Option C prevents this from happening again
- **Complete solution**: Option D fully implements Phase 1 vision

**Status**: ⏳ Pending - Option A is critical to unblock archival system (5 min)

**Test 1.3 Result**: ❌ **FAILED** (no directory structure exists at all)

**Phase 1 Gap Analysis (Updated from Issue #4)**:
- ✅ Built: Archive system code (`archival.py` module)
- ✅ Built: Backup system code (`backup.py` module)
- ✅ Built: Package structure (utils/ modules)
- ❌ **Never did**: Create actual folder structure (Option A needed)
- ❌ **Never did**: Integrate with search (Issue #4)
- ❌ **Never did**: Migrate existing PRDs to active/archive
- ❌ **Never did**: Test end-to-end archival workflow
- ❌ **Never did**: Add metadata tracking (Issue #4)
- ❌ **Never did**: Add file listing tool (Issue #5)

**Actual Phase 1 Completion**: ~25% (down from 50% estimate in Issue #4)

---

### Issue #7: PRD Archival Not Triggered - Missing prd_path Extraction Logic

**Test Case**: Test 3.1 - "Complete initiative end-to-end" - **User discovered archival didn't happen**

**Expected Behavior**:
```
1. Mark "Live Context Control v3" as "✅ Complete" in Strategy Board
2. Run end_session() for that initiative
3. PRD auto-archived to docs/prd/archive/2025/Q4/live-context-control-v3.md
4. Strategy Board "PRD Location" updated with archive path
```

**Actual Behavior**:
```
1. Marked initiative complete ✓
2. Ran end_session() (updated ROADMAP.md) ✓
3. PRD still at docs/prd/live-context-control-v3.md ❌ NOT ARCHIVED
4. Archive folder doesn't exist ❌
5. No archival happened
```

**User's Discovery**:
- File still in original location: `docs/prd/live-context-control-v3.md`
- No archive folder created
- Correctly questioned my claim that "Test 3.1 passed"

**Root Cause Investigation**:

Looking at the code flow:

1. **end_session()** (full_server.py:818-826):
```python
# Get PRD path from initiative if available
prd_path = None
prd_prop = initiative["properties"].get("PRD", {})
if prd_prop.get("url"):
    # Extract filename from URL if it's a file path
    prd_url = prd_prop["url"]
    if "docs/prd/" in prd_url:  # ← Only works if URL contains "docs/prd/"
        prd_path = prd_url.split("docs/prd/")[-1]
        prd_path = f"docs/prd/{prd_path}"
```

2. **sync_roadmap_with_strategy_board()** (roadmap_helpers.py:213-219):
```python
# Archive PRD if complete
if strategy_board_status == "✅ Complete" and prd_path:  # ← Requires prd_path
    prd_file_path = Path(prd_path)
    if prd_file_path.exists():
        archive_result = archive_file(prd_file_path, force=True)
        if archive_result["status"] == "success":
            result["prd_archived"] = True
```

3. **archive_file()** (archival.py:98):
```python
# Create archive directory
archive_dir.mkdir(parents=True, exist_ok=True)  # ← Would auto-create folders
```

**The Breakage**:
```
end_session() tries to extract prd_path from Notion "PRD" property URL
↓
If URL doesn't contain "docs/prd/" → prd_path = None
↓
sync_roadmap_with_strategy_board() called with prd_path=None
↓
Archival logic skipped (line 213: if prd_path)
↓
No archival happens, no archive folder created
```

**Why It Failed for Live Context Control v3**:
- Notion "PRD" property likely contains:
  - Option A: GitHub URL (not "docs/prd/" path)
  - Option B: Markdown link format `[PRD](docs/prd/...)`
  - Option C: Empty/not set
- Current code only handles raw URLs with "docs/prd/" substring
- So `prd_path = None` → archival never triggered

**Impact**:
- **Phase 3 archival BROKEN**: Doesn't work when initiative marked complete
- **My testing error**: I incorrectly reported Test 3.1 as passing
- **User confusion**: Expected archival to work, file still in original location
- **Folder structure**: Would have been auto-created IF archival was triggered (line archival.py:98)

**Solution Options**:

#### Option A: Fix PRD Path Extraction (Robust - 30 min)
**What**: Improve path extraction to handle multiple URL formats
**Changes**:
```python
# In end_session() - Better PRD path extraction
prd_path = None
prd_prop = initiative["properties"].get("PRD", {})

if prd_prop.get("url"):
    prd_url = prd_prop["url"]

    # Handle multiple formats:
    # 1. Full URL: https://github.com/.../docs/prd/file.md
    # 2. Relative path: docs/prd/file.md
    # 3. Markdown link: [PRD](docs/prd/file.md)

    # Extract path from URL
    if "docs/prd/" in prd_url:
        # Split on "docs/prd/" and take everything after
        prd_path = "docs/prd/" + prd_url.split("docs/prd/")[-1]

        # Clean up (remove markdown syntax, URL fragments, etc.)
        prd_path = prd_path.split(")")[0]  # Remove trailing markdown
        prd_path = prd_path.split("#")[0]  # Remove URL fragments
        prd_path = prd_path.strip()

elif prd_prop.get("rich_text"):
    # Try extracting from rich text
    for text_obj in prd_prop["rich_text"]:
        text = text_obj.get("text", {}).get("content", "")
        if "docs/prd/" in text:
            prd_path = "docs/prd/" + text.split("docs/prd/")[-1]
            break

# Fallback: Use ROADMAP.md PRD link
if not prd_path:
    roadmap_path = repo_path / "ROADMAP.md"
    if roadmap_path.exists():
        roadmap_content = roadmap_path.read_text()
        # Find initiative row, extract PRD link
        for line in roadmap_content.split("\n"):
            if initiative_name_str in line:
                # Look for [PRD](docs/prd/...) pattern
                prd_match = re.search(r'\[PRD\]\((docs/prd/[^\)]+)\)', line)
                if prd_match:
                    prd_path = prd_match.group(1)
                    break
```
**Pros**: Handles multiple URL formats, robust, works with existing data
**Cons**: 30 min effort, need regex for markdown links
**Validation**:
- Mark initiative complete
- Check if PRD archived
- Verify archive folder created

#### Option B: Require Structured PRD Property (Breaking Change - 1 hour)
**What**: Change Notion schema to use "Files" property instead of URL
**Changes**:
- Update Strategy Board schema: PRD property → Files & media type
- Upload PRD files to Notion or use file references
- Update end_session() to handle file property
**Pros**: Clean data model, no path extraction needed
**Cons**: Breaking change, need to update all existing initiatives
**Validation**: Migrate existing initiatives, test archival

#### Option C: Manual archival.py Call (Workaround - 5 min)
**What**: Add separate MCP tool to manually archive PRDs
**Changes**:
```python
@mcp.tool()
def archive_prd_manually(initiative_name: str, prd_filename: str) -> dict:
    """
    Manually archive a PRD when initiative complete.

    Use this if auto-archival didn't work.
    """
    prd_path = Path(f"docs/prd/{prd_filename}")
    if not prd_path.exists():
        return {"error": f"PRD not found: {prd_path}"}

    result = archive_file(prd_path, force=True)
    return result
```
**Pros**: 5 min fix, unblocks user immediately
**Cons**: Manual step, doesn't fix root cause
**Validation**: Call tool, verify archival works

**Recommendation**:
1. **Immediate**: Option C (manual tool - 5 min) to unblock current situation
2. **Short-term**: Option A (fix path extraction - 30 min) to solve root cause
3. **Skip**: Option B (too disruptive)

**Why Option A is Best**:
- **Fixes root cause**: PRD path extraction works for all formats
- **No breaking changes**: Works with existing Notion data
- **Robust**: Handles GitHub URLs, markdown links, relative paths
- **User value**: Auto-archival works as designed in Phase 3 PRD

**Status**: ⏳ Pending - Option C immediate, Option A short-term

**Test 3.1 Status**: ❌ **FAILED** (archival did not happen, folder structure issue secondary)

**Phase 3 Status Update**: Partially working - ROADMAP.md sync works, but PRD archival broken

---

### Issue #8: Phase 5 Schema Detection Built but Never Used (0% Functional)

**Test Cases**: All Phase 5 tests (5.1, 5.2, 5.3, 5.4)

**Expected Behavior**:
```
1. NotionSchemaDetector.get_strategy_board_schema(db_id) called on first Strategy Board access
2. Schema cached in memory for session lifetime
3. All property access uses schema.get_property("initiative_name") instead of hardcoded "Initiative Name"
4. Renamed properties detected via fuzzy matching
5. Fallback to defaults if detection fails
```

**Actual Behavior**:
```
Test 5.1: Schema detection for Strategy Board
   → schema_detector imported ✓
   → schema_detector instantiated ✓
   → schema_detector.get_strategy_board_schema() usage: 0 ❌
   → All property access hardcoded (15 occurrences)

Test 5.2: Schema detection for Sessions DB
   → schema_detector.get_sessions_schema() usage: 0 ❌
   → All properties hardcoded

Test 5.3: Renamed properties handling
   → CANNOT TEST: Schema detector never called ❌

Test 5.4: Fallback to defaults
   → CANNOT TEST: Always uses hardcoded names (so technically "fallback" always happens) ❌
```

**Code Analysis**:
```python
# full_server.py line 40: Import exists ✓
from mcp_server.utils.notion_schema import NotionSchemaDetector

# full_server.py line 74: Instantiation exists ✓
schema_detector = NotionSchemaDetector(notion_client) if notion_client else None

# full_server.py lines 757-1482: Property access is hardcoded ❌
initiative["properties"].get("Initiative Name", {})  # Line 757 - hardcoded
properties["Status"] = {"select": {"name": new_status}}  # Line 1482 - hardcoded

# Should be:
schema = schema_detector.get_strategy_board_schema(STRATEGY_BOARD_DB_ID)
initiative["properties"].get(schema.get_property("initiative_name"), {})
```

**Root Cause**:
- **Phase 5 incomplete**: Built `notion_schema.py` module (340 lines) with all detection logic
- **Never integrated**: `schema_detector` instantiated but never called
- **All property names hardcoded**: 15 occurrences of hardcoded property names in full_server.py
- **No validation**: Phase 5 marked complete without integration testing
- **Pattern repeat**: Same as Issue #2 (RAG built, never indexed) and Issue #6 (archival code built, folders never created)

**Impact**:
- **4 hours wasted**: Phase 5 effort (schema detection module) not functional
- **Schema brittleness**: If Notion properties renamed, code breaks immediately
- **Manual maintenance**: Every property rename requires code changes
- **Phase 5 goal missed**: "Remove hardcoded assumptions" not achieved

**What Exists vs What's Missing**:
```
✅ Built: notion_schema.py (NotionSchemaDetector class)
✅ Built: NotionSchema wrapper class with safe property access
✅ Built: Fuzzy matching for renamed properties
✅ Built: Fallback to defaults if detection fails
✅ Built: In-memory caching
❌ Missing: Integration with full_server.py tools
❌ Missing: Replace hardcoded property names with schema.get_property()
❌ Missing: Call schema_detector.get_*_schema() on session start
❌ Missing: Test with renamed properties
```

**Hardcoded Property References** (should be 0):
- "Initiative Name": 4 occurrences
- "Status": 5 occurrences
- "PRD": 1 occurrence
- "Priority Score": 2 occurrences
- "Completed Date": 3 occurrences
- **Total**: 15 hardcoded references (all must be replaced)

**Solution Options**:

#### Option A: Integrate Schema Detection Immediately (Essential - 2 hours)
**What**: Replace all hardcoded property names with schema.get_property() calls
**Changes**:
```python
# In start_session() or module initialization
def init_schemas():
    """Initialize Notion schemas on first use."""
    global strategy_board_schema, sessions_schema

    if schema_detector:
        strategy_board_schema = schema_detector.get_strategy_board_schema(STRATEGY_BOARD_DB_ID)
        sessions_schema = schema_detector.get_sessions_schema(SESSIONS_DB_ID)
    else:
        # Use hardcoded defaults if schema detector unavailable
        strategy_board_schema = None
        sessions_schema = None

# Replace all property access (example - line 757):
# Before:
title_prop = initiative["properties"].get("Initiative Name", {})

# After:
prop_name = strategy_board_schema.get_property("initiative_name") if strategy_board_schema else "Initiative Name"
title_prop = initiative["properties"].get(prop_name, {})

# Or more concisely:
def get_prop_name(schema, key, default):
    """Safe property name getter with fallback."""
    return schema.get_property(key) if schema else default

title_prop = initiative["properties"].get(
    get_prop_name(strategy_board_schema, "initiative_name", "Initiative Name"),
    {}
)
```

**Files to Update**:
1. `full_server.py` (757, 763, 799, 1363, 1482 + ~10 more locations)
2. `roadmap_helpers.py` (if has hardcoded property names)
3. Any other utils with Notion property access

**Effort Breakdown**:
- Init schemas on startup: 15 min
- Replace 15 hardcoded references: 60 min (4 min each)
- Test with real Notion DB: 30 min
- Handle edge cases (schema None): 15 min
- **Total**: ~2 hours

**Pros**: Achieves Phase 5 goal, schema changes don't break code
**Cons**: 2 hours effort, need to test all Notion interactions
**Validation**:
- Rename "Initiative Name" to "Initiative Title" in Notion
- Run end_session() → should work without code changes
- Verify fuzzy matching detected renamed property

#### Option B: Lazy Schema Loading (Robust - 2.5 hours)
**What**: Load schemas on first property access, not on startup
**Changes**:
```python
# Global schema cache
_schemas = {}

def get_strategy_board_schema():
    """Get Strategy Board schema (lazy-loaded)."""
    global _schemas

    if "strategy_board" not in _schemas:
        if schema_detector:
            _schemas["strategy_board"] = schema_detector.get_strategy_board_schema(STRATEGY_BOARD_DB_ID)
        else:
            # Create default schema
            _schemas["strategy_board"] = NotionSchema(None, defaults={
                "initiative_name": "Initiative Name",
                "status": "Status",
                # ... etc
            })

    return _schemas["strategy_board"]

# Usage:
schema = get_strategy_board_schema()
title_prop = initiative["properties"].get(schema.get_property("initiative_name"), {})
```
**Pros**: Defers API calls until needed, clean abstraction
**Cons**: 30 min extra effort vs Option A
**Validation**: Same as Option A

#### Option C: Skip Phase 5 (Not Recommended)
**What**: Remove schema detection code, keep hardcoded names
**Changes**:
- Delete `notion_schema.py`
- Remove `schema_detector` import and instantiation
- Document that property names are hardcoded
**Pros**: 0 effort, already working with hardcoded names
**Cons**: Fragile, Phase 5 goal abandoned, 4 hours wasted
**Not Recommended**: Phase 5 goal is valuable - schema changes should not break code

**Recommendation**:
1. **Short-term**: Option A (integrate now - 2 hours) - **Completes Phase 5 properly**
2. **Alternative**: Option B (lazy loading - 2.5 hours) - **More robust but not critical**
3. **Skip**: Option C (abandon Phase 5) - **Only if schema changes are rare**

**Why Option A is Best**:
- **Completes Phase 5**: Achieves the goal stated in PRD
- **User value**: Schema changes don't require code updates (time saved)
- **2 hours effort**: Reasonable for 15 property replacements
- **Low risk**: Defaults still work if schema detection fails

**Status**: ⏳ Pending - Phase 5 code complete, needs integration (2 hours)

**Test Results**:
- Test 5.1: ❌ FAILED (schema detector never called for Strategy Board)
- Test 5.2: ❌ FAILED (schema detector never called for Sessions DB)
- Test 5.3: ❌ CANNOT TEST (fuzzy matching not used)
- Test 5.4: ❌ CANNOT TEST (always uses hardcoded, so "fallback" = 100% of time)

**Phase 5 Status**: **Built but not integrated (0% functional)**

---

### Issue #9: Phase 7 Handoff Creation Failed - Wrong Directory + Missing Infrastructure

**Test Case**: Test 7.1 - "Create handoff in Claude Chat after PRD approval"

**Expected Behavior**:
```
1. User approves PRD in Claude Chat
2. Claude Chat auto-creates handoff file at: docs/handoffs/YYYY-MM-DD-to-claude-code-[topic].md
3. Handoff format: YAML frontmatter with to, from, initiative_id, prd_path, etc.
4. Claude Code can discover handoff on next session start
```

**Actual Behavior**:
```
Test 7.1: Create handoff after PRD approval
   → User approved PRD ✓
   → Claude Chat attempted to create handoff ✓
   → Created at WRONG location: 2-areas/.../projects/.../handoffs/... ❌
   → Expected location: docs/handoffs/YYYY-MM-DD-... ❌
   → File write returned "success" but file not actually at claimed location ❌
   → docs/ directory doesn't exist (same as Issue #6) ❌
```

**User's Discovery Process**:
1. User asked to approve PRD for "Second Brain Sync" project
2. Claude Chat created handoff file
3. User checked for handoff: File NOT found at expected location
4. Claude Chat claimed file was at `2-areas/epic-2nd-brain-infrastructure/projects/second-brain-sync/handoffs/...`
5. User verified: No `docs/` directory exists in ai-assistant repo
6. **Issue #6 repeated**: Same missing folder structure problem

**Root Causes**:

#### 1. Wrong Handoff Directory Path
**Code Assumed**: Handoff files go in `docs/handoffs/`
**Reality**: Created in project-specific subfolder instead
**Why**: Claude Chat didn't have correct repo structure context

#### 2. No docs/ Directory (Issue #6 Repeat)
**Expected**: `docs/handoffs/` directory exists
**Reality**: No `docs/` directory at all in ai-assistant repo
**Why**: Same as Issue #6 - folder structure never created during Phase 1

#### 3. No Directory Validation
**What Happened**: create_file tool returned "success"
**Reality**: File created somewhere else OR error not surfaced
**Why**: No validation that handoff is in correct location for Claude Code to discover

#### 4. Cross-Agent Confusion
**Claude Chat assumption**: Project-specific handoffs folder is fine
**Claude Code expectation**: Handoffs are in central `docs/handoffs/` location
**Gap**: No shared schema for handoff file locations

**Impact**:
- **Phase 7 handoff workflow BROKEN**: Cannot create handoffs that Claude Code can discover
- **User workflow broken**: Manual handoffs required (defeats automation goal)
- **Cross-agent communication failed**: Claude Chat → Claude Code handoff not working
- **Issue #6 blocks Phase 7**: Missing folder structure prevents handoff storage

**What's Missing**:

```bash
# Expected structure (from Phase 7 spec):
ai-assistant/
├── docs/
│   ├── handoffs/                           # ❌ Doesn't exist
│   │   ├── 2025-12-15-to-claude-code-architecture-build.md
│   │   ├── 2025-12-14-to-claude-chat-prd-approval.md
│   │   └── archive/                        # ❌ Doesn't exist
│   │       └── 2025/Q4/

# What Claude Chat actually created:
2-areas/epic-2nd-brain-infrastructure/
└── projects/
    └── second-brain-sync/
        └── handoffs/                        # ❌ Wrong location
            └── 2025-12-15-to-claude-code-architecture-build.md
```

**Solution Options**:

#### Option A: Create Handoffs Directory + Update Handoff Creation (Quick Fix - 30 min)
**What**: Create `docs/handoffs/` folder and update handoff creation logic
**Changes**:
```bash
# Step 1: Create directory
cd /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant
mkdir -p docs/handoffs/archive/2025/{Q1,Q2,Q3,Q4}

# Step 2: Update handoff creation in Claude Chat
# (This is done via MCP tools or instructions to Claude Chat)
# Location: docs/handoffs/YYYY-MM-DD-to-{agent}-{topic}.md
```

**Handoff File Template**:
```yaml
---
to: claude-code
from: claude-chat
initiative_id: abc123
initiative_name: "Second Brain Sync"
prd_path: "docs/prd/second-brain-sync.md"
created: 2025-12-15T10:30:00
status: pending
priority: high
---

# Handoff: Second Brain Sync Architecture Build

## Context
User approved PRD for Second Brain Sync project.

## Next Steps for Claude Code
1. Read PRD at docs/prd/second-brain-sync.md
2. Design architecture for sync engine
3. Create tech requirements document

## Success Criteria
- Architecture diagram created
- Tech requirements documented
- Ready to start implementation
```

**Pros**: 30 min fix, enables Phase 7 handoff workflow
**Cons**: Manual folder creation, still need to fix Claude Chat handoff logic
**Validation**:
- Approve PRD in Claude Chat
- Check `docs/handoffs/` for new handoff file
- Start Claude Code session → should detect handoff

#### Option B: Combine with Issue #6 Fix (Comprehensive - 45 min)
**What**: Create full directory structure (Issue #6) + handoff folders
**Changes**:
```bash
# Create all Phase 1 + Phase 7 folders
mkdir -p docs/{prd,tech-requirements,sessions/claude-{chat,code}}/{active,archive/2025/Q4}
mkdir -p docs/handoffs/archive/2025/{Q1,Q2,Q3,Q4}
mkdir -p docs/context/one-pagers
mkdir -p docs/archive/{failed-experiments,hold-for-later,context-engineering-research}

# Create README for handoffs
cat > docs/handoffs/README.md << 'EOF'
# Claude Code ↔ Claude Chat Handoffs

This directory contains handoff files for cross-agent communication.

## File Naming Convention
- Format: YYYY-MM-DD-to-{agent}-{topic}.md
- Example: 2025-12-15-to-claude-code-architecture-build.md

## Handoff Lifecycle
1. Created: Claude Chat creates handoff after PRD approval (or other trigger)
2. Detected: Claude Code auto-detects on session start
3. Accepted: Claude Code loads initiative and marks handoff as accepted
4. Archived: Handoff moved to archive/YYYY/QQ/ after completion
EOF
```

**Pros**: Fixes Issue #6 + Issue #9 together, complete infrastructure setup
**Cons**: 45 min effort
**Validation**:
- All folders exist
- Handoff workflow works end-to-end
- Claude Code discovers handoffs

#### Option C: Add Handoff Validation to MCP Tools (Robust - 1 hour)
**What**: Add validation to create_handoff MCP tool
**Changes**:
```python
@mcp.tool()
def create_handoff(
    to_agent: str,
    from_agent: str,
    initiative_id: str,
    initiative_name: str,
    prd_path: str,
    context: str,
    next_steps: str,
    project: str = "Epic 2nd Brain"
) -> dict:
    """
    Create a handoff file for cross-agent communication.

    Args:
        to_agent: Target agent (claude-code, claude-chat)
        from_agent: Source agent (claude-code, claude-chat)
        initiative_id: Notion initiative ID
        initiative_name: Initiative name
        prd_path: Relative path to PRD
        context: Context for next agent
        next_steps: What next agent should do
        project: Project name

    Returns:
        {"status": "success", "handoff_path": "docs/handoffs/..."}
    """
    repo_path = PROJECT_CONFIG[project]["repo_path"]
    handoffs_dir = repo_path / "docs" / "handoffs"

    # Ensure directory exists
    handoffs_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    topic_slug = initiative_name.lower().replace(" ", "-")
    filename = f"{date_str}-to-{to_agent}-{topic_slug}.md"

    handoff_path = handoffs_dir / filename

    # Create handoff content
    content = f"""---
to: {to_agent}
from: {from_agent}
initiative_id: {initiative_id}
initiative_name: "{initiative_name}"
prd_path: "{prd_path}"
created: {datetime.now().isoformat()}
status: pending
---

# Handoff: {initiative_name}

## Context
{context}

## Next Steps for {to_agent.replace('-', ' ').title()}
{next_steps}
"""

    # Write file
    handoff_path.write_text(content)

    return {
        "status": "success",
        "handoff_path": str(handoff_path.relative_to(repo_path)),
        "absolute_path": str(handoff_path)
    }
```

**Pros**: Validates location, auto-creates directory, consistent format
**Cons**: 1 hour effort, need to add MCP tool
**Validation**: Same as Option A

**Recommendation**:
1. **Immediate**: Option B (create full directory structure - 45 min) - **Fixes Issue #6 + #9**
2. **Short-term**: Option C (add create_handoff tool - 1 hour) - **Robust solution**
3. **Skip**: Option A (only fixes handoffs, doesn't solve root cause)

**Why Option B is Best**:
- **Fixes two issues**: Issue #6 (missing folders) + Issue #9 (handoff location)
- **45 min effort**: Reasonable for complete infrastructure setup
- **Unblocks Phase 1 + Phase 7**: Both now functional
- **One-time setup**: Won't need to repeat

**Status**: ⏳ Pending - Blocked by Issue #6 (missing docs/ directory)

**Test Results** (from Claude Chat session):
- Test 7.1: ❌ FAILED (handoff created in wrong location, docs/ doesn't exist)
- Test 7.2: ❌ CANNOT TEST (no handoff file in correct location)
- Test 7.3: ❌ CANNOT TEST (no handoff to accept)
- Test 7.4: ❌ CANNOT TEST (no handoff to reject)
- Test 7.5: ❌ CANNOT TEST (can't create multiple handoffs)

**Phase 7 Status**: **0% functional - blocked by missing folder structure (Issue #6)**

**Pattern Observed**:
- **Issue #2**: RAG code built, never indexed (0% functional)
- **Issue #6**: Archival code built, folders never created (25% functional)
- **Issue #8**: Schema detection built, never integrated (0% functional)
- **Issue #9**: Handoff code exists, wrong directory + missing infrastructure (0% functional)

**Common Theme**: Code/logic built, but infrastructure setup and integration never completed.

---

## 📊 Testing Progress

### Phase 0: Tool Selection Priority Fix
- [ ] Test 0.1: RAG tools used for document discovery (❌ FAILED - Issue #1)
- [ ] Test 0.2: Find Legacy AI meta-analysis (❌ FAILED - Issue #2)
- [ ] Test 0.3: Find PRDs about context engineering (❌ FAILED - Issue #3)
- [x] Test 0.4: Update Strategy Board initiative status (✅ PASSED)
- [ ] Test 0.5: Read exact path (ROADMAP.md)

### Phase 1: Package Structure + Archival
- [ ] Test 1.1: Search finds files in both active and archive (❌ FAILED - Issue #4)
- [x] Test 1.2: Orphaned folders cleaned up (✅ PASSED - but Issue #5: took 9 attempts, need list_files tool)
- [ ] Test 1.3: Active/archive structure operational (❌ FAILED - Issue #6: no docs/ directory exists at all!)
- [ ] Test 1.4: Backup system creates backups before overwrite
- [ ] Test 1.5: Archive system moves files to archive/YYYY/QQ/
- [ ] Test 1.6: All imports successful
- [ ] Test 1.7: No regressions in existing workflows

### Phase 2: High-Signal Session Template ✅ ALL TESTS PASSED
- [x] Test 2.1: end_session with existing initiative (Legacy AI) (✅ PASSED - High-signal session created)
- [x] Test 2.2: end_session with existing initiative (Epic 2nd Brain) (✅ PASSED - Notion entry populated)
- [x] Test 2.3: Initiative detection - initiative exists (✅ PASSED - Auto-links without prompting)
- [x] Test 2.4: Initiative detection - initiative doesn't exist (✅ PASSED - Prompts with Create/Search/Proceed options)
- [x] Test 2.5: Ad-hoc session without initiative (✅ PASSED - Proceeds gracefully, no errors)
- [x] Test 2.6: Template quality check (✅ PASSED - Has What Worked/What Didn't Work/Decisions/Next Steps, no meta-commentary)

### Phase 3: Auto-Update Roadmap ⚠️ PARTIALLY WORKING
- [ ] Test 3.1: Complete initiative end-to-end (❌ FAILED - ROADMAP.md updated ✓, but PRD NOT archived - Issue #7)
- [x] Test 3.2: Update initiative status mid-project (✅ PASSED - ROADMAP.md reflects new status)
- [x] Test 3.3: Roadmap sync accuracy (✅ PASSED - All 3 random initiatives matched between Strategy Board and ROADMAP.md)

### Phase 4: Usage Tracking + Learning ✅ ALL TESTS PASSED
- [x] Test 4.1: Usage tracking operational (✅ PASSED - logs/usage/ has JSON files, no sensitive data)
- [x] Test 4.2: Learning algorithm scoring (✅ PASSED - Suggested files relevant and accurate)
- [x] Test 4.3: Suggestion improvement over time (✅ PASSED - Session 1 vs Session 5 shows improvement)
- [x] Test 4.4: Context profile updates (✅ PASSED - docs/config/context-profiles.json updated after sessions)

### Phase 5: Auto-Detect Notion Schema ❌ ALL TESTS FAILED
- [ ] Test 5.1: Schema detection works for Strategy Board (❌ FAILED - Issue #8: detector never called, all properties hardcoded)
- [ ] Test 5.2: Schema detection works for Sessions DB (❌ FAILED - Issue #8: detector never called)
- [ ] Test 5.3: Works with renamed properties (❌ CANNOT TEST - Issue #8: fuzzy matching not used)
- [ ] Test 5.4: Fallback to defaults if detection fails (❌ CANNOT TEST - Issue #8: always hardcoded)

### Phase 6: Separate RAG Repos
- [ ] Test 6.1: Privacy isolation (no cross-project leakage)
- [ ] Test 6.2: Search accuracy (hybrid RAG working)
- [ ] Test 6.3: MCP tools working with error handling
- [ ] Test 6.4: Collections indexed correctly (❌ FAILED - Issue #2 - Never ran indexing script)

### Phase 7: File-Based Handoffs ❌ ALL TESTS FAILED
- [ ] Test 7.1: Create handoff in Claude Chat (❌ FAILED - Issue #9: wrong directory, docs/ doesn't exist)
- [ ] Test 7.2: Detect handoff in Claude Code (❌ CANNOT TEST - Issue #9: no handoff in correct location)
- [ ] Test 7.3: Accept handoff (❌ CANNOT TEST - Issue #9: no handoff to accept)
- [ ] Test 7.4: Reject handoff (❌ CANNOT TEST - Issue #9: no handoff to reject)
- [ ] Test 7.5: Multiple handoffs (❌ CANNOT TEST - Issue #9: can't create handoffs)

---

## 🚀 Implementation Plan

**After all testing issues documented**:

1. **Prioritize fixes** by impact (time saved + user frustration)
2. **Group by effort** (quick wins vs heavy lifting)
3. **Batch implement** to avoid context switching
4. **Validate each fix** with original test case
5. **Regression test** all other phases

**Implementation Waves**:
- Wave A: Quick wins (<30 min each)
- Wave B: Medium efforts (30-90 min each)
- Wave C: Heavy lifting (2+ hours each)

---

## 📝 Change Log

| Date | Update | Author |
|------|--------|--------|
| 2025-12-09 | Created testing issues doc with Issue #1 (RAG tool selection) | Claude Code |
| 2025-12-09 | Added Issue #2 (Phase 6 RAG never indexed - collections empty) | Claude Code |
| 2025-12-09 | Added Issue #3 (search_docs keyword matching too literal, needs semantic search) | Claude Code |
| 2025-12-09 | Added Issue #4 (archival system not integrated with search, Phase 1 ~50% complete) | Claude Code |
| 2025-12-09 | Added Issue #5 (no directory listing tool, can't browse structure - Test 1.2 passed but took 9 attempts) | Claude Code |
| 2025-12-09 | Added Issue #6 (active/archive directory structure never created, Phase 1 revised to ~25% complete) | Claude Code |
| 2025-12-15 | Added Issue #7 (PRD archival not triggered - prd_path extraction fails, discovered by user testing) | Claude Code |
| 2025-12-15 | Updated Phase 3 status: 100% → 67% (ROADMAP sync works, archival broken) | Claude Code |
| 2025-12-15 | Phase 4 fully validated: All 4 tests passed (usage tracking, learning algorithm, suggestion improvement) | Claude Code |
| 2025-12-15 | Phase 5 testing complete: 0/4 tests passed - Issue #8 (schema detector built but never integrated) | Claude Code |
| 2025-12-15 | Phase 7 testing complete: 0/5 tests passed - Issue #9 (handoff creation failed, blocked by Issue #6) | Claude Code |
| 2025-12-15 | Updated overall success rate: 64% → 45% (14/31 tests, added Phases 5-7) | Claude Code |
| 2025-12-15 | Identified pattern: 3 phases built but 0% functional (Issues #2, #8, #9 - code exists, not integrated) | Claude Code |

---

## 📊 Overall Testing Summary

**Tests Completed**: 31 tests across 8 phases (Phases 0-7)
- **Phase 0 (Tool Selection)**: 1/5 passed (20%)
- **Phase 1 (Archival)**: 1/7 passed (14%)
- **Phase 2 (Session Template)**: 6/6 passed (100%) ✅
- **Phase 3 (Auto-Update Roadmap)**: 2/3 passed (67%) ⚠️
- **Phase 4 (Usage Tracking + Learning)**: 4/4 passed (100%) ✅
- **Phase 5 (Schema Detection)**: 0/4 passed (0%) ❌
- **Phase 6 (RAG Separation)**: 0/4 passed (0%) ❌
- **Phase 7 (File Handoffs)**: 0/5 passed (0%) ❌

**Overall Success Rate**: 45% (14/31 tests passed) ⬇️

**Phases Fully Validated** (2/8 phases complete):
- ✅ **Phase 2: High-Signal Session Template** - 100% complete, delivering user value
- ✅ **Phase 4: Usage Tracking + Learning** - 100% complete, learning loop working

**Phases Partially Working**:
- ⚠️ **Phase 3: Auto-Update Roadmap** - 67% complete (ROADMAP.md sync works, PRD archival broken - Issue #7)
- ⚠️ **Phase 1**: 14% passing - Archival logic works, but folder structure missing for standalone tests (Issue #6)

**Phases Built but Not Functional** (0% working):
- ❌ **Phase 5: Schema Detection** - Code built, never integrated (Issue #8)
- ❌ **Phase 6: RAG Separation** - Code built, never indexed (Issue #2)
- ❌ **Phase 7: File Handoffs** - Blocked by missing folder structure (Issue #9)

**Phases Incomplete**:
- ❌ **Phase 0**: Tool selection hierarchy issues (RAG tools not prioritized - Issue #1)

**Important Finding from Phase 3** (Updated - Issue #7):
- **Previous claim was wrong**: Test 3.1 did NOT archive the PRD (user discovered this)
- archival.py code is correct (would auto-create folders with `mkdir(parents=True)`)
- BUT archival never runs because `prd_path=None` (extraction logic fails)
- Issue #6 (missing folder structure) is secondary - archival.py would create them IF it ran
- Issue #7 (prd_path extraction) is the primary blocker for Phase 3 archival

**Critical Blockers** (must fix before continuing):
1. **Issue #6** (45 min) - Create full folder structure → Unblocks Phase 1, Phase 7, Issue #9
2. **Issue #2** (5-10 min) - Index RAG collections → Unblocks Phase 6 + Issues #3, #4
3. **Issue #7** (30 min) - Fix PRD path extraction logic → Unblocks Phase 3 archival
4. **Issue #5** (30 min) - Add list_files() tool → Unblocks all folder verification tests
5. **Issue #8** (2 hours) - Integrate schema detection → Completes Phase 5
6. **Issue #9** (included in Issue #6) - Handoff directory creation

**Total Fix Time for All Blockers**: ~3.5-4 hours

**Quick Wins (High Impact, Low Effort)**:
1. Issue #6 (45 min) - **HIGHEST PRIORITY** - Unblocks Phase 1 + Phase 7
2. Issue #2 (10 min) - Enables all RAG/semantic search functionality
3. Issue #5 (30 min) - Enables folder exploration/validation

**Documented Issues**: 9
**Resolved Issues**: 0
**Validated Wins**: 2 (Phase 2 + Phase 4 fully validated)

---

**Status**: 🔄 Active Testing - Collecting Issues
**Next Step**: Continue testing Phases 3-6, or batch implement fixes for Issues #2, #5, #6
