# PRD: Context Profile Optimization - Intelligent Context Loading

**Status**: In Progress
**Priority**: High
**Estimated Effort**: 6-7 hours (Phase 1)
**Owner**: Dharan Chandra Hasan
**Created**: 2025-11-13
**Last Updated**: 2025-11-17
**Parent Initiative**: [Context Profile Optimization](https://www.notion.so/Context-Profile-Optimization-2aa8369c73058053a3cdd97a3d0b4823)
**Notion Strategy Board**: [Epic 2nd Brain - Strategy Board](https://www.notion.so/)
**Tech Requirements**: [context-profile-optimization.md](../tech-requirements/context-profile-optimization.md) ✅

---

## 📋 Implementation Readiness Checklist

**Pre-Implementation** (Before Claude Code starts):
- [x] Tech requirements document created (2025-11-17)
- [x] Architecture decisions approved (Phase 1 quick impl, Phase 2 modular refactor)
- [x] Success criteria defined (<5s suggestion, >80% signal-to-noise)
- [x] Dependencies identified (None)
- [x] Added to roadmap (Phase 5D refactoring task)

**Implementation** (Claude Code updates during work):
- [x] Config files created (project-paths.json, file-type-patterns.json, context-profiles.json) - 2025-11-17
- [x] Core functions implemented (file discovery, profile management) - 2025-11-17
- [x] Integration points complete (MCP tool registration) - 2025-11-17
- [x] Unit tests written (parse_user_selection, classify_file_type, find_project) - 2025-11-17
- [ ] Integration tests written (first-time suggestion, learned profile loading) - Deferred to real usage validation

**Post-Implementation** (Before marking Complete):
- [ ] All tests passing
- [ ] Documentation updated (README, MCP server docs)
- [ ] Code reviewed (self-review for docstrings, edge cases)
- [ ] Ready for production use (validated with real Legacy AI workflow)

---

## 🎯 TL;DR

Build a **learning context system** that collaboratively suggests 3-6 targeted files based on work stream, learns from your selections, and auto-applies learned profiles in future sessions - reducing context loading from 10-16 random docs to 3-6 high-signal docs while improving relevance from 30-40% to 80-90%.

**Key Innovation**: System gets smarter with use. First time = you teach it. Every time after = it remembers.

**Time Investment**: 5-6 hours implementation  
**ROI**: 10-15 min saved × 50 sessions/10 weeks = **8-12 hours saved before baby arrives**

---

## 🎯 Problem Statement

**User Pain Point**: I know what I want to load, but the system auto-loads everything blindly.

**Current Broken Flow:**
```
You: start_session("Legacy AI", "customer-discovery")
System: *auto-loads ALL docs*
  - requirements-vision.md ✅ (needed)
  - meta-interview-analysis.md ✅ (needed)
  - All 5 interview analyses ❌ (only need last 3)
  - All interview transcripts ❌ (don't need any)
  - technical-feasibility.md ❌ (not relevant today)
  
Result: 10 docs loaded, only 3-4 are relevant
Signal-to-noise: ~30-40%
```

**What You Actually Want:**
```
You: "Legacy AI, interview analysis"
System: "For interview analysis, I recommend:
  1. interview-guides/sarah-cronin.md (latest)
  2. interview-guides/missy-bob-exemplar.md (exemplar)
  3. insights/segment-comparison-meta-analysis.md
  
  Always available:
  4. requirements-vision.md
  5. product-strategy.md
  
  Which should I load? (1,2,3,4)"

You: "1,2,3,4"
System: *loads only those 4 files*
System: "Next time, I'll suggest these by default."
```

**The Structural Issue:**

You're the one who knows what context is relevant for a given task. The system should:
1. **Suggest intelligently** based on project structure and past usage
2. **Let you decide** what to actually load
3. **Learn from your choices** and improve over time
4. **Apply learned profiles** automatically in future sessions

Currently, the system makes all decisions upfront (static profiles) or loads everything (current behavior). Neither respects your agency or learns from your patterns.

**Why Now:**

1. **Tomorrow's interviews**: Testing new workflow on 2 customer profiles
2. **25+ interviews coming**: Every saved minute compounds
3. **Baby deadline (10 weeks)**: Need efficient context loading before time availability drops
4. **Meta-Interview Analysis ready**: Source of truth doc exists (Session 3)
5. **Learning foundation**: This pattern applies to ALL future work streams

---

## 🔧 High-Level Approach

**Strategy**: Collaborative Learning System - You teach it once, it remembers forever.

### The Three-Phase Flow

**Phase 1: First Time (Discovery)**
```
You declare work stream → System suggests files → You approve/edit → System loads + remembers
```

**Phase 2: Learned Profile (Efficiency)**  
```
You declare work stream → System shows learned profile → You confirm/adjust → System loads
```

**Phase 3: Continuous Improvement (Adaptation)**
```
Profile evolves with your workflow → Add new files → Remove outdated ones → System adapts
```

### How File Suggestion Works

**1. Project Structure Scanning:**
```python
# System scans known folders for each project
Legacy AI:
  - interview-guides/  (latest + exemplars)
  - insights/          (meta-analysis, validation questions)
  - research/          (requirements, strategy)
  
Epic 2nd Brain:
  - prd/              (latest PRD)
  - architecture/     (system design)
  - sessions/         (recent logs)
```

**2. "Latest" Auto-Detection:**
- Sort files by modification date
- Flag most recent as "latest"
- Confirm with user: "sarah-cronin.md modified Nov 16 is latest. Correct?"

**3. Context Relevance Ranking:**
- **Always**: Core docs that never change (requirements, vision)
- **Latest**: Most recent work (latest interview guide)
- **Exemplar**: Reference material (missy-bob-exemplar.md)
- **Insights**: Synthesis docs (meta-analysis, validation questions)

**4. Learning from Selection:**
```json
// After you approve files 1,2,3,4
// Stored in: docs/config/context-profiles.json

{
  "Legacy AI": {
    "interview-analysis": {
      "created": "2025-11-17",
      "last_used": "2025-11-17", 
      "usage_count": 1,
      "files": [
        "interview-guides/sarah-cronin.md",
        "interview-guides/missy-bob-exemplar.md", 
        "insights/segment-comparison-meta-analysis.md",
        "requirements-vision.md"
      ],
      "always_suggest": [
        "product-strategy.md"
      ]
    }
  }
}
```

### Why This Approach

**✅ Respects Your Agency**: You decide what to load, system just suggests
**✅ Gets Smarter**: Each session improves future sessions  
**✅ Adapts to Change**: Add product-strategy.md when it exists, system remembers
**✅ Zero Configuration**: No upfront profile design needed
**✅ Auditable**: Learned profiles are in Git, you can review/edit manually
**✅ Scalable**: Works for ANY project + work stream combination

**Alternatives Considered:**

**Alternative A: Static Profiles (Previous PRD)**
- Why not: Requires upfront design, doesn't adapt to workflow changes, you know better than pre-defined rules
- When: Good for 100% predictable workflows (rare)

**Alternative B: AI-Predicted Context**  
- Why not: Black box decisions, not trustworthy, over-engineered for current need
- When: After 50+ sessions with learned profiles, train ML on usage patterns (Tier 1)

**Alternative C: Load Everything (Current Behavior)**
- Why not: Wastes tokens, slow loading, poor signal-to-noise ratio
- When: Never (this is what we're fixing)

---

## ✅ Success Criteria

**Must Have** (Launch blockers):

1. **First-time file suggestion <5 seconds**
   - Measurement: Time from work stream declaration to showing file list
   - Baseline: N/A (new feature)
   - Target: <5 seconds (scan + rank + display)

2. **Profile learning works on first approval**
   - Measurement: After approving files, check context-profiles.json
   - Baseline: N/A (new feature)  
   - Target: 100% - selected files persisted correctly

3. **Second-time loading uses learned profile**
   - Measurement: Next session with same work stream shows learned files
   - Baseline: N/A (new feature)
   - Target: 100% - learned profile displayed and loadable

4. **Signal-to-noise ratio >80%** (from current 30-40%)
   - Measurement: % of loaded docs that Claude references in response
   - Baseline: 30-40% (reference 3-5 docs out of 10-16 loaded)  
   - Target: >80% (reference 4-5 docs out of 5-6 loaded)

5. **Context loading time <3 seconds** (from current 5s)
   - Measurement: Time from approval to context ready
   - Baseline: 5s (10-16 docs)
   - Target: <3s (3-6 docs)

**Nice to Have** (Post-launch):

1. **Profile analytics** - show usage frequency, last used, etc.
2. **Profile export/import** - share profiles across machines
3. **Semantic search** - find files by content similarity (Tier 1)
4. **Auto-update "latest"** - when new interview guide added, suggest updating profile

---

## 🚫 Non-Goals

1. **AI-powered file selection** (Tier 1 - Week 3-4)
   - Why: Learning from explicit choices is sufficient, AI prediction is premature
   - When: After 50+ sessions with learned profiles

2. **Notion-based profile storage** (Tier 1)
   - Why: Git version control is sufficient, Notion adds complexity
   - When: If mobile editing becomes important

3. **Real-time profile updates during session** (Tier 2)
   - Why: Start-of-session learning is sufficient
   - When: If sessions become multi-hour and context needs change

4. **Cross-project context mixing** (Tier 1)  
   - Why: Clean separation is valuable (IP hygiene)
   - When: If you discover patterns that span projects

5. **Automatic profile merging** (Tier 2)
   - Why: Manual override is fine for now
   - When: If you have 10+ profiles per project and management becomes burden

---

## 👥 User Stories

### Story 1: First-Time Interview Analysis (Discovery Mode)

**As Dharan** (preparing for customer interview),  
**I want** the system to suggest relevant files based on project structure,  
**So that** I can quickly approve the right context without manually searching.

**Acceptance Criteria**:
- [ ] I say: "Legacy AI, interview analysis"
- [ ] System scans interview-guides/ and insights/ folders
- [ ] System suggests:
  - Latest interview guide (auto-detected by date)
  - Exemplar guide (marked in filename or specified)
  - Segment comparison meta-analysis
  - Always-available: requirements-vision.md, product-strategy.md
- [ ] Files are numbered (1, 2, 3, 4, 5)
- [ ] I respond with numbers: "1,2,3,4"
- [ ] System loads only those 4 files
- [ ] System saves my selection to context-profiles.json
- [ ] Confirmation: "Next time you do interview analysis, I'll suggest 1,2,3,4 by default"

---

### Story 2: Repeat Interview Analysis (Learned Profile)

**As Dharan** (doing another interview analysis),  
**I want** the system to show my previous selection by default,  
**So that** I can quickly confirm or adjust without re-selecting everything.

**Acceptance Criteria**:
- [ ] I say: "Legacy AI, interview analysis"  
- [ ] System loads learned profile from context-profiles.json
- [ ] System displays: "Loading your interview analysis profile:
  - 1. interview-guides/sarah-cronin.md (latest)
  - 2. interview-guides/missy-bob-exemplar.md  
  - 3. insights/segment-comparison-meta-analysis.md
  - 4. requirements-vision.md
  
  Add/remove files? (Enter numbers or press Enter to load)"
- [ ] I press Enter (or say "5" to add product-strategy.md)
- [ ] System loads confirmed files
- [ ] If I added/removed files, system updates profile

---

### Story 3: Profile Evolution (Adaptation)

**As Dharan** (workflow changes over time),  
**I want** to add/remove files from learned profiles,  
**So that** the system adapts as my work evolves.

**Acceptance Criteria**:
- [ ] I start session with learned profile
- [ ] System shows numbered list of current profile files
- [ ] I can:
  - Add new file: "Also load 5" (product-strategy.md)
  - Remove file: "Skip 2" (don't load exemplar today)
  - Replace file: "Use interview-guides/new-latest.md instead of 1"
- [ ] System updates context-profiles.json with changes
- [ ] Next session reflects updated profile

---

### Story 4: Manual Profile Inspection (Auditability)

**As Dharan** (reviewing learned behaviors),  
**I want** to see and edit context-profiles.json manually,  
**So that** I can understand what the system learned and fix mistakes.

**Acceptance Criteria**:
- [ ] context-profiles.json is human-readable JSON
- [ ] Stored in docs/config/ (version controlled)
- [ ] Contains:
  - Project name
  - Work stream name  
  - Creation date, last used date, usage count
  - List of file paths
  - List of always-suggest files
- [ ] I can manually edit this file and system respects changes
- [ ] If file doesn't exist, system warns me and suggests alternatives

---

### Story 5: "Latest" Auto-Detection (Smart Defaults)

**As Dharan** (working with evolving content),  
**I want** the system to auto-detect the latest interview guide,  
**So that** I don't have to manually update profiles when new guides are created.

**Acceptance Criteria**:
- [ ] System scans interview-guides/ folder
- [ ] Sorts files by modification date (most recent first)
- [ ] Flags most recent as "latest"  
- [ ] Confirms with me: "sarah-cronin.md (modified Nov 16) is latest. Correct?"
- [ ] If I say "no", asks: "Which file is the latest?"
- [ ] Remembers my correction for next time
- [ ] When new interview guide is created, suggests updating profile

---

## 🎨 Design Notes

### **Learned Profile Structure**

```json
// docs/config/context-profiles.json

{
  "Legacy AI": {
    "interview-analysis": {
      "created": "2025-11-17T10:30:00Z",
      "last_used": "2025-11-17T14:45:00Z",
      "usage_count": 3,
      "files": [
        {
          "path": "interview-guides/sarah-cronin.md",
          "type": "latest",
          "added": "2025-11-17T10:30:00Z"
        },
        {
          "path": "interview-guides/missy-bob-exemplar.md",
          "type": "exemplar",
          "added": "2025-11-17T10:30:00Z"
        },
        {
          "path": "insights/segment-comparison-meta-analysis.md",
          "type": "synthesis",
          "added": "2025-11-17T10:30:00Z"
        },
        {
          "path": "requirements-vision.md",
          "type": "always",
          "added": "2025-11-17T10:30:00Z"
        }
      ],
      "always_suggest": [
        "product-strategy.md",
        "technical-feasibility/summary.md"
      ]
    },
    
    "interview-synthesis": {
      "created": "2025-11-20T09:00:00Z",
      "last_used": "2025-11-20T11:30:00Z", 
      "usage_count": 1,
      "files": [
        {
          "path": "requirements-vision.md",
          "type": "always",
          "added": "2025-11-20T09:00:00Z"
        },
        {
          "path": "insights/segment-comparison-meta-analysis.md",
          "type": "synthesis",
          "added": "2025-11-20T09:00:00Z"
        }
      ],
      "always_suggest": []
    }
  },
  
  "Epic 2nd Brain": {
    "infrastructure": {
      "created": "2025-11-15T08:00:00Z",
      "last_used": "2025-11-17T07:30:00Z",
      "usage_count": 12,
      "files": [
        {
          "path": "roadmap.md",
          "type": "always",
          "added": "2025-11-15T08:00:00Z"
        },
        {
          "path": "Systems_Thinking_Workbook.md",
          "type": "always", 
          "added": "2025-11-15T08:00:00Z"
        },
        {
          "path": "prd/context-profile-optimization.md",
          "type": "latest",
          "added": "2025-11-17T07:30:00Z"
        }
      ],
      "always_suggest": [
        "architecture/context-sync-bridge.mermaid.md"
      ]
    }
  }
}
```

### **File Type Classification**

**always**: Core docs that never change (requirements, vision, roadmap)  
**latest**: Most recent work (auto-detected by modification date)  
**exemplar**: Reference material (marked in filename or specified by user)  
**synthesis**: Meta-analysis, validation questions, summaries  
**optional**: User can add, but not suggested by default

### **File Discovery Logic**

```python
# Pseudo-code for first-time suggestion

def suggest_files_for_workstream(project, workstream):
    # 1. Scan known folders
    folders = get_folders_for_project(project)
    
    # 2. Find "latest" files (by modification date)
    latest_files = []
    for folder in folders:
        files = sorted(os.listdir(folder), key=os.path.getmtime, reverse=True)
        latest_files.append(files[0])  # Most recent
    
    # 3. Find "always" files (core docs)
    always_files = [
        "requirements-vision.md",
        "roadmap.md", 
        "Systems_Thinking_Workbook.md"
    ]
    
    # 4. Find "exemplar" files (contains "exemplar" in filename)
    exemplar_files = [f for f in all_files if "exemplar" in f.lower()]
    
    # 5. Find "synthesis" files (meta-analysis, validation, etc.)
    synthesis_files = [
        "meta-interview-analysis.md",
        "segment-comparison-meta-analysis.md",
        "validation-questions-library.md"
    ]
    
    # 6. Rank and present
    suggestions = {
        "recommended": latest_files + exemplar_files + synthesis_files,
        "always_available": always_files
    }
    
    return suggestions
```

### **User Interaction Flow**

```python
# start_session API with learning

def start_session(project, workstream, debug=False):
    # 1. Check if learned profile exists
    profile = load_profile(project, workstream)
    
    if profile:
        # 2a. Learned profile exists - show and confirm
        print(f"Loading your {workstream} profile:")
        for i, file in enumerate(profile["files"], start=1):
            print(f"  {i}. {file['path']} ({file['type']})")
        
        response = input("\nAdd/remove files? (Enter numbers or press Enter to load): ")
        
        if response:
            # User wants to modify
            files_to_load = parse_user_selection(response, profile["files"])
            update_profile(project, workstream, files_to_load)
        else:
            # User confirmed, use profile as-is
            files_to_load = [f["path"] for f in profile["files"]]
    
    else:
        # 2b. First time - suggest files
        suggestions = suggest_files_for_workstream(project, workstream)
        
        print(f"For {workstream}, I recommend:")
        for i, file in enumerate(suggestions["recommended"], start=1):
            print(f"  {i}. {file}")
        
        print(f"\nAlways available:")
        for i, file in enumerate(suggestions["always_available"], 
                                 start=len(suggestions["recommended"])+1):
            print(f"  {i}. {file}")
        
        response = input("\nWhich should I load? (Enter numbers): ")
        files_to_load = parse_user_selection(response, suggestions)
        
        # 3. Save learned profile
        save_profile(project, workstream, files_to_load)
        print(f"\n✓ Next time, I'll suggest {len(files_to_load)} files by default.")
    
    # 4. Load approved files
    context = load_files(files_to_load)
    
    if debug:
        print(f"\nLoaded {len(files_to_load)} files ({count_tokens(context)} tokens)")
    
    return context
```

### **API Changes**

**Before:**
```python
start_session(project_name, work_stream=None)
```

**After:**
```python
start_session(
    project_name: str,
    work_stream: str,           # Required now (no default)
    debug: bool = False,        # Show what was loaded
    force_suggest: bool = False # Ignore learned profile, suggest fresh
)
```

**New Helper Functions:**
```python
# View all learned profiles
list_profiles(project_name=None)

# Edit profile manually
edit_profile(project_name, work_stream)

# Delete profile (start fresh)
delete_profile(project_name, work_stream)

# Export/import profiles
export_profiles(output_path)
import_profiles(input_path)
```

---

## ❓ Open Issues & Key Decisions

### Key Decisions Made

**1. Learning from Explicit Selection (Not AI Prediction)** (Nov 17, 2025):
- **Why**: You know what you need better than any AI. System should suggest, you decide, system learns.
- **Trade-offs**: Less "magical" than AI prediction, requires user input first time
- **Impact**: 100% control, auditable, trustworthy, adapts to your workflow
- **Door Type**: Two-way (can add AI prediction in Tier 1 after 50+ sessions)

**2. Profile Storage in Git (Not Notion)** (Nov 17, 2025):
- **Why**: Version controlled, auditable, survives laptop death, easy to edit manually
- **Trade-offs**: Not accessible from mobile (but you do context loading on Mac)
- **Impact**: Can review profile history, rollback if needed, share across machines
- **Door Type**: Two-way (can add Notion sync in Tier 1 if mobile becomes important)

**3. Auto-Detect "Latest" by Modification Date** (Nov 17, 2025):
- **Why**: Easy to implement (os.path.getmtime), accurate enough, user can override
- **Trade-offs**: Might flag wrong file if you edit old guide (but rare)
- **Impact**: Zero manual maintenance, system stays current automatically
- **Door Type**: Two-way (can add explicit latest marker if needed)

**4. File Discovery by Folder Scanning (Not Semantic Search)** (Nov 17, 2025):
- **Why**: Project structure is known, folder names are meaningful, fast and simple
- **Trade-offs**: Won't find files outside known folders (but can add manually)
- **Impact**: <5 second suggestion time, no external dependencies
- **Door Type**: Two-way (can add semantic search in Tier 1 for discovery)

**5. Numbered File Selection (Not Checkboxes)** (Nov 17, 2025):
- **Why**: Terminal-friendly, fast to type "1,2,3,4", works with voice input
- **Trade-offs**: Less visual than GUI checkboxes (but you prefer speed)
- **Impact**: Zero friction, works in Claude Code terminal
- **Door Type**: Two-way (can add GUI in Tier 1 if needed)

---

## 🔗 Links

- **Tech Requirements**: [To be created by Claude Code]
- **Notion Initiative**: [Context Profile Optimization](https://www.notion.so/Context-Profile-Optimization-2aa8369c73058053a3cdd97a3d0b4823)
- **Parent PRD**: [Context Sync Bridge](context-sync-bridge.md)
- **Related**: [Multi-Project Expansion](multi-project-expansion.md)

---

## 📅 Timeline & Status

**Current Status**: Approved (ready for implementation)  
**Implementation Session**: Week 1 (Nov 17-18, 2025)  
**Estimated Implementation**: 5-6 hours (Claude Code)  
**Target Completion**: Nov 18, 2025  
**First Test**: Nov 18, 2025 (2 customer interview scripts)

**Implementation Phases:**

**Phase 1: Core Infrastructure (2 hours)**
- File discovery logic (scan folders, detect latest)
- Profile storage (load/save context-profiles.json)
- Numbered file selection parser

**Phase 2: Learning System (1.5 hours)**
- First-time suggestion flow
- Profile persistence after approval
- Profile loading on repeat session

**Phase 3: User Interaction (1 hour)**
- Numbered list display
- User input parsing ("1,2,3,4" → file list)
- Add/remove file modification

**Phase 4: Integration (30 min)**
- Update start_session() to use learning system
- Backward compatibility (if no work_stream, prompt for it)
- Debug mode output

**Phase 5: Testing (30 min)**
- Test first-time suggestion (Legacy AI interview-analysis)
- Test profile learning and persistence
- Test repeat session with learned profile
- Test profile modification (add/remove files)

**Phase 6: Tomorrow's Validation (User Testing)**
- Create 2 interview scripts using new workflow
- Measure time vs old workflow
- Validate relevance of suggested context

**Dependencies:**
- None (standalone feature)

---

## 🎓 Systems Thinking Applied

**Leverage Point #6: Information Flows** (High Impact)

**Before (Broken Flow):**
```
System decides what to load → User gets irrelevant context → Wastes time filtering
```

**After (Optimized Flow):**
```
System suggests files → User approves → System loads → System learns → Future sessions get better
```

**The Learning Feedback Loop:**

**R1: Context Quality Reinforcement** (Virtuous Cycle)
```
Better suggestions → More relevant context → Better responses → User approves
     ↑                                                                ↓
     ←───── System learns from approval ←──── Profile stored ←──────┘
```

**This compounds**: Each session improves suggestions for future sessions. After 10 sessions, system knows exactly what you need for each work stream.

**B1: Profile Accuracy Balancing** (Self-Correction)
```
Profile drift → User modifies files → System updates profile → Accurate again
```

System self-corrects when your workflow changes. No manual profile maintenance needed.

---

## 🎯 Alignment with Personal Context

**Your Baby Deadline (10 weeks):**
- 8-12 hours saved through efficient context loading
- Learning system adapts as your work evolves (baby arrives → different work patterns)
- Zero maintenance overhead (system manages itself)

**Your 100,000X Philosophy:**
- **Amplifies, not replaces**: You decide what to load, system just suggests and remembers
- **Structural leverage**: Learning compounds over career (every project benefits)
- **Contemplative technology**: Intentional context selection preserves agency

**Your Customer Discovery Phase:**
- 25+ interviews coming
- Each interview: 10-15 min saved in prep = **4-6 hours total saved**
- Meta-analysis as source of truth = high-signal context
- Tomorrow's test: Validate time savings immediately

**Your Systems Thinking Approach:**
- Information flow optimization (Leverage Point #6)
- Feedback loop creates virtuous cycle (system gets smarter)
- Self-organizing system (adapts without manual intervention)
- Respects your agency (you're in control, not the AI)

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|----------|
| 2025-11-13 | Claude (Sonnet 4.5) | Initial draft - static profile approach |
| 2025-11-17 | Claude (Sonnet 4.5) | **Major revision** - switched to learning profile system based on Dharan's collaborative workflow requirements. Key changes: removed static profiles, added file suggestion + approval flow, profile learning and persistence, auto-detect latest files, numbered selection UI |

---

**End of PRD**
