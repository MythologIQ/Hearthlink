# Hearthlink

## Overview
Hearthlink is an AI agent orchestration system with voice interaction capabilities, designed for secure, multi-agent collaboration and user assistance.

## Electron Asset Loading & Troubleshooting

### ✅ Asset Loading Resolution
The Electron application now properly loads all static assets (CSS, icons, PNGs) through:

1. **Protocol Handler**: Custom `app://` protocol for secure asset serving
2. **Static Server Fallback**: HTTP server on port 3001 for robust delivery
3. **Security Validation**: Path traversal protection and content type handling
4. **Error Recovery**: Graceful handling of missing or corrupted assets

### 🚀 Quick Launch Instructions

#### Method 1: Using Launch Script (Recommended)
```bash
# Windows
.\launch_electron_dev.bat

# The script will:
# - Clear previous Electron processes
# - Create log directory if needed
# - Set NODE_ENV=development
# - Build if needed (auto-rebuild if >5 minutes old)
# - Launch Electron with proper asset loading
```

#### Method 2: Manual Launch
```bash
# Set environment variables
set NODE_ENV=development
set ELECTRON_START_URL=file://%CD%\build\index.html

# Build the application
npm run build

# Launch Electron
npm start
```

#### Method 3: Development Mode
```bash
# Start React dev server
npm start

# In another terminal, launch Electron pointing to dev server
set ELECTRON_START_URL=http://localhost:3000
npm run electron-dev
```

### 🔧 Troubleshooting

#### Asset Loading Issues
**Symptoms**: CSS not applied, icons missing, ERR_FILE_NOT_FOUND errors

**Solutions**:
1. **Clear Cache**: Delete `build/` directory and rebuild
2. **Check Protocol**: Ensure `app://` protocol is registered in main.js
3. **Verify Static Server**: Check if port 3001 is available
4. **Validate Assets**: Run `node tests/electron_asset_load.test.js`

#### Window Not Displaying
**Symptoms**: Electron process running but no window visible

**Solutions**:
1. **Check Task Manager**: Verify electron.exe is running
2. **Force Focus**: Use Alt+Tab or check for hidden windows
3. **Restart Process**: Kill electron.exe and relaunch
4. **Check Logs**: Review logs in `logs/` directory

#### Build Issues
**Symptoms**: Build fails or assets missing

**Solutions**:
1. **Clean Install**: `rm -rf node_modules && npm install`
2. **Clear Cache**: `npm run build -- --reset-cache`
3. **Check Dependencies**: Ensure all packages installed
4. **Validate package.json**: Check homepage field is set to "./"

### 📊 Validation Checklist

#### ✅ Pre-Launch Validation
- [ ] Build directory exists with `index.html`
- [ ] All 16 required assets present in `build/assets/`
- [ ] CSS and JS files in `build/static/`
- [ ] Asset manifest valid (`build/asset-manifest.json`)

#### ✅ Launch Validation
- [ ] Log directory created (`logs/`)
- [ ] NODE_ENV=development set
- [ ] Static server starts on port 3001
- [ ] Electron process visible in Task Manager
- [ ] Main window displays correctly

#### ✅ Asset Loading Validation
- [ ] CSS styles applied correctly
- [ ] All icons and images display
- [ ] Radial menu functional
- [ ] Navigation working properly
- [ ] Voice HUD responsive

### 🧪 Test Suite
Run comprehensive asset loading tests:
```bash
node tests/electron_asset_load.test.js
```

**Expected Output**:
```
🚀 Starting Electron Asset Loading Tests
==========================================
✅ Build directory exists
✅ index.html exists
✅ static directory exists
✅ assets directory exists
✅ Asset manifest is valid
✅ 2 entrypoints validated
✅ All 16 required assets exist
✅ Static server started on port 3001
✅ All static server tests passed
✅ No hardcoded file:// paths found
✅ Protocol handler properly configured

📊 ELECTRON ASSET LOADING TEST REPORT
==========================================
Total Tests: 6
Passed: 6
Failed: 0
Duration: 6062ms

🎉 ALL TESTS PASSED!
✅ Electron asset loading is properly configured
```

## Navigation Model

### Main Interface Access
- **Alden Radial Menu**: Primary navigation hub accessible via voice command "Hey Alden" or main interface
- **Module Launcher**: Central dashboard for accessing all system modules
- **Voice HUD**: Universal voice interface with real-time input display

### Core Modules & Screens

#### Alden (Productivity Assistant)
- **Radial Menu**: Main navigation interface with quick access to all Alden features
- **Weekly Dashboard**: Goal tracking, decision friction analysis, and productivity metrics
- **Self-Care Tracker**: Wellness monitoring and self-care activity logging
- **Goal Setting Panel**: SMART goal creation and progress tracking
- **Decision Friction Panel**: Analysis of decision-making patterns and blockers
- **Productivity Center**: Task management and workflow optimization

#### Core (System Orchestration)
- **Command Center**: Central system control and agent management
- **Agent Orchestration**: Multi-agent coordination and task delegation
- **Session Management**: Active session monitoring and control
- **Logs/Diagnostics**: System health monitoring and troubleshooting
- **Secure Room Management**: Isolated environments for sensitive operations
- **Dev Mode Interface**: Developer tools and advanced configurations

#### Synapse (Plugin Management)
- **Plugin Manager Dashboard**: Installed plugins overview and management
- **Plugin Install/Config Modal**: New plugin installation and configuration
- **External Integrations**: Third-party service connections and APIs

