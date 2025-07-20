# 📘 Project Command: README (Platinum+ Standard)

## 🎯 Purpose

Project Command is the centralized project orchestration utility within the Hearthlink CORE module. It enables high-fidelity, AI-assisted program and sprint planning, methodology management, role delegation, and retrospective learning. Built to support multi-agent collaboration and human oversight, it adheres to strict traceability and evolving refinement standards.

## 🔐 Privileged Access

**Authorized Entities:**

* **Alden** (Primary orchestrator)
* **User** (Full control)
* **Mimic** (Only when explicitly delegated roles)

> No other agent or module may access or influence Project Command.

---

## 🧱 Architecture Overview

* **Backend:** Python (vault-driven, IPC-integrated)
* **Frontend:** React + Tailwind (Electron-rendered, togglable visual interfaces)
* **IPC Layer:** Event-channel bridge between UI and core logic
* **Vault Integration:** Full state persistence and changelog audit trail

---

## 🧩 Core Functional Units

### 1. **Methodology Evaluation Engine**

* *Inputs:* Project risk profile, stakeholder roles, constraints, exploration appetite
* *Outputs:* Ranked methodology recommendations
* *Delegated to:* Mimic (scoring), Alden (confirmation)
* *Visuals:* Color-coded methodology cards (effort, risk, return)

### 2. **Postmortem Learning System**

* *Captures:* Method switches, rationale, impact metrics, velocity history, blockers
* *Used by:* Mimic to adjust scoring confidence
* *Stored in:* `postmortem_reference.json`

### 3. **Role Assignment Manager**

* *Validates:* Required roles per methodology
* *Delegates:* Agents by role & expiration window
* *Tracks:* `roles_log.json` with expiry monitoring
* *Secure handoffs via:* Alden only

### 4. **Changelog Logger**

* *Tracks:* All system actions, timestamps, agents, components
* *File:* `project_command_changelog.json`

### 5. **Retrospective & Feedback Loop**

* *Includes:* Velocity trends, sentiment, adherence, blockers
* *Viewer UI:* Categorized feedback display with sentiment indicator

---

## 🔄 SOP Map

| SOP Name                             | Purpose                              |
| ------------------------------------ | ------------------------------------ |
| `SOP_Methodology_Evaluation.md`      | Evaluates best-fit methodology       |
| `SOP_Method_Switch_Protocol.md`      | Handles method switching logic       |
| `SOP_Retrospective_Cycle.md`         | Postmortem learning + scoring update |
| `Platinum_Method_Switch_Protocol.md` | Emergency/cooldown/override logic    |

---

## 📁 File Structure (MVP)

```
docs/
  SOP_Methodology_Evaluation.md
  SOP_Method_Switch_Protocol.md
  SOP_Retrospective_Cycle.md
  Platinum_Method_Switch_Protocol.md
config/
  project_schema.json
src/core/
  project_command.py
ui/components/
  MethodologySelector.js
  MethodCard.js
  RetrospectiveViewer.js
  *.css
__tests__/
  test_project_command.py
vault/
  project_command_changelog.json
  roles_log.json
  risk_profile.json
  postmortem_reference.json
  reeval_schedule.json
```

---

## 🧠 Integration Points

* **Alden:** Oversees and confirms all actions. Delegates roles.
* **Mimic:** Scoring, rationale, learning (only when delegated)
* **Vault:** Persistent state + JSON schema validation
* **Electron IPC:** UI communication and method switching

---

## ✅ MVP Readiness

Project Command is MVP-ready with:

* 🔒 Secure role and methodology delegation
* 📈 Visual selection and feedback loops
* 📜 Full auditability and changelog tracing
* 🧪 Unit-tested logic with scenario coverage
* 🎨 Fully styled UI matching CORE aesthetics

Next step: Deploy into Electron window as tab within **CORE > Command Console**.

> Status: **Locked & Operational**
> Prepared for immediate handoff to Claude Code for full system integration
