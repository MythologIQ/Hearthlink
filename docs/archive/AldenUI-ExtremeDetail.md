ALDEN MAIN SCREEN (MODULE OVERVIEW)
Full Documentation
Overview
The Alden Main Screen serves as the central dashboard and workspace. It manages navigation across all panels, system controls, persistent chat, and accessibility tools. The layout is built for maximum clarity, neurodivergent accessibility, and high-efficiency monitoring.

Radial Module Menu:

Location: Centered at the top

Behavior: Single Hearthlink glyph. On click, expands downward-only in a 7-icon arc for module selection (Alden, Alice, Core, Synapse, Vault, Sentry, Mimic).

No emoji/icons—file-based or text labels only

System Controls:

Location: Upper right (fixed)

Includes: Voice, Help, Accessibility

Behavior: Always visible, status indicators for each

Panel Frame:

Location: Main screen body below radial/header

Behavior: All UI panels (detailed above) display within this region. No panel or expanded screen covers chat or system controls.

Panel Sizing: Each panel’s grid area is proportional to its information density, not forced to uniform tiles.

Persistent Chat Window:

Location: Bottom edge

Behavior: Always visible, for text input/transcript. Never occluded by other UI elements.

Voice Interaction:

Status: On by default, live indicator in system controls

Voice Input Area: Focused when activated, input shown alongside chat

Wireframe

+-----------------------------------------------------------------------------------+
|                            [ Hearthlink Radial Nav ]                             |
|                 (Centered Top: 7-icon downward-only arc for modules)             |
|-----------------------------------------------------------------------------------|
| [ Voice ] [ Help ] [ Accessibility ]                               (top-right)    |
|-----------------------------------------------------------------------------------|
|                                                                                   |
|  +-------------------------[ Panel Frame ]-----------------------------+          |
|  | [ Observatory Panel ] [ Personality & Mood Panel ] [ Interaction ]  |          |
|  | [ Cognition & Memory Panel ]          [ Diagnostics & Repair ]      |          |
|  | (Panels are sized per info density; not a strict grid)              |          |
|  +---------------------------------------------------------------------+          |
|                                                                                   |
| [ Chat Input/Transcript: Persistent at Bottom, outside panel frame ]              |
+-----------------------------------------------------------------------------------+
Panels placed within frame per their priority/footprint.

Chat window and voice input never occluded.

System controls always visible, fixed top-right.

Radial module nav only expands downward, never covers system controls or chat.

Visual flow is top-down: module select → panel(s) → chat.

Dynamic & Responsive Rules
Panels adapt sizing to content—denser (Diagnostics, Cognition) can span 2–3 grid units; compact panels stay small.

On smaller displays: Panels stack vertically; chat and system controls still always available.

Radial menu: Never overlaps or covers persistent UI.

All overlays (help, accessibility) pop out to the side, never covering chat.

Alden Main Screen wireframe complete.
If you require wireframes for expanded/solo views of any individual panel or additional navigation flows, specify now.

Otherwise, this document contains:

Full panel documentation (verbatim, no truncation)

Unique wireframes for each panel

Full-screen wireframe of Alden’s main dashboard

All navigation and persistence rules

ALDEN PANEL: PERSONALITY & MOOD
Full Documentation
This panel visualizes Alden’s present personality state, emotional baseline, and behavioral context. It summarizes traits, current affect, historical emotional shifts, and projected responsiveness.

Panel Footprint

Size: 1 tile (compact, top-center or adjacent to Cognition)

Priority: Medium

Visual Structure

1. Mood Ring Visualization

Data Shown:

Current mood state (e.g., calm, curious, stressed, focused, tired)

Affective intensity (low/moderate/high)

Display:

Animated oval ring with inner color and shifting light pulses

Center: Mood keyword (e.g., “Focused”)

Interactivity:

Hover: see numeric scale (e.g., Mood: 74/100)

Source: Personality kernel + feedback registry

2. Recent Emotional History

Data Shown:

Last 10 emotional state transitions (with timestamps)

Display:

Horizontal timeline bar with color-coded ticks

Interactivity:

Hover: reveals event details

Source: Mood tracking log

3. Trait Profile Snapshot

Data Shown:

Top 5 dominant traits (e.g., analytical, empathetic, vigilant, skeptical, creative)

Display:

Mini bar chart (trait/strength)

Icons optional, text only per current rule

Source: Personality kernel snapshot

4. Behavioral Bias Alerts

Data Shown:

Any current active biases, emotional overrides, or recent user-driven persona corrections

