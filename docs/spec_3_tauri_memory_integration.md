# SPEC-3-Tauri-Memory-Integration

## Purpose

Advance to Phase 3 by auditing all incomplete features, eliminating tech debt, and ensuring every function and component is actionable.

## Objectives

1. **Complete Feature Verification**

   * Inventory all components (Core, Synapse, Sentry, Alice, Mimic) and assert their implementation status.
   * For each missing or partial feature, define clear action items and ownership.

2. **Stupid Bug Audit**

   * Scan UI and backend logs to collect uncaught runtime errors and hook mismatches.
   * Ensure all test suites catch these issues; update tests accordingly.
   * **Specific UI Bug Fixes:**
     • Add a delete-task button in the Task Management UI and corresponding API call.
     • Ensure the "August Weekly Focus Formula" template appears when licensed.
     • Fix Local LLM settings population in SettingsManager.
     • Resolve sprite management crash by correcting hook usage in `renderSpriteManagementSettings`.

3. **Function Enactment Paths**

   * For every exported function or API endpoint, verify there is a UI or script to invoke it.
   * Add missing buttons, CLI commands, or automated jobs so nothing is orphaned.

4. **Tech Debt Elimination**

   * Remove deprecated code, simulations, and test scaffolding from production branches.
   * Identify modules with low value (no usage in 6+ months) and archive or delete.

5. **Alpha Testing Readiness**

   * Define alpha user scenarios across all modules.
   * Prepare a checklist to verify each scenario: login, CRUD operations, memory persistence, LLM responses, dashboard metrics, and settings management.

6. **Built‑In Bug Reporting System**

   * Embed an in‑app feedback module allowing alpha testers to submit bugs, feature requests, and screenshots/log bundles.
   * Route submissions to `/api/bugs` with metadata (build hash, user role, page context).
   * Provide CLI fallback (`hl bug --title --desc --attach <file>`).
   * Store reports in Vault with tagging (`bug|feedback`) and expose a Grafana panel for triage metrics.

## Deliverables

* **SPEC-3 Final Audit Document** with inventory, action items, and timelines.
* **Test Suite Enhancements** covering all previously uncaught errors.
* **UI/CLI Invocation Map** listing every function and its activation path.
* **Tech Debt Report** summarizing removals and archives.
* **Alpha Test Plan** with detailed user scenarios and acceptance criteria.

## Phase 1.6 Remediation Build Summary

All five Phase 1.5 blockers resolved; system now alpha‑ready.

| Contract                         | Status |
| -------------------------------- | ------ |
| Vault ↔ Alden Memory Integration | ✅ Pass |
| Conversation Schema Constraints  | ✅ Pass |
| RAG/CAG Memory Persistence       | ✅ Pass |
| Cross‑Agent Handoff Continuity   | ✅ Pass |
| Config Schema Alignment          | ✅ Pass |

**Key Improvements**

* **VaultManager** deterministic init, health checks, retry logic.
* **DB Migrations** fix foreign keys, idempotent agent creation.
* **RAG/CAG Pipeline** full retrieve → reason → persist, encrypted at rest.
* **Handoff System** context bundle persistence, tag preservation across Alden ↔ Alice.
* **Unified Config** JSON schema + strict env verifier.

Evidence: `alpha_readiness_test.py` logs, migration\_v1\_1, updated validation suite.

**Alpha Readiness Checklist:** All critical items now ✅.

Next Immediate Fixes: *(none – proceed to Week 2 tasks)*

## Timeline

* **Week 1:** Audit & Inventory
* **Week 2:** Test & Invocation Coverage
* **Week 3:** Tech Debt Removal & Alpha Plan

## Acceptance Criteria

* No uncaught runtime errors in alpha build.
* 100% coverage of function enactment paths.
* All deprecated code removed or archived.
* Alpha test plan approved and ready for distribution.

*SPEC-3 positions Hearthlink for external alpha testing with a clean, complete codebase.*
