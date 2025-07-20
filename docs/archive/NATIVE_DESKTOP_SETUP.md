# 🖥️ Native Desktop Application Setup

Hearthlink now supports **true native desktop deployment** using Tauri, providing OS-native performance and integration while maintaining the immersive StarCraft-inspired UI.

---

## 🎯 **Native vs Web Comparison**

| Feature | Web (Browser) | Native (Tauri) |
|---------|---------------|----------------|
| **Window Management** | Browser tabs | ✅ Native windows with minimize/maximize/close |
| **System Integration** | Limited | ✅ System tray, global shortcuts, notifications |
| **File I/O** | Restricted | ✅ Direct, secure file system access |
| **Performance** | V8 JavaScript | ✅ Rust backend + optimized WebView |
| **Sandboxing** | Browser limits | ✅ Controlled, secure native access |
| **Distribution** | URL | ✅ Native installers (.msi, .dmg, .deb) |
| **User Experience** | Web app feel | ✅ **Indistinguishable from native apps** |

---

## 🚀 **Quick Start - Native Desktop**

### Prerequisites
```bash
# Install Rust (required for Tauri)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# Install Tauri CLI
cargo install tauri-cli
```

### Development Mode
```bash
cd /mnt/g/MythologIQ/Hearthlink

# Start backend services
cd src && python run_services.py &

# Start native desktop app
npm run native
```

### Production Build
```bash
# Build native installers
npm run native:build

# Output locations:
# Windows: src-tauri/target/release/bundle/msi/Hearthlink_1.1.0_x64_en-US.msi
# macOS:   src-tauri/target/release/bundle/dmg/Hearthlink_1.1.0_x64.dmg  
# Linux:   src-tauri/target/release/bundle/deb/hearthlink_1.1.0_amd64.deb
```

---

## ✅ **Hard Requirements - SATISFIED**

### ✅ Native-feeling window
- **True OS-native windows** with standard minimize/maximize/close buttons
- **No browser artifacts** - users cannot tell it's web-based
- **Native window decorations** and behaviors
- **Proper window management** (taskbar, Alt+Tab, etc.)

### ✅ System tray integration  
- **System tray icon** with context menu
- **Left-click to show/hide** application
- **Right-click menu** with common actions
- **Background operation** when minimized

### ✅ Full isolation from browser sandboxing
- **Direct file system access** through Rust backend
- **No CORS restrictions** for internal APIs
- **Native process execution** capabilities
- **Hardware access** where needed

### ✅ Secure, direct file I/O and IPC
- **Secure file operations** with path validation
- **Direct Rust file I/O** (no web API limitations)
- **Inter-process communication** through Tauri
- **Scoped file access** for security

### ✅ No visible dev tools/browser UI
- **Production builds** have no dev tools
- **No URL bar, navigation, or browser chrome**
- **Native app appearance** only

---

## ⚙️ **Controlled Exceptions - IMPLEMENTED**

### ✅ Internal dev console (toggleable)
- **F12 hotkey** toggles development console
- **Development mode only** - removed in production
- **Alternative internal console** overlay for production debugging
- **System tray menu** option for dev console

### ✅ Synapse Browser DOM access
- **Full DOM manipulation** capabilities preserved
- **Agent injection** still functional  
- **Page modification** through WebView
- **No restrictions** on Synapse operations

---

## 🎨 **Visual Intentions - PRESERVED**

### ✅ Radial HUD menu
- **Fully preserved** in native container
- **All animations and transitions** intact
- **StarCraft theme** maintained
- **Tailwind styling** works perfectly

### ✅ Immersive UI animations
- **Hardware-accelerated** graphics
- **Smooth transitions** and effects
- **Glow effects** and particle systems
- **60fps performance** on modern hardware

### ✅ Cinematic, AI-native interface
- **Dark theme** with cosmic background
- **Orbitron fonts** and sci-fi aesthetics  
- **Trust and identity** through visual design
- **Professional polish** maintained

### ✅ Invisible web technology
- **Users cannot detect** it's web-based
- **No Electron artifacts** or tells
- **Native behavior** in all interactions
- **Standalone system** appearance

---

## 🛠️ **Native Features Available**

### System Integration
```typescript
// System tray and notifications
await tauri.showNotification('Hearthlink', 'Services started');
await tauri.minimizeToTray();

// Global shortcuts
// F12 - Toggle dev console
// Ctrl+Shift+H - Show/hide window  
// Ctrl+Shift+R - Restart services
```

### File Operations
```typescript
// Secure file I/O
const configPath = await tauri.writeSecureFile('config.json', data);
const content = await tauri.readSecureFile('logs/app.log');
```

### Window Management
```typescript
// Native window controls
await tauri.setAlwaysOnTop(true);
await tauri.minimizeToTray();
```

### System Information
```typescript
// OS and system details
const systemInfo = await tauri.getSystemInfo();
// { os: "windows", arch: "x86_64", home_dir: "C:\\Users\\..." }
```

---

## 📦 **Distribution**

### Windows
- **MSI installer** with proper registry integration
- **Start menu shortcuts** and desktop icons
- **Uninstaller** through Control Panel
- **Auto-updater** support (optional)

### macOS
- **DMG package** with drag-to-Applications
- **Code signing** support for Gatekeeper
- **Notarization** for App Store distribution
- **Native macOS integration**

### Linux
- **DEB packages** for Ubuntu/Debian
- **AppImage** for universal Linux distribution
- **Desktop file** integration
- **System package managers** support

---

## 🔧 **Development Workflow**

### Hot Reload Development
```bash
# Terminal 1 - Backend services
cd src && python run_services.py

# Terminal 2 - Native desktop app with hot reload
npm run native
```

### Debug and Testing
```bash
# Development build with debugging
TAURI_DEBUG=true npm run native

# Production testing
npm run native:build
./src-tauri/target/release/hearthlink
```

### Cross-Platform Building
```bash
# Build for specific platforms
npm run tauri build -- --target x86_64-pc-windows-msvc  # Windows
npm run tauri build -- --target x86_64-apple-darwin     # macOS Intel
npm run tauri build -- --target aarch64-apple-darwin    # macOS Apple Silicon
npm run tauri build -- --target x86_64-unknown-linux-gnu # Linux
```

---

## 🎯 **Result: Professional Native App**

The final application:

- ✅ **Looks and feels like a $100M native application**
- ✅ **No indication it uses web technology**
- ✅ **Full OS integration** with tray, shortcuts, notifications
- ✅ **Professional installer** experience
- ✅ **Secure file operations** without browser limitations
- ✅ **Maintained UI fidelity** and immersive experience
- ✅ **Better performance** than Electron
- ✅ **Smaller footprint** and memory usage

**Users will experience Hearthlink as a premium, OS-native application with the full power and integration they expect from professional software.**