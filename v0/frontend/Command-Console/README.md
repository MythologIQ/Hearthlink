
# Nexus Command Console: Unified System Documentation

## 1. Project Overview

The Nexus Command Console is a sophisticated observability and orchestration interface designed to manage a complex ecosystem of AI agents, Docker-based microservices, and RAG-enabled data infrastructure. Its primary purpose is to provide a centralized hub for developers to monitor, control, and interact with various interconnected components, including a localized AI agent ("Alden"), a specialized web crawling and RAG MCP server ("Crawl4ai-rag"), and a browser integration layer via a Chrome Extension ("Nexus Lens").

The ecosystem is geared towards enabling advanced AI-driven tasks, data acquisition, and context-aware assistance for AI agents and coding assistants. The Console itself serves as the primary user interface into this system.

## 2. System Architecture & Components

The Nexus system is composed of several key, interconnected components:

### 2.1. Nexus Command Console (Frontend)

*   **Technology:** React (with Vite), TailwindCSS.
*   **Purpose:** The main user interface for monitoring and controlling the entire Nexus ecosystem.
*   **Functionalities:**
    *   Displays operational status from Alden, Crawl4ai-rag, and Docker containers.
    *   Provides interactive controls for these components.
    *   Features a chat interface for communicating with Alden and potentially other system agents (via "Nexus Core" context).
    *   Manages and displays memory inventory, logs, tasks, and system metrics.
    *   Initiates file ingestion processes.
*   **Communication:** Interacts with backend services (likely "Gatekeeper") via HTTP/WebSocket and MCP servers (like Crawl4ai-rag) via SSE or stdio.

### 2.2. Alden (Local AI Agent)

*   **Purpose:** A localized AI agent with capabilities for reflection, learning, and maintaining a personality. It operates with its own RAG database and a unique "wake-up" protocol.
*   **Backend:**
    *   Technology: Python, Flask.
    *   API: Provides endpoints for submitting prompts (`/submit_prompt`), retrieving feedback queues (`/feedback_queue`), user-specific conversation threads (`/user_thread/:user_id`), and detailed memory slices (`/slice/:slice_id`).
*   **Memory & Personality:**
    *   Database: SQLite (`Alden/backend/memory/alden_memory.db`) stores procedural memory, RAG chunks, and metadata.
    *   Personality Vector: `Alden/backend/memory/personality_vector.json` stores evolving personality traits and reflections.
    *   Memory Slices: Individual JSON files (e.g., `Alden/backend/memory/slices/init_roan.json`) capture specific reflections or interactions.
*   **Engine & Constructs:**
    *   Mentor Manifests: Defines different AI mentors (e.g., Alice, Roan in `Alden/engine/`) that guide Alden's development.
    *   Text Library: Utilizes a collection of texts (e.g., poetry, strategy books in `Alden/engine/library_manifest.json`) for learning and context.
    *   Constructs: Thematic environments like "Garden" and "Observatory" (`Alden/constructs/construct_schema.json`) influence Alden's emotional state and mentor interactions.
*   **Reflection Cycle:** Follows directives (`Alden/backend/runtime/directives.md`) for init, engage, reflect, archive, and respond phases.

### 2.3. Crawl4ai-RAG (Web Crawling & RAG MCP Server)

