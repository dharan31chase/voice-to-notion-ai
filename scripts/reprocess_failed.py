#!/usr/bin/env python3
"""
Quick script to reprocess failed transcripts without re-transcription.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

load_dotenv()

from core.logging_utils import get_logger
from scripts.process_transcripts import process_transcript_file

logger = get_logger(__name__)

def reprocess_failed_files(file_paths: list):
    """
    Reprocess specific failed transcript files.

    Args:
        file_paths: List of failed transcript file paths
    """
    logger.info(f"🔄 Reprocessing {len(file_paths)} failed transcripts")

    success_count = 0
    failed_count = 0

    for file_path in file_paths:
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"❌ File not found: {file_path}")
            failed_count += 1
            continue

        logger.info(f"\n{'='*60}")
        logger.info(f"📄 Processing: {file_path.name}")
        logger.info(f"{'='*60}")

        try:
            # Process transcript file directly (dry_run=False to create in Notion)
            result = process_transcript_file(file_path, dry_run=False)

            if result:
                logger.info(f"✅ Successfully processed {file_path.name}")
                success_count += 1

                # Move out of failed folder (rename to mark as processed)
                new_name = file_path.parent / f"REPROCESSED_{file_path.name}"
                file_path.rename(new_name)
                logger.info(f"📦 Archived: {new_name.name}")
            else:
                logger.error(f"❌ Failed to process {file_path.name}")
                failed_count += 1

        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
            failed_count += 1

    logger.info(f"\n{'='*60}")
    logger.info(f"📊 REPROCESSING SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Success: {success_count}")
    logger.info(f"❌ Failed: {failed_count}")
    logger.info(f"{'='*60}")

if __name__ == "__main__":
    # Files to reprocess
    failed_dir = Path("/Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/Failed/failed_transcripts")

    files_to_process = [
        failed_dir / "251106_0851_BOOKNOTE_TEST.txt"
    ]

    reprocess_failed_files(files_to_process)
