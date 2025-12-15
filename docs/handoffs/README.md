# Claude Code ↔ Claude Chat Handoffs

**Purpose**: Cross-agent communication for seamless workflow transitions

---

## 📋 Handoff Workflow

### 1. **Create** (Claude Chat)
When user approves PRD or completes strategic planning:
```yaml
---
to: claude-code
from: claude-chat
initiative_id: abc123
initiative_name: "Feature Name"
prd_path: "docs/prd/feature-name.md"
created: 2025-12-15T10:30:00
status: pending
priority: high
---

# Handoff: Feature Name

## Context
User approved PRD for Feature Name project.

## Next Steps for Claude Code
1. Read PRD at docs/prd/feature-name.md
2. Design architecture
3. Create tech requirements

## Success Criteria
- Architecture diagram created
- Tech requirements documented
- Ready for implementation
```

### 2. **Detect** (Claude Code)
On session start, Claude Code checks `docs/handoffs/` for pending handoffs:
```
Found handoff: Feature Name (from Claude Chat, 2 hours ago)
Priority: high

Next steps:
- Read PRD
- Design architecture  
- Create tech requirements

Load this initiative? [Yes/No/Later]
```

### 3. **Accept** (Claude Code)
User confirms handoff:
- Claude Code loads PRD automatically
- Reads initiative context
- Starts implementation phase
- Marks handoff status: `pending` → `accepted`

### 4. **Archive** (Auto)
After initiative completion:
- Handoff moved to `archive/YYYY/QQ/`
- Status updated: `accepted` → `completed`

---

## 📁 File Naming Convention

**Format**: `YYYY-MM-DD-to-{agent}-{topic-slug}.md`

**Examples**:
- `2025-12-15-to-claude-code-architecture-build.md`
- `2025-12-14-to-claude-chat-prd-review.md`

---

## 🎯 Handoff Types

### Claude Chat → Claude Code
**Trigger**: PRD approval, architecture planning complete
**Purpose**: Transition from strategy to implementation
**Contains**: PRD path, initiative context, implementation next steps

### Claude Code → Claude Chat
**Trigger**: Implementation blockers, design questions, PRD updates needed
**Purpose**: Escalate to strategic decision-making
**Contains**: Blocker description, options analysis, questions for user

---

## 🔍 Discovery

Claude Code auto-detects handoffs on `start_session()`:
- Scans `docs/handoffs/` for pending files
- Sorted by priority (high → medium → low)
- Shows most recent first (if multiple)

---

## ⚙️ MCP Tool Reference

```python
# Create handoff (Claude Chat)
create_handoff(
    to_agent="claude-code",
    from_agent="claude-chat",
    initiative_id="abc123",
    initiative_name="Feature Name",
    prd_path="docs/prd/feature-name.md",
    context="User approved PRD...",
    next_steps="1. Read PRD\n2. Design architecture..."
)

# Detect handoffs (Claude Code)
detect_handoffs(project="Epic 2nd Brain")
# Returns: List of pending handoffs with metadata

# Accept handoff (Claude Code)
accept_handoff(handoff_path="docs/handoffs/2025-12-15-to-claude-code-feature.md")
# Returns: Initiative context, updates status to "accepted"
```

---

## 📝 Notes

- **Created**: 2025-12-15 (Phase 7 infrastructure)
- **Related PRD**: [live-context-control-v3.md](../prd/live-context-control-v3.md)
- **Implementation**: See [handoff_detector.py](../../mcp_server/utils/handoff_detector.py)
