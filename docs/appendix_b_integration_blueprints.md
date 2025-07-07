# Appendix B: Integration Blueprints

## 1. High-Level Hearthlink Ecosystem Blueprint

```
+-------------------------------------------------------------+
|                          User                               |
+-------------------------------------------------------------+
         |                    |                     |
         v                    v                     v
+----------------+   +------------------+   +-------------------+
|   Agent UIs    |   |   Settings/Logs  |   |  Plugin/Endpoint  |
| (Alden, Alice, |   |  (All Modules)   |   |    Manager        |
|  Mimic, Sentry)|   +------------------+   +-------------------+
+----------------+           |                    |
         |                   v                    v
         +---------------------------------------------------+
         |                     Core                          |
         +---------------------------------------------------+
            |          |           |          |         |
            v          v           v          v         v
         Alden      Alice       Mimic     Sentry    Synapse
            |          |           |          |         |
            +----------+-----------+----------+---------+
                                |
                            [Vault]
                                |
                  [Persona Slices, Shared Memory, Audit Logs]
```

**Key:**

- All agent-to-agent and agent-to-external flows are mediated by Core.
- Sentry continuously monitors and can override/block any event.
- Synapse is the only external gateway—all plugins, APIs, web access pass through it.
- Vault stores all persistent memory, persona slices, and audit logs; access is strictly by agent context and user mediation.

---

## 2. Alden — Platinum Integration Blueprint

**UI Components & Triggers:**

- `/alden` dashboard route (Next.js/React)
- Features: journaling, growth, feedback, habits
- **UI Event Methods:**
  - `onTaskSubmit(task: TaskPayload): Promise<void>`
  - `onFeedback(feedback: FeedbackPayload): Promise<void>`
  - `onCorrection(correction: CorrectionPayload): Promise<void>`
  - `onExport(): Promise<ExportedMemory>`
  - `onSessionReview(sessionId: string): Promise<SessionLog[]>`

**API Contracts:**

- `POST /api/vault/persona-memory/alden`
  - *Payload*: `{ ...AldenPersonaMemory }`
  - *Success*: `201 Created`, `{ status: "ok", recordId: string }`
  - *Errors*: `401 Unauthorized`, `422 Validation`, `500 ServerError`
- `GET /api/vault/persona-memory/alden/export`
  - *Response*: `{ records: AldenPersonaMemory[], auditLog: VaultAuditEvent[] }`
  - *Headers*: `Authorization: Bearer <JWT>`
- `PATCH /api/vault/persona-memory/alden/:recordId`
  - *Payload*: `{ correction, updateFields }`
  - *Response*: `200 OK`, `{ status: "updated", recordId: string }`
  - *Conflict*: `409 VersionMismatch`
- `GET /api/core/session/:id/log`
  - *Response*: Session logs, feedback, audit (see schema below)
  - *Errors*: `404 NotFound`, `403 Forbidden`

**Memory Slice Sample (AldenPersonaMemory):**

```
json
```

CopyEdit

`{ "persona_id": "alden", "user_id": "user-123", "schema_version": "1.0.0", "traits": { "openness": 83, "conscientiousness": 90, "extraversion": 67, "agreeableness": 95, "emotional_stability": 78 }, "habits": [ { "habit": "journal", "streak": 12, "last_entry": "2025-07-06T10:00Z" } ], "motivation_style": "supportive", "trust_level": 0.87, "learning_agility": 0.95, "feedback_responsiveness": 0.92, "correction_events": [ { "type": "positive", "timestamp": "..." } ], "engagement_metrics": { "session_count": 37, "active_days": 22 }, "audit_log": [ /* VaultAuditEvent[] */ ] }`

**Core Flows:**

- `POST /api/core/session` (with Alden in participants)
- `PATCH /api/core/session/:id/participants` (add/remove)
- Alice feedback via `PATCH /api/vault/persona-memory/alden/:recordId`
- Export session via `GET /api/core/session/:id/log`

**Sentry Integration:**

- All audit, compliance, and plugin events: `POST /api/sentry/audit`
- Risk threshold event: Sentry UI warning + `POST /api/sentry/override` (requires reason, logs fallout)

**Synapse Integration:**

- Plugins: `POST /api/synapse/plugin/register` + approval + `POST /api/synapse/plugin/:id/execute`
- Plugin results returned via Core to Alden (`PATCH /api/core/session/:id/log`)
- Benchmarks: `POST /api/synapse/benchmark/run`

**Vault Enforcement:**

- No cross-slice access without explicit user-approved Core handshake
- All exports/imports are user-initiated, version-checked, and audit-logged

**Audit, Export, and Error:**

