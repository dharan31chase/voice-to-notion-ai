"""
Transcription Engine Module

Responsibilities:
- Audio-to-text transcription using Whisper
- Intelligent batch processing with work budget balancing
- System resource monitoring (disk, memory, CPU)
- Parallel transcription with ThreadPoolExecutor
- CPU throttling to prevent overload
- Smart retry policy (skip permission/short file errors)
- Duplicate transcript detection
- Transcription state management

Does NOT handle:
- File validation (FileValidator)
- USB operations (USBDetector)
- Staging management (StagingManager)
- Archive management (ArchiveManager)
"""

import os
import shutil
import subprocess
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

logger = logging.getLogger(__name__)


class TranscriptionEngine:
    """Handles audio-to-text transcription with batching and resource management."""

    def __init__(self, config, file_validator):
        """
        Initialize transcription engine.

        Args:
            config: ConfigLoader instance for transcription settings
            file_validator: FileValidator instance for dependency checks
        """
        self.config = config
        self.file_validator = file_validator
        logger.info("TranscriptionEngine initialized")

    def extract_file_metadata(self, file_path: Path) -> Dict:
        """
        Extract metadata from audio file.

        Uses file size to estimate duration (1MB ≈ 1 minute).

        Args:
            file_path: Path to audio file

        Returns:
            Dict: Metadata with name, size_mb, timestamps, estimated_minutes
        """
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
            logger.error(f"ERROR: Error extracting metadata for {file_path.name}: {e}")
            return {
                "name": file_path.name,
                "size_mb": 0,
                "created_time": None,
                "modified_time": None,
                "estimated_minutes": 0,
                "path": str(file_path),
                "error": str(e)
            }

    def check_system_resources(self, project_root: Path) -> Tuple[bool, Dict]:
        """
        Check if system has sufficient resources for transcription.

        Requirements:
        - Disk space: >500MB free
        - Memory: >1GB available (if psutil installed)

        Args:
            project_root: Project root directory to check space for

        Returns:
            Tuple[bool, Dict]: (resources_ok, resource_status)
        """
        try:
            # Check disk space
            total, used, free = shutil.disk_usage(project_root)
            free_gb = free / (1024**3)

            # Check available memory (rough estimate)
            try:
                import psutil
                memory = psutil.virtual_memory()
                available_gb = memory.available / (1024**3)
                memory_ok = available_gb > 1.0
                memory_available = round(available_gb, 2)
            except ImportError:
                logger.debug("psutil not available, skipping memory check")
                memory_ok = True  # Assume OK if we can't check
                memory_available = "Unknown"

            # Requirements: 500MB free disk, 1GB available memory
            disk_ok = free_gb > 0.5

            resource_status = {
                "disk_free_gb": round(free_gb, 2),
                "disk_ok": disk_ok,
                "memory_available_gb": memory_available,
                "memory_ok": memory_ok,
                "all_ok": disk_ok and memory_ok
            }

            if not resource_status["all_ok"]:
                logger.warning(f"WARNING: Resource check failed:")
                if not disk_ok:
                    logger.warning(f"   - Disk space: {free_gb:.2f}GB (need >0.5GB)")
                if not memory_ok and memory_available != "Unknown":
                    logger.warning(f"   - Memory: {memory_available}GB (need >1GB)")

            return resource_status["all_ok"], resource_status

        except Exception as e:
            logger.error(f"ERROR: Error checking system resources: {e}")
            return False, {"error": str(e)}

    def create_balanced_batches(self, files: List[Path]) -> List[List[Path]]:
        """
        Create duration-aware batches with work budget balancing.

        Distributes files to prevent one long file from dominating a batch.
        Uses work budget (default 7 minutes) instead of fixed file count.

        Args:
            files: List of audio files to batch

        Returns:
            List[List[Path]]: Batches of files, each batch ~7 minutes of audio
        """
        if not files:
            return []

        work_budget_minutes = self.config.get("processing.batch_work_budget_minutes", 7)
        min_files = self.config.get("processing.batch_min_files", 1)
        max_files = self.config.get("processing.batch_max_files", 4)

        # Extract file durations
        file_info = []
        for file_path in files:
            metadata = self.extract_file_metadata(file_path)
            file_info.append({
                'path': file_path,
                'duration_minutes': metadata.get('estimated_minutes', 1),
                'name': file_path.name
            })

        # Sort by duration (longest first) for better distribution
        file_info.sort(key=lambda x: x['duration_minutes'], reverse=True)

        batches = []
        current_batch = []
        current_batch_minutes = 0

        for info in file_info:
            file_path = info['path']
            duration = info['duration_minutes']

            # Check if adding this file would exceed work budget
            would_exceed = (current_batch_minutes + duration) > work_budget_minutes
            batch_full = len(current_batch) >= max_files

            if current_batch and (would_exceed or batch_full):
                # Start new batch
                batches.append(current_batch)
                current_batch = [file_path]
                current_batch_minutes = duration
            else:
                # Add to current batch
                current_batch.append(file_path)
                current_batch_minutes += duration

            # Ensure we don't create batches that are too small (unless it's the last file)
            if len(current_batch) < min_files and len(batches) == 0:
                continue

        # Add final batch
        if current_batch:
            batches.append(current_batch)

        # Log batch distribution
        logger.info(f"Created {len(batches)} balanced batches (target: {work_budget_minutes}min per batch)")
        for i, batch in enumerate(batches, 1):
            batch_minutes = sum(self.extract_file_metadata(f).get('estimated_minutes', 1) for f in batch)
            logger.info(f"   Batch {i}: {len(batch)} files, ~{batch_minutes}min audio")

        return batches

    def monitor_cpu_usage(self) -> float:
        """
        Monitor current CPU usage percentage.

        Returns:
            float: CPU usage percentage (0-100), or 0.0 if psutil unavailable
        """
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0
        except Exception as e:
            logger.debug(f"CPU monitoring error: {e}")
            return 0.0

    def should_transcribe(self, audio_file: Path, transcripts_folder: Path) -> bool:
        """
        Check if audio file should be transcribed (duplicate detection).

        Skips transcription if:
        - Transcript already exists
        - Transcript is recent (<1 hour old)
        - Transcript has meaningful content (>10 characters)

        Args:
            audio_file: Path to audio file
            transcripts_folder: Folder where transcripts are stored

        Returns:
            bool: True if should transcribe, False if should skip
        """
        try:
            # Ensure we have a Path object
            if isinstance(audio_file, str):
                audio_file = Path(audio_file)

            # Check if transcript already exists
            transcript_file = transcripts_folder / f"{audio_file.stem}.txt"

            if transcript_file.exists():
                # Check if transcript is recent (within last hour) and has content
                transcript_age = time.time() - transcript_file.stat().st_mtime
                if transcript_age < 3600:  # 1 hour
                    with open(transcript_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if len(content) > 10:  # Has meaningful content
                        logger.info(f"INFO: Transcript already exists: {transcript_file.name} (age: {transcript_age/60:.1f} min)")
                        return False

            return True

        except Exception as e:
            logger.warning(f"WARNING: Error checking transcript existence for {audio_file}: {e}")
            return True  # Default to transcribing if check fails

    def transcribe_single_file(self, file_path: Path, transcripts_folder: Path,
                               batch_num: int, file_num: int) -> Tuple[bool, str, str]:
        """
        Transcribe a single audio file using Whisper CLI.

        Args:
            file_path: Path to audio file (.mp3)
            transcripts_folder: Output folder for transcript
            batch_num: Batch number (for logging)
            file_num: File number within batch (for logging)

        Returns:
            Tuple[bool, str, str]:
                - success: True if transcription succeeded
                - error_or_path: Error message (if failed) or transcript path (if succeeded)
                - transcript_content: Transcript text (empty if failed)
        """
        try:
            # Generate output filename
            output_name = file_path.stem + ".txt"
            output_path = transcripts_folder / output_name

            # Get Whisper settings from config
            whisper_model = self.config.get("whisper.model", "small")
            whisper_language = self.config.get("whisper.language", "en")
            whisper_output_format = self.config.get("whisper.output_format", "txt")

            # Whisper command
            cmd = [
                'whisper',
                str(file_path),
                '--model', whisper_model,
                '--language', whisper_language,
                '--output_dir', str(transcripts_folder),
                '--output_format', whisper_output_format
            ]

            logger.info(f"Transcribing {file_path.name} (Batch {batch_num}, File {file_num})")

            # Run Whisper with 300-second timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0 and output_path.exists():
                # Validate transcript
                with open(output_path, 'r', encoding='utf-8') as f:
                    transcript_content = f.read().strip()

                if len(transcript_content) > 10:  # Basic validation
                    logger.info(f"SUCCESS: Transcribed {file_path.name} -> {output_name}")
                    return True, str(output_path), transcript_content
                else:
                    logger.warning(f"WARNING: Transcript too short: {file_path.name}")
                    return False, "Transcript too short", transcript_content
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                logger.error(f"ERROR: Transcription failed: {file_path.name} - {error_msg}")
                return False, error_msg, ""

        except subprocess.TimeoutExpired:
            logger.error(f"ERROR: Transcription timeout: {file_path.name}")
            return False, "Transcription timeout", ""
        except Exception as e:
            logger.error(f"ERROR: Transcription error: {file_path.name} - {e}")
            return False, str(e), ""

    def transcribe_batch(self, files: List[Path], transcripts_folder: Path,
                        failed_folder: Path, state: Dict,
                        move_failed_callback=None) -> Tuple[bool, List[Path], List[Path]]:
        """
        Transcribe multiple audio files with parallel processing.

        Main orchestration method that:
        1. Checks system resources
        2. Creates balanced batches
        3. Runs parallel transcription (ThreadPoolExecutor)
        4. Monitors CPU and throttles if needed
        5. Implements smart retry policy
        6. Updates state with results

        Args:
            files: List of audio files to transcribe
            transcripts_folder: Output folder for transcripts
            failed_folder: Folder for failed files
            state: Session state dict to update
            move_failed_callback: Optional callback to move failed files (orchestrator's responsibility)

        Returns:
            Tuple[bool, List[Path], List[Path]]:
                - success: True if at least one file succeeded
                - successful_transcripts: List of transcript file paths
                - failed_files: List of audio files that failed
        """
        try:
            if not files:
                logger.warning("WARNING: No files to transcribe")
                return True, [], []

            # Check Whisper installation
            if not self.file_validator.check_dependencies():
                return False, [], []

            # Check disk space (estimate: file size + 100MB buffer)
            total_size_mb = sum(self.extract_file_metadata(f).get('size_mb', 0) for f in files)
            required_space = total_size_mb + 100
            if not self.file_validator.check_disk_space(Path.cwd(), required_space):
                return False, [], []

            # Check system resources
            resources_ok, resource_status = self.check_system_resources(Path.cwd())
            if not resources_ok:
                logger.error("ERROR: Insufficient system resources for transcription")
                return False, [], []

            logger.info(f"System resources OK:")
            logger.info(f"   - Disk: {resource_status['disk_free_gb']}GB free")
            if resource_status['memory_available_gb'] != "Unknown":
                logger.info(f"   - Memory: {resource_status['memory_available_gb']}GB available")

            # Create balanced batches with work budget
            batches = self.create_balanced_batches(files)

            successful_transcripts = []
            failed_files = []

            # Get Whisper model from config for logging
            whisper_model = self.config.get("whisper.model", "small")
            whisper_language = self.config.get("whisper.language", "en")

            logger.info(f"Initializing Whisper ({whisper_model} model, {whisper_language.upper()})")
            logger.info(f"Processing {len(files)} files in {len(batches)} batches")

            # Process each batch
            for batch_num, batch in enumerate(batches, 1):
                logger.info(f"")
                logger.info(f"Batch {batch_num}/{len(batches)} ({len(batch)} files) - Processing...")

                batch_start_time = time.time()
                batch_successes = []
                batch_failures = []

                # Process files in parallel within batch
                max_workers = self.config.get("processing.parallel_transcription_workers", 3)
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Filter out files that already have transcripts
                    files_to_transcribe = []
                    for file_path in batch:
                        if self.should_transcribe(file_path, transcripts_folder):
                            files_to_transcribe.append(file_path)
                        else:
                            # Add existing transcript to successful list
                            transcript_path = transcripts_folder / f"{file_path.stem}.txt"
                            if transcript_path.exists():
                                successful_transcripts.append(transcript_path)
                                batch_successes.append(file_path)
                                # Update state
                                state["transcripts_created"].append(transcript_path.name)

                    if not files_to_transcribe:
                        logger.info(f"   INFO: All files in batch {batch_num} already have transcripts")
                        continue

                    # Submit transcription tasks
                    future_to_file = {
                        executor.submit(self.transcribe_single_file, file_path,
                                      transcripts_folder, batch_num, i+1): file_path
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
                                transcript_path = transcripts_folder / transcript_name

                                if transcript_path.exists():
                                    successful_transcripts.append(transcript_path)
                                    batch_successes.append(file_path)

                                    # Update state
                                    state["transcripts_created"].append(transcript_name)
                                else:
                                    logger.error(f"ERROR: Transcript file not found: {transcript_name}")
                                    failed_files.append(file_path)
                                    batch_failures.append(file_path)
                            else:
                                # Smart retry policy - check if should retry
                                should_retry = True

                                # Don't retry on permission errors (use staging instead)
                                if not self.config.get("processing.retry_on_permission_errors", False):
                                    if "permission" in error_reason.lower() or "not permitted" in error_reason.lower():
                                        should_retry = False
                                        logger.info(f"SKIP: Skipping retry for {file_path.name}: permission error (use staging)")

                                # Don't retry on "too short" errors
                                if not self.config.get("processing.retry_on_short_transcript_errors", False):
                                    if "too short" in error_reason.lower() or "transcript too short" in error_reason.lower():
                                        should_retry = False
                                        logger.info(f"SKIP: Skipping retry for {file_path.name}: transcript too short")

                                if should_retry:
                                    logger.info(f"RETRY: Retrying transcription: {file_path.name}")
                                    retry_success, retry_error, retry_content = self.transcribe_single_file(
                                        file_path, transcripts_folder, batch_num, 0
                                    )

                                    if retry_success:
                                        transcript_name = file_path.stem + ".txt"
                                        transcript_path = transcripts_folder / transcript_name
                                        if transcript_path.exists():
                                            successful_transcripts.append(transcript_path)
                                            batch_successes.append(file_path)
                                            state["transcripts_created"].append(transcript_name)
                                        else:
                                            failed_files.append(file_path)
                                            batch_failures.append(file_path)
                                    else:
                                        failed_files.append(file_path)
                                        batch_failures.append(file_path)

                                        # Move failed file (if callback provided)
                                        if move_failed_callback:
                                            move_failed_callback(file_path, retry_error, "recording")

                                        # Update state
                                        state["failed_transcriptions"].append(file_path.name)

                                else:
                                    # Don't retry - mark as failed immediately
                                    failed_files.append(file_path)
                                    batch_failures.append(file_path)

                                    # Move failed file (if callback provided)
                                    if move_failed_callback:
                                        move_failed_callback(file_path, error_reason, "recording")

                                    # Update state
                                    state["failed_transcriptions"].append(file_path.name)

                            # Monitor CPU usage with configurable threshold
                            cpu_usage = self.monitor_cpu_usage()
                            cpu_limit = self.config.get("processing.cpu_usage_limit_percent", 70)
                            if cpu_usage > cpu_limit:
                                logger.warning(f"WARNING: High CPU usage: {cpu_usage:.1f}% (limit: {cpu_limit}%) - waiting 2 seconds")
                                time.sleep(2)

                        except Exception as e:
                            logger.error(f"ERROR: Error processing {file_path.name}: {e}")
                            failed_files.append(file_path)
                            batch_failures.append(file_path)

                            if move_failed_callback:
                                move_failed_callback(file_path, str(e), "recording")

                            state["failed_transcriptions"].append(file_path.name)

                # Report batch completion
                batch_time = time.time() - batch_start_time
                logger.info(f"   SUCCESS: {len(batch_successes)} files")
                if batch_failures:
                    logger.info(f"   FAILED: {len(batch_failures)} files")
                logger.info(f"   Batch {batch_num} complete in {batch_time:.0f}s")

            # Final summary
            logger.info(f"")
            logger.info(f"Transcription Summary:")
            logger.info(f"   SUCCESS: {len(successful_transcripts)}/{len(files)} files")
            logger.info(f"   FAILED: {len(failed_files)} files")
            logger.info(f"   Transcripts Created: {len(successful_transcripts)}")

            # Update state summary
            state["transcription_complete"] = True
            state["transcription_summary"] = {
                "total_files": len(files),
                "successful": len(successful_transcripts),
                "failed": len(failed_files),
                "success_rate": len(successful_transcripts) / len(files) if files else 0
            }

            return True, successful_transcripts, failed_files

        except Exception as e:
            logger.error(f"ERROR: Transcription batch failed: {e}")
            return False, [], []
