# Technical Requirements: Auto RAG Reindexing

**Status**: Draft - Ready for Implementation
**Owner**: Dharan Chandrahasan
**Created**: 2025-12-15
**Related PRD**: [rag-implementation-legacy-ai.md](../prd/rag-implementation-legacy-ai.md)
**Related Issue**: Issue #10 (Auto-reindex specified in PRD but never implemented)

---

## 🎯 Problem Statement

**Current Workflow Tax**:
- User creates new PRDs, session logs, or tech-req docs
- Must manually run `python scripts/index_rag.py --force` to make them searchable
- Forgets to reindex → stale search results → wastes time
- **Current workaround**: Copy-pasting to Notion to avoid manual reindexing friction

**Impact**:
- User avoids adding files due to reindexing friction
- Workflow interrupted (manual command execution)
- Stale RAG index (new docs not searchable)
- Notion workaround creates duplicate effort

**Goal**: Zero-friction document addition - write doc, auto-searchable next morning (7am).

---

## ✅ Success Criteria

1. **Zero manual steps**: User never runs `python scripts/index_rag.py` manually
2. **Fresh index daily**: RAG auto-reindexes at 7am (before work block starts)
3. **Secure credentials**: OPENAI_API_KEY never exposed in crontab or logs
4. **Reliable execution**: Works even if computer was asleep (runs on wake)
5. **Observable errors**: Failures logged and visible
6. **No workflow interruption**: Runs silently in background

---

## 🏗️ Architecture

### **Components**

```
┌─────────────────────────────────────────────────────────────┐
│ macOS Cron (7am daily trigger)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Wrapper Script: scripts/reindex_cron.sh                     │
│ - Load .env (OPENAI_API_KEY)                                │
│ - Change to repo directory                                  │
│ - Run indexing script                                       │
│ - Log success/failure                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Indexing Script: scripts/index_rag.py --force               │
│ - Delete old index                                          │
│ - Scan docs/ folders                                        │
│ - Generate embeddings (OpenAI API)                          │
│ - Store in ChromaDB                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ChromaDB: .chroma/chroma.sqlite3                            │
│ - Updated collections (epic-2nd-brain, legacy-ai)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Plan

### **Phase 1: Create Wrapper Script** (15 min)

**File**: `scripts/reindex_cron.sh`

**Requirements**:
- Load `.env` file securely (no hardcoded API keys)
- Change to correct directory
- Run indexing with `--force` flag
- Log output with timestamps
- Exit with proper status codes

**Pseudocode**:
```bash
#!/bin/bash

# 1. Change to repo directory
cd /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant

# 2. Create log directory if missing
mkdir -p logs

# 3. Load environment variables from .env
export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)

# 4. Verify OPENAI_API_KEY loaded
if [ -z "$OPENAI_API_KEY" ]; then
    echo "$(date): ❌ ERROR: OPENAI_API_KEY not found in .env" >> logs/rag-reindex.log
    exit 1
fi

# 5. Run indexing script
/usr/bin/python3 scripts/index_rag.py --force >> logs/rag-reindex.log 2>&1
EXIT_CODE=$?

# 6. Log result
if [ $EXIT_CODE -eq 0 ]; then
    echo "$(date): ✅ Reindexing successful (exit code: 0)" >> logs/rag-reindex.log
else
    echo "$(date): ❌ Reindexing failed (exit code: $EXIT_CODE)" >> logs/rag-reindex.log
fi

exit $EXIT_CODE
```

**Validation**:
- Run manually: `bash scripts/reindex_cron.sh`
- Check logs: `tail -20 logs/rag-reindex.log`
- Verify ChromaDB updated: `ls -lh .chroma/chroma.sqlite3`

---

### **Phase 2: Add to Crontab** (5 min)

**Cron Entry**:
```cron
# RAG Reindexing - Daily at 7am
0 7 * * * /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/scripts/reindex_cron.sh
```

**Installation**:
```bash
# Edit crontab
crontab -e

# Add the line above, save and exit

# Verify crontab
crontab -l
```

**Validation**:
- Manually trigger cron job (change to `* * * * *` for next minute)
- Wait 1 minute, check logs
- Verify it ran successfully
- Change back to `0 7 * * *` (7am daily)

---

### **Phase 3: Configure macOS Wake Settings** (5 min)

**Problem**: Cron won't run if computer is asleep at 7am

**Solution Options**:

#### **Option A: Prevent Sleep on AC Power** (Recommended)
```bash
# Computer stays awake when plugged in
sudo pmset -c sleep 0
```

**Pros**: Simple, reliable
**Cons**: Computer always on (but display can sleep)

#### **Option B: Schedule Wake Time**
```bash
# Wake computer at 6:55am daily (before 7am cron)
sudo pmset repeat wake MTWRFSU 06:55:00
```

**Pros**: Computer can sleep overnight, wakes before cron
**Cons**: More complex, requires testing

**Recommendation**: Start with Option A, switch to Option B if battery drain is an issue.

**Validation**:
```bash
# Check current power settings
pmset -g