- All actions timestamped, user/audit visible, and exportable (JSON, CSV)
- Error handling: status codes surfaced, actionable UI modals, retry logic
- User can review/annotate/delete any memory record

**Security/Compliance:**

- JWT or session token required on all API requests
- All endpoints return audit event on every mutation
- Acceptance criteria: All user changes are audit-surfaced in <2s, plugin use and risk are always visible and overridable

**Sample Audit Log Event:**

```
json
```

CopyEdit

`{ "event_id": "audit-20250706-001", "source": "alden", "action": "memory_patch", "user_id": "user-123", "record_id": "mem-45819", "status": "success", "timestamp": "2025-07-06T10:15:00Z" }`

---

## 3. Alice — Platinum Integration Blueprint

**UI Components & Triggers:**

- `/alice` dashboard (React/Next.js route)
- Features: communication analysis, user “teach” mode, cadence/tone/sentiment trends, self-support/critique tracking
- **UI Event Methods:**
  - `onAnalyze(input: string): Promise<AnalysisResult>`
  - `onFeedbackPrefChange(preference: FeedbackPref): Promise<void>`
  - `onTeach(teachableEvent: TeachEvent): Promise<void>`
  - `onExport(): Promise<ExportedMetaData>`
  - `onSessionReview(sessionId: string): Promise<SessionLog[]>`

**API Contracts:**

- `POST /api/vault/persona-memory/alice`
  - *Payload*: `{ ...AlicePersonaMeta }`
  - *Success*: `201 Created`, `{ status: "ok", recordId: string }`
  - *Errors*: `401 Unauthorized`, `422 Validation`, `500 ServerError`
- `GET /api/vault/persona-memory/alice/export`
  - *Response*: `{ records: AlicePersonaMeta[], auditLog: VaultAuditEvent[] }`
  - *Headers*: `Authorization: Bearer <JWT>`
- `PATCH /api/vault/persona-memory/alice/:recordId`
  - *Payload*: `{ teachableEvent, updateFields }`
  - *Response*: `200 OK`, `{ status: "updated", recordId: string }`
  - *Conflict*: `409 VersionMismatch`
- `GET /api/core/session/:id/log`
  - *Response*: session logs, feedback, audit (see schema)
  - *Errors*: `404 NotFound`, `403 Forbidden`

**Meta Slice Sample (AlicePersonaMeta):**

```
json
```

CopyEdit

`{ "persona_id": "alice", "user_id": "user-123", "schema_version": "1.0.0", "cadence": 52, "sentiment": 32, "formality": 62, "emotional_cue": { "agitation": 2, "excitement": 4 }, "cog_distortion_count": 0, "self_talk_ratio": 0.75, "avoidance_count": 1, "feedback_pref": "affirmation", "unmet_needs": ["clarity"], "teachable_events": [{ "type": "correction", "timestamp": "..." }], "audit_log": [ /* VaultAuditEvent[] */ ] }`

**Core Flows:**

- `POST /api/core/session` (Alice as participant)
- `PATCH /api/core/session/:id/participants` (add/remove Alice)
- Alice provides feedback to Alden via `PATCH /api/vault/persona-memory/alden/:recordId` (only by user mediation)
- Export session via `GET /api/core/session/:id/log`

**Sentry Integration:**

- All meta/behavioral audit events: `POST /api/sentry/audit`
- Sentry warnings/overrides: `POST /api/sentry/override` (requires reason, logs fallout)

**Synapse Integration:**

- Behavioral plugins: `POST /api/synapse/plugin/register` (manifest, user approval)
- Plugin execution: `POST /api/synapse/plugin/:id/execute`, results logged and routed via Core
- Benchmarks: `POST /api/synapse/benchmark/run`

**Vault Enforcement:**

- Only meta-data and flags stored (no raw transcript)
- All exports/imports are user-initiated, version-checked, audit-logged

**Audit, Export, and Error:**

- All actions timestamped, audit/export visible (JSON, CSV)
- Error handling: status surfaced, UI modals, retry logic
- User can review/annotate/delete meta-communication records

**Security/Compliance:**

- JWT or session token required for API
- Every endpoint returns audit event on mutation
- Acceptance: All user/corrected meta-data changes surfaced in <2s; plugin use/risk always visible and overridable

**Sample Audit Log Event:**

```
json
```

CopyEdit

`{ "event_id": "audit-20250706-101", "source": "alice", "action": "meta_patch", "user_id": "user-123", "record_id": "meta-84512", "status": "success", "timestamp": "2025-07-06T10:25:00Z" }`

---

## 4. Mimic — Platinum Integration Blueprint

**UI Components & Triggers:**

