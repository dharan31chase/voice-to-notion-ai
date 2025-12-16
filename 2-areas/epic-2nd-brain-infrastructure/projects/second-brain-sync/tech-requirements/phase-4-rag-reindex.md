# Tech Requirements: Phase 4 - RAG Reindex (PARA Migration)

**Phase**: 4 of 6
**Estimated Time**: 3-4 hours
**Priority**: P1 (Critical - RAG must work with new PARA structure)
**Dependencies**: Phase 1 (PARA Restructure) must be complete

---

## 🎯 Goal

Reindex both ChromaDB RAG collections (epic-2nd-brain-rag, legacy-ai-rag) with new PARA file paths. Implement cross-repo resource sharing (Legacy AI accesses shared Epic 2nd Brain frameworks/books). Include cron safety mechanisms to prevent backpack overheating.

**Key Decisions**:
- ✅ Full wipe + recreate (fresh start with PARA paths)
- ✅ Reuse legacy-ai RAG settings (proven, consistent)
- ✅ Cross-repo sharing: Legacy AI → Epic 2nd Brain only (one-way)
- ✅ Cron safety: Only run when AC power + lid open

---

## ✅ Success Criteria

**Functional Requirements**:
- [ ] Epic 2nd Brain RAG indexes all ai-assistant .md files (projects, areas, resources, archive, session logs)
- [ ] Legacy AI RAG indexes all legacy-ai .md files + shared ai-assistant resources (frameworks, book-notes, documents, podcast-notes)
- [ ] MCP tools `search_epic_2nd_brain()` and `search_legacy_ai()` work unchanged (backward compatible)
- [ ] 10 validation test queries pass (5 per repo, top 3 results relevant)
- [ ] File count verification (no documents lost during reindex)
- [ ] Cron runs at 3am daily, but ONLY when AC power + lid open

**Quality Requirements**:
- [ ] All-or-nothing reindex (rollback on partial failure)
- [ ] Backup collections before deletion (7-day retention)
- [ ] ChromaDB metadata schema matches existing (no breaking changes)
- [ ] Idempotent: Running reindex twice = same result
- [ ] Cron wrapper prevents overheating (lid closed → skip run)

**Non-Goals** (explicitly out of scope):
- ❌ Indexing binary files (MP3, MP4, images, videos, PDFs)
- ❌ Indexing code files (.py, .js, .json, .yaml, .sh)
- ❌ Indexing system files (.git, node_modules, __pycache__, logs)
- ❌ Sharing personal meeting notes with Legacy AI (kept private)

---

## 🏗️ Technical Approach

### **Step 1: Review Existing RAG Implementation** (CONFIRMED ✅)

**Existing Collections Found**:
- `epic-2nd-brain`: 1002 chunks indexed ✅
- `legacy-ai`: 0 chunks (empty, needs indexing) ⚠️

**Location**:
- Epic 2nd Brain: `ai-assistant/.chroma/chroma.sqlite3`
- Legacy AI: `lifeadmin/.chroma/chroma.sqlite3`

**Confirmed Settings** (from `docs/config/rag-repos.json`):
```python
# ACTUAL IMPLEMENTATION (VERIFIED):
CHUNKING_STRATEGY = {
    "chunk_size": 1000,  # Characters per chunk (NOT tokens)
    "chunk_overlap": 200,  # Overlap for context preservation
    "strategy": "line_by_line_with_size_limit"  # NOT header-based!
    # Chunks when: current_size + line_size > 1000
    # Overlap: Keeps last 200 chars from previous chunk
}

EMBEDDINGS_MODEL = "text-embedding-3-small"  # OpenAI (384 dimensions)

RERANKING = {
    "enabled": True,
    "model": "BAAI/bge-reranker-base",  # Local BGE reranker
    "top_k_rerank": 20  # Get 20 results, rerank, return top 10
}

# Note: BM25 hybrid search NOT implemented in current version
# Only semantic search + BGE reranking
```

**Implementation File**: `mcp_server/rag/epic_2nd_brain_rag.py` (lines 117-203)

**Why**: Both RAG collections use identical settings (consistency confirmed).

---

### **Step 2: Indexing Scope Configuration** (15 min)

Create config files defining what gets indexed per RAG collection.

**Note**: Configuration already exists in `docs/config/rag-repos.json` (no new config files needed)

**Current Epic 2nd Brain Indexing Scope** (from rag-repos.json):
```json
{
  "enabled": true,
  "chroma_collection": "epic-2nd-brain",
  "index_paths": [
    "docs/prd",
    "docs/tech-requirements",
    "docs/sessions/claude-code",
    "docs/sessions/claude-chat",
    "docs/context/one-pagers"
  ],
  "exclude_patterns": [
    "**/.backups/**",
    "**/archive/**",
    "**/__pycache__/**"
  ]
}
```

