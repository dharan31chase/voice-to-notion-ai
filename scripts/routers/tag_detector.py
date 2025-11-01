"""
TagDetector Router - Detects task tags and note types

Responsibilities:
- Detect task tags (🤙 Communications, ❤️ Needs Jessica Input, etc.)
- Detect note types (🤝 Meeting Notes, 💡 Ideas, 📚 Book Notes, etc.)
- Keyword-based detection with pattern matching
- Validation against exact Notion values (case-sensitive, emoji-included)
- Multi-select support (can return multiple tags)

Design Principles:
- Single Responsibility: Tag detection only
- Configuration-driven: All patterns in YAML
- Exact value matching: Prevent tag drift in Notion
- Extensible: Easy to add new tags without code changes

Phase A Step 2: Extracted from intelligent_router.py (lines 247-279)
"""

from pathlib import Path
from typing import List, Dict, Any
import sys

# Add parent directory for imports
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from scripts.routers.base_router import BaseRouter

logger = get_logger(__name__)


class TagDetector(BaseRouter):
    """Detects tags for tasks and note types for notes"""

    def __init__(self, config=None):
        """
        Initialize TagDetector

        Args:
            config: ConfigLoader instance (optional, uses hardcoded if None)
        """
        super().__init__(config)
        self._load_tag_config()

    def _load_tag_config(self):
        """Load tag and note type configurations"""
        if self.config:
            try:
                # Load from config files
                # Note: task_tags.yaml defines "tags:" at top level
                # Note: note_types.yaml defines "note_types:" at top level
                self.task_tags = self.config.get("tags", {})
                self.note_types = self.config.get("note_types", {})

                # Handle None values (empty config files)
                if self.task_tags is None:
                    self.task_tags = {}
                if self.note_types is None:
                    self.note_types = {}

                logger.info(f"✅ Loaded {len(self.task_tags)} task tags, {len(self.note_types)} note types from config")
            except Exception as e:
                logger.warning(f"⚠️ Config loading failed: {e}, falling back to hardcoded")
                self.task_tags = self._get_hardcoded_task_tags()
                self.note_types = {}
        else:
            # Hardcoded fallback (same as current implementation)
            self.task_tags = self._get_hardcoded_task_tags()
            self.note_types = {}
            logger.warning("⚠️ Using hardcoded task tags (config unavailable)")

    def _get_hardcoded_task_tags(self) -> Dict[str, Any]:
        """
        Hardcoded task tags as fallback (matches current implementation)

        IMPORTANT: Uses exact Notion values with emojis
        """
        return {
            "Communications": {
                "notion_value": "🤙 Communications",
                "description": "Tasks involving actual communication with people",
                "detection": {
                    "type": "keyword",
                    "patterns": [
                        "call", "email", "text", "message", "phone",
                        "update parents", "contact", "coordinate with",
                        "reach out", "follow up with", "send to",
                        "notify", "inform", "tell"
                    ],
                    "requires_context": {
                        "people_indicators": [
                            "parents", "team", "client", "customer",
                            "person", "people", "someone", "them", "him", "her"
                        ]
                    }
                }
            },
            "NeedsJessicaInput": {
                "notion_value": "❤️ Needs Jessica Input",
                "description": "Tasks requiring Jessica's input or decision",
                "detection": {
                    "type": "keyword",
                    "keywords": [
                        "home remodel", "baby", "green card",
                        "major decision", "couple decision", "jessica"
                    ]
                }
            }
        }

    def route(self, content: str, content_type: str = "task") -> List[str]:
        """
        Detect tags/note types for the given content

        Args:
            content: Content to analyze
            content_type: "task" or "note" (determines which tags to detect)

        Returns:
            List of detected tag values (exact Notion values with emojis, case-sensitive)

        Examples:
            >>> detector = TagDetector()
            >>> detector.route("Call parents about green card interview", "task")
            ['🤙 Communications', '❤️ Needs Jessica Input']

            >>> detector.route("Email team about project update", "task")
            ['🤙 Communications']
        """
        if content_type == "task":
            return self._detect_task_tags(content)
        elif content_type == "note":
            return self._detect_note_types(content)
        else:
            logger.warning(f"⚠️ Unknown content_type: {content_type}, defaulting to task tags")
            return self._detect_task_tags(content)

    def _detect_task_tags(self, content: str) -> List[str]:
        """
        Detect task tags using keyword matching

        Args:
            content: Task content

        Returns:
            List of detected tag values (exact Notion values with emojis)
        """
        content_lower = content.lower()
        detected_tags = []

        for tag_name, tag_config in self.task_tags.items():
            if self._matches_tag(content_lower, tag_config):
                # Use exact Notion value (case-sensitive, emoji-included)
                notion_value = tag_config.get("notion_value", tag_name)
                detected_tags.append(notion_value)
                logger.debug(f"✅ Detected tag: {notion_value}")

        return detected_tags

    def _detect_note_types(self, content: str) -> List[str]:
        """
        Detect note types using keyword matching

        Args:
            content: Note content

        Returns:
            List of detected note type values (exact Notion values with emojis)
        """
        # Future implementation
        # For now, return empty list (no note type detection)
        logger.debug("ℹ️ Note type detection not yet implemented")
        return []

    def _matches_tag(self, content_lower: str, tag_config: Dict[str, Any]) -> bool:
        """
        Check if content matches tag detection patterns

        This implements the EXACT logic from intelligent_router.py detect_special_tags()
        to maintain backward compatibility.

        Args:
            content_lower: Lowercased content
            tag_config: Tag configuration dict

        Returns:
            True if content matches tag patterns
        """
        detection = tag_config.get("detection", {})
        detection_type = detection.get("type", "keyword")

        if detection_type == "keyword":
            # Get all patterns/keywords
            patterns = detection.get("patterns", [])
            keywords = detection.get("keywords", [])
            all_patterns = patterns + keywords

            # Check if any pattern matches
            matched = False
            for pattern in all_patterns:
                if pattern.lower() in content_lower:
                    matched = True
                    break

            if not matched:
                return False

            # Check context requirements (e.g., people indicators for Communications)
            requires_context = detection.get("requires_context", {})
            if requires_context:
                people_indicators = requires_context.get("people_indicators", [])
                if people_indicators:
                    # EXACT LOGIC from intelligent_router.py lines 263-269:
                    # Check if people are mentioned OR if pattern is explicit (call, email, etc.)
                    explicit_patterns = ["call", "email", "text", "message", "phone"]
                    has_explicit = any(p in content_lower for p in explicit_patterns)
                    has_people = any(ind.lower() in content_lower for ind in people_indicators)

                    if not (has_explicit or has_people):
                        return False

            return True

        # Future: Support AI-based detection
        logger.warning(f"⚠️ Unsupported detection type: {detection_type}")
        return False


