"""
File Utilities with Safety Checks and Error Handling
Provides safe, validated file operations for all scripts.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Union, Optional

logger = logging.getLogger(__name__)

# Project root for safety checks
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.
    
    Returns:
        Path: The project root directory
    """
    return PROJECT_ROOT


def is_path_safe(path: Union[str, Path]) -> bool:
    """
    Check if a path is within the project root (safety check).
    
    Args:
        path: The path to check
    
    Returns:
        bool: True if path is within project root, False otherwise
    """
    try:
        resolved_path = Path(path).resolve()
        return PROJECT_ROOT in resolved_path.parents or resolved_path == PROJECT_ROOT
    except Exception as e:
        logger.warning(f"⚠️ Could not validate path safety: {e}")
        return False


def ensure_directory(
    path: Union[str, Path],
    parents: bool = True,
    exist_ok: bool = True
) -> Path:
    """
    Create a directory if it doesn't exist, with error handling.
    
    Args:
        path: Directory path to create
        parents: Create parent directories if needed
        exist_ok: Don't raise error if directory already exists
    
    Returns:
        Path: The created/existing directory path
    
    Raises:
        ValueError: If path is invalid or unsafe
        OSError: If directory creation fails
    """
    try:
        dir_path = Path(path).resolve()
        
        # Create directory
        dir_path.mkdir(parents=parents, exist_ok=exist_ok)
        
        if not exist_ok or not dir_path.exists():
            logger.debug(f"📁 Created directory: {dir_path}")
        
        return dir_path
        
    except Exception as e:
        logger.error(f"❌ Failed to create directory {path}: {e}")
        raise


def safe_copy_file(
    source: Union[str, Path],
    destination: Union[str, Path],
    overwrite: bool = False
) -> Path:
    """
    Safely copy a file with validation and error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Allow overwriting existing files
    
    Returns:
        Path: The destination file path
    
    Raises:
        FileNotFoundError: If source file doesn't exist
        FileExistsError: If destination exists and overwrite=False
        ValueError: If paths are invalid
    """
    try:
        src_path = Path(source).resolve()
        dst_path = Path(destination).resolve()
        
        # Validate source exists
        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")
        
        if not src_path.is_file():
            raise ValueError(f"Source is not a file: {src_path}")
        
        # Check if destination exists
        if dst_path.exists() and not overwrite:
            raise FileExistsError(f"Destination already exists: {dst_path}")
        
        # Ensure destination directory exists
        ensure_directory(dst_path.parent)
        
        # Copy file
        shutil.copy2(src_path, dst_path)
        logger.debug(f"📄 Copied: {src_path.name} → {dst_path}")
        
        return dst_path
        
    except Exception as e:
        logger.error(f"❌ Failed to copy {source} to {destination}: {e}")
        raise


def safe_move_file(
    source: Union[str, Path],
    destination: Union[str, Path],
    overwrite: bool = False
) -> Path:
    """
    Safely move a file with validation and error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Allow overwriting existing files
    
    Returns:
        Path: The destination file path
    
    Raises:
        FileNotFoundError: If source file doesn't exist
        FileExistsError: If destination exists and overwrite=False
    """
    try:
        src_path = Path(source).resolve()
        dst_path = Path(destination).resolve()
        
        # Validate source exists
        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")
        
        # Check if destination exists
        if dst_path.exists() and not overwrite:
            raise FileExistsError(f"Destination already exists: {dst_path}")
        
        # Ensure destination directory exists
        ensure_directory(dst_path.parent)
        
        # Move file
        shutil.move(str(src_path), str(dst_path))
        logger.debug(f"📦 Moved: {src_path.name} → {dst_path}")
        
        return dst_path
        
    except Exception as e:
        logger.error(f"❌ Failed to move {source} to {destination}: {e}")
        raise


def safe_delete_file(
    path: Union[str, Path],
    require_project_root: bool = True
) -> bool:
    """
    Safely delete a file with validation.
    
    Args:
        path: File path to delete
        require_project_root: Only allow deletion within project root
    
    Returns:
        bool: True if file was deleted, False if file didn't exist
    
    Raises:
        ValueError: If path is outside project root (when require_project_root=True)
    """
    try:
        file_path = Path(path).resolve()
        
        # Safety check: prevent deletion outside project
        if require_project_root and not is_path_safe(file_path):
            raise ValueError(
                f"❌ SAFETY: Cannot delete file outside project root: {file_path}\n"
                f"   Project root: {PROJECT_ROOT}"
            )
        
        # Check if file exists
        if not file_path.exists():
            logger.debug(f"File already deleted or doesn't exist: {file_path}")
            return False
        
        # Delete file
        file_path.unlink()
        logger.debug(f"🗑️ Deleted file: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to delete {path}: {e}")
        raise


def safe_delete_directory(
    path: Union[str, Path],
    require_project_root: bool = True,
    recursive: bool = False
) -> bool:
    """
    Safely delete a directory with validation.
    
    Args:
        path: Directory path to delete
        require_project_root: Only allow deletion within project root
        recursive: Delete directory and all contents
    
    Returns:
        bool: True if directory was deleted, False if didn't exist
    
    Raises:
        ValueError: If path is outside project root or directory not empty (when recursive=False)
    """
    try:
        dir_path = Path(path).resolve()
        
        # Safety check: prevent deletion outside project
        if require_project_root and not is_path_safe(dir_path):
            raise ValueError(
                f"❌ SAFETY: Cannot delete directory outside project root: {dir_path}\n"
                f"   Project root: {PROJECT_ROOT}"
            )
        
        # Check if directory exists
        if not dir_path.exists():
            logger.debug(f"Directory already deleted or doesn't exist: {dir_path}")
            return False
        
        if not dir_path.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path}")
        
        # Delete directory
        if recursive:
            shutil.rmtree(dir_path)
            logger.debug(f"🗑️ Deleted directory (recursive): {dir_path}")
        else:
            dir_path.rmdir()  # Will fail if not empty
            logger.debug(f"🗑️ Deleted empty directory: {dir_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to delete directory {path}: {e}")
        raise


def validate_file_exists(path: Union[str, Path]) -> Path:
    """
    Validate that a file exists and return its path.
    
    Args:
        path: File path to validate
    
    Returns:
        Path: The validated file path
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is not a file
    """
    file_path = Path(path).resolve()
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    return file_path


def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False
) -> list[Path]:
    """
    List files in a directory matching a pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (e.g., "*.txt", "*.mp3")
        recursive: Search subdirectories recursively
    
    Returns:
        list[Path]: List of matching file paths
    """
    try:
        dir_path = Path(directory).resolve()
        
        if not dir_path.exists():
            logger.warning(f"⚠️ Directory doesn't exist: {dir_path}")
            return []
        
        if not dir_path.is_dir():
            logger.warning(f"⚠️ Path is not a directory: {dir_path}")
            return []
        
        # Use rglob for recursive, glob for non-recursive
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))
        
        # Filter to only files (exclude directories)
        files = [f for f in files if f.is_file()]
        
        logger.debug(f"📂 Found {len(files)} files matching '{pattern}' in {dir_path}")
        return files
        
    except Exception as e:
        logger.error(f"❌ Failed to list files in {directory}: {e}")
        return []

