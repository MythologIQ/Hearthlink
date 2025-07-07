# Hearthlink Process Refinement – Living SOP

## Purpose

This document is a living record of our evolving standard operating procedures (SOP) for Hearthlink development. It codifies modularity, traceability, review cycles, git hygiene, AI prompt discipline, and platinum-grade quality controls. All updates are iterative, reflecting lessons learned and continuous improvement.

---

## 1. Modular Development & Branching

* **Every major module/component** (e.g., Core, Vault, Synapse, Sentry) is developed in its own dedicated branch (e.g., `feature/core-orchestration`, `feature/vault-memory`).
* **Branches** are created at the start of each module’s work and named by convention (`feature/<module-name>`).
* **Merges** into `main` or `develop` occur *only after* QA and code review.
* **No direct commits to main.**
* **SOP is enforced in both project documentation and development prompts.**

---

## 2. Regular GitHub Pushes & Versioning

* **Every meaningful implementation step** (feature complete, bugfix, refactor) is committed and pushed to GitHub, not just at project milestones.
* **Commit messages** must reference Issues/Sprints (e.g., `feat(core): add roundtable logic #13`).
* **Pushing is a default step** after completing local implementation and testing of any branch.
* **Release versions** are tagged per semantic versioning (e.g., `v0.2.1`).

---

## 3. AI/Agent Prompt Discipline

* **All prompts to Cursor or AI assistants:**

  * Reference system documentation and platinum blockers.
  * Include explicit branch, commit, and push instructions where module work is involved.
  * For major suggestions or intrusive changes, require a *validation of concept* before approval:

    * Alignment with platinum blockers and SOP
    * Impact on current phase/sprint goals
    * Logging and audit requirements
  * No implementation of major changes without explicit approval.
* **Minor suggestions** (refactors, style) may be auto-logged and reviewed at phase/sprint end.

---

## 4. Documentation & Traceability

* **Every architectural/design change** must be reflected in the relevant documentation (system docs, blockers, phase supplements, or this SOP).
* **Traceability** is maintained from Issue → branch → commit → documentation update.
* **Open items tables** are used to track unresolved and active enhancements for each phase.

---

## 5. Phase-End Review & Approval Loop

* **Major features and design changes** are primarily reviewed and approved at phase/sprint end.
* **Any urgent/architecturally significant suggestions** encountered during a phase require a validation prompt and explicit approval before implementation.
* **All approved changes are logged, and rejected suggestions are documented with rationale.**

---

## 6. Testing & QA Automation

* **Negative and edge-case testing** is mandated for every control and module before merging.
* **A dedicated test plugin/module** is used to verify plugin rails and audit features.
* **QA checklists from documentation** must be satisfied before advancing to the next phase.

---

## 7. Deferral and Out-of-Scope Management

* **Non-core/advanced features** (multi-user, regulatory certification, ML anomaly detection, major UI or persona expansions) are marked as out-of-scope and deferred until foundation is proven stable.
* **No scope creep**—future features cannot block or dilute platinum-grade core foundation.

---

## 8. Continuous Process Improvement

* This document is updated after every phase or critical process decision.
* Lessons learned, new requirements, and all operational tweaks are captured here to institutionalize best practices.

---

*Latest update: 2025-07-07 (Phase 2 launch, modular branching/push enforcement, validation prompts for major AI suggestions, full QA traceability enforced)*
