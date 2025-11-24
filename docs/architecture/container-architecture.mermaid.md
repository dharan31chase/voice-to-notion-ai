# Container Architecture - Epic 2nd Brain
# Mermaid Source of Truth
# Last Updated: 2024-11-24

## Overview

This is the **builder view** - complete architecture showing how all pieces connect.
For the visual HTML version, see: `visuals/container-architecture.html`

## Diagram

```mermaid
flowchart TB
    subgraph Actors["👥 EXTERNAL ACTORS"]
        You["👤 You (Dharan)"]
        Sony["🎙️ Sony Recorder"]
        Chat["💬 Claude Chat"]
        Code["⚡ Claude Code"]
    end

    subgraph SharedState["📦 SHARED STATE (Read + Write)"]
        Notion["📋 Notion<br/>5 databases"]
        Repo["📂 Git Repo<br/>docs, PRDs, sessions"]
        RAGIndex["🗄️ RAG Index<br/>ChromaDB + BM25"]
    end

    subgraph Interface["🔌 INTERFACE LAYER"]
        MCP1["MCP Server #1<br/>9 tools"]
        MCP2["MCP Server #2<br/>3 RAG tools"]
        Hooks["🪝 Git Hooks<br/>post-commit"]
        FS["📁 File System<br/>direct access"]
    end

    subgraph Subsystems["⚙️ PROCESSING SUBSYSTEMS"]
        Voice["🎙️ Voice Pipeline<br/>8 stages"]
        AI["🤖 AI Processing<br/>4 routers"]
        Sync["🔄 Notion Sync"]
        RAG["🔍 RAG Search"]
        Context["📂 Context Loader"]
    end

    subgraph APIs["🌐 EXTERNAL APIs"]
        Groq["⚡ Groq"]
        OpenAI["🤖 OpenAI"]
        NotionAPI["📋 Notion API"]
        GitHub["🐙 GitHub"]
    end

    %% Actor connections
    You -->|"voice notes"| Sony
    You -->|"strategy"| Chat
    You -->|"implementation"| Code
    
    Sony -->|".mp3 files"| Voice
    Chat <-->|"MCP protocol"| MCP1
    Chat <-->|"MCP protocol"| MCP2
    Code <-->|"read/write"| FS
    
    %% Interface to Shared State
    MCP1 <-->|"query/update"| Notion
    MCP1 <-->|"read/write"| Repo
    MCP2 <-->|"search"| RAGIndex
    Hooks -->|"sync"| Notion
    FS <-->|"files"| Repo
    
    %% Interface to Subsystems
    MCP1 --> Context
    MCP2 --> RAG
    Hooks --> Sync
    
    %% Subsystem connections
    Voice --> AI
    AI --> Sync
    Context -->|"reads"| Notion
    Context -->|"reads"| Repo
    RAG -->|"searches"| RAGIndex
    Sync -->|"writes"| Notion
    
    %% API connections
    Voice -.->|"transcribe"| Groq
    AI -.->|"analyze"| OpenAI
    RAG -.->|"embed"| OpenAI
    Sync -.->|"CRUD"| NotionAPI
    Hooks -.->|"push"| GitHub

    classDef actor fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    classDef state fill:#fef3c7,stroke:#f59e0b,stroke-width:2px
    classDef interface fill:#dbeafe,stroke:#3b82f6,stroke-width:2px
    classDef subsystem fill:#1e293b,stroke:#334155,stroke-width:2px,color:#fff
    classDef api fill:#f1f5f9,stroke:#94a3b8,stroke-width:1px

    class You,Sony,Chat,Code actor
    class Notion,Repo,RAGIndex state
    class MCP1,MCP2,Hooks,FS interface
    class Voice,AI,Sync,RAG,Context subsystem
    class Groq,OpenAI,NotionAPI,GitHub api
```

## Data Flows

| # | Flow | Path | Timing |
|---|------|------|--------|
| 1 | Voice → Notion | Sony → Voice Pipeline → AI Processing → Notion | 5-15 min batch |
| 2 | Git → Notion | Commit → Git Hook → Notion Sync → Roadmap/Sessions | 2-5 sec (blocking) |
| 3 | Session Start | start_session() → MCP #1 → Context Loader → Read Notion + Repo | 3-5 sec |
| 4 | RAG Search | Query → MCP #2 → RAG Search → ChromaDB + BM25 → Rerank | ~500ms |
| 5 | Claude Code → Repo | Write file → File System → Git Repo → Commit → Flow #2 | Direct |
| 6 | Handoff (Chat → Code) | end_session() → MCP #1 → Write handoff.md → **Manual copy-paste** | ⚠️ Friction |

## Connection Summary

### Who Talks to What
- **Claude Chat** → MCP Servers (#1 and #2)
- **Claude Code** → File System (direct read/write)
- **Git Commit** → Git Hooks (auto-triggers)
- **Sony USB** → Voice Pipeline (manual trigger)

### Subsystem → API Dependencies
- **Voice Pipeline** → Groq (transcription)
- **AI Processing** → OpenAI (GPT-4)
- **RAG Search** → OpenAI (embeddings) + Local (BGE rerank)
- **Notion Sync** → Notion API + GitHub API

### Shared State Access
- **Notion**: Read by Context Loader, written by Voice Pipeline & Notion Sync
- **Git Repo**: Read by Context Loader & MCP, written by Claude Code & MCP
- **RAG Index**: Read by RAG Search, written by Indexer (manual)

## Related Diagrams

- [System Context](./system-context.mermaid.md) - Executive overview
- [Leverage Points](./leverage-points.mermaid.md) - Where to invest (TODO)
- [Component Inventory](./component-inventory.md) - Detailed code documentation
