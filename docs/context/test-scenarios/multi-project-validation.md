# Test Scenario: Multi-Project Expansion Validation

**Purpose**: Validate end-to-end workflow for both Epic 2nd Brain and Legacy AI
**When**: Part 7 of Session 2B (after implementation complete)
**Duration**: 30-45 minutes
**Who**: You (Dharan) with Claude Code guidance

---

## 🎯 Test Suite Overview

**5 Test Scenarios:**
1. **Epic 2nd Brain Regression Test** (ensure we didn't break existing workflow)
2. **Legacy AI Context Loading Test** (new functionality works)
3. **Cross-Project Search Test** (can find info across projects)
4. **Git Hooks Sync Test** (commits go to right Notion view)
5. **Real Usage Simulation** (end-to-end customer discovery workflow)

---

## Test 1: Epic 2nd Brain Regression (Ensure Nothing Broke)

**Objective**: Verify existing workflow still works perfectly

### **1.1 Context Loading Test**

**Action**: Call start_session for Epic 2nd Brain
```python
result = await start_session("Epic 2nd Brain")
```

**Expected Result**:
- ✅ Loads in <10 seconds
- ✅ Returns context from ai-assistant/ repo
- ✅ Includes: Recent PRDs, tech requirements, session logs
- ✅ Strategy Board data (filtered to Epic 2nd Brain initiatives)

**Validation Questions**:
- [ ] Does it include "context-sync-bridge.md" PRD?
- [ ] Does it include recent session logs from docs/sessions/claude-chat/?
- [ ] Are Legacy AI docs EXCLUDED from context?

### **1.2 Search Test**

**Action**: Search for infrastructure-related term
```python
result = await search_docs("MCP server", project_name="Epic 2nd Brain")
```

**Expected Result**:
- ✅ Returns results ONLY from ai-assistant/ repo
- ✅ Results include tech requirements, PRDs mentioning MCP
- ✅ NO results from legacy-ai/ repo

### **1.3 Session Log Test**

**Action**: Create test session log
```python
result = await end_session(
    project_name="Epic 2nd Brain",
    summary="Test session - regression validation",
    decisions=["Validated multi-project expansion works"],
    next_steps=["Move to Legacy AI tests"]
)
```

**Expected Result**:
- ✅ Session log created at: `ai-assistant/docs/sessions/claude-chat/2025-11-XX-test.md`
- ✅ NOT created in legacy-ai/ repo

### **1.4 Git Hook Test**

**Action**: Make a commit in ai-assistant/ repo
```bash
cd ~/Documents/1.\ Projects/ai-assistant
echo "Test" >> docs/prd/multi-project-expansion.md
git add docs/prd/multi-project-expansion.md
git commit -m "Test: Git hook for Epic 2nd Brain"
```

**Expected Result**:
- ✅ Commit syncs to Notion
- ✅ Update appears in "Epic 2nd Brain Only" view (or "All Initiatives")
- ✅ Does NOT appear in "Legacy AI Only" view

**Manual Verification**:
- [ ] Open Notion Strategy Board → "Epic 2nd Brain Only" view
- [ ] Verify Multi-Project Expansion initiative shows recent activity
- [ ] Open "Legacy AI Only" view → Should NOT show this update

---

## Test 2: Legacy AI Context Loading (New Functionality)

**Objective**: Verify Legacy AI workflow works from scratch

### **2.1 Context Loading Test**

**Action**: Call start_session for Legacy AI
```python
result = await start_session("Legacy AI", "customer-discovery")
```

**Expected Result**:
- ✅ Loads in <10 seconds
- ✅ Returns context from legacy-ai/ repo
- ✅ Includes: requirements-vision.md, positioning.md, interview analyses
- ✅ Strategy Board data (filtered to Legacy AI initiatives)

**Validation Questions**:
- [ ] Does it include "requirements-vision.md"?
- [ ] Does it include at least 2 interview analyses?
- [ ] Are Epic 2nd Brain docs EXCLUDED from context?
- [ ] Does work_stream="customer-discovery" affect what's loaded?

### **2.2 Search Test**

**Action**: Search for business-related term
```python
result = await search_docs("customer pain points", project_name="Legacy AI")
```

**Expected Result**:
- ✅ Returns results ONLY from legacy-ai/ repo
- ✅ Results include interview analyses, requirements doc
- ✅ NO results from ai-assistant/ repo

### **2.3 Write File Test** (New Tool)

**Action**: Add entry to decision log
```python
result = await write_file(
    path="docs/decision-log.md",
    content="## 2025-11-XX - Test Decision\n\nThis is a test entry.",
    project="Legacy AI"
)
```

**Expected Result**:
- ✅ File updated at: `legacy-ai/docs/decision-log.md`
- ✅ Content appended correctly
- ✅ NOT written to ai-assistant/ repo

### **2.4 Session Log Test**

**Action**: Create test session log
```python
result = await end_session(
    project_name="Legacy AI",
    work_stream="customer-discovery",
    summary="Test session - validated new workflow",
    decisions=["Multi-project context loading works"],
    next_steps=["Ready for real interview analysis"]
)
```

**Expected Result**:
- ✅ Session log created at: `legacy-ai/sessions/customer-discovery/2025-11-XX-test.md`
- ✅ NOT created in ai-assistant/ repo

### **2.5 Git Hook Test**

**Action**: Make a commit in legacy-ai/ repo
```bash
cd ~/Documents/1.\ Projects/legacy-ai
echo "Test entry" >> docs/decision-log.md
git add docs/decision-log.md
git commit -m "Test: Git hook for Legacy AI"
```

**Expected Result**:
- ✅ Commit syncs to Notion
- ✅ Update appears in "Legacy AI Only" view (or "All Initiatives")
- ✅ Does NOT appear in "Epic 2nd Brain Only" view

**Manual Verification**:
- [ ] Open Notion Strategy Board → "Legacy AI Only" view
- [ ] Verify an initiative shows recent activity
- [ ] Open "Epic 2nd Brain Only" view → Should NOT show this update

---

## Test 3: Cross-Project Search (Find Info Anywhere)

**Objective**: Verify search can query across ALL projects when needed

### **3.1 Unfiltered Search Test**

**Action**: Search without project filter
```python
result = await search_docs("voice transcription")
```

**Expected Result**:
- ✅ Returns results from BOTH repos
- ✅ Results clearly indicate which project each result is from
- ✅ Epic 2nd Brain results: MCP server, voice-to-Notion pipeline
- ✅ Legacy AI results: Customer interview transcription notes

**Validation Question**:
- [ ] Can you tell which project each result belongs to?
- [ ] Are results ranked by relevance (not just by project)?

### **3.2 Cross-Project Pattern Detection**

**Action**: Search for concept that appears in both projects
```python
result = await search_docs("systems thinking")
```

**Expected Result**:
- ✅ Epic 2nd Brain: Systems Thinking Workbook, leverage points analysis
- ✅ Legacy AI: Strategic implications in interview analyses (if applicable)
- ✅ Shows how same concept applies across different contexts

---

## Test 4: Strategy Board Notion Views (Manual)

**Objective**: Verify Notion views show correct initiatives

### **4.1 View: "All Initiatives"**

**Manual Steps**:
1. Open Notion Strategy Board
2. Switch to "All Initiatives" view
3. Verify you see initiatives from BOTH projects

**Expected State**:
- [ ] Multi-Project Expansion (Epic 2nd Brain)
- [ ] Customer Interview Analysis (Legacy AI)
- [ ] Notion Command Center (Epic 2nd Brain)
- [ ] All visible in one unified view

### **4.2 View: "Epic 2nd Brain Only"**

**Manual Steps**:
1. Switch to "Epic 2nd Brain Only" view
2. Verify you see ONLY infrastructure initiatives

**Expected State**:
- [ ] Multi-Project Expansion
- [ ] Notion Command Center
- [ ] Context Sync Bridge-related initiatives
- [ ] NO Legacy AI initiatives visible

### **4.3 View: "Legacy AI Only"**

**Manual Steps**:
1. Switch to "Legacy AI Only" view
2. Verify you see ONLY business initiatives

**Expected State**:
- [ ] Customer Interview Analysis
- [ ] Uncle Bob Interview Design (if created)
- [ ] Prototype Validation Plan (if created)
- [ ] NO Epic 2nd Brain initiatives visible

### **4.4 Mobile Access Test**

**Manual Steps**:
1. Open Notion mobile app
2. Navigate to Strategy Board
3. Switch between views

**Expected State**:
- [ ] All 3 views are accessible on mobile
- [ ] Can filter to "Legacy AI Only" while on the go
- [ ] Can see initiative details and status

---

## Test 5: Real Usage Simulation (End-to-End)

**Objective**: Simulate actual customer discovery workflow

**Scenario**: You just completed an interview, want to analyze it

### **5.1 Session Start**

**Action**: Start Legacy AI customer discovery session
```
You: "Start session for Legacy AI, customer-discovery"
Claude: [Loads context]
```

**Validation**:
- [ ] Context loads in <10 seconds
- [ ] Claude knows: Requirements & Vision, Positioning, Past interviews
- [ ] Claude is ready to analyze new interview

### **5.2 Analysis Work**

**Action**: Analyze a sample interview (use one of the migrated analyses as reference)
```
You: "Help me analyze this interview. Key quote: 'I wish my grandkids cared about my stories.'"
Claude: [Uses Jobs-to-be-done framework, references positioning]
```

**Validation**:
- [ ] Claude references your positioning strategy
- [ ] Claude applies Jobs-to-be-done framework correctly
- [ ] Claude identifies pain points consistent with past analyses

### **5.3 Document Creation**

**Action**: Create new interview analysis doc
```python
result = await write_file(
    path="research/customer-interviews/analyses/2025-11-XX-test-interviewee.md",
    content="[Full interview analysis using template]",
    project="Legacy AI"
)
```

**Validation**:
- [ ] File created in correct location
- [ ] Follows Customer Interview Analysis template structure
- [ ] Git detects new file (ready to commit)

### **5.4 Commit & Sync**

**Action**: Commit the new analysis
```bash
cd ~/Documents/1.\ Projects/legacy-ai
git add research/customer-interviews/analyses/2025-11-XX-test-interviewee.md
git commit -m "Add interview analysis: Test Interviewee - Jobs-to-be-done insights"
git push origin main
```

**Validation**:
- [ ] Commit succeeds
- [ ] Push to GitHub succeeds
- [ ] Git hook triggers Notion sync
- [ ] Update appears in "Legacy AI Only" view (check within 5-10 seconds)

### **5.5 Session End**

**Action**: End session with summary
```python
result = await end_session(
    project_name="Legacy AI",
    work_stream="customer-discovery",
    summary="Analyzed test interview, validated Jobs-to-be-done framework",
    decisions=["Positioning resonates with elder storytellers"],
    next_steps=["Conduct Uncle Bob interview next week", "Refine template based on usage"]
)
```

**Validation**:
- [ ] Session log created in legacy-ai/sessions/customer-discovery/
- [ ] Contains summary, decisions, next steps
- [ ] Ready for review in Session 2C

### **5.6 Mobile Review**

**Action**: Check results on phone
1. Open Notion mobile app
2. Go to Strategy Board → "Legacy AI Only"
3. Find the initiative related to customer interviews

**Validation**:
- [ ] Can see that commit happened (timestamp updated)
- [ ] Can navigate to session log (if Notion sync implemented)
- [ ] Can review decisions and next steps on the go

---

## 📊 Test Results Summary

**After completing all 5 test scenarios**, fill out this scorecard:

### **Core Functionality** (Must Pass)

| Test | Status | Notes |
|------|--------|-------|
| Epic 2nd Brain context loading (<10s) | ⬜ Pass / ⬜ Fail | |
| Legacy AI context loading (<10s) | ⬜ Pass / ⬜ Fail | |
| Search filters by project correctly | ⬜ Pass / ⬜ Fail | |
| Git hooks sync to correct Notion views | ⬜ Pass / ⬜ Fail | |
| Session logs route to correct repo | ⬜ Pass / ⬜ Fail | |
| Write file creates in correct location | ⬜ Pass / ⬜ Fail | |

### **Notion Integration** (Must Pass)

| Test | Status | Notes |
|------|--------|-------|
| "All Initiatives" view shows both projects | ⬜ Pass / ⬜ Fail | |
| "Epic 2nd Brain Only" filters correctly | ⬜ Pass / ⬜ Fail | |
| "Legacy AI Only" filters correctly | ⬜ Pass / ⬜ Fail | |
| Mobile app access works | ⬜ Pass / ⬜ Fail | |

### **Performance** (Target)

| Metric | Target | Actual | Pass? |
|--------|--------|--------|-------|
| Epic 2nd Brain context load time | <10s | ___s | ⬜ |
| Legacy AI context load time | <10s | ___s | ⬜ |
| Cross-project search time | <5s | ___s | ⬜ |
| Git hook sync time | <10s | ___s | ⬜ |

### **Usability** (Subjective)

| Question | Answer |
|----------|--------|
| Does start_session prompt help when project not specified? | ⬜ Yes / ⬜ No |
| Are search results clearly labeled by project? | ⬜ Yes / ⬜ No |
| Is Notion view switching intuitive on mobile? | ⬜ Yes / ⬜ No |
| Overall: Does the workflow feel natural? | ⬜ Yes / ⬜ No |

---

## 🚨 If Any Tests Fail

**Don't Panic** - This is expected in Session 2B. Debugging is part of the process.

### **Common Issues & Solutions**

**Issue: Context loading >10 seconds**
- **Likely Cause**: Loading too many files
- **Fix**: Limit to most recent N files (e.g., last 10 PRDs, last 20 session logs)

**Issue: Search returns wrong project results**
- **Likely Cause**: Project filter not applied correctly
- **Fix**: Check PROJECT_CONFIG paths in MCP server

**Issue: Git hooks not syncing to Notion**
- **Likely Cause**: Hook not executable or wrong project detection
- **Fix**: `chmod +x .git/hooks/post-commit`, check sync_to_notion.py --project flag

**Issue: Session logs go to wrong repo**
- **Likely Cause**: Project detection in end_session() incorrect
- **Fix**: Verify project_name parameter is passed correctly

**Issue: Write file creates in wrong location**
- **Likely Cause**: PROJECT_CONFIG paths incorrect
- **Fix**: Double-check repo_path settings

---

## ✅ Sign-Off Checklist

Before declaring Session 2B complete:

- [ ] All 6 "Core Functionality" tests passed
- [ ] All 4 "Notion Integration" tests passed
- [ ] All 4 "Performance" metrics under target
- [ ] All "Usability" questions answered "Yes"
- [ ] Test 5 (Real Usage Simulation) completed successfully
- [ ] Session 2B session log created by Claude Code
- [ ] Ready for Session 2C review with Claude Chat

---

**If all tests pass: Session 2B is COMPLETE! 🎉**

**Next**: Return to Claude Chat for Session 2C review, then prepare for Session 3 (real Uncle Bob interview analysis).