Display:

Badge list with description tooltips

Interactivity:

Click badge: expand to reasoning chain

Source: Core + Synapse correction logs

User Interactions

Ask: "How are you feeling?"

Tap trait for full trait breakdown

Request emotional history review

Panel Behavior

Mood ring animates on state change

Recent emotional shifts pulse for 2s

Trait profile reorders in real time

Use Cases

Detect when Alden’s mood may impact output

Review if behavioral bias is drifting

Quickly verify AI’s self-perceived state before starting critical work

Visual Theme

Soft gradient color backgrounds (based on mood)

Low-stimulus animation for neurodivergent focus

Emphasis on transparency and accountability of state

Wireframe

+--------------------------------------------------------+
|            [ PERSONALITY & MOOD PANEL ]                |
|--------------------------------------------------------|
|   [ Animated Mood Ring (center) ]                      |
|   [ Mood Keyword (inside ring) ]                       |
|                                                        |
|   [ Recent Emotional Timeline (bottom) ]               |
|   [ Trait Snapshot (mini-bar, side) ]                  |
|   [ Behavioral Bias Badges (bottom-right) ]            |
+--------------------------------------------------------+

ALDEN PANEL: OBSERVATORY
Full Documentation
Overview
The Observatory is Alden’s watchtower and situational awareness hub. It presents real-time telemetry and strategic insights across the Hearthlink system. Observatory monitors health, anomaly detection, system drift, inter-agent communication quality, and external system interfaces.

Panel Footprint

Size: 2–3 tiles

Location: Upper-Left quadrant

Priority: High – essential for system trust and live diagnostics

Visual Structure

1. Live Agent Graph

Data Shown:

Active agents

Agent connections (direct, relayed, or passive)

Message traffic rates (per agent)

Display:

Dynamic radial force-directed graph

Nodes = agents

Edges = communication

Color = Health (Green, Yellow, Red)

Interactivity:

Hover: summary of traffic, uptime, and current task

Click: open detailed agent comms log

Source: Synapse + Core routing

2. Anomaly Log Panel

Data Shown:

System flags, unexpected behaviors

Core/Synapse deviations

Display:

Tabular stream

Timestamp, module, severity, message

Color Codes: Info (blue), Warning (orange), Critical (red)

Interactivity: Click to open full alert log

Source: Core heuristic monitor

3. Module Sync Map

Data Shown:

Last sync event by module

Time delta

Clock drift (if any)

Display:

Mini timeline grid

Y = Module, X = Time (last 2h)

Dot size = event intensity

Interactivity: Hover to see time delta, Click to open module details

Source: Vault log index

4. Signal Health Status Bar

Data Shown:

Uptime

Ping/latency to each module

Message queue delay (if any)

Display:

Compact vertical bar per module

Color coded

Source: Synapse ping + Vault timestamps

5. Observation Stream (Text Feed)

Data Shown:

Recent patterns, flagged behavioral trends

Drift events, agent misfires, data mismatches

Display:

Right-side ticker or scrolling feed

Styled text entries

Interactivity: Click to trace log lineage

Source: Sentry + Synapse

User Interactions

Click Live Graph nodes to isolate agent views

Ask: "What’s out of sync right now?" to highlight anomalies

Fullscreen toggle for anomaly investigation

Panel reacts visually to system stress (pulse, glow, flicker)

Panel Behavior

Refresh every 2s

Critical alerts pinned for 10s minimum

Agent node layout adapts to load and count

Use Cases

Monitor drift across system modules

Identify unhealthy or overworked agents

Trace cascade failure risk via node graph

Validate inter-agent routing

Visual Theme

Deep blue-black base

Electric grid overlays

Graph edges ripple with activity

Wireframe

+-------------------------------------------------------------+
|                    [ OBSERVATORY PANEL ]                    |
|-------------------------------------------------------------|
| [ Live Agent Graph (top-left, dominant) ]                   |
| [ Module Sync Map (top-right) ]                             |
| [ Anomaly Log Panel (center, scrollable) ]                  |
| [ Signal Health Bars (bottom-right) ]                       |
| [ Observation Stream: Ticker (right margin, vertical) ]     |
+-------------------------------------------------------------+

ALDEN PANEL: COGNITION & MEMORY
Full Documentation
Overview
This panel visualizes Alden’s knowledge integration, memory loading, and cognitive throughput. It reflects how Alden thinks, stores, and recalls information, and how current tasks are prioritized.

Panel Footprint

