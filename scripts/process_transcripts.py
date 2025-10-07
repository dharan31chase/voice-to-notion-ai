import os
import sys
import argparse
from pathlib import Path
import json
from dotenv import load_dotenv
from project_matcher import ProjectMatcher

# Load environment variables first
load_dotenv()

# Add parent directory to path for core imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Import shared utilities
from core.openai_client import get_openai_client
from core.logging_utils import get_logger

# Initialize logger and OpenAI client
logger = get_logger(__name__)
client = get_openai_client()

def analyze_transcript(transcript_text):
    """Enhanced category detection with robust parsing for new format"""
    
    # Clean and normalize the text
    content = transcript_text.strip()
    content_lower = content.lower()
    
    # Look for category indicators in the last sentence AND check for alternative formats
    sentences = content.split('.')
    last_sentence = sentences[-1].strip() if sentences else ""
    
    # Check for Task (multiple or single) - look in last sentence OR anywhere if it's the only occurrence
    task_occurrences = content_lower.count('task')
    if 'task' in last_sentence.lower() or (task_occurrences == 1 and 'task' in content_lower):
        return process_tasks(content)
    
    # Check for Note - look in last sentence OR anywhere if it's the only occurrence  
    note_occurrences = content_lower.count('note')
    if 'note' in last_sentence.lower() or (note_occurrences == 1 and 'note' in content_lower):
        # Initialize router for icon selection
        from intelligent_router import IntelligentRouter
        router = IntelligentRouter()
        return process_note(content, router=router)
    
    # CRITICAL FIX: Check for alternative format where task/note comes before project name
    # Look for project names in last 1-5 words, then check for task/note before that
    words = content.split()
    if len(words) >= 3:
        # Check last 1-5 words for potential project names
        for i in range(1, min(6, len(words))):
            potential_project = ' '.join(words[-i:])
            # Look for task/note before this potential project
            before_project = ' '.join(words[:-i])
            if 'task' in before_project.lower():
                return process_tasks(content)
            elif 'note' in before_project.lower():
                # Initialize router for icon selection
                from intelligent_router import IntelligentRouter
                router = IntelligentRouter()
                return process_note(content, router=router)
    
    # Default to task with manual review tag if unclear
    # Check if this looks like unclear content (no clear task/note indicators)
    words = content.split()
    if len(words) > 10:  # Long content without clear indicators
        return process_unclear_content(content)
    else:
        # For shorter content, try to process as task but with manual review
        return process_single_task(content, content.split('.'), manual_review=True)

def process_tasks(content):
    """Handle single or multiple tasks with project association"""
    
    # Initialize router for icon selection
    from intelligent_router import IntelligentRouter
    router = IntelligentRouter()
    
    # Split by periods and count 'Task' occurrences
    parts = content.split('.')
    task_occurrences = [i for i, part in enumerate(parts) if 'task' in part.lower().strip()]
    
    if len(task_occurrences) == 1:
        # Single task: [Task description]. [Project Name]. Task
        return process_single_task(content, parts, router=router)
    elif len(task_occurrences) > 1:
        # Multiple tasks: [Task 1]. Task. [Task 2]. Task. [Project Name]. Task
        return process_multiple_tasks(content, parts, task_occurrences, router=router)
    else:
        # Fallback - treat as single task with manual review
        return process_single_task(content, parts, manual_review=True, router=router)

