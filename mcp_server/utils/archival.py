"""
Archival Utility

Provides active/archive folder structure with YYYY/QQ organization.

Features:
- Active/archive split based on initiative status
- YYYY/QQ folder structure (e.g., 2025/Q4)
- Prompt before archiving (warn + force parameter)
- Auto-creates archive directories
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging


def get_archive_path(base_dir: Path, year: Optional[int] = None, quarter: Optional[int] = None) -> Path:
    """
    Get archive path for given year and quarter.

    Args:
        base_dir: Base directory (e.g., "docs/prd")
        year: Year (default: current year)
        quarter: Quarter 1-4 (default: current quarter)

    Returns:
        Path to archive directory (e.g., "docs/prd/archive/2025/Q4")

    Example:
        >>> path = get_archive_path(Path("docs/prd"))
        >>> # Returns: docs/prd/archive/2025/Q4
    """
    if year is None:
        year = datetime.now().year

    if quarter is None:
        # Calculate current quarter (1-4)
        month = datetime.now().month
        quarter = (month - 1) // 3 + 1

    # Validate quarter
    if quarter not in [1, 2, 3, 4]:
        raise ValueError(f"Invalid quarter {quarter}. Must be 1-4.")

    return base_dir / "archive" / str(year) / f"Q{quarter}"


def archive_file(
    file_path: Path,
    archive_base: Optional[Path] = None,
    force: bool = False,
    year: Optional[int] = None,
    quarter: Optional[int] = None
) -> dict:
    """
    Archive a file to archive/YYYY/QQ structure.

    Args:
        file_path: Path to file to archive
        archive_base: Base archive directory (default: file_path.parent / "archive")
        force: Skip confirmation prompt (default: False)
        year: Year for archive (default: current year)
        quarter: Quarter for archive (default: current quarter)

    Returns:
        Dict with status, archived_path, and message

    Example:
        >>> result = archive_file(
        ...     Path("docs/prd/active/feature.md"),
        ...     force=True
        ... )
        >>> # Moves to: docs/prd/archive/2025/Q4/feature.md
    """
    if not file_path.exists():
        return {
            "status": "error",
            "message": f"File not found: {file_path}"
        }

    # Determine archive base directory
    if archive_base is None:
        archive_base = file_path.parent.parent / "archive"

    # Get archive path
    try:
        archive_dir = get_archive_path(archive_base.parent, year, quarter)
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }

    # Create archive directory
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Destination path
    archived_path = archive_dir / file_path.name

    # Check if file already exists in archive
    if archived_path.exists() and not force:
        return {
            "status": "warning",
            "message": f"File already exists in archive: {archived_path}. Use force=True to overwrite.",
            "action_required": "Confirm overwrite or cancel"
        }

    # Warn before archiving (unless force=True)
    if not force:
        return {
            "status": "confirmation_required",
            "message": f"About to archive {file_path} to {archived_path}",
            "action_required": "Call archive_file() again with force=True to confirm",
            "preview": {
                "source": str(file_path),
                "destination": str(archived_path)
            }
        }

    # Move file to archive
    try:
        shutil.move(str(file_path), str(archived_path))
        logging.info(f"Archived {file_path} to {archived_path}")

        return {
            "status": "success",
            "archived_path": str(archived_path),
            "message": f"File archived successfully to {archived_path}"
        }

    except Exception as e:
        logging.error(f"Error archiving {file_path}: {e}")
        return {
            "status": "error",
            "message": f"Error archiving file: {str(e)}"
        }


def unarchive_file(archived_path: Path, active_dir: Path, force: bool = False) -> dict:
    """
    Restore a file from archive to active directory.

    Args:
        archived_path: Path to archived file
        active_dir: Active directory to restore to
        force: Skip confirmation prompt (default: False)

    Returns:
        Dict with status, restored_path, and message

    Example:
        >>> result = unarchive_file(
        ...     Path("docs/prd/archive/2025/Q4/feature.md"),
        ...     Path("docs/prd/active"),
        ...     force=True
        ... )
        >>> # Moves to: docs/prd/active/feature.md
    """
    if not archived_path.exists():
        return {
            "status": "error",
            "message": f"Archived file not found: {archived_path}"
        }

    # Destination path
    restored_path = active_dir / archived_path.name

    # Check if file already exists in active dir
    if restored_path.exists() and not force:
        return {
            "status": "warning",
            "message": f"File already exists in active directory: {restored_path}. Use force=True to overwrite.",
            "action_required": "Confirm overwrite or cancel"
        }

    # Warn before unarchiving (unless force=True)
    if not force:
        return {
            "status": "confirmation_required",
            "message": f"About to restore {archived_path} to {restored_path}",
            "action_required": "Call unarchive_file() again with force=True to confirm",
            "preview": {
                "source": str(archived_path),
                "destination": str(restored_path)
            }
        }

    # Create active directory if needed
    active_dir.mkdir(parents=True, exist_ok=True)

    # Move file from archive
    try:
        shutil.move(str(archived_path), str(restored_path))
        logging.info(f"Restored {archived_path} to {restored_path}")

        return {
            "status": "success",
            "restored_path": str(restored_path),
            "message": f"File restored successfully to {restored_path}"
        }

    except Exception as e:
        logging.error(f"Error restoring {archived_path}: {e}")
        return {
            "status": "error",
            "message": f"Error restoring file: {str(e)}"
        }


def list_archived_files(archive_base: Path, year: Optional[int] = None, quarter: Optional[int] = None) -> list[dict]:
    """
    List files in archive directory.

    Args:
        archive_base: Base archive directory
        year: Filter by year (default: None = all years)
        quarter: Filter by quarter (default: None = all quarters)

    Returns:
        List of file info dicts with path, year, quarter, size

    Example:
        >>> files = list_archived_files(Path("docs/prd/archive"))
        >>> for file in files:
        >>>     print(f"{file['year']}/Q{file['quarter']}: {file['name']}")
    """
    if not archive_base.exists():
        return []

    archived_files = []

    # Scan archive directory
    if year and quarter:
        # Specific year/quarter
        archive_dir = get_archive_path(archive_base.parent, year, quarter)
        if archive_dir.exists():
            for file_path in archive_dir.glob("*.md"):
                archived_files.append({
                    "path": str(file_path),
                    "name": file_path.name,
                    "year": year,
                    "quarter": quarter,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
    else:
        # All years/quarters
        for year_dir in archive_base.glob("*"):
            if not year_dir.is_dir() or not year_dir.name.isdigit():
                continue

            year_num = int(year_dir.name)

            for quarter_dir in year_dir.glob("Q*"):
                if not quarter_dir.is_dir():
                    continue

                quarter_num = int(quarter_dir.name[1:])

                for file_path in quarter_dir.glob("*.md"):
                    archived_files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "year": year_num,
                        "quarter": quarter_num,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })

    return sorted(archived_files, key=lambda x: (x["year"], x["quarter"], x["name"]))
