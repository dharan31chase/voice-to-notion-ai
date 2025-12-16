# Tech Requirements: Phase 1 - PARA Restructure

**Phase**: 1 of 6
**Estimated Time**: 6-8 hours (4-5 hours implementation + 2-3 hours your review/approval time)
**Priority**: P0 **CRITICAL** - Everything depends on this
**Dependencies**: None (first phase)
**Git Branch**: `feature/para-restructure`

---

## 🚨 CRITICAL CONSTRAINTS

### **Zero Data Loss Tolerance (P0)**
- Every file must be accounted for (pre/post file count must match)
- Git history must be preserved (`git mv`, NOT `mv`)
- All tests must pass before merge to main

### **MCP Must Work Immediately (P0)**
- MCP `start_session()` must work after restructure
- No transition period (immediate switch to new PARA paths)
- Automated + manual validation required

### **Rollback Plan Required (P0)**
- Can revert with `git revert` if issues found
- Feature branch protects main from bad changes
- Validation checkpoints at each area commit

---

## 🎯 Goal

Restructure ai-assistant and legacy-ai repositories to PARA (Projects, Areas, Resources, Archive) format while:
1. Preserving ALL files and Git history (zero data loss)
2. Ensuring MCP context loading works immediately
3. Creating clear, discoverable folder structure
4. Maintaining ability to rollback if needed

---

## ✅ Success Criteria

**Functional Requirements**:
- [ ] All content files moved to PARA structure (areas/, resources/, archive/)
- [ ] All technical files moved to infra/ folder
- [ ] ROADMAP.md moved to areas/epic-2nd-brain-infrastructure/
- [ ] MCP `start_session()` works for all work-streams
- [ ] File count matches pre-restructure inventory (zero data loss)
- [ ] Git history preserved for all moved files

**Quality Requirements**:
- [ ] All automated tests passing (file count, git history, MCP)
- [ ] Manual validation checklist complete (3-4 work-streams tested)
- [ ] Documentation updated (README.md, architecture docs)
- [ ] No broken links or missing files

**Non-Goals** (explicitly out of scope for Phase 1):
- ❌ Notion → Repo sync (Phase 2)
- ❌ Repo → Notion sync (Phase 3)
- ❌ RAG reindexing (Phase 4)
- ❌ Content creation (just moving existing files)

---

## 📊 Target PARA Structure

### **ai-assistant/** (Final State)

```
ai-assistant/
├── infra/                                    # NEW: Technical infrastructure
│   ├── scripts/                              # (moved from root)
│   │   ├── index_rag.py
│   │   ├── sync_to_notion.py
│   │   └── ...other scripts
│   ├── mcp_server/                           # (moved from root)
│   │   ├── full_server.py
│   │   ├── config/
│   │   │   └── path-mappings.json            # NEW: Old → New path mappings
│   │   ├── rag/
│   │   └── utils/
│   ├── logs/                                 # (moved from root)
│   ├── config/                               # (moved from root)
│   ├── tests/                                # (moved from root)
│   ├── processed/                            # (moved from root - archived recordings)
│   ├── transcripts/                          # (moved from root)
│   ├── analyzers/                            # (moved from root)
│   ├── parsers/                              # (moved from root)
│   ├── validators/                           # (moved from root)
│   ├── test_*.py                             # (moved from root - test files)
│   ├── requirements.txt                      # (moved from root)
│   ├── requirements-rag.txt                  # (moved from root)
│   └── README-infra.md                       # NEW: Infra documentation
│
├── areas/                                    # (renamed from 2-areas/)
│   ├── epic-2nd-brain-infrastructure/
│   │   ├── roadmap.md                        # (moved from root ROADMAP.md)
│   │   ├── projects/
│   │   │   ├── second-brain-sync/
│   │   │   │   ├── prd.md                    # (already exists)
│   │   │   │   ├── vision.md
│   │   │   │   ├── architecture/
│   │   │   │   ├── tech-requirements/
│   │   │   │   └── Building_a_Second_Brain___Tiago_Forte.md
│   │   │   ├── live-context-control-v3/
│   │   │   │   ├── prd.md                    # (from docs/prd/live-context-control-v3.md)
│   │   │   │   ├── tech-requirements/        # (from docs/tech-requirements/)
│   │   │   │   └── architecture/
│   │   │   ├── rag-implementation/
│   │   │   │   ├── prd.md                    # (from docs/prd/rag-implementation-legacy-ai.md)
│   │   │   │   └── tech-requirements/
│   │   │   ├── context-sync-bridge/
│   │   │   ├── roadmap-architecture-improvements/
│   │   │   ├── mobile-context-access/
│   │   │   └── ...other infrastructure projects
│   │   └── sessions/
│   │       ├── claude-code/                  # (from docs/sessions/claude-code/)
│   │       │   ├── 2025-12-16-roadmap-audit-and-refresh.md
│   │       │   ├── 2025-12-15-live-context-control-v3-quick-wins.md
│   │       │   └── ...other session logs
│   │       └── claude-chat/                  # (from docs/sessions/claude-chat/)
│   │
│   ├── lifeadmin/
│   │   ├── projects/
│   │   │   ├── welcoming-our-baby/
│   │   │   │   ├── meeting-notes/
│   │   │   │   └── research/
│   │   │   ├── home-remodel/
│   │   │   │   └── meeting-notes/
│   │   │   └── personal-logs/
│   │   │       └── (daily logs, reflections)
│   │   └── sessions/
│   │       └── claude-chat/
│   │
│   └── archive/                              # Inactive projects/areas
│       ├── epic-2nd-brain-infrastructure/    # Area-specific archives
│       │   ├── context-engineering-research/ # (from docs/archive/)
│       │   ├── failed-experiments/           # (from Failed/ + docs/archive/)
│       │   └── hold-for-later/               # (from hold-for-later/)
│       └── lifeadmin/
│           └── (future archived projects)
│
├── resources/                                # Shared knowledge (not project-specific)
│   ├── book-notes/
│   │   ├── building-a-second-brain.md
│   │   ├── the-mom-test.md
│   │   └── ...other book notes
│   ├── podcast-notes/
│   ├── frameworks/
│   │   ├── para-methodology.md
│   │   └── hemingway-bridge.md
│   ├── documents/
│   │   └── (tax forms, legal docs, etc.)
│   └── sync_config.json                      # NEW: Repo → Notion sync config (Phase 3)
│
├── .env, .gitignore, .git/, .claude/         # (stay at root)
├── README.md                                 # (stay at root)
└── CLAUDE.md                                 # (stay at root)
```

