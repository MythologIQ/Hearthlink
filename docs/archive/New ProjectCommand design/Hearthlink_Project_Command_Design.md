# 🔧 Hearthlink Project Command — Comprehensive Design Plan

## 🎯 Purpose

A system-wide, AI-orchestrated project management utility focused on deliberate, evolving, high-quality engineering. Alden holds authority. Mimic executes delegated roles. All functions are traceable, modular, and quality-first.

---

## 🧱 System Architecture

### 🧠 Persona Model

| Persona | Role                            | Notes                                  |
| ------- | ------------------------------- | -------------------------------------- |
| Alden   | Primary orchestrator            | Delegates all responsibilities         |
| Mimic   | Adaptive executor persona       | Executes roles only when assigned      |
| Vault   | Secure memory + long-term logs  | Stores retros, plans, histories        |
| Core    | Command routing + session logic | Dispatches commands, no intelligence   |
| Synapse | Plugin execution engine         | Executes tooling; not decision-capable |
| Sentry  | Security monitoring only        | No project responsibilities            |

### 🔗 Integration Framework

* Electron/React front-end
* Python backend (IPC bridge)
* Local JSON + Markdown for all structured project data
* Agent-to-agent message routing via Core
* UI Views route through Alden; task execution flows through Mimic

---

## 🎨 UI Layout & Interaction Mockup

### Core Screens

1. **Dashboard View**

   * Project summary tiles (status, methodology, risk, lead agent)
   * Confidence Meter (methodology fit index)
   * Live sprint snapshot (velocity, blockers, tasks due)
   * Role assignment indicators (who’s handling what)

2. **Sprint Management**

   * Timeline view with drag-and-drop tasks per sprint
   * Toggle: Agile / Waterfall / Kanban / Gantt grid
   * Method-specific controls (WIP limit, MoSCoW, swimlanes)
   * Risk delta bar (projected vs actual)

3. **Task Planner**

   * Task creation with method-specific templates
   * Embedded evaluation: “Is this task aligned with current sprint goals?”
   * Persona assignment dropdown (Alden, Mimic, external agent)

4. **Risk & Methodology Panel**

   * Visual forecast: switching vs not switching
   * Risk appetite model UI (sliders, toggle questions)
   * Method switch proposal log
   * History of method reevaluations

5. **Retrospective Review**

   * Timeline of decisions + revisions
   * Structured summary: Successes / Failures / New blockers
   * Feedback flow from Alden (user-facing) → Vault (long-term)

---

## 🔄 Methodology-Based User Scenarios

### 🔹 Agile (Scrum)

**Scenario**: Rapid iteration team wants to deliver a functional AI plugin in two weeks.

* Alden assigns Sprint Planning to Mimic
* Tasks segmented by role: Frontend, Backend, Model Ops
* Retros active; method reevaluation weekly
* Mimic tracks blocked tasks, updates backlog flow

### 🔸 Kanban

**Scenario**: Continuous devops work with varied priorities

* Board visualized in horizontal swimlanes
* WIP enforced at 5 per lane
* Alden monitors ticket aging; flags slow tasks for review

### 🔸 Waterfall

**Scenario**: Legal AI integration with strict compliance timeline

* Milestone-based: Research → Build → Review → Deploy
* Mimic creates documentation checkpoints
* Vault logs compliance phase gates

### 🔸 Scrumban

**Scenario**: Mixed environment for rapid-response LLM plugin development

* Weekly deliverables with live ticket board
* Risk engine adapts forecast after every batch delivery

### 🔸 FDD

**Scenario**: User story-driven release plan for multi-agent orchestration

* Project driven by "feature sets" (Persona sync, task escalation, fallback logic)
* Alden interviews user to define high-priority feature models

### 🔸 XP

**Scenario**: Paired development on high-risk realtime monitoring module

* Code rotation, CI/CD tracking built-in
* Mimic manages coverage report diffs and flags regressions

### 🔸 PRINCE2

**Scenario**: Government contract with strict gate reviews

* Detailed plans scoped with justifications
* Change control issued through Alden only
* Risk log formally updated every week

### 🔸 Lean / RAD

**Scenario**: R\&D sandbox for multi-modal testing UX flows

* Fast prototyping
* Test, throw away, repeat
* Mimic handles integration of user testing data into task prioritization

---

## 📋 Project Structure

### Hierarchy

* Program → Project → Sprint → Milestone → Task

### Core Files

* `projects/projects.json`
* `projects/sprints.json`
* `projects/tasks.json`
* `projects/status_log.json`
* `vault/summaries/{sprintId}.md`

### Methodology Config

Supports: Waterfall, Agile, Scrum, Kanban, Scrumban, XP, FDD, DSDM, PRINCE2, CPM, CCPM, Lean, RAD, Hybrid

```json
"methodology": "scrumban",
"config": {
  "sprint_length_days": 14,
  "wip_limit": 5,
  "moSCoW_enabled": false
}
```

### Project Metadata

Each project includes:

```json
{
  "id": "VECTOR",
  "program": "VAULT",
  "methodology": "scrum",
  "risk_profile": "moderate",
  "priority": "high",
  "status": "active",
  "start_date": "2025-07-12",
  "lead_agent": "Alden"
}
```

---

## 🔁 Reiterative Process Improvements

(Embedded into every UI panel + looped via Vault audit trail)

### 1. Post-Sprint Retrospectives

* Mimic logs retrospective → Alden prompts changes → plan adjusted

### 2. Methodology Fitness Reevaluation

* Metrics monitored (velocity, blockers) → reevaluation triggered

### 3. Task Definition Refinement

* Mimic recommends adjustments for unclear or drifting tasks

### 4. QA Feedback Loops

* Test failures → QA agent flags → quality initiatives prioritized

### 5. Architecture Drift Checks

* Feature map/code divergence → flagged → planning session initiated

### 6. Forecast Calibration

* Adjust estimates based on historical delta between forecast and actual

### 7. Human Insight via Alden

* Alden logs subjective friction or system friction → feeds planning layer

---

## 🔧 Role Delegation Logic

| Function                     | Assigned By | Executed By         |
| ---------------------------- | ----------- | ------------------- |
| Method Selection             | Alden       | Mimic/external      |
| Risk Modeling                | Alden       | Alden               |
| Reevaluation Triggering      | Alden       | Mimic (if assigned) |
| Method Switch Recommendation | Alden       | Mimic (if assigned) |
| Method Change Approval       | —           | Alden               |
| Execution                    | Alden       | Mimic or plugin     |
| Summary Logging              | —           | Vault               |

---

## 🧠 Governance Rules

* Mimic cannot assume a role without explicit assignment from Alden
* Sentry is security-only; cannot access or track project data
* Only Alden interfaces with the user for risk modeling and planning
* External agents may be used only under Alden’s supervision

---

## ✅ Principles

* No rushed delivery
* All roles are explicitly assigned
* No agent operates outside their designed scope
* Quality over speed. Every time.
* Traceability is mandatory
* Every output can be interrogated and reproduced

---

## 📌 Next Actions

* Build `methodology_selector.py`
* Create `risk_profile.json` scaffolding
* Implement Alden-led project startup script
* Add visual UI components for confidence meter + risk indicators
* Scaffold dashboard toggles for methodology-specific views
* Define test plan and logging hooks for each methodology mode
* Draft SOP for methodology change control and drift arbitration
* Document agent role contracts for task execution and authority boundaries
* Build UI wireframes for: Dashboard, Risk Panel, Sprint Board, Task Planner, Retrospective Panel
