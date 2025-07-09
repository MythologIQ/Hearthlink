# VOICE\_ACCESS\_POLICY.md

## Overview

This document outlines voice access rules, boundaries, and system behavior across Hearthlink's AI agents, modules, and external integrations. Policies apply whether voice control is enabled system-wide or agent-specifically.

---

## 🎙️ Voice Access States

### ✅ Voice Interaction Enabled

* User may interact with local agents (Alden, Alice, Mimic, Sentry) using conversational input.
* External agents (e.g., Gemini CLI, Google API, Trae CLI) are permitted if explicitly enabled.
* Universal voice HUD (if active) routes input according to active agent context or agent name.

### 🔒 Voice Interaction Disabled

* Voice HUD and microphone remain inactive.
* No voice parsing, transcription, or command handling occurs.
* Agent memory marks user preference to disable voice interactions.

---

## 🧠 Local Agent Voice Interaction Rules

### Alden, Alice, Mimic, Sentry

* Fully conversational when voice is enabled.
* Can be addressed by name ("Hey Alden") or selected via voice HUD.
* If no agent is specified, Core delegates to the currently active agent.

### Example Triggers:

* "Alden, what's on my schedule today?"
* "Mimic, help me rewrite this paragraph."

---

## ☁️ External Agent Voice Permissions (Gemini CLI, Google API, Trae CLI)

### Default Behavior

* Disabled by default for security.
* **Per-agent permissions**: Enabled via **Core → Agent Settings → [Agent Name] → Voice Interaction**
* **Global default rules**: Configured via **Settings → Hearthlink Voice Settings → External Agent Defaults (SET-003)**
* **Override Model**: Global defaults can override per-agent permissions at the system level

### Permission Layers

* Voice requests routed to external agents require:

  * Explicit user activation.
  * Agent connection to **Core** (not direct access to Vault or UI).
  * Active session tracking via Synapse.
  * Compliance with both per-agent and global default rules.

---

## 🧭 Voice Routing Logic

### Universal Voice HUD Modes

* **Agent Agnostic Mode**:

  * System listens for any active agent by name.
  * Example: "Hey Alice…" or "Mimic, can you…"
* **Isolated Mode (Pinned Agent)**:

  * All voice input routes to selected agent only.
  * Prevents accidental access to external services.

### Safety Reinforcement

* Core never routes input to external agents unless the agent is actively in session and has been granted permission.
* System confirms agent routing in voice response ("You're speaking with Gemini CLI now").

---

## 🔐 Voice Authentication & Dev Mode Activation

### Secure Mode Activation

* Activation phrase → Challenge phrase → PIN entry → Dev Mode UI
* Temporarily unlocks system modification mode
* Logged in Vault with timestamp and success/fail status
* **Current Implementation**: Stub logic with simulated challenge prompt and PIN UI stub

### Voiceprint (Optional)

* Voice biometric may be enrolled for internal agent security, not required.

---

## 📴 Offline Mode / No Internet

### Dynamic Detection Logic

* **Not a boolean flag** - implements dynamic, observable detection using:
  * Failed ping attempts to known good IPs
  * OS-level "no internet" state detection
  * Timeout events from known external agents
  * Null modem activity monitoring
* **Detection Method**: `network_status.check()` function with multiple validation points
* **Observable Model**: System continuously monitors network state and adjusts behavior dynamically

### Behavior:

* **Local Agents Remain Fully Functional**

  * Voice conversations with Alden, Alice, Mimic, and Sentry remain available using local LLM.
* **Conversational Intelligence Maintained**

  * Contextual dialogue, task guidance, and session support remain uninterrupted.
  * Vault access and agent-specific logic continue to function.
* **Command Mode Available**

  * Local-only voice commands (e.g., open logs, add memory, launch app) are still recognized.
* **External Agent Access Disabled**

  * All outbound requests to external APIs are blocked.
* **User Alert**

  * Spoken notice: "External services unavailable. Local systems fully operational."

---

## 🔄 Fallback & Error States

### Voice Misrouting Handling (Alden Recovery Protocol)

* **No rigid fallback prompts** - Alden handles all misroutes via intelligent recovery dialogue
* **Alden as Default Handler**: Alden is the default handler for misrouted input and gracefully reroutes or requests clarification
* **Recovery Scenarios**:
  * "I think you meant to talk to Alice about that. Would you like me to switch you over?"
  * "That's outside my expertise, but I can connect you with Mimic who specializes in that area."
  * "Let me help you get to the right agent for this request."
  * "I'm not sure I'm the best agent for this. Would you like me to connect you with someone more specialized?"

### Agent Deference Protocol (Feature ID: AGENT-004)

* **Three Interaction Styles**:
  1. **Passive Suggestion**: "Alice might be better at this…"
  2. **User-Initiated Handoff**: "Can I talk to Alice?"
  3. **Direct Delegation**: "Hand this off to Alice."
* **Implementation**: Agents can suggest better-suited agents for specific tasks
* **UI Integration**: Deference logic hooks integrated into agent interface code stubs and UI flows

---

## 📝 Logging & Transparency

* All voice sessions (transcripts + command triggers) are stored in Vault unless private mode is active.
* **Vault Logging Requirements**:
  * Use mock implementation that hits real Vault logging interface or validated stub
  * Include test logic to simulate actual logging
  * Must validate logging at API or mock layer
* External agent voice interaction logs include:

  * Agent identity
  * Duration
  * Purpose and routed command summary

---

## 🎯 Voice HUD Implementation Requirements

### Required Components

* **Live Input Transcript**: Real-time display of user voice input
* **Active Agent Display**: Clear indication of which agent is currently active
* **Reroute Handling Visual**: Visual feedback when voice input is rerouted between agents

---

## ✅ Summary of Rules

| Scenario                      | Local Agent | External Agent             | User Prompt            | Logging |
| ----------------------------- | ----------- | -------------------------- | ---------------------- | ------- |
| Voice Enabled (General Use)   | ✅ Allowed   | ❌ Blocked unless permitted | 🟢 Yes (agent confirm) | ✅ Vault |
| Voice Disabled                | ❌ Blocked   | ❌ Blocked                  | 🔴 No                  | ❌ None  |
| Dev Mode Activation via Voice | ✅ Allowed   | ❌ Blocked                  | 🟢 Yes                 | ✅ Vault |
| Offline Mode                  | ✅ Allowed   | ❌ Blocked                  | 🟡 Partial             | ✅ Vault |
| Pinned Agent Active           | ✅ Allowed   | ❌ Unless pinned            | 🟢 Yes                 | ✅ Vault |
| Misroute Recovery             | ✅ Alden handles           | ❌ N/A                     | 🟢 Recovery dialogue    | ✅ Vault |
| Agent Deference               | ✅ All agents              | ❌ N/A                     | 🟢 Suggestion/switch    | ✅ Vault |

---

## 🔚 Final Note

Voice functionality is a central part of Hearthlink but should always prioritize clarity, user consent, and security. All agent responses must reinforce the routing logic and confirm agent identity in voice interactions.

For questions, contact: `system@hearthlink.local`
