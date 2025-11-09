# Detailed Implementation Plan

# Tier 0: Detailed Implementation Plan

Timeline: Nov 8-22, 2025 (2 weeks)

Owner: Dharan + Claude + Claude Code

Status: Ready to Execute

Last Updated: Nov 8, 2025

---

## 📋 Overview

This document provides step-by-step implementation details for each phase of the Tier 0 roadmap. Each phase includes:

- Exact files to create/modify

- Code snippets and templates

- Success criteria and validation tests

- Time estimates and dependencies

- Rollback/fallback plans

Companion Document: See Roadmap for high-level strategy and architecture decisions.

---

## 🔑 Phase 1A: MCP Proof-of-Concept (Day 1-2)

Time Estimate: 2 hours

Owner: Claude Code

Dependencies: None (can start immediately)

### Goal

Prove that MCP (Model Context Protocol) works on your Mac before investing in full implementation.

### Background

You previously tried MCP with Cursor and it didn't work. This is because:

- Cursor doesn't support MCP (it's Claude Desktop specific)

- MCP is cutting-edge (launched April 2024)

- Requires proper configuration

This phase validates MCP is viable for your setup before proceeding.

---

### Step 1: Install MCP SDK (15 minutes)

```bash
# Navigate to your project
cd ~/ai-assistant

# Install MCP Python SDK
pip install mcp --break-system-packages

# Create MCP server directory
mkdir -p mcp_server
cd mcp_server
```

Validation: Run pip show mcp and verify version >= 0.1.0

---

### Step 2: Create Minimal MCP Server (30 minutes)

File: mcp_server/simple_server.py

```python
#!/usr/bin/env python3
"""
Simple MCP Server - Proof of Concept
Tests basic file reading capability
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import os

# Initialize MCP server
app = Server("ai-assistant-poc")

@app.tool()
async def read_file(path: str) -> str:
    """
    Read a file from the ai-assistant repo.
    
    Args:
        path: Relative path from repo root (e.g., 'README.md')
    
    Returns:
        File contents as string
    """
    repo_root = os.path.expanduser("~/ai-assistant")
    full_path = os.path.join(repo_root, path)
    
    if not os.path.exists(full_path):
        return f"Error: File not found at {full_path}"
    
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

Validation: Run python simple_server.py - should start without errors

---

### Step 3: Configure Claude Desktop (30 minutes)

File: ~/Library/Application Support/Claude/claude_desktop_config.json

```json
{
  "mcpServers": {
    "ai-assistant": {
      "command": "python3",
      "args": [
        "/Users/[YOUR_USERNAME]/ai-assistant/mcp_server/simple_server.py"
      ],
      "env": {}
    }
  }
}
```

Steps:

1. Open Claude Desktop app

1. Go to Settings > Developer

1. Enable "MCP Servers"

1. Edit config file with above JSON

1. Replace [YOUR_USERNAME] with your actual username

1. Restart Claude Desktop

Validation:

- Open Claude Desktop

- Look for "MCP: ai-assistant" in bottom status bar

- Green indicator = working

---

### Step 4: Test MCP Tool (15 minutes)

In Claude Desktop, try these commands:

```javascript
Test 1:
"Use the read_file tool to read README.md"

Expected: Claude calls tool, returns README content

Test 2:
"Use the read_file tool to read docs/project-state.md"

Expected: Claude calls tool, returns project state

Test 3:
"Use the read_file tool to read nonexistent.md"

Expected: Claude calls tool, returns error message
```

Success Criteria:

- ✅ All 3 tests work as expected

- ✅ Claude can read files without you pasting them

- ✅ Error handling works (graceful failure)

If Tests Fail:

1. Check Claude Desktop logs: ~/Library/Logs/Claude/

1. Verify config file path is correct

1. Verify Python path is correct (which python3)

1. Try manual server test: python3 simple_server.py (should run without errors)

---

### Phase 1A Success Criteria

Decision Point:

- If all tests pass → Proceed to Phase 1B (expand MCP tools)

- If tests fail → Fallback to manual file reading, defer MCP to Tier 1

---

## 📝 Phase 1B: Documentation Templates (Day 1-2)

Time Estimate: 4-6 hours

Owner: Claude Code

Dependencies: None (can run parallel with Phase 1A)

### Goal

Create structured documentation system in ai-assistant/docs/ folder with templates for PRDs, tech requirements, and session logs.

---

### Step 1: Create Folder Structure (10 minutes)

```bash
cd ~/ai-assistant

# Create documentation folders
mkdir -p docs/prd
mkdir -p docs/tech-requirements
mkdir -p docs/sessions/claude-chat
mkdir -p docs/sessions/claude-code
mkdir -p docs/architecture/diagrams

# Create placeholder README
touch docs/README.md
```

Validation: Run tree docs/ and verify structure

---

### Step 2: Create PRD Template (45 minutes)

File: docs/prd/TEMPLATE.md

```markdown
# PRD: [Feature Name]

**Status**: Draft | In Review | Approved | In Development | Shipped  
**Owner**: [Your name]  
**Last Updated**: [YYYY-MM-DD]  
**Tech Requirements**: [Link to tech-requirements/[feature].md]

---

## 🎯 Problem Statement

**User Pain Point**:  
[What problem does this solve? Be specific about user frustration.]

**Current Workaround**:  
[How do users currently solve this? Why is it painful?]

**Why Now**:  
[Why is this the right time to build this?]

---

## ✅ Success Criteria

**Must Have** (Launch blockers):
1. [Measurable outcome 1]
2. [Measurable outcome 2]
3. [Measurable outcome 3]

**Nice to Have** (Post-launch):
1. [Enhancement 1]
2. [Enhancement 2]

**Metrics**:
- [Metric 1]: Baseline → Target
- [Metric 2]: Baseline → Target

---

## 👥 User Stories

**As a** [user type],  
**I want** [capability],  
**So that** [benefit].

**Acceptance Criteria**:
- [ ] [Specific, testable condition 1]
- [ ] [Specific, testable condition 2]
- [ ] [Specific, testable condition 3]

---

## 🎨 Design Notes

**UI/UX Considerations**:  
[Wireframes, mockups, user flow diagrams]

**Visual Design**:  
[Figma links, style guidelines]

**Information Architecture**:  
[How does this fit into existing structure?]

---

## ❓ Open Questions

1. **[Question 1]**  
   - Options: A, B, C  
   - Recommendation: [Your recommendation + rationale]  
   - Status: Open | Under Review | Resolved

2. **[Question 2]**  
   - Options: X, Y, Z  
   - Recommendation: [Your recommendation]  
   - Status: Open | Under Review | Resolved

---

## 🔗 Links

- **Tech Requirements**: [Link to tech-requirements/[feature].md]
- **Figma**: [Link to design mockups]
- **Notion Page**: [Link to Notion roadmap item]
- **Related PRDs**: [Links to dependent/related PRDs]

