# ![Hearthlink](https://github.com/user-attachments/assets/a4ef30dd-d0f0-4150-8eb1-f7945c2f6897)

> ⚡ **This README is the authoritative project overview for Hearthlink. All module and test documentation is found in `/docs/` or per-module folders. Please keep this README as the single source of truth.**

---

# Hearthlink

Hearthlink is a local-first, persona-aware AI companion framework designed for collaborative, ethical, and privacy-respecting AI orchestration on your desktop.

## 🔥 Overview

- **Persona-Aware**: Evolutionary and behavioral AI companions (Alden, Alice, Mimic)
- **Modular**: Every major feature is its own independently versioned, audited module
- **Privacy-First**: Local encrypted memory, no forced cloud, full user control
- **Platinum-Standard Safety**: Ethical rails, audit trails, dependency mitigation
- **Zero-Trust Security**: Sentry oversight, plugin sandboxing, no auto-internet calls

## 🏗️ System Architecture

**Core Modules:**
- **Alden** – Evolutionary Companion AI
- **Alice** – Behavioral/Cognitive Support
- **Mimic** – Dynamic Persona Engine
- **Vault** – Persona-Aware Secure Memory Store
- **Core** – Communication Switch & Moderator
- **Synapse** – Secure Plugin/API Gateway
- **Sentry** – Security, Compliance, Oversight

> **See [`/docs/hearthlink_system_documentation_master.md`](./docs/hearthlink_system_documentation_master.md) for full architecture diagrams and system flow.**

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10+ (primary target), macOS, or Linux

### Installation

```bash
git clone https://github.com/WulfForge/Hearthlink.git
cd Hearthlink
python src/main.py
Logs:
Windows: %LOCALAPPDATA%\Hearthlink\logs\hearthlink.log
Unix-like: ~/.hearthlink/logs/hearthlink.log
(Automatic directory creation, 10MB rotation, 5 backup files)

Tests:

python tests/test_logging.py
See /docs/ for complete test suites and QA checklists.

🌟 Key Features
Global Orchestration: Run background across all processes (desktop, terminal, system tray)

Alice: Empathic, neurodivergent-aware support, non-clinical

Alden: Evolutionary feedback, context-tracking, LLM integration

Mimic: Extensible persona, plugin system, audit sandbox

Vault: Secure, encrypted, persona & communal memory

Core: Multi-agent orchestration, roundtable, session management

Sentry: Local-only security, audit, anomaly detection

Synapse: Plugin manifest system, sandboxed external API

🛡️ Compliance & Safety
PLATINUM_BLOCKERS.md: See /docs/PLATINUM_BLOCKERS.md for all compliance, ethics, and neurodivergent support standards

User Sovereignty: User is always in control

MIT License: Permissive, but users are reminded of ethical guardrails

📚 Module & Testing Index
Major Modules (Details in /docs/ or /src/<module>/README.md)

Alden: /src/personas/alden.py

Alice: /src/personas/alice.py

Mimic: /src/personas/mimic.py

Vault: /src/vault/vault.py

Core: /src/core/core.py

Synapse: /src/synapse/synapse.py

Sentry: /src/sentry/sentry.py

Testing:

Core tests: /tests/test_core_multi_agent.py, /tests/test_core_memory_management.py, /tests/run_core_tests.py

QA Checklist: /docs/appendix_h_developer_qa_platinum_checklists.md

See /docs/ for all implementation, integration, and testing details.

⚙️ Development Workflow
Modular, Branch-Per-Feature:
See Process Refinement

Regular pushes to GitHub required for every milestone

Single README in root is authoritative (all others are legacy and will be removed)

🤝 Contribution & Access
Private Repo: Access by invitation

Development managed via feature branches and issue tracker

All PRs require review and variance report for merge

📝 License
MIT License – See LICENSE

📞 Contact, Status, Disclaimer
Closed Beta – Not public, request access via maintainer

Disclaimer: Hearthlink and Alice are for productivity/support only—not medical or therapeutic tools.

Open, honest, transparent… Real.

This README supersedes all prior module-specific or legacy README files. Please maintain this file as the project’s single authoritative overview.
