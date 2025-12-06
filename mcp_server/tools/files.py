"""
File Operations Tools

Provides file read/write operations with backup and multi-project support.
"""

from pathlib import Path
from typing import Optional
import logging

from ..utils.backup import create_backup


# Multi-Project Configuration
PROJECT_CONFIG = {
    "Epic 2nd Brain": {
        "repo_path": Path.home() / "Documents" / "1. Projects" / "ai-assistant",
        "context_folders": ["docs/prd", "docs/tech-requirements", "docs/sessions"],
        "session_log_path": "docs/sessions/claude-chat",
        "strategy_board_view": "Epic 2nd Brain Only"
    },
    "Legacy AI": {
        "repo_path": Path.home() / "Documents" / "1. Projects" / "legacy-ai",
        "context_folders": ["research", "product", "business", "sessions"],
        "session_log_path": "sessions/customer-discovery",
        "strategy_board_view": "Legacy AI Only"
    },
    "Lifeadmin": {
        "repo_path": Path.home() / "Documents" / "1. Projects" / "lifeadmin",
        "context_folders": ["decisions"],
        "session_log_path": "sessions/financial-planning",
        "strategy_board_view": "Lifeadmin Only"
    }
}


def read_file(path: str, project: str = "Epic 2nd Brain") -> str:
    """
    🎯 USE THIS FIRST: Read a file from a project repo.

    IMPORTANT: Use this tool instead of bash commands like cat, view, or head.
    This tool is optimized for reading project documentation and supports
    multi-project access with proper path resolution.

    Args:
        path: Relative path from repo root (e.g., 'docs/prd/feature.md')
        project: Project name (default: "Epic 2nd Brain")
                 Options: "Epic 2nd Brain", "Legacy AI", "Lifeadmin"

    Returns:
        File contents as string

    Examples:
        - read_file("README.md")
        - read_file("docs/prd/context-sync-bridge.md")
        - read_file("research/requirements-vision.md", project="Legacy AI")
        - read_file("decisions/decision-log.md", project="Lifeadmin")
    """
    # Get project repo path
    if project not in PROJECT_CONFIG:
        return f"Error: Unknown project '{project}'. Valid options: {list(PROJECT_CONFIG.keys())}"

    repo_path = PROJECT_CONFIG[project]["repo_path"]
    full_path = repo_path / path

    if not full_path.exists():
        return f"Error: File not found at {full_path}"

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(path: str, content: str, project: str = "Epic 2nd Brain", create_backup: bool = True) -> dict:
    """
    🎯 USE THIS FIRST: Write a file to a project repo.

    IMPORTANT: Use this tool instead of bash commands like echo >, cat with heredoc,
    or redirection operators. This tool handles multi-project paths, creates parent
    directories automatically, and provides proper error handling.

    This enables Claude (chat) to create PRDs, session logs, and other
    docs directly in the repo without using /mnt/user-data/outputs workaround.

    NEW: Automatically creates backup before overwriting existing files.
    Backups are stored in .backups/ subfolder (last 3 versions kept).

    Args:
        path: Relative path from repo root (e.g., 'docs/prd/feature.md')
        content: Full file content to write
        project: Project name (default: "Epic 2nd Brain")
                 Options: "Epic 2nd Brain", "Legacy AI", "Lifeadmin"
        create_backup: Create backup before overwrite (default: True)

    Returns:
        Dict with status and file path

    Security:
        - Only allows writes within project repos
        - Creates parent directories if needed
        - Overwrites existing files (with backup if enabled)

    Examples:
        - write_file("docs/prd/new-feature.md", "# PRD: New Feature...")
        - write_file("research/requirements-vision.md", "# Requirements...", project="Legacy AI")
        - write_file("decisions/decision-log.md", "# Decision Log...", project="Lifeadmin")
    """
    # Get project repo path
    if project not in PROJECT_CONFIG:
        return {
            "status": "error",
            "message": f"Unknown project '{project}'. Valid options: {list(PROJECT_CONFIG.keys())}"
        }

    repo_path = PROJECT_CONFIG[project]["repo_path"]
    full_path = repo_path / path

    # Security: Ensure path is within project
    try:
        full_path = full_path.resolve()
        if not str(full_path).startswith(str(repo_path)):
            return {
                "status": "error",
                "message": f"Path {path} is outside project root"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Invalid path: {str(e)}"
        }

    # Create backup if file exists and backup enabled
    backup_path = None
    if create_backup and full_path.exists():
        from ..utils.backup import create_backup as do_backup
        backup_path = do_backup(full_path)

    # Create parent directories if needed
    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating directories: {str(e)}"
        }

    # Write file
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        result = {
            "status": "success",
            "path": str(full_path),
            "relative_path": path,
            "message": f"File written successfully: {path}"
        }

        if backup_path:
            result["backup_created"] = str(backup_path)
            result["message"] += f" (backup: {backup_path.name})"

        return result

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error writing file: {str(e)}"
        }
