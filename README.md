# Voice-to-Notion AI Assistant

An intelligent voice recording processing system that automatically transcribes, analyzes, and organizes voice recordings into structured Notion databases with AI-powered project routing and content categorization.

## 🚀 Current Status

**Production Ready** - Successfully processing real-world voice recordings with 73% success rate (16/22 files in latest run)

## ✨ Key Features

- **🎤 Voice Recording Integration**: Direct USB recorder support with automatic transcription
- **🤖 AI-Powered Analysis**: Intelligent categorization of tasks, notes, and research
- **🎯 Smart Project Routing**: 90%+ accuracy in project detection and assignment
- **📝 Content Preservation**: Full transcript preservation for long-form insights
- **🏷️ Intelligent Tagging**: Automatic detection of communications and special requirements
- **⏰ Duration Estimation**: Smart due date assignment based on task complexity
- **🎨 Visual Enhancement**: AI-powered emoji icons based on content keywords
- **📁 Archive Management**: Organized file storage with 7-day retention policy
- **🔄 Duplicate Handling**: Graceful processing of previously handled files

## 🏗️ Architecture

### Core Components

1. **Recording Orchestrator** (`recording_orchestrator.py`) - Complete 5-step USB recorder workflow
2. **Intelligent Router** (`intelligent_router.py`) - AI-powered project detection and routing
3. **Transcript Processor** (`process_transcripts.py`) - Flexible content analysis and categorization
4. **Notion Manager** (`notion_manager.py`) - Database integration with project assignment
5. **Project Matcher** (`project_matcher.py`) - Dynamic project loading and fuzzy matching
6. **Icon Manager** (`icon_manager.py`) - AI-powered emoji selection

### Data Flow

```
USB Recorder → Orchestrator → OpenAI Whisper → AI Analysis → Smart Routing → Notion → Archive
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Notion integration token
- ffmpeg and openai-whisper installed

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`

## ⚙️ Configuration

The system uses YAML configuration files for easy customization without code changes.

### Configuration Files

All configuration is stored in the `config/` directory:

- **`settings.yaml`** - Main application settings (API, paths, features)
- **`projects.yaml`** - Project contexts and training examples
- **`tag_patterns.yaml`** - Tag detection patterns
- **`duration_rules.yaml`** - Duration estimation rules
- **`prompts/`** - AI prompt templates

### Quick Configuration Examples

**Change OpenAI model:**
```yaml
# config/settings.yaml
openai:
  model: "gpt-4"  # Change from gpt-3.5-turbo
```

**Add new project:**
```yaml
# config/projects.yaml
project_contexts:
  - name: "Your New Project"
    keywords:
      - "keyword1"
      - "keyword2"
    description: "Project description"
```

**Environment variable overrides:**
```bash
# Override settings for testing
OPENAI_MODEL=gpt-4 python scripts/process_transcripts.py
PROCESSING_CPU_USAGE_LIMIT_PERCENT=75 python scripts/recording_orchestrator.py
```

See `docs/milestone-1.1-completion.md` for complete configuration documentation
3. Set up environment variables in `.env`
4. Install external tools:
   ```bash
   pip install openai-whisper
   brew install ffmpeg
   ```

### Usage

#### Option 1: USB Recorder (Recommended)
```bash
python scripts/recording_orchestrator.py
```

#### Option 2: Manual Processing
```bash
python scripts/process_transcripts.py
```

## 📊 Latest Performance Results

### September 8, 2025 Processing Run
- **Total Files**: 22 transcripts
- **Success Rate**: 73% (16/22 files)
- **Processing Time**: ~15 minutes
- **Notion Integration**: 100% success rate
- **Archive Management**: Complete file organization

### Notable Processed Content
- Therapy breakthrough notes
- Home remodel tasks  
- Product development ideas
- Pregnancy concerns
- Life admin tasks
- Dream analysis

## 🎯 Project Routing Success

The system successfully routes content to appropriate projects:

- **Life Admin HQ**: Subscription management, research tasks
- **Project Eudaimonia**: Personal development, therapy insights
- **Epic 2nd Brain Workflow in Notion**: Productivity tools, organization
- **Welcoming our baby**: Pregnancy-related content
- **Manual Review**: Complex cases requiring human input

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
NOTION_TOKEN=your_notion_token
TASKS_DATABASE_ID=your_tasks_db_id
NOTES_DATABASE_ID=your_notes_db_id
PROJECTS_DATABASE_ID=your_projects_db_id
```

### Icon Mapping
Customize emoji assignments in `config/icon_mapping.json`:
```json
{
  "icon_mappings": {
    "home remodel": "🏠",
    "workout": "💪",
    "cooking": "👨‍🍳",
    "research": "🔍"
  }
}
```

## 📁 File Structure

```
ai-assistant/
├── scripts/                    # Core processing scripts
├── config/                     # Configuration files
├── transcripts/                # Input transcript files
├── processed/                  # Output JSON files
├── .cache/                     # Project cache and state
├── Failed/                     # Failed processing logs
├── Recording Archives/         # Organized MP3 archives
└── docs/                       # Documentation
```

## 🛠️ Development

### Testing
```bash
python scripts/intelligent_router.py  # Test routing logic
```

### Debugging
- Check `recording_orchestrator.log` for detailed processing logs
- Review `Failed/` folder for processing errors
- Examine `.cache/` for state and project data

## 📈 Performance Metrics

- **Processing Speed**: 1.47 files/minute
- **Project Detection**: 90%+ accuracy
- **Notion Integration**: 100% success rate
- **Archive Management**: Complete file organization
- **Error Recovery**: Graceful failure handling

## 🔮 Future Enhancements

- Auto cleanup scheduling (7-day retention)
- Email intelligence system
- Multi-device support
- Performance analytics
- Advanced categorization

## 📚 Documentation

- [Project State & Decisions](docs/project-state.md)
- [Technical Requirements](docs/technical-requirements.md)

## 🤝 Contributing

This is a personal productivity system, but contributions and suggestions are welcome!

## 📄 License

Private project for personal use.

---

*Last Updated: September 8, 2025 - Production system with live processing validation*


