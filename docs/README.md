# Documentation Organization

**Last Updated**: 2025-12-15
**Phase 1 Infrastructure**: Active/Archive System

---

## 📁 Directory Structure

### Active Documents
Documents currently in progress (drafts, in-review, or actively referenced).

- `prd/active/` - Product Requirement Documents being worked on
- `tech-requirements/active/` - Technical requirement documents in progress
- `sessions/claude-chat/active/` - Recent Claude Chat session logs
- `sessions/claude-code/active/` - Recent Claude Code session logs

### Archive
Completed documents organized by year and quarter.

- `prd/archive/YYYY/QQ/` - Completed PRDs by quarter
- `tech-requirements/archive/YYYY/QQ/` - Completed tech specs by quarter
- `sessions/claude-{chat,code}/archive/YYYY/QQ/` - Historical session logs

### Handoffs
Cross-agent communication files (Claude Chat ↔ Claude Code).

- `handoffs/` - Pending handoff files
- `handoffs/archive/YYYY/QQ/` - Completed handoffs

See [handoffs/README.md](handoffs/README.md) for handoff workflow.

### Context
High-level context and reference documents.

- `context/one-pagers/infrastructure/` - Epic 2nd Brain infrastructure initiatives
- `context/one-pagers/legacy-ai/` - Legacy AI business initiatives

### Archive (Deprecated/Hold)
Documents no longer active but kept for reference.

- `archive/failed-experiments/` - Experiments that didn't pan out
- `archive/hold-for-later/` - Deferred initiatives
- `archive/context-engineering-research/` - Historical research

---

## 🔄 Archival Logic

Documents are **automatically archived** when:
- Initiative status changes to "✅ Complete" in Notion Strategy Board
- `end_session()` tool called for completed initiative
- PRD moved to `prd/archive/YYYY/QQ/` based on completion quarter

**Manual archival** available via:
- `archive_file(file_path, force=True)` utility function

---

## 🔍 Search Behavior

### Active Documents (High Priority)
- Searched first by default
- Higher relevance score in RAG semantic search
- Suggested more frequently in context profiles

### Archived Documents (Lower Priority)
- Still searchable (include_archive=True)
- Lower relevance score
- Suggested only if highly relevant

---

## 📊 Document Lifecycle

```
1. DRAFT → Created in active/
2. IN PROGRESS → Edited/refined in active/
3. COMPLETE → Auto-archived to archive/YYYY/QQ/
4. REFERENCE → Searchable from archive, low priority
```

---

## 🛠️ Tools Reference

- `search_epic_2nd_brain(query)` - Semantic search across all docs (active + archive)
- `list_files(project, path)` - Browse directory structure
- `archive_file(path, force=True)` - Manually archive a document
- `end_session(initiative_id)` - Auto-archive PRD if initiative complete

---

## 📝 Notes

- **Created**: 2025-12-15 (Phase 1 infrastructure setup)
- **Related PRD**: [live-context-control-v3.md](prd/live-context-control-v3.md)
- **Implementation**: See [archival.py](../mcp_server/utils/archival.py)
