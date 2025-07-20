# Hearthlink v1.2.0 - Launch Instructions

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm 8+
- Python 3.8+ (optional, for backend services)

### Standard Launch (Recommended)
```bash
# Install dependencies
npm install

# Build the application
npm run build

# Launch Hearthlink with enhanced features
npm run launch
```

### Development Mode
```bash
# Start React development server
npm run start:react

# In another terminal, launch the enhanced Electron app
npm run dev:enhanced
```

### Production Build
```bash
# Build and package for distribution
npm run native:enhanced

# Or build MSI installer (Windows)
npm run dist-msi
```

## 🎯 Launch Modes

### 1. Enhanced Native Launcher (New)
```bash
npm run launch
```
**Features:**
- Advanced Alice behavioral analysis integration
- Comprehensive system health monitoring  
- Enhanced authentication and authorization
- Real-time diagnostics and performance metrics
- Production-ready error handling and logging

### 2. Standard Electron Launcher
```bash
npm run start
```
**Features:**
- Basic Electron application
- Core functionality
- Standard error handling

### 3. Tauri Native (Alternative)
```bash
npm run native
```
**Features:**
- Rust-based native wrapper
- Smaller bundle size
- Cross-platform compatibility

## 🏗️ System Architecture

### Alice Behavioral Analysis Module ✨
The enhanced launcher includes our new **Alice** module for advanced behavioral analysis:

- **Real-time mood analysis** from user interactions
- **Communication pattern recognition** and optimization suggestions  
- **Context-aware coaching** recommendations
- **Behavioral profile** building and adaptation
- **Cross-session learning** and insights

### Core Infrastructure
- **SystemLogger**: Centralized logging with correlation IDs
- **HealthMonitor**: Real-time system health and performance tracking
- **AuthenticationManager**: Role-based access control and session management
- **ConfigManager**: Environment-specific configuration management
- **APIManager**: Cross-module communication and event orchestration

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Development/Production Mode
NODE_ENV=production

# API Keys (optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key  
GOOGLE_API_KEY=your_google_key

# System Configuration
HEARTHLINK_LOG_LEVEL=info
HEARTHLINK_MONITORING_ENABLED=true
HEARTHLINK_ALICE_ENABLED=true

# Python Backend (optional)
PYTHON_PATH=python
```

### Configuration Files
The system supports multiple configuration sources:
- `/config/default.json` - Base configuration
- `/config/production.json` - Production overrides
- `/config/local.json` - Local development settings
- Environment variables with `REACT_APP_HEARTHLINK_` prefix

## 🎮 User Interface

### Radial Navigation
Access different modules through the central radial navigation:
- **ALDEN** - Main conversational AI
- **ALICE** - Behavioral analysis interface ⭐ 
- **CORE** - System orchestration
- **VAULT** - Memory and knowledge management
- **SYNAPSE** - Security and permissions
- **SENTRY** - System monitoring

### Alice Interface Features
When you select Alice from the radial navigation:

1. **Overview Tab**
   - Real-time mood analysis with visual mood ring
   - Communication style metrics
   - Behavioral profile summary
   - Stress and engagement indicators

2. **Analysis Tab**  
   - Communication pattern visualization
   - Context flow analysis
   - Topic switching detection
   - Conversation depth metrics

3. **Coaching Tab**
   - Personalized recommendations
   - Communication effectiveness tips
   - Behavioral optimization suggestions
   - Implementation guidance

## 🔍 System Monitoring

### Health Dashboard
Access through the system menu: **System → Health Monitor**

**Real-time Metrics:**
- Memory usage and optimization
- CPU performance tracking  
- Network connectivity status
- Module health verification
- Alice analysis performance

### Performance Analytics
Access through: **System → Performance Metrics**

**Analytics Include:**
- Response time optimization
- Behavioral analysis accuracy
- Communication pattern trends
- User engagement metrics
- System efficiency scores

## 🛠️ Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check Node.js version
node --version

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Try standard launcher first
npm run start
```

#### 2. Alice Module Not Loading
```bash
# Verify Alice integration
npm run launch -- --debug

# Check system logs
tail -f userData/logs/system.log
```

#### 3. Performance Issues
```bash
# Clear application cache
rm -rf userData/cache/*

# Reset Alice behavioral profile
rm -rf userData/alice/*

# Restart with health monitoring
HEARTHLINK_MONITORING_ENABLED=true npm run launch
```

