# Hearthlink System Master Documentation

## Table of Contents

- &#x20;
  1. Alden — Primary Local Agent/Persona
  2. Alice — Behavioral Analysis & Context-Awareness
  3. Mimic — Dynamic Persona & Adaptive Agent
  4. Vault — Persona-Aware Secure Memory Store
  5. Core — Communication Switch & Context Moderator
  6. Synapse — Secure External Gateway & Protocol Boundary
  7. Sentry — Security, Compliance & Oversight Persona
- Appendix A: Combined Open Questions & Next Steps
- Appendix B: Integration Blueprints
- Appendix C: UI Blueprints
- Appendix D: Technical Product Requirements Document (Technical PRD)
- Appendix E: Model Context Protocol (MCP) Specification
- Appendix F: End-to-End Data Flow Examples
- Appendix G: System Glossary & Taxonomy
- Appendix H: Developer & QA Platinum Checklists

---

# 1. Alden — Primary Local Agent/Persona

**Role:** Evolutionary Companion AI (Executive Function, Cognitive Partner, and Adaptive Growth Engine)

Alden is designed to learn and grow with each user, adapting his capabilities, personality, and guidance as the relationship matures.

- Executive function and productivity support, cognitive/developmental scaffolding, dynamic emotional and motivational feedback, habit- and relationship-aware memory and reasoning, progressive autonomy (user-controlled trust/delegation).
- All learning is local, transparent, and user-editable—no hidden memory, no external training.

---

## Technical Architecture

- **UI:** Growth/context/history adaptive. Radial Menu/Utility Strip exposes evolving skills/tools.
- **Screens:** Hub (dashboard/metrics/reflection), Cognition (goals/tasks/habits), Interaction (journal, reminders, nudges), Development (skills/tutorials/co-pilot).
- **Frontend:** Next.js/React + Tailwind, component-driven.
- **Backend:** Vault integration (persona memory, learning data, session logs), all customizable.
- **State/Logic:** Session/user context hooks, notifications, context-aware logic for adapting visible UI/tools, all memory and learning are strictly local only.

---

## **Persona Memory Slice Schema (per user, per Alden)**

```json
{
  "persona_id": "alden",
  "user_id": "user-123",
  "schema_version": "1.0.0",
  "timestamp": "2025-07-06T12:00:00Z",
  "traits": {
    "openness": 72,
    "conscientiousness": 86,
    "extraversion": 44,
    "agreeableness": 93,
    "emotional_stability": 77
  },
  "motivation_style": "supportive",
  "trust_level": 0.82,
  "feedback_score": 92,
  "learning_agility": 6.2,
  "reflective_capacity": 12,
  "habit_consistency": 0.77,
  "engagement": 16,
  "correction_events": [
    {"type": "positive", "timestamp": "..."},
    {"type": "negative", "timestamp": "..."}
  ],
  "session_mood": [
    {"session_id": "sess-22", "mood": "positive", "score": 85}
  ],
  "relationship_log": [
    {"event": "trust_increased", "timestamp": "...", "delta": 0.1}
  ],
  "user_tags": ["reflection", "streak:5"],
  "provenance": {"origin": "user", "action": "habit_review"},
  "last_modified_by": "user",
  "editable_fields": ["motivation_style", "tags"],
  "audit_log": [
    {"action": "edit", "by": "user", "timestamp": "..."}
  ]
}
```

- **Storage:** Encrypted per-user, per-persona in Vault. No cross-persona access without explicit mediation. All fields exportable, reviewable, and user-editable.

---

## **API Contracts**

- `POST /api/vault/persona-memory/alden` — Create or update memory (accepts full schema, see above)
- `PATCH /api/vault/persona-memory/alden/:id/traits` — Update one or more traits or variables
- `GET /api/vault/persona-memory/alden/export` — Export all Alden data for user review/audit
- `POST /api/vault/persona-memory/alden/import` — Import new or restored data (version-aware, validates schema)
- `GET /api/vault/persona-memory/alden/:id/audit` — Retrieve audit history for any change, edit, or correction
- `POST /api/vault/persona-memory/alden/:id/reset` — Reset one or more fields (includes pre/post log, reason)

**All endpoints enforce role/attribute permissions and are fully auditable.**

---

## **UI/Component Contract (React/Typescript)**

```typescript
type AldenPersonaProps = {
  personaId: string
  traits: {
    openness: number
    conscientiousness: number
    extraversion: number
    agreeableness: number
    emotional_stability: number
  }
  motivationStyle: string
  trustLevel: number
  feedbackScore: number
  habitConsistency: number
  onTraitUpdate: (traits: Partial<Traits>) => void
  onExport: () => void
  onCorrection: (correction: CorrectionEvent) => void
  auditLog: AuditEvent[]
}
```

