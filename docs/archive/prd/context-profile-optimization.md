> **⚠️ ARCHIVED**: This PRD has been superseded by [Live Context Control v2](../live-context-control.md) as of 2025-12-03.
> 
> **Why archived**: The learning loop and intelligent context loading features from this PRD were merged into Live Context Control Phase 4. Repo onboarding automation was added as Phase 1 to solve the Life Admin setup problem.
> 
> **For current work**: See [Live Context Control PRD](../live-context-control.md)
>
> **What was preserved**: All implementation work (configs, functions, learning algorithm) became the foundation for Live Context Control Phase 4.

---

# PRD: Context Profile Optimization - Intelligent Context Loading

**Status**: ARCHIVED - Merged into Live Context Control v2
**Priority**: High
**Estimated Effort**: 6-7 hours (Phase 1)
**Owner**: Dharan Chandra Hasan
**Created**: 2025-11-13
**Last Updated**: 2025-11-17
**Archived**: 2025-12-03
**Parent Initiative**: [Context Profile Optimization](https://www.notion.so/Context-Profile-Optimization-2aa8369c73058053a3cdd97a3d0b4823)
**Notion Strategy Board**: [Epic 2nd Brain - Strategy Board](https://www.notion.so/)
**Tech Requirements**: [context-profile-optimization.md](../../tech-requirements/context-profile-optimization.md) ✅

---

## 📋 Implementation Readiness Checklist

**Pre-Implementation** (Before Claude Code starts):
- [x] Tech requirements document created (2025-11-17)
- [x] Architecture decisions approved (Phase 1 quick impl, Phase 2 modular refactor)
- [x] Success criteria defined (<5s suggestion, >80% signal-to-noise)
- [x] Dependencies identified (None)
- [x] Added to roadmap (Phase 5D refactoring task)

**Implementation** (Claude Code updates during work):
- [x] Config files created (project-paths.json, file-type-patterns.json, context-profiles.json) - 2025-11-17
- [x] Core functions implemented (file discovery, profile management) - 2025-11-17
- [x] Integration points complete (MCP tool registration) - 2025-11-17
- [x] Unit tests written (parse_user_selection, classify_file_type, find_project) - 2025-11-17
- [ ] Integration tests written (first-time suggestion, learned profile loading) - Deferred to real usage validation

**Post-Implementation** (Before marking Complete):
- [ ] All tests passing
- [ ] Documentation updated (README, MCP server docs)
- [ ] Code reviewed (self-review for docstrings, edge cases)
- [ ] Ready for production use (validated with real Legacy AI workflow)

---

## 🎯 TL;DR

Build a **learning context system** that collaboratively suggests 3-6 targeted files based on work stream, learns from your selections, and auto-applies learned profiles in future sessions - reducing context loading from 10-16 random docs to 3-6 high-signal docs while improving relevance from 30-40% to 80-90%.

**Key Innovation**: System gets smarter with use. First time = you teach it. Every time after = it remembers.

**Time Investment**: 5-6 hours implementation  
**ROI**: 10-15 min saved × 50 sessions/10 weeks = **8-12 hours saved before baby arrives**

---

[... rest of original document content ...]

---

**End of ARCHIVED PRD**