---

## 📅 Timeline

- **PRD Draft**: [Date]
- **Review Complete**: [Date]
- **Dev Start**: [Date]
- **Launch**: [Date]

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|----------|
| YYYY-MM-DD | [Name] | Initial draft |
| YYYY-MM-DD | [Name] | Updated success criteria |
```

Validation: Create a sample PRD for "Context Sync Bridge" using this template

---

### Step 3: Create Tech Requirements Template (45 minutes)

File: docs/tech-requirements/TEMPLATE.md

```markdown
# Technical Requirements: [Feature Name]

**Status**: Draft | Ready to Build | In Progress | Complete  
**PRD**: [Link to prd/[feature].md]  
**Owner**: [Developer name]  
**Last Updated**: [YYYY-MM-DD]

---

## 🎯 Architecture Decision

**Approach**: [High-level approach chosen]  
**Rationale**: [Why this approach over alternatives]

**Alternatives Considered**:
1. **[Alternative A]**: [Brief description]  
   - Pros: [List pros]  
   - Cons: [List cons]  
   - Why rejected: [Reason]

2. **[Alternative B]**: [Brief description]  
   - Pros: [List pros]  
   - Cons: [List cons]  
   - Why rejected: [Reason]

**Trade-offs Accepted**:
- [Trade-off 1]: [What we're giving up + what we're gaining]
- [Trade-off 2]: [What we're giving up + what we're gaining]

---

## 🛠️ Implementation Plan

### Phase 1: [Phase Name] (X hours)
**Goal**: [What this phase achieves]

**Steps**:
1. [Step 1] (X min)  
   - Files: `[file1.py]`, `[file2.py]`  
   - Changes: [Brief description]

2. [Step 2] (X min)  
   - Files: `[file3.py]`  
   - Changes: [Brief description]

**Success Criteria**:
- [ ] [Testable condition 1]
- [ ] [Testable condition 2]

### Phase 2: [Phase Name] (X hours)
[Same structure as Phase 1]

---

## 📁 Files Modified

### New Files
```

path/to/new_file1.py  # Purpose: [Brief description]

path/to/new_file2.py  # Purpose: [Brief description]

```javascript

### Modified Files
```

path/to/existing_file.py  # Changes: [Brief description]

```javascript

### Configuration Changes
```

config/settings.json  # Added: [new settings]

.env                  # Added: [new env vars]

```javascript

---

## ⚙️ Configuration Changes

**Environment Variables** (`.env`):
```

NEW_VAR_1=value  # Purpose: [Why needed]

NEW_VAR_2=value  # Purpose: [Why needed]

```javascript

**Config Files** (`config/[file].json`):
```

{

}

```javascript

---

## ✅ Testing Strategy

### Unit Tests
```

def test_feature_1():

def test_feature_2_edge_case():

```javascript

### Integration Tests
- [ ] Test end-to-end workflow
- [ ] Test error handling
- [ ] Test with real data

### Manual Testing
1. [Test case 1]: [Expected behavior]
2. [Test case 2]: [Expected behavior]
3. [Test case 3]: [Expected behavior]

---

## 🚀 Rollout Plan

**Phase 1: Dev Testing** (Day 1):
- Test in local environment
- Validate against success criteria
- Fix any bugs

**Phase 2: User Testing** (Day 2):
- You test the feature in real workflow
- Collect feedback
- Iterate if needed

**Phase 3: Launch** (Day 3):
- Merge to main branch
- Update documentation
- Monitor for issues

**Rollback Plan**:
- Git revert to commit [hash]
- Restore previous config
- Document what went wrong

---

## 🚨 Critical Alerts

**Bugs**:
- [Bug 1]: [Description, severity, workaround]
- [Bug 2]: [Description, severity, workaround]

**Design Flaws**:
- [Flaw 1]: [Description, impact, fix plan]
- [Flaw 2]: [Description, impact, fix plan]

**System Decisions**:
- [Decision 1]: [What was decided, why it matters for future]
- [Decision 2]: [What was decided, why it matters for future]

---

## 🔗 Links

- **PRD**: [Link to prd/[feature].md]
- **Architecture Diagram**: [Link to mermaid or Figma]
- **GitHub Issue**: [Link to issue tracker]
- **Notion Roadmap**: [Link to Notion]

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|----------|
| YYYY-MM-DD | [Name] | Initial draft |
| YYYY-MM-DD | [Name] | Updated architecture |
```

Validation: Create a sample tech req for "MCP Server Implementation" using this template

---

### Step 4: Create Session Log Template (45 minutes)

File: docs/sessions/TEMPLATE.md

```markdown
# Session: [YYYY-MM-DD] - [Agent: Claude | Claude Code]

**Project**: [Project Name]  
**Duration**: [X hours Y minutes]  
**Status**: Active | Blocked | Complete  
**Session Type**: Strategy | Implementation | Debug | Review

---

## 🚀 What Shipped

**Features Completed**:
- [Feature 1]: [Brief description + impact]
- [Feature 2]: [Brief description + impact]

**Bugs Fixed**:
- [Bug 1]: [What was broken + how fixed]
- [Bug 2]: [What was broken + how fixed]

**Files Changed**:
```

path/to/file1.py  (+50, -20)  # Added [feature]

path/to/file2.py  (+30, -10)  # Fixed [bug]

```javascript

**Git Commits**:
- `abc123`: [Commit message]
- `def456`: [Commit message]

---

## 🧠 Architecture Decisions

