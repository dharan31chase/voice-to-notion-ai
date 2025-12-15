# Archived PRDs

Completed Product Requirement Documents organized by completion quarter.

---

## 📁 Structure

```
archive/
├── 2025/
│   ├── Q1/ (Jan-Mar 2025)
│   ├── Q2/ (Apr-Jun 2025)
│   ├── Q3/ (Jul-Sep 2025)
│   └── Q4/ (Oct-Dec 2025)
└── 2026/
    └── ...
```

---

## 🔄 Auto-Archival

PRDs are **automatically archived** when:
1. Initiative marked "✅ Complete" in Notion Strategy Board
2. `end_session()` called for that initiative
3. PRD moved from `docs/prd/` to `docs/prd/archive/YYYY/QQ/`

Quarter determined by completion date:
- Q1: Jan-Mar
- Q2: Apr-Jun
- Q3: Jul-Sep
- Q4: Oct-Dec

---

## 🔍 Search Behavior

Archived PRDs are **still searchable** but with lower priority:
- `search_epic_2nd_brain(query)` searches both active + archive
- Archive results ranked lower than active docs
- Useful for historical reference, pattern analysis

---

## 📊 Why Archive?

**Benefits**:
- Clean active folder (only in-progress docs)
- Historical record of completed work
- Pattern analysis (search "completed auth PRDs Q4 2025")
- Performance (smaller active folder, faster search)

**Note**: Archival ≠ deletion. All docs remain searchable and accessible.

---

## 🛠️ Manual Archival

If auto-archival didn't work:

```python
from mcp_server.utils.archival import archive_file
from pathlib import Path

prd_path = Path("docs/prd/my-feature.md")
result = archive_file(prd_path, force=True)
# Moved to: docs/prd/archive/2025/Q4/my-feature.md
```

---

**Created**: 2025-12-15 (Phase 1 infrastructure)