*   **Purpose:** An MCP (Model Context Protocol) server providing advanced web crawling and Retrieval Augmented Generation (RAG) capabilities.
*   **Technology:** Python, using [Crawl4AI](https://crawl4ai.com) and an MCP server framework.
*   **Tools (exposed via MCP):**
    *   `crawl_single_page`: Crawls and indexes a single web page.
    *   `smart_crawl_url`: Intelligently crawls based on URL type (sitemap, `llms-full.txt`, or recursive webpage crawl).
    *   `get_available_sources`: Lists available data sources (domains) for RAG.
    *   `perform_rag_query`: Performs semantic search over crawled content, with optional source filtering.
*   **Database:** Supabase (Postgres with `pgvector` extension) for storing crawled pages and their embeddings (`Crawl4ai-rag/crawled_pages.sql`).
*   **Embeddings:** Utilizes OpenAI API for generating embeddings.
*   **Communication:** Supports SSE (Server-Sent Events) and stdio transports for MCP communication.
*   **Configuration:** Managed via an `.env` file (OpenAI key, Supabase credentials, server host/port).

### 2.4. Gatekeeper (System Backend & WebSocket Hub)

*   **Location:** `backend/gatekeeper.js` (formerly `legacy code/bridgekeeper.js`)
*   **Purpose:** Acts as a central communication hub and API gateway for the Nexus Command Console frontend. It manages WebSocket connections, sessions, and routes commands/data between the console, Alden, and the Chrome extension.
*   **Technology:** Node.js, Express, WebSocket (`ws` module).
*   **APIs (Served):**
    *   Serves API endpoints for `/api/containers`, `/api/events`, `/api/system/status`, `/api/ingest`, `/api/gemini/generate`, etc.
    *   `/api/status` (HTTP endpoint for basic health check).
*   **WebSocket Server:** Runs on a configurable port (e.g., 8765 or same as HTTP), handling client sessions, message routing.
*   **Authentication:** Uses a token (`GATEKEEPER_TOKEN`) for WebSocket connections.
*   **Logging:** Produces structured logs to daily rotated files.

### 2.5. Nexus Lens (Chrome Extension)

*   **Location:** `Nexus-suite/Nexus/extension/` (formerly `legacy code/extension/`)
*   **Purpose:** Provides browser integration, allowing interaction with web pages, identifying agents within tabs, and relaying information to/from the backend (Gatekeeper).
*   **Components:**
    *   `manifest.json`: Defines permissions and host permissions.
    *   `background.js`: Service worker for managing WebSocket connection to Gatekeeper and message listening.
    *   `content-minimal.js`: Injected into web pages to detect agents, log interactions, and communicate with `background.js`.
    *   `popup.html/js/css`: UI for the extension, showing connection status and providing controls.
    *   `modules/AgentMemory.js`: Module for managing agent-related memory.

## 3. Technology Stack

*   **Frontend (Nexus Command Console):** React, TailwindCSS, TypeScript (powered by Vite).
*   **Backend (Gatekeeper - Console Backend):** Node.js, Express, WebSocket (`ws` module).
*   **Backend (Alden - Local AI):** Python, Flask.
*   **Backend (Crawl4ai-RAG - MCP Server):** Python, Crawl4AI, MCP framework.
*   **Databases:**
    *   **Alden Local RAG & Personality:** SQLite.
    *   **Crawl4ai-RAG Content:** Supabase (Postgres with `pgvector`).
    *   **Gatekeeper Events/Logs (Primary):** File-based (rotated text logs). (Supabase for Alden events if configured).
*   **AI & Embeddings:** Gemini API (via Gatekeeper), OpenAI API (for Crawl4ai-RAG).
*   **Containerization:** Docker.
*   **Browser Extension:** Standard WebExtension technologies.

## 4. Key Functionalities

*   **Nexus Command Console:**
    *   **Container Management:** Listing, starting, stopping, deleting Docker containers (interfacing with Gatekeeper).
    *   **Task Logging & Tracking:** Displaying system events and commands from Gatekeeper.
    *   **System Health & Metrics:** Visualizing system status from Gatekeeper.
    *   **Chat Interface:** Centralized communication with Alden (proxied via Gatekeeper).
    *   **File Ingestion:** UI to `POST /api/ingest` to Gatekeeper for RAG pipeline.
    *   **Memory Inventory:** Displaying data from Alden and Crawl4ai-RAG (via Gatekeeper).
    *   **Operations Hub:** Tabbed interface for Logs, Insights, Tasks, Crawl Sources.
*   **Alden (Local AI):** (Functionality as described before, accessed via Gatekeeper if necessary)
*   **Crawl4ai-RAG Server (MCP):** (Functionality as described before)
*   **Gatekeeper (Backend):**
    *   **WebSocket Communication:** Real-time bidirectional communication with Console frontend and Nexus Lens extension.
    *   **Session Management:** Tracking connected WebSocket clients.
    *   **Message Routing:** Directing messages between connected components.
    *   **HTTP API Serving:** Exposing RESTful endpoints for console operations and proxying to other services.
    *   **Logging:** Centralized logging to rotated files.
*   **Nexus Lens (Chrome Extension):**
    *   **Agent Detection & Communication:** Relaying messages to/from Gatekeeper.
    *   **User Interface:** Popup for status and basic interactions.

## 5. Getting Started & Running the System (High-Level)

### 5.1. Prerequisites

*   Docker Desktop, Node.js (v18+), Python (3.12+ with `uv`), Supabase Account & CLI, Gemini API Key (for Gatekeeper), OpenAI API Key (for Alden/Crawl4ai-RAG).

### 5.2. Component Setup & Execution

#### 5.2.1. Alden (Local AI)
 (Setup as before, ensure `settings.json` uses relative paths)

#### 5.2.2. Crawl4ai-RAG (MCP Server)
 (Setup as before)

#### 5.2.3. Gatekeeper (Backend & WebSocket Hub)
1.  Navigate to `Nexus-suite/Nexus/backend/`.
2.  Create a `.env` file with `GATEKEEPER_HTTP_PORT`, `GATEKEEPER_TOKEN`, `GEMINI_API_KEY`, Supabase credentials, Alden start command, etc.
3.  Install Node.js dependencies: `npm install` (if `package.json` is updated for backend).
4.  Run the server: `node gatekeeper.js`.

#### 5.2.4. Nexus Command Console (React Frontend)
1.  Navigate to `Nexus-suite/Nexus/frontend/Command-Console/`.
2.  Ensure `.env` file for Vite does NOT contain API keys. Frontend connects to Gatekeeper API endpoints.
3.  Install Node.js dependencies: `npm install`.
4.  Start development server: `npm run dev`.

#### 5.2.5. Nexus Lens (Chrome Extension)
1.  Open Chrome extensions, enable Developer mode.
2.  Click "Load unpacked" and select `Nexus-suite/Nexus/extension/` directory.
3.  (Potentially configure Gatekeeper WebSocket URL in extension if not hardcoded to default).

### 5.3. Configuration Overview

*   **Alden:** `settings.json` (relative paths).
*   **Crawl4ai-RAG:** `.env` file.
*   **Gatekeeper:** `.env` file (`GATEKEEPER_TOKEN`, `GEMINI_API_KEY`, ports, DB URLs).
*   **Nexus Command Console:** Connects to Gatekeeper API. No direct API keys.
*   **Nexus Lens Extension:** Connects to Gatekeeper WebSocket.

## 6. Core Interfaces & Data Flow (Summary)

*   **Console Frontend <-> Gatekeeper Backend:** HTTP/WebSocket.
*   **Gatekeeper <-> Alden API:** Gatekeeper proxies requests.
*   **Gatekeeper <-> Docker CLI:** Gatekeeper uses Docker CLI.
*   **Gatekeeper <-> Nexus Lens Extension:** WebSocket.
*   **Console Frontend / System <-> Crawl4ai-RAG MCP Server:** (May connect directly or be proxied by Gatekeeper).

## 7. Future Development Phases (From Console README)
 (As before)

## 8. Project Structure Highlights
*   `Nexus-suite/Nexus/frontend/Command-Console/`: React Frontend.
*   `Nexus-suite/Nexus/backend/`: Gatekeeper Node.js server.
    *   `gatekeeper.js`: Main server file.
    *   `routes/`: Express route modules.
    *   `services/`: Business logic services (e.g., Docker interaction).
    *   `utils/`: Utility modules (e.g., logger).
    *   `websocket/`: WebSocket handling logic.
    *   `logs/`: Directory for Gatekeeper log files.
*   `Nexus-suite/Alden/`: Local AI Agent system.
*   `Nexus-suite/Crawl4ai-rag/`: Web Crawling & RAG MCP Server.
*   `Nexus-suite/Nexus/extension/`: Chrome "Nexus Lens" extension.

This README provides a consolidated view. Consult specific component READMEs and Gatekeeper's `.env.example` (if created) for detailed configuration.
