## 1. Global Shell Layout (All Personas)

```
pgsql
```

CopyEdit

`+------------------------------------------------------------------+ | [Persona Icon, fixed] | [Persona Name, Progress/State] | | [Status Bar: LLM | Vault | Sentry | Synapse | Learning State] | +------------------------------------------------------------------+ | [Utility Strip / Radial Menu — contextually adaptive controls] | +------------------------------------------------------------------+ | [Main Area: Active Screen per persona] | +------------------------------------------------------------------+ | [Footer: Session summary | Reflection prompt | Version/Status] | +------------------------------------------------------------------+`

**Design Principles & Visual Language:**

- MythologIQ gold (`#E3B23C`), sapphire blue, deep violet, and onyx black theme tokens.
- Dark mode default, ancient/mineral texture (`obsidian-bg.png`) with animated starfield overlay (`stars.png`)—toggleable for accessibility.
- Persistent persona icon, mythic-cyber theme: runes, stardust, glowing accent lines.
- Status bar icons animate on activity, pulse on alert; module “orbs” (LLM, Vault, etc.) light up as if magical artifacts.
- Fully accessible (WCAG 2.1 AA), all icons/controls labeled, tab order logical.
- Persona tokens and mood shown as color/aura or animated highlight.

---

## 2. Alden — Evolutionary Companion UI

**Screens & Thematic Overlays:**

- **Hub:**
  - Growth trajectory “milestone stones” (runes light up with progress).
  - “Our Journey” timeline (animated path; glyphs mark events).
  - Reflection prompt: parchment overlay, mythic font.
- **Cognition:**
  - Dynamic board: gold-threaded habit/task links.
  - Adaptive checklists, animated “habit streak” meter (glows).
- **Interaction:**
  - Rich journal, illuminated with “memory glyphs” on review.
  - Mood tracker: color pulse behind Alden’s icon.
  - “Coach Mode”: Alice insights rendered as stardust or ripple effect.
- **Development:**
  - “Level-up” cards: rise from milestone stone, shimmer on earn.
  - Tutorial/skill hints as illuminated scrolls.

**Navigation/Utility:**

- Radial menu animates open, bubbles up “reflection” or “review session” after major events.
- Reflection button: launches animated “fireside” summary, badges float up on achievement.

**Session Review/Feedback:**

- All screens live-update with context; edits visibly animate, “rewind” shows history.
- Achievement badges and progress rings light up with mythic sparkle.
- Direct feedback overlays: animated as golden or blue runic shields.

---

## 3. Alice — Behavioral Analysis & Context UI

**Screens & Thematic Overlays:**

- Dashboard:
  - Trend graphs for tone/cadence are superimposed over a shimmering “insight pool”.
  - “Current Understanding” scroll (soft-glow border).
- Feedback Overlay:
  - “Teach Alice” moments: ancient sigil appears, then dissolves into background.
- Session Log:
  - Every correction or inference appears as a faint constellation node.
  - Exportable as “scroll” with digital overlay.
- Coaching:
  - Alice’s suggestions surface via glowing blue badges, only via Alden or user request.

---

## 4. Mimic — Persona & Analytics UI

**Screens & Thematic Overlays:**

- Persona Carousel:
  - Carousel is a “wheel of fate”, each persona is a mask with animated glow showing “life”/usage.
- Persona Generation:
  - Steps: name, icon (mask variant), trait pins, preview, all in an arcane circle overlay.
- Performance:
  - Metrics shown as animated star constellations—stars light up as metrics grow.
- Archive/Restore:
  - Retired personas fade into background with “tomb of legends” animation.
  - Fork/Merge via interactive “thread of fate”.

---

## 5. Vault — Memory Management UI

**Screens & Thematic Overlays:**

- Memory Usage:
  - Animated gold “memory veins” pulse as new records are created.
  - Usage graphs as branching lines in obsidian.
- Audit Log:
  - Timeline/book format; entries glow as added, filter glows on search.
- Export/Backup:
  - Export and purge actions: “Key of Destiny” unlock animation.
- Access Control:
  - Persona badges, access trails animate as glowing paths.
  - Full permissions map appears as illuminated network.

---

## 6. Core — Collaboration & Session UI

**Screens & Thematic Overlays:**

- Active Personas:
  - Agents seated around a circular table, avatars glow as they “speak”.
- Session History:
  - Timeline as a burning “log” (embers pulse as agents act).
- Context Flow:
  - Arrows between avatars animate as glowing “threads of fate”.
- Breakout Sessions:
  - Radial “side chambers” animate out from the main hearth; drag agents in/out.

---

## 7. Synapse — External Gateway UI

**Screens & Thematic Overlays:**

- Connections:
  - Active/pending plugins shown as animated star “links” or “constellations”.
- Plugins:
  - Each plugin is an “obelisk”—permission status locks/unlocks glow with runes.
- Logs:
  - Risk tier overlays: aurora borealis effect, flares with risk.
