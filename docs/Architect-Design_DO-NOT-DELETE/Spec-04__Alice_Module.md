# SPEC-04: Alice Module

1. Background
The Alice module delivers adaptive conversational intelligence within Hearthlink. It manages dynamic chat
sessions, builds a Cognitive Behavior Profile (CBP) from user interactions, and exposes context-aware
actions. Alice powers user-facing chat UIs, automations via the Project Command framework, and informs
personalization across the platform.
2. Requirements (MoSCoW)
## Must have
• Stateful chat sessions with context window management
• Text and voice input support with transcription
• CBP Panel capturing sentiment, engagement, and behavioral metrics
• Inline actions & quick commands (Diagnostics, Observatory)
• Secure API with OAuth2 scopes:  alice.session.* ,  alice.message.* ,  alice.cbp.*
## Should have
• Persistent session history in Vault for auditing and analysis
• Editable persona traits via quick trait editor
• Settings panel for conversation preferences and LLM backend selection
## Could have
• Multi-language support with locale-based models
• Customized voice activation phrases per user
Won’t have (this increment)
• External workflow connectors beyond Project Command
• Extensive analytics dashboards (handled by Core Services)
3. Method
## 3.1 Architecture Diagram
@startuml
package "Alice Frontend" {
[ChatUI] --> [Alice API]
[CBPPanel] --> [Alice API]
[SettingsPanel] --> [Alice API]
}
1
package "Alice Backend" {
[API Service] --> [Session Store]
[API Service] --> [CBP Engine]
[API Service] --> [LLM Backend]
[API Service] --> [Vault]
}
[ChatUI] -> [Session Store] : GET/POST messages
[CBP Engine] --> [CBP Store]
[LLM Backend] -> [API Service]
@enduml
## 3.2 Data Schema
@startuml
table Session {
+ session_id  : UUID [PK]
+ user_id     : UUID
+ persona_id  : UUID
+ created_at  : TIMESTAMP
+ updated_at  : TIMESTAMP
}
table Message {
+ msg_id      : UUID [PK]
+ session_id  : UUID [FK]
+ sender      : ENUM('user','assistant')
+ content     : TEXT
+ timestamp   : TIMESTAMP
}
table CBPProfile {
+ profile_id  : UUID [PK]
+ session_id  : UUID [FK]
+ sentiment   : FLOAT
+ engagement  : FLOAT
+ metrics     : JSON
+ updated_at  : TIMESTAMP
}
@enduml
2
4. UI Components & Wireframes
## 4.1 Chat Interface Panel
+----------------------------------------------------------+
| Alice Chat - Session <ID>                                |
| [Message History Scrollable Area]                        |
|                                                          |
| [TextInput][Send][VoiceToggle]                           |
+----------------------------------------------------------+
## Component Function API/Data Call
Displays messages with sender GET /v1/sessions/{id}/messages?
## MessageHistory
styling limit=50
## TextInputField Captures user text N/A
SendButton Sends user message POST /v1/sessions/{id}/messages
## Toggles voice input and
VoiceToggle Browser Web Speech API → POST message
transcription
TypingIndicator Shows assistant typing status GET /v1/sessions/{id}/typing
## 4.2 CBP Panel
+----------------------------------------------------------+
| Cognitive Behavior Profile                              |
| [Summary Cards: Sentiment, Engagement, Rhythm]          |
| [History Timeline View]                                 |
| [Configure Triggers] [Export Profile]                   |
+----------------------------------------------------------+
## Component Function API/Data Call
GET /v1/sessions/{id}/cbp/
## SummaryCards Shows current CBP metrics
summary
Displays metric history over GET /v1/sessions/{id}/cbp/
## TimelineView
session timeline
## Opens modal to set adaptive
## ConfigureTriggersBtn N/A
triggers
GET /v1/sessions/{id}/cbp/
## ExportProfileBtn Exports CBP JSON
export
3
## 4.3 Settings Panel
+----------------------------------------------------------+
| Alice Settings                                           |
| [LLM Backend ▼] [Model ▼] [Response Timeout]             |
| [Default Persona ▼] [Language ▼]                         |
| [Save] [Cancel]                                          |
+----------------------------------------------------------+
## Component Function API/Data Call
Select LLM backend (OpenAI/ GET /v1/settings ,  PUT /v1/
## BackendDropdown
Claude/Local) settings
## ModelDropdown Choose model for selected backend
## TimeoutInput Set max response latency
## PersonaDropdown Select default persona
## LanguageDropdown Choose locale
## SaveSettingsButton Persist settings PUT /v1/settings
5. API Endpoints
## Method Path Description Auth Scope
## POST /v1/sessions Create or resume a session alice.session.write
GET /v1/sessions/{id} Retrieve session metadata alice.session.read
GET /v1/sessions/{id}/messages Fetch recent messages alice.message.read
POST /v1/sessions/{id}/messages Post user message alice.message.write
GET /v1/sessions/{id}/typing Get typing status alice.message.read
/v1/sessions/{id}/cbp/
## GET Fetch CBP summary alice.cbp.read
summary
/v1/sessions/{id}/cbp/
## GET Fetch CBP history alice.cbp.read
timeline
/v1/sessions/{id}/cbp/
## GET Export full CBP profile alice.cbp.read
export
## Retrieve user-specific Alice
## GET /v1/settings alice.settings.read
settings
4
## Method Path Description Auth Scope
## Update user-specific Alice
## PUT /v1/settings alice.settings.write
settings
6. Implementation
1. Develop React components for Chat, CBP, and Settings panels.
2. Implement WebSocket & REST API clients.
3. Build CBP Engine service to compute metrics post-message ingest.
4. Persist session and CBP data to Vault/Database.
5. Integrate voice transcription stream via Web Speech API and backend processing.
6. Write unit, E2E tests covering 95% of UI flows and API contracts.
7. Milestones
## Milestone Timeline Owner
## Chat Interface MVP Week 1 Frontend Team
## CBP Engine & Panel Week 2 ML/Backend Team
## Settings Panel & Integration Week 3 Full-stack Team
## Voice Integration Week 4 Voice Lead
## Testing & Accessibility Week 5 QA & Accessibility
8. Gathering Results
• Session creation & messaging success rate ≥99.9%
• CBP computation latency <200 ms per message
• Settings persist and apply correctly across reloads
• Voice transcription accuracy ≥90% in test scenarios
• Accessibility audit passes WCAG 2.1 AA
10. Additional Enhancement Suggestions
Building on your feedback and Alice’s core focus on user well-being and contextual intelligence, consider
these targeted enhancements:
• Contextual Smart Replies\ Provide proactive suggestion chips based on CBP insights (e.g., “Would
you like a summary of today’s discussion?”) to accelerate common tasks. Absolutely
• Adaptive UI Themes (Alice Only)\ Dynamically adjust Alice’s chat interface colors or fonts based on
detected user mood or time of day, leveraging CBP sentiment data. This personalization boosts
engagement without affecting other modules.
5
• Expressive Avatar\ Introduce an animated avatar for Alice in the chat UI that reflects core emotions
(happy, thoughtful, concerned) with minimal resource overhead (simple SVG-based animations or
CSS-driven transitions).
• Contextual Well-Being Prompts\ Leverage CBP to send timed, empathetic reminders (e.g., “You’ve
been focused for two hours-consider a short break.”) to encourage healthy behaviors.
## Confirmed
• Session Summaries & Export\ After conversation end, auto-generate a concise transcript summary
and action-item list. Expose an “Export to Alden Tasks” button so Alden can mirror and integrate
these action items into the user’s task list. Affirmative
• Privacy Mode Toggle\ Support a “Privacy Mode” where CBP recording pauses and chat data is held
only in volatile memory-discarded at session end-to protect sensitive interactions. Supported
• Quick Reaction Buttons\ Replace thumbs-up/down with simple “+” and “-” buttons aligned with
Alice’s minimal theme to capture immediate feedback on each assistant message, feeding back into
## CBP adjustments in real time.
• Persona Switching Shortcut\ Provide both a voice command (e.g., “Switch to [PersonaName]”) and
a manual dropdown in the chat header for on-the-fly persona changes local to Alice’s session.
• Session Rating Prompt\ After a configurable session duration (e.g., sessions longer than X minutes,
set in Alice Settings), display a casual prompt-“Do you have any feedback on how that session
went?”-with a 1-5 star selector and optional text comment. This prompt respects user preference to
enable/disable ratings in settings.
*Removed multi-modal input and escalation suggestions as they overlap or conflict with performance
constraints and Alice’s role as the specialized diagnostic agent.Session Rating Prompt\ At session end,
prompt the user for a one-click session satisfaction rating (e.g., 1-5 stars) and optional comment, feeding
into system analytics and CBP refinement.
Removed multi-modal input and escalation suggestions as they overlap or conflict with performance constraints
and Alice’s role as the specialized diagnostic agent.
11. System Amendments. System Amendments
Reflecting cross-cutting enhancements and avoiding redundancy:
• Audit Trail Explorer\ Enhancement to existing Vault Module (SPEC-02): extend the Audit Log Viewer
to filter across Vault and Sentry events for comprehensive traceability.
• Usage Analytics Integration\ Enhancement to Core Services (SPEC-07): surface Alice session and
CBP metrics within the Usage Analytics Dashboard to track conversational load and engagement
trends.
6
9. References & Dependencies References & Dependencies
• Vault Module (SPEC-02) for session persistence and audit
• Synapse Module (SPEC-05) for message routing
• Core Services (SPEC-07) for auth, settings, and metrics
• LLM Backend Setup: LLM_BACKEND_SETUP.md
• Voice Policy: VOICE_ACCESS_POLICY.md
Need Professional Help in Developing Your Architecture?
Please contact me at sammuti.com :)
7