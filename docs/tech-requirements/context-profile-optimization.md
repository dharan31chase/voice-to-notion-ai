# Tech Requirements: Context Profile Optimization

**Status**: In Progress
**Owner**: Claude Code (Sonnet 4.5)
**Created**: 2025-11-17
**Parent PRD**: [Context Profile Optimization](../prd/context-profile-optimization.md)

---

## Summary

Implementing a learning context system that suggests 3-6 files based on work stream, learns from user selections, and auto-applies learned profiles. Phase 1 delivers core functionality in `full_server.py` (6-7 hours), with modular refactoring scheduled for Phase 2 after 3+ MCP tools exist.

**Key Design Decisions:**
- ✅ MCP tool integration (`start_session`)
- ✅ Config-driven project paths with natural language matching
- ✅ Simple numbered selection (`"1,2,3"` or `"all"`)
- ✅ Central profile storage in ai-assistant project
- ✅ Debug mode writes to log file
- ✅ Prompt for work_stream if not provided (backward compatible)

---

## Architecture

### Phase 1: Quick Implementation (This Session)

**Implementation Location:** `mcp_server/full_server.py`

**New Functions:**
```python
# Context Loading
def start_session(project_name: str, work_stream: str, debug: bool = False)
def suggest_files_for_workstream(project: dict, workstream: str) -> dict
def load_profile(project_name: str, work_stream: str) -> dict | None
def save_profile(project_name: str, work_stream: str, files: list)
def update_profile(project_name: str, work_stream: str, files: list)

# Project Management
def find_project(user_input: str) -> dict
def load_project_config() -> dict

# File Discovery
def scan_folders(project: dict) -> list
def detect_latest_files(folder: str) -> list
def classify_file_type(file_path: str) -> str

# User Interaction
def parse_user_selection(response: str, options: list) -> list
def display_numbered_list(files: list)
```

**Config Files:**
```
ai-assistant/
  docs/
    config/
      project-paths.json       # Project name → path mapping + aliases
      file-type-patterns.json  # Regex patterns for auto-classification
      context-profiles.json    # Learned profiles per project/workstream
```

**Log Files:**
```
ai-assistant/
  logs/
    context-loader-YYYY-MM-DD.log  # Debug mode output
```

---

### Phase 2: Modular Refactoring (After 3+ MCP Tools)

**⚠️ TRACKED IN ROADMAP** - See "Refactor MCP Server to Modular Architecture"

**Target Structure:**
```
mcp_server/
  full_server.py              # Main entry point (routing only)
  tools/
    __init__.py
    session_manager.py        # start_session, end_session
    context_loader.py         # Profile management
    project_manager.py        # Project path mapping
  utils/
    file_discovery.py         # Folder scanning
    profile_storage.py        # JSON persistence
    input_parser.py           # User input parsing
  config/
    project_paths.json
```

**Refactoring Triggers:**
- When 3+ MCP tools exist
- When `full_server.py` exceeds 1000 lines
- When adding cross-tool shared utilities

**Estimated Effort:** 2-3 hours

---

## Configuration Schema

### 1. Project Paths (`docs/config/project-paths.json`)

```json
{
  "projects": [
    {
      "name": "Legacy AI",
      "aliases": ["legacy ai", "legacy-ai", "legacy", "customer discovery"],
      "root_path": "/Users/dharanchandrahasan/Documents/1. Projects/legacy-ai",
      "folders_to_scan": [
        "interview-guides",
        "insights",
        "research/customer-interviews"
      ],
      "always_files": [
        "requirements-vision.md",
        "product-strategy.md"
      ]
    },
    {
      "name": "Epic 2nd Brain",
      "aliases": ["ai-assistant", "2nd brain", "epic", "mcp", "orchestrator"],
      "root_path": "/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant",
      "folders_to_scan": [
        "docs/prd",
        "docs/sessions",
        "docs/context"
      ],
      "always_files": [
        "docs/roadmap.md",
        "docs/Systems_Thinking_Workbook.md"
      ]
    }
  ]
}
```

