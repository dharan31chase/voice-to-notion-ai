# Session 2B Quick Start: What to Tell Claude Code

**When**: Ready to implement (today or tomorrow)
**Where**: Claude Code (not here)
**Duration**: 6-8 hours
**Input**: This checklist + handoff document

---

## 🎯 Opening Statement for Claude Code

```
Hi Claude Code, I'm ready to implement Multi-Project Expansion.

Context:
- I have a handoff document from Claude Chat (Session 2A)
- Path: docs/context/handoffs/2025-11-11-multi-project-expansion-session-2b.md
- Please read it and confirm you understand the mission

My role in this session:
- I'll provide documents when you need them (5 docs to migrate)
- I'll make decisions when you present architectural options
- Otherwise, you drive the implementation

Let's start with Part 1: Creating the legacy-ai repo structure.
```

---

## 📋 Documents You Need to Have Ready

**Before starting Session 2B**, gather these from Notion:

### **1. Customer Interview Analysis Template**
- Location: Notion → Legacy AI project → Templates
- Format: Export as Markdown or copy-paste text
- What Claude Code needs: The full template structure with all sections

### **2. Requirements & Vision Doc**
- Location: Notion → Legacy AI project
- What: Your strategic overview of Legacy AI vision
- Export as Markdown

### **3. Positioning Strategy Doc**
- Location: Notion → Legacy AI project
- What: "Family legacy voice capture that connects generations" positioning
- Export as Markdown

### **4. Best Customer Interview Analysis** (Example)
- Location: Notion → Legacy AI → Customer Interviews
- What: Your best-structured interview analysis so far
- Purpose: Validates template works in practice
- Export as Markdown

### **5. Most Recent Interview Analysis**
- Location: Notion → Legacy AI → Customer Interviews
- What: Latest interview (shows current thinking)
- Export as Markdown

### **6. Technical Feasibility Summary**
- Location: Notion → Legacy AI → Technical Analysis
- What: Your feasibility assessment (AI voice, transcription, etc.)
- Export as Markdown

---

## 🔄 Interactive Checkpoints

Claude Code will pause at these points and need your input:

### **Checkpoint 1: GitHub Organization Setup**
**When**: After creating local repo structure
**Decision**: Confirm you created "Legacy Tech" organization on GitHub
**Action**: Share the organization URL with Claude Code

### **Checkpoint 2: Document Review**
**When**: After migrating 5 documents
**Decision**: Review converted markdown, confirm accuracy
**Action**: "Looks good" or "Change X in document Y"

### **Checkpoint 3: Template Validation**
**When**: After porting Customer Interview Analysis template
**Decision**: Does the markdown template preserve your framework structure?
**Action**: "Approve" or "Add section for X"

### **Checkpoint 4: MCP Tools Testing**
**When**: After updating start_session() and search_docs()
**Decision**: Test that both projects still work
**Action**: Try: `start_session("Epic 2nd Brain")` and `start_session("Legacy AI")`

### **Checkpoint 5: Notion Views Setup**
**When**: After creating filtered views
**Decision**: Confirm you can see separate views in Strategy Board
**Action**: Open Notion, verify "Legacy AI Only" and "Epic 2nd Brain Only" views exist

---

## ✅ Session 2B Success Checklist

By end of session, you should have:

- [ ] `~/Documents/1. Projects/legacy-ai/` folder exists with full structure
- [ ] GitHub "Legacy Tech" organization created
- [ ] `legacy-ai` repo is private, pushed to GitHub
- [ ] README.md explains project (you or Peter can read it and understand)
- [ ] 5 documents migrated to correct folders
- [ ] Customer Interview Analysis template in `docs/templates/`
- [ ] MCP tools updated (can call `start_session("Legacy AI")`)
- [ ] Git hooks set up (commits sync to correct Notion view)
- [ ] Strategy Board has 3 views (All, Epic 2nd Brain Only, Legacy AI Only)
- [ ] Test passed: Context loads in <10 seconds for both projects
- [ ] Session log created by Claude Code documenting what shipped

---

