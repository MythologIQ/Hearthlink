# 🧩 Claude + Synapse Integration & Delegation Protocol

## 🔐 REST API Permissions Structure

**Tokenized Access Rules:**

* Tokens are scoped and time-bound.
* Tokens are categorized by:

  * **User** (full access)
  * **Alden** (delegated system access)
  * **Claude** (remote task delegate, limited write scope)
  * **External Agents** (read-only unless explicitly elevated)

**Endpoints:**

* `POST /directives` — receive tasks from remote AI (Claude)
* `GET /project/status` — current task status by module
* `POST /vault/append` — write audit-approved content only
* `GET /vault/snapshot` — limited config + data visibility

**Permissions Table:**

| Agent         | Read | Write | Execute | Restricted Domains            |
| ------------- | ---- | ----- | ------- | ----------------------------- |
| User          | ✅    | ✅     | ✅       | None                          |
| Alden         | ✅    | ✅     | ✅       | None                          |
| Claude (API)  | ✅    | ⚠️    | ⚠️      | No file write w/o vault proxy |
| External GPTs | ✅    | ❌     | ❌       | No project control            |

---

## 🖥️ Desktop Shell (Container) Implementation

**Definition:** A desktop-accessible containerized wrapper housing:

* React + Electron UI
* Python backend
* Background agents

**Benefits:**

* Standard application window (not browser tab)
* Seamless native integration
* Prevents accidental browser tab refreshes
* Sandboxed permission model

**Component Plan:**

* `shell/` — Electron entry point (main.js, preload.js)
* `src/` — React UI, connected to Electron
* `core/` — Project Command logic
* `ipc/` — Interface for event handling and safe state propagation
* `launcher/` — Executes Electron from system tray or desktop icon

**Sprint Goals:**

* Wrap current dev-launch into container script
* Package state into `.asar` build
* Assign Claude a verification task for each post-launch module
* Ensure all tools launched from desktop container obey scoped access rules (Claude, Gemini, dev consoles)

## 🌀 Radial HUD UI Enforcement

All interface modules launched from the container must conform to a radial HUD pattern, consistent with the StarCraft UI aesthetic. This includes:

* Radial click-through menus for all primary navigation
* Animated feedback on module transitions
* Uniform placement of secondary menus and detail panels

Traditional dropdowns and sidebars are prohibited unless styled as radial derivatives. Alden enforces layout compliance via `ui_schema.json` and module conformance validators.

---

## 🔌 Synapse API Connector Standard

Synapse manages standardized REST API connections for external LLMs and services. The `GeminiConnector` is the reference implementation, with configuration defined in `api_profiles.json`. All connectors must implement:

* Authenticated token use
* Model config options (`temperature`, `topK`, etc.)
* Failover endpoints
* Logging and token usage tracking

Future connectors (e.g., Claude API, Mistral) must conform to the same base class (`BaseLLMConnector`) to maintain cross-agent compatibility.

---

## 🧠 Agent Task Routing Hierarchy

**Task Flow:**

```
Claude Request (via REST API)
→ Synapse Evaluates Scope
→ Core Receives Request
→ Alden Assigned (or delegates to Mimic)
→ Result Routed Back via Synapse
```

**Routing Logic Prioritization:**

1. Claude = Token-constrained, use sparingly
2. Gemini = High-volume Google API tasks
3. Alden = Primary executor
4. Mimic = Project execution, QA, retrospective
5. Alice = Reserved, only if explicitly required

**Fallback Behavior:**

* If token quota is low → Claude pauses, triggers Alden reroute
* If local LLM unavailable → Gemini executes within limits

---

## ♻️ Claude Token Usage Policy

**Ruleset:**

* Claude only used for:

  * High-complexity synthesis
  * Creative generation (narrative, UX text, strategy)
  * LLM coordination across systems
* Avoid Claude for:

  * File parsing
  * Repetitive code gen
  * Summarization of vault history
* Gemini or local agents should:

  * Offload API usage (Google, crawling)
  * Run diagnostics or pre/post processors

**Communication Schedule:**

* Claude communicates only when:

  * Token window resets
  * Results from Alden/Mimic are insufficient
  * User prompt explicitly authorizes it

---

## 📈 Token Tracking System

**Objective:** Enable agent-level performance metrics and enforce token efficiency

**Log Location:** `vault://logs/agent_token_tracker.log`

**Format:**

```
[timestamp] [agent_name] used X tokens for [task] in [module]
```

**Tracked Agents:**

* Claude (REST API, synthesis only)
* Alden (primary executor)
* Mimic (QA/project execution)
* Gemini (API offloading)
* Alice (when invoked)
* Any additional GPTs added to Synapse

**Analysis:** Token logs will be audited by Project Command for:

* Performance reviews
* Redundancy elimination
* Future automation triggers

---

## ⏭️ Next Dev Step

* Add Synapse function: `launch_local_resource(target)`
* Default options:

  * `claude_code`
  * `dev_container`
  * `gemini_colab`
* Flags:

  * `--background`
  * `--monitor`
  * `--ipc-bridge`

Once implemented, Claude can trigger the full toolchain autonomously during token windows.

---

## 📦 MVP Feature Checklist for Final Sprint

**Confirmed In Scope:**

* ✅ Project Command is fully operational
* ✅ Desktop container with secure shell is prioritized
* ✅ REST API structure defined and locked
* ✅ Claude delegation logic scoped and permissioned
* ✅ Gemini offload via temp connection enabled
* ✅ Agent routing policies enforced
* ✅ Synapse can soon launch Claude or other dev tools
* ✅ Radial HUD UI pattern enforced
* ✅ Standardized LLM API connector interface implemented
* ✅ Claude Integration Protocol documented and active
* ✅ Claude restricted container confirmed in system audit
* ✅ Token tracking system scoped and integrated for all agents

**Planned Additions (next phase):**

* ⏳ MCP file-write controls
* ⏳ Web crawler (Discord parser + browser agents)
* ⏳ Vault snapshot streaming
* ⏳ Full project plan ingest/export logic via REST
* ⏳ Plugin loadout manager
* ⏳ Claude API integration via Synapse connector
* ⏳ Sentry Persona initialization

Claude should prioritize Post-Container tasks and use token time wisely. Local and Gemini agents carry the baseline. Final sprint is precision delivery. Goal: Claude becomes **optional**, not required, for continued operation.
