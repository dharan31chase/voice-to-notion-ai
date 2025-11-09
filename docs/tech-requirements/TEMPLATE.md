# Technical Requirements: [Feature Name]

**Status**: Draft | Ready to Build | In Progress | Complete
**PRD**: [Link to prd/[feature].md]
**Owner**: [Developer name]
**Last Updated**: [YYYY-MM-DD]

---

## 🎯 TL;DR
[One sentence: Technical approach + estimated effort]

---

## 🎯 Architecture Decision

**Approach**: [High-level approach chosen]
**Rationale**: [Why this approach over alternatives]

**Alternatives Considered**:
1. **[Alternative A]**: [Brief description]
   - Pros: [List pros]
   - Cons: [List cons]
   - Why rejected: [Reason]

2. **[Alternative B]**: [Brief description]
   - Pros: [List pros]
   - Cons: [List cons]
   - Why rejected: [Reason]

**Trade-offs Accepted**:
- [Trade-off 1]: [What we're giving up + what we're gaining]
- [Trade-off 2]: [What we're giving up + what we're gaining]

---

## 🚫 Out of Scope (PARITY Approach)

**What We're NOT Doing Now**:
1. [Enhancement/Optimization X]
   - Why deferred: [Reason - complexity, time, dependencies]
   - Effort if done later: [X hours]
   - Benefit: [What it would unlock]
   - Roadmap: [Yes - added to future enhancements | No]

**Future Enhancements** (documented for later):
- [Enhancement 1]: [Brief description + estimated effort]
- [Enhancement 2]: [Brief description + estimated effort]

---

## 🛠️ Implementation Plan

### Phase 1: [Phase Name] (X hours)
**Goal**: [What this phase achieves]

**Steps**:
1. [Step 1] (X min)
   - Files: `[file1.py]`, `[file2.py]`
   - Changes: [Brief description]

2. [Step 2] (X min)
   - Files: `[file3.py]`
   - Changes: [Brief description]

**Success Criteria**:
- [ ] [Testable condition 1]
- [ ] [Testable condition 2]

### Phase 2: [Phase Name] (X hours)
[Same structure as Phase 1]

---

## 📁 Files Modified

### New Files
```
path/to/new_file1.py  # Purpose: [Brief description]
path/to/new_file2.py  # Purpose: [Brief description]
```

### Modified Files
```
path/to/existing_file.py  # Changes: [Brief description]
```

### Configuration Changes
```
config/settings.json  # Added: [new settings]
.env                  # Added: [new env vars]
```

---

## ⚙️ Configuration Changes

**Environment Variables** (`.env`):
```
NEW_VAR_1=value  # Purpose: [Why needed]
NEW_VAR_2=value  # Purpose: [Why needed]
```

**Config Files** (`config/[file].json`):
```json
{
  "new_setting": "value"
}
```

---

## ✅ Testing Strategy

### Unit Tests
```python
def test_feature_1():
    # Test implementation

def test_feature_2_edge_case():
    # Test implementation
```

### Integration Tests
- [ ] Test end-to-end workflow
- [ ] Test error handling
- [ ] Test with real data

### Manual Testing
1. [Test case 1]: [Expected behavior]
2. [Test case 2]: [Expected behavior]
3. [Test case 3]: [Expected behavior]

---

## 📅 Timeline & Status

**Current Status**: Draft | Ready to Build | In Progress | Complete
**Estimated Effort**: [X hours total]
**Target Completion**: [Date]

**Key Milestones**:
- [Phase 1]: [Date] - [What gets unlocked]
- [Phase 2]: [Date] - [What gets unlocked]

**Blockers**: [None | List blockers]

---

## 🚀 Deployment Plan

**Validation Steps**:
1. Run tests (unit + integration)
2. Manual smoke test with real data
3. Verify success criteria met

**Rollback Plan**:
- Git revert to commit `[hash]`
- Restore config if needed
- Document what went wrong

---

## 🚨 Open Issues & Decisions

**Bugs Discovered**:
- [Bug 1]: [Description, severity, workaround]

**Design Decisions**:
1. **[Decision]**: [What was decided]
   - Why: [Rationale]
   - Trade-offs: [What we're accepting]
   - Impact: [How this affects future work]
   - Date: [When]

**Platform Limitations**:
- [Limitation 1]: [Description, workaround, cross-platform alternative if needed]

---

## 🔗 Links

- **PRD**: [Link to prd/[feature].md]
- **Architecture Diagram**: [Link to mermaid or Figma]
- **GitHub Issue**: [Link to issue tracker]
- **Notion Roadmap**: [Link to Notion]

---

## 📝 Version History

| Date | Author | Changes |
|------|--------|----------|
| YYYY-MM-DD | [Name] | Initial draft |
| YYYY-MM-DD | [Name] | Updated architecture |
