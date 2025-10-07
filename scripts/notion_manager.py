import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
import json
from datetime import datetime
from intelligent_router import IntelligentRouter
from project_matcher import ProjectMatcher

# Load environment variables first
load_dotenv()

# Add parent directory to path for core imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import shared utilities
from core.logging_utils import get_logger

# Initialize logger
logger = get_logger(__name__)

# Load Notion client (no change needed - uses notion_client library)
notion = Client(auth=os.getenv("NOTION_TOKEN"))

class AdvancedNotionManager:
    def __init__(self):
        self.tasks_db = os.getenv("TASKS_DATABASE_ID")
        self.notes_db = os.getenv("NOTES_DATABASE_ID")
        self.projects_db = os.getenv("PROJECTS_DATABASE_ID")
        self.areas_db = os.getenv("AREAS_DATABASE_ID")
        self.router = IntelligentRouter()
        self.project_matcher = ProjectMatcher()
    
    def create_intelligent_task(self, analysis):
        """Create a task with AI-powered smart routing and clean formatting"""
        try:
            content = analysis.get("content", "")
            title = analysis.get("title", "")
            
            # Extra safety check to remove any quotes
            title = title.strip('"').strip("'")
            
            # Clean and format the title to ensure Verb + Object + Context pattern
            title = self.clean_task_title(title)
            
            # NEW: Clean the content to remove meta-commentary
            cleaned_content = self.organize_task_content(content)
            
            # Get AI recommendations (existing code)
            project = self.router.detect_project(content)
            duration_info = self.router.estimate_duration_and_due_date(content)
            special_tags = self.router.detect_special_tags(content)
            
            # Build properties (existing code)
            properties = {
                "Task": {"title": [{"text": {"content": title}}]},  # Use cleaned title
                "Done": {"status": {"name": "Not started"}},
                "Due Date": {"date": {"start": duration_info["due_date"]}}
            }
            
            # STEP 4: Add project assignment to Notion
            # Use project from analysis (which comes from fuzzy matching)
            analysis_project = analysis.get("project", "")
            if analysis_project and analysis_project != "Manual Review Required":
                # Get project ID from cache
                project_id = self.project_matcher.get_project_id_from_cache(analysis_project)
                if project_id:
                    properties["Project"] = {"relation": [{"id": project_id}]}
                    print(f"   🎯 Project assigned: {analysis_project} (ID: {project_id[:8]}...)")
                else:
                    print(f"   ⚠️ Project not found in cache: {analysis_project}")
            else:
                print(f"   📝 No project assigned (Manual Review Required or empty)")
            
            # Add project detection info (existing)
            if project != "Manual Review Required":
                print(f"   Would assign to project: {project}")
            else:
                special_tags.append("🔍 AI Review Needed")
            
            # Add manual review tag if needed
            if analysis.get("manual_review", False):
                special_tags.append("🏷️ Needs Manual Review")
            
            # Get icon for page-level setting
            icon = analysis.get("icon", "⁉️")
            
            # Add tags (existing)
            if special_tags:
                properties["Tags"] = {"multi_select": [{"name": tag} for tag in special_tags]}
            
            # Create content blocks with CLEANED content
            content_blocks = [
                {
                    "object": "block",
                    "type": "paragraph", 
                    "paragraph": {
                        "rich_text": [{"text": {"content": cleaned_content}}]  # Use cleaned
                    }
                },
                {
                    "object": "block",
                    "type": "divider",
                    "divider": {}
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": f"🤖 AI Analysis:\n• Duration: {duration_info['duration_category']} ({duration_info['estimated_minutes']} min)\n• Project: {project}\n• Tags: {', '.join(special_tags) if special_tags else 'None'}\n• Reasoning: {duration_info['reasoning']}"}}]
                    }
                }
            ]
            
            # Create the page with icon
            page = notion.pages.create(
                parent={"database_id": self.tasks_db},
                icon={"type": "emoji", "emoji": icon},
                properties=properties,
                children=content_blocks
            )
            
            print(f"✅ Created intelligent task: {title}")
            print(f"   🎯 Project: {project}")
            print(f"   ⏰ Due: {duration_info['due_date']} ({duration_info['duration_category']})")
            print(f"   🏷️ Tags: {special_tags}")
            
            return page
        
        except Exception as e:
            print(f"❌ Failed to create task: {e}")
            print(f"   Content: {content[:100]}...")
            return None
    
    def create_organized_note(self, analysis):
        """Create a note with intelligent organization and embedded action items"""
        try:
            content = analysis.get("content", "")
            title = analysis.get("title", "")
            
            # Build properties for Notes database
            properties = {
                "Name": {"title": [{"text": {"content": title}}]},  # Using your actual title property name
                "Created Date": {"date": {"start": datetime.now().isoformat()}}
            }
            
            # STEP 4: Add project assignment to Notes
            # Use project from analysis (which comes from fuzzy matching)
            analysis_project = analysis.get("project", "")
            if analysis_project and analysis_project != "Manual Review Required":
                # Get project ID from cache
                project_id = self.project_matcher.get_project_id_from_cache(analysis_project)
                if project_id:
                    properties["Project"] = {"relation": [{"id": project_id}]}
                    print(f"   🎯 Project assigned: {analysis_project} (ID: {project_id[:8]}...)")
                else:
                    print(f"   ⚠️ Project not found in cache: {analysis_project}")
            else:
                print(f"   📝 No project assigned (Manual Review Required or empty)")
            
            # Get icon for page-level setting
            icon = analysis.get("icon", "⁉️")
            
            # Handle manual review cases
            if analysis_project == "Manual Review Required":
                # Use Jessica's Input checkbox instead
                properties["Need Jessica's Input"] = {"checkbox": True}
            
            # Organize the content using AI (or preserve if too long)
            organized_content = self.organize_note_content(content)

            # Split content into chunks for Notion's 2000 character limit
            content_chunks = self.chunk_content(organized_content)

            # Create content blocks from chunks
            content_blocks = []
            for i, chunk in enumerate(content_chunks):
                content_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": chunk}}]
                    }
                })
                
                # Add space between chunks (except last one)
                if i < len(content_chunks) - 1:
                    content_blocks.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": ""}}]
                        }
                    })
            
            # Add action items if any (embedded in note, not separate tasks)
            action_items = analysis.get("action_items", [])
            if action_items:
                content_blocks.extend([
                    {
                        "object": "block",
                        "type": "divider", 
                        "divider": {}
                    },
                    {
                        "object": "block",
                        "type": "heading_3",
                        "heading_3": {
                            "rich_text": [{"type": "text", "text": {"content": "📋 Action Items"}}]
                        }
                    }
                ])
                
                for item in action_items:
                    content_blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item}}]
                        }
                    })
            
            page = notion.pages.create(
                parent={"database_id": self.notes_db},
                icon={"type": "emoji", "emoji": icon},
                properties=properties,
                children=content_blocks
            )
            
            print(f"✅ Created organized note: {title}")
            print(f"   🎯 Project: {analysis_project}")
            print(f"   📝 Action items: {len(action_items)}")
            
            return page
            
        except Exception as e:
            print(f"❌ Failed to create note: {e}")
            print(f"   Content: {content[:100]}...")
            return None
    
    def organize_task_content(self, content):
        """Clean content while removing meta-commentary but preserving context"""
        
        # Remove common prompt artifacts
        meta_patterns = [
            "I recorded a message instructing you to",
            "I recorded a message asking you to",
            "I recorded a message telling you to",
            "This task is important because it will help",
            "The user wants to",
            "The user needs to", 
            "The recording says to",
            "I need you to",
            "Please help me",
            "Remember to",
            "Don't forget to",
        ]
        
        cleaned_content = content
        for pattern in meta_patterns:
            # Case-insensitive replacement
            import re
            cleaned_content = re.sub(pattern, "", cleaned_content, flags=re.IGNORECASE)
        
        # Clean up the content while preserving insights
        prompt = f"""
    Format this task content by removing ALL meta-commentary while keeping the actual task details:

    "{cleaned_content}"

    REMOVE:
    - "I recorded a message..." phrases
    - "This task is important because..." explanations
    - Instructions about formatting
    - Meta-commentary about what you should do

    KEEP:
    - The actual task details and requirements
    - Context that explains WHY this matters
    - Specific constraints or deadlines
    - Any insights or reasoning that adds value

    Return ONLY the clean, formatted task context.
    """
        
        try:
            from intelligent_router import client
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error organizing task content: {e}")
            # Basic fallback - at least remove the patterns
            return cleaned_content.strip()
    
    def organize_note_content(self, content):
        """Preserve original note content with only basic formatting"""
        
        # Just do basic cleanup - NO AI processing to preserve voice
        cleaned_content = content
        
        # Only fix obvious formatting issues
        # Remove multiple spaces
        import re
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
        
        # Add paragraph breaks at obvious points (after periods followed by capital letters)
        cleaned_content = re.sub(r'\. ([A-Z])', r'.\n\n\1', cleaned_content)
        
        # Return the content with minimal changes to preserve original voice
        return cleaned_content.strip()
    
    def route_content(self, analysis):
        """Handle both single analysis and list of analyses with structured results"""
        
        # Check if it's a list (multiple tasks) or single object
        if isinstance(analysis, list):
            # Multiple tasks - process each one
            successful_tasks = []
            failed_tasks = []
            
            for i, task_analysis in enumerate(analysis, 1):
                try:
                    result = self.create_intelligent_task(task_analysis)
                    if result:
                        successful_tasks.append(result)
                        print(f"✅ Task {i} created successfully")
                    else:
                        failed_tasks.append({
                            "task": task_analysis,
                            "error": "Failed to create task in Notion"
                        })
                        print(f"❌ Task {i} failed to create")
                except Exception as e:
                    failed_tasks.append({
                        "task": task_analysis,
                        "error": str(e)
                    })
                    print(f"❌ Task {i} failed with error: {e}")
            
            print(f"📊 Multiple tasks summary: {len(successful_tasks)} successful, {len(failed_tasks)} failed")
            
            return {
                "successful": successful_tasks,
                "failed": failed_tasks,
                "summary": {
                    "total": len(analysis),
                    "successful": len(successful_tasks),
                    "failed": len(failed_tasks)
                }
            }
            
        else:
            # Single analysis - use structured format for consistency
            try:
                category = analysis.get("category", "").lower()
                
                if category == "task":
                    result = self.create_intelligent_task(analysis)
                elif category in ["note", "research"]:
                    result = self.create_organized_note(analysis)
                else:
                    print(f"⚠️ Unknown category: {category}, creating as note with manual review flag")
                    result = self.create_organized_note(analysis)
                
                if result:
                    return {
                        "successful": [result],
                        "failed": [],
                        "summary": {
                            "total": 1,
                            "successful": 1,
                            "failed": 0
                        }
                    }
                else:
                    return {
                        "successful": [],
                        "failed": [{
                            "task": analysis,
                            "error": "Failed to create content in Notion"
                        }],
                        "summary": {
                            "total": 1,
                            "successful": 0,
                            "failed": 1
                        }
                    }
                    
            except Exception as e:
                return {
                    "successful": [],
                    "failed": [{
                        "task": analysis,
                        "error": str(e)
                    }],
                    "summary": {
                        "total": 1,
                        "successful": 0,
                        "failed": 1
                    }
                }
    def chunk_content(self, content, max_length=1800):
        """Split long content into chunks that fit Notion's 2000 character limit"""
        if len(content) <= max_length:
            return [content]
        
        chunks = []
        words = content.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_length and current_chunk:
                # Start new chunk
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def clean_task_title(self, title):
        """Clean and format title to Verb + Object + Context pattern"""
        
        # Common spelling corrections
        corrections = {
            "tremor": "trimmer",
            "calender": "calendar",
            "recieve": "receive",
            "jessie": "Jessi",
            "jessy": "Jessi",
        }
        
        # Apply corrections to title
        clean_title = title
        for wrong, right in corrections.items():
            clean_title = clean_title.replace(wrong, right)
        
        # Simple, direct prompt to ensure Verb + Object + Context format
        prompt = f"""
    Format this task title to follow the pattern: [Verb] + [Object] + [Essential Context]
    
    Current title: "{clean_title}"
    
    RULES:
    1. Start with an action verb (Fix, Buy, Research, Call, Schedule, Review, etc.)
    2. Follow with the specific object/target
    3. Keep essential context like project names or locations
    4. Aim for 5-8 words when context is needed
    5. DO NOT add quotation marks around the title
    
    Return ONLY the formatted title without quotes.
    """
        
        try:
            from intelligent_router import client
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            
            # Strip any quotes that GPT might add
            cleaned = response.choices[0].message.content.strip()
            # Remove leading/trailing quotes if present
            cleaned = cleaned.strip('"').strip("'")
            
            return cleaned
            
        except Exception as e:
            print(f"Error cleaning title: {e}")
            # Basic fallback cleaning
            clean_title = title
            for wrong, right in corrections.items():
                clean_title = clean_title.replace(wrong, right)
            return clean_title.strip('"').strip("'")

def main():
    """Test the advanced Notion manager with processed transcripts"""
    manager = AdvancedNotionManager()
    
    # Look for processed files
    from pathlib import Path
    processed_files = list(Path("processed").glob("*.json"))
    
    if not processed_files:
        print("No processed files found. Run process_transcripts.py first!")
        return
    
    print(f"Found {len(processed_files)} processed transcript files")
    
    for file_path in processed_files:
        print(f"\n{'='*60}")
        print(f"Processing: {file_path.name}")
        print(f"{'='*60}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        analysis = data.get("analysis")
        if analysis:
            result = manager.route_content(analysis)
            if result:
                print("🎉 Successfully routed to Notion!")
            else:
                print("❌ Failed to create Notion content")

if __name__ == "__main__":
    print("🚀 Starting Notion Manager test...")
    main()
    print("✅ Test completed!")