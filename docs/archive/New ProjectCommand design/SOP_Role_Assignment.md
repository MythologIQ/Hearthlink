# 📘 SOP: Role Assignment (Platinum+ Standard)

## 🎯 Objective

Define strict, testable parameters for assigning system roles to personas, ensuring auditability, avoiding scope drift, and respecting hierarchical command delegation in Hearthlink.

---

## 🗝️ Role Assignment Principles

* No role is assumed without explicit assignment
* Alden is the only persona with authority to delegate
* Mimic, external agents, and plugins can only act within their assignment boundary
* Vault never executes, only observes and records
* Sentry does not interact with project logic

---

## 🔄 Assignment Lifecycle

### 1. **Define Role Need**

**Agent:** Alden

* Role request triggered by:

  * Project startup
  * Method shift
  * Retrospective finding
  * New capability added to system

### 2. **Request Scope Boundaries**

**Agent:** Alden

* Prompt user to define role requirements:

  * Task type (QA, scheduler, testing, planning, plugin execution)
  * Duration or cadence
  * Risk sensitivity

### 3. **Evaluate Available Agents**

**Agent:** Alden or logic plugin

* Filter available personas or tools based on:

  * Capability
  * Availability
  * Conflict-of-role

### 4. **Assign with Trace**

**Agent:** Alden

* Log result in `roles_log.json`:

```json
{
  "persona": "Mimic",
  "role": "QA tracker",
  "project": "VAULT",
  "start": "2025-07-15",
  "expires": "2025-07-30",
  "delegated_by": "Alden"
}
```

### 5. **Revoke / Expire Role**

**Agent:** Alden or task trigger

* Revocation: on violation or completion
* Expiry: auto-remove after term end, notify Vault

---

## 🔐 Safeguards

* Mimic cannot escalate scope without renewal
* Core may never assign roles
* All assigned roles are logged and timestamped
* Redundant roles across modules flagged by Vault
* Any attempt by Sentry to interact with assignment system logs warning

---

## 📎 Associated Files

* `roles_log.json`
* `project_config.json`
* `methodology_selector.py`

---

## 🧠 Platinum+ Enhancements

* Role Conflict Warning UI component
* Delegation Traceback map per project
* Role Cadence Tracker (heatmap of persona overuse)
* Role Expiry Notifier for Alden and Vault