# Verify sleep settings changed
pmset -g | grep sleep
```

---

### **Phase 4: Error Monitoring** (10 min)

**Add Log Rotation**:

Create `scripts/rotate_rag_logs.sh`:
```bash
#!/bin/bash
cd /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant

# Keep last 30 days of logs
LOG_FILE="logs/rag-reindex.log"
if [ -f "$LOG_FILE" ]; then
    # Archive old logs
    ARCHIVE_DATE=$(date -v-30d +%Y-%m-%d)
    sed -i.bak "/$ARCHIVE_DATE/,\$!d" "$LOG_FILE"
    rm -f "${LOG_FILE}.bak"
fi
```

**Add to Weekly Cron**:
```cron
# Log rotation - Weekly on Sunday at 8am
0 8 * * 0 /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant/scripts/rotate_rag_logs.sh
```

**Validation**:
- Check log file size: `du -h logs/rag-reindex.log`
- After 30 days, verify old entries removed

---

## 🔒 Security Considerations

### **1. API Key Protection**

**✅ Safe (Our Approach)**:
- API key stored in `.env` file (gitignored)
- Wrapper script loads `.env` at runtime
- Never hardcoded in crontab

**❌ Unsafe (Avoid)**:
```cron
# DON'T DO THIS - API key visible in crontab
0 7 * * * OPENAI_API_KEY='sk-...' python3 scripts/index_rag.py
```

### **2. File Permissions**

```bash
# Ensure .env is not world-readable
chmod 600 .env

# Ensure wrapper script is executable only by user
chmod 700 scripts/reindex_cron.sh

# Verify permissions
ls -la .env scripts/reindex_cron.sh
```

### **3. Log File Security**

```bash
# Logs should not expose API keys
# Wrapper script only logs success/failure (not env vars)
# Indexing script should never print OPENAI_API_KEY
```

**Validation**:
```bash
# Check logs for exposed secrets
grep -i "sk-" logs/rag-reindex.log  # Should return nothing
grep -i "api" logs/rag-reindex.log  # Should only show "API" in messages, not keys
```

---

## 🧪 Testing Plan

### **Test 1: Wrapper Script Works Manually**

```bash
cd /Users/dharanchandrahasan/Documents/1. Projects/ai-assistant
bash scripts/reindex_cron.sh
echo $?  # Should be 0 (success)
tail -5 logs/rag-reindex.log  # Should show success
```

**Expected Output**:
```
2025-12-15 10:30:00: ✅ Reindexing successful (exit code: 0)
```

---

### **Test 2: Cron Job Runs Successfully**

```bash
# Temporarily set cron to run in 2 minutes
crontab -e
# Change to: $(date +%M +2) * * * * ...

# Wait 2 minutes
sleep 120

# Check logs
tail -10 logs/rag-reindex.log
```

**Expected**: New log entry with timestamp ~2 minutes after current time

---

### **Test 3: Handles Missing .env Gracefully**

```bash
# Temporarily rename .env
mv .env .env.backup

# Run wrapper
bash scripts/reindex_cron.sh
echo $?  # Should be 1 (failure)

# Check logs
tail -5 logs/rag-reindex.log
# Expected: "❌ ERROR: OPENAI_API_KEY not found in .env"

# Restore .env
mv .env.backup .env
```

---

### **Test 4: Indexing Actually Updates ChromaDB**

```bash
# Check current DB timestamp
ls -lh .chroma/chroma.sqlite3

# Run indexing
bash scripts/reindex_cron.sh

# Check new timestamp (should be updated)
ls -lh .chroma/chroma.sqlite3
```

**Expected**: Modified timestamp changes to current time

---

### **Test 5: Search Returns Fresh Content**

```bash
# Add a new test doc
echo "# Test Document $(date)" > docs/prd/test-reindex.md

# Run indexing
bash scripts/reindex_cron.sh

