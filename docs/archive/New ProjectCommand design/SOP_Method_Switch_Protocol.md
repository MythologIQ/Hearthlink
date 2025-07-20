# 📘 SOP: Method Switch Protocol (Platinum+ Standard)

## 🎯 Objective

Ensure that any change in project methodology is performed with full awareness of risk, justification, impact, and agent delegation in compliance with traceability and governance standards.

---

## 🔄 Trigger Conditions

* Velocity decay over two sprints
* Feedback loop failure or user directive
* Forecast divergence or milestone miss
* Retrospective flag on methodology fit
* Human override via Alden

---

## 🧭 Process Stages

### 1. **Switch Proposal Triggered**

**Agent:** Mimic (if explicitly assigned) or user via Alden

* Method mismatch pattern detected
* Log in `method_switch_log.json` with justification and timestamp

### 2. **Forecast Impact Assessment**

**Agent:** Mimic + Risk Module

* Projected risk delta (positive, neutral, negative)
* Potential for rework, team disruption, velocity impact
* Log in `switch_impact.md`

### 3. **Present Options to User**

**Agent:** Alden

* Displays side-by-side model comparison:

  * Visual layout change
  * Risk overlays
  * Historical fit score per method

### 4. **Human Review & Confirmation**

**Agent:** Alden

* User confirms or rejects switch
* Decision and rationale saved to `methodology_report.md`

### 5. **Apply Switch**

**Agent:** Alden

* Overwrite `project_config.json` with new method
* Trigger UI transformation (Gantt → Kanban, Sprint board reset, etc.)

### 6. **Lock Reevaluation Delay**

* Prevent method switching again for 1–2 sprints (unless emergency)
* Set cooldown in `reeval_schedule.json`

---

## 🧠 Inclusion Rules

* No automatic switches—confirmation required
* Mimic must provide rationale, not verdict
* Vault maintains full switch history
* Risk model must include both short-term and long-term outcome
* Cognitive UX impact (neurodivergent-friendly logic shift) always factored

---

## 📎 Associated Files

* `method_switch_log.json`
* `switch_impact.md`
* `project_config.json`
* `methodology_report.md`
* `reeval_schedule.json`

---

## 🧠 Platinum+ Features

* Methodology Fit Score overlay with confidence delta
* Rationale Viewer linked to past project post-mortems
* Visual impact model (with optional toggles for effort, delay, risk, gain)
* Drift sensor triggers early review window if change rejection causes degradation
