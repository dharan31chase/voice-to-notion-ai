"""
Staging Management Module

Responsibilities:
- Copy files from USB to local staging folder
- Safely delete files from USB (with macOS permission handling)
- Clean up staging folder after successful processing

Does NOT handle:
- File validation (FileValidator)
- USB detection (USBDetector)
- State management (StateManager)
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


class StagingManager:
    """Manages local staging of USB files for processing."""

    def __init__(self, staging_folder: Path):
        """
        Initialize staging manager.

        Args:
            staging_folder: Path to local staging directory
        """
        self.staging_folder = staging_folder
        self.staging_folder.mkdir(exist_ok=True)
        logger.info(f"StagingManager initialized: {staging_folder}")

    def copy_to_staging(self, files: List[Path]) -> Tuple[List[Path], List[Tuple[Path, str]]]:
        """
        Copy files from USB to local staging folder.

        Args:
            files: List of USB file paths to copy

        Returns:
            Tuple[List[Path], List[Tuple[Path, str]]]:
                - successful: List of staging paths
                - failed: List of (usb_path, error_message) tuples
        """
        successful = []
        failed = []

        logger.info(f"📦 Copying {len(files)} files from USB to staging...")

        for file_path in files:
            try:
                # Copy to staging
                staging_path = self.staging_folder / file_path.name

                if staging_path.exists():
                    # Check if file is the same size (already staged correctly)
                    if staging_path.stat().st_size == file_path.stat().st_size:
                        logger.info(f"ℹ️ {file_path.name} already in staging")
                        successful.append(staging_path)
                        continue
                    else:
                        # Size mismatch - remove old file and re-copy
                        logger.info(f"⚠️ {file_path.name} exists but size differs - re-copying")
                        try:
                            # Strip extended attributes first (macOS-specific)
                            subprocess.run(['xattr', '-c', str(staging_path)],
                                         capture_output=True, check=False, timeout=5)
                        except Exception:
                            pass  # xattr might not exist or fail
                        staging_path.unlink()

                # Copy file to staging (use copy instead of copy2 to avoid metadata issues)
                # copy2 preserves extended attributes which can cause permission errors
                shutil.copy(str(file_path), str(staging_path))

                # Strip extended attributes from the copy (prevents permission issues)
                try:
                    subprocess.run(['xattr', '-c', str(staging_path)],
                                 capture_output=True, check=False, timeout=5)
                except Exception:
                    pass  # Not critical if xattr cleanup fails

                logger.info(f"✅ Copied {file_path.name} to staging ({file_path.stat().st_size / (1024*1024):.1f}MB)")
                successful.append(staging_path)

            except Exception as e:
                error_msg = f"Copy failed: {e}"
                logger.error(f"❌ {file_path.name}: {error_msg}")
                failed.append((file_path, error_msg))

        logger.info(f"📦 Staging complete: {len(successful)} copied, {len(failed)} failed")
        return successful, failed

    def safe_delete_usb(self, usb_file: Path) -> bool:
        """
        Safely delete file from USB with macOS permission handling.

        Strips extended attributes and tries multiple deletion methods
        to handle macOS-specific permission issues.

        Args:
            usb_file: Path to USB file to delete

        Returns:
            bool: True if deletion succeeded, False otherwise
        """
        try:
            # Step 1: Strip extended attributes (macOS metadata that blocks deletion)
            try:
                subprocess.run(['xattr', '-c', str(usb_file)],
                             capture_output=True, check=False, timeout=5)
                logger.debug(f"   Stripped extended attributes from {usb_file.name}")
            except Exception as e:
                logger.debug(f"   Could not strip xattr (may not exist): {e}")

            # Step 2: Ensure write permissions
            try:
                usb_file.chmod(0o644)  # rw-r--r--
                logger.debug(f"   Set permissions for {usb_file.name}")
            except Exception as e:
                logger.debug(f"   Could not set permissions: {e}")

            # Step 3: Try multiple deletion methods

            # Method 1: Path.unlink()
            try:
                usb_file.unlink()
                logger.info(f"✅ Deleted from USB: {usb_file.name}")
                return True
            except PermissionError:
                logger.debug(f"   Path.unlink() failed with PermissionError")
            except Exception as e:
                logger.debug(f"   Path.unlink() failed: {e}")

            # Method 2: os.remove()
            try:
                os.remove(str(usb_file))
                logger.info(f"✅ Deleted from USB: {usb_file.name}")
                return True
            except PermissionError:
                logger.debug(f"   os.remove() failed with PermissionError")
            except Exception as e:
                logger.debug(f"   os.remove() failed: {e}")

            # Method 3: subprocess rm -f
            try:
                result = subprocess.run(['rm', '-f', str(usb_file)],
                                       capture_output=True, text=True, timeout=10)
                if result.returncode == 0 and not usb_file.exists():
                    logger.info(f"✅ Deleted from USB: {usb_file.name}")
                    return True
                else:
                    logger.debug(f"   subprocess rm failed: {result.stderr}")
            except Exception as e:
                logger.debug(f"   subprocess rm failed: {e}")

            # All methods failed
            logger.warning(f"⚠️ Could not delete {usb_file.name} from USB (Operation not permitted)")
            logger.warning(f"   File remains on USB - safe to manually delete after verification")
            return False

        except Exception as e:
            logger.error(f"❌ Error during USB deletion for {usb_file.name}: {e}")
            return False

    def cleanup_staging(self) -> int:
        """
        Clean up staging folder after successful processing.

        Returns:
            int: Count of files successfully cleaned
        """
        try:
            if not self.staging_folder.exists():
                return 0

            cleaned_count = 0
            staging_files = list(self.staging_folder.glob("*.mp3"))

            if not staging_files:
                logger.debug("   No staging files to clean")
                return 0

            logger.info(f"🧹 Cleaning staging folder ({len(staging_files)} files)...")

            for staging_file in staging_files:
                try:
                    staging_file.unlink()
                    cleaned_count += 1
                    logger.debug(f"   Cleaned staging: {staging_file.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean staging file {staging_file.name}: {e}")

            if cleaned_count > 0:
                logger.info(f"✅ Staging cleanup complete: {cleaned_count} files removed")

            return cleaned_count

        except Exception as e:
            logger.error(f"❌ Error during staging cleanup: {e}")
            return 0