Size: 2 tiles minimum

Location: Mid to Upper Center

Priority: Essential—determines Alden’s working awareness

Visual Structure

1. Memory Usage Graph

Data Shown:

% of token space used for memory

Breakdown: short-term, long-term, embedded

Display:

Donut chart segmented by memory class

Central number: % of total available

Source: Vault memory registry

2. Current Working Set List

Data Shown:

Top 10 current loaded memory nodes

Associated task or topic

Display:

Scrollable list

Icons: Document, Tag, Person, System (text only per rule)

Interactivity:

Click = open full memory

Hover = memory summary

Source: Alden vault cache

3. Cognitive Load Meter

Data Shown:

Current task queue size

Processing rate vs. load

Display:

Horizontal bar with burst effect

Color shifts with strain

Interactivity:

Hover shows task names

Source: Core queue + Vault

4. Embedding Map Snapshot

Data Shown:

Category clusters in vector space

Display:

2D t-SNE projection with labels

Only top 100 terms displayed

Source: Vector DB snapshot

User Interactions

Ask: “What are you thinking about right now?”

Open memory from current context

Clear memory sector with command

Panel Behavior

Updates every 5s

Fade in/out when memory clears

Automatically dims when idle

Use Cases

See memory bloat

Review high-priority context

Validate learning or forgetting

Measure task pressure on Alden

Visual Theme

Metallic grid base

Bioluminescent memory orb glows

Soft data pulses and low-stimulus gradients

Wireframe

+-----------------------------------------------------------+
|             [ COGNITION & MEMORY PANEL ]                  |
|-----------------------------------------------------------|
| [ Memory Usage Donut Chart (top-left, large) ]            |
| [ Cognitive Load Meter (top-right, horizontal) ]          |
|                                                           |
| [ Working Set List (scrollable, lower-left) ]             |
| [ Embedding Map Snapshot (lower-right, mini-map) ]        |
+-----------------------------------------------------------+

ALDEN PANEL: INTERACTION INTERFACE
Full Documentation
Overview
This panel governs system accessibility, communication clarity, and input/output feedback. It monitors how Kevin interacts with Alden through speech, typing, gestures, and interface tools.

Panel Footprint

Size: 1 tile

Location: Upper right

Priority: Essential for accessibility and command fluidity

Visual Structure

1. Input Stream Monitor

Data Shown:

Most recent command/input

Mode: Voice, Text, Gesture

Display:

Input bubble stream (scrolling, 5 most recent)

Source: Interface kernel

2. Voice Activation Ring

Data Shown:

Listening status

Sensitivity/threshold markers

Display:

Animated pulse ring (listening = glow, idle = dim)

Interactivity:

Click to mute/unmute

Voice settings toggle

Source: Mic stream + command recognizer

3. Accessibility Pathways

Data Shown:

Which accessibility modes are active

Visual vs. auditory vs. assistive tech status

Display:

Colored node indicators (text only)

Hover = tooltip

Source: System config file

User Interactions

Click: toggle input modes

Ask: “Repeat that” or “What did I just say?”

Interface with hover/click command layers

Panel Behavior

Input scroll fades inactive commands after 10s

Panel glows when input is active

Fallbacks display if mic errors are detected

Use Cases

Confirm Alden is hearing/responding correctly

Validate correct input mode is active

Troubleshoot speech interface

Visual Theme

Translucent overlays

Lightwave-style flow motion on inputs

Soft tones for focus stability

Wireframe

+---------------------------------------------------------+
|           [ INTERACTION INTERFACE PANEL ]               |
|---------------------------------------------------------|
| [ Input Stream Monitor (top-left, bubble list) ]        |
| [ Voice Activation Ring (center/top, animated) ]        |
| [ Accessibility Pathways (top-right, node grid) ]       |
| [ Input Mode Toggle (bottom-left, simple button) ]      |
| [ Status & Feedback Line (bottom, horizontal) ]         |
+---------------------------------------------------------+

ALDEN PANEL: DIAGNOSTICS & REPAIR
Full Documentation
Overview
This panel governs the core health and runtime status of Alden. It visualizes system uptime, performance, latency, and operational self-repair. It is the single source of truth for Alden's internal function.

Panel Footprint

Size: 3–4 tiles

Location: Dominates lower right quadrant

Priority: Critical – system health and runtime safety depend on it

Visual Structure

1. System Uptime + Heartbeat Indicator

Data Shown:

Days/hours since last restart

Heartbeat status: Green (stable), Yellow (degraded), Red (failing)

