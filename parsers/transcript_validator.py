"""
Transcript Validator Module
Validates transcript files and content before AI processing.

Protects manual workflow (MacWhisper) from processing invalid files.
Orchestrator workflow already has validation built-in.
"""

import sys
from pathlib import Path
from typing import Tuple, Optional
import logging

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class TranscriptValidator:
    """
    Validates transcript files before AI processing.
    
    Prevents wasted API calls on invalid/malformed transcripts.
    Uses configurable rules from parsing_rules.yaml.
    """
    
    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize validator with configuration.
        
        Args:
            config: ConfigLoader instance (creates new if not provided)
        """
        self.config = config or ConfigLoader()
        
        # Load validation rules from config
        validation_rules = self.config.get("validation", {})
        self.min_word_count = validation_rules.get("minimum_word_count", 3)
        self.min_char_count = validation_rules.get("minimum_char_count", 10)
        self.max_word_count = validation_rules.get("maximum_word_count", 10000)
        
        # Load content length thresholds
        length_rules = self.config.get("content_length", {})
        self.short_threshold = length_rules.get("short_threshold", 800)
        self.long_threshold = length_rules.get("long_threshold", 800)
        
        logger.debug(f"TranscriptValidator initialized: "
                    f"min_words={self.min_word_count}, "
                    f"preservation_threshold={self.long_threshold}")
    
    def validate_file(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate that a file is processable.
        
        Args:
            file_path: Path to transcript file
        
        Returns:
            Tuple of (is_valid, reason)
            - is_valid: True if file can be processed
            - reason: Explanation if invalid, "OK" if valid
        """
        try:
            # Check file exists
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            # Check it's a file (not directory)
            if not file_path.is_file():
                return False, f"Path is not a file: {file_path}"
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size == 0:
                return False, "File is empty (0 bytes)"
            
            if file_size < self.min_char_count:
                return False, f"File too small ({file_size} bytes, min: {self.min_char_count})"
            
            # Check file extension
            if file_path.suffix.lower() != '.txt':
                return False, f"Wrong file type: {file_path.suffix} (expected .txt)"
            
            # Try to read file (check encoding)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                return False, "File encoding error (not valid UTF-8)"
            except Exception as e:
                return False, f"Cannot read file: {e}"
            
            # Validate the content
            is_valid, reason = self.validate_content(content)
            if not is_valid:
                return False, reason
            
            logger.debug(f"✅ File validated: {file_path.name}")
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Validation error for {file_path}: {e}")
            return False, f"Validation exception: {e}"
    
    def validate_content(self, text: str) -> Tuple[bool, str]:
        """
        Validate transcript content.
        
        Args:
            text: Transcript text content
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check not empty
        if not text or not text.strip():
            return False, "Content is empty or only whitespace"
        
        # Check minimum character count
        char_count = len(text.strip())
        if char_count < self.min_char_count:
            return False, f"Content too short ({char_count} chars, min: {self.min_char_count})"
        
        # Check minimum word count
        word_count = len(text.split())
        if word_count < self.min_word_count:
            return False, f"Content too short ({word_count} words, min: {self.min_word_count})"
        
        # Check maximum word count (sanity check)
        if word_count > self.max_word_count:
            return False, f"Content too long ({word_count} words, max: {self.max_word_count})"
        
        logger.debug(f"✅ Content validated: {word_count} words, {char_count} chars")
        return True, "OK"
    
    def get_length_category(self, text: str) -> str:
        """
        Determine if content is short or long for preservation logic.
        
        Args:
            text: Transcript text
        
        Returns:
            "short" if below threshold (full AI analysis)
            "long" if above threshold (preserve original)
        """
        word_count = len(text.split())
        
        if word_count > self.long_threshold:
            logger.debug(f"Content classified as LONG ({word_count} words > {self.long_threshold})")
            return "long"
        else:
            logger.debug(f"Content classified as SHORT ({word_count} words <= {self.short_threshold})")
            return "short"
    
    def get_word_count(self, text: str) -> int:
        """Get word count of text"""
        return len(text.split())


