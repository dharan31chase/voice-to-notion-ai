import os
from dotenv import load_dotenv
from notion_client import Client
import json
from datetime import datetime
from intelligent_router import IntelligentRouter

# Load environment variables
load_dotenv()
notion = Client(auth=os.getenv("NOTION_TOKEN"))

class AdvancedNotionManager:
    def __init__(self):
        self.tasks_db = os.getenv("TASKS_DATABASE_ID")
        self.notes_db = os.getenv("NOTES_DATABASE_ID")
        self.projects_db = os.getenv("PROJECTS_DATABASE_ID")
        self.areas_db = os.getenv("AREAS_DATABASE_ID")
        self.router = IntelligentRouter()
    
    def create_intelligent_task(self, analysis):
        """Create a task with AI-powered smart routing"""
        try:
            content = analysis.get("content", "")
            title = analysis.get("title", "")
            
            # Get AI recommendations
            project = self.router.detect_project(content)
            duration_info = self.router.estimate_duration_and_due_date(content)
            special_tags = self.router.detect_special_tags(content)
            
            # Build properties with EXACT property types
            properties = {
                "Task": {"title": [{"text": {"content": title}}]},
                "Done": {"status": {"name": "Not started"}},  # Status property, not select
                "Due Date": {"date": {"start": duration_info["due_date"]}}
            }
            
            # Add project if detected (Relation property - need project page ID)
            # For now, skip project assignment to avoid relation complexity
            if project != "Manual Review Required":
                print(f"   Would assign to project: {project} (relation setup needed)")
            else:
                special_tags.append("🔍 AI Review Needed")
            
            # Add tags (Multi-select)
            if special_tags:
                properties["Tags"] = {"multi_select": [{"name": tag} for tag in special_tags]}
            
            organized_content = self.organize_task_content(content)

            # Create content blocks with preserved context
            content_blocks = [
                {
                    "object": "block",
                    "type": "paragraph", 
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": organized_content}}]
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
                        "rich_text": [{"type": "text", "text": {"content": f"🤖 AI Analysis:\n• Duration: {duration_info['duration_category']} ({duration_info['estimated_minutes']} min)\n• Project: {project}\n• Tags: {', '.join(special_tags) if special_tags else 'None'}\n• Reasoning: {duration_info['reasoning']}"}}]
                    }
                }
            ]
            
            page = notion.pages.create(
                parent={"database_id": self.tasks_db},
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
            
            # Get AI recommendations
            project = self.router.detect_project(content)
            
            # Build properties for Notes database (skip Project relation for now)
            properties = {
                "Name": {"title": [{"text": {"content": title}}]},  # Using your actual title property name
                "Created Date": {"date": {"start": datetime.now().isoformat()}}
            }
            
            # Skip project relation for now
            if project != "Manual Review Required":
                print(f"   Would assign to project: {project} (relation setup needed)")
            else:
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
                properties=properties,
                children=content_blocks
            )
            
            print(f"✅ Created organized note: {title}")
            print(f"   🎯 Project: {project}")
            print(f"   📝 Action items: {len(action_items)}")
            
            return page
            
        except Exception as e:
            print(f"❌ Failed to create note: {e}")
            print(f"   Content: {content[:100]}...")
            return None
    def organize_task_content(self, content):
        """Use AI to organize task content while preserving context and insights"""
        
        prompt = f"""
        Format this voice recording into a clear task description while preserving ALL context and insights:
        
        Original content: "{content}"
        
        Guidelines:
        1. Keep ALL the original context, thoughts, and insights exactly as expressed
        2. Fix grammar, spelling, and sentence structure ONLY
        3. Preserve the original tone and personal voice
        4. Add paragraph breaks for readability
        5. DO NOT summarize or remove any background context - it's valuable!
        6. DO NOT rephrase the core insights - keep original expressions
        7. The full context helps understand WHY this task matters
        
        Format as: [Context/Insights] + [Clear Action Item]
        
        Return the formatted content with ALL original thoughts and context intact.
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
            return content  # Return original if AI fails
    
    def organize_note_content(self, content):
        """Use AI to organize and format note content while preserving insights"""
        
        prompt = f"""
        CRITICAL: This is a voice transcript that must preserve the speaker's exact thoughts, insights, and voice.

        Original transcript: "{content}"

        Your ONLY job:
        1. Add punctuation and paragraph breaks for readability
        2. Fix obvious typos or transcription errors
        3. Keep EVERY single insight, phrase, and observation exactly as spoken
        4. Preserve ALL specific terms, concepts, and unique expressions
        5. Do NOT summarize, condense, or rephrase ANY content
        6. Do NOT make it "professional" - keep the original voice and tone
        7. Do NOT add your own interpretations or explanations

        FORBIDDEN:
        - Rewriting sentences
        - Adding new explanations  
        - Making it sound "polished"
        - Removing any content whatsoever
        - Changing the speaker's words or expressions

        Return the content with ONLY formatting improvements - every thought and insight must remain exactly as originally expressed.
        """
        
        try:
            from intelligent_router import client
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2500  # Increased for longer content
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error organizing content: {e}")
            return content  # Return original if AI fails
    
    def route_content(self, analysis):
        """Intelligently route content to appropriate PARA database"""
        category = analysis.get("category", "").lower()
        
        if category == "task":
            return self.create_intelligent_task(analysis)
        elif category in ["note", "research"]:
            return self.create_organized_note(analysis)
        else:
            print(f"⚠️ Unknown category: {category}, creating as note with manual review flag")
            return self.create_organized_note(analysis)
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