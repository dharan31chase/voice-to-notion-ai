"""
Context Learning Utility

Provides intelligent context loading with profile learning:
- File type classification (always, latest, exemplar, synthesis, optional)
- Workstream-based suggestions
- Profile saving and loading
- Usage tracking for learning loop
"""

import json
import os
import re
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict


# Project root
project_root = Path.home() / "Documents" / "1. Projects" / "ai-assistant"


def setup_debug_logging() -> str:
    """
    Setup debug logging to file for context loading.

    Returns:
        Path to log file
    """
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"context-loader-{datetime.now().strftime('%Y-%m-%d')}.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return str(log_file)


def load_project_config() -> dict:
    """
    Load project configuration from docs/config/project-paths.json.

    Returns:
        Project configuration dict
    """
    config_path = project_root / "docs" / "config" / "project-paths.json"

    if not config_path.exists():
        raise FileNotFoundError(f"Project config not found at {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_file_type_patterns() -> dict:
    """
    Load file type patterns from docs/config/file-type-patterns.json.

    Returns:
        File type patterns dict
    """
    patterns_path = project_root / "docs" / "config" / "file-type-patterns.json"

    if not patterns_path.exists():
        raise FileNotFoundError(f"File type patterns not found at {patterns_path}")

    with open(patterns_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_project(user_input: str) -> Optional[dict]:
    """
    Find project by name or alias using natural language matching.

    Args:
        user_input: Project name or alias (e.g., "Legacy AI", "customer discovery")

    Returns:
        Project dict or None if not found

    Examples:
        - find_project("Legacy AI") → exact match
        - find_project("customer discovery") → alias match
        - find_project("legacy ai interview") → fuzzy match
    """
    config = load_project_config()
    user_input_lower = user_input.lower().strip()

    for project in config["projects"]:
        # Exact name match (case-insensitive)
        if project["name"].lower() == user_input_lower:
            return project

        # Alias match
        for alias in project["aliases"]:
            if alias.lower() == user_input_lower:
                return project

        # Fuzzy match: check if user input is substring of name or aliases
        if user_input_lower in project["name"].lower():
            return project

        for alias in project["aliases"]:
            if user_input_lower in alias.lower():
                return project

    return None


def classify_file_type(file_path: str) -> str:
    """
    Classify file type based on patterns.

    Priority: always > latest > exemplar > synthesis > optional

    Args:
        file_path: Relative file path

    Returns:
        File type: "always", "latest", "exemplar", "synthesis", or "optional"
    """
    patterns = load_file_type_patterns()

    # Sort by priority (lower number = higher priority)
    sorted_patterns = sorted(
        patterns["patterns"].items(),
        key=lambda x: x[1].get("priority", 999)
    )

    for type_name, config in sorted_patterns:
        if "regex" in config:
            for pattern in config["regex"]:
                if re.search(pattern, file_path, re.IGNORECASE):
                    return type_name

    return "optional"


def scan_folders(project: dict) -> List[dict]:
    """
    Scan project folders and return all markdown files with metadata.

    Args:
        project: Project dict from config

    Returns:
        List of file dicts with path, type, mtime
    """
    all_files = []
    root = Path(project["root_path"])

    for folder_rel in project["folders_to_scan"]:
        folder_path = root / folder_rel
        if not folder_path.exists():
            logging.warning(f"Folder not found: {folder_path}")
            continue

        # Recursively find all .md files
        for md_file in folder_path.rglob("*.md"):
            if md_file.name in ["TEMPLATE.md", ".gitkeep"]:
                continue

            rel_path = str(md_file.relative_to(root))
            file_type = classify_file_type(rel_path)
            mtime = md_file.stat().st_mtime

            all_files.append({
                "path": rel_path,
                "type": file_type,
                "mtime": mtime,
                "name": md_file.name
            })

    return all_files


def suggest_files_for_workstream(project: dict, workstream: str) -> List[dict]:
    """
    Suggest files for a given workstream.

    NEW: Supports workstream-specific configuration in project config.
    If project has "workstreams" section with config for this workstream,
    uses that. Otherwise falls back to generic heuristics.

    Workstream-specific config format:
    {
      "workstreams": {
        "synthesis": {
          "description": "Synthesizing insights across interviews",
          "always_files": ["path/to/meta-analysis.md"],
          "folders_with_latest": {
            "path/to/analyses": 3
          }
        }
      }
    }

    Generic heuristic strategy (fallback):
    1. Always include "always" type files
    2. For each folder, get latest file (by mtime)
    3. Include exemplar and synthesis files
    4. Limit to 3-6 total suggestions

    Args:
        project: Project dict from config
        workstream: Work stream name

    Returns:
        List of suggested files with type and path
    """
    # Check for workstream-specific configuration
    workstream_config = project.get("workstreams", {}).get(workstream)

    if workstream_config:
        # Use workstream-specific configuration
        logging.info(f"Using workstream-specific config for '{workstream}'")
        return suggest_files_from_workstream_config(project, workstream_config)
    else:
        # Fall back to generic heuristics
        logging.info(f"No workstream config for '{workstream}', using generic heuristics")
        return suggest_files_generic(project)


def suggest_files_from_workstream_config(project: dict, workstream_config: dict) -> List[dict]:
    """
    Suggest files using workstream-specific configuration.

    Args:
        project: Project dict from config
        workstream_config: Workstream-specific config dict

    Returns:
        List of suggested files
    """
    suggestions = []
    root = Path(project["root_path"])

    # 1. Add global always_files from project
    for always_file in project.get("always_files", []):
        file_path = root / always_file
        if file_path.exists():
            suggestions.append({
                "path": always_file,
                "type": "always",
                "mtime": file_path.stat().st_mtime,
                "name": file_path.name
            })

    # 2. Add workstream-specific always_files
    for always_file in workstream_config.get("always_files", []):
        file_path = root / always_file
        if file_path.exists():
            suggestions.append({
                "path": always_file,
                "type": "always",
                "mtime": file_path.stat().st_mtime,
                "name": file_path.name
            })
        else:
            logging.warning(f"Workstream always_file not found: {always_file}")

    # 3. Add last N files from specified folders
    for folder_rel, count in workstream_config.get("folders_with_latest", {}).items():
        folder_path = root / folder_rel
        if not folder_path.exists():
            logging.warning(f"Workstream folder not found: {folder_rel}")
            continue

        # Get all markdown files in folder
        md_files = []
        for md_file in folder_path.glob("*.md"):
            if md_file.name in ["TEMPLATE.md", ".gitkeep"]:
                continue

            rel_path = str(md_file.relative_to(root))
            file_type = classify_file_type(rel_path)
            mtime = md_file.stat().st_mtime

            md_files.append({
                "path": rel_path,
                "type": file_type,
                "mtime": mtime,
                "name": md_file.name
            })

        # Sort by mtime (descending) and take last N
        md_files.sort(key=lambda x: x["mtime"], reverse=True)
        suggestions.extend(md_files[:count])

    return suggestions


def suggest_files_generic(project: dict) -> List[dict]:
    """
    Suggest files using generic heuristics (fallback when no workstream config).

    Strategy:
    1. Always include "always" type files
    2. Get latest file overall (by mtime)
    3. Include exemplar files (up to 1)
    4. Include synthesis files (up to 1)
    5. Limit to 6 files max

    Args:
        project: Project dict from config

    Returns:
        List of suggested files
    """
    all_files = scan_folders(project)
    suggestions = []

    # 1. Add "always" files
    always_files = [f for f in all_files if f["type"] == "always"]
    suggestions.extend(always_files)

    # 2. Add latest file (highest mtime)
    non_always_files = [f for f in all_files if f["type"] != "always"]
    if non_always_files:
        latest = max(non_always_files, key=lambda x: x["mtime"])
        if latest not in suggestions:
            suggestions.append(latest)

    # 3. Add exemplar files (up to 1)
    exemplar_files = [f for f in all_files if f["type"] == "exemplar"]
    if exemplar_files:
        # Take most recent exemplar
        exemplar = max(exemplar_files, key=lambda x: x["mtime"])
        if exemplar not in suggestions:
            suggestions.append(exemplar)

    # 4. Add synthesis files (up to 1)
    synthesis_files = [f for f in all_files if f["type"] == "synthesis"]
    if synthesis_files:
        # Take most recent synthesis
        synthesis = max(synthesis_files, key=lambda x: x["mtime"])
        if synthesis not in suggestions:
            suggestions.append(synthesis)

    # Limit to 6 files max
    return suggestions[:6]


def load_profile(project_name: str, work_stream: str) -> Optional[dict]:
    """
    Load learned profile from context-profiles.json.

    Args:
        project_name: Project name
        work_stream: Work stream name

    Returns:
        Profile dict or None if not found
    """
    profile_path = project_root / "docs" / "config" / "context-profiles.json"

    if not profile_path.exists():
        return None

    with open(profile_path, 'r', encoding='utf-8') as f:
        profiles_data = json.load(f)

    profiles = profiles_data.get("profiles", {})
    return profiles.get(project_name, {}).get(work_stream)


def save_profile(project_name: str, work_stream: str, files: List[dict]):
    """
    Save user's file selection to learned profile.

    Args:
        project_name: Project name
        work_stream: Work stream name
        files: List of selected file dicts
    """
    profile_path = project_root / "docs" / "config" / "context-profiles.json"

    # Load existing profiles
    profiles_data = {"profiles": {}}
    if profile_path.exists():
        with open(profile_path, 'r', encoding='utf-8') as f:
            profiles_data = json.load(f)

    profiles = profiles_data.get("profiles", {})

    # Create/update profile
    if project_name not in profiles:
        profiles[project_name] = {}

    now = datetime.now(timezone.utc).isoformat()

    if work_stream in profiles[project_name]:
        # Update existing profile
        profile = profiles[project_name][work_stream]
        profile["last_used"] = now
        profile["usage_count"] = profile.get("usage_count", 0) + 1
        profile["files"] = [
            {
                "path": f["path"],
                "type": f["type"],
                "added": f.get("added", now)
            }
            for f in files
        ]
    else:
        # Create new profile
        profiles[project_name][work_stream] = {
            "created": now,
            "last_used": now,
            "usage_count": 1,
            "files": [
                {
                    "path": f["path"],
                    "type": f["type"],
                    "added": now
                }
                for f in files
            ]
        }

    profiles_data["profiles"] = profiles

    # Atomic write (temp file + rename)
    temp_path = str(profile_path) + ".tmp"
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(profiles_data, f, indent=2)

    os.rename(temp_path, profile_path)


def parse_user_selection(response: str, options: List[dict]) -> List[int]:
    """
    Parse user input like "1,2,3" or "all" into file indices.

    Supported formats:
    - "1,2,3" → Select files 1, 2, 3
    - "all" → Select all files
    - "" (empty) → Confirm learned profile (load all)

    Args:
        response: User input string
        options: List of file options

    Returns:
        List of selected indices (0-indexed)

    Raises:
        ValueError: If invalid format or out of range
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
                raise ValueError(f"Index {idx+1} out of range (1-{len(options)})")

        return indices

    except ValueError as e:
        raise ValueError(f"Invalid selection: {response}. Use format: '1,2,3' or 'all'")
