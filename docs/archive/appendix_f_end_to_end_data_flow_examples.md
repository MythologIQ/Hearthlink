# Appendix F – End-to-End Data Flow Examples

Platinum Grade: Five comprehensive, fully-annotated, and timestamped system flows, with all actors, logs, and boundaries.

---

## Table of Contents
1. Local Persona Task Creation (Direct Vault Flow, No Core)
2. AI Roundtable Session (Cross-Agent, Core-mediated, Sentry-logged)
3. Plugin Execution (Facilitator Agent, Synapse, Sentry, Core, Plugin, Vault Writeback)
4. Core Communal Memory Access (Agent → Core → Vault Communal, Multi-agent)
5. Security Incident & Override (Sentry intercept, user override, rollback)

---

### 1. Local Persona Task Creation (Direct Vault Flow)

**Actors:** User, Alden (persona/agent), Vault

**Steps:**
1. **User Input:**  
   T+0s – User enters a new task in Alden’s dashboard UI.
2. **Alden Task API Call:**  
   T+0.1s – Alden constructs a `CreateTask` API call, packages task data with metadata and timestamp.
3. **Direct Vault Write:**  
   T+0.2s – Alden calls `Vault.Create(slice="alden-tasks", payload=<encrypted task>)`. No Core involvement.
4. **Vault Response:**  
   T+0.3s – Vault stores encrypted record, returns confirmation.
5. **Alden UI Update:**  
   T+0.4s – Alden updates UI, shows task as added.
6. **Audit Log (Vault):**  
   T+0.5s – Vault logs the action in Alden’s persona audit log.  
   - Log entry:  
     `{ event: "create_task", persona: "alden", user_id: "user-001", timestamp: "...", details: { ... } }`

**Permission Boundaries:**
- Only Alden and Vault involved; no other agent or module has access.

---

### 2. AI Roundtable Session (Cross-Agent, Core-mediated, Sentry-logged)

**Actors:** User, Core (session orchestrator), Alden, Alice, Mimic (agents), Sentry (audit/log), Vault (communal memory)

**Steps:**
1. **Session Start:**  
   T+0s – User initiates a roundtable in the Core UI, selects agents.
2. **Core Context Setup:**  
   T+0.1s – Core creates a new session context (`session-5678`), logs initiation.
3. **Sentry Logs:**  
   T+0.2s – Sentry logs session start, agents present, user action.
4. **Agent Prompts:**  
   T+0.3s – Core sends session context and prompt to each agent via MCP.
5. **Agent Responses:**  
   T+0.4s–T+0.8s – Each agent independently processes, then submits responses via Core, using MCP.
6. **Moderation & Scoring:**  
   T+1.0s – Core collates, ranks, and moderates agent responses, assigns scores.
7. **Vault Communal Write:**  
   T+1.1s – Core writes the entire exchange (prompts, responses, scores) to Vault’s communal memory area.
8. **User Feedback:**  
   T+1.2s – User sees ranked responses and can review logs/agent performance.
9. **Audit Log:**  
   - Sentry logs each MCP exchange, all moderation/scoring events, and Vault write.

**Permission Boundaries:**
- All cross-agent exchanges go through Core.
- Sentry logs every message and moderation.
- Only communal memory accessed; local persona slices are untouched.

---

### 3. Plugin Execution (Facilitator Agent, Synapse, Sentry, Core, Plugin, Vault Writeback)

**Actors:** User, Facilitator Agent (e.g., Alden/CLI Agent), Core, Synapse (plugin manager), Sentry (security), Vault, External Plugin (e.g., Summarizer)

**Steps:**
1. **User Request:**  
   T+0s – User issues a natural language request to a facilitator agent (e.g., Alden or CLI Agent).
2. **Facilitator Prepares Request:**  
   T+0.1s – Facilitator agent interprets, packages context, and submits plugin execution request to Core.
3. **Core Plugin Request:**  
   T+0.2s – Core assembles MCP payload with context, submits to Synapse.
4. **Synapse Permission Check:**  
   T+0.3s – Synapse checks plugin manifest, user permission, risk/benchmark score.
5. **Sentry Logs:**  
   T+0.4s – Sentry logs plugin execution request.
6. **Plugin Execution:**  
   T+0.5s – Synapse launches plugin in sandbox, passes MCP payload.
7. **Plugin Response:**  
   T+1.0s – Plugin returns output, risk/exec summary, audit record.
8. **Vault Writeback:**  
   T+1.1s – Core (or plugin, if authorized) writes plugin result to Vault (e.g., session summary to communal memory).
9. **User Notification:**  
   T+1.2s – User receives result, can view plugin log.
10. **Audit Log:**  
   - Sentry logs all Synapse actions, plugin execution, Vault writeback.

**Permission Boundaries:**
- Plugin sandboxed via Synapse, cannot access Vault directly unless manifest permits.
- All events logged by Sentry.

---

### 4. Core Communal Memory Access (Multi-agent Flow)

**Actors:** User, Agent(s) (e.g., Alice), Core, Sentry, Vault (communal)

**Steps:**
1. **User Enables Communal Memory:**  
   T+0s – User enables/requests communal memory access for specific agents.
2. **Agent Request:**  
   T+0.1s – Agent prepares MCP to read/write to communal memory, sends to Core.
3. **Core Validation:**  
   T+0.2s – Core validates request, session, and user approval.
4. **Sentry Audit:**  
   T+0.3s – Sentry logs access intent.
5. **Vault Communal Access:**  
   T+0.4s – Core relays request to Vault; Vault enforces permission.
6. **Agent Updates:**  
   T+0.5s – Agent receives data or writes update.
7. **User Control:**  
   T+0.6s – User can view/approve all access and edit communal memory.
8. **Audit Log:**  
   - Every step and data change logged by Sentry and in communal audit trail.

**Permission Boundaries:**
- Only agents with explicit user-approved permission access communal memory.
- Local persona data remains isolated.

---

### 5. Security Incident & Override (Sentry intercept, user override, rollback)

**Actors:** Sentry (monitoring), User/Admin, Affected Module (e.g., plugin or agent), Vault, Core/Synapse (as context)

**Steps:**
1. **Anomaly Detected:**  
   T+0s – Sentry detects suspicious action (e.g., plugin resource spike).
2. **Incident Logged:**  
   T+0.1s – Sentry logs event, flags user/admin, pauses affected process.
3. **User Notification:**  
   T+0.2s – User receives alert, incident report, recommended action.
4. **User/Admin Decision (Final Authority):**  
   T+0.5s – User chooses to override (continue anyway) or terminate process.
   - **If override:** Sentry logs override, resumes process, escalates monitoring. No action is irreversible without user consent.
   - **If terminate:** Sentry force-kills process, quarantines changes. Vault rolls back to last safe state if write was involved. User can always restore/rollback via UI or admin panel.
5. **Audit & Recovery:**  
   T+0.6s–1.0s – Full incident trace, override flag, and recovery log written to Sentry audit and Vault.

**Permission Boundaries:**
- Sentry cannot be bypassed; all overrides or rollbacks are logged and surfaced to user.
- **User always has final authority on all actions.**

---

**All flows are explicit, timestamped, and include memory/permission boundaries and audit steps. Appendix F is now platinum standard and ready for review or direct implementation.**

