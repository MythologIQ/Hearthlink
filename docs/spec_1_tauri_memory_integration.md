# SPEC-1-Tauri-Memory-Integration

## Background

We have recently completed a full migration from Electron to Tauri to achieve a more stable desktop application, eliminating previous port and startup failures.

The core of our system relies on an encrypted database implementing Retrieval-Augmented Generation (RAG), Chain-of-Thought Augmentation (CAG), and memory slicing with on-demand knowledge graphing (“Vault”). This Vault provides persistent learning across sessions.

Our LLM agent, **Alden**, is powered by the Llama 3.2 3B model. While Alden handles basic interactions, its reasoning performance feels less fluid compared to higher-tier models, and we need to maintain or reduce current resource usage while improving “human-like” reasoning.

Dashboard components are in place for monitoring system metrics and user interactions, but they are not reflecting real-time data despite backend confirmation that logging and data collection are functioning correctly.

Finally, we aim to integrate more effectively with GitHub workflows to streamline development, but are experiencing authentication challenges in CI/CD and are underutilizing GitHub’s capabilities.

---

## Requirements

### Must Have

* **Persistent Memory & Vault Integration:** Session-to-session memory stored in an encrypted Vault-backed database with RAG, CAG, and memory slicing.
* **Shared & Alden Memory Architecture:** Core Vault service maintains shared memory; the Alden adapter maintains its own memory slice.
* **Alden Memory Schema:** Long-term and session-specific tables for Alden, with tagging and retrieval mechanisms.
* **LLM Model Selection:** Adopt **Llama 3.5 micro** as the definitive model, providing improved fluid reasoning within the same resource footprint as Llama 3.2 3B.
* **Real-Time Dashboards:** Accurate live metrics for session logs, memory usage, and inference latency.
* **GitHub Integration & CI/CD:** Secure authentication, automated linting, testing, and Tauri builds via GitHub Actions.

### Should Have

* **Vault Key Rotation:** Automated key rotation policy for the Vault service.
* **Legacy File Archiving:** Archive the following obsolete dirs/files to `/archives`:

  * `.claude`, `.claude-context.md`, `.failsafe`, `Deviation`
  * `Archive/`, `ArchiveCode/`
  * Compiled assets: `dist/`, `releases/`, `hearthlink_data/`, `userData/`, `logs/`
  * Build/deploy artifacts and scripts: `deploy/`, `docker/`, batch/VBS scripts (`*.bat`, `*.vbs`), `.exe` binaries (`hearthlink.exe`)
  * Python/JS caches: `__pycache__/`, `api_data/`, `ipcHandlers/`
  * Redundant config/env files: `.env.development`, `.env.local`, `.env.production`, `.mcp.json`
* **Environment File Consolidation:** Merge and document environment configs into a canonical `.env` with usage guidelines.
* **Automated Memory Sync:** Sync strategies between Vault and Alden’s memory slice with conflict resolution.
* **Memory Debug Tools:** Dashboard widgets for inspecting Alden’s memory states.
* **Monorepo Layout:** Clear structure with `/apps/`, `/services/`, `/packages/`, and `/archives/`.

### Could Have

* **Runtime LLM Swapping:** Hot-swap models without downtime.
* **Advanced Analytics:** Trends on memory growth, retrieval hit rates, and reasoning metrics.
* **GitHub Workflow Templates:** Reusable CI/CD action templates for common tasks.

### Won’t Have

* **Cloud-Only LLM Hosting:** All inference remains on-prem/local.
* **Unencrypted Storage:** Memory data remains encrypted at rest.

---

## Method

> **Note:** This is an incremental enhancement of the existing repo—no full structural rewrite is required. Migrate modules in priority order.

1. **Core Memory & Vault Service**

   * **Responsibilities:** Encrypted Vault DB (RAG/CAG), key management, memory slicing, graph generation.
   * **Tech:** Rust-based Tauri plugin (gRPC/REST), PostgreSQL + PGVector, Neo4j, HashiCorp Vault.

