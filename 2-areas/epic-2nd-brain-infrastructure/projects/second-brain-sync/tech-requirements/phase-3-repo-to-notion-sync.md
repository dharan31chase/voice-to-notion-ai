# Tech Requirements: Phase 3 - Repo → Notion Sync (PRDs Only)

**Phase**: 3 of 6
**Estimated Time**: 2-3 hours (reduced from 4-6h due to scope reduction)
**Priority**: P2 (was P1, reduced - nice-to-have dashboard visibility)
**Dependencies**: Phase 1 (PARA Restructure) must be complete

---

## 🎯 Goal

Implement one-way Git → Notion sync for PRDs only, allowing mobile dashboard visibility while keeping Git as source of truth. Manual opt-in per file (sync_to_notion flag), manual organization in Notion.

**Scope Reduction**:
- ✅ Keep: PRDs only
- ❌ Remove: Session logs (handled by commit workflow)
- ❌ Remove: Tech requirements sync
- ❌ Remove: Decision logs sync

---

## ✅ Success Criteria

**Functional Requirements**:
- [ ] PRDs with `sync_to_notion: true` sync to Notion Notes database
- [ ] Notion pages created with: Title, Note Type (📝PRD), Source Path
- [ ] `notion_page_id` written back to frontmatter after first sync
- [ ] Cron runs at 1am/1pm, syncs marked files automatically
- [ ] 95%+ sync success rate

**Quality Requirements**:
- [ ] Idempotent: Running sync twice = same result
- [ ] No duplicate pages created
- [ ] Error handling: Rate limits, API failures, invalid frontmatter
- [ ] Sync logs written for debugging

**Non-Goals** (explicitly out of scope):
- ❌ Automatic tagging to Projects/Areas (Dharan does manually)
- ❌ Bidirectional sync (this is ONE-WAY: Git → Notion)
- ❌ Syncing other document types (only PRDs for now)

---

## 🏗️ Technical Approach

### **Step 1: Configuration Setup** (30 min)

Create `sync_config.json` in each repo's `resources/` folder:

**File**: `ai-assistant/resources/sync_config.json`
```json
{
  "repo_to_notion": {
    "enabled": true,
    "notes_database_id": "${NOTION_NOTES_DATABASE_ID}",
    "note_types": {
      "📝PRD": {
        "enabled": true,
        "description": "Product Requirements Documents"
      },
      "Vision Document": {
        "enabled": false,
        "description": "Future: Vision docs (not implemented yet)"
      },
      "Pitch Document": {
        "enabled": false,
        "description": "Future: Pitch docs (not implemented yet)"
      },
      "Roadmap": {
        "enabled": false,
        "description": "Future: Roadmap docs (not implemented yet)"
      }
    },
    "sync_schedule": {
      "cron": "0 1,13 * * *",
      "enabled": true
    }
  }
}
```

**File**: `legacy-ai/resources/sync_config.json` (same structure)

**Why per-repo config**:
- Each repo can enable/disable repo→notion sync independently
- Different repos might have different note types enabled
- Easier to manage than global config

---

### **Step 2: Frontmatter Design** (15 min)

**Standard PRD Frontmatter**:
```yaml
---
title: Second Brain Sync
sync_to_notion: true  # Manual flag - Dharan controls what syncs
notion_note_type: 📝PRD  # Must match Notion "Note Type" values EXACTLY
notion_page_id: null  # Auto-filled after first sync (Notion page ID)
last_synced: null  # Auto-updated (ISO timestamp)
---
```

**Field Specifications**:
- `sync_to_notion`: Boolean, default false, Dharan adds manually when ready
- `notion_note_type`: String, must match Notion database values (case + emoji sensitive)
- `notion_page_id`: String (UUID), null until first sync, then persisted
- `last_synced`: ISO 8601 timestamp (e.g., "2025-12-16T14:30:00Z")

**Validation**:
- If `sync_to_notion: true` but `notion_note_type` missing → ERROR (skip file, log warning)
- If `notion_note_type` not in enabled list → ERROR (skip file, log warning)
- If frontmatter parse fails → ERROR (skip file, log warning)

---

### **Step 3: Sync Script Implementation** (60 min)