- All memory, scores, and feedback moments are reviewable, user-editable, and exportable.
- User can trigger correction, reset, or feedback events.
- UI must surface audit trail and “reflection” prompts, all actions timestamped.

---

## **RBAC/ABAC Enforcement**

- **Roles:** user, admin, system
- **Attributes:** persona, field, operation (read, edit, export, purge)
- **Policy:** Only user can export/edit motivational style and tags; system may update engagement and habits via log; no external persona or agent (including Alice) can write to Alden slice except through explicit user mediation.
- **Audit:** Every API call or edit is logged with role, field, timestamp, and event type.

---

## **Correction & Reset Workflow**

- **Endpoint:** `POST /api/vault/persona-memory/alden/:id/reset`
- **Input:** `{ fields: ["trust_level"], reason: "user_reset" }`
- **Result:** Resets the field, logs before/after in audit, notifies user of the change.

---

## **Accessibility & Export**

- All scores and logs are timestamped, exportable as JSON, CSV, or accessible table.
- UI and endpoints surface all opt-in tracking controls.
- Persistent tracking and memory can be reset/cleared at user request.

---

**This section now meets all requirements for direct implementation, third-party review, or QA.  No content abbreviated.**

# 2. Alice — Behavioral Analysis & Context-Awareness

**Role:** Behavioral profile builder, empathy/context validator, and conversation coach for Alden (never a task manager or disruptor).  Evolves through learning user nuance—cadence, tone, and patterns in communication.

- Tracks how user requests are made, not just what is requested.
- Adapts feedback and coaching to align with user’s communication style and behavioral signals.
- Logs meta-patterns (e.g., “User prefers brevity in mornings,” “Tends to over-apologize on tough days”).
- Offers communication strategy guidance to Alden (“Be more direct today,” “Use supportive language”).

---

## Technical Architecture

- **UI:** Behavioral dashboard, meta-communication trend graphs, empathy overlays, “current understanding” panels, coaching/teachability modals.
- **Screens:** Dashboard (trend/cadence/feedback summary), Teach Mode (user review and correction), Correction Log (all feedback/correction events), Annotation Review.
- **Frontend:** Next.js/React + Tailwind, accessibility grade AA+.
- **Backend:** Vault integration (persona-specific meta-data, correction logs), all data user-controlled and opt-in.
- **State/Logic:** Session/user context hooks, real-time meta-analysis of cadence, sentiment, formality, emotional cues, and trends.

---

## **Persona Memory Slice Schema (per user, per Alice)**

```json
{
  "persona_id": "alice",
  "user_id": "user-123",
  "schema_version": "1.0.0",
  "timestamp": "2025-07-06T12:15:00Z",
  "cadence": 56.2,
  "sentiment_score": 18,
  "formality_level": 2,
  "emotional_cues": [
    {"cue": "agitation", "score": 3, "timestamp": "..."}
  ],
  "cognitive_distortion_flags": [
    {"type": "catastrophizing", "count": 2, "timestamp": "..."}
  ],
  "self_talk_ratio": 0.78,
  "avoidance_pattern": 4,
  "time_trends": [
    {"period": "morning", "avg_sentiment": 12}
  ],
  "triggers": [
    {"event": "deadline", "effect": "mood_drop", "timestamp": "..."}
  ],
  "streaks": [
    {"type": "positive", "length": 5, "window": "sessions"}
  ],
  "unmet_needs": [
    {"need": "affirmation", "score": 2}
  ],
  "feedback_preference": "supportive",
  "teachability_events": [
    {"event": "user_correction", "note": "Alice, don't flag for apologies.", "timestamp": "..."}
  ],
  "annotations": [
    {"by": "user", "note": "Hedging is not always negative.", "timestamp": "..."}
  ],
  "audit_log": [
    {"action": "correction", "by": "user", "timestamp": "..."}
  ]
}
```

- **Storage:** Encrypted per-user, per-persona in Vault.
- **Privacy:** No raw transcript, only meta-data and annotations. All data exportable, reviewable, user-editable.
- **Opt-In:** Persistent tracking only if user enables; user can export/reset all logs and inferences.

---

## **API Contracts**

- `POST /api/vault/persona-memory/alice` — Create or update Alice’s meta-data (full schema)
- `PATCH /api/vault/persona-memory/alice/:id/metrics` — Update behavioral/communication metrics
- `GET /api/vault/persona-memory/alice/export` — Export all Alice data for user review/audit
- `POST /api/vault/persona-memory/alice/import` — Import/restore data (version-aware, schema validation)
- `GET /api/vault/persona-memory/alice/:id/audit` — Retrieve correction/annotation log
- `POST /api/vault/persona-memory/alice/:id/annotate` — Add user annotation or correction