**Decision 1**: [What was decided]  
- **Context**: [Why this decision was needed]
- **Options Considered**: A, B, C
- **Chosen**: [Option X]
- **Rationale**: [Why this option]
- **Trade-offs**: [What we're accepting]
- **Impact**: [How this affects future work]

**Decision 2**: [What was decided]  
[Same structure as Decision 1]

---

## 📝 Roadmap Updates

**Items Completed**:
- ✅ [Roadmap item 1]: Shipped
- ✅ [Roadmap item 2]: Shipped

**Items Started**:
- 🟡 [Roadmap item 3]: In progress (50% complete)
- 🟡 [Roadmap item 4]: Blocked (waiting on X)

**Items Added**:
- ⭐ [New item 1]: [Why added, priority]
- ⭐ [New item 2]: [Why added, priority]

---

## ➡️ Next Steps (Choose 1)

### Option A: [Next Action A]
**Why This Makes Sense**:  
[Rationale for why this is the logical next step]

**Time Estimate**: [X hours]  
**Dependencies**: [None | Blocked on Y]  
**Impact**: [What this unlocks]

### Option B: [Next Action B]
**Why This Makes Sense**:  
[Rationale for alternative path]

**Time Estimate**: [X hours]  
**Dependencies**: [None | Blocked on Z]  
**Impact**: [What this unlocks]

### Option C: [Next Action C]
**Why This Makes Sense**:  
[Rationale for third option]

**Time Estimate**: [X hours]  
**Dependencies**: [None | Blocked on W]  
**Impact**: [What this unlocks]

**Recommendation**: [Option X] because [brief rationale]

---

## 🚨 Critical Alerts

**Blockers**:
- 🛑 [Blocker 1]: [Description, impact, needed to unblock]
- 🛑 [Blocker 2]: [Description, impact, needed to unblock]

**Bugs Discovered**:
- 🐛 [Bug 1]: [Description, severity, workaround]
- 🐛 [Bug 2]: [Description, severity, workaround]

**Design Flaws**:
- ⚠️ [Flaw 1]: [Description, impact on future work]
- ⚠️ [Flaw 2]: [Description, impact on future work]

**System Decisions Requiring Review**:
- 🤔 [Decision 1]: [What needs review, why it matters]
- 🤔 [Decision 2]: [What needs review, why it matters]

---

## 📚 Context for Next Session

**What the Next Agent Needs to Know**:
1. [Key context point 1]
2. [Key context point 2]
3. [Key context point 3]

**Assumptions Made**:
- [Assumption 1]: [Why this assumption, how to validate]
- [Assumption 2]: [Why this assumption, how to validate]

**Open Questions**:
- [Question 1]: [Why this matters, who should answer]
- [Question 2]: [Why this matters, who should answer]

**Recommended Reading** (if applicable):
- [Doc 1]: [Why relevant]
- [Doc 2]: [Why relevant]

---

## 🔗 Links

- **PRD**: [Link if relevant]
- **Tech Requirements**: [Link if relevant]
- **Architecture Diagram**: [Link if updated]
- **GitHub Commits**: [Links to commits]
- **Notion Updates**: [Links to Notion pages updated]

---

## ⏱️ Time Breakdown

| Activity | Time Spent |
|----------|------------|
| Planning | X min |
| Coding | X min |
| Testing | X min |
| Debugging | X min |
| Documentation | X min |
| **Total** | **X hours Y min** |
```

Validation: Create a sample session log for today's session using this template

---

### Step 5: Create Architecture Diagram Template (30 minutes)

File: docs/architecture/TEMPLATE.mermaid.md

```markdown
# Architecture: [System Name]

**Last Updated**: [YYYY-MM-DD]  
**Owner**: [Your name]

---

## System Overview

```

graph TB

```javascript

**Components**:
- **Input System**: [Purpose and responsibilities]
- **Processing Engine**: [Purpose and responsibilities]
- **Output System**: [Purpose and responsibilities]
- **Storage**: [Purpose and responsibilities]

---

## Data Flow

```

sequenceDiagram

```javascript

**Flow Steps**:
1. [Step 1]: [What happens]
2. [Step 2]: [What happens]
3. [Step 3]: [What happens]

---

## Component Details

### [Component Name]

```

graph LR

```javascript

**Responsibilities**:
- [Responsibility 1]
- [Responsibility 2]

**Dependencies**:
- [Dependency 1]
- [Dependency 2]

---

## Future Enhancements

```

graph TB

```javascript

**Planned Additions**:
- [Enhancement 1]: [When and why]
- [Enhancement 2]: [When and why]
```

Validation: Create architecture diagram for "Context Sync Bridge" using this template

---

### Step 6: Create Documentation Index (30 minutes)

File: docs/README.md

```markdown
# AI Assistant Documentation

**Last Updated**: [YYYY-MM-DD]

This folder contains all project documentation organized by type.

---

## 📁 Folder Structure

```

docs/

├── prd/                    # Product Requirements Documents

│   ├── TEMPLATE.md

│   └── [feature].md

├── tech-requirements/     # Technical Implementation Plans

│   ├── TEMPLATE.md

│   └── [feature].md

├── sessions/              # Session Logs

│   ├── TEMPLATE.md

│   ├── claude-chat/

│   │   └── YYYY-MM-DD-[topic].md

│   └── claude-code/

│       └── YYYY-MM-DD-[topic].md

├── architecture/          # System Diagrams

│   ├── TEMPLATE.mermaid.md

│   └── diagrams/

└── README.md              # This file

```javascript

---

## 📝 Document Types

### PRDs (Product Requirements Documents)
**Purpose**: Define WHAT to build and WHY  
**Owner**: Claude (strategy agent)  
**Audience**: Both agents + future collaborators

**When to Create**:
- Before starting any new feature
- When requirements change significantly
- When needing stakeholder alignment

**Template**: `prd/TEMPLATE.md`

---

### Tech Requirements
**Purpose**: Define HOW to build and implementation details  
**Owner**: Claude Code (implementation agent)  
**Audience**: Developers + technical reviewers

**When to Create**:
- After PRD is approved
- Before writing any code
- When architecture decisions needed

**Template**: `tech-requirements/TEMPLATE.md`

---

### Session Logs
**Purpose**: Record what happened in each work session  
**Owner**: Both agents (whoever did the work)  
**Audience**: Future self, other agent, collaborators

**When to Create**:
- End of every work session
- After major decisions or breakthroughs
- When context needs to be preserved

**Template**: `sessions/TEMPLATE.md`

---

### Architecture Diagrams
**Purpose**: Visualize system structure and data flow  
**Owner**: Both agents (as needed)  
**Audience**: Anyone needing to understand the system

**When to Create**:
- During architecture design phase
- When explaining complex systems
- For onboarding new collaborators

**Template**: `architecture/TEMPLATE.mermaid.md`

---

## 🔄 Documentation Workflow

### Creating New Features

1. **Claude (Chat)**: Write PRD in `prd/[feature].md`
2. **Claude Code**: Write tech req in `tech-requirements/[feature].md`
3. **Claude Code**: Implement feature
4. **Claude Code**: Update session log in `sessions/claude-code/YYYY-MM-DD-[feature].md`
5. **Git**: Commit with message referencing PRD/tech req
6. **Notion**: Auto-syncs via git hook

### Strategic Decisions

1. **Claude (Chat)**: Discuss strategy, make decisions
2. **Claude (Chat)**: Update relevant PRD with decisions
3. **Claude (Chat)**: Create session log in `sessions/claude-chat/YYYY-MM-DD-[topic].md`
4. **Git**: Commit session log
5. **Notion**: Auto-syncs decisions to roadmap

---

## 🔍 Finding Documents

### By Feature
1. Look in `prd/` for product context
2. Look in `tech-requirements/` for implementation details
3. Look in `sessions/` for development history

### By Date
1. Look in `sessions/claude-chat/` or `sessions/claude-code/`
2. Files named `YYYY-MM-DD-[topic].md`
3. Use `git log` to see commit history

### By Agent
- **Claude Chat**: `sessions/claude-chat/`
- **Claude Code**: `sessions/claude-code/`

---

## 🤖 MCP Tools (For Claude)

Claude can automatically read these docs using MCP tools:

```

# Read a PRD

"Read PRD for [feature name]"

# Read tech requirements

"Read tech requirements for [feature name]"

# Find recent sessions

"Show me the last 3 session logs"

# Search across all docs

"Search docs for 'icon matching'"

```javascript

---

## 🔗 Related Documentation

- **Project Root**: `../README.md` (project overview)
- **Old Docs**: `../docs-old/` (pre-Tier 0 docs, archived)
- **Notion Roadmap**: [Link to Notion]
- **GitHub Repo**: [Link to repo]

---

**Maintained by**: Dharan + Claude + Claude Code  
**Questions?**: Ask in Claude chat or create GitHub issue
```

Validation: Verify all links work, folder structure matches

---

### Phase 1B Success Criteria

Estimated Time: 4-6 hours total

---

## 🔗 Phase 2: Git Hooks + Notion Sync (Day 3-4)

Time Estimate: 6-8 hours

Owner: Claude Code

Dependencies: Phase 1B complete (docs structure exists)

### Goal

Automate the flow: git commit → parse commit → update Notion roadmap/sessions

---

### Step 1: Create Post-Commit Hook (1 hour)

File: .git/hooks/post-commit

```bash
#!/bin/bash
#
# Post-commit hook: Sync to Notion after each commit
# Triggered automatically after 'git commit'
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'  # No color

echo "${YELLOW}[Post-Commit Hook] Starting Notion sync...${NC}"

# Extract commit info
COMMIT_MSG=$(git log -1 --pretty=%B)
COMMIT_HASH=$(git log -1 --pretty=%h)
COMMIT_AUTHOR=$(git log -1 --pretty=%an)
COMMIT_DATE=$(git log -1 --pretty=%ai)
FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD | tr '\n' ',')