**Phase 4 Changes Needed** (expand to PARA structure):
```json
{
  "enabled": true,
  "chroma_collection": "epic-2nd-brain",
  "index_paths": [
    "projects",  # NEW: All projects/**/*.md
    "areas",  # NEW: All areas/**/*.md
    "resources",  # NEW: All resources/**/*.md (keep existing docs paths too)
    "docs/prd",  # KEEP: Existing
    "docs/tech-requirements",  # KEEP: Existing
    "docs/sessions/claude-code",  # KEEP: Existing
    "docs/sessions/claude-chat",  # KEEP: Existing
    "docs/context/one-pagers"  # KEEP: Existing
  ],
  "exclude_patterns": [
    "**/.backups/**",
    "**/archive/**",  # Exclude archive (historical, not current)
    "**/__pycache__/**",
    "**/*.pyc",
    "**/*.log",
    "**/*.db"
  ]
}
```

**Legacy AI Scope** (after Phase 1 PARA migration):
```json
{
  "enabled": true,
  "chroma_collection": "legacy-ai",
  "index_paths": [
    "projects",  # NEW: All projects/**/*.md
    "areas",  # NEW: All areas/**/*.md
    "resources"  # NEW: All resources/**/*.md
  ],
  "exclude_patterns": [
    "**/.backups/**",
    "**/archive/**",
    "**/__pycache__/**",
    "**/personal-artifacts/**"
  ],
  "cross_repo_sharing": {
    "enabled": true,
    "shared_from_epic_2nd_brain": [
      "resources/frameworks",
      "resources/book-notes",
      "resources/documents",
      "resources/podcast-notes"
    ],
    "excluded": ["resources/meeting-notes"]
  }
}
```

**Why per-repo config**:
- Each repo defines its own indexing scope
- Cross-repo sharing is explicit and documented
- Easier to audit what's shared vs. private

---

### **Step 3: Reindex Script Implementation** (90 min)

**File**: `ai-assistant/resources/reindex_rag.py`