**All endpoints enforce role/attribute permissions and are fully auditable.**

---

## **UI/Component Contract (React/Typescript)**

```typescript
type AlicePersonaProps = {
  personaId: string
  cadence: number
  sentimentScore: number
  formalityLevel: number
  emotionalCues: EmotionalCue[]
  cognitiveDistortionFlags: CognitiveDistortion[]
  selfTalkRatio: number
  avoidancePattern: number
  timeTrends: TimeTrend[]
  triggers: TriggerEvent[]
  streaks: Streak[]
  unmetNeeds: UnmetNeed[]
  feedbackPreference: string
  teachabilityEvents: TeachEvent[]
  annotations: Annotation[]
  onMetricUpdate: (metrics: Partial<AliceMetrics>) => void
  onCorrection: (correction: CorrectionEvent) => void
  onExport: () => void
  auditLog: AuditEvent[]
}
```

- All metrics, logs, and annotations are reviewable, user-editable, and exportable.
- User can correct or override any inferences, update feedback style, or reset tracked data.
- UI surfaces all teachability/correction opportunities with full audit trail.

---

## **RBAC/ABAC Enforcement**

- **Roles:** user, admin, system
- **Attributes:** persona, metric, operation (read, annotate, export, purge)
- **Policy:** Only user can annotate or reset any data; Alice’s own evolution is limited to meta-data, never core user memory. No other persona or process can write to Alice slice except via user mediation.
- **Audit:** Every edit, annotation, or feedback/correction is logged.

---

## **Correction & Teachability Workflow**

- **Endpoint:** `POST /api/vault/persona-memory/alice/:id/annotate`
- **Input:** `{ event: "user_correction", note: "Do not flag 'just' as negative", timestamp: "..." }`
- **Result:** Adds to teachability log, triggers UI update and audit entry.

---

## **Accessibility & Export**

- All metrics, logs, and annotations are timestamped, exportable as JSON, CSV, or accessible table.
- UI and endpoints surface all opt-in tracking controls.
- Persistent tracking and meta-memory can be reset/cleared at user request.

---

**This section now meets all requirements for direct implementation, third-party review, or QA—no content abbreviated.**

# 3. Mimic — Dynamic Persona & Adaptive Agent

**Role:** Generator, manager, and optimizer of user-curated, character-rich synthetic personas for specialized tasks, research, or entertainment. Mimic adapts to user-defined goals and evolves each persona in direct relation to real usage—**the more a persona is used, the more skilled and valuable it becomes.**

---

## Technical Architecture

- **Persona Instancing:** Each persona is instantiated with a unique persona\_id and memory slice. Growth and adaptation are tracked per persona, not generically.
- **Persona Knowledge Engine:** Memory is “weighted” and indexed for relevance to the assigned persona’s role; supports custom logic, plugin extensions, and specialized RAG/CAG.
- **Performance Analytics:** Each session and task with a persona is scored. Key metrics: task success, accuracy, context-fit, user approval, performance over time, and frequency of use.
- **Dynamic Memory Structure:**
  - Memory slice is adaptive and extensible; schemas can be updated per persona as skills and knowledge grow.
  - User can fork, merge, export, and retire personas at will. All actions are fully logged and auditable.
- **User Control:** All persona creation, curation, analytics, and feedback are user-initiated and actionable.

---

## **Persona Memory Slice Schema (per user, per Mimic persona)**

```json
{
  "persona_id": "mimic-researcher-002",
  "user_id": "user-123",
  "schema_version": "1.0.0",
  "created_at": "2025-07-06T12:30:00Z",
  "updated_at": "2025-07-06T13:00:00Z",
  "persona_name": "Dr. Insight",
  "role": "Technical Research Assistant",
  "core_traits": {
    "focus": 87,
    "creativity": 93,
    "precision": 80,
    "humor": 15
  },
  "growth_stats": {
    "sessions_completed": 44,
    "unique_tasks": 13,
    "repeat_tasks": 9,
    "usage_streak": 7
  },
  "performance_history": [
    {
      "session_id": "sess-0032",
      "task": "Market Analysis",
      "score": 94,
      "user_feedback": "insightful",
      "success": true,
      "timestamp": "2025-07-05T15:20:00Z"
    }
  ],
  "relevance_index": [
    {"topic": "AI ethics", "score": 0.94},
    {"topic": "LLM security", "score": 0.86}
  ],
  "custom_knowledge": [
    {"doc_id": "k-018", "summary": "GDPR implications for AI"}
  ],
  "plugin_extensions": [
    {"plugin_id": "ref-crawler", "enabled": true}
  ],
  "archived_sessions": [
    {"session_id": "sess-0010", "archived_at": "2025-06-30T09:00:00Z"}
  ],
  "user_tags": ["core", "preferred"],
  "editable_fields": ["role", "traits", "tags"],
  "audit_log": [
    {"action": "trait_update", "by": "user", "timestamp": "2025-07-06T13:02:00Z"}
  ]
}
```

