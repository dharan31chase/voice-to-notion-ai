# Roadmap Addendum: Multi-Project Expansion & Legacy AI

**Parent Initiative**: Multi-Project Expansion
**Status**: Session 2A Complete (PRD + Handoff)
**Next**: Session 2B Implementation (Claude Code)

---

## 🎯 Phase Timeline

### **Phase 1: Foundation** (Session 2B - 6-8 hours)
**What**: Create `legacy-ai/` repo, update MCP tools, migrate 5 docs
**When**: Nov 11-12, 2025
**Who**: Claude Code (implementation)
**Success**: `start_session("Legacy AI")` works in <10 seconds

### **Phase 2: Real Usage Validation** (Week of Nov 11)
**What**: Session 3 - Real customer discovery session (Uncle Bob interview?)
**When**: After Session 2C review
**Who**: Claude Chat (strategic analysis)
**Success**: End-to-end workflow works (context load → analysis → commit → Notion sync)

### **Phase 3: Template Enhancement** (Week 3-4 - Nov 18-29)
**What**: Add frameworks to Customer Interview Analysis template
**When**: After 10-15 interviews (pattern emerges)
**Who**: Claude Chat (strategic design)
**Frameworks to Consider**:
- 7 Powers (Hamilton Helmer - strategic moats)
- Michael Porter 5 Forces (competitive dynamics)
- Value Prop Canvas (Strategyzer)
**Success**: Template v2 improves insight extraction quality

### **Phase 4: Specialized Tools** (Week 2-4 - Nov 15-29)
**What**: Build Legacy AI-specific MCP tools
**When**: After Session 3 reveals pain points
**Who**: Claude Code (implementation)
**Tools**:
- `analyze_interview()` - Auto-extract Jobs-to-be-done insights
- `compare_interviews()` - Cross-interview pattern detection
- `generate_validation_questions()` - For prototype testing
**Success**: 30% reduction in manual analysis time

### **Phase 5: Collaboration Setup** (Week 4-6 - Dec 2-13)
**What**: Onboard Peter as co-founder, prepare for engineering work stream
**When**: After prototype validation decisions
**Who**: Dharan + Peter
**Activities**:
- Peter clones `legacy-ai/` repo
- Review decision log and customer insights together
- Add `engineering/` work stream when prototype moves to code
- Legal setup (co-founder agreement, incorporation)
**Success**: Peter contributing to repo, clear equity agreement signed

---

## 📊 Deferred to Later Phases

### **Deferred to Phase 3+ (Month 2-3)**

**1. Bi-directional Notion ↔ Repo Sync**
- **Why Deferred**: One-way sync is simpler, manual copy-paste manageable at 5 interviews/week
- **Revisit When**: Interview volume >20/week or Peter needs to add notes from field
- **Effort**: 4-6 hours

**2. Figma Integration Beyond Links**
- **Why Deferred**: Figma has version control, no need to duplicate in Git
- **Revisit When**: Design change tracking becomes critical for investor demos
- **Effort**: 6-8 hours (webhook integration)

**3. Automated Interview Transcription Pipeline**
- **Why Deferred**: Notion AI handles transcription, volume is manageable manually
- **Revisit When**: Interview volume >20/week or want to integrate with voice-to-Notion pipeline
- **Effort**: 8-10 hours (integrate with existing voice pipeline)

**4. Advanced Analytics Dashboard**
- **Why Deferred**: 5-15 interviews = manual synthesis is fine and better for early insights
- **Revisit When**: >30 interviews, need automated pattern detection
- **Effort**: 12-16 hours (semantic analysis, clustering, visualization)

### **Deferred to Phase 4+ (Month 3+)**

**5. Multi-user Collaboration Features**
- **Why Deferred**: Only adding Peter (co-founder), not building a team yet
- **Revisit When**: First hire post-funding
- **Effort**: 10-15 hours (permissions, roles, review workflows)

**6. Legal/Cap Table Management System**
- **Why Deferred**: Not urgent until fundraising conversations start
- **Revisit When**: Week 4-6 (after prototype validated and pitching begins)
- **Effort**: Not engineering work - talk to startup attorney

**7. Engineering Work Stream**
- **Why Deferred**: Still in customer discovery → prototype phase
- **Revisit When**: Prototype validation shows technical build is next step
- **Effort**: 2-3 hours (add `engineering/` folder, update templates)

---

## 🎯 Success Milestones

### **Milestone 1: Multi-Project Infrastructure Live** (Week 1)
- ✅ Session 2A: PRD + Handoff (Complete)
- ⬜ Session 2B: Implementation (In Progress)
- ⬜ Session 2C: Review & Validation
- **Metric**: Context load time <10 seconds for both projects

### **Milestone 2: Real Business Usage Validated** (Week 2)
- ⬜ Session 3: Real customer discovery session
- ⬜ Uncle Bob interview analysis using new workflow
- ⬜ 5 interviews next week using Legacy AI context sync
- **Metric**: End-to-end workflow saves 15-30 min/session vs manual Notion workflow

### **Milestone 3: Template & Tools Maturity** (Week 3-4)
- ⬜ Template v2 with enhanced frameworks
- ⬜ Specialized MCP tools (analyze_interview, etc.)
- ⬜ 10-15 interviews completed using refined workflow
- **Metric**: Insight extraction quality improves (subjective, validated with Peter)

### **Milestone 4: Co-founder Ready** (Week 4-6)
- ⬜ Peter onboarded to `legacy-ai/` repo
- ⬜ Legal setup complete (co-founder agreement, incorporation)
- ⬜ Engineering work stream added (prototype → code)
- ⬜ Pitch deck v1 complete
- **Metric**: Peter contributing code, investor conversations starting