#### 4. Build Issues
```bash
# Clean build
rm -rf build/
npm run build

# Verify build output
ls -la build/
```

### Debug Mode
```bash
# Launch with debug logging
DEBUG=* npm run launch

# Launch with Alice debug mode
HEARTHLINK_ALICE_DEBUG=true npm run launch
```

### Log Files
System logs are located in:
- **System logs**: `userData/logs/system.log`
- **Alice logs**: `userData/logs/alice.log`  
- **Health logs**: `userData/logs/health.log`
- **Error logs**: `userData/logs/error.log`

## 📱 Platform Support

### Windows
```bash
# Standard launch
npm run launch

# Create MSI installer
npm run dist-msi
```

### macOS  
```bash
# Standard launch
npm run launch

# Create DMG installer
npm run dist-mac
```

### Linux
```bash
# Standard launch
npm run launch

# Create AppImage
npm run dist-linux
```

## 🔐 Security Features

### Authentication
- Local user authentication
- Token-based session management
- Role-based access control (Admin, User, Agent, Viewer)
- Session timeout and security monitoring

### Data Protection
- AES-256 encryption for sensitive data
- Local-first behavioral data storage
- No external transmission of personal insights
- Comprehensive audit logging

### Privacy by Design
- All Alice behavioral analysis stays local
- User has complete control over behavioral data
- Optional data export/import functionality
- Transparent data usage documentation

## 🎯 Performance Optimization

### Memory Management
- Automatic garbage collection optimization
- Behavioral profile caching strategies
- Efficient data structure usage
- Memory leak detection and prevention

### CPU Optimization  
- Background processing for Alice analysis
- Efficient event handling and debouncing
- Smart caching of computation results
- Adaptive performance scaling

### Storage Optimization
- Compressed behavioral data storage
- Intelligent cache management
- Automatic cleanup of old data
- Configurable retention policies

## 📚 Documentation

### User Guides
- **Getting Started**: Basic application usage
- **Alice Guide**: Behavioral analysis features
- **Voice Commands**: Complete voice command reference
- **Accessibility**: WCAG compliance and accessibility features

### Developer Documentation
- **API Reference**: Complete API documentation
- **Module Architecture**: System design and patterns
- **Alice Integration**: Behavioral analysis SDK
- **Security Guidelines**: Security best practices

### Support
- **GitHub Issues**: Bug reports and feature requests
- **Community Forum**: User discussions and support
- **Documentation Wiki**: Comprehensive guides and tutorials

## 🚀 Advanced Usage

### Custom Behavioral Analysis
```javascript
// Access Alice API from renderer process
const alice = await window.electronAPI.alice;

// Analyze custom interaction data
const analysis = await alice.analyze({
  text: "User interaction text",
  context: "conversation context",
  metadata: { sessionId: "123" }
});

console.log('Behavioral Analysis:', analysis);
```

### System Health Monitoring
```javascript
// Monitor system health
const health = await window.electronAPI.system.getStatus();

console.log('System Health:', health.health);
console.log('Performance Metrics:', health.metrics);
```

### Configuration Management
```javascript
// Get/set configuration values
const theme = await window.electronAPI.config.get('ui.theme');
await window.electronAPI.config.set('ui.theme', 'dark');
```

## 🔄 Updates and Maintenance

### Automatic Updates
- Built-in update checking and notification
- Staged rollout for safety
- Behavioral profile migration support
- Rollback capability for failed updates

### Manual Updates
```bash
# Check for updates
npm run check-updates

# Update dependencies
npm update

# Rebuild with latest features
npm run build && npm run launch
```

### Data Backup
```bash
# Backup user data
npm run backup

# Restore from backup
npm run restore -- backup-file.json
```

---

## 🎉 Welcome to Hearthlink v1.2.0!

Your AI-powered productivity system is now enhanced with advanced behavioral analysis through Alice. The system learns from your interaction patterns to provide personalized coaching and optimization recommendations.

**Key New Features in v1.2.0:**
- ✨ Alice behavioral analysis module
- 🔍 Advanced system health monitoring  
- 🛡️ Enhanced security and authentication
- ⚡ Performance optimization improvements
- 🎯 Real-time coaching recommendations

Launch the application and explore the Alice interface to start benefiting from personalized AI assistance!

For questions or support, check the documentation or reach out through our support channels.