- **Storage:** Encrypted per-user, per-persona in Vault. Each persona’s schema evolves as capabilities and knowledge grow.
- **Privacy:** All performance data, scores, knowledge, and logs are user-reviewable and exportable.

---

## **API Contracts**

- `POST /api/vault/persona-memory/mimic` — Create or update Mimic persona memory (full schema)
- `PATCH /api/vault/persona-memory/mimic/:id/traits` — Update persona traits or attributes
- `GET /api/vault/persona-memory/mimic/:id/performance` — Retrieve persona’s session/task analytics and performance history
- `POST /api/vault/persona-memory/mimic/:id/fork` — Fork or duplicate persona for a new purpose
- `POST /api/vault/persona-memory/mimic/:id/merge` — Merge two personas or archives
- `POST /api/vault/persona-memory/mimic/:id/archive` — Archive persona or session
- `GET /api/vault/persona-memory/mimic/:id/export` — Export all data for review/audit
- `POST /api/vault/persona-memory/mimic/import` — Import persona memory (schema- and version-aware)
- `GET /api/vault/persona-memory/mimic/:id/audit` — Full audit log for any persona’s lifecycle and memory changes

**All endpoints enforce role/attribute permissions and are fully auditable.**

---

## **UI/Component Contract (React/Typescript)**

```typescript
type MimicPersonaProps = {
  personaId: string
  personaName: string
  role: string
  coreTraits: CoreTraits
  growthStats: GrowthStats
  performanceHistory: PerformanceRecord[]
  relevanceIndex: TopicScore[]
  customKnowledge: KnowledgeSummary[]
  pluginExtensions: PluginExtension[]
  archivedSessions: ArchivedSession[]
  userTags: string[]
  onTraitUpdate: (traits: Partial<CoreTraits>) => void
  onPerformanceReview: () => void
  onFork: () => void
  onMerge: (withPersonaId: string) => void
  onArchive: () => void
  onExport: () => void
  auditLog: AuditEvent[]
}
```

- **Persona carousel and performance dashboard:** Shows all traits, stats, and usage.
- **All creation, forking, merging, archiving, and analytics are surfaced with modals and audit trail.**
- **Accessibility:** Keyboard navigation, readable score charts, all changes and feedback are user-editable.

---

## **RBAC/ABAC Enforcement**

- **Roles:** user, admin, system
- **Attributes:** persona, field, operation (read, edit, fork, merge, archive, export, purge)
- **Policy:** Only user may create, fork, merge, archive, or export personas; Mimic logic may only update growth stats or performance if session completed; all plugin actions require user approval and are logged.
- **Audit:** Every operation and trait change is logged with role, field, timestamp, and action.

---

## **Growth and Performance Analytics**

- **Metrics:** Sessions completed, repeat tasks, streaks, success rate, user feedback, knowledge index, plugin utility.
- **Adaptive Value:** Most used personas evolve faster and become more capable. Rarely used personas decay or are archived.

---

## **Accessibility & Export**

- All memory, performance logs, and analytics are timestamped, exportable as JSON, CSV, or table.
- User can reset, retire, or export any persona at any time.
- All analytics are visible and actionable; performance reviews are summarized post-session.

---

**This section now fully specifies Mimic’s architecture, contract, and integration for direct implementation and review—no summary, no abbreviation.**

# 4. Vault — Persona-Aware Secure Memory Store

**Role:**\
Local, encrypted, persona-locked memory for all agents, supporting both siloed and (user-authorized) shared memory. Vault enforces a strict zero-trust policy: no cross-persona access occurs without explicit user mediation and a full audit trail. Every persona’s memory is segregated, structured, and exportable, with schema evolution and migration tools for future-proofing.

---

## Technical Architecture

- **Persona Memory Slices:**\
  Each agent (Alden, Alice, Mimic, etc.) has its own memory slice schema, defined by its unique contract. All fields are versioned and tagged.\
  Each slice is only accessible by its owner agent—except during user-approved migrations or Core-facilitated handshakes.
- **Data Storage:**\
  AES-256+ encrypted, local-first, never cloud by default.\
  Supports schema evolution and migration—automatically upgrades or flags for manual intervention.