def extract_project_from_content(content: str, project_matcher: ProjectMatcher) -> str:
    """
    Extract project name from content using flexible patterns.
    
    Patterns supported:
    - <Content> <Project Name>. <Task/Note>
    - <Content><Project Name> <Task/Note> (no period)
    - Handles embedded periods, case insensitive, ignores junk words
    """
    logger.debug(f"🔍 Extracting project from: '{content[:50]}{'...' if len(content) > 50 else ''}'")
    
    # Step 1: Find last task/note keyword (case insensitive)
    content_lower = content.lower()
    
    # Find last occurrence, with priority: last keyword wins
    last_note_pos = content_lower.rfind('note')
    last_task_pos = content_lower.rfind('task')
    
    if last_note_pos > last_task_pos:
        last_keyword_pos = last_note_pos
        keyword = 'note'
    elif last_task_pos > last_note_pos:
        last_keyword_pos = last_task_pos
        keyword = 'task'
    else:
        logger.debug("  ❌ No task/note keyword found")
        return "Manual Review Required"
    
    logger.debug(f"  Found keyword '{keyword}' at position {last_keyword_pos}")
    
    # Step 2: Extract text before the keyword (ignore everything after)
    before_keyword = content[:last_keyword_pos].strip()
    logger.debug(f"  Text before keyword: '{before_keyword}'")
    
    # Step 3: Try word combinations from end (1-5 words)
    words = before_keyword.split()
    for i in range(1, min(6, len(words) + 1)):  # 1-5 words
        potential_project = ' '.join(words[-i:])
        
        # Normalize: remove embedded periods and normalize spaces
        normalized_project = ' '.join(potential_project.replace('.', ' ').split())
        
        # Skip if the potential project is ONLY a keyword that should be ignored
        ignored_keywords = ['task', 'note', 'project', 'tasks', 'notes', 'projects']
        normalized_lower = normalized_project.lower().strip()
        if normalized_lower in ignored_keywords:
            logger.debug(f"  Skipping keyword: '{normalized_project}'")
            continue
        
        logger.debug(f"  Trying word combination: '{potential_project}'")
        
        # Use fuzzy matching with error handling
        try:
            matched_project = project_matcher.fuzzy_match_project(normalized_project)
            logger.debug(f"  Fuzzy match result: '{matched_project}'")
            if matched_project != "Manual Review Required":
                return matched_project
        except Exception as e:
            logger.warning(f"  ⚠️ Fuzzy matching failed: {e}")
            continue
    
    logger.debug("  ❌ No project match found")
    return "Manual Review Required"

def process_single_task(content, parts, manual_review=False, router=None):
    """Process single task with project extraction"""
    
    # Initialize ProjectMatcher for fuzzy matching
    project_matcher = ProjectMatcher()
    
    # Use new flexible project extraction method
    project_name = extract_project_from_content(content, project_matcher)
    
    # Extract task content (everything before the project name)
    task_content = content
    
    # Clean up task content
    if task_content.endswith('.'):
        task_content = task_content[:-1].strip()
    
    # Handle manual review cases
    if project_name == "Manual Review Required":
        manual_review = True
        project_name = ""  # Clear the unmatched project name
    
    # Use AI to generate title and analyze task
    prompt = f"""
    Create a clean, descriptive title for this task (4-8 words):
    
    Task: "{task_content}"
    Project: "{project_name}"
    
    Return ONLY the title, no quotes, no extra text.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        
        ai_title = response.choices[0].message.content.strip().strip('"').strip("'")
        
        # Select icon based on content, title and project
        task_icon = router.select_icon_for_analysis(ai_title, project_name, content) if router else "⁉️"
        
        # Create the result object
        return {
            "category": "task",
            "title": ai_title,
            "icon": task_icon,  # Add icon to result
            "content": task_content,
            "action_items": [],
            "key_insights": [],
            "confidence": "high",
            "project": project_name,
            "manual_review": manual_review
        }
    
    except Exception as e:
        logger.error(f"Error analyzing single task: {e}")
        # Fallback - return original with default icon
        fallback_title = task_content[:60]
        fallback_icon = router.select_icon_for_analysis(fallback_title, project_name, content) if router else "⁉️"
        
        return {
            "category": "task",
            "title": fallback_title,
            "icon": fallback_icon,  # Add icon to fallback result
            "content": task_content,
            "action_items": [],
            "key_insights": [],
            "confidence": "low",
            "project": project_name,
            "manual_review": manual_review
        }

def process_multiple_tasks(content, parts, task_occurrences, router=None):
    """Process multiple tasks and return list of task objects"""
    
    tasks = []
    
    # Initialize ProjectMatcher for fuzzy matching
    project_matcher = ProjectMatcher()
    
    # Use new flexible project extraction method for shared project
    project_name = extract_project_from_content(content, project_matcher)
    
    # Handle manual review cases
    manual_review_needed = False
    if project_name == "Manual Review Required":
        project_name = ""  # Clear the unmatched project name
        manual_review_needed = True
    
    # Process each task
    for i, task_index in enumerate(task_occurrences[:-1]):  # Exclude last 'Task'
        if i == 0:
            # First task: everything from start to first 'Task'
            task_content = '.'.join(parts[:task_index]).strip()
        else:
            # Subsequent tasks: from previous 'Task' to current 'Task'
            prev_task_index = task_occurrences[i-1]
            task_content = '.'.join(parts[prev_task_index+1:task_index]).strip()
        
        # Clean up task content
        if task_content.endswith('.'):
            task_content = task_content[:-1].strip()
        
        # Create task object
        basic_title = task_content[:60]
        basic_icon = router.select_icon_for_analysis(basic_title, project_name, content) if router else "⁉️"
        
        task_obj = {
            "category": "task",
            "title": basic_title,
            "icon": basic_icon,  # Add icon to basic task object
            "content": task_content,
            "action_items": [],
            "key_insights": [],
            "confidence": "high",
            "project": project_name,
            "manual_review": manual_review_needed
        }
        
        # Use AI to enhance the task
        try:
            prompt = f"""
            Create a clean, descriptive title for this task (4-8 words):
            
            Task: "{task_content}"
            Project: "{project_name}"
            
            Return ONLY the title, no quotes, no extra text.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50
            )
            
            ai_title = response.choices[0].message.content.strip().strip('"').strip("'")
            task_obj["title"] = ai_title
            task_obj["confidence"] = "high"
            
            # Select icon for this specific task
            task_icon = router.select_icon_for_analysis(ai_title, project_name, content) if router else "⁉️"
            task_obj["icon"] = task_icon
            
        except Exception as e:
            logger.error(f"Error analyzing task {i+1}: {e}")
            # Keep the basic task object
        
        tasks.append(task_obj)
    
    return tasks

