# 📘 SOP: Project Creation (Platinum+ Standard)

## 🎯 Objective

Define the complete, traceable protocol for initiating a new project in Hearthlink, respecting Alden's authority, system modularity, and AI-human transparency.

---

## 🔑 Initiation Criteria

* New system feature or tool to be scoped
* Cross-module development cycle required
* New customer/partner engagement cycle
* Internal performance initiative requiring milestone tracking

---

## 🧭 Process Overview

### 1. **Initiate Intake with Alden**

**Agent:** Alden

* Prompt user to describe:

  * Project purpose
  * Business or operational outcome
  * External constraints (deadline, budget, compliance)
  * Desired personas (if known)
* Output saved to: `project_intake.json`

### 2. **Assign Methodology Selector**

* Launch SOP: Methodology Evaluation

### 3. **Define Metadata**

**Agent:** Alden

```json
{
  "id": "PROJECT_ID",
  "program": "CORE",
  "priority": "high",
  "status": "active",
  "lead_agent": "Alden",
  "methodology": "to be set",
  "risk_profile": "moderate"
}
```

* Logged in: `projects/projects.json`

### 4. **Create Sprint or Milestone Scaffolding**

**Agent:** Mimic (if explicitly assigned)

* Auto-generate 2-week sprint blocks or milestone stages
* Populate `sprints.json` and `milestones.json`

### 5. **Link Vault Channel**

**Agent:** Core/Vault sync

* Dedicated log location created under `/vault/projects/{project_id}`

### 6. **Activate Visual View + Delegation Fields**

**Agent:** UI toggle

* Show method-specific UI modules
* Populate “Assigned To” fields for initial phase

---

## 🔁 Continuous Linkages

* Intake updates sync to metadata
* Risk flags influence planning UI in real time
* Vault monitors for drift between plan and task execution

---

## 📎 Associated Files

* `project_intake.json`
* `projects/projects.json`
* `projects/sprints.json`
* `vault/projects/{id}/`
* `project_config.json`

---

## 🧠 Special Considerations

* No project may exist without Alden authorization
* Sentry never interacts with project scaffolding
* Mimic may not auto-assign itself unless instructed
* All project creation triggers retrospective eligibility
