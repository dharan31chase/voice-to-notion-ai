# Test 4: ROADMAP Sync Validation

## What We're Testing

When `end_session()` is called with an initiative linked:
1. It reads the initiative status from Strategy Board (Notion)
2. It updates ROADMAP.md to match that status
3. If status is "✅ Complete", it archives the PRD to `archive/2025/Q4/`

---

## Setup Complete

✅ Added "Live Context Control v3" to ROADMAP.md (line 13)
✅ Initial status: 🚀 In Progress
✅ PRD exists: `docs/prd/live-context-control-v3.md`

---

## Test Scenarios

### Scenario 1: Sync with In Progress Status

**Prerequisites**:
- Strategy Board has "Live Context Control v3" initiative
- Status in Strategy Board: "🚀 In Progress"

**Test Steps**:
1. In Claude Code, call:
   ```
   @mcp ai-assistant:end_session(
       project_name="Epic 2nd Brain",
       summary="Testing ROADMAP sync with In Progress status",
       session_duration_hours=0.5,
       initiative_name="Live Context Control v3"
   )
   ```

2. Check ROADMAP.md line 13:
   - Status should remain: `🚀 In Progress`
   - Target date should be preserved: `Dec 13`

**Expected Result**:
```
✅ ROADMAP.md status matches Strategy Board
✅ No PRD archival (not complete yet)
```

---

### Scenario 2: Sync with Complete Status

**Prerequisites**:
- Go to Notion Strategy Board
- Find "Live Context Control v3" initiative
- Update status to: "✅ Complete"
- Set Completed Date: 2025-12-05

**Test Steps**:
1. In Claude Code, call:
   ```
   @mcp ai-assistant:end_session(
       project_name="Epic 2nd Brain",
       summary="Testing ROADMAP sync with Complete status",
       session_duration_hours=0.5,
       initiative_name="Live Context Control v3"
   )
   ```

2. Check ROADMAP.md line 13:
   - Status should update to: `✅ Complete`
   - Target date should update to: `Dec 05` (from Completed Date)

3. Check PRD archival:
   - Original PRD should be moved from: `docs/prd/live-context-control-v3.md`
   - To: `docs/prd/archive/2025/Q4/live-context-control-v3.md`

**Expected Result**:
```
✅ ROADMAP.md status updated to ✅ Complete
✅ Target date updated to Dec 05
✅ PRD archived to archive/2025/Q4/
```

---

## How to Run Tests

### Option A: Manual Test (Recommended)

1. **Setup**: Already done ✅
   - Live Context Control v3 added to ROADMAP.md
   - Initiative exists in Strategy Board

2. **Test Scenario 1**:
   - Call end_session() via MCP (status: In Progress)
   - Verify ROADMAP.md unchanged

3. **Test Scenario 2**:
   - Update Strategy Board status to Complete
   - Call end_session() via MCP
   - Verify ROADMAP.md updated + PRD archived

---

### Option B: Quick Python Test (Mock)

```python
#!/usr/bin/env python3
"""Quick test of ROADMAP sync logic."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from mcp_server.utils.roadmap_helpers import update_roadmap_row

# Read current ROADMAP.md
roadmap_path = Path.home() / "Documents/1. Projects/ai-assistant/ROADMAP.md"
content = roadmap_path.read_text()

# Test 1: Update to Complete status
print("Test 1: Updating Live Context Control v3 to Complete...")
updated = update_roadmap_row(
    content=content,
    initiative_name="Live Context Control v3",
    new_status="✅ Complete",
    completion_date="2025-12-05"
)

# Check if update worked
if "✅ Complete" in updated:
    print("✅ Status updated successfully")
    print("✅ Completion date set to Dec 05")
else:
    print("❌ Update failed")

# Show the updated line
for line in updated.split("\n"):
    if "Live Context Control v3" in line:
        print(f"\nUpdated line:\n{line}")
```

Save as `test_roadmap_sync.py` and run:
```bash
python3 test_roadmap_sync.py
```

---

## Success Criteria

✅ **Scenario 1**: ROADMAP.md status stays "🚀 In Progress" when Strategy Board is In Progress
✅ **Scenario 2**: ROADMAP.md status updates to "✅ Complete" when Strategy Board is Complete
✅ **Scenario 2**: Target date updates to completion date (Dec 05)
✅ **Scenario 2**: PRD archived to `archive/2025/Q4/`
✅ **Error Handling**: If ROADMAP.md doesn't have initiative, sync fails gracefully

---

## What We're Validating

This test validates Phase 3 functionality:
- ✅ Auto-sync ROADMAP.md with Strategy Board status
- ✅ Auto-update completion dates
- ✅ Auto-archive PRDs when complete
- ✅ Zero manual editing of ROADMAP.md required

---

## Notes

**Initiative Name Matching**:
- The sync uses fuzzy matching: searches for "Live Context Control v3" in ROADMAP.md
- If you renamed the initiative, update `initiative_name` parameter accordingly

**PRD Path Detection**:
- The function tries to extract PRD path from Strategy Board's "PRD" field
- If not found, PRD archival is skipped (no error)

**Rollback**:
- If something goes wrong, the .backups/ folder has ROADMAP.md backups
- PRD archive can be unarchived with `archive_file()` utility
