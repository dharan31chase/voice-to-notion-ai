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

# Import new parsers
from parsers.content_parser import ContentParser, CategoryDetector
from parsers.project_extractor import ProjectExtractor
from parsers.transcript_validator import TranscriptValidator

# Import analyzers
from analyzers.task_analyzer import TaskAnalyzer
from analyzers.note_analyzer import NoteAnalyzer

# Initialize logger and OpenAI client
logger = get_logger(__name__)
client = get_openai_client()

# Initialize parser and validator
content_parser = ContentParser()
transcript_validator = TranscriptValidator()

# Initialize analyzers (will create with router when needed)
task_analyzer = None
note_analyzer = None

def analyze_transcript(transcript_text):
    """
    Enhanced category detection using smart heuristics.
    
    Now uses ContentParser for improved accuracy:
    - Tier 1: Explicit keywords (task, note) - 90% confidence
    - Tier 2: Imperative verbs (fix, make, create) - 80% confidence
    - Tier 3: Note indicators (I noticed, was, truth is) - 75% confidence
    - Tier 4: Intent patterns (I want to, I need to) - 75% confidence
    - Tier 5: Calendar keywords (block, schedule) - 70% confidence, manual review
    - Default: Note (passive content) - 50% confidence, manual review
    """
    # Clean content
    content = transcript_text.strip()
    
    # Use new smart category detector
    detection = content_parser.parse(content)
    category = detection["category"]
    confidence = detection["confidence_score"]
    manual_review = detection["manual_review"]
    
    logger.debug(f"Smart detection: {category} (confidence: {confidence:.2f}, review: {manual_review})")
    
    # Initialize router for analyzers
        from intelligent_router import IntelligentRouter
        router = IntelligentRouter()
    
    # Initialize analyzers with router
    global task_analyzer, note_analyzer
    if task_analyzer is None:
        task_analyzer = TaskAnalyzer(parser=content_parser, router=router)
    if note_analyzer is None:
        note_analyzer = NoteAnalyzer(parser=content_parser, router=router)
    
    # Route to appropriate analyzer based on detected category
    if category == "task":
        return process_tasks(content, router)
    elif category == "note":
        return process_note_with_analyzer(content, router)
    else:
        # Future: Handle other categories (event, project, etc.)
        # For now, default to task with manual review
        return task_analyzer.analyze_single(content, manual_review=True)

def process_tasks(content, router):
    """Handle single or multiple tasks using new TaskAnalyzer"""
    
    # Use task analyzer for all task processing
    global task_analyzer
    if task_analyzer is None:
        task_analyzer = TaskAnalyzer(parser=content_parser, router=router)
    
    # Split by periods and count 'Task' occurrences
    parts = content.split('.')
    task_occurrences = [i for i, part in enumerate(parts) if 'task' in part.lower().strip()]
    
    if len(task_occurrences) == 1:
        # Single task
        return task_analyzer.analyze_single(content)
    elif len(task_occurrences) > 1:
        # Multiple tasks
        return task_analyzer.analyze_multiple(content, parts, task_occurrences)
    else:
        # Fallback - treat as single task with manual review
        return task_analyzer.analyze_single(content, manual_review=True)

def process_note_with_analyzer(content, router):
    """Process note using new NoteAnalyzer"""
    
    # Use note analyzer
    global note_analyzer
    if note_analyzer is None:
        note_analyzer = NoteAnalyzer(parser=content_parser, router=router)
    
    return note_analyzer.analyze(content)

# OLD FUNCTIONS REMOVED:
# - extract_project_from_content() → Now in ProjectExtractor
# - process_single_task() → Now in TaskAnalyzer.analyze_single()
# - process_multiple_tasks() → Now in TaskAnalyzer.analyze_multiple()
# - process_note() → Now in NoteAnalyzer.analyze()
# - process_unclear_content() → Removed (handled by low-confidence detection)

def process_transcript_file(file_path, dry_run=False, output_dir='processed'):
    """Process a single transcript file - handles both single and multiple analyses"""
    
    try:
        # Validate file before processing
        is_valid, reason = transcript_validator.validate_file(file_path)
        if not is_valid:
            logger.warning(f"❌ Skipping invalid file: {file_path.name}")
            logger.warning(f"   Reason: {reason}")
            return None
        
        # Read the transcript file
        with open(file_path, 'r', encoding='utf-8') as file:
            transcript_text = file.read()
        
        logger.info(f"Processing: {file_path.name}")
        logger.debug(f"Content preview: {transcript_text[:100]}...")
        
        # Log content length category
        length_category = transcript_validator.get_length_category(transcript_text)
        word_count = transcript_validator.get_word_count(transcript_text)
        logger.debug(f"Content: {word_count} words ({length_category})")
        
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
                # 🔒 FIX #1: Only save JSON if at least one Notion entry was created
                if not dry_run:
                    # Check if at least one task has a Notion ID
                    has_notion_ids = any(task.get('notion_entry_id') for task in analysis)
                    
                    if has_notion_ids:
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
                        logger.error(f"🚨 NOT saving JSON - no Notion entries created (prevents data loss)")
                        logger.error(f"   File retained for retry: {file_path.name}")
                        return None  # Return None to signal failure to orchestrator
                else:
                    logger.info(f"🔍 DRY RUN: Would save to: {output_dir}/{file_path.stem}_processed.json")
                
                return analysis if has_notion_ids or dry_run else None
                
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
                # 🔒 FIX #1: Only save JSON if Notion entry was created
                if not dry_run:
                    # Check if analysis has a Notion ID
                    has_notion_id = analysis.get('notion_entry_id') is not None
                    
                    if has_notion_id:
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
                        logger.error(f"🚨 NOT saving JSON - no Notion entry created (prevents data loss)")
                        logger.error(f"   File retained for retry: {file_path.name}")
                        return None  # Return None to signal failure to orchestrator
                else:
                    logger.info(f"🔍 DRY RUN: Would save to: {output_dir}/{file_path.stem}_processed.json")
                
                return analysis if has_notion_id or dry_run else None
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