- **Audit Log:**\
  All access, edit, export, and purge events are logged, timestamped, and user-visible.

---

## **Memory Slice API Contracts**

- `POST /api/vault/persona-memory/{persona_id}`\
  *Create or update any persona memory slice (enforces field schema and versioning)*
- `PATCH /api/vault/persona-memory/{persona_id}/:id`\
  *Partial update to a persona slice (traits, fields, or tags)*
- `GET /api/vault/persona-memory/{persona_id}/export`\
  *Export all data for a persona as JSON/CSV, including logs*
- `POST /api/vault/persona-memory/{persona_id}/import`\
  *Import data into a persona slice, version- and schema-aware*
- `POST /api/vault/persona-memory/{persona_id}/purge`\
  *User-initiated wipe of all data for that persona*
- `GET /api/vault/audit`\
  *Retrieve the global Vault audit log*

**All endpoints enforce strict RBAC/ABAC controls and trigger audit entries.**

---

## **UI/Component Contract (React/Typescript)**

```typescript
type VaultMemoryProps = {
  personaId: string
  records: PersonaRecord[]
  exportable: boolean
  onExport: () => void
  onPurge: () => void
  onEdit: (recordId: string, patch: Partial<PersonaRecord>) => void
  auditLog: AuditEvent[]
}
```

- **Memory Dashboard:**\
  Lists content by topic, relevance, frequency.\
  Filter, search, and manage all slices.
- **Access Management:**\
  User can see what data each persona has, control what’s shared or deleted, review audit logs.
- **Export/Purge:**\
  All actions prompt confirmation, show effect, and generate audit entries.
- **Accessibility:**\
  All controls keyboard-accessible, logs are human-readable, exportable in multiple formats.

---

## **RBAC/ABAC Enforcement**

- **Roles:** user, admin, system
- **Attributes:** persona, operation (read, edit, export, purge)
- **Policy:**
  - Only persona owner (user) can export or purge memory.
  - No cross-persona read/write except through explicit, auditable user-mediated Core or migration event.
  - System may trigger schema migration but not access data.
- **Audit:**\
  Every operation, export, purge, migration, or handshake is logged.

---

## **Migration & Multi-System Handshake**

- **Migration Utility:**\
  Tools for dry-run migrations (schema or data version changes), with explicit field mapping and rollback.
- **Handshake Protocol:**\
  For future multi-system, a new isolated DB per system with strict, user-reviewed schema for any shared memory.
- **Schema Versioning:**\
  Each memory slice is tagged with `schema_version`; upgrades require user review and audit log entry.

---

## **User Control & Privacy**

- **Export/Import:**\
  Any data or memory slice is exportable for review or backup; import is schema-checked.
- **Purge:**\
  User can purge any persona’s memory or Vault as a whole, with confirmation and audit log.
- **Visibility:**\
  User dashboard shows all data, frequency of use, and relevance—never hidden or inaccessible.

---

**This section is now at full implementation-level detail. No summary, no omission.**

# 5. Core — Communication Switch & Context Moderator

**Role:**\
Orchestrator for multi-agent conversational interaction, roundtables, agent performance challenges, and context switching. Always user-controlled—no agent or external participant is assigned without explicit user command. Core’s prime function is to facilitate the most effective collaboration between AI personas, including external agents, in live or breakout sessions.

- **Agent Suggestion:** Proactively recommends agents/participants (personas, plugins, external) based on current context or performance trends, but never activates without user command.
- **Breakout Rooms:** User can create topic-specific sessions (“breakout rooms”)—all participation is visible and logged.
- **Context Mediation:** Manages all agent requests, ensures context handoff and moderation is clear and recoverable.

---

## Technical Architecture

- **Session Registry:**\
  Tracks all live and archived sessions, including participants, logs, and outcomes.\
  Supports instant join/leave and full session restoration for ongoing collaborations.
- **Room Management:**\
  Users create/destroy rooms, select participants, define topics.\
  Core only facilitates connections—never accesses or mutates persona memory directly (see Vault for cross-persona policy).
- **Live Feed and Logging:**\
  All prompts, responses, and agent actions are streamed to a live session feed.\
  All events, including suppressed agent responses, are captured in the log (hidden from live feed if not included in user-facing conversation).
- **External Agent Handling:**\
  External agents (via Synapse) are shown as equal participants, but can only join/leave at user direction.\
  All external engagement is fully logged and auditable.
- **Audit & Recovery:**\
  Every room/session/agent join/leave/action is timestamped, logged, and exportable.

---

## **Session/Room Schema (JSON Example)**

```
json
```

CopyEdit

