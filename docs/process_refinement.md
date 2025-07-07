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

Latest update: 2025-07-07 – Logically reorganized and synchronized, platinum standards fully enforced.

