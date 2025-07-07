---

> ⚡ **This document is a dynamic, ever-evolving process manual—purpose-built to learn from failing forward and continuous improvement. Every lesson, challenge, and enhancement is recorded here to drive Hearthlink toward platinum-grade excellence.**

---

# Hearthlink Process Refinement – Living SOP

## Purpose

This document is a living record of our evolving standard operating procedures (SOP) for Hearthlink development. It codifies modularity, traceability, review cycles, git hygiene, AI prompt discipline, and platinum-grade quality controls. All updates are iterative, reflecting lessons learned and continuous improvement.

---

## 1. Modular Development & Branching

* **Every major module/component** (e.g., Core, Vault, Synapse, Sentry) is developed in its own dedicated branch (e.g., `feature/core-orchestration`, `feature/vault-memory`).
* **Branches** are created at the start of each module's work and named by convention (`feature/<module-name>`).
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

## 9. Lessons Learned & Further Refinement (Phase 2+)

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

   * Missing tests or import issues in one module triggered fast corrective sprints and prevented "false sense of completion."

### Further Refinements for Next Phase

1. **Proactive Import/Dependency Health Checks**

   * Automate dependency validation and import structure checks at every sprint start (not just after test failures).
   * Add an "import health" status to every variance or status report.
2. **Mandatory Documentation Updates in Every Branch**

   * Require every feature/fix branch to include updated documentation alongside code (not just after-the-fact in main).
   * Automate docs status as a checklist item before merge.
3. **Automated Suggestion/Improvement Logging**

   * Any AI/agent-generated recommendation (even if not implemented) should be auto-logged to a running "improvements" list for later review.
4. **Pre-Merge Peer or Owner Review—Always**

   * Before any branch merges to main, mandate a checkpoint review, not just a variance report.
   * Owner/QA can spot-check both code and updated process docs.
5. **Post-Phase Retrospective**

   * Schedule a brief review at the end of each phase: what worked, what blocked us, what needs tightening next time.
   * Summarize lessons here, in `process_refinement.md`, for institutional knowledge.
6. **Standardize "Blocker Triage"**

   * As soon as a critical gap is found (security, persona, test failure), trigger a mandatory triage/priority review before further development.

---

## 11. README Hygiene: Single Root README Standard

* The project root **must contain only one authoritative `README.md` file**.
* This README provides the high-level overview, installation, system intent, quickstart, and reference pointers to `/docs/` for all module-specific or deep-dive technical docs.
* All detailed module documentation is to be maintained in `/docs/` (or submodule folders if essential), and referenced by the root README. Duplicate or legacy README files are strictly disallowed elsewhere in the repo.
* Any restructure or addition of modules must include updates to the root README and, as needed, new/updated `/docs/` content.
* All feature work, merge, and audit protocols must verify that the README is current, singular, and referenced by contributors and automation.
* The README hygiene policy is enforced in prompts, review checklists, and merge gates for every phase.

---

## 12. Documentation Standardization (2025-07-07)

### README Standardization

**New SOP:** Single root README.md as the authoritative project documentation.

**Rationale:**
- Eliminates documentation fragmentation and version conflicts
- Provides single source of truth for project overview
- Reduces maintenance overhead and merge conflicts
- Ensures consistent project presentation

**Implementation:**
- **Root README.md:** Comprehensive project documentation, setup, and usage
- **Module-specific docs:** Detailed technical documentation in `docs/` directory
- **Process docs:** Living SOP and process refinement in `docs/process_refinement.md`
- **Implementation guides:** Feature-specific documentation in `docs/` directory

**Benefits:**
- **Reduced merge conflicts:** Single README eliminates branch merge conflicts
- **Clear hierarchy:** Root README for overview, docs/ for technical details
- **Easier maintenance:** Single file to update for project changes
- **Better discoverability:** New contributors find everything in one place

**Documentation Structure:**
```
/
├── README.md                    # Project overview, setup, usage
├── docs/
│   ├── process_refinement.md    # Living SOP and lessons learned
│   ├── PLATINUM_BLOCKERS.md     # Security and compliance requirements
│   ├── MIMIC_IMPLEMENTATION_GUIDE.md  # Feature-specific guides
│   └── [other technical docs]   # Detailed technical documentation
└── src/
    └── [modules]/               # Code with inline documentation
```

### Process Enhancements

1. **README Updates:** All project-level changes must update root README.md
2. **Technical Documentation:** Detailed implementation docs go in `docs/` directory
3. **Merge Conflict Prevention:** Single README eliminates documentation conflicts
4. **Documentation Review:** README updates reviewed with feature merges

---

*Latest update: 2025-07-07 (Documentation standardization and README consolidation)*

---

## 10. Remote Sync, Branch Reconstruction, and Platinum SOP Enforcement

### Context

In early phases, the GitHub remote was not configured, and no branches or history were pushed. This created an audit and traceability gap in the remote repository.

### SOP Correction and Action Items

1. **Immediate Remote Sync Required:**

   * All branches, commits, and tags from local development must be pushed to GitHub before any new merges or approvals.
   * Remote traceability is now a non-negotiable precondition for further work or release.
2. **Branch Reconstruction (if needed):**

   * If branches for previous features/phases do not exist, reconstruct them from commit history using `git checkout -b <branch> <commit-hash>`, then push to remote.
   * Ensure commit history and documentation for each phase/module is present and visible in GitHub.
3. **SOP Enforcement:**

   * Remote sync and branch management is explicitly part of the process going forward.
   * Every new feature branch must be created locally, pushed to GitHub, and validated before any implementation work begins.
   * No code is merged or released without full remote auditability.
4. **Documentation Update:**

   * Log any correction or reconstruction in this document for historical traceability.

### Prompts for Automated Correction (for Cursor or AI assistant)

---

*Latest update: 2025-07-07 (Phase 2 lessons learned and further refinements appended)*
