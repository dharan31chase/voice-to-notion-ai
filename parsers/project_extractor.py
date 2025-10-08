"""
Project Extractor Module
Extracts project names from transcript content using flexible pattern matching.

Patterns supported:
- <Content> <Project Name>. <Task/Note>
- <Content><Project Name> <Task/Note> (no period)
- Handles embedded periods, case insensitive, ignores junk words
"""

import sys
from pathlib import Path
from typing import Tuple, Optional
import logging

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from scripts.project_matcher import ProjectMatcher

logger = logging.getLogger(__name__)


class ProjectExtractor:
    """
    Extracts project names from transcript content with confidence scoring.
    
    Uses flexible word-combination approach with fuzzy matching fallback.
    """
    
    def __init__(self, project_matcher: Optional[ProjectMatcher] = None):
        """
        Initialize project extractor.
        
        Args:
            project_matcher: ProjectMatcher instance (creates new if not provided)
        """
        self.project_matcher = project_matcher or ProjectMatcher()
        self.ignored_keywords = ['task', 'note', 'project', 'tasks', 'notes', 'projects']
    
    def extract_project(self, content: str, category_keyword: Optional[str] = None) -> Tuple[str, float]:
        """
        Extract project name from content with confidence score.
        
        Args:
            content: The transcript content
            category_keyword: Optional category keyword position hint (e.g., 'task', 'note')
        
        Returns:
            Tuple of (project_name, confidence_score)
            - project_name: Extracted project or "Manual Review Required"
            - confidence_score: 0.0-1.0 (1.0 = exact match, 0.0 = no match)
        """
        logger.debug(f"🔍 Extracting project from: '{content[:50]}{'...' if len(content) > 50 else ''}'")
        
        # Step 1: Find category keyword position (if not provided, search for it)
        if category_keyword:
            last_keyword_pos = content.lower().rfind(category_keyword.lower())
        else:
            last_keyword_pos = self._find_last_category_keyword(content)
        
        if last_keyword_pos == -1:
            logger.debug("  ❌ No category keyword found, using full content")
            before_keyword = content
        else:
            # Extract text before the keyword (ignore everything after)
            before_keyword = content[:last_keyword_pos].strip()
            logger.debug(f"  Text before keyword: '{before_keyword}'")
        
        # Step 2: Try word combinations from end (1-5 words)
        words = before_keyword.split()
        if not words:
            logger.debug("  ❌ No words to extract project from")
            return "Manual Review Required", 0.0
        
        best_match = None
        best_confidence = 0.0
        
        for i in range(1, min(6, len(words) + 1)):  # 1-5 words
            potential_project = ' '.join(words[-i:])
            
            # Normalize: remove embedded periods and normalize spaces
            normalized_project = ' '.join(potential_project.replace('.', ' ').split())
            
            # Skip if the potential project is ONLY a keyword that should be ignored
            normalized_lower = normalized_project.lower().strip()
            if normalized_lower in self.ignored_keywords:
                logger.debug(f"  Skipping keyword: '{normalized_project}'")
                continue
            
            logger.debug(f"  Trying word combination: '{potential_project}'")
            
            # Use fuzzy matching with error handling
            try:
                matched_project = self.project_matcher.fuzzy_match_project(normalized_project)
                logger.debug(f"  Fuzzy match result: '{matched_project}'")
                
                if matched_project != "Manual Review Required":
                    # Calculate confidence based on match quality
                    confidence = self._calculate_match_confidence(normalized_project, matched_project, i)
                    
                    if confidence > best_confidence:
                        best_match = matched_project
                        best_confidence = confidence
                    
                    # If we found a very high confidence match, return immediately
                    if confidence >= 0.95:
                        logger.debug(f"  ✅ High confidence match: '{matched_project}' (confidence: {confidence:.2f})")
                        return matched_project, confidence
                        
            except Exception as e:
                logger.warning(f"  ⚠️ Fuzzy matching failed: {e}")
                continue
        
        # Return best match found, or manual review if none
        if best_match:
            logger.debug(f"  ✅ Best match: '{best_match}' (confidence: {best_confidence:.2f})")
            return best_match, best_confidence
        
        logger.debug("  ❌ No project match found")
        return "Manual Review Required", 0.0
    
    def _find_last_category_keyword(self, content: str) -> int:
        """Find position of last occurrence of task/note keyword"""
        content_lower = content.lower()
        
        # Find last occurrence, with priority: last keyword wins
        last_note_pos = content_lower.rfind('note')
        last_task_pos = content_lower.rfind('task')
        
        if last_note_pos > last_task_pos:
            return last_note_pos
        elif last_task_pos > last_note_pos:
            return last_task_pos
        else:
            return -1  # Not found
    
    def _calculate_match_confidence(self, input_text: str, matched_project: str, word_count: int) -> float:
        """
        Calculate confidence score for project match.
        
        Args:
            input_text: Original input text
            matched_project: Project name that was matched
            word_count: How many words were used (1-5)
        
        Returns:
            Confidence score 0.0-1.0
        """
        # Start with base confidence
        confidence = 0.6
        
        # Exact match (case-insensitive) = very high confidence
        if input_text.lower() == matched_project.lower():
            confidence = 1.0
        
        # Partial exact match
        elif input_text.lower() in matched_project.lower() or matched_project.lower() in input_text.lower():
            confidence = 0.9
        
        # Fuzzy match quality (longer matches are better)
        elif word_count >= 3:  # 3+ word match is more specific
            confidence = 0.85
        elif word_count == 2:  # 2-word match
            confidence = 0.75
        else:  # 1-word match (less specific)
            confidence = 0.65
        
        return confidence


def extract_project_from_content(content: str, project_matcher: ProjectMatcher) -> str:
    """
    Legacy function for backwards compatibility.
    
    Args:
        content: Transcript content
        project_matcher: ProjectMatcher instance
    
    Returns:
        Project name or "Manual Review Required"
    """
    extractor = ProjectExtractor(project_matcher)
    project, confidence = extractor.extract_project(content)
    return project

