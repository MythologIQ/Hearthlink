⚡ **This document is a dynamic, ever-evolving process manual—purpose-built to learn from failing forward and continuous improvement. Every lesson, challenge, and enhancement is recorded here to drive Hearthlink toward platinum-grade excellence.**

---

# Hearthlink Process Refinement – Living SOP

## Purpose

A living record of evolving standard operating procedures (SOP) for Hearthlink. Codifies modularity, traceability, review cycles, git hygiene, AI prompt discipline, and platinum-grade quality controls. All updates reflect lessons learned and continuous improvement.

---

## 1. Modular Development & Branching

* Major modules (Core, Vault, Synapse, etc.) are developed in dedicated branches (`feature/<module-name>`), created at work start.
* No direct commits to main; merges after QA/code review only.
* SOP enforced in documentation and prompts.

---

## 2. Remote Sync, Branch Management & SOP Enforcement

* All branches, commits, and tags are pushed to GitHub before merges.
* Missing branches are reconstructed and pushed as needed.
* Remote auditability is mandatory before implementation or release.
* Every correction/reconstruction is logged for traceability.

---

## 3. Regular GitHub Pushes & Versioning

* All work is committed and pushed to GitHub—never only at milestones.
* Semantic versioning (`vX.Y.Z`) and Issue/Sprint-linked commit messages.
* Pushing follows local implementation/testing of any branch.

---

## 4. Documentation & Traceability

* Every design/architecture change must be updated in system docs, blockers, supplements, or SOP.
* Issue → branch → commit → documentation update is strictly maintained.
* Open items tables track phase/feature enhancements.

---

## 5. README Hygiene: Single Root README Standard

* Only one authoritative `README.md` in the project root.
* Detailed module docs go in `/docs/` and are referenced in the README.
* All merges, audits, and onboarding check for README currency and singularity.

---

## 6. Documentation Enforcement in Prompts and Review

* Every prompt (manual or AI) must reference `/docs/` and system documentation.
* No branch or feature is "complete" until docs (including root README) are updated and cross-linked.
* Prompt templates always end with:

  > Reference the relevant `/docs/` for system and module specifics. Confirm all documentation updates before requesting review or merge.

---

## 7. AI/Agent Prompt Discipline

* Prompts to Cursor/AI reference documentation and blockers.
* Explicit instructions for branch, commit, and push.
* Intrusive/major suggestions require validation and explicit owner approval.
* Minor suggestions are auto-logged, reviewed at phase end.

---

## 8. Testing & QA Automation

* Negative/edge-case tests for every control and module before merging.
* Dedicated test plugin/module verifies plugin rails and audit features.
* QA checklists must be met before next phase advances.

---

## 9. Deferral & Scope Management

* Non-core/advanced features (multi-user, major ML, expanded personas) are deferred until the core is stable.
* No scope creep—future features cannot block/dilute platinum-grade foundation.

---

## 10. Phase-End Review & Approval Loop

* Features and design changes are reviewed at phase/sprint end.
* Urgent/architectural changes require validation prompt and explicit approval.
* All decisions, approvals, and rejections are logged with rationale.

---

## 11. Continuous Process Improvement

* Updated after every phase or process decision.
* Lessons learned, new requirements, and operational tweaks are captured here.

---

## 12. Lessons Learned & Further Refinement

### Key Lessons

* Process documentation prevents drift.
* Branching/modularity and regular pushing are non-negotiable.
* Prompt hygiene is project hygiene.
* Variance reports and approval loops are essential.
* Negative/edge-case QA is not optional.

### Next Phase Refinements

* Proactive import/dependency health checks.
* Mandatory documentation updates in every branch.
* Automated suggestion/improvement logging.
* Pre-merge owner review—always.
* Post-phase retrospectives.
* Blocker triage on critical issues.

## 13. Synapse Connection Integration SOP

* **All new Synapse connections (agents, plugins, APIs) are documented as supplements in `/docs/` using the Synapse Integration Template.**
* **Integration workflow:**

  1. *Design PRD/blueprint* in a new `/docs/SYNAPSE_<AGENT/PLUGIN>_SUPPLEMENT.md` file.
  2. *Reference the new integration in the root `README.md`* (see template below).
  3. *Cross-link* from the main Synapse blueprint to the supplement.
  4. *Implementation* occurs in its own feature branch: `feature/synapse-<agent/connection>`.
  5. *If new connection requires a custom setup/config wizard, document required steps, CLI/UI hooks, and post-merge checklist.*
  6. *Update Synapse's `config/connection_registry.json` (or equivalent) to recognize the new connection, supporting future dynamic discovery/UI setup.*
  7. *Full QA, docs, and process review before merge to main.*
* **A new connections wizard/config is recommended in Synapse's roadmap for all agent/plugin integrations.** (Planned for enhancement if not yet implemented.)

---

## 14. MCP Resource Policy Implementation SOP

* **All agent resource access must be controlled through MCP (Model Context Protocol) with explicit scoped permissions.**
* **Resource policy workflow:**

  1. *Define agent resource scope* in `/docs/MCP_AGENT_RESOURCE_POLICY.md` with explicit disk, network, workspace, and memory permissions.
  2. *Implement policy enforcement* in `src/enterprise/mcp_resource_policy.py` with security controls and audit logging.
  3. *Agent-specific policies* must include timeout limits, audit requirements, and security controls (encryption, sandbox, risk assessment).
  4. *All resource access requests* flow through MCP with validation, logging, and automatic timeout enforcement.
  5. *Security controls* are mandatory for sensitive operations (user consent, data anonymization, content validation).
  6. *Audit trails* capture all access decisions, violations, and security events for compliance and monitoring.
  7. *Integration with Sentry* ensures real-time security monitoring and incident response for policy violations.

* **Key Implementation Patterns:**
  - Zero trust principle: No default access, all permissions explicitly granted
  - Least privilege: Agents only access resources required for their function
  - Time-bound access: All permissions expire automatically
  - Comprehensive audit: Every access decision logged with full context
  - Security controls: Encryption, sandboxing, risk assessment as required
  - Violation handling: Immediate blocking, alerting, and incident creation

* **Agent Resource Scopes Defined:**
  - **Sentry:** Security monitoring (logs, alerts, policies)
  - **Alden:** User companion (workspace, goals, personal memory)
  - **Alice:** Behavioral analysis (interaction logs, research, patterns)
  - **Mimic:** Persona generation (templates, knowledge, generated content)
  - **Core:** Session orchestration (session data, coordination, communal memory)
  - **Vault:** Memory management (encrypted storage, backup, all memory slices)
  - **Synapse:** External gateway (plugins, APIs, sandboxed execution)

* **Security Controls Required:**
  - Encryption for sensitive data access
  - Sandboxing for external connections
  - Risk assessment for new connections
  - User consent for personal data access
  - Data anonymization for behavioral analysis
  - Content validation for generated content
  - Session boundaries for multi-agent operations
