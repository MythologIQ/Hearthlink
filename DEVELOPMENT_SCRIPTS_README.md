# Hearthlink Development Scripts

This directory contains secure launch and shutdown scripts for the Hearthlink development environment.

## 📁 Files

- `launch_hearthlink_dev.bat` - Secure development environment launcher
- `shutdown_hearthlink_dev.bat` - Clean development environment shutdown
- `DEVELOPMENT_SCRIPTS_README.md` - This documentation

## 🚀 Quick Start

### Launch Development Environment
```bash
# Double-click or run from command line
launch_hearthlink_dev.bat
```

### Shutdown Development Environment
```bash
# Double-click or run from command line
shutdown_hearthlink_dev.bat
```

## 📋 Features

### Launch Script (`launch_hearthlink_dev.bat`)

✅ **Environment Validation**
- Checks for Python, Node.js, and npm
- Validates all required tools are available

✅ **Virtual Environment Management**
- Creates Python virtual environment if needed
- Activates virtual environment automatically
- Installs Python dependencies from `requirements.txt`

✅ **Dependency Management**
- Installs Node.js dependencies with `--legacy-peer-deps`
- Handles dependency conflicts gracefully

✅ **Service Launch**
- Starts React development server (minimized)
- Launches Electron development (minimized)
- Starts Python backend if available (minimized)

✅ **Comprehensive Logging**
- Timestamped log files in `logs/` directory
- Detailed error reporting and diagnostics
- Automatic log file opening for review

✅ **Error Handling**
- Graceful failure with helpful error messages
- Common issue troubleshooting guidance
- Non-blocking warnings for non-critical issues

### Shutdown Script (`shutdown_hearthlink_dev.bat`)

✅ **Process Termination**
- Kills all Node.js processes (React, Electron)
- Terminates Python processes (backend)
- Cleans up any remaining development processes

✅ **Port Cleanup**
- Checks for port conflicts on common dev ports
- Reports port status for troubleshooting

✅ **File Cleanup**
- Removes temporary cache files
- Cleans Python cache (`__pycache__`, `.pyc`)
- Manages npm cache

✅ **Log Management**
- Rotates log files (keeps last 10)
- Prevents log directory bloat
- Maintains clean development environment

## 🔧 Configuration

### Environment Variables
The scripts automatically detect and use:
- `APP_DIR` - Current script directory
- `LOG_DIR` - `logs/` subdirectory
- `PYTHON_ENV` - `venv/` Python virtual environment
- `NODE_ENV` - Set to `development`

### Customization
Edit the scripts to modify:
- **Ports**: Change default development ports
- **Paths**: Adjust directory structures
- **Dependencies**: Modify package installation commands
- **Logging**: Customize log file naming and retention

## 📊 Log Files

### Launch Logs
- Location: `logs/hearthlink_launch_YYYY-MM-DD_HH-MM-SS.log`
- Contains: Environment checks, dependency installation, service startup
- Format: Timestamped entries with error levels

### Shutdown Logs
- Location: `logs/hearthlink_shutdown_YYYY-MM-DD_HH-MM-SS.log`
- Contains: Process termination, cleanup operations, port status
- Format: Timestamped entries with operation results

### Log Rotation
- Keeps last 10 log files automatically
- Removes older logs to prevent disk space issues
- Maintains clean development environment

## 🐛 Troubleshooting

### Common Issues

#### Python Not Found
```
[ERROR] Python not found in PATH
```
**Solution**: Install Python and add to PATH, or use full path to Python executable.

#### Node.js Not Found
```
[ERROR] Node.js not found in PATH
```
**Solution**: Install Node.js and add to PATH, or use full path to Node.js executable.

#### Port Conflicts
```
[WARNING] Port 3000 is still in use
```
**Solution**: 
1. Run `shutdown_hearthlink_dev.bat` to clean up
2. Check for other development servers
3. Use different ports in configuration

#### Permission Errors
```
[ERROR] Failed to create virtual environment
```
**Solution**: 
1. Run as Administrator
2. Check folder permissions
3. Ensure sufficient disk space

#### Dependency Installation Failures
```
[ERROR] Failed to install Node.js dependencies
```
**Solution**:
1. Clear npm cache: `npm cache clean --force`
2. Delete `node_modules` and reinstall
3. Check network connectivity

### Debug Mode
To enable verbose logging, edit the scripts and add:
```batch
set DEBUG=1
```

## 🔒 Security Features

### Environment Isolation
- Python virtual environment prevents system conflicts
- Node.js dependencies isolated to project
- No system-wide changes

### Process Management
- Controlled startup and shutdown
- Proper process termination
- No orphaned processes

### Logging Security
- No sensitive data in logs
- Timestamped entries for audit trail
- Automatic log rotation

## 📈 Performance

### Startup Time
- **First Run**: 2-5 minutes (dependency installation)
- **Subsequent Runs**: 30-60 seconds
- **Hot Reload**: 5-10 seconds

### Resource Usage
- **Memory**: 200-400 MB total
- **CPU**: Low during idle, moderate during development
- **Disk**: 500 MB - 1 GB for dependencies

## 🔄 Workflow Integration

### Development Workflow
1. **Start**: Run `launch_hearthlink_dev.bat`
2. **Develop**: Make changes, see hot reload
3. **Test**: Use built-in testing tools
4. **Stop**: Run `shutdown_hearthlink_dev.bat`

### CI/CD Integration
- Scripts can be called from build systems
- Log files provide build feedback
- Environment setup automated

### Team Development
- Consistent environment across team members
- Shared logging for debugging
- Standardized startup/shutdown procedures

## 📝 Best Practices

### Daily Development
1. Always use the launch script to start development
2. Check log files for any warnings or errors
3. Use shutdown script when finished
4. Keep log files for troubleshooting

### Troubleshooting
1. Check log files first for error details
2. Verify environment requirements
3. Clear caches if needed
4. Restart development environment

### Maintenance
1. Regularly review and clean log files
2. Update dependencies as needed
3. Test scripts after environment changes
4. Keep scripts in version control

## 🤝 Contributing

### Script Improvements
1. Test changes thoroughly
2. Update documentation
3. Maintain backward compatibility
4. Add error handling for new features

### Bug Reports
Include in bug reports:
- Script version/date
- Log file contents
- Environment details
- Steps to reproduce

---

**Note**: These scripts are designed for development use only. For production deployment, use the proper build and deployment processes. 