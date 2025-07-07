## Purpose

To define a universal, explicit, and evolvable schema and operational contract for agent-to-agent, agent-to-system, and cross-module context exchanges within Hearthlink. The MCP is the canonical protocol by which all memory, intent, feedback, and meta-context flows are described, validated, and versioned—enabling secure, auditable, and future-proof interoperability.

---

## 1. Protocol Philosophy

- **Explicit Boundaries:** All context and data passed between agents, plugins, and modules is strictly schema-bound and versioned.
- **Composable & Minimal:** Start with MCP-Lite (intent, context anchor, memory reference, feedback). Extensions are opt-in and versioned.
- **Auditability:** Every MCP transaction is logged by Sentry with request, response, and agent/user metadata.
- **No Direct Local Memory Mediation:** Local persona memory is never routed through Core unless user initiates a communal memory operation.
- **Zero Trust, User-First:** Every cross-agent or external context exchange is authenticated, logged, and user-reviewable.

---

## 2. Protocol Scope

- **In-Scope:**
  - All agent-to-agent or agent-to-system context and memory references
  - Session/context anchoring for Core Communal Memory
  - Plugin or external agent interactions via Synapse
  - Memory slice migration or protocol negotiation
- **Out-of-Scope:**
  - Direct agent-to-Vault local memory operations (these use native Vault APIs, not MCP)
  - UI/UX-only flows with no system memory/intent transfer

---

## 3. Protocol Schema

**All MCP payloads are JSON or YAML (with JSON as default wire format).**

### 3.1 MCP-Lite: Minimal Transaction

```
json
```

CopyEdit

`{ "mcp_version": "1.0.0", "msg_id": "uuid-12345", "timestamp": "2025-07-06T22:30:00Z", "from_agent": "alden", "to_agent": "alice", "context_anchor": "session-0099", "intent": { "type": "reflection_request", "description": "Review recent goal milestone" }, "memory_refs": [ { "vault_id": "alden-slice-001", "slice_type": "habit-streak", "access_scope": "read-only" } ], "feedback": { "confirmation": true, "status_flag": "pending" }, "extensions": null }`

---

### 3.2 Full Field Definitions

| FieldTypeRequiredDescription |        |          |                                                                   |
| ---------------------------- | ------ | -------- | ----------------------------------------------------------------- |
| mcp\_version                 | string | yes      | Protocol version, e.g. "1.0.0"                                    |
| msg\_id                      | string | yes      | Unique transaction/request ID (UUID)                              |
| timestamp                    | string | yes      | ISO8601 UTC timestamp                                             |
| from\_agent                  | string | yes      | Originating persona/module name                                   |
| to\_agent                    | string | yes      | Destination persona/module name                                   |
| context\_anchor              | string | yes      | Session, event, or object this context references                 |
| intent                       | object | yes      | { type, description, [params] }                                   |
| memory\_refs                 | array  | optional | References to Vault memory slices/objects by ID/type/scope        |
| feedback                     | object | optional | Status/confirmation, rejection, error, or meta-response           |
| extensions                   | object | optional | Arbitrary extension fields for new features, versioned sub-schema |

---

## 4. Operation & Flow

### 4.1 Request Lifecycle

1. **Initiation:**\
   Agent/module creates a signed MCP payload (JSON).
2. **Transmission:**\
   Payload delivered via Core (for communal/session context) or Synapse (for plugins/external).
3. **Validation:**\
   Receiving agent/system checks version, schema, intent, and permissions.\
   Rejects or requests fallback on error/mismatch.
4. **Execution:**\
   Action, review, or reflection performed using referenced context/memory only if permissioned.
5. **Feedback:**\
   Response MCP sent with feedback object and any outputs/next-action hints.
6. **Logging:**\
   Every MCP transaction is Sentry-logged (with redaction for sensitive fields as needed).

---

### 4.2 Security & Error Handling

- All cross-agent/system MCP exchanges require mutual authentication (agent keys, session tokens).
- Invalid, unauthorized, or ambiguous MCPs are rejected, logged, and surfaced to user/admin for review.
- Extension fields must be ignored by incompatible agents/modules; fallback to last supported schema.
- MCP traffic is always encrypted in transit (local or remote).

---

### 4.3 Versioning & Negotiation

- Every MCP includes a version header.
- If version mismatch, protocol negotiation sequence is triggered:
  - Fallback to last mutually supported version.
  - If not possible, reject with feedback (error, reason, expected version).
- All extensions are opt-in, namespaced, and versioned (e.g., `"extensions": { "rationale-v2": { ... } }`).

---

## 5. Protocol Extensions (Examples)

- **Agent Analytics:**\
  `"extensions": { "persona_analytics": { "openness": 74, "agreeableness": 82 } }`
- **Session Rules:**\
  `"extensions": { "session_rules": { "max_agents": 8, "turn_policy": "moderator" } }`
- **Plugin/External API:**\
  `"extensions": { "external_call": { "plugin_id": "summarizer-v2", "result_ref": "plugin-log-77" } }`

---

## 6. Reference Implementation and Testing

- MCP validator provided as CLI tool and Node/Python module.
- All agents/modules must include test harness for all supported MCP versions and fallbacks.
- Protocol evolution follows strict versioning (semver); breaking changes require migration guide.
- Full transaction logs are reviewable in Sentry.

---

## 7. Sample Flows

### 7.1 Cross-Agent Reflection Request (Alden → Alice)

1. Alden sends MCP:
   - Intent: `"type": "reflection_request"`
   - Memory Ref: `"alden-slice-001"`
2. Core validates, forwards to Alice.
3. Alice reviews context, sends feedback (confirmation + insight).
4. All steps logged; user can review in session audit.

### 7.2 Plugin Operation (Core → Synapse → External Plugin)

1. Core assembles MCP, referencing session context and plugin permissions.
2. Synapse checks manifest, permissions, risk score.
3. Plugin invoked; output/feedback attached as `"extensions"`.
4. All traffic logged by Sentry, with audit trail.

---

## 8. Security, Privacy, and User Control

- MCP payloads are always auditable and exportable.
- All agents honor “redact” flags; user can mask fields from audit/UI if desired.
- No memory migration, export, or cross-agent context is permitted without user-initiated action and full logging.

---

## 9. Protocol Governance

- MCP spec is version-controlled in public repo with migration docs and deprecation schedule.
- Proposed extensions or changes must be RFC’d, reviewed, and backward-compatible unless major version bump.
