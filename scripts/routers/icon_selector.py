"""
IconSelector Router - Selects emoji icons for Notion entries

Responsibilities:
- Select appropriate emoji icon based on content analysis
- 3-tier fallback strategy: content → title → project
- Delegate pattern matching to IconManager
- Project name simplification for better matching

Design Principles:
- Single Responsibility: Icon selection only
- Thin wrapper: Delegates heavy lifting to IconManager
- Configuration-driven: Uses existing config/icon_mapping.json
- Extensible: Easy to add new icon selection strategies

Phase A Step 3: Extracted from intelligent_router.py (lines 267-342)
"""

from pathlib import Path
from typing import Optional
import sys

# Add parent directory for imports
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from scripts.routers.base_router import BaseRouter
from scripts.icon_manager import IconManager

logger = get_logger(__name__)


class IconSelector(BaseRouter):
    """Selects emoji icons for tasks and notes"""

    def __init__(self, config=None):
        """
        Initialize IconSelector

        Args:
            config: ConfigLoader instance (optional, not used currently)
        """
        super().__init__(config)
        self.icon_manager = IconManager()

    def route(self, title: str, project: str = "", content: str = "") -> str:
        """
        Select icon based on content, title, and project (3-tier fallback)

        This implements the EXACT logic from intelligent_router.py select_icon_for_analysis()
        to maintain backward compatibility.

        Args:
            title: AI-generated title for the task/note
            project: Project name (optional, used as fallback)
            content: Original transcript content (optional, primary source)

        Returns:
            Selected emoji icon or default icon

        Examples:
            >>> selector = IconSelector()
            >>> selector.route("Buy groceries", "", "Need to buy milk and eggs")
            '🛒'  # Matched from content keywords

            >>> selector.route("Fix home remodel bug", "Home Remodel", "")
            '🏠'  # Matched from title/project
        """
        try:
            # Tier 1: Try original content (primary source - where keywords live!)
            if content:
                icon = self.icon_manager.select_icon(content, title)
                if icon != self.icon_manager.default_icon:
                    logger.debug(f"✅ Icon matched from content: {icon}")
                    return icon

            # Tier 2: Try title only (secondary source)
            icon = self.icon_manager.select_icon("", title)
            if icon != self.icon_manager.default_icon:
                logger.debug(f"✅ Icon matched from title: {icon}")
                return icon

            # Tier 3: Try project name (tertiary source)
            if project and project != "Manual Review Required":
                # Simplify project name for better matching
                simplified_project = self._simplify_project_name(project)
                icon = self.icon_manager.select_icon("", simplified_project)
                if icon != self.icon_manager.default_icon:
                    logger.debug(f"✅ Icon matched from project: {icon}")
                    return icon

            # Tier 4: Return default icon
            logger.debug(f"ℹ️ Using default icon: {self.icon_manager.default_icon}")
            return self.icon_manager.default_icon

        except Exception as e:
            logger.warning(f"⚠️ Error in icon selection: {e}")
            return self.icon_manager.default_icon

    def _simplify_project_name(self, project: str) -> str:
        """
        Simplify project name for better icon matching

        Removes common prefixes and suffixes that don't help with keyword matching.

        EXACT LOGIC from intelligent_router.py (lines 305-342) preserved.

        Args:
            project: Full project name

        Returns:
            Simplified project name

        Examples:
            >>> selector = IconSelector()
            >>> selector._simplify_project_name("Project Eudaimonia: Focus. Flow. Fulfillment.")
            'Eudaimonia'

            >>> selector._simplify_project_name("Epic 2nd Brain Workflow in Notion")
            '2nd Brain'
        """
        simplified = project

        # Remove common suffixes
        suffixes_to_remove = [
            ": Focus. Flow. Fulfillment.",
            " - Zen Product Craftsman",
            " Application",
            " Workflow in Notion"
        ]

        for suffix in suffixes_to_remove:
            if simplified.endswith(suffix):
                simplified = simplified[:-len(suffix)]
                break

        # Remove common prefixes
        prefixes_to_remove = [
            "Project ",
            "Epic "
        ]

        for prefix in prefixes_to_remove:
            if simplified.startswith(prefix):
                simplified = simplified[len(prefix):]
                break

        return simplified.strip()


# Standalone function for backward compatibility and testing
def select_icon_for_analysis(title: str, project: str = "", content: str = "", config=None) -> str:
    """
    Standalone function for backward compatibility

    Args:
        title: AI-generated title
        project: Project name (optional)
        content: Original transcript content (optional)
        config: ConfigLoader instance (optional)

    Returns:
        Selected emoji icon

    Examples:
        >>> select_icon_for_analysis("Call mom", "", "Need to call mom about dinner")
        '📞'
    """
    selector = IconSelector(config)
    return selector.route(title, project, content)


# Test function
def main():
    """Test the IconSelector"""
    print("🎨 Testing IconSelector...")
    print("=" * 60)

    selector = IconSelector()

    # Test cases covering 3-tier fallback
    test_cases = [
        # (title, project, content, description)
        ("Call parents about green card", "Green Card Application",
         "Need to call parents about the interview",
         "Should match communication icon from content"),

        ("Fix home remodel bug", "",
         "Fix the lock installation bug in home remodel project",
         "Should match home icon from content"),

        ("Research Notion workflow", "Epic 2nd Brain Workflow in Notion",
         "Research Notion API integration for automation",
         "Should match from title or simplified project name"),

        ("Update documentation", "Project Eudaimonia: Focus. Flow. Fulfillment.",
         "",
         "Should match from simplified project name 'Eudaimonia'"),

        ("Buy groceries", "",
         "Need milk, eggs, bread from the store",
         "Should match from content keywords"),

        ("Generic task with no keywords", "",
         "Do something unspecific",
         "Should return default icon"),
    ]

    print(f"\n🔧 Default icon: {selector.icon_manager.default_icon}")
    print(f"📊 Total icon patterns: {len(selector.icon_manager.compiled_patterns)}\n")

    for title, project, content, description in test_cases:
        result = selector.route(title, project, content)

        print(f"{'='*60}")
        print(f"Description: {description}")
        print(f"Title: {title}")
        print(f"Project: {project}")
        print(f"Content: {content[:50]}{'...' if len(content) > 50 else ''}")
        print(f"🎨 Selected Icon: {result}")

        # Test project simplification if project provided
        if project:
            simplified = selector._simplify_project_name(project)
            if simplified != project:
                print(f"📝 Simplified Project: '{project}' → '{simplified}'")

    print("\n" + "=" * 60)
    print("✅ IconSelector test completed")

    # Test project name simplification
    print("\n" + "=" * 60)
    print("Testing project name simplification:")
    simplification_tests = [
        "Project Eudaimonia: Focus. Flow. Fulfillment.",
        "Epic 2nd Brain Workflow in Notion",
        "Green Card Application",
        "Improve my Product Sense & Taste - Zen Product Craftsman",
    ]

    for project in simplification_tests:
        simplified = selector._simplify_project_name(project)
        print(f"  '{project}'")
        print(f"  → '{simplified}'")
        print()


if __name__ == "__main__":
    main()