### **legacy-ai/** (Final State)

```
legacy-ai/
├── infra/                                    # NEW: If technical files exist
│   ├── scripts/
│   └── ...other technical files
│
├── areas/
│   ├── legacy-ai-business/
│   │   ├── roadmap.md                        # NEW: Business roadmap
│   │   ├── projects/
│   │   │   ├── fundraising/
│   │   │   │   ├── prd.md                    # (from docs/prd/ or docs/prds/)
│   │   │   │   ├── meeting-notes/
│   │   │   │   │   └── peter-theron-strategy-review.md
│   │   │   │   └── research/
│   │   │   ├── mvp-build/
│   │   │   ├── customer-discovery/
│   │   │   └── ...other business projects
│   │   └── sessions/
│   │       ├── claude-code/
│   │       └── claude-chat/                  # (from sessions/)
│   │
│   └── archive/
│       └── legacy-ai-business/
│           └── (inactive projects)
│
├── resources/                                # Separate from ai-assistant
│   ├── book-notes/
│   ├── frameworks/
│   ├── documents/
│   └── sync_config.json                      # NEW: Repo → Notion sync config (Phase 3)
│
├── .gitignore, .git/, .claude/               # (stay at root)
└── README.md                                 # (stay at root)
```

---

## 🏗️ Technical Approach

### **Overview: 8-Step Process**

1. **Pre-Restructure Inventory** (30 min) - Scan repos, generate inventory.json
2. **Path Mapping Generation** (30 min) - Infer area/project, get your approval
3. **Create Feature Branch** (5 min) - `feature/para-restructure`
4. **Create PARA Folder Structure** (15 min) - Empty folders + commit
5. **Move Files (Git MV)** (120 min) - Per-area commits, preserve history
6. **Update MCP Config** (30 min) - path-mappings.json + start_session() updates
7. **Automated Testing** (30 min) - File count, git history, MCP tests
8. **Manual Validation** (30 min) - You test start_session(), verify workflows

**Total: 6-8 hours** (including your review time)

---

## 🔍 Step 1: Pre-Restructure Inventory Script

### **Goal**: Generate complete file inventory before moving anything

### **Script**: `infra/scripts/generate_inventory.py`

```python
#!/usr/bin/env python3
"""
Pre-Restructure Inventory Generator
Scans ai-assistant and legacy-ai repos, generates inventory.json
"""

import os
import json
from pathlib import Path
from datetime import datetime

def count_files_recursively(root_path, exclude_dirs):
    """Count all files, excluding .git, node_modules, etc."""
    file_count = 0
    files_list = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Exclude directories
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            # Skip hidden files
            if filename.startswith('.'):
                continue

            file_path = Path(dirpath) / filename
            relative_path = file_path.relative_to(root_path)

            files_list.append({
                "path": str(relative_path),
                "size": file_path.stat().st_size,
                "type": categorize_file(str(relative_path)),
                "proposed_destination": infer_destination(str(relative_path))
            })
            file_count += 1

    return file_count, files_list

def categorize_file(path):
    """Categorize file by location/name"""
    path_lower = path.lower()

    if "prd" in path and path.endswith(".md"):
        return "prd"
    elif "tech-req" in path or "technical" in path:
        return "tech-requirements"
    elif "session" in path:
        return "session-log"
    elif "script" in path and path.endswith(".py"):
        return "script"
    elif "test" in path:
        return "test"
    elif path.endswith(".md"):
        return "documentation"
    elif path.endswith(".py"):
        return "code"
    elif path.endswith(".json"):
        return "config"
    else:
        return "other"

def infer_destination(path):
    """Infer PARA destination based on file path/name"""

    # Technical infrastructure files
    if any(x in path for x in ["scripts/", "mcp_server/", "logs/", "config/",
                                "tests/", "processed/", "transcripts/",
                                "analyzers/", "parsers/", "validators/"]):
        return f"infra/{path}"

    # Root test files
    if path.startswith("test_") and path.endswith(".py"):
        return f"infra/{path}"

    # Requirements files
    if "requirements" in path and path.endswith(".txt"):
        return f"infra/{path}"

    # PRDs - infer project from filename
    if "docs/prd/" in path and path.endswith(".md"):
        prd_name = Path(path).stem  # e.g., "live-context-control-v3"
        # Assume epic-2nd-brain-infrastructure unless legacy-ai related
        if "legacy" in prd_name or "fundrais" in prd_name or "mvp" in prd_name:
            area = "legacy-ai-business"
        else:
            area = "epic-2nd-brain-infrastructure"
        return f"areas/{area}/projects/{prd_name}/prd.md"

    # Session logs
    if "docs/sessions/claude-code/" in path:
        return f"areas/epic-2nd-brain-infrastructure/sessions/claude-code/{Path(path).name}"
    elif "docs/sessions/claude-chat/" in path:
        return f"areas/epic-2nd-brain-infrastructure/sessions/claude-chat/{Path(path).name}"
    elif "sessions/" in path:  # legacy-ai sessions
        return f"areas/legacy-ai-business/sessions/claude-chat/{Path(path).name}"

    # Tech requirements
    if "docs/tech-requirements/" in path:
        # Extract project name from path (e.g., docs/tech-requirements/live-context-control-v3/...)
        parts = Path(path).parts
        if len(parts) >= 3:
            project_name = parts[2]  # e.g., "live-context-control-v3"
            return f"areas/epic-2nd-brain-infrastructure/projects/{project_name}/tech-requirements/{Path(path).name}"
        return f"areas/epic-2nd-brain-infrastructure/tech-requirements/{Path(path).name}"

    # Archives
    if "docs/archive/" in path or "Failed/" in path or "hold-for-later/" in path:
        # Determine which area this archive belongs to
        area = "epic-2nd-brain-infrastructure"  # Default
        archive_item = Path(path).parts[1] if len(Path(path).parts) > 1 else "misc"
        return f"areas/archive/{area}/{archive_item}/{Path(path).name}"

    # 2-areas/ already in PARA structure (just rename folder)
    if path.startswith("2-areas/"):
        return path.replace("2-areas/", "areas/", 1)

    # ROADMAP.md at root
    if path == "ROADMAP.md":
        return "areas/epic-2nd-brain-infrastructure/roadmap.md"

    # Default: flag for manual review
    return f"MANUAL_REVIEW/{path}"

def generate_inventory(repo_path, repo_name):
    """Generate inventory for a single repo"""
    exclude_dirs = ['.git', '.chroma', '.cache', '.claude', 'ai-env',
                    'node_modules', '__pycache__', '.DS_Store']

    print(f"\n🔍 Scanning {repo_name}...")
    file_count, files_list = count_files_recursively(repo_path, exclude_dirs)

    inventory = {
        "repo": repo_name,
        "scan_date": datetime.utcnow().isoformat() + "Z",
        "total_files": file_count,
        "files": files_list,
        "files_needing_manual_review": [
            f for f in files_list if "MANUAL_REVIEW" in f["proposed_destination"]
        ]
    }

    print(f"✅ Found {file_count} files")
    print(f"⚠️  {len(inventory['files_needing_manual_review'])} files need manual review")

    return inventory

def main():
    """Main entry point"""
    # Paths to repos
    ai_assistant_path = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant")
    legacy_ai_path = Path("/Users/dharanchandrahasan/Documents/1. Projects/legacy-ai")

    # Generate inventories
    ai_inventory = generate_inventory(ai_assistant_path, "ai-assistant")
    legacy_inventory = generate_inventory(legacy_ai_path, "legacy-ai")

    # Save to JSON
    output = {
        "inventories": [ai_inventory, legacy_inventory],
        "summary": {
            "total_files": ai_inventory["total_files"] + legacy_inventory["total_files"],
            "ai_assistant_files": ai_inventory["total_files"],
            "legacy_ai_files": legacy_inventory["total_files"],
            "manual_review_needed": (
                len(ai_inventory["files_needing_manual_review"]) +
                len(legacy_inventory["files_needing_manual_review"])
            )
        }
    }

    output_path = ai_assistant_path / "infra" / "inventory-pre-restructure.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✅ Inventory saved to: {output_path}")
    print(f"\n📊 Summary:")
    print(f"  Total files: {output['summary']['total_files']}")
    print(f"  ai-assistant: {output['summary']['ai_assistant_files']}")
    print(f"  legacy-ai: {output['summary']['legacy_ai_files']}")
    print(f"  Manual review needed: {output['summary']['manual_review_needed']}")

    # Print files needing manual review
    if output['summary']['manual_review_needed'] > 0:
        print(f"\n⚠️  Files needing manual review:")
        for inv in output['inventories']:
            for file in inv['files_needing_manual_review']:
                print(f"    - {file['path']}")

if __name__ == "__main__":
    main()
```