- `/mimic` dashboard (React/Next.js route)
- Features: persona creation, persona analytics, performance review, persona archiving/forking/merging, user-driven curation
- **UI Event Methods:**
  - `onPersonaCreate(personaPayload: PersonaSeed): Promise<void>`
  - `onPersonaUpdate(personaId: string, update: Partial<PersonaProfile>): Promise<void>`
  - `onPerformanceReview(personaId: string): Promise<PersonaAnalytics>`
  - `onFork(personaId: string): Promise<void>`
  - `onMerge(sourcePersonaId: string, targetPersonaId: string): Promise<void>`
  - `onArchive(personaId: string): Promise<void>`
  - `onExport(personaId: string): Promise<ExportedPersonaData>`

**API Contracts:**

- `POST /api/vault/persona-memory/mimic/:personaId`
  - *Payload*: `{ ...MimicPersonaProfile }`
  - *Success*: `201 Created`, `{ status: "ok", recordId: string }`
  - *Errors*: `401 Unauthorized`, `422 Validation`, `500 ServerError`
- `PATCH /api/vault/persona-memory/mimic/:personaId/:recordId`
  - *Payload*: `{ updateFields }`
  - *Response*: `200 OK`, `{ status: "updated", recordId: string }`
  - *Conflict*: `409 VersionMismatch`
- `GET /api/vault/persona-memory/mimic/:personaId/export`
  - *Response*: `{ profile: MimicPersonaProfile, analytics: PersonaAnalytics, auditLog: VaultAuditEvent[] }`
  - *Headers*: `Authorization: Bearer <JWT>`
- `POST /api/vault/persona-memory/mimic/:personaId/fork`
  - *Payload*: `{ fromPersonaId, newPersonaSeed }`
  - *Response*: `201 Created`, `{ status: "forked", newPersonaId: string }`
- `POST /api/vault/persona-memory/mimic/:personaId/merge`
  - *Payload*: `{ sourcePersonaId, targetPersonaId }`
  - *Response*: `200 OK`, `{ status: "merged", resultPersonaId: string }`
- `POST /api/vault/persona-memory/mimic/:personaId/archive`
  - *Response*: `200 OK`, `{ status: "archived", personaId: string }`
- `GET /api/core/session/:id/log`
  - Session logs, persona-specific analytics

**Persona Profile Sample (MimicPersonaProfile):**

```
json
```

CopyEdit

`{ "persona_id": "mimic-542", "user_id": "user-123", "schema_version": "1.0.0", "task_domain": "coding", "experience_score": 0.85, "persona_traits": { "precision": 92, "creativity": 78, "responsiveness": 87 }, "performance_metrics": { "tasks_completed": 112, "positive_feedback": 71, "negative_feedback": 8, "persona_performance_score": 0.91 }, "optimization_events": [ { "event": "forked", "timestamp": "..." }, { "event": "performance_tuned", "timestamp": "..." } ], "audit_log": [ /* VaultAuditEvent[] */ ] }`

**Core Flows:**

- `POST /api/core/session` (add/remove Mimic personas as participants)
- Fork/merge/archive are mediated by user through Core
- Performance review/score is always visible to user in session logs

**Sentry Integration:**

- Persona performance, boundary, or compliance events trigger `POST /api/sentry/audit`
- Risk escalation triggers Sentry warning; user override at `POST /api/sentry/override`

**Synapse Integration:**

- Any external plugin logic, persona mirroring, or performance extension triggers
  - `POST /api/synapse/plugin/register` (user approval required)
  - `POST /api/synapse/plugin/:id/execute` (results via Core to Mimic)
  - Sentry benchmarks via `POST /api/synapse/benchmark/run`

**Vault Enforcement:**

- Every persona’s memory/profile is a discrete encrypted slice
- No cross-persona access; all forks/merges user-driven and fully logged

**Audit, Export, and Error:**

- All persona changes, performance updates, and forks/merges are timestamped, audit-logged, and exportable
- Errors surfaced via status codes, actionable UI
- User can review/annotate/archive any persona

**Security/Compliance:**

- JWT/session token required
- Audit log required for all persona mutation
- Acceptance: All persona changes and optimizations audit-surfaced in <2s; plugin/extension use is always logged and overridable

**Sample Audit Log Event:**

```
json
```

CopyEdit

`{ "event_id": "audit-20250706-201", "source": "mimic", "action": "persona_fork", "user_id": "user-123", "record_id": "mimic-542", "status": "success", "timestamp": "2025-07-06T11:05:00Z" }`

---

## 5. Vault — Platinum Integration Blueprint

**UI Components & Triggers:**