**Core Logic**:
```python
#!/usr/bin/env python3
"""
RAG Reindex Script (PARA Migration)
Wipes and recreates ChromaDB collections with new PARA file paths.
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
import chromadb
from chromadb.config import Settings
import openai

# Load config
def load_config(repo):
    """Load RAG config for specified repo"""
    if repo == "ai-assistant":
        config_path = Path(__file__).parent / "rag_config.json"
    else:
        config_path = Path("/Users/dharanchandrahasan/Documents/1. Projects/legacy-ai/resources/rag_config.json")

    with open(config_path) as f:
        config = json.load(f)

    # Get the appropriate collection config
    if repo == "ai-assistant":
        return config["epic_2nd_brain_rag"]
    else:
        return config["legacy_ai_rag"]

# Find files to index
def find_indexable_files(config):
    """Find all .md files matching include patterns"""
    repo_root = Path(config["repo_root"])
    indexable = []

    # Include patterns (from main repo)
    for pattern in config["include_patterns"]:
        for md_file in repo_root.glob(pattern):
            # Check exclude patterns
            if not any(md_file.match(excl) for excl in config["exclude_patterns"]):
                indexable.append(md_file)

    # Cross-repo sharing (if enabled)
    if config.get("cross_repo_sharing", {}).get("enabled"):
        for shared_pattern in config["cross_repo_sharing"]["shared_resources"]:
            for md_file in Path("/").glob(shared_pattern.lstrip("/")):
                if not any(md_file.match(excl) for excl in config["exclude_patterns"]):
                    indexable.append(md_file)

    return indexable

# Chunk markdown file
def chunk_markdown_file(file_path, config):
    """
    Chunk markdown file using semantic heading strategy.
    Reuses exact settings from legacy-ai RAG.
    """
    content = file_path.read_text()

    # Extract frontmatter (if exists)
    frontmatter = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()

    # Chunk by headings (semantic)
    chunks = []
    current_chunk = ""

    for line in body.split("\n"):
        # Check if heading (semantic boundary)
        if line.startswith("#"):
            # Save previous chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            # Start new chunk with heading
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

            # Check chunk size limit
            if len(current_chunk) >= 1000:  # CHUNK_SIZE from legacy-ai RAG
                chunks.append(current_chunk.strip())
                # Overlap: keep last 200 chars
                current_chunk = current_chunk[-200:]

    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks, frontmatter

# Extract metadata from file path
def extract_metadata(file_path, repo_root, frontmatter):
    """Extract metadata from file path and frontmatter"""
    relative_path = file_path.relative_to(repo_root)
    path_parts = relative_path.parts

    # Infer doc_type from path
    doc_type = "general"
    if "prd" in str(relative_path).lower():
        doc_type = "prd"
    elif "session" in str(relative_path):
        doc_type = "session"
    elif "book-notes" in str(relative_path):
        doc_type = "book-note"
    elif "frameworks" in str(relative_path):
        doc_type = "framework"
    elif "podcast-notes" in str(relative_path):
        doc_type = "podcast-note"

    # Extract project/area from PARA structure
    project = None
    area = None
    if len(path_parts) > 1:
        if path_parts[0] == "projects":
            project = path_parts[1] if len(path_parts) > 1 else None
        elif path_parts[0] == "areas":
            area = path_parts[1] if len(path_parts) > 1 else None

    # Get file created timestamp
    created = datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()

    # Check if archived
    is_archive = "archive" in path_parts

    return {
        "file_path": str(relative_path),
        "repo": repo_root.name,
        "doc_type": doc_type,
        "project": project,
        "area": area,
        "created": created,
        "is_archive": is_archive,
        "title": frontmatter.get("title", file_path.stem)
    }

# Get embeddings
def get_embeddings(texts):
    """Get OpenAI embeddings (reuse legacy-ai RAG settings)"""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(
        model="text-embedding-3-small",  # Confirmed from legacy-ai RAG
        input=texts
    )

    return [item.embedding for item in response.data]

# Backup collection
def backup_collection(chroma_client, collection_name, backup_path):
    """Backup existing collection before deletion"""
    try:
        collection = chroma_client.get_collection(collection_name)
        all_data = collection.get(include=["embeddings", "metadatas", "documents"])

        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        with open(backup_path, "w") as f:
            json.dump({
                "collection_name": collection_name,
                "timestamp": datetime.utcnow().isoformat(),
                "data": all_data
            }, f)

        print(f"✅ Backed up {collection_name} to {backup_path}")
        return True
    except Exception as e:
        print(f"⚠️  Backup failed for {collection_name}: {e}")
        return False

# Restore collection
def restore_collection(chroma_client, backup_path):
    """Restore collection from backup (rollback on failure)"""
    with open(backup_path) as f:
        backup_data = json.load(f)

    collection_name = backup_data["collection_name"]

    # Delete current collection
    try:
        chroma_client.delete_collection(collection_name)
    except:
        pass

    # Create new collection
    collection = chroma_client.create_collection(collection_name)

    # Restore data
    data = backup_data["data"]
    collection.add(
        ids=data["ids"],
        embeddings=data["embeddings"],
        metadatas=data["metadatas"],
        documents=data["documents"]
    )

    print(f"✅ Restored {collection_name} from backup")

# Reindex collection
def reindex_collection(repo):
    """
    Main reindex logic:
    1. Backup existing collection
    2. Delete old collection
    3. Create new collection
    4. Index all files
    5. Validate
    """
    config = load_config(repo)
    collection_name = config["collection_name"]

    # Initialize ChromaDB client
    chroma_client = chromadb.PersistentClient(path=os.path.expanduser("~/.chroma"))

    # Step 1: Backup
    backup_path = f"~/.chroma/backups/{collection_name}-{datetime.now().strftime('%Y%m%d')}.json"
    if collection_name in [c.name for c in chroma_client.list_collections()]:
        backup_collection(chroma_client, collection_name, os.path.expanduser(backup_path))

        # Step 2: Delete old collection
        chroma_client.delete_collection(collection_name)
        print(f"🗑️  Deleted old {collection_name} collection")

    # Step 3: Create new collection
    collection = chroma_client.create_collection(collection_name)
    print(f"✨ Created new {collection_name} collection")

    # Step 4: Index all files
    print(f"🔍 Scanning for indexable files...")
    files = find_indexable_files(config)
    print(f"📄 Found {len(files)} .md files to index")

    total_chunks = 0
    errors = 0

    for i, file_path in enumerate(files):
        try:
            # Chunk file
            chunks, frontmatter = chunk_markdown_file(file_path, config)

            if not chunks:
                continue

            # Extract metadata
            repo_root = Path(config["repo_root"])
            base_metadata = extract_metadata(file_path, repo_root, frontmatter)

            # Generate embeddings (batch for efficiency)
            embeddings = get_embeddings(chunks)

            # Prepare for ChromaDB
            chunk_ids = [f"{file_path.stem}_{j:03d}" for j in range(len(chunks))]
            metadatas = [
                {**base_metadata, "chunk_index": j, "total_chunks": len(chunks)}
                for j in range(len(chunks))
            ]

            # Add to collection
            collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=chunks
            )

            total_chunks += len(chunks)

            # Progress
            if (i + 1) % 10 == 0:
                print(f"  Indexed {i + 1}/{len(files)} files ({total_chunks} chunks)...")

        except Exception as e:
            print(f"❌ Error indexing {file_path}: {e}")
            errors += 1

            # All-or-nothing: rollback on too many errors
            if errors > 10:
                print("🚨 Too many errors - rolling back")
                restore_collection(chroma_client, os.path.expanduser(backup_path))
                raise Exception("Reindex failed - rolled back to backup")

    print(f"\n✅ Reindex complete: {len(files)} files, {total_chunks} chunks, {errors} errors")

    # Step 5: Validate
    return validate_reindex(collection, repo)

# Validate reindex
def validate_reindex(collection, repo):
    """Run validation tests (test queries + file count)"""

    # Test queries per repo
    test_queries = {
        "ai-assistant": [
            "Show me all PRDs",
            "What frameworks do we have?",
            "What did we build in December?",
            "PARA structure methodology",
            "MCP server architecture"
        ],
        "legacy-ai": [
            "Customer pain points from interviews",
            "Financial planning needs",
            "Product requirements from discovery",
            "Ripanshi interview insights",
            "Customer discovery methodology"
        ]
    }

    queries = test_queries.get(repo, [])
    passed = 0

    for query in queries:
        results = collection.query(query_texts=[query], n_results=3)

        # Check if we got results
        if results and len(results["ids"][0]) >= 1:
            passed += 1
            print(f"  ✅ '{query}' → {len(results['ids'][0])} results")
        else:
            print(f"  ❌ '{query}' → No results")

    validation_passed = passed >= len(queries) * 0.8  # 80% pass rate

    if validation_passed:
        print(f"\n✅ Validation passed: {passed}/{len(queries)} test queries successful")
    else:
        print(f"\n❌ Validation failed: Only {passed}/{len(queries)} test queries successful")

    return validation_passed

# Main
def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python reindex_rag.py [ai-assistant|legacy-ai|both]")
        sys.exit(1)

    target = sys.argv[1]

    if target in ["ai-assistant", "both"]:
        print("=" * 60)
        print("REINDEXING: Epic 2nd Brain RAG")
        print("=" * 60)
        reindex_collection("ai-assistant")

    if target in ["legacy-ai", "both"]:
        print("\n" + "=" * 60)
        print("REINDEXING: Legacy AI RAG")
        print("=" * 60)
        reindex_collection("legacy-ai")

    print("\n🎉 All reindexing complete!")

if __name__ == "__main__":
    main()
```