def process_note(content, router=None):
    """Process single note with project extraction"""
    
    # Initialize ProjectMatcher for fuzzy matching
    project_matcher = ProjectMatcher()
    
    # Use new flexible project extraction method
    project_name = extract_project_from_content(content, project_matcher)
    
    # Extract note content (everything before the project name)
    note_content = content
    
    # Clean up note content
    if note_content.endswith('.'):
        note_content = note_content[:-1].strip()
    
    # Handle manual review cases
    if project_name == "Manual Review Required":
        project_name = ""  # Clear the unmatched project name
    
    # Use AI ONLY for title generation
    title_prompt = f"""
    Create a concise, descriptive title for this note (4-8 words):
    
    {note_content[:500]}
    
    Focus on the MAIN TOPIC or KEY INSIGHT. Examples:
    - "Preserving Authentic Voice in Writing"
    - "Product Strategy Documentation Workflow"
    - "Integration and Elusiveness in Eudaimonia"
    - "High Signal Social Media Platform Concept"
    
    Return ONLY the title, no quotes, no extra text.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": title_prompt}],
            max_tokens=30
        )
        title = response.choices[0].message.content.strip().strip('"')
    except Exception as e:
        logger.error(f"Error generating title: {e}")
        # Fallback to first words
        first_words = note_content.split()[:8]
        title = " ".join(first_words) + "..."
    
    # Select icon based on title and project
    note_icon = router.select_icon_for_analysis(title, project_name, content) if router else "⁉️"
        
    return {
        "category": "note",
        "title": title,  # Smart AI title
        "icon": note_icon,  # Add icon to result
        "content": note_content,  # Clean note content
        "action_items": [],
        "key_insights": [],
        "confidence": "high",
        "project": project_name
    }

def process_unclear_content(content):
    """Process unclear content as task with manual review tag - preserves original content exactly"""
    
    # Create a simple title from the first 60 characters of original content
    title = content[:60]
    if len(content) > 60:
        title += "..."
    
    return {
        "category": "task",
        "title": title,
        "content": content,  # Original transcript preserved exactly as-is
        "action_items": [],
        "key_insights": [],
        "confidence": "low",
        "project": "Manual Review Required",  # Clear flag for manual review
        "manual_review": True
    }
    
    # Only use AI for TASKS (existing code)
    if category == "task":
        prompt = f"""
        Analyze this task transcript and extract the action item.
        
        Transcript: {transcript_text}
        
        Return JSON:
        {{
            "category": "task",
            "title": "Brief descriptive title following Verb + Object pattern",
            "content": "The full transcript with light formatting",
            "action_items": ["specific tasks if any"],
            "key_insights": ["main insights if any"],
            "confidence": "high|medium|low"
        }}
        
        IMPORTANT: Keep ALL original content in the "content" field, just add formatting.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing transcript: {e}")
            # Fallback - return original
            return {
                "category": "task",
                "title": transcript_text[:60],
                "content": transcript_text,
                "action_items": [],
                "key_insights": [],
                "confidence": "low"
            }
    
    # Default fallback
    return {
        "category": category,
        "title": transcript_text[:60],
        "content": transcript_text,
        "action_items": [],
        "key_insights": [],
        "confidence": "low"
    }

        
