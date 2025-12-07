# Handoff YAML Frontmatter Specification

**Version**: 1.0
**Date**: 2025-12-06
**Purpose**: Standardize handoffs between Claude Chat and Claude Code

---

## Overview

Handoff files use YAML frontmatter to encode metadata about context transfers between agents. This enables automatic detection, validation, and context loading.

---

## YAML Frontmatter Schema

### Required Fields

```yaml
---
to: claude-code | claude-chat
from: claude-code | claude-chat
initiative_id: string          # Notion page ID from Strategy Board
prd_path: string               # Relative path to PRD (e.g., docs/prd/feature.md)
priority: P0 | P1 | P2 | P3    # Priority level
type: string                   # Handoff type (see types below)
status: pending | accepted | rejected | completed
---
```

### Optional Fields

```yaml
one_pager_url: string          # Notion URL or repo path to one-pager
tech_requirements_path: string # Path to tech requirements doc
context_files: list            # Additional files to load
  - docs/context/architecture.md
  - docs/sessions/prior-session.md
estimated_hours: number        # Estimated work (for planning)
deadline: YYYY-MM-DD           # Target completion date
notes: string                  # Additional context or instructions
```

---

## Handoff Types

| Type | Description | Direction | Typical Use Case |
|------|-------------|-----------|------------------|
| `implementation` | PRD → Code | Chat → Code | "Build this feature per PRD" |
| `validation` | Code → Review | Code → Chat | "Review implementation, validate against requirements" |
| `decision` | Context → Strategic decision | Code → Chat | "Need decision on architecture approach" |
| `research` | Question → Analysis | Either | "Research customer pain points" |
| `bug-fix` | Bug report → Fix | Either | "Fix critical bug in authentication" |

---

## Status Lifecycle

```
pending → accepted → completed
    ↓
rejected
```

- **pending**: Handoff created, awaiting agent to pick up
- **accepted**: Agent acknowledged, working on handoff
- **rejected**: Agent declined (with reason in notes)
- **completed**: Work finished, handoff closed

---

## File Naming Convention

**Format**: `YYYY-MM-DD-to-{agent}-{slug}.md`

**Examples**:
- `2025-12-06-to-claude-code-implement-rag-search.md`
- `2025-12-05-to-claude-chat-review-architecture.md`

**Location**: `docs/handoffs/` (Epic 2nd Brain repo)

---

## Example Handoff Files

### Example 1: Implementation Handoff (Chat → Code)

**File**: `docs/handoffs/2025-12-06-to-claude-code-implement-rag-search.md`

```markdown
---
to: claude-code
from: claude-chat
initiative_id: 2a68369c7305802ebbe6c355a80d65e5
prd_path: docs/prd/rag-separate-repos.md
priority: P1
type: implementation
status: pending
one_pager_url: https://notion.so/rag-separate-repos-one-pager
tech_requirements_path: docs/tech-requirements/live-context-control-v3.md
context_files:
  - docs/config/rag-repos.json
  - docs/sessions/claude-chat/2025-12-05-rag-architecture-decisions.md
estimated_hours: 16
deadline: 2025-12-13
notes: Privacy-first RAG with separate ChromaDB collections. See tech requirements for architecture details.
---

# Handoff: Implement RAG Separate Repos

## Context

PRD approved for privacy-first RAG with separate collections for Legacy AI and Epic 2nd Brain.

## What to Build

1. Base RAG class with abstract interface
2. Legacy AI RAG implementation (customer research)
3. Epic 2nd Brain RAG implementation (infrastructure docs)
4. MCP tools: search_legacy_ai() and search_epic_2nd_brain()

## Success Criteria

- Separate ChromaDB collections (no data leakage)
- Hybrid search: BM25 + semantic + BGE reranking
- Test suite validates privacy isolation

## Files to Create

- `mcp_server/rag/base_rag.py`
- `mcp_server/rag/legacy_ai_rag.py`
- `mcp_server/rag/epic_2nd_brain_rag.py`
- `tests/test_rag_separation.py`

## Open Questions

None - architecture decided in previous session.
```

---

### Example 2: Validation Handoff (Code → Chat)

**File**: `docs/handoffs/2025-12-06-to-claude-chat-review-phase-6.md`

