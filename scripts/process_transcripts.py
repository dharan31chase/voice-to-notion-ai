import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client (THIS LINE MIGHT BE MISSING)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_transcript(transcript_text):
    """Uses AI to analyze and categorize transcript content"""
    
    # For long content, preserve original and do minimal analysis
    word_count = len(transcript_text.split())
    if word_count > 800:  # If more than 800 words
        print(f"   Long content detected ({word_count} words) - preserving original")
        
        # Determine category from ending
        content_lower = transcript_text.lower()
        if content_lower.endswith("this is a task"):
            category = "task"
        elif content_lower.endswith("this is a note"):
            category = "note"
        elif content_lower.endswith("this is research"):
            category = "research"
        else:
            category = "note"  # Default for unclear endings
        
        # Extract title from first part of content
        first_words = transcript_text.split()[:10]
        title = " ".join(first_words)
        if len(title) > 60:
            title = title[:60] + "..."
            
        return {
            "category": category,
            "title": title,
            "content": transcript_text,  # FULL ORIGINAL CONTENT
            "action_items": [],
            "key_insights": [],
            "confidence": "high"
        }
    
    # For shorter content, use AI analysis
    prompt = f"""
    Analyze this voice transcript and organize it into categories.
    
    Transcript: {transcript_text}
    
    CATEGORIZATION RULES (in priority order):
    1. If the transcript ends with "This is a task" → category = "task"
    2. If the transcript ends with "This is a note" → category = "note" 
    3. If the transcript ends with "This is research" → category = "research"
    
    Return JSON:
    {{
        "category": "task|note|research",
        "title": "Brief descriptive title",
        "content": "Clean up the content with formatting but preserve all details",
        "action_items": ["specific tasks if any"],
        "key_insights": ["main insights if any"],
        "confidence": "high|medium|low"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error analyzing transcript: {e}")
        return {
            "category": "note",
            "title": "Voice Recording",
            "content": transcript_text,  # Fallback to original
            "action_items": [],
            "key_insights": [],
            "confidence": "low"
        }

        
def process_transcript_file(file_path):
    """Process a single transcript file"""
    
    try:
        # Read the transcript file
        with open(file_path, 'r', encoding='utf-8') as file:
            transcript_text = file.read()
        
        print(f"Processing: {file_path.name}")
        print(f"Content preview: {transcript_text[:100]}...")
        
        # Analyze with AI
        analysis = analyze_transcript(transcript_text)
        
        if analysis:
            print(f"✅ Category: {analysis['category']}")
            print(f"✅ Title: {analysis['title']}")
            print(f"✅ Confidence: {analysis['confidence']}")
            
            # Save processed result
            output_file = Path("processed") / f"{file_path.stem}_processed.json"
            with open(output_file, 'w') as f:
                json.dump({
                    "original_file": str(file_path),
                    "analysis": analysis,
                    "timestamp": str(Path(file_path).stat().st_mtime)
                }, f, indent=2)
            
            print(f"✅ Saved analysis to: {output_file}")
            
            # 🚀 AUTO-ROUTE TO NOTION! 🚀
            try:
                from notion_manager import AdvancedNotionManager
                manager = AdvancedNotionManager()
                result = manager.route_content(analysis)
                if result:
                    print("🎉 Successfully routed to Notion!")
                else:
                    print("❌ Failed to create Notion content")
            except Exception as e:
                print(f"⚠️ Notion routing failed: {e}")
            
            return analysis
        else:
            print("❌ Failed to analyze transcript")
            return None
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    """Main function to process all transcript files"""
    
    # Look for transcript files
    transcript_folder = Path("transcripts")
    
    if not transcript_folder.exists():
        print("Creating transcripts folder...")
        transcript_folder.mkdir()
        print("📁 Please copy your .txt files from MacWhisper to the 'transcripts' folder")
        return
    
    # Find all .txt files
    txt_files = list(transcript_folder.glob("*.txt"))
    
    if not txt_files:
        print("No .txt files found in transcripts folder")
        print("📁 Please copy your .txt files from MacWhisper to the 'transcripts' folder")
        return
    
    print(f"Found {len(txt_files)} transcript files")
    
    # Process each file
    for txt_file in txt_files:
        print(f"\n{'='*50}")
        analysis = process_transcript_file(txt_file)
        if analysis:
            print("🎉 Successfully processed!")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()