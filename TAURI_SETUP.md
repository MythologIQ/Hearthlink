# Hearthlink Tauri Native Setup Guide

This guide covers the complete setup and build process for Hearthlink's Tauri-based native desktop application with multi-process Python service orchestration.

## Prerequisites

### System Requirements
- **Windows 10/11** (primary target)
- **Python 3.11+** installed and in PATH
- **Node.js 18+** and npm
- **Rust** (latest stable)
- **Visual Studio Build Tools** (Windows)

### Quick Environment Check
```bash
# Verify Python
python --version  # or python3 --version
python -m pip --version

# Verify Node.js
node --version
npm --version

# Verify Rust
cargo --version
rustc --version
```

## Installation

### 1. Install Dependencies
```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
node scripts/setup_python_requirements.js
# OR manually:
pip install -r requirements_full.txt

# Install Tauri CLI (if not already installed)
cargo install tauri-cli
```

### 2. Install Rust Dependencies
```bash
cd src-tauri
cargo build
```

## Development

### Development Mode (Recommended)
```bash
# Start development server with hot reload
npm run tauri:dev

# Alternative command
npm run native
```

This will:
1. Start React development server on port 3005
2. Launch Tauri development window
3. Automatically start all Python services:
   - **Alden** (AI Assistant) on port 8888
   - **Vault** (Memory Storage) on port 8001  
   - **Core** (Orchestration) on port 8000
   - **Synapse** (Plugin Management) on port 8002

### Service Health Monitoring

The application includes built-in health monitoring accessible via:
- **Frontend**: Service status panel in the UI
- **Backend**: Tauri commands for service management
- **API**: Health check endpoints on each service

```javascript
// Get system health status
const health = await invoke('get_system_health');
console.log(health);

// Restart a specific service  
await invoke('restart_service', { serviceName: 'alden' });
```

## Production Build

### Build Native Executable

```bash
# Build optimized production version
npm run tauri:build

# Build specific Windows formats
npm run native:build:msi     # MSI installer
npm run native:build:exe     # NSIS installer
```

### Build Output
The build process creates:
- **MSI Installer**: `src-tauri/target/release/bundle/msi/Hearthlink_1.3.0_x64_en-US.msi`
- **NSIS Installer**: `src-tauri/target/release/bundle/nsis/Hearthlink_1.3.0_x64-setup.exe`
- **Portable Executable**: `src-tauri/target/release/Hearthlink.exe`

## Architecture Overview

### Process Management
The Tauri application acts as a process orchestrator:

```rust
// Services started automatically on app launch
services = [
    ("alden", "src/api/alden_api.py", 8888),
    ("vault", "src/vault/vault.py", 8001), 
    ("core", "src/api/core_api.py", 8000),
    ("synapse", "src/api/synapse_api_server.py", 8002),
]
```

### Service Discovery & Health Checks
- **Automatic Discovery**: Services register on localhost with predefined ports
- **Health Monitoring**: 30-second interval health checks via HTTP endpoints
- **Error Recovery**: Automatic restart on service failure
- **Graceful Shutdown**: All processes terminated on app exit

### Resource Bundling
Python source code and dependencies are bundled as Tauri resources:

```json
"resources": [
    "../src/**/*.py",
    "../config/**/*.json", 
    "../hearthlink_data/**/*",
    "../requirements_full.txt"
]
```

## Configuration

### Environment Variables
Set these for proper operation:

```bash
# Vault encryption key (auto-generated if not set)
HEARTHLINK_VAULT_KEY=yFLl9T3j6l_rsrgSIHMDqr5O_vt62MdpkJuhIEuilAM=

# Data directory (auto-configured)
HEARTHLINK_DATA_DIR=./hearthlink_data
```

### Service Ports
Default port assignments (configurable):
- **Frontend**: 3005 (development), bundled (production)
- **Alden API**: 8888
- **Vault API**: 8001
- **Core API**: 8000  
- **Synapse API**: 8002

### Tauri Configuration
Key settings in `src-tauri/tauri.conf.json`:

```json
{
  "build": {
    "devUrl": "http://localhost:3005",
    "frontendDist": "../build"
  },
  "bundle": {
    "resources": ["../src/**/*.py", "..."],
    "externalBin": ["python3", "python"]
  }
}
```