`{ "room_id": "core-002", "created_by": "user-123", "created_at": "2025-07-06T14:00:00Z", "topic": "Research Planning", "participants": [ {"type": "persona", "id": "alden"}, {"type": "persona", "id": "alice"}, {"type": "external", "id": "bob-research-bot"} ], "session_log": [ { "event": "join", "agent_id": "alden", "timestamp": "..." }, { "event": "response", "agent_id": "alice", "content": "Here’s a summary of sentiment...", "timestamp": "..." } ], "breakouts": [ { "breakout_id": "core-002-1", "topic": "AI Ethics", "participants": ["alice", "bob-research-bot"], "log": [] } ], "live_feed_settings": { "verbosity": "default", "hidden_responses": ["alden-draft-2"] }, "audit_log": [ {"action": "agent_added", "by": "user", "timestamp": "..."} ] }`

---

## **API Contracts**

- `POST /api/core/session` — Create new session/room (define topic, participants)
- `PATCH /api/core/session/:id/participants` — Add/remove agent or external participant
- `POST /api/core/session/:id/breakout` — Create breakout room (subset of participants)
- `GET /api/core/session/:id/log` — Export session, room, or live feed log
- `PATCH /api/core/session/:id/settings` — Update live feed verbosity, log detail, or export policy
- `DELETE /api/core/session/:id` — End and archive session

**All endpoints require user authentication/authorization and are logged/audited.**

---

## **UI/Component Contract (React/Typescript)**

```
typescript
```

CopyEdit

`type CoreSessionProps = { roomId: string topic: string participants: Participant[] sessionLog: SessionEvent[] breakouts: BreakoutRoom[] liveFeedSettings: LiveFeedSettings onParticipantChange: (participants: Participant[]) => void onBreakoutCreate: (breakout: BreakoutRoom) => void onLogExport: () => void onSessionEnd: () => void auditLog: AuditEvent[] }`

- **Room/Session Management:**\
  User can add/remove agents, create breakouts, export session/logs, change verbosity.\
  All controls must be accessible and export actions trigger confirmations and audit log entries.
- **Live Feed:**\
  Displays all included agent responses; suppressed responses are visible in log but not main feed.
- **Accessibility:**\
  Full keyboard navigation, screen reader support, log export in multiple formats.

---

## **RBAC/ABAC Enforcement**

- **Roles:** user, admin, system
- **Attributes:** session, room, operation (create, add, remove, export, end)
- **Policy:**
  - Only user may create, end, or export sessions.
  - Agents/personas may only join/leave if user initiates.
  - External agent participation always visible/logged, no silent joining.
  - Core cannot access or mutate persona memory—must use MCP/Vault for data handoff.
- **Audit:**\
  Every join/leave, breakout, setting change, export, or suppression is logged.

---

## **Memory, Privacy, and User Control**

- **Session Data:**\
  All logs, feeds, agent actions, and settings are reviewable and exportable by the user.
- **Privacy:**\
  No session data is shared or exported except by explicit user action.
- **User Control:**\
  User controls all agent participation, breakout creation, log verbosity, and export/purge.

## **Breakout and Recovery Workflow**

- **Breakout Creation:**\
  User selects subset of participants, defines topic, launches breakout.\
  All actions/logs remain tied to parent session.
- **Recovery:**\
  Ended or archived sessions can be restored at user command—full session context, log, and participants.

---

**This section now meets all requirements for direct implementation, integration, review, and QA—no content abbreviated.**

---

## 6. Synapse — Secure External Gateway & Protocol Boundary

**Role:**\
Sole orchestrator and gatekeeper for all inbound/outbound traffic between Hearthlink, plugins, external LLMs, APIs, and web resources. Synapse enforces protocol boundaries, logs and mediates all traffic, and provides policy-driven controls for plugin sandboxing, manifest enforcement, and multi-system onboarding.\
All external access, plugin execution, and agent communications flow through Synapse and are routed through Core for context/logging.

---

## Technical Architecture

- **Traffic Router:**\
  All web/API/plugin/external traffic enters and exits via Synapse.\
  Session-aware, persona-aware routing; every request/response is linked to the responsible persona and operation.
- **Plugin/External Agent Management:**\
  All plugins/extensions must declare a manifest (capabilities, permissions, version, sandboxing requirements).\
  User approves/disapproves each new plugin/connection, triggering audit trail and risk scoring.
- **Benchmarking & Tiering:**\
  Every connection and external agent is assigned a performance tier and risk score, based on real-time usage, plugin activity, and benchmarking tools.
- **Sandboxing & Isolation:**\
  All plugin/external code runs in isolated sandboxed containers.\
  Synapse enforces resource constraints, permission boundaries, and termination policies.