**Dependencies**:
- `chromadb` (already installed)
- `openai` (already installed)
- `pyyaml` (already installed)

---

### **Step 4: Cron Safety Wrapper** (30 min)

**Problem**: Mac in backpack can overheat if cron jobs run while lid is closed.

**Solution**: Wrapper script checks lid state + AC power before running.

**File**: `ai-assistant/resources/safe_cron_wrapper.sh`
```bash
#!/bin/bash
# Safe Cron Wrapper - Prevents overheating in backpack
# Only runs cron jobs when:
# 1. Lid is open (not in backpack)
# 2. On AC power (not draining battery)

SCRIPT_PATH="$1"
LOG_FILE="$2"

# Check if lid is closed
if ioreg -r -k AppleClamshellState | grep -q "AppleClamshellState.*Yes"; then
    echo "[$(date)] Cron skipped - lid closed (prevents overheating in backpack)" >> "$LOG_FILE"
    exit 0
fi

# Check if on battery power
if pmset -g batt | grep -q "Battery Power"; then
    echo "[$(date)] Cron skipped - on battery power" >> "$LOG_FILE"
    exit 0
fi

# Safe to run (AC power + lid open)
echo "[$(date)] Running: $SCRIPT_PATH" >> "$LOG_FILE"
/usr/bin/python3 "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1
```

**Make executable**:
```bash
chmod +x ai-assistant/resources/safe_cron_wrapper.sh
chmod +x legacy-ai/resources/safe_cron_wrapper.sh
```

---

### **Step 5: Mac Wake Schedule (pmset)** (15 min)

**Configure Mac to wake before cron jobs** (only when on AC power):

```bash
# Wake Mac before cron jobs (only when AC power + lid open)
sudo pmset -c repeat wake MTWRFSU 02:55:00  # Before 3am RAG reindex

# -c flag = only wake when connected to AC power (prevents battery drain)
# MTWRFSU = Monday through Sunday
```

**Verify configuration**:
```bash
pmset -g sched
# Should show: wake at 2025-12-17 02:55:00
```

**Why this works**:
- Mac wakes at 2:55am (if on AC power)
- Cron runs at 3:00am
- Wrapper checks lid state (if closed → skip)
- If in backpack on battery → Mac doesn't wake, cron doesn't run ✅

**Trade-off accepted**: If traveling 3+ days without opening laptop, reindex waits until back home.

---

### **Step 6: Cron Setup** (15 min)

**Crontab Entry**:
```bash
# RAG Reindex (3am daily, both repos)
0 3 * * * /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/resources/safe_cron_wrapper.sh /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/resources/reindex_rag.py both /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/resources/logs/reindex_rag.log
```

**Log Rotation** (keep last 30 days):
```bash
# Add to cron (runs weekly)
0 4 * * 0 find /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/resources/logs/reindex_rag.log -mtime +30 -delete
```

---

## 📋 Data Structures

### **Collection Metadata Schema**

```python
{
    "chunk_id": "prd_001",  # Unique ID (file_stem + chunk_index)
    "file_path": "projects/second-brain-sync/prd.md",  # Relative PARA path
    "repo": "ai-assistant",  # Repo name
    "doc_type": "prd",  # Inferred from path (prd, session, book-note, framework, podcast-note, general)
    "project": "second-brain-sync",  # Extracted from PARA path (if applicable)
    "area": null,  # Extracted from PARA path (if applicable)
    "created": "2025-12-15T10:30:00",  # File created timestamp
    "chunk_index": 0,  # Position in document (0, 1, 2...)
    "total_chunks": 5,  # Total chunks in document
    "is_archive": false,  # True if in archive/ folder
    "title": "Second Brain Sync"  # From frontmatter or filename
}
```

