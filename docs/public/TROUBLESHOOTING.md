# Hearthlink Troubleshooting Guide

## Quick Diagnostic Steps

Before diving into specific issues, try these quick diagnostic steps:

1. **Check Service Status**: Look at status lights in the main interface
2. **Restart Services**: Try restarting individual services from Settings
3. **Check System Resources**: Monitor CPU and memory usage
4. **Review Error Logs**: Check the diagnostics panel for recent errors
5. **Test Network Connectivity**: Ensure local services can communicate

## Common Issues and Solutions

### Application Launch Issues

#### Problem: Hearthlink Won't Start

**Symptoms:**
- Application doesn't launch
- Black screen or loading screen hangs
- Error messages during startup

**Solutions:**

1. **Check Node.js Version**
   ```bash
   node --version  # Should be 18.x or higher
   npm --version   # Should be 8.x or higher
   ```

2. **Reinstall Dependencies**
   ```bash
   npm install
   npm run build
   ```

3. **Clear Application Cache**
   - Windows: `%APPDATA%\Hearthlink\`
   - macOS: `~/Library/Application Support/Hearthlink/`
   - Linux: `~/.config/Hearthlink/`

4. **Check Port Availability**
   ```bash
   netstat -an | grep :800  # Check if ports 8000-8004 are free
   ```

#### Problem: Electron Opens But Shows "File Not Found"

**Symptoms:**
- Electron window opens successfully
- Content area shows "File not found" or blank page
- Developer console shows 404 errors

**Solutions:**

1. **Rebuild React Application**
   ```bash
   npm run build
   ```

2. **Check Build Directory**
   - Verify `build/` directory exists and contains `index.html`
   - Check file permissions on build directory

3. **Use Fallback Test Page**
   - Temporarily use `public/test.html` for basic functionality
   - Check if main.js fallback logic is working

4. **WSL/Windows Permission Issues**
   ```bash
   # If using WSL, try from Windows directly:
   G:\MythologIQ\Hearthlink> npm start
   ```

### Service Connection Issues

#### Problem: Services Not Starting

**Symptoms:**
- Red status lights in interface
- "Service unavailable" errors
- API endpoints returning 500 errors

**Solutions:**

1. **Check Individual Services**
   - LLM API (Port 8001): `curl http://localhost:8001/api/health`
   - Core API (Port 8000): `curl http://localhost:8000/api/health`
   - Vault API (Port 8002): `curl http://localhost:8002/api/vault/health`
   - Synapse API (Port 8003): `curl http://localhost:8003/api/synapse/health`
   - Sentry API (Port 8004): `curl http://localhost:8004/api/sentry/health`

2. **Restart Backend Services**
   ```bash
   python src/main.py                    # Core services
   python src/run_services.py           # All services
   python src/api/simple_backend.py     # LLM API service
   ```

