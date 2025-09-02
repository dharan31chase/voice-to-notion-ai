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
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recording_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RecordingOrchestrator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.recorder_path = Path("/Volumes/IC RECORDER/REC_FILE/FOLDER01")
        self.transcripts_folder = self.project_root / "transcripts"
        self.archives_folder = self.project_root / "Recording Archives"
        self.failed_folder = self.project_root / "Failed"
        self.state_file = self.project_root / ".cache" / "recording_states.json"
        self.cache_folder = self.project_root / ".cache"
        
        # Ensure required folders exist
        self._setup_folders()
        
        # Load or create state
        self.state = self._load_state()
        
        # Current session info
        self.current_session_id = None
        self.session_start_time = None
        
    def _setup_folders(self):
        """Create necessary folders if they don't exist"""
        self.transcripts_folder.mkdir(exist_ok=True)
        self.archives_folder.mkdir(exist_ok=True)
        self.failed_folder.mkdir(exist_ok=True)
        (self.failed_folder / "failed_recordings").mkdir(exist_ok=True)
        (self.failed_folder / "failed_transcripts").mkdir(exist_ok=True)
        (self.failed_folder / "failure_logs").mkdir(exist_ok=True)
        self.cache_folder.mkdir(exist_ok=True)
        
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
        """Scan recorder folder for .mp3 files"""
        try:
            mp3_files = list(self.recorder_path.glob("*.mp3"))
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
            
            for file_path in unprocessed_files:
                metadata = self._extract_file_metadata(file_path)
                if "error" not in metadata:
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
            cmd = [
                'whisper',
                str(file_path),
                '--model', 'small',
                '--language', 'en',
                '--output_dir', str(self.transcripts_folder),
                '--output_format', 'txt'
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
            
            # Create batches
            batches = self._create_processing_batches(valid_files, batch_size)
            
            successful_transcripts = []
            failed_files = []
            
            logger.info(f"🤖 Initializing Whisper (small model, English)")
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
                    # Submit transcription tasks
                    future_to_file = {
                        executor.submit(self._transcribe_single_file, file_path, batch_num, i+1): file_path
                        for i, file_path in enumerate(batch)
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
                            if cpu_usage > 50:
                                logger.warning(f"⚠️ High CPU usage: {cpu_usage:.1f}% - waiting 10 seconds")
                                time.sleep(10)
                                
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
            invalid_transcripts = []
            
            for transcript in successful_transcripts:
                if self._validate_transcript_for_processing(transcript):
                    valid_transcripts.append(transcript)
                else:
                    invalid_transcripts.append(transcript)
            
            if invalid_transcripts:
                logger.warning(f"⚠️ {len(invalid_transcripts)} transcripts failed validation")
                for transcript in invalid_transcripts:
                    self._move_failed_transcript(transcript, "Failed validation")
            
            if not valid_transcripts:
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
                    successful_analyses.append({
                        "transcript": transcript.name,
                        "result": result_data,
                        "processed_file": f"{transcript.stem}_processed.json"
                    })
                    
                    # Update state
                    self.state["current_session"]["ai_processing_success"].append(transcript.name)
                    
                    # Check if Notion entry was created (based on processed file content)
                    if result_data.get("analysis") or result_data.get("analyses"):
                        self.state["current_session"]["notion_success"].append(transcript.name)
                        logger.info(f"   ✅ AI Analysis: Success")
                        logger.info(f"   ✅ Notion Entry: Created")
                    else:
                        logger.warning(f"   ⚠️ AI Analysis: Success but no Notion entry")
                        
                else:
                    failed_transcripts.append(transcript)
                    self._move_failed_transcript(transcript, error_reason)
                    self.state["current_session"]["ai_processing_failed"].append(transcript.name)
                    logger.error(f"   ❌ Failed: {error_reason}")
            
            # Final summary
            logger.info(f"")
            logger.info(f"📊 Processing Summary:")
            logger.info(f"   ✅ Successful: {len(successful_analyses)}/{len(valid_transcripts)} transcripts")
            logger.info(f"   ❌ Failed: {len(failed_transcripts)} transcripts")
            logger.info(f"   🤖 AI Analysis: {len(successful_analyses)} successful")
            logger.info(f"   📝 Notion Entries: {len([a for a in successful_analyses if a['result'].get('analysis') or a['result'].get('analyses')])} created")
            
            # Update state
            self.state["current_session"]["processing_complete"] = True
            self.state["current_session"]["processing_summary"] = {
                "total_transcripts": len(valid_transcripts),
                "successful_analyses": len(successful_analyses),
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
    
    def _archive_single_recording(self, mp3_file: Path, archive_folder: Path, session_id: str) -> Tuple[bool, Path, str]:
        """Archive a single .mp3 file with session ID"""
        try:
            # Create archive filename with session ID
            archive_name = f"{mp3_file.stem}_{session_id}.mp3"
            archive_path = archive_folder / archive_name
            
            # Copy file to archive (safer than move during testing)
            shutil.copy2(str(mp3_file), str(archive_path))
            
            # Verify archive was created successfully
            if not archive_path.exists():
                return False, archive_path, "Archive file not created"
            
            # Verify file integrity (size should match)
            if mp3_file.stat().st_size != archive_path.stat().st_size:
                return False, archive_path, "File size mismatch after archiving"
            
            logger.info(f"📁 Archived: {mp3_file.name} → {archive_name}")
            return True, archive_path, ""
            
        except Exception as e:
            error_msg = f"Archive error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return False, archive_path, error_msg
    
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
    
    def _update_archive_state(self, session_id: str, archived_files: List[Dict], archive_folder: Path):
        """Update state with archive information"""
        try:
            # Add archive info to current session
            self.state["current_session"]["archive_complete"] = True
            self.state["current_session"]["archive_folder"] = str(archive_folder)
            self.state["current_session"]["archived_recordings"] = [
                {
                    "original_name": file_info["original_name"],
                    "archive_name": file_info["archive_name"],
                    "archive_path": str(file_info["archive_path"]),
                    "size_mb": file_info["size_mb"]
                }
                for file_info in archived_files
            ]
            
            # Mark session for future cleanup (7 days from now)
            cleanup_date = datetime.now() + timedelta(days=7)
            self.state["current_session"]["cleanup_ready"] = True
            self.state["current_session"]["cleanup_date"] = cleanup_date.isoformat()
            
            logger.info(f"📊 Updated state with {len(archived_files)} archived files")
            
        except Exception as e:
            logger.error(f"❌ Error updating archive state: {e}")
    
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
    
    def step5_verify_and_archive(self, successful_transcripts: List[Path], successful_analyses: List[Dict]) -> bool:
        """
        Step 5: Verify & Archive
        Verifies session success, archives recordings, and prepares for cleanup
        """
        logger.info("🔍 Step 5: Verify & Archive")
        logger.info("=" * 50)
        
        try:
            # Step 1: Verify session success
            verification_passed, verification_result = self._verify_session_success(successful_transcripts, successful_analyses)
            
            if not verification_passed:
                logger.warning(f"⚠️ Session verification failed: {verification_result['reason']}")
                logger.info("🔄 Keeping files in recorder for manual review")
                return False
            
            logger.info(f"✅ Session verification passed: {verification_result['reason']}")
            
            # Step 2: Get list of .mp3 files to archive
            session_id = self.state["current_session"]["session_id"]
            mp3_files = []
            
            # Find corresponding .mp3 files for successful transcripts
            for transcript in successful_transcripts:
                mp3_name = transcript.stem + ".mp3"
                mp3_path = Path("/Volumes/IC RECORDER/REC_FILE/FOLDER01") / mp3_name
                if mp3_path.exists():
                    mp3_files.append(mp3_path)
                else:
                    logger.warning(f"⚠️ MP3 file not found for transcript: {mp3_name}")
            
            if not mp3_files:
                logger.warning("⚠️ No MP3 files found to archive")
                return False
            
            logger.info(f"📁 Found {len(mp3_files)} MP3 files to archive")
            
            # Step 3: Create archive structure
            archive_folder = self._create_archive_structure(session_id)
            
            # Step 4: Archive files
            archived_files = []
            failed_archives = []
            
            for mp3_file in mp3_files:
                logger.info(f"📁 Archiving: {mp3_file.name}")
                
                success, archive_path, error = self._archive_single_recording(mp3_file, archive_folder, session_id)
                
                if success:
                    # Get file size for state tracking
                    size_mb = mp3_file.stat().st_size / (1024 * 1024)
                    
                    archived_files.append({
                        "original_name": mp3_file.name,
                        "archive_name": archive_path.name,
                        "archive_path": archive_path,
                        "size_mb": round(size_mb, 2)
                    })
                else:
                    failed_archives.append({
                        "file": mp3_file.name,
                        "error": error
                    })
                    logger.error(f"❌ Failed to archive {mp3_file.name}: {error}")
            
            if failed_archives:
                logger.warning(f"⚠️ {len(failed_archives)} files failed to archive")
                for failure in failed_archives:
                    logger.warning(f"   - {failure['file']}: {failure['error']}")
            
            if not archived_files:
                logger.error("❌ No files were successfully archived")
                return False
            
            # Step 5: Clean up recorder files (only successfully archived ones)
            cleanup_success = 0
            for file_info in archived_files:
                # Find the original MP3 file
                mp3_path = Path("/Volumes/IC RECORDER/REC_FILE/FOLDER01") / file_info["original_name"]
                if mp3_path.exists():
                    if self._cleanup_recorder_file(mp3_path, file_info["archive_path"]):
                        cleanup_success += 1
                        # Update state
                        self.state["current_session"]["recordings_processed"].append(file_info["original_name"])
                else:
                    logger.warning(f"⚠️ MP3 file no longer exists: {file_info['original_name']}")
            
            logger.info(f"🗑️ Cleaned up {cleanup_success}/{len(archived_files)} files from recorder")
            
            # Step 6: Update state
            self._update_archive_state(session_id, archived_files, archive_folder)
            
            # Step 7: Finalize session
            self._finalize_session(session_id)
            
            # Step 8: Save final state
            self._save_state(self.state)
            
            # Final summary
            logger.info(f"")
            logger.info(f"📊 Archive & Cleanup Summary:")
            logger.info(f"   📁 Files Archived: {len(archived_files)}/{len(mp3_files)}")
            logger.info(f"   🗑️ Recorder Cleaned: {cleanup_success}/{len(archived_files)}")
            logger.info(f"   📅 Archive Location: {archive_folder}")
            logger.info(f"   🧹 Cleanup Date: 7 days from now")
            
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
            success, unprocessed_files = self.step1_monitor_and_detect()
            
            if not success:
                logger.error("❌ Orchestrator failed at Step 1")
                return False
            
            if not unprocessed_files:
                logger.info("✅ No new files to process - orchestrator complete")
                return True
            
            logger.info(f"📋 Ready to process {len(unprocessed_files)} files")
            
            # Step 2: Validate & Prepare
            success, valid_files, time_estimate = self.step2_validate_and_prepare(unprocessed_files)
            
            if not success:
                logger.error("❌ Orchestrator failed at Step 2")
                return False
            
            if not valid_files:
                logger.info("✅ No valid files to process - orchestrator complete")
                return True
            
            logger.info(f"📋 Ready to transcribe {len(valid_files)} files")
            
            # Step 3: Transcribe
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
            
            # Wait for user signal to proceed
            input("\n🎯 Press Enter to proceed to Step 4 (Stage & Process)...")
            
            # Step 4: Stage & Process
            success, successful_analyses, failed_transcripts = self.step4_stage_and_process(successful_transcripts)
            
            if not success:
                logger.error("❌ Orchestrator failed at Step 4")
                return False
            
            if not successful_analyses:
                logger.info("✅ No successful analyses - orchestrator complete")
                return True
            
            logger.info(f"🤖 Successfully processed {len(successful_analyses)} transcripts")
            logger.info("🔄 Next steps: Verify, Archive, Cleanup")
            logger.info("⏸️ Stopping here for Step 4 validation")
            
            # Wait for user signal to proceed
            input("\n🎯 Press Enter to proceed to Step 5 (Verify & Archive)...")
            
            # Step 5: Verify & Archive
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

def main():
    """Main entry point"""
    orchestrator = RecordingOrchestrator()
    success = orchestrator.run()
    
    if success:
        print("\n🎉 Orchestrator completed successfully!")
    else:
        print("\n❌ Orchestrator failed!")
        exit(1)

if __name__ == "__main__":
    main()
