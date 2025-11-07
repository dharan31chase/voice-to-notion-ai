"""
Cleanup Management Module - Phase B Step 7

Responsibilities:
- Cleanup source files after successful archiving
- Automatic cleanup scheduling (7-day retention)
- Safe cleanup with verification
- Handle cleanup failures

Does NOT handle:
- Archiving (ArchiveManager)
- Verification (NotionVerifier)
- State updates (StateManager)
"""

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class CleanupManager:
    """Manages cleanup of source files and old archives."""

    def __init__(self, recorder_path: Path, archives_folder: Path, transcripts_folder: Path, staging_manager=None):
        """
        Initialize cleanup manager.

        Args:
            recorder_path: USB recorder path
            archives_folder: Archives folder path
            transcripts_folder: Transcripts folder path
            staging_manager: Optional StagingManager for file deletion
        """
        self.recorder_path = recorder_path
        self.archives_folder = archives_folder
        self.transcripts_folder = transcripts_folder
        self.staging_manager = staging_manager
        logger.info("CleanupManager initialized")

    def cleanup_usb_file(self, mp3_file: Path, archive_path: Path) -> Tuple[bool, str]:
        """
        Clean up USB file after successful archiving.

        CRITICAL: Only deletes if archive verified to exist!

        Args:
            mp3_file: USB file to cleanup
            archive_path: Archive path to verify

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Double-check: archive must exist and have correct size
            if not archive_path.exists():
                msg = f"Cannot delete {mp3_file.name}: Archive file missing"
                logger.error(f"❌ {msg}")
                return False, msg

            # Verify archive integrity
            if mp3_file.stat().st_size != archive_path.stat().st_size:
                msg = f"Cannot delete {mp3_file.name}: Archive size mismatch"
                logger.error(f"❌ {msg}")
                return False, msg

            # Use StagingManager for safe deletion if available
            if self.staging_manager:
                success = self.staging_manager.safe_delete_usb(mp3_file)
                if success:
                    return True, "Deleted successfully"
                else:
                    return False, "Safe deletion failed"
            else:
                # Fallback: direct deletion
                mp3_file.unlink()
                return True, "Deleted successfully"

        except Exception as e:
            msg = f"Error cleaning up {mp3_file.name}: {e}"
            logger.error(f"❌ {msg}")
            return False, msg

    def cleanup_source_files(
        self,
        archived_files: List[Dict]
    ) -> Tuple[int, int, List[Dict]]:
        """
        Clean up source files (USB + transcripts) after archiving.

        Args:
            archived_files: List of successfully archived files

        Returns:
            Tuple[int, int, List[Dict]]:
                - mp3_cleaned: Number of MP3 files cleaned
                - transcript_cleaned: Number of transcripts cleaned
                - cleanup_failures: List of files that failed cleanup
        """
        logger.info("🗑️ Cleaning up successful source files...")

        mp3_cleanup_count = 0
        transcript_cleanup_count = 0
        cleanup_failures = []

        for file_info in archived_files:
            try:
                # Clean up .mp3 file from recorder
                mp3_path = self.recorder_path / file_info["original_name"]
                if mp3_path.exists():
                    # Handle duplicates (no archive path to verify)
                    if file_info.get("skip_reason") == "duplicate":
                        # For duplicates, use safe deletion
                        if self.staging_manager:
                            if self.staging_manager.safe_delete_usb(mp3_path):
                                mp3_cleanup_count += 1
                        else:
                            mp3_path.unlink()
                            mp3_cleanup_count += 1
                    else:
                        # For successful analyses, verify archive before cleanup
                        success, msg = self.cleanup_usb_file(mp3_path, Path(file_info["archive_path"]))
                        if success:
                            mp3_cleanup_count += 1
                            logger.info(f"🗑️ Cleaned up recorder: {file_info['original_name']}")
                        else:
                            cleanup_failures.append({
                                "file": file_info["original_name"],
                                "type": "mp3",
                                "error": f"Recorder cleanup failed: {msg}"
                            })
                else:
                    cleanup_failures.append({
                        "file": file_info["original_name"],
                        "type": "mp3",
                        "error": "MP3 file no longer exists"
                    })

                # Clean up .txt transcript file
                transcript_path = self.transcripts_folder / file_info["transcript_name"]
                if transcript_path.exists():
                    try:
                        transcript_path.unlink()
                        transcript_cleanup_count += 1
                        logger.info(f"🗑️ Cleaned up transcript: {file_info['transcript_name']}")
                    except Exception as e:
                        cleanup_failures.append({
                            "file": file_info["transcript_name"],
                            "type": "transcript",
                            "error": f"Transcript cleanup failed: {str(e)}"
                        })
                else:
                    cleanup_failures.append({
                        "file": file_info["transcript_name"],
                        "type": "transcript",
                        "error": "Transcript file not found"
                    })

            except Exception as e:
                cleanup_failures.append({
                    "file": file_info.get("transcript_name", "unknown"),
                    "type": "unknown",
                    "error": f"Cleanup error: {str(e)}"
                })
                logger.error(f"❌ Error during cleanup: {e}")

        logger.info(f"📊 Cleanup Summary: {mp3_cleanup_count} MP3s, {transcript_cleanup_count} transcripts")

        # Clean up staging folder if staging_manager available
        if self.staging_manager:
            staging_cleaned = self.staging_manager.cleanup_staging()
            if staging_cleaned > 0:
                logger.info(f"🧹 Staging cleanup: {staging_cleaned} files removed")

        return mp3_cleanup_count, transcript_cleanup_count, cleanup_failures

    def cleanup_old_archives(self, retention_days: int = 7) -> int:
        """
        Clean up archives older than retention period.

        Args:
            retention_days: Number of days to retain archives

        Returns:
            int: Number of archive folders deleted
        """
        try:
            if retention_days <= 0:
                logger.info("⏭️ Archive retention disabled (retention_days = 0)")
                return 0

            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0

            # Clean up old date folders (YYYY-MM-DD format)
            for date_folder in self.archives_folder.iterdir():
                if not date_folder.is_dir():
                    continue

                # Check if folder is older than retention period
                try:
                    folder_mtime = datetime.fromtimestamp(date_folder.stat().st_mtime)
                    if folder_mtime < cutoff_date:
                        # Delete entire date folder
                        shutil.rmtree(date_folder)
                        deleted_count += 1
                        logger.info(f"🗑️ Deleted old archive folder: {date_folder.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not delete {date_folder.name}: {e}")

            logger.info(f"🧹 Cleanup complete: {deleted_count} old archive folders removed")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return 0

    def run_automatic_cleanup(self, retention_days: int = 7) -> None:
        """
        Run automatic cleanup of old archives.

        Args:
            retention_days: Number of days to retain archives (from config)
        """
        logger.info(f"🧹 Running automatic cleanup (retention: {retention_days} days)...")
        deleted = self.cleanup_old_archives(retention_days)
        if deleted > 0:
            logger.info(f"✅ Cleaned up {deleted} old archive folders")
        else:
            logger.info("✅ No old archives to clean up")
