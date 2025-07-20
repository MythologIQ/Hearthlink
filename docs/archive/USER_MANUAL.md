# Hearthlink User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Voice Interaction](#voice-interaction)
3. [Main Interface](#main-interface)
4. [Module Screens](#module-screens)
5. [Settings & Configuration](#settings--configuration)
6. [Help & Support](#help--support)
7. [Troubleshooting](#troubleshooting)
8. [Launch Troubleshooting](#launch-troubleshooting)

---

## Getting Started

### First Launch
1. **Installation**: Follow the installation guide in the Quick Start section
2. **Voice Setup**: Complete voice interaction calibration in Settings
3. **Initial Configuration**: Set up your preferences and accessibility options
4. **Agent Introduction**: Meet Alden, your primary productivity assistant

### Quick Navigation
- **Voice Command**: Say "Hey Alden" to activate the main interface
- **Radial Menu**: Click the central Alden icon for quick access to all features
- **Module Launcher**: Use the module icons to switch between system components

---

## Launch Troubleshooting

### 🚀 Launch Methods

#### Method 1: Launch Script (Recommended)
```bash
# Windows
.\launch_electron_dev.bat
```

**What the script does:**
- ✅ Clears previous Electron processes
- ✅ Creates log directory if needed
- ✅ Sets NODE_ENV=development
- ✅ Builds if needed (auto-rebuild if >5 minutes old)
- ✅ Launches Electron with proper asset loading

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

### 🔧 Common Launch Issues

#### Issue 1: Electron Window Not Displaying
**Symptoms**: 
- Electron process running in Task Manager
- No visible application window
- Console shows "Main window loaded successfully"

**Solutions**:
1. **Check for Hidden Windows**:
   - Press Alt+Tab to cycle through windows
   - Check if window is minimized to system tray
   - Look for window behind other applications

2. **Force Window Focus**:
   ```bash
   # Kill existing process
   taskkill /f /im electron.exe
   
   # Relaunch with focus
   npm start
   ```

3. **Check Display Settings**:
   - Ensure primary display is active
   - Check for multi-monitor issues
   - Verify display scaling settings

#### Issue 2: Asset Loading Failures
**Symptoms**:
- CSS not applied (plain text appearance)
- Icons and images missing
- Console errors: "ERR_FILE_NOT_FOUND"

**Solutions**:
1. **Clear Build Cache**:
   ```bash
   # Remove build directory
   rmdir /s build
   
   # Rebuild application
   npm run build
   ```

2. **Validate Asset Loading**:
   ```bash
   # Run asset loading tests
   node tests/electron_asset_load.test.js
   ```

3. **Check Protocol Handler**:
   - Verify `app://` protocol is registered in main.js
   - Ensure static server starts on port 3001
   - Check for port conflicts

#### Issue 3: Build Failures
**Symptoms**:
- Build process fails with errors
- Missing dependencies
- Asset manifest issues

**Solutions**:
1. **Clean Install**:
   ```bash
   # Remove node_modules and reinstall
   rmdir /s node_modules
   npm install
   ```

2. **Clear NPM Cache**:
   ```bash
   npm cache clean --force
   npm install
   ```

3. **Reset Build Cache**:
   ```bash
   npm run build -- --reset-cache
   ```

#### Issue 4: Environment Variable Issues
**Symptoms**:
- NODE_ENV not respected
- Wrong asset loading behavior
- Development vs production confusion

**Solutions**:
1. **Verify Environment Variables**:
   ```bash
   # Check current environment
   echo %NODE_ENV%
   echo %ELECTRON_START_URL%
   ```

2. **Set Correct Environment**:
   ```bash
   # For development
   set NODE_ENV=development
   set ELECTRON_START_URL=file://%CD%\build\index.html
   
   # For production
   set NODE_ENV=production
   set ELECTRON_START_URL=file://%CD%\build\index.html
   ```

#### Issue 5: Port Conflicts
**Symptoms**:
- Static server fails to start
- "Port already in use" errors
- Asset loading fails

**Solutions**:
1. **Check Port Usage**:
   ```bash
   # Check what's using port 3001
   netstat -ano | findstr :3001
   ```

2. **Kill Conflicting Processes**:
   ```bash
   # Kill process using port 3001
   taskkill /f /pid <PID>
   ```

3. **Use Different Port**:
   - Modify main.js to use different port
   - Update ELECTRON_START_URL accordingly

#### Issue 6: Log Directory Issues
**Symptoms**:
- Launch script fails to create logs
- Permission errors
- Missing log files

**Solutions**:
1. **Manual Log Directory Creation**:
   ```bash
   # Create logs directory
   mkdir logs
   ```

2. **Check Permissions**:
   - Ensure write permissions to project directory
   - Run as administrator if needed

3. **Verify Log File Creation**:
   ```bash
   # Check if log files are created
   dir logs
   ```

### 📊 Launch Validation Checklist

#### Pre-Launch Checks
- [ ] **Build Directory**: `build/` directory exists with `index.html`
- [ ] **Assets Present**: All 16 required assets in `build/assets/`
- [ ] **Static Files**: CSS and JS files in `build/static/`
- [ ] **Manifest Valid**: `build/asset-manifest.json` is valid
- [ ] **Dependencies**: All npm packages installed
- [ ] **Environment**: NODE_ENV and ELECTRON_START_URL set correctly

#### Launch Process Checks
- [ ] **Log Directory**: `logs/` directory created successfully
- [ ] **Process Cleanup**: Previous Electron processes terminated
- [ ] **Static Server**: Server starts on port 3001 without conflicts
- [ ] **Protocol Handler**: `app://` protocol registered successfully
- [ ] **Electron Process**: electron.exe visible in Task Manager
- [ ] **Window Display**: Main window appears and is visible

#### Post-Launch Validation
- [ ] **Asset Loading**: CSS styles applied correctly
- [ ] **Images Display**: All icons and images visible
- [ ] **Navigation**: Radial menu and navigation functional
- [ ] **Voice HUD**: Voice interface responsive
- [ ] **Error Logs**: No critical errors in console
- [ ] **Performance**: Application responds quickly

### 🧪 Diagnostic Commands

#### Asset Loading Test
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

#### Process Status Check
```bash
# Check if Electron is running
tasklist | findstr electron

# Check port usage
netstat -ano | findstr :3001

# Check log files
dir logs
```

#### Environment Validation
```bash
# Check environment variables
echo %NODE_ENV%
echo %ELECTRON_START_URL%

# Check build status
dir build
dir build\assets
dir build\static
```

### 🚨 Emergency Recovery

#### Complete Reset
If all else fails, perform a complete reset:

```bash
# 1. Kill all Electron processes
taskkill /f /im electron.exe

# 2. Clear all caches
rmdir /s build
rmdir /s node_modules
npm cache clean --force

# 3. Reinstall dependencies
npm install

# 4. Rebuild application
npm run build

# 5. Launch with fresh environment
set NODE_ENV=development
set ELECTRON_START_URL=file://%CD%\build\index.html
npm start
```

#### Fallback Launch
If the main launch methods fail, try the fallback:

```bash
# Use static server fallback
npx serve -s build -p 3001

# In another terminal, launch Electron
set ELECTRON_START_URL=http://localhost:3001
npm start
```

### 📞 Getting Help

#### Before Contacting Support
1. **Run Diagnostic Tests**: Execute `node tests/electron_asset_load.test.js`
2. **Check Logs**: Review files in `logs/` directory
3. **Verify Environment**: Ensure all environment variables are set correctly
4. **Test Alternative Methods**: Try different launch methods

#### Support Information
- **Documentation**: Check this manual and README.md
- **Log Files**: Review logs in `logs/` directory for error details
- **Test Results**: Include output from asset loading tests
- **Environment**: Provide details about your system and environment

---

## Voice Interaction

### Basic Voice Commands
- **"Hey Alden"**: Activate the main interface and radial menu
- **"Open [Module]"**: Navigate to specific modules (Core, Vault, Synapse, Sentry)
- **"Show [Screen]"**: Access specific screens within modules
- **"Help"**: Get contextual help and command suggestions

### Voice HUD (Heads-Up Display)
The Voice HUD provides real-time feedback for voice interactions:
- **Listening Indicator**: Shows when the system is listening for commands
- **Command Display**: Shows recognized voice input
- **Agent Selection**: Visual interface for choosing which agent to interact with
- **Status Updates**: Real-time feedback on command processing

### Agent Deference Protocol
When you ask a question that would be better handled by a different agent:
1. **Suggestion**: The current agent suggests a better-suited agent
2. **Confirmation**: You can accept or decline the suggestion
3. **Handoff**: Smooth transition to the suggested agent
4. **Context Transfer**: Relevant information is passed to the new agent

---

## Main Interface

### Alden Radial Menu
The primary navigation hub accessible via voice or click:

**Central Features:**
- **Weekly Dashboard**: Goal tracking and productivity metrics
- **Self-Care Tracker**: Wellness monitoring and activities
- **Goal Setting**: SMART goal creation and management
- **Decision Friction**: Analysis of decision-making patterns
- **Productivity Center**: Task management and workflows

**Navigation:**
- **Voice**: "Show Weekly Dashboard", "Open Goal Setting"
- **Click**: Click on any radial menu item
- **Keyboard**: Use arrow keys to navigate, Enter to select

### Module Launcher
Central dashboard for accessing all system modules:

**Available Modules:**
- **Alden**: Productivity assistant and main interface
- **Core**: System orchestration and agent management
- **Synapse**: Plugin management and external integrations
- **Sentry**: Security monitoring and controls
- **Vault**: Memory management and data storage

**Access Methods:**
- **Voice**: "Open Core", "Show Synapse"
- **Click**: Click on module icons
- **Menu**: Use the main menu system

---

## Module Screens

### Alden Module

#### Weekly Dashboard
**Purpose**: Track goals, productivity, and decision-making patterns

**Features:**
- **Goal Progress**: Visual progress tracking for current goals
- **Decision Friction Analysis**: Identify and address decision blockers
- **Productivity Metrics**: Weekly performance indicators
- **Self-Care Tracking**: Wellness activity monitoring

**Navigation**: 
- Voice: "Show Weekly Dashboard"
- Radial Menu: Click "Weekly Dashboard"
- Direct: `/alden/weekly-dashboard`

#### Self-Care Tracker
**Purpose**: Monitor wellness activities and self-care practices

**Features:**
- **Activity Logging**: Track self-care activities
- **Mood Tracking**: Daily mood and energy levels
- **Wellness Goals**: Set and monitor wellness objectives
- **Progress Reports**: Weekly wellness summaries

**Navigation**:
- Voice: "Open Self-Care Tracker"
- Radial Menu: Click "Self-Care"
- Direct: `/alden/self-care`

#### Goal Setting Panel
**Purpose**: Create and manage SMART goals

**Features:**
- **Goal Creation**: SMART goal formulation wizard
- **Progress Tracking**: Visual progress indicators
- **Milestone Management**: Break down goals into milestones
- **Goal Review**: Regular goal assessment and adjustment

**Navigation**:
- Voice: "Show Goal Setting"
- Radial Menu: Click "Goals"
- Direct: `/alden/goals`

#### Decision Friction Panel
**Purpose**: Analyze and reduce decision-making friction

**Features:**
- **Friction Identification**: Spot decision blockers
- **Pattern Analysis**: Understand decision-making patterns
- **Solution Suggestions**: Automated recommendations
- **Progress Tracking**: Monitor friction reduction

**Navigation**:
- Voice: "Open Decision Friction"
- Radial Menu: Click "Decisions"
- Direct: `/alden/decisions`

#### Productivity Center
**Purpose**: Task management and workflow optimization

**Features:**
- **Task Management**: Create and organize tasks
- **Workflow Templates**: Predefined productivity workflows
- **Time Tracking**: Monitor time spent on activities
- **Performance Analytics**: Productivity insights

**Navigation**:
- Voice: "Show Productivity Center"
- Radial Menu: Click "Productivity"
- Direct: `/alden/productivity`

### Core Module

#### Command Center
**Purpose**: Central system control and agent management

**Features:**
- **Agent Status**: Monitor all active agents
- **System Health**: Real-time system monitoring
- **Quick Actions**: Common system operations
- **Performance Metrics**: System performance indicators

**Navigation**:
- Voice: "Open Command Center"
- Module Launcher: Click "Core"
- Direct: `/core/command-center`

#### Agent Orchestration
**Purpose**: Coordinate multiple agents for complex tasks

**Features:**
- **Agent Coordination**: Manage multi-agent workflows
- **Task Delegation**: Assign tasks to appropriate agents
- **Workflow Management**: Create and monitor agent workflows
- **Performance Tracking**: Agent collaboration metrics

**Navigation**:
- Voice: "Show Agent Orchestration"
- Core Menu: Click "Orchestration"
- Direct: `/core/orchestration`

#### Session Management
**Purpose**: Monitor and control active sessions

**Features:**
- **Active Sessions**: View all current sessions
- **Session Control**: Start, stop, or modify sessions
- **Resource Monitoring**: Track session resource usage
- **Session History**: Review past sessions

**Navigation**:
- Voice: "Open Session Management"
- Core Menu: Click "Sessions"
- Direct: `/core/sessions`

#### Logs/Diagnostics
**Purpose**: System health monitoring and troubleshooting

**Features:**
- **System Logs**: View system event logs
- **Error Tracking**: Monitor and analyze errors
- **Performance Metrics**: System performance data
- **Diagnostic Tools**: System troubleshooting utilities

**Navigation**:
- Voice: "Show Diagnostics"
- Core Menu: Click "Logs"
- Direct: `/core/diagnostics`

#### Secure Room Management
**Purpose**: Isolated environments for sensitive operations

**Features:**
- **Secure Rooms**: Create isolated workspaces
- **Access Control**: Manage room permissions
- **Data Isolation**: Secure data handling
- **Audit Logging**: Complete activity tracking

**Navigation**:
- Voice: "Open Secure Rooms"
- Core Menu: Click "Secure Rooms"
- Direct: `/core/secure-rooms`

#### Dev Mode Interface
**Purpose**: Developer tools and advanced configurations

**Features:**
- **Development Tools**: Advanced debugging and testing
- **Configuration Management**: System configuration options
- **API Testing**: Test system APIs and integrations
- **Performance Profiling**: Advanced performance analysis

**Navigation**:
- Voice: "Show Dev Mode"
- Core Menu: Click "Dev Mode"
- Direct: `/core/dev-mode`

### Synapse Module

#### Plugin Manager Dashboard
**Purpose**: Manage installed plugins and extensions

**Features:**
- **Installed Plugins**: View and manage current plugins
- **Plugin Status**: Monitor plugin health and performance
- **Update Management**: Update plugins and dependencies
- **Configuration**: Configure plugin settings

**Navigation**:
- Voice: "Open Plugin Manager"
- Module Launcher: Click "Synapse"
- Direct: `/synapse/plugins`

#### Plugin Install/Config Modal
**Purpose**: Install and configure new plugins

**Features:**
- **Plugin Discovery**: Browse available plugins
- **Installation Wizard**: Step-by-step plugin installation
- **Configuration Setup**: Initial plugin configuration
- **Dependency Management**: Handle plugin dependencies

**Navigation**:
- Voice: "Install Plugin"
- Plugin Manager: Click "Install New Plugin"
- Direct: `/synapse/install`

#### External Integrations
**Purpose**: Manage third-party service connections

**Features:**
- **Service Connections**: Manage external API connections
- **Authentication**: Handle service authentication
- **Data Sync**: Synchronize data with external services
- **Integration Health**: Monitor integration status

**Navigation**:
- Voice: "Show Integrations"
- Synapse Menu: Click "Integrations"
- Direct: `/synapse/integrations`

### Sentry Module

#### Security Dashboard
**Purpose**: Real-time security monitoring and alerts

**Features:**
- **Security Alerts**: Real-time security notifications
- **Threat Monitoring**: Monitor potential security threats
- **Access Logs**: Track system access and authentication
- **Security Metrics**: Security performance indicators

**Navigation**:
- Voice: "Open Security Dashboard"
- Module Launcher: Click "Sentry"
- Direct: `/sentry/dashboard`

#### Kill Switch Panel
**Purpose**: Emergency system shutdown and security controls

**Features:**
- **Emergency Shutdown**: Immediate system shutdown
- **Security Lockdown**: Lock down sensitive operations
- **Access Revocation**: Revoke compromised access
- **Recovery Procedures**: System recovery options

**Navigation**:
- Voice: "Show Kill Switch"
- Sentry Menu: Click "Kill Switch"
- Direct: `/sentry/kill-switch`

#### Audit Logs
**Purpose**: Comprehensive security event logging and analysis

**Features:**
- **Event Logging**: Complete system event records
- **Security Analysis**: Analyze security events
- **Compliance Reporting**: Generate compliance reports
- **Forensic Tools**: Security investigation utilities

**Navigation**:
- Voice: "Show Audit Logs"
- Sentry Menu: Click "Audit Logs"
- Direct: `/sentry/audit-logs`

### Vault Module

#### Main Dashboard
**Purpose**: Memory overview and data management

**Features:**
- **Memory Overview**: View all stored memories and data
- **Data Management**: Organize and manage stored information
- **Search Functionality**: Search through stored data
- **Memory Analytics**: Analyze memory usage patterns

**Navigation**:
- Voice: "Open Vault"
- Module Launcher: Click "Vault"
- Direct: `/vault/dashboard`

#### Memory Permissions Manager
**Purpose**: Access control and data privacy settings

**Features:**
- **Permission Management**: Control access to stored data
- **Privacy Settings**: Configure data privacy options
- **Access Logs**: Track data access and usage
- **Compliance Tools**: Ensure data compliance

**Navigation**:
- Voice: "Show Memory Permissions"
- Vault Menu: Click "Permissions"
- Direct: `/vault/permissions`

#### Diagnostics Toolset
**Purpose**: Memory system health and performance monitoring

**Features:**
- **System Health**: Monitor memory system performance
- **Performance Metrics**: Track memory system metrics
- **Troubleshooting Tools**: Diagnose memory system issues
- **Optimization Suggestions**: Improve memory system performance

**Navigation**:
- Voice: "Show Vault Diagnostics"
- Vault Menu: Click "Diagnostics"
- Direct: `/vault/diagnostics`

---

## Settings & Configuration

### Voice Settings
**Purpose**: Configure voice interaction and recognition

**Features:**
- **Voice Calibration**: Calibrate voice recognition
- **Language Settings**: Configure language preferences
- **Audio Settings**: Adjust audio input/output
- **Voice Commands**: Customize voice commands

**Navigation**:
- Voice: "Open Voice Settings"
- Settings Menu: Click "Voice"
- Direct: `/settings/voice`

### Security & Privacy Config
**Purpose**: Authentication, encryption, and privacy controls

**Features:**
- **Authentication**: Set up and manage authentication
- **Encryption Settings**: Configure data encryption
- **Privacy Controls**: Manage privacy settings
- **Security Policies**: Configure security policies

**Navigation**:
- Voice: "Show Security Settings"
- Settings Menu: Click "Security"
- Direct: `/settings/security`

### Accessibility Panel
**Purpose**: Accessibility features and accommodations

**Features:**
- **Screen Reader Support**: Configure screen reader settings
- **High Contrast Mode**: Enable high contrast display
- **Keyboard Navigation**: Configure keyboard shortcuts
- **Voice Feedback**: Set up voice feedback options

**Navigation**:
- Voice: "Open Accessibility"
- Settings Menu: Click "Accessibility"
- Direct: `/settings/accessibility`

---

## Help & Support

### Help Main Panel
**Purpose**: User guides and troubleshooting resources

**Features:**
- **User Guides**: Comprehensive user documentation
- **Video Tutorials**: Step-by-step video guides
- **FAQ**: Frequently asked questions
- **Contact Support**: Get help from support team

**Navigation**:
- Voice: "Show Help"
- Menu: Click "Help"
- Direct: `/help/main`

### Voice Interaction Guide
**Purpose**: Voice command reference and tutorials

**Features:**
- **Command Reference**: Complete voice command list
- **Tutorial Videos**: Voice interaction tutorials
- **Best Practices**: Voice interaction tips
- **Troubleshooting**: Voice-related issues

**Navigation**:
- Voice: "Show Voice Guide"
- Help Menu: Click "Voice Guide"
- Direct: `/help/voice`

### Accessibility Guide
**Purpose**: Accessibility features and usage instructions

**Features:**
- **Accessibility Features**: Overview of accessibility options
- **Setup Guides**: How to configure accessibility
- **Usage Instructions**: How to use accessibility features
- **Support Resources**: Accessibility support information

**Navigation**:
- Voice: "Show Accessibility Guide"
- Help Menu: Click "Accessibility Guide"
- Direct: `/help/accessibility`

---

## Troubleshooting

### Common Issues

#### Voice Recognition Problems
**Symptoms**: Voice commands not recognized or inaccurate recognition

**Solutions**:
1. **Recalibrate Voice**: Go to Voice Settings and recalibrate
2. **Check Microphone**: Ensure microphone is working and properly connected
3. **Reduce Background Noise**: Minimize background noise
4. **Speak Clearly**: Enunciate clearly and speak at normal volume
5. **Check Language Settings**: Ensure correct language is selected

#### Navigation Issues
**Symptoms**: Unable to access certain screens or modules

**Solutions**:
1. **Check Permissions**: Ensure you have access to the requested module
2. **Try Voice Commands**: Use voice commands as alternative navigation
3. **Restart Application**: Close and reopen the application
4. **Check Updates**: Ensure you have the latest version
5. **Contact Support**: If issue persists, contact support

#### Performance Issues
**Symptoms**: Slow response times or system lag

**Solutions**:
1. **Check System Resources**: Ensure adequate system resources
2. **Close Other Applications**: Close unnecessary applications
3. **Restart Application**: Restart the application
4. **Check for Updates**: Install any available updates
5. **Contact Support**: If issue persists, contact support

### Getting Help

#### Support Channels
- **In-App Help**: Use the Help menu for contextual assistance
- **Documentation**: Refer to this user manual and other documentation
- **Video Tutorials**: Watch step-by-step video guides
- **Community Forum**: Connect with other users
- **Support Team**: Contact the support team for direct assistance

#### Contact Information
- **Email**: support@hearthlink.local
- **Documentation**: `/docs/` directory
- **Voice Command**: "Contact Support"
- **Help Menu**: Use the Help menu in the application

---

## Keyboard Shortcuts

### General Navigation
- **Ctrl+N**: New session
- **F1**: Open user guide
- **Ctrl+Q**: Quit application
- **Ctrl+R**: Reload application
- **F11**: Toggle fullscreen

### Voice Interaction
- **Space**: Activate voice input
- **Esc**: Cancel voice input
- **Ctrl+Space**: Toggle voice HUD

### Accessibility
- **Tab**: Navigate through interface elements
- **Enter**: Activate selected element
- **Arrow Keys**: Navigate through options
- **Ctrl+U**: Toggle high contrast mode

---

## Voice Command Reference

### Navigation Commands
- "Hey Alden" - Activate main interface
- "Open [Module]" - Navigate to module
- "Show [Screen]" - Access specific screen
- "Go back" - Return to previous screen
- "Home" - Return to main interface

### Module-Specific Commands
- "Show Weekly Dashboard" - Open Alden's weekly dashboard
- "Open Goal Setting" - Access goal setting panel
- "Show Self-Care" - Open self-care tracker
- "Open Command Center" - Access Core command center
- "Show Security Dashboard" - Open Sentry security dashboard
- "Open Vault" - Access Vault memory management

### System Commands
- "Help" - Get contextual help
- "Settings" - Open settings
- "Quit" - Close application
- "Reload" - Reload application
- "Contact Support" - Get support assistance

### Accessibility Commands
- "Enable High Contrast" - Toggle high contrast mode
- "Screen Reader On" - Enable screen reader
- "Voice Feedback On" - Enable voice feedback
- "Keyboard Navigation" - Enable keyboard navigation mode

---

*For the most up-to-date information, refer to the in-app help system and documentation.* 