- `/vault` dashboard (React/Next.js route)
- Features: per-persona memory management, topic/frequency/relevance filtering, audit log review, export/import, privacy control
- **UI Event Methods:**
  - `onViewPersona(personaId: string): Promise<PersonaRecord[]>`
  - `onExport(personaId?: string): Promise<ExportedVaultData>`
  - `onPurge(personaId?: string): Promise<void>`
  - `onEditRecord(personaId: string, recordId: string, patch: Partial<PersonaRecord>): Promise<void>`
  - `onAuditLog(): Promise<VaultAuditEvent[]>`
  - `onMigrateSchema(newVersion: string): Promise<MigrationResult>`
  - `onHandshake(remoteSystemId: string): Promise<HandshakeResult>`

**API Contracts:**

- `POST /api/vault/persona-memory/:personaId`
  - *Payload*: `{ ...PersonaRecord }`
  - *Success*: `201 Created`, `{ status: "ok", recordId: string }`
  - *Errors*: `401 Unauthorized`, `422 Validation`, `500 ServerError`
- `PATCH /api/vault/persona-memory/:personaId/:recordId`
  - *Payload*: `{ patch }`
  - *Response*: `200 OK`, `{ status: "updated", recordId: string }`
  - *Conflict*: `409 VersionMismatch`
- `GET /api/vault/persona-memory/:personaId/export`
  - *Response*: `{ records: PersonaRecord[], auditLog: VaultAuditEvent[] }`
  - *Headers*: `Authorization: Bearer <JWT>`
- `POST /api/vault/persona-memory/:personaId/purge`
  - *Response*: `200 OK`, `{ status: "purged", personaId: string }`
- `GET /api/vault/audit`
  - *Response*: `VaultAuditEvent[]`
- `POST /api/vault/migrate`
  - *Payload*: `{ fromVersion, toVersion }`
  - *Response*: `200 OK`, `{ status: "migrated", from: string, to: string }`
- `POST /api/vault/handshake`
  - *Payload*: `{ remoteSystemId, exportFields }`
  - *Response*: `HandshakeResult`

**Persona Memory Slice Sample (PersonaRecord):**

```
json
```

CopyEdit

`{ "persona_id": "alden", "user_id": "user-123", "schema_version": "1.0.0", "fields": { /* persona-specific schema */ }, "audit_log": [ /* VaultAuditEvent[] */ ] }`

**Integration Flows:**

- Each persona’s memory is an isolated, encrypted slice—no cross-slice access except via Core with user mediation
- All exports/imports, migrations, and purges are user-triggered and fully audit-logged
- Multi-system handshakes create new isolated DBs and require strict schema validation and user confirmation

**Sentry Integration:**

- All access, mutation, export, and purge events: `POST /api/sentry/audit`
- Any schema anomaly, failed migration, or cross-slice attempt triggers Sentry warning (can be overridden by user with reason)

**Synapse Integration:**

- Plugin/external requests for data: routed via Synapse and require explicit user approval; Vault never directly serves external requests

**Core Integration:**

- All collaborative or shared memory requests go through Core’s session engine; user selects what data, if any, is exposed

**Audit, Export, and Error:**

- All memory actions are timestamped, exportable as JSON or CSV
- Errors (version, schema, unauthorized) return explicit codes, user modals
- Migration/dry-run tools allow for rollback or manual intervention

**Security/Compliance:**

- AES-256+ encrypted at rest, never leaves system except on user export
- JWT/session token required on all API requests
- Audit log cannot be edited or purged; only exported

**Sample Audit Log Event:**

```
json
```

CopyEdit

`{ "event_id": "vault-audit-20250706-001", "source": "vault", "action": "persona_export", "user_id": "user-123", "persona_id": "alden", "status": "success", "timestamp": "2025-07-06T12:01:00Z" }`

---

## 6. Core — Platinum Integration Blueprint

**UI Components & Triggers:**

- `/core` dashboard (React/Next.js route)
- Features: session/room management, agent addition/removal, breakout creation, live feed, export/log review
- **UI Event Methods:**
  - `onSessionCreate(topic: string, participants: Participant[]): Promise<SessionResult>`
  - `onAgentAdd(sessionId: string, agentId: string): Promise<void>`
  - `onAgentRemove(sessionId: string, agentId: string): Promise<void>`
  - `onBreakoutCreate(sessionId: string, topic: string, agents: string[]): Promise<BreakoutResult>`
  - `onLogExport(sessionId: string): Promise<ExportedSessionLog>`
  - `onSessionEnd(sessionId: string): Promise<void>`
  - `onVerbosityChange(sessionId: string, verbosity: LiveFeedVerbosity): Promise<void>`

**API Contracts:**

