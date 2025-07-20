# 📘 SOP: Methodology Evaluation

## 🎯 Objective

Establish a rigorous, repeatable process for selecting, validating, and adapting the project methodology using Alden-directed decision logic and Mimic-executed analytical support.

---

## 🧩 Trigger Conditions

* New project initialization
* Major project phase shift
* Metrics below performance thresholds (velocity, blocker count, failure rates)
* Explicit user feedback or directive via Alden

---

## 🔁 Process Steps

### 1. **Capture Intent**

**Agent:** Alden

* Engage user to understand:

  * Project scope
  * Constraints (time, cost, regulation)
  * Stakeholder roles
  * Appetite for exploration vs reliability
* Save as `risk_profile.json`

### 2. **Delegate Selection Agent**

**Agent:** Alden

* Assign `method_selector` role to Mimic or plugin

### 3. **Score Methodologies**

**Agent:** Mimic or tool

* Input: risk profile + preferences
* Output: ranked method list with pros/cons + complexity score

### 4. **Present Recommendation**

**Agent:** Alden

* Show methodology chart + risk overlays to user
* Log decision in `methodology_report.md`

### 5. **Implement Chosen Model**

**Agent:** Alden

* Inject into project config:

```json
"methodology": "kanban",
"config": {...}
```

* Trigger any UI view mode switches (e.g. from Gantt to Kanban)

### 6. **Schedule Reevaluation Date**

**Agent:** Alden

* Timestamp stored in `reeval_schedule.json`

---

## 📐 Inclusion Checklist

* ✅ Recommends both traditional and modern hybrid methods
* ✅ Aligns with security roles (e.g., PRINCE2 phase gates)
* ✅ Accounts for neurodiverse working styles (e.g., Kanban WIP)
* ✅ Always auditable (saved to Vault)
* ✅ Human-first, AI-enhanced

---

## 📎 Associated Files

* `risk_profile.json`
* `methodology_selector.py`
* `methodology_report.md`
* `reeval_schedule.json`
* `project_config.json`

---

## 🔄 Cycle Duration

* Initial: project start
* Reevaluation: every 2–4 weeks (sprint cadence)
* Emergency: triggered by severe drift or failure signal

---

## 🧠 Notes

* Mimic never executes without assignment
* Alden always confirms final methodology choice
* Vault logs rationale and method history per project ID
* Future integration: external tools may be queried for industry-specific recommendations
