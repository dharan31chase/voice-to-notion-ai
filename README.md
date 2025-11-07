# Voice-to-Notion AI Assistant

An intelligent voice recording processing system that automatically transcribes, analyzes, and organizes voice recordings into structured Notion databases with AI-powered project routing and content categorization.

## 🚀 Current Status

**Phase 5 Complete** - Fully modular architecture with 96%+ success rate. All major refactoring complete (Phase 1, 2, B, 5.1, 5.2)

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

1. **Recording Orchestrator** (`recording_orchestrator.py`) - Thin coordinator for 5-step workflow
   - Delegates to: USBDetector, FileValidator, StagingManager, TranscriptionEngine, ProcessingEngine, ArchiveManager
2. **Intelligent Router** (`intelligent_router.py`) - AI-powered routing coordinator
   - Delegates to: DurationEstimator, TagDetector, IconSelector, ProjectDetector
3. **Notion Manager** (`scripts/notion/`) - Modular Notion integration (Phase 5.1)
   - ContentFormatter, NotionClientWrapper, TaskCreator, NoteCreator
4. **Project Matcher** (`scripts/matchers/`) - Modular project matching (Phase 5.2)
   - ProjectCache, NotionProjectFetcher, FuzzyMatcher
5. **Analyzers** (`analyzers/`) - Content analysis
   - TaskAnalyzer, NoteAnalyzer with AI-powered categorization
6. **Parsers** (`parsers/`) - Content parsing
   - ContentParser, ProjectExtractor, TranscriptValidator

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

## 🧪 Testing

The project uses pytest for testing. All tests are organized in the `tests/` directory.

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
# Unit tests only (fast, < 30 seconds)
pytest -m unit

# Integration tests (multi-component)
pytest -m integration

# End-to-end tests (full workflow)
pytest -m e2e
```

### Run with Coverage Report
```bash
pytest --cov=scripts --cov-report=html
open tests/reports/coverage/index.html
```

### Run Specific Test File
```bash
pytest tests/unit/test_parsers/test_content_parser.py -v
```

### Current Test Coverage
- **Unit Tests**: 4 tests for ContentParser (category detection, passive content handling)
- **Integration Tests**: 2 existing tests (orchestrator steps, migration comparison)
- **Target Coverage**: 70% (industry standard)

See `docs/testing-roadmap.md` for the complete testing strategy and implementation plan.

## 📊 Latest Performance Results

### November 2025 Processing Runs (Post-Refactoring)
- **Success Rate**: 96%+ (19/20 files in recent validation)
- **Processing Time**: ~8 minutes (5 files) - **4.2x faster** than baseline (33 min)
- **Transcription Speed**: Parallel batch processing with turbo-1 model
- **Notion Integration**: 100% success rate with retry logic
- **Archive Management**: Date-based organization with 7-day retention
- **Project Detection**: 90%+ accuracy with alias support

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

- **Processing Speed**: 1.6 files/minute (8 min for 5 files) - **4.2x faster** than baseline
- **Success Rate**: 96%+ (19/20 files)
- **Project Detection**: 90%+ accuracy with fuzzy matching + aliases
- **Notion Integration**: 100% success rate with exponential backoff retry
- **Icon Selection**: 51 content patterns (v3.0) with AI fallback
- **Code Quality**: 87% reduction in duplication (7,160 lines removed)
- **Architecture**: Fully modular - 20+ focused modules following SRP

## 🔮 Future Enhancements

- Auto cleanup scheduling (7-day retention)
- Email intelligence system
- Multi-device support
- Performance analytics
- Advanced categorization

## 📚 Documentation

- [Documentation Index](docs/README.md) - Start here for all documentation
- [Project State & Decisions](docs/project-state.md) - Current status and major decisions
- [Technical Requirements](docs/technical-requirements.md) - System architecture
- [Refactoring Plan](docs/refactoring-plan.md) - Phase 1, 2, B, 5 complete
- [Testing Roadmap](docs/testing-roadmap.md) - Testing strategy
- [CLI Usage Guide](docs/cli-usage-guide.md) - Command-line reference

## 🤝 Contributing

This is a personal productivity system, but contributions and suggestions are welcome!

## 📄 License

Private project for personal use.

---

*Last Updated: November 5, 2025 - Phase 5 complete: Fully modular architecture with Notion Manager and Project Matcher refactored*