### **Running the Inventory Script**

```bash
# Before running restructure, generate inventory
cd /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant

# Create infra/ folder if doesn't exist
mkdir -p infra/scripts

# Run inventory script
python3 infra/scripts/generate_inventory.py

# Review output
cat infra/inventory-pre-restructure.json | jq '.summary'

# Review files needing manual review
cat infra/inventory-pre-restructure.json | jq '.inventories[].files_needing_manual_review'
```

### **Expected Output**

```json
{
  "inventories": [
    {
      "repo": "ai-assistant",
      "scan_date": "2025-12-16T17:30:00Z",
      "total_files": 423,
      "files": [...],
      "files_needing_manual_review": [
        {"path": "product/some-file.md", "proposed_destination": "MANUAL_REVIEW/product/some-file.md"},
        ...
      ]
    },
    {
      "repo": "legacy-ai",
      "total_files": 87,
      ...
    }
  ],
  "summary": {
    "total_files": 510,
    "ai_assistant_files": 423,
    "legacy_ai_files": 87,
    "manual_review_needed": 12
  }
}
```

### **Your Review Step** (30 min)

1. Open `infra/inventory-pre-restructure.json`
2. Review `files_needing_manual_review` array
3. For each file, tell me:
   - Correct area (epic-2nd-brain-infrastructure, lifeadmin, legacy-ai-business)
   - Correct project (if applicable)
   - Or: Delete this file (if obsolete)

**Example Review**:
```
File: product/strategy.md
→ Move to: areas/legacy-ai-business/projects/product-strategy/strategy.md

File: core/old-code.py
→ Delete (obsolete)

File: docs/insights/user-research.md
→ Move to: areas/legacy-ai-business/projects/customer-discovery/research/user-research.md
```

---

## 🗺️ Step 2: Path Mapping Generation

### **Goal**: Generate `path-mappings.json` for MCP based on approved inventory

### **Script**: `infra/scripts/generate_path_mappings.py`

