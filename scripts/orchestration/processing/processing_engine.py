"""
Processing Engine Module

Responsibilities:
- AI processing of transcripts via process_transcripts module
- Transcript validation (file size, content, duplicate detection)
- Classify transcripts (valid/duplicate/invalid/error)
- Notion entry verification with retry and rate limiting
- Handle duplicate transcripts for archiving
- Failed transcript management

Does NOT handle:
- Transcription (TranscriptionEngine)
- File staging (StagingManager)
- Archiving (ArchiveManager)
"""

import sys
import json
import time
import signal
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessingEngine:
    """Handles AI processing and Notion verification of transcripts."""

    def __init__(self, config, project_root: Path):
        """
        Initialize processing engine.

        Args:
            config: ConfigLoader instance for processing settings
            project_root: Project root directory path
        """
        self.config = config
        self.project_root = project_root
        logger.info("ProcessingEngine initialized")

    def import_processor(self) -> Optional[Callable]:
        """
        Import the process_transcripts module dynamically.

        Adds scripts directory to sys.path and imports process_transcript_file function.

        Returns:
            Callable: process_transcript_file function, or None if import fails
        """
        try:
            # Add the scripts directory to Python path
            scripts_dir = self.project_root / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))

            # Import the process_transcript_file function
            from process_transcripts import process_transcript_file
            logger.info("Successfully imported AI processing system")
            return process_transcript_file

        except ImportError as e:
            logger.error(f"ERROR: Failed to import process_transcripts: {e}")
            return None
        except Exception as e:
            logger.error(f"ERROR: Error importing process_transcripts: {e}")
            return None

    def validate_transcript(self, transcript_path: Path) -> str:
        """
        Validate transcript and determine processing status.

        Args:
            transcript_path: Path to transcript file

        Returns:
            str: Processing status:
                - "valid": Ready for AI processing
                - "duplicate": Already processed, skip AI but cleanup MP3
                - "invalid": File problems, move to failed folder
                - "error": Unexpected error during validation
        """
        try:
            if not transcript_path.exists():
                logger.warning(f"WARNING: Transcript file not found: {transcript_path}")
                return "invalid"

            # Check file size
            file_size = transcript_path.stat().st_size
            min_size = self.config.get("processing.validate_transcript_min_size", 10) if self.config else 10

            if file_size < min_size:
                logger.warning(f"WARNING: Transcript too small: {transcript_path} ({file_size} bytes)")
                return "invalid"

            # Check if already processed
            processed_file = self.project_root / "processed" / f"{transcript_path.stem}_processed.json"
            if processed_file.exists():
                logger.info(f"INFO: Transcript already processed: {transcript_path.stem}")
                return "duplicate"

            # Read and validate content
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            min_content = self.config.get("processing.validate_transcript_min_content", 10) if self.config else 10

            if len(content) < min_content:
                logger.warning(f"WARNING: Transcript content too short: {transcript_path}")
                return "invalid"

            logger.info(f"SUCCESS: Transcript validated: {transcript_path.name} ({file_size} bytes, {len(content)} chars)")
            return "valid"

        except Exception as e:
            logger.error(f"ERROR: Error validating transcript {transcript_path}: {e}")
            return "error"

    def process_single_transcript(self, transcript_path: Path,
                                  process_function: Callable) -> Tuple[bool, Dict, str]:
        """
        Process a single transcript using the AI system.

        Args:
            transcript_path: Path to transcript file
            process_function: The process_transcript_file function from process_transcripts module

        Returns:
            Tuple[bool, Dict, str]:
                - success: True if processing succeeded
                - processed_data: Dict with analysis results
                - error_message: Error message if failed
        """
        try:
            logger.info(f"Processing transcript: {transcript_path.name}")

            # Call the existing process function
            result = process_function(transcript_path)

            if result is None:
                return False, {}, "AI analysis returned None"

            # Check if processed file was created
            processed_file = self.project_root / "processed" / f"{transcript_path.stem}_processed.json"
            if not processed_file.exists():
                return False, {}, "No processed file created"

            # Read the processed result
            with open(processed_file, 'r', encoding='utf-8') as f:
                processed_data = json.load(f)

            logger.info(f"SUCCESS: Successfully processed: {transcript_path.name}")
            return True, processed_data, ""

        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            logger.error(f"ERROR: {error_msg}")
            return False, {}, error_msg

    def verify_notion_entry(self, notion_entry_id: str, notion_client) -> Tuple[bool, str]:
        """
        Verify that a Notion entry exists via API call.

        Implements retry logic with exponential backoff (3 attempts).
        Uses signal.alarm() for timeout (Unix/Mac only).

        Note: signal.alarm() only works on Unix/Mac systems, not Windows.
        Future enhancement: Use threading.Timer or ThreadPoolExecutor.result(timeout)
        for platform-independent timeout mechanism.

        Args:
            notion_entry_id: Notion page ID to verify
            notion_client: Notion client instance

        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        if not notion_client:
            return False, "Notion client not available"

        max_retries = self.config.get("processing.max_notion_retries", 3) if self.config else 3
        base_delay = self.config.get("processing.notion_retry_base_delay", 1) if self.config else 1
        timeout_seconds = self.config.get("processing.notion_api_timeout", 10) if self.config else 10

        for attempt in range(max_retries):
            try:
                # Add delay between retries (rate limiting)
                if attempt > 0:
                    time.sleep(base_delay * (2 ** (attempt - 1)))

                # Define timeout handler (Unix/Mac only)
                def timeout_handler(signum, frame):
                    raise TimeoutError("API call timed out")

                # Set timeout using signal.alarm (Unix/Mac only)
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)

                try:
                    page = notion_client.pages.retrieve(notion_entry_id)
                    signal.alarm(0)  # Cancel timeout

                    if page and page.get("id"):
                        return True, ""
                    else:
                        return False, "Page not found or invalid response"

                except TimeoutError:
                    signal.alarm(0)
                    return False, f"API call timed out after {timeout_seconds} seconds"

            except Exception as e:
                error_msg = str(e)
                if "rate_limited" in error_msg.lower() or "429" in error_msg:
                    # Rate limited - wait longer
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"WARNING: Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                elif "not_found" in error_msg.lower() or "404" in error_msg:
                    return False, "Page not found"
                elif attempt == max_retries - 1:
                    return False, f"API error after {max_retries} attempts: {error_msg}"
                else:
                    logger.warning(f"WARNING: API error on attempt {attempt + 1}: {error_msg}")
                    continue

        return False, f"Failed after {max_retries} attempts"

    def process_and_verify(self, transcripts: List[Path], project_root: Path,
                          failed_folder: Path, state: Dict,
                          move_failed_callback: Optional[Callable] = None,
                          notion_client=None) -> Tuple[bool, List[Dict], List[Path]]:
        """
        Process transcripts through AI system and verify Notion entries.

        Main orchestration method that:
        1. Imports process_transcripts module
        2. Validates transcripts (valid/duplicate/invalid/error)
        3. Processes valid transcripts through AI system
        4. Extracts Notion entry IDs from results
        5. Handles duplicates for archiving
        6. Updates state with results

        Args:
            transcripts: List of transcript file paths
            project_root: Project root directory
            failed_folder: Folder for failed transcripts
            state: Session state dict to update
            move_failed_callback: Optional callback to move failed transcripts
            notion_client: Optional Notion client for verification

        Returns:
            Tuple[bool, List[Dict], List[Path]]:
                - success: True if at least one transcript succeeded
                - successful_analyses: List of analysis result dicts
                - failed_transcripts: List of transcript paths that failed
        """
        try:
            if not transcripts:
                logger.warning("WARNING: No transcripts to process")
                return True, [], []

            # Import the processing function
            process_function = self.import_processor()
            if not process_function:
                logger.error("ERROR: Failed to import process_transcripts module")
                return False, [], []

            logger.info(f"Processing {len(transcripts)} transcripts")

            # Validate transcripts before processing
            valid_transcripts = []
            duplicate_transcripts = []
            invalid_transcripts = []

            for transcript in transcripts:
                status = self.validate_transcript(transcript)

                if status == "valid":
                    valid_transcripts.append(transcript)
                elif status == "duplicate":
                    duplicate_transcripts.append(transcript)
                else:  # status == "invalid" or "error"
                    invalid_transcripts.append(transcript)

            # Handle invalid transcripts
            if invalid_transcripts:
                logger.warning(f"WARNING: {len(invalid_transcripts)} transcripts failed validation")
                for transcript in invalid_transcripts:
                    if move_failed_callback:
                        move_failed_callback(transcript, "Failed validation")

            # Handle duplicates
            if duplicate_transcripts:
                logger.info(f"INFO: {len(duplicate_transcripts)} transcripts are duplicates (already processed)")
                # Store duplicates in state for Step 5 cleanup
                for transcript in duplicate_transcripts:
                    state["duplicate_skipped"] = state.get("duplicate_skipped", [])
                    state["duplicate_skipped"].append(transcript.name)

                    # Add to cleanup candidates for archiving and MP3 cleanup
                    duplicate_cleanup_candidate = {
                        "transcript_name": transcript.name,
                        "original_name": transcript.stem + ".mp3",
                        "skip_reason": "duplicate",
                        "notion_entry_id": None  # No new Notion entry for duplicates
                    }
                    state["duplicate_cleanup_candidates"] = state.get("duplicate_cleanup_candidates", [])
                    state["duplicate_cleanup_candidates"].append(duplicate_cleanup_candidate)
                    logger.info(f"INFO: Added duplicate to cleanup candidates: {transcript.name}")

            if not valid_transcripts:
                if duplicate_transcripts:
                    logger.warning("WARNING: No valid transcripts to process, but duplicates will be cleaned up in Step 5")
                else:
                    logger.warning("WARNING: No valid transcripts to process")
                return True, [], []

            logger.info(f"Processing {len(valid_transcripts)} valid transcripts")

            # Process transcripts sequentially
            # Note: Sequential processing avoids OpenAI API rate limits.
            # Future enhancement: Parallel processing with controlled concurrency (3-5 workers)
            # to improve speed 2-3x while staying within rate limits.
            successful_analyses = []
            failed_transcripts = []

            for i, transcript in enumerate(valid_transcripts, 1):
                logger.info(f"")
                logger.info(f"Processing {i}/{len(valid_transcripts)}: {transcript.name}")

                success, result_data, error_reason = self.process_single_transcript(transcript, process_function)

                if success:
                    # Extract notion_entry_id from the result data
                    # Handles two formats:
                    # 1. result["analysis"]["notion_entry_id"]
                    # 2. result["analyses"][0]["notion_entry_id"]
                    notion_entry_id = None
                    if result_data.get("analysis") and result_data["analysis"].get("notion_entry_id"):
                        # Single analysis case
                        notion_entry_id = result_data["analysis"]["notion_entry_id"]
                    elif result_data.get("analyses"):
                        # Multiple analyses case - get the first one's ID
                        if result_data["analyses"] and result_data["analyses"][0].get("notion_entry_id"):
                            notion_entry_id = result_data["analyses"][0]["notion_entry_id"]

                    successful_analyses.append({
                        "transcript_name": transcript.name,
                        "transcript": transcript.name,  # Keep both for compatibility
                        "result": result_data,
                        "processed_file": f"{transcript.stem}_processed.json",
                        "notion_entry_id": notion_entry_id,
                        "title": result_data.get("analysis", {}).get("title") or
                                (result_data.get("analyses", [{}])[0].get("title") if result_data.get("analyses") else None),
                        "content": result_data.get("analysis", {}).get("content") or
                                  (result_data.get("analyses", [{}])[0].get("content") if result_data.get("analyses") else None)
                    })

                    # Update state
                    state["ai_processing_success"] = state.get("ai_processing_success", [])
                    state["ai_processing_success"].append(transcript.name)

                    # Check if Notion entry was created
                    if notion_entry_id:
                        state["notion_success"] = state.get("notion_success", [])
                        state["notion_success"].append(transcript.name)
                        logger.info(f"   SUCCESS: AI Analysis complete")
                        logger.info(f"   SUCCESS: Notion Entry created (ID: {notion_entry_id[:8]}...)")
                    else:
                        logger.warning(f"   WARNING: AI Analysis complete but no Notion entry ID found")

                else:
                    failed_transcripts.append(transcript)
                    if move_failed_callback:
                        move_failed_callback(transcript, error_reason)
                    state["ai_processing_failed"] = state.get("ai_processing_failed", [])
                    state["ai_processing_failed"].append(transcript.name)
                    logger.error(f"   ERROR: Failed: {error_reason}")

            # Final summary
            logger.info(f"")
            logger.info(f"Processing Summary:")
            logger.info(f"   SUCCESS: {len(successful_analyses)}/{len(valid_transcripts)} transcripts")
            logger.info(f"   SKIP: {len(duplicate_transcripts)} duplicates")
            logger.info(f"   FAILED: {len(failed_transcripts)} transcripts")
            logger.info(f"   AI Analysis: {len(successful_analyses)} successful")
            logger.info(f"   Notion Entries: {len([a for a in successful_analyses if a.get('notion_entry_id')])} created")
            logger.info(f"   Cleanup Candidates: {len(state.get('duplicate_cleanup_candidates', []))} duplicates")

            # Update state summary
            state["processing_complete"] = True
            state["processing_summary"] = {
                "total_transcripts": len(valid_transcripts),
                "successful_analyses": len(successful_analyses),
                "duplicate_transcripts": len(duplicate_transcripts),
                "failed_transcripts": len(failed_transcripts),
                "notion_entries_created": len([a for a in successful_analyses if a.get('notion_entry_id')]),
                "success_rate": len(successful_analyses) / len(valid_transcripts) if valid_transcripts else 0
            }

            return True, successful_analyses, failed_transcripts

        except Exception as e:
            logger.error(f"ERROR: Processing and verification failed: {e}")
            return False, [], []
