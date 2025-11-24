# Component Inventory: Epic 2nd Brain System
**Generated**: 2025-11-24
**Purpose**: Systems architecture discovery for diagram generation
**Scope**: ai-assistant/ repository only

---

## Executive Summary

The ai-assistant (Epic 2nd Brain) system is a **voice-to-knowledge pipeline** that transforms Sony recorder audio files into structured Notion database entries through multi-stage orchestration. The architecture consists of:

- **6 major subsystems** (MCP, Voice Pipeline, AI Processing, Notion Sync, RAG, Git Integration)
- **50+ Python modules** organized in modular layers
- **4 external API dependencies** (OpenAI, Notion, Groq, GitHub)
- **3 human interaction points** (Claude Chat, Claude Code, Git commits)
- **2 storage layers** (Local filesystem + Notion databases)

**Key Characteristic**: The system is a **push-based workflow** - Sony recorder files trigger processing that flows through transcription → AI analysis → Notion creation, with git commits triggering backward sync to update Notion roadmap items.

---

## Component Inventory

### 1. MCP Server (Model Context Protocol)
**Purpose**: Expose tools for Claude Chat (web) to interact with both projects

#### 1.1 Full Server (`mcp_server/full_server.py`)
**Location**: `mcp_server/full_server.py` (1,872 lines)
**Purpose**: Primary MCP server providing 9 tools for Claude Chat
**Inputs**: MCP tool calls from Claude Desktop app
**Outputs**: File contents, Notion data, session logs
**Dependencies**:
- `notion-client` (Notion API)
- `fastmcp` (MCP protocol implementation)
- Internal: `docs/config/project-paths.json`, `docs/config/context-profiles.json`
**Triggers**: Auto-launched by Claude Desktop on startup (configured in `~/.config/claude/claude_desktop_config.json`)

**Tools Provided**:
1. `read_file(path, project)` - Read files from ai-assistant or legacy-ai repos
2. `write_file(path, content, project)` - Write PRDs, session logs, docs
3. `start_session(project, workstream)` - Load context with intelligent file selection
4. `end_session(project, summary, duration)` - Create session logs + update Notion
5. `search_docs(query, doc_types, project)` - Keyword search across markdown docs
6. `query_strategy_board(filter_status, limit, project)` - Query Notion Strategy Board
7. `update_initiative_status(page_id, new_status, notes)` - Update Strategy Board items
8. `write_to_page_content(page_id, content)` - Write to Notion page content
9. `save_context_profile(project, workstream, files)` - Save learned context preferences

