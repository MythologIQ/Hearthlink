# Appendix G — Hearthlink System Glossary & Taxonomy

---

### A

**Agent**
*Definition*: An autonomous or semi-autonomous process or persona capable of interpreting instructions, maintaining state, and acting on user or system input.
*Examples*: Alden, Alice, Mimic
*Not to be confused with*: “Plugin” (external code module), “User” (human operator)

**Audit Log**
*Definition*: An immutable, timestamped record of all significant system, user, agent, and plugin actions.
*Examples*: Sentry logs, Vault access logs
*Not to be confused with*: “Session Log” (which may be mutable or session-specific)

---

### B

**Breakout Room**
*Definition*: A temporary, user-created context within a Core roundtable session, in which a subset of agents or plugins can engage in a focused discussion or task.
*Examples*: “Create a breakout for brainstorming features”
*Not to be confused with*: “Session” (which is the top-level context for all activity)

---

### C

**Core**
*Definition*: The orchestrator and mediator for multi-agent and multi-plugin collaboration, managing session state, roundtables, and all communal memory flows.
*Examples*: Initiates roundtable sessions, manages agent turn-taking
*Not to be confused with*: “Vault” (storage), “Sentry” (audit/security)

**Core Communal Memory**
*Definition*: A dedicated Vault slice accessible to multiple agents during sessions, governed by explicit user approval and Core mediation.
*Examples*: Shared project memory in a team roundtable
*Not to be confused with*: “Local Persona Memory” (private, agent-specific)

---

### D

**Dashboard**
*Definition*: The main UI panel for a persona or system module, exposing status, key actions, and logs.
*Examples*: Alden’s growth dashboard, Sentry incident feed

---

### E

**Extension**
*Definition*: Any add-on to the base system (plugin, browser add-on, tool) loaded through Synapse and subject to manifest, sandboxing, and risk scoring.
*Examples*: Summarizer plugin, voice assistant
*Not to be confused with*: “Agent” (which is a first-class module)

---

### F

**Facilitator Agent**
*Definition*: An agent whose purpose is to mediate or translate user requests into system actions (e.g., Alden as a task creator, or a CLI agent invoking plugins).
*Examples*: User asks Alden to summarize a session, Alden initiates plugin
*Not to be confused with*: Core (which manages only system-wide, not user-agent-specific, requests)

---

### I

**Intent**
*Definition*: The declared action, purpose, or request encoded in an MCP payload or user instruction.
*Examples*: “reflection_request”, “plugin_execute”
*Not to be confused with*: “Context” (which defines scope, not action)

---

### L

**Local Persona Memory**
*Definition*: The private, encrypted memory slice specific to a given agent/persona, stored only in Vault and never routed through Core.
*Examples*: Alden’s habit log, Mimic’s skill history
*Not to be confused with*: “Core Communal Memory”

---

### M

**MCP (Model Context Protocol)**
*Definition*: The protocol and schema governing all agent-to-agent, agent-to-core, and agent-to-plugin context exchanges in the system.
*Examples*: MCP-Lite reflection, plugin call, context negotiation
*Not to be confused with*: Vault API (used only for direct memory access)

**Memory Slice**
*Definition*: A discrete, versioned unit of stored data within Vault, scoped to a persona or communal context.
*Examples*: Alice’s tone analysis slice, Vault session log
*Not to be confused with*: “Session Log” (which may be a memory slice, but is always event-based)

---

### P

**Persona**
*Definition*: The combination of agent identity, skills, configuration, and evolving memory defining a unique participant in the Hearthlink ecosystem.
*Examples*: Alden, Alice, user-defined Mimic personas
*Not to be confused with*: “User” (human operator), “Plugin” (external code)

**Plugin**
*Definition*: Executable code (local or external) loaded through Synapse and governed by manifest, risk score, and Sentry audit; may provide new actions, UIs, or integrations.
*Examples*: Third-party summarizer, local LLM connector
*Not to be confused with*: “Agent” (which is a core module)

**Protocol Negotiation**
*Definition*: The version and feature handshake between agents, plugins, or system modules to ensure compatibility for MCP or API requests.
*Examples*: Fallback to MCP-Lite if extension not supported

---

### R

**Roundtable**
*Definition*: A session where multiple agents (and optionally, plugins) collaborate via Core, with turn-taking, scoring, and moderation.
*Examples*: Brainstorming new project names with Alden, Alice, and Mimic

---

### S

**Sentry**
*Definition*: The always-on, unkillable system guardian, logging all audit events, detecting anomalies, and enforcing policy and user overrides.
*Examples*: Incident alert, policy override
*Not to be confused with*: Vault (which is passive storage)

**Session Log**
*Definition*: An ordered, timestamped record of all activity, communications, and outcomes for a single session (roundtable, plugin, or agent event).
*Examples*: Roundtable transcript, plugin execution audit

**Slice (see Memory Slice)**

**Synapse**
*Definition*: The gateway module for all external, plugin, API, or browser extension connections; mediates plugin loading, sandboxing, and security scoring.
*Examples*: Synapse launches plugin, scores risk
*Not to be confused with*: Sentry (which audits) or Core (which orchestrates sessions)

---

### T

**Turn Policy**
*Definition*: The rules by which agent, plugin, or user comments are prioritized and sequenced in a roundtable or breakout session.
*Examples*: “Moderator”, “score-based”, “first-come”

---

### U

**User**
*Definition*: The human operator, always sovereign, able to override any system or agent action with explicit confirmation.
*Examples*: Approves/denies plugin execution, resolves Sentry incident
*Not to be confused with*: “Persona” (an agent identity)

---

### V

**Vault**
*Definition*: The secure, encrypted, local-first database for all persona and communal memory, with per-persona, session, and audit log slices.
*Examples*: Local-only memory store for Alden; communal slice for roundtables
*Not to be confused with*: Core (which orchestrates, but does not store memory)

---

**End of Platinum Hearthlink System Glossary & Taxonomy**

