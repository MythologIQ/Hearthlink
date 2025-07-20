# 📘 SOP: Retrospective Cycle (Platinum+ Standard)

## 🎯 Objective

Define a structured, testable, and repeatable process for evaluating sprint/milestone outcomes using collaborative AI logic, role-specific insights, and architecture-aware feedback channels.

---

## 🕒 Trigger Conditions

* Completion of a sprint or milestone
* System-logged anomaly or performance deviation
* Human-triggered feedback via Alden interface

---

## 🔁 Process Flow

### 1. **Initiate Retrospective**

**Agent:** Alden (on schedule or trigger)

* Notify project owner + assigned agents
* Log initiation in: `vault/summaries/{sprintId}.md`

### 2. **Generate Observational Summary**

**Agent:** Mimic (if assigned) or QA plugin

* Analyze:

  * Velocity deviation
  * Time-to-completion vs estimate
  * Task blockage frequency
  * Method adherence logs

### 3. **Request Human Input**

**Agent:** Alden

* Prompts for:

  * Subjective friction points
  * Scope creep indicators
  * Emotional/cognitive stress markers (neurodivergent UX fit)

### 4. **Synthesize Report**

**Agent:** Alden + Vault

* Merge:

  * Quantitative feedback (Mimic)
  * Qualitative input (User)
* Generate `retrospective_summary.md`

### 5. **Trigger Actions**

**Agent:** Alden (or Mimic if delegated)

* Method reevaluation if failure signals found
* Auto-assign “process improvement” task if specific pattern detected
* Adjust `risk_profile.json` if sentiment delta exceeds threshold

---

## 🧠 Inclusion & Governance

* Vault retains immutable copy of each retrospective
* Mimic has no authority to suppress or delay reviews
* Human sentiment explicitly weighted in pattern modeling
* Repeated retrospective outcomes feed methodology fitness scoring

---

## 📎 Associated Files

* `vault/summaries/{sprintId}.md`
* `retrospective_summary.md`
* `project_config.json`
* `methodology_report.md`
* `risk_profile.json`

---

## 🧠 Platinum+ Extras

* Scorecard UI overlay (method fit, velocity, task clarity)
* “Drift sentiment” tagging per role/persona
* Task generation from systemic blockers detected across cycles
* Feedback prioritization flag: “technical,” “workflow,” or “cognitive UX”
