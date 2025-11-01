#!/usr/bin/env python3
"""
Routers Package
Specialized routing components for intelligent content analysis.

Each router has a single responsibility:
- DurationEstimator: Task duration and due date calculation
- TagDetector: Tag detection and assignment
- IconSelector: Emoji icon selection
- ProjectDetector: Project assignment detection
"""

# Make routers easily importable
from .base_router import BaseRouter
from .duration_estimator import DurationEstimator

__all__ = ['BaseRouter', 'DurationEstimator']