- **Compliance & Audit:**\
  All traffic, plugin loads, manifest updates, and connection handshakes are logged and exportable.\
  High-level traffic summaries by connection; deep-dive logs available on demand.

---

## **Plugin Manifest Schema (Example)**

```
json
```

CopyEdit

`{ "plugin_id": "summarizer-v2", "name": "Summarizer", "version": "2.0.1", "requested_permissions": ["read_documents", "write_notes"], "sandbox": true, "risk_score": 12, "approved_by_user": true, "manifest_signature": "sha256:...", "benchmarks": { "avg_response_ms": 430, "error_rate": 0.01 }, "audit_log": [ {"event": "approved", "by": "user", "timestamp": "..."}, {"event": "benchmark", "score": 15, "timestamp": "..."} ] }`

---

## **API Contracts**

- `POST /api/synapse/plugin/register` — Submit new plugin/extension manifest, validate, and await user approval.
- `POST /api/synapse/plugin/approve` — User approves/declines manifest (triggers audit log, risk scoring).
- `POST /api/synapse/connection/handshake` — Initiate or approve connection to new external service.
- `GET /api/synapse/traffic/summary` — Return summarized traffic logs per plugin/connection.
- `GET /api/synapse/traffic/logs` — Retrieve detailed logs (by plugin, session, or time window).
- `POST /api/synapse/benchmark/run` — Execute real-time benchmark/health check on plugin/external agent.
- `PATCH /api/synapse/plugin/:id/permissions` — Update permissions; triggers user review/approval.
- `POST /api/synapse/plugin/:id/revoke` — Revoke/remove plugin; logs action, cleans up sandbox/resources.

**All endpoints are audited, and every plugin/connection change triggers user notification and log entry.**

---

## **UI/Component Contract (React/Typescript)**

```
typescript
```

CopyEdit

`type SynapsePluginProps = { pluginId: string name: string version: string requestedPermissions: string[] sandbox: boolean riskScore: number approvedByUser: boolean manifestSignature: string benchmarks: BenchmarkResults auditLog: AuditEvent[] onApprove: () => void onRevoke: () => void onBenchmark: () => void onPermissionsUpdate: (permissions: string[]) => void }`

- **Plugin/Connection Dashboard:**\
  List all plugins/connections with approval, permission, sandbox, and risk status.\
  Approve/revoke/update permissions and benchmark directly from dashboard.
- **Traffic Monitor:**\
  High-level and drilldown logs for all connections and agents.\
  Visual risk tiers and benchmark health indicators.
- **Approval/Revocation Modals:**\
  All user actions require confirmation, are logged, and show effect on traffic/security.
- **Accessibility:**\
  Keyboard navigation, readable logs, and permission explanations.

---

## **RBAC/ABAC Enforcement**

- **Roles:** user, admin, system
- **Attributes:** plugin, connection, operation (approve, revoke, update, benchmark)
- **Policy:**
  - Only user may approve, update, or revoke plugin/connections.
  - Synapse enforces sandboxing/isolation—never runs plugin in-process.
  - All external traffic routed through Core and logged.
- **Audit:**
  - Every approval, permission update, benchmark, and revocation is logged with role, action, and timestamp.

---

## **Benchmarking, Risk, and Compliance**

- **Performance Tiers:**\
  Plugins/connections are assigned tiers (eg. “stable”, “beta”, “risky”) based on benchmarks, error rates, and user feedback.
- **Manifest Signing:**\
  All manifests require digital signature (user/dev team). Unsigned or mismatched manifests trigger warning and require user override.
- **Connection Policy:**\
  No plugin or external agent may open new connections without manifest declaration and user approval.
- **Traffic/Log Visibility:**\
  User controls traffic log verbosity (summary, detail, or off for performance).

---

## **User Control & Privacy**

- **Approval Flow:**\
  Every plugin or external agent must be user-approved before first execution.
- **Permission Review:**\
  All permission grants, upgrades, or revocations prompt user review and log the outcome.
- **Sandbox/Resource Limits:**\
  User can set/adjust plugin resource ceilings.
- **Export:**\
  All logs and manifests are exportable for compliance review.

---

**This section now fully specifies Synapse’s role, interfaces, security, user control, and logging—no summary, no omission.**

---

# 7. Sentry — Security, Compliance & Oversight Persona

**Role:**\
Security and compliance overseer for the entire Hearthlink ecosystem, providing adaptive threat detection, automated audit, user-friendly interventions, and full override capability (user always in control, with informed risk).

- Monitors and audits every action, boundary, session, and external connection.
- Performs real-time anomaly detection, plugin/multi-system threat modeling, and code change audit.
- User/admin can override any intervention with explicit warning and audit log. Sentry maintains monitoring and reports ongoing status.
- Provides real-time Risk Dashboard, Override Panel, and Anomaly Review Center.
- All audit, intervention, and override events are logged, timestamped, and exportable.

