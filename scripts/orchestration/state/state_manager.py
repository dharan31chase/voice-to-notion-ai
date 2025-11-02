"""
State Management Module

Responsibilities:
- Load and save orchestrator state from JSON
- Session ID generation and tracking
- Archive state updates with verification
- Session finalization

Does NOT handle:
- File operations (StagingManager, ArchiveManager)
- Notion verification (NotionVerifier)
- Business logic (Orchestrator)
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class StateManager:
    """Manages state persistence and session tracking for the orchestrator."""

    def __init__(self, state_file: Path, cache_folder: Path):
        """
        Initialize state manager.

        Args:
            state_file: Path to state JSON file
            cache_folder: Path to cache directory
        """
        self.state_file = state_file
        self.cache_folder = cache_folder
        self.state: Dict = {}

        logger.info(f"StateManager initialized with state file: {state_file}")

    def load_state(self) -> Dict:
        """
        Load state from JSON file.

        Returns:
            Dict: State dictionary with sessions, processed files, etc.
        """
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    logger.info("✅ Loaded existing state file")
                    self.state = state
                    return state
            else:
                # Create new state file
                state = self._default_state()
                self.save_state(state)
                logger.info("✅ Created new state file")
                self.state = state
                return state
        except Exception as e:
            logger.error(f"❌ Error loading state: {e}")
            # Return minimal state
            state = self._default_state()
            self.state = state
            return state

    def save_state(self, state: Dict) -> bool:
        """
        Save state to JSON file using atomic write.

        Atomic write prevents data loss if crash occurs during write:
        1. Write to temp file first
        2. Atomic rename (all-or-nothing operation)

        Args:
            state: State dictionary to save

        Returns:
            bool: True if save successful
        """
        try:
            # Atomic write: write to temp file first, then rename
            temp_file = self.state_file.with_suffix('.tmp')

            with open(temp_file, 'w') as f:
                json.dump(state, f, indent=2)

            # Atomic rename - original file stays intact until this succeeds
            temp_file.replace(self.state_file)

            self.state = state
            return True

        except Exception as e:
            logger.error(f"❌ Error saving state: {e}")
            return False

    def generate_session_id(self) -> str:
        """
        Generate unique session ID based on timestamp.

        Returns:
            str: Session ID (format: session_YYYYMMDD_HHMMSS)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"

    def update_archive_state(
        self,
        session_id: str,
        archived_files: List[Dict],
        verification_summary: Dict,
        failed_entries: List[Dict],
        failed_archives: List[Dict],
        cleanup_failures: List[Dict]
    ) -> None:
        """
        Update state with archive results and verification data.

        Args:
            session_id: Current session ID
            archived_files: Successfully archived files
            verification_summary: Notion verification results
            failed_entries: Files with failed Notion entries
            failed_archives: Files that failed to archive
            cleanup_failures: Files that failed cleanup
        """
        try:
            # Add archive info to current session
            self.state["current_session"]["archive_complete"] = True
            self.state["current_session"]["archive_folder"] = str(self.cache_folder.parent / "Recording Archives")
            self.state["current_session"]["archived_recordings"] = [
                {
                    "transcript_name": file_info["transcript_name"],
                    "original_name": file_info["original_name"],
                    "archive_name": file_info["archive_name"],
                    "archive_path": str(file_info["archive_path"]),
                    "size_mb": file_info["size_mb"],
                    "notion_entry_id": file_info.get("notion_entry_id")
                }
                for file_info in archived_files
            ]

            # Add verification status
            self.state["current_session"]["verification_summary"] = verification_summary
            self.state["current_session"]["failed_entries"] = failed_entries
            self.state["current_session"]["failed_archives"] = failed_archives
            self.state["current_session"]["cleanup_failures"] = cleanup_failures

            # Mark session for future cleanup (7 days from now)
            cleanup_date = datetime.now() + timedelta(days=7)
            self.state["current_session"]["cleanup_ready"] = True
            self.state["current_session"]["cleanup_date"] = cleanup_date.isoformat()

            logger.info(f"📊 Updated state with {len(archived_files)} archived files and verification status")

        except Exception as e:
            logger.error(f"❌ Error updating archive state: {e}")

    def finalize_session(
        self,
        session_id: str,
        verification_summary: Dict,
        archived_files: List[Dict],
        failed_entries: List[Dict]
    ) -> None:
        """
        Finalize session with verification results.

        Args:
            session_id: Session to finalize
            verification_summary: Notion verification results
            archived_files: Successfully archived files
            failed_entries: Files with failed Notion entries
        """
        try:
            # Create previous session entry with verification info
            previous_session = {
                "session_id": session_id,
                "start_time": self.state["current_session"]["start_time"],
                "end_time": datetime.now().isoformat(),
                "cleanup_ready": True,
                "cleanup_date": self.state["current_session"].get("cleanup_date"),
                "verification_summary": verification_summary,
                "files_to_delete": {
                    "recordings": [f["archive_path"] for f in archived_files],
                    "transcripts": [f["transcript_name"] for f in archived_files]
                },
                "failed_entries": failed_entries,
                "summary": {
                    "total_recordings": len(archived_files),
                    "total_transcripts": len(archived_files),
                    "success_rate": verification_summary.get("success_rate", 0),
                    "verification_passed": verification_summary.get("verification_passed", False)
                }
            }

            # Add to previous sessions
            if "previous_sessions" not in self.state:
                self.state["previous_sessions"] = []

            self.state["previous_sessions"].append(previous_session)

            # Keep only last 7 days of sessions
            cutoff_date = datetime.now() - timedelta(days=7)
            self.state["previous_sessions"] = [
                session for session in self.state["previous_sessions"]
                if datetime.fromisoformat(session["start_time"]) > cutoff_date
            ]

            # Clear current session (will be recreated on next USB connection)
            self.state["current_session"] = {}

            logger.info(f"✅ Session {session_id} finalized with verification details")

        except Exception as e:
            logger.error(f"❌ Error finalizing session: {e}")

    def _finalize_session_legacy(self, session_id: str) -> None:
        """
        Legacy session finalization (backward compatibility).

        Args:
            session_id: Session to finalize
        """
        try:
            # Create previous session entry
            previous_session = {
                "session_id": session_id,
                "start_time": self.state["current_session"]["start_time"],
                "end_time": datetime.now().isoformat(),
                "cleanup_ready": True,
                "cleanup_date": self.state["current_session"].get("cleanup_date"),
                "files_to_delete": {
                    "recordings": [f["archive_path"] for f in self.state["current_session"].get("archived_recordings", [])],
                    "transcripts": [f for f in self.state["current_session"].get("transcripts_created", [])]
                },
                "summary": {
                    "total_recordings": len(self.state["current_session"].get("recordings_processed", [])),
                    "total_transcripts": len(self.state["current_session"].get("transcripts_created", [])),
                    "success_rate": self.state["current_session"].get("transcription_summary", {}).get("success_rate", 0)
                }
            }

            # Add to previous sessions
            if "previous_sessions" not in self.state:
                self.state["previous_sessions"] = []

            self.state["previous_sessions"].append(previous_session)

            # Keep only last 7 days of sessions
            cutoff_date = datetime.now() - timedelta(days=7)
            self.state["previous_sessions"] = [
                session for session in self.state["previous_sessions"]
                if datetime.fromisoformat(session["start_time"]) > cutoff_date
            ]

            # Clear current session (will be recreated on next USB connection)
            self.state["current_session"] = {}

            logger.info(f"✅ Session {session_id} finalized and moved to previous sessions")

        except Exception as e:
            logger.error(f"❌ Error finalizing session: {e}")

    def get_processed_files(self) -> set:
        """
        Get set of all processed MP3 filenames from state.

        Returns:
            set: Filenames that have been processed
        """
        processed_files = set()

        # Get list of already processed files from state
        if self.state.get("current_session") and self.state["current_session"].get("recordings_processed"):
            processed_files.update(self.state["current_session"]["recordings_processed"])

        # Also check previous sessions (within 7 days)
        if self.state.get("previous_sessions"):
            for session in self.state["previous_sessions"]:
                if session.get("summary", {}).get("total_recordings"):
                    # Extract filenames from archived recordings
                    if session.get("files_to_delete", {}).get("recordings"):
                        for path in session["files_to_delete"]["recordings"]:
                            # Extract filename from path
                            filename = Path(path).name
                            processed_files.add(filename)

        return processed_files

    def mark_file_processed(self, filename: str, session_id: str) -> None:
        """
        Mark file as processed in current session.

        Args:
            filename: MP3 filename
            session_id: Current session ID
        """
        if "recordings_processed" not in self.state["current_session"]:
            self.state["current_session"]["recordings_processed"] = []

        if filename not in self.state["current_session"]["recordings_processed"]:
            self.state["current_session"]["recordings_processed"].append(filename)
            logger.debug(f"✅ Marked {filename} as processed")

    def _default_state(self) -> Dict:
        """
        Get default state structure.

        Returns:
            Dict: Empty state with required structure
        """
        return {
            "current_session": {},
            "previous_sessions": [],
            "archive_management": {
                "last_cleanup": None,
                "files_to_delete": [],
                "deletion_scheduled": None
            },
            "system_health": {
                "total_recordings_processed": 0,
                "success_rate": 1.0,
                "last_error": None,
                "last_success": None
            }
        }
