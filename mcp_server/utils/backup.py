"""
Backup Utility

Provides backup before overwrite functionality with automatic cleanup.

Features:
- Creates backups in .backups/ subfolder
- Keeps last 3 backups per file
- Auto-deletes older backups
- Timestamp format: YYYY-MM-DD-HH-MM-SS
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging


def create_backup(file_path: Path) -> Optional[Path]:
    """
    Create backup of file before overwriting.

    Args:
        file_path: Path to file to backup

    Returns:
        Path to backup file, or None if file doesn't exist

    Example:
        >>> backup_path = create_backup(Path("docs/prd/feature.md"))
        >>> # Creates: docs/prd/.backups/feature.md.2025-12-05-15-30-00
    """
    if not file_path.exists():
        return None

    # Create .backups/ subfolder
    backup_dir = file_path.parent / ".backups"
    backup_dir.mkdir(exist_ok=True)

    # Generate timestamped backup filename
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    backup_filename = f"{file_path.name}.{timestamp}"
    backup_path = backup_dir / backup_filename

    # Copy file to backup
    try:
        shutil.copy2(file_path, backup_path)
        logging.info(f"Created backup: {backup_path}")

        # Clean up old backups (keep last 3)
        cleanup_old_backups(file_path, keep_count=3)

        return backup_path

    except Exception as e:
        logging.error(f"Error creating backup for {file_path}: {e}")
        return None


def cleanup_old_backups(file_path: Path, keep_count: int = 3):
    """
    Delete old backups, keeping only the most recent N backups.

    Args:
        file_path: Original file path
        keep_count: Number of backups to keep (default: 3)

    Example:
        >>> cleanup_old_backups(Path("docs/prd/feature.md"), keep_count=3)
        >>> # Keeps: feature.md.2025-12-05-15-30-00, feature.md.2025-12-04-10-20-30, etc.
    """
    backup_dir = file_path.parent / ".backups"
    if not backup_dir.exists():
        return

    # Find all backups for this file
    prefix = file_path.name + "."
    backups = sorted(
        [f for f in backup_dir.glob(f"{prefix}*") if f.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True  # Most recent first
    )

    # Delete old backups
    for old_backup in backups[keep_count:]:
        try:
            old_backup.unlink()
            logging.info(f"Deleted old backup: {old_backup}")
        except Exception as e:
            logging.error(f"Error deleting old backup {old_backup}: {e}")


def restore_from_backup(file_path: Path, backup_index: int = 0) -> bool:
    """
    Restore file from backup.

    Args:
        file_path: Original file path
        backup_index: Which backup to restore (0 = most recent, 1 = second most recent, etc.)

    Returns:
        True if restored successfully, False otherwise

    Example:
        >>> restore_from_backup(Path("docs/prd/feature.md"), backup_index=0)
        >>> # Restores from most recent backup
    """
    backup_dir = file_path.parent / ".backups"
    if not backup_dir.exists():
        logging.error(f"No backups found for {file_path}")
        return False

    # Find all backups for this file
    prefix = file_path.name + "."
    backups = sorted(
        [f for f in backup_dir.glob(f"{prefix}*") if f.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True  # Most recent first
    )

    if backup_index >= len(backups):
        logging.error(f"Backup index {backup_index} out of range (only {len(backups)} backups)")
        return False

    backup_path = backups[backup_index]

    try:
        shutil.copy2(backup_path, file_path)
        logging.info(f"Restored {file_path} from backup {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Error restoring from backup: {e}")
        return False


def list_backups(file_path: Path) -> list[dict]:
    """
    List all backups for a file.

    Args:
        file_path: Original file path

    Returns:
        List of backup info dicts with path, timestamp, size

    Example:
        >>> backups = list_backups(Path("docs/prd/feature.md"))
        >>> for backup in backups:
        >>>     print(f"{backup['timestamp']}: {backup['size']} bytes")
    """
    backup_dir = file_path.parent / ".backups"
    if not backup_dir.exists():
        return []

    # Find all backups for this file
    prefix = file_path.name + "."
    backups = sorted(
        [f for f in backup_dir.glob(f"{prefix}*") if f.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True  # Most recent first
    )

    return [
        {
            "path": str(backup),
            "timestamp": datetime.fromtimestamp(backup.stat().st_mtime).isoformat(),
            "size": backup.stat().st_size
        }
        for backup in backups
    ]
