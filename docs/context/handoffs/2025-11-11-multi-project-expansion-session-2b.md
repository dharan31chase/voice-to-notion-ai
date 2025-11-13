# Handoff Document: Multi-Project Expansion Implementation

**From**: Claude Chat (Sonnet 4.5) - Session 2A
**To**: Claude Code (Sonnet 4.5) - Session 2B
**Date**: 2025-11-11
**PRD**: `docs/prd/multi-project-expansion.md`
**Estimated Implementation**: 6-8 hours

---

## 🎯 Mission

Expand Context Sync Bridge to support Legacy AI (business repo) alongside Epic 2nd Brain (infrastructure repo) with clean IP separation, professional documentation, and automated context loading.

---

## ✅ Implementation Checklist

### **Part 1: Create Legacy AI Repo** (1-2 hours)

**1.1 Create Local Repo Structure**
```bash
cd ~/Documents/1.\ Projects/
mkdir legacy-ai
cd legacy-ai
git init

# Create folder structure
mkdir -p research/customer-interviews/{transcripts,analyses,insights}
mkdir -p research/technical-feasibility
mkdir -p product/prototypes/systems-diagrams
mkdir -p product/prd
mkdir -p product/design
mkdir -p business/{pitch-deck,fundraising-strategy,go-to-market}
mkdir -p sessions/{customer-discovery,prototype-iteration,funding-prep}
mkdir -p docs/templates

# Create placeholder files
touch research/requirements-vision.md
touch research/positioning.md
touch research/technical-feasibility/.gitkeep
touch docs/decision-log.md
touch docs/roadmap.md
touch README.md
```

**1.2 Write README.md**

Create professional README that explains:
- Project vision ("Family legacy voice capture that connects generations")
- Folder structure (research/product/business)
- Workflow (customer discovery → prototypes → pitch → funding)
- How to contribute (for when Peter joins)
- Current stage (customer discovery, 5+ interviews conducted)

**1.3 Create .gitignore**
```
# Sensitive data
*.env
.env.*
secrets/
cap-table/
legal-docs/

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/

# Notion exports (we'll keep structured docs only)
*.zip
exports/
```

**1.4 Initial Commit**
```bash
git add .
git commit -m "Initial commit: Legacy AI repo structure

- Set up research/product/business folder structure
- Add README with project vision and workflow
- Create placeholder docs for requirements, positioning, decision log"
```

**1.5 Create GitHub Organization & Remote**
- Go to GitHub → Create new organization "Legacy Tech"
- Create private repo `legacy-ai` under that org
- Push local repo to remote:
```bash
git remote add origin git@github.com:legacy-tech/legacy-ai.git
git branch -M main
git push -u origin main
```

---

### **Part 2: Port Customer Interview Analysis Template** (30-45 min)

**2.1 Get Template from Dharan**

Ask Dharan to:
1. Export existing Customer Interview Analysis template from Notion
2. Provide as markdown or text

**2.2 Create Template File**

Location: `legacy-ai/docs/templates/customer-interview-analysis.md`

Port template AS-IS (don't enhance yet - that's Week 3-4)

Ensure it includes:
- Jobs-to-be-done sections (functional, emotional, social)
- Mom Test validation structure
- Key insights & quotes
- Strategic implications
- Next actions

**2.3 Add Template Usage Instructions**

Create `legacy-ai/docs/templates/README.md`:
```markdown
# Templates

## Customer Interview Analysis

**When to use**: After every customer interview (transcription available)

**How to use**:
1. Copy `customer-interview-analysis.md` to `research/customer-interviews/analyses/`
2. Rename: `YYYY-MM-DD-[interviewee-name].md`
3. Fill out sections based on interview transcript
4. Commit with message: "Add interview analysis: [Name]"

**Framework**: Jobs-to-be-done + Mom Test

**Review frequency**: After every 5 interviews, review template effectiveness
```

**2.4 Test Template**

Create a sample analysis file to validate structure:
`research/customer-interviews/analyses/2025-11-11-sample-interview.md`

---

### **Part 3: Migrate Initial 5 Documents** (1-2 hours)

**3.1 Get Documents from Dharan**

Ask Dharan for these 5 docs (in priority order):
1. Requirements & Vision
2. Positioning strategy
3. Best customer interview analysis (as template validation)
4. Most recent interview analysis (shows current thinking)
5. Technical feasibility summary

**3.2 Convert to Markdown & Organize**

- `research/requirements-vision.md`
- `research/positioning.md`
- `research/customer-interviews/analyses/[date]-[name].md` (2 files)
- `research/technical-feasibility/summary.md`

**3.3 Add Metadata Headers**

Each doc should start with:
```markdown
# [Title]

**Status**: Draft | In Review | Approved
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Owner**: Dharan Chandra Hasan

---
```