3. **Check Python Environment**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_full.txt
   ```

4. **Port Conflicts**
   ```bash
   # Kill processes using required ports
   sudo lsof -i :8000  # Find process using port 8000
   sudo kill -9 <PID>  # Kill the process
   ```

#### Problem: Service Status Lights Not Updating

**Symptoms:**
- Status lights don't reflect actual service state
- Services running but showing as offline
- Inconsistent status across different components

**Solutions:**

1. **Refresh Service Status**
   - Click "Check Service Status" button in Settings
   - Restart the frontend application
   - Clear browser cache if running in development

2. **Check Service Endpoints**
   - Verify all health check endpoints are responding
   - Check for endpoint URL changes in configuration
   - Ensure proper CORS headers are set

3. **Review Network Configuration**
   - Check firewall settings
   - Verify localhost resolution
   - Test with 127.0.0.1 instead of localhost

### Voice Interface Issues

#### Problem: Voice Commands Not Working

**Symptoms:**
- Microphone icon shows but no recognition
- Voice commands not triggering actions
- "Voice not available" errors

**Solutions:**

1. **Check Browser Permissions**
   - Ensure microphone permissions are granted
   - Check browser security settings
   - Test in different browsers (Chrome, Firefox, Edge)

2. **Audio Device Issues**
   ```bash
   # Check audio devices (Linux)
   arecord -l
   
   # Test microphone
   arecord -d 5 test.wav && aplay test.wav
   ```

3. **Web Speech API Support**
   - Test in supported browsers (Chrome recommended)
   - Check for HTTPS requirement in production
   - Verify WebRTC functionality

4. **Voice Settings Configuration**
   - Check voice settings in Settings panel
   - Adjust microphone sensitivity
   - Test different voice recognition languages

#### Problem: Voice Commands Recognized But Not Executed

**Symptoms:**
- Voice input appears in interface
- Commands are understood but no action taken
- Partial command execution

**Solutions:**

1. **Check Command Mapping**
   - Verify voice command handlers are registered
   - Check for exact command phrase matching
   - Review voice routing compliance settings

2. **Agent State Issues**
   - Ensure target agent is active and available
   - Check agent permission settings
   - Verify external agent access policies

3. **Context Issues**
   - Check current application context
   - Verify active session state
   - Ensure proper focus management

### AI Agent Issues

#### Problem: Agents Not Responding

**Symptoms:**
- Agent shows as active but doesn't respond
- Long delays in agent responses
- "Agent unavailable" messages

**Solutions:**

1. **Check LLM Service Connection**
   ```bash
   curl http://localhost:8001/api/llm/health
   curl http://localhost:11434/api/tags  # For Ollama
   ```

2. **Restart LLM Backend**
   ```bash
   # Restart Ollama if using local LLM
   ollama serve
   
   # Or restart custom LLM service
   python src/api/local_llm_api.py
   ```

3. **Check Model Availability**
   - Verify required models are downloaded
   - Check model compatibility
   - Monitor system resources (RAM/CPU)

4. **Configuration Issues**
   - Check LLM configuration in Settings
   - Verify API endpoints are correct
   - Test with different model sizes

#### Problem: Multi-Agent Sessions Not Working

**Symptoms:**
- Cannot create sessions with multiple agents
- Agents not taking turns properly
- Session creation fails

**Solutions:**

1. **Check Core Service**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Review Session Configuration**
   - Verify agent selection in Core interface
   - Check turn-taking settings
   - Ensure proper session management

3. **Memory Management Issues**
   - Check Vault service status
   - Verify memory persistence settings
   - Clear old session data if needed

### Memory and Data Issues

#### Problem: Settings Not Saving

**Symptoms:**
- Settings changes don't persist
- Configuration resets on restart
- "Save failed" error messages

**Solutions:**

1. **Check Settings API**
   ```bash
   curl -X POST http://localhost:8001/api/settings \
        -H "Content-Type: application/json" \
        -d '{"test": "data"}'
   ```

2. **File Permissions**
   ```bash
   # Check settings file permissions
   ls -la config/
   chmod 644 config/*.json
   ```

3. **Local Storage Fallback**
   - Check browser localStorage
   - Clear localStorage if corrupted
   - Verify localStorage quota

4. **Backend Service Issues**
   - Restart settings API service
   - Check database connectivity
   - Verify write permissions

#### Problem: Memory/Data Loss

**Symptoms:**
- Agent memories not persisting
- Session history missing
- Conversation context lost

**Solutions:**

1. **Check Vault Service**
   ```bash
   curl http://localhost:8002/api/vault/health
   ```

2. **Database Issues**
   - Check database file integrity
   - Verify backup systems
   - Restore from backup if needed

3. **Memory Management**
   - Check available disk space
   - Verify memory limits in configuration
   - Monitor memory usage patterns

### Performance Issues

#### Problem: Slow Response Times

**Symptoms:**
- Long delays between commands and responses
- Interface feels sluggish
- High CPU or memory usage

**Solutions:**

1. **System Resource Monitoring**
   ```bash
   # Check system resources
   top           # Linux/macOS
   taskmgr       # Windows
   
   # Check disk space
   df -h         # Linux/macOS
   ```

2. **Service Optimization**
   - Reduce number of active agents
   - Limit concurrent sessions
   - Optimize model selection for available hardware

3. **Database Optimization**
   - Clean up old session data
   - Optimize database indexes
   - Vacuum database files

4. **Network Issues**
   - Check local network latency
   - Test with different DNS servers
   - Verify firewall isn't blocking traffic

### Security and Permission Issues

#### Problem: External Agent Access Denied

**Symptoms:**
- External agents blocked by default
- Permission denied errors
- Security warnings

**Solutions:**

1. **Check Voice Routing Policy**
   - Review voice access policy settings
   - Verify external agent permissions
   - Check security mode activation

2. **Sentry Security Settings**
   - Review Sentry monitoring configuration
   - Check threat detection sensitivity
   - Verify whitelist/blacklist settings

3. **Plugin Security**
   - Check Synapse plugin permissions
   - Verify sandbox execution settings
   - Review API rate limiting

### Development and Build Issues

#### Problem: Build Failures

**Symptoms:**
- `npm run build` fails
- Missing dependencies errors
- TypeScript compilation errors

**Solutions:**

1. **Clean Build Environment**
   ```bash
   rm -rf node_modules/
   rm package-lock.json
   npm install
   npm run build
   ```

2. **Check Node/npm Versions**
   ```bash
   nvm use 18      # Use Node.js 18
   npm install -g npm@latest
   ```

3. **Dependency Issues**
   ```bash
   npm audit fix
   npm update
   ```

#### Problem: Hot Reload Not Working

**Symptoms:**
- Changes not reflected in development
- Manual refresh required
- Development server issues

**Solutions:**

1. **Restart Development Server**
   ```bash
   npm run dev
   ```

2. **Check File Watchers**
   ```bash
   # Increase file watcher limit (Linux)
   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```

3. **Clear Development Cache**
   ```bash
   npm start -- --reset-cache
   ```

## Diagnostic Tools

### Built-in Diagnostics

1. **Service Status Panel**
   - Location: Settings → Service Status
   - Shows real-time status of all services
   - Provides quick restart options

2. **System Health Dashboard**
   - Location: Core → System Overview
   - Displays system metrics
   - Shows resource usage

3. **Error Log Viewer**
   - Location: Settings → Diagnostics
   - Real-time error monitoring
   - Searchable log history

### Command Line Diagnostics

1. **Service Health Check Script**
   ```bash
   node test-service-status-lights.js
   ```

2. **Core Tests**
   ```bash
   python run_core_tests.py
   python tests/test_voice_routing_compliance.py
   ```

3. **Network Connectivity Test**
   ```bash
   curl -v http://localhost:8001/api/health
   ping localhost
   ```

### Log File Locations

- **Application Logs**: `logs/hearthlink_*.log`
- **Service Logs**: `logs/services/`
- **Error Logs**: `logs/errors/`
- **Audit Logs**: `logs/audit/`

## Getting Help

### Self-Service Resources

1. **In-App Help**: Press F1 or say "Help"
2. **Documentation**: Complete user guides and API docs
3. **FAQ**: Common questions and answers
4. **Community Forums**: User-to-user support

### Official Support

1. **GitHub Issues**: Report bugs and request features
2. **Technical Support**: For complex technical issues
3. **Live Chat**: Available during business hours
4. **Email Support**: support@hearthlink.app

### Emergency Support

For critical system failures:

1. **Emergency Contacts**: Listed in app about section
2. **Safe Mode**: Launch with minimal services
3. **Backup Recovery**: Automatic backup restoration
4. **System Reset**: Complete configuration reset option

---

*This troubleshooting guide covers the most common issues. If you encounter a problem not listed here, please consult the community forums or contact technical support.*