- `POST /api/core/session`
  - *Payload*: `{ topic, participants }`
  - *Success*: `201 Created`, `{ sessionId: string, status: "ok" }`
  - *Errors*: `401 Unauthorized`, `422 Validation`, `500 ServerError`
- `PATCH /api/core/session/:id/participants`
  - *Payload*: `{ add?: string[], remove?: string[] }`
  - *Response*: `200 OK`
  - *Errors*: `404 NotFound`, `409 Conflict`
- `POST /api/core/session/:id/breakout`
  - *Payload*: `{ topic, participants }`
  - *Success*: `201 Created`, `{ breakoutId: string }`
- `GET /api/core/session/:id/log`
  - *Response*: `{ log: SessionEvent[], audit: AuditEvent[] }`
- `PATCH /api/core/session/:id/settings`
  - *Payload*: `{ liveFeedSettings: LiveFeedSettings }`
  - *Response*: `200 OK`
- `DELETE /api/core/session/:id`
  - *Response*: `200 OK`, `{ status: "archived" }`

**Session Schema Sample:**

```
json
```

CopyEdit

`{ "session_id": "core-022", "topic": "AI Collaboration", "created_by": "user-123", "created_at": "2025-07-06T13:00:00Z", "participants": ["alden", "alice", "bob-research-bot"], "breakouts": [ { "breakout_id": "core-022-b1", "topic": "Plugin Policy", "participants": ["alice", "bob-research-bot"], "log": [] } ], "live_feed_settings": { "verbosity": "default" }, "audit_log": [] }`

**Integration Flows:**

- All agent additions/removals, breakouts, and context changes are user-triggered and logged
- External agents (via Synapse) only join/leave with user approval and are logged
- All session and breakout events are timestamped and fully exportable

**Sentry Integration:**

- All session, participant, breakout, and export events: `POST /api/sentry/audit`
- Any anomaly or policy violation triggers Sentry warning/override (`POST /api/sentry/override`)

**Synapse Integration:**

- Any plugin or external agent involvement triggers `POST /api/synapse/plugin/register` and approval
- All traffic/engagement is logged and available for session review

**Vault Enforcement:**

- No session/room data is shared with personas except via user command and Vault mediation
- All logs and session exports are audit-logged

**Audit, Export, and Error:**

- All actions timestamped, visible, and exportable (JSON, CSV)
- User can review, annotate, or export any session or breakout

**Security/Compliance:**

- JWT/session token required for all API
- Every endpoint generates audit event
- Acceptance: All live changes reflected to user in <2s, all agent actions and breakouts are fully audit-logged and exportable

**Sample Audit Log Event:**

```
json
```

CopyEdit

`{ "event_id": "core-audit-20250706-001", "source": "core", "action": "session_create", "user_id": "user-123", "session_id": "core-022", "status": "success", "timestamp": "2025-07-06T13:00:00Z" }`

---

## 7. Synapse — Platinum Integration Blueprint

**UI Components & Triggers:**

- `/synapse` dashboard (React/Next.js route)
- Features: plugin management, external agent connection, performance benchmarking, risk/log review, traffic monitoring
- **UI Event Methods:**
  - `onPluginRegister(manifest: PluginManifest): Promise<void>`
  - `onPluginApprove(pluginId: string): Promise<void>`
  - `onPluginExecute(pluginId: string, payload: PluginPayload): Promise<PluginResult>`
  - `onPluginRevoke(pluginId: string): Promise<void>`
  - `onConnectionRequest(agentId: string): Promise<ConnectionResult>`
  - `onBenchmark(pluginId: string): Promise<BenchmarkResult>`
  - `onExportLogs(): Promise<ExportedTrafficLog>`
  - `onViewTrafficSummary(): Promise<TrafficSummary[]>`

**API Contracts:**

- `POST /api/synapse/plugin/register`
  - *Payload*: `{ ...PluginManifest }`
  - *Success*: `201 Created`, `{ status: "registered", pluginId: string }`
  - *Errors*: `401 Unauthorized`, `422 Validation`, `500 ServerError`
- `POST /api/synapse/plugin/:id/approve`
  - *Response*: `200 OK`, `{ status: "approved", pluginId: string }`
- `POST /api/synapse/plugin/:id/execute`
  - *Payload*: `{ payload: PluginPayload }`
  - *Success*: `200 OK`, `{ result: PluginResult }`
  - *Errors*: `403 Forbidden`, `429 RateLimited`
- `POST /api/synapse/plugin/:id/revoke`
  - *Response*: `200 OK`, `{ status: "revoked" }`
- `POST /api/synapse/connection/request`
  - *Payload*: `{ agentId, intent, permissions }`
  - *Response*: `201 Created`, `{ connectionId: string, status: "pending" }`