2. **Alden Adapter Service**

   * **Responsibilities:** Fetch context from Vault, perform inference, push new memory back.
   * **Tech:** Node.js microservice with `llama.cpp`/`ggml` runtime; optional Claude middleware.

3. **Dashboard Pipeline**

   * **Responsibilities:** Collect Prometheus metrics from services; embed Grafana in Tauri UI.

   * **UI Evaluation & Fine-Tuning:**

     1. **Audit Existing Dashboards:** Catalog all current UI widgets, panels, and metrics exposed in the Tauri app.
     2. **User Feedback Sessions:** Run short interviews with internal users to identify which metrics are most actionable and which are confusing or redundant.
     3. **Metric Relevance Mapping:** Map each dashboard element to a specific user task (e.g., diagnosing high inference latency, verifying memory sync).
     4. **Content Optimization:** Remove low-value charts, condense panels to surface top‑10 key indicators (session throughput, vector-store health, sync conflicts).
     5. **UI Polishing:** Ensure charts use clear labels, tooltips, and contextual help text. Embed drill-down links to logs or detailed views.

   * **UI Component Exports:** Confirm existence of shared UI components (`ui/card.tsx`, `ui/button.tsx`, `ui/badge.tsx`, `ui/tabs.tsx`, `ui/alert.tsx`) with proper named exports.

   * **Icon Imports:** Update Lucide imports (e.g. `import RefreshCw from 'lucide-react';`) to match package exports.

   * **Fetch Timeout Handling:** Replace unsupported `timeout` property on `fetch()` calls with `AbortController` or switch to `axios` for timeout support.### Dashboard Audit Results

> **Note:** Panel titles and metrics must be programmatically extracted from the JSON dashboard definitions to ensure accuracy. We will generate a script to parse all `monitoring/grafana/dashboards/*.json` files and produce a canonical list of panels and their data sources.

**Next Steps:**

1. **Extract Panel Metadata:** Use a small Python script to read each dashboard JSON and list `panels[].title` and associated `targets[]`. Example:

