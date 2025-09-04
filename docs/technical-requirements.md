# AI Assistant Transcript Processing System - Technical Requirements

## 1. System Overview

### 1.1 Purpose
The AI Assistant Transcript Processing System is designed to automatically process voice transcripts from MacWhisper, categorize them as tasks, notes, or research, and intelligently route them to appropriate Notion databases with AI-powered enhancements.

### 1.2 Architecture
- **Input**: Text transcript files (.txt) from MacWhisper OR USB recorder (.mp3) files
- **Processing**: AI-powered analysis and categorization with flexible project extraction
- **Output**: Structured JSON files and Notion database entries with project assignments and emoji icons
- **Integration**: OpenAI GPT-3.5-turbo for AI analysis, OpenAI Whisper for transcription, Notion API for database management
- **Workflow Options**:
  - **Manual**: MacWhisper → .txt → AI Analysis → Notion
  - **Automated**: USB Recorder → Orchestrator → Whisper → AI Analysis → Notion → Archive

## 2. Functional Requirements

### 2.1 Transcript Processing
- **Input Format**: Text files containing voice transcripts
- **Content Format**: Flexible patterns supported:
  - `[Content]. [Task/Note]. [Project Name]`
  - `[Content] [Project Name]. [Task/Note]`
  - `[Content][Project Name] [Task/Note]` (no period)
  - Handles embedded periods, case insensitivity, junk word filtering
- **File Handling**: Process all .txt files in the `transcripts/` directory
- **Output**: Generate processed JSON files in `processed/` directory

### 2.2 Content Categorization
- **Categories**: Task, Note, Research
- **Detection Logic**: Flexible parsing with multiple pattern recognition
- **Default Behavior**: Unclear content defaults to "note" category
- **Confidence Levels**: High, Medium, Low based on AI analysis quality

### 2.3 AI-Powered Analysis

#### 2.3.1 Task Analysis
- **Title Generation**: Create descriptive titles following "Verb + Object" pattern
- **Content Cleaning**: Remove meta-commentary while preserving task details
- **Action Items**: Extract specific actionable tasks
- **Key Insights**: Identify important insights or context

#### 2.3.2 Note Analysis
- **Title Generation**: Create concise, descriptive titles (4-8 words)
- **Content Preservation**: Maintain original voice and content integrity
- **Minimal Processing**: Only basic formatting and paragraph breaks

#### 2.3.3 Research Analysis
- **Same as Note Analysis**: Treated identically to notes
- **Future Enhancement**: Potential for specialized research processing

### 2.4 Intelligent Routing

#### 2.4.1 Project Detection
- **Dynamic Project Loading**: Real-time fetching from Notion Projects database
- **Caching System**: 60-minute cache with smart invalidation
- **Fallback**: Hardcoded project list when Notion API unavailable
- **Detection Method**: Multi-layered fuzzy matching with confidence scoring
- **Alias Support**: Project aliases for variations and abbreviations
- **Fallback**: "Manual Review Required" for unclear matches

#### 2.4.2 Flexible Project Extraction
- **Pattern Recognition**: 1-5 word combinations from end of content
- **Keyword Filtering**: Excludes standalone "task", "note", "project" keywords
- **Embedded Period Handling**: Normalizes periods within project names
- **Case Insensitivity**: Handles mixed case and transcription variations
- **Junk Word Filtering**: Ignores non-English words and background noise
- **Success Rate**: 92% accuracy on test cases, 90% on real-world transcripts

#### 2.4.3 Enhanced Fuzzy Matching
- **Multi-layered Approach**:
  1. Exact project name match (confidence: 1.0)
  2. Exact alias match (confidence: 0.95)
  3. Partial project name match (confidence: 0.8-0.9)
  4. Partial alias match (confidence: 0.75-0.85)
  5. Fuzzy match fallback (confidence: 0.7+)
- **Confidence Threshold**: 80% minimum for project assignment
- **Number Normalization**: Handles "2nd Brain" vs "Second Brain" variations
- **Substring Matching**: Precise matching to avoid false positives

#### 2.4.4 Duration Estimation
- **Categories**: QUICK (≤2 min), MEDIUM (15-30 min), LONG (hours/days)
- **Due Date Logic**:
  - QUICK: Due today
  - MEDIUM: Due end of week (Friday)
  - LONG: Due end of month
- **Output**: JSON with duration category, estimated minutes, due date, and reasoning

