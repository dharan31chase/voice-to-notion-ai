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

# Import shared utilities
from core.logging_utils import configure_root_logger, get_logger
from core.config_loader import ConfigLoader

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
    def __init__(self, dry_run=False, skip_steps=None, auto_continue=False):
        self.project_root = Path(__file__).parent.parent
        self.recorder_path = Path("/Volumes/IC RECORDER/REC_FILE/FOLDER01")
        self.transcripts_folder = self.project_root / "transcripts"
        self.archives_folder = self.project_root / "Recording Archives"
        self.failed_folder = self.project_root / "Failed"
        self.state_file = self.project_root / ".cache" / "recording_states.json"
        self.cache_folder = self.project_root / ".cache"
        
        # Load configuration
        self.config = ConfigLoader()
        
        # CLI options
        self.dry_run = dry_run
        self.skip_steps = set(skip_steps) if skip_steps else set()
        self.auto_continue = auto_continue
        
        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No file operations will be performed")
        if self.skip_steps:
            logger.info(f"⏭️ Skipping steps: {', '.join(sorted(self.skip_steps))}")
        
        # Ensure required folders exist
        self._setup_folders()
        
        # Load or create state
        self.state = self._load_state()
        
        # Current session info
        self.current_session_id = None
        self.session_start_time = None
        
        # Initialize Notion client for verification
        self._setup_notion_client()
        
    def _setup_folders(self):
        """Create necessary folders if they don't exist"""
        self.transcripts_folder.mkdir(exist_ok=True)
        self.archives_folder.mkdir(exist_ok=True)
        self.failed_folder.mkdir(exist_ok=True)
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
        """Save state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving state: {e}")
    
    def _check_usb_connection(self) -> bool:
        """Check if USB recorder is connected and accessible"""
        try:
            if not self.recorder_path.exists():
                logger.error(f"❌ USB recorder not found at: {self.recorder_path}")
                return False
            
            # Test if we can read the directory
            os.listdir(self.recorder_path)
            logger.info(f"✅ USB recorder connected: {self.recorder_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cannot access USB recorder: {e}")
            return False
    
    def _scan_mp3_files(self) -> List[Path]:
        """Scan recorder folder for .mp3 files, excluding macOS hidden files"""
        try:
            all_mp3_files = list(self.recorder_path.glob("*.mp3"))
            
            # Filter out macOS hidden files (._* prefix)
            mp3_files = [f for f in all_mp3_files if not f.name.startswith('._')]
            
            hidden_count = len(all_mp3_files) - len(mp3_files)
            if hidden_count > 0:
                logger.debug(f"⏭️ Filtered out {hidden_count} macOS hidden files (._* prefix)")
            
            logger.info(f"📁 Found {len(mp3_files)} .mp3 files in {self.recorder_path}")
            return mp3_files
        except Exception as e:
            logger.error(f"❌ Error scanning for .mp3 files: {e}")
            return []
    
    def _validate_file_integrity(self, file_path: Path) -> Tuple[bool, str]:
        """Validate .mp3 file integrity"""
        try:
            # Check if file exists and is readable
            if not file_path.exists():
                return False, "File does not exist"
            
            # Check file size (should be > 0 bytes)
            file_size = file_path.stat().st_size
            if file_size == 0:
                return False, "File is empty (0 bytes)"
            
            # Check if file is readable
            with open(file_path, 'rb') as f:
                f.read(1024)  # Read first 1KB to test access
                
            # Basic .mp3 validation (check file extension and size)
            if file_path.suffix.lower() != '.mp3':
                return False, "File is not .mp3 format"
            
            # Log file info
            logger.debug(f"✅ File validated: {file_path.name} ({file_size} bytes)")
            return True, "OK"
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID based on current timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}"
    
    def _get_unprocessed_files(self, mp3_files: List[Path]) -> List[Path]:
        """Identify files that haven't been processed yet"""
        processed_files = set()
        
        # Get list of already processed files from state
        if self.state.get("current_session") and self.state["current_session"].get("recordings_processed"):
            processed_files.update(self.state["current_session"]["recordings_processed"])
        
        # Add files from previous sessions
        for session in self.state.get("previous_sessions", []):
            if session.get("recordings_processed"):
                processed_files.update(session["recordings_processed"])
        
        # Filter out already processed files
        unprocessed = [f for f in mp3_files if f.name not in processed_files]
        
        logger.info(f"🔍 Already processed: {len(processed_files)}")
        logger.info(f"📋 New files to process: {len(unprocessed)}")
        
        return unprocessed
    
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
                "processing_complete": False
            }
            
            # Log discovery summary
            logger.info(f"🆔 Session ID: {self.current_session_id}")
            logger.info(f"📊 Valid files found: {len(valid_files)}")
            logger.info(f"📋 New files to process: {len(unprocessed_files)}")
            logger.info(f"⚠️ Invalid files: {len(invalid_files)}")
            
            if invalid_files:
                for file_path, message in invalid_files:
                    logger.warning(f"   - {file_path.name}: {message}")
            
            # Save state
            self._save_state(self.state)
            
            logger.info("✅ Step 1 complete - ready for transcription")
            return True, unprocessed_files
            
        except Exception as e:
            logger.error(f"❌ Step 1 failed: {e}")
            return False, []
    
    def _extract_file_metadata(self, file_path: Path) -> Dict:
        """Extract metadata from .mp3 file"""
        try:
            stat = file_path.stat()
            file_size_mb = stat.st_size / (1024 * 1024)  # Convert to MB
            
            # Estimate duration based on file size (rough approximation)
            # Assuming ~1MB per minute for typical voice recording
            estimated_minutes = int(file_size_mb)
            
            return {
                "name": file_path.name,
                "size_mb": round(file_size_mb, 1),
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "estimated_minutes": estimated_minutes,
                "path": str(file_path)
            }
        except Exception as e:
            logger.error(f"❌ Error extracting metadata for {file_path.name}: {e}")
            return {
                "name": file_path.name,
                "size_mb": 0,
                "created_time": None,
                "modified_time": None,
                "estimated_minutes": 0,
                "path": str(file_path),
                "error": str(e)
            }
    
    def _check_system_resources(self) -> Tuple[bool, Dict]:
        """Check if system has sufficient resources for processing"""
        try:
            import shutil
            
            # Check disk space
            total, used, free = shutil.disk_usage(self.project_root)
            free_gb = free / (1024**3)
            
            # Check available memory (rough estimate)
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            # Requirements: 500MB free disk, 1GB available memory
            disk_ok = free_gb > 0.5
            memory_ok = available_gb > 1.0
            
            resource_status = {
                "disk_free_gb": round(free_gb, 2),
                "disk_ok": disk_ok,
                "memory_available_gb": round(available_gb, 2),
                "memory_ok": memory_ok,
                "all_ok": disk_ok and memory_ok
            }
            
            if not resource_status["all_ok"]:
                logger.warning(f"⚠️ Resource check failed:")
                if not disk_ok:
                    logger.warning(f"   - Disk space: {free_gb:.2f}GB (need >0.5GB)")
                if not memory_ok:
                    logger.warning(f"   - Memory: {available_gb:.2f}GB (need >1GB)")
            
            return resource_status["all_ok"], resource_status
            
        except ImportError:
            # If psutil not available, just check disk space
            try:
                import shutil
                total, used, free = shutil.disk_usage(self.project_root)
                free_gb = free / (1024**3)
                disk_ok = free_gb > 0.5
                
                resource_status = {
                    "disk_free_gb": round(free_gb, 2),
                    "disk_ok": disk_ok,
                    "memory_available_gb": "Unknown",
                    "memory_ok": True,  # Assume OK if we can't check
                    "all_ok": disk_ok
                }
                
                if not disk_ok:
                    logger.warning(f"⚠️ Disk space low: {free_gb:.2f}GB (need >0.5GB)")
                
                return disk_ok, resource_status
                
            except Exception as e:
                logger.error(f"❌ Error checking system resources: {e}")
                return False, {"error": str(e)}
    
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
        """Check if Whisper is installed and accessible"""
        try:
            result = subprocess.run(['whisper', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ Whisper CLI found and accessible")
                return True
            else:
                logger.error("❌ Whisper CLI not working properly")
                return False
        except FileNotFoundError:
            logger.error("❌ Whisper CLI not found. Please install: pip install openai-whisper")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking Whisper: {e}")
            return False
    
    def _check_disk_space(self, required_mb: float) -> bool:
        """Check if sufficient disk space is available"""
        try:
            total, used, free = shutil.disk_usage(self.project_root)
            free_mb = free / (1024 * 1024)
            
            if free_mb < required_mb:
                logger.error(f"❌ Insufficient disk space: {free_mb:.1f}MB available, {required_mb:.1f}MB required")
                return False
            
            logger.info(f"✅ Disk space OK: {free_mb:.1f}MB available, {required_mb:.1f}MB required")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking disk space: {e}")
            return False
    
    def _should_transcribe_audio(self, audio_file: Path) -> bool:
        """Check if we should transcribe this audio file (prevents duplicates)"""
        try:
            # Ensure we have a Path object
            if isinstance(audio_file, str):
                audio_file = Path(audio_file)
            
            # Check if transcript already exists
            transcript_file = self.transcripts_folder / f"{audio_file.stem}.txt"
            
            if transcript_file.exists():
                # Check if transcript is recent (within last hour) and has content
                transcript_age = time.time() - transcript_file.stat().st_mtime
                if transcript_age < 3600:  # 1 hour
                    with open(transcript_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if len(content) > 10:  # Has meaningful content
                        logger.info(f"ℹ️ Transcript already exists: {transcript_file.name} (age: {transcript_age/60:.1f} min)")
                        return False
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking transcript existence for {audio_file}: {e}")
            return True  # Default to transcribing if check fails
    
    def _monitor_cpu_usage(self) -> float:
        """Monitor current CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            logger.warning("⚠️ psutil not available, skipping CPU monitoring")
            return 0.0
        except Exception as e:
            logger.warning(f"⚠️ CPU monitoring error: {e}")
            return 0.0
    
    def _transcribe_single_file(self, file_path: Path, batch_num: int, file_num: int) -> Tuple[bool, str, str]:
        """Transcribe a single .mp3 file using Whisper"""
        try:
            # Generate output filename
            output_name = file_path.stem + ".txt"
            output_path = self.transcripts_folder / output_name
            
            # Whisper command
            # Get Whisper settings from config
            whisper_model = self.config.get("whisper.model", "small")
            whisper_language = self.config.get("whisper.language", "en")
            whisper_output_format = self.config.get("whisper.output_format", "txt")
            
            cmd = [
                'whisper',
                str(file_path),
                '--model', whisper_model,
                '--language', whisper_language,
                '--output_dir', str(self.transcripts_folder),
                '--output_format', whisper_output_format
            ]
            
            logger.info(f"🎙️ Transcribing {file_path.name} (Batch {batch_num}, File {file_num})")
            
            # Run Whisper
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and output_path.exists():
                # Validate transcript
                with open(output_path, 'r', encoding='utf-8') as f:
                    transcript_content = f.read().strip()
                
                if len(transcript_content) > 10:  # Basic validation
                    logger.info(f"✅ Transcribed {file_path.name} → {output_name}")
                    return True, str(output_path), transcript_content
                else:
                    logger.warning(f"⚠️ Transcript too short: {file_path.name}")
                    return False, "Transcript too short", transcript_content
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                logger.error(f"❌ Transcription failed: {file_path.name} - {error_msg}")
                return False, error_msg, ""
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Transcription timeout: {file_path.name}")
            return False, "Transcription timeout", ""
        except Exception as e:
            logger.error(f"❌ Transcription error: {file_path.name} - {e}")
            return False, str(e), ""
    
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
        Step 3: Transcribe
        Converts .mp3 files to text using Whisper with batch processing
        """
        logger.info("🎙️ Step 3: Transcribe")
        logger.info("=" * 50)
        
        try:
            if not valid_files:
                logger.warning("⚠️ No files to transcribe")
                return True, [], []
            
            # Check Whisper installation
            if not self._check_whisper_installation():
                return False, [], []
            
            # Check disk space (100MB requirement)
            required_space = time_estimate.get("total_size_mb", 0) + 100  # Add 100MB buffer
            if not self._check_disk_space(required_space):
                return False, [], []
            
            # Get processing plan from state
            processing_plan = self.state["current_session"].get("processing_plan", {})
            batch_size = processing_plan.get("batch_size", 4)
            
            # Check for existing transcripts before starting
            existing_transcripts = []
            files_needing_transcription = []
            for file_path in valid_files:
                if self._should_transcribe_audio(file_path):
                    files_needing_transcription.append(file_path)
                else:
                    transcript_path = self.transcripts_folder / f"{file_path.stem}.txt"
                    if transcript_path.exists():
                        existing_transcripts.append(transcript_path)
            
            if existing_transcripts:
                logger.info(f"ℹ️ Found {len(existing_transcripts)} existing transcripts, {len(files_needing_transcription)} files need transcription")
            
            # Create batches
            batches = self._create_processing_batches(valid_files, batch_size)
            
            successful_transcripts = []
            failed_files = []
            
            # Get Whisper model from config for logging
            whisper_model = self.config.get("whisper.model", "small")
            whisper_language = self.config.get("whisper.language", "en")
            
            logger.info(f"🤖 Initializing Whisper ({whisper_model} model, {whisper_language.upper()})")
            logger.info(f"📊 Processing {len(valid_files)} files in {len(batches)} batches")
            
            # Process each batch
            for batch_num, batch in enumerate(batches, 1):
                logger.info(f"")
                logger.info(f" Batch {batch_num}/{len(batches)} ({len(batch)} files) - Processing...")
                
                batch_start_time = time.time()
                batch_successes = []
                batch_failures = []
                
                # Process files in parallel within batch
                with ThreadPoolExecutor(max_workers=4) as executor:
                    # Filter out files that already have transcripts
                    files_to_transcribe = []
                    for file_path in batch:
                        if self._should_transcribe_audio(file_path):
                            files_to_transcribe.append(file_path)
                        else:
                            # Add existing transcript to successful list
                            transcript_path = self.transcripts_folder / f"{file_path.stem}.txt"
                            if transcript_path.exists():
                                successful_transcripts.append(transcript_path)
                                batch_successes.append(file_path)
                                # Update state
                                self.state["current_session"]["transcripts_created"].append(transcript_path.name)
                    
                    if not files_to_transcribe:
                        logger.info(f"   ℹ️ All files in batch {batch_num} already have transcripts")
                        continue
                    
                    # Submit transcription tasks only for files that need transcription
                    future_to_file = {
                        executor.submit(self._transcribe_single_file, file_path, batch_num, i+1): file_path
                        for i, file_path in enumerate(files_to_transcribe)
                    }
                    
                    # Process completed transcriptions
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]
                        try:
                            success, error_reason, transcript_content = future.result()
                            
                            if success:
                                # Find the created transcript file
                                transcript_name = file_path.stem + ".txt"
                                transcript_path = self.transcripts_folder / transcript_name
                                
                                if transcript_path.exists():
                                    successful_transcripts.append(transcript_path)
                                    batch_successes.append(file_path)
                                    
                                    # Update state
                                    self.state["current_session"]["transcripts_created"].append(transcript_name)
                                else:
                                    logger.error(f"❌ Transcript file not found: {transcript_name}")
                                    failed_files.append(file_path)
                                    batch_failures.append(file_path)
                            else:
                                # Retry once
                                logger.info(f"🔄 Retrying transcription: {file_path.name}")
                                retry_success, retry_error, retry_content = self._transcribe_single_file(
                                    file_path, batch_num, 0
                                )
                                
                                if retry_success:
                                    transcript_name = file_path.stem + ".txt"
                                    transcript_path = self.transcripts_folder / transcript_name
                                    if transcript_path.exists():
                                        successful_transcripts.append(transcript_path)
                                        batch_successes.append(file_path)
                                        self.state["current_session"]["transcripts_created"].append(transcript_name)
                                    else:
                                        failed_files.append(file_path)
                                        batch_failures.append(file_path)
                                else:
                                    failed_files.append(file_path)
                                    batch_failures.append(file_path)
                                    
                                    # Move failed file to failed folder
                                    self._move_failed_file(file_path, retry_error, "recording")
                                    
                                    # Update state
                                    self.state["current_session"]["failed_transcriptions"].append(file_path.name)
                            
                            # Monitor CPU usage
                            cpu_usage = self._monitor_cpu_usage()
                            if cpu_usage > 75:
                                logger.warning(f"⚠️ High CPU usage: {cpu_usage:.1f}% - waiting 2 seconds")
                                time.sleep(2)
                                
                        except Exception as e:
                            logger.error(f"❌ Error processing {file_path.name}: {e}")
                            failed_files.append(file_path)
                            batch_failures.append(file_path)
                            self._move_failed_file(file_path, str(e), "recording")
                            self.state["current_session"]["failed_transcriptions"].append(file_path.name)
                
                # Report batch completion
                batch_time = time.time() - batch_start_time
                logger.info(f"   ✅ Successful: {len(batch_successes)} files")
                if batch_failures:
                    logger.info(f"   ❌ Failed: {len(batch_failures)} files")
                logger.info(f"   ⏱️ Batch {batch_num} complete in {batch_time:.0f}s")
            
            # Final summary
            logger.info(f"")
            logger.info(f"📊 Transcription Summary:")
            logger.info(f"   ✅ Successful: {len(successful_transcripts)}/{len(valid_files)} files")
            logger.info(f"   ❌ Failed: {len(failed_files)} files")
            if existing_transcripts:
                logger.info(f"   ℹ️ Reused existing: {len(existing_transcripts)} transcripts")
            logger.info(f"   📝 Transcripts Created: {len(successful_transcripts)}")
            logger.info(f"   📁 Failed Files: {len(failed_files)}")
            
            # Update state
            self.state["current_session"]["transcription_complete"] = True
            self.state["current_session"]["transcription_summary"] = {
                "total_files": len(valid_files),
                "successful": len(successful_transcripts),
                "failed": len(failed_files),
                "success_rate": len(successful_transcripts) / len(valid_files)
            }
            
            # Save state
            self._save_state(self.state)
            
            logger.info("✅ Step 3 complete - ready for staging")
            return True, successful_transcripts, failed_files
            
        except Exception as e:
            logger.error(f"❌ Step 3 failed: {e}")
            return False, [], []
    
    def _import_process_transcripts(self):
        """Import the process_transcripts module dynamically"""
        try:
            # Add the scripts directory to Python path
            scripts_dir = self.project_root / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            
            # Import the process_transcript_file function
            from process_transcripts import process_transcript_file
            return process_transcript_file
            
        except ImportError as e:
            logger.error(f"❌ Failed to import process_transcripts: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error importing process_transcripts: {e}")
            return None
    
    def _validate_transcript_for_processing(self, transcript_path: Path) -> bool:
        """Validate that a transcript is ready for AI processing"""
        try:
            if not transcript_path.exists():
                logger.warning(f"⚠️ Transcript file not found: {transcript_path}")
                return False
            
            # Check file size
            file_size = transcript_path.stat().st_size
            if file_size < 10:  # Less than 10 bytes
                logger.warning(f"⚠️ Transcript too small: {transcript_path} ({file_size} bytes)")
                return False
            
            # Check if already processed
            processed_file = self.project_root / "processed" / f"{transcript_path.stem}_processed.json"
            if processed_file.exists():
                logger.info(f"ℹ️ Transcript already processed: {transcript_path.stem}")
                return False
            
            # Read and validate content
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if len(content) < 10:
                logger.warning(f"⚠️ Transcript content too short: {transcript_path}")
                return False
            
            logger.info(f"✅ Transcript validated: {transcript_path.name} ({file_size} bytes, {len(content)} chars)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating transcript {transcript_path}: {e}")
            return False
    
    def _get_transcript_processing_status(self, transcript_path: Path) -> str:
        """Get detailed processing status for a transcript
        
        Returns:
            "valid" - Ready for AI processing
            "duplicate" - Already processed, skip AI but cleanup MP3
            "invalid" - File problems, move to failed folder
            "error" - Unexpected error during validation
        """
        try:
            if not transcript_path.exists():
                logger.warning(f"⚠️ Transcript file not found: {transcript_path}")
                return "invalid"
            
            # Check file size
            file_size = transcript_path.stat().st_size
            if file_size < 10:  # Less than 10 bytes
                logger.warning(f"⚠️ Transcript too small: {transcript_path} ({file_size} bytes)")
                return "invalid"
            
            # Check if already processed
            processed_file = self.project_root / "processed" / f"{transcript_path.stem}_processed.json"
            if processed_file.exists():
                logger.info(f"ℹ️ Transcript already processed: {transcript_path.stem}")
                return "duplicate"
            
            # Read and validate content
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if len(content) < 10:
                logger.warning(f"⚠️ Transcript content too short: {transcript_path}")
                return "invalid"
            
            logger.info(f"✅ Transcript validated: {transcript_path.name} ({file_size} bytes, {len(content)} chars)")
            return "valid"
            
        except Exception as e:
            logger.error(f"❌ Error validating transcript {transcript_path}: {e}")
            return "error"
    
    def _process_single_transcript(self, transcript_path: Path, process_function) -> Tuple[bool, Dict, str]:
        """Process a single transcript using the existing AI system"""
        try:
            logger.info(f"🤖 Processing transcript: {transcript_path.name}")
            
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
            
            logger.info(f"✅ Successfully processed: {transcript_path.name}")
            return True, processed_data, ""
            
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, {}, error_msg
    
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
        Step 4: Stage & Process
        Integrates transcripts with existing AI transcription system
        """
        logger.info("🚀 Step 4: Stage & Process")
        logger.info("=" * 50)
        
        try:
            if not successful_transcripts:
                logger.warning("⚠️ No transcripts to process")
                return True, [], []
            
            # Import the processing function
            process_function = self._import_process_transcripts()
            if not process_function:
                logger.error("❌ Failed to import process_transcripts module")
                return False, [], []
            
            logger.info(f"✅ Successfully imported AI processing system")
            logger.info(f"📊 Processing {len(successful_transcripts)} transcripts")
            
            # Validate transcripts before processing
            valid_transcripts = []
            duplicate_transcripts = []
            invalid_transcripts = []
            
            for transcript in successful_transcripts:
                status = self._get_transcript_processing_status(transcript)
                
                if status == "valid":
                    valid_transcripts.append(transcript)
                elif status == "duplicate":
                    duplicate_transcripts.append(transcript)
                else:  # status == "invalid" or "error"
                    invalid_transcripts.append(transcript)
            
            if invalid_transcripts:
                logger.warning(f"⚠️ {len(invalid_transcripts)} transcripts failed validation")
                for transcript in invalid_transcripts:
                    self._move_failed_transcript(transcript, "Failed validation")
            
            if duplicate_transcripts:
                logger.info(f"ℹ️ {len(duplicate_transcripts)} transcripts are duplicates (already processed)")
                # Store duplicates in state for Step 5 cleanup
                for transcript in duplicate_transcripts:
                    self.state["current_session"]["duplicate_skipped"] = self.state["current_session"].get("duplicate_skipped", [])
                    self.state["current_session"]["duplicate_skipped"].append(transcript.name)
                    
                    # Add to cleanup candidates for archiving and MP3 cleanup
                    duplicate_cleanup_candidate = {
                        "transcript_name": transcript.name,
                        "original_name": transcript.stem + ".mp3",
                        "skip_reason": "duplicate",
                        "notion_entry_id": None  # No new Notion entry for duplicates
                    }
                    self.state["current_session"]["duplicate_cleanup_candidates"] = self.state["current_session"].get("duplicate_cleanup_candidates", [])
                    self.state["current_session"]["duplicate_cleanup_candidates"].append(duplicate_cleanup_candidate)
                    logger.info(f"📋 Added duplicate to cleanup candidates: {transcript.name}")
            
            if not valid_transcripts:
                if duplicate_transcripts:
                    logger.warning("⚠️ No valid transcripts to process, but duplicates will be cleaned up in Step 5")
                else:
                    logger.warning("⚠️ No valid transcripts to process")
                    return True, [], []
            
            logger.info(f"🎯 Processing {len(valid_transcripts)} valid transcripts")
            
            # Process transcripts sequentially (your system handles batching internally)
            successful_analyses = []
            failed_transcripts = []
            
            for i, transcript in enumerate(valid_transcripts, 1):
                logger.info(f"")
                logger.info(f" Processing {i}/{len(valid_transcripts)}: {transcript.name}")
                
                success, result_data, error_reason = self._process_single_transcript(transcript, process_function)
                
                if success:
                    # Extract notion_entry_id from the result data
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
                    self.state["current_session"]["ai_processing_success"].append(transcript.name)
                    
                    # Check if Notion entry was created (based on processed file content)
                    if notion_entry_id:
                        self.state["current_session"]["notion_success"].append(transcript.name)
                        logger.info(f"   ✅ AI Analysis: Success")
                        logger.info(f"   ✅ Notion Entry: Created (ID: {notion_entry_id[:8]}...)")
                    else:
                        logger.warning(f"   ⚠️ AI Analysis: Success but no Notion entry ID found")
                        
                else:
                    failed_transcripts.append(transcript)
                    self._move_failed_transcript(transcript, error_reason)
                    self.state["current_session"]["ai_processing_failed"].append(transcript.name)
                    logger.error(f"   ❌ Failed: {error_reason}")
            
            # Final summary
            logger.info(f"")
            logger.info(f"📊 Processing Summary:")
            logger.info(f"   ✅ Successful: {len(successful_analyses)}/{len(valid_transcripts)} transcripts")
            logger.info(f"   ⏭️ Duplicates: {len(duplicate_transcripts)} transcripts")
            logger.info(f"   ❌ Failed: {len(failed_transcripts)} transcripts")
            logger.info(f"   🤖 AI Analysis: {len(successful_analyses)} successful")
            logger.info(f"   📝 Notion Entries: {len([a for a in successful_analyses if a['result'].get('analysis') or a['result'].get('analyses')])} created")
            logger.info(f"   🧹 Cleanup Candidates: {len(self.state['current_session'].get('duplicate_cleanup_candidates', []))} duplicates")
            
            # Update state
            self.state["current_session"]["processing_complete"] = True
            self.state["current_session"]["processing_summary"] = {
                "total_transcripts": len(valid_transcripts),
                "successful_analyses": len(successful_analyses),
                "duplicate_transcripts": len(duplicate_transcripts),
                "failed_transcripts": len(failed_transcripts),
                "notion_entries_created": len([a for a in successful_analyses if a['result'].get('analysis') or a['result'].get('analyses')]),
                "success_rate": len(successful_analyses) / len(valid_transcripts) if valid_transcripts else 0
            }
            
            # Save state
            self._save_state(self.state)
            
            logger.info("✅ Step 4 complete - ready for verification")
            return True, successful_analyses, failed_transcripts
            
        except Exception as e:
            logger.error(f"❌ Step 4 failed: {e}")
            return False, [], []
    
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
        """Check if USB recorder file has proper permissions for reading"""
        try:
            if not mp3_file.exists():
                logger.error(f"❌ USB file not found: {mp3_file}")
                return False
            
            # Check if file is readable
            if not os.access(mp3_file, os.R_OK):
                logger.warning(f"⚠️ USB file not readable: {mp3_file}")
                logger.info(f"💡 File permissions: {oct(mp3_file.stat().st_mode)[-3:]}")
                logger.info(f"💡 Try: chmod 644 '{mp3_file}'")
                return False
            
            # Check file size
            file_size = mp3_file.stat().st_size
            if file_size == 0:
                logger.error(f"❌ USB file is empty: {mp3_file}")
                return False
            
            logger.info(f"✅ USB file permissions OK: {mp3_file.name} ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking USB file permissions: {e}")
            return False
    
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
        """Safely delete .mp3 file from recorder after successful archiving"""
        try:
            # Double-check: archive must exist and have correct size
            if not archive_path.exists():
                logger.error(f"❌ Cannot delete {mp3_file.name}: Archive file missing")
                return False
            
            # Verify archive integrity
            if mp3_file.stat().st_size != archive_path.stat().st_size:
                logger.error(f"❌ Cannot delete {mp3_file.name}: Archive size mismatch")
                return False
            
            # Safe to delete from recorder
            mp3_file.unlink()
            logger.info(f"🗑️ Cleaned up recorder: {mp3_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up {mp3_file.name}: {e}")
            return False
    
    def _update_archive_state_with_verification(self, session_id: str, archived_files: List[Dict], verification_summary: Dict, failed_entries: List[Dict], failed_archives: List[Dict], cleanup_failures: List[Dict]):
        """Update state with archive information and verification status"""
        try:
            # Add archive info to current session
            self.state["current_session"]["archive_complete"] = True
            self.state["current_session"]["archive_folder"] = str(self.archives_folder)
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
    
    def _finalize_session_with_verification(self, session_id: str, verification_summary: Dict, archived_files: List[Dict], failed_entries: List[Dict]):
        """Move current session to previous sessions with verification details"""
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
    
    def _finalize_session(self, session_id: str):
        """Move current session to previous sessions and prepare for cleanup"""
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
    
    def _verify_notion_entry_exists(self, notion_entry_id: str) -> Tuple[bool, str]:
        """
        Verify that a Notion entry exists via API call
        Returns: (success, error_message)
        """
        if not self.notion_client:
            return False, "Notion client not available"
        
        max_retries = 3
        base_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add delay between retries (rate limiting)
                if attempt > 0:
                    time.sleep(base_delay * (2 ** (attempt - 1)))
                
                # Query the specific page with timeout
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("API call timed out")
                
                # Set 10 second timeout
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(10)
                
                try:
                    page = self.notion_client.pages.retrieve(notion_entry_id)
                    signal.alarm(0)  # Cancel timeout
                    
                    if page and page.get("id"):
                        return True, ""
                    else:
                        return False, "Page not found or invalid response"
                        
                except TimeoutError:
                    signal.alarm(0)
                    return False, "API call timed out after 10 seconds"
                    
            except Exception as e:
                error_msg = str(e)
                if "rate_limited" in error_msg.lower() or "429" in error_msg:
                    # Rate limited - wait longer
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"⚠️ Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                elif "not_found" in error_msg.lower() or "404" in error_msg:
                    return False, "Page not found"
                elif attempt == max_retries - 1:
                    return False, f"API error after {max_retries} attempts: {error_msg}"
                else:
                    logger.warning(f"⚠️ API error on attempt {attempt + 1}: {error_msg}")
                    continue
        
        return False, f"Failed after {max_retries} attempts"
    
    def _verify_notion_entries(self, successful_analyses: List[Dict]) -> Tuple[Dict, List[Dict], List[Dict]]:
        """
        Step 5a: Verify Notion entries exist and are valid
        Returns: verification_summary, verified_entries, failed_entries
        """
        logger.info("🔍 Step 5a: Verifying Notion entries...")
        
        verified_entries = []
        failed_entries = []
        
        for analysis in successful_analyses:
            try:
                # Check if analysis has Notion entry ID
                if "notion_entry_id" not in analysis:
                    failed_entries.append({
                        "transcript": analysis.get("transcript_name", "unknown"),
                        "error": "Missing Notion entry ID from analysis",
                        "analysis": analysis
                    })
                    continue
                
                # Basic validation: check if we have required fields
                if not analysis.get("title") or not analysis.get("content"):
                    failed_entries.append({
                        "transcript": analysis.get("transcript_name", "unknown"),
                        "error": "Missing required fields (title or content)",
                        "analysis": analysis
                    })
                    continue
                
                # Verify Notion entry exists via API
                notion_entry_id = analysis.get("notion_entry_id")
                if notion_entry_id:
                    success, error = self._verify_notion_entry_exists(notion_entry_id)
                    if not success:
                        failed_entries.append({
                            "transcript": analysis.get("transcript_name", "unknown"),
                            "error": f"Notion verification failed: {error}",
                            "analysis": analysis,
                            "notion_entry_id": notion_entry_id
                        })
                        continue
                else:
                    failed_entries.append({
                        "transcript": analysis.get("transcript_name", "unknown"),
                        "error": "Missing Notion entry ID from analysis",
                        "analysis": analysis
                    })
                    continue
                
                verified_entries.append(analysis)
                logger.info(f"✅ Verified Notion entry for: {analysis.get('transcript_name', 'unknown')}")
                
            except Exception as e:
                failed_entries.append({
                    "transcript": analysis.get("transcript_name", "unknown"),
                    "error": f"Verification error: {str(e)}",
                    "analysis": analysis
                })
                logger.error(f"❌ Failed to verify entry: {e}")
        
        # Calculate verification summary
        total_entries = len(successful_analyses)
        successful_verifications = len(verified_entries)
        failed_verifications = len(failed_entries)
        success_rate = successful_verifications / total_entries if total_entries > 0 else 0
        
        verification_summary = {
            "total_entries": total_entries,
            "successful_verifications": successful_verifications,
            "failed_verifications": failed_verifications,
            "success_rate": success_rate,
            "verification_passed": success_rate > 0  # Allow partial success
        }
        
        logger.info(f"📊 Notion Verification Summary:")
        logger.info(f"   ✅ Successful: {successful_verifications}/{total_entries}")
        logger.info(f"   ❌ Failed: {failed_verifications}/{total_entries}")
        logger.info(f"   📈 Success Rate: {success_rate:.1%}")
        
        return verification_summary, verified_entries, failed_entries
    
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
                        # For duplicates, just delete the MP3 (archive already exists)
                        mp3_path.unlink()
                        mp3_cleanup_count += 1
                        logger.info(f"🗑️ Cleaned up duplicate recorder: {file_info['original_name']}")
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
                success, unprocessed_files = self.step1_monitor_and_detect()
                
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
                success, valid_files, time_estimate = self.step2_validate_and_prepare(unprocessed_files)
                
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
            else:
                success, successful_transcripts, failed_files = self.step3_transcribe(valid_files, time_estimate)
            
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
                success, successful_analyses, failed_transcripts = self.step4_stage_and_process(successful_transcripts)
                
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
                success = self.step5_verify_and_archive(successful_transcripts, successful_analyses)
            
            if not success:
                logger.warning("⚠️ Step 5 failed - keeping files for manual review")
                return True  # Still consider orchestrator successful
            
            logger.info("🎉 Orchestrator completed successfully!")
            logger.info("🔄 Ready for next recording session")
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
        auto_continue=args.auto_continue
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
