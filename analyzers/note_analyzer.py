"""
Note Analyzer Module
Analyzes note content with strong focus on preservation.

Features:
- Notes ALWAYS preserve original content (more important than tasks)
- Short notes (<800 words): AI title + light formatting
- Long notes (>800 words): AI title only, content untouched
- NO summarization ever (preserves insights and voice)
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from parsers.content_parser import ContentParser
from parsers.project_extractor import ProjectExtractor
from scripts.project_matcher import ProjectMatcher

logger = logging.getLogger(__name__)


class NoteAnalyzer:
    """
    Analyzes note content with preservation-first approach.

    Philosophy: Notes capture insights, reflections, and learnings.
    These are MORE valuable in original form than tasks.
    AI is used ONLY for title generation, never for summarization.
    """

    def __init__(
        self,
        parser: Optional[ContentParser] = None,
        project_matcher: Optional[ProjectMatcher] = None,
        router=None
    ):
        """
        Initialize note analyzer with dependencies.

        Args:
            parser: ContentParser for shared helpers
            project_matcher: ProjectMatcher for project extraction
            router: IntelligentRouter for icon selection
        """
        self.parser = parser or ContentParser()
        self.project_matcher = project_matcher or ProjectMatcher()
        self.project_extractor = ProjectExtractor(self.project_matcher)
        self.router = router

        # Get preservation threshold from config
        self.config = self.parser.config
        length_rules = self.config.get("content_length", {})
        self.preservation_threshold = length_rules.get("long_threshold", 800)

        logger.debug(f"NoteAnalyzer initialized with preservation threshold: {self.preservation_threshold} words")
    
    def analyze(self, content: str, project: str = "") -> Dict[str, Any]:
        """
        Analyze note content with preservation logic.

        Args:
            content: Note content to analyze
            project: Pre-extracted project name (optional)

        Returns:
            Dict with note analysis results
        """
        word_count = len(content.split())
        logger.debug(f"Analyzing note ({word_count} words)")

        # Extract project if not provided
        if not project:
            project, proj_confidence = self.project_extractor.extract_project(content)
            if project == "Manual Review Required":
                project = ""

        # Clean up content
        note_content = content.strip()
        if note_content.endswith('.'):
            note_content = note_content[:-1].strip()
        
        if word_count > self.preservation_threshold:
            # LONG NOTE: Maximum preservation mode
            logger.info(f"📚 Long note content ({word_count} words) - using preservation mode")
            logger.info(f"   (e.g., Paul Graham essay notes - preserve original insights)")
            
            # Generate title from first portion only
            excerpt = ' '.join(note_content.split()[:500])  # First 500 words for context
            title = self.parser.generate_title(excerpt, "note", project, max_length=8)
            
            # Select icon
            icon = self.parser.select_icon(title, project, note_content, self.router)
            
            return {
                "category": "note",
                "title": title,
                "icon": icon,
                "content": note_content,  # COMPLETE ORIGINAL PRESERVED
                "action_items": [],
                "key_insights": [],
                "confidence": "high",
                "project": project,
                "preserved": True,  # Flag: content is original, not AI-modified
                "word_count": word_count,
                "summarized": False,  # Explicitly not summarized
                "ai_enhanced": False  # Only title is AI-generated
            }
        else:
            # SHORT NOTE: Title generation + light formatting
            logger.debug(f"Standard note analysis ({word_count} words)")
            
            # Generate title from full content
            title = self.parser.generate_title(note_content, "note", project, max_length=8)
            
            # Select icon
            icon = self.parser.select_icon(title, project, note_content, self.router)
            
            return {
                "category": "note",
                "title": title,
                "icon": icon,
                "content": note_content,  # Still preserved, just shorter
                "action_items": [],
                "key_insights": [],
                "confidence": "high",
                "project": project,
                "preserved": True,  # Notes always preserve
                "word_count": word_count,
                "summarized": False,
                "ai_enhanced": True  # Title + light formatting
            }