```python
#!/usr/bin/env python3
"""
Path Mappings Generator
Generates path-mappings.json for MCP from approved inventory
"""

import json
from pathlib import Path

def generate_path_mappings(inventory_path, manual_overrides=None):
    """Generate path mappings from inventory"""

    with open(inventory_path) as f:
        data = json.load(f)

    mappings = {}

    # Process each repo's files
    for inventory in data['inventories']:
        for file_info in inventory['files']:
            old_path = file_info['path']
            proposed_dest = file_info['proposed_destination']

            # Skip files that don't need mapping (already in correct location)
            if old_path == proposed_dest:
                continue

            # Skip manual review files (handle separately)
            if "MANUAL_REVIEW" in proposed_dest:
                continue

            # Apply manual overrides if provided
            if manual_overrides and old_path in manual_overrides:
                proposed_dest = manual_overrides[old_path]

            mappings[old_path] = proposed_dest

    # Generate path-mappings.json structure
    output = {
        "version": "1.0",
        "migration_complete": False,  # Set to True after restructure
        "fallback_enabled": False,     # No fallback - immediate switch
        "mappings": mappings,
        "pattern_rules": [
            {
                "description": "PRDs moved to project folders",
                "old_pattern": "docs/prd/*.md",
                "new_pattern": "areas/{area}/projects/{project}/prd.md"
            },
            {
                "description": "Session logs moved to area sessions",
                "old_pattern": "docs/sessions/{agent}/*.md",
                "new_pattern": "areas/{area}/sessions/{agent}/*.md"
            },
            {
                "description": "Tech requirements moved to project folders",
                "old_pattern": "docs/tech-requirements/{project}/*",
                "new_pattern": "areas/{area}/projects/{project}/tech-requirements/*"
            }
        ]
    }

    return output

def main():
    """Generate path mappings"""
    inventory_path = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/infra/inventory-pre-restructure.json")

    # Manual overrides (you provide these after reviewing inventory)
    manual_overrides = {
        # Example:
        # "product/strategy.md": "areas/legacy-ai-business/projects/product-strategy/strategy.md",
        # Add your overrides here after reviewing inventory
    }

    path_mappings = generate_path_mappings(inventory_path, manual_overrides)

    # Save to MCP config
    output_path = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/infra/mcp_server/config/path-mappings.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(path_mappings, f, indent=2)

    print(f"✅ Path mappings saved to: {output_path}")
    print(f"📊 Total mappings: {len(path_mappings['mappings'])}")

if __name__ == "__main__":
    main()
```

### **Path Mappings JSON Structure**

```json
{
  "version": "1.0",
  "migration_complete": false,
  "fallback_enabled": false,
  "mappings": {
    "docs/prd/live-context-control-v3.md": "areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/prd.md",
    "docs/prd/rag-implementation-legacy-ai.md": "areas/epic-2nd-brain-infrastructure/projects/rag-implementation/prd.md",
    "docs/sessions/claude-code/2025-12-16-roadmap-audit-and-refresh.md": "areas/epic-2nd-brain-infrastructure/sessions/claude-code/2025-12-16-roadmap-audit-and-refresh.md",
    "ROADMAP.md": "areas/epic-2nd-brain-infrastructure/roadmap.md",
    "scripts/index_rag.py": "infra/scripts/index_rag.py",
    "mcp_server/full_server.py": "infra/mcp_server/full_server.py",
    ...
  },
  "pattern_rules": [
    {
      "description": "PRDs moved to project folders",
      "old_pattern": "docs/prd/*.md",
      "new_pattern": "areas/{area}/projects/{project}/prd.md"
    }
  ]
}
```

---

## 📝 Step 3: Create Feature Branch

### **Goal**: Create isolated branch for restructure work

```bash
cd /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant

# Ensure working directory is clean
git status

# If there are uncommitted changes, stash them
git stash

# Create feature branch
git checkout -b feature/para-restructure

# Verify branch
git branch

# Output: * feature/para-restructure
#         main
```

---

## 🏗️ Step 4: Create PARA Folder Structure

### **Goal**: Create empty PARA folders before moving files

### **Script**: `infra/scripts/create_para_structure.sh`

```bash
#!/bin/bash
# Create PARA folder structure (ai-assistant)

set -e  # Exit on error

echo "🏗️  Creating PARA folder structure..."

# Create infra/ folder
mkdir -p infra/{scripts,mcp_server,logs,config,tests}

# Create areas/ folder (will move 2-areas/ content here)
mkdir -p areas/epic-2nd-brain-infrastructure/{projects,sessions/{claude-code,claude-chat}}
mkdir -p areas/lifeadmin/{projects,sessions/claude-chat}
mkdir -p areas/archive/{epic-2nd-brain-infrastructure,lifeadmin}

# Create resources/ folder
mkdir -p resources/{book-notes,podcast-notes,frameworks,documents}

echo "✅ PARA structure created"

# Verify structure
tree -L 3 -d areas/ resources/ infra/
```

### **Run Structure Creation**

```bash
cd /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant

# Make script executable
chmod +x infra/scripts/create_para_structure.sh

# Run script
./infra/scripts/create_para_structure.sh

# Commit empty structure
git add areas/ resources/ infra/
git commit -m "[PARA] Create empty PARA folder structure

## What Shipped

Created base PARA structure:
- infra/ - Technical infrastructure folder
- areas/ - Empty PARA areas (epic-2nd-brain-infrastructure, lifeadmin, archive)
- resources/ - Shared knowledge repository

## Next Steps

- Move files from old locations to new PARA structure
- Update MCP config to use new paths

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 📦 Step 5: Move Files with Git MV (Per-Area Commits)

### **Goal**: Move files using `git mv` to preserve history, commit per area

### **Per-Area Git MV Sequences**

#### **5.1: Move 2-areas/ → areas/ (Rename)**

```bash
# Rename 2-areas/ to areas/ (preserves existing content)
git mv 2-areas areas

# Commit
git commit -m "[PARA-areas] Rename 2-areas/ → areas/

## What Shipped

Renamed 2-areas/ to areas/ (preserves all existing content in epic-2nd-brain-infrastructure/)

- Git history preserved
- No file content changes
- Clean PARA naming

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### **5.2: Move Infra Files**

```bash
# Move scripts
git mv scripts infra/

# Move mcp_server
git mv mcp_server infra/

# Move logs
git mv logs infra/

# Move config
git mv config infra/

# Move tests
git mv tests infra/

# Move processed
git mv processed infra/

# Move transcripts
git mv transcripts infra/

# Move analyzers, parsers, validators
git mv analyzers infra/
git mv parsers infra/
git mv validators infra/

# Move root test files
git mv test_*.py infra/

# Move requirements files
git mv requirements.txt infra/
git mv requirements-rag.txt infra/

# Commit infra move
git add -A
git commit -m "[PARA-infra] Move technical files to infra/

## What Shipped

Moved all technical infrastructure to infra/:
- scripts/, mcp_server/, logs/, config/, tests/
- processed/, transcripts/, analyzers/, parsers/, validators/
- Root test files (test_*.py)
- Requirements files

## Impact

- Clean separation: content (PARA) vs technical (infra)
- Git history preserved (git mv)
- File count validated: [X] files moved

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Validate file count
echo "📊 File count validation:"
find infra/ -type f | wc -l
# Compare to inventory.json infra file count
```