# Standalone function for backward compatibility and testing
def detect_special_tags(content: str, config=None) -> List[str]:
    """
    Standalone function for backward compatibility

    Args:
        content: Content to analyze
        config: ConfigLoader instance (optional)

    Returns:
        List of detected tag values (exact Notion values with emojis)

    Examples:
        >>> detect_special_tags("Call parents about green card")
        ['🤙 Communications', '❤️ Needs Jessica Input']
    """
    detector = TagDetector(config)
    return detector.route(content, content_type="task")


# Test function
def main():
    """Test the TagDetector"""
    print("🏷️  Testing TagDetector...")
    print("=" * 60)

    detector = TagDetector()

    # Test cases from original implementation
    test_cases = [
        ("Call parents about green card interview", ["🤙 Communications", "❤️ Needs Jessica Input"]),
        ("Email team about project update", ["🤙 Communications"]),
        ("Update Notion bug fix documentation", []),
        ("Coordinate with Jessica on home remodel decisions", ["❤️ Needs Jessica Input"]),  # Only Jessica tag (not Communications)
        ("Research baby cribs and mattresses", ["❤️ Needs Jessica Input"]),
        ("Fix the authentication bug", []),
        ("Send message to client", ["🤙 Communications"]),
        ("Major decision about green card timing", ["❤️ Needs Jessica Input"]),
    ]

    passed = 0
    failed = 0

    for content, expected in test_cases:
        result = detector.route(content, "task")
        is_correct = set(result) == set(expected)

        status = "✅ PASS" if is_correct else "❌ FAIL"
        print(f"\n{status}")
        print(f"Content: {content}")
        print(f"Expected: {expected}")
        print(f"Got:      {result}")

        if is_correct:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed - review logic")


if __name__ == "__main__":
    main()