## Troubleshooting

### Common Issues

#### Python Not Found
```
Error: Python 3.x not found
```
**Solution**: Install Python 3.11+ and ensure it's in PATH
```bash
python --version  # Should show 3.11+
```

#### Service Start Failures
```
Error: Failed to start alden service
```
**Solution**: Check dependencies and port availability
```bash
# Check if ports are in use
netstat -an | findstr "8888\|8001\|8000\|8002"

# Install missing Python packages
pip install -r requirements_full.txt
```

#### Build Errors
```
Error: failed to bundle project
```
**Solution**: Ensure Rust toolchain is up to date
```bash
rustup update
cargo clean
cd src-tauri && cargo build
```

#### Permission Issues (Windows)
```
Error: Access denied when starting services
```
**Solution**: Run as administrator or check Windows Defender exclusions

### Debug Mode

For detailed debugging:

```bash
# Build in debug mode (more verbose output)
npm run tauri:build:debug

# Check service logs
# (Logs available in UI or via API)
```

### Log Files
Application logs are stored in:
- **Windows**: `%LOCALAPPDATA%\\Hearthlink\\logs\\`
- **Service Logs**: Available via `get_service_logs` API call
- **Tauri Logs**: Console output in development mode

## API Integration

### Tauri Commands
Available for frontend integration:

```javascript
import { invoke } from '@tauri-apps/api/tauri';

// System health
const health = await invoke('get_system_health');

// Service management  
await invoke('restart_service', { serviceName: 'alden' });

// Service logs
const logs = await invoke('get_service_logs', { serviceName: 'vault' });

// Vault operations
await invoke('rotate_vault_keys');
const status = await invoke('get_vault_key_status');
```

### Python Service APIs
Each service exposes RESTful APIs:

```bash
# Health checks
GET http://127.0.0.1:8888/health  # Alden
GET http://127.0.0.1:8001/health  # Vault  
GET http://127.0.0.1:8000/health  # Core
GET http://127.0.0.1:8002/health  # Synapse

# Service-specific endpoints
POST http://127.0.0.1:8888/chat   # Alden chat
GET http://127.0.0.1:8001/memory  # Vault memory
POST http://127.0.0.1:8000/session # Core session
GET http://127.0.0.1:8002/plugins  # Synapse plugins
```

## Security Considerations

### Process Isolation
- Each Python service runs in its own process
- Services bind only to 127.0.0.1 (localhost)
- No external network access by default

### Data Encryption
- Vault uses AES-256-GCM encryption
- Keys stored securely in Windows Credential Manager
- Memory cleared on process termination

### Sandboxing
- Tauri security model limits frontend access
- Python services run with limited permissions
- File system access restricted to app directories

## Performance Optimization

### Resource Usage
- **Memory**: ~200-400MB total (all services)
- **CPU**: Low idle usage, scales with AI operations  
- **Disk**: <100MB installation size
- **Network**: Localhost only, minimal bandwidth

### Startup Optimization
- Services start in parallel
- Health checks begin after 5-second grace period
- UI remains responsive during service startup

## Contributing

### Development Workflow
1. Make changes to Python services in `src/`
2. Test with `npm run tauri:dev`
3. Update Rust code in `src-tauri/src/` if needed
4. Build and test: `npm run tauri:build:debug`
5. Create production build: `npm run tauri:build`

### Adding New Services
1. Create Python service in `src/api/`
2. Add service configuration to `main.rs`
3. Update health check endpoints
4. Test integration with existing services

## Deployment

### Single-Click Distribution
The built MSI/EXE files are completely self-contained:
- No external Python installation required
- All dependencies bundled
- Automatic service orchestration
- Clean uninstall process

### System Integration
- Desktop shortcuts created automatically  
- Windows Start Menu integration
- File association support (optional)
- Auto-start options available

---

## Quick Start Summary

```bash
# Complete setup and build
git clone <repo>
cd hearthlink
npm install
node scripts/setup_python_requirements.js
npm run tauri:build

# The resulting MSI/EXE in src-tauri/target/release/bundle/ 
# is ready for distribution!
```

For advanced configuration and deployment options, see the individual service documentation in `docs/`.