# Search for it (would need MCP tool, but conceptually):
# search_epic_2nd_brain("test-reindex") should return the new doc
```

---

## 📊 Performance

**Current Reindexing Stats** (from earlier test):
- Documents: 63
- Chunks: 1,002
- Time: ~30-60 seconds
- API Cost: ~$0.01 per reindex (OpenAI embeddings)

**Daily Cost**:
- 1 reindex/day × $0.01 = **$0.01/day** = **$3.65/year**
- Negligible cost vs. time saved

**Time Savings**:
- Manual reindex: 60 sec (command + wait)
- Auto reindex: 0 sec (runs while user is in morning routine)
- Frequency: ~5x/week (as doc creation increases)
- **Savings**: 5 min/week = **260 min/year** = **4.3 hours/year**

**ROI**: 30 min setup saves 4+ hours annually, removes workflow friction

---

## 🚧 Edge Cases & Error Handling

### **Edge Case 1: Computer Off at 7am**

**Scenario**: Computer shut down overnight

**Behavior**: Cron job skipped (won't run)

**Mitigation**:
- User turns on computer → next day's cron runs
- OR: Add "run on boot" logic (launchd alternative)

**Impact**: Stale index for 1 day (acceptable for daily updates)

---

### **Edge Case 2: Network Down (OpenAI API Unreachable)**

**Scenario**: No internet at 7am

**Behavior**: Indexing script fails, logs error

**Mitigation**:
- Error logged: "❌ Reindexing failed (exit code: 1)"
- Next day's cron retries automatically

**Impact**: Stale index for 1 day (acceptable)

---

### **Edge Case 3: .env File Corrupted**

**Scenario**: `.env` file has syntax error or missing key

**Behavior**: Wrapper script exits with error

**Mitigation**:
- Error logged: "❌ ERROR: OPENAI_API_KEY not found in .env"
- User sees error in logs when checking

**Recovery**: Fix `.env` file, next cron run succeeds

---

### **Edge Case 4: ChromaDB Database Corruption**

**Scenario**: `.chroma/` directory corrupted

**Behavior**: Indexing script fails

**Mitigation**:
- Delete `.chroma/` directory
- Next cron run recreates from scratch

**Recovery Time**: 1 day (next morning's cron)

---

## 🔄 Maintenance

### **Daily Tasks**: None (fully automated)

### **Weekly Tasks**: Check logs for errors
```bash
tail -50 logs/rag-reindex.log | grep "❌"
```

### **Monthly Tasks**: None

### **Quarterly Tasks**: Review log file size, rotate if needed

---

## 📈 Future Enhancements (Not in Scope)

### **Enhancement 1: Incremental Indexing** (3 hours)
- Track file modification timestamps
- Only reindex changed files
- **Benefit**: Faster reindexing (5-10 sec vs 60 sec)

### **Enhancement 2: Slack/Email Notifications on Failure** (1 hour)
- Send alert if reindexing fails
- **Benefit**: Immediate error visibility

### **Enhancement 3: Reindex on File Change (inotify/fswatch)** (2 hours)
- Watch `docs/` folder for changes
- Trigger reindex immediately on new file
- **Benefit**: Real-time search index updates

---

## 📝 Clarifying Questions for User

### **Question 1: Sleep Settings**

**Q**: Do you want your computer to stay awake 24/7 (when plugged in), or should we schedule a wake time for 6:55am?

**Options**:
- **A**: Keep computer awake always (when on AC power) - `sudo pmset -c sleep 0`
- **B**: Schedule wake at 6:55am daily - `sudo pmset repeat wake MTWRFSU 06:55:00`

**Recommendation**: A (simpler, reliable), but B if battery drain is a concern

---

### **Question 2: Failure Notifications**

**Q**: If reindexing fails (e.g., no internet, API error), how do you want to know?

**Options**:
- **A**: Check logs manually when you remember (`tail logs/rag-reindex.log`)
- **B**: Get Slack/email notification on failure (requires 1 hour extra setup)

**Recommendation**: A for now (simple), add B later if failures become frequent

---

### **Question 3: Both Projects or Just Epic 2nd Brain?**

**Q**: Should cron reindex both Epic 2nd Brain AND Legacy AI, or just Epic 2nd Brain?

**Current State**:
- Epic 2nd Brain: ✅ Working (63 docs indexed)
- Legacy AI: ❌ Broken (0 docs, path config issue)

**Options**:
- **A**: Just Epic 2nd Brain (`python scripts/index_rag.py --epic-2nd-brain --force`)
- **B**: Both projects (`python scripts/index_rag.py --force`)

**Recommendation**: B (both), but Legacy AI needs path fix first

---

### **Question 4: Log Retention**

**Q**: How long should we keep reindexing logs?

**Options**:
- **A**: 30 days (rotate monthly)
- **B**: 90 days (rotate quarterly)
- **C**: Forever (manual cleanup only)

**Recommendation**: A (30 days) - balance between debugging and disk space

---

### **Question 5: Testing Before 7am Schedule**

**Q**: Should we test the cron job by setting it to run in 2 minutes first, or go straight to 7am daily?

**Options**:
- **A**: Test in 2 minutes (safer, verify it works)
- **B**: Set to 7am immediately (trust it will work)

**Recommendation**: A (test first) - catches issues before going live

---

## ✅ Ready for Implementation?

**Setup Time**: 30-45 minutes total
- Phase 1 (wrapper script): 15 min
- Phase 2 (crontab): 5 min
- Phase 3 (wake settings): 5 min
- Phase 4 (testing): 10 min

**Please answer the 5 clarifying questions above, then I'll implement immediately.**

---

## 📎 Related Documents

- [rag-implementation-legacy-ai.md](../prd/rag-implementation-legacy-ai.md) - Original PRD with auto-reindex requirement
- [live-context-control-v3.md](../prd/live-context-control-v3.md) - Mentions nightly reindex
- `scripts/index_rag.py` - Indexing script we're wrapping
- `scripts/reindex_cron.sh` - Wrapper script (to be created)

---

**Status**: Awaiting user answers to clarifying questions before implementation.
