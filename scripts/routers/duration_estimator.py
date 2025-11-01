#!/usr/bin/env python3
"""
Duration Estimator Router
Estimates task duration and calculates due dates.

Single Responsibility: Duration and due date calculation ONLY

Current behavior (preserves existing logic):
- QUICK: ≤2 min, due today
- MEDIUM: 15-30 min, due end of week (Friday)
- LONG: hours/days, due end of month

Future enhancements (configurable when needed):
- Add more categories (IDEAS_BUCKET, QUICK_ACTION, etc.)
- Custom due date logic per category
- Context-aware estimation
- Load prompt template from config
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path
import sys
import json

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from scripts.routers.base_router import BaseRouter
from core.config_loader import ConfigLoader
from core.openai_client import get_openai_client
from core.logging_utils import get_logger

logger = get_logger(__name__)


class DurationEstimator(BaseRouter):
    """
    Estimates task duration and calculates due dates.

    Uses AI (GPT-3.5-turbo) to analyze task complexity and assign:
    - Duration category (QUICK/MEDIUM/LONG)
    - Estimated minutes
    - Due date based on category
    - Reasoning for the estimate
    """

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize with configuration.

        Args:
            config: ConfigLoader instance (creates default if None)
        """
        super().__init__(config)
        self.openai_client = get_openai_client()

        # Load duration rules from config (available for future use)
        self.duration_rules = self.config.get('duration_rules', {})

    def route(self, content: str) -> Dict[str, any]:
        """
        Estimate duration and calculate due date for a task.

        This is the BaseRouter.route() implementation for DurationEstimator.

        Args:
            content: The task description to analyze

        Returns:
            Dictionary with:
            {
                'duration_category': 'QUICK|MEDIUM|LONG',
                'estimated_minutes': int,
                'due_date': 'YYYY-MM-DD',
                'reasoning': str
            }
        """
        return self.estimate(content)

    def estimate(self, content: str) -> Dict[str, any]:
        """
        Estimate duration and calculate due date for a task.

        This is the main method (same as route, for backward compatibility).

        Args:
            content: The task description to analyze

        Returns:
            Dictionary with:
            {
                'duration_category': 'QUICK|MEDIUM|LONG',
                'estimated_minutes': int,
                'due_date': 'YYYY-MM-DD',
                'reasoning': str
            }
        """
        # Calculate dates dynamically
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        day_name = today.strftime("%A")

        # Calculate end of week (Friday)
        days_until_friday = (4 - today.weekday()) % 7  # Friday is weekday 4
        if days_until_friday == 0:  # If today is Friday
            days_until_friday = 7   # Next Friday
        end_of_week = (today + timedelta(days=days_until_friday)).strftime("%Y-%m-%d")

        # Calculate end of month
        next_month = today.replace(day=28) + timedelta(days=4)
        end_of_month = (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")

        # Build AI prompt (hardcoded for now, will be configurable later)
        # TODO: Load prompt template from config/prompts/duration_estimation.txt
        prompt = f"""
Analyze this task and estimate duration: "{content}"

Duration Guidelines:
- QUICK (2 minutes or less): Calls, payments, quick Google searches, simple emails
- MEDIUM (15-30 minutes): Research tasks, planning, coordination, writing
- LONG (hours/days): Setup, installation, complex research, multi-step projects

Due Date Logic:
- QUICK tasks: Due today ({today_str})
- MEDIUM tasks: Due end of week ({end_of_week})
- LONG tasks: Due end of month ({end_of_month})

Today is {day_name}, {today_str}.

Return JSON format:
{{
    "duration_category": "QUICK|MEDIUM|LONG",
    "estimated_minutes": number,
    "due_date": "{today_str}",
    "reasoning": "Brief explanation"
}}
"""

        try:
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )

            result = json.loads(response.choices[0].message.content)
            logger.debug(f"  Duration: {result['duration_category']} ({result['estimated_minutes']} min)")
            return result

        except Exception as e:
            # Fallback to safe defaults on any error
            logger.error(f"❌ Error estimating duration: {e}")
            return {
                "duration_category": "MEDIUM",
                "estimated_minutes": 20,
                "due_date": end_of_week,
                "reasoning": "Default fallback due to estimation error"
            }


# Standalone testing
if __name__ == "__main__":
    from core.logging_utils import configure_root_logger

    # Configure logging for testing
    configure_root_logger("INFO")

    print("=" * 60)
    print("DurationEstimator Standalone Test")
    print("=" * 60)

    estimator = DurationEstimator()

    # Test cases covering different durations
    test_cases = [
        "Call dentist to schedule appointment",
        "Research best project management tools for team",
        "Set up new dev environment with Docker and configure CI/CD pipeline",
        "Send quick email to Jessica about dinner plans",
        "Create comprehensive documentation for the API"
    ]

    print("\nTesting duration estimation for various tasks:\n")

    for i, task in enumerate(test_cases, 1):
        print(f"{i}. Task: {task}")
        result = estimator.estimate(task)
        print(f"   → Category: {result['duration_category']}")
        print(f"   → Estimated: {result['estimated_minutes']} minutes")
        print(f"   → Due Date: {result['due_date']}")
        print(f"   → Reasoning: {result['reasoning']}")
        print()

    print("=" * 60)
    print("✅ DurationEstimator test complete")
    print("=" * 60)
