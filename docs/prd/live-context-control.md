# PRD: Live Context Control - Epic 2nd Brain v2

**Status**: Approved - Ready to Build
**Owner**: Dharan Chandrahasan
**Created**: 2025-11-25
**Last Updated**: 2025-12-03 (v2 - Merged with Context Profile Optimization)
**One-Pager**: [Applied Context Engineering](../context/one-pagers/infrastructure/context-engineering.md)
**Architecture**: [Context Management Architecture](../architecture/context-management-current-vs-proposed.mermaid.md)
**Related**: [Context Sync Bridge PRD](context-sync-bridge.md)

---

## 🎯 TL;DR

Build comprehensive context management system for Claude Chat that eliminates 100-140 min/week of friction through 5 integrated phases: Tool Priority Fix (1 hour) + **Repo Onboarding Automation (4-6 hours)** + Visibility & Control (6-8 hours) + Smart Discovery (6-8 hours) + Learning Loop (4-6 hours). Total investment: 21-29 hours for foundation that scales to 5-10 projects without multiplying friction.

**v2 Changes**: Added Phase 1 (Repo Onboarding Automation) to solve Life Admin and future project setup pain. Merged Context Profile Optimization PRD into Phase 4 (Learning Loop).

---

## 🎯 Problem Statement

### The Complete Context Management Problem (5 Pain Points)

**Problem 0: Tool Selection Spiral** (Validated Nov 25)
- **Test**: "Read the meta-analysis from the Insights folder in Legacy AI"
- **What happened**: 8 steps, 90-120 seconds wasted
- **Root cause**: Claude tries bash/view/grep before MCP tools

**Problem 1: Repo Onboarding Hell** (NEW - Dec 3, 2025)
- **Pain**: Created Life Admin repo, MCP tools don't recognize it
- **Current flow**: Manual config hell - edit 3+ files, create folder structure, test everything
- **Time cost**: 30-60 minutes per new project
- **Scaling disaster**: With 5-10 projects planned, this is 2.5-10 hours of manual setup

**Problem 2: Useless Suggestions at Session Start**
- **Current**: MCP suggests 3-6 files, ~30% accuracy ("completely useless")
- **Root cause**: No learning loop - system doesn't track which files you actually use

**Problem 3: Invisible Context Mid-Session**
- **Pain**: "I forget halfway in which files are in context"
- **Root cause**: No way to see what's loaded, leads to restart spirals

**Problem 4: Manual File Discovery Hell**
- **Pain**: "So hard to add a file... have to paste the path name exactly"
- **Root cause**: No search/discovery tools, leads to 8-step spiral

---

[Content continues with all sections from the merged PRD...]

---

**End of PRD v2**