**3.4 Commit Migration**
```bash
git add research/
git commit -m "Migrate initial 5 documents from Notion

- Requirements & Vision: Strategic overview
- Positioning: Family legacy voice capture positioning
- Interview analyses: [Names] - Jobs-to-be-done insights
- Technical feasibility: Initial validation

Source: Notion Legacy AI project (30+ docs total)
Next: Migrate remaining docs iteratively"
```

---

### **Part 4: Update MCP Tools for Multi-Project** (2-3 hours)

**4.1 Add Project Configuration**

In `mcp_server/server.py`, add project registry:

```python
PROJECT_CONFIG = {
    "Epic 2nd Brain": {
        "repo_path": Path.home() / "Documents" / "1. Projects" / "ai-assistant",
        "context_folders": ["docs/prd", "docs/tech-requirements", "docs/sessions"],
        "strategy_board_view": "Epic 2nd Brain Only"
    },
    "Legacy AI": {
        "repo_path": Path.home() / "Documents" / "1. Projects" / "legacy-ai",
        "context_folders": ["research", "product", "business", "sessions"],
        "strategy_board_view": "Legacy AI Only"
    }
}
```

**4.2 Update `start_session()` Tool**

Enhance to support project selection:

```python
@server.call_tool()
async def start_session(project_name: str = "Epic 2nd Brain", work_stream: str = None):
    """
    Load context for a specific project session.
    
    Args:
        project_name: "Epic 2nd Brain" | "Legacy AI"
        work_stream: Optional workflow phase
            - For Legacy AI: "customer-discovery" | "prototype" | "pitch" | "funding"
            - For Epic 2nd Brain: "infrastructure" | "implementation"
    """
    if project_name not in PROJECT_CONFIG:
        return {"error": f"Unknown project: {project_name}"}
    
    config = PROJECT_CONFIG[project_name]
    repo_path = config["repo_path"]
    
    # Load project-specific context
    context = {
        "project": project_name,
        "work_stream": work_stream,
        "timestamp": datetime.now().isoformat()
    }
    
    # Query Strategy Board (filtered by project)
    # Load recent docs from context_folders
    # Load session logs
    # etc.
    
    return context
```

**4.3 Update `search_docs()` Tool**

Add project filtering:

```python
@server.call_tool()
async def search_docs(query: str, project_name: str = None, doc_types: list = None):
    """
    Search across project docs.
    
    Args:
        query: Search query
        project_name: Filter to specific project (default: all projects)
        doc_types: Types to search ["prd", "tech-req", "sessions", "research"]
    """
    # If project_name specified, search only that project's repo
    # Otherwise search all projects (show which project each result is from)
```

**4.4 Update `end_session()` Tool**

Make project-aware for session log routing:

```python
@server.call_tool()
async def end_session(project_name: str, summary: str, decisions: list = None, ...):
    """
    Log session and create handoff if needed.
    
    Routes session log to correct project folder:
    - Epic 2nd Brain → ai-assistant/docs/sessions/claude-chat/
    - Legacy AI → legacy-ai/sessions/customer-discovery/ (or other work stream)
    """
```

**4.5 Test MCP Tools**

Create test script:
```python
# Test that start_session loads correct context
result = await start_session("Legacy AI", "customer-discovery")
assert result["project"] == "Legacy AI"
assert "requirements-vision.md" in result["context_loaded"]

# Test search is project-scoped
results = await search_docs("positioning", project_name="Legacy AI")
assert all("legacy-ai" in r["path"] for r in results)
```

---

### **Part 5: Set Up Git Hooks for Legacy AI** (30-45 min)

**5.1 Create Post-Commit Hook**

`legacy-ai/.git/hooks/post-commit`:

```bash
#!/bin/bash

# Sync Legacy AI commits to Notion Strategy Board (Legacy AI view)
python3 ~/Documents/1.\ Projects/ai-assistant/scripts/sync_to_notion.py \
    --project "Legacy AI" \
    --repo-path ~/Documents/1.\ Projects/legacy-ai
```

**5.2 Update `sync_to_notion.py`**

Enhance to handle multiple projects:
- Add `--project` flag
- Route to correct Strategy Board filtered view
- Handle different folder structures (research/ vs docs/)

**5.3 Make Hook Executable**
```bash
chmod +x legacy-ai/.git/hooks/post-commit
```

**5.4 Test Hook**
```bash
cd ~/Documents/1.\ Projects/legacy-ai
echo "Test" >> docs/decision-log.md
git add docs/decision-log.md
git commit -m "Test: Git hook sync to Notion"
# Verify update appears in Notion "Legacy AI Only" view
```

---

### **Part 6: Set Up Strategy Board Filtered Views** (30 min)

**6.1 Access Strategy Board**

Open: https://www.notion.so/2a58369c73058079a356cbf2dd2d86bc

**6.2 Add "Project" Property** (if not exists)