**File**: `ai-assistant/resources/repo_to_notion_sync.py`

**Core Logic**:
```python
#!/usr/bin/env python3
"""
Repo → Notion Sync (PRDs only)
Syncs markdown files with sync_to_notion: true to Notion Notes database.
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from notion_client import Client

# Load config
def load_config():
    config_path = Path(__file__).parent / "sync_config.json"
    with open(config_path) as f:
        config = json.load(f)

    # Substitute env vars
    notes_db_id = os.getenv("NOTION_NOTES_DATABASE_ID")
    config["repo_to_notion"]["notes_database_id"] = notes_db_id

    return config

# Find files to sync
def find_syncable_files(repo_root):
    """Find all .md files with sync_to_notion: true"""
    syncable = []

    for md_file in Path(repo_root).rglob("*.md"):
        try:
            content = md_file.read_text()

            # Extract frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])

                    # Check if sync enabled
                    if frontmatter.get("sync_to_notion") == True:
                        syncable.append({
                            "path": md_file,
                            "frontmatter": frontmatter,
                            "body": parts[2].strip()
                        })
        except Exception as e:
            print(f"⚠️  Error reading {md_file}: {e}")
            continue

    return syncable

# Sync to Notion
def sync_to_notion(file_info, config, notion_client):
    """Create or update Notion page"""

    frontmatter = file_info["frontmatter"]

    # Validate
    note_type = frontmatter.get("notion_note_type")
    if not note_type:
        print(f"❌ Missing notion_note_type in {file_info['path']}")
        return False

    if note_type not in config["repo_to_notion"]["note_types"]:
        print(f"❌ Unknown note_type '{note_type}' in {file_info['path']}")
        return False

    if not config["repo_to_notion"]["note_types"][note_type]["enabled"]:
        print(f"⏭️  Skipping {note_type} (disabled in config)")
        return False

    # Get relative path
    repo_root = Path(__file__).parent.parent
    relative_path = file_info["path"].relative_to(repo_root)

    # Check if page exists
    page_id = frontmatter.get("notion_page_id")

    properties = {
        "Title": {"title": [{"text": {"content": frontmatter["title"]}}]},
        "Note Type": {"multi_select": [{"name": note_type}]},
        "Source Path": {"rich_text": [{"text": {"content": str(relative_path)}}]}
    }

    try:
        if page_id:
            # Update existing page
            notion_client.pages.update(page_id=page_id, properties=properties)
            print(f"✅ Updated: {frontmatter['title']}")
        else:
            # Create new page
            response = notion_client.pages.create(
                parent={"database_id": config["repo_to_notion"]["notes_database_id"]},
                properties=properties,
                children=markdown_to_blocks(file_info["body"])
            )
            page_id = response["id"]

            # Write page_id back to frontmatter
            update_frontmatter(file_info["path"], page_id)

            print(f"✅ Created: {frontmatter['title']}")

        return True

    except Exception as e:
        print(f"❌ Failed to sync {frontmatter['title']}: {e}")
        return False

# Markdown to Notion blocks
def markdown_to_blocks(markdown_body):
    """Convert markdown to Notion blocks (SIMPLIFIED)"""
    # TODO: Full markdown parsing (headings, lists, code blocks)
    # For now: Just paragraph blocks

    blocks = []
    for line in markdown_body.split("\n\n"):
        if line.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line.strip()}}]
                }
            })

    return blocks

# Update frontmatter with notion_page_id
def update_frontmatter(file_path, page_id):
    """Write notion_page_id back to frontmatter"""
    content = file_path.read_text()

    if content.startswith("---"):
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])

        # Update fields
        frontmatter["notion_page_id"] = page_id
        frontmatter["last_synced"] = datetime.utcnow().isoformat() + "Z"

        # Write back
        updated = f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n{parts[2]}"
        file_path.write_text(updated)

# Main
def main():
    config = load_config()

    if not config["repo_to_notion"]["enabled"]:
        print("ℹ️  Repo → Notion sync disabled in config")
        return

    notion_client = Client(auth=os.getenv("NOTION_API_KEY"))
    repo_root = Path(__file__).parent.parent

    print("🔍 Scanning for syncable files...")
    files = find_syncable_files(repo_root)
    print(f"📄 Found {len(files)} files with sync_to_notion: true")

    success = 0
    failed = 0

    for file_info in files:
        if sync_to_notion(file_info, config, notion_client):
            success += 1
        else:
            failed += 1

    print(f"\n✅ Synced: {success}")
    print(f"❌ Failed: {failed}")

if __name__ == "__main__":
    main()
```

