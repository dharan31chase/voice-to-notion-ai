"""
Task Analyzer Module
Analyzes task content with AI-powered title generation and content preservation.

Features:
- Short content (<800 words): Full AI analysis
- Long content (>800 words): Preserve original, title only
- Uses shared helpers from ContentParser (DRY)
- Handles single and multiple tasks
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from parsers.content_parser import ContentParser
from parsers.project_extractor import ProjectExtractor
from scripts.project_matcher import ProjectMatcher

logger = logging.getLogger(__name__)


class TaskAnalyzer:
    """
    Analyzes task content with content preservation for long transcripts.
    
    Dependencies injected for testability.
    """
    
    def __init__(
        self,
        parser: Optional[ContentParser] = None,
        project_matcher: Optional[ProjectMatcher] = None,
        router=None
    ):
        """
        Initialize task analyzer with dependencies.
        
        Args:
            parser: ContentParser for shared helpers (generate_title, select_icon)
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
        
        logger.debug(f"TaskAnalyzer initialized with preservation threshold: {self.preservation_threshold} words")
    
    def analyze_single(self, content: str, project: str = "", manual_review: bool = False) -> Dict[str, Any]:
        """
        Analyze single task with content preservation logic.
        
        Args:
            content: Task content to analyze
            project: Pre-extracted project name (optional)
            manual_review: Force manual review flag
        
        Returns:
            Dict with task analysis results
        """
        logger.debug(f"Analyzing single task ({len(content.split())} words)")
        
        # Extract project if not provided
        if not project:
            project, proj_confidence = self.project_extractor.extract_project(content)
            if project == "Manual Review Required":
                manual_review = True
                project = ""
        
        # Clean up content
        task_content = content.strip()
        if task_content.endswith('.'):
            task_content = task_content[:-1].strip()
        
        # Check word count for preservation logic
        word_count = len(task_content.split())
        
        if word_count > self.preservation_threshold:
            # LONG CONTENT: Preserve mode - only generate title from excerpt
            logger.info(f"📝 Long task content ({word_count} words) - using preservation mode")
            
            # Generate title from first part only (don't overwhelm AI with long content)
            excerpt = ' '.join(task_content.split()[:200])  # First 200 words
            title = self.parser.generate_title(excerpt, "task", project, max_length=8)
            
            # Select icon based on content
            icon = self.parser.select_icon(title, project, task_content, self.router)
            
            return {
                "category": "task",
                "title": title,
                "icon": icon,
                "content": task_content,  # FULL ORIGINAL PRESERVED
                "action_items": [],
                "key_insights": [],
                "confidence": "high" if not manual_review else "low",
                "project": project,
                "manual_review": manual_review,
                "preserved": True,  # Flag indicating preservation mode
                "word_count": word_count,
                "ai_enhanced": False
            }
        else:
            # SHORT CONTENT: Full AI analysis
            logger.debug(f"Standard task analysis ({word_count} words)")
            
            # Generate full title
            title = self.parser.generate_title(task_content, "task", project, max_length=8)
            
            # Select icon
            icon = self.parser.select_icon(title, project, task_content, self.router)
            
            return {
                "category": "task",
                "title": title,
                "icon": icon,
                "content": task_content,
                "action_items": [],
                "key_insights": [],
                "confidence": "high" if not manual_review else "low",
                "project": project,
                "manual_review": manual_review,
                "preserved": False,
                "word_count": word_count,
                "ai_enhanced": True
            }
    
    def analyze_multiple(
        self,
        content: str,
        parts: List[str],
        task_indices: List[int],
        project: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple tasks from single transcript.
        
        Args:
            content: Full transcript content
            parts: Content split by periods
            task_indices: Indices where 'task' keyword appears
            project: Pre-extracted project name (shared across tasks)
        
        Returns:
            List of task analysis dicts
        """
        logger.debug(f"Analyzing multiple tasks ({len(task_indices)-1} tasks found)")
        
        # Extract shared project if not provided
        if not project:
            project, proj_confidence = self.project_extractor.extract_project(content)
            manual_review_needed = (project == "Manual Review Required")
            if manual_review_needed:
                project = ""
        else:
            manual_review_needed = False
        
        tasks = []
        
        # Process each task
        for i, task_index in enumerate(task_indices[:-1]):  # Exclude last 'Task'
            if i == 0:
                # First task: everything from start to first 'Task'
                task_content = '.'.join(parts[:task_index]).strip()
            else:
                # Subsequent tasks: from previous 'Task' to current 'Task'
                prev_task_index = task_indices[i-1]
                task_content = '.'.join(parts[prev_task_index+1:task_index]).strip()
            
            if not task_content:  # Skip empty tasks
                continue
            
            # Clean up
            if task_content.endswith('.'):
                task_content = task_content[:-1].strip()
            
            # Analyze this individual task (with preservation logic)
            task_analysis = self.analyze_single(
                task_content,
                project=project,
                manual_review=manual_review_needed
            )
            
            tasks.append(task_analysis)
        
        logger.debug(f"  Analyzed {len(tasks)} tasks")
        return tasks