#### 2.4.5 Special Tags
- **Communications**: Tasks involving people interaction
- **Needs Jessica Input**: Home, baby, green card, or major decisions
- **AI Review Needed**: When project detection fails
- **Manual Review**: When fuzzy matching confidence is below threshold

### 2.5 Smart Icon Assignment System
- **Icon Selection**: AI-powered emoji assignment based on content keywords
- **Matching Logic**: Priority-based keyword matching (longer phrases first)
- **Content Source**: Uses original transcript content for keyword matching (not just AI-generated titles)
- **Fallback**: Default to ⁉️ if no keywords match
- **Configuration**: External JSON file for maintainable icon mappings
- **Integration**: Page-level emoji icons in Notion (not database properties)

### 2.6 Voice Recording Orchestrator
- **USB Integration**: Automatic detection of Sony IC Recorder at `/Volumes/IC RECORDER/REC_FILE/FOLDER01`
- **5-Step Workflow**:
  1. **Monitor & Detect**: Find new .mp3 recordings and validate
  2. **Prepare & Plan**: Calculate processing requirements and resource needs
  3. **Transcribe**: OpenAI Whisper with parallel processing and CPU monitoring
  4. **Stage & Process**: Integrate with existing AI analysis pipeline
  5. **Verify & Archive**: Archive recordings with 7-day retention and cleanup
- **State Management**: Comprehensive JSON-based session tracking
- **Error Recovery**: Robust failure handling with detailed logging
- **Resource Monitoring**: CPU usage limits (50%) and disk space validation
- **Archive Organization**: Date-based folder structure with session IDs
- **Duplicate Handling**: Smart detection of previously processed files with graceful cleanup
- **JSON Serialization**: Proper handling of Path objects in state files

## 3. Technical Requirements

### 3.1 Dependencies
```
openai==1.100.2
notion-client==2.4.0
python-dotenv==1.1.1
psutil==5.9.0
pathlib (built-in)
json (built-in)
datetime (built-in)
concurrent.futures (built-in)
subprocess (built-in)
shutil (built-in)
```

### 3.1.1 External Dependencies
- **OpenAI Whisper CLI**: `pip install openai-whisper` for audio transcription
- **ffmpeg**: `brew install ffmpeg` for audio file processing
- **System Requirements**: macOS with USB support, minimum 100MB disk space

### 3.2 Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI analysis
- `NOTION_TOKEN`: Notion integration token
- `TASKS_DATABASE_ID`: Notion Tasks database ID
- `NOTES_DATABASE_ID`: Notion Notes database ID
- `PROJECTS_DATABASE_ID`: Notion Projects database ID
- `AREAS_DATABASE_ID`: Notion Areas database ID

### 3.3 File Structure
```
ai-assistant/
├── scripts/
│   ├── process_transcripts.py      # Main processing script with flexible extraction
│   ├── intelligent_router.py       # AI routing logic with icon selection
│   ├── notion_manager.py          # Notion integration with project assignment and icons
│   ├── project_matcher.py         # Dynamic project loading and fuzzy matching
│   ├── icon_manager.py            # AI-powered emoji selection
│   ├── recording_orchestrator.py  # Complete USB recorder workflow
│   └── test_*.py                  # Test scripts
├── config/
│   └── icon_mapping.json         # Configurable icon keyword mappings
├── transcripts/                   # Input transcript files
├── processed/                     # Output JSON files
├── .cache/                        # Project cache and orchestrator state
├── Failed/                        # Failed transcriptions and processing errors
├── Recording Archives/            # Organized .mp3 archives with 7-day retention
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
└── README.md                     # Project overview
```

### 3.4 API Requirements

#### 3.4.1 OpenAI API
- **Model**: gpt-3.5-turbo
- **Max Tokens**: 30-800 depending on analysis type
- **Rate Limits**: Handle API errors gracefully
- **Fallback**: Basic text processing when API fails

#### 3.4.2 Notion API
- **Authentication**: Bearer token
- **Databases**: Tasks, Notes, Projects, Areas
- **Content Blocks**: Paragraph, divider, heading, bulleted list
- **Character Limits**: 2000 characters per block (with chunking)
- **Project Relations**: Two-way relations for project assignment

## 4. Data Models

### 4.1 Analysis Output Structure
```json
{
  "category": "task|note|research",
  "title": "Descriptive title",
  "content": "Full original content",
  "action_items": ["item1", "item2"],
  "key_insights": ["insight1", "insight2"],
  "confidence": "high|medium|low",
  "project": "Matched project name or empty",
  "manual_review": true|false
}
```

