#!/usr/bin/env python3
"""
Project matching module for fuzzy matching extracted project names
against the actual project list. Supports both hardcoded and future database-driven lists.
"""

import difflib
import os
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from notion_client import Client
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class ProjectCache:
    """In-memory cache for project data with file persistence"""
    
    def __init__(self, cache_file: str = ".cache/projects.json"):
        self.cache_file = Path(cache_file)
        self._cache = {
            "projects": {},  # project_name -> full_data
            "aliases": {},   # normalized_alias -> project_name
            "metadata": {
                "last_fetch": None,
                "cache_age_minutes": 0,
                "source": "none",
                "total_projects": 0,
                "fetch_duration_ms": 0,
                "last_successful_fetch": None,
                "failed_fetch_attempts": 0
            }
        }
        self._load_cache()
    
    def _load_cache(self):
        """Load cache from file if it exists"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self._cache = data
                    self._update_cache_age()
                    print(f"📋 Loaded {self._cache['metadata']['total_projects']} projects from cache ({self._cache['metadata']['cache_age_minutes']}min old)")
        except Exception as e:
            print(f"⚠️ Failed to load cache: {e}")
            self._cache = {
                "projects": {},
                "aliases": {},
                "metadata": {
                    "last_fetch": None,
                    "cache_age_minutes": 0,
                    "source": "none",
                    "total_projects": 0,
                    "fetch_duration_ms": 0,
                    "last_successful_fetch": None,
                    "failed_fetch_attempts": 0
                }
            }
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            # Create cache directory if it doesn't exist
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file, 'w') as f:
                json.dump(self._cache, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️ Failed to save cache: {e}")
    
    def _update_cache_age(self):
        """Update cache age based on last fetch time"""
        if self._cache["metadata"]["last_fetch"]:
            try:
                last_fetch = datetime.fromisoformat(self._cache["metadata"]["last_fetch"])
                age = datetime.now() - last_fetch
                self._cache["metadata"]["cache_age_minutes"] = int(age.total_seconds() / 60)
            except Exception:
                self._cache["metadata"]["cache_age_minutes"] = 999999  # Very old
    
    def _normalize_alias(self, alias: str) -> str:
        """Normalize alias for consistent matching"""
        return alias.lower().strip()
    
    def update_from_notion(self, projects_data: List[Dict[str, Any]], fetch_duration_ms: int = 0):
        """Update cache with data from Notion"""
        start_time = datetime.now()
        
        # Clear existing data
        self._cache["projects"] = {}
        self._cache["aliases"] = {}
        
        # Process each project
        for project in projects_data:
            name = project.get("name", "")
            if name:
                # Store project data
                self._cache["projects"][name] = project
                
                # Process aliases
                aliases = project.get("aliases", [])
                for alias in aliases:
                    normalized_alias = self._normalize_alias(alias)
                    if normalized_alias:
                        self._cache["aliases"][normalized_alias] = name
        
        # Update metadata
        self._cache["metadata"].update({
            "last_fetch": start_time.isoformat(),
            "cache_age_minutes": 0,
            "source": "notion",
            "total_projects": len(self._cache["projects"]),
            "fetch_duration_ms": fetch_duration_ms,
            "last_successful_fetch": start_time.isoformat(),
            "failed_fetch_attempts": 0
        })
        
        # Save to file
        self._save_cache()
        
        print(f"✅ Updated cache with {len(self._cache['projects'])} projects and {len(self._cache['aliases'])} aliases")
    
    def get_project_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get project by exact name match"""
        return self._cache["projects"].get(name)
    
    def get_project_by_alias(self, alias: str) -> Optional[Dict[str, Any]]:
        """Get project by normalized alias"""
        normalized_alias = self._normalize_alias(alias)
        project_name = self._cache["aliases"].get(normalized_alias)
        return self.get_project_by_name(project_name) if project_name else None
    
    def get_all_project_names(self) -> List[str]:
        """Get list of all project names (for backward compatibility)"""
        return list(self._cache["projects"].keys())
    
    def is_cache_fresh(self, max_age_minutes: int = 60) -> bool:
        """Check if cache is fresh enough to use"""
        self._update_cache_age()
        return self._cache["metadata"]["cache_age_minutes"] < max_age_minutes
    
    def should_refresh_cache(self, max_age_minutes: int = 60) -> bool:
        """Determine if cache should be refreshed"""
        cache_age = self._cache["metadata"]["cache_age_minutes"]
        total_projects = self._cache["metadata"]["total_projects"]
        
        # Always refresh if cache is empty
        if total_projects == 0:
            return True
        
        # Always refresh if cache is very old (>24 hours)
        if cache_age > 1440:  # 24 hours
            return True
        
        # Try to refresh if cache is moderately old (>max_age_minutes)
        if cache_age > max_age_minutes:
            return True
        
        # Use cached data if fresh
        return False
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache metadata for debugging"""
        self._update_cache_age()
        return self._cache["metadata"].copy()
    
    def clear_cache(self):
        """Clear cache and delete file"""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
            self._cache = {
                "projects": {},
                "aliases": {},
                "metadata": {
                    "last_fetch": None,
                    "cache_age_minutes": 0,
                    "source": "none",
                    "total_projects": 0,
                    "fetch_duration_ms": 0,
                    "last_successful_fetch": None,
                    "failed_fetch_attempts": 0
                }
            }
            print("🗑️ Cache cleared")
        except Exception as e:
            print(f"⚠️ Failed to clear cache: {e}")

class ProjectMatcher:
    def __init__(self):
        self._cache = ProjectCache()
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
        
        start_time = datetime.now()
        
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
            
            fetch_duration = int((datetime.now() - start_time).total_seconds() * 1000)
            print(f"✅ Fetched {len(projects)} active projects from Notion ({fetch_duration}ms)")
            
            # Update cache with new data
            self._cache.update_from_notion(projects, fetch_duration)
            
            return projects
            
        except Exception as e:
            print(f"❌ Notion query failed: {e}")
            # Increment failed fetch attempts
            self._cache._cache["metadata"]["failed_fetch_attempts"] += 1
            self._cache._save_cache()
            return []
    
    def get_project_list(self) -> List[str]:
        """
        Get the current project list. 
        Tries Notion first, falls back to hardcoded list.
        """
        # Check if we should refresh cache
        if self._cache.should_refresh_cache():
            notion_projects = self.fetch_projects_from_notion()
            
            if notion_projects:
                # Cache was updated with Notion data
                return self._cache.get_all_project_names()
            else:
                # Notion failed, check if we have cached data
                if self._cache._cache["metadata"]["total_projects"] > 0:
                    cache_age = self._cache._cache["metadata"]["cache_age_minutes"]
                    print(f"⚠️ Using {cache_age}min old cached data (Notion unavailable)")
                    return self._cache.get_all_project_names()
        
        # Use cached data if fresh or fallback to hardcoded
        if self._cache._cache["metadata"]["total_projects"] > 0:
            return self._cache.get_all_project_names()
        
        # Fallback to hardcoded list
        hardcoded_projects = [
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
        print(f"📋 Using {len(hardcoded_projects)} hardcoded projects (fallback)")
        return hardcoded_projects
    
    def fuzzy_match_project(self, extracted_project_name: str) -> str:
        """
        Enhanced fuzzy match extracted project name against actual project list and aliases.
        
        Args:
            extracted_project_name: Project name extracted from transcript
            
        Returns:
            Matched project name from actual list, or "Manual Review Required" if no match
        """
        if not extracted_project_name or not extracted_project_name.strip():
            return "Manual Review Required"
        
        extracted = extracted_project_name.strip()
        normalized_extracted = extracted.lower()
        
        # Get all project names and cache for alias lookups
        actual_projects = self.get_project_list()
        
        # Track all potential matches with confidence scores
        matches = []
        
        # 1. Try exact match against project names (highest priority)
        for project in actual_projects:
            if normalized_extracted == project.lower():
                matches.append({
                    "project": project,
                    "confidence": 1.0,
                    "type": "exact_project_name",
                    "source": project
                })
                print(f"🎯 Exact project name match: '{extracted}' → '{project}' (confidence: 1.0)")
                return project  # Return immediately for exact matches
        
        # 2. Try exact match against aliases (high priority)
        alias_match = self._cache.get_project_by_alias(extracted)
        if alias_match:
            project_name = alias_match["name"]
            matches.append({
                "project": project_name,
                "confidence": 0.95,
                "type": "exact_alias",
                "source": f"alias: {extracted}"
            })
            print(f"🎯 Exact alias match: '{extracted}' → '{project_name}' (confidence: 0.95)")
            return project_name
        
        # 3. Try partial word matching against project names
        project_matches = self._partial_match_against_projects(extracted, actual_projects)
        matches.extend(project_matches)
        
        # 4. Try partial word matching against aliases
        alias_matches = self._partial_match_against_aliases(extracted)
        matches.extend(alias_matches)
        
        # 5. Try fuzzy matching as fallback
        fuzzy_match = self._fuzzy_match_fallback(extracted, actual_projects)
        if fuzzy_match:
            matches.append(fuzzy_match)
        
        # Return best match if any found
        if matches:
            # Sort by confidence (highest first)
            matches.sort(key=lambda x: x["confidence"], reverse=True)
            best_match = matches[0]
            
            print(f"🔍 Best match: '{extracted}' → '{best_match['project']}' "
                  f"(type: {best_match['type']}, confidence: {best_match['confidence']:.2f})")
            
            # Log all matches for debugging
            if len(matches) > 1:
                print(f"   Other matches: {[(m['project'], m['confidence']) for m in matches[1:3]]}")
            
            return best_match["project"]
        
        print(f"❌ No match found for '{extracted}'")
        return "Manual Review Required"
    
    def _partial_match_against_projects(self, extracted: str, actual_projects: List[str]) -> List[Dict]:
        """Partial word matching against project names"""
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
        """Partial word matching against aliases"""
        matches = []
        extracted_words = extracted.lower().split()
        
        # Get all aliases from cache
        aliases = self._cache._cache["aliases"]
        
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
        """Fuzzy matching as fallback using difflib"""
        best_match = None
        best_ratio = 0
        
        for project in actual_projects:
            ratio = difflib.SequenceMatcher(None, extracted.lower(), project.lower()).ratio()
            if ratio > best_ratio and ratio > self._similarity_threshold:
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
