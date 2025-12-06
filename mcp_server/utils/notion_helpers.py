"""
Notion Helper Functions

Provides utilities for Notion API interactions:
- Markdown to Notion blocks conversion
- Handoff template generation
"""

from datetime import datetime
from typing import List


def markdown_to_notion_blocks(content: str) -> list:
    """
    Convert markdown to Notion blocks (simple V1 implementation).

    Supports:
    - Headings (# ## ###)
    - Paragraphs
    - Bulleted lists (- or *)
    - Code blocks (```)

    Does NOT support (V1 limitation):
    - Tables
    - Images
    - Embeds

    Args:
        content: Markdown content

    Returns:
        List of Notion block objects
    """
    blocks = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Heading 1
        if line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                }
            })
            i += 1

        # Heading 2
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]
                }
            })
            i += 1

        # Heading 3
        elif line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]
                }
            })
            i += 1

        # Bulleted list
        elif line.strip().startswith("- ") or line.strip().startswith("* "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": line.strip()[2:].strip()}}]
                }
            })
            i += 1

        # Code block
        elif line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)}}],
                    "language": "plain text"
                }
            })
            i += 1

        # Paragraph (default)
        else:
            if line.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line.strip()}}]
                    }
                })
            i += 1

    return blocks


def generate_handoff_template(
    summary: str,
    decisions: List[str],
    next_steps: List[str],
    prd_path: str,
    one_pager_location: str,
    initiative_id: str
) -> str:
    """
    Generate standardized handoff prompt for Claude Code.

    Template structure:
    1. Git commands (at top)
    2. Implementation mode (INTERACTIVE)
    3. What to build (goals, success criteria)
    4. Documents to reference (PRD, one-pager)
    5. High-level context
    6. Clarifying questions

    Args:
        summary: Brief summary of what to build
        decisions: List of decisions made
        next_steps: List of next steps
        prd_path: Path to PRD file
        one_pager_location: Notion URL or repo path to one-pager
        initiative_id: Notion page ID for initiative

    Returns:
        Formatted handoff markdown content
    """
    # Generate topic for branch name
    topic = summary.lower().replace(" ", "-")[:30]
    topic = "".join(c for c in topic if c.isalnum() or c == "-")

    # Format decisions and next steps
    decisions_text = "\n".join(f"{i}. {d}" for i, d in enumerate(decisions, 1)) if decisions else "None documented"
    next_steps_text = "\n".join(f"{i}. {s}" for i, s in enumerate(next_steps, 1)) if next_steps else "See PRD for details"

    template = f"""# Handoff to Claude Code: {summary}

**Date**: {datetime.now().strftime("%Y-%m-%d")}
**From**: Claude Chat (Sonnet 4.5)
**To**: Claude Code
**Project**: Epic 2nd Brain

---

## 🚀 Git Commands - RUN THESE FIRST

```bash
# Navigate to repo
cd ~/Documents/1.\\ Projects/ai-assistant/

# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/{topic}

# Commit session log and handoff
git add docs/sessions/claude-chat/* docs/handoffs/*
git commit -m "feat: {summary}

Ref: Notion Strategy Board initiative"

# Push to remote
git push origin feature/{topic}
```

---

## 🎯 Implementation Mode: INTERACTIVE

**CRITICAL**: This is an **interactive implementation**, not autonomous coding.

**Your protocol**:
1. Read the PRD and one-pager thoroughly
2. Present **2-3 architectural options** for each major decision
3. **Wait for Dharan's choice** before proceeding
4. Only after alignment, create tech requirements
5. Only after tech requirements approved, start coding
6. After coding complete, **update documentation** (roadmap, tech req, implementation plan)

---

## 📋 What to Build

**Summary**: {summary}

**Decisions Made**:
{decisions_text}

**Next Steps**:
{next_steps_text}

---

## 📚 Documents to Reference

**Primary Documents**:
- **PRD**: `{prd_path}`
- **One-Pager**: `{one_pager_location}` (Notion URL or repo path)
- **Notion Initiative**: `https://www.notion.so/{initiative_id}`

---

## 🔑 High-Level Context

This handoff was generated from Claude Chat after PRD approval. The Strategy Board initiative has been updated to "🚀 In Progress".

**Why This Matters**:
- Aligns with current priorities (from Strategy Board)
- PRD reviewed and approved
- One-pager provides strategic context

---

## ❓ Clarifying Questions Before You Code

Before creating tech requirements, ask Dharan these questions:

1. **Tool Configurability**: Should new tools have hardcoded defaults or configurable parameters?
2. **Error Handling Strategy**: Fail-fast or retry with backoff when external APIs fail?
3. **Testing Strategy**: Mock external dependencies or test with real services?
4. **Integration Assumptions**: Any assumptions about git hooks, dependencies, or existing systems?
5. **Performance vs Simplicity**: Any trade-offs to discuss (e.g., sequential vs parallel processing)?

---

## 📝 Next Steps

1. Read PRD and one-pager thoroughly
2. Ask clarifying questions above
3. Create tech requirements document
4. Get approval on tech requirements
5. Implement features
6. Update documentation (roadmap, tech req, implementation plan)
7. Create session log and commit

---

**End of Handoff Prompt**
"""

    return template
