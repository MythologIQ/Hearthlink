# Hearthlink Port Management Guide

## Overview

Hearthlink v1.3.0 includes an enhanced launcher with intelligent port conflict detection and resolution. This guide explains how to handle port conflicts gracefully.

## The Problem

When you see "port 3001 is already in use", it means another process is using a port that Hearthlink needs. The enhanced launcher now detects and resolves these conflicts automatically.

## Quick Solutions

### 1. Automatic Resolution (Recommended)
```bash
./start_hearthlink.sh --auto-ports
```
- Automatically finds alternative ports for any conflicts
- No user intervention required
- Safest option for production use

### 2. Clean Up Existing Processes
```bash
./start_hearthlink.sh --cleanup-ports
```
- Terminates existing Hearthlink processes
- Frees up occupied ports
- Launches fresh instance

### 3. Force Resolution
```bash
./start_hearthlink.sh --force-ports --auto-ports
```
- Automatically terminates conflicting processes
- Finds alternative ports if termination fails
- Use with caution - may terminate important processes

### 4. Interactive Resolution (Default)
```bash
./start_hearthlink.sh
```
- Detects conflicts and asks for permission to terminate
- Shows process details before termination
- Gives you full control over the resolution

## Port Management Options

| Option | Description | Use Case |
|--------|-------------|----------|
| `--check-ports` | Check port availability only | Diagnostic purposes |
| `--cleanup-ports` | Terminate Hearthlink processes | Clean restart |
| `--force-ports` | Force terminate conflicting processes | Automated deployment |
| `--auto-ports` | Find alternative ports automatically | Production environments |

## Detailed Usage Examples

### Example 1: Port 3001 Conflict
```bash
# Problem: Port 3001 is already in use
$ ./start_hearthlink.sh

# Solution 1: Let Hearthlink find an alternative port
$ ./start_hearthlink.sh --auto-ports

# Solution 2: Clean up and use original ports
$ ./start_hearthlink.sh --cleanup-ports
```

### Example 2: Multiple Port Conflicts
```bash
# Comprehensive resolution
$ ./start_hearthlink.sh --force-ports --auto-ports --verbose

# This will:
# 1. Terminate conflicting processes automatically
# 2. Find alternative ports if termination fails
# 3. Show detailed logging of all actions
```

### Example 3: Development Environment
```bash
# Safe development mode with automatic resolution
$ ./start_hearthlink.sh --development --auto-ports --verbose

# This preserves your development workflow while
# handling any port conflicts automatically
```

## What Ports Does Hearthlink Use?

| Port | Service | Purpose |
|------|---------|---------|
| 3000 | React Development Server | Frontend development |
| 3001 | React Production Server | Frontend production |
| 8000 | Python Backend API | Backend services |
| 8001 | FastAPI Documentation | API documentation |

## How Port Resolution Works

1. **Detection**: Launcher scans all required ports
2. **Analysis**: Identifies conflicting processes
3. **Classification**: Determines if processes are Hearthlink-related
4. **Resolution**: 
   - Interactive: Asks permission to terminate
   - Automatic: Finds alternative ports
   - Force: Terminates processes automatically

## Advanced Features

### Smart Process Detection
The launcher can identify:
- Existing Hearthlink instances
- Node.js/Electron processes
- React development servers
- Python/FastAPI backends

### Port Range Scanning
When finding alternative ports, the launcher:
- Starts from the original port number
- Scans up to 50 consecutive ports
- Verifies availability using multiple methods
- Updates environment variables automatically

### Environment Variable Integration
When alternative ports are used:
```bash
export REACT_APP_PORT=3002      # If 3000 was occupied
export REACT_PROD_PORT=3003     # If 3001 was occupied
export BACKEND_PORT=8002        # If 8000 was occupied
export DOCS_PORT=8003           # If 8001 was occupied
```

## Troubleshooting

### "Could not find available port"
```bash
# Too many services running - restart system or manually kill processes
sudo lsof -ti:3000-3010 | xargs kill -9
sudo lsof -ti:8000-8010 | xargs kill -9
```

### "Failed to terminate process"
```bash
# Some processes require elevated privileges
sudo ./start_hearthlink.sh --force-ports
```

### "Permission denied"
```bash
# Make launcher executable
chmod +x start_hearthlink.sh
```

## Best Practices

### Development
- Use `--auto-ports` for hassle-free development
- Use `--verbose` to understand what's happening
- Regular cleanup with `--cleanup-ports`

### Production
- Use `--force-ports --auto-ports` for automated deployment
- Monitor port usage with `--check-ports`
- Document any custom port assignments

### CI/CD
```bash
# Automated pipeline example
./start_hearthlink.sh --force-ports --auto-ports --skip-checks
```

## Manual Port Management

If you prefer manual control:

### Check what's using a port
```bash
lsof -i :3001
netstat -tulpn | grep 3001
```

### Kill process on specific port
```bash
kill -9 $(lsof -ti:3001)
```

### Use custom ports
```bash
export REACT_PROD_PORT=3005
./start_hearthlink.sh
```

## Integration with Package.json

The launcher works with your existing npm scripts:
```json
{
  "scripts": {
    "start": "react-scripts start",
    "launch": "electron launcher.js",
    "dev:enhanced": "concurrently \"npm run launch\" \"npm run react-start\""
  }
}
```

Port environment variables are automatically available to all scripts.

## Monitoring and Logging

### Verbose Mode
```bash
./start_hearthlink.sh --verbose
```
Shows detailed port scanning and resolution process.

### Health Check
```bash
./start_hearthlink.sh --health-check
```
Includes port availability in system health report.

### Port-Only Check
```bash
./start_hearthlink.sh --check-ports
```
Diagnostic tool for port-related issues.

## Common Scenarios

### Scenario 1: Another React App Running
```bash
# Hearthlink detects React on port 3001
# Automatically assigns port 3002 to Hearthlink
./start_hearthlink.sh --auto-ports
```

### Scenario 2: Previous Hearthlink Crashed
```bash
# Clean up zombie processes and restart
./start_hearthlink.sh --cleanup-ports
```

### Scenario 3: Docker Containers Using Ports
```bash
# Force resolution and find alternatives
./start_hearthlink.sh --force-ports --auto-ports
```

### Scenario 4: System Restart Required
```bash
# Check port availability first
./start_hearthlink.sh --check-ports

# If many conflicts exist, system restart may be needed
sudo reboot
```

## Summary

The enhanced Hearthlink launcher eliminates port conflicts through:

✅ **Intelligent Detection** - Identifies conflicts automatically  
✅ **Smart Resolution** - Multiple resolution strategies  
✅ **User Control** - Interactive or automated modes  
✅ **Production Ready** - Suitable for CI/CD and deployment  
✅ **Comprehensive Logging** - Full visibility into resolution process  

Choose the option that best fits your workflow and environment.