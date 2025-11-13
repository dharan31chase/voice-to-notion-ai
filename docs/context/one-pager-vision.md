# Epic 2nd Brain: Vision One-Pager

**Purpose**: Overview of the personal operating system I'm building  
**Last Updated**: November 11, 2025

---

## What I'm Building

A personal operating system that eliminates friction between thought and execution by orchestrating multiple AI agents with a unified context layer.

Think of it as building my own Chief of Staff + implementation team that knows everything I've decided, why I decided it, and can execute across domains (strategy, code, design, research) without me manually bridging context between systems.

---

## The Core Problem

Right now, I spend 10-15 minutes at the start of every work session reconstructing context:
- What did we decide last time?
- What's blocking me today?
- Where are we in the roadmap?

I also spend 30-45 minutes daily on digital housekeeping:
- Organizing notes and tasks
- Copying requirements between Claude (strategy) and Claude Code (implementation)
- Manually updating project status in Notion
- Searching for past decisions

**This overhead compounds**: With limited time for focused work, I can't afford to spend 25% of it on context loading and admin.

---

## The Solution Architecture

### Three-System Integration

**1. Git/GitHub** (Source of truth for decisions)
- PRDs, technical docs, session logs
- Version control for life decisions
- Survives laptop death, provides rollback

**2. Notion** (Dashboard for current state)
- PARA-organized tasks and projects
- Priority scoring and daily focus
- Mobile access for status checks

**3. MCP + Agents** (Automated context + execution)
- Claude reads context automatically (no copy-paste)
- Claude Code executes with full context
- Git hooks auto-sync to Notion

### The Workflow Loop

```
Voice note → Transcription → AI routing → Notion task →
Priority scoring → Claude strategic clarification → Claude Code implementation →
Git commit → Notion auto-update → Context preserved
```

Every cycle accumulates context. By month 3, the system knows my decision patterns. By year 3, it has three years of my thinking.

---

## Why This Approach

### Hybrid Architecture > Pure Solutions

**Why not pure Notion?**
- No version control (can't rollback mistakes)
- Mixing IP-sensitive work with personal life creates collaboration friction
- Vendor lock-in risk

**Why not pure Git/CLI?**
- I've invested heavily in Notion PARA methodology
- Visual dashboard is valuable for quick status checks
- Mobile access matters for on-the-go planning

**Why hybrid?**
- Git gives me portability and history
- Notion gives me workflow and visualization
- Best of both, mitigates vendor lock-in

### Multi-Agent Orchestration > Single AI

Different problems need different agents:
- **Strategic decisions** → Claude (broad reasoning, frameworks)
- **Code implementation** → Claude Code (focused execution)
- **Design work** → Figma agent (visual thinking)
- **Domain expertise** → Specialized agents (tax, research)

I'm building the orchestration layer that routes work to the right agent and preserves context across handoffs.

---

## Current State

**What's Working:**
- Voice-to-Notion pipeline: 96% success rate, processes 10-20 notes/day
- 130x transcription speed improvement (13.6 sec vs 29.6 min)
- MCP proof-of-concept: Auto-context loading validated
- Basic git hooks syncing docs to Notion

**What's In Progress:**
- Session log automation (Claude Code → Git → Notion)
- Agent handoff protocols (Claude → Claude Code with full context)
- RAG search across all project docs

**Timeline:**
- Tier 0 target: 2 weeks (by Nov 22)
- Current status: Week 1 complete, ahead of schedule

---

## Measurable Goals

**Time Savings:**
- Context loading: 10-15 min → <3 min (80% reduction)
- Daily organization: 30-45 min → <15 min (60% reduction)
- Total weekly savings: 70-120 minutes

**Quality Improvements:**
- Zero "what did we decide?" moments (currently 3-5/week)
- Full decision history searchable
- Complete context for every session

**System Health:**
- 95%+ routing accuracy
- <5 min from voice note to organized
- <1 hour documentation lag

---

## What Success Looks Like (1 Year)

**Morning (7am):**
- Open Notion dashboard
- See top 3 priorities auto-calculated
- Context for each already loaded
- Start working in <3 minutes

**During Work:**
- Voice notes automatically organized
- Claude has full context of past decisions
- Claude Code receives requirements without copy-paste
- Git commits auto-update Notion status

**Evening (8pm):**
- System shows what got done
- Open loops captured
- Nothing slipped through cracks
- Fully disconnect from work

**Result:** 2 hours/day of focused work feels like 4 hours because overhead is gone.

---

## Why This Matters

This infrastructure compounds. Every project benefits—customer discovery, planning work, financial decisions, strategic frameworks. Build the context bridge once, apply it forever.

The goal isn't just productivity. It's building cognitive infrastructure that gets more valuable over time as it accumulates context about how I think, decide, and create.

---

## Technical Architecture

**Key Components:**
- **Voice Pipeline**: USB recorder → Whisper transcription → GPT-4 analysis → Notion routing
- **Context Sync**: MCP tools auto-load from Git, git hooks auto-update Notion
- **Agent Orchestration**: Claude (strategy) ↔ Claude Code (implementation) with preserved context
- **Priority Engine**: Formula-based scoring (Impact × 2 + Urgency + Leverage × 3 + Energy Match)

**Infrastructure:**
- Language: Python
- Storage: Git (history) + Notion (dashboard)
- AI: OpenAI GPT-4, Anthropic Claude
- Integration: Model Context Protocol (MCP), git hooks, Notion API

---

## Three-Year Vision

**Year 1: Foundation**
- Operational second brain reducing org time to <15 min/day
- Claude + Claude Code + handoff protocols working smoothly

**Year 2: Intelligence**
- Proactive context surfacing
- Zero-search workflows
- System learns from corrections

**Year 3: Orchestration**
- Multi-agent ecosystem (5-10 specialized agents)
- Intelligent auto-routing of tasks to right agent
- Unified intelligence layer

**Long-term: Compounding Wisdom**

By Year 10, the system holds a decade of decision context. By Year 30, an irreplaceable strategic asset—cognitive infrastructure that gets more valuable with every year of accumulated wisdom.

---

*This is what I'm building. A personal operating system that transforms how I think, decide, and execute.*
