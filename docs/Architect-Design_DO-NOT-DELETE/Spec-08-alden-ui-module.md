# SPEC-08: Alden UI Module

1. Background
The Alden UI Module is a peer in the Hearthlink ecosystem, providing a focused dashboard for monitoring
and interacting with core system components. It offers global navigation among modules, persistent
controls, and specialized panels-Observatory, Diagnostics & Repair, Personality & Mood, and Interaction-
without serving as an overseer of other modules.
2. Requirements (MoSCoW)
## Must have
• Radial module navigation menu to switch between peer modules
• Persistent system controls: voice toggle, help access, accessibility options
• Responsive layout: supports 1024×768 minimum, multi-DPI, multi-monitor
• Persistent chat window for message input and transcript
• Accessibility compliance: keyboard navigation, ARIA landmarks, screen-reader support
## Should have
• Dynamic panel sizing based on content density
• Light/dark theme toggle persisted per user preferences
## Could have
• Keyboard shortcuts for panel switching (e.g., Ctrl+1 for Observatory)
• Drag-and-drop panel reordering
Won’t have (this increment)
• Module launch or welcome flows (handled by system launcher)
• In-panel tutorials or guided onboarding
3. Method
## Architecture Diagram
@startuml
package "Alden UI" {
[RadialModuleNav] --> [PanelFrame]
[SystemControlsBar] --> [PanelFrame]
[PanelFrame] --> [PersistentChatWindow]
1
}
@enduml
## Data Schema
@startuml
table AldenUIState {
+ user_id      : UUID [PK]
+ theme        : ENUM('light','dark')
+ last_panel   : VARCHAR
+ layout_pref  : JSON
+ updated_at   : TIMESTAMP
}
@enduml
4. UI Components & Wireframes
## 4.1 Radial Module Navigation
[ Hearthlink Glyph ]
*
*  *  *
* Alden Alice Synapse *
* Vault Sentry Mimic *
*
## Component Function Data/API Call
Displays peer modules in an arc; onClick POST /ui/navigate
## RadialModuleNav
navigates module { moduleId }
## 4.2 System Controls Bar
[Voice][Help][Accessibility]  [Theme Toggle]
## Component Function Data/API Call
## VoiceToggleButton Toggle voice input mode PUT /user/preferences/voice
## HelpButton Opens help modal N/A
## Opens accessibility settings GET/PUT /user/preferences/
## AccessibilityButton
modal accessibility
2
## Component Function Data/API Call
## Switch between light/dark
## ThemeToggleButton PUT /user/preferences/theme
theme
## 4.3 Observatory Panel
+---------------------------------------------------------+
| Observatory                                             |
| Tabs: [Live Feed] [Metrics]                             |
|                                                         |
| [Real-time telemetry graph or table view]               |
+---------------------------------------------------------+
## Sub-Component Function Data/API Call
LiveFeedTab Streams live events (redraws on each update) GET /sentry/events/stream
MetricsTab Shows aggregated metrics (charts, counters) GET /observatory/data
TelemetryChart Renders data using Recharts for trends Data from metrics API
## 4.4 Diagnostics & Repair Panel
+---------------------------------------------------------+
| Diagnostics & Repair                                    |
| Buttons: [Run Diagnostics] [Repair Actions]             |
|                                                         |
| [Diagnostic logs output area]                           |
+---------------------------------------------------------+
## Sub-Component Function Data/API Call
## RunDiagnosticsButton Initiates system diagnostics POST /diagnostics/run
## Lists available repair actions with
## RepairActionsList GET /diagnostics/actions
status
GET /diagnostics/logs?
## LogsOutputPane Streams real-time diagnostic logs
session={id}
## 4.5 Personality & Mood Panel
+---------------------------------------------------------+
| Personality & Mood                                      |
|                                                         |
3
| [Mood Indicator: 😊/😐/☹️ ]   [Trait Overview]           |
|                                                         |
| [Editable list of persona traits and weights]           |
+---------------------------------------------------------+
## Sub-
## Function Data/API Call
## Component
GET /mimic/personas/{id}/
## MoodIndicator Shows current persona mood via icon
traits
Editable list for traits; inline JSON-schema
TraitListEditor PUT /mimic/personas/{id}
validation
## 4.7 Full-Screen Wireframes
## Alden Main Screen Full Wireframe
+-----------------------------------------------------------------------------------
+
|                                   Hearthlink Radial
Nav                            |
|                             (Centered Top: 7-icon downward
arc)                   |
|-----------------------------------------------------------------------------------|
| [Voice] [Help] [Accessibility]                                        (top-
right)  |
|-----------------------------------------------------------------------------------|
|
|
|  +-------------------------[ Panel Frame ]-----------------------------
+          |
|  | [ Observatory ] [ Personality & Mood ] [ Interaction ]
|          |
|  | [ Cognition & Memory ]             [ Diagnostics & Repair ]
|          |
|  | (Panels sized per info density; adaptive layout)
|          |
|  +---------------------------------------------------------------------
+          |
|
|
| [ Chat Input/Transcript: Persistent at Bottom, outside panel
frame ]              |
+-----------------------------------------------------------------------------------
+
4
## Panel Expansion Example
+-----------------------------------------------------------------------------------
+
|                              Alden Panel: Observatory
(Expanded)                   |
|-----------------------------------------------------------------------------------|
| [Close] [Live Feed] [Metrics]
X |
|-----------------------------------------------------------------------------------|
|
|
|  [Full-width data visualization or log table occupies multi-column
span]          |
|
|
+-----------------------------------------------------------------------------------
+
5. API Endpoints API Endpoints API Endpoints
## Method Path Description Auth Scope
## POST /ui/navigate Switch to another module ui.navigate
## GET /user/preferences Retrieve user UI preferences user.prefs.read
## PUT /user/preferences Update user UI preferences user.prefs.write
GET /alice/sessions/{id}/messages Load chat history alice.message.read
POST /alice/sessions/{id}/messages Send chat message alice.message.write
6. Implementation
1. Integrate RadialModuleNav and SystemControlsBar into React/Tailwind codebase.
2. Implement adaptive CSS Grid for PanelFrameContainer and responsive behaviors.
3. Develop Chat components linked to Alice APIs.
4. Persist AldenUIState through user preferences service.
5. Conduct WCAG 2.1 AA accessibility audit.
6. Write unit and E2E tests for navigation, theming, and chat flows.
7. Milestones
## Milestone Timeline Owner
## RadialNav & Controls Setup Week 1 Frontend Team
5
## Milestone Timeline Owner
## Panel Layout & Responsiveness Week 2 Frontend Team
## Chat Window Integration Week 3 Full-stack Team
## Accessibility & Theming Week 4 Accessibility Lead
## Testing & QA Week 5 QA Team
8. Gathering Results
• Module navigation latency <100 ms.
• UI preferences persisted correctly across sessions.
• Responsive layout verified at 1024×768 and multi-DPI.
• Accessibility compliance at AA level.
9. Dynamic & Responsive Rules
• Panel sizing: Each panel adjusts its grid span based on content density (e.g., Diagnostics spans two
columns when showing logs).
• Breakpoints: At viewport widths <800 px, panels stack vertically; chat and controls remain fixed.
• Animation timing: Radial menu opens with a 200 ms ease-out fade and 150 ms option slide.
• Z-ordering: SystemControlsBar and PersistentChatWindow always overlay panels; modals appear
above all.
10. References & Dependencies
• UI Blueprints: appendix_c_ui_blueprints.md
• Integration Blueprints: appendix_b_integration_blueprints.md
• CSS Guidelines: include spacing/typography tokens from design system
• Accessibility Guidelines: VOICE_ACCESS_POLICY.md sections on UI
• DevOps Guide: _DEVELOPMENT_OPERATIONS_GUIDE.md
6