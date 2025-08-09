# Passive Widget Audit - Targeted UI Functionality Sprint

**Audit Date:** 2025-07-30  
**Scope:** All *Panel.js, *Interface.js components + EmbeddedGrafana.tsx  
**Objective:** Identify passive widgets requiring user controls when action is needed

## 🔍 AUDIT FINDINGS

### **HIGH PRIORITY - Critical Passive Widgets**

#### 1. **ObservatoryPanel.js** - Anomaly Detection Section (Lines 293-309)
**PASSIVE WIDGET:** Anomaly list displays critical/warning alerts with no action controls
- **CURRENT STATE:** Shows anomalies with timestamp, severity, message - READ ONLY
- **USER NEED:** When critical anomalies appear, users need to investigate details or acknowledge
- **JUSTIFIED CONTROL:** "Details" button → Opens log viewer with full anomaly context
- **ENDPOINT:** `/api/sentry/anomaly/{anomaly.id}/details`

#### 2. **DiagnosticsRepairPanel.js** - System Actions (Lines 211-215)  
**PASSIVE WIDGET:** RESTART SYSTEM and MAINTENANCE MODE buttons are placeholders
- **CURRENT STATE:** Buttons exist but have no onClick handlers
- **USER NEED:** System restart/maintenance controls for critical failures
- **JUSTIFIED CONTROL:** Wire existing buttons to real system endpoints
- **ENDPOINTS:** `/api/core/restart`, `/api/core/maintenance-mode`

#### 3. **SentryInterface.js** - Vulnerability Scan Results (Lines 731-752)
**PASSIVE WIDGET:** Vulnerability scan results show issues but no remediation actions
- **CURRENT STATE:** Displays vulnerabilities with descriptions - NO ACTION BUTTONS
- **USER NEED:** Address critical vulnerabilities (especially CVE-2025-49596)
- **JUSTIFIED CONTROL:** "Fix" button for each critical vulnerability → Auto-remediation
- **ENDPOINT:** `/api/sentry/remediate/{vulnerability.type}`

#### 4. **SentryInterface.js** - MCP Server Cards (Lines 614-638)
**PASSIVE WIDGET:** Shows vulnerable MCP servers but no update controls
- **CURRENT STATE:** claude-code server shows "⚠️ VULNERABLE" with CVE info - READ ONLY
- **USER NEED:** Update vulnerable servers to secure versions
- **JUSTIFIED CONTROL:** "Update" button on vulnerable servers → Server update process
- **ENDPOINT:** `/api/mcp/servers/{server}/update`

### **MEDIUM PRIORITY - Observability Enhancement**

#### 5. **EmbeddedGrafana.tsx** - Dashboard Sidebar (Lines 337-378)
**PASSIVE WIDGET:** Dashboard list shows status indicators but no quick actions
- **CURRENT STATE:** Shows dashboard status dots, no drill-down controls
- **USER NEED:** Quick access to dashboard-specific actions when issues detected
- **JUSTIFIED CONTROL:** "View Details" icon → Opens dashboard-specific log viewer
- **ENDPOINT:** `/api/grafana/dashboard/{id}/logs`

#### 6. **DiagnosticsRepairPanel.js** - Failure Events (Lines 283-305)
**PASSIVE WIDGET:** Failure timeline shows events but no resolution actions
- **CURRENT STATE:** Displays failure events with timestamps - READ ONLY
- **USER NEED:** Mark failures as resolved or get resolution suggestions
- **JUSTIFIED CONTROL:** "Resolve" button → Mark failure as addressed + log resolution
- **ENDPOINT:** `/api/diagnostics/failures/{id}/resolve`

### **LOW PRIORITY - User Experience Polish**

#### 7. **ObservatoryPanel.js** - Agent Graph (Lines 272-291)
**PASSIVE WIDGET:** Live agent graph shows health but no agent-specific actions
- **CURRENT STATE:** Visual graph with health indicators - CLICK TO EXPAND ONLY
- **USER NEED:** Quick agent restart or details when agent shows issues
- **JUSTIFIED CONTROL:** Click on unhealthy agent nodes → Agent management popup
- **ENDPOINT:** `/api/agents/{agent}/status`

#### 8. **EmbeddedGrafana.tsx** - Active Alerts Banner (Lines 309-332)
**PASSIVE WIDGET:** Shows active alerts but no dismiss/acknowledge actions
- **CURRENT STATE:** Displays alert count and messages - READ ONLY
- **USER NEED:** Acknowledge alerts to reduce noise
- **JUSTIFIED CONTROL:** "Dismiss" button on alert items → Acknowledge alert
- **ENDPOINT:** `/api/grafana/alerts/{id}/acknowledge`

## 📋 JUSTIFIED CONTROLS SUMMARY

| Component | Widget | Control | Justification | Priority |
|-----------|--------|---------|---------------|----------|
| ObservatoryPanel | Anomaly List | "Details" button | Critical anomalies need investigation | HIGH |
| DiagnosticsRepairPanel | System Actions | Wire existing buttons | System maintenance requires user control | HIGH |
| SentryInterface | Vulnerability Results | "Fix" button | Critical CVEs need immediate action | HIGH |
| SentryInterface | MCP Server Cards | "Update" button | Vulnerable servers need updates | HIGH |
| EmbeddedGrafana | Dashboard List | "View Details" icon | Dashboard issues need context | MEDIUM |
| DiagnosticsRepairPanel | Failure Events | "Resolve" button | Failure tracking needs closure | MEDIUM |
| ObservatoryPanel | Agent Graph | Clickable agent nodes | Unhealthy agents need management | LOW |
| EmbeddedGrafana | Alert Banner | "Dismiss" button | Alert acknowledgment reduces noise | LOW |

## 🎯 IMPLEMENTATION STRATEGY

### Phase 1: High Priority (Critical Security & System Controls)
1. **Sentry vulnerability remediation controls** - Address critical security gaps
2. **Observatory anomaly detail viewer** - Enable incident investigation
3. **Diagnostics system action wiring** - Enable system maintenance

### Phase 2: Medium Priority (Observability Enhancement)  
1. **Grafana dashboard quick actions** - Improve monitoring workflow
2. **Diagnostics failure resolution tracking** - Complete incident lifecycle

### Phase 3: Low Priority (UX Polish)
1. **Agent management popup** - Streamline agent operations  
2. **Alert acknowledgment system** - Reduce alert fatigue

## 🛠️ TECHNICAL REQUIREMENTS

### Shared UI Components Needed:
- `<DetailButton />` - Consistent details access pattern
- `<ActionButton />` - Primary action buttons with loading states
- `<StatusPopup />` - Modal for detailed views
- `<ConfirmationDialog />` - Dangerous action confirmations

### API Endpoints Required:
- Sentry remediation endpoints
- Agent management endpoints  
- Grafana integration endpoints
- System control endpoints

### E2E Test Scenarios:
- Click vulnerability "Fix" button → Verify remediation API call
- Click anomaly "Details" button → Verify detail popup appears
- Click agent node → Verify management popup opens
- Click system restart → Verify confirmation dialog + API call

**AUDIT COMPLETE** - 8 passive widgets identified, 8 justified controls defined, implementation strategy prioritized by user value.