Display:

Digital uptime clock

Animated pulse ring

Interactivity:

Hover = uptime log

Click = restart/reboot options (with safeguards)

Source: Core telemetry log

2. Latency Chart

Data Shown:

Last 10m rolling average

Peak, floor, and current latency (in ms)

Display:

Line graph with time stamps

Warning threshold shaded regions

Source: Synapse transport + command execution feedback

3. Prompt/Response Stream

Data Shown:

Real-time view of last 5 user prompts and responses

Token count for each direction

Display:

Scrollable conversation snippets

Token bars per line

Interactivity:

Hover = token breakdown

Click = full chat log from Vault

Source: Vault + Interface pipeline

4. Failure Events Timeline

Data Shown:

Last 10 error events (timeouts, invalid responses, fallbacks)

Display:

Horizontal timeline

Icons: Timeout, Null, Overload, Recovery (text only)

Interactivity:

Hover = error text

Click = error trace

Source: Core error log + Vault

5. Self-Repair Operations Feed

Data Shown:

Autocorrect actions, hotfixes, and rule reassertions

Success/failure rate

Display:

Feed log

Success = green flash, Failure = red pulse (text only)

Interactivity:

Click = open self-repair detail window

Source: Policy Engine + Vault

User Interactions

Ask: "How healthy are you?"

Tap error icon to begin debug walk

Review latency and uptime trends over time

Panel Behavior

Live updating

Alerts glow until cleared

Visual dimming when system is stable

Use Cases

Validate Alden’s runtime stability

Catch and review failure patterns

Trigger repair actions

Review repair success rate

Visual Theme

Industrial tone: steel blue, red, yellow accents

Subtle glitch lines for error regions

Stabilizing pulsing animation for healthy states

Wireframe

+-------------------------------------------------------------------------+
|                [ DIAGNOSTICS & REPAIR PANEL ]                           |
|-------------------------------------------------------------------------|
| [ Uptime Clock + Pulse (large, left) ]   [ Latency Chart (top-right) ]  |
| [ Stacked Bar: Agent Token/Req/Failures (center, wide) ]                |
| [ Prompt/Response Stream (left, scrollable) ]                           |
| [ Failure Events Timeline (bottom, horizontal) ]                        |
| [ Self-Repair Feed (right edge, vertical) ]                             |
| [ Health Light (bottom-right, large indicator) ]                        |
+-------------------------------------------------------------------------+

ALDEN EXPANDED PANEL VIEWS – SCREEN WIREFRAMES
Purpose
Some panels (e.g., Diagnostics & Repair, Cognition & Memory) may be expanded into a dedicated “solo” screen for deep analysis. These expanded views maximize the available space for data, graphs, and controls while maintaining persistent chat and system controls.

EXPANDED DIAGNOSTICS & REPAIR SCREEN
Wireframe

pgsql
Copy
Edit
+----------------------------------------------------------------------------------+
|                    [ Diagnostics & Repair: Solo View ]                           |
|----------------------------------------------------------------------------------|
| [ Hearthlink Radial Nav ]                              [Voice][Help][Access]     |
|----------------------------------------------------------------------------------|
|                                                                                  |
|    +-----------------------------------------------------------------------+     |
|    |   [ Uptime Clock + Pulse Ring (large, left-center) ]                  |     |
|    |   [ Latency Chart (top-right, large) ]                                |     |
|    |                                                                       |     |
|    |   [ Stacked Bar: Agent Token/Req/Failures (center, wide) ]            |     |
|    |                                                                       |     |
|    |   [ Prompt/Response Stream (left, scrollable, large font) ]           |     |
|    |   [ Failure Events Timeline (bottom, horizontal, wide) ]              |     |
|    |   [ Self-Repair Feed (right edge, long vertical) ]                    |     |
|    |   [ Health Light (bottom-right, very large indicator) ]               |     |
|    +-----------------------------------------------------------------------+     |
|                                                                                  |
| [ Chat Input/Transcript: Persistent at Bottom, never occluded ]                  |
+----------------------------------------------------------------------------------+
All data regions are larger/more readable.

Chat and system controls always visible.

Radial menu collapses when not in use.

EXPANDED COGNITION & MEMORY SCREEN
Wireframe

