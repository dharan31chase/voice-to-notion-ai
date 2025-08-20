import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import json

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_transcript(transcript_text):
    """Uses AI to analyze and categorize transcript content"""
    
    # Initialize OpenAI client (new way)
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""
    Analyze this voice transcript and organize it into categories.
    
    The person will end recordings with phrases like:
    - "This is a task" - for actionable items
    - "This is a note" - for information/learnings
    - "This is research" - for research topics
    
    Transcript: {transcript_text}
    
    Return a JSON response with this structure:
    {{
        "category": "task|note|research|mixed",
        "title": "Brief descriptive title",
        "content": "Main content cleaned up",
        "action_items": ["list of specific tasks if any"],
        "key_insights": ["main points or learnings"],
        "confidence": "high|medium|low"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        # Parse JSON response
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"Error analyzing transcript: {e}")
        return None

        
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