- Endpoint Management:
  - Whitelist/blacklist as enchanted gates, controls animate on change.

---

## 8. Sentry — Security & Compliance UI

**Screens & Thematic Overlays:**

- Security Events:
  - Central “Watcher’s Eye” pulses outward for alerts/violations.
- Policy Editor:
  - Editable scroll/GUI; policy check passes show as scales balancing, failures tip scales.
- Compliance:
  - Ancient “book” with digital overlays, live export/audit status.
- Incident Log:
  - Incident events ripple across UI, override actions logged with glowing highlight.

---

## 9. Accessibility & UX Guidance

- High-contrast, tokenized color for every persona.
- All modules keyboard and screen-reader navigable.
- Animated feedback: mythic effects for switching, policy triggers, learning events.
- Persistent guided overlays, mythic/modern “voice” for onboarding.
- Responsive (desktop/tablet/mobile), accessibility settings for animation/background.

---

## 10. Asset Management

- All icons/persona images managed in `/public/assets` and referenced by module.
- MythologIQ branding/theme tokens in global theme file.
- Animation/CSS variables for effects, background layers toggleable for performance/accessibility.
- Source/design docs referenced in UI folder.



# 11. UI Kit Generation: MythologIQ Hearthlink

## 11.1 Color System

| NameTokenHEXUsage |                |         |                              |
| ----------------- | -------------- | ------- | ---------------------------- |
| MythologIQ Gold   | `color-gold`   | #E3B23C | Accents, active, achievement |
| Sapphire Blue     | `color-blue`   | #2785C4 | Info, primary buttons, Alice |
| Deep Violet       | `color-violet` | #2E244A | Headers, core, backgrounds   |
| Onyx Black        | `color-onyx`   | #181923 | Base, panels, cards          |
| Stardust White    | `color-white`  | #FAFAFC | Text, icons, overlays        |
| Ember Red         | `color-ember`  | #D94F4F | Alerts, destructive          |
| Memory Green      | `color-green`  | #48C784 | Success, good feedback       |

---

## 11.2 Typography

- **Heading**: `Cinzel`, serif, uppercase, letterspaced
- **Body**: `Inter`/`Roboto`, clean sans, 16px base
- **Mono**: `Fira Mono` for logs/code
- **Display**: MythologIQ “brand font” for logo, banners, persona names

---

## 11.3 Spacing & Layout

- 8px grid
- Main content max width: 1200px
- Card radius: 16px
- Shell padding: 32px (desktop), 16px (mobile)
- Footer/header: fixed height, always visible

---

## 11.4 Core Components

### 1. **Header**

- Logo left, persona/avatar center, status bar right
- Supports “live” accent underline for active persona/module

### 2. **Status Bar**

- Animated orbs for: LLM, Vault, Sentry, Synapse, Learning State
- Hover: tooltips, click: open log/details

### 3. **Persona Card**

- Icon, name, state, mood aura ring
- Glow/animation on select or level up

### 4. **Utility Menu**

- Radial (desktop), collapsible linear (mobile)
- Contextual: shows most-used or active tool first

### 5. **Main Content Area**

- Tabbed or single page SPA
- Supports grid, card, or timeline layouts as needed

### 6. **Session/Timeline Log**

- Log entries as “embers” or “runes”, animate on add
- Scrollable, filterable by type/persona

### 7. **Animated Elements**

- “Milestone Stones” (Alden), “Insight Pool” (Alice), “Masks” (Mimic)
- Animated SVGs for achievement, event, or error
- Starlit parallax background with toggle

### 8. **Modal/Dialog**

- Mythic border, gold highlight, blurred background
- Focus trap, always dismissable with ESC/close

### 9. **Form Elements**

- Inputs, toggles, and dropdowns styled with dark base and gold/blue focus
- Buttons: primary (gold), secondary (blue), danger (ember)

### 10. **Footer**

- Session stats, reflection prompt (editable), app version, feedback link

---

## 11.5 Iconography & Illustration

- **All Persona Icons**: Provided as SVG, sized 48x48 and 96x96
- **Global Glyphs**: Rune library, scalable, used for achievements/events
- **Status Orbs**: SVGs with animated states (pulse, glow, flicker)

---

## 11.6 Asset Catalog

| AssetFileRecommended SizeUsage |                   |                  |                       |
| ------------------------------ | ----------------- | ---------------- | --------------------- |
| Header Logo                    | `header-logo.png` | SVG, 320x80      | Main shell header     |
| Obsidian BG                    | `obsidian-bg.png` | 1920x1080        | All pages, main shell |
| Stars Overlay                  | `stars.png`       | 1920x1080, alpha | Overlay, parallax     |
| Persona Icons                  | `/persona/*.svg`  | 48x48, 96x96     | Persona cards, status |
| Module Badges                  | `/badges/*.svg`   | 32x32            | Achievements, log     |
| Milestone Stones               | `/runes/*.svg`    | 64x64            | Timeline, badges      |

