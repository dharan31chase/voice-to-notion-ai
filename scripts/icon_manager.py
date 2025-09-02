#!/usr/bin/env python3
"""
Icon Manager for AI transcript processing
Handles icon selection based on content keywords
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple

class IconManager:
    def __init__(self, config_path: str = "config/icon_mapping.json"):
        """
        Initialize IconManager with icon mapping configuration
        
        Args:
            config_path: Path to icon mapping JSON file
        """
        self.config_path = Path(config_path)
        self.icon_mapping = self._load_icon_mapping()
        self.compiled_patterns = self._compile_patterns()
        self.default_icon = self._get_default_icon()
        
        print(f"🎨 Loaded {len(self.compiled_patterns)} icon patterns from {self.config_path}")
    
    def _load_icon_mapping(self) -> Dict[str, str]:
        """Load icon mapping from config file with fallback to defaults"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                mapping = data.get("icon_mapping", {})
                print(f"✅ Loaded icon mapping: {len(mapping)} patterns")
                return mapping
        except FileNotFoundError:
            print(f"⚠️ Icon mapping file not found: {self.config_path}")
            print("📝 Using default icon mapping")
            return self._get_default_mapping()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing icon mapping file: {e}")
            print("📝 Using default icon mapping")
            return self._get_default_mapping()
        except Exception as e:
            print(f"❌ Unexpected error loading icon mapping: {e}")
            print("📝 Using default icon mapping")
            return self._get_default_mapping()
    
    def _get_default_icon(self) -> str:
        """Get default icon from config or use fallback"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("metadata", {}).get("default_icon", "⁉️")
        except:
            return "⁉️"
    
    def _compile_patterns(self) -> List[Tuple[re.Pattern, str, int]]:
        """
        Compile regex patterns for efficient matching
        
        Returns:
            List of (pattern, icon, keyword_length) tuples sorted by length (longest first)
        """
        patterns = []
        
        for keywords, icon in self.icon_mapping.items():
            # Split by | and create word boundary patterns
            keyword_list = keywords.split('|')
            for keyword in keyword_list:
                keyword = keyword.strip()
                if keyword:
                    # Create pattern with word boundaries for exact matching
                    pattern = re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE)
                    patterns.append((pattern, icon, len(keyword)))
        
        # Sort by keyword length (longest first) for priority
        patterns.sort(key=lambda x: x[2], reverse=True)
        
        return patterns
    
    def select_icon(self, content: str, title: str) -> str:
        """
        Select appropriate icon based on content and title
        
        Args:
            content: Original transcript content
            title: AI-generated title
            
        Returns:
            Selected emoji icon or default icon
        """
        try:
            # Combine title and content for keyword search
            search_text = f"{title} {content}".lower()
            
            # Find first matching pattern (longest keywords have priority)
            for pattern, icon, keyword_length in self.compiled_patterns:
                if pattern.search(search_text):
                    print(f"   🎨 Icon selected: {icon} (matched: {pattern.pattern})")
                    return icon
            
            # No matches found, return default
            print(f"   🎨 No icon match found, using default: {self.default_icon}")
            return self.default_icon
            
        except Exception as e:
            print(f"   ⚠️ Error in icon selection: {e}")
            return self.default_icon
    
    def _get_default_mapping(self) -> Dict[str, str]:
        """Fallback default mapping if config file is not available"""
        return {
            "ideas|brainstorm|concept": "💡",
            "groceries|buy|purchase|shop": "🛒",
            "email|send|forward": "📧",
            "call|phone|contact": "🤙",
            "text|message|sms": "💬",
            "ai|claude|automation|llm|agent|robot|bot|technology|software": "🤖",
            "product|design|build|craft": "📐",
            "baby|pregnancy|nursery|doula": "👼",
            "notion|workflow|second brain": "🧠",
            "research|study|analyze|review": "🔬",
            "trimmer|cut|scissors": "✂️",
            "meeting|calendar|schedule": "📅",
            "read|book|article": "📚",
            "fix|repair|maintenance": "🔧",
            "home remodel|architect|kitchen|adu|contractor": "🏡",
            "eudaimonia|philosophy|writing|author": "🌊"
        }
    
    def get_available_icons(self) -> Dict[str, str]:
        """Get all available icons for debugging/testing"""
        return self.icon_mapping.copy()
    
    def validate_mapping(self) -> bool:
        """Validate that icon mapping is properly formatted"""
        try:
            if not self.icon_mapping:
                print("❌ Icon mapping is empty")
                return False
            
            for keywords, icon in self.icon_mapping.items():
                if not keywords or not icon:
                    print(f"❌ Invalid mapping: '{keywords}' -> '{icon}'")
                    return False
                
                # Check if keywords contain valid characters
                if not re.match(r'^[a-zA-Z\s|]+$', keywords):
                    print(f"⚠️ Keywords contain special characters: '{keywords}'")
            
            print("✅ Icon mapping validation passed")
            return True
            
        except Exception as e:
            print(f"❌ Icon mapping validation failed: {e}")
            return False

# Test function for development
def test_icon_selection():
    """Test icon selection with sample content"""
    print("🧪 Testing Icon Selection")
    print("=" * 40)
    
    icon_manager = IconManager()
    
    test_cases = [
        ("AI research on product design", "Research AI Product Design"),
        ("Buy groceries for the week", "Weekly Grocery Shopping"),
        ("Fix the home remodel issues", "Home Remodel Fixes"),
        ("Email the team about the meeting", "Team Meeting Email"),
        ("Read the philosophy book", "Philosophy Reading"),
        ("Random content without keywords", "Random Task"),
    ]
    
    for content, title in test_cases:
        icon = icon_manager.select_icon(content, title)
        print(f"Content: '{content}'")
        print(f"Title: '{title}'")
        print(f"Icon: {icon}")
        print("-" * 20)

if __name__ == "__main__":
    test_icon_selection()
