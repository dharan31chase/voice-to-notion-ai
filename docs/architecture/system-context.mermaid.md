# System Context Diagram - Epic 2nd Brain
# Mermaid Source of Truth
# Last Updated: 2024-11-24

## Overview

This is the **executive view** - simplified for quick understanding.
For the visual HTML version, see: `visuals/system-overview.html`

## Diagram

```mermaid
flowchart LR
    subgraph Inputs["📥 INPUTS"]
        Voice["🎙️ Voice Notes<br/>5-20/day"]
        Chat["💬 Claude Chat<br/>Strategy, PRDs"]
        Code["⚡ Claude Code<br/>Implementation"]
    end

    subgraph System["🧠 EPIC 2ND BRAIN"]
        Core["Transcribe<br/>Analyze<br/>Route<br/>Sync"]
    end

    subgraph Outputs["📤 OUTPUTS"]
        Tasks["✅ Organized Tasks"]
        Context["🔍 Instant Context"]
        Mobile["📱 Mobile Dashboard"]
    end

    subgraph APIs["⚙️ POWERED BY"]
        Groq["⚡ Groq"]
        OpenAI["🤖 OpenAI"]
        Notion["📋 Notion"]
        GitHub["🐙 GitHub"]
    end

    Voice --> System
    Chat <--> System
    Code <--> System
    
    System --> Tasks
    System --> Context
    System --> Mobile
    
    System -.-> Groq
    System -.-> OpenAI
    System -.-> Notion
    System -.-> GitHub
```

## Key Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Voice note success rate | 96% | ✅ Good |
| Context load time | 3 min (was 15 min) | ✅ Good |
| Time saved per week | 70-120 min | ✅ Good |

## Current Friction Points

1. **Claude Chat → Code Handoff**: Manual copy-paste, context loss (~5 min per handoff)
2. **Notion Sync Visibility**: No confirmation, can't select files for mobile
3. **Context Loading Opacity**: Can't see why files were selected, hard to adjust

## Related Diagrams

- [Container Architecture](./container-architecture.mermaid.md) - How pieces connect
- [Leverage Points](./leverage-points.mermaid.md) - Where to invest (TODO)