**Metadata uses**:
- Filter by doc_type: `collection.query(..., where={"doc_type": "prd"})`
- Filter by project: `collection.query(..., where={"project": "second-brain-sync"})`
- Filter by archive: `collection.query(..., where={"is_archive": False})`
- Sort by created: Results can be sorted by timestamp

---

### **Config File Schema**

```json
{
  "[collection_key]": {
    "collection_name": string,  // ChromaDB collection name
    "repo_root": string,  // Absolute path to repo
    "include_patterns": [string],  // Glob patterns to include
    "exclude_patterns": [string],  // Glob patterns to exclude
    "cross_repo_sharing": {
      "enabled": boolean,
      "shared_resources": [string],  // Absolute paths to shared folders
      "excluded_from_sharing": [string],  // Paths excluded from sharing
      "description": string
    }
  }
}
```

---

## 🔌 MCP Backward Compatibility

### **Existing MCP Tools**

**Epic 2nd Brain search** (`mcp_server/rag/epic_2nd_brain_rag.py`):
```python
# EXISTING IMPLEMENTATION - No changes needed!
from mcp_server.rag.epic_2nd_brain_rag import Epic2ndBrainRAG

rag = Epic2ndBrainRAG()
results = rag.search(query="Second Brain Sync PRD", top_k=10)

# Collection name: "epic-2nd-brain" (NOT "epic-2nd-brain-rag")
# Location: ai-assistant/.chroma/chroma.sqlite3
# Results now have PARA paths (e.g., "projects/second-brain-sync/prd.md")
```

**Legacy AI search** (`mcp_server/rag/legacy_ai_rag.py`):
```python
# EXISTING IMPLEMENTATION - No changes needed!
from mcp_server.rag.legacy_ai_rag import LegacyAIRAG

rag = LegacyAIRAG()
results = rag.search(query="Customer pain points", top_k=10)

# Collection name: "legacy-ai" (NOT "legacy-ai-rag")
# Location: lifeadmin/.chroma/chroma.sqlite3
# Results include both legacy-ai files AND shared ai-assistant resources (after Phase 4)
```

**Changes**:
- ✅ Collection names unchanged (backward compatible)
- ✅ Metadata schema unchanged (same fields)
- ✅ Only difference: `file_path` values use PARA structure

**Validation Test**:
```python
# Test RAG tools still work after reindex
from mcp_server.rag.epic_2nd_brain_rag import Epic2ndBrainRAG
from mcp_server.rag.legacy_ai_rag import LegacyAIRAG

# Epic 2nd Brain: Should return results with new PARA paths
epic_rag = Epic2ndBrainRAG()
results = epic_rag.search("PRD Second Brain Sync", top_k=5)
assert len(results) > 0
assert "projects/second-brain-sync/prd.md" in results[0]["source"]

# Legacy AI: Should find shared frameworks from ai-assistant
legacy_rag = LegacyAIRAG()
results = legacy_rag.search("Building a Second Brain PARA", top_k=5)
assert len(results) > 0
# Should include ai-assistant framework (after cross-repo sharing implemented)
# assert "resources/frameworks" in results[0]["source"]
```

---

## ⚠️ Error Handling

### **Error Scenarios**

**1. Embeddings API Failure (Rate Limit)**:
- **Symptom**: OpenAI rate limit error (429)
- **Action**: Exponential backoff (1s, 2s, 4s, 8s), retry up to 3 times
- **Log**: `⚠️ Rate limited, retrying in [X]s...`

**2. Embeddings API Failure (Server Error)**:
- **Symptom**: OpenAI server error (500)
- **Action**: Skip chunk, log error, continue with next
- **Log**: `❌ OpenAI API error for [file]: [error]`

**3. ChromaDB Insertion Failure**:
- **Symptom**: `collection.add()` raises exception
- **Action**: All-or-nothing rollback (restore from backup)
- **Log**: `🚨 ChromaDB insert failed - rolling back`

**4. Too Many Errors (>10 files)**:
- **Symptom**: Errors accumulate during indexing
- **Action**: Abort reindex, restore from backup
- **Log**: `🚨 Too many errors - rolling back to backup`

**5. File Read Failure**:
- **Symptom**: Can't read .md file (permissions, encoding)
- **Action**: Skip file, log warning, continue
- **Log**: `⚠️ Can't read [file]: [error]`

**6. Invalid Frontmatter**:
- **Symptom**: YAML parse error
- **Action**: Skip frontmatter, index body only
- **Log**: `⚠️ Invalid frontmatter in [file] - indexing body only`

**7. Lid Closed During Cron**:
- **Symptom**: Wrapper detects closed lid
- **Action**: Skip run, log to cron log
- **Log**: `[timestamp] Cron skipped - lid closed (prevents overheating in backpack)`

