"""
Handoff Detection Module (Phase 7.2)

Auto-detect handoffs between Claude Chat and Claude Code via YAML frontmatter.
Scans docs/handoffs/ for pending handoffs and enables context loading.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HandoffDetector:
    """
    Detect and manage handoffs between agents using YAML frontmatter.

    Workflow:
    1. scan_for_handoffs() - Find pending handoffs for agent
    2. parse_handoff_frontmatter() - Extract YAML metadata
    3. validate_handoff() - Validate required fields and formats
    4. mark_handoff_status() - Update handoff status (accepted/rejected/completed)
    """

    VALID_AGENTS = ["claude-code", "claude-chat"]
    VALID_PRIORITIES = ["P0", "P1", "P2", "P3"]
    VALID_STATUSES = ["pending", "accepted", "rejected", "completed"]
    VALID_TYPES = ["implementation", "validation", "decision", "research", "bug-fix"]

    def __init__(self, repo_path: Path):
        """
        Initialize handoff detector for a repository.

        Args:
            repo_path: Path to repository (e.g., Epic 2nd Brain)
        """
        self.repo_path = Path(repo_path)
        self.handoffs_dir = self.repo_path / "docs" / "handoffs"

        # Ensure handoffs directory exists
        self.handoffs_dir.mkdir(parents=True, exist_ok=True)

    def scan_for_handoffs(
        self,
        agent: str = "claude-code",
        status: Optional[str] = "pending",
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan for handoffs matching criteria.

        Args:
            agent: Target agent (claude-code or claude-chat)
            status: Filter by status (default: pending)
            priority: Filter by priority (P0, P1, P2, P3) - optional

        Returns:
            List of handoff dicts with parsed frontmatter and file path
        """
        if agent not in self.VALID_AGENTS:
            raise ValueError(f"Invalid agent '{agent}'. Must be one of {self.VALID_AGENTS}")

        if status and status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {self.VALID_STATUSES}")

        handoffs = []

        # Find all markdown files in handoffs directory
        if not self.handoffs_dir.exists():
            logger.warning(f"Handoffs directory does not exist: {self.handoffs_dir}")
            return []

        for handoff_file in self.handoffs_dir.glob("*.md"):
            try:
                # Parse frontmatter
                handoff_data = self.parse_handoff_frontmatter(handoff_file)

                if not handoff_data:
                    continue

                # Filter by agent
                if handoff_data.get("to") != agent:
                    continue

                # Filter by status
                if status and handoff_data.get("status") != status:
                    continue

                # Filter by priority (optional)
                if priority and handoff_data.get("priority") != priority:
                    continue

                # Add file path to handoff data
                handoff_data["file_path"] = handoff_file
                handoff_data["file_name"] = handoff_file.name

                handoffs.append(handoff_data)

            except Exception as e:
                logger.error(f"Error parsing handoff {handoff_file}: {e}")
                continue

        # Sort by priority (P0 > P1 > P2 > P3) then by date (newest first)
        def sort_key(h):
            priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
            priority_val = priority_order.get(h.get("priority", "P3"), 3)

            # Extract date from filename (YYYY-MM-DD)
            date_match = re.match(r"(\d{4}-\d{2}-\d{2})", h["file_name"])
            date_str = date_match.group(1) if date_match else "0000-00-00"

            return (priority_val, date_str)  # Lower priority number = higher priority

        handoffs.sort(key=sort_key, reverse=True)

        return handoffs

    def parse_handoff_frontmatter(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse YAML frontmatter from handoff markdown file.

        Expected format:
        ---
        to: claude-code
        from: claude-chat
        initiative_id: abc123
        prd_path: docs/prd/feature.md
        priority: P1
        type: implementation
        status: pending
        ---

        Args:
            file_path: Path to handoff markdown file

        Returns:
            Dict with frontmatter fields, or None if no frontmatter found
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return None

        # Extract YAML frontmatter (between --- markers)
        frontmatter_match = re.match(
            r'^---\s*\n(.*?)\n---\s*\n',
            content,
            re.DOTALL
        )

        if not frontmatter_match:
            logger.warning(f"No YAML frontmatter found in {file_path}")
            return None

        frontmatter_text = frontmatter_match.group(1)

        # Parse YAML manually (simple key: value format)
        # NOTE: Using simple regex parser to avoid PyYAML dependency
        # For production, consider using PyYAML: yaml.safe_load(frontmatter_text)

        handoff_data = {}

        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Handle simple key: value
            if ':' in line and not line.startswith('-'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                handoff_data[key] = value

            # Handle list items (context_files, etc.)
            elif line.startswith('-'):
                # Find the key for this list (look backwards)
                list_key = None
                for prev_line in reversed(frontmatter_text.split('\n')):
                    if ':' in prev_line and not prev_line.strip().startswith('-'):
                        list_key = prev_line.split(':')[0].strip()
                        break

                if list_key:
                    if list_key not in handoff_data:
                        handoff_data[list_key] = []

                    value = line[1:].strip()  # Remove leading '-'
                    if value:
                        handoff_data[list_key].append(value)

        # Extract summary from markdown body (first paragraph after frontmatter)
        body = content[frontmatter_match.end():].strip()

        # Get first heading as summary
        heading_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
        if heading_match:
            handoff_data["summary"] = heading_match.group(1)
        else:
            # Use first line as summary
            first_line = body.split('\n')[0] if body else ""
            handoff_data["summary"] = first_line[:100]

        return handoff_data

    def validate_handoff(self, handoff_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate handoff frontmatter fields.

        Args:
            handoff_data: Parsed handoff frontmatter

        Returns:
            Dict with:
                - valid: bool
                - errors: List[str] (validation errors)
                - warnings: List[str] (non-critical issues)
        """
        errors = []
        warnings = []

        # Required fields
        required_fields = ["to", "from", "initiative_id", "prd_path", "priority", "type", "status"]

        for field in required_fields:
            if field not in handoff_data or not handoff_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate enum values
        if "to" in handoff_data and handoff_data["to"] not in self.VALID_AGENTS:
            errors.append(f"Invalid 'to' agent: {handoff_data['to']}. Must be one of {self.VALID_AGENTS}")

        if "from" in handoff_data and handoff_data["from"] not in self.VALID_AGENTS:
            errors.append(f"Invalid 'from' agent: {handoff_data['from']}. Must be one of {self.VALID_AGENTS}")

        if "priority" in handoff_data and handoff_data["priority"] not in self.VALID_PRIORITIES:
            errors.append(f"Invalid priority: {handoff_data['priority']}. Must be one of {self.VALID_PRIORITIES}")

        if "status" in handoff_data and handoff_data["status"] not in self.VALID_STATUSES:
            errors.append(f"Invalid status: {handoff_data['status']}. Must be one of {self.VALID_STATUSES}")

        if "type" in handoff_data and handoff_data["type"] not in self.VALID_TYPES:
            warnings.append(f"Uncommon type: {handoff_data['type']}. Recommended: {self.VALID_TYPES}")

        # Validate initiative_id format (32-char Notion ID)
        if "initiative_id" in handoff_data:
            initiative_id = handoff_data["initiative_id"]
            # Remove hyphens for validation
            clean_id = initiative_id.replace('-', '')
            if len(clean_id) != 32:
                errors.append(f"Invalid initiative_id format: {initiative_id}. Must be 32-char Notion page ID")

        # Validate file paths exist (optional - warn if not)
        if "prd_path" in handoff_data:
            prd_path = self.repo_path / handoff_data["prd_path"]
            if not prd_path.exists():
                warnings.append(f"PRD file not found: {handoff_data['prd_path']}")

        if "tech_requirements_path" in handoff_data:
            tech_req_path = self.repo_path / handoff_data["tech_requirements_path"]
            if not tech_req_path.exists():
                warnings.append(f"Tech requirements file not found: {handoff_data['tech_requirements_path']}")

        # Validate context_files exist
        if "context_files" in handoff_data:
            for context_file in handoff_data["context_files"]:
                context_path = self.repo_path / context_file
                if not context_path.exists():
                    warnings.append(f"Context file not found: {context_file}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def mark_handoff_status(
        self,
        file_path: Path,
        new_status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update handoff status in YAML frontmatter.

        Args:
            file_path: Path to handoff file
            new_status: New status (accepted, rejected, completed)
            notes: Optional notes to append

        Returns:
            True if update successful, False otherwise
        """
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Must be one of {self.VALID_STATUSES}")

        try:
            content = file_path.read_text(encoding='utf-8')

            # Update status in YAML frontmatter
            # Match status: <value> and replace
            updated_content = re.sub(
                r'^(status:\s*)(.+)$',
                f'\\1{new_status}',
                content,
                count=1,
                flags=re.MULTILINE
            )

            # Add timestamp for status change
            timestamp = datetime.now().isoformat()
            status_history_line = f"{new_status}_at: {timestamp}"

            # Insert timestamp after status line
            updated_content = re.sub(
                r'^(status:\s*.+)$',
                f'\\1\n{status_history_line}',
                updated_content,
                count=1,
                flags=re.MULTILINE
            )

            # Add notes if provided
            if notes:
                # Add to frontmatter
                notes_line = f"status_notes: \"{notes}\""
                updated_content = re.sub(
                    r'^(status:\s*.+)$',
                    f'\\1\n{notes_line}',
                    updated_content,
                    count=1,
                    flags=re.MULTILINE
                )

            # Write updated content
            file_path.write_text(updated_content, encoding='utf-8')

            logger.info(f"Updated handoff status: {file_path.name} → {new_status}")
            return True

        except Exception as e:
            logger.error(f"Error updating handoff status: {e}")
            return False

    def get_handoff_context_files(self, handoff_data: Dict[str, Any]) -> List[Path]:
        """
        Get list of context files to load for handoff.

        Args:
            handoff_data: Parsed handoff frontmatter

        Returns:
            List of absolute paths to context files
        """
        context_files = []

        # Add PRD
        if "prd_path" in handoff_data:
            prd_path = self.repo_path / handoff_data["prd_path"]
            if prd_path.exists():
                context_files.append(prd_path)

        # Add tech requirements
        if "tech_requirements_path" in handoff_data:
            tech_req_path = self.repo_path / handoff_data["tech_requirements_path"]
            if tech_req_path.exists():
                context_files.append(tech_req_path)

        # Add additional context files
        if "context_files" in handoff_data:
            for context_file in handoff_data["context_files"]:
                context_path = self.repo_path / context_file
                if context_path.exists():
                    context_files.append(context_path)

        return context_files

    def format_handoff_summary(self, handoff_data: Dict[str, Any]) -> str:
        """
        Format handoff as human-readable summary.

        Args:
            handoff_data: Parsed handoff frontmatter

        Returns:
            Formatted string summary
        """
        summary_parts = []

        summary_parts.append(f"**Handoff**: {handoff_data.get('summary', 'Untitled')}")
        summary_parts.append(f"**Type**: {handoff_data.get('type', 'unknown')}")
        summary_parts.append(f"**Priority**: {handoff_data.get('priority', 'P3')}")
        summary_parts.append(f"**From**: {handoff_data.get('from', 'unknown')}")
        summary_parts.append(f"**PRD**: {handoff_data.get('prd_path', 'Not specified')}")

        if "deadline" in handoff_data:
            summary_parts.append(f"**Deadline**: {handoff_data['deadline']}")

        if "estimated_hours" in handoff_data:
            summary_parts.append(f"**Estimated**: {handoff_data['estimated_hours']} hours")

        if "notes" in handoff_data:
            summary_parts.append(f"\n**Notes**: {handoff_data['notes']}")

        return "\n".join(summary_parts)
