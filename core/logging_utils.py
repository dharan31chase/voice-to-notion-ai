"""
Logging Utilities with Unified Configuration
Provides consistent logging setup across all scripts.
"""

import os
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Logging configuration
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "ai-assistant.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
BACKUP_COUNT = 5  # Keep 5 backup files


def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
    file_output: bool = True
) -> logging.Logger:
    """
    Set up a logger with file rotation and console output.
    
    Args:
        name: Logger name (usually __name__ from calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Custom log file path (default: logs/ai-assistant.log)
        console_output: Enable console (stdout) logging
        file_output: Enable file logging
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        logger = setup_logger(__name__)
        logger.info("Processing started")
        logger.error("Something went wrong")
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Set level
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    logger.setLevel(level_map.get(level.upper(), logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    # File handler with rotation
    if file_output:
        # Ensure log directory exists
        log_path = log_file or LOG_FILE
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Capture everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level_map.get(level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Prevent propagation to root logger (avoid duplicate logs)
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.
    
    Args:
        name: Logger name (usually __name__ from calling module)
    
    Returns:
        logging.Logger: Logger instance
    
    Example:
        from core.logging_utils import get_logger
        logger = get_logger(__name__)
        logger.info("Message")
    """
    logger = logging.getLogger(name)
    
    # If logger not configured, set it up with defaults
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


def configure_root_logger(level: str = "INFO") -> None:
    """
    Configure the root logger for the entire application.
    
    This is useful when you want to set up logging once at the start
    of your application and have all modules use the same configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Example:
        # In your main script
        from core.logging_utils import configure_root_logger
        configure_root_logger("INFO")
        
        # In other modules
        import logging
        logger = logging.getLogger(__name__)
        logger.info("This will use the root configuration")
    """
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Level mapping
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # Create formatter
    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level_map.get(level.upper(), logging.INFO))
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def set_log_level(logger: logging.Logger, level: str) -> None:
    """
    Change the log level of an existing logger.
    
    Args:
        logger: The logger to modify
        level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Example:
        logger = get_logger(__name__)
        set_log_level(logger, "DEBUG")  # Enable debug output
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    logger.setLevel(level_map.get(level.upper(), logging.INFO))
    
    # Update console handler level too
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, RotatingFileHandler):
            handler.setLevel(level_map.get(level.upper(), logging.INFO))


def cleanup_old_logs(days: int = 7) -> int:
    """
    Delete log files older than specified days.
    
    Args:
        days: Delete logs older than this many days
    
    Returns:
        int: Number of log files deleted
    
    Example:
        deleted = cleanup_old_logs(7)  # Delete logs older than 7 days
        print(f"Deleted {deleted} old log files")
    """
    import time
    from datetime import datetime, timedelta
    
    if not LOG_DIR.exists():
        return 0
    
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    deleted_count = 0
    
    for log_file in LOG_DIR.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                deleted_count += 1
            except Exception as e:
                logging.warning(f"Failed to delete old log file {log_file}: {e}")
    
    return deleted_count