**Dependencies**:
- `notion-client` (already installed)
- `pyyaml` (already installed)

---

### **Step 4: Cron Safety Wrapper** (30 min)

**Problem**: Mac in backpack can overheat if cron runs while lid is closed.

**Solution**: Wrapper script checks lid state + AC power before running sync.

**File**: `ai-assistant/resources/safe_cron_wrapper.sh` (reuse from Phase 4)
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
chmod +x legacy-ai/resources/safe_cron_wrapper.sh  # Copy to legacy-ai too
```

---

### **Step 5: Mac Wake Schedule (pmset)** (15 min)

**Configure Mac to wake before cron jobs** (only when on AC power):

```bash
# Wake Mac before cron jobs (only when AC power + lid open)
sudo pmset -c repeat wake MTWRFSU 00:55:00  # Before 1am sync
sudo pmset -c repeat wake MTWRFSU 12:55:00  # Before 1pm sync

# -c flag = only wake when connected to AC power (prevents battery drain)
# MTWRFSU = Monday through Sunday
```

**Verify configuration**:
```bash
pmset -g sched
# Should show: wake at 00:55:00 and 12:55:00
```

**Why this works**:
- Mac wakes at 12:55pm/00:55am (if on AC power)
- Cron runs at 1:00pm/1:00am
- Wrapper checks lid state (if closed → skip)
- If in backpack on battery → Mac doesn't wake, cron doesn't run ✅

**Trade-off accepted**: If traveling 3+ days without opening laptop, sync waits until back home.

---

### **Step 6: Cron Setup** (15 min)

**Crontab Entry (Updated with Safety Wrapper)**:
```bash
# Repo → Notion Sync (1am and 1pm daily with safety checks)
0 1,13 * * * /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/resources/safe_cron_wrapper.sh /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/resources/repo_to_notion_sync.py /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/resources/logs/repo_to_notion_sync.log

0 1,13 * * * /Users/dharanchandrahasan/Documents/1.\ Projects/legacy-ai/resources/safe_cron_wrapper.sh /Users/dharanchandrahasan/Documents/1.\ Projects/legacy-ai/resources/repo_to_notion_sync.py /Users/dharanchandrahasan/Documents/1.\ Projects/legacy-ai/resources/logs/repo_to_notion_sync.log
```

**Log Rotation** (optional):
```bash
# Keep last 30 days of sync logs
find /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/resources/logs/repo_to_notion_sync.log -mtime +30 -delete
find /Users/dharanchandrahasan/Documents/1.\ Projects/legacy-ai/resources/logs/repo_to_notion_sync.log -mtime +30 -delete
```

---

## 📋 Data Structures

### **Frontmatter Schema**

```yaml
---
# REQUIRED for sync
title: string  # Document title
sync_to_notion: boolean  # Manual flag (default: false)
notion_note_type: string  # Must match Notion Note Type values

# AUTO-MANAGED (don't edit manually)
notion_page_id: string | null  # Notion page UUID
last_synced: string | null  # ISO 8601 timestamp

