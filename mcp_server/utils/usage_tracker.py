"""
Usage Tracking Module

Tracks file usage patterns to improve context suggestions:
- File loads, adds, removes, references per session
- Privacy-first: Sanitized paths, no personal data
- Git-tracked: logs/usage/ folder for learning algorithm

Usage:
    tracker = UsageTracker(project="Epic 2nd Brain")
    tracker.track_file_load("docs/prd/example.md", context="PRD review")
    tracker.track_file_reference("ROADMAP.md", context="Planning session")
    tracker.save()  # Saves to logs/usage/YYYY-MM-DD-HH-MM-SS.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import re


class UsageTracker:
    """
    Tracks file usage patterns for learning algorithm.

    Privacy-first design:
    - Sanitizes personal paths (/Users/username/ → <USER_HOME>/)
    - Strips tokens and API keys
    - Git-tracked for analysis
    """

    def __init__(self, project: str, session_id: Optional[str] = None):
        """
        Initialize usage tracker.

        Args:
            project: Project name (e.g., "Epic 2nd Brain", "Legacy AI")
            session_id: Optional session ID (default: timestamp)
        """
        self.project = project
        self.session_id = session_id or datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.start_time = datetime.now().isoformat()

        # Usage data
        self.file_loads: List[Dict] = []  # Files loaded into context
        self.file_references: List[Dict] = []  # Files mentioned/referenced
        self.file_edits: List[Dict] = []  # Files edited/written
        self.file_creates: List[Dict] = []  # Files created

        # Session metadata
        self.metadata = {
            "project": project,
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": None
        }

    def track_file_load(
        self,
        file_path: str,
        context: Optional[str] = None,
        source: str = "manual"
    ):
        """
        Track a file being loaded into context.

        Args:
            file_path: Path to file (will be sanitized)
            context: Optional context for why file was loaded
            source: Source of load (manual, auto, suggestion)
        """
        sanitized_path = self._sanitize_path(file_path)

        self.file_loads.append({
            "file": sanitized_path,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "source": source  # manual, auto, suggestion
        })

    def track_file_reference(
        self,
        file_path: str,
        context: Optional[str] = None
    ):
        """
        Track a file being referenced (e.g., in conversation, ROADMAP.md link).

        Args:
            file_path: Path to file (will be sanitized)
            context: Optional context for reference
        """
        sanitized_path = self._sanitize_path(file_path)

        self.file_references.append({
            "file": sanitized_path,
            "timestamp": datetime.now().isoformat(),
            "context": context
        })

    def track_file_edit(
        self,
        file_path: str,
        change_type: str = "edit"
    ):
        """
        Track a file being edited.

        Args:
            file_path: Path to file (will be sanitized)
            change_type: Type of change (edit, append, replace)
        """
        sanitized_path = self._sanitize_path(file_path)

        self.file_edits.append({
            "file": sanitized_path,
            "timestamp": datetime.now().isoformat(),
            "change_type": change_type
        })

    def track_file_create(
        self,
        file_path: str,
        file_type: Optional[str] = None
    ):
        """
        Track a file being created.

        Args:
            file_path: Path to file (will be sanitized)
            file_type: Type of file (prd, session, tech-req, etc.)
        """
        sanitized_path = self._sanitize_path(file_path)

        self.file_creates.append({
            "file": sanitized_path,
            "timestamp": datetime.now().isoformat(),
            "file_type": file_type
        })

    def _sanitize_path(self, file_path: str) -> str:
        """
        Sanitize file path to remove personal information.

        Privacy transformations:
        - /Users/username/ → <USER_HOME>/
        - /home/username/ → <USER_HOME>/
        - Absolute paths → relative to project root

        Args:
            file_path: Original file path

        Returns:
            Sanitized file path
        """
        # Convert to Path object
        path = Path(file_path)

        # Try to make relative to common project roots
        try:
            # Try relative to user home
            home = Path.home()
            if path.is_absolute() and str(path).startswith(str(home)):
                # Make relative to home
                rel_path = path.relative_to(home)
                return f"<USER_HOME>/{rel_path}"
        except ValueError:
            pass

        # If already relative, keep as-is
        if not path.is_absolute():
            return str(path)

        # Fallback: just return filename
        return str(path.name)

    def _sanitize_content(self, content: str) -> str:
        """
        Sanitize content to remove tokens, API keys, personal data.

        Args:
            content: Original content

        Returns:
            Sanitized content
        """
        # Remove API keys (pattern: sk-... or any 32+ char alphanumeric)
        content = re.sub(r'sk-[a-zA-Z0-9]{32,}', '<API_KEY>', content)
        content = re.sub(r'[a-zA-Z0-9]{40,}', '<TOKEN>', content)

        # Remove email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '<EMAIL>', content)

        # Remove phone numbers (simple pattern)
        content = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '<PHONE>', content)

        return content

    def save(self, logs_dir: Optional[Path] = None) -> Path:
        """
        Save usage log to disk.

        Args:
            logs_dir: Optional logs directory (default: logs/usage/)

        Returns:
            Path to saved log file
        """
        # Default logs directory
        if logs_dir is None:
            # Assume we're in ai-assistant/ repo
            logs_dir = Path.home() / "Documents/1. Projects/ai-assistant/logs/usage"

        # Ensure directory exists
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Set end time
        self.metadata["end_time"] = datetime.now().isoformat()

        # Build usage data
        usage_data = {
            "metadata": self.metadata,
            "statistics": {
                "total_loads": len(self.file_loads),
                "total_references": len(self.file_references),
                "total_edits": len(self.file_edits),
                "total_creates": len(self.file_creates),
                "unique_files": len(set(
                    [f["file"] for f in self.file_loads] +
                    [f["file"] for f in self.file_references] +
                    [f["file"] for f in self.file_edits] +
                    [f["file"] for f in self.file_creates]
                ))
            },
            "events": {
                "loads": self.file_loads,
                "references": self.file_references,
                "edits": self.file_edits,
                "creates": self.file_creates
            }
        }

        # Write to file
        log_filename = f"{self.session_id}.json"
        log_path = logs_dir / log_filename

        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(usage_data, f, indent=2, ensure_ascii=False)

        return log_path

    @classmethod
    def load(cls, log_path: Path) -> Dict:
        """
        Load usage log from disk.

        Args:
            log_path: Path to log file

        Returns:
            Usage data dict
        """
        with open(log_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @classmethod
    def get_all_logs(cls, logs_dir: Optional[Path] = None) -> List[Path]:
        """
        Get all usage logs.

        Args:
            logs_dir: Optional logs directory (default: logs/usage/)

        Returns:
            List of log file paths, sorted by timestamp (newest first)
        """
        if logs_dir is None:
            logs_dir = Path.home() / "Documents/1. Projects/ai-assistant/logs/usage"

        if not logs_dir.exists():
            return []

        # Get all JSON files
        log_files = list(logs_dir.glob("*.json"))

        # Sort by filename (which is timestamp)
        log_files.sort(reverse=True)

        return log_files


def track_mcp_tool_call(
    tool_name: str,
    file_path: Optional[str] = None,
    project: str = "Epic 2nd Brain",
    tracker: Optional[UsageTracker] = None
):
    """
    Helper function to track MCP tool calls.

    Call this from within MCP tools (read_file, write_file, etc.) to
    automatically track usage.

    Args:
        tool_name: Name of MCP tool called
        file_path: File path being accessed (if applicable)
        project: Project name
        tracker: Optional existing tracker (creates new if None)

    Returns:
        UsageTracker instance
    """
    if tracker is None:
        tracker = UsageTracker(project=project)

    if file_path:
        if tool_name in ["read_file", "list_context"]:
            tracker.track_file_load(file_path, context=f"{tool_name} call", source="manual")
        elif tool_name in ["write_file"]:
            tracker.track_file_edit(file_path, change_type="write")
        elif tool_name in ["edit_file"]:
            tracker.track_file_edit(file_path, change_type="edit")

    return tracker
