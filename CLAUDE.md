- ## Commit Message Format (REQUIRED)

  **ALWAYS use this format for git commits:**

  ```
  [ROADMAP-X] Brief summary (70 chars max)

  ## What Shipped

  1. [Feature/Fix]: [Description + impact]
  2. [Feature/Fix]: [Description + impact]
  (Max 5 items, 1-2 sentences each)

  ## Critical Discovery (Optional)

  [User pain point or workflow issue discovered]
  Solution: [How addressed or deferred]

  ## Decisions

  - [Decision 1]: [Why this approach]
  - [Decision 2]: [Why this approach]
  (Max 3 decisions)

  ## Architecture Decisions (Optional)

  [Significant technical choice made]
  - Options: [A, B, C]
  - Chosen: [X] because [rationale]
  - Trade-offs: [What we're accepting]

  ## Impact

  [Metrics or unblocked work]

  ## Next Steps

  [What's next, what's deferred]

  ## Key Learnings

  [1-sentence insight from this work]

  🤖 Generated with [Claude Code](https://claude.com/claude-code)

  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

  **Character Limit**: Keep total message ≤1000 chars to avoid GitHub UI truncation
  - Subject line: ≤70 chars
  - Each section: ≤3 items, 1-2 sentences each
  - Optional sections: Skip if not applicable

  **Git Hook**: `.git/hooks/prepare-commit-msg` pre-fills this template

- ## Session Log Format (REQUIRED)

  **When user says "close session" or "end session":**

  1. Create session log: `docs/sessions/claude-code/[YYYY-MM-DD]-[topic].md`
  2. Use template from: `docs/sessions/TEMPLATE.md`
  3. Mark optional sections: "Critical Discovery" and "Architecture Decisions"
  4. Keep concise: 1-2 sentences per item, max 3 items per section
  5. Include handoff prompt for next session

  **Template structure** (see TEMPLATE.md for full format):
  - What Shipped (required)
  - Critical Discovery (optional)
  - Decisions (required)
  - Architecture Decisions (optional)
  - Impact (required)
  - Next Steps (required)
  - Key Learnings (required)
  - Time Breakdown (required)

- ## Testing Criteria Guidelines

  **When defining testing criteria for PRDs or tech requirements:**

  1. **Priority Hierarchy**: Data integrity (P0) > Performance (P1) > Quality output (P2)
  2. **TDD First**: Write failing test BEFORE code - defines expected behavior, ensures alignment
  3. **Test Structure**: Unit (70%, fast/isolated) > Integration (20%, multi-component) > E2E (10%, full workflow)
  4. **Separate Test Environment**: Dedicated test workspace/APIs - prevents production pollution
  5. **Coverage Target**: 70% code coverage (industry standard) - focus on critical paths
  6. **Golden Dataset**: Canonical test files with known expected outputs - reproducible tests
  7. **Performance Baselines**: Track regression with 20% degradation threshold - save benchmarks, compare to golden
  8. **Test Requirements**: Tests REQUIRED for new features and bug fixes - enforced at session end
  9. **Success Metrics**: 95%+ test pass rate, unit <30s, integration <2min, E2E <10min
  10. **End-to-End Validation**: "Code built ≠ infrastructure exists" - verify folders/databases/config actually exist

  **Full details**: See `docs/context/testing-roadmap.md`

- ## Tech Requirements Review Protocol

  **BEFORE starting implementation:**

  1. ✅ Create tech requirements doc (detailed, comprehensive)
  2. ✅ Include Architecture Decision Framework (all 8 steps from ~/CLAUDE.md):
     - Cohesion Analysis (What belongs together?)
     - Single Responsibility Test (One reason to change)
     - Dependency Flow Mapping (What depends on what?)
     - Testability Check (Can I unit test this?)
     - Extensibility Analysis (Future features)
     - Pattern Validation (Proven patterns)
     - Alternative Comparison (Why this over that?)
     - Trade-offs Summary (Explicit trade-offs)
  3. ✅ State ALL assumptions explicitly
  4. ✅ Ask clarifying questions
  5. ⏸️  **WAIT FOR USER APPROVAL** before writing code
  6. ✅ User confirms: "Approved - start implementation"

  **Why**: Ensures user understands "why" and validates assumptions before effort is invested.

  **Example Flow**:
  - User: "Implement X feature"
  - Claude: Creates detailed tech requirements doc
  - Claude: "I've created the tech requirements. Please review and approve before I start implementation."
  - User: "Approved - start implementation"
  - Claude: Proceeds with coding

  **Gates This Applies To**:
  - New features (not trivial bug fixes)
  - Architecture changes
  - Refactoring with >2 files
  - Performance optimizations
  - External API integrations

- ::# Router Extraction Prompt Template
  Use this checklist BEFORE creating implementation plan

  ## 1. CURRENT STATE ANALYSIS
  □ Read the code to be extracted (lines X-Y in intelligent_router.py)
  □ Explain what it currently does in simple terms
  □ Identify dependencies (what it calls, what calls it)
  □ Note any "quirks" or non-obvious logic

  ## 2. NOTION DATABASE CONSTRAINTS
  □ Get EXACT property names (case-sensitive, emoji-included)
  □ Confirm property type (select, multi-select, text, etc.)
  □ Request screenshots if any ambiguity
  □ Identify data integrity risks (duplicates, case-sensitivity)
  □ Document exact values that must be preserved

  ## 3. SCOPE DEFINITION
  □ Default: PARITY + INFRASTRUCTURE (extract as-is, prepare for future)
  □ Clearly state what we're NOT changing
  □ Identify future enhancement opportunities
  □ Get explicit approval before "fixing" anything

  ## 4. INTEGRATION POINTS
  □ How does ConfigLoader load this? (top-level key? nested?)
  □ What calls this method? (check all usages)
  □ Backward compatibility requirements
  □ Lazy loading needed? (circular import risk?)

  ## 5. EDGE CASES FROM ORIGINAL
  □ What edge cases does current code handle?
  □ Are there intentional gaps/limitations?
  □ Any hardcoded fallbacks we should preserve?
  □ Test cases that cover current behavior

  ## 6. IMPLEMENTATION PLAN STRUCTURE
  □ Files to create (with exact structure)
  □ Files to modify (with line numbers)
  □ Configuration keys (explain merge behavior)
  □ Success criteria (specific, measurable)
  □ Test plan (cover all edge cases)

  ## 7. CLARIFYING QUESTIONS (Ask BEFORE implementing)
  □ Exact Notion values (with screenshots if needed)
  □ Scope confirmation (parity vs enhancement)
  □ Any intentional limitations to preserve?
  □ Should we fix gaps or extract as-is?

  ## 8. FINAL CHECKLIST BEFORE CODING
  □ User has approved the plan
  □ All exact values documented
  □ No assumptions about "fixes"
  □ Backward compatibility guaranteed
  □ Test cases defined