### 2. File Type Patterns (`docs/config/file-type-patterns.json`)

```json
{
  "patterns": {
    "always": {
      "regex": ["requirements.*\\.md$", "roadmap\\.md$", "vision\\.md$"],
      "priority": 1
    },
    "latest": {
      "detection": "modification_date",
      "priority": 2
    },
    "exemplar": {
      "regex": [".*exemplar.*\\.md$", ".*reference.*\\.md$"],
      "priority": 3
    },
    "synthesis": {
      "regex": [".*meta.*analysis.*\\.md$", ".*comparison.*\\.md$", ".*validation.*\\.md$"],
      "priority": 4
    }
  }
}
```

### 3. Context Profiles (`docs/config/context-profiles.json`)

```json
{
  "Legacy AI": {
    "interview-analysis": {
      "created": "2025-11-17T10:30:00Z",
      "last_used": "2025-11-17T14:45:00Z",
      "usage_count": 3,
      "files": [
        {
          "path": "interview-guides/sarah-cronin.md",
          "type": "latest",
          "added": "2025-11-17T10:30:00Z"
        },
        {
          "path": "interview-guides/missy-bob-exemplar.md",
          "type": "exemplar",
          "added": "2025-11-17T10:30:00Z"
        },
        {
          "path": "insights/segment-comparison-meta-analysis.md",
          "type": "synthesis",
          "added": "2025-11-17T10:30:00Z"
        },
        {
          "path": "requirements-vision.md",
          "type": "always",
          "added": "2025-11-17T10:30:00Z"
        }
      ],
      "always_suggest": [
        "product-strategy.md"
      ]
    }
  }
}
```

---

## Implementation Details

### File Discovery Logic

**1. Scan Known Folders:**
```python
def scan_folders(project: dict) -> list:
    """
    Scan project folders and return all markdown files.

    Returns: List of file paths relative to project root
    """
    all_files = []
    root = project["root_path"]

    for folder in project["folders_to_scan"]:
        folder_path = os.path.join(root, folder)
        if not os.path.exists(folder_path):
            continue

        # Recursively find all .md files
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.endswith('.md'):
                    rel_path = os.path.relpath(
                        os.path.join(dirpath, filename),
                        root
                    )
                    all_files.append(rel_path)

    return all_files
```

**2. Detect Latest Files:**
```python
def detect_latest_files(folder: str) -> list:
    """
    Sort files by modification date, return most recent.

    Returns: List of (file_path, mtime) tuples
    """
    files = []
    for file_path in os.listdir(folder):
        if file_path.endswith('.md'):
            mtime = os.path.getmtime(os.path.join(folder, file_path))
            files.append((file_path, mtime))

    # Sort by mtime descending
    files.sort(key=lambda x: x[1], reverse=True)

    return files
```

**3. Classify File Type:**
```python
def classify_file_type(file_path: str) -> str:
    """
    Match file against patterns to determine type.

    Priority: always > latest > exemplar > synthesis > optional
    """
    patterns = load_file_type_patterns()

    for type_name, config in sorted(patterns["patterns"].items(),
                                   key=lambda x: x[1]["priority"]):
        if "regex" in config:
            for pattern in config["regex"]:
                if re.match(pattern, file_path, re.IGNORECASE):
                    return type_name

    return "optional"
```

### Profile Management

**Load Profile:**
```python
def load_profile(project_name: str, work_stream: str) -> dict | None:
    """
    Load learned profile from context-profiles.json.

    Returns: Profile dict or None if not found
    """
    profile_path = "docs/config/context-profiles.json"

    if not os.path.exists(profile_path):
        return None

    with open(profile_path) as f:
        profiles = json.load(f)

    return profiles.get(project_name, {}).get(work_stream)
```

