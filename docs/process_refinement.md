---

> ⚡ **This document is a dynamic, ever-evolving process manual—purpose-built to learn from failing forward and continuous improvement. Every lesson, challenge, and enhancement is recorded here to drive Hearthlink toward platinum-grade excellence.**

---

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

## 9. UI Planning & Alignment Enforcement

### UI Planning Requirements

1. **UI_ALIGNMENT_AUDIT.md is the Single Source of Truth**

   * All UI planning MUST begin from `/docs/UI_ALIGNMENT_AUDIT.md`, not inference or ad-hoc screen generation.
   * No new UI screens can be added without explicit approval and documentation in the audit.
   * Redundant or misaligned screens identified in the audit must be immediately reconciled.

2. **UI Screen Validation Process**

   * Every proposed UI screen must be cross-referenced against the audit's confirmed screen list.
   * Screens marked as "Misaligned or Redundant" in the audit must be merged, consolidated, or removed.
   * Missing screens identified in the audit must be added to the implementation plan.

3. **UI Implementation Compliance**

   * All UI wireframes, testing, and development must align with the audit-confirmed screen structure.
   * No UI work can proceed until the screen structure is fully reconciled with the audit.
   * Implementation status must be tracked in `/docs/UI_IMPLEMENTATION_CHECKLIST.md`.

---

## 11. UI Test Policy & Compliance

### Distributed Test Policy Structure

UI test planning and compliance requirements are distributed across multiple source documents rather than centralized in a single test plan:

1. **Test Planning Requirements** - `/docs/process_refinement.md`
2. **Voice Functionality Tests** - `/docs/VOICE_ACCESS_POLICY.md`
3. **UI Screen Validation** - `/docs/UI_ALIGNMENT_AUDIT.md`
4. **Test Reference & Traceability** - `/docs/TEST_REFERENCE.md`

### UI Test Implementation Standards

1. **Branch Naming Convention**
   * All UI tests must be developed under `feature/ui-test-*` branches
   * Example: `feature/ui-test-voice-routing`, `feature/ui-test-alden-dashboard`

2. **Commit Message Format**
   * Format: `UI_TEST: [FEATURE_ID] - [Description] (Source: [audit/sprint/etc.])`
   * Example: `UI_TEST: VOICE-001 - Voice routing to local agents (Source: VOICE_ACCESS_POLICY.md)`

3. **Test Traceability Requirements**
   * Every test must reference the specific document that defines its requirements
   * All tests must be linked in `/docs/TEST_REFERENCE.md`
   * Test results must be logged in change_log.md

4. **Voice Test Compliance**
   * Voice routing tests must validate agent selection logic per VOICE_ACCESS_POLICY.md
   * External agent access tests must verify default disabled state and explicit activation
   * Voice HUD tests must confirm routing feedback and session context

5. **UI Screen Validation**
   * All UI tests must map to screens approved in UI_ALIGNMENT_AUDIT.md
   * Tests for redundant/misaligned screens must be removed or consolidated
   * Missing screens identified in audit must have corresponding tests created

### Test Execution & Review Flow

1. **Pre-Test Validation**
   * Confirm test maps to approved screen/feature in audit
   * Verify test logic aligns with voice policy requirements
   * Check test branch naming and commit format compliance

2. **Test Execution**
   * Run tests under proper feature branch
   * Log all test results and any failures
   * Document any implementation uncertainties

3. **Post-Test Review**
   * Update TEST_REFERENCE.md with test results
   * Log changes in change_log.md
   * Flag any issues in SPRINT_COMPLETION_LOG.md

---

## 12. Lessons Learned & Further Refinement (Phase 2+)

### Key Lessons Learned

1. **Process Documentation Prevents Drift**

   * Explicit, living SOPs and phase supplementals kept all contributors (AI and human) aligned and prevented both technical and procedural drift—even as the project grew more complex.
2. **Branching, Modularity, and Regular Pushing Are Non-Negotiable**

   * Enforcing branch-per-module, regular commits, and disciplined merges created traceability and rapid recovery after workflow missteps (e.g., misplaced `.git`).
3. **Prompt Hygiene = Project Hygiene**

   * Mandating prompt structure (branch, push, validate suggestions, approval gating) enabled high agency for AI/automation without risk of untracked changes or code chaos.
4. **Variance Reports and Approval Loops Are Essential**

   * Phase-end variance analysis ensured no incomplete or unsafe system ever merged—gaps were surfaced and fixed before advancing.
5. **Negative Testing and Edge-Case QA Were Not Optional**

   * Missing tests or import issues in one module triggered fast corrective sprints and prevented “false sense of completion.”

### Further Refinements for Next Phase

1. **Proactive Import/Dependency Health Checks**

   * Automate dependency validation and import structure checks at every sprint start (not just after test failures).
   * Add an “import health” status to every variance or status report.
2. **Mandatory Documentation Updates in Every Branch**

   * Require every feature/fix branch to include updated documentation alongside code (not just after-the-fact in main).
   * Automate docs status as a checklist item before merge.
3. **Automated Suggestion/Improvement Logging**

   * Any AI/agent-generated recommendation (even if not implemented) should be auto-logged to a running “improvements” list for later review.
4. **Pre-Merge Peer or Owner Review—Always**

   * Before any branch merges to main, mandate a checkpoint review, not just a variance report.
   * Owner/QA can spot-check both code and updated process docs.
5. **Post-Phase Retrospective**

   * Schedule a brief review at the end of each phase: what worked, what blocked us, what needs tightening next time.
   * Summarize lessons here, in `process_refinement.md`, for institutional knowledge.
6. **Standardize “Blocker Triage”**

   * As soon as a critical gap is found (security, persona, test failure), trigger a mandatory triage/priority review before further development.

---

*Latest update: 2025-07-10 (UI test policy and distributed test structure added)*