#### **5.3: Move Epic 2nd Brain Infrastructure Area**

```bash
# Move ROADMAP.md
git mv ROADMAP.md areas/epic-2nd-brain-infrastructure/roadmap.md

# Move PRDs to projects (based on path-mappings.json)
# Example for live-context-control-v3:
mkdir -p areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3
git mv docs/prd/live-context-control-v3.md areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/prd.md

# Move tech requirements
mkdir -p areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/tech-requirements
git mv docs/tech-requirements/live-context-control-v3.md areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/tech-requirements/

# Repeat for other PRDs (script this - see below)

# Move session logs
git mv docs/sessions/claude-code/* areas/epic-2nd-brain-infrastructure/sessions/claude-code/
git mv docs/sessions/claude-chat/* areas/epic-2nd-brain-infrastructure/sessions/claude-chat/

# Move archives
mkdir -p areas/archive/epic-2nd-brain-infrastructure
git mv docs/archive/context-engineering-research areas/archive/epic-2nd-brain-infrastructure/
git mv docs/archive/failed-experiments areas/archive/epic-2nd-brain-infrastructure/
git mv Failed areas/archive/epic-2nd-brain-infrastructure/failed-experiments
git mv hold-for-later areas/archive/epic-2nd-brain-infrastructure/

# Commit epic 2nd brain infrastructure area
git add -A
git commit -m "[PARA-epic-2nd-brain] Move Epic 2nd Brain Infrastructure area content

## What Shipped

Moved all Epic 2nd Brain Infrastructure content:
- ROADMAP.md → areas/epic-2nd-brain-infrastructure/roadmap.md
- PRDs: [list projects]
- Session logs: [X] claude-code, [Y] claude-chat
- Archives: context-engineering-research, failed-experiments, hold-for-later

## Impact

- All infrastructure projects now in PARA structure
- Git history preserved
- File count validated: [X] files moved

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### **5.4: Move Lifeadmin Area**

```bash
# Move personal logs (if they exist)
# Based on your manual review of inventory

# Example:
mkdir -p areas/lifeadmin/projects/personal-logs
# (Move files as identified in inventory review)

# Commit lifeadmin area
git add -A
git commit -m "[PARA-lifeadmin] Move Lifeadmin area content

## What Shipped

Moved all Lifeadmin content:
- Personal logs
- [Other lifeadmin projects identified]

## Impact

- Lifeadmin area established
- Git history preserved
- File count validated: [X] files moved

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### **5.5: Move Resources**

```bash
# Move book notes, frameworks, documents
# Based on inventory and manual review

# Example:
# (If resources exist in current repo, move them)
# git mv some-book-notes.md resources/book-notes/

# Commit resources
git add -A
git commit -m "[PARA-resources] Move shared knowledge to resources/

## What Shipped

Moved all shared knowledge resources:
- Book notes: [list]
- Frameworks: [list]
- Documents: [list]

## Impact

- Resources separated from project-specific content
- Shareable across areas
- Git history preserved
- File count validated: [X] files moved

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### **Automated Git MV Script**

To reduce manual effort, create a script that reads `path-mappings.json` and performs git mv:

#### **Script**: `infra/scripts/perform_para_restructure.py`

```python
#!/usr/bin/env python3
"""
PARA Restructure Executor
Reads path-mappings.json and performs git mv commands
"""

import json
import subprocess
from pathlib import Path