# OPTIONAL (not used by sync script)
created: string  # ISO 8601
author: string
status: string  # draft | active | archived
---
```

### **Config File Schema**

```json
{
  "repo_to_notion": {
    "enabled": boolean,
    "notes_database_id": string,  // Notion database UUID
    "note_types": {
      "[note_type_name]": {
        "enabled": boolean,
        "description": string
      }
    },
    "sync_schedule": {
      "cron": string,  // Cron expression
      "enabled": boolean
    }
  }
}
```

### **Sync Log Format**

```
2025-12-16 01:00:15 - INFO - Repo → Notion sync started
2025-12-16 01:00:16 - INFO - Found 3 files with sync_to_notion: true
2025-12-16 01:00:17 - SUCCESS - Created: Second Brain Sync PRD
2025-12-16 01:00:18 - SUCCESS - Updated: Live Context Control v3 PRD
2025-12-16 01:00:19 - ERROR - Missing notion_note_type: docs/prd/invalid.md
2025-12-16 01:00:20 - INFO - Synced: 2, Failed: 1
```

---

## 🔌 API Calls

### **Notion API Endpoints Used**

**1. Create Page** (when `notion_page_id` is null):
```python
notion_client.pages.create(
    parent={"database_id": NOTION_NOTES_DATABASE_ID},
    properties={
        "Title": {"title": [{"text": {"content": "PRD Title"}}]},
        "Note Type": {"multi_select": [{"name": "📝PRD"}]},
        "Source Path": {"rich_text": [{"text": {"content": "2-areas/..."}}]}
    },
    children=[...]  # Notion blocks
)
```

**2. Update Page** (when `notion_page_id` exists):
```python
notion_client.pages.update(
    page_id=notion_page_id,
    properties={...}  # Same as create
)
```

**Rate Limiting**:
- Notion API: 3 requests/second
- Mitigation: Add 350ms delay between requests
- Error handling: Exponential backoff on 429 errors

---

## ⚠️ Error Handling

### **Error Scenarios**

**1. Missing Frontmatter**:
- **Symptom**: File doesn't start with `---`
- **Action**: Skip file, log warning
- **Log**: `⚠️ No frontmatter found in [file_path]`

**2. Invalid YAML**:
- **Symptom**: `yaml.safe_load()` raises exception
- **Action**: Skip file, log error
- **Log**: `❌ Invalid YAML in [file_path]: [error]`

**3. Missing Required Fields**:
- **Symptom**: `sync_to_notion: true` but no `notion_note_type`
- **Action**: Skip file, log error
- **Log**: `❌ Missing notion_note_type in [file_path]`

**4. Unknown Note Type**:
- **Symptom**: `notion_note_type` not in config
- **Action**: Skip file, log error
- **Log**: `❌ Unknown note_type '[type]' in [file_path]`

**5. Notion API Rate Limit (429)**:
- **Symptom**: `notion_client` raises RateLimitError
- **Action**: Exponential backoff (1s, 2s, 4s, 8s), retry up to 3 times
- **Log**: `⚠️ Rate limited, retrying in [X]s...`

**6. Notion API Failure (500)**:
- **Symptom**: Notion server error
- **Action**: Skip file, log error, continue with next file
- **Log**: `❌ Notion API error for [file]: [error]`

**7. File Write Failure**:
- **Symptom**: Can't write `notion_page_id` back to frontmatter
- **Action**: Log error, page created but frontmatter not updated
- **Log**: `⚠️ Created page but failed to update frontmatter: [file]`

---

## 🧪 Testing Requirements

### **Unit Tests**

**Test Suite**: `tests/test_repo_to_notion_sync.py`

**Test 1: Frontmatter Parsing**
- Given: Markdown file with valid frontmatter
- When: `parse_frontmatter()` called
- Then: Returns dict with all fields

**Test 2: Find Syncable Files**
- Given: Repo with 3 .md files (2 with `sync_to_notion: true`, 1 without)
- When: `find_syncable_files()` called
- Then: Returns 2 files

**Test 3: Validate Note Type**
- Given: Config with `📝PRD` enabled, `Vision Document` disabled
- When: Validate file with `notion_note_type: 📝PRD`
- Then: Returns True
- When: Validate file with `notion_note_type: Vision Document`
- Then: Returns False

**Test 4: Update Frontmatter**
- Given: File with `notion_page_id: null`
- When: `update_frontmatter(file, "abc-123")` called
- Then: File contains `notion_page_id: abc-123` and `last_synced: [timestamp]`

---

### **Integration Tests**

**Test 5: Full Sync Flow (Mock Notion API)**
- Given: Test PRD with `sync_to_notion: true`
- When: Sync script runs (with mocked Notion API)
- Then:
  - Notion API `create_page()` called with correct properties
  - Frontmatter updated with `notion_page_id`
  - Log shows "✅ Created: [title]"

**Test 6: Update Existing Page**
- Given: Test PRD with existing `notion_page_id`
- When: Sync script runs
- Then:
  - Notion API `update_page()` called (not `create_page()`)
  - Log shows "✅ Updated: [title]"

**Test 7: Error Handling (Invalid Note Type)**
- Given: Test PRD with `notion_note_type: InvalidType`
- When: Sync script runs
- Then:
  - File skipped
  - Log shows "❌ Unknown note_type 'InvalidType'"

---

### **End-to-End Test**

**Test 8: Real Notion Sync (Manual)**
- Setup: Create test PRD in `ai-assistant/test-prd.md`
- Frontmatter:
  ```yaml
  ---
  title: Test PRD for Sync
  sync_to_notion: true
  notion_note_type: 📝PRD
  notion_page_id: null
  last_synced: null
  ---
  ```
- Run: `python3 resources/repo_to_notion_sync.py`
- Verify:
  - [ ] Page created in Notion Notes database
  - [ ] Title = "Test PRD for Sync"
  - [ ] Note Type = 📝PRD
  - [ ] Source Path = "test-prd.md"
  - [ ] Frontmatter updated with `notion_page_id` and `last_synced`
- Cleanup: Delete test PRD and Notion page

---

## 🔄 Rollback Plan

### **If Sync Script Fails**

**Symptom**: Script crashes, no pages created
**Impact**: Low (Git still source of truth, just no Notion visibility)

**Rollback Steps**:
1. Check sync logs: `tail -f logs/repo_to_notion_sync.log`
2. Identify error (invalid frontmatter, API auth, etc.)
3. Fix error, re-run script manually
4. No data loss (Git unchanged)

---

### **If Duplicate Pages Created**

**Symptom**: Multiple Notion pages for same PRD
**Impact**: Medium (Notion clutter, manual cleanup needed)

**Rollback Steps**:
1. Disable cron: Comment out crontab entries
2. Identify duplicates in Notion Notes database
3. Delete duplicates (keep most recent)
4. Fix script bug (likely `notion_page_id` not written back)
5. Re-enable cron after fix confirmed

---

### **If Frontmatter Corrupted**

**Symptom**: Git commit shows corrupted YAML in frontmatter
**Impact**: High (Git history polluted, file unreadable)

**Rollback Steps**:
1. Immediately disable cron
2. Revert Git commits: `git revert [bad_commit]`
3. Fix script bug (YAML serialization)
4. Test script on single file before re-enabling cron
5. Add pre-commit validation (YAML parse check)

---

## 📁 Files Changed

### **New Files Created**

```
ai-assistant/
├── resources/
│   ├── sync_config.json  # NEW: Config file
│   └── repo_to_notion_sync.py  # NEW: Sync script
└── logs/
    └── repo_to_notion_sync.log  # NEW: Sync logs

