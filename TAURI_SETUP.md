# Tauri Native Windows Setup Guide

**Version:** 1.3.0 | **Last Updated:** August 9, 2025

This is the single source of truth documentation for building, developing, and deploying Hearthlink as a native Windows application using Tauri 2.0.

## Table of Contents

1. [Windows Quick Start](#windows-quick-start)
2. [Installer Build Process](#installer-build-process)
3. [Codespaces Section](#codespaces-section)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Verification Checklist](#verification-checklist)
6. [Advanced Configuration](#advanced-configuration)

---

## Windows Quick Start

### Prerequisites

Install these components in order:

1. **Python 3.11+** - [Download from python.org](https://python.org/downloads/)
   ```powershell
   python --version  # Should show 3.11 or higher
   ```

2. **Node.js 18+** - [Download from nodejs.org](https://nodejs.org/en/download/)
   ```powershell
   node --version  # Should show 18 or higher
   npm --version   # Should be included
   ```

3. **Rust** - Install via [rustup.rs](https://rustup.rs/)
   ```powershell
   # Run the rustup installer, then:
   rustc --version  # Verify installation
   cargo --version  # Package manager
   ```

4. **Tauri CLI** - Install globally
   ```powershell
   cargo install tauri-cli --version "^2.0"
   tauri --version  # Verify installation
   ```

### Installation Steps

1. **Clone and Install Dependencies**
   ```powershell
   # Install Node.js dependencies
   npm install
   
   # Create Python virtual environment
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/macOS
   
   # Install Python dependencies
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

2. **Verify Installation**
   ```powershell
   # Check Python environment
   python -c "import fastapi, uvicorn, pydantic, requests; print('✅ Python environment OK')"
   
   # Validate Tauri configuration
   npm run test:tauri-config
   ```

### Development Commands

**Primary Development Command:**
```powershell
npm run tauri:dev
# OR
npm run native
```

This command will:
- Build the React frontend on port 3005
- Start the Tauri native window
- Launch Python backend services automatically
- Enable hot reload for frontend changes

### Health Check URLs

When the application starts, verify these services are running:

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| **React Dev Server** | 3005 | http://localhost:3005 | Frontend development server |
| **Core API** | 8000 | http://127.0.0.1:8000/health | Core orchestration service |
| **Vault API** | 8001 | http://127.0.0.1:8001/health | Memory & secure storage |
| **Synapse API** | 8002 | http://127.0.0.1:8002/health | Plugin management |
| **Alden Backend** | 8888 | http://127.0.0.1:8888/health | AI assistant service |

**Quick Health Check Script:**
```powershell
# Create check-health.ps1
@('3005', '8000', '8001', '8002', '8888') | ForEach-Object {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$_/health" -TimeoutSec 2 -UseBasicParsing
        Write-Host "✅ Port $_`: OK ($($response.StatusCode))"
    } catch {
        Write-Host "❌ Port $_`: Failed"
    }
}
```

### Clean Exit Behavior

The Tauri application should:
- ✅ Close all child Python processes when window closes
- ✅ Release all ports (3005, 8000, 8001, 8002, 8888)
- ✅ Show graceful shutdown logs
- ✅ Leave no orphaned processes in Task Manager

**Verify Clean Exit:**
```powershell
# Before starting app
Get-Process | Where-Object {$_.Name -match "python|node|tauri"} | Select-Object Name, Id

# Start app, use it, then close
npm run tauri:dev

# After closing app - should show same or fewer processes
Get-Process | Where-Object {$_.Name -match "python|node|tauri"} | Select-Object Name, Id
```

---

## Installer Build Process

### Production Build Command

```powershell
# Complete build - both MSI and EXE installers
npm run tauri:build

# MSI only
npm run native:build:msi

# NSIS EXE only  
npm run native:build:exe

# Debug build (faster, larger)
npm run tauri:build:debug
```

### Build Process Steps

The build process automatically:

1. **Frontend Build** (`npm run build`)
   - Compiles React application to `/build` directory
   - Optimizes assets and bundles
   - Validates build output exists

2. **Rust Compilation**
   - Compiles Tauri backend to native binary
   - Links against system WebView2
   - Embeds application resources

3. **Installer Generation**
   - Creates MSI installer (Windows Installer format)
   - Creates NSIS EXE installer (self-extracting)
   - Signs installers if certificates configured

### Artifacts Path

After successful build, find installers at:

```
src-tauri/target/release/bundle/
├── msi/
│   └── Hearthlink Native_1.3.0_x64_en-US.msi
└── nsis/
    └── Hearthlink Native_1.3.0_x64-setup.exe
```

**Artifact Details:**
- **MSI Installer**: ~50-80MB, enterprise-friendly, supports unattended installation
- **NSIS EXE Installer**: ~50-80MB, user-friendly, supports custom branding
- Both include all Python dependencies and bundled resources

### Build Validation

```powershell
# Verify artifacts exist
Test-Path "src-tauri/target/release/bundle/msi/*.msi"
Test-Path "src-tauri/target/release/bundle/nsis/*.exe"

# Check installer sizes
Get-ChildItem "src-tauri/target/release/bundle" -Recurse -Include "*.msi","*.exe" | 
  Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

---

## Codespaces Section

### API-Only Smoke Testing

Codespaces cannot run GUI applications, but you can test backend services:

```bash
# Install dependencies
npm install
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start backend services only
python src/main.py &          # Core API on 8000
python src/vault/vault.py &   # Vault API on 8001  
python src/synapse/api.py &   # Synapse API on 8002
python src/personas/alden.py & # Alden on 8888

# Test endpoints
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8002/health
curl http://127.0.0.1:8888/health
```

### Limitations

**What Works in Codespaces:**
- ✅ Python backend services
- ✅ API endpoint testing
- ✅ Database operations
- ✅ Configuration validation
- ✅ Unit tests

**What Doesn't Work:**
- ❌ Tauri native window (requires GUI)
- ❌ React development server preview
- ❌ Desktop integration features
- ❌ System tray functionality
- ❌ Full end-to-end testing

### Codespaces Commands

```bash
# Basic validation
npm run python:verify
npm run test:tauri-config

# API testing
python -m pytest tests/api/
npm run test -- --testPathPattern=api

# Build validation (no GUI)
npm run build  # React only, skip Tauri
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. `cargo: command not found`

**Symptom:** Tauri CLI installation fails
```
'cargo' is not recognized as an internal or external command
```

**Solution:** Install Rust toolchain
```powershell
# Download and run rustup-init.exe from https://rustup.rs/
# OR via Chocolatey:
choco install rust

# Restart terminal, then verify:
cargo --version
```

#### 2. Missing script: `tauri:dev`

**Symptom:** npm script not found
```
npm ERR! missing script: tauri:dev
```

**Solution:** Update package.json scripts
```powershell
# Check current scripts
npm run

# If tauri:dev missing, add to package.json:
"tauri:dev": "tauri dev",
"native": "tauri dev",
"tauri:build": "tauri build"
```

#### 3. Tauri v1/v2 Schema Errors

**Symptom:** Configuration validation errors
```
Error: Invalid configuration file
```

**Solution:** Tauri v2 configuration key mappings

| Tauri v1 | Tauri v2 | Purpose |
|----------|----------|---------|
| `tauri.bundle.identifier` | `bundle.identifier` | App identifier |
| `tauri.allowlist` | `app.security` | Permission model |
| `build.distDir` | `build.frontendDist` | Build output |
| `build.devPath` | `build.devUrl` | Dev server URL |

**Fix Script:**
```powershell
# Backup current config
Copy-Item "src-tauri/tauri.conf.json" "src-tauri/tauri.conf.json.backup"

# Validate against Tauri v2 schema
tauri info  # Shows configuration issues
```

#### 4. Port Conflicts

**Symptom:** Services fail to start
```
Error: Address already in use (os error 10048)
```

**Solution:** Change ports while keeping 127.0.0.1

```powershell
# Check port usage
netstat -ano | findstr ":8000 :8001 :8002 :8888"

# Kill conflicting processes
taskkill /PID <process_id> /F

# Alternative: Change ports in configuration
# Edit config files to use 8010, 8011, 8012, 8898 etc.
```

**Configuration Files to Update:**
- `config/core_config.json` - Core API port
- `config/vault_config.json` - Vault API port  
- `config/alden_config.json` - Alden backend port
- `src-tauri/tauri.conf.json` - Frontend dev server port

#### 5. Orphaned Processes

**Symptom:** Processes remain after app closes
```
Multiple python.exe processes still running
```

**Solution:** Enhanced shutdown sequence
```powershell
# Manual cleanup
Get-Process python | Where-Object {$_.MainWindowTitle -match "Hearthlink"} | Stop-Process -Force

# Prevention: Add to src-tauri/src/main.rs
use tauri::Manager;

#[tauri::command]
async fn cleanup_processes() {
    // Graceful shutdown logic
    std::process::Command::new("taskkill")
        .args(&["/F", "/IM", "python.exe", "/FI", "WINDOWTITLE eq Hearthlink*"])
        .output()
        .expect("Failed to cleanup processes");
}
```

#### 6. Build Failures

**Symptom:** tauri build fails with errors

**Common Causes & Solutions:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Icon file not found` | Missing icon files | Ensure all icons in `src-tauri/icons/` |
| `WebView2 not found` | Missing WebView2 runtime | Install from Microsoft |
| `Resource bundling failed` | Large Python dependencies | Check `tauri.conf.json` resource paths |
| `Linker errors` | Missing Visual Studio tools | Install "C++ build tools" |

**Build Environment Verification:**
```powershell
# Pre-build checklist
Write-Host "=== Build Environment Check ==="
Write-Host "Node: $(node --version)"
Write-Host "Python: $(python --version)" 
Write-Host "Rust: $(rustc --version)"
Write-Host "Tauri: $(tauri --version)"

# Check required files
$requiredFiles = @(
    "package.json",
    "src-tauri/tauri.conf.json", 
    "src-tauri/Cargo.toml",
    "src-tauri/src/main.rs",
    "requirements.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file"
    } else {
        Write-Host "❌ $file (missing)"
    }
}
```

---

## Verification Checklist

Use this checklist to verify your Hearthlink Tauri setup:

### Development Environment

- [ ] **App opens via `npm run tauri:dev`**
  - ✅ Native window appears within 30 seconds
  - ⚠️ Window appears but with errors (check console)
  - ❌ Command fails or window doesn't appear

- [ ] **Health endpoints return 200 on all ports**
  - ✅ All 5 services (3005, 8000, 8001, 8002, 8888) respond
  - ⚠️ 3-4 services respond (partial functionality)
  - ❌ 0-2 services respond (major issues)

- [ ] **Closing app terminates child processes**
  - ✅ All python.exe processes end within 10 seconds
  - ⚠️ Some processes linger but terminate within 60 seconds
  - ❌ Processes remain indefinitely

### Production Build

- [ ] **Actions workflow produces installer artifacts**
  - ✅ Both MSI and EXE installers generated successfully
  - ⚠️ One installer type generated, other failed
  - ❌ No installer artifacts produced

- [ ] **Install/uninstall works cleanly**
  - ✅ Silent install, runs correctly, clean uninstall
  - ⚠️ Installs and runs, but leaves some residual files
  - ❌ Installation fails or app doesn't start

### Functional Testing

**Quick Test Script:**
```powershell
# Save as test-hearthlink.ps1
Write-Host "🧪 Hearthlink Tauri Verification Test"
Write-Host "===================================="

# 1. Development startup test
Write-Host "1. Testing development startup..."
$job = Start-Job -ScriptBlock { npm run tauri:dev }
Start-Sleep 30

$processes = Get-Process | Where-Object {$_.Name -match "tauri|python"}
if ($processes.Count -gt 0) {
    Write-Host "✅ App started ($($processes.Count) processes)"
    $processes | Stop-Process -Force
} else {
    Write-Host "❌ App failed to start"
}

# 2. Health check test
Write-Host "2. Testing health endpoints..."
$ports = @(8000, 8001, 8002, 8888)
$healthyPorts = 0

foreach ($port in $ports) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/health" -TimeoutSec 5 -UseBasicParsing
        Write-Host "✅ Port $port`: Health OK"
        $healthyPorts++
    } catch {
        Write-Host "❌ Port $port`: Health Failed"
    }
}

Write-Host "Health Score: $healthyPorts / $($ports.Count)"

# 3. Build test
Write-Host "3. Testing production build..."
try {
    npm run build
    if (Test-Path "build") {
        Write-Host "✅ Frontend build successful"
    } else {
        Write-Host "❌ Frontend build failed"
    }
} catch {
    Write-Host "❌ Build command failed"
}

Write-Host "===================================="
Write-Host "Verification complete. Check results above."
```

### GitHub Actions Integration

The repository includes automated Windows building via `.github/workflows/tauri-build-windows.yml`.

**Latest Build Status:** [Check Actions Tab](https://github.com/mythologiq/hearthlink/actions)

**Successful Build Artifacts:**
- `Hearthlink-1.3.0-{release-type}-{timestamp}-x86_64-pc-windows-msvc.msi`
- `Hearthlink-1.3.0-{release-type}-{timestamp}-x86_64-pc-windows-msvc.exe`
- `build-info.json` (metadata)

**Trigger Manual Build:**
1. Go to Actions → "Windows Native Build - Tauri"
2. Click "Run workflow"
3. Select release type (development/alpha/release)
4. Choose build target (MSI/NSIS/both)
5. Monitor progress and download artifacts

---

## Advanced Configuration

### Performance Tuning

**Optimize Build Times:**
```toml
# Add to src-tauri/Cargo.toml
[profile.dev]
opt-level = 1      # Faster dev builds
debug = true
split-debuginfo = "unpacked"

[profile.release]
opt-level = "s"    # Optimize for size
lto = true         # Link-time optimization
codegen-units = 1  # Better optimization
```

**Reduce Installer Size:**
```json
// In src-tauri/tauri.conf.json
{
  "bundle": {
    "resources": [
      // Only include essential Python files
      "../src/core/*.py",
      "../src/vault/*.py", 
      "../src/personas/alden.py",
      "../requirements.txt"
      // Remove: "../src/**/*.py" (too broad)
    ]
  }
}
```

### Security Configuration

**Code Signing (Optional):**
```powershell
# Generate self-signed certificate for testing
New-SelfSignedCertificate -Type CodeSigning -Subject "CN=Hearthlink Dev" -CertStoreLocation Cert:\CurrentUser\My

# Add to tauri.conf.json:
"windows": {
  "certificateThumbprint": "YOUR_CERT_THUMBPRINT",
  "timestampUrl": "http://timestamp.comodoca.com/authenticode"
}
```

**Content Security Policy:**
```json
// Restrict network access in tauri.conf.json
"app": {
  "security": {
    "csp": "default-src 'self'; connect-src 'self' http://127.0.0.1:*"
  }
}
```

### Custom Window Configuration

```json
// Enhanced window settings
"app": {
  "windows": [{
    "title": "Hearthlink - AI Orchestration System",
    "width": 1400,
    "height": 900,
    "minWidth": 1000,
    "minHeight": 700,
    "decorations": true,
    "transparent": false,
    "alwaysOnTop": false,
    "center": true,
    "resizable": true
  }]
}
```

---

## Support and Resources

### Documentation Links
- [Tauri v2 Documentation](https://v2.tauri.app/)
- [Tauri Configuration Reference](https://v2.tauri.app/reference/config/)
- [Rust Installation Guide](https://www.rust-lang.org/tools/install)

### Project-Specific Files
- `src-tauri/tauri.conf.json` - Main Tauri configuration
- `package.json` - Node.js scripts and dependencies
- `requirements.txt` - Python dependencies
- `.github/workflows/tauri-build-windows.yml` - CI/CD pipeline

### Reporting Issues
1. Check this troubleshooting guide first
2. Verify your environment meets prerequisites  
3. Test with a clean clone of the repository
4. Include output of `tauri info` in issue reports
5. Provide specific error messages and steps to reproduce

---

**Last Updated:** August 9, 2025
**Tauri Version:** 2.0+
**Node.js Version:** 18+
**Python Version:** 3.11+

This document is maintained as the definitive guide for Hearthlink Tauri development. For updates or corrections, edit this file directly in the repository.