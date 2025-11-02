#!/usr/bin/env python3
"""
Voice Recording Orchestrator
Handles end-to-end processing of Sony recorder .mp3 files to Notion entries
"""

import os
import json
import time
import subprocess
import shutil
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add parent directory to path for core imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Add scripts directory to path for orchestration imports
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# Import shared utilities
from core.logging_utils import configure_root_logger, get_logger
from core.config_loader import ConfigLoader

# Import orchestration modules
from orchestration.state import StateManager
from orchestration.detection import USBDetector, FileValidator

# Try to import Notion client, but don't fail if it's not available
try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    Client = None

# Configure unified logging
configure_root_logger("INFO")
logger = get_logger(__name__)

class RecordingOrchestrator:
    def __init__(self, dry_run=False, skip_steps=None, auto_continue=False, max_files=None):
        self.project_root = Path(__file__).parent.parent
        self.recorder_path = Path("/Volumes/IC RECORDER/REC_FILE/FOLDER01")
        self.transcripts_folder = self.project_root / "transcripts"
        self.archives_folder = self.project_root / "Recording Archives"
        self.failed_folder = self.project_root / "Failed"
        self.staging_folder = self.project_root / "staging"  # Phase 1: Local staging
        self.state_file = self.project_root / ".cache" / "recording_states.json"
        self.cache_folder = self.project_root / ".cache"

        # Load configuration
        self.config = ConfigLoader()

        # CLI options
        self.dry_run = dry_run
        self.skip_steps = set(skip_steps) if skip_steps else set()
        self.auto_continue = auto_continue
        self.max_files = max_files  # Phase 1: Limit files for testing

        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No file operations will be performed")
        if self.skip_steps:
            logger.info(f"⏭️ Skipping steps: {', '.join(sorted(self.skip_steps))}")
        if self.max_files:
            logger.info(f"📊 Max files limit: {self.max_files}")

        # Ensure required folders exist
        self._setup_folders()

        # Initialize state manager (Phase B Step 2)
        self.state_manager = StateManager(self.state_file, self.cache_folder)
        self.state = self.state_manager.load_state()

        # Initialize detection modules (Phase B Step 3)
        self.usb_detector = USBDetector(self.recorder_path)
        self.file_validator = FileValidator(self.config)

        # Initialize staging manager (Phase B Step 4)
        from orchestration.staging import StagingManager
        self.staging_manager = StagingManager(self.staging_folder)

        # Initialize transcription engine (Phase B Step 5)
        from orchestration.transcription import TranscriptionEngine
        self.transcription_engine = TranscriptionEngine(self.config, self.file_validator)

        # Initialize processing engine (Phase B Step 6)
        from orchestration.processing import ProcessingEngine
        self.processing_engine = ProcessingEngine(self.config, self.project_root)

        # Current session info
        self.current_session_id = None
        self.session_start_time = None

        # Initialize Notion client for verification
        self._setup_notion_client()

        # Phase 1: Performance tracking
        from core.performance_tracker import PerformanceTracker
        self.performance_tracker = PerformanceTracker()
        self.performance_tracker.set_baseline({'duration_minutes': 32})  # From latest run
        
    def _setup_folders(self):
        """Create necessary folders if they don't exist"""
        self.transcripts_folder.mkdir(exist_ok=True)
        self.archives_folder.mkdir(exist_ok=True)
        self.failed_folder.mkdir(exist_ok=True)
        self.staging_folder.mkdir(exist_ok=True)  # Phase 1: Local staging folder
        (self.failed_folder / "failed_recordings").mkdir(exist_ok=True)
        (self.failed_folder / "failed_transcripts").mkdir(exist_ok=True)
        (self.failed_folder / "failure_logs").mkdir(exist_ok=True)
        self.cache_folder.mkdir(exist_ok=True)
        
    def _setup_notion_client(self):
        """Initialize Notion client for entry verification"""
        try:
            self.notion_token = os.getenv('NOTION_TOKEN')
            
            if not self.notion_token:
                logger.warning("⚠️ NOTION_TOKEN not found - verification will be limited")
                self.notion_client = None
                return
            
            if not NOTION_AVAILABLE:
                logger.warning("⚠️ notion-client not installed - verification will be limited")
                self.notion_client = None
                return
            
            self.notion_client = Client(auth=self.notion_token)
            logger.info("✅ Notion client initialized for verification")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Notion client: {e}")
            self.notion_client = None
        
    def _load_state(self) -> Dict:
        """Load existing state or create new state file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    logger.info("✅ Loaded existing state file")
                    return state
            else:
                # Create new state file
                state = {
                    "current_session": None,
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
                self._save_state(state)
                logger.info("✅ Created new state file")
                return state
        except Exception as e:
            logger.error(f"❌ Error loading state: {e}")
            # Return minimal state
            return {
                "current_session": None,
                "previous_sessions": [],
                "archive_management": {"last_cleanup": None, "files_to_delete": [], "deletion_scheduled": None},
                "system_health": {"total_recordings_processed": 0, "success_rate": 1.0, "last_error": None, "last_success": None}
            }
    
    def _save_state(self, state: Dict):
        """
        Save state to file.

        Now delegates to StateManager with atomic writes.
        """
        self.state_manager.save_state(state)
    
    def _check_usb_connection(self) -> bool:
        """
        Check if USB recorder is connected and accessible.

        Now delegates to USBDetector.
        """
        return self.usb_detector.check_connection()
    
    def _scan_mp3_files(self) -> List[Path]:
        """
        Scan recorder folder for .mp3 files, excluding macOS hidden files.

        Now delegates to USBDetector.
        """
        return self.usb_detector.scan_files()
    
    def _validate_file_integrity(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate .mp3 file integrity.

        Now delegates to FileValidator.
        """
        return self.file_validator.validate_integrity(file_path)
    
    def _generate_session_id(self) -> str:
        """
        Generate unique session ID based on current timestamp.

        Now delegates to StateManager.
        """
        return self.state_manager.generate_session_id()
    
    def _get_unprocessed_files(self, mp3_files: List[Path]) -> List[Path]:
        """
        Identify files that haven't been processed yet.

        Now delegates to USBDetector (gets processed files from StateManager).
        """
        # Get processed files from state manager
        processed_files = self.state_manager.get_processed_files()

        # Delegate filtering to USBDetector
        return self.usb_detector.get_unprocessed_files(mp3_files, processed_files)
    
    def _run_automatic_cleanup(self):
        """Run automatic 7-day cleanup of old archives"""
        try:
            current_time = datetime.now()
            last_cleanup = self.state.get("archive_management", {}).get("last_cleanup")
            
            # Check if cleanup is needed
            if last_cleanup:
                last_cleanup_dt = datetime.fromisoformat(last_cleanup)
                days_since_cleanup = (current_time - last_cleanup_dt).days
                
                if days_since_cleanup >= 7:
                    logger.info("🧹 Running automatic 7-day cleanup...")
                    self._cleanup_old_archives()
                    self.state["archive_management"]["last_cleanup"] = current_time.isoformat()
                    self._save_state(self.state)
                else:
                    logger.info(f"⏰ Next cleanup in {7 - days_since_cleanup} days")
            else:
                # First time running - set cleanup date
                self.state["archive_management"]["last_cleanup"] = current_time.isoformat()
                self._save_state(self.state)
                logger.info("⏰ First run - cleanup scheduled for 7 days from now")
                
        except Exception as e:
            logger.error(f"❌ Error in automatic cleanup: {e}")
    
    def _cleanup_old_archives(self):
        """Remove archive files older than 7 days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=7)
            deleted_count = 0
            
            # Clean up old .mp3 archives
            for mp3_file in self.archives_folder.glob("*.mp3"):
                if mp3_file.stat().st_mtime < cutoff_date.timestamp():
                    mp3_file.unlink()
                    deleted_count += 1
                    logger.info(f"🗑️ Deleted old archive: {mp3_file.name}")
            
            # Clean up old .txt archives
            for txt_file in self.archives_folder.glob("*.txt"):
                if txt_file.stat().st_mtime < cutoff_date.timestamp():
                    txt_file.unlink()
                    deleted_count += 1
                    logger.info(f"🗑️ Deleted old archive: {txt_file.name}")
            
            logger.info(f"🧹 Cleanup complete: {deleted_count} old files removed")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
    
    def step1_monitor_and_detect(self) -> Tuple[bool, List[Path]]:
        """
        Step 1: Monitor & Detect
        Scans USB recorder for new .mp3 files and validates them
        """
        logger.info("🔍 Step 1: Monitor & Detect")
        logger.info("=" * 50)
        
        try:
            # Run automatic cleanup first
            self._run_automatic_cleanup()
            
            # Check USB connection
            if not self._check_usb_connection():
                return False, []
            
            # Scan for .mp3 files
            mp3_files = self._scan_mp3_files()
            if not mp3_files:
                logger.warning("⚠️ No .mp3 files found in recorder folder")
                return True, []  # Success but no files to process
            
            # Validate file integrity
            valid_files = []
            invalid_files = []
            
            for file_path in mp3_files:
                is_valid, message = self._validate_file_integrity(file_path)
                if is_valid:
                    valid_files.append(file_path)
                else:
                    invalid_files.append((file_path, message))
                    logger.warning(f"⚠️ Invalid file: {file_path.name} - {message}")
            
            if not valid_files:
                logger.error("❌ No valid .mp3 files found")
                return False, []
            
            # Get unprocessed files
            unprocessed_files = self._get_unprocessed_files(valid_files)

            # Phase 1: Apply max_files limit if set
            if self.max_files and len(unprocessed_files) > self.max_files:
                logger.info(f"📊 Limiting to first {self.max_files} files (--max-files flag)")
                unprocessed_files = unprocessed_files[:self.max_files]

            # Phase 1: Copy files to staging
            staged_files, staging_failures = self._copy_files_to_staging(unprocessed_files)

            if not staged_files:
                logger.error("❌ No files successfully staged")
                return False, []

            # Generate session ID
            self.current_session_id = self._generate_session_id()
            self.session_start_time = datetime.now()

            # Initialize current session in state
            self.state["current_session"] = {
                "session_id": self.current_session_id,
                "start_time": self.session_start_time.isoformat(),
                "recordings_processed": [],
                "transcripts_created": [],
                "notion_success": [],
                "ai_processing_success": [],
                "ai_processing_failed": [],
                "failed_transcriptions": [],
                "failed_notion": [],
                "cleanup_candidates": [],
                "preparation_complete": False,
                "processing_plan": {},
                "transcription_complete": False,
                "processing_complete": False,
                "usb_files_map": {}  # Phase 1: Map staging files to original USB paths
            }

            # Phase 1: Store USB-to-staging mapping for later cleanup
            for usb_file in unprocessed_files:
                staging_file = self.staging_folder / usb_file.name
                if staging_file in staged_files:
                    self.state["current_session"]["usb_files_map"][str(staging_file)] = str(usb_file)

            # Log discovery summary
            logger.info(f"🆔 Session ID: {self.current_session_id}")
            logger.info(f"📊 Valid files found: {len(valid_files)}")
            logger.info(f"📋 Files staged for processing: {len(staged_files)}")
            if staging_failures:
                logger.info(f"⏭️ Files skipped: {len(staging_failures)}")
            logger.info(f"⚠️ Invalid files: {len(invalid_files)}")

            if invalid_files:
                for file_path, message in invalid_files:
                    logger.warning(f"   - {file_path.name}: {message}")

            if staging_failures:
                for file_path, reason in staging_failures:
                    logger.info(f"   ⏭️ {file_path.name}: {reason}")

            # Save state
            self._save_state(self.state)

            logger.info("✅ Step 1 complete - files staged and ready for transcription")
            return True, staged_files  # Phase 1: Return staging paths, not USB paths
            
        except Exception as e:
            logger.error(f"❌ Step 1 failed: {e}")
            return False, []
    
    def _extract_file_metadata(self, file_path: Path) -> Dict:
        """
        Phase B Step 5: Extract metadata from audio file
        Delegates to TranscriptionEngine
        """
        return self.transcription_engine.extract_file_metadata(file_path)

    def _should_skip_short_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Phase 1: Check if file should be skipped due to being too short
        Uses file size estimate: 1MB ≈ 1 minute, so 33KB ≈ 2 seconds
        """
        try:
            skip_threshold_seconds = self.config.get("processing.skip_short_audio_seconds", 2)
            skip_threshold_bytes = skip_threshold_seconds * 33 * 1024  # 33KB per 2 seconds

            file_size = file_path.stat().st_size

            if file_size < skip_threshold_bytes:
                estimated_seconds = file_size / (33 * 1024) * 2
                reason = f"File too short (~{estimated_seconds:.1f}s, minimum {skip_threshold_seconds}s)"
                return True, reason

            return False, ""
        except Exception as e:
            logger.error(f"❌ Error checking file size for {file_path.name}: {e}")
            return False, ""

    def _copy_files_to_staging(self, files: List[Path]) -> Tuple[List[Path], List[Tuple[Path, str]]]:
        """
        Phase B Step 4: Copy files from USB to local staging folder
        Delegates to StagingManager after filtering short files
        Returns: (successful_copies, failed_copies)
        """
        # Check if staging is enabled
        staging_enabled = self.config.get("processing.staging_enabled", True)
        if not staging_enabled:
            logger.info("ℹ️ Staging disabled - will transcribe directly from USB")
            return files, []

        # Filter out short files BEFORE staging (Option B: Orchestrator responsibility)
        files_to_stage = []
        failed = []

        for file_path in files:
            should_skip, skip_reason = self._should_skip_short_file(file_path)
            if should_skip:
                logger.info(f"⏭️ Skipping {file_path.name}: {skip_reason}")
                failed.append((file_path, skip_reason))
            else:
                files_to_stage.append(file_path)

        # Delegate to StagingManager
        successful, staging_failures = self.staging_manager.copy_to_staging(files_to_stage)

        # Combine failures from filtering and staging
        failed.extend(staging_failures)

        return successful, failed

    def _safe_delete_usb_file(self, usb_file: Path) -> bool:
        """
        Phase B Step 4: Safely delete file from USB
        Delegates to StagingManager for platform-specific deletion handling
        """
        return self.staging_manager.safe_delete_usb(usb_file)

    def _cleanup_staging_files(self) -> int:
        """
        Phase B Step 4: Clean up staging folder after successful processing
        Delegates to StagingManager
        Returns count of files cleaned
        """
        return self.staging_manager.cleanup_staging()

    def _create_balanced_batches(self, files: List[Path]) -> List[List[Path]]:
        """
        Phase B Step 5: Create duration-aware batches with work budget balancing
        Delegates to TranscriptionEngine
        """
        return self.transcription_engine.create_balanced_batches(files)

    def _check_system_resources(self) -> Tuple[bool, Dict]:
        """
        Phase B Step 5: Check if system has sufficient resources for processing
        Delegates to TranscriptionEngine
        """
        return self.transcription_engine.check_system_resources(self.project_root)
    
    def _create_processing_batches(self, files: List[Path], batch_size: int = 4) -> List[List[Path]]:
        """Create optimal processing batches"""
        batches = []
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            batches.append(batch)
        return batches
    
    def _estimate_processing_time(self, files: List[Path]) -> Dict:
        """Estimate total processing time for all files"""
        try:
            total_size_mb = 0
            total_estimated_minutes = 0
            
            for file_path in files:
                metadata = self._extract_file_metadata(file_path)
                total_size_mb += metadata["size_mb"]
                total_estimated_minutes += metadata["estimated_minutes"]
            
            # Whisper processing time estimate: ~2x real-time for small model
            # Plus overhead for file I/O and transcription
            estimated_processing_minutes = total_estimated_minutes * 2.5
            
            return {
                "total_files": len(files),
                "total_size_mb": round(total_size_mb, 1),
                "total_audio_minutes": total_estimated_minutes,
                "estimated_processing_minutes": round(estimated_processing_minutes, 1),
                "estimated_processing_hours": round(estimated_processing_minutes / 60, 1)
            }
        except Exception as e:
            logger.error(f"❌ Error estimating processing time: {e}")
            return {
                "total_files": len(files),
                "total_size_mb": 0,
                "total_audio_minutes": 0,
                "estimated_processing_minutes": 0,
                "estimated_processing_hours": 0,
                "error": str(e)
            }
    
    def step2_validate_and_prepare(self, unprocessed_files: List[Path]) -> Tuple[bool, List[Path], Dict]:
        """
        Step 2: Validate & Prepare
        Prepares files for batch transcription with resource validation
        """
        logger.info("📊 Step 2: Validate & Prepare")
        logger.info("=" * 50)
        
        try:
            if not unprocessed_files:
                logger.warning("⚠️ No files to prepare")
                return True, [], {}
            
            # Check system resources
            resources_ok, resource_status = self._check_system_resources()
            if not resources_ok:
                logger.error("❌ Insufficient system resources for processing")
                return False, [], {}
            
            logger.info(f"✅ System resources OK:")
            logger.info(f"   - Disk: {resource_status['disk_free_gb']}GB free")
            if 'memory_available_gb' in resource_status and resource_status['memory_available_gb'] != "Unknown":
                logger.info(f"   - Memory: {resource_status['memory_available_gb']}GB available")
            
            # Extract metadata for all files
            logger.info("📋 Extracting file metadata...")
            file_metadata = []
            valid_files = []
            invalid_files = []
            skipped_large_files = []
            
            for file_path in unprocessed_files:
                metadata = self._extract_file_metadata(file_path)
                if "error" not in metadata:
                    # Skip files over 10 minutes
                    if metadata["estimated_minutes"] > 10:
                        skipped_large_files.append((file_path, metadata["estimated_minutes"]))
                        logger.info(f"⏭️ Skipping large file: {file_path.name} (~{metadata['estimated_minutes']} min)")
                        continue
                    
                    file_metadata.append(metadata)
                    valid_files.append(file_path)
                else:
                    invalid_files.append(file_path)
                    logger.warning(f"⚠️ Invalid file metadata: {file_path.name}")
            
            if not valid_files:
                logger.error("❌ No valid files to process")
                return False, [], {}
            
            # Sort files by creation time (oldest first)
            valid_files.sort(key=lambda x: x.stat().st_ctime)
            
            # Create processing batches
            batch_size = 4  # Optimal batch size for parallel processing
            batches = self._create_processing_batches(valid_files, batch_size)
            
            # Estimate processing time
            time_estimate = self._estimate_processing_time(valid_files)
            
            # Log processing plan
            logger.info(f"📊 Processing Plan Generated")
            logger.info(f"   Total Files: {time_estimate['total_files']}")
            if skipped_large_files:
                logger.info(f"   Skipped (>10 min): {len(skipped_large_files)} files")
            logger.info(f"   Batch Size: {batch_size} files")
            logger.info(f"   Estimated Time: ~{time_estimate['estimated_processing_minutes']} minutes")
            logger.info(f"   Disk Space Required: ~{time_estimate['total_size_mb']} MB")
            
            # Log batch details
            for i, batch in enumerate(batches, 1):
                batch_size_actual = len(batch)
                batch_files = [f.name for f in batch]
                logger.info(f"📋 Batch {i} ({batch_size_actual} files):")
                for file_path in batch:
                    metadata = next(m for m in file_metadata if m["name"] == file_path.name)
                    logger.info(f"   - {file_path.name} ({metadata['size_mb']} MB, ~{metadata['estimated_minutes']} min)")
            
            # Update state with preparation info
            self.state["current_session"]["preparation_complete"] = True
            self.state["current_session"]["processing_plan"] = {
                "total_files": time_estimate["total_files"],
                "batch_size": batch_size,
                "estimated_time_minutes": time_estimate["estimated_processing_minutes"],
                "disk_space_mb": time_estimate["total_size_mb"],
                "batches": len(batches)
            }
            
            # Save state
            self._save_state(self.state)
            
            logger.info("✅ Step 2 complete - ready for transcription")
            return True, valid_files, time_estimate
            
        except Exception as e:
            logger.error(f"❌ Step 2 failed: {e}")
            return False, [], {}
    
    def _check_whisper_installation(self) -> bool:
        """
        Check if Whisper is installed and accessible.

        Now delegates to FileValidator.
        """
        return self.file_validator.check_dependencies()
    
    def _check_disk_space(self, required_mb: float) -> bool:
        """
        Check if sufficient disk space is available.

        Now delegates to FileValidator.
        """
        return self.file_validator.check_disk_space(self.project_root, required_mb)
    
    def _should_transcribe_audio(self, audio_file: Path) -> bool:
        """
        Phase B Step 5: Check if we should transcribe this audio file (prevents duplicates)
        Delegates to TranscriptionEngine
        """
        return self.transcription_engine.should_transcribe(audio_file, self.transcripts_folder)
    
    def _monitor_cpu_usage(self) -> float:
        """
        Phase B Step 5: Monitor current CPU usage percentage
        Delegates to TranscriptionEngine
        """
        return self.transcription_engine.monitor_cpu_usage()
    
    def _move_failed_file(self, file_path: Path, error_reason: str, file_type: str = "recording"):
        """Move failed file to appropriate failed folder with error logging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if file_type == "recording":
                failed_dir = self.failed_folder / "failed_recordings"
                safe_error = error_reason[:20].replace('/', '_').replace('\\', '_')
                new_name = f"{file_path.stem}_{timestamp}_FAILED_{safe_error}.mp3"
            else:
                failed_dir = self.failed_folder / "failed_transcripts"
                safe_error = error_reason[:20].replace('/', '_').replace('\\', '_')
                new_name = f"{file_path.stem}_{timestamp}_FAILED_{safe_error}.txt"
            
            failed_path = failed_dir / new_name
            shutil.move(str(file_path), str(failed_path))
            
            # Log failure details
            log_file = self.failed_folder / "failure_logs" / f"failure_{timestamp}.log"
            with open(log_file, 'w') as f:
                f.write(f"File: {file_path.name}\n")
                f.write(f"Type: {file_type}\n")
                f.write(f"Error: {error_reason}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Original Path: {file_path}\n")
                f.write(f"Failed Path: {failed_path}\n")
            
            logger.info(f"📁 Moved failed {file_type}: {file_path.name} → {failed_path.name}")
            
        except Exception as e:
            logger.error(f"❌ Error moving failed file {file_path.name}: {e}")
    
    def step3_transcribe(self, valid_files: List[Path], time_estimate: Dict) -> Tuple[bool, List[Path], List[Path]]:
        """
        Phase B Step 5: Transcribe audio files to text
        Delegates to TranscriptionEngine for parallel batch transcription
        """
        logger.info("🎙️ Step 3: Transcribe")
        logger.info("=" * 50)

        # Delegate to TranscriptionEngine with _move_failed_file callback
        success, transcripts, failed = self.transcription_engine.transcribe_batch(
            files=valid_files,
            transcripts_folder=self.transcripts_folder,
            failed_folder=self.failed_folder,
            state=self.state["current_session"],
            move_failed_callback=self._move_failed_file
        )

        # Save state after transcription
        if success:
            self._save_state(self.state)
            logger.info("✅ Step 3 complete - ready for AI processing")

        return success, transcripts, failed
    
    def _move_failed_transcript(self, transcript_path: Path, error_reason: str):
        """Move failed transcript to failed folder"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_error = error_reason[:20].replace('/', '_').replace('\\', '_')
            
            failed_dir = self.failed_folder / "failed_transcripts"
            new_name = f"{transcript_path.stem}_{timestamp}_FAILED_{safe_error}.txt"
            failed_path = failed_dir / new_name
            
            shutil.move(str(transcript_path), str(failed_path))
            
            # Log failure details
            log_file = self.failed_folder / "failure_logs" / f"failure_{timestamp}.log"
            with open(log_file, 'w') as f:
                f.write(f"File: {transcript_path.name}\n")
                f.write(f"Type: transcript\n")
                f.write(f"Error: {error_reason}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Original Path: {transcript_path}\n")
                f.write(f"Failed Path: {failed_path}\n")
            
            logger.info(f"📁 Moved failed transcript: {transcript_path.name} → {failed_path.name}")
            
        except Exception as e:
            logger.error(f"❌ Error moving failed transcript {transcript_path.name}: {e}")
    
    def step4_stage_and_process(self, successful_transcripts: List[Path]) -> Tuple[bool, List[Dict], List[Path]]:
        """
        Phase B Step 6: Stage & Process
        Delegates to ProcessingEngine for AI processing and Notion verification
        """
        logger.info("🚀 Step 4: Stage & Process")
        logger.info("=" * 50)

        # Delegate to ProcessingEngine
        success, successful_analyses, failed_transcripts = self.processing_engine.process_and_verify(
            transcripts=successful_transcripts,
            project_root=self.project_root,
            failed_folder=self.failed_folder,
            state=self.state["current_session"],
            move_failed_callback=self._move_failed_transcript,
            notion_client=self.notion_client
        )

        # Save state after processing
        if success:
            self._save_state(self.state)
            logger.info("✅ Step 4 complete - ready for verification")

        return success, successful_analyses, failed_transcripts
    
    def _verify_session_success(self, successful_transcripts: List[Path], successful_analyses: List[Dict]) -> Tuple[bool, Dict]:
        """Verify that the session completed successfully enough to proceed with archiving"""
        try:
            if not successful_transcripts:
                return False, {"reason": "No transcripts to verify"}
            
            # Calculate success rates
            total_transcripts = len(successful_transcripts)
            successful_count = len(successful_analyses)
            success_rate = successful_count / total_transcripts if total_transcripts > 0 else 0
            
            # Check if we meet the 80% success threshold
            meets_threshold = success_rate >= 0.8
            
            verification_result = {
                "total_transcripts": total_transcripts,
                "successful_count": successful_count,
                "failed_count": total_transcripts - successful_count,
                "success_rate": success_rate,
                "meets_threshold": meets_threshold,
                "can_proceed": meets_threshold,
                "reason": f"Success rate: {success_rate:.1%} ({successful_count}/{total_transcripts})"
            }
            
            if meets_threshold:
                logger.info(f"✅ Session verification passed: {success_rate:.1%} success rate")
            else:
                logger.warning(f"⚠️ Session verification failed: {success_rate:.1%} success rate (need 80%+)")
            
            return meets_threshold, verification_result
            
        except Exception as e:
            logger.error(f"❌ Error during verification: {e}")
            return False, {"reason": f"Verification error: {e}"}
    
    def _create_archive_structure(self, session_id: str) -> Path:
        """Create date-based archive structure for the session"""
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
    
    def _check_usb_file_permissions(self, mp3_file: Path) -> bool:
        """
        Check if USB recorder file has proper permissions for reading.

        Now delegates to USBDetector.
        """
        return self.usb_detector.check_permissions(mp3_file)
    
    def _ensure_archive_permissions(self, archive_folder: Path) -> bool:
        """Ensure archive folder has proper permissions for writing"""
        try:
            # Create archive folder if it doesn't exist
            archive_folder.mkdir(parents=True, exist_ok=True)
            
            # Check if folder is writable
            if not os.access(archive_folder, os.W_OK):
                logger.error(f"❌ Archive folder not writable: {archive_folder}")
                logger.info(f"💡 Try: chmod 755 '{archive_folder}'")
                return False
            
            # Check if we can create a test file
            test_file = archive_folder / ".test_permissions"
            try:
                test_file.write_text("test")
                test_file.unlink()  # Clean up test file
                logger.info(f"✅ Archive folder permissions OK: {archive_folder}")
                return True
            except Exception as e:
                logger.error(f"❌ Cannot write to archive folder: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error checking archive permissions: {e}")
            return False
    
    def _archive_single_recording(self, mp3_file: Path, archive_folder: Path, session_id: str) -> Tuple[bool, Path, str]:
        """Archive a single .mp3 file with session ID"""
        try:
            # Check USB file permissions first
            if not self._check_usb_file_permissions(mp3_file):
                return False, Path(), f"USB file permission check failed: {mp3_file}"
            
            # Ensure archive folder has proper permissions
            if not self._ensure_archive_permissions(archive_folder):
                return False, Path(), f"Archive folder permission check failed: {archive_folder}"
            
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
    
    def _cleanup_recorder_file(self, mp3_file: Path, archive_path: Path) -> bool:
        """
        Phase 1: Safely delete .mp3 file from recorder after successful archiving
        Uses permission-aware deletion with extended attribute handling
        """
        try:
            # Double-check: archive must exist and have correct size
            if not archive_path.exists():
                logger.error(f"❌ Cannot delete {mp3_file.name}: Archive file missing")
                return False

            # Verify archive integrity
            if mp3_file.stat().st_size != archive_path.stat().st_size:
                logger.error(f"❌ Cannot delete {mp3_file.name}: Archive size mismatch")
                return False

            # Phase 1: Use safe deletion with permission handling
            success = self._safe_delete_usb_file(mp3_file)
            return success

        except Exception as e:
            logger.error(f"❌ Error cleaning up {mp3_file.name}: {e}")
            return False
    
    def _update_archive_state_with_verification(self, session_id: str, archived_files: List[Dict], verification_summary: Dict, failed_entries: List[Dict], failed_archives: List[Dict], cleanup_failures: List[Dict]):
        """
        Update state with archive information and verification status.

        Now delegates to StateManager.
        """
        self.state_manager.update_archive_state(
            session_id,
            archived_files,
            verification_summary,
            failed_entries,
            failed_archives,
            cleanup_failures
        )
        # Keep state in sync
        self.state = self.state_manager.state
    
    def _finalize_session_with_verification(self, session_id: str, verification_summary: Dict, archived_files: List[Dict], failed_entries: List[Dict]):
        """
        Move current session to previous sessions with verification details.

        Now delegates to StateManager.
        """
        self.state_manager.finalize_session(
            session_id,
            verification_summary,
            archived_files,
            failed_entries
        )
        # Keep state in sync
        self.state = self.state_manager.state
    
    def _finalize_session(self, session_id: str):
        """
        Move current session to previous sessions and prepare for cleanup (legacy).

        Now delegates to StateManager._finalize_session_legacy().
        """
        self.state_manager._finalize_session_legacy(session_id)
        # Keep state in sync
        self.state = self.state_manager.state
    
    def _archive_successful_recordings(self, all_cleanup_candidates: List[Dict], session_id: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Step 5b: Archive .mp3 files for successfully verified Notion entries
        Returns: archived_files, failed_archives
        """
        logger.info("📁 Step 5b: Archiving successful recordings...")
        
        archived_files = []
        failed_archives = []
        
        # Create archive structure
        archive_folder = self._create_archive_structure(session_id)
        
        for entry in all_cleanup_candidates:
            try:
                # Find corresponding .mp3 file
                transcript_name = entry.get("transcript_name", "")
                mp3_name = transcript_name.replace(".txt", ".mp3")
                mp3_path = Path("/Volumes/IC RECORDER/REC_FILE/FOLDER01") / mp3_name
                
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
                success, archive_path, error = self._archive_single_recording(mp3_path, archive_folder, session_id)
                
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
    
    def _cleanup_successful_sources(self, archived_files: List[Dict]) -> Tuple[int, int, List[Dict]]:
        """
        Step 5c: Clean up source files for successfully archived recordings
        Returns: mp3_cleanup_count, transcript_cleanup_count, cleanup_failures
        """
        logger.info("🗑️ Step 5c: Cleaning up successful source files...")
        
        mp3_cleanup_count = 0
        transcript_cleanup_count = 0
        cleanup_failures = []
        
        for file_info in archived_files:
            try:
                # Clean up .mp3 file from recorder
                mp3_path = Path("/Volumes/IC RECORDER/REC_FILE/FOLDER01") / file_info["original_name"]
                if mp3_path.exists():
                    # Handle duplicates (no archive path to verify)
                    if file_info.get("skip_reason") == "duplicate":
                        # Phase 1: For duplicates, use safe deletion
                        if self._safe_delete_usb_file(mp3_path):
                            mp3_cleanup_count += 1
                    else:
                        # For successful analyses, verify archive before cleanup
                        if self._cleanup_recorder_file(mp3_path, Path(file_info["archive_path"])):
                            mp3_cleanup_count += 1
                            logger.info(f"🗑️ Cleaned up recorder: {file_info['original_name']}")
                        else:
                            cleanup_failures.append({
                                "file": file_info["original_name"],
                                "type": "mp3",
                                "error": "Recorder cleanup failed"
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

        # Phase 1: Clean up staging folder
        staging_cleaned = self._cleanup_staging_files()
        if staging_cleaned > 0:
            logger.info(f"🧹 Staging cleanup: {staging_cleaned} files removed")

        return mp3_cleanup_count, transcript_cleanup_count, cleanup_failures
    
    def step5_verify_and_archive(self, successful_transcripts: List[Path], successful_analyses: List[Dict]) -> bool:
        """
        Step 5: Verify & Archive (Restructured)
        Step 5a: Verify Notion entries
        Step 5b: Archive successful recordings
        Step 5c: Clean up successful sources
        Step 5d: Finalize session
        """
        logger.info("🔍 Step 5: Verify & Archive (Restructured)")
        logger.info("=" * 50)
        
        try:
            # Step 5a: Verify Notion entries
            verification_summary, verified_entries, failed_entries = self._verify_notion_entries(successful_analyses)
            
            # Check if we have duplicates to clean up even if no Notion entries
            duplicate_cleanup_candidates = self.state["current_session"].get("duplicate_cleanup_candidates", [])
            
            if not verification_summary["verification_passed"] and not duplicate_cleanup_candidates:
                logger.error("❌ No Notion entries verified successfully and no duplicates to clean up - cannot proceed")
                return False
            elif not verification_summary["verification_passed"] and duplicate_cleanup_candidates:
                logger.info("ℹ️ No Notion entries verified, but proceeding with duplicate cleanup")
            
            logger.info(f"✅ Notion verification completed: {verification_summary['success_rate']:.1%} success rate")
            
            # Step 5a.5: Add duplicate cleanup candidates to verified entries
            all_cleanup_candidates = verified_entries + duplicate_cleanup_candidates
            
            logger.info(f"🧹 Cleanup candidates: {len(verified_entries)} successful + {len(duplicate_cleanup_candidates)} duplicates")
            
            # Step 5b: Archive successful recordings
            archived_files, failed_archives = self._archive_successful_recordings(all_cleanup_candidates, self.state["current_session"]["session_id"])
            
            if not archived_files:
                if duplicate_cleanup_candidates:
                    logger.info("ℹ️ No files archived (duplicates skip archiving), but cleanup will proceed")
                else:
                    logger.error("❌ No files were successfully archived")
                    return False
            
            # Step 5c: Clean up successful sources
            mp3_cleanup_count, transcript_cleanup_count, cleanup_failures = self._cleanup_successful_sources(archived_files)
            
            # Step 5d: Update state and finalize session
            self._update_archive_state_with_verification(
                self.state["current_session"]["session_id"],
                archived_files,
                verification_summary,
                failed_entries,
                failed_archives,
                cleanup_failures
            )
            
            self._finalize_session_with_verification(
                self.state["current_session"]["session_id"],
                verification_summary,
                archived_files,
                failed_entries
            )
            
            self._save_state(self.state)
            
            # Final summary
            logger.info(f"")
            logger.info(f"📊 Final Step 5 Summary:")
            logger.info(f"   🔍 Notion Verification: {verification_summary['successful_verifications']}/{verification_summary['total_entries']} successful")
            logger.info(f"   📁 Files Archived: {len(archived_files)}")
            logger.info(f"   🗑️ MP3s Cleaned: {mp3_cleanup_count}")
            logger.info(f"   🗑️ Transcripts Cleaned: {transcript_cleanup_count}")
            logger.info(f"   ❌ Failed Entries: {len(failed_entries)} (kept in recorder)")
            logger.info(f"   📅 Archive Location: {self.archives_folder}")
            logger.info(f"   🧹 Cleanup Date: 7 days from now")
            
            if failed_entries:
                logger.info(f"")
                logger.info(f"⚠️ Failed Notion Entries (kept in recorder):")
                for failure in failed_entries:
                    logger.info(f"   - {failure['transcript']}: {failure['error']}")
            
            if cleanup_failures:
                logger.info(f"")
                logger.info(f"⚠️ Cleanup Failures:")
                for failure in cleanup_failures:
                    logger.info(f"   - {failure['file']} ({failure['type']}): {failure['error']}")
            
            logger.info("✅ Step 5 complete - session finalized and ready for next recording")
            return True
            
        except Exception as e:
            logger.error(f"❌ Step 5 failed: {e}")
            return False
    
    def run(self):
        """Main orchestrator run method"""
        logger.info("🚀 Starting Voice Recording Orchestrator")
        logger.info("=" * 60)

        try:
            # Step 1: Monitor & Detect
            if 'detect' in self.skip_steps:
                logger.info("⏭️ SKIPPED: Step 1 (Monitor & Detect)")
                logger.info("   Using manual file list for testing...")
                # For testing: assume files exist
                unprocessed_files = []
            else:
                self.performance_tracker.start_phase('detect')
                success, unprocessed_files = self.step1_monitor_and_detect()
                self.performance_tracker.end_phase('detect', files_processed=len(unprocessed_files) if unprocessed_files else 0)
                
                if not success:
                    logger.error("❌ Orchestrator failed at Step 1")
                    return False
                
                if not unprocessed_files:
                    logger.info("✅ No new files to process - orchestrator complete")
                    return True
            
            logger.info(f"📋 Ready to process {len(unprocessed_files)} files")
            
            # Step 2: Validate & Prepare
            if 'validate' in self.skip_steps:
                logger.info("⏭️ SKIPPED: Step 2 (Validate & Prepare)")
                valid_files = unprocessed_files
                time_estimate = 0
            else:
                self.performance_tracker.start_phase('validate')
                success, valid_files, time_estimate = self.step2_validate_and_prepare(unprocessed_files)
                self.performance_tracker.end_phase('validate', files_processed=len(valid_files) if valid_files else 0)
                
                if not success:
                    logger.error("❌ Orchestrator failed at Step 2")
                    return False
                
                if not valid_files:
                    logger.info("✅ No valid files to process - orchestrator complete")
                    return True
            
            logger.info(f"📋 Ready to transcribe {len(valid_files)} files")
            
            # Step 3: Transcribe
            if 'transcribe' in self.skip_steps:
                logger.info("⏭️ SKIPPED: Step 3 (Transcribe)")
                logger.info("   Using existing transcripts in transcripts/ folder...")
                # Assume transcripts already exist
                successful_transcripts = list(self.transcripts_folder.glob("*.txt"))
                failed_files = []
                success = True
            else:
                self.performance_tracker.start_phase('transcribe')
                success, successful_transcripts, failed_files = self.step3_transcribe(valid_files, time_estimate)
                self.performance_tracker.end_phase('transcribe',
                    files_processed=len(successful_transcripts) if successful_transcripts else 0,
                    files_failed=len(failed_files) if failed_files else 0)

            if not success:
                logger.error("❌ Orchestrator failed at Step 3")
                return False
            
            if not successful_transcripts:
                logger.info("✅ No successful transcriptions - orchestrator complete")
                return True
            
            logger.info(f"📝 Successfully transcribed {len(successful_transcripts)} files")
            logger.info("🔄 Next steps: Stage, Process, Verify, Archive, Cleanup")
            logger.info("⏸️ Stopping here for Step 3 validation")
            
            # Wait for user signal to proceed (skip if dry-run or auto-continue)
            if not self.dry_run and not self.auto_continue:
                input("\n🎯 Press Enter to proceed to Step 4 (Stage & Process)...")
            elif self.auto_continue:
                logger.info("⚡ AUTO-CONTINUE: Proceeding to Step 4...")
            else:
                logger.info("🔍 DRY RUN: Auto-continuing to Step 4...")
            
            # Step 4: Stage & Process
            if 'process' in self.skip_steps:
                logger.info("⏭️ SKIPPED: Step 4 (Stage & Process)")
                successful_analyses = []
                failed_transcripts = []
            else:
                self.performance_tracker.start_phase('process')
                success, successful_analyses, failed_transcripts = self.step4_stage_and_process(successful_transcripts)
                self.performance_tracker.end_phase('process',
                    files_processed=len(successful_analyses) if successful_analyses else 0,
                    files_failed=len(failed_transcripts) if failed_transcripts else 0)
                
                if not success:
                    logger.error("❌ Orchestrator failed at Step 4")
                    return False
                
                if not successful_analyses:
                    # Check if there are duplicates to clean up
                    duplicate_candidates = self.state["current_session"].get("duplicate_cleanup_candidates", [])
                    if duplicate_candidates:
                        logger.info("✅ No successful analyses, but duplicates will be cleaned up in Step 5")
                    else:
                        logger.info("✅ No successful analyses - orchestrator complete")
                        return True
            
            logger.info(f"🤖 Successfully processed {len(successful_analyses)} transcripts")
            logger.info("🔄 Next steps: Verify, Archive, Cleanup")
            logger.info("⏸️ Stopping here for Step 4 validation")
            
            # Wait for user signal to proceed (skip if dry-run or auto-continue)
            if not self.dry_run and not self.auto_continue and 'archive' not in self.skip_steps:
                input("\n🎯 Press Enter to proceed to Step 5 (Verify & Archive)...")
            elif self.auto_continue:
                logger.info("⚡ AUTO-CONTINUE: Proceeding to Step 5...")
            else:
                logger.info("🔍 DRY RUN/SKIP: Auto-continuing to Step 5...")
            
            # Step 5: Verify & Archive
            if 'archive' in self.skip_steps and 'cleanup' in self.skip_steps:
                logger.info("⏭️ SKIPPED: Step 5 (Verify & Archive & Cleanup)")
                success = True
            else:
                self.performance_tracker.start_phase('archive')
                success = self.step5_verify_and_archive(successful_transcripts, successful_analyses)
                self.performance_tracker.end_phase('archive',
                    files_processed=len(successful_analyses) if successful_analyses else 0)

            if not success:
                logger.warning("⚠️ Step 5 failed - keeping files for manual review")
                # Generate performance report even on partial failure
                logger.info("")
                logger.info("=" * 60)
                report = self.performance_tracker.generate_report()
                print(report)
                return True  # Still consider orchestrator successful

            logger.info("🎉 Orchestrator completed successfully!")
            logger.info("🔄 Ready for next recording session")

            # Phase 1: Generate performance report
            logger.info("")
            logger.info("=" * 60)
            report = self.performance_tracker.generate_report()
            print(report)

            # Save detailed report to file
            report_path = self.project_root / "logs" / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            report_path.parent.mkdir(exist_ok=True)
            self.performance_tracker.save_report(str(report_path))
            logger.info(f"📊 Detailed performance report saved to: {report_path.name}")

            return True
            
        except Exception as e:
            logger.error(f"❌ Orchestrator failed: {e}")
            return False

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Voice Recording Orchestrator - Process Sony recorder files to Notion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full workflow (default behavior)
  python recording_orchestrator.py
  
  # Dry-run mode (no file operations, show what would happen)
  python recording_orchestrator.py --dry-run
  
  # Skip slow transcription step (test with existing transcripts)
  python recording_orchestrator.py --skip-steps transcribe
  
  # Skip archiving and cleanup (keep files for re-testing)
  python recording_orchestrator.py --skip-steps archive,cleanup
  
  # Debug mode with verbose output
  python recording_orchestrator.py --verbose
  
  # Test only detection and validation
  python recording_orchestrator.py --skip-steps transcribe,process,archive,cleanup --dry-run

Available steps to skip:
  detect     - USB file detection
  validate   - File validation  
  transcribe - Whisper transcription (slowest step)
  process    - AI analysis and Notion creation
  archive    - Move files to archives
  cleanup    - Delete source files
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without any file operations (shows what would happen)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable debug-level logging for detailed output'
    )
    
    parser.add_argument(
        '--skip-steps',
        type=str,
        metavar='STEPS',
        help='Comma-separated list of steps to skip (detect,validate,transcribe,process,archive,cleanup)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        metavar='PATH',
        help='Use custom configuration file (not yet implemented - placeholder for future)'
    )
    
    parser.add_argument(
        '--auto-continue',
        action='store_true',
        help='Auto-continue through all steps without manual approval prompts'
    )

    parser.add_argument(
        '--max-files',
        type=int,
        metavar='N',
        help='Limit processing to first N files (useful for testing, Phase 1 optimization)'
    )

    return parser.parse_args()

def main():
    """Main entry point"""
    # Parse command-line arguments
    args = parse_arguments()
    
    # Enable verbose logging if requested
    if args.verbose:
        from core.logging_utils import set_log_level
        set_log_level(logger, "DEBUG")
        logger.debug("Debug logging enabled")
    
    # Parse skip-steps
    skip_steps = []
    if args.skip_steps:
        skip_steps = [step.strip() for step in args.skip_steps.split(',')]
        valid_steps = {'detect', 'validate', 'transcribe', 'process', 'archive', 'cleanup'}
        invalid_steps = [s for s in skip_steps if s not in valid_steps]
        if invalid_steps:
            logger.error(f"Invalid steps: {invalid_steps}")
            logger.error(f"Valid steps: {valid_steps}")
            exit(1)
    
    # Show dry-run banner if enabled
    if args.dry_run:
        logger.info("=" * 60)
        logger.info("🔍 DRY RUN MODE - No file operations will be performed")
        logger.info("   - Files will NOT be copied or moved")
        logger.info("   - Transcripts will NOT be created")
        logger.info("   - Archives will NOT be modified")
        logger.info("   - This shows what WOULD happen in a real run")
        logger.info("=" * 60)
    
    # Create orchestrator with options
    orchestrator = RecordingOrchestrator(
        dry_run=args.dry_run,
        skip_steps=skip_steps,
        auto_continue=args.auto_continue,
        max_files=args.max_files  # Phase 1: File limit for testing
    )
    success = orchestrator.run()
    
    if success:
        if args.dry_run:
            logger.info("\n🔍 Dry-run completed successfully!")
        else:
            logger.info("\n🎉 Orchestrator completed successfully!")
    else:
        logger.error("\n❌ Orchestrator failed!")
        exit(1)

if __name__ == "__main__":
    main()