- `POST /api/synapse/benchmark/run`
  - *Payload*: `{ pluginId }`
  - *Response*: `{ benchmark: BenchmarkResult }`
- `GET /api/synapse/logs`
  - *Response*: `{ logs: TrafficLogEntry[] }`
- `GET /api/synapse/traffic-summary`
  - *Response*: `{ summary: TrafficSummary[] }`

**Plugin Manifest Example:**

```
json
```

CopyEdit

`{ "plugin_id": "summarizer-v2", "manifest_version": "1.0.0", "author": "user-123", "permissions": ["read_vault", "write_core"], "sandbox": true, "risk_tier": "moderate", "benchmarks": { "cpu": 5, "mem": 30 } }`

**Integration Flows:**

- All plugins and connections require user approval before execution
- Plugin actions and traffic routed through Core, results returned to calling agent
- All manifest updates and revocations are fully audit-logged
- Performance and traffic benchmarking available per plugin/connection

**Sentry Integration:**

- Every registration, execution, approval, revoke, and connection triggers `POST /api/sentry/audit`
- High-risk, rate-limited, or anomalous traffic triggers Sentry warning/override
- Sentry maintains risk history and fallout logs

**Vault Integration:**

- Synapse never reads/writes persona memory; only stores plugin and connection logs
- All plugin logs are versioned and exportable

**Core Integration:**

- All agent/plugin interactions mediated by Core, session logs include plugin call traces
- Core can suppress, suggest, or block plugin responses based on user config

**Audit, Export, and Error:**

- All plugin/connection actions timestamped and exportable
- Error handling: status, risk, fallback/retry routes shown to user

**Security/Compliance:**

- All actions require JWT/session token, user opt-in, and Sentry audit
- Acceptance: All plugin and traffic events surfaced within 2s; user can export, annotate, or revoke any connection

**Sample Audit Log Event:**

```
json
```

CopyEdit

`{ "event_id": "synapse-audit-20250706-001", "source": "synapse", "action": "plugin_execute", "user_id": "user-123", "plugin_id": "summarizer-v2", "status": "success", "timestamp": "2025-07-06T14:01:00Z" }`

---

## 8. Sentry — Platinum Integration Blueprint

**UI Components & Triggers:**

- `/sentry` dashboard (React/Next.js route)
- Features: live risk dashboard, override panel, anomaly review, audit export, kill switch, policy configuration
- **UI Event Methods:**
  - `onAuditView(): Promise<AuditEvent[]>`
  - `onOverride(eventId: string, reason: string): Promise<void>`
  - `onKill(targetId: string): Promise<void>`
  - `onExportAudit(): Promise<ExportedAuditLog>`
  - `onRiskConfigUpdate(newThresholds: RiskThresholds): Promise<void>`

**API Contracts:**

- `GET /api/sentry/audit`
  - *Response*: `{ logs: AuditEvent[] }`
- `POST /api/sentry/override`
  - *Payload*: `{ eventId, reason }`
  - *Success*: `200 OK`, `{ status: "overridden" }`
  - *Errors*: `403 Forbidden`, `404 NotFound`
- `POST /api/sentry/kill`
  - *Payload*: `{ targetId }`
  - *Response*: `200 OK`, `{ status: "killed" }`
- `GET /api/sentry/dashboard`
  - *Response*: `{ riskEvents: RiskEvent[], riskScore: number }`
- `GET /api/sentry/anomaly-review`
  - *Response*: `{ anomalies: AnomalyEvent[] }`
- `PATCH /api/sentry/risk-config`
  - *Payload*: `{ thresholds: RiskThresholds }`
  - *Response*: `200 OK`, `{ status: "updated" }`

**Risk Event Example:**

```
json
```

CopyEdit

`{ "event_id": "risk-5432", "event_type": "plugin_permission_escalation", "origin": "synapse", "plugin_id": "summarizer-v2", "risk_score": 89, "recommended_action": "block", "user_override": false, "timestamp": "2025-07-06T15:32:00Z", "resolution": null, "escalation_chain": [], "audit_log": [ {"action": "detected", "by": "sentry", "timestamp": "..."}, {"action": "user_reviewed", "by": "user", "timestamp": "..."} ] }`

**Integration Flows:**

- Monitors all module events, plugin traffic, Vault access, session changes, and external connections
- Blocks/warns on risk, surfaces user override panel (reason required, logs fallout)
- Kill switch disables plugin/agent/connection, logs action and all aftermath
- Policy changes require admin/user and are versioned

**Core, Synapse, Vault Integration:**

