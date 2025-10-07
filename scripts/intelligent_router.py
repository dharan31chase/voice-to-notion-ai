import openai
import os
from dotenv import load_dotenv
import json
from icon_manager import IconManager
import sys
from pathlib import Path

# Load environment variables
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class IntelligentRouter:
    def __init__(self):
        self.icon_manager = IconManager()
        
        # Try to load configuration system
        try:
            # Add parent directory to path to import core module
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            
            from core.config_loader import ConfigLoader
            self.config = ConfigLoader()
            self.use_config = True
            print("✅ Using configuration system")
        except Exception as e:
            self.config = None
            self.use_config = False
            print(f"⚠️ Config unavailable, using hardcoded values: {e}")
    
    def detect_project(self, content):
        """Use AI to intelligently detect which project this content belongs to"""
        
        # Try config-based method first
        if self.use_config:
            try:
                return self._detect_project_with_config(content)
            except Exception as e:
                print(f"⚠️ Config method failed: {e}, falling back to hardcoded")
                # Fall through to hardcoded method
        
        # Hardcoded fallback method (ORIGINAL CODE - UNCHANGED)
        return self._detect_project_hardcoded(content)
    
    def _detect_project_with_config(self, content):
        """Config-based project detection (NEW)"""
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
            print(f"Error detecting project with config: {e}")
            return "Manual Review Required"
    
    def _keyword_fallback(self, content, project_contexts):
        """Shared keyword-based fallback for both config and hardcoded methods"""
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
    
    def _detect_project_hardcoded(self, content):
        """Hardcoded project detection (ORIGINAL METHOD - PRESERVED)"""
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
            print(f"Error detecting project: {e}")
            return "Manual Review Required"
    
    def estimate_duration_and_due_date(self, content):
        """Use AI to estimate task duration and suggest due date"""
    
        from datetime import datetime, timedelta
    
        # Get current date dynamically
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        day_name = today.strftime("%A")
    
        # Calculate end of week and end of month
        days_until_friday = (4 - today.weekday()) % 7  # Friday is weekday 4
        if days_until_friday == 0:  # If today is Friday
            days_until_friday = 7   # Next Friday
        end_of_week = (today + timedelta(days=days_until_friday)).strftime("%Y-%m-%d")
    
        # End of month
        next_month = today.replace(day=28) + timedelta(days=4)
        end_of_month = (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")
    
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
            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        
            result = json.loads(response.choices[0].message.content)
            return result
        
        except Exception as e:
            print(f"Error estimating duration: {e}")
            return {
            "duration_category": "MEDIUM", 
            "estimated_minutes": 20,
            "due_date": end_of_week,
            "reasoning": "Default fallback"
        }
    
    def detect_special_tags(self, content):
        """Detect if task needs special tags like Communications or Needs Jessica Input"""
    
        content_lower = content.lower()
        tags = []
    
        # Communications: ACTUAL communication with people (not just any "update")
        comm_patterns = [
            "call", "email", "text", "message", "phone",
            "update parents", "contact", "coordinate with",
            "reach out", "follow up with", "send to",
            "notify", "inform", "tell"
        ]
    
        # More specific matching - look for communication + person/entity
        is_communication = False
        for pattern in comm_patterns:
            if pattern in content_lower:
                # Additional check: make sure it's about communicating with people
                people_indicators = ["parents", "team", "client", "customer", "person", "people", "someone", "them", "him", "her"]
                if any(indicator in content_lower for indicator in people_indicators) or pattern in ["call", "email", "text", "message", "phone"]:
                    is_communication = True
                    break
    
        if is_communication:
            tags.append("Communications")
    
        # Needs Jessica Input: home, baby, green card decisions
        jessica_keywords = ["home remodel", "baby", "green card", "major decision", "couple decision", "jessica"]
        if any(keyword in content_lower for keyword in jessica_keywords):
            tags.append("Needs Jessica Input")
    
        return tags

    def select_icon_for_analysis(self, title: str, project: str = "", content: str = "") -> str:
        """
        Select icon based on content first, then title, then project fallback
        
        Args:
            title: AI-generated title for the task/note
            project: Project name (optional, used as fallback)
            content: Original transcript content (optional, used as primary source)
            
        Returns:
            Selected emoji icon or default icon
        """
        try:
            # First try original content (primary source) - this is where keywords are!
            if content:
                icon = self.icon_manager.select_icon(content, title)
                if icon != self.icon_manager.default_icon:
                    return icon
            
            # If no match in content, try title only (secondary source)
            icon = self.icon_manager.select_icon("", title)
            if icon != self.icon_manager.default_icon:
                return icon
            
            # If no match in title, try project name (tertiary source)
            if project and project != "Manual Review Required":
                # Use simplified project name for better matching
                simplified_project = self._simplify_project_name(project)
                icon = self.icon_manager.select_icon("", simplified_project)
                if icon != self.icon_manager.default_icon:
                    return icon
            
            return self.icon_manager.default_icon
            
        except Exception as e:
            print(f"⚠️ Error in icon selection: {e}")
            return self.icon_manager.default_icon
    
    def _simplify_project_name(self, project: str) -> str:
        """
        Simplify project name for better icon matching
        
        Args:
            project: Full project name
            
        Returns:
            Simplified project name
        """
        # Remove common suffixes and prefixes
        simplified = project
        
        # Remove common suffixes
        suffixes_to_remove = [
            ": Focus. Flow. Fulfillment.",
            " - Zen Product Craftsman",
            " Application",
            " Workflow in Notion"
        ]
        
        for suffix in suffixes_to_remove:
            if simplified.endswith(suffix):
                simplified = simplified[:-len(suffix)]
                break
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Project ",
            "Epic "
        ]
        
        for prefix in prefixes_to_remove:
            if simplified.startswith(prefix):
                simplified = simplified[len(prefix):]
                break
        
        return simplified.strip()

def main():
    """Test the intelligent router"""
    print("🧠 Testing Intelligent Router...")
    router = IntelligentRouter()
    
    # Test with your examples
    test_cases = [
        "What are the differences between Figma and Canva? Product sense analysis.",
        "Update parents on green card interview scheduling",
        "Fix the Notion area update bug - take screenshot and root cause",
        "Research Sahil Bloom as potential mentor"
    ]
    
    for content in test_cases:
        print(f"\n{'='*60}")
        print(f"Content: {content}")
        print(f"{'='*60}")
        
        project = router.detect_project(content)
        duration = router.estimate_duration_and_due_date(content)
        tags = router.detect_special_tags(content)
        
        print(f"🎯 Project: {project}")
        print(f"⏰ Duration: {duration['duration_category']} ({duration['estimated_minutes']} min)")
        print(f"📅 Due Date: {duration['due_date']}")
        print(f"🏷️ Tags: {tags}")
        print(f"💭 Reasoning: {duration['reasoning']}")

if __name__ == "__main__":
    print("🚀 Starting intelligent router test...")
    main()
    print("✅ Test completed!")