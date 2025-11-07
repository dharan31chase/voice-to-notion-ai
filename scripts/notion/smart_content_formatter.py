"""
Smart Content Formatter - Phase 5.3

Responsibilities:
- Apply specialized AI prompts to format content based on content_type
- Load formatter configurations from YAML
- Handle formatting failures gracefully (fallback to original content)

Config-Driven Design:
- Keywords and prompts defined in config/content_formatters.yaml
- Easy to add new formatters without code changes
- Supports multiple content types: booknote, dailylog, meeting, etc.
"""

import sys
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

# Import shared utilities
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from core.openai_client import get_openai_client

logger = get_logger(__name__)


class SmartContentFormatter:
    """Routes content to appropriate AI formatter based on content_type."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize smart content formatter.

        Args:
            config_path: Path to content_formatters.yaml (defaults to config/content_formatters.yaml)
        """
        if config_path is None:
            config_path = parent_dir / "config" / "content_formatters.yaml"
        else:
            config_path = Path(config_path)

        self.config_path = config_path
        self.formatters_config = self._load_config()
        self.openai_client = get_openai_client()

        logger.debug(f"SmartContentFormatter initialized with {len(self.formatters_config.get('note_formatters', {}))} formatters")

    def _load_config(self) -> Dict[str, Any]:
        """Load formatters configuration from YAML."""
        try:
            if not self.config_path.exists():
                logger.warning(f"⚠️ Config file not found: {self.config_path}")
                return {}

            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            logger.debug(f"✅ Loaded formatters config: {self.config_path}")
            return config

        except Exception as e:
            logger.error(f"❌ Failed to load formatters config: {e}")
            return {}

    def format(self, content: str, content_type: Optional[str], word_count: int = 0) -> str:
        """
        Apply specialized formatting to content based on content_type.

        Args:
            content: Raw content to format
            content_type: Type of content (e.g., "booknote", "dailylog")
            word_count: Word count of content (for min_words check)

        Returns:
            Formatted content (or original if formatter not found/fails)
        """
        # No content_type specified - return as-is
        if not content_type:
            logger.debug("No content_type specified - skipping formatting")
            return content

        # Get formatter config
        note_formatters = self.formatters_config.get('note_formatters', {})
        formatter_config = note_formatters.get(content_type)

        if not formatter_config:
            logger.warning(f"⚠️ No formatter found for content_type: {content_type}")
            return content

        # Check min_words requirement
        min_words = formatter_config.get('min_words', 0)
        if word_count < min_words:
            logger.info(f"📋 Skipping {content_type} formatter: {word_count} words < {min_words} min")
            return content

        # Apply formatter
        logger.info(f"🎨 Applying {content_type} formatter (model: {formatter_config.get('model', 'gpt-3.5-turbo')})")
        return self._apply_formatter(content, formatter_config)

    def _apply_formatter(self, content: str, config: Dict[str, Any]) -> str:
        """
        Apply AI formatter with prompt template from config.

        Args:
            content: Content to format
            config: Formatter configuration dict

        Returns:
            Formatted content (or original if fails)
        """
        try:
            model = config.get('model', 'gpt-3.5-turbo')
            prompt_template = config.get('prompt_template', '')

            if not prompt_template:
                logger.error("❌ No prompt_template in formatter config")
                return content

            # Replace {content} placeholder in template
            prompt = prompt_template.replace('{content}', content)

            logger.debug(f"Calling OpenAI {model} for formatting...")

            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for consistent formatting
                max_tokens=16000  # Allow long book notes
            )

            formatted_content = response.choices[0].message.content.strip()

            logger.info(f"✅ Content formatted successfully ({len(formatted_content)} chars)")
            return formatted_content

        except Exception as e:
            logger.error(f"❌ Formatting failed: {e}")
            logger.warning(f"⚠️ Fallback: Using original content (unformatted)")
            return content  # Graceful fallback