```python
import json
import glob

def extract_panels(path_pattern="monitoring/grafana/dashboards/*.json"):
    panels = []
    for file in glob.glob(path_pattern):
        data = json.load(open(file))
        for panel in data.get('dashboard', {}).get('panels', []):
            title = panel.get('title')
            targets = panel.get('targets', [])
            metrics = [t.get('expr') or t.get('metric') or t.get('refId') for t in targets]
            panels.append({'file': file, 'title': title, 'metrics': metrics})
    return panels

if __name__ == '__main__':
    for p in extract_panels():
        print(f"{p['file']}: {p['title']} -> {p['metrics']}")

---

## UI Component Audit Results

**Overview:** Below is a concise audit summary for all front-end components, grouped by persona or function. Each entry lists *key metrics displayed*, *primary user task*, and *top 2–3 actionable enhancements*.

### Alden
- **Panels:** Chat interface, Memory Usage, System Status
- **Tasks:** Context retrieval, inference feedback, memory health
- **Enhancements:** Show live memory hit rates; surface pending command queue length; add drill-down from status chips to detailed logs

### Alice
- **Panels:** Mood & Cognitive Patterns, Intervention Metrics, Session Duration
- **Tasks:** Behavioral analysis, intervention tracking, engagement monitoring
- **Enhancements:** Add mood history sparkline; chart intervention acceptance over time; link patterns to raw session transcripts

### Sentry
- **Panels:** Intrusion Attempts, Access Denials, Threat Feed Freshness
- **Tasks:** Security monitoring, alert prioritization, feed health checking
- **Enhancements:** Break out threat severity levels; show incident response times; drill into failed authentication endpoints

### Mimic
- **Panels:** Perplexity Distribution, Similarity Scores, Feedback Counts
- **Tasks:** Response fidelity evaluation, user satisfaction tracking
- **Enhancements:** Add percentile markers (p10/p90); correlate similarity with feedback; show response quality trends over time

### Core & Vault
- **Panels:** Vault Memory Counts, Storage Usage, Backup & Integrity Status
- **Tasks:** Memory persistence monitoring, storage planning, data integrity checks
- **Enhancements:** Chart storage growth trends; filter memories by type; alert on integrity-check failures

### Shared Utilities
- **Panels:** Task Dashboard, Calendar, Health Monitor, Circuit Breaker, Settings, LLM Metadata Monitor
- **Tasks:** Productivity overview, scheduling, system health diagnostics, fail-safe monitoring, configuration management, LLM performance tracking
- **Enhancements:** Add trend lines (e.g., productivity over time); visualize calendar slot utilization; derive an overall health score; show circuit-breaker state history; enable live validation of settings changes; **track LLM metadata** (confidence scores histogram, average accuracy over recent sessions, latency vs. confidence scatterplot)

This streamlined format focuses on what matters most—ensuring dashboards surface critical insights for each persona and core service, with clear, implementable next steps.

---

## Additional Missing Insights

Beyond LLM metadata, consider adding:

- **RAG/CAG Retrieval Metrics:**
  - Retrieval Hit Rate by memory type (short-term, long-term, graph)  
  - Average number of context chunks fetched per query  
  - Graph traversal depth statistics for knowledge graph expansions

- **Memory Slice Health:**
  - Count of memory slices per category over time (episodic, semantic, procedural)  
  - Memory slice expiry/removal rates  
  - Fragmentation metrics indicating uneven slice distribution

- **Chain-of-Thought Analysis:**
  - Average reasoning chain length  
  - Confidence score per chain step  
  - Completion vs. abort rates of multi-step queries

- **Agent Interaction Metrics:**
  - Cross-agent handoff counts (e.g. queries passed from Alden to Sentry)  
  - Average session duration per persona  
  - Agent utilization heatmap across working hours

- **Error & Exception Dashboards:**
  - Logged exception counts by type  
  - Alert spikes for unusual error patterns  
  - Correlation of errors with recent deployments or config changes

Including these will ensure full observability of your RAG/CAG pipeline, memory system health, and multi-agent workflows.

---

## Next Phase: End-to-End Context Retrieval Validation

We’ve enriched our dashboards and UI interactions. The next critical task is to verify the complete flow from user input through Vault retrieval, LLM inference, and memory push:

1. **Test Scenarios:**
   - **Simple Query:** Retrieve a known fact, infer response, push a new memory slice.
   - **Edge Case:** Missing memory context—ensure fallback to default behavior.
   - **Multi-Step Dialogues:** Chain-of-thought prompts that span multiple retrievals.
   - **Agent Handoff:** Query routed from Alden → Sentry → Alden, verifying memory consistency.

2. **Validation Criteria:**
   - **Accuracy:** Response matches expected answer within confidence threshold.
   - **Persistence:** New memory slice appears in Vault and is retrievable in the next session.
   - **Performance:** Total round-trip latency under 500 ms (on local hardware).
   - **Error Handling:** Graceful fallback when Vault is unreachable or LLM errors occur.

3. **Implementation Steps:**
   - **E2E Test Suite:** Build a Playwright/Puppeteer script that automates desktop UI interactions.
   - **API Smoke Tests:** Use pytest or Postman to hit `/api/semantic/retrieve`, `/api/llm/infer`, `/api/semantic/store` in sequence.
   - **CI Integration:** Add these tests to GitHub Actions under a new workflow `e2e-validation.yml`.

4. **Deliverable:**
   - A set of passing E2E and API tests demonstrating end-to-end context retrieval → inference → memory-push.
   - A summary report with metrics and any detected regressions.

Once this phase is complete, we can confidently move into packaging the full Tauri installer and opening to live testers.

```

REFER to Spec-2 documentation for the latest