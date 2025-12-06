"""
Roadmap Helper Functions

Provides utilities for ROADMAP.md management:
- Update initiative status in ROADMAP.md
- Mark initiatives as complete with dates
- Sync with Strategy Board
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


def update_roadmap_row(
    content: str,
    initiative_name: str,
    new_status: Optional[str] = None,
    completion_date: Optional[str] = None,
    target_date: Optional[str] = None
) -> str:
    """
    Update a single initiative row in ROADMAP.md.

    Matches initiative by name and updates status, completion date, or target.

    Args:
        content: Full ROADMAP.md content
        initiative_name: Name of initiative to update
        new_status: New status emoji (e.g., "✅ Complete", "🚀 In Progress")
        completion_date: Completion date in ISO format (YYYY-MM-DD)
        target_date: Target date in format (e.g., "Dec 13", "Nov 24")

    Returns:
        Updated ROADMAP.md content

    Example:
        >>> content = read_file("ROADMAP.md")
        >>> updated = update_roadmap_row(
        ...     content,
        ...     "Applied Context Engineering",
        ...     new_status="✅ Complete",
        ...     completion_date="2025-12-05"
        ... )
        >>> write_file("ROADMAP.md", updated)
    """
    lines = content.split("\n")
    updated_lines = []

    for line in lines:
        # Check if this line contains the initiative name
        if initiative_name in line and line.strip().startswith("|"):
            # Parse table row
            columns = [col.strip() for col in line.split("|")]

            # Update status column (usually index 4 or 5)
            if new_status:
                # Find status column by looking for emoji
                for i, col in enumerate(columns):
                    if any(emoji in col for emoji in ["✅", "🚀", "🟢", "📋", "🔴", "🟡"]):
                        columns[i] = new_status
                        break

            # Update target column if completion_date provided
            if completion_date:
                # Convert ISO date to "Mon DD" format
                date_obj = datetime.fromisoformat(completion_date)
                formatted_date = date_obj.strftime("%b %d")

                # Find target column (usually index 6)
                for i, col in enumerate(columns):
                    if "Dec" in col or "Nov" in col or "Jan" in col or target_date:
                        columns[i] = formatted_date
                        break

            # Rebuild line
            line = "|".join(columns)

        updated_lines.append(line)

    return "\n".join(updated_lines)


def mark_initiative_complete_in_roadmap(
    roadmap_content: str,
    initiative_name: str,
    completion_date: Optional[str] = None
) -> str:
    """
    Mark initiative as complete in ROADMAP.md.

    Updates status to ✅ Complete and adds completion date.

    Args:
        roadmap_content: Full ROADMAP.md content
        initiative_name: Name of initiative
        completion_date: Completion date in ISO format (default: today)

    Returns:
        Updated ROADMAP.md content

    Example:
        >>> content = read_file("ROADMAP.md")
        >>> updated = mark_initiative_complete_in_roadmap(
        ...     content,
        ...     "RAG Implementation",
        ...     "2025-11-24"
        ... )
    """
    if completion_date is None:
        completion_date = datetime.now().date().isoformat()

    return update_roadmap_row(
        content=roadmap_content,
        initiative_name=initiative_name,
        new_status="✅ Complete",
        completion_date=completion_date
    )


def find_initiative_in_roadmap(
    roadmap_content: str,
    initiative_name: str
) -> Optional[Dict]:
    """
    Find initiative row in ROADMAP.md.

    Args:
        roadmap_content: Full ROADMAP.md content
        initiative_name: Name of initiative to find

    Returns:
        Dict with initiative data, or None if not found

    Example:
        >>> content = read_file("ROADMAP.md")
        >>> initiative = find_initiative_in_roadmap(
        ...     content,
        ...     "Context Engineering"
        ... )
        >>> if initiative:
        ...     print(initiative["status"])
    """
    lines = roadmap_content.split("\n")

    for line in lines:
        if initiative_name in line and line.strip().startswith("|"):
            # Parse table row
            columns = [col.strip() for col in line.split("|")]

            # Extract data
            return {
                "found": True,
                "raw_line": line,
                "columns": columns
            }

    return None


def sync_roadmap_with_strategy_board(
    roadmap_content: str,
    initiative_name: str,
    strategy_board_status: str,
    completed_date: Optional[str] = None,
    prd_path: Optional[str] = None
) -> Dict:
    """
    Sync ROADMAP.md with Strategy Board status.

    Updates ROADMAP.md to match Strategy Board, archives PRD if complete.

    Args:
        roadmap_content: Full ROADMAP.md content
        initiative_name: Name of initiative
        strategy_board_status: Status from Strategy Board (e.g., "✅ Complete")
        completed_date: Completion date from Strategy Board (ISO format)
        prd_path: Path to PRD file (for archiving)

    Returns:
        Dict with updated_content, prd_archived, and status

    Example:
        >>> result = sync_roadmap_with_strategy_board(
        ...     roadmap_content,
        ...     "Context Engineering",
        ...     "✅ Complete",
        ...     "2025-12-05",
        ...     "docs/prd/context-engineering.md"
        ... )
        >>> write_file("ROADMAP.md", result["updated_content"])
        >>> if result["prd_archived"]:
        ...     print(f"PRD archived to: {result['archive_path']}")
    """
    from .archival import archive_file

    # Update ROADMAP.md
    updated_content = update_roadmap_row(
        content=roadmap_content,
        initiative_name=initiative_name,
        new_status=strategy_board_status,
        completion_date=completed_date if strategy_board_status == "✅ Complete" else None
    )

    result = {
        "status": "success",
        "updated_content": updated_content,
        "prd_archived": False
    }

    # Archive PRD if complete
    if strategy_board_status == "✅ Complete" and prd_path:
        prd_file_path = Path(prd_path)
        if prd_file_path.exists():
            archive_result = archive_file(prd_file_path, force=True)
            if archive_result["status"] == "success":
                result["prd_archived"] = True
                result["archive_path"] = archive_result["archived_path"]

    return result