def process_transcript_file(file_path, dry_run=False, output_dir='processed'):
    """Process a single transcript file - handles both single and multiple analyses"""
    
    try:
        # Read the transcript file
        with open(file_path, 'r', encoding='utf-8') as file:
            transcript_text = file.read()
        
        logger.info(f"Processing: {file_path.name}")
        logger.debug(f"Content preview: {transcript_text[:100]}...")
        
        if dry_run:
            logger.debug("Dry-run mode: Will show analysis without creating Notion entries")
        
        # Analyze with AI
        analysis = analyze_transcript(transcript_text)
        
        if analysis:
            # Handle both single analysis and multiple tasks
            if isinstance(analysis, list):
                # Multiple tasks
                logger.info(f"✅ Processing {len(analysis)} tasks from transcript")
                for i, task in enumerate(analysis, 1):
                    logger.info(f"   Task {i}: {task.get('title', 'No title')} → {task.get('project', 'No project')}")
                    if task.get('manual_review', False):
                        logger.warning(f"   ⚠️ Task {i} marked for manual review")
                
                # 🚀 AUTO-ROUTE TO NOTION! 🚀
                if not dry_run:
                    try:
                        from notion_manager import AdvancedNotionManager
                        manager = AdvancedNotionManager()
                        result = manager.route_content(analysis)
                        if result and result["summary"]["successful"] > 0:
                            logger.info(f"🎉 Successfully routed {result['summary']['successful']}/{result['summary']['total']} to Notion!")
                            
                            # 🆕 PHASE 1: CAPTURE NOTION ENTRY IDS FOR MULTIPLE ANALYSES
                            if isinstance(analysis, list) and result["successful"]:
                                for i, task in enumerate(analysis):
                                    if i < len(result["successful"]):
                                        task["notion_entry_id"] = result["successful"][i].get("id")
                                        logger.info(f"   📝 Task {i+1} Notion ID: {task['notion_entry_id'][:8]}...")
                            
                            if result["summary"]["failed"] > 0:
                                logger.warning(f"⚠️ {result['summary']['failed']} tasks failed to route")
                        else:
                            logger.error("❌ Failed to create Notion content")
                    except Exception as e:
                        logger.warning(f"⚠️ Notion routing failed: {e}")
                else:
                    logger.info("🔍 DRY RUN: Would create Notion entries for:")
                    for i, task in enumerate(analysis, 1):
                        logger.info(f"   Task {i}: {task.get('title', 'No title')}")
                        logger.info(f"      Project: {task.get('project', 'No project')}")
                        logger.info(f"      Icon: {task.get('icon', 'No icon')}")
                
                # 🆕 SAVE ENHANCED ANALYSES WITH NOTION IDS
                if not dry_run:
                    output_file = Path(output_dir) / f"{file_path.stem}_processed.json"
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w') as f:
                        json.dump({
                            "original_file": str(file_path),
                            "analyses": analysis,  # Array of task objects with Notion IDs
                            "timestamp": str(Path(file_path).stat().st_mtime)
                        }, f, indent=2)
                    
                    logger.info(f"✅ Saved {len(analysis)} enhanced analyses to: {output_file}")
                else:
                    logger.info(f"🔍 DRY RUN: Would save to: {output_dir}/{file_path.stem}_processed.json")
                
                return analysis
                
            else:
                # Single analysis (task or note)
                logger.info(f"✅ Category: {analysis['category']}")
                logger.info(f"✅ Title: {analysis['title']}")
                logger.info(f"✅ Confidence: {analysis['confidence']}")
                if analysis.get('manual_review', False):
                    logger.warning("⚠️ Marked for manual review")
                
                # 🚀 AUTO-ROUTE TO NOTION! 🚀
                if not dry_run:
                    try:
                        from notion_manager import AdvancedNotionManager
                        manager = AdvancedNotionManager()
                        result = manager.route_content(analysis)
                        if result and result["summary"]["successful"] > 0:
                            logger.info(f"🎉 Successfully routed {result['summary']['successful']}/{result['summary']['total']} to Notion!")
                            
                            # 🆕 PHASE 1: CAPTURE NOTION ENTRY ID FOR SINGLE ANALYSIS
                            if result["successful"]:
                                analysis["notion_entry_id"] = result["successful"][0].get("id")
                                logger.info(f"   📝 Notion ID: {analysis['notion_entry_id'][:8]}...")
                            
                            if result["summary"]["failed"] > 0:
                                logger.warning(f"⚠️ {result['summary']['failed']} tasks failed to route")
                        else:
                            logger.error("❌ Failed to create Notion content")
                    except Exception as e:
                        logger.warning(f"⚠️ Notion routing failed: {e}")
                else:
                    logger.info("🔍 DRY RUN: Would create Notion entry:")
                    logger.info(f"   Title: {analysis.get('title', 'No title')}")
                    logger.info(f"   Category: {analysis.get('category', 'unknown')}")
                    logger.info(f"   Project: {analysis.get('project', 'No project')}")
                    logger.info(f"   Icon: {analysis.get('icon', 'No icon')}")
                    logger.info(f"   Confidence: {analysis.get('confidence', 'unknown')}")
                
                # 🆕 SAVE ENHANCED ANALYSIS WITH NOTION ID
                if not dry_run:
                    output_file = Path(output_dir) / f"{file_path.stem}_processed.json"
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w') as f:
                        json.dump({
                            "original_file": str(file_path),
                            "analysis": analysis,  # Single object with Notion ID (backward compatible)
                            "timestamp": str(Path(file_path).stat().st_mtime)
                        }, f, indent=2)
                    
                    logger.info(f"✅ Saved enhanced analysis to: {output_file}")
                else:
                    logger.info(f"🔍 DRY RUN: Would save to: {output_dir}/{file_path.stem}_processed.json")
                
                return analysis
        else:
            logger.error("❌ Failed to analyze transcript")
            return None
            
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return None

