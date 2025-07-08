**Title:** Alden Weekly Dashboard Module — Platinum+ Spec

**Purpose:**
A unified weekly operating system for ADHD users that emphasizes prioritization, cognitive scaffolding, and executive function alignment without relying on traditional time-blocking or neurotypical planners. This module integrates directly into Alden’s Cognition layer.

---

### SECTION 1: WEEKLY HEADER

* **Field: Week of \[Date Input]**
* **Self-Care Tracker (Daily x 4 Fields)**

  * Categories: Sleep, Meds, Movement, Nutrition
  * UI: 7-day toggle grid (M–S) for each category
  * Function: Tied to dynamic EF status indicators in Alden’s reflection engine

---

### SECTION 2: MAGNETIC NORTH

> **Permanent Top Panel: Always Visible (Pinned)**

* **Mission**

  * User-defined statement of purpose
  * Used for weekly alignment scoring

* **Vision**

  * Description of what successful implementation looks like

* **Values**

  * List of 3–5 guiding principles
  * Influence decision triage and prioritization sort logic

---

### SECTION 3: DECISION FRICTION (UNMADE DECISIONS)

* **Function:** Externalize cognitive load from pending choices
* **UI Element:** Plain text list, editable
* **Optional Feature:** Nudging logic triggers if decision remains static > 3 days

---

### SECTION 4: GOALS / ROCKS / NEXT STEPS TABLE

* **Structure:** 3-column goal layout

* **Rows:**

  * Goal
  * Weekly Rock
  * Smallest Next Step

* **Behavior:** Inline editing, checklist support, auto-promotion of completed thin slices into reflection log

---

### SECTION 5: PRIORITY FILTERING WORKFLOW

1. **Brain Dump Zone**

   * UI: Freeform scratchpad, text + audio input
   * Constraint: No sorting or editing in this zone

2. **Filter to 5 Priorities**

   * Function: Select 5 items most aligned with Magnetic North
   * Feature: Built-in friction score meter (low = dopamine trap, high = aligned challenge)

3. **Select 2–3 for Execution Track**

   * Drag-and-drop into execution pipeline
   * Validation: At least one must align directly with a Weekly Rock

---

### SECTION 6: WEEK STRUCTURE (EXECUTION LANE)

* **Grid Layout: Monday–Friday**

* **Columns:**

  * 2-Hour Workday Priority
  * Other Stuff

* **Rules:**

  * Max one 2HR W/D task per day
  * Auto-alert if more than 3 low-friction tasks populate week

* **No Time Anchoring:**

  * Emphasis is on sequence, not clock

* **Feedback Loop:** Daily check-in nudges to confirm completion + mood snapshot

---

### SECTION 7: COMPLETION TRACKER

* **Zone:** ‘✅ Tasks Completed This Week’
* **Display:** Progressive list with timestamp + emoji/mood marker
* **Syncs with:**

  * Vault → Weekly log
  * Alden’s reflection engine
  * Optional export to user-defined folder

---

### SYSTEM INTERACTIONS

* **Anchored UI Components:**

  * Magnetic North panel always visible
  * Self-care tracker semi-transparent overlay on dashboard when relevant

* **Persona Feedback (Alden):**

  * Positive reinforcement on alignment
  * Gentle course correction on misalignment (via nudges, not commands)

* **Voice Support (if enabled):**

  * Weekly check-in and summary available via TTS/STT

---

### NOTES FOR IMPLEMENTATION

* All fields are user-editable
* Memory slices to store weekly snapshots
* Audit trail in Vault to support habit review and alignment over time
* No assumptions about daily consistency: dynamic adaptation preferred

---

**End of Spec: Ready for UI integration into Alden's Cognition module.**
