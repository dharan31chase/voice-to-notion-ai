# Phase 2: Notion → Repo Sync - Technical Requirements

**Project**: Second Brain Sync
**Phase**: 2 of 6
**Status**: Ready for Implementation
**Time Estimate**: 4-6 hours
**Dependencies**: Phase 1 (PARA restructure) must be complete
**Last Updated**: 2025-12-16

---

## Table of Contents

1. [Overview](#overview)
2. [Exact Notion Schema](#exact-notion-schema)
3. [Routing Logic](#routing-logic)
4. [Frontmatter Design](#frontmatter-design)
5. [File Naming & Slug Generation](#file-naming--slug-generation)
6. [INDEX.md Generation](#indexmd-generation)
7. [Sync Engine Architecture](#sync-engine-architecture)
8. [Incremental Sync Strategy](#incremental-sync-strategy)
9. [Conflict Resolution](#conflict-resolution)
10. [Deletion Handling](#deletion-handling)
11. [Git Commit Strategy](#git-commit-strategy)
12. [Error Handling](#error-handling)
13. [Testing Strategy](#testing-strategy)
14. [Configuration Schema](#configuration-schema)
15. [Cron Setup](#cron-setup)
16. [Success Criteria](#success-criteria)
17. [Implementation Checklist](#implementation-checklist)

---

## Overview

### Purpose

Phase 2 implements **Notion → Repo sync**: pulling selected notes from Notion Notes database into the appropriate Git repo locations with proper frontmatter, file naming, and INDEX.md generation.

### Scope

**What Syncs**:
- 📝 Meeting Notes
- 📚 Book Notes
- 🎧 Podcast Notes
- 🔬 Research
- ⚙️ Framework
- 📄 Document

**Control Mechanism**:
- User manually checks "Sync to Repo" checkbox in Notion
- Explicit opt-in per note (prevents accidental syncs)

**Timing**:
- Cron schedule: 1am + 1pm daily
- Incremental sync (only changed notes)
- Expected volume: 10-20 notes/day

**Key Features**:
- Intelligent routing (repo + folder selection)
- Slug generation from Notion titles
- Frontmatter preservation with emoji stripping
- INDEX.md generation (4-level nested structure)
- Conflict resolution (most recent edit wins)
- Archive on deletion (no hard deletes)
- Grouped git commits by note type

### Out of Scope (Future Phases)

- ❌ Repo → Notion sync (Phase 3)
- ❌ RAG reindexing (Phase 4)
- ❌ On-demand sync (manual trigger)
- ❌ Bi-directional conflict resolution
- ❌ Real-time sync (webhook-based)

---

## Exact Notion Schema

### Properties in Notes Database

| Property Name | Type | Required | Description |
|---------------|------|----------|-------------|
| **Note Type** | Multi-select | Yes | One or more types (Meeting Notes, Book Notes, etc.) |
| **Project** | Relation | No | Link to Projects database |
| **Area / Resource** | Relation | Yes | Link to Areas database (for repo selection) |
| **Sync to Repo** | Checkbox | Yes | Explicit opt-in flag |
| **Source Path** | Text | No | Auto-populated after first sync |
| **Tags** | Multi-select | No | Custom tags |

### Note Type Values (Exact)

```python
NOTE_TYPES = [
    "📝 Meeting Notes",
    "📚 Book Notes",
    "🎧 Podcast Notes",
    "🔬 Research",
    "⚙️ Framework",
    "📄 Document"
]
```

**Important**: Note Type is **multi-select**. A single note can have multiple types (e.g., ["📝 Meeting Notes", "🔬 Research"]). Use the **first type** for folder routing.

### Area / Resource Values (Exact)

```python
AREA_VALUES = {
    "Epic 2nd Brain Workflow": "ai-assistant",
    "Legacy AI": "legacy-ai",
    "Life": "ai-assistant/areas/lifeadmin"
}
```

**Note**: Exact spelling and capitalization matter. These map to repository selection.

### Property Access via Notion API

```python
# Example: Reading properties from a Notion page
page = notion.pages.retrieve(page_id="...")

# Note Type (multi-select)
note_types = [nt["name"] for nt in page["properties"]["Note Type"]["multi_select"]]
# Returns: ["📝 Meeting Notes", "🔬 Research"]

# Area / Resource (relation)
area_relations = page["properties"]["Area / Resource"]["relation"]
if area_relations:
    area_id = area_relations[0]["id"]
    area_page = notion.pages.retrieve(area_id)
    area_name = area_page["properties"]["Name"]["title"][0]["plain_text"]
    # Returns: "Epic 2nd Brain Workflow"

# Project (relation)
project_relations = page["properties"]["Project"]["relation"]
if project_relations:
    project_id = project_relations[0]["id"]
    project_page = notion.pages.retrieve(project_id)
    project_name = project_page["properties"]["Name"]["title"][0]["plain_text"]
    # Returns: "Second Brain Sync"

# Sync to Repo (checkbox)
sync_enabled = page["properties"]["Sync to Repo"]["checkbox"]
# Returns: True or False

# Tags (multi-select)
tags = [t["name"] for t in page["properties"]["Tags"]["multi_select"]]
# Returns: ["legacy-ai", "fundraising"]
```

---

## Routing Logic

### Decision Hierarchy

```
1. Check "Sync to Repo" checkbox
   ├─ False → Skip sync
   └─ True → Continue

2. Repo Selection: Check "Area / Resource"
   ├─ "Epic 2nd Brain Workflow" → ai-assistant/
   ├─ "Legacy AI" → legacy-ai/
   ├─ "Life" → ai-assistant/areas/lifeadmin/
   └─ No match → DEFAULT: ai-assistant/

3. Folder Routing: Check "Project" relation
   ├─ Project exists → Project-based routing (projects/[project-name]/)
   └─ Project blank → Area-based routing (resources/ or areas/[area-name]/)

4. Note Type Subfolder: Use first Note Type
   ├─ "📝 Meeting Notes" → meeting-notes/
   ├─ "📚 Book Notes" → book-notes/
   ├─ "🎧 Podcast Notes" → podcast-notes/
   ├─ "🔬 Research" → research/
   ├─ "⚙️ Framework" → frameworks/
   └─ "📄 Document" → documents/
```

### Routing Table

| Note Type | Project Exists? | Area Only? | Destination |
|-----------|----------------|------------|-------------|
| Meeting Notes | Yes | N/A | `projects/[project-name]/meeting-notes/` |
| Meeting Notes | No | Epic 2nd Brain / Legacy AI | `resources/meeting-notes/` |
| Book Notes | Any | Any | `resources/book-notes/` |
| Podcast Notes | Any | Any | `resources/podcast-notes/` |
| Framework | Any | Any | `resources/frameworks/` |
| Document | Any | Any | `resources/documents/` |
| Research | Yes | N/A | `projects/[project-name]/research/` |
| Research | No | Area exists | `areas/[area-name]/research/` |
| Ideas | Yes | N/A | `projects/[project-name]/ideas/` |
| Ideas | No | Area exists | `areas/[area-name]/ideas/` |

**Special Case**: "Epic 2nd Brain Workflow" and "Legacy AI" are **areas** (not projects), so their meeting notes go to `resources/meeting-notes/` not `projects/*/meeting-notes/`.

### Python Implementation

```python
class RoutingEngine:
    """Determines repo and folder path for Notion notes"""

    AREA_TO_REPO = {
        "Epic 2nd Brain Workflow": "ai-assistant",
        "Legacy AI": "legacy-ai",
        "Life": "ai-assistant/areas/lifeadmin"
    }

    NOTE_TYPE_TO_FOLDER = {
        "📝 Meeting Notes": "meeting-notes",
        "📚 Book Notes": "book-notes",
        "🎧 Podcast Notes": "podcast-notes",
        "🔬 Research": "research",
        "⚙️ Framework": "frameworks",
        "📄 Document": "documents"
    }

    # Note types that always go to resources/ regardless of project
    ALWAYS_RESOURCES = {"📚 Book Notes", "🎧 Podcast Notes", "⚙️ Framework", "📄 Document"}

    def __init__(self, repo_base_paths):
        """
        repo_base_paths: dict mapping repo names to absolute paths
        Example: {"ai-assistant": "/path/to/ai-assistant", "legacy-ai": "/path/to/legacy-ai"}
        """
        self.repo_base_paths = repo_base_paths

    def route_note(self, note_properties):
        """
        Determine full file path for a Notion note

        Args:
            note_properties: dict with keys:
                - note_types: list of note type strings (e.g., ["📝 Meeting Notes"])
                - area_name: str (e.g., "Epic 2nd Brain Workflow")
                - project_name: str or None
                - title: str (Notion page title)

        Returns:
            dict with keys:
                - repo: str (repo name, e.g., "ai-assistant")
                - folder: str (relative path, e.g., "projects/second-brain-sync/meeting-notes")
                - filename: str (slugified filename, e.g., "meeting-with-peter.md")
                - full_path: str (absolute path)
        """
        # 1. Repo selection
        area_name = note_properties.get("area_name")
        repo = self.AREA_TO_REPO.get(area_name, "ai-assistant")  # Default to ai-assistant

        # Handle Life area special case (nested path)
        if repo == "ai-assistant/areas/lifeadmin":
            base_repo = "ai-assistant"
            prefix = "areas/lifeadmin"
        else:
            base_repo = repo
            prefix = ""

        # 2. Note type subfolder (use first note type)
        note_types = note_properties.get("note_types", [])
        if not note_types:
            raise ValueError("Note must have at least one Note Type")

        first_note_type = note_types[0]
        note_type_folder = self.NOTE_TYPE_TO_FOLDER.get(first_note_type)
        if not note_type_folder:
            raise ValueError(f"Unknown note type: {first_note_type}")

        # 3. Folder routing (project vs area vs resources)
        project_name = note_properties.get("project_name")

        # Always resources note types
        if first_note_type in self.ALWAYS_RESOURCES:
            folder = f"resources/{note_type_folder}"

        # Project-based routing
        elif project_name:
            project_slug = self._slugify(project_name)
            folder = f"projects/{project_slug}/{note_type_folder}"

        # Area-based routing (special cases: Epic 2nd Brain, Legacy AI are areas without projects)
        elif area_name in ["Epic 2nd Brain Workflow", "Legacy AI"]:
            # Meeting notes from areas (not projects) go to resources
            if first_note_type == "📝 Meeting Notes":
                folder = f"resources/{note_type_folder}"
            else:
                # Research, Ideas, etc. can go to area-specific folders
                area_slug = self._slugify(area_name)
                folder = f"areas/{area_slug}/{note_type_folder}"

        # No project, no area → skip
        else:
            raise ValueError("Note must have either Project or Area relation")

        # Handle Life area prefix
        if prefix:
            folder = f"{prefix}/{folder}"

        # 4. Filename (slug from title)
        title = note_properties.get("title", "untitled")
        filename = self._generate_slug(title, note_type_folder)

        # 5. Full path
        repo_base = self.repo_base_paths[base_repo]
        full_path = os.path.join(repo_base, folder, filename)

        return {
            "repo": base_repo,
            "folder": folder,
            "filename": filename,
            "full_path": full_path
        }

    def _slugify(self, text):
        """Convert text to URL-safe slug"""
        # Lowercase
        slug = text.lower()
        # Replace spaces with hyphens
        slug = slug.replace(" ", "-")
        # Remove special characters
        slug = re.sub(r'[^\w\-]', '', slug)
        # Collapse multiple hyphens
        slug = re.sub(r'-+', '-', slug)
        # Strip leading/trailing hyphens
        slug = slug.strip('-')
        return slug

    def _generate_slug(self, title, note_type_folder):
        """Generate filename slug with .md extension"""
        slug = self._slugify(title)
        return f"{slug}.md"
```

### Edge Cases

**Edge Case 1**: Note has both Project and Area
- **Resolution**: Project takes priority (Project > Area)

**Edge Case 2**: Note has neither Project nor Area
- **Resolution**: Skip sync, log warning: `"Note '{title}' skipped: no Project or Area relation"`

**Edge Case 3**: Note tagged to multiple Areas
- **Resolution**: Not possible - "Area / Resource" is single-select relation (one-to-one)

**Edge Case 4**: Life notes
- **Resolution**: Use Area/Resource = "Life" → routes to `ai-assistant/areas/lifeadmin/`

**Edge Case 5**: Epic 2nd Brain or Legacy AI get projects later
- **Resolution**: Routing logic already handles - if Project exists → use project path, else → use area path (resources/)

---

## Frontmatter Design

### Standard Frontmatter Schema

```yaml
---
title: Meeting with Peter - Fundraising Strategy
note_types: [Meeting Notes, Research]  # Array, stripped emojis
tags: [legacy-ai, fundraising]  # Array from Notion tags
created: 2025-11-10  # Notion created timestamp
last_synced: 2025-12-16T14:30:00Z  # Auto-updated by sync script
notion_url: https://notion.so/page-id
notion_page_id: abc123-def456-ghi789  # For reverse lookup
project: Second Brain Sync  # Project name (not ID), null if none
area: Epic 2nd Brain Workflow  # Area name (not ID)
---

# Meeting with Peter - Fundraising Strategy

[Notion content here...]
```

### Simplification Rules

1. **Strip emojis from note_types**:
   - Input: `["📝 Meeting Notes", "🔬 Research"]`
   - Output: `note_types: [Meeting Notes, Research]`

2. **Strip formatting from rich text**:
   - Bold, italics, links → plain text only
   - Preserves content, simplifies parsing

3. **Store names (not IDs)**:
   - `project: "Second Brain Sync"` (NOT `project_id: "abc123"`)
   - Easier to read, no reverse lookup needed

4. **Preserve arrays as YAML arrays**:
   - `note_types: [Meeting Notes, Research]`
   - `tags: [legacy-ai, fundraising]`

5. **Null for optional fields**:
   - `project: null` if no Project relation
   - `tags: null` if no Tags

### Python Implementation

```python
import re
import yaml
from datetime import datetime

class FrontmatterGenerator:
    """Generate YAML frontmatter from Notion page properties"""

    @staticmethod
    def strip_emoji(text):
        """Remove emojis from text"""
        # Regex to match emojis
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub('', text).strip()

    @staticmethod
    def strip_rich_text(rich_text_array):
        """Extract plain text from Notion rich text array"""
        if not rich_text_array:
            return ""
        return "".join([rt["plain_text"] for rt in rich_text_array])

    def generate(self, notion_page, project_name=None, area_name=None):
        """
        Generate frontmatter dict from Notion page

        Args:
            notion_page: dict (Notion API page object)
            project_name: str or None (resolved Project name)
            area_name: str or None (resolved Area name)

        Returns:
            dict (frontmatter key-value pairs)
        """
        props = notion_page["properties"]

        # Title
        title_array = props.get("Name", {}).get("title", [])
        title = self.strip_rich_text(title_array) or "Untitled"

        # Note Types (strip emojis, store as array)
        note_types_raw = [nt["name"] for nt in props.get("Note Type", {}).get("multi_select", [])]
        note_types = [self.strip_emoji(nt) for nt in note_types_raw]

        # Tags
        tags = [t["name"] for t in props.get("Tags", {}).get("multi_select", [])]

        # Created timestamp
        created_str = notion_page.get("created_time", "")
        created = datetime.fromisoformat(created_str.replace("Z", "+00:00")).strftime("%Y-%m-%d")

        # Last synced (now)
        last_synced = datetime.utcnow().isoformat() + "Z"

        # Notion URL
        notion_url = notion_page.get("url", "")
        notion_page_id = notion_page.get("id", "")

        # Build frontmatter dict
        frontmatter = {
            "title": title,
            "note_types": note_types if note_types else None,
            "tags": tags if tags else None,
            "created": created,
            "last_synced": last_synced,
            "notion_url": notion_url,
            "notion_page_id": notion_page_id,
            "project": project_name,
            "area": area_name
        }

        # Remove None values for cleaner YAML
        frontmatter = {k: v for k, v in frontmatter.items() if v is not None}

        return frontmatter

    @staticmethod
    def format_as_yaml(frontmatter_dict, content_markdown):
        """
        Combine frontmatter + content into full markdown file

        Args:
            frontmatter_dict: dict (key-value pairs)
            content_markdown: str (Notion content as markdown)

        Returns:
            str (full markdown file with YAML frontmatter)
        """
        yaml_str = yaml.dump(frontmatter_dict, default_flow_style=False, allow_unicode=True, sort_keys=False)
        return f"---\n{yaml_str}---\n\n{content_markdown}"
```

---

## File Naming & Slug Generation

### Slug Generation Rules

1. **Lowercase**: `Meeting with Peter` → `meeting with peter`
2. **Replace spaces with hyphens**: `meeting with peter` → `meeting-with-peter`
3. **Remove special characters**: `Meeting w/ Peter (Strategy & Fundraising)` → `meeting-w-peter-strategy-fundraising`
4. **Preserve keywords and meaning**: Keep hyphens and underscores intact
5. **Collapse multiple hyphens**: `meeting--with--peter` → `meeting-with-peter`
6. **Strip leading/trailing hyphens**: `-meeting-with-peter-` → `meeting-with-peter`

### Special Characters to Remove

```python
REMOVE_CHARS = r'[\/\\:;,?!@#$%^&*()\[\]{}<>\'"`~+=|]'
```

### Conflict Handling

If filename already exists in destination folder:
- Append `-2`, `-3`, etc.
- Example: `meeting-with-peter.md` → `meeting-with-peter-2.md`

### Python Implementation

```python
import re
import os

class SlugGenerator:
    """Generate URL-safe filenames from Notion titles"""

    REMOVE_CHARS = r'[\/\\:;,?!@#$%^&*()\[\]{}<>\'"`~+=|]'

    @staticmethod
    def generate(title, folder_path=None):
        """
        Generate slug from title, handle conflicts if folder_path provided

        Args:
            title: str (Notion page title)
            folder_path: str or None (destination folder for conflict detection)

        Returns:
            str (filename with .md extension)
        """
        # 1. Lowercase
        slug = title.lower()

        # 2. Replace spaces with hyphens
        slug = slug.replace(" ", "-")

        # 3. Remove special characters
        slug = re.sub(SlugGenerator.REMOVE_CHARS, '', slug)

        # 4. Collapse multiple hyphens
        slug = re.sub(r'-+', '-', slug)

        # 5. Strip leading/trailing hyphens
        slug = slug.strip('-')

        # 6. Add .md extension
        filename = f"{slug}.md"

        # 7. Handle conflicts
        if folder_path:
            filename = SlugGenerator._handle_conflict(filename, folder_path)

        return filename

    @staticmethod
    def _handle_conflict(filename, folder_path):
        """
        If filename exists, append -2, -3, etc.

        Args:
            filename: str (e.g., "meeting-with-peter.md")
            folder_path: str (absolute path to folder)

        Returns:
            str (unique filename)
        """
        base_name, ext = os.path.splitext(filename)  # ("meeting-with-peter", ".md")

        counter = 2
        new_filename = filename

        while os.path.exists(os.path.join(folder_path, new_filename)):
            new_filename = f"{base_name}-{counter}{ext}"
            counter += 1

        return new_filename
```

### Examples

| Notion Title | Slug |
|-------------|------|
| `Meeting with Peter` | `meeting-with-peter.md` |
| `Meeting w/ Peter (Strategy & Fundraising)` | `meeting-w-peter-strategy-fundraising.md` |
| `Book Notes: Atomic Habits` | `book-notes-atomic-habits.md` |
| `Research: AI in Healthcare (2025)` | `research-ai-in-healthcare-2025.md` |
| `Product Ideas -- Legacy AI` | `product-ideas-legacy-ai.md` |

---

## INDEX.md Generation

### Purpose

INDEX.md files provide **human-navigable summaries** of folder contents. They are regenerated after each sync (1am/1pm) by scanning the actual directory structure.

**Not for RAG**: RAG reindexing is Phase 4 (separate from INDEX.md generation).

### 4-Level Nested Structure

```markdown
# [Folder Path]

## Area: [Area Name]
## Project: [Project Name]  (OR "Resources" if no project)

### 📝 Meeting Notes
- meeting-with-peter-2025-12-15.md
- strategy-session-q4-planning.md

### 🔬 Research
- market-analysis-legacy-ai.md

---

# [Next Folder Path]
...
```

### Example 1: Project-Based Folder

**Path**: `areas/legacy-ai-business/projects/customer-discovery/meeting-notes/`

**INDEX.md**:
```markdown
# areas/legacy-ai-business/projects/customer-discovery/meeting-notes/

## Area: Legacy AI Business
## Project: Customer Discovery

### 📝 Meeting Notes
- meeting-with-peter-2025-12-15.md
- interview-carrie-esker-2025-11-20.md
- strategy-session-q4-planning-2025-10-05.md
```

### Example 2: Resources Folder

**Path**: `resources/book-notes/`

**INDEX.md**:
```markdown
# resources/book-notes/

## Resources (No Project)

### 📚 Book Notes
- atomic-habits-summary.md
- deep-work-notes.md
- building-a-second-brain-tiago-forte.md
```

### Example 3: Life Area Folder

**Path**: `areas/lifeadmin/resources/meeting-notes/`

**INDEX.md**:
```markdown
# areas/lifeadmin/resources/meeting-notes/

## Area: Life
## Resources

### 📝 Meeting Notes
- meeting-with-accountant-2025-tax-planning.md
- dentist-follow-up-2025-12-01.md
```

### Python Implementation

```python
import os
from pathlib import Path
from collections import defaultdict

class IndexGenerator:
    """Generate INDEX.md files for human navigation"""

    NOTE_TYPE_EMOJIS = {
        "meeting-notes": "📝 Meeting Notes",
        "book-notes": "📚 Book Notes",
        "podcast-notes": "🎧 Podcast Notes",
        "research": "🔬 Research",
        "frameworks": "⚙️ Framework",
        "documents": "📄 Document"
    }

    def __init__(self, repo_base_path):
        """
        repo_base_path: str (absolute path to repo root)
        """
        self.repo_base_path = Path(repo_base_path)

    def regenerate_all(self):
        """
        Scan entire repo and regenerate INDEX.md in all note folders

        Returns:
            list of str (paths to generated INDEX.md files)
        """
        generated = []

        # Find all folders containing markdown files
        for folder_path in self._find_note_folders():
            index_path = self.generate_for_folder(folder_path)
            generated.append(index_path)

        return generated

    def generate_for_folder(self, folder_path):
        """
        Generate INDEX.md for a specific folder

        Args:
            folder_path: str or Path (absolute path to folder)

        Returns:
            str (path to generated INDEX.md)
        """
        folder_path = Path(folder_path)

        # 1. Parse folder structure to extract Area, Project, Note Type
        relative_path = folder_path.relative_to(self.repo_base_path)
        parts = relative_path.parts

        area_name = None
        project_name = None
        note_type_folder = parts[-1] if parts else "unknown"

        # Parse path structure
        if "areas" in parts:
            area_idx = parts.index("areas")
            if len(parts) > area_idx + 1:
                area_name = self._humanize_slug(parts[area_idx + 1])

            if "projects" in parts:
                project_idx = parts.index("projects")
                if len(parts) > project_idx + 1:
                    project_name = self._humanize_slug(parts[project_idx + 1])

        elif "resources" in parts:
            area_name = "Resources"
            project_name = None

        # 2. Scan folder for markdown files
        md_files = sorted([f.name for f in folder_path.glob("*.md") if f.name != "INDEX.md"])

        # 3. Generate INDEX.md content
        content = self._format_index(
            relative_path=str(relative_path),
            area_name=area_name,
            project_name=project_name,
            note_type_folder=note_type_folder,
            files=md_files
        )

        # 4. Write to INDEX.md
        index_path = folder_path / "INDEX.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(index_path)

    def _format_index(self, relative_path, area_name, project_name, note_type_folder, files):
        """
        Format INDEX.md content

        Args:
            relative_path: str (e.g., "areas/legacy-ai-business/projects/customer-discovery/meeting-notes")
            area_name: str or None (e.g., "Legacy AI Business")
            project_name: str or None (e.g., "Customer Discovery")
            note_type_folder: str (e.g., "meeting-notes")
            files: list of str (markdown filenames)

        Returns:
            str (INDEX.md content)
        """
        lines = []

        # Header
        lines.append(f"# {relative_path}/")
        lines.append("")

        # Area
        if area_name:
            lines.append(f"## Area: {area_name}")

        # Project or Resources
        if project_name:
            lines.append(f"## Project: {project_name}")
        else:
            lines.append("## Resources (No Project)")

        lines.append("")

        # Note Type Section
        note_type_display = self.NOTE_TYPE_EMOJIS.get(note_type_folder, note_type_folder.title())
        lines.append(f"### {note_type_display}")

        if files:
            for filename in files:
                lines.append(f"- {filename}")
        else:
            lines.append("*(No files yet)*")

        return "\n".join(lines)

    def _find_note_folders(self):
        """
        Find all folders that contain synced notes (by note type folder name)

        Returns:
            list of Path (absolute paths to folders)
        """
        note_folders = []

        for note_type_folder in self.NOTE_TYPE_EMOJIS.keys():
            # Find all occurrences of this folder name
            for folder_path in self.repo_base_path.rglob(note_type_folder):
                if folder_path.is_dir():
                    note_folders.append(folder_path)

        return note_folders

    @staticmethod
    def _humanize_slug(slug):
        """
        Convert slug to human-readable name

        Args:
            slug: str (e.g., "legacy-ai-business")

        Returns:
            str (e.g., "Legacy AI Business")
        """
        return slug.replace("-", " ").title()
```

### Regeneration Trigger

INDEX.md is regenerated:
1. **After each sync run** (1am + 1pm cron)
2. **After any manual file moves** (safe to manually reorganize files)
3. **On-demand** via script: `python infra/scripts/regenerate_index.py`

---

## Sync Engine Architecture

### File Structure

```
infra/
├── scripts/
│   ├── notion_to_repo_sync.py          # Main sync script
│   └── regenerate_index.py             # Standalone INDEX.md generator
├── config/
│   └── sync_config.json                # Sync configuration
└── logs/
    ├── sync.log                         # General sync logs
    └── sync_errors.log                  # Error logs
```

### Main Script: `notion_to_repo_sync.py`

```python
#!/usr/bin/env python3
"""
Notion → Repo Sync Script

Syncs notes from Notion Notes database to Git repos based on routing logic.
Runs via cron at 1am and 1pm daily.

Usage:
    python infra/scripts/notion_to_repo_sync.py [--dry-run]
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from notion_client import Client as NotionClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from infra.scripts.modules.routing_engine import RoutingEngine
from infra.scripts.modules.frontmatter_generator import FrontmatterGenerator
from infra.scripts.modules.slug_generator import SlugGenerator
from infra.scripts.modules.index_generator import IndexGenerator
from infra.scripts.modules.git_committer import GitCommitter

class SyncOrchestrator:
    """Orchestrates the Notion → Repo sync process"""

    def __init__(self, config_path):
        """
        Load config and initialize components

        Args:
            config_path: str (path to sync_config.json)
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Initialize Notion client
        self.notion = NotionClient(auth=os.environ["NOTION_API_KEY"])

        # Initialize components
        repo_base_paths = self.config["repo_paths"]
        self.routing = RoutingEngine(repo_base_paths)
        self.frontmatter_gen = FrontmatterGenerator()
        self.slug_gen = SlugGenerator()
        self.git_committer = GitCommitter(repo_base_paths)

        # Logging
        self.setup_logging()

    def setup_logging(self):
        """Configure logging to file and console"""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "sync.log"),
                logging.StreamHandler()
            ]
        )

        # Separate error log
        error_handler = logging.FileHandler(log_dir / "sync_errors.log")
        error_handler.setLevel(logging.ERROR)
        logging.getLogger().addHandler(error_handler)

    def run(self, dry_run=False):
        """
        Main sync loop

        Args:
            dry_run: bool (if True, log actions but don't write files)
        """
        logging.info("=" * 80)
        logging.info(f"Starting Notion → Repo sync at {datetime.now()}")
        logging.info(f"Dry run: {dry_run}")
        logging.info("=" * 80)

        # 1. Query Notion for notes with "Sync to Repo" = True
        notes_to_sync = self.query_notion_notes()
        logging.info(f"Found {len(notes_to_sync)} notes marked for sync")

        # 2. Filter notes that need syncing (incremental)
        notes_to_sync = self.filter_incremental(notes_to_sync)
        logging.info(f"After incremental filter: {len(notes_to_sync)} notes need syncing")

        if not notes_to_sync:
            logging.info("No notes to sync. Exiting.")
            return

        # 3. Sync each note
        synced_by_type = {}  # Track synced files by note type for grouped commits

        for note in notes_to_sync:
            try:
                result = self.sync_note(note, dry_run=dry_run)
                if result:
                    note_type = result["note_type"]
                    if note_type not in synced_by_type:
                        synced_by_type[note_type] = []
                    synced_by_type[note_type].append(result)
            except Exception as e:
                logging.error(f"Failed to sync note '{note['title']}': {e}", exc_info=True)

        # 4. Regenerate INDEX.md files
        if not dry_run:
            logging.info("Regenerating INDEX.md files...")
            for repo_name, repo_path in self.routing.repo_base_paths.items():
                index_gen = IndexGenerator(repo_path)
                index_gen.regenerate_all()

        # 5. Commit changes (grouped by note type)
        if not dry_run:
            self.git_committer.commit_grouped(synced_by_type)

        logging.info("=" * 80)
        logging.info(f"Sync complete at {datetime.now()}")
        logging.info("=" * 80)

    def query_notion_notes(self):
        """
        Query Notion for notes with "Sync to Repo" = True

        Returns:
            list of dict (simplified note objects)
        """
        database_id = self.config["notion"]["notes_database_id"]

        # Query with filter
        results = self.notion.databases.query(
            database_id=database_id,
            filter={
                "property": "Sync to Repo",
                "checkbox": {"equals": True}
            }
        )

        notes = []
        for page in results["results"]:
            # Resolve relations (Project, Area)
            project_name = self._resolve_relation(page, "Project")
            area_name = self._resolve_relation(page, "Area / Resource")

            # Extract properties
            note = {
                "page_id": page["id"],
                "title": self._get_title(page),
                "note_types": [nt["name"] for nt in page["properties"]["Note Type"]["multi_select"]],
                "project_name": project_name,
                "area_name": area_name,
                "last_edited": page["last_edited_time"],
                "page_object": page  # Full page object for later
            }
            notes.append(note)

        return notes

    def filter_incremental(self, notes):
        """
        Filter notes that need syncing (changed since last sync)

        Args:
            notes: list of dict (from query_notion_notes)

        Returns:
            list of dict (notes that need syncing)
        """
        filtered = []

        for note in notes:
            # Check if file exists and read last_synced from frontmatter
            try:
                route = self.routing.route_note({
                    "note_types": note["note_types"],
                    "area_name": note["area_name"],
                    "project_name": note["project_name"],
                    "title": note["title"]
                })

                file_path = route["full_path"]

                if os.path.exists(file_path):
                    # Read frontmatter
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract last_synced
                    last_synced = self._extract_last_synced(content)

                    if last_synced:
                        # Compare timestamps (60-second threshold)
                        notion_edited = datetime.fromisoformat(note["last_edited"].replace("Z", "+00:00"))
                        last_synced_dt = datetime.fromisoformat(last_synced.replace("Z", "+00:00"))

                        time_diff = abs((notion_edited - last_synced_dt).total_seconds())

                        if time_diff <= 60:
                            # Within threshold, consider equal
                            logging.info(f"Skipping '{note['title']}': within 60s threshold")
                            continue
                        elif notion_edited < last_synced_dt:
                            # Repo is newer, skip Notion sync
                            logging.warning(f"Skipping '{note['title']}': repo file is newer than Notion")
                            continue

                # Either file doesn't exist or Notion is newer
                filtered.append(note)

            except Exception as e:
                logging.error(f"Error filtering note '{note['title']}': {e}")
                # Include in sync to be safe
                filtered.append(note)

        return filtered

    def sync_note(self, note, dry_run=False):
        """
        Sync a single note from Notion to repo

        Args:
            note: dict (from query_notion_notes)
            dry_run: bool

        Returns:
            dict or None (sync result for git commit tracking)
        """
        title = note["title"]
        logging.info(f"Syncing: '{title}'")

        # 1. Route note
        route = self.routing.route_note({
            "note_types": note["note_types"],
            "area_name": note["area_name"],
            "project_name": note["project_name"],
            "title": title
        })

        logging.info(f"  → Repo: {route['repo']}")
        logging.info(f"  → Folder: {route['folder']}")
        logging.info(f"  → Filename: {route['filename']}")

        if dry_run:
            return None

        # 2. Fetch full Notion page content
        page = self.notion.pages.retrieve(note["page_id"])
        blocks = self.notion.blocks.children.list(note["page_id"])
        content_markdown = self._blocks_to_markdown(blocks["results"])

        # 3. Generate frontmatter
        frontmatter = self.frontmatter_gen.generate(
            page,
            project_name=note["project_name"],
            area_name=note["area_name"]
        )

        # 4. Combine frontmatter + content
        full_markdown = self.frontmatter_gen.format_as_yaml(frontmatter, content_markdown)

        # 5. Write to file
        folder_path = Path(route["full_path"]).parent
        folder_path.mkdir(parents=True, exist_ok=True)

        with open(route["full_path"], 'w', encoding='utf-8') as f:
            f.write(full_markdown)

        logging.info(f"  ✓ Written to: {route['full_path']}")

        # Return result for git commit
        return {
            "repo": route["repo"],
            "file_path": route["full_path"],
            "note_type": note["note_types"][0],  # First note type
            "action": "added" if not os.path.exists(route["full_path"]) else "updated"
        }

    def _resolve_relation(self, page, property_name):
        """Resolve relation property to name"""
        relations = page["properties"][property_name]["relation"]
        if relations:
            related_page = self.notion.pages.retrieve(relations[0]["id"])
            return self._get_title(related_page)
        return None

    @staticmethod
    def _get_title(page):
        """Extract title from page"""
        title_array = page["properties"].get("Name", {}).get("title", [])
        if title_array:
            return title_array[0]["plain_text"]
        return "Untitled"

    @staticmethod
    def _extract_last_synced(markdown_content):
        """Extract last_synced from frontmatter"""
        import re
        match = re.search(r'last_synced:\s*(.+)', markdown_content)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def _blocks_to_markdown(blocks):
        """Convert Notion blocks to markdown (simplified)"""
        # TODO: Implement full block → markdown conversion
        # For now, return placeholder
        lines = []
        for block in blocks:
            block_type = block["type"]
            if block_type == "paragraph":
                text = "".join([rt["plain_text"] for rt in block["paragraph"]["rich_text"]])
                lines.append(text)
            elif block_type == "heading_1":
                text = "".join([rt["plain_text"] for rt in block["heading_1"]["rich_text"]])
                lines.append(f"# {text}")
            # ... (add more block types)

        return "\n\n".join(lines)

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync notes from Notion to Git repos")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without writing files")
    args = parser.parse_args()

    # Load config
    config_path = Path(__file__).parent.parent / "config" / "sync_config.json"

    # Run sync
    orchestrator = SyncOrchestrator(str(config_path))
    orchestrator.run(dry_run=args.dry_run)

if __name__ == "__main__":
    main()
```

### Component Modules

Create separate modules in `infra/scripts/modules/`:

1. **routing_engine.py**: RoutingEngine class (see [Routing Logic](#routing-logic))
2. **frontmatter_generator.py**: FrontmatterGenerator class (see [Frontmatter Design](#frontmatter-design))
3. **slug_generator.py**: SlugGenerator class (see [File Naming](#file-naming--slug-generation))
4. **index_generator.py**: IndexGenerator class (see [INDEX.md Generation](#indexmd-generation))
5. **git_committer.py**: GitCommitter class (see [Git Commit Strategy](#git-commit-strategy))

---

## Incremental Sync Strategy

### Goal

Only sync notes that have changed since last sync to reduce API calls and improve performance.

### Logic

1. **Query Notion** for notes with "Sync to Repo" = True
2. **For each note**:
   - Check if file exists in repo
   - If exists: Read `last_synced` from frontmatter
   - Compare `notion_last_edited` vs `last_synced`
   - **If `notion_last_edited > last_synced + 60s`**: Sync (Notion is newer)
   - **If `last_synced > notion_last_edited + 60s`**: Skip (Repo is newer)
   - **If within 60s**: Skip (consider equal, avoid thrashing)
3. **If file doesn't exist**: Always sync (first sync)

### Python Implementation

```python
def filter_incremental(self, notes):
    """
    Filter notes that need syncing (changed since last sync)

    Args:
        notes: list of dict (from query_notion_notes)

    Returns:
        list of dict (notes that need syncing)
    """
    filtered = []

    for note in notes:
        # Check if file exists and read last_synced from frontmatter
        try:
            route = self.routing.route_note({
                "note_types": note["note_types"],
                "area_name": note["area_name"],
                "project_name": note["project_name"],
                "title": note["title"]
            })

            file_path = route["full_path"]

            if os.path.exists(file_path):
                # Read frontmatter
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract last_synced
                last_synced = self._extract_last_synced(content)

                if last_synced:
                    # Compare timestamps (60-second threshold)
                    notion_edited = datetime.fromisoformat(note["last_edited"].replace("Z", "+00:00"))
                    last_synced_dt = datetime.fromisoformat(last_synced.replace("Z", "+00:00"))

                    time_diff = abs((notion_edited - last_synced_dt).total_seconds())

                    if time_diff <= 60:
                        # Within threshold, consider equal
                        logging.info(f"Skipping '{note['title']}': within 60s threshold")
                        continue
                    elif notion_edited < last_synced_dt:
                        # Repo is newer, skip Notion sync
                        logging.warning(f"Skipping '{note['title']}': repo file is newer than Notion")
                        continue

            # Either file doesn't exist or Notion is newer
            filtered.append(note)

        except Exception as e:
            logging.error(f"Error filtering note '{note['title']}': {e}")
            # Include in sync to be safe
            filtered.append(note)

    return filtered
```

### Performance Impact

**Without incremental sync**:
- 100 notes × 3 API calls each = 300 API calls
- Time: ~100 seconds (3 req/sec rate limit)

**With incremental sync**:
- 100 notes queried, 10 changed → 10 notes × 3 API calls = 30 API calls
- Time: ~10 seconds

**90% reduction in API calls**

---

## Conflict Resolution

### Scenario

Note edited in **both Notion AND repo** between syncs.

### Resolution Strategy

**Most recent edit wins**

### Logic

```python
if notion_last_edited > file_modified_time + 60s:
    # Notion is newer → Notion wins
    overwrite_repo_file_from_notion()
elif file_modified_time > notion_last_edited + 60s:
    # Repo is newer → Repo wins (skip Notion sync)
    log_warning("Repo file newer, skipping Notion sync")
    skip_sync()
else:
    # Within 60s threshold → Consider equal, Notion wins (default)
    overwrite_repo_file_from_notion()
```

### 60-Second Threshold

**Why 60 seconds?**
- Accounts for clock skew between systems
- Prevents thrashing on near-simultaneous edits
- Safer than 5 seconds (more tolerance)

**Example**:
- Notion edited: `2025-12-16T14:30:00Z`
- File modified: `2025-12-16T14:30:45Z`
- Difference: 45 seconds
- Result: Within threshold → Notion wins (default)

### Logging Conflicts

All conflicts logged to `infra/logs/sync.log` with `WARNING` level:

```
2025-12-16 14:30:00 - WARNING - Conflict detected: 'Meeting with Peter'
  Notion last edited: 2025-12-16T14:30:00Z
  File modified: 2025-12-16T14:30:45Z
  Time diff: 45s (within 60s threshold)
  Resolution: Notion wins (default)
```

### Weekly Review

User reviews `sync.log` weekly to identify patterns:
- Frequent conflicts → Consider increasing threshold or workflow changes
- Repo edits winning → May need to sync repo → Notion (Phase 3)

---

## Deletion Handling

### When Note Deleted in Notion

**Behavior**: Move to archive in repo (don't hard delete)

### Archive Path Format

```
areas/archive/YYYY-MM-DD-[original-path]/[filename].md
```

### Examples

**Example 1**: Delete meeting note from project

- **Original**: `areas/legacy-ai-business/projects/customer-discovery/meeting-notes/meeting-with-peter.md`
- **Archived**: `areas/archive/2025-12-16-legacy-ai-business-projects-customer-discovery-meeting-notes/meeting-with-peter.md`

**Example 2**: Delete book note from resources

- **Original**: `resources/book-notes/atomic-habits-summary.md`
- **Archived**: `areas/archive/2025-12-16-resources-book-notes/atomic-habits-summary.md`

### Rationale

1. **Accidental deletions recoverable**: User can restore from archive
2. **Git history preserved**: All commits remain intact
3. **No data loss**: Can always hard-delete manually later
4. **Audit trail**: Know when and what was deleted

### Python Implementation

```python
def handle_deletion(self, note_page_id, repo_base_paths):
    """
    Archive a deleted Notion note

    Args:
        note_page_id: str (Notion page ID)
        repo_base_paths: dict (repo name → absolute path)

    Returns:
        str or None (path to archived file)
    """
    # 1. Find file in repo by notion_page_id in frontmatter
    file_path = self._find_file_by_notion_id(note_page_id, repo_base_paths)

    if not file_path:
        logging.warning(f"Cannot find file for deleted note: {note_page_id}")
        return None

    # 2. Generate archive path
    repo_base = self._get_repo_base(file_path, repo_base_paths)
    relative_path = Path(file_path).relative_to(repo_base)

    today = datetime.now().strftime("%Y-%m-%d")
    archive_folder = f"areas/archive/{today}-{relative_path.parent}".replace("/", "-")
    archive_path = Path(repo_base) / archive_folder / Path(file_path).name

    # 3. Move file
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(file_path, archive_path)

    logging.info(f"Archived: {file_path} → {archive_path}")

    return str(archive_path)

def _find_file_by_notion_id(self, notion_page_id, repo_base_paths):
    """Find file containing notion_page_id in frontmatter"""
    for repo_base in repo_base_paths.values():
        for md_file in Path(repo_base).rglob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if f"notion_page_id: {notion_page_id}" in content:
                return str(md_file)

    return None
```

### Detection Logic

**How to detect deletions?**

1. **Query all synced files** in repo (scan for `notion_page_id` in frontmatter)
2. **Query Notion** for all pages with "Sync to Repo" = True
3. **Compare**:
   - Files in repo but not in Notion → Deleted in Notion → Archive
   - Files in Notion but not in repo → New notes → Sync

**Run frequency**: After each sync (1am + 1pm)

---

## Git Commit Strategy

### Strategy

**Group by note type**: One commit per note type per sync run.

### Commit Message Format

```
[SYNC] Notion→Repo: 3 meeting notes, 2 book notes

## Added
- areas/legacy-ai-business/projects/customer-discovery/meeting-notes/meeting-with-peter.md
- resources/book-notes/atomic-habits-summary.md

## Updated
- areas/legacy-ai-business/projects/customer-discovery/meeting-notes/strategy-session.md
- resources/book-notes/deep-work-notes.md

## Archived
- areas/archive/2025-12-16-resources-book-notes/old-note.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Python Implementation

```python
class GitCommitter:
    """Handle git commits for synced notes"""

    def __init__(self, repo_base_paths):
        """
        repo_base_paths: dict (repo name → absolute path)
        """
        self.repo_base_paths = repo_base_paths

    def commit_grouped(self, synced_by_type):
        """
        Create grouped commits by note type

        Args:
            synced_by_type: dict mapping note type → list of sync results
            Example: {
                "Meeting Notes": [
                    {"repo": "ai-assistant", "file_path": "...", "action": "added"},
                    {"repo": "ai-assistant", "file_path": "...", "action": "updated"}
                ],
                "Book Notes": [...]
            }
        """
        # Group by repo first
        by_repo = {}
        for note_type, results in synced_by_type.items():
            for result in results:
                repo = result["repo"]
                if repo not in by_repo:
                    by_repo[repo] = {}
                if note_type not in by_repo[repo]:
                    by_repo[repo][note_type] = []
                by_repo[repo][note_type].append(result)

        # Commit per repo
        for repo, note_types in by_repo.items():
            self._commit_repo(repo, note_types)

    def _commit_repo(self, repo_name, note_types):
        """
        Create commit for a single repo

        Args:
            repo_name: str (e.g., "ai-assistant")
            note_types: dict (note type → list of results)
        """
        repo_path = self.repo_base_paths[repo_name]

        # Count added/updated/archived
        total_added = 0
        total_updated = 0
        total_archived = 0

        added_files = []
        updated_files = []
        archived_files = []

        for note_type, results in note_types.items():
            for result in results:
                action = result["action"]
                file_path = result["file_path"]
                relative_path = Path(file_path).relative_to(repo_path)

                if action == "added":
                    total_added += 1
                    added_files.append(str(relative_path))
                elif action == "updated":
                    total_updated += 1
                    updated_files.append(str(relative_path))
                elif action == "archived":
                    total_archived += 1
                    archived_files.append(str(relative_path))

        # Build commit message
        summary_parts = []
        if total_added > 0:
            summary_parts.append(f"{total_added} added")
        if total_updated > 0:
            summary_parts.append(f"{total_updated} updated")
        if total_archived > 0:
            summary_parts.append(f"{total_archived} archived")

        summary = ", ".join(summary_parts)

        commit_msg = f"""[SYNC] Notion→Repo: {summary}

## Added
{self._format_file_list(added_files)}

## Updated
{self._format_file_list(updated_files)}

## Archived
{self._format_file_list(archived_files)}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"""

        # Git add all changed files
        os.chdir(repo_path)
        subprocess.run(["git", "add", "."], check=True)

        # Git commit
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        logging.info(f"✓ Committed to {repo_name}: {summary}")

    @staticmethod
    def _format_file_list(files):
        """Format file list for commit message"""
        if not files:
            return "*(none)*"
        return "\n".join([f"- {f}" for f in files])
```

---

## Error Handling

### Strategy

1. **Retry with exponential backoff**: 3 attempts with 2s, 4s, 8s delays
2. **Log errors to file**: `infra/logs/sync_errors.log`
3. **Continue on error**: Skip failed notes, don't fail entire batch

### Python Implementation

```python
import time
import logging

def retry_with_backoff(func, max_retries=3, base_delay=2):
    """
    Retry function with exponential backoff

    Args:
        func: callable (function to retry)
        max_retries: int (max attempts, default 3)
        base_delay: int (initial delay in seconds, default 2)

    Returns:
        Result of func() or raises last exception
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries:
                logging.error(f"Failed after {max_retries} attempts: {e}", exc_info=True)
                raise

            delay = base_delay * (2 ** (attempt - 1))  # 2s, 4s, 8s
            logging.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)

# Usage in sync_note:
def sync_note(self, note, dry_run=False):
    """Sync a single note with retry logic"""
    try:
        return retry_with_backoff(lambda: self._sync_note_impl(note, dry_run))
    except Exception as e:
        logging.error(f"Failed to sync note '{note['title']}' after retries: {e}")
        return None  # Continue with other notes
```

### Error Scenarios

| Error | Handling |
|-------|----------|
| **Notion API rate limit** | Retry with backoff (automatically handled by exponential backoff) |
| **Notion API 404** (page deleted) | Log warning, skip sync |
| **Notion API 401** (auth failed) | Log error, abort sync (critical) |
| **File write permission denied** | Log error, skip note, continue batch |
| **Git commit failed** | Log error, abort (critical - manual intervention needed) |
| **Invalid routing** (no Project/Area) | Log warning, skip note |
| **Slug generation failed** | Log error, skip note |

### Error Log Format

```
2025-12-16 14:30:00 - ERROR - Failed to sync note 'Meeting with Peter': NotionAPIError(404, "Page not found")
Traceback (most recent call last):
  File "notion_to_repo_sync.py", line 123, in sync_note
    page = self.notion.pages.retrieve(note["page_id"])
  ...
```

---

## Testing Strategy

### Golden Dataset (3 Test Notes)

Create 3 test notes in **production Notion workspace** with `test-` prefix:

**1. Test Meeting Note (with Project)**
- Title: `test-meeting-peter-fundraising`
- Note Type: `📝 Meeting Notes`
- Project: `Customer Discovery`
- Area / Resource: `Legacy AI`
- Sync to Repo: ✓
- Expected Path: `legacy-ai/areas/legacy-ai-business/projects/customer-discovery/meeting-notes/test-meeting-peter-fundraising.md`

**2. Test Book Note (no Project)**
- Title: `test-atomic-habits-summary`
- Note Type: `📚 Book Notes`
- Project: *(blank)*
- Area / Resource: `Epic 2nd Brain Workflow`
- Sync to Repo: ✓
- Expected Path: `ai-assistant/resources/book-notes/test-atomic-habits-summary.md`

**3. Test Research Note (Area only)**
- Title: `test-market-analysis-legacy-ai`
- Note Type: `🔬 Research`
- Project: *(blank)*
- Area / Resource: `Epic 2nd Brain Workflow`
- Sync to Repo: ✓
- Expected Path: `ai-assistant/areas/epic-2nd-brain-workflow/research/test-market-analysis-legacy-ai.md`

### Test Execution

```bash
# 1. Create 3 test notes in Notion (manually)

# 2. Run sync in dry-run mode
python infra/scripts/notion_to_repo_sync.py --dry-run

# 3. Review logs
cat infra/logs/sync.log

# 4. Run actual sync
python infra/scripts/notion_to_repo_sync.py

# 5. Validate results (see checklist below)
```

### Validation Checklist

#### ✅ Repo Selection
- [ ] Meeting note → `legacy-ai/` (Area = "Legacy AI")
- [ ] Book note → `ai-assistant/` (Area = "Epic 2nd Brain Workflow")
- [ ] Research note → `ai-assistant/` (Area = "Epic 2nd Brain Workflow")

#### ✅ Folder Routing
- [ ] Meeting note → `projects/customer-discovery/meeting-notes/` (has Project)
- [ ] Book note → `resources/book-notes/` (no Project, always resources)
- [ ] Research note → `areas/epic-2nd-brain-workflow/research/` (no Project, area-specific)

#### ✅ Frontmatter
- [ ] `note_types` array with emojis stripped (`[Meeting Notes]` not `[📝 Meeting Notes]`)
- [ ] `project` field populated for meeting note, null for others
- [ ] `area` field populated for all 3 notes
- [ ] `tags` array populated if present, null otherwise
- [ ] `last_synced` timestamp present (ISO 8601 format)
- [ ] `notion_url` and `notion_page_id` present

#### ✅ File Naming
- [ ] Meeting note: `test-meeting-peter-fundraising.md`
- [ ] Book note: `test-atomic-habits-summary.md`
- [ ] Research note: `test-market-analysis-legacy-ai.md`

#### ✅ Conflict Resolution (Manual Test)
1. Edit meeting note in Notion (change title)
2. Edit same file in repo (change content)
3. Wait 60+ seconds
4. Run sync
5. Validate: Most recent edit wins (check timestamps in log)

#### ✅ Deletion Handling (Manual Test)
1. Delete book note in Notion (uncheck "Sync to Repo")
2. Run sync
3. Validate: File moved to `areas/archive/YYYY-MM-DD-resources-book-notes/test-atomic-habits-summary.md`

#### ✅ Incremental Sync
1. Run sync twice without changes
2. Validate: Second run skips all notes (logs "Skipping: within 60s threshold")

#### ✅ INDEX.md Generation
- [ ] INDEX.md created in `projects/customer-discovery/meeting-notes/`
- [ ] INDEX.md created in `resources/book-notes/`
- [ ] INDEX.md created in `areas/epic-2nd-brain-workflow/research/`
- [ ] Each INDEX.md has 4-level structure (path, area, project, note type, files)

#### ✅ Git Commits
- [ ] One commit created per repo
- [ ] Commit message format: `[SYNC] Notion→Repo: X added, Y updated`
- [ ] Commit lists all changed files under "Added" section

### Unit Tests

Create `infra/tests/test_phase2.py`:

```python
import unittest
from infra.scripts.modules.slug_generator import SlugGenerator
from infra.scripts.modules.routing_engine import RoutingEngine
from infra.scripts.modules.frontmatter_generator import FrontmatterGenerator

class TestSlugGenerator(unittest.TestCase):
    def test_basic_slug(self):
        slug = SlugGenerator.generate("Meeting with Peter")
        self.assertEqual(slug, "meeting-with-peter.md")

    def test_special_chars(self):
        slug = SlugGenerator.generate("Meeting w/ Peter (Strategy & Fundraising)")
        self.assertEqual(slug, "meeting-w-peter-strategy-fundraising.md")

    def test_conflict_handling(self):
        # Mock folder with existing file
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing file
            existing = os.path.join(tmpdir, "meeting-with-peter.md")
            open(existing, 'w').close()

            # Generate slug with conflict
            slug = SlugGenerator.generate("Meeting with Peter", folder_path=tmpdir)
            self.assertEqual(slug, "meeting-with-peter-2.md")

class TestRoutingEngine(unittest.TestCase):
    def setUp(self):
        self.routing = RoutingEngine({
            "ai-assistant": "/tmp/ai-assistant",
            "legacy-ai": "/tmp/legacy-ai"
        })

    def test_project_routing(self):
        route = self.routing.route_note({
            "note_types": ["📝 Meeting Notes"],
            "area_name": "Legacy AI",
            "project_name": "Customer Discovery",
            "title": "Meeting with Peter"
        })
        self.assertEqual(route["repo"], "legacy-ai")
        self.assertEqual(route["folder"], "projects/customer-discovery/meeting-notes")

    def test_resources_routing(self):
        route = self.routing.route_note({
            "note_types": ["📚 Book Notes"],
            "area_name": "Epic 2nd Brain Workflow",
            "project_name": None,
            "title": "Atomic Habits"
        })
        self.assertEqual(route["repo"], "ai-assistant")
        self.assertEqual(route["folder"], "resources/book-notes")

class TestFrontmatterGenerator(unittest.TestCase):
    def test_strip_emoji(self):
        gen = FrontmatterGenerator()
        result = gen.strip_emoji("📝 Meeting Notes")
        self.assertEqual(result, "Meeting Notes")

    def test_generate_frontmatter(self):
        # Mock Notion page object
        mock_page = {
            "id": "abc123",
            "url": "https://notion.so/abc123",
            "created_time": "2025-12-16T14:30:00.000Z",
            "properties": {
                "Name": {"title": [{"plain_text": "Test Meeting"}]},
                "Note Type": {"multi_select": [{"name": "📝 Meeting Notes"}]},
                "Tags": {"multi_select": [{"name": "test"}]}
            }
        }

        gen = FrontmatterGenerator()
        frontmatter = gen.generate(mock_page, project_name="Test Project", area_name="Test Area")

        self.assertEqual(frontmatter["title"], "Test Meeting")
        self.assertEqual(frontmatter["note_types"], ["Meeting Notes"])
        self.assertEqual(frontmatter["project"], "Test Project")
        self.assertIn("last_synced", frontmatter)

if __name__ == "__main__":
    unittest.main()
```

Run tests:
```bash
python -m unittest infra/tests/test_phase2.py
```

---

## Configuration Schema

### File: `infra/config/sync_config.json`

```json
{
  "notion": {
    "notes_database_id": "${NOTION_NOTES_DATABASE_ID}",
    "api_key_env_var": "NOTION_API_KEY"
  },
  "repo_paths": {
    "ai-assistant": "/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant",
    "legacy-ai": "/Users/dharanchandrahasan/Documents/1. Projects/legacy-ai"
  },
  "sync": {
    "schedule": {
      "cron": "0 1,13 * * *",
      "enabled": true
    },
    "incremental": {
      "enabled": true,
      "conflict_threshold_seconds": 60
    }
  },
  "routing": {
    "area_to_repo": {
      "Epic 2nd Brain Workflow": "ai-assistant",
      "Legacy AI": "legacy-ai",
      "Life": "ai-assistant/areas/lifeadmin"
    },
    "note_type_to_folder": {
      "📝 Meeting Notes": "meeting-notes",
      "📚 Book Notes": "book-notes",
      "🎧 Podcast Notes": "podcast-notes",
      "🔬 Research": "research",
      "⚙️ Framework": "frameworks",
      "📄 Document": "documents"
    },
    "always_resources": ["📚 Book Notes", "🎧 Podcast Notes", "⚙️ Framework", "📄 Document"]
  },
  "error_handling": {
    "max_retries": 3,
    "base_delay_seconds": 2,
    "continue_on_error": true
  },
  "logging": {
    "log_dir": "infra/logs",
    "log_file": "sync.log",
    "error_log_file": "sync_errors.log",
    "level": "INFO"
  }
}
```

### Environment Variables

Create `.env` file (git-ignored):

```bash
# Notion API credentials
NOTION_API_KEY=secret_xyz123...
NOTION_NOTES_DATABASE_ID=abc123def456...
```

---

## Cron Setup

### Cron Safety Wrapper (Prevents Backpack Overheating)

**Problem**: Mac in backpack can overheat if cron runs while lid is closed.

**Solution**: Wrapper script checks lid state + AC power before running sync.

**File**: `infra/scripts/safe_cron_wrapper.sh`
```bash
#!/bin/bash
# Safe Cron Wrapper - Prevents overheating in backpack
# Only runs cron jobs when:
# 1. Lid is open (not in backpack)
# 2. On AC power (not draining battery)

SCRIPT_PATH="$1"
LOG_FILE="$2"

# Check if lid is closed
if ioreg -r -k AppleClamshellState | grep -q "AppleClamshellState.*Yes"; then
    echo "[$(date)] Cron skipped - lid closed (prevents overheating in backpack)" >> "$LOG_FILE"
    exit 0
fi

# Check if on battery power
if pmset -g batt | grep -q "Battery Power"; then
    echo "[$(date)] Cron skipped - on battery power" >> "$LOG_FILE"
    exit 0
fi

# Safe to run (AC power + lid open)
echo "[$(date)] Running: $SCRIPT_PATH" >> "$LOG_FILE"
/usr/bin/python3 "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1
```

**Make executable**:
```bash
chmod +x infra/scripts/safe_cron_wrapper.sh
```

### Mac Wake Schedule (pmset)

**Configure Mac to wake before cron jobs** (only when on AC power):

```bash
# Wake Mac before cron jobs (only when AC power + lid open)
sudo pmset -c repeat wake MTWRFSU 00:55:00  # Before 1am sync
sudo pmset -c repeat wake MTWRFSU 12:55:00  # Before 1pm sync

# -c flag = only wake when connected to AC power (prevents battery drain)
# MTWRFSU = Monday through Sunday
```

**Verify configuration**:
```bash
pmset -g sched
# Should show: wake at 00:55:00 and 12:55:00
```

### Crontab Entry (Updated with Safety Wrapper)

```bash
# Notion → Repo Sync (1am + 1pm daily with safety checks)
0 1,13 * * * /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/infra/scripts/safe_cron_wrapper.sh /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/infra/scripts/notion_to_repo_sync.py /Users/dharanchandrahasan/Documents/1.\ Projects/ai-assistant/infra/logs/cron.log
```

### Installation

```bash
# 1. Create and make wrapper executable
chmod +x infra/scripts/safe_cron_wrapper.sh

# 2. Configure pmset wake schedule
sudo pmset -c repeat wake MTWRFSU 00:55:00
sudo pmset -c repeat wake MTWRFSU 12:55:00

# 3. Open crontab editor
crontab -e

# 4. Add the crontab entry above
# Save and exit

# 5. Verify
crontab -l
pmset -g sched
```

### Cron Output

Logs are redirected to `infra/logs/cron.log`:

```
2025-12-16 01:00:00 - INFO - Starting Notion → Repo sync
2025-12-16 01:00:05 - INFO - Found 15 notes marked for sync
2025-12-16 01:00:10 - INFO - After incremental filter: 5 notes need syncing
...
2025-12-16 01:00:35 - INFO - Sync complete
```

### Debugging Cron

If cron doesn't run:

1. **Check cron service**: `sudo launchctl list | grep cron` (macOS)
2. **Check logs**: `cat infra/logs/cron.log`
3. **Test manually**: Run script with absolute paths to verify environment
4. **Environment issues**: Add to crontab:
   ```bash
   PATH=/usr/bin:/bin:/usr/local/bin
   NOTION_API_KEY=...
   ```

---

## Success Criteria

### Phase 2 Complete When:

1. ✅ **All 3 golden test notes sync correctly**
   - Correct repo selection (ai-assistant vs legacy-ai)
   - Correct folder path (projects vs areas vs resources)
   - Frontmatter preserved (all properties, emojis stripped)
   - File naming correct (slug generation, no conflicts)

2. ✅ **Conflict resolution works**
   - Most recent edit wins (timestamp comparison)
   - 60-second threshold prevents thrashing
   - Conflicts logged for weekly review

3. ✅ **Deletion handling works**
   - Deleted notes moved to `areas/archive/YYYY-MM-DD-[path]/`
   - No hard deletes (accidental deletion recoverable)

4. ✅ **Incremental sync works**
   - Only changed notes synced (skip unchanged)
   - Performance: <10s for 100 notes (90% unchanged)

5. ✅ **INDEX.md generation works**
   - Generated in all note folders
   - 4-level nested structure (Area → Project → Note Type → Files)
   - Regenerated after each sync

6. ✅ **Git commits grouped correctly**
   - One commit per repo per sync run
   - Grouped by note type in commit message
   - Lists all added/updated/archived files

7. ✅ **Error handling robust**
   - Retry with exponential backoff (3x: 2s, 4s, 8s)
   - Errors logged to `sync_errors.log`
   - Continue on error (don't fail entire batch)

8. ✅ **Cron runs successfully**
   - 1am + 1pm daily syncs execute
   - Logs written to `cron.log` and `sync.log`
   - No manual intervention needed

9. ✅ **All unit tests pass**
   - Slug generation (basic + special chars + conflicts)
   - Routing logic (project vs area vs resources)
   - Frontmatter generation (emoji stripping, arrays)

10. ✅ **Documentation complete**
    - This tech requirements document
    - Inline code comments
    - README for infra/scripts/

---

## Implementation Checklist

### Pre-Implementation

- [ ] Review and approve this tech requirements document
- [ ] Verify Notion property names (get screenshot confirmation)
- [ ] Confirm `NOTION_API_KEY` and `NOTION_NOTES_DATABASE_ID` in `.env`
- [ ] Ensure Phase 1 (PARA restructure) is complete

### Core Components

- [ ] Create `infra/scripts/modules/routing_engine.py`
- [ ] Create `infra/scripts/modules/frontmatter_generator.py`
- [ ] Create `infra/scripts/modules/slug_generator.py`
- [ ] Create `infra/scripts/modules/index_generator.py`
- [ ] Create `infra/scripts/modules/git_committer.py`

### Main Script

- [ ] Create `infra/scripts/notion_to_repo_sync.py`
- [ ] Implement `SyncOrchestrator` class
- [ ] Implement `query_notion_notes()` method
- [ ] Implement `filter_incremental()` method
- [ ] Implement `sync_note()` method
- [ ] Implement deletion detection and archiving
- [ ] Add error handling with retry logic

### Configuration

- [ ] Create `infra/config/sync_config.json`
- [ ] Add `.env` file with Notion credentials (git-ignored)
- [ ] Update `.gitignore` to exclude `.env` and logs

### Testing

- [ ] Write unit tests in `infra/tests/test_phase2.py`
- [ ] Run unit tests: `python -m unittest infra/tests/test_phase2.py`
- [ ] Create 3 golden test notes in Notion
- [ ] Run dry-run: `python infra/scripts/notion_to_repo_sync.py --dry-run`
- [ ] Run actual sync: `python infra/scripts/notion_to_repo_sync.py`
- [ ] Validate all 10 success criteria (see above)
- [ ] Test conflict resolution (manual edit in both Notion + repo)
- [ ] Test deletion handling (delete note in Notion)
- [ ] Test incremental sync (run twice without changes)

### Cron Setup

- [ ] Add crontab entry for 1am + 1pm syncs
- [ ] Verify cron execution: `crontab -l`
- [ ] Test cron manually: Wait for next scheduled run
- [ ] Review `infra/logs/cron.log` for errors

### Documentation

- [ ] Update project README with Phase 2 instructions
- [ ] Document INDEX.md structure and purpose
- [ ] Add inline code comments
- [ ] Create `infra/scripts/README.md`

### Cleanup

- [ ] Delete 3 golden test notes from Notion (prefix: `test-`)
- [ ] Delete test files from repos
- [ ] Review and clean up logs

### Final Validation

- [ ] All 10 success criteria met (see above)
- [ ] No errors in `sync_errors.log` for 24 hours
- [ ] Cron runs successfully for 3 consecutive days
- [ ] User validates INDEX.md navigation experience

---

## Time Estimate

| Task | Time |
|------|------|
| Core components (5 modules) | 2h |
| Main sync script | 1.5h |
| Configuration + environment setup | 0.5h |
| Unit tests | 1h |
| Integration testing (golden dataset) | 1h |
| Cron setup + debugging | 0.5h |
| Documentation | 0.5h |
| **Total** | **6-7 hours** |

**Assumes**:
- Phase 1 (PARA restructure) is complete
- Notion API credentials available
- No major blockers or scope changes

---

## Dependencies

**Required Before Starting Phase 2**:
- ✅ Phase 1 complete (PARA structure in place)
- ✅ Notion database schema finalized
- ✅ `.env` file with API credentials

**Blocks Phase 3**:
- Phase 2 must be complete and stable before starting Phase 3 (Repo → Notion sync)

---

## Notes

### Design Decisions

1. **Frontmatter-only state tracking**: Simpler than separate state file, source of truth is the file itself
2. **60-second conflict threshold**: Safer than 5 seconds, accounts for clock skew
3. **Archive on deletion**: Preserves content and git history, recoverable
4. **Grouped commits by note type**: Cleaner git history than per-file commits
5. **INDEX.md separate from RAG**: Human navigation vs machine retrieval (different purposes)

### Future Enhancements (Post-Phase 2)

- [ ] On-demand sync (manual trigger via Alfred/CLI)
- [ ] Email notifications on sync failures
- [ ] Notion blocks → markdown converter (full support for all block types)
- [ ] Bi-directional conflict resolution (merge strategies)
- [ ] Real-time sync (webhook-based, not cron)

---

## Questions for User

**Before implementation, confirm**:

1. ✅ Exact Notion property names (screenshot reviewed)
2. ✅ Script location: `infra/scripts/` (confirmed)
3. ✅ Git commits grouped by note type (confirmed)
4. ✅ Archive under `areas/archive/` (confirmed)
5. ✅ INDEX.md as part of Phase 2 (confirmed, 4-level nested structure)
6. ✅ Testing in production Notion workspace (confirmed)
7. ✅ Frontmatter-only state tracking (confirmed)
8. ✅ Error handling: retry + logging (confirmed)

**All questions resolved ✅**

---

**Phase 2 Tech Requirements - APPROVED AND READY FOR IMPLEMENTATION**