legacy-ai/
├── resources/
│   ├── sync_config.json  # NEW: Config file
│   └── repo_to_notion_sync.py  # NEW: Sync script (identical)
└── logs/
    └── repo_to_notion_sync.log  # NEW: Sync logs
```

### **Modified Files**

```
# Frontmatter updated in synced PRDs:
2-areas/epic-2nd-brain-infrastructure/projects/second-brain-sync/prd.md
docs/prd/live-context-control-v3.md
docs/prd/rag-implementation-legacy-ai.md
# (Any PRD with sync_to_notion: true)
```

### **Crontab**
```
# Modified: Add two cron entries for 1am/1pm sync
crontab -e
```

---

## ⏱️ Time Estimate Breakdown

| Activity | Time | Notes |
|----------|------|-------|
| Setup: Config files | 30 min | Create sync_config.json for both repos |
| Implementation: Sync script | 60 min | Core logic, frontmatter parsing, Notion API |
| Implementation: Markdown → Notion blocks | 30 min | SIMPLIFIED (just paragraphs for now) |
| Testing: Unit tests | 30 min | Frontmatter parsing, file discovery, validation |
| Testing: Integration tests | 30 min | Mock Notion API, full sync flow |
| Testing: E2E test | 15 min | Real Notion sync with test PRD |
| Setup: Cron | 15 min | Crontab entries, log rotation |
| Documentation: Update this doc | 15 min | Add learnings, update time estimates |
| **TOTAL** | **~3.5 hours** | |

**Optimistic**: 2 hours (if no issues)
**Realistic**: 3 hours
**Pessimistic**: 4 hours (if Notion API issues)

---

## 🤔 Open Questions for Dharan

### **Question 1: View-Only Callout?**

Should synced Notion pages have a callout at the top?

**Option A**: Add callout ⚠️
```
⚠️ View-only: Synced from repo
Source: 2-areas/epic-2nd-brain-infrastructure/projects/second-brain-sync/prd.md
Last synced: 2025-12-16 14:30
```
- **Pro**: Clear visual indicator, prevents accidental edits in Notion
- **Con**: Extra block clutter, you're organizing manually anyway

**Option B**: Skip callout
- **Pro**: Cleaner Notion pages
- **Con**: No visual indicator of sync status

**Recommendation**: **Option A** - Add callout for clarity. Even though you're organizing manually, the visual indicator prevents confusion about source of truth.

---

### **Question 2: Markdown → Notion Blocks Fidelity?**

Current implementation: SIMPLIFIED (just paragraphs)

**Option A**: Simple paragraphs (current)
- **Pro**: Fast to implement (30 min)
- **Con**: Loses formatting (headings, lists, code blocks)

**Option B**: Full markdown parsing (headings, lists, code blocks)
- **Pro**: Better fidelity, prettier Notion pages
- **Con**: Extra 2-3 hours implementation

**Recommendation**: **Option A** for Phase 3 - You can read formatted markdown in repo. Notion is just for mobile dashboard visibility. Add full parsing in future phase if needed.

---

### **Question 3: Sync Schedule?**

Current: 1am + 1pm daily (2x/day)

**Option A**: 2x/day (current)
- **Pro**: More frequent updates
- **Con**: More API usage

**Option B**: 1x/day (1am only)
- **Pro**: Less API usage
- **Con**: 24h delay for afternoon updates

**Recommendation**: **Option A** - 2x/day gives reasonable freshness without excessive API usage.

---

## ✅ Success Metrics

**Completion Criteria**:
- [ ] Config files created in both repos
- [ ] Sync script implemented and tested
- [ ] Cron jobs configured
- [ ] All tests passing (unit + integration + E2E)
- [ ] At least 1 PRD successfully synced to Notion
- [ ] Frontmatter auto-updated with `notion_page_id`

**Quality Metrics**:
- Sync success rate: ≥95%
- Sync duration: <10 seconds for typical workload (3-5 PRDs)
- Zero data loss (Git source of truth preserved)
- Zero duplicate pages created

---

## 🔗 Related Documentation

**Project Documentation**:
- `../prd.md` - Product requirements (all decisions locked)
- `../architecture/sync-engine.md` - Bidirectional sync architecture
- `phase-2-notion-to-repo-sync.md` - Notion → Repo sync (opposite direction)

**Reference Materials**:
- Notion API docs: https://developers.notion.com/reference/intro
- YAML frontmatter spec: https://jekyllrb.com/docs/front-matter/

---

## 📝 Implementation Notes

**Why per-repo scripts instead of global?**
- Each repo can have different sync behavior
- Easier to disable sync for one repo without affecting the other
- Simpler debugging (logs per repo)
- Future: Repos can diverge in sync logic if needed

**Why manual `sync_to_notion` flag?**
- Dharan controls what syncs (explicit opt-in)
- Prevents accidental sync of draft/WIP docs
- Easier to test (enable sync on test docs, verify, then enable on real docs)

**Why skip Project/Area relations?**
- Dharan organizes manually in Notion anyway
- Auto-tagging would require complex heuristics (error-prone)
- Simpler implementation = faster shipping

---

## 📅 Version History

| Date | Author | Changes |
|------|--------|---------|
| 2025-12-16 | Claude Code (Sonnet 4.5) | Initial Phase 3 tech requirements (simplified scope: PRDs only, manual organization) |

---

**Status**: ✅ Tech requirements complete - Ready for implementation

**Next Step**: Implement sync script after Phase 1 (PARA Restructure) complete