```markdown
---
to: claude-chat
from: claude-code
initiative_id: 2a68369c7305802ebbe6c355a80d65e5
prd_path: docs/prd/rag-separate-repos.md
priority: P1
type: validation
status: pending
context_files:
  - docs/sessions/claude-code/2025-12-06-phase-6-rag-completion.md
  - mcp_server/rag/legacy_ai_rag.py
  - mcp_server/rag/epic_2nd_brain_rag.py
estimated_hours: 1
notes: Phase 6 RAG implementation complete. Please validate against PRD requirements.
---

# Handoff: Review Phase 6 RAG Implementation

## What Was Built

- Privacy-first RAG with isolated ChromaDB collections
- Legacy AI RAG: customer interviews, analyses, product docs
- Epic 2nd Brain RAG: PRDs, tech requirements, sessions
- MCP tools with error handling

## Validation Checklist

- [ ] Separate collections verified (no cross-project data)
- [ ] Hybrid search working (BM25 + semantic + BGE)
- [ ] MCP tools integrated correctly
- [ ] Test suite passes
- [ ] Documentation complete

## Files Changed

See `docs/sessions/claude-code/2025-12-06-phase-6-rag-completion.md` for details.

## Next Steps

If validation passes:
1. Merge feature branch to main
2. Update Strategy Board status to ✅ Complete
3. Move to Phase 7 (File-based handoffs)
```

---

### Example 3: Decision Handoff (Code → Chat)

**File**: `docs/handoffs/2025-12-06-to-claude-chat-decide-reranking-model.md`

```markdown
---
to: claude-chat
from: claude-code
initiative_id: 2a68369c7305802ebbe6c355a80d65e5
prd_path: docs/prd/rag-separate-repos.md
priority: P2
type: decision
status: pending
estimated_hours: 0.5
notes: Need decision on BGE reranker model - local vs API trade-offs
---

# Decision Needed: BGE Reranking Model

## Context

Implementing RAG search with reranking. Two options for reranking model.

## Option A: Local BGE Reranker (BAAI/bge-reranker-base)

**Pros**:
- Privacy-preserved (runs locally)
- No API costs
- Fast (<100ms for 20 results)

**Cons**:
- Requires downloading 1GB model
- Needs sentence-transformers dependency

## Option B: OpenAI Reranking API

**Pros**:
- No model download
- Always up-to-date
- No local compute

**Cons**:
- Privacy concern (sends docs to OpenAI)
- API costs (~$0.0001 per query)
- Latency (200-400ms)

## Recommendation

**Option A (Local BGE)** - Privacy-first aligns with project goals.

## Decision Required

Which option should we use?
```

---

## Validation Rules

When parsing handoff YAML, validators should check:

1. **Required fields present**: to, from, initiative_id, prd_path, priority, type, status
2. **Valid enum values**:
   - `to/from`: claude-code, claude-chat
   - `priority`: P0, P1, P2, P3
   - `status`: pending, accepted, rejected, completed
3. **Valid paths**: Files referenced in paths must exist (or note if not)
4. **Valid initiative_id**: 32-char Notion page ID format
5. **Date format**: Deadlines use YYYY-MM-DD

---

## Handoff Workflow

### Creating a Handoff (Claude Chat)

1. Generate handoff file with YAML frontmatter
2. Write to `docs/handoffs/YYYY-MM-DD-to-{agent}-{slug}.md`
3. Set status: `pending`
4. Commit to git

### Detecting a Handoff (Claude Code start_session)

1. Scan `docs/handoffs/` for files with `to: claude-code` and `status: pending`
2. Parse YAML frontmatter
3. Display handoff summary to user
4. Prompt: "Accept this handoff? (Y/N)"
   - If Y: Set status to `accepted`, load PRD + context files
   - If N: Set status to `rejected`, log reason

### Completing a Handoff (Claude Code end_session)

1. Mark handoff status: `completed`
2. Update Notion Strategy Board if initiative_id provided
3. Create reverse handoff if validation needed (Code → Chat)

---

## Integration with MCP Tools

### start_session()

```python
# On session start, check for pending handoffs
handoffs = scan_for_handoffs(agent="claude-code", status="pending")

if handoffs:
    print(f"Found {len(handoffs)} pending handoff(s):")
    for handoff in handoffs:
        print(f"  - {handoff['type']}: {handoff['summary']}")
        print(f"    PRD: {handoff['prd_path']}")
        print(f"    Priority: {handoff['priority']}")

    # User chooses which to accept
    # Load PRD + context files automatically
```

### end_session()

```python
# Optionally create handoff when ending session
end_session(
    create_handoff=True,
    handoff_to="claude-chat",
    handoff_type="validation",
    handoff_notes="Phase 6 complete, please validate"
)
```

---

## Security Considerations

1. **No secrets in handoffs**: Never include API keys, tokens, or credentials
2. **Sanitize file paths**: Validate all paths are within repo
3. **Validate initiative_id**: Confirm exists in Notion before loading
4. **Git-tracked**: All handoffs committed to version control

---

## Future Enhancements

- **Multi-agent support**: Extend beyond Claude Chat/Code
- **Priority queue**: Auto-sort by P0 > P1 > P2 > P3
- **Deadline alerts**: Warn if handoff approaching deadline
- **Handoff history**: Track all handoffs for analytics

---

**Last Updated**: 2025-12-06
**Status**: Specification Complete
