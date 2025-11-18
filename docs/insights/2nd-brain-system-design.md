# 2nd Brain System Design

**Source**: 2a08369c73058044baceefd7a2665570

---

## Key Components of the System

Let's frame your second brain as an ecosystem with five subsystems:

## Draft Heuristic Logic (from your narrative)

Here's how the logic can operate at a systems level, pulling from GTD and your notes:

### 1️⃣

### Capture → Clarify

Every new item enters an In-Basket with metadata:

source | timestamp | project alias | emotion | energy | duration_estimate

The system then runs through:

- Intent detection (verb = actionable, noun = idea/reference)
- Classification rules (keyword like "task", "note", "project", "switchback")
- Ambiguity handler (flag for "needs refinement" if task is vague like "research")
### 2️⃣

### If Actionable → Define Next Action

If task is actionable, the system predicts:

- Next Action Type: communication, research, build, learn, plan, reflect
- Estimated Duration: based on your historical data + heuristics (ML-assisted)
### 3️⃣

### Duration Logic Model

Let's formalize this — early prototype logic:

🔹 Over time, the model adjusts these based on actual completion data.

### 4️⃣

### Prioritization Engine (Dual Model)

Two models working in parallel:

### a. Adaptive Weighting Model

Dynamic scoring per task:

Priority Score = (Urgency × 0.4) + (Leverage × 0.4) + (Energy Fit × 0.2)

where:

- Urgency = proximity to deadline or verbal cue ("today", "soon")
- Leverage = project-level weight (Legacy AI > Second Brain > Remodel > Craftsman)
- Energy Fit = match between task energy demand and current user energy (switchback data)
### b. Nudge × (Motivation – Friction)^Satisfaction

This sits on top as a behavioral override—helps decide which high-leverage items should be nudged even if friction is high.

### 5️⃣

### Scheduling Orchestrator

When you enter a deep work block, the orchestrator:

1. Filters tasks for that project + energy fit + duration match.
1. Presents a shortlist sorted by adaptive priority score.
1. As you approve/override tasks, it learns your implicit preferences.
1. Once confidence ≥ 0.95, transitions to auto-scheduling mode.
## 🧠 PHASE 4 — Learning & Feedback Loop

After each day or deep work block:

1. Capture meta-voice note →
1. Tag as Reflection Log, link back to the task/project.
1. The model fine-tunes:
1. Weekly system reflection produces insights:
## 🧩 1. Meta-Pattern Analysis

### A. You Think in Narratives, Not Discrete Tasks

You naturally explain why a task matters, its emotional or leverage context, and how it ties to larger arcs (e.g., "this helps Legacy AI interviews").

→ Insight: The system should capture "context paragraphs," not just task titles. Those paragraphs are rich training data for priority inference (urgency, leverage, emotional charge).

Design Hook:

Add a Context or Why / So-That field.

Let voice capture auto-fill it; later an NLP model can extract leverage signals ("communication", "learning", "customer outreach").

---

### B. You Reclassify on the Fly

You frequently realize "this isn't a task, it's a note / idea / milestone."

→ Insight: Classification is dynamic; you use semantic correction mid-review.

Design Hook:

Implement a Reclassification Shortcut (Cmd+Shift+R or a voice tag like "convert to note").

Feed those corrections back into the classification model as supervised examples.

---

### C. You Work in Blocks (Energy + Theme Cohorts)

You group actions by communication, learning, research, ideation—then batch within those.

→ Insight: Your natural unit of work is a mode, not a project or due date.

Design Hook:

Add a Mode property (Communication / Learning / Build / Reflect).

Use it for "batch suggestions": when you open a communication block, the orchestrator surfaces all pending communication tasks.

---

### D. You Think in Time Horizons, Not Just Deadlines

You repeatedly say "end of week," "end of month," "later in design phase."

→ Insight: Your mental scheduling operates in fuzzy horizons, not absolute times.

Design Hook:

Allow "fuzzy deadlines" (This week, Later this month, Next phase).

The prioritization engine can translate these into rolling target windows.

---

### E. You Use Quick Micro-Decisions as Momentum Builders

Example: doing a 2-minute re-tag or marking duplicates immediately.

→ Insight: You intuitively apply the "two-minute rule" to create flow.

Design Hook:

Detect micro-tasks (<2 min by language or your historical average) and queue them into a Quick Wins list for momentum sessions.

---

### F. You Assign Leverage Qualitatively

You evaluate importance by systemic leverage ("improves workflow → enables Legacy AI → creates impact").

→ Insight: Leverage is relational, not numeric; it's hierarchical across projects.

Design Hook:

Model leverage as graph edges:

Task → Sub-Project → Project → Mission.

Each layer inherits weighted leverage. The prioritization algorithm propagates importance upward.

---

### G. You Verbally Reflect Mid-Process

You narrate why you defer or delegate ("I'll wait till communication block").

→ Insight: Reflection happens within execution, not only at weekly review.

Design Hook:

Capture those verbal cues as micro-reflection data:

Reason_for_deferral, Emotion_at_choice, Confidence_level.

Used to train the adaptive model on real decision logic.

---

## ⚙️ 2. Workflow Friction Points


🧠 3. Emerging System Heuristics


## 🔧 4. Next-Step Implementation Map (Task Module)

1. Schema Upgrade
1. Smart Processing Rules
1. Prioritization Engine Prototype
Priority = (Leverage × 0.5) + (Urgency × 0.3) + (EnergyFit × 0.2)

- Re-rank daily.
- Override learning from manual reorder or deferral voice notes.
1. Review Loop
---

## 🔭 5. Where to Go Next

I'd suggest we now visualize this task-module flow—from capture → clarify → organize → prioritize → reflect—

and design the adaptive prioritization algorithm spec that plugs into Notion.