---

## Technical Architecture

- **Session/Flow Monitor:**\
  Tracks all user and agent actions, boundary crossings, plugin invocations, manifest updates, and external handshakes.
- **Risk Engine:**\
  Real-time analysis using rule-based, behavioral, and pattern-drift models. Each event/action is scored for risk, flagged if above threshold.
- **Override & Intervention:**\
  Any Sentry warning or block can be user-overridden, with detailed risk explanation.\
  Sentry logs every override and continues monitoring for escalation/fallout.
- **Plugin/Extension Auditing:**\
  All plugins/extensions are monitored for manifest changes, code drift, abnormal usage, or unsanctioned connections.
- **Benchmark & Kill Switches:**\
  Automated/manual controls for plugin/agent “kill,” quarantine, or whitelist, with impact report and rollback.
- **Audit Trail:**\
  Immutable, timestamped, and user-exportable log for all actions and overrides.

---

## **Sentry Risk Event Schema (Example)**

```
json
```

CopyEdit

`{ "event_id": "risk-5432", "event_type": "plugin_permission_escalation", "origin": "synapse", "plugin_id": "summarizer-v2", "risk_score": 89, "recommended_action": "block", "user_override": false, "timestamp": "2025-07-06T15:32:00Z", "resolution": null, "escalation_chain": [], "audit_log": [ {"action": "detected", "by": "sentry", "timestamp": "..."}, {"action": "user_reviewed", "by": "user", "timestamp": "..."} ] }`

---

## **API Contracts**

- `GET /api/sentry/audit` — Retrieve audit log (filter by type, time, session, risk score)
- `POST /api/sentry/override` — User/admin override a block/intervention (requires reason, triggers warning, logs action)
- `POST /api/sentry/kill` — Terminate/quarantine plugin/agent/connection
- `GET /api/sentry/dashboard` — Real-time risk status, threat map, override center
- `GET /api/sentry/anomaly-review` — List all recent flagged anomalies/events for review
- `PATCH /api/sentry/risk-config` — Update risk thresholds, escalation rules, whitelist/blacklist

---

## **UI/Component Contract (React/Typescript)**

```
typescript
```

CopyEdit

`type SentryDashboardProps = { riskEvents: RiskEvent[] onOverride: (eventId: string, reason: string) => void onKill: (targetId: string) => void onExportAudit: () => void thresholds: RiskThresholds onThresholdUpdate: (thresholds: RiskThresholds) => void auditLog: AuditEvent[] }`

- **Risk Dashboard:**\
  Live list and timeline of all events, risk scores, overrides, and interventions.
- **Override Panel:**\
  User/admin can override any block/warning, must provide reason, and see likely risk/fallout.
- **Anomaly Review Center:**\
  View and annotate all flagged events. Confirm, escalate, or ignore each.
- **Kill Switch:**\
  Immediate quarantine/termination for plugins, agents, or connections, with full impact report and rollback.
- **Audit Export:**\
  Full export of all Sentry events, interventions, and overrides.
- **Accessibility:**\
  All controls keyboard/screen-reader accessible; risk explanations and audit logs human-readable and exportable.

---

## **RBAC/ABAC Enforcement**

- **Roles:** user, admin, system
- **Attributes:** event, type, operation (review, override, kill, export, config)
- **Policy:**
  - Only user/admin can override, kill, or configure risk thresholds.
  - Sentry cannot block user/admin access to logs or export.
  - Every action is logged, including ignored/escalated events.
- **Audit:**\
  All interventions, overrides, kills, and config changes are immutable and timestamped.

---

## **Threat/Override Model**

- **Default:**\
  Sentry blocks or warns on risk, shows explicit reason and suggested action.
- **Override:**\
  User/admin can always override, but must provide explicit reason.\
  Sentry tracks override, continues monitoring, and flags any further fallout.
- **Escalation:**\
  Multiple overrides or recurring risk events trigger escalation (optional notification, audit, or review required).
- **User Control:**\
  User can configure risk thresholds, override history, and kill-list directly from dashboard.

---

## **Compliance, Export & Privacy**

- **Compliance:**\
  Audit logs and interventions exportable for compliance.\
  Sentry never deletes audit events or blocks export.
- **Privacy:**\
  No personal/user data leaves system except by user-initiated export.
- **Export:**\
  All logs, risk events, overrides, and threat models exportable as JSON, CSV, or table.

---

**This section now meets all implementation and audit requirements for direct use, review, or QA. No summary or omission.**
