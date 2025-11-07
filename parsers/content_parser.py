"""
Content Parser Module
Smart category detection using configurable heuristics and pattern matching.

Implements 5-tier detection system:
1. Explicit keywords (task, note) - 90% confidence
2. Imperative verbs (fix, create, etc.) - 80% confidence  
3. Note indicators (I noticed, was, etc.) - 75% confidence
4. Intent patterns (I want to, I need to) - 75% confidence
5. Calendar patterns (future workflow) - 70% confidence, manual review
Default: Note category - 50% confidence, manual review
"""

import sys
import re
from pathlib import Path
from typing import Dict, Tuple, List, Any, Optional
import logging

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.config_loader import ConfigLoader
from core.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = get_openai_client()


class CategoryDetector:
    """
    Detects content category (task/note/event) using configurable heuristics.
    
    Features:
    - 5-tier detection system with confidence scoring
    - Config-driven keywords and patterns
    - Smart defaults (passive content → note, not task)
    - Future-proof for calendar/event workflow
    """
    
    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize category detector.
        
        Args:
            config: ConfigLoader instance (creates new if not provided)
        """
        self.config = config or ConfigLoader()
        self.rules = self.config.get("category_detection", {})
        
        # Load detection rules from config
        self.task_keywords = set(k.lower() for k in self.rules.get("task_keywords", []))
        self.note_keywords = set(k.lower() for k in self.rules.get("note_keywords", []))
        self.task_imperatives = set(v.lower() for v in self.rules.get("task_imperative_verbs", []))
        self.note_indicators = self.rules.get("note_indicators", [])
        self.task_intents = self.rules.get("task_intent_patterns", [])
        self.calendar_keywords = set(k.lower() for k in self.rules.get("calendar_keywords", []))
        
        # Thresholds
        thresholds = self.rules.get("thresholds", {})
        self.manual_review_threshold = thresholds.get("manual_review", 0.7)
        self.high_confidence_threshold = thresholds.get("high_confidence", 0.8)
        
        # Behavior
        behavior = self.rules.get("behavior", {})
        self.check_entire_text = behavior.get("check_entire_text", True)
        self.case_insensitive = behavior.get("case_insensitive", True)
        
        logger.debug(f"CategoryDetector initialized with {len(self.task_keywords)} task keywords, "
                    f"{len(self.note_keywords)} note keywords, "
                    f"{len(self.task_imperatives)} imperative verbs")
    
    def detect_category(self, content: str) -> Tuple[str, float, bool]:
        """
        Detect category with confidence scoring and manual review flag.

        Args:
            content: The transcript text to analyze

        Returns:
            Tuple of (category, confidence, manual_review)
            - category: "task" or "note" (or future: "event")
            - confidence: 0.0-1.0 score
            - manual_review: True if confidence below threshold
        """
        text = content.lower() if self.case_insensitive else content

        logger.debug(f"🔍 Detecting category for: '{content[:50]}{'...' if len(content) > 50 else ''}'")

        # Tier 0: Explicit metadata at END of transcript (HIGHEST priority)
        # Pattern: "Note 2" or "Task 1" in last 20 lines
        category, confidence = self._check_metadata_suffix(content)
        if category:
            logger.debug(f"  ✅ Tier 0 (Metadata Suffix): {category} (confidence: {confidence})")
            return category, confidence, False

        # Tier 1: Explicit keywords (highest confidence)
        category, confidence = self._check_explicit_keywords(text)
        if category:
            logger.debug(f"  ✅ Tier 1 (Keywords): {category} (confidence: {confidence})")
            return category, confidence, False
        
        # Tier 2: Task imperative verbs
        if self._has_task_imperative(text, content):
            logger.debug(f"  ✅ Tier 2 (Imperative): task (confidence: 0.8)")
            return "task", 0.8, False
        
        # Tier 3: Note indicators
        if self._has_note_indicator(text):
            logger.debug(f"  ✅ Tier 3 (Note Indicator): note (confidence: 0.75)")
            return "note", 0.75, False
        
        # Tier 4: Intent patterns (I want to, I need to)
        if self._has_intent_pattern(text):
            logger.debug(f"  ✅ Tier 4 (Intent): task (confidence: 0.75)")
            return "task", 0.75, False
        
        # Tier 5: Calendar keywords (future event workflow)
        if self._has_calendar_keyword(text):
            logger.debug(f"  ⏸️ Tier 5 (Calendar): task with manual review (confidence: 0.7)")
            logger.debug(f"     (Future: Will route to Google Calendar as 'event')")
            return "task", 0.7, True  # Manual review until calendar workflow exists
        
        # Default: Passive content is NOTE, not task
        logger.debug(f"  ℹ️ Default: note (passive content, confidence: 0.5)")
        return "note", 0.5, True  # Low confidence, requires review

    def _check_metadata_suffix(self, content: str) -> Tuple[Optional[str], float]:
        """
        Check for explicit metadata at the END of the transcript.

        Pattern: Standalone "note" or "task" in the last 20 lines.
        This has HIGHEST priority because it's explicit user metadata.

        Logic:
        - Check last 20 lines (handles garbage/transcription errors up to 12+ lines)
        - Look for standalone "note" or "task" (word boundary)
        - Case-insensitive matching
        - If nothing found: return None → defaults to "task" (user forgot tag)

        Args:
            content: Full transcript text

        Returns:
            Tuple of (category, confidence) or (None, 0.0)
        """
        import re

        # Get last 20 lines of transcript (handles garbage at end - seen up to 12 lines)
        lines = content.strip().split('\n')
        last_lines = lines[-20:] if len(lines) >= 20 else lines

        # Join and search for pattern
        last_text = ' '.join(last_lines).lower()

        # Pattern: standalone "note" or "task" (word boundary)
        note_pattern = r'\bnote\b'
        task_pattern = r'\btask\b'

        # Check for note metadata (highest priority)
        if re.search(note_pattern, last_text):
            logger.debug(f"  🎯 Found 'note' metadata in last 20 lines")
            return "note", 1.0  # Explicit metadata = 100% confidence

        # Check for task metadata
        if re.search(task_pattern, last_text):
            logger.debug(f"  🎯 Found 'task' metadata in last 20 lines")
            return "task", 1.0  # Explicit metadata = 100% confidence

        # Nothing found - caller will default to "task" (user forgot tag)
        return None, 0.0

    def _check_explicit_keywords(self, text: str) -> Tuple[Optional[str], float]:
        """Check for explicit task/note keywords"""
        # Check for task keywords
        for keyword in self.task_keywords:
            if keyword in text:
                return "task", 0.9
        
        # Check for note keywords
        for keyword in self.note_keywords:
            if keyword in text:
                return "note", 0.9
        
        return None, 0.0
    
    def _has_task_imperative(self, text: str, original_content: str) -> bool:
        """
        Check if text starts with or contains task imperative verbs.
        
        Flexible detection: checks anywhere in text (not just start).
        Excludes calendar-related verbs for future calendar workflow.
        """
        # Get first few words to check for imperative at start
        words = text.split()
        if not words:
            return False
        
        first_word = words[0].strip('.,!?;:')
        
        # High priority: Imperative at start of text
        if first_word in self.task_imperatives:
            logger.debug(f"    Found imperative verb at start: '{first_word}'")
            return True
        
        # Flexible: Check anywhere in text (fallback)
        for verb in self.task_imperatives:
            # Match whole word only (not partial matches)
            pattern = r'\b' + re.escape(verb) + r'\b'
            if re.search(pattern, text):
                logger.debug(f"    Found imperative verb in text: '{verb}'")
                return True
        
        return False
    
    def _has_note_indicator(self, text: str) -> bool:
        """Check for note indicators (reflective/passive patterns)"""
        for indicator in self.note_indicators:
            if indicator.lower() in text:
                logger.debug(f"    Found note indicator: '{indicator}'")
                return True
        return False
    
    def _has_intent_pattern(self, text: str) -> bool:
        """Check for intent patterns (I want to, I need to, etc.)"""
        for pattern in self.task_intents:
            if pattern.lower() in text:
                logger.debug(f"    Found intent pattern: '{pattern}'")
                return True
        return False
    
    def _has_calendar_keyword(self, text: str) -> bool:
        """Check for calendar/scheduling keywords (future event workflow)"""
        for keyword in self.calendar_keywords:
            if keyword in text:
                logger.debug(f"    Found calendar keyword: '{keyword}'")
                return True
        return False


class ContentParser:
    """
    Main content parser that orchestrates category detection and content parsing.
    
    Provides high-level parsing interface for transcript processing.
    """
    
    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize content parser.
        
        Args:
            config: ConfigLoader instance (creates new if not provided)
        """
        self.config = config or ConfigLoader()
        self.detector = CategoryDetector(self.config)
        logger.debug("ContentParser initialized")
    
    def parse(self, transcript_text: str) -> Dict[str, Any]:
        """
        Parse transcript text into structured data.

        Args:
            transcript_text: Raw transcript text

        Returns:
            Dict with keys:
            - category: "task" or "note"
            - confidence: 0.0-1.0
            - manual_review: bool
            - content: cleaned content
            - raw_text: original text
        """
        # Clean and normalize
        content = transcript_text.strip()

        # Detect category with heuristics
        category, confidence, manual_review = self.detector.detect_category(content)

        logger.info(f"📊 Detected category: {category} (confidence: {confidence:.2f}, "
                   f"manual_review: {manual_review})")

        return {
            "category": category,
            "confidence_score": confidence,
            "manual_review": manual_review,
            "content": content,
            "raw_text": transcript_text
        }
    
    def split_multi_tasks(self, content: str) -> List[str]:
        """
        Split content containing multiple tasks.
        
        Args:
            content: Content with multiple task markers
        
        Returns:
            List of individual task content strings
        """
        # Split by periods and find task occurrences
        parts = content.split('.')
        task_indices = [i for i, part in enumerate(parts) if 'task' in part.lower().strip()]
        
        if len(task_indices) <= 1:
            return [content]  # Single task or no tasks
        
        # Extract individual tasks
        tasks = []
        for i, task_index in enumerate(task_indices[:-1]):  # Exclude last 'Task'
            if i == 0:
                # First task: everything from start to first 'Task'
                task_content = '.'.join(parts[:task_index]).strip()
            else:
                # Subsequent tasks: from previous 'Task' to current 'Task'
                prev_task_index = task_indices[i-1]
                task_content = '.'.join(parts[prev_task_index+1:task_index]).strip()
            
            if task_content:  # Only add non-empty tasks
                tasks.append(task_content)
        
        logger.debug(f"  Split into {len(tasks)} tasks")
        return tasks if tasks else [content]
    
    def generate_title(
        self,
        content: str,
        category: str,
        project: str = "",
        max_length: int = 8
    ) -> str:
        """
        Generate AI-powered title for task or note.
        
        Shared logic used by all content types to eliminate duplication.
        
        Args:
            content: The content to generate title for
            category: "task" or "note"
            project: Project name (optional, provides context)
            max_length: Maximum words in title
        
        Returns:
            Generated title string
        """
        if category == "task":
            prompt = f"""
            Create a clean, descriptive title for this task ({max_length-2}-{max_length} words):
            
            Task: "{content[:200]}"
            Project: "{project}"
            
            Return ONLY the title, no quotes, no extra text.
            Follow Verb + Object + Context pattern.
            """
        else:  # note
            prompt = f"""
            Create a concise, descriptive title for this note ({max_length-2}-{max_length} words):
            
            {content[:500]}
            
            Focus on the MAIN TOPIC or KEY INSIGHT. Examples:
            - "Preserving Authentic Voice in Writing"
            - "Product Strategy Documentation Workflow"
            - "Integration and Elusiveness in Eudaimonia"
            
            Return ONLY the title, no quotes, no extra text.
            """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            
            title = response.choices[0].message.content.strip().strip('"').strip("'")
            logger.debug(f"  ✅ Generated title: '{title}'")
            return title
            
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            # Fallback to first words
            words = content.split()[:max_length]
            fallback_title = " ".join(words)
            if len(content.split()) > max_length:
                fallback_title += "..."
            return fallback_title
    
    def select_icon(
        self,
        title: str,
        project: str,
        original_content: str,
        router=None
    ) -> str:
        """
        Select appropriate icon for content.
        
        Shared logic to eliminate duplication across task/note processing.
        
        Args:
            title: Generated title
            project: Project name
            original_content: Original transcript (for keyword matching)
            router: IntelligentRouter instance (optional)
        
        Returns:
            Selected emoji icon
        """
        if router:
            return router.select_icon_for_analysis(title, project, original_content)
        
        # Fallback if no router provided
        return "⁉️"