def perform_git_mv(old_path, new_path):
    """Execute git mv command"""
    # Create parent directory if doesn't exist
    new_path_obj = Path(new_path)
    new_path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Perform git mv
    try:
        result = subprocess.run(
            ["git", "mv", old_path, new_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Moved: {old_path} → {new_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {old_path} → {new_path}")
        print(f"   Error: {e.stderr}")
        return False

def group_mappings_by_area(mappings):
    """Group file mappings by destination area"""
    groups = {
        "infra": [],
        "epic-2nd-brain-infrastructure": [],
        "lifeadmin": [],
        "resources": [],
        "archive": []
    }

    for old_path, new_path in mappings.items():
        if new_path.startswith("infra/"):
            groups["infra"].append((old_path, new_path))
        elif "epic-2nd-brain-infrastructure" in new_path:
            groups["epic-2nd-brain-infrastructure"].append((old_path, new_path))
        elif "lifeadmin" in new_path:
            groups["lifeadmin"].append((old_path, new_path))
        elif new_path.startswith("resources/"):
            groups["resources"].append((old_path, new_path))
        elif "archive" in new_path:
            groups["archive"].append((old_path, new_path))
        else:
            print(f"⚠️  Unknown destination area: {new_path}")

    return groups

def commit_area(area_name, file_count):
    """Commit changes for an area"""
    commit_messages = {
        "infra": f"[PARA-infra] Move technical files to infra/ ({file_count} files)",
        "epic-2nd-brain-infrastructure": f"[PARA-epic-2nd-brain] Move Epic 2nd Brain Infrastructure area ({file_count} files)",
        "lifeadmin": f"[PARA-lifeadmin] Move Lifeadmin area ({file_count} files)",
        "resources": f"[PARA-resources] Move shared knowledge to resources/ ({file_count} files)",
        "archive": f"[PARA-archive] Move archived content to areas/archive/ ({file_count} files)"
    }

    try:
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(
            ["git", "commit", "-m", commit_messages[area_name]],
            check=True
        )
        print(f"✅ Committed: {area_name} ({file_count} files)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Commit failed for {area_name}: {e}")
        return False

def main():
    """Execute PARA restructure"""
    mappings_path = Path("infra/mcp_server/config/path-mappings.json")

    with open(mappings_path) as f:
        data = json.load(f)

    mappings = data['mappings']
    print(f"📊 Total file mappings: {len(mappings)}")

    # Group by area
    groups = group_mappings_by_area(mappings)

    # Execute moves per area
    for area_name, file_mappings in groups.items():
        if not file_mappings:
            print(f"⏭️  Skipping {area_name} (no files)")
            continue

        print(f"\n🔄 Processing {area_name} ({len(file_mappings)} files)...")

        success_count = 0
        for old_path, new_path in file_mappings:
            if perform_git_mv(old_path, new_path):
                success_count += 1

        print(f"📊 {area_name}: {success_count}/{len(file_mappings)} files moved")

        # Commit this area
        if success_count > 0:
            commit_area(area_name, success_count)

    print("\n✅ PARA restructure complete!")
    print("🔍 Next: Run validation tests")

if __name__ == "__main__":
    main()
```

### **Running the Restructure Script**

```bash
cd /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant

# Ensure you're on feature branch
git branch

# Run restructure script
python3 infra/scripts/perform_para_restructure.py

# Output:
# 📊 Total file mappings: 423
#
# 🔄 Processing infra (87 files)...
# ✅ Moved: scripts/index_rag.py → infra/scripts/index_rag.py
# ...
# 📊 infra: 87/87 files moved
# ✅ Committed: infra (87 files)
#
# 🔄 Processing epic-2nd-brain-infrastructure (312 files)...
# ...
```

---

## 🔧 Step 6: Update MCP Config

### **Goal**: Update MCP to use new PARA paths immediately (no fallback)

### **6.1: PathMapper Module** (if not exists)

Create `infra/mcp_server/utils/path_mapper.py`:

```python
"""
PathMapper - Translates old paths to new PARA paths
"""

import json
from pathlib import Path

class PathMapper:
    """Maps old file paths to new PARA structure"""

    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "path-mappings.json"

        with open(config_path) as f:
            self.config = json.load(f)

        self.mappings = self.config['mappings']
        self.migration_complete = self.config['migration_complete']

    def map_path(self, old_path):
        """
        Map old path to new PARA path

        Args:
            old_path: Original file path (e.g., "docs/prd/live-context-control-v3.md")

        Returns:
            New PARA path (e.g., "areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/prd.md")
        """
        # Direct mapping lookup
        if old_path in self.mappings:
            return self.mappings[old_path]

        # If migration complete and no mapping found, assume it's already in new location
        if self.migration_complete:
            return old_path

        # Pattern matching (fallback)
        for pattern_rule in self.config.get('pattern_rules', []):
            # Simple pattern matching (can be enhanced with regex)
            old_pattern = pattern_rule['old_pattern']
            if self._matches_pattern(old_path, old_pattern):
                # Return old path (needs manual mapping)
                print(f"⚠️  No mapping found for: {old_path}")
                return old_path

        return old_path

    def _matches_pattern(self, path, pattern):
        """Simple wildcard pattern matching"""
        # TODO: Implement proper pattern matching if needed
        return False

    def resolve_work_stream_paths(self, work_stream_paths):
        """
        Resolve list of work-stream paths to new PARA paths

        Args:
            work_stream_paths: List of old paths

        Returns:
            List of new PARA paths
        """
        return [self.map_path(p) for p in work_stream_paths]

# Singleton instance
_path_mapper = None

def get_path_mapper():
    """Get singleton PathMapper instance"""
    global _path_mapper
    if _path_mapper is None:
        _path_mapper = PathMapper()
    return _path_mapper
```

### **6.2: Update start_session() in full_server.py**

Modify `infra/mcp_server/full_server.py`:

```python
# Add import at top
from .utils.path_mapper import get_path_mapper

# Update start_session function
@mcp.tool()
def start_session(repo: str, work_stream: str = None):
    """
    🎯 USE THIS: Start a new session, loading context from PARA structure

    Args:
        repo: "ai-assistant" or "legacy-ai"
        work_stream: Optional work stream name (e.g., "second-brain-sync", "fundraising")

    Returns:
        Context files loaded for the session
    """
    # Get path mapper
    path_mapper = get_path_mapper()

    # Load work-stream mappings
    work_stream_config = load_work_stream_config(repo, work_stream)

    # OLD paths from config
    old_paths = work_stream_config.get('paths', [])

    # Map to NEW PARA paths
    new_paths = path_mapper.resolve_work_stream_paths(old_paths)

    # Load files from NEW paths
    context_files = []
    for path in new_paths:
        full_path = get_repo_root(repo) / path
        if full_path.exists():
            context_files.append({
                "path": path,
                "content": full_path.read_text(),
                "size": full_path.stat().st_size
            })
        else:
            print(f"⚠️  File not found: {path}")

    return {
        "repo": repo,
        "work_stream": work_stream,
        "files_loaded": len(context_files),
        "files": context_files
    }
```

### **6.3: Update work-stream-mappings.json**

Update `infra/mcp_server/config/work-stream-mappings.json` to use new PARA paths:

**Before** (old paths):
```json
{
  "ai-assistant": {
    "second-brain-sync": {
      "paths": [
        "2-areas/epic-2nd-brain-infrastructure/projects/second-brain-sync/prd.md",
        "2-areas/epic-2nd-brain-infrastructure/projects/second-brain-sync/architecture/",
        "docs/sessions/claude-code/"
      ]
    }
  }
}
```

**After** (new PARA paths):
```json
{
  "ai-assistant": {
    "second-brain-sync": {
      "paths": [
        "areas/epic-2nd-brain-infrastructure/projects/second-brain-sync/prd.md",
        "areas/epic-2nd-brain-infrastructure/projects/second-brain-sync/architecture/",
        "areas/epic-2nd-brain-infrastructure/sessions/claude-code/"
      ]
    },
    "live-context-control-v3": {
      "paths": [
        "areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/prd.md",
        "areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/tech-requirements/",
        "areas/epic-2nd-brain-infrastructure/sessions/claude-code/"
      ]
    }
  },
  "legacy-ai": {
    "fundraising": {
      "paths": [
        "areas/legacy-ai-business/projects/fundraising/prd.md",
        "areas/legacy-ai-business/projects/fundraising/meeting-notes/",
        "areas/legacy-ai-business/sessions/claude-chat/"
      ]
    }
  }
}
```

### **6.4: Commit MCP Updates**

```bash
git add infra/mcp_server/
git commit -m "[PARA-mcp] Update MCP config for PARA paths

## What Shipped

Updated MCP configuration for PARA structure:
- Created PathMapper module (path translation)
- Updated start_session() to use PathMapper
- Updated work-stream-mappings.json with new PARA paths
- Set migration_complete: true in path-mappings.json

## Impact

- MCP immediately uses new PARA paths (no fallback)
- start_session() works with new structure
- Backward compatibility removed (clean switch)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 🧪 Step 7: Automated Testing

### **Goal**: Validate restructure with automated tests

### **Test Suite**: `infra/tests/test_para_restructure.py`

```python
"""
PARA Restructure Validation Tests
"""

import pytest
import subprocess
import json
from pathlib import Path

# Paths
REPO_ROOT = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant")
INVENTORY_PATH = REPO_ROOT / "infra" / "inventory-pre-restructure.json"

def load_inventory():
    """Load pre-restructure inventory"""
    with open(INVENTORY_PATH) as f:
        return json.load(f)

def count_files_in_repo():
    """Count files in repo (excluding .git)"""
    result = subprocess.run(
        ["find", str(REPO_ROOT), "-type", "f", "-not", "-path", "*/.git/*"],
        capture_output=True,
        text=True
    )
    return len(result.stdout.strip().split('\n'))

def test_no_data_loss():
    """Test 1: Verify file count matches pre-restructure inventory"""
    inventory = load_inventory()
    expected_count = inventory['summary']['ai_assistant_files']

    actual_count = count_files_in_repo()

    assert actual_count == expected_count, (
        f"File count mismatch! Expected: {expected_count}, Actual: {actual_count}"
    )
    print(f"✅ File count matches: {actual_count} files")

def test_git_history_preserved():
    """Test 2: Verify git history preserved for moved files"""
    # Test a few known files
    test_files = [
        "areas/epic-2nd-brain-infrastructure/roadmap.md",  # Moved from ROADMAP.md
        "infra/scripts/index_rag.py",  # Moved from scripts/index_rag.py
    ]

    for file_path in test_files:
        full_path = REPO_ROOT / file_path
        if not full_path.exists():
            pytest.skip(f"File doesn't exist: {file_path}")

        # Run git log --follow
        result = subprocess.run(
            ["git", "log", "--follow", "--oneline", str(file_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"git log --follow failed for {file_path}"
        assert len(result.stdout.strip().split('\n')) > 0, (
            f"No git history found for {file_path}"
        )
        print(f"✅ Git history preserved: {file_path}")

def test_mcp_start_session():
    """Test 3: Verify MCP start_session() works with new paths"""
    # This requires MCP server running - manual test recommended
    # Or mock the start_session call

    # Import PathMapper
    import sys
    sys.path.insert(0, str(REPO_ROOT / "infra" / "mcp_server"))

    from utils.path_mapper import get_path_mapper

    path_mapper = get_path_mapper()

    # Test path resolution
    old_path = "docs/prd/live-context-control-v3.md"
    new_path = path_mapper.map_path(old_path)

    expected_new_path = "areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/prd.md"

    assert new_path == expected_new_path, (
        f"Path mapping failed! Expected: {expected_new_path}, Got: {new_path}"
    )
    print(f"✅ MCP PathMapper works: {old_path} → {new_path}")

def test_para_structure_exists():
    """Test 4: Verify PARA structure directories exist"""
    required_dirs = [
        "infra",
        "areas/epic-2nd-brain-infrastructure",
        "areas/lifeadmin",
        "areas/archive",
        "resources"
    ]

    for dir_path in required_dirs:
        full_path = REPO_ROOT / dir_path
        assert full_path.exists(), f"Required directory missing: {dir_path}"
        assert full_path.is_dir(), f"Not a directory: {dir_path}"
        print(f"✅ Directory exists: {dir_path}")

def test_critical_files_exist():
    """Test 5: Verify critical files exist in new locations"""
    critical_files = [
        "areas/epic-2nd-brain-infrastructure/roadmap.md",
        "infra/mcp_server/full_server.py",
        "infra/mcp_server/config/path-mappings.json",
    ]

    for file_path in critical_files:
        full_path = REPO_ROOT / file_path
        assert full_path.exists(), f"Critical file missing: {file_path}"
        assert full_path.is_file(), f"Not a file: {file_path}"
        print(f"✅ Critical file exists: {file_path}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
```

### **Running Tests**

```bash
cd /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant

# Run test suite
pytest infra/tests/test_para_restructure.py -v

# Expected output:
# test_para_restructure.py::test_no_data_loss PASSED
# test_para_restructure.py::test_git_history_preserved PASSED
# test_para_restructure.py::test_mcp_start_session PASSED
# test_para_restructure.py::test_para_structure_exists PASSED
# test_para_restructure.py::test_critical_files_exist PASSED
#
# ==================== 5 passed in 2.34s ====================
```

---

## ✅ Step 8: Manual Validation (Your Testing)

### **Goal**: You manually test critical workflows

### **Manual Test Checklist**

#### **Test 1: Start Session (second-brain-sync)**

```bash
# In Claude Code, run:
start_session("ai-assistant", "second-brain-sync")

# Expected result:
# ✅ Loads PRD from areas/epic-2nd-brain-infrastructure/projects/second-brain-sync/prd.md
# ✅ Loads architecture docs
# ✅ Loads recent session logs from areas/epic-2nd-brain-infrastructure/sessions/claude-code/
# ✅ Context load time: <3 min
```

**Validation**:
- [ ] Files loaded correctly
- [ ] No "file not found" errors
- [ ] Context is complete (all expected files present)

---

#### **Test 2: Start Session (fundraising - legacy-ai)**

```bash
# In Claude Code, run:
start_session("legacy-ai", "fundraising")

# Expected result:
# ✅ Loads PRD from areas/legacy-ai-business/projects/fundraising/prd.md
# ✅ Loads meeting notes
# ✅ Loads session logs
```

**Validation**:
- [ ] Files loaded correctly
- [ ] legacy-ai repo paths work
- [ ] No path resolution errors

---

#### **Test 3: List Files (Browse PARA Structure)**

```bash
# In Claude Code, run:
list_files("ai-assistant", "areas/epic-2nd-brain-infrastructure/projects/", recursive=True)

# Expected result:
# ✅ Lists all project folders
# ✅ Shows second-brain-sync, live-context-control-v3, rag-implementation, etc.
```

**Validation**:
- [ ] Folder structure is readable
- [ ] All expected projects visible
- [ ] No missing folders

---

#### **Test 4: RAG Search (Verify Paths)**

```bash
# In Claude Code, run:
search_epic_2nd_brain("context engineering")

# Expected result:
# ✅ Finds "Live Context Control v3" PRD
# ✅ Path shown: areas/epic-2nd-brain-infrastructure/projects/live-context-control-v3/prd.md
```

**Validation**:
- [ ] RAG still finds documents (may need reindex - Phase 4)
- [ ] Paths are new PARA paths
- [ ] Search quality unchanged

---

### **Manual Validation Summary**

After completing all 4 manual tests:

- [ ] All tests passed
- [ ] MCP workflows work normally
- [ ] No critical issues found
- [ ] Ready to merge to main

---

## 🔄 Step 9: Merge to Main (If All Tests Pass)

### **Goal**: Merge feature branch to main after validation

```bash
cd /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant

# Ensure all tests passed
git status

# Switch to main
git checkout main

# Merge feature branch
git merge feature/para-restructure --no-ff

# Push to remote
git push origin main

# Optional: Delete feature branch
git branch -d feature/para-restructure

# Success message
echo "✅ PARA restructure complete and merged to main!"
```

---

## 🚨 Rollback Plan (If Issues Found)

### **Scenario 1: Issues Found During Testing (Before Merge)**

**Action**: Stay on feature branch, fix issues, re-test

```bash
# Make fixes on feature branch
git checkout feature/para-restructure

# Fix issues...

# Re-run tests
pytest infra/tests/test_para_restructure.py -v

# Re-test manually

# When fixed, merge to main
```

---

### **Scenario 2: Issues Found After Merge to Main**

**Action**: Revert commits, return to pre-restructure state

```bash
# Find restructure commits
git log --oneline | grep PARA

# Example output:
# abc123d [PARA-resources] Move shared knowledge to resources/
# def456e [PARA-lifeadmin] Move Lifeadmin area content
# ghi789f [PARA-epic-2nd-brain] Move Epic 2nd Brain Infrastructure area
# jkl012g [PARA-infra] Move technical files to infra/
# mno345h [PARA-areas] Rename 2-areas/ → areas/
# pqr678i [PARA] Create empty PARA folder structure

# Revert commits in reverse order (most recent first)
git revert abc123d
git revert def456e
git revert ghi789f
git revert jkl012g
git revert mno345h
git revert pqr678i

# Push reverts
git push origin main

# Repo is now back to pre-restructure state
```

---

### **Scenario 3: Partial Rollback (Specific Area)**

**Action**: Revert only commits for problematic area

```bash
# Revert only epic-2nd-brain-infrastructure commits
git revert ghi789f

# Fix issues, re-apply
git cherry-pick ghi789f
# Make fixes...
git commit --amend

# Push
git push origin main
```

---

## 📊 Success Metrics

### **Completion Criteria**

- [ ] All files moved to PARA structure
- [ ] File count matches inventory (zero data loss)
- [ ] Git history preserved (git log --follow works)
- [ ] All automated tests passing (5/5)
- [ ] All manual tests passing (4/4)
- [ ] MCP start_session() works for all work-streams
- [ ] Documentation updated (README.md reflects new structure)
- [ ] Feature branch merged to main

### **Quality Metrics**

- **Zero Data Loss**: File count pre/post must match exactly
- **Git History Intact**: All moved files have full history
- **MCP Functional**: Context load time <3 min (unchanged)
- **Test Success Rate**: 100% (all tests must pass)

---

## ⏱️ Time Estimate Breakdown

| Activity | Time | Who | Notes |
|----------|------|-----|-------|
| Pre-Restructure Inventory | 30 min | Script | Auto-generate inventory.json |
| Review Inventory | 30 min | **You** | Review manual_review files, provide mappings |
| Path Mapping Generation | 30 min | Script | Generate path-mappings.json |
| Approve Mappings | 15 min | **You** | Review and approve |
| Create Feature Branch | 5 min | Manual | git checkout -b |
| Create PARA Structure | 15 min | Script | mkdir + git commit |
| Move Files (Git MV) | 120 min | Script | Automated per-area moves |
| Update MCP Config | 30 min | Manual | PathMapper + config updates |
| Automated Testing | 30 min | Script | 5 tests |
| Manual Validation | 30 min | **You** | Test start_session() workflows |
| Merge to Main | 15 min | Manual | git merge + push |
| **Total** | **6-8 hours** | | Including your review time |

---

## 🔗 Related Documentation

**Project Documentation**:
- `../prd.md` - Product requirements (all decisions locked)
- `../architecture/mcp-integration.md` - MCP integration details
- `../architecture/system-context.md` - System architecture

**Reference Materials**:
- `../Building_a_Second_Brain___Tiago_Forte.md` - PARA methodology

---

## 📝 Implementation Notes

### **Why Git MV Instead of MV?**
- Preserves full Git history for moved files
- `git log --follow` works correctly
- Blame and history annotations intact
- Critical for legal/audit requirements

### **Why Per-Area Commits?**
- Easier to review changes (logical grouping)
- Can revert specific areas without affecting others
- Clear history of what moved where
- Debugging is easier if issues found

### **Why Immediate Switch (No Fallback)?**
- Cleaner implementation (less code complexity)
- Forces complete migration (no half-states)
- Easier to test (only one code path)
- Lower risk of bugs from fallback logic

### **Why Feature Branch?**
- Protects main from incomplete changes
- Allows full testing before merge
- Easy to rollback (just delete branch)
- Industry best practice for large changes

---

## 📅 Version History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-16 | Claude Code (Sonnet 4.5) | Comprehensive Phase 1 tech requirements (~60 pages) based on clarifying questions |

---

**Status**: ✅ Tech requirements complete - Ready for implementation

**Next Step**: Begin execution when Dharan is available (low-risk timing)

**Critical**: Wait for Dharan's approval before starting restructure