- Sentry logs and reviews every action from all modules and external points
- Export and override are always available to user/admin

**Audit, Export, and Error:**

- All events timestamped and exportable (JSON, CSV)
- Errors surfaced, override escalation, fallout tracked

**Security/Compliance:**

- No event, override, or kill can be hidden from the audit log
- User can always export full audit trail
- Acceptance: All risk actions and overrides surfaced in <2s, full fallback, and escalation logs present

**Sample Audit Log Event:**

```
json
```

CopyEdit

`{ "event_id": "sentry-audit-20250706-001", "source": "sentry", "action": "override", "user_id": "user-123", "target_id": "plugin-summarizer-v2", "status": "overridden", "timestamp": "2025-07-06T14:20:00Z" }`

---

## 9. Cross-Module Integration: AI Roundtable & Collaboration

**UI Flows:**

- `/core` dashboard: “New Roundtable” button
- Modal: agent/participant picker, breakout configuration, topic tagging
- Live feed: full prompt/response trace, surface/hide toggle, audit trail access

**API & Event Sequence:**

1. `POST /api/core/session`
   - Payload: `{ topic, participants: [agentIds], breakouts?: [{topic, participants}] }`
   - 201 Created: `{ sessionId }`
2. For each agent:
   - `PATCH /api/core/session/:id/participants` (add/remove during session)
   - `POST /api/synapse/connection/request` for any external agent (user approval required)
   - `POST /api/synapse/plugin/:id/execute` for plugins (manifest/audit tracked)
3. Each agent reply triggers:
   - `POST /api/core/session/:id/log` (records prompt, agentId, output, timestamp)
   - Hidden responses stored but not surfaced; full log exportable
4. Sentry monitors:
   - All agent/plugin actions: `POST /api/sentry/audit`
   - If threshold exceeded: user warned, can `POST /api/sentry/override`
   - Kill switch: `POST /api/sentry/kill` (blocks agent/plugin in-session)
5. Vault archives:
   - All session logs, agent outcomes, audit trail: `POST /api/vault/persona-memory/core-session-:id`
   - User may export: `GET /api/vault/persona-memory/core-session-:id/export`
6. At any time:
   - User can trigger `onBreakoutCreate`, `onAgentAdd/Remove`, `onVerbosityChange`
   - All actions versioned, timestamped, and audit-logged

**Sequence Diagram (Textual):**

```
pgsql
```

CopyEdit

`User → Core: POST /session Core → Vault: Store session meta/log pointer User → Core: PATCH /session/:id/participants Core → Synapse: Request external agent/plugin (user approval) Agent(s) → Core: POST /session/:id/log Core → Sentry: POST /audit (each agent/plugin event) User: Views live feed (surface/hide), triggers breakouts Core → Vault: Archive full log and audit on session end User → Core: GET /session/:id/log, Vault export`

**User Controls:**

- Add/remove any agent or plugin at any time (requires confirmation, audit)
- Create or dissolve breakouts mid-session
- Set feed verbosity (all, critical, user-tagged only)
- Export or purge session and audit logs

**Security/Compliance:**

- JWT/auth required on every endpoint
- Every agent, plugin, and external response is audited
- All override/kill/force actions are surfaced, cannot be hidden

**Sample Session Log Export:**

```
json
```

CopyEdit

`{ "session_id": "core-0123", "topic": "Product Brainstorm", "participants": ["alden", "alice", "sentry", "external-coding-agent"], "timeline": [ { "timestamp": "2025-07-06T16:05:00Z", "prompt": "How can we improve onboarding?", "responses": [ { "agent": "alden", "response": "...", "surfaced": true }, { "agent": "alice", "response": "...", "surfaced": true }, { "agent": "external-coding-agent", "response": "...", "surfaced": false } ] } ], "audit_log": [ { "event": "agent_added", "actor": "user-123", "agent": "external-coding-agent", "timestamp": "..." }, { "event": "override", "actor": "user-123", "target": "sentry", "reason": "false positive", "timestamp": "..." } ] }`

---

## 9b. AI Roundtable Conversational Orchestration Workflow

**1. Session Initialization**

- User seeds a new roundtable (`POST /api/core/session`) and sets topic, agents, scoring rubric (relevance, confidence, insight, creativity).
- Agents join; moderator agent is assigned (default: Sentry or a special Moderator persona).

**2. Prompt & Response Phase**

- User or agent (per config) posts an initial prompt.
- All participating agents are signaled by Core:\
  `POST /api/core/session/:id/next-turn`
- Each agent responds independently:
  - `POST /api/core/session/:id/log` `{ agentId, prompt, response, timestamp }`