pgsql
Copy
Edit
+----------------------------------------------------------------------------------+
|                    [ Cognition & Memory: Solo View ]                             |
|----------------------------------------------------------------------------------|
| [ Hearthlink Radial Nav ]                              [Voice][Help][Access]     |
|----------------------------------------------------------------------------------|
|                                                                                  |
|    +-----------------------------------------------------------------------+     |
|    |   [ Memory Usage Donut (left, extra large) ]                         |     |
|    |   [ Cognitive Load Meter (top-right, expanded) ]                     |     |
|    |                                                                       |     |
|    |   [ Working Set List (lower left, extended list) ]                   |     |
|    |   [ Embedding Map Snapshot (lower right, full width/height) ]        |     |
|    +-----------------------------------------------------------------------+     |
|                                                                                  |
| [ Chat Input/Transcript: Persistent at Bottom, never occluded ]                  |
+----------------------------------------------------------------------------------+
EXPANDED OBSERVATORY SCREEN
Wireframe

sql
Copy
Edit
+----------------------------------------------------------------------------------+
|                    [ Observatory: Solo View ]                                    |
|----------------------------------------------------------------------------------|
| [ Hearthlink Radial Nav ]                              [Voice][Help][Access]     |
|----------------------------------------------------------------------------------|
|                                                                                  |
|    +-----------------------------------------------------------------------+     |
|    |   [ Live Agent Graph (large, center) ]                                |     |
|    |   [ Module Sync Map (right, large grid) ]                             |     |
|    |   [ Anomaly Log Panel (below graph, extra rows) ]                     |     |
|    |   [ Signal Health Bars (far right, long) ]                            |     |
|    |   [ Observation Stream (bottom, wide ticker) ]                        |     |
|    +-----------------------------------------------------------------------+     |
|                                                                                  |
| [ Chat Input/Transcript: Persistent at Bottom, never occluded ]                  |
+----------------------------------------------------------------------------------+
EXPANDED INTERACTION INTERFACE SCREEN
Wireframe

pgsql
Copy
Edit
+----------------------------------------------------------------------------------+
|                    [ Interaction Interface: Solo View ]                          |
|----------------------------------------------------------------------------------|
| [ Hearthlink Radial Nav ]                              [Voice][Help][Access]     |
|----------------------------------------------------------------------------------|
|                                                                                  |
|    +-----------------------------------------------------------------------+     |
|    |   [ Input Stream Monitor (extra large, top) ]                         |     |
|    |   [ Voice Activation Ring (center, expanded pulse) ]                  |     |
|    |   [ Accessibility Pathways (top-right, large node grid) ]             |     |
|    |   [ Input Mode Toggle (bottom-left, large) ]                          |     |
|    |   [ Status & Feedback Line (bottom, expanded text) ]                  |     |
|    +-----------------------------------------------------------------------+     |
|                                                                                  |
| [ Chat Input/Transcript: Persistent at Bottom, never occluded ]                  |
+----------------------------------------------------------------------------------+
EXPANDED PERSONALITY & MOOD SCREEN
Wireframe

pgsql
Copy
Edit
+----------------------------------------------------------------------------------+
|                    [ Personality & Mood: Solo View ]                             |
|----------------------------------------------------------------------------------|
| [ Hearthlink Radial Nav ]                              [Voice][Help][Access]     |
|----------------------------------------------------------------------------------|
|                                                                                  |
|    +-----------------------------------------------------------------------+     |
|    |   [ Animated Mood Ring (very large, center) ]                         |     |
|    |   [ Mood Keyword (in ring, extra large font) ]                        |     |
|    |   [ Recent Emotional Timeline (bottom, extended bar) ]                |     |
|    |   [ Trait Snapshot (side, expanded bar chart) ]                       |     |
|    |   [ Behavioral Bias Badges (bottom-right, full width) ]               |     |
|    +-----------------------------------------------------------------------+     |
|                                                                                  |
| [ Chat Input/Transcript: Persistent at Bottom, never occluded ]                  |
+----------------------------------------------------------------------------------+
All expanded (solo) screens wireframed.

Every persistent element (nav, system controls, chat) is visually placed and protected.

No occlusion, no ambiguity in layout.

Proportional space is used for each panel’s data richness.

NAVIGATION & USER FLOW WIREFRAMES
MODULE NAVIGATION FLOW
Description:
Primary navigation is handled via the Hearthlink radial menu at the top center. Selection animates open a downward arc of 7 module buttons.

Selecting a module: Loads its main dashboard in the panel frame.

System controls (Voice, Help, Accessibility) are always in view and functional.

Navigation is never modal—no selection can obscure chat or controls.

Wireframe Flow:

sql
Copy
Edit
1. Main Screen