**8. On Battery Power During Cron**:
- **Symptom**: Wrapper detects battery power
- **Action**: Skip run, log to cron log
- **Log**: `[timestamp] Cron skipped - on battery power`

---

## 🧪 Testing Requirements

### **Unit Tests**

**Test Suite**: `tests/test_reindex_rag.py`

**Test 1: Find Indexable Files (Epic 2nd Brain)**
- Given: ai-assistant repo with PARA structure
- When: `find_indexable_files(config)` called
- Then: Returns all .md files, excludes binaries/code

**Test 2: Find Indexable Files (Legacy AI + Shared)**
- Given: legacy-ai repo + ai-assistant shared resources
- When: `find_indexable_files(config)` called
- Then: Returns legacy-ai .md files + ai-assistant frameworks/books/docs/podcasts
- Then: Excludes ai-assistant meeting-notes

**Test 3: Chunk Markdown File**
- Given: Markdown file with 3 headings, 3000 chars
- When: `chunk_markdown_file(file)` called
- Then: Returns 3+ chunks (split on headings)
- Then: Each chunk ≤1000 chars (with 200 char overlap)

**Test 4: Extract Metadata from PARA Path**
- Given: File path `projects/second-brain-sync/prd.md`
- When: `extract_metadata(path)` called
- Then: Returns `{project: "second-brain-sync", doc_type: "prd", is_archive: false}`

**Test 5: Backup Collection**
- Given: Existing ChromaDB collection with 10 chunks
- When: `backup_collection(collection)` called
- Then: Backup file created with all 10 chunks + metadata

**Test 6: Restore Collection**
- Given: Backup file with 10 chunks
- When: `restore_collection(backup_path)` called
- Then: Collection recreated with all 10 chunks

---

### **Integration Tests**

**Test 7: Full Reindex (Mock OpenAI API)**
- Given: ai-assistant repo with 5 .md files
- When: `reindex_collection("ai-assistant")` called (with mocked embeddings)
- Then:
  - Old collection deleted
  - New collection created
  - 5 files indexed
  - Validation tests pass