#### Sentry (Security Monitoring)
- **Security Dashboard**: Real-time security monitoring and alerts
- **Kill Switch Panel**: Emergency system shutdown and security controls
- **Audit Logs**: Comprehensive security event logging and analysis

#### Vault (Memory Management)
- **Main Dashboard**: Memory overview and data management
- **Memory Permissions Manager**: Access control and data privacy settings
- **Diagnostics Toolset**: Memory system health and performance monitoring

#### Settings & Configuration
- **Voice Settings**: Voice interaction configuration and calibration
- **Security & Privacy**: Authentication, encryption, and privacy controls
- **Accessibility Panel**: Accessibility features and accommodations
- **System Preferences**: General application settings and preferences

#### Help & Documentation
- **Help Main Panel**: User guides and troubleshooting resources
- **Voice Interaction Guide**: Voice command reference and tutorials
- **Accessibility Guide**: Accessibility features and usage instructions
- **Troubleshooting**: Common issues and solutions

### Universal Features
- **Voice Interaction HUD**: Real-time voice input display and agent selection
- **Agent Chat Interface**: Per-agent communication and interaction
- **Notification Center**: System alerts and user notifications
- **Room Manager**: Workspace organization and context switching

### Navigation Methods
1. **Voice Commands**: "Hey Alden", "Open Core", "Show Vault", etc.
2. **Radial Menu**: Click-based navigation through Alden's interface
3. **Module Launcher**: Direct access to all system modules
4. **Keyboard Shortcuts**: Quick access to frequently used features
5. **Menu System**: Traditional menu-based navigation

### Access Control
- **Role-Based Access**: Different features available based on user role
- **Permission Levels**: Granular control over feature access
- **Secure Mode**: Enhanced security for sensitive operations
- **Offline Mode**: Limited functionality when offline

## Voice Interaction System

### Voice Routing & Agent Management
- **Multi-Agent Support**: Alden, Alice, Mimic, Sentry, and external agents
- **Voice HUD**: Real-time voice input display and agent selection interface
- **Misroute Recovery**: Alden handles all voice misroutes via intelligent recovery dialogue (no rigid prompts)
- **Agent Deference**: Agents can suggest better-suited agents through three interaction styles
- **Default Handler**: Alden serves as the default handler for misrouted input

### Voice Policy Compliance
- **Local Agents**: Fully conversational with name-based addressing
- **External Agents**: Disabled by default, require explicit permission activation
- **Offline Mode**: Dynamic, observable detection using multiple validation points
- **Authentication**: Secure mode activation with challenge/PIN system
- **Permission Override**: Global defaults can override per-agent permissions

## Test-Driven Development

### Distributed Test Policy Structure
Test requirements are distributed across multiple source documents rather than centralized in a single test plan:

- **Test Planning Requirements**: `/docs/process_refinement.md`
- **Voice Functionality Tests**: `/docs/VOICE_ACCESS_POLICY.md`
- **UI Screen Validation**: `/docs/UI_ALIGNMENT_AUDIT.md`
- **Test Reference & Traceability**: `/docs/TEST_REFERENCE.md`

### Test Implementation Standards
- **Feature Branches**: All tests under `feature/ui-test-*` branches
- **Commit Format**: `UI_TEST: [FEATURE_ID] - [Description] (Source: [audit/sprint/etc.])`
- **Pass Rate**: 100% required for merge approval
- **JSON Logging**: Required for all state/data tests

## Documentation Structure

### Core Policy Documents
- **Voice Access Policy**: `/docs/VOICE_ACCESS_POLICY.md` - Voice interaction rules and system behavior
- **UI Alignment Audit**: `/docs/UI_ALIGNMENT_AUDIT.md` - Approved UI screens and validation requirements
- **Process Refinement**: `/docs/process_refinement.md` - Development standards and compliance requirements

### User Documentation
- **User Manual**: `/docs/USER_MANUAL.md` - Voice interaction guide and troubleshooting
- **Feature Map**: `/docs/FEATURE_MAP.md` - Feature implementation status and traceability

### Test Documentation
- **Test Reference**: `/docs/TEST_REFERENCE.md` - Test traceability and compliance documentation
- **Sprint Completion Log**: `/docs/SPRINT_COMPLETION_LOG.md` - Sprint status and implementation uncertainties

## Quick Start

### Voice Interaction
1. **Enable Voice**: Ensure voice interaction is enabled in settings
2. **Address Agents**: Say "Hey Alden" or "Alice, can you help me..."
3. **Use Voice HUD**: Visual interface for agent selection and input display
4. **Trust Recovery**: Let Alden handle misroutes and suggest better agents

### Development
1. **Feature Branches**: Create `feature/ui-test-*` branches for all UI work
2. **Test Compliance**: Ensure 100% test pass rate before merge
3. **Documentation**: Update relevant policy and audit documents
4. **Traceability**: Link all changes to source documents and feature IDs

## Architecture

### Core Components
- **Core**: Agent orchestration and session management
- **Vault**: Memory management and audit logging
- **Synapse**: Plugin management and external integrations
- **Sentry**: Security monitoring and kill switch functionality

### Voice System
- **Voice HUD**: Universal voice interface with live transcript
- **Agent Routing**: Intelligent routing with misroute recovery
- **Authentication**: Secure mode activation for system modifications
- **Logging**: Complete session logging and audit trail

## Support

For questions about voice interaction, testing, or development:
- **Voice Policy**: `/docs/VOICE_ACCESS_POLICY.md`
- **UI Requirements**: `/docs/UI_ALIGNMENT_AUDIT.md`
- **Process Standards**: `/docs/process_refinement.md`
- **Contact**: `system@hearthlink.local`