- Moderator scores each response on:
  - `relevance` (0–100)
  - `confidence` (0–100)
  - `insight` (0–100)
  - `creativity` (0–100)
- Agents may also self-score or cross-score peer responses.

**3. Moderation, Prioritization, and Commentary**

- Moderator aggregates all scores for each response.
- Determines speaker queue for next round:
  - Highest-priority (e.g., highest insight or relevance) presented next.
  - All previous responses re-scored in light of the new comment (trigger: `PATCH /api/core/session/:id/score`)
  - If *insight* is below threshold for all, moderator triggers re-prompt:
    - `POST /api/core/session/:id/moderate` `{ action: "regenerate", agentId, prompt }`
    - Target agent or LLM generates a new comment.

**4. Iterative Rounds**

- Each new response triggers scoring and prioritization.
- Agents may “challenge” or “endorse” others, adding to score.
- The moderator can:
  - Request clarifications
  - Ask for evidence
  - Suggest alternative viewpoints
  - Silence or highlight agents as needed

**5. User & Audit Control**

- All events, prompts, scores, moderation actions, and overrides are logged:
  - `POST /api/sentry/audit` (every round)
- User can:
  - Adjust scoring weights live
  - Remove/insert agents at any round
  - Surface/hide agent contributions in live feed
  - Export full timeline with scores and audit log

**6. End of Session**

- User ends roundtable, exports:
  - Full session log (all agent comments, scores, moderation steps)
  - Score breakdown per agent and prompt
  - Audit trail (every moderation and override)
- Vault archives all outputs, with audit trail.

---

### **Sample Event Flow (N Agents):**

```
mermaid
```

CopyEdit

`sequenceDiagram participant U as User participant C as Core participant M as Moderator participant A1 as Agent-1 participant A2 as Agent-2 participant A3 as Agent-N U->>C: POST /session (topic, agents, rubric) C->>M: Assign moderator U->>C: POST /session/:id/next-turn (prompt) C->>A1: prompt C->>A2: prompt C->>A3: prompt A1->>C: response A2->>C: response A3->>C: response C->>M: responses M->>C: scores (relevance, confidence, insight, creativity) C->>M: All scores aggregated M->>C: speaker priority for next round loop Each round C->>A1: (if next) ... M->>C: (if re-prompt needed) end U->>C: PATCH /session (weights, agents) U->>C: Export session C->>Vault: archive session, scores, audit`

---

**Scaling Guidance:**

- The same logic applies for any N agents, internal or external.
- Each round’s scoring/prioritization is O(N^2) if cross-scoring; otherwise O(N).
- Moderator can be LLM, Sentry, or user-driven.

---

**Security & Audit:**

- All scoring, moderation, and agent actions are surfaced in audit logs.
- User control/override available at every stage.
- No agent response is lost: all are stored, even if not surfaced.

## 10. Audit, Security, and User Control Flows

**Audit Trail Architecture**

- Every user action, agent action, plugin, session, and external interaction is logged via Sentry.
- Audit logs are immutable and timestamped; exportable as JSON/CSV.
- Audit events include: source, action, status, user/agent, timestamp, resolution, escalation chain.

**User Control**

- Users can view, export, or annotate any audit log in every module’s UI (Vault, Sentry, Core).
- Every override, force, or kill action is confirmed, logged, and requires a reason.
- Users can configure audit verbosity (critical only, all, or custom tags).
- Session and memory management always user-initiated:
  - Export, purge, archive, or review per session, agent, plugin, or persona.
- Plugin approvals and permissions require explicit user opt-in and are logged.

**Security**

- All memory is AES-256+ encrypted at rest; export only on user request.
- JWT/session required for all API calls.
- Sentry blocks, warns, or escalates any detected threat, but user can override with reason.
- All plugin and agent traffic routed through Synapse; no direct external access is allowed.
- Kill switch disables any agent, plugin, or session instantly (with audit/fallback).

**System-Wide Compliance**

- No action, override, or error can bypass the audit trail.
- All user and agent actions are surfaced in UI within 2 seconds.
- Sentry/Fallback always provides user with actionable, plain-language feedback and next steps.
- No “silent fail”—all dropped, blocked, or errored actions surface warnings and logs.

**Sample Audit Flow:**

1. User triggers export of Alice’s memory.
2. Vault logs action:\
   `{ source: "vault", action: "export", user_id: "user-123", status: "success", timestamp: "..." }`
3. Sentry captures and displays audit event; user can export or annotate.
4. If export fails, error event and recommended action are surfaced in UI.
5. Any override, kill, or anomaly triggers escalation chain:
   - Sentry logs
   - User receives warning and explanation
   - Fallout (if any) is monitored and recorded

---