- Type: Select
- Options: Epic 2nd Brain, Legacy AI, Life Admin, Baby Prep, Multiple

**6.3 Create Filtered Views**

**View: "Legacy AI Only"**
- Filter: Project = "Legacy AI"
- Sort: Priority Score (descending)
- Visible properties: Initiative Name, Work Stream, Status, Priority Score, Impact Score

**View: "Epic 2nd Brain Only"**
- Filter: Project = "Epic 2nd Brain"
- Sort: Priority Score (descending)

**View: "All Initiatives"** (default)
- No filter (show everything)
- Group by: Project

**6.4 Test Views**

Create test initiative in "Legacy AI Only" view:
- Name: "Test Initiative - Delete This"
- Project: Legacy AI
- Verify it appears in "All Initiatives" but not "Epic 2nd Brain Only"

---

### **Part 7: Testing & Validation** (1 hour)

**7.1 Test Multi-Project Context Loading**

```python
# Test Epic 2nd Brain (should still work)
result = await start_session("Epic 2nd Brain")
assert "context-sync-bridge" in str(result)

# Test Legacy AI (new)
result = await start_session("Legacy AI", "customer-discovery")
assert "requirements-vision" in str(result)
assert "positioning" in str(result)
```

**7.2 Test Session Logging**

Create test session log in both projects:
- Epic 2nd Brain → should go to `ai-assistant/docs/sessions/claude-chat/`
- Legacy AI → should go to `legacy-ai/sessions/customer-discovery/`

**7.3 Test Git Hooks**

Make commits in both repos, verify:
- Epic 2nd Brain commit → updates "Epic 2nd Brain Only" view
- Legacy AI commit → updates "Legacy AI Only" view
- No cross-contamination

**7.4 Test Search Across Projects**

```python
# Search all projects
results = await search_docs("voice transcription")
# Should return results from BOTH projects with project indicators

# Search single project
results = await search_docs("customer pain points", project_name="Legacy AI")
# Should only return Legacy AI results
```

**7.5 Performance Check**

- Context loading for Epic 2nd Brain: Should still be <10 seconds
- Context loading for Legacy AI: Should be <10 seconds (fewer docs initially)
- Search across both projects: Should be <5 seconds

---

## 📋 Success Criteria

Before declaring Session 2B complete, verify:

- [ ] `legacy-ai/` repo created with full folder structure
- [ ] GitHub "Legacy Tech" organization created, repo is private
- [ ] README.md explains project vision and structure
- [ ] Customer Interview Analysis template ported to markdown
- [ ] 5 initial documents migrated and organized
- [ ] MCP `start_session()` supports "Legacy AI" parameter
- [ ] MCP `search_docs()` supports project filtering
- [ ] Git hooks sync Legacy AI commits to correct Notion view
- [ ] Strategy Board has 3 filtered views (All, Epic 2nd Brain Only, Legacy AI Only)
- [ ] Test: `start_session("Legacy AI")` loads context in <10 seconds
- [ ] Test: Commits to both repos sync to correct Notion views
- [ ] Test: Search can query single project or all projects

---

## 🚨 Potential Blockers & Solutions

**Blocker 1: Dharan needs to provide documents**
- **Solution**: Work on repo structure and MCP tools first, migrate docs later

**Blocker 2: GitHub organization creation requires payment**
- **Solution**: Use personal account for now, can transfer to org later (two-way door)

**Blocker 3: Notion API rate limits**
- **Solution**: Git hooks already handle rate limits (implemented in Session 1)

**Blocker 4: MCP tool changes break existing Epic 2nd Brain workflow**
- **Solution**: Add new functionality without changing defaults (backward compatible)

**Blocker 5: Customer Interview Analysis template is complex to port**
- **Solution**: Start with simplified version, iterate in Week 3-4

---

## 📝 Session Log Requirements

When Session 2B is complete, create session log at:
`ai-assistant/docs/sessions/claude-code/2025-11-XX-multi-project-expansion.md`

Include:
- **What Shipped**: Checklist of completed items above
- **Architecture Decisions**: Any choices made during implementation
- **Roadmap Updates**: What was deferred to Week 2-3
- **Next Steps**: Prep for Session 2C review and Session 3 real usage
- **Critical Alerts**: Any issues Dharan needs to know about

---

## 🎯 Handoff Back to Claude Chat (Session 2C)

After implementation, Dharan will return to Claude Chat for review session. Be ready to discuss:
- What worked smoothly
- What was more complex than expected
- Any architectural decisions you had to make
- Whether Session 3 (real Legacy AI usage) is ready to go

---

**End of Handoff Document**

**Implementation Mode**: Interactive
- Present options when facing architectural choices
- Ask for Dharan's input on naming, structure, etc.
- Document decisions in session log

**Good luck, Claude Code! Let's make this business-grade. 🚀**
