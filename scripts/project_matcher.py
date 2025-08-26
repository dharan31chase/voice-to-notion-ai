#!/usr/bin/env python3
"""
Project matching module for fuzzy matching extracted project names
against the actual project list. Supports both hardcoded and future database-driven lists.
"""

import difflib
from typing import List, Optional

class ProjectMatcher:
    def __init__(self):
        self._project_list = None
        self._similarity_threshold = 0.8  # 80% similarity threshold
    
    def get_project_list(self) -> List[str]:
        """
        Get the current project list. 
        Future: This will query the Notion database.
        Current: Returns hardcoded list.
        """
        if self._project_list is None:
            self._project_list = [
                "Green Card Application",
                "Welcoming our Baby",
                "Project 2035 - Zen Product Craftsman",
                "Home Remodel",
                "AI Ethics / Sci Author Extraordinaire",
                "Legendary Seed-stage Investor",
                "Tinker with Claude",
                "Nutrition & Morning Routine",
                "India Wedding Planning",
                "Epic 2nd Brain Workflow in Notion",
                "Lume Coaching Notes & Meetings",
                "Project Eudaimonia: Focus. Flow. Fulfillment.",
                "Life Admin HQ",
                "Improve my Product Sense & Taste",
                "Woodworking Projects"
            ]
        return self._project_list
    
    def fuzzy_match_project(self, extracted_project_name: str) -> str:
        """
        Fuzzy match extracted project name against actual project list.
        
        Args:
            extracted_project_name: Project name extracted from transcript
            
        Returns:
            Matched project name from actual list, or "Manual Review Required" if no match
        """
        if not extracted_project_name or not extracted_project_name.strip():
            return "Manual Review Required"
        
        extracted = extracted_project_name.strip()
        actual_projects = self.get_project_list()
        
        # Try exact match first (case insensitive)
        for project in actual_projects:
            if extracted.lower() == project.lower():
                return project
        
        # Try partial word matching (more flexible)
        extracted_words = extracted.lower().split()
        
        # Track best partial match
        best_partial_match = None
        best_partial_score = 0
        
        for project in actual_projects:
            project_words = project.lower().split()
            
            # Check if all extracted words are found in project
            matches = 0
            exact_matches = 0
            
            for word in extracted_words:
                # Handle number variations (2nd vs Second, etc.)
                normalized_word = self._normalize_word(word)
                for project_word in project_words:
                    normalized_project_word = self._normalize_word(project_word)
                    # More precise matching to avoid false positives
                    if (word.lower() == project_word.lower() or  # Exact match
                        normalized_word == normalized_project_word or  # Normalized exact match
                        (len(word) >= 3 and word.lower() in project_word.lower()) or  # Word is substring of project word
                        (len(project_word) >= 3 and project_word.lower() in word.lower())):  # Project word is substring of word
                        matches += 1
                        # Check for exact word match (higher priority)
                        if word.lower() == project_word.lower():
                            exact_matches += 1
                        break
            
            # Calculate match score with bonus for exact matches
            match_score = matches / len(extracted_words) if extracted_words else 0
            exact_bonus = exact_matches / len(extracted_words) if extracted_words else 0
            total_score = match_score + exact_bonus * 0.5  # Bonus for exact matches
            
            # If most words match, consider it a potential match
            if match_score >= 0.7:  # 70% of words must match
                if total_score > best_partial_score:
                    best_partial_score = total_score
                    best_partial_match = project
        
        if best_partial_match:
            print(f"🔍 Partial matched '{extracted}' → '{best_partial_match}' (score: {best_partial_score:.2f})")
            return best_partial_match
        
        # Try fuzzy matching as fallback
        best_match = None
        best_ratio = 0
        
        for project in actual_projects:
            # Use difflib for fuzzy string matching
            ratio = difflib.SequenceMatcher(None, extracted.lower(), project.lower()).ratio()
            
            if ratio > best_ratio and ratio >= self._similarity_threshold:
                best_ratio = ratio
                best_match = project
        
        if best_match:
            print(f"🔍 Fuzzy matched '{extracted}' → '{best_match}' (similarity: {best_ratio:.2f})")
            return best_match
        else:
            print(f"❌ No match found for '{extracted}' (best similarity: {best_ratio:.2f})")
            return "Manual Review Required"
    
    def set_similarity_threshold(self, threshold: float):
        """Set the similarity threshold for fuzzy matching (0.0 to 1.0)"""
        if 0.0 <= threshold <= 1.0:
            self._similarity_threshold = threshold
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")
    
    def refresh_project_list(self):
        """Force refresh of project list (useful for future database integration)"""
        self._project_list = None
    
    def _normalize_word(self, word: str) -> str:
        """Normalize word for better matching (handle numbers, etc.)"""
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

# Global instance for easy access
project_matcher = ProjectMatcher()

def fuzzy_match_project(extracted_project_name: str) -> str:
    """
    Convenience function for fuzzy project matching.
    
    Args:
        extracted_project_name: Project name extracted from transcript
        
    Returns:
        Matched project name or "Manual Review Required"
    """
    return project_matcher.fuzzy_match_project(extracted_project_name)

def test_project_matching():
    """Test the fuzzy matching functionality"""
    print("🧪 Testing Project Matching")
    print("=" * 50)
    
    test_cases = [
        # Exact matches
        ("Life Admin HQ", "Life Admin HQ"),
        ("Green Card Application", "Green Card Application"),
        
        # Fuzzy matches
        ("Product Craftsman", "Project 2035 - Zen Product Craftsman"),
        ("Product Sense", "Improve my Product Sense & Taste"),
        ("Second Brain", "Epic 2nd Brain Workflow in Notion"),
        ("Eudaimonia", "Project Eudaimonia: Focus. Flow. Fulfillment."),
        ("Baby", "Welcoming our Baby"),
        ("Home", "Home Remodel"),
        
        # No matches
        ("Email plumber", "Manual Review Required"),
        ("Random project", "Manual Review Required"),
        ("", "Manual Review Required"),
    ]
    
    results = []
    
    for input_name, expected in test_cases:
        result = fuzzy_match_project(input_name)
        success = result == expected
        results.append(success)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: '{input_name}' → '{result}' (expected: '{expected}')")
    
    # Summary
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n📊 Results: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 Excellent fuzzy matching!")
        return True
    else:
        print("⚠️ Some issues to address")
        return False

if __name__ == "__main__":
    test_project_matching()
