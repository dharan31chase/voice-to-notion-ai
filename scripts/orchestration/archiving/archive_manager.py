"""
Archive Management Module - Phase B Step 7

Responsibilities:
- Create date-based archive structure
- Archive individual recordings with metadata
- Batch archiving of verified entries
- Permission management for archives

Does NOT handle:
- Cleanup operations (CleanupManager)
- Notion verification (NotionVerifier)
- State updates (StateManager)
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class ArchiveManager:
    """Manages archive structure and file archiving."""

    def __init__(self, archives_folder: Path):
        """
        Initialize archive manager.

        Args:
            archives_folder: Root folder for archives
        """
        self.archives_folder = archives_folder
        self.archives_folder.mkdir(exist_ok=True)
        logger.info(f"ArchiveManager initialized with folder: {archives_folder}")

    def create_structure(self, session_id: str) -> Path:
        """
        Create date-based archive folder structure.

        Args:
            session_id: Session ID (format: session_YYYYMMDD_HHMMSS)

        Returns:
            Path: Created archive folder path
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            archive_date_folder = self.archives_folder / today
            archive_session_folder = archive_date_folder / session_id

            # Create folders
            archive_date_folder.mkdir(exist_ok=True)
            archive_session_folder.mkdir(exist_ok=True)

            logger.info(f"📁 Created archive structure: {archive_session_folder}")
            return archive_session_folder

        except Exception as e:
            logger.error(f"❌ Error creating archive structure: {e}")
            raise

    def archive_recording(
        self,
        mp3_file: Path,
        archive_folder: Path,
        session_id: str,
        usb_detector=None
    ) -> Tuple[bool, Path, str]:
        """
        Archive single recording to date-based folder.

        Args:
            mp3_file: Path to MP3 file (USB or staging)
            archive_folder: Target archive folder
            session_id: Current session ID
            usb_detector: Optional USBDetector instance for permission checks

        Returns:
            Tuple[bool, Path, str]:
                - success: True if archived successfully
                - archive_path: Path to archived file
                - error_message: Error message if failed
        """
        try:
            # Check USB file permissions first if detector provided
            if usb_detector and not usb_detector.check_permissions(mp3_file):
                return False, Path(), f"USB file permission check failed: {mp3_file}"

            # Ensure archive folder has proper permissions
            has_perms, perm_msg = self.ensure_permissions(archive_folder)
            if not has_perms:
                return False, Path(), f"Archive folder permission check failed: {perm_msg}"

            # Create archive filename with session ID
            archive_name = f"{mp3_file.stem}_{session_id}.mp3"
            archive_path = archive_folder / archive_name

            # Copy file to archive (safer than move during testing)
            try:
                # Try using shutil.copy2 first
                shutil.copy2(str(mp3_file), str(archive_path))
            except PermissionError as pe:
                logger.warning(f"⚠️ Permission error with copy2, trying alternative methods...")
                try:
                    # Try using shutil.copy
                    shutil.copy(str(mp3_file), str(archive_path))
                except PermissionError as pe2:
                    logger.warning(f"⚠️ Permission error with copy, trying file read/write...")
                    try:
                        # Try manual file read/write
                        with open(mp3_file, 'rb') as src, open(archive_path, 'wb') as dst:
                            dst.write(src.read())
                    except Exception as e3:
                        return False, archive_path, f"All copy methods failed: copy2={pe}, copy={pe2}, manual={e3}"
                except OSError as ose2:
                    return False, archive_path, f"OS error with copy: {ose2}"
            except OSError as ose:
                return False, archive_path, f"OS error with copy2: {ose}"

            # Verify archive was created successfully
            if not archive_path.exists():
                return False, archive_path, "Archive file not created"

            # Verify file integrity (size should match)
            if mp3_file.stat().st_size != archive_path.stat().st_size:
                return False, archive_path, "File size mismatch after archiving"

            # Set proper permissions on archived file (readable by owner and group)
            try:
                archive_path.chmod(0o644)  # rw-r--r--
            except Exception as e:
                logger.warning(f"⚠️ Could not set permissions on {archive_path.name}: {e}")

            logger.info(f"📁 Archived: {mp3_file.name} → {archive_name}")
            return True, archive_path, ""

        except Exception as e:
            error_msg = f"Archive error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, Path(), error_msg

    def archive_batch(
        self,
        cleanup_candidates: List[Dict],
        session_id: str,
        usb_path: Path,
        usb_detector=None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Archive batch of verified recordings.

        Args:
            cleanup_candidates: List of files ready for archiving
            session_id: Current session ID
            usb_path: Path to USB recorder folder
            usb_detector: Optional USBDetector instance for permission checks

        Returns:
            Tuple[List[Dict], List[Dict]]:
                - archived_files: Successfully archived files
                - failed_archives: Files that failed to archive
        """
        logger.info("📁 Archiving successful recordings...")

        archived_files = []
        failed_archives = []

        # Create archive structure
        archive_folder = self.create_structure(session_id)

        for entry in cleanup_candidates:
            try:
                # Find corresponding .mp3 file
                transcript_name = entry.get("transcript_name", "")
                mp3_name = transcript_name.replace(".txt", ".mp3")
                mp3_path = usb_path / mp3_name

                if not mp3_path.exists():
                    failed_archives.append({
                        "transcript": transcript_name,
                        "error": f"MP3 file not found: {mp3_name}",
                        "mp3_path": str(mp3_path)
                    })
                    continue

                # Handle duplicates (skip archiving, just cleanup)
                if entry.get("skip_reason") == "duplicate":
                    logger.info(f"⏭️ Processing duplicate for cleanup: {transcript_name} (archive should exist)")
                    # Skip archiving, just add to cleanup list
                    size_mb = mp3_path.stat().st_size / (1024 * 1024)
                    archived_files.append({
                        "transcript_name": transcript_name,
                        "original_name": mp3_name,
                        "archive_name": f"{mp3_name} (duplicate - already archived)",
                        "archive_path": "already_archived",  # Placeholder
                        "size_mb": round(size_mb, 2),
                        "notion_entry_id": None,
                        "skip_reason": "duplicate"
                    })
                    logger.info(f"⏭️ Added duplicate to cleanup: {mp3_name}")
                    continue

                # Archive the file (normal flow for successful analyses)
                success, archive_path, error = self.archive_recording(
                    mp3_path, archive_folder, session_id, usb_detector
                )

                if success:
                    size_mb = mp3_path.stat().st_size / (1024 * 1024)
                    archived_files.append({
                        "transcript_name": transcript_name,
                        "original_name": mp3_name,
                        "archive_name": archive_path.name,
                        "archive_path": str(archive_path),
                        "size_mb": round(size_mb, 2),
                        "notion_entry_id": entry.get("notion_entry_id")
                    })
                    logger.info(f"📁 Archived: {mp3_name} → {archive_path.name}")
                else:
                    failed_archives.append({
                        "transcript": transcript_name,
                        "error": f"Archive failed: {error}",
                        "mp3_path": str(mp3_path)
                    })

            except Exception as e:
                failed_archives.append({
                    "transcript": entry.get("transcript_name", "unknown"),
                    "error": f"Archive error: {str(e)}",
                    "mp3_path": "unknown"
                })
                logger.error(f"❌ Error archiving {entry.get('transcript_name', 'unknown')}: {e}")

        logger.info(f"📊 Archive Summary: {len(archived_files)} successful, {len(failed_archives)} failed")
        return archived_files, failed_archives

    def ensure_permissions(self, archive_folder: Path) -> Tuple[bool, str]:
        """
        Ensure archive folder has proper permissions.

        Args:
            archive_folder: Archive folder to check

        Returns:
            Tuple[bool, str]: (has_permissions, message)
        """
        try:
            # Create archive folder if it doesn't exist
            archive_folder.mkdir(parents=True, exist_ok=True)

            # Check if folder is writable
            if not os.access(archive_folder, os.W_OK):
                msg = f"Archive folder not writable: {archive_folder}"
                logger.error(f"❌ {msg}")
                logger.info(f"💡 Try: chmod 755 '{archive_folder}'")
                return False, msg

            # Check if we can create a test file
            test_file = archive_folder / ".test_permissions"
            try:
                test_file.write_text("test")
                test_file.unlink()  # Clean up test file
                logger.info(f"✅ Archive folder permissions OK: {archive_folder}")
                return True, "Permissions OK"
            except Exception as e:
                msg = f"Cannot write to archive folder: {e}"
                logger.error(f"❌ {msg}")
                return False, msg

        except Exception as e:
            msg = f"Error checking archive permissions: {e}"
            logger.error(f"❌ {msg}")
            return False, msg
