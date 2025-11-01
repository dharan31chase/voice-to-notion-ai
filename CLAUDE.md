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