# Call Python sync script
if python3 scripts/sync_to_notion.py \
  --commit-msg "$COMMIT_MSG" \
  --commit-hash "$COMMIT_HASH" \
  --commit-author "$COMMIT_AUTHOR" \
  --commit-date "$COMMIT_DATE" \
  --files "$FILES_CHANGED"; then
  
  echo "${GREEN}[Post-Commit Hook] ✓ Notion sync complete${NC}"
else
  echo "${RED}[Post-Commit Hook] ✗ Notion sync failed (non-blocking)${NC}"
  echo "${YELLOW}    You can manually sync later with: python3 scripts/sync_to_notion.py${NC}"
fi

# Auto-push to GitHub (backup)
echo "${YELLOW}[Post-Commit Hook] Pushing to GitHub...${NC}"
if git push origin main 2>&1 | grep -q "Everything up-to-date\|branch is ahead\|done"; then
  echo "${GREEN}[Post-Commit Hook] ✓ Pushed to GitHub${NC}"
else
  echo "${RED}[Post-Commit Hook] ✗ GitHub push failed${NC}"
  echo "${YELLOW}    You can manually push later with: git push${NC}"
fi

echo "${GREEN}[Post-Commit Hook] All done!${NC}"
```

Make executable:

```bash
chmod +x .git/hooks/post-commit
```

Validation:

- Create a test commit: git commit --allow-empty -m "Test hook"

- Verify hook runs (see output in terminal)

- Verify script is called (even if it fails due to missing script)

---

### Step 2: Create Notion Sync Script (4-5 hours)

File: scripts/sync_to_notion.py

```python
#!/usr/bin/env python3
"""
Notion Sync Script

Syncs git commits to Notion databases:
1. Parse commit for roadmap item references
2. Update Roadmap database (status, last updated)
3. Create session log in Sessions database
4. Link to relevant PRD/tech docs

Usage:
    python3 sync_to_notion.py \
      --commit-msg "[ROADMAP-123] Implement feature" \
      --commit-hash "abc123" \
      --commit-author "Dharan" \
      --commit-date "2025-11-08 10:00:00" \
      --files "file1.py,file2.md"
"""

import os
import sys
import argparse
import re
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.notion.client import NotionClient

# Notion database IDs (from environment)
ROADMAP_DB_ID = os.getenv("NOTION_ROADMAP_DB")  # You'll need to create this
SESSIONS_DB_ID = os.getenv("NOTION_SESSIONS_DB")  # You'll need to create this

class NotionSyncEngine:
    """Syncs git commits to Notion databases"""
    
    def __init__(self):
        self.client = NotionClient()
        self.roadmap_db = ROADMAP_DB_ID
        self.sessions_db = SESSIONS_DB_ID
    
    def extract_roadmap_refs(self, commit_msg: str) -> list[str]:
        """
        Extract roadmap item references from commit message.
        
        Format: [ROADMAP-123] or [roadmap-456]
        
        Args:
            commit_msg: Git commit message
        
        Returns:
            List of roadmap item IDs
        """
        pattern = r"\[ROADMAP-(\d+)\]"
        matches = re.findall(pattern, commit_msg, re.IGNORECASE)
        return matches
    
    def update_roadmap_status(self, item_id: str, status: str = "In Progress"):
        """
        Update roadmap item status in Notion.
        
        Args:
            item_id: Roadmap item ID (e.g., "123")
            status: New status (default: "In Progress")
        """
        # TODO: Implement Notion API call to update roadmap item
        # This requires:
        # 1. Query Roadmap database for item with matching ID
        # 2. Update the Status property
        # 3. Update Last Updated timestamp
        
        print(f"  → Updating roadmap item {item_id} to '{status}'")
        # Placeholder for now
        pass
    
    def create_session_log(
        self,
        agent: str,
        commit_msg: str,
        commit_hash: str,
        commit_author: str,
        commit_date: str,
        files_changed: str
    ) -> dict:
        """
        Create session log entry in Notion.
        
        Args:
            agent: "Claude Code" or "Claude Chat"
            commit_msg: Git commit message
            commit_hash: Short commit hash
            commit_author: Commit author name
            commit_date: Commit timestamp
            files_changed: Comma-separated file paths
        
        Returns:
            Dict with Notion page URL and ID
        """
        # TODO: Implement Notion API call to create session log
        # This requires:
        # 1. Create new page in Sessions database
        # 2. Set Title, Agent, Project, What Shipped, Git Commit, Session Date
        # 3. Return page URL
        
        print(f"  → Creating session log for commit {commit_hash}")
        # Placeholder for now
        return {
            "url": f"https://notion.so/session-{commit_hash}",
            "id": "placeholder"
        }
    
    def sync_commit(
        self,
        commit_msg: str,
        commit_hash: str,
        commit_author: str,
        commit_date: str,
        files_changed: str
    ) -> dict:
        """
        Main sync function: parse commit and update Notion.
        
        Args:
            commit_msg: Git commit message
            commit_hash: Short commit hash
            commit_author: Commit author name
            commit_date: Commit timestamp
            files_changed: Comma-separated file paths
        
        Returns:
            Dict with sync results
        """
        print(f"\nSyncing commit {commit_hash}: {commit_msg}")
        
        # Extract roadmap references
        roadmap_items = self.extract_roadmap_refs(commit_msg)
        print(f"  Found {len(roadmap_items)} roadmap references")
        
        # Update each roadmap item
        for item_id in roadmap_items:
            self.update_roadmap_status(item_id, "In Progress")
        
        # Determine agent (Claude Code for code commits, Claude Chat for docs)
        if any(f.endswith('.py') for f in files_changed.split(',')):
            agent = "Claude Code"
        elif any(f.startswith('docs/prd') or f.startswith('docs/sessions/claude-chat') for f in files_changed.split(',')):
            agent = "Claude Chat"
        else:
            agent = "Unknown"
        
        # Create session log
        session_log = self.create_session_log(
            agent=agent,
            commit_msg=commit_msg,
            commit_hash=commit_hash,
            commit_author=commit_author,
            commit_date=commit_date,
            files_changed=files_changed
        )
        
        print(f"  ✓ Session log created: {session_log['url']}")
        
        return {
            "roadmap_items_updated": len(roadmap_items),
            "session_log": session_log
        }