---

## 11.7 Animations & Motion

- **Transitions**: fade, slide, or swirl (stardust) for module switches
- **Success/Error**: gold wave (success), ember spark (error)
- **Badges/Achievements**: float up, shimmer, rotate
- **Status Bar**: Orbs pulse when active, flicker on warning

---

## 11.8 Theming & Tokens

- CSS custom properties or Tailwind theme map
- All color, spacing, and font variables prefixed (e.g., `--myth-color-gold`)
- Animation keyframes documented for all major interactions
- Persona modules can override accent theme per mode

---

## 11.9 Accessibility

- High contrast, no reliance on color alone
- Tab order, focus, aria-labels everywhere
- All icons alt-tagged, motion can be reduced/toggled in settings
- Keyboard navigation to all interactive elements
- Dynamic scaling for mobile/tablet

---

## 11.10 Sample Figma/Page Layouts

**[Provide to designer:]**

- Global Shell
- Alden Hub
- Alice Dashboard
- Mimic Carousel
- Vault Memory Map
- Core Roundtable
- Synapse Plugin Manager
- Sentry Security Center



## 12. High-Fidelity Mockup

### 12.1 Global Shell (All Personas)

- **Header:**
  - *Left*: Persona Icon (SVG), always visible.
  - *Center*: Persona Name, Level/Title, animated aura ring.
  - *Right*: Status Bar (animated “artifact orbs”: LLM, Vault, Sentry, Synapse, Learning), User Avatar.
- **Background:**
  - Layer 1: `obsidian-bg.png` (full-viewport, 50% opacity overlay)
  - Layer 2: `stars.png` (CSS parallax, starfield moves with mouse/scroll; toggle in settings)
- **Utility Strip:**
  - Floating radial or collapsible strip, context-sensitive (theme: gold/blue buttons, subtle glow on hover)
- **Main Area:**
  - Content panel (rounded corners, soft inner shadow), card grid for module/dashboard, shadowed header.
- **Footer:**
  - Left: Session summary (activity, stats)
  - Center: Reflection prompt (editable, hinting mythic wisdom)
  - Right: Build version, feedback link, live clock (optional)

---

### 12.2 Alden Hub

- **Growth Path Timeline:**
  - Horizontal or spiral stone path, “milestone stones” (runes light up on unlock)
  - Animated gold threads connect tasks/habits
  - Reflection/journal overlay: parchment sheet, mythic font
- **Mood/Coach Tracker:**
  - Color pulse/animation around Alden icon for mood
  - Alice “coach” hints appear as floating stardust
- **Level-Up Event:**
  - Achievement badge floats up, shimmer effect
  - Radial menu animates open after progress

---

### 12.3 Alice Dashboard

- **Trend Graphs:**
  - Tone/cadence lines animate over liquid “insight pool” background
  - Sigils for user feedback, softly dissolve into pool
- **Session Log:**
  - Timeline: constellation nodes, highlight on feedback events
  - Export overlay: illuminated scroll (digital + mythic styling)
- **Feedback/Teach:**
  - Popup with ancient runic border, dissolves after correction

---

### 12.4 Mimic Carousel

- **Persona Masks:**
  - Carousel (wheel of fate): mask avatars morph as user scrolls
  - Stats and traits as stars/constellations; animate on changes
- **Fork/Merge:**
  - “Thread of fate” effect: animated thread weaves between personas during merge
  - Archive: mask fades, enters “tomb” panel

---

### 12.5 Vault

- **Memory Graph:**
  - Radial network map (nodes: memory slices/persona), gold lines pulse on access
  - Usage/permission overlays: glowing paths, color-coded by risk/access
- **Audit Book:**
  - Timeline with turning pages, entries glow as added
  - “Key of Destiny” animation on export/purge (large, gold, visually satisfying)

---

### 12.6 Core Roundtable

- **Hearth Table:**
  - Circular “roundtable”, avatars/agents around edge, glow as they “speak”
  - Firelight or ember animation on main topic area
- **Breakout/Context:**
  - Side chambers as floating panels, agents drag/drop in/out
  - Animated arrows (glowing threads of fate) show context flow

---

### 12.7 Synapse Plugin Manager

- **Constellation Map:**
  - Plugins as obelisks; star links animate as connections live
  - Risk state: aurora flare effect behind plugin card
- **Endpoint Controls:**
  - Enchanted gates (open/close animation), whitelist/blacklist toggle

---

### 12.8 Sentry Security Center

- **Watcher’s Eye:**
  - Central animated glyph pulses on alert
  - Policy scroll: digital + ancient, animated scales for policy checks
- **Incident Log:**
  - Ripple highlight for new event, all override actions glow

---

### 12.9 Global Accessibility

- **Contrast preview toggle:** see how every page/element looks for low vision
- **Animation toggle:** reduce motion, flatten parallax if desired
- **All icons alt-tagged, tab order preview in prototype**

---