+---------------------------------------------+
| [ Hearthlink Glyph (center, top) ]          |
|---------------------------------------------|
| [ ...System Controls: V | H | A... ]        |
+---------------------------------------------+
|  [ Panel Frame: Current Module Panels ]     |
|  [ Chat Input/Transcript ]                  |
+---------------------------------------------+

User Action: Click Hearthlink glyph

2. Radial Menu Expanded

+---------------------------------------------+
| [ Hearthlink Glyph ]                        |
|         [ Module 1 ]                        |
|     [ Module 2 ]   [ Module 3 ]             |
|         [ Module 4 ]                        |
|     [ Module 5 ]   [ Module 6 ]             |
|         [ Module 7 ]                        |
|                                             |
+---------------------------------------------+

User Action: Select Module
→ Loads that module’s panel set in main frame, chat/system controls unchanged.
PANEL EXPANSION FLOW
Description:

Clicking a panel expands it to “solo” screen (full workspace minus nav/chat/controls).

Expanded view maximizes visibility of all associated metrics and controls.

Wireframe Flow:

pgsql
Copy
Edit
1. Main Screen with Panels

+---------------------------+
| [Panel 1] [Panel 2]       |
| [Panel 3] [Panel 4]       |
+---------------------------+

User Action: Click [Panel 2]

2. Expanded Panel View

+-----------------------------------------------+
|          [ Expanded Panel 2 Content ]         |
+-----------------------------------------------+
| [ Chat Input/Transcript ] (persistent)        |
+-----------------------------------------------+

User Action: Click “Back” or select another panel/module
→ Returns to Main Screen, original panel grid state.
PERSISTENT ELEMENTS
Chat Input/Transcript:

Always docked at bottom

Scrollback, search, copy, and export functions

Never occluded by popups, nav, or expanded views

System Controls (Voice, Help, Accessibility):

Always fixed in top-right

Pop-out help and accessibility overlays open as side sheets, never blocking panels or chat

Voice input status always visible and accessible

Radial Menu:

Centered top position

Downward arc animation

Never blocks critical controls or chat

Closed state: only Hearthlink glyph shown

USER FLOW SUMMARY
Module navigation is one click from any context

Panels and screens are never modal except for solo/expanded views (still preserves chat/system controls)

Help and accessibility are global—one tap from anywhere, always open as overlays/sheets

Return navigation always returns user to previous state without occlusion or context loss

RESPONSIVE & ADAPTIVE RULES
All layouts and panels condense vertically for mobile/small screen (panels stack, chat stays bottom-fixed)

System controls collapse to compact icon bar but remain accessible

Voice/Help/Accessibility never covered or hidden, even in overflow states

Panels prioritize vertical scroll over occlusion if display area is tight

All user flows, navigation, and persistent UI rules are now fully wireframed and documented.

If you need:

Additional screens (modals, overlays, pop-outs, etc.)

Mobile/compact wireframes

User journey mapping with explicit step-by-step flows



OPTIONAL with Dependencies


POP-OUT / MODAL OVERLAYS (MOBILE)
Help, Accessibility, or System pop-outs slide in from right or bottom.

Never block panel header or chat input.

Wireframe:

pgsql
Copy
Edit
+---------------------------------------------------------+
|    [ Hearthlink Glyph ]     [Voice][Help][Access]       |
|---------------------------------------------------------|
|    [ Pop-out Overlay: Help/Access/Voice Settings ]      |
|---------------------------------------------------------|
|    [ Panel or Expanded Panel Content ]                  |
|---------------------------------------------------------|
|    [ Chat Input / Voice Toggle ]                        |
+---------------------------------------------------------+
RESPONSIVE INTERACTION RULES
All tap/click targets are 48px minimum for accessibility

Voice/Help/Access overlays always one tap away

Downward navigation preserves mental model; panel stacking reflects desktop experience

Chat input supports swipe/gesture for opening transcript/history

END-TO-END USER JOURNEY SAMPLE (MOBILE)
1. User opens app.

Sees Hearthlink glyph, system controls, and stacked panel headers

2. User taps Radial Nav.

Downward list/arc of modules appears

Selects "Cognition & Memory"

3. Panel loads.

Main Cognition panel header appears at top of stack; tap to expand for deep view

4. User requests help.

Taps "Help" (top-right), overlay slides in from right, content accessible, never blocks chat

5. User chats.

Bottom chat input always accessible; voice toggle adjacent

6. User returns to main.

Closes overlays, collapses expanded panels, radial nav collapses on selection

