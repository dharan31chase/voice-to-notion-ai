#!/usr/bin/env python3
"""
Project matching module for fuzzy matching extracted project names
against the actual project list. Supports both hardcoded and future database-driven lists.
"""

import difflib
import os
from typing import List, Optional, Dict, Any
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ProjectMatcher:
    def __init__(self):
        self._project_list = None
        self._project_data = None  # NEW: Store full project data
        self._similarity_threshold = 0.8  # 80% similarity threshold
        self._notion_client = None
        self._projects_db_id = os.getenv("PROJECTS_DATABASE_ID")
        
        # Initialize Notion client if token is available
        notion_token = os.getenv("NOTION_TOKEN")
        if notion_token and self._projects_db_id:
            try:
                self._notion_client = Client(auth=notion_token)
            except Exception as e:
                print(f"⚠️ Failed to initialize Notion client: {e}")
    
    def fetch_projects_from_notion(self) -> List[Dict[str, Any]]:
        """
        Query Notion Projects database and return active projects.
        
        Returns:
            List of project dictionaries with name, id, status, and aliases
        """
        if not self._notion_client or not self._projects_db_id:
            print("❌ Notion client or Projects database ID not available")
            return []
        
        try:
            # Filter for active projects (not archived, status in active categories)
            # Note: Status is a "status" type, Archived is "Archives" checkbox
            filter_params = {
                "and": [
                    {
                        "or": [
                            {
                                "property": "Status",
                                "status": {
                                    "equals": "In progress"
                                }
                            },
                            {
                                "property": "Status",
                                "status": {
                                    "equals": "Ongoing"
                                }
                            },
                            {
                                "property": "Status",
                                "status": {
                                    "equals": "Backlog"
                                }
                            },
                            {
                                "property": "Status",
                                "status": {
                                    "equals": "On Hold"
                                }
                            }
                        ]
                    },
                    {
                        "property": "Archives", 
                        "checkbox": {
                            "equals": False
                        }
                    }
                ]
            }
            
            # Query the database
            response = self._notion_client.databases.query(
                database_id=self._projects_db_id,
                filter=filter_params
            )
            
            projects = []
            for page in response["results"]:
                properties = page["properties"]
                
                # Extract project name (title field)
                name_property = properties.get("Name", {})
                name = ""
                if name_property.get("title") and len(name_property["title"]) > 0:
                    name = name_property["title"][0]["text"]["content"]
                
                # Extract status (status type)
                status_property = properties.get("Status", {})
                status = status_property.get("status", {}).get("name", "")
                
                # Extract aliases (text field)
                aliases_property = properties.get("Aliases", {})
                aliases_text = ""
                if aliases_property.get("rich_text") and len(aliases_property["rich_text"]) > 0:
                    aliases_text = aliases_property["rich_text"][0]["text"]["content"]
                
                # Parse aliases (split by comma, strip whitespace)
                aliases = []
                if aliases_text:
                    aliases = [alias.strip() for alias in aliases_text.split(",") if alias.strip()]
                
                if name:  # Only include projects with names
                    projects.append({
                        "name": name,
                        "id": page["id"],
                        "status": status,
                        "aliases": aliases,
                        "archived": False
                    })
            
            print(f"✅ Fetched {len(projects)} active projects from Notion")
            return projects
            
        except Exception as e:
            print(f"❌ Notion query failed: {e}")
            return []
    
    def get_project_list(self) -> List[str]:
        """
        Get the current project list. 
        Tries Notion first, falls back to hardcoded list.
        """
        if self._project_list is None:
            # Try to fetch from Notion first
            notion_projects = self.fetch_projects_from_notion()
            
            if notion_projects:
                # Use Notion projects
                self._project_data = notion_projects
                self._project_list = [project["name"] for project in notion_projects]
                print(f"📋 Using {len(self._project_list)} projects from Notion")
            else:
                # Fallback to hardcoded list
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
                print(f"📋 Using {len(self._project_list)} hardcoded projects (fallback)")
        
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
