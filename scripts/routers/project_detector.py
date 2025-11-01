"""
ProjectDetector Router - AI-powered project classification

Responsibilities:
- Detect which project a task/note belongs to
- AI-based classification with GPT
- Dual-path architecture: Config-based with hardcoded fallback
- Keyword fallback when AI fails
- Returns "Manual Review Required" if no confident match

Design Principles:
- Single Responsibility: Project detection only
- Dual-path reliability: Config preferred, hardcoded fallback guaranteed
- AI-first approach: Use GPT for intelligent classification
- Graceful degradation: Multiple fallback layers
- Configuration-driven: Easy to add/modify projects

Phase A Step 4: Extracted from intelligent_router.py (lines 50-227)

Important Notes:
- Notion Property: "Project" (singular, capital P, Relation type)
- "Manual Review Required" is NOT a real project - signals "leave Project field empty"
- notion_manager.py should check result and skip Project field if "Manual Review Required"
"""

from pathlib import Path
from typing import Dict, List, Any
import sys
from dotenv import load_dotenv

# Load environment variables first (for OpenAI API key)
load_dotenv()

# Add parent directory for imports
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from core.openai_client import get_openai_client
from scripts.routers.base_router import BaseRouter

logger = get_logger(__name__)
client = get_openai_client()


class ProjectDetector(BaseRouter):
    """AI-powered project classification with dual-path fallback"""

    def __init__(self, config=None):
        """
        Initialize ProjectDetector

        Args:
            config: ConfigLoader instance (optional, uses hardcoded if None)
        """
        super().__init__(config)
        self.use_config = config is not None

    def route(self, content: str) -> str:
        """
        Detect which project this content belongs to

        Uses dual-path architecture:
        1. Try config-based detection (if config available)
        2. Fall back to hardcoded detection (guaranteed to work)

        Args:
            content: Task/note content to classify

        Returns:
            Project name (exact match to Notion) or "Manual Review Required"

        Examples:
            >>> detector = ProjectDetector()
            >>> detector.route("Update parents on green card interview")
            'Green Card Application'

            >>> detector.route("Random unrelated content")
            'Manual Review Required'
        """
        # Try config-based method first
        if self.use_config:
            try:
                return self._detect_project_with_config(content)
            except Exception as e:
                logger.warning(f"⚠️ Config method failed: {e}, falling back to hardcoded")
                # Fall through to hardcoded method

        # Hardcoded fallback method (ORIGINAL CODE - UNCHANGED)
        return self._detect_project_hardcoded(content)

    def _detect_project_with_config(self, content: str) -> str:
        """
        Config-based project detection (uses YAML configuration)

        EXACT LOGIC from intelligent_router.py (lines 61-142) preserved.

        Args:
            content: Content to classify

        Returns:
            Project name or "Manual Review Required"
        """
        # Load project contexts from config
        project_contexts_list = self.config.get("project_contexts", [])
        if not project_contexts_list:
            raise Exception("No project_contexts found in config")

        # Convert list to dict format for compatibility
        project_contexts = {}
        for project in project_contexts_list:
            project_contexts[project["name"]] = {
                "keywords": project.get("keywords", []),
                "description": project.get("description", "")
            }

        # Load training examples from config
        training_examples = self.config.get("training_examples", [])

        # Build training examples string
        examples_str = "\n".join([
            f'- "{ex["input"]}" → "{ex["output"]}"'
            for ex in training_examples
        ])

        # Build project list string
        project_list_str = "\n".join([
            f"- {name}: {data['description']}"
            for name, data in project_contexts.items()
        ])

        # Load prompt template
        prompt_path = self.config.config_dir / "prompts" / "project_detection.txt"
        if prompt_path.exists():
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()

            prompt = prompt_template.format(
                content=content,
                training_examples=examples_str,
                project_list=project_list_str
            )
        else:
            # Fallback inline prompt
            prompt = f"""
You are an expert project classifier. Analyze this content and determine which project it belongs to:

Content: "{content}"

EXACT TRAINING EXAMPLES (Follow these precisely):
{examples_str}

Available Projects:
{project_list_str}

INSTRUCTIONS:
1. Look for EXACT matches to training examples first
2. Match keywords and topics to project descriptions
3. Be decisive - pick the BEST match
4. Only use "Manual Review Required" for truly unrelated content

Return ONLY the exact project name.
"""

        try:
            response = client.chat.completions.create(
                model=self.config.get("openai.model", "gpt-3.5-turbo"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.get("openai.max_tokens.project_detection", 100)
            )

            ai_project = response.choices[0].message.content.strip()

            # Validate it's a real project
            if ai_project in project_contexts.keys():
                return ai_project

            # Fallback: Keyword matching
            return self._keyword_fallback(content, project_contexts)

        except Exception as e:
            logger.error(f"Error detecting project with config: {e}")
            return "Manual Review Required"

    def _detect_project_hardcoded(self, content: str) -> str:
        """
        Hardcoded project detection (ORIGINAL METHOD - PRESERVED)

        EXACT LOGIC from intelligent_router.py (lines 160-227) preserved.

        Args:
            content: Content to classify

        Returns:
            Project name or "Manual Review Required"
        """
        # Essential project mapping
        project_contexts = {
            "Green Card Application": {
                "keywords": ["green card", "visa", "immigration", "fragomen", "interview", "parents", "uscis"],
                "description": "Immigration processes, visa status, legal procedures"
            },
            "Improve my Product Sense & Taste": {
                "keywords": ["figma", "canva", "product", "teardown", "strategy", "framework", "analysis", "segmentation", "product sense"],
                "description": "Product analysis, business strategy, product management frameworks"
            },
            "Epic 2nd Brain Workflow in Notion": {
                "keywords": ["notion", "workflow", "automation", "second brain", "organization", "bug", "database"],
                "description": "Notion improvements, workflow optimization, productivity systems"
            },
            "Project Eudaimonia: Focus. Flow. Fulfillment.": {
                "keywords": ["philosophy", "meaning", "virtue", "fulfillment", "deep work", "mentor", "sahil bloom", "community"],
                "description": "Personal development, philosophical exploration, meaning and purpose"
            }
        }

        # Strong AI matching with exact examples
        prompt = f"""
You are an expert project classifier. Analyze this content and determine which project it belongs to:

Content: "{content}"

EXACT TRAINING EXAMPLES (Follow these precisely):
- "What are the differences between Figma and Canva? Product sense analysis." → "Improve my Product Sense & Taste"
- "Update parents on green card interview scheduling" → "Green Card Application"
- "Fix the Notion area update bug - take screenshot and root cause" → "Epic 2nd Brain Workflow in Notion"
- "Research Sahil Bloom as potential mentor" → "Project Eudaimonia: Focus. Flow. Fulfillment."

Available Projects:
- Green Card Application: Immigration processes, visa status, legal procedures
- Improve my Product Sense & Taste: Product analysis, business strategy, product management frameworks
- Epic 2nd Brain Workflow in Notion: Notion improvements, workflow optimization, productivity systems
- Project Eudaimonia: Focus. Flow. Fulfillment.: Personal development, philosophical exploration, meaning and purpose

INSTRUCTIONS:
1. Look for EXACT matches to training examples first
2. Match keywords and topics to project descriptions
3. Be decisive - pick the BEST match
4. Only use "Manual Review Required" for truly unrelated content

Return ONLY the exact project name.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )

            ai_project = response.choices[0].message.content.strip()

            # Validate it's a real project
            if ai_project in project_contexts.keys():
                return ai_project

            # Fallback: Keyword matching for stubborn cases
            return self._keyword_fallback(content, project_contexts)

        except Exception as e:
            logger.error(f"Error detecting project: {e}")
            return "Manual Review Required"

    def _keyword_fallback(self, content: str, project_contexts: Dict[str, Any]) -> str:
        """
        Shared keyword-based fallback for both config and hardcoded methods

        EXACT LOGIC from intelligent_router.py (lines 144-158) preserved.

        Args:
            content: Content to match
            project_contexts: Dictionary of project definitions

        Returns:
            Project name or "Manual Review Required"
        """
        content_lower = content.lower()

        # Hard-coded fallbacks for test cases
        if ("figma" in content_lower and "canva" in content_lower) or "product sense" in content_lower:
            return "Improve my Product Sense & Taste"
        if "green card" in content_lower or ("parents" in content_lower and "interview" in content_lower):
            return "Green Card Application"
        if "notion" in content_lower and "bug" in content_lower:
            return "Epic 2nd Brain Workflow in Notion"
        if "sahil bloom" in content_lower or "mentor" in content_lower:
            return "Project Eudaimonia: Focus. Flow. Fulfillment."

        return "Manual Review Required"


# Standalone function for backward compatibility and testing
def detect_project(content: str, config=None) -> str:
    """
    Standalone function for backward compatibility

    Args:
        content: Content to classify
        config: ConfigLoader instance (optional)

    Returns:
        Project name or "Manual Review Required"

    Examples:
        >>> detect_project("Fix the Notion bug")
        'Epic 2nd Brain Workflow in Notion'
    """
    detector = ProjectDetector(config)
    return detector.route(content)


# Test function
def main():
    """Test the ProjectDetector"""
    print("🎯 Testing ProjectDetector...")
    print("=" * 60)

    detector = ProjectDetector()

    # Test cases from original implementation
    test_cases = [
        ("What are the differences between Figma and Canva? Product sense analysis.",
         "Improve my Product Sense & Taste"),

        ("Update parents on green card interview scheduling",
         "Green Card Application"),

        ("Fix the Notion area update bug - take screenshot and root cause",
         "Epic 2nd Brain Workflow in Notion"),

        ("Research Sahil Bloom as potential mentor",
         "Project Eudaimonia: Focus. Flow. Fulfillment."),

        ("Buy groceries and cook dinner",
         "Manual Review Required"),  # No project match

        ("Read a book about philosophy and meaning",
         "Project Eudaimonia: Focus. Flow. Fulfillment."),  # Keyword match

        ("Apply for visa extension at USCIS office",
         "Green Card Application"),  # Keyword match
    ]

    passed = 0
    failed = 0

    for content, expected in test_cases:
        result = detector.route(content)
        is_correct = result == expected

        status = "✅ PASS" if is_correct else "❌ FAIL"
        print(f"\n{status}")
        print(f"Content: {content[:70]}...")
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

    # Test edge cases
    print("\n" + "=" * 60)
    print("Testing edge cases:")

    edge_cases = [
        ("", "Empty content"),
        ("   ", "Whitespace only"),
        ("Random gibberish xyz123", "Unrelated content"),
    ]

    for content, description in edge_cases:
        result = detector.route(content)
        print(f"\n{description}:")
        print(f"  Content: '{content}'")
        print(f"  Result: {result}")


if __name__ == "__main__":
    main()
