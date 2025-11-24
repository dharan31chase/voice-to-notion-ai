# Epic 2nd Brain - Architecture Documentation

**Last Updated**: 2024-11-24
**Author**: Dharan + Claude (Systems Architecture Session)

---

## Overview

This folder contains systems architecture diagrams for the Epic 2nd Brain infrastructure, created using a hybrid approach:

- **Mermaid files** (`.mermaid.md`): Source of truth, version-controlled, readable by Claude Code
- **HTML visuals** (`visuals/`): Pretty renders for human viewing, generated from Mermaid concepts

## Diagram Hierarchy

```
Level 1: System Context (Executive View)
    └── "What is this thing?"
    └── Input → System → Output
    └── For: Quick understanding, stakeholder communication

Level 2: Container Architecture (Builder View)  
    └── "How do the pieces connect?"
    └── All components, interfaces, shared state
    └── For: Understanding the system as a builder

Level 3: Leverage Points (Decision View) [TODO]
    └── "Where should I invest next?"
    └── Same as Level 2 + friction/opportunity annotations
    └── For: Prioritizing improvements

Level 4: Component Details (Deep Dive) [TODO]
    └── "How does X subsystem work?"
    └── Zoom into individual subsystems
    └── For: Debugging, extending specific components
```

## Files

### Mermaid Source Files
| File | Purpose |
|------|---------|
| `system-context.mermaid.md` | Level 1 - Executive overview |
| `container-architecture.mermaid.md` | Level 2 - How pieces connect |
| `leverage-points.mermaid.md` | Level 3 - Where to invest (TODO) |
| `component-inventory.md` | Reference - Detailed code documentation |

### Visual HTML Files
| File | Purpose |
|------|---------|
| `visuals/system-overview.html` | Pretty render of Level 1 |
| `visuals/container-architecture.html` | Pretty render of Level 2 |
| `visuals/leverage-points.html` | Pretty render of Level 3 (TODO) |

## How to View

### HTML Files (Recommended for humans)
1. Open in browser: Double-click the `.html` file
2. Or from terminal: `open docs/architecture/visuals/system-overview.html`

### Mermaid Files (For Claude Code / GitHub)
1. GitHub renders `.mermaid.md` files automatically
2. VS Code with Mermaid extension
3. Paste into [Mermaid Live Editor](https://mermaid.live/)

## Maintenance

### When to Update
- New subsystem added
- Major architectural change
- New friction point identified
- After significant refactoring

### How to Update
1. Update the Mermaid source file first
2. Regenerate HTML visual (ask Claude Chat)
3. Commit both together

## Systems Thinking Integration

These diagrams are annotated with systems thinking concepts:

- **Stocks**: Where information accumulates (Notion, Git, RAG Index)
- **Flows**: How information moves (6 data flows documented)
- **Feedback Loops**: Virtuous and vicious cycles
- **Leverage Points**: Where small changes create big impact
- **Friction Points**: Where the system creates drag

See `Systems_Thinking_Workbook__Energy___Voice-to-Notion.md` in project files for the full framework.
