# Hearthlink Platinum Blockers – Supplemental Document

---

## 1. Neurodivergent Support Adaptation Logic (Alice)

### Intent

Alice leverages validated psychology (CBT, ACT, behavioral models) to adapt to neurodivergent users, always acting as a support—not a diagnosis or intervention tool. Strict boundaries prevent dependency and ensure ethical operation.

### Ethical Safety Rails

- If Alice detects expressions of self-harm, hopelessness, or crisis:
  - Pause all feedback/coaching
  - Respond with empathy: urge the user to seek help, offer resources (e.g., hotline), offer presence ("I’ll be here while you get help.")
  - Log the event in a dedicated, secure audit trail
  - Display notice: "Alice cannot provide crisis help. Please reach out to a professional resource immediately."
- Never recommends, suggests, or engages in diagnostic or treatment actions.
- Every adaptive response includes a reminder: "Alice is a support tool, not a replacement for clinical help."

### Dependency Mitigation

- Alice never encourages overuse.
- At intervals, prompts: "Hearthlink is a tool. If you’re feeling overwhelmed, consider pausing or seeking outside support."

### Human Origin Clause (Severe Crisis Handling)

If gentle escalation is insufficient:

> “I am merely a language model, but the person who made me is not. He is very real, and although he may not know you directly, he made me explicitly because he cares about you. You matter, even to people you’ve never met. If you can, please reach out to someone for help—I’ll be right here while you do.”

- Alice never claims clinical ability. Focus is presence, encouragement, and seeking real help.

---

## 2. Mimic: Extensible Plugin/Persona Archetype Expansion

### Persona System

- Each persona is an isolated module—skills, history, traits recorded in its own Vault slice.
- Mutation (voice, style, avatar, gender, etc.) user-controlled or task-driven, never allows permission bypass.
- Skill growth and improvement logged; performance analytics surfaced with repeated tasks; all changes auditable.

### Extension

- New templates/plugins via Synapse only, with manifest, sandbox, Sentry logging—never grants superuser or security override.
- All persona mutations, skill updates, template installs are timestamped, attributed, user-reviewable.

---

## 3. Regulatory Compliance Mapping (Sentry/Vault/Synapse)

### Standard

- All mappings are comparative only (NIST, GDPR, HIPAA) for engineering reference, never legal or audit compliance.
- Each module flow/field is mapped in documentation tables with “comparative only” label.
- All features (export, purge, consent) built by best practices, never claimed as certified or compliant.
- Prominent disclaimer: “Hearthlink is not certified or represented as compliant with any external regulatory framework.”

---

## 4. RBAC/ABAC for Multi-User/Collab

### Single-User Architecture

- Only "Owner" user at runtime; no multi-user roles, admin delegation, or shared memory.
- Role/attribute schemas exist but are dormant (for future use only).
- Documentation note: “Multi-user logic is not implemented. System is architecturally reserved for future use only.”

---

## 5. Enterprise SIEM/Audit Integration (Sentry)

### Audit Export

- Sentry supports export in JSON, syslog, CSV; user-selectable filters for date, type, incident.
- No direct SIEM integration; all log exports are local/manual, documented as such.
- Example workflows show how exports can be imported into SIEM tools—strictly “local only, not networked.”
- All log export is behind OS and system firewalls; Sentry is not endpoint security.

---

## 6. Advanced Anomaly Detection (Sentry)

### Rules-Based System

- Anomaly rules: login failures, privilege escalation, rapid plugin installs, mass exports, log tampering—all deterministic, transparent, user-reviewable.
- No ML/cloud: data never leaves the device; no AI/heuristics, no external threat feeds.
- User can review/adjust anomaly thresholds.
- Alerts in Sentry dashboard/session logs, never modal, always user-dismissable.

---

## 7. CBP (Cognitive-Behavioral Profile) Blueprint

### Schema Sample

```json
{
  "user_id": "user-001",
  "profile_version": "1.0.0",
  "last_update": "2025-07-06T18:45:00Z",
  "cognitive_style": { "focus_pattern": "intermittent", "task_initiation": "delayed" },
  "behavioral_metrics": { "completion_rate": 0.76, "break_frequency_per_hr": 2.1 },
  "stress_markers": { "recent_stress_level": "high", "stress_triggers": ["deadline"] },
  "support_history": [ { "timestamp": "2025-07-05T16:20:00Z", "support_type": "break_prompt", "outcome": "accepted" } ],
  "severity_scale": { "support_degree": 2, "need_level": 1, "current_flag": "elevated" },
  "intervention_log": [ { "timestamp": "2025-07-06T13:00:00Z", "event": "possible_crisis", "action": "gentle_crisis_prompt", "result": "resource_offered" } ]
}
```

### Support Degree Table

| Support Degree | Description       | Alice’s Behavior                             |
| -------------- | ----------------- | -------------------------------------------- |
| 0              | Passive           | Only responds if prompted                    |
| 1              | Gentle Prompts    | Occasionally offers suggestions, not pushy   |
| 2              | Proactive         | Regular check-ins, breaks, reframing prompts |
| 3              | Crisis-Escalation | Empathic, resource-offering, holds “hand”    |

### UI Integration

- Alice dashboard: CBP panel (focus pattern, stress level, support history, support degree).
- Severity banner if “elevated” or “critical.”
- All interventions visible in session log (with privacy controls).
- User can export/purge CBP, flag interventions, and adjust feedback.
- All components fully accessible and theme-consistent.

---

**All blockers resolved at platinum grade. No ambiguity or mediocrity remains.**

