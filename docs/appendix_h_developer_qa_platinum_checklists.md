# Appendix H – Developer & QA Platinum Checklists

*Each module receives its own section. Every checklist is actionable, detailed, and maps directly to documented requirements. Suitable for copy/paste into GitHub Issues, PRs, or QA tools.*

---

## 1. Core (Orchestration)

### Developer Checklist

- Implements API boundary: Core does not access local persona memory (only Core Communal Memory)
- WebSocket/session manager fully isolates agent connections
- Session initiation, roundtable, and breakout flows implemented
- Sentry logging for every Core-mediated event
- Room management (creation, join/leave, agent suggestion, close)
- All permission checks against user/agent roles
- Session export/import matches versioned schema

### QA Checklist

- No local memory flows route through Core (test with simulated agents)
- Session, roundtable, and breakout flows exercised with >2 agents
- Sentry logs complete for all session events and errors
- Permissions correctly restrict/allow agent participation
- Exported session matches documented schema; import restores full state

---

## 2. Alden (Evolutionary Companion)

### Developer Checklist

- Implements growth, habit, and learning agility logs per persona
- Personality matrix scores stored only in Alden’s Vault slice
- Reflection/feedback logic supports user teaching/corrections
- API for CRUD on tasks, streaks, feedback, export/import
- UI renders growth dashboard, session mood, and habit history
- All logs/audits reference only user/Alden context

### QA Checklist

- Creating/updating tasks or streaks logs only to Alden’s memory
- No cross-persona access possible; test read/write lockout
- Reflection/correction flows update Alden’s state
- All UI features accessible (keyboard, screen reader, contrast)
- Export/import round-trips all Alden-specific data

---

## 3. Alice (Cognitive-Behavioral)

### Developer Checklist

- Tone, cadence, formality, and feedback stats computed per session
- Corrections, feedback, and teachability logs tracked
- Session mood and streaks UI implemented
- Only Alice’s Vault slice stores session analytics
- No data written to other personas
- All correction events auditable and user-editable

### QA Checklist

- Sentiment/tone/cadence correctly tracked and logged
- Feedback/correction triggers logged and reflected in state
- Data isolation validated: only Alice’s memory stores her analytics
- UI accessible, metrics readable, feedback flows testable
- Import/export round-trips all analytics and corrections

---

## 4. Mimic (Dynamic Persona)

### Developer Checklist

- Persona creation/curation wizard complete
- CRUD for persona data, analytics, archive/restore
- Skill/task history logged per Mimic persona
- Each Mimic persona has isolated memory
- UI reflects persona traits, analytics, and performance score
- Import/export supports persona definition and history

### QA Checklist

- Persona creation/update reflected in UI, logs, and Vault
- Isolation: one Mimic cannot read/write another’s data
- Performance analytics update with task repetition
- UI accessible; performance score displayed and correct
- Import/export round-trips persona and history data

---

## 5. Sentry (Security & Audit)

### Developer Checklist

- Hooks every event, process, and external action (cannot be bypassed)
- Policy override and incident response implemented
- User/admin final override logic present
- Technical log and user-friendly dashboard complete
- Incident quarantine and rollback logic implemented
- All actions exportable and reviewable by user

### QA Checklist

- Every system/process/plugin event logged in Sentry
- Override/terminate flows tested (admin and user)
- Incident quarantine and rollback restore full state
- User-friendly dashboard: all alerts surfaced
- No bypass of Sentry logging is possible

---

## 6. Vault (Secure Memory)

### Developer Checklist

- Implements per-persona and communal memory schemas
- AES-256 (or higher) encryption at rest
- API for CRUD, query, audit, export/import, purge
- User controls memory topic, frequency, and relevance
- Immutable audit log per persona and communal slice
- No external/network API except through Synapse

### QA Checklist

- Only agents with user consent can access communal slices
- No agent can read/write another’s local memory
- User can filter/export/purge memory by topic, relevance
- Export/import, backup/restore tested with real data
- All memory actions logged and auditable

---

## 7. Synapse (Plugin/API Gateway)

### Developer Checklist

- Manifest-based plugin loader, sandboxing, risk scoring
- Permission workflow and plugin approval UI
- Logs all plugin, API, and browser extension events
- Audit log export and per-connection traffic view
- Only Synapse can load/execute plugin code
- Benchmarks and resource controls implemented

### QA Checklist

- Plugins/extensions load only via manifest; sandbox enforced
- Risk scoring and approval flows test all code paths
- Sentry logs all plugin actions (deny, load, execute, fail)
- UI: traffic logs, plugin management, risk/benchmark visible
- Benchmark and performance tiers honored on resource use

---

## 8. UI/UX (Global & Cross-Module)

### Developer Checklist

- Implements global shell, theme, and accessibility guidelines
- Keyboard/screen reader/contrast compliance (WCAG 2.1 AA+)
- Real-time log/alert surfacing across modules
- Global export/import, backup, onboarding flows
- All UI flows local-first, no network required

### QA Checklist

- All core, persona, and plugin UIs fully accessible (tab, ARIA, high contrast)
- No critical flows require network/online
- Real-time logs/alerts always visible
- Global onboarding/backup flows work start to finish

---

**End of Platinum Developer & QA Checklists (Appendix H).**