def main():
    """CLI entrypoint"""
    parser = argparse.ArgumentParser(description="Sync git commits to Notion")
    parser.add_argument("--commit-msg", required=True, help="Commit message")
    parser.add_argument("--commit-hash", required=True, help="Short commit hash")
    parser.add_argument("--commit-author", required=True, help="Commit author")
    parser.add_argument("--commit-date", required=True, help="Commit date")
    parser.add_argument("--files", required=True, help="Comma-separated file paths")
    
    args = parser.parse_args()
    
    # Check for required environment variables
    if not ROADMAP_DB_ID:
        print("WARNING: NOTION_ROADMAP_DB not set (Notion sync disabled)")
        return
    
    if not SESSIONS_DB_ID:
        print("WARNING: NOTION_SESSIONS_DB not set (Notion sync disabled)")
        return
    
    # Sync to Notion
    engine = NotionSyncEngine()
    result = engine.sync_commit(
        commit_msg=args.commit_msg,
        commit_hash=args.commit_hash,
        commit_author=args.commit_author,
        commit_date=args.commit_date,
        files_changed=args.files
    )
    
    print(f"\n✓ Sync complete: {result['roadmap_items_updated']} roadmap items updated")

if __name__ == "__main__":
    main()
```

Make executable:

```bash
chmod +x scripts/sync_to_notion.py
```

Validation:

- Run manually: python3 scripts/sync_to_notion.py --commit-msg "[ROADMAP-1] Test" --commit-hash "abc123" --commit-author "Test" --commit-date "2025-11-08" --files "test.py"

- Verify it runs without errors (may not update Notion yet, but shouldn't crash)

---

### Step 3: Create Notion Databases (1-2 hours)

This step you'll do manually in Notion. Create these two databases:

1. Roadmap Database:

- Name: "Roadmap (Epic 2nd Brain)"

- Properties:

  - Feature Name (Title)

  - Status (Select): Backlog, In Progress, Blocked, Shipped

  - Priority (Select): P0, P1, P2, P3

  - Owner (Person): You

  - Project (Relation): Links to Projects database

  - PRD Link (URL): Link to GitHub docs/prd/

  - Tech Req Link (URL): Link to GitHub docs/tech-requirements/

  - Last Updated (Last Edited Time)

  - Notes (Text): Quick context

2. Sessions Database:

- Name: "Sessions (Epic 2nd Brain)"

- Properties:

  - Title (Title): Auto-generated "Session: [Date] - [Agent]"

  - Agent (Select): Claude, Claude Code

  - Project (Relation): Links to Projects database

  - Duration (Number): Minutes

  - What Shipped (Text)

  - Decisions Made (Text)

  - Next Steps (Text)

  - Critical Alerts (Text)

  - Git Commit (URL): Link to commit

  - Session Date (Date)

After creating:

1. Get database IDs from URLs (the long ID in the Notion URL)

1. Add to .env:

```bash
NOTION_ROADMAP_DB=your_roadmap_db_id_here
NOTION_SESSIONS_DB=your_sessions_db_id_here
```

Validation:

- Manually create 1 roadmap item

- Manually create 1 session log

- Verify properties display correctly

---

### Step 4: Implement Notion API Calls (2-3 hours)

Now update the sync_to_notion.py script with actual Notion API calls:

Update update_roadmap_status() method:

```python
def update_roadmap_status(self, item_id: str, status: str = "In Progress"):
    """
    Update roadmap item status in Notion.
    """
    # Query for roadmap item with matching ID
    # Note: You'll need a "Roadmap ID" property in Notion to match against
    
    query_response = self.client.query_database(
        database_id=self.roadmap_db,
        filter={
            "property": "Roadmap ID",  # Add this property to Notion
            "rich_text": {
                "equals": item_id
            }
        }
    )
    
    if query_response["results"]:
        page_id = query_response["results"][0]["id"]
        
        # Update status
        self.client.update_page(
            page_id=page_id,
            properties={
                "Status": {
                    "select": {
                        "name": status
                    }
                }
            }
        )
        print(f"  ✓ Updated roadmap item {item_id} to '{status}'")
    else:
        print(f"  ✗ Roadmap item {item_id} not found")
```

Update create_session_log() method:

```python
def create_session_log(
    self,
    agent: str,
    commit_msg: str,
    commit_hash: str,
    commit_author: str,
    commit_date: str,
    files_changed: str
) -> dict:
    """
    Create session log entry in Notion.
    """
    # Format title
    date_str = datetime.fromisoformat(commit_date).strftime("%Y-%m-%d")
    title = f"Session: {date_str} - {agent}"
    
    # Create page in Sessions database
    response = self.client.create_page(
        parent={"database_id": self.sessions_db},
        properties={
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Agent": {
                "select": {
                    "name": agent
                }
            },
            "What Shipped": {
                "rich_text": [
                    {
                        "text": {
                            "content": commit_msg
                        }
                    }
                ]
            },
            "Git Commit": {
                "url": f"https://github.com/[your-username]/ai-assistant/commit/{commit_hash}"
            },
            "Session Date": {
                "date": {
                    "start": commit_date
                }
            }
        }
    )
    
    return {
        "url": response["url"],
        "id": response["id"]
    }
