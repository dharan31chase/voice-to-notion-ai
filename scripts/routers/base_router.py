#!/usr/bin/env python3
"""
Base Router Class
Abstract base class for all routing components.

Purpose:
- Enforce consistent interface across all routers
- Make routers easy to test and swap
- Self-documenting code pattern
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pathlib import Path
import sys

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.config_loader import ConfigLoader
from core.logging_utils import get_logger


class BaseRouter(ABC):
    """
    Base class for all routing components.

    All routers should inherit from this class and implement the route() method.
    This ensures consistent behavior and makes testing easier.

    Example:
        class DurationEstimator(BaseRouter):
            def route(self, content: str) -> dict:
                # Duration estimation logic
                return {"duration": "MEDIUM", ...}
    """

    def __init__(self, config: Optional[ConfigLoader] = None):
        """
        Initialize router with optional configuration.

        Args:
            config: ConfigLoader instance (creates default if None)
        """
        self.config = config or ConfigLoader()
        self.logger = get_logger(self.__class__.__name__)
        self.logger.debug(f"✅ {self.__class__.__name__} initialized")

    @abstractmethod
    def route(self, *args, **kwargs) -> Any:
        """
        Main routing method - each router implements this differently.

        This is the core method that all routers must implement.
        The signature and return type will vary per router:

        - DurationEstimator.route(content: str) -> dict
        - TagDetector.route(content: str, title: str) -> list[str]
        - IconSelector.route(content: str, title: str) -> str
        - ProjectDetector.route(content: str) -> dict

        Returns:
            Router-specific output (dict, str, list, etc.)
        """
        pass
