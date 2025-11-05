"""
FuzzyMatcher Module - Phase 5.2

Responsibilities:
- Perform exact, partial, and fuzzy matching of project names
- Handle aliases and word normalization
- Return confidence scores for matches

Does NOT handle:
- Caching (ProjectCache)
- Fetching from Notion (NotionProjectFetcher)
- Project detection (ProjectMatcher)
"""

import difflib
from typing import List, Dict, Optional

# Import shared utilities
import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from core.logging_utils import get_logger
from core.config_loader import ConfigLoader

logger = get_logger(__name__)


class FuzzyMatcher:
    """
    Fuzzy matching engine for project names and aliases.

    Performs multi-level matching:
    1. Exact match against project names (confidence: 1.0)
    2. Exact match against aliases (confidence: 0.95)
    3. Partial word matching against projects (confidence: 0.8-0.9)
    4. Partial word matching against aliases (confidence: 0.75-0.85)
    5. Fuzzy matching fallback (confidence: 0.0-0.7)
    """

    def __init__(self, project_cache, config: ConfigLoader = None):
        """
        Initialize fuzzy matcher.

        Args:
            project_cache: ProjectCache instance for lookups
            config: Optional ConfigLoader instance
        """
        self.cache = project_cache
        self.config = config or ConfigLoader()

        # Get threshold from config (default: 0.6 for more flexible matching)
        self.threshold = self.config.get("project_matching.fuzzy_threshold", 0.6)

    def match_project(self, extracted_name: str, available_projects: List[str]) -> str:
        """
        Enhanced fuzzy match extracted project name against actual project list and aliases.

        Args:
            extracted_name: Project name extracted from transcript
            available_projects: List of actual project names

        Returns:
            Matched project name from actual list, or "Manual Review Required" if no match
        """
        if not extracted_name or not extracted_name.strip():
            return "Manual Review Required"

        extracted = extracted_name.strip()
        normalized_extracted = extracted.lower()

        # Track all potential matches with confidence scores
        matches = []

        # 1. Try exact match against project names (highest priority)
        for project in available_projects:
            if normalized_extracted == project.lower():
                matches.append({
                    "project": project,
                    "confidence": 1.0,
                    "type": "exact_project_name",
                    "source": project
                })
                logger.info(f"🎯 Exact project name match: '{extracted}' → '{project}' (confidence: 1.0)")
                return project  # Return immediately for exact matches

        # 2. Try exact match against aliases (high priority)
        alias_match = self.cache.get_project_by_alias(extracted)
        if alias_match:
            project_name = alias_match["name"]
            matches.append({
                "project": project_name,
                "confidence": 0.95,
                "type": "exact_alias",
                "source": f"alias: {extracted}"
            })
            logger.info(f"🎯 Exact alias match: '{extracted}' → '{project_name}' (confidence: 0.95)")
            return project_name

        # 3. Try partial word matching against project names
        project_matches = self._partial_match_against_projects(extracted, available_projects)
        matches.extend(project_matches)

        # 4. Try partial word matching against aliases
        alias_matches = self._partial_match_against_aliases(extracted)
        matches.extend(alias_matches)

        # 5. Try fuzzy matching as fallback
        fuzzy_match = self._fuzzy_match_fallback(extracted, available_projects)
        if fuzzy_match:
            matches.append(fuzzy_match)

        # Return best match if any found
        if matches:
            # Sort by confidence (highest first)
            matches.sort(key=lambda x: x["confidence"], reverse=True)
            best_match = matches[0]

            logger.info(
                f"🔍 Best match: '{extracted}' → '{best_match['project']}' "
                f"(type: {best_match['type']}, confidence: {best_match['confidence']:.2f})"
            )

            # Log all matches for debugging
            if len(matches) > 1:
                logger.debug(f"   Other matches: {[(m['project'], m['confidence']) for m in matches[1:3]]}")

            return best_match["project"]

        logger.warning(f"❌ No match found for '{extracted}'")
        return "Manual Review Required"

    def _partial_match_against_projects(self, extracted: str, actual_projects: List[str]) -> List[Dict]:
        """
        Partial word matching against project names.

        Args:
            extracted: Extracted project name
            actual_projects: List of actual project names

        Returns:
            List of match dictionaries with confidence scores
        """
        matches = []
        extracted_words = extracted.lower().split()

        for project in actual_projects:
            project_words = project.lower().split()

            # Check if extracted words are found in project
            matches_count = 0
            exact_matches = 0

            for word in extracted_words:
                normalized_word = self._normalize_word(word)
                for project_word in project_words:
                    normalized_project_word = self._normalize_word(project_word)

                    if (word.lower() == project_word.lower() or  # Exact match
                        normalized_word == normalized_project_word or  # Normalized exact match
                        (len(word) >= 3 and word.lower() in project_word.lower()) or  # Word is substring
                        (len(project_word) >= 3 and project_word.lower() in word.lower())):  # Project word is substring
                        matches_count += 1
                        if word.lower() == project_word.lower():
                            exact_matches += 1
                        break

            # Calculate match score
            match_score = matches_count / len(extracted_words) if extracted_words else 0
            exact_bonus = exact_matches / len(extracted_words) if extracted_words else 0
            total_score = match_score + exact_bonus * 0.5

            # If most words match, consider it a potential match
            if match_score >= 0.7:  # 70% threshold
                confidence = min(0.9, 0.8 + total_score * 0.1)  # 0.8-0.9 range
                matches.append({
                    "project": project,
                    "confidence": confidence,
                    "type": "partial_project_name",
                    "source": project
                })

        return matches

    def _partial_match_against_aliases(self, extracted: str) -> List[Dict]:
        """
        Partial word matching against aliases.

        Args:
            extracted: Extracted project name

        Returns:
            List of match dictionaries with confidence scores
        """
        matches = []
        extracted_words = extracted.lower().split()

        # Get all aliases from cache
        aliases = self.cache._cache["aliases"]

        for alias, project_name in aliases.items():
            alias_words = alias.split()

            # Check if extracted words are found in alias
            matches_count = 0
            exact_matches = 0

            for word in extracted_words:
                normalized_word = self._normalize_word(word)
                for alias_word in alias_words:
                    normalized_alias_word = self._normalize_word(alias_word)

                    if (word.lower() == alias_word.lower() or  # Exact match
                        normalized_word == normalized_alias_word or  # Normalized exact match
                        (len(word) >= 3 and word.lower() in alias_word.lower()) or  # Word is substring
                        (len(alias_word) >= 3 and alias_word.lower() in word.lower())):  # Alias word is substring
                        matches_count += 1
                        if word.lower() == alias_word.lower():
                            exact_matches += 1
                        break

            # Calculate match score
            match_score = matches_count / len(extracted_words) if extracted_words else 0
            exact_bonus = exact_matches / len(extracted_words) if extracted_words else 0
            total_score = match_score + exact_bonus * 0.5

            # If most words match, consider it a potential match
            if match_score >= 0.7:  # 70% threshold
                confidence = min(0.85, 0.75 + total_score * 0.1)  # 0.75-0.85 range (lower than project names)
                matches.append({
                    "project": project_name,
                    "confidence": confidence,
                    "type": "partial_alias",
                    "source": f"alias: {alias}"
                })

        return matches

    def _fuzzy_match_fallback(self, extracted: str, actual_projects: List[str]) -> Optional[Dict]:
        """
        Fuzzy matching as fallback using difflib.

        Args:
            extracted: Extracted project name
            actual_projects: List of actual project names

        Returns:
            Match dictionary or None
        """
        best_match = None
        best_ratio = 0

        for project in actual_projects:
            ratio = difflib.SequenceMatcher(None, extracted.lower(), project.lower()).ratio()
            if ratio > best_ratio and ratio > self.threshold:
                best_ratio = ratio
                best_match = project

        if best_match:
            return {
                "project": best_match,
                "confidence": best_ratio * 0.7,  # Scale down fuzzy match confidence
                "type": "fuzzy_match",
                "source": best_match
            }

        return None

    def _normalize_word(self, word: str) -> str:
        """
        Normalize word for better matching (handle numbers, etc.).

        Args:
            word: Word to normalize

        Returns:
            Normalized word
        """
        word = word.lower()

        # Handle number variations
        number_mappings = {
            '2nd': 'second',
            '3rd': 'third',
            '1st': 'first',
            '4th': 'fourth',
            '5th': 'fifth',
            '6th': 'sixth',
            '7th': 'seventh',
            '8th': 'eighth',
            '9th': 'ninth',
            '10th': 'tenth',
        }

        return number_mappings.get(word, word)

    def set_threshold(self, threshold: float):
        """
        Set the similarity threshold for fuzzy matching.

        Args:
            threshold: Threshold value (0.0 to 1.0)

        Raises:
            ValueError: If threshold is not between 0.0 and 1.0
        """
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
            logger.info(f"🎯 Fuzzy matching threshold set to {threshold}")
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")