**Context Loading Mechanism** (Friction Point #1):
- **Phase 1 (Legacy)**: Loads all files from `context_folders` (10-16 docs, noisy)
- **Phase 2 (Intelligent)**: Uses `suggest_files_for_workstream()` to recommend 3-6 files
  - Workstream-specific config in `project-paths.json` (synthesis, interview-analysis, etc.)
  - Falls back to generic heuristics if no config
  - Saves user selections to `context-profiles.json` for next time
  - File classification: always, latest, exemplar, synthesis, optional

#### 1.2 Simple Server (`mcp_server/simple_server.py`)
**Status**: Legacy, replaced by full_server.py

#### 1.3 Context Profile Optimization
**Location**: `docs/config/context-profiles.json`
**Purpose**: Learned preferences for which files to load per project+workstream
**Format**: `{ "profiles": { "Project Name": { "workstream": { "files": [...], "usage_count": N } } } }`
**Usage**: Read by `start_session`, written by `save_context_profile`

---

### 2. Voice Recording Pipeline
**Purpose**: Process Sony recorder audio files → structured Notion entries

#### 2.1 Recording Orchestrator (`scripts/recording_orchestrator.py`)
**Location**: `scripts/recording_orchestrator.py` (1,500+ lines)
**Purpose**: End-to-end orchestration of voice recording processing
**Inputs**:
- Sony recorder USB mount at `/Volumes/IC RECORDER/REC_FILE/FOLDER01`
- .mp3 audio files (typically 30sec - 5min)
**Outputs**:
- Notion task/note entries in 2nd Brain database
- Processed JSON files in `processed/`
- Archived recordings in `Recording Archives/YYYY-MM-DD/`
**Dependencies**:
- USB detector (Phase B Step 3)
- Staging manager (Phase B Step 4)
- Transcription engine (Phase B Step 5)
- Processing engine (Phase B Step 6)
- Notion uploader (Phase B Step 7)
- Archive manager (Phase B Step 8)
**Triggers**: Manual execution via `python scripts/recording_orchestrator.py`

**Workflow**:
1. **USB Detection** → Scan for Sony recorder mount
2. **File Validation** → Check for valid .mp3 files
3. **Staging** → Copy files to local `staging/` folder
4. **Transcription** → Groq Whisper API (sequential)
5. **AI Processing** → OpenAI analysis (task vs note classification)
6. **Notion Upload** → Create database entries
7. **Archival** → Move to `Recording Archives/` by date
8. **State Tracking** → Update `.cache/recording_states.json`

**CLI Options**:
- `--dry-run`: Preview without file operations
- `--skip-steps`: Skip specific steps (e.g., "usb,archive")
- `--auto-continue`: Skip manual confirmations
- `--max-files N`: Limit batch size

#### 2.2 Orchestration Modules (`scripts/orchestration/`)

##### State Management
**Location**: `scripts/orchestration/state/state_manager.py`
**Purpose**: Track processing state to prevent reprocessing
**Storage**: `.cache/recording_states.json`
**State Machine**: `pending → staged → transcribed → analyzed → uploaded → archived → failed`

##### USB Detection
**Location**: `scripts/orchestration/detection/`
**Purpose**: Detect Sony recorder USB mount and validate files
**Classes**: `USBDetector`, `FileValidator`

##### Staging
**Location**: `scripts/orchestration/staging/staging_manager.py`
**Purpose**: Copy files from USB to local staging area
**Why**: Allows USB unmount while processing continues

##### Transcription Engine
**Location**: `scripts/orchestration/transcription/`
**Purpose**: Convert audio → text via Groq Whisper API
**Components**:
- `transcription_engine.py` - Main coordinator
- `backends/groq_backend.py` - Groq API implementation
- `backends/local_whisper_backend.py` - Local fallback (not used)
- `batch_manager.py` - Batch processing logic
- `resource_monitor.py` - Track API usage
**API**: Groq Whisper API (faster + cheaper than OpenAI)
**Mode**: Sequential processing (rate limit safety)

##### Processing Engine
**Location**: `scripts/orchestration/processing/`
**Purpose**: AI analysis of transcripts (task vs note, project detection, etc.)
**Components**:
- `processing_engine.py` - Main coordinator
- `ai_processor.py` - OpenAI API calls
**Delegates To**:
- `analyzers/task_analyzer.py` - Task-specific analysis
- `analyzers/note_analyzer.py` - Note-specific analysis
- `scripts/intelligent_router.py` - Project/tag/icon routing

##### Notion Uploader
**Location**: `scripts/orchestration/notion/notion_uploader.py`
**Purpose**: Create Notion database entries from processed transcripts
**API**: Notion API via `notion-client`

##### Archive Manager
**Location**: `scripts/orchestration/archival/archive_manager.py`
**Purpose**: Move processed recordings to date-stamped archive folders
**Structure**: `Recording Archives/YYYY-MM-DD/[original_filename].mp3`

---

### 3. AI Processing Layer
**Purpose**: Classify and enrich transcript content with AI

#### 3.1 Intelligent Router (`scripts/intelligent_router.py`)
**Location**: `scripts/intelligent_router.py` (243 lines - refactored from 430)
**Purpose**: Facade for 4 specialized AI routers
**Architecture**: Pure delegation pattern, zero business logic
**Refactoring**: Phase A complete (Oct 31 - Nov 1, 2025) - 67% size reduction

**Delegates To**:
1. `scripts/routers/project_detector.py` - AI-powered project classification
2. `scripts/routers/duration_estimator.py` - Duration + due date estimation
3. `scripts/routers/tag_detector.py` - Multi-select tag detection
4. `scripts/routers/icon_selector.py` - 3-tier icon fallback selection

**Methods**:
- `detect_project(content)` → Project name or "Manual Review Required"
- `estimate_duration_and_due_date(content)` → {duration, due_date, reasoning}
- `detect_special_tags(content)` → List of exact Notion tag values
- `select_icon_for_analysis(title, project, content)` → Emoji icon

#### 3.2 Specialized Routers (`scripts/routers/`)

##### Project Detector
**Location**: `scripts/routers/project_detector.py`
**Purpose**: Classify transcript into one of user's active projects
**Method**: OpenAI GPT-4 with project definitions from `config/projects.yaml`
**Output**: Exact Notion project name or "Manual Review Required"

##### Duration Estimator
**Location**: `scripts/routers/duration_estimator.py`
**Purpose**: Estimate task duration and suggest due date
**Method**: Rule-based heuristics from `config/duration_rules.yaml`
**Output**: {duration_category: QUICK/MEDIUM/LONG, estimated_minutes, due_date}

##### Tag Detector
**Location**: `scripts/routers/tag_detector.py`
**Purpose**: Detect special tags (Communications, Needs Jessica Input, etc.)
**Method**: OpenAI GPT-4 with tag patterns from `config/tag_patterns.yaml`
**Output**: List of exact Notion multi-select values (emoji-included)

##### Icon Selector
**Location**: `scripts/routers/icon_selector.py`
**Purpose**: Select emoji icon based on content/title/project
**Method**: 3-tier fallback (content → title → project → default)
**Config**: `config/icon_mapping.json`

#### 3.3 Analyzers (`analyzers/`)

##### Task Analyzer
**Location**: `analyzers/task_analyzer.py`
**Purpose**: Analyze task-type transcripts (actionable items)
**Output**: {title, category, project, tags, duration, due_date, icon}

##### Note Analyzer
**Location**: `analyzers/note_analyzer.py`
**Purpose**: Analyze note-type transcripts (information capture)
**Output**: {title, category, project, tags, icon}

#### 3.4 Parsers (`parsers/`)

##### Content Parser
**Location**: `parsers/content_parser.py`
**Purpose**: Parse and clean transcript text
**Methods**: Remove filler words, normalize spacing

##### Transcript Validator
**Location**: `parsers/transcript_validator.py`
**Purpose**: Validate transcript structure and content
**Checks**: Min length, valid UTF-8, required fields

##### Project Extractor
**Location**: `parsers/project_extractor.py`
**Purpose**: Extract project references from content
**Method**: Keyword matching + NLP

---

### 4. Notion Integration Layer
**Purpose**: Read/write Notion databases and pages

#### 4.1 Notion Client Wrapper (`scripts/notion/notion_client_wrapper.py`)
**Location**: `scripts/notion/notion_client_wrapper.py`
**Purpose**: Thin wrapper around `notion-client` for error handling
**Dependencies**: `notion-client` Python package

#### 4.2 Notion Manager (`scripts/notion_manager.py`)
**Location**: `scripts/notion_manager.py` (1,094 lines)
**Purpose**: High-level Notion operations (create tasks, notes, etc.)
**Methods**:
- `create_task()` - Create task in 2nd Brain database
- `create_note()` - Create note entry
- `query_database()` - Query database with filters
- `update_page()` - Update page properties

#### 4.3 Specialized Notion Modules (`scripts/notion/`)

##### Task Creator
**Location**: `scripts/notion/task_creator.py`
**Purpose**: Create task entries with full property mapping

##### Note Creator
**Location**: `scripts/notion/note_creator.py`
**Purpose**: Create note entries with metadata

##### Content Formatter
**Location**: `scripts/notion/content_formatter.py`
**Purpose**: Format markdown content for Notion blocks
**Types**: Basic formatter (paragraph, headings, lists)

##### Smart Content Formatter
**Location**: `scripts/notion/smart_content_formatter.py`
**Purpose**: Advanced formatting with tables, embeds, etc.

##### Page Fetcher
**Location**: `scripts/notion/page_fetcher.py`
**Purpose**: Fetch Notion page content for analysis

#### 4.4 Notion Validator (`validators/notion_validator.py`)
**Location**: `validators/notion_validator.py`
**Purpose**: Validate Notion data structures before upload
**Checks**: Required properties, valid select values, character limits

---

### 5. Notion Sync Engine (Git → Notion)
**Purpose**: Sync git commits back to Notion databases

#### 5.1 Sync to Notion Script (`scripts/sync_to_notion.py`)
**Location**: `scripts/sync_to_notion.py` (450+ lines)
**Purpose**: Parse git commits and update Notion Roadmap + Sessions databases
**Inputs**:
- Commit message (with `[ROADMAP-X]` tags)
- Commit hash, author, date
- Changed files list
**Outputs**:
- Updated Roadmap database entries
- New Sessions database entries
**Triggers**: Git post-commit hook (`.git/hooks/post-commit`)

**Workflow** (Friction Point #3):
1. **Parse commit message** → Extract `[ROADMAP-X]` references
2. **Query Roadmap DB** → Find matching Roadmap entries by ID
3. **Update Roadmap item** → Set status, last updated, commit link
4. **Create Session entry** → Log session in Sessions database
5. **Link Session ↔ Roadmap** → Relation property

**Delay**: Runs synchronously in post-commit hook (~2-5 seconds)

#### 5.2 Git Post-Commit Hook (`.git/hooks/post-commit`)
**Location**: `.git/hooks/post-commit`
**Purpose**: Trigger Notion sync after each commit
**Workflow**:
1. Extract commit metadata (message, hash, author, date, files)
2. Call `python3 scripts/sync_to_notion.py` with metadata
3. Push to GitHub (`git push origin main`)

**Non-blocking**: Errors logged but don't block commit

---

### 6. RAG System (Retrieval-Augmented Generation)
**Purpose**: Semantic search over Legacy AI customer interview corpus

#### 6.1 RAG Architecture (`scripts/rag/`)

##### MCP Server
**Location**: `scripts/rag/mcp_server.py`
**Purpose**: Expose RAG tools via MCP for Claude Chat
**Tools**:
- `search_legacy_corpus(query, top_k, content_type, customer_name)` - Semantic search
- `get_chunk_context(chunk_id, lines_before, lines_after)` - Expand context around result
- `read_source_document(file_path)` - Read full source file

**Note**: This is a SEPARATE MCP server from `mcp_server/full_server.py` (runs on different port)

##### Indexer
**Location**: `scripts/rag/indexer.py`
**Purpose**: Build vector + BM25 indexes from corpus
**Process**: Scan markdown → chunk → embed → store
**Triggers**: Manual via `python scripts/rag/indexer.py`

##### Chunker
**Location**: `scripts/rag/chunker.py`
**Purpose**: Split documents into semantic chunks
**Strategy**: Header-aware chunking (respects # ## ### structure)
**Config**: `config/rag_config.yaml` (max_chunk_tokens: 2000, overlap: 200)

##### Embeddings
**Location**: `scripts/rag/embeddings.py`
**Purpose**: Generate embeddings via OpenAI API
**Model**: `text-embedding-3-small` (1536 dimensions)
**Batch Size**: 100 texts per API call

##### Storage
**Location**: `scripts/rag/storage.py`
**Purpose**: Vector database interface (ChromaDB)
**Storage Path**: `~/.cache/legacy-ai-rag/chroma`

##### BM25 Index
**Location**: `scripts/rag/bm25_index.py`
**Purpose**: Traditional keyword search index
**Storage**: `~/.cache/legacy-ai-rag/bm25_index.pkl`

##### Searcher
**Location**: `scripts/rag/searcher.py`
**Purpose**: Hybrid search (BM25 + semantic embeddings)
**Algorithm**: Reciprocal Rank Fusion (RRF) with k=60
**Weights**: 30% BM25, 70% semantic

##### Reranker
**Location**: `scripts/rag/reranker.py`
**Purpose**: Rerank search results with cross-encoder
**Model**: `BAAI/bge-reranker-base` (runs on Apple Silicon MPS)
**Process**: Take top 50 from hybrid search → rerank → return top 5

#### 6.2 RAG Configuration (`config/rag_config.yaml`)
**Location**: `config/rag_config.yaml`
**Purpose**: Centralized RAG settings
**Sections**: corpus, chunking, embeddings, storage, bm25, reranker, search, logging

**Corpus Path**: `~/Documents/1. Projects/legacy-ai/research`
**Note**: RAG system lives in ai-assistant repo but indexes legacy-ai repo

---

### 7. Configuration System
**Purpose**: Centralized YAML-based configuration

#### 7.1 Config Loader (`core/config_loader.py`)
**Location**: `core/config_loader.py` (300+ lines)
**Purpose**: Load all YAML configs with environment variable overrides
**Priority**: ENV Variable > YAML > Hardcoded Default
**Features**:
- Dot notation access: `config.get("openai.model")`
- Lazy loading
- Validation with sensible defaults

#### 7.2 Configuration Files (`config/`)

##### settings.yaml
**Location**: `config/settings.yaml`
**Purpose**: Global settings (OpenAI model, Notion DB IDs, etc.)
**Key Sections**: openai, notion, transcription, processing

##### projects.yaml
**Location**: `config/projects.yaml`
**Purpose**: Define user's active projects for classification
**Format**: List of {name, description, keywords}

##### icon_mapping.json
**Location**: `config/icon_mapping.json`
**Purpose**: Map keywords → emoji icons
**Format**: {keyword: emoji} pairs

##### tag_patterns.yaml
**Location**: `config/tag_patterns.yaml`
**Purpose**: Patterns for detecting special tags
**Format**: {tag_name: {patterns: [regex], examples: [...]}}

##### duration_rules.yaml
**Location**: `config/duration_rules.yaml`
**Purpose**: Rules for estimating task duration
**Categories**: QUICK (<30min), MEDIUM (30min-2hr), LONG (>2hr)

##### parsing_rules.yaml
**Location**: `config/parsing_rules.yaml`
**Purpose**: Rules for parsing and cleaning transcripts
**Sections**: filler_words, normalization, validation

##### note_types.yaml
**Location**: `config/note_types.yaml`
**Purpose**: Define note categories (research, reflection, etc.)

##### task_tags.yaml
**Location**: `config/task_tags.yaml`
**Purpose**: Define task-specific tags

##### content_formatters.yaml
**Location**: `config/content_formatters.yaml`
**Purpose**: Configuration for Notion content formatting

##### rag_config.yaml
**Location**: `config/rag_config.yaml`
**Purpose**: RAG system configuration (documented above)

##### project-paths.json
**Location**: `docs/config/project-paths.json`
**Purpose**: Multi-project support (ai-assistant + legacy-ai)
**Format**:
```json
{
  "projects": [
    {
      "name": "Legacy AI",
      "aliases": ["legacy", "customer discovery"],
      "root_path": "/path/to/legacy-ai",
      "folders_to_scan": [...],
      "always_files": [...],
      "workstreams": {
        "synthesis": {...},
        "interview-analysis": {...}
      }
    }
  ]
}
```

##### file-type-patterns.json
**Location**: `docs/config/file-type-patterns.json`
**Purpose**: Classify files for intelligent context loading
**Types**: always, latest, exemplar, synthesis, optional

##### context-profiles.json
**Location**: `docs/config/context-profiles.json`
**Purpose**: Learned user preferences for context loading (documented above)

---

### 8. Core Utilities (`core/`)

#### 8.1 Logging Utils
**Location**: `core/logging_utils.py`
**Purpose**: Unified logging configuration
**Features**: Color output, file logging, structured logging

#### 8.2 OpenAI Client
**Location**: `core/openai_client.py`
**Purpose**: Wrapper around OpenAI API with retry logic
**Methods**: `chat_completion()`, `embedding()`

#### 8.3 File Utils
**Location**: `core/file_utils.py`
**Purpose**: Common file operations (safe delete, atomic write, etc.)

#### 8.4 Performance Tracker
**Location**: `core/performance_tracker.py`
**Purpose**: Track timing and resource usage

---

### 9. Session Management Scripts

#### 9.1 End Session Script (`scripts/end_session.py`)
**Location**: `scripts/end_session.py` (303 lines)
**Purpose**: End Claude Code session and update Notion
**Workflow** (Friction Point #2):
1. Fetch most recent session from Notion Sessions DB
2. Update with metadata (duration, decisions, next steps, alerts)
3. Optionally update Roadmap items

**Usage**:
```bash
python3 scripts/end_session.py \
  --duration 120 \
  --decisions "Decided X" \
  --next-steps "Build Y"
```

**Friction**: Manual invocation required (not auto-triggered by Claude Code)

#### 9.2 Session Logs (`docs/sessions/`)

##### Claude Code Sessions
**Location**: `docs/sessions/claude-code/`
**Format**: `YYYY-MM-DD-topic.md`
**Created By**: Claude Code via Write tool (manual)

##### Claude Chat Sessions
**Location**: `docs/sessions/claude-chat/`
**Format**: `YYYY-MM-DD-topic.md`
**Created By**: `end_session` MCP tool (automated)

---

### 10. Handoff System
**Purpose**: Coordinate Claude Chat ↔ Claude Code transitions

#### 10.1 Handoff Documents (`docs/handoffs/`)
**Location**: `docs/handoffs/`
**Format**: `YYYY-MM-DD-to-claude-code-topic.md`
**Created By**: `end_session` MCP tool (when `create_handoff=True`)

**Structure**:
1. Git commands (checkout branch, commit, push)
2. Implementation mode (INTERACTIVE vs autonomous)
3. What to build (goals, success criteria)
4. Documents to reference (PRD, one-pager, Notion links)
5. High-level context
6. Clarifying questions

**Friction Point #4**:
- **Current**: Handoff document created in repo, user manually copy-pastes to Claude Code
- **No Automation**: No direct API to inject prompt into Claude Code session

#### 10.2 Handoff Template Generation
**Location**: `mcp_server/full_server.py` (function `generate_handoff_template()`)
**Purpose**: Generate standardized handoff prompts
**Inputs**: Summary, decisions, next steps, PRD path, one-pager location, initiative ID
**Output**: Markdown handoff document

---

### 11. Other Scripts

#### 11.1 Process Transcripts (`scripts/process_transcripts.py`)
**Location**: `scripts/process_transcripts.py`
**Purpose**: Standalone transcript processing (without USB orchestration)
**Usage**: Process JSON transcript files directly

#### 11.2 Reprocess Failed (`scripts/reprocess_failed.py`)
**Location**: `scripts/reprocess_failed.py`
**Purpose**: Retry failed recordings from `Failed/` folder

#### 11.3 Fetch Notion Page (`scripts/fetch_notion_page.py`)
**Location**: `scripts/fetch_notion_page.py`
**Purpose**: Fetch Notion page content for offline analysis

#### 11.4 Backfill Roadmap (`scripts/backfill_roadmap.py`)
**Location**: `scripts/backfill_roadmap.py`
**Purpose**: Backfill Roadmap database entries from git history

#### 11.5 Migrate Session Roadmap Links (`scripts/migrate_session_roadmap_links.py`)
**Location**: `scripts/migrate_session_roadmap_links.py`
**Purpose**: Migrate old session logs to new Roadmap schema

#### 11.6 Icon Manager (`scripts/icon_manager.py`)
**Location**: `scripts/icon_manager.py`
**Purpose**: Manage icon mappings (add, remove, list)

#### 11.7 Project Matcher (`scripts/project_matcher.py`)
**Location**: `scripts/project_matcher.py`
**Purpose**: Test project detection accuracy

#### 11.8 Analyze Transcripts Scripts
**Location**: `scripts/analyze_successful_transcripts.py`, `scripts/analyze_transcript_endings.py`
**Purpose**: Analytics on transcript processing

---

## Data Flow Map

### Primary Data Flow: Voice → Notion

```
Sony Recorder .mp3 Files
  ↓
[USB Detection] (scripts/orchestration/detection/)
  ↓
[Staging] (scripts/orchestration/staging/) → staging/
  ↓
[Transcription] (scripts/orchestration/transcription/) → Groq Whisper API
  ↓
[AI Processing] (scripts/orchestration/processing/) → OpenAI GPT-4
  ├─ Task Analyzer (analyzers/task_analyzer.py)
  ├─ Note Analyzer (analyzers/note_analyzer.py)
  └─ Intelligent Router (scripts/intelligent_router.py)
      ├─ Project Detector → OpenAI
      ├─ Duration Estimator → Rule-based
      ├─ Tag Detector → OpenAI
      └─ Icon Selector → Config lookup
  ↓
[Notion Upload] (scripts/orchestration/notion/) → Notion API
  ↓
[Archival] (scripts/orchestration/archival/) → Recording Archives/YYYY-MM-DD/
  ↓
[State Update] (scripts/orchestration/state/) → .cache/recording_states.json
```

### Secondary Data Flow: Git → Notion

```
Git Commit
  ↓
[Post-Commit Hook] (.git/hooks/post-commit)
  ↓
[Sync to Notion Script] (scripts/sync_to_notion.py)
  ├─ Parse commit message → Extract [ROADMAP-X] tags
  ├─ Query Roadmap DB → Find matching entries
  ├─ Update Roadmap → Set status, last updated
  └─ Create Session → Link to Roadmap
  ↓
[GitHub Push] (git push origin main)
```

### Tertiary Data Flow: Claude Chat Context Loading

```
Claude Chat (web)
  ↓
[MCP start_session Tool] (mcp_server/full_server.py)
  ├─ Load project config → docs/config/project-paths.json
  ├─ Check learned profile → docs/config/context-profiles.json
  │   ├─ Profile exists → Show learned files
  │   └─ No profile → Suggest files (workstream config or heuristics)
  ├─ Query Strategy Board → Notion API
  └─ Load roadmap → ROADMAP.md
  ↓
[User Confirms Files]
  ↓
[save_context_profile Tool] → Update context-profiles.json
  ↓
[Files Loaded into Context] (Claude Chat reads files via read_file tool)
```

### Quaternary Data Flow: RAG Search

```
Claude Chat (web)
  ↓
[MCP search_legacy_corpus Tool] (scripts/rag/mcp_server.py)
  ↓
[RAG Searcher] (scripts/rag/searcher.py)
  ├─ BM25 Search (scripts/rag/bm25_index.py) → Top 50 keyword matches
  ├─ Semantic Search (scripts/rag/storage.py) → Top 50 embedding matches
  └─ Hybrid Fusion (RRF) → Merge to top 50
  ↓
[Reranker] (scripts/rag/reranker.py) → BAAI/bge-reranker-base
  ↓
Top 5 Results → Formatted with metadata
  ↓
[Dive Deeper Options]
  ├─ get_chunk_context → Expand context ±30 lines
  └─ read_source_document → Full source file
```

---

## Data Entry Points

### 1. Sony Recorder Audio Files
- **Format**: .mp3 files (16kHz, mono, 64kbps)
- **Location**: `/Volumes/IC RECORDER/REC_FILE/FOLDER01`
- **Frequency**: Manual (user records voice notes throughout day)
- **Volume**: Typically 5-20 recordings per session

### 2. Git Commits
- **Format**: Git commit with message containing `[ROADMAP-X]` tags
- **Frequency**: Per development session (2-10 commits per day)
- **Trigger**: Automatic via post-commit hook

### 3. Claude Chat Tool Calls
- **Format**: MCP tool invocations from Claude Desktop app
- **Frequency**: Per chat session (5-20 tool calls per session)
- **Tools**: start_session, read_file, write_file, search_docs, etc.

### 4. Manual Script Invocations
- **Format**: Python script execution via terminal
- **Frequency**: Occasional (maintenance, debugging, backfills)
- **Examples**: `python scripts/recording_orchestrator.py`, `python scripts/end_session.py`

---

## Transformations

### 1. Audio → Text (Transcription)
- **Input**: .mp3 audio file
- **Process**: Groq Whisper API (whisper-large-v3)
- **Output**: Plain text transcript
- **Error Handling**: Retry with exponential backoff, fallback to local Whisper

### 2. Text → Structured Data (AI Analysis)
- **Input**: Text transcript
- **Process**: OpenAI GPT-4 with structured output
- **Output**: JSON with {title, category, project, tags, duration, icon, ...}
- **Error Handling**: Retry with backoff, fallback to "Manual Review Required"

### 3. Structured Data → Notion Entry (Database Insert)
- **Input**: JSON analysis result
- **Process**: Notion API pages.create() with property mapping
- **Output**: Notion page in 2nd Brain database
- **Error Handling**: Validation, retry, log to Failed/ folder

### 4. Markdown → Notion Blocks (Content Formatting)
- **Input**: Markdown content (headings, lists, code blocks)
- **Process**: Parse markdown → convert to Notion block objects
- **Output**: Array of Notion block objects
- **Limitations**: V1 supports headings, paragraphs, lists, code blocks (no tables/embeds)

### 5. Text → Embeddings (RAG Indexing)
- **Input**: Markdown chunks (500-2000 tokens)
- **Process**: OpenAI text-embedding-3-small API
- **Output**: 1536-dimensional vectors stored in ChromaDB
- **Batch Size**: 100 chunks per API call

### 6. Query → Search Results (RAG Search)
- **Input**: User query string
- **Process**: Hybrid search (BM25 + semantic) + reranking
- **Output**: Top 5 ranked chunks with metadata
- **Latency**: ~500ms (including reranking)

---

## Storage Locations

### 1. Local Filesystem (`ai-assistant/`)
- **transcripts/**: Raw transcript JSON files
- **processed/**: Processed transcript JSONs (with AI analysis)
- **Recording Archives/**: Archived audio files by date
- **staging/**: Temporary staging area for USB files
- **Failed/**: Failed processing attempts
- **.cache/**:
  - `recording_states.json` - Processing state machine
  - `projects.json` - Cached project data

### 2. Notion Databases
- **2nd Brain Database** (Primary):
  - Tasks (with duration, due date, project, tags)
  - Notes (with category, project, tags)
  - Properties: Title, Category, Project, Tags, Status, Due Date, Duration, Icon
- **Strategy Board Database**:
  - Initiatives with Status (🟡 Needs Decision, 🚀 In Progress, ✅ Complete, 🔴 Blocked)
  - Properties: Initiative Name, Status, Category, Priority Score, Project (relation)
- **Roadmap Database**:
  - Roadmap items linked to Strategy Board initiatives
  - Properties: Roadmap ID, Feature Name, Status, Priority, PRD Link, Tech Req Link
- **Sessions Database**:
  - Session logs from Claude Code and Claude Chat
  - Properties: Title, Session Date, Duration, Decisions Made, Next Steps, Critical Alerts, 🎯 Strategy Board (relation)
- **Projects Database**:
  - Active projects for classification
  - Properties: Name, Description, Keywords

### 3. ChromaDB Vector Store
- **Location**: `~/.cache/legacy-ai-rag/chroma`
- **Collection**: `legacy_ai_interviews`
- **Contents**: Embedded chunks from Legacy AI corpus
- **Size**: ~500-1000 chunks (varies with corpus)

### 4. BM25 Index
- **Location**: `~/.cache/legacy-ai-rag/bm25_index.pkl`
- **Format**: Pickled Python object
- **Contents**: Keyword index for BM25 search

### 5. Git Repository
- **Location**: `~/Documents/1. Projects/ai-assistant/`
- **Remote**: GitHub (dharan31chase/ai-assistant)
- **Branches**: main, feature/* (for PRs)

---

## Exit Points (Information Surfaces to User)

### 1. Notion Workspace
- **2nd Brain Database**: User reviews tasks/notes in Notion web/desktop app
- **Strategy Board**: User tracks initiatives and priorities
- **Roadmap**: User views implementation progress
- **Sessions**: User reviews session logs and decisions

### 2. Claude Chat (Web)
- **Context-loaded files**: User sees relevant docs loaded at session start
- **RAG search results**: User sees search results with dive-deeper options
- **Tool outputs**: User sees file contents, Notion data, etc.

### 3. Claude Code (Desktop)
- **Handoff prompts**: User copy-pastes handoff to start implementation
- **Tool outputs**: User sees file reads, git status, etc.

### 4. Git Commits
- **Session logs**: Committed to repo for version control
- **PRDs, tech requirements**: Committed as markdown files
- **Handoffs**: Committed to docs/handoffs/

### 5. Terminal Output
- **Recording orchestrator**: Progress updates, errors, summaries
- **End session script**: Confirmation of Notion updates
- **RAG indexer**: Indexing progress and statistics

---

## Integration Points

### External APIs

#### 1. OpenAI API
- **Used By**:
  - AI processor (task/note analysis)
  - Project detector (GPT-4 classification)
  - Tag detector (GPT-4 classification)
  - Embeddings module (text-embedding-3-small)
- **Models**:
  - `gpt-4o` (analysis, classification)
  - `text-embedding-3-small` (embeddings)
- **Rate Limits**:
  - GPT-4: 500 RPM (Tier 2)
  - Embeddings: 5000 RPM
- **Cost**:
  - GPT-4: $2.50/1M input tokens, $10/1M output tokens
  - Embeddings: $0.02/1M tokens

#### 2. Notion API
- **Used By**:
  - MCP server (query_strategy_board, update_initiative_status, write_to_page_content)
  - Notion uploader (create tasks/notes)
  - Sync to Notion script (update roadmap, create sessions)
- **Endpoints**:
  - `databases.query` (search databases)
  - `pages.create` (create entries)
  - `pages.update` (update properties)
  - `pages.retrieve` (fetch page data)
  - `blocks.children.append` (write page content)
- **Rate Limits**: 3 requests/second (burst up to 10)
- **Authentication**: Bearer token (NOTION_TOKEN in .env)

#### 3. Groq API
- **Used By**: Transcription engine
- **Model**: `whisper-large-v3`
- **Rate Limits**: 20 requests/minute (free tier)
- **Cost**: Free (currently)
- **Advantage**: 10x faster than OpenAI Whisper

#### 4. GitHub API (Implicit)
- **Used By**: Git push in post-commit hook
- **Authentication**: SSH key or HTTPS token
- **Usage**: Backup commits to remote

### External Services

#### 1. Claude Desktop (Anthropic)
- **Purpose**: Host Claude Chat with MCP servers
- **Config**: `~/.config/claude/claude_desktop_config.json`
- **MCP Servers**:
  - `ai-assistant-full` (main MCP server)
  - `legacy-ai-rag` (RAG MCP server)
- **Protocol**: Model Context Protocol (MCP) over stdio

#### 2. Sony IC Recorder
- **Model**: Sony ICD-PX470 (or similar)
- **Connection**: USB mount at `/Volumes/IC RECORDER`
- **Format**: .mp3 files (16kHz, mono, 64kbps)

### Local Tools

#### 1. Git
- **Used By**: Post-commit hook, manual commits
- **Version**: Git 2.x
- **Operations**: commit, push, log, diff-tree

#### 2. Python 3.x
- **Version**: 3.10+ (Apple Silicon native)
- **Virtual Env**: `ai-env/` (venv)
- **Key Packages**:
  - `notion-client` - Notion API
  - `openai` - OpenAI API
  - `groq` - Groq API
  - `fastmcp` - MCP server framework
  - `chromadb` - Vector database
  - `torch` - PyTorch (for reranker, MPS backend)
  - `transformers` - Hugging Face (for reranker)
  - `python-dotenv` - Environment variables
  - `pyyaml` - YAML parsing

#### 3. ChromaDB
- **Purpose**: Vector database for RAG
- **Storage**: `~/.cache/legacy-ai-rag/chroma`
- **Backend**: SQLite + HNSW index

#### 4. Apple Silicon MPS (Metal Performance Shaders)
- **Purpose**: GPU acceleration for reranker model
- **Device**: Apple M1/M2/M3 GPU
- **Framework**: PyTorch with MPS backend

---

## Friction Point Analysis

### Friction Point #1: MCP Context Loading Opacity

**What**: User unclear which files Claude Chat loads at session start

**Current Implementation**:
- **Phase 1 (Legacy)**: Loads ALL files from `context_folders` (10-16 docs)
  - Result: Noisy, includes irrelevant files
  - User has no visibility into what was loaded
- **Phase 2 (Intelligent - Nov 2025)**: Suggests 3-6 files based on workstream
  - Uses workstream config in `project-paths.json` OR generic heuristics
  - Shows user suggestions, user confirms/adjusts
  - Saves selection to `context-profiles.json` for next time
  - **Improvement**: User now sees suggested files before loading

**How It Works**:
1. User calls `start_session("Legacy AI", "synthesis")`
2. MCP server checks `context-profiles.json` for learned profile
3. If profile exists: Shows learned files (e.g., meta-analysis.md + last 3 interviews)
4. If no profile: Suggests files based on workstream config or heuristics
5. User confirms → MCP server loads files via `read_file` tool
6. User adjusts → Calls `save_context_profile` to save preference

**Remaining Friction**:
- No visibility into HOW files were selected (heuristics are opaque)
- No easy way to see what's loaded mid-session
- No UI to adjust context without re-running `start_session`

**Potential Improvements**:
- Add `list_loaded_context()` tool to show current files
- Add `reload_context(add=[...], remove=[...])` tool for mid-session adjustments
- Add `explain_suggestions()` tool to show WHY files were suggested
- Add telemetry to track which files are actually used (clicked, referenced)

---

### Friction Point #2: Session Start/End Mechanism

**What**: Session start/end requires manual tool calls, no auto-detection

**Current Implementation**:

**Session Start**:
- User manually calls `start_session("Project", "workstream")` in Claude Chat
- MCP server loads context, queries Notion, shows roadmap
- No auto-trigger when opening Claude Chat

**Session End**:
- **Claude Chat**: User manually calls `end_session(...)` with summary, duration, etc.
  - Creates session log in `docs/sessions/claude-chat/`
  - Updates Notion Sessions DB
  - Optionally creates handoff document
- **Claude Code**: NO automated end session
  - User manually runs `python scripts/end_session.py` with CLI args
  - OR user manually creates session log with Write tool
  - Inconsistent with Claude Chat experience

**How It Works**:
- `start_session` MCP tool in `mcp_server/full_server.py:195-392`
- `end_session` MCP tool in `mcp_server/full_server.py:399-637`
- `end_session.py` script in `scripts/end_session.py:1-303` (for Claude Code)

**Friction**:
- No session boundary detection (when did session start/end?)
- No auto-capture of session metadata (duration, decisions, next steps)
- Claude Code session end is manual CLI invocation (clunky)
- No centralized session state (each tool call is stateless)

**Potential Improvements**:
- Add MCP hook for "conversation start" event (if MCP protocol supports)
- Add `get_session_state()` tool to show current session metadata
- Add auto-timer to track session duration
- Create unified `end_session` command for both Claude Chat and Claude Code
- Add session context to MCP server (persist across tool calls)

---

### Friction Point #3: Notion Sync Delay & Transparency

**What**: Git commit → Notion sync happens in background, user has no visibility

**Current Implementation**:
1. User commits code with `[ROADMAP-X]` tags
2. Post-commit hook runs `scripts/sync_to_notion.py`
3. Script queries Notion, updates Roadmap + Sessions databases
4. Hook pushes to GitHub
5. **Total time**: 2-5 seconds (blocks commit completion)

**How It Works**:
- Post-commit hook: `.git/hooks/post-commit:1-48`
- Sync script: `scripts/sync_to_notion.py:1-450+`
- Workflow:
  - Extract commit metadata (lines 18-22 in hook)
  - Call Python script with `--commit-msg`, `--commit-hash`, etc. (lines 25-30)
  - Script parses `[ROADMAP-X]` tags (lines 74-88 in sync script)
  - Query Roadmap DB for matching items
  - Update Roadmap properties (status, last updated, commit link)
  - Create Sessions DB entry linked to Roadmap
  - Push to GitHub (lines 39-45 in hook)

**Friction**:
- No visibility: User doesn't see what was synced unless they check Notion
- Blocking: 2-5 second delay after commit (feels sluggish)
- Silent failures: If sync fails, only logged to stderr (user may miss)
- No retry: If Notion API fails, changes are lost (not queued)

**Potential Improvements**:
- **Async sync**: Move to background process, don't block commit
  - Use queue (e.g., Redis, SQLite) to persist sync tasks
  - Separate daemon process polls queue and syncs
- **Visibility**: Print summary after sync completes
  - "✓ Synced to Notion: ROADMAP-123 updated, Session created"
- **Retry logic**: Queue failed syncs for retry with exponential backoff
- **Status command**: `git notion-status` to see sync queue and last sync time

---

### Friction Point #4: Claude Chat ↔ Claude Code Handoff

**What**: No automated handoff between Claude Chat (planning) and Claude Code (implementation)

**Current Implementation**:
1. User works in Claude Chat to create PRD
2. User calls `end_session(create_handoff=True, ...)`
3. MCP server generates handoff document in `docs/handoffs/YYYY-MM-DD-to-claude-code-topic.md`
4. **User manually**:
   - Opens handoff file in editor
   - Copy-pastes content
   - Opens Claude Code
   - Pastes handoff as initial prompt
5. Claude Code starts implementation

**How It Works**:
- `end_session` with `create_handoff=True` parameter
- Calls `generate_handoff_template()` in `mcp_server/full_server.py:1224-1357`
- Template includes:
  - Git commands (checkout branch, commit)
  - Implementation mode (INTERACTIVE)
  - What to build
  - Documents to reference (PRD path, one-pager URL, Notion initiative ID)
  - Clarifying questions
- Written to `docs/handoffs/` with Write tool

**Friction**:
- Fully manual: User must copy-paste handoff
- Context loss: No way to "inject" handoff into Claude Code session via API
- Easy to forget: User may forget to check for handoff
- No bidirectional link: Claude Code can't easily respond back to Claude Chat

**Why This Friction Exists**:
- Claude Code CLI has no API for programmatic prompt injection
- MCP is one-way (tools expose functionality TO Claude, not FROM Claude)
- Anthropic intentionally keeps human in the loop for safety

**Potential Improvements**:
- **Handoff notifications**:
  - Create `.handoff-pending` file that Claude Code checks on startup
  - Claude Code prompts: "Found pending handoff from Claude Chat, load it?"
- **Shared context bridge**:
  - Use MCP to create shared "inbox" both Claude Chat and Claude Code can read/write
  - Claude Chat writes handoff to inbox, Claude Code reads from inbox
- **Clipboard automation** (MacOS):
  - Auto-copy handoff to clipboard when created
  - Show notification: "Handoff copied to clipboard, paste in Claude Code"
- **Web integration**:
  - Create simple web UI that both Claude Chat and Claude Code can access
  - Claude Chat writes handoff to web UI, Claude Code fetches from web UI

---

### Friction Point #5: RAG Implementation Location

**What**: User asked to document where RAG lives

**Current Implementation**:
- **Code Location**: `ai-assistant/scripts/rag/` (all RAG modules)
- **Corpus Location**: `legacy-ai/research/` (customer interview markdown files)
- **Index Location**: `~/.cache/legacy-ai-rag/` (ChromaDB + BM25 index)
- **MCP Server**: `scripts/rag/mcp_server.py` (separate from main MCP server)
- **Config**: `ai-assistant/config/rag_config.yaml`

**How It Works**:
1. **Indexing** (manual, one-time):
   - Run `python scripts/rag/indexer.py`
   - Scans `~/Documents/1. Projects/legacy-ai/research/**/*.md`
   - Chunks files with header-aware chunking (500-2000 tokens)
   - Generates embeddings via OpenAI API (text-embedding-3-small)
   - Stores in ChromaDB (`~/.cache/legacy-ai-rag/chroma`)
   - Builds BM25 index (`~/.cache/legacy-ai-rag/bm25_index.pkl`)

2. **Searching** (via MCP):
   - User calls `search_legacy_corpus("customer pain points", top_k=5)`
   - MCP server delegates to `scripts/rag/searcher.py`
   - Hybrid search: BM25 (30%) + Semantic (70%) → RRF merge
   - Rerank with `BAAI/bge-reranker-base` on Apple Silicon GPU
   - Return top 5 chunks with metadata

3. **Dive Deeper**:
   - `get_chunk_context(chunk_id, ±30 lines)` → Expand context
   - `read_source_document(file_path)` → Full source file

**Why This Setup**:
- RAG code lives in ai-assistant (infrastructure repo)
- RAG corpus lives in legacy-ai (domain repo)
- Separation of concerns: Infrastructure vs domain knowledge
- Allows RAG to index multiple projects in future

**Friction**:
- Not obvious where RAG lives (spans 2 repos)
- Manual indexing (no auto-update when corpus changes)
- MCP server runs separately from main MCP server (2 processes)

**Potential Improvements**:
- **Auto-indexing**: Watch legacy-ai repo for changes, re-index automatically
- **Unified MCP server**: Merge RAG tools into main MCP server (single process)
- **Multi-project RAG**: Extend to index ai-assistant docs as well
- **Incremental indexing**: Only re-embed changed files (delta updates)

---

## Observations

### Architecture Highlights

1. **Modular Orchestration**: Voice pipeline is well-factored into 8 separate modules (detection, staging, transcription, processing, etc.), each with single responsibility

2. **Configuration-Driven**: Heavy use of YAML configs (11 config files) makes system adaptable without code changes

3. **AI-Powered Intelligence**: 4 specialized AI routers provide smart classification, estimation, and enrichment

4. **Multi-Project Support**: MCP server handles both ai-assistant and legacy-ai projects with unified tools

5. **Hybrid RAG**: Combines BM25 (keyword) + semantic embeddings + neural reranking for best retrieval quality

6. **Learned Context**: Context profile system learns user preferences over time (reduces noise from 10-16 docs to 3-6)

### Design Patterns

1. **Facade Pattern**: `IntelligentRouter` delegates to 4 specialized routers (clean separation)

2. **Pipeline Pattern**: Voice processing flows through 8 sequential stages with state tracking

3. **Strategy Pattern**: Transcription backend (Groq vs local Whisper) and content formatter (basic vs smart)

4. **Lazy Loading**: Routers and heavy modules loaded on-demand to avoid circular imports

5. **Atomic Operations**: State updates use temp file + rename for crash safety

### Surprising Findings

1. **Two MCP Servers**: Main MCP server + separate RAG MCP server (2 processes, could be unified)

2. **Sequential Transcription**: Processes recordings one-by-one (could be parallelized with worker pool)

3. **No Auto-Indexing**: RAG requires manual re-indexing when corpus changes (could watch for changes)

4. **Blocking Git Hook**: Notion sync runs synchronously in post-commit (could be async queue)

5. **Manual Handoff**: Claude Chat → Claude Code handoff is fully manual copy-paste (no API available)

6. **Dual Session End**: Claude Chat has automated `end_session` tool, Claude Code requires manual CLI script

7. **Groq for Transcription**: Uses Groq instead of OpenAI Whisper (10x faster, free tier)

8. **Apple Silicon Optimization**: Reranker uses MPS backend for GPU acceleration (2-3x faster)

9. **Rich Context System**: File type classification (always, latest, exemplar, synthesis, optional) provides nuanced context selection

10. **Git-Notion Sync**: Bidirectional sync between git commits and Notion databases (unusual integration)

---

## Component Statistics

- **Total Python Files**: 50+
- **Total Lines of Code**: ~15,000+ (estimated)
- **Configuration Files**: 11 YAML/JSON configs
- **External APIs**: 4 (OpenAI, Notion, Groq, GitHub)
- **Notion Databases**: 5 (2nd Brain, Strategy Board, Roadmap, Sessions, Projects)
- **MCP Tools**: 12 (9 in main server + 3 in RAG server)
- **Git Hooks**: 1 (post-commit)
- **Storage Locations**: 5 (local filesystem, Notion, ChromaDB, BM25 index, git)

---

## Next Steps for Systems Thinking

This component inventory provides the foundation for Claude Chat to:

1. **Generate Mermaid Diagrams**:
   - System context diagram (external actors + system boundary)
   - Container diagram (subsystems + interactions)
   - Component diagram (modules within each subsystem)
   - Data flow diagrams (voice pipeline, git sync, RAG search)

2. **Identify Architectural Improvements**:
   - Friction point #1: MCP context loading transparency
   - Friction point #2: Session start/end automation
   - Friction point #3: Async Notion sync with queue
   - Friction point #4: Improved Claude Chat ↔ Code handoff
   - Friction point #5: Auto-indexing for RAG

3. **Design Intervention Points**:
   - Where to add observability (logging, metrics, dashboards)
   - Where to add resilience (retries, queues, fallbacks)
   - Where to add automation (watchers, triggers, schedulers)
   - Where to add user control (override flags, preferences, toggles)

4. **Map Information Architecture**:
   - How knowledge flows through the system
   - Where knowledge is captured, transformed, stored, retrieved
   - What gets lost in translation (friction points)
   - What could be made more explicit (implicit assumptions)

---

**End of Component Inventory**