## 🚨 If Something Goes Wrong

**Problem: Can't create GitHub organization**
- **Solution**: Use personal account for now, tell Claude Code to use that
- **Impact**: Two-way door, can transfer later

**Problem: Documents are too complex to migrate quickly**
- **Solution**: Migrate just 2-3 docs, defer rest to later
- **Impact**: Still proves system works

**Problem: MCP tool changes break Epic 2nd Brain**
- **Solution**: Git revert the changes, try different approach
- **Impact**: Might need Session 2B Part 2 tomorrow

**Problem: Running out of time/energy**
- **Solution**: Stop at natural checkpoint, resume tomorrow
- **Suggested checkpoints**: 
  - After Part 3 (documents migrated)
  - After Part 4 (MCP tools updated)
  - Continue Parts 5-7 next session

---

## 📝 What to Bring Back to Claude Chat (Session 2C)

After Session 2B with Claude Code, come back to me (Claude Chat) with:

1. **Session log from Claude Code** 
   - Location: `ai-assistant/docs/sessions/claude-code/2025-11-XX-multi-project-expansion.md`
   - I'll read this to understand what shipped

2. **Your observations**:
   - What worked smoothly?
   - What was harder than expected?
   - Any decisions you had to make?
   - Are you confident Session 3 (real Legacy AI usage) will work?

3. **Quick test results**:
   - Did `start_session("Legacy AI")` work?
   - Did context load in <10 seconds?
   - Can you see the Notion filtered views?

**Session 2C will be short** (15-30 min) - just validation that we're ready for Session 3 (real business usage).

---

## 🎯 After Session 2C: Prepare for Session 3

**Session 3 = Real Legacy AI Customer Discovery Session**

Come back to me (Claude Chat) when you're ready to:
- Analyze an actual interview (Uncle Bob or another from next week)
- Use the new workflow end-to-end
- Validate that this actually saves you time vs manual Notion workflow

**What I'll need for Session 3**:
- Interview transcript (from Notion AI or your USB recorder)
- Any background context on the interviewee
- Specific questions you want to explore (Jobs-to-be-done insights, positioning validation, etc.)

**Expected Session 3 flow**:
1. "Start session for Legacy AI, customer-discovery"
2. Claude loads context in <10 seconds
3. We work through interview analysis together using template
4. I help extract Jobs-to-be-done insights, strategic implications
5. We commit to repo, auto-syncs to Notion
6. Session log documents insights + next actions

---

## 💡 Pro Tips for Session 2B

**Tip 1: Take breaks**
- 6-8 hours is a long session
- Natural breakpoints after Parts 3, 4, 5
- Don't rush if you're tired (mistakes happen)

**Tip 2: Test incrementally**
- Don't wait until end to test
- After each part, run quick validation
- Easier to debug small issues than big ones at end

**Tip 3: Document as you go**
- If you make architectural decisions, tell Claude Code to log them
- Future you (and Peter) will thank you

**Tip 4: Don't optimize prematurely**
- If something is "good enough", move on
- Phase 3-4 is for refinement
- Goal is "working" not "perfect"

**Tip 5: Keep momentum**
- Session 2B is mechanical (less strategic than 2A or 2C)
- Claude Code is great at this kind of work
- Stay in execution mode, don't second-guess architecture we already decided

---

## ✅ Final Confirmation

Before you start Session 2B, make sure:

- [ ] You have 6-8 hours available (or can split across 2 days)
- [ ] You've gathered the 6 documents listed above
- [ ] You have GitHub account access (for creating organization)
- [ ] You're in your morning deep work block OR midday implementation mode
- [ ] You've read the handoff document at least once
- [ ] You're ready to make decisions when Claude Code presents options

**When ready**: Open Claude Code, paste the opening statement from this doc, and let Claude Code drive.

**Good luck! See you in Session 2C for review. 🚀**

---

**P.S.** If you get stuck or have questions during Session 2B, you can always come back to me (Claude Chat) for strategic guidance. But try to let Claude Code handle the tactical implementation - that's what it's great at.