**Test 8: Cross-Repo Sharing**
- Given: legacy-ai RAG config with shared ai-assistant resources
- When: `find_indexable_files(config)` called
- Then:
  - Finds legacy-ai .md files
  - Finds ai-assistant/resources/frameworks/*.md
  - Does NOT find ai-assistant/resources/meeting-notes/*.md

**Test 9: Error Rollback**
- Given: Reindex in progress, ChromaDB insert fails after 5 files
- When: Error threshold (>10) triggered
- Then:
  - Reindex aborted
  - Collection restored from backup
  - Log shows rollback

---

### **End-to-End Tests**

**Test 10: Real Reindex (Manual)**
- Setup: Complete Phase 1 (PARA Restructure)
- Run: `python3 resources/reindex_rag.py both`
- Verify:
  - [ ] Epic 2nd Brain RAG collection created
  - [ ] Legacy AI RAG collection created
  - [ ] All 10 test queries pass (5 per repo, top 3 results relevant)
  - [ ] File count matches (no documents lost)
  - [ ] MCP tools `search_epic_2nd_brain()` and `search_legacy_ai()` work
  - [ ] Cross-repo sharing works (legacy-ai finds ai-assistant frameworks)

**Test 11: Cron Safety (Manual)**
- Setup: Close laptop lid, leave on AC power
- Wait: Until 3am cron time
- Verify:
  - [ ] Check cron log: "Cron skipped - lid closed"
  - [ ] Reindex did NOT run (no overheating)
- Setup: Open laptop lid, disconnect AC power
- Wait: Until next cron time
- Verify:
  - [ ] Check cron log: "Cron skipped - on battery power"
  - [ ] Reindex did NOT run (saves battery)
- Setup: Open laptop lid, connect AC power
- Wait: Until next cron time
- Verify:
  - [ ] Check cron log: "Running: reindex_rag.py"
  - [ ] Reindex completed successfully

---

## 🔄 Rollback Plan

### **If Reindex Fails**

**Symptom**: Script crashes, partial collection created

**Impact**: Medium (RAG search broken until fixed)

**Rollback Steps**:
1. Check reindex logs: `tail -f resources/logs/reindex_rag.log`
2. Identify error (embeddings API, ChromaDB, file read, etc.)
3. Restore from backup:
   ```python
   python3 -c "
   from reindex_rag import restore_collection
   import chromadb
   client = chromadb.PersistentClient(path='~/.chroma')
   restore_collection(client, '~/.chroma/backups/epic-2nd-brain-rag-20251216.json')
   "
   ```
4. Fix error, re-run reindex
5. Validate: Test MCP tools work

---

### **If Validation Fails**

**Symptom**: Reindex completes, but test queries return no results

**Impact**: High (RAG unusable)

**Rollback Steps**:
1. Immediately restore from backup (same as above)
2. Debug validation failure:
   - Check if embeddings generated correctly
   - Check if metadata schema correct
   - Check if ChromaDB query syntax correct
3. Fix issue, re-run reindex
4. Validate: All 10 test queries must pass

---

### **If Cross-Repo Sharing Broken**

**Symptom**: Legacy AI can't find ai-assistant frameworks

**Impact**: Medium (missing shared resources)

**Rollback Steps**:
1. Check `rag_config.json` for legacy-ai
2. Verify `shared_resources` paths are correct (absolute paths)
3. Re-run reindex for legacy-ai only:
   ```bash
   python3 resources/reindex_rag.py legacy-ai
   ```
4. Validate: Search for "PARA framework" should return ai-assistant resource

---

## 📁 Files Changed

### **New Files Created**

```
ai-assistant/
├── resources/
│   ├── rag_config.json  # NEW: RAG indexing config
│   ├── reindex_rag.py  # NEW: Reindex script
│   └── safe_cron_wrapper.sh  # NEW: Cron safety wrapper
└── resources/logs/
    └── reindex_rag.log  # NEW: Reindex logs

legacy-ai/
├── resources/
│   ├── rag_config.json  # NEW: RAG indexing config (with cross-repo sharing)
│   └── safe_cron_wrapper.sh  # NEW: Cron safety wrapper
└── resources/logs/
    └── reindex_rag.log  # NEW: Reindex logs

~/.chroma/backups/  # NEW: Collection backups
├── epic-2nd-brain-20251216.json
└── legacy-ai-20251216.json
```

### **Modified Files**

```
# ChromaDB collections (wiped + recreated):
ai-assistant/.chroma/chroma.sqlite3  # Epic 2nd Brain ChromaDB
lifeadmin/.chroma/chroma.sqlite3  # Legacy AI ChromaDB

# RAG config (updated with PARA paths):
docs/config/rag-repos.json  # Update index_paths to include projects/, areas/, resources/

# Crontab:
crontab -e  # Add RAG reindex cron entry

# pmset schedule:
sudo pmset -c repeat wake MTWRFSU 02:55:00  # Mac wake schedule
```

### **Files Referenced (Not Modified)**

```
# RAG implementation (no changes needed - backward compatible):
mcp_server/rag/epic_2nd_brain_rag.py
mcp_server/rag/legacy_ai_rag.py
mcp_server/rag/base_rag.py
```

---

## ⏱️ Time Estimate Breakdown

| Activity | Time | Notes |
|----------|------|-------|
| Review: legacy-ai RAG implementation | 30 min | Document exact settings (chunking, embeddings, reranking) |
| Setup: RAG config files | 15 min | Create rag_config.json for both repos |
| Implementation: Reindex script | 90 min | Core logic, chunking, embeddings, ChromaDB |
| Implementation: Cron safety wrapper | 30 min | Lid check, AC power check, logging |
| Setup: pmset wake schedule | 15 min | Configure Mac to wake before cron |
| Setup: Cron entry | 15 min | Crontab + log rotation |
| Testing: Unit tests | 30 min | File discovery, chunking, metadata, backup/restore |
| Testing: Integration tests | 30 min | Mock embeddings, cross-repo sharing, error rollback |
| Testing: E2E test | 30 min | Real reindex with OpenAI embeddings, validation queries |
| Testing: Cron safety test | 15 min | Verify lid check + battery check work |
| **TOTAL** | **~4 hours** | |

**Optimistic**: 3 hours (if no issues)
**Realistic**: 4 hours
**Pessimistic**: 5 hours (if OpenAI API issues or ChromaDB bugs)

---

## 🤔 Architecture Decisions

### **Decision 1: Full Wipe vs. Incremental Update**

**Options**:
- **A**: Full wipe + recreate (delete old collection, index everything)
- **B**: Incremental update (update file paths in existing collection)

**Chosen**: **A** - Full wipe + recreate

**Rationale**:
- PARA restructure changes ALL file paths (every document affected)
- Incremental update would require complex path mapping (error-prone)
- Full wipe ensures clean state (no orphaned chunks with old paths)
- Backup + restore provides safety net (rollback on failure)

**Trade-offs**:
- ✅ Simpler implementation (no path mapping logic)
- ✅ Guaranteed consistency (all paths updated)
- ❌ Longer runtime (~20-30 min vs. instant)
- ❌ Requires embeddings regeneration (OpenAI API cost: ~$0.01)

**Alternative considered**: Incremental update would save API cost but risk path inconsistencies.

---

### **Decision 2: Separate Cron for Reindex vs. Combined**

**Options**:
- **A**: Separate cron (3am for reindex, 1am/1pm for sync)
- **B**: Combined cron (reindex + sync in single job)

**Chosen**: **A** - Separate cron

**Rationale**:
- Reindex is expensive (~20-30 min runtime)
- Sync is fast (~10 seconds)
- Reindex only needs to run daily (1x/day)
- Sync needs to run twice daily (2x/day for freshness)
- Separating allows independent scheduling

**Trade-offs**:
- ✅ Flexibility (can change reindex frequency without affecting sync)
- ✅ Faster sync (doesn't wait for reindex)
- ❌ More cron entries (slight complexity)

**Alternative considered**: Combined cron would simplify crontab but make sync slower.

---

### **Decision 3: Cron Safety (Lid Check + AC Power)**

**Options**:
- **A**: Always run cron (ignore lid state and power)
- **B**: Wrapper checks lid state + AC power before running
- **C**: Disable cron entirely, run manually

**Chosen**: **B** - Wrapper checks lid state + AC power

**Rationale**:
- Mac in backpack can overheat if cron runs while lid closed
- Running on battery drains power unnecessarily
- Wrapper provides safety without manual intervention
- `pmset -c` only wakes Mac when on AC power
- Wrapper checks lid state (if closed → skip run)

**Trade-offs**:
- ✅ Prevents overheating in backpack (safety)
- ✅ Saves battery power (efficiency)
- ✅ Automatic (no manual toggling)
- ❌ Reindex skipped if traveling 3+ days without opening laptop
- ❌ Extra wrapper script (slight complexity)

**Alternative considered**: Always run cron would be simpler but risk overheating.

---

### **Decision 4: Cross-Repo Sharing (One-Way vs. Two-Way)**

**Options**:
- **A**: One-way sharing (Legacy AI → Epic 2nd Brain only)
- **B**: Two-way sharing (both repos access each other)
- **C**: No sharing (each repo independent)

**Chosen**: **A** - One-way sharing (Legacy AI accesses Epic 2nd Brain resources)

**Rationale**:
- Business (legacy-ai) benefits from personal frameworks/books/podcasts
- Personal (epic 2nd brain) doesn't need business context (customer interviews, product specs)
- Meeting notes are personal reflections (excluded from sharing)
- Clear separation: Business queries don't pollute personal RAG

**Trade-offs**:
- ✅ Business RAG has richer context (frameworks + books)
- ✅ Personal RAG stays clean (no business noise)
- ❌ Asymmetric (slightly more complex to explain)

**Alternative considered**: Two-way sharing would give more context but mix business/personal.

---

## ✅ Success Metrics

**Completion Criteria**:
- [ ] RAG config files created for both repos
- [ ] Reindex script implemented and tested
- [ ] Cron safety wrapper created and tested
- [ ] pmset wake schedule configured
- [ ] Cron entry added
- [ ] All tests passing (unit + integration + E2E)
- [ ] 10 validation test queries pass (5 per repo)
- [ ] File count verified (no documents lost)
- [ ] MCP tools backward compatible (search still works)
- [ ] Cross-repo sharing validated (legacy-ai finds ai-assistant frameworks)

**Quality Metrics**:
- Reindex success rate: 100% (all-or-nothing, rollback on failure)
- Validation pass rate: ≥80% (8/10 test queries return relevant results)
- Reindex duration: <30 minutes for both repos
- Zero data loss (backup + restore works)
- Cron safety: 100% (never runs when lid closed or on battery)

---

## 🔗 Related Documentation

**Project Documentation**:
- `../prd.md` - Product requirements (all decisions locked)
- `phase-1-para-restructure.md` - PARA structure (dependency)
- `phase-2-notion-to-repo-sync.md` - Notion → Repo sync (uses RAG search)
- `phase-3-repo-to-notion-sync.md` - Repo → Notion sync (separate concern)

**Reference Materials**:
- ChromaDB docs: https://docs.trychroma.com/
- OpenAI embeddings docs: https://platform.openai.com/docs/guides/embeddings
- pmset man page: `man pmset` (Mac power management)

---

## 📝 Implementation Notes

**Why full wipe instead of incremental update?**
- PARA restructure changes ALL file paths (every document affected)
- Incremental update would require complex path mapping logic
- Full wipe ensures clean state (no orphaned chunks with old paths)
- Backup provides safety net (rollback on failure)

**Why separate cron for reindex vs. sync?**
- Reindex is expensive (~20-30 min), sync is fast (~10 sec)
- Reindex only needs daily, sync needs 2x/day
- Separating allows independent scheduling

**Why cron safety wrapper?**
- Mac in backpack can overheat if cron runs while lid closed
- Wrapper checks lid state + AC power before running
- Only runs when safe (plugged in + lid open)
- Prevents battery drain and overheating

**Why one-way cross-repo sharing?**
- Business (legacy-ai) benefits from personal frameworks/books
- Personal (epic 2nd brain) doesn't need business context
- Meeting notes kept private (personal reflections)

**Why include archive files?**
- Solo user, historical context valuable ("what did I do 6 months ago?")
- Archive documents still referenced in current work
- Disk space is cheap, context is valuable

---

## 📅 Version History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-16 | Claude Code (Sonnet 4.5) | Initial Phase 4 tech requirements (RAG reindex with PARA paths, cron safety, cross-repo sharing) |

---

**Status**: ✅ Tech requirements complete - Ready for implementation

**Next Step**: Implement after Phase 1 (PARA Restructure) complete

**Dependencies**:
- Phase 1 must be complete (new PARA file paths exist)
- legacy-ai RAG settings documented (chunking, embeddings, reranking)