**Save Profile:**
```python
def save_profile(project_name: str, work_stream: str, files: list):
    """
    Save user's file selection to learned profile.

    Updates: created, last_used, usage_count, files
    """
    profile_path = "docs/config/context-profiles.json"

    # Load existing profiles
    profiles = {}
    if os.path.exists(profile_path):
        with open(profile_path) as f:
            profiles = json.load(f)

    # Create/update profile
    if project_name not in profiles:
        profiles[project_name] = {}

    now = datetime.now(timezone.utc).isoformat()

    if work_stream in profiles[project_name]:
        # Update existing
        profile = profiles[project_name][work_stream]
        profile["last_used"] = now
        profile["usage_count"] += 1
        profile["files"] = files
    else:
        # Create new
        profiles[project_name][work_stream] = {
            "created": now,
            "last_used": now,
            "usage_count": 1,
            "files": files,
            "always_suggest": []
        }

    # Atomic write (temp file + rename)
    temp_path = profile_path + ".tmp"
    with open(temp_path, 'w') as f:
        json.dump(profiles, f, indent=2)
    os.rename(temp_path, profile_path)
```

### User Input Parsing

**Parse Selection:**
```python
def parse_user_selection(response: str, options: list) -> list:
    """
    Parse user input like "1,2,3" or "all" into file list.

    Supported formats:
    - "1,2,3" → Select files 1, 2, 3
    - "all" → Select all files
    - "" (empty) → Confirm learned profile (load all)

    Returns: List of selected file indices (0-indexed)
    """
    response = response.strip().lower()

    if not response or response == "all":
        # Empty or "all" → select everything
        return list(range(len(options)))

    # Parse "1,2,3" format
    try:
        indices = [int(x.strip()) - 1 for x in response.split(',')]
        # Validate indices
        for idx in indices:
            if idx < 0 or idx >= len(options):
                raise ValueError(f"Index {idx+1} out of range")
        return indices
    except ValueError as e:
        raise ValueError(f"Invalid selection: {response}. Use format: '1,2,3' or 'all'")
```

### MCP Tool Interface

**start_session Tool:**
```python
@mcp_server.tool()
async def start_session(
    project_name: str,
    work_stream: str = None,
    debug: bool = False
) -> dict:
    """
    Start a new session with intelligent context loading.

    Args:
        project_name: Project name or alias (e.g., "Legacy AI", "customer discovery")
        work_stream: Work stream type (e.g., "interview-analysis", "synthesis")
        debug: Enable debug logging to file

    Returns:
        {
            "status": "success",
            "files_loaded": ["path1", "path2"],
            "profile_saved": true,
            "message": "Loaded 4 files for Legacy AI interview-analysis"
        }
    """
    # Setup debug logging
    if debug:
        setup_debug_logging()

    # Find project
    project = find_project(project_name)

    # Prompt for work_stream if not provided
    if not work_stream:
        work_stream = prompt_for_workstream(project)

    # Check for learned profile
    profile = load_profile(project["name"], work_stream)

    if profile:
        # Learned profile exists
        files_to_load = show_learned_profile(profile)
    else:
        # First time - suggest files
        suggestions = suggest_files_for_workstream(project, work_stream)
        selected_indices = prompt_user_selection(suggestions)
        files_to_load = [suggestions[i] for i in selected_indices]

        # Save learned profile
        save_profile(project["name"], work_stream, files_to_load)

    # Load files (using existing Read tool)
    context = load_files_into_context(project["root_path"], files_to_load)

    return {
        "status": "success",
        "files_loaded": files_to_load,
        "profile_saved": profile is None,
        "message": f"Loaded {len(files_to_load)} files for {project['name']} {work_stream}"
    }
```

---

## Testing Plan

### Unit Tests (Phase 1)

**Test File:** `tests/test_context_loader.py`

