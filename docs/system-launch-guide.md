# Hearthlink System Launch Guide

**Updated**: July 22, 2025 - Post-Migration Launch Procedures  
**Version**: 1.3.0 Native Migration  

## Quick Start Commands

### Native Application (Recommended)
```bash
# Full native launch with all services
npm run native:full

# Or step-by-step:
python service_orchestrator.py &  # Backend services
npm run start:react &            # React dev server
npm run native                   # Native Tauri app
```

### Legacy Electron (Fallback)
```bash
npm run dev    # Traditional Electron launch
```

## Launch Sequence Overview

### 1. Backend Services (Required First)
**Command**: `python service_orchestrator.py`
**Ports**: 8000, 8001, 8005, 3001
**Status Check**: `curl http://localhost:8000/health`

Services Started:
- **Alden Backend** (8000) - Primary AI assistant
- **Core Orchestrator** (8001) - Multi-agent coordination  
- **MCP Direct API** (8005) - Plugin execution
- **Static Server** (3001) - Asset serving

### 2. Frontend Application
**Native**: `npm run native` (launches Tauri wrapper)
**Legacy**: `npm run dev` (launches Electron)

### 3. System Verification
- Open native app or navigate to `http://localhost:3005`
- Verify all status indicators are green
- Test voice activation: "Hello Alden"
- Confirm MCP operations: Create test file

## Detailed Launch Procedures

### Method 1: Native Application Launch (Primary)

#### Prerequisites
```bash
# Ensure dependencies are installed
npm install
pip install -r requirements.txt
pip install -r requirements_full.txt

# Verify Tauri CLI (if using native)
npx @tauri-apps/cli --version
```

#### Step 1: Start Backend Services
```bash
# Option A: Unified orchestrator (recommended)
python service_orchestrator.py

# Option B: Individual services
python src/alden_backend.py &
python run_core_simple.py &  
python mcp_api_direct.py &
node start-static.js &
```

#### Step 2: Launch Native Application
```bash
# Start React development server
npm run start:react &

# Wait for React server (3005) then launch native
npm run native
```

#### Expected Behavior
- Tauri native window opens with custom title bar
- React application loads in iframe
- System tray icon appears
- All status indicators show green

### Method 2: Direct React Development

#### For React-only development without native wrapper:
```bash
# Start all services
python service_orchestrator.py &

# Start React dev server
PORT=3005 npm run start:react

# Access via browser: http://localhost:3005
```

### Method 3: Legacy Electron (Fallback)

#### When native application has issues:
```bash
# Traditional launch sequence
npm run dev

# This starts:
# - TypeScript compilation (watch mode)
# - React dev server (port 3005)
# - Electron application
```

## Service Port Mapping

| Service | Port | Health Check | Purpose |
|---------|------|--------------|---------|
| Alden Backend | 8000 | `/health` | Primary AI assistant |
| Core Orchestrator | 8001 | `/api/core/health` | Multi-agent sessions |
| MCP Direct API | 8005 | `/health` | Plugin execution |
| Static Server | 3001 | `/` | Asset serving |
| React Dev Server | 3005 | `/` | Frontend application |
| Native App | - | System Tray | Tauri wrapper |

## Troubleshooting Launch Issues

### Issue: Backend Services Won't Start
```bash
# Check port availability
netstat -tulpn | grep -E ':(8000|8001|8005|3001)'

# Kill conflicting processes
sudo lsof -ti:8000 | xargs kill -9

# Restart services individually
python src/alden_backend.py
```

### Issue: Native Application Compilation Errors
```bash
# Check Tauri version compatibility
npx @tauri-apps/cli --version
cat src-tauri/Cargo.toml | grep tauri

# Clear Rust build cache
cd src-tauri && cargo clean

# Rebuild dependencies
cargo build
```

### Issue: React Development Server Problems
```bash
# Clear npm cache
npm start -- --reset-cache

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Use fixed port
cross-env PORT=3005 BROWSER=none npm run start:react
```

### Issue: WSL/NTFS Permission Problems
```bash
# Option A: Use Windows PowerShell instead of WSL
# Run npm commands from Windows terminal

# Option B: Fix WSL permissions
sudo chown -R $(whoami) node_modules/
chmod -R 755 node_modules/

# Option C: Use different mount options
# Add to /etc/wsl.conf:
# [automount]
# options = "metadata,umask=22,fmask=11"
```

## Environment-Specific Instructions

### Windows Development
```powershell
# Use PowerShell to avoid WSL filesystem issues
npm run native:full

# Or step by step:
Start-Process python -ArgumentList "service_orchestrator.py"
npm run start:react
npm run native
```

### Linux Development
```bash
# Standard launch sequence
python3 service_orchestrator.py &
npm run start:react &
npm run native
```

### macOS Development
```bash
# May require additional Tauri dependencies
brew install --cask tauri
python3 service_orchestrator.py &
npm run start:react &
npm run native
```

## Performance Optimization

### Memory Usage
- **Native App**: ~200MB (Tauri + React)
- **Legacy Electron**: ~400MB (Chromium overhead)
- **Backend Services**: ~300MB total Python processes

### Startup Time
- **Backend Services**: 3-5 seconds
- **React Dev Server**: 10-15 seconds
- **Native Application**: 2-3 seconds
- **Total Cold Start**: ~20 seconds

### Development Workflow
```bash
# Keep backends running during development
python service_orchestrator.py &

# Hot reload frontend only
npm run start:react

# Test native wrapper as needed
npm run native
```

## System Health Monitoring

### Automated Health Checks
The native application includes built-in health monitoring:
- Backend service availability (every 10 seconds)
- React application responsiveness
- MCP plugin connectivity
- Voice system status

### Manual Verification
```bash
# Backend health
curl http://localhost:8000/health
curl http://localhost:8001/api/core/health  
curl http://localhost:8005/health

# Frontend accessibility
curl http://localhost:3005

# MCP functionality test
curl -X POST http://localhost:8005/mcp/filesystem \
  -H "Content-Type: application/json" \
  -d '{"tool": "create_file", "parameters": {"path": "/tmp/test.txt", "content": "test"}}'
```

## Production Deployment Notes

### Building for Distribution
```bash
# Create production build
npm run build

# Build native executable
npm run native:build

# Output location: src-tauri/target/release/
```

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 500MB for application, 2GB for dependencies
- **Network**: Required for external MCP plugins (GitHub, Gmail)
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+

---

**Note**: This guide reflects the post-migration launch procedures. For legacy Electron-only setups, refer to the original CLAUDE.md launch instructions. The native migration provides improved performance and system integration while maintaining full backward compatibility.

**Last Updated**: July 22, 2025 - Post Native Migration