### 4.2 Processed File Structure
```json
{
  "original_file": "path/to/transcript.txt",
  "analysis": { /* Analysis Output Structure */ },
  "timestamp": "file_modification_time"
}
```

### 4.3 Multiple Tasks Structure
```json
{
  "original_file": "path/to/transcript.txt",
  "analyses": [
    { /* Analysis Output Structure */ },
    { /* Analysis Output Structure */ }
  ],
  "timestamp": "file_modification_time"
}
```

### 4.4 Project Cache Structure
```json
{
  "projects": [
    {
      "id": "project_id",
      "name": "Project Name",
      "status": "In progress|Ongoing|Backlog|On Hold",
      "aliases": ["alias1", "alias2"],
      "archived": false
    }
  ],
  "metadata": {
    "last_updated": "timestamp",
    "cache_age_minutes": 30,
    "total_projects": 19
  }
}
```

### 4.5 Icon Mapping Structure
```json
{
  "icon_mappings": {
    "home remodel": "🏠",
    "workout": "💪",
    "cooking": "👨‍🍳",
    "reading": "📚",
    "meeting": "🤝",
    "planning": "📋",
    "research": "🔍"
  },
  "metadata": {
    "version": "1.0",
    "total_mappings": 7,
    "last_updated": "timestamp"
  }
}
```

### 4.6 Orchestrator State Structure
```json
{
  "current_session": {
    "session_id": "session_YYYYMMDD_HHMMSS",
    "start_time": "ISO timestamp",
    "recordings_processed": ["file1.mp3", "file2.mp3"],
    "transcripts_created": ["file1.txt", "file2.txt"],
    "ai_processing_success": ["file1.txt"],
    "ai_processing_failed": [],
    "duplicate_skipped": ["file3.txt"],
    "duplicate_cleanup_candidates": [
      {
        "transcript_name": "file3.txt",
        "mp3_name": "file3.mp3",
        "skip_reason": "duplicate"
      }
    ],
    "transcription_complete": true,
    "processing_complete": false,
    "archive_complete": false,
    "cleanup_ready": false
  },
  "previous_sessions": [
    {
      "session_id": "session_YYYYMMDD_HHMMSS",
      "start_time": "ISO timestamp",
      "end_time": "ISO timestamp",
      "cleanup_ready": true,
      "cleanup_date": "ISO timestamp",
      "files_to_delete": {
        "recordings": ["archive_paths"],
        "transcripts": ["transcript_paths"]
      }
    }
  ],
  "archive_management": {
    "last_cleanup": "ISO timestamp",
    "files_to_delete": [],
    "deletion_scheduled": null
  }
}
```

### 4.5 Duration Estimation Structure
```json
{
  "duration_category": "QUICK|MEDIUM|LONG",
  "estimated_minutes": 15,
  "due_date": "YYYY-MM-DD",
  "reasoning": "Explanation of estimation"
}
```

## 5. Error Handling

### 5.1 API Failures
- **OpenAI API**: Fallback to basic text processing
- **Notion API**: Log errors, continue processing other files, fallback to hardcoded projects
- **Network Issues**: Retry logic with exponential backoff

### 5.2 File Processing Errors
- **Missing Files**: Skip and continue
- **Encoding Issues**: Try UTF-8, fallback to system default
- **Malformed Content**: Default to "note" category with low confidence

### 5.3 Content Parsing Errors
- **Invalid Format**: Default to "note" category
- **Missing Periods**: Use flexible extraction logic as fallback
- **Empty Content**: Skip file with warning

### 5.4 Project Matching Errors
- **No Match Found**: Return "Manual Review Required"
- **Low Confidence**: Flag for manual review
- **Cache Issues**: Fallback to hardcoded project list

### 5.5 Duplicate Processing Errors
- **Previously Processed Files**: Detect and skip AI processing, cleanup source files
- **Archive Verification**: Ensure archive exists before cleanup
- **State Corruption**: Handle JSON serialization issues with Path objects

### 5.6 Icon Matching Errors
- **No Keywords Found**: Default to ⁉️ icon
- **Content Access Issues**: Fallback to title-only matching
- **Pattern Matching Failures**: Graceful degradation to default icon

## 6. Performance Requirements

