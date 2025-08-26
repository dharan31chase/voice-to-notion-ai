# AI Assistant Transcript Processing System - Technical Requirements

## 1. System Overview

### 1.1 Purpose
The AI Assistant Transcript Processing System is designed to automatically process voice transcripts from MacWhisper, categorize them as tasks, notes, or research, and intelligently route them to appropriate Notion databases with AI-powered enhancements.

### 1.2 Architecture
- **Input**: Text transcript files (.txt) from MacWhisper
- **Processing**: AI-powered analysis and categorization
- **Output**: Structured JSON files and Notion database entries
- **Integration**: OpenAI GPT-3.5-turbo for AI analysis, Notion API for database management

## 2. Functional Requirements

### 2.1 Transcript Processing
- **Input Format**: Text files containing voice transcripts
- **Content Format**: `[Content]. [Task/Note]. [Project Name]`
  - Example: "Email regarding plumbing repairs. Task. Life Admin HQ"
- **File Handling**: Process all .txt files in the `transcripts/` directory
- **Output**: Generate processed JSON files in `processed/` directory

### 2.2 Content Categorization
- **Categories**: Task, Note, Research
- **Detection Logic**: Parse content by periods to extract category from second segment
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
- **Supported Projects**:
  - Green Card Application
  - Improve my Product Sense & Taste
  - Epic 2nd Brain Workflow in Notion
  - Project Eudaimonia: Focus. Flow. Fulfillment.
- **Detection Method**: AI-powered keyword matching with fallback logic
- **Fallback**: "Manual Review Required" for unclear matches

#### 2.4.2 Duration Estimation
- **Categories**: QUICK (≤2 min), MEDIUM (15-30 min), LONG (hours/days)
- **Due Date Logic**:
  - QUICK: Due today
  - MEDIUM: Due end of week (Friday)
  - LONG: Due end of month
- **Output**: JSON with duration category, estimated minutes, due date, and reasoning

#### 2.4.3 Special Tags
- **Communications**: Tasks involving people interaction
- **Needs Jessica Input**: Home, baby, green card, or major decisions
- **AI Review Needed**: When project detection fails

## 3. Technical Requirements

### 3.1 Dependencies
```
openai==1.100.2
notion-client==2.4.0
python-dotenv==1.1.1
pathlib (built-in)
json (built-in)
datetime (built-in)
```

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
│   ├── process_transcripts.py      # Main processing script
│   ├── intelligent_router.py       # AI routing logic
│   ├── notion_manager.py          # Notion integration
│   └── test_*.py                  # Test scripts
├── transcripts/                   # Input transcript files
├── processed/                     # Output JSON files
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

## 4. Data Models

### 4.1 Analysis Output Structure
```json
{
  "category": "task|note|research",
  "title": "Descriptive title",
  "content": "Full original content",
  "action_items": ["item1", "item2"],
  "key_insights": ["insight1", "insight2"],
  "confidence": "high|medium|low"
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

### 4.3 Duration Estimation Structure
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
- **Notion API**: Log errors, continue processing other files
- **Network Issues**: Retry logic with exponential backoff

### 5.2 File Processing Errors
- **Missing Files**: Skip and continue
- **Encoding Issues**: Try UTF-8, fallback to system default
- **Malformed Content**: Default to "note" category with low confidence

### 5.3 Content Parsing Errors
- **Invalid Format**: Default to "note" category
- **Missing Periods**: Use endswith logic as fallback
- **Empty Content**: Skip file with warning

## 6. Performance Requirements

### 6.1 Processing Speed
- **Target**: Process 10+ transcript files per minute
- **AI Analysis**: Parallel processing where possible
- **Notion Integration**: Sequential to avoid rate limits

### 6.2 Resource Usage
- **Memory**: Minimal memory footprint (<100MB)
- **CPU**: Efficient text processing
- **Network**: Optimize API calls to minimize latency

### 6.3 Scalability
- **File Volume**: Handle 100+ transcript files per run
- **Content Length**: Support transcripts up to 10,000 characters
- **Concurrent Users**: Single-user system (not multi-tenant)

## 7. Security Requirements

### 7.1 API Key Management
- **Environment Variables**: Store sensitive keys in .env file
- **Access Control**: No hardcoded credentials
- **Key Rotation**: Support for API key updates

### 7.2 Data Privacy
- **Content Processing**: No persistent storage of sensitive content
- **Logging**: Minimal logging, no content in logs
- **Transmission**: Secure API calls over HTTPS

## 8. Testing Requirements

### 8.1 Unit Tests
- **Category Detection**: Test all categorization scenarios
- **AI Analysis**: Mock API responses for consistent testing
- **Error Handling**: Test all error conditions

### 8.2 Integration Tests
- **End-to-End**: Full processing pipeline
- **Notion Integration**: Test database creation and updates
- **API Integration**: Test OpenAI and Notion API interactions

### 8.3 Test Data
- **Sample Transcripts**: Various formats and content types
- **Edge Cases**: Malformed content, empty files, special characters
- **Expected Outputs**: Known good results for validation

## 9. Maintenance Requirements

### 9.1 Monitoring
- **Processing Logs**: Track success/failure rates
- **API Usage**: Monitor OpenAI and Notion API usage
- **Performance Metrics**: Processing time and resource usage

### 9.2 Updates
- **Dependency Updates**: Regular security and feature updates
- **API Changes**: Adapt to OpenAI and Notion API changes
- **Project Mapping**: Update project keywords and descriptions

### 9.3 Backup
- **Processed Files**: Archive processed JSON files
- **Configuration**: Backup environment variables and settings
- **Test Data**: Maintain test files for regression testing

## 10. Future Enhancements

### 10.1 Planned Features
- **Multi-language Support**: Process transcripts in different languages
- **Advanced Categorization**: More sophisticated content classification
- **Batch Processing**: Process multiple files simultaneously
- **Web Interface**: GUI for transcript processing

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