def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Process voice transcripts and create Notion entries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all files (default behavior)
  python process_transcripts.py
  
  # Dry-run mode (no Notion changes, no file saves)
  python process_transcripts.py --dry-run
  
  # Process single file with verbose output
  python process_transcripts.py --file transcripts/test.txt --verbose
  
  # Use custom config in dry-run mode
  python process_transcripts.py --config test-settings.yaml --dry-run --verbose
  
  # Custom input/output directories
  python process_transcripts.py --input-dir my_transcripts --output-dir my_output
        """
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without creating Notion entries or saving files (shows what would happen)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable debug-level logging for detailed output'
    )
    
    parser.add_argument(
        '--file',
        type=str,
        metavar='PATH',
        help='Process single file instead of all transcripts in input directory'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        metavar='PATH',
        help='Use custom configuration file (merges with default config/settings.yaml)'
    )
    
    parser.add_argument(
        '--input-dir',
        type=str,
        default='transcripts',
        metavar='PATH',
        help='Directory containing transcript files (default: transcripts)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='processed',
        metavar='PATH',
        help='Directory for processed output JSON files (default: processed)'
    )
    
    return parser.parse_args()

def main():
    """Main function to process all transcript files"""
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Enable verbose logging if requested
    if args.verbose:
        from core.logging_utils import set_log_level
        set_log_level(logger, "DEBUG")
        logger.debug("Debug logging enabled")
    
    # Show dry-run banner if enabled
    if args.dry_run:
        logger.info("=" * 60)
        logger.info("🔍 DRY RUN MODE - No changes will be made")
        logger.info("   - Notion entries will NOT be created")
        logger.info("   - Processed JSON files will NOT be saved")
        logger.info("   - This shows what WOULD happen in a real run")
        logger.info("=" * 60)
    
    # Determine which files to process
    if args.file:
        # Process single file
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"File not found: {args.file}")
            return
        txt_files = [file_path]
        logger.info(f"Processing single file: {args.file}")
    else:
        # Process all files in input directory
        transcript_folder = Path(args.input_dir)
        
        if not transcript_folder.exists():
            logger.info(f"Creating {args.input_dir} folder...")
            transcript_folder.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Please copy your .txt files to the '{args.input_dir}' folder")
            return
        
        # Find all .txt files
        txt_files = list(transcript_folder.glob("*.txt"))
        
        if not txt_files:
            logger.warning(f"No .txt files found in {args.input_dir} folder")
            logger.info(f"📁 Please copy your .txt files to the '{args.input_dir}' folder")
            return
        
        logger.info(f"Found {len(txt_files)} transcript files in {args.input_dir}")
    
    # Process each file
    for txt_file in txt_files:
        logger.info(f"\n{'='*50}")
        analysis = process_transcript_file(txt_file, dry_run=args.dry_run, output_dir=args.output_dir)
        if analysis:
            if args.dry_run:
                logger.info("🔍 Dry-run complete - no changes made")
            else:
                logger.info("🎉 Successfully processed!")
        logger.info(f"{'='*50}")
    
    # Final summary
    if args.dry_run:
        logger.info("\n" + "=" * 60)
        logger.info("🔍 DRY RUN COMPLETE")
        logger.info(f"   Processed {len(txt_files)} file(s) in simulation mode")
        logger.info("   No Notion entries created, no files saved")
        logger.info("   Remove --dry-run flag to execute for real")
        logger.info("=" * 60)

if __name__ == "__main__":
    main()