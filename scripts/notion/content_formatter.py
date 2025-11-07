"""
Content Formatter Module - Phase 5.1

Responsibilities:
- Clean and format task titles
- Organize task content (remove meta-commentary)
- Organize note content (preserve voice)
- Chunk long content for Notion's 2000 character limit
- Future: Confidence scoring for Epic 2nd Brain Workflow

Does NOT handle:
- Notion API calls (NotionClientWrapper)
- Task/Note creation logic (TaskCreator/NoteCreator)
- Routing decisions (NotionManager)
"""

import re
from typing import List, Dict, Optional
from datetime import datetime

# Import shared logging
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger

logger = get_logger(__name__)


class ContentFormatter:
    """Formats content for Notion entries with confidence scoring."""

    def __init__(self, openai_client=None):
        """
        Initialize content formatter.

        Args:
            openai_client: Optional OpenAI client for AI-powered formatting
                          If None, will import from intelligent_router
        """
        self.openai_client = openai_client

    def organize_task_content(self, content: str) -> Dict[str, any]:
        """
        Clean task content while removing meta-commentary but preserving context.

        Future-proofed for Epic 2nd Brain Workflow with confidence scoring.

        Args:
            content: Raw task content to format

        Returns:
            Dict with formatted content and metadata:
            {
                "formatted_text": str,
                "confidence_score": float (0.0-1.0),
                "needs_review": bool,
                "review_reasons": List[str]
            }
        """
        # Remove common prompt artifacts
        meta_patterns = [
            "I recorded a message instructing you to",
            "I recorded a message asking you to",
            "I recorded a message telling you to",
            "This task is important because it will help",
            "The user wants to",
            "The user needs to",
            "The recording says to",
            "I need you to",
            "Please help me",
            "Remember to",
            "Don't forget to",
        ]

        cleaned_content = content
        pattern_matches = 0
        for pattern in meta_patterns:
            if re.search(pattern, cleaned_content, flags=re.IGNORECASE):
                pattern_matches += 1
            cleaned_content = re.sub(pattern, "", cleaned_content, flags=re.IGNORECASE)

        # Calculate initial confidence (more meta-patterns = lower confidence)
        confidence_score = max(0.5, 1.0 - (pattern_matches * 0.1))

        # AI-powered cleanup
        prompt = f"""
Format this task content by removing ALL meta-commentary while keeping the actual task details:

"{cleaned_content}"

REMOVE:
- "I recorded a message..." phrases
- "This task is important because..." explanations
- Instructions about formatting
- Meta-commentary about what you should do

KEEP:
- The actual task details and requirements
- Context that explains WHY this matters
- Specific constraints or deadlines
- Any insights or reasoning that adds value

Return ONLY the clean, formatted task context.
"""

        formatted_text = cleaned_content.strip()
        review_reasons = []

        try:
            # Import OpenAI client if not provided
            if self.openai_client is None:
                from core.openai_client import get_openai_client
                self.openai_client = get_openai_client()

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )

            formatted_text = response.choices[0].message.content.strip()

            # Boost confidence if AI formatting succeeded
            confidence_score = min(1.0, confidence_score + 0.1)

        except Exception as e:
            logger.warning(f"Error organizing task content: {e}")
            review_reasons.append("ai_formatting_failed")
            confidence_score *= 0.9  # Slight confidence penalty

        # Determine if review needed (future Epic 2nd Brain Workflow)
        needs_review = confidence_score < 0.7 or len(review_reasons) > 0

        if needs_review and not review_reasons:
            review_reasons.append("low_confidence_score")

        return {
            "formatted_text": formatted_text,
            "confidence_score": round(confidence_score, 2),
            "needs_review": needs_review,
            "review_reasons": review_reasons
        }

    def organize_note_content(self, content: str) -> Dict[str, any]:
        """
        Preserve original note content with only basic formatting.

        Future-proofed for Epic 2nd Brain Workflow with confidence scoring.

        Args:
            content: Raw note content to format

        Returns:
            Dict with formatted content and metadata
        """
        # Just do basic cleanup - NO AI processing to preserve voice
        cleaned_content = content

        # Only fix obvious formatting issues
        # Remove multiple spaces
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)

        # Add paragraph breaks at obvious points (after periods followed by capital letters)
        cleaned_content = re.sub(r'\. ([A-Z])', r'.\n\n\1', cleaned_content)

        # Notes always have high confidence (minimal formatting = preserve voice)
        confidence_score = 0.95

        review_reasons = []
        needs_review = False

        # Check if note is very short (might be unclear)
        if len(cleaned_content.strip()) < 50:
            confidence_score = 0.7
            review_reasons.append("very_short_content")
            needs_review = True

        return {
            "formatted_text": cleaned_content.strip(),
            "confidence_score": confidence_score,
            "needs_review": needs_review,
            "review_reasons": review_reasons
        }

    def clean_task_title(self, title: str) -> Dict[str, any]:
        """
        Clean and format title to Verb + Object + Context pattern.

        Future-proofed for Epic 2nd Brain Workflow with confidence scoring.

        Args:
            title: Raw task title to clean

        Returns:
            Dict with formatted title and metadata
        """
        # Common spelling corrections
        corrections = {
            "tremor": "trimmer",
            "calender": "calendar",
            "recieve": "receive",
            "jessie": "Jessi",
            "jessy": "Jessi",
        }

        # Apply corrections to title
        clean_title = title
        corrections_applied = 0
        for wrong, right in corrections.items():
            if wrong in clean_title.lower():
                corrections_applied += 1
            clean_title = clean_title.replace(wrong, right)

        # Simple, direct prompt to ensure Verb + Object + Context format
        prompt = f"""
Format this task title to follow the pattern: [Verb] + [Object] + [Essential Context]

Current title: "{clean_title}"

RULES:
1. Start with an action verb (Fix, Buy, Research, Call, Schedule, Review, etc.)
2. Follow with the specific object/target
3. Keep essential context like project names or locations
4. Aim for 5-8 words when context is needed
5. DO NOT add quotation marks around the title

Return ONLY the formatted title without quotes.
"""

        formatted_title = clean_title
        confidence_score = 0.8
        review_reasons = []

        try:
            # Import OpenAI client if not provided
            if self.openai_client is None:
                from core.openai_client import get_openai_client
                self.openai_client = get_openai_client()

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )

            # Strip any quotes that GPT might add
            formatted_title = response.choices[0].message.content.strip()
            formatted_title = formatted_title.strip('"').strip("'")

            # Boost confidence if AI formatting succeeded
            confidence_score = 0.9

        except Exception as e:
            logger.warning(f"Error cleaning title: {e}")
            review_reasons.append("ai_formatting_failed")
            confidence_score = 0.7

        # Check if title is too short (might be unclear)
        if len(formatted_title.split()) < 3:
            confidence_score *= 0.9
            review_reasons.append("short_title")

        # Check if title starts with a verb (basic validation)
        action_verbs = ["fix", "buy", "call", "schedule", "review", "update", "create",
                       "send", "research", "contact", "order", "setup", "configure"]
        first_word = formatted_title.split()[0].lower() if formatted_title else ""
        if first_word not in action_verbs:
            confidence_score *= 0.95
            review_reasons.append("missing_action_verb")

        needs_review = confidence_score < 0.7 or len(review_reasons) > 0

        return {
            "formatted_text": formatted_title,
            "confidence_score": round(confidence_score, 2),
            "needs_review": needs_review,
            "review_reasons": review_reasons
        }

    def chunk_content(self, content: str, max_length: int = 1800) -> List[str]:
        """
        Split long content into chunks that fit Notion's 2000 character limit.

        Args:
            content: Content to chunk
            max_length: Maximum chunk size (default 1800 to be safe)

        Returns:
            List of content chunks
        """
        if len(content) <= max_length:
            return [content]

        chunks = []
        words = content.split()
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_length and current_chunk:
                # Start new chunk
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length

        # Add remaining chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def create_content_blocks(self, content: str, content_type: str = "task") -> List[Dict]:
        """
        Create Notion content blocks from formatted content.

        Args:
            content: Formatted content text
            content_type: "task" or "note"

        Returns:
            List of Notion block dictionaries
        """
        # Chunk content if needed
        chunks = self.chunk_content(content)

        # Create content blocks
        blocks = []
        for chunk in chunks:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": chunk}}]
                }
            })

        return blocks