```

Validation:

- Create test commit with [ROADMAP-1] in message

- Verify roadmap item status updates in Notion

- Verify session log appears in Notion

- Verify all fields populated correctly

---

### Phase 2 Success Criteria

Estimated Time: 6-8 hours total

---

## 🤖 Phase 3: Claude Chat Integration (Day 5-6)

Time Estimate: 4-6 hours

Owner: Claude Code

Dependencies: Phase 1A complete (MCP proven working), Phase 1B complete (docs exist)

### Goal

Expand MCP server so Claude can automatically load context at session start and log context at session end.

---

### Step 1: Expand MCP Server (3-4 hours)

File: mcp_server/full_server.py

```python
#!/usr/bin/env python3
"""
Full MCP Server for AI Assistant Project

Provides tools for Claude to:
1. Read project documentation
2. Start sessions (auto-load context)
3. End sessions (auto-log work)
4. Search across docs (RAG)
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Add project root to path
project_root = Path.home() / "ai-assistant"
sys.path.insert(0, str(project_root))

# Initialize MCP server
app = Server("ai-assistant")

# ============================================================================
# TOOL 1: Read Files
# ============================================================================

@app.tool()
async def read_file(path: str) -> str:
    """
    Read a file from the ai-assistant repo.
    
    Args:
        path: Relative path from repo root (e.g., 'docs/prd/feature.md')
    
    Returns:
        File contents as string
    """
    full_path = project_root / path
    
    if not full_path.exists():
        return f"Error: File not found at {full_path}"
    
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

# ============================================================================
# TOOL 2: Start Session
# ============================================================================

@app.tool()
async def start_session(project_name: str = "Epic 2nd Brain") -> dict:
    """
    Load all context needed for a Claude chat session.
    
    Fetches:
    - Latest PRD(s) for this project
    - Latest tech requirements
    - Recent session logs (last 3)
    - Open roadmap items (from Notion)
    - Critical alerts
    
    Args:
        project_name: Name of project (default: "Epic 2nd Brain")
    
    Returns:
        Dict with all context
    """
    context = {
        "project": project_name,
        "timestamp": datetime.now().isoformat(),
        "prds": [],
        "tech_requirements": [],
        "recent_sessions": [],
        "roadmap": {},
        "alerts": []
    }
    
    # Load PRDs
    prd_dir = project_root / "docs" / "prd"
    if prd_dir.exists():
        for prd_file in sorted(prd_dir.glob("*.md"), reverse=True):
            if prd_file.name != "TEMPLATE.md":
                with open(prd_file) as f:
                    context["prds"].append({
                        "file": prd_file.name,
                        "content": f.read()[:1000]  # First 1000 chars
                    })
                if len(context["prds"]) >= 2:  # Max 2 PRDs
                    break
    
    # Load tech requirements
    tech_dir = project_root / "docs" / "tech-requirements"
    if tech_dir.exists():
        for tech_file in sorted(tech_dir.glob("*.md"), reverse=True):
            if tech_file.name != "TEMPLATE.md":
                with open(tech_file) as f:
                    context["tech_requirements"].append({
                        "file": tech_file.name,
                        "content": f.read()[:1000]
                    })
                if len(context["tech_requirements"]) >= 2:
                    break
    
    # Load recent sessions
    sessions_dir = project_root / "docs" / "sessions"
    for agent_dir in ["claude-chat", "claude-code"]:
        agent_path = sessions_dir / agent_dir
        if agent_path.exists():
            for session_file in sorted(agent_path.glob("*.md"), reverse=True)[:3]:
                with open(session_file) as f:
                    context["recent_sessions"].append({
                        "file": session_file.name,
                        "agent": agent_dir,
                        "content": f.read()[:500]  # Summary only
                    })
    
    # TODO: Fetch from Notion (roadmap, alerts)
    # For now, placeholder
    context["roadmap"] = {
        "in_progress": "[Fetch from Notion]",
        "blocked": "[Fetch from Notion]"
    }
    context["alerts"] = ["[Fetch from Notion]"]
    
    return context

# ============================================================================
# TOOL 3: End Session
# ============================================================================

@app.tool()
async def end_session(
    project_name: str,
    summary: str,
    decisions: list[str] = None,
    next_steps: list[str] = None
) -> dict:
    """
    Log Claude chat session to docs/ and Notion.
    
    Args:
        project_name: Project name
        summary: Brief summary of session
        decisions: List of key decisions made
        next_steps: List of recommended next actions
    
    Returns:
        Dict with log path and Notion URL
    """
    decisions = decisions or []
    next_steps = next_steps or []
    
    # Generate session log filename
    date_str = datetime.now().strftime("%Y-%m-%d")
    topic = summary.lower().replace(" ", "-")[:30]
    filename = f"{date_str}-{topic}.md"
    
    log_path = project_root / "docs" / "sessions" / "claude-chat" / filename
    
    # Write session log
    with open(log_path, 'w') as f:
        f.write(f"# Session: {date_str} - Claude Chat\n\n")
        f.write(f"**Project**: {project_name}\n")
        f.write(f"**Status**: Complete\n\n")
        f.write(f"---\n\n")
        f.write(f"## Summary\n\n{summary}\n\n")
        
        if decisions:
            f.write(f"## Decisions Made\n\n")
            for i, decision in enumerate(decisions, 1):
                f.write(f"{i}. {decision}\n")
            f.write("\n")
        
        if next_steps:
            f.write(f"## Next Steps\n\n")
            for i, step in enumerate(next_steps, 1):
                f.write(f"{i}. {step}\n")
            f.write("\n")
    
    # TODO: Sync to Notion
    # For now, placeholder
    notion_url = "[Will be synced on next git commit]"
    
    return {
        "log_path": str(log_path),
        "notion_url": notion_url,
        "reminder": "Don't forget to commit this session log!"
    }

# ============================================================================
# TOOL 4: Search Docs (Basic RAG)
# ============================================================================

@app.tool()
async def search_docs(
    query: str,
    doc_types: list[str] = None
) -> list[dict]:
    """
    Search across project documentation.
    
    Args:
        query: Search query (keywords or phrase)
        doc_types: Types to search (default: all)
                   Options: "prd", "tech-req", "sessions"
    
    Returns:
        List of relevant doc snippets with context
    """
    doc_types = doc_types or ["prd", "tech-req", "sessions"]
    results = []
    
    # Map doc types to folders
    folder_map = {
        "prd": project_root / "docs" / "prd",
        "tech-req": project_root / "docs" / "tech-requirements",
        "sessions": project_root / "docs" / "sessions"
    }
    
    # Simple keyword search (can enhance with semantic search later)
    query_lower = query.lower()
    
    for doc_type in doc_types:
        folder = folder_map.get(doc_type)
        if not folder or not folder.exists():
            continue
        
        # Search all markdown files
        for md_file in folder.rglob("*.md"):
            if md_file.name == "TEMPLATE.md":
                continue
            
            with open(md_file) as f:
                content = f.read()
                content_lower = content.lower()
                
                # Check if query appears
                if query_lower in content_lower:
                    # Find context around match
                    idx = content_lower.find(query_lower)
                    start = max(0, idx - 100)
                    end = min(len(content), idx + 100)
                    snippet = content[start:end]
                    
                    results.append({
                        "file": str(md_file.relative_to(project_root)),
                        "doc_type": doc_type,
                        "snippet": f"...{snippet}...",
                        "relevance": "high" if query_lower in content_lower[:500] else "medium"
                    })
    
    # Sort by relevance and return top 5
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results[:5]

# ============================================================================
# Server Entry Point
# ============================================================================

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

Update Claude Desktop config (~/Library/Application Support/Claude/claude_desktop_config.json):

```json
{
  "mcpServers": {
    "ai-assistant": {
      "command": "python3",
      "args": [
        "/Users/[YOUR_USERNAME]/ai-assistant/mcp_server/full_server.py"
      ],
      "env": {}
    }
  }
}
```

Restart Claude Desktop

Validation:

- "Start session for Epic 2nd Brain" → Returns full context

- "Search docs for 'icon matching'" → Returns relevant snippets

- "End session with summary 'Completed roadmap'" → Creates session log

---

### Step 2: Test All MCP Tools (1-2 hours)

Test Suite (run in Claude Desktop):

```javascript
Test 1: Start Session
"Use start_session tool for Epic 2nd Brain"

Expected:
- Returns PRDs, tech reqs, recent sessions
- Shows roadmap placeholder
- No errors

Test 2: Search Docs
"Use search_docs tool to find 'MCP server'"

Expected:
- Returns relevant file snippets
- Includes file paths
- Ranked by relevance

Test 3: End Session
"Use end_session tool with:
- project: Epic 2nd Brain
- summary: Tested MCP tools
- decisions: ['MCP server works', 'Ready for Week 2']
- next_steps: ['Build Notion dashboard', 'Implement RAG']
"

Expected:
- Creates session log file
- Returns file path
- Reminds to commit

Test 4: Read File
"Use read_file tool to read docs/README.md"

Expected:
- Returns full README content
- No errors
```

Success Criteria:

---

### Phase 3 Success Criteria

Estimated Time: 4-6 hours total

---

[Continuing in next message due to length...]

## 📊 Phase 4: Notion Dashboard (Day 7-9)

Time Estimate: 6-8 hours

Owner: You (manual Notion setup) + Claude (guidance)

Dependencies: Phase 2 complete (Notion databases created)

### Goal

Create visual command center in Notion for 15-minute morning ritual.

---

Step 1: Create Command Center Page (2 hours)

Location: Under "Epic 2nd Brain Workflow" project in Notion

Page Structure:

# 🎯 Command Center
*Last Updated: [Auto-updated from databases]*

---

## 🎯 Active Projects
[Linked Database View: Projects, Gallery View]
- Filter: Status = Active
- Display: Project name, health indicator, phase

---

## 🚀 In Progress (This Week)
[Linked Database View: Roadmap, Board View]
- Group by: Status
- Filter: Status IN [In Progress, Blocked]
- Sort: Priority (P0 first)

---

## 📊 Recent Activity
[Linked Database View: Sessions, Timeline View]
- Sort: Session Date (newest first)
- Filter: Last 7 days
- Display: Title, Agent, What Shipped

---

## 🚨 Critical Alerts
[Linked Database View: Sessions, Table View]
- Filter: Critical Alerts IS NOT EMPTY
- Sort: Session Date (newest first)
- Display: Alert text, Session link

Validation:

- Open Command Center page

- Verify all linked databases show correct data

- Test filters work

- Accessible from mobile

---

Step 2: Create Project Deep-Dive Template (2 hours)

Template Structure:

# Project: [Name]

## Quick Status
- **Phase**: [Discovery | Design | Build | Test | Ship]
- **Health**: 🟢 On Track | 🟡 At Risk | 🔴 Blocked
- **Last Updated**: [Auto from database]

---

## 🏗️ Architecture
[Link to architecture diagram in GitHub]

**Key Components**:
1. [Component 1]: [Purpose]
2. [Component 2]: [Purpose]

---

## 🎯 Active Work
[Linked Database: Roadmap]
- Filter: Project = THIS PROJECT AND Status IN [In Progress, Blocked]
- View: Board

---

## 📝 Recent Sessions
[Linked Database: Sessions]
- Filter: Project = THIS PROJECT
- Sort: Session Date (newest)
- Limit: Last 5

---

## 📚 Key Documents
**PRDs**: [Links to GitHub]
**Tech Requirements**: [Links to GitHub]
**Architecture**: [Links to GitHub]

---

Step 3: Configure Database Views (2-4 hours)

Roadmap Database Views:

1. Board View (default): Group by Status

1. Table View: Show all properties

1. Timeline View: For roadmap planning

Sessions Database Views:

1. Timeline View (default): Group by Agent

1. Table View: All details

1. Alerts View: Filter for Critical Alerts only

---

Phase 4 Success Criteria

Estimated Time: 6-8 hours total

---

## 🔍 Phase 5: RAG Search (Repo-Only) (Day 10-12)

Time Estimate: 6-8 hours

Owner: Claude Code

Dependencies: Phase 3 complete (MCP tools working)

### Goal

Upgrade basic keyword search to semantic search with relevance scoring.

---

Step 1: Enhanced Search Implementation (4-5 hours)

Update mcp_server/full_server.py → search_docs() function:

python

def calculate_relevance_score(query: str, content: str, file_path: str) -> float:
    """
    Calculate relevance score (0-100) based on:
    - Keyword frequency (max 30 points)
    - Position in document (max 20 points)
    - File type (max 20 points: PRD > tech-req > sessions)
    - Recency (max 30 points: newer = higher score)
    """
    score = 0
    query_lower = query.lower()
    content_lower = content.lower()
    
    # Factor 1: Keyword frequency
    keyword_count = content_lower.count(query_lower)
    score += min(keyword_count * 5, 30)
    
    # Factor 2: Position (earlier = more relevant)
    first_occurrence = content_lower.find(query_lower)
    if first_occurrence >= 0:
        position_score = 20 * (1 - (first_occurrence / len(content)))
        score += position_score
    
    # Factor 3: File type priority
    if 'prd' in file_path:
        score += 20
    elif 'tech-requirements' in file_path:
        score += 15
    elif 'sessions' in file_path:
        score += 10
    
    # Factor 4: Recency (newer files score higher)
    import re
    from datetime import datetime
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path)
    if date_match:
        file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
        days_old = (datetime.now() - file_date).days
        recency_score = max(0, 30 - (days_old / 10))
        score += recency_score
    
    return score

@app.tool()
async def search_docs(
    query: str,
    doc_types: list[str] = None,
    max_results: int = 5
) -> list[dict]:
    """Enhanced search with relevance scoring"""
    # [Implementation that uses calculate_relevance_score]# Returns results sorted by score

---

Step 2: Test Search Quality (2-3 hours)

Test Suite (10 queries):

Test 1: "architecture decision"
Expected: Tech requirements, session logs with high scores

Test 2: "notion sync"
Expected: Recent tech req about git hooks

Test 3: "MCP tools"
Expected: Tech req + session logs about MCP

Test 4: "roadmap item"
Expected: Sessions mentioning roadmap updates

Test 5: "context sync"
Expected: PRD, tech req, sessions (all relevant)

Test 6: "[specific phrase from a doc]"
Expected: That exact doc with high score

Test 7: "[gibberish query]"
Expected: Empty results or very low scores

Test 8-10: [Your real questions from daily work]

Success Criteria: 8/10 queries return useful results

---

Phase 5 Success Criteria

Estimated Time: 6-8 hours total

## ✅ Phase 6: Testing & Validation (Day 13-14)

Time Estimate: 3-4 hours

Owner: You + Claude + Claude Code

Dependencies: All previous phases complete

### Goal

Validate 2x leverage achieved and document lessons learned.

---

Validation Test Suite

Test 1: Context Sync (30 minutes)

bash

# Make test commit
cd ~/ai-assistant
echo "# Test" > test.md
git add test.md
git commit -m "[ROADMAP-999] Test context sync"

# Verify:
1. Post-commit hook ran
2. Notion updated within 30 seconds
3. Session log created in Notion
4. GitHub shows pushed commit

Expected: All pass ✅

Test 2: Claude Start Session (30 minutes)

In Claude Desktop:
"Start session for Epic 2nd Brain"

Verify:
1. Returns at least 1 PRD
2. Returns at least 1 tech requirement
3. Returns at least 1 recent session
4. Shows roadmap status
5. Completes in <10 seconds

Expected: Full context loaded ✅

Test 3: Handoff Test (1 hour)

Day 13 Morning (Claude Chat):
1. Start session
2. Discuss: "Let's add error handling to MCP"
3. Update PRD with decision
4. End session, commit log

Day 13 Afternoon (Claude Code):
1. Read PRD (via MCP or manual)
2. Implement error handling
3. Commit: "[ROADMAP-999] Add error handling"
4. Verify Notion updates

Day 14 Morning (Claude Chat):
1. Start session
2. Ask: "What did Claude Code ship yesterday?"
3. Verify: Claude finds yesterday's session
4. Verify: Can discuss without re-explaining

Expected: No manual copy-paste needed ✅

Test 4: Dashboard Test (30 minutes)

Desktop:
1. Open Command Center
2. Verify projects, roadmap, sessions, alerts show correctly
3. Click through to project deep-dive
4. Verify links to GitHub docs work

Mobile (iPhone):
5. Open Command Center
6. Verify readable and navigable
7. Can check status on the go

Expected: 15-min morning ritual works ✅

Test 5: RAG Search Test (30 minutes)

In Claude Desktop:
1. "Search docs for 'MCP server implementation'"
   → Returns tech req and sessions with scores

2. "Search docs for 'architecture decision about git hooks'"
   → Returns relevant tech req with context

3. "Search docs for 'what shipped last week'"
   → Returns recent session logs

Expected: All 3 return useful results in <2 seconds ✅

Test 6: Time Saved Measurement (1 hour)

Baseline (simulate old workflow):
1. Time: Load context manually (copy-paste from old chat)
2. Time: Search for "when did we decide X"
3. Time: Update Notion manually with summary

Total baseline: [X minutes]

New workflow (Tier 0 system):
1. Time: "Start session" → context loaded
2. Time: "Search docs for X" → answer found
3. Time: "End session" → log created

Total new time: [Y minutes]

Time saved: [X - Y] minutes
Target: 50%+ reduction

Expected: At least 50% time saved ✅

---

Success Scorecard

MetricTargetActualPass?Context loading time<3 min___ min☐Copy-paste events/session<2___☐"What changed?" moments0/week___☐Notion sync speed<30 sec___ sec☐Search speed<2 sec___ sec☐Dashboard mobile accessWorks☐/☑☐Time saved per session50%+___%☐Overall: 2x Leverage?Yes☐/☑☐

Target: At least 6/8 checks pass

---

Phase 6 Success Criteria

Estimated Time: 3-4 hours total

---

## 🎓 Lessons Learned & Retrospective

To be filled in after Week 2 completion

### What Worked Well

- [Document after validation]

### What Didn't Work

- [Document after validation]

### Unexpected Challenges

- [Document after validation]

### What We'd Do Differently

- [Document after validation]

### Recommendations for Tier 1

- [Document after validation]

## 🚀 Tier 1 Priorities (Next Steps)

To be defined after Tier 0 validation

Candidates (pending validation):

1. Notion RAG expansion (search across PARA)

1. Semantic search upgrade (embeddings + vector DB)

1. Calendar sync (meetings → session blocks)

1. Email pipeline (feedback → roadmap items)

1. Advanced Figma integration (auto-export diagrams)

Decision Criteria:

- Highest leverage based on Tier 0 usage

- Addresses pain points discovered in validation

- Builds on what works

---

## 📞 Support & Troubleshooting

If MCP Server Fails:

1. Check logs: ~/Library/Logs/Claude/

1. Verify config: ~/Library/Application Support/Claude/claude_desktop_config.json

1. Test manually: python3 mcp_server/full_server.py

1. Fallback: Use manual file reading

If Git Hook Fails:

1. Check terminal output after commit

1. Verify executable: ls -la .git/hooks/post-commit

1. Run manually: python3 scripts/sync_to_notion.py ...

1. Check error logs

If Notion Sync Fails:

1. Verify database IDs in .env

1. Check Notion API permissions

1. Test client: python3 -c "from src.notion.client import NotionClient; NotionClient()"

1. Fallback: Manual Notion update

If RAG Search Quality Poor:

1. Check if docs exist in docs/

1. Try different query phrasings

1. Verify not searching TEMPLATE.md files

1. Consider semantic search upgrade in Tier 1

---

## 🎯 Final Checklist (Day 14)

Before Closing Tier 0:

Celebration Moment: 🎉

You've built a world-class development framework at solo founder scale. Context sync between Claude, Claude Code, and Notion is now automated. You're no longer the manual bridge - the system is.

Next: Use this system daily, observe what works, iterate in Tier 1.

---

Last Updated: Nov 8, 2025

Status: ✅ Implementation Plan Complete

Next Update: Nov 15, 2025 (Week 1 checkpoint)

Ready to Execute: YES 🚀

---