```python
def test_parse_user_selection():
    options = ["file1.md", "file2.md", "file3.md"]

    # Test "1,2,3"
    assert parse_user_selection("1,2,3", options) == [0, 1, 2]

    # Test "all"
    assert parse_user_selection("all", options) == [0, 1, 2]

    # Test empty (confirm)
    assert parse_user_selection("", options) == [0, 1, 2]

    # Test invalid
    with pytest.raises(ValueError):
        parse_user_selection("5,6", options)

def test_classify_file_type():
    assert classify_file_type("requirements-vision.md") == "always"
    assert classify_file_type("interview-guide-exemplar.md") == "exemplar"
    assert classify_file_type("segment-meta-analysis.md") == "synthesis"

def test_find_project():
    # Exact match
    assert find_project("Legacy AI")["name"] == "Legacy AI"

    # Alias match
    assert find_project("customer discovery")["name"] == "Legacy AI"

    # Fuzzy match
    assert find_project("legacy ai interview")["name"] == "Legacy AI"
```

### Integration Tests (Phase 5)

**Test Scenarios:**

1. **First-Time Suggestion** (<5s)
   ```python
   result = start_session("Legacy AI", "interview-analysis", debug=True)
   assert result["status"] == "success"
   assert len(result["files_loaded"]) >= 3
   assert result["profile_saved"] == True
   ```

2. **Learned Profile Loading**
   ```python
   # Run twice
   start_session("Legacy AI", "interview-analysis")
   result = start_session("Legacy AI", "interview-analysis")
   assert result["profile_saved"] == False  # Already exists
   ```

3. **Missing File Handling**
   ```python
   # Manually edit profile to include non-existent file
   # System should warn and offer to remove
   ```

4. **Empty Folder**
   ```python
   # Delete all files from interview-guides/
   # Should skip that folder, suggest from others
   ```

---

## Success Criteria Validation

| Criterion | Target | How to Measure | Status |
|-----------|--------|----------------|--------|
| First-time suggestion <5s | <5s | Time from call to numbered list | ⏳ To test |
| Profile learning works | 100% | Check context-profiles.json after approval | ⏳ To test |
| Second-time uses profile | 100% | Repeat session shows learned files | ⏳ To test |
| Signal-to-noise >80% | >80% | % of loaded docs Claude references | ⏳ To validate |
| Loading time <3s | <3s | Time from approval to context ready | ⏳ To test |

---

## Roadmap Integration

**Added to Roadmap:**

**[ROADMAP-X] Refactor MCP Server to Modular Architecture**
- **Description**: Extract context loading, session management, and project management into separate modules under `mcp_server/tools/` with shared utilities in `mcp_server/utils/`. Follow Single Responsibility Principle (SRP).
- **Priority**: Medium (after 3+ MCP tools exist)
- **Effort**: 2-3 hours
- **Dependencies**: Context Profile Optimization (this feature)
- **Why**: Current implementation in `full_server.py` is quick to ship but will become unmaintainable as MCP server grows. Modular architecture enables adding 10+ tools without bloat.
- **Gate**: Trigger when `full_server.py` exceeds 1000 lines OR when adding 3rd MCP tool

---

## Open Questions

1. **Profile Versioning**: Should we version context-profiles.json schema in case structure changes?
   - **Decision**: Not yet - wait until schema evolves

2. **Profile Sharing**: Should profiles be shareable across machines (export/import)?
   - **Decision**: Post-launch (Nice to Have in PRD)

3. **Semantic Search**: Should we add content-based file suggestions?
   - **Decision**: Tier 1 (after 50+ sessions with profiles)

---

## Version History

| Date | Author | Changes |
|------|--------|---------|
| 2025-11-17 | Claude Code (Sonnet 4.5) | Initial tech requirements based on approved PRD. Phase 1 implementation in `full_server.py`, Phase 2 modular refactoring tracked in roadmap. |

---

**End of Tech Requirements**
