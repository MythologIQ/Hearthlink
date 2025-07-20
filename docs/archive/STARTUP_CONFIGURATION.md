# 🚀 Startup Configuration Guide

Complete guide for configuring Hearthlink's startup behavior and Claude Code CLI integration.

---

## 🎯 **Overview**

Hearthlink supports advanced startup configuration including:
- **Auto-launch at system startup** (Windows, macOS, Linux)
- **Silent Claude Code CLI background support**
- **System tray integration** with immediate availability
- **Synapse forwarding mechanism** for seamless AI interaction

---

## ⚙️ **Startup Features**

### ✅ Auto-Launch Configuration
- **Cross-platform support** for Windows, macOS, and Linux
- **Registry/Launch Agent management** handled automatically
- **Silent background startup** with system tray presence
- **Configurable through UI** or Tauri commands

### ✅ Claude Code CLI Integration
- **Background process launching** for Synapse support
- **Environment variable configuration** for Hearthlink mode
- **Silent operation** without user interaction
- **Automatic failure handling** and logging

---

## 🛠️ **Implementation Details**

### Windows Implementation
```rust
// Registry path: HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
// Key: "Hearthlink"
// Value: "C:\Path\To\Hearthlink.exe"

use winreg::enums::*;
use winreg::RegKey;

let hkcu = RegKey::predef(HKEY_CURRENT_USER);
let path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run";
let (key, _) = hkcu.create_subkey(&path)?;
key.set_value("Hearthlink", &exe_path.to_string_lossy())?;
```

### macOS Implementation
```xml
<!-- Launch Agent: ~/Library/LaunchAgents/com.hearthlink.app.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hearthlink.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Hearthlink.app/Contents/MacOS/hearthlink</string>
        <string>--startup</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

### Linux Implementation
```desktop
# Autostart file: ~/.config/autostart/hearthlink.desktop
[Desktop Entry]
Type=Application
Name=Hearthlink
Comment=AI Orchestration System
Exec=/usr/local/bin/hearthlink --startup
Icon=hearthlink
Terminal=false
X-GNOME-Autostart-enabled=true
```

---

## 🎮 **User Interface**

### Startup Settings Component
The `StartupSettings.tsx` component provides:

```typescript
interface StartupSettingsProps {
  className?: string;
}

// Features:
- Auto-launch toggle switch
- Claude Code CLI launch button
- Real-time status indicators
- Error handling and notifications
- Cross-platform compatibility checks
```

### Available Controls
- **✅ Enable/Disable Startup Launch**
- **🤖 Start Claude Code CLI Support**
- **📊 Real-time Status Display**
- **🔔 Notification Feedback**

---

## 🔧 **Tauri Commands**

### Startup Management
```rust
#[tauri::command]
fn enable_startup_launch() -> Result<String, String>

#[tauri::command] 
fn disable_startup_launch() -> Result<String, String>

#[tauri::command]
fn check_startup_enabled() -> Result<bool, String>
```

### Claude Code Integration
```rust
#[tauri::command]
fn launch_claude_code_silent() -> Result<String, String>
```

### Usage from Frontend
```typescript
import { invoke } from '@tauri-apps/api/tauri';

// Enable startup
const result = await invoke<string>('enable_startup_launch');

// Launch Claude Code
const status = await invoke<string>('launch_claude_code_silent');

// Check startup status
const enabled = await invoke<boolean>('check_startup_enabled');
```

---

## 🔄 **Startup Flow**

### 1. System Boot Sequence
```
System Boot → OS Startup Manager → Hearthlink Launch → Background Mode
```

### 2. Hearthlink Initialization
```rust
// Check for --startup flag
let args: Vec<String> = std::env::args().collect();
if args.contains(&"--startup".to_string()) {
    // Launch in background mode
    // Start system tray
    // Launch Claude Code CLI silently
}
```

### 3. Claude Code CLI Launch
```bash
# Environment variables set automatically
export CLAUDE_SYNAPSE_MODE=true
export CLAUDE_HEARTHLINK_SUPPORT=true

# Command executed
claude --background --silent
```

---

## 📋 **Configuration Options**

### Environment Variables
```bash
# Claude Code integration
CLAUDE_SYNAPSE_MODE=true
CLAUDE_HEARTHLINK_SUPPORT=true

# Debug mode
TAURI_DEBUG=true
HEARTHLINK_STARTUP_DEBUG=true
```

### Command Line Arguments
```bash
# Launch in startup mode
hearthlink --startup

# Launch with debug
hearthlink --startup --debug

# Launch with specific Claude Code path
hearthlink --startup --claude-path="/custom/path/claude"
```

---

## 🛡️ **Security Considerations**

### Permission Requirements
- **Windows**: Current user registry access
- **macOS**: User Launch Agents directory write access
- **Linux**: User autostart directory write access

### Safe Path Handling
```rust
// Ensure executable path is valid
let exe_path = std::env::current_exe()?;

// Validate path before writing to system
if !exe_path.exists() {
    return Err("Invalid executable path".to_string());
}
```

### Claude Code Validation
```rust
// Verify Claude Code is available before launching
let output = std::process::Command::new("claude")
    .arg("--version")
    .output()?;

if !output.status.success() {
    return Err("Claude Code CLI not available".to_string());
}
```

---

## 🔍 **Troubleshooting**

### Common Issues

#### 1. Startup Not Working
```bash
# Check if entry exists
# Windows: Check registry key
# macOS: ls ~/Library/LaunchAgents/com.hearthlink.app.plist
# Linux: ls ~/.config/autostart/hearthlink.desktop

# Verify executable path
which hearthlink
```

#### 2. Claude Code Not Launching
```bash
# Verify Claude Code installation
claude --version

# Check PATH
echo $PATH | grep claude

# Manual test
claude --background --silent
```

#### 3. Permission Errors
```bash
# Windows: Run as administrator for initial setup
# macOS: Check Accessibility permissions
# Linux: Verify user has write access to ~/.config
```

### Debug Mode
```bash
# Enable detailed logging
HEARTHLINK_STARTUP_DEBUG=true hearthlink --startup

# Check system logs
# Windows: Event Viewer
# macOS: Console.app
# Linux: journalctl --user
```

---

## 📊 **Status Monitoring**

### Real-time Status
The startup system provides real-time monitoring:

```typescript
interface StartupStatus {
  isStartupEnabled: boolean;
  isClaudeCodeRunning: boolean;
  lastStartupTime?: Date;
  claudeCodePid?: number;
}
```

### Health Checks
```rust
// Periodic validation
- Check if startup entry still exists
- Verify Claude Code process is running
- Monitor system tray availability
- Test Synapse forwarding connection
```

---

## 🎯 **Best Practices**

### 1. Graceful Degradation
- System continues to work if Claude Code is unavailable
- Startup configuration is optional
- Clear error messages for troubleshooting

### 2. User Control
- Easy enable/disable through UI
- Clear status indicators
- Informative help text

### 3. System Integration
- Follows OS conventions for startup applications
- Respects user privacy and system resources
- Minimal performance impact

---

## 🔮 **Future Enhancements**

### Planned Features
- **Auto-update integration** with startup management
- **Advanced Claude Code configuration** options
- **Startup delay settings** for system load management
- **Multi-user support** for shared systems

### Configuration Profiles
```yaml
startup_profiles:
  minimal:
    auto_launch: true
    claude_code: false
    system_tray: true
  
  full_support:
    auto_launch: true
    claude_code: true
    synapse_forwarding: true
    startup_delay: 10s
```

---

**🎉 Result: Professional startup experience with seamless Claude Code integration and cross-platform system management.**