### 6.1 Processing Speed
- **Target**: Process 10+ transcript files per minute
- **AI Analysis**: Parallel processing where possible
- **Notion Integration**: Sequential to avoid rate limits
- **Project Caching**: 60-minute cache reduces API calls
- **Transcription**: 3-4 files in parallel with Whisper, 50% CPU limit
- **Orchestrator**: Complete workflow in 5-15 minutes depending on file count

### 6.2 Resource Usage
- **Memory**: Minimal memory footprint (<100MB)
- **CPU**: Efficient text processing
- **Network**: Optimize API calls to minimize latency
- **Cache**: File-based persistence for project data

### 6.3 Scalability
- **File Volume**: Handle 100+ transcript files per run
- **Content Length**: Support transcripts up to 10,000 characters
- **Concurrent Users**: Single-user system (not multi-tenant)
- **Project Scale**: Support 100+ projects with efficient matching

## 7. Security Requirements

### 7.1 API Key Management
- **Environment Variables**: Store sensitive keys in .env file
- **Access Control**: No hardcoded credentials
- **Key Rotation**: Support for API key updates

### 7.2 Data Privacy
- **Content Processing**: No persistent storage of sensitive content
- **Logging**: Minimal logging, no content in logs
- **Transmission**: Secure API calls over HTTPS
- **Cache**: Local file storage only, no external data sharing

## 8. Testing Requirements

### 8.1 Unit Tests
- **Category Detection**: Test all categorization scenarios
- **Project Extraction**: Test flexible pattern matching with real-world examples
- **Fuzzy Matching**: Test multi-layered matching with confidence scoring
- **AI Analysis**: Mock API responses for consistent testing
- **Error Handling**: Test all error conditions

### 8.2 Integration Tests
- **End-to-End**: Full processing pipeline
- **Notion Integration**: Test database creation and project assignment
- **API Integration**: Test OpenAI and Notion API interactions
- **Cache System**: Test project loading and invalidation
- **Orchestrator Pipeline**: Test complete 5-step workflow
- **Icon System**: Test emoji assignment and Notion integration
- **Archive Management**: Test file archiving and cleanup processes
- **Duplicate Handling**: Test processing of previously processed files
- **Icon Matching**: Test content-based icon selection with various keywords
- **State Management**: Test JSON serialization and session tracking

### 8.3 Test Data
- **Sample Transcripts**: Various formats and content types
- **Edge Cases**: Malformed content, empty files, special characters
- **Project Variations**: Different project name formats and aliases
- **Expected Outputs**: Known good results for validation

## 9. Maintenance Requirements

### 9.1 Monitoring
- **Processing Logs**: Track success/failure rates
- **API Usage**: Monitor OpenAI and Notion API usage
- **Performance Metrics**: Processing time and resource usage
- **Project Matching**: Track accuracy and manual review rates

### 9.2 Updates
- **Dependency Updates**: Regular security and feature updates
- **API Changes**: Adapt to OpenAI and Notion API changes
- **Project Mapping**: Update project keywords and descriptions
- **Cache Management**: Monitor cache performance and invalidation

### 9.3 Backup
- **Processed Files**: Archive processed JSON files
- **Configuration**: Backup environment variables and settings
- **Test Data**: Maintain test files for regression testing
- **Cache Files**: Backup project cache for recovery

## 10. Future Enhancements

### 10.1 Planned Features
- **Auto Cleanup Scheduling**: Automated 7-day archive cleanup
- **Multi-language Support**: Process transcripts in different languages
- **Advanced Categorization**: More sophisticated content classification
- **Batch Processing**: Process multiple files simultaneously
- **Web Interface**: GUI for transcript processing
- **Project Learning**: Improve matching based on user corrections
- **Multi-Device Support**: Extend orchestrator to other recording devices
- **Progress Tracking**: Real-time progress bars and status updates
- **Email Notifications**: Success/failure alerts for completed sessions
- **Performance Analytics**: Track processing times and resource usage

### 10.2 Potential Integrations
- **Calendar Integration**: Auto-schedule tasks based on due dates
- **Email Integration**: Send notifications for important tasks
- **Slack Integration**: Post updates to team channels
- **Analytics Dashboard**: Track productivity and task completion

### 10.3 Scalability Improvements
- **Database Storage**: Store processed data in local database
- **Caching**: Cache AI analysis results for similar content
- **Queue System**: Process transcripts asynchronously
- **Microservices**: Split functionality into separate services
- **Machine Learning**: Train custom models for project detection