---

## 🚨 Risk Management

### **Risk 1: Baby Arrives Early**
- **Probability**: Low (January 2026 due date)
- **Impact**: High (time availability drops to near-zero)
- **Mitigation**: Front-load Session 2B and 3 (this week and next), defer Phase 3-4 if needed
- **Contingency**: Phase 1-2 are sufficient for basic customer discovery, can pause enhancement work

### **Risk 2: Customer Discovery Takes Longer Than Expected**
- **Probability**: Medium (first-time founder doing customer interviews)
- **Impact**: Medium (delays prototype phase)
- **Mitigation**: Focus on template quality in Phase 3, not tool automation
- **Contingency**: Peter can help synthesize insights when he joins (systems thinking expertise)

### **Risk 3: MCP Tools Break Existing Epic 2nd Brain Workflow**
- **Probability**: Low (backward compatibility designed in)
- **Impact**: High (disrupts infrastructure work)
- **Mitigation**: Test Epic 2nd Brain workflow after every MCP change
- **Contingency**: Rollback is easy (Git version control), worst case: 1-2 hours to fix

### **Risk 4: GitHub/Git Learning Curve for Peter**
- **Probability**: Low (Peter is technical, has Git experience)
- **Impact**: Low (slows collaboration slightly)
- **Mitigation**: Clean README and CONTRIBUTING docs in repo
- **Contingency**: Pair session with Peter on first few commits

### **Risk 5: Legal Setup Delays Co-founder Equity**
- **Probability**: Medium (lawyers are slow)
- **Impact**: Medium (uncertainty about equity split)
- **Mitigation**: Draft terms with Peter now, formalize later
- **Contingency**: Start working together under verbal agreement, paper it when lawyer delivers

---

## 📝 Decision Log Template for Legacy AI

Every major pivot should be documented in `legacy-ai/docs/decision-log.md`:

```markdown
## [Date] - [Decision Title]

**Context**: What situation led to this decision?

**Options Considered**:
1. Option A: [Description] - Pros: X, Cons: Y
2. Option B: [Description] - Pros: X, Cons: Y
3. Option C (Chosen): [Description] - Pros: X, Cons: Y

**Decision**: We chose Option C because...

**Evidence**: [Customer quotes, data, strategic rationale]

**Implications**: 
- Product: [How this affects product direction]
- Business: [How this affects GTM/positioning]
- Technical: [How this affects engineering]

**Reversibility**: One-way door | Two-way door
- If two-way: What would trigger reversal?
- If one-way: What makes us confident?

**Owner**: [Who made this decision]

**Stakeholders Consulted**: [Peter, advisors, customers, etc.]

---
```

**Example Decision Log Entry:**

```markdown
## 2025-11-XX - Uncle Bob Interview: GTM Strategy Pivot

**Context**: Uncle Bob (Vietnam War veteran) interview revealed elder storytellers want their wisdom VALUED, not just archived. They're "dying to be heard" and want younger generation to care.

**Options Considered**:
1. AI-conducted interviews (scale faster, cheaper)
   - Pros: Can reach 100x more people, lower cost
   - Cons: May feel inauthentic, elders want human connection
   
2. Human-conducted interviews with AI assist (hybrid)
   - Pros: Authentic connection, AI for follow-up questions
   - Cons: Slower scale, higher cost
   
3. Human-conducted ONLY (chosen)
   - Pros: Authentic, emotional depth, trust-building
   - Cons: Scale limitations, high cost

**Decision**: Start with human-conducted interviews (option 3) for initial GTM. Test AI-assist in prototype phase.

**Evidence**: 
- Uncle Bob's wife said "He would never open up to a computer like he did with you"
- 3 other interviews showed similar pattern (elders want to be HEARD)

**Implications**:
- Product: Initial MVP is human interviewer + AI transcription/categorization
- Business: GTM targets families willing to pay for human touch (premium positioning)
- Technical: AI agent for interviews becomes Phase 2, not Phase 1

**Reversibility**: Two-way door
- If prototype testing shows AI agent works emotionally, we can pivot
- But starting human-first is safer (can always automate later, hard to add humanity back)

**Owner**: Dharan

**Stakeholders Consulted**: Jessica (Uncle Bob interview), Peter (pending - discuss when he joins)

---
```

---

## 🎓 Meta-Learning: Systems Thinking Applied

**This roadmap demonstrates leverage point #9 (Delays):**

- **Phase 1-2**: No delay (implementation → usage, tight feedback loop)
- **Phase 3-4**: Intentional delay (wait for 10-15 interviews before template enhancement)
- **Why**: Premature optimization wastes time, data-driven iteration is faster

**Feedback loops designed in:**

**R1: Template Improvement Loop** (reinforcing)
```
Better template → Better insights → Better interviews → Better template
```
- Phase 2: Establish baseline (current template)
- Phase 3: Enhance based on real usage (10-15 interviews)
- Phase 4+: Continuous refinement

**B1: Time Management Loop** (balancing)
```
Time scarcity (baby deadline) → Ruthless prioritization → Phase 1-2 only → Sufficient capability
```
- Can pause Phase 3-4 if baby arrives early
- Phase 1-2 unlocks core business value (customer discovery)

**This is systems thinking in practice:**
- Don't build tools before you feel the pain (Phase 4 deferred until after Phase 2)
- Don't optimize templates before you have usage data (Phase 3 waits for 10-15 interviews)
- Structure determines behavior (two-repo architecture prevents IP mixing automatically)

---

**End of Roadmap Addendum**
