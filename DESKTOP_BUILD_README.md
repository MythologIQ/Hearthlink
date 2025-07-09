# Hearthlink Desktop Application Build Guide

This guide covers building and packaging the Hearthlink application as a self-contained desktop application using Electron.

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10+ (x64)
- **Node.js**: 18.0.0 or higher
- **npm**: 8.0.0 or higher
- **Git**: For version control

### Required Software
- **Visual Studio Build Tools** (for native dependencies)
- **Windows SDK** (for MSI packaging)

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/WulfForge/Hearthlink.git
cd Hearthlink
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Build the Application
```bash
# Option 1: Use the automated build script
node build.js

# Option 2: Manual build process
npm run build          # Build React app
npm run dist-msi       # Build MSI installer
```

## 📦 Build Output

### Generated Files
- **MSI Installer**: `dist/windows/HearthlinkSetup-v1.1.0.msi`
- **Size**: Approximately 150-200 MB
- **Architecture**: x64
- **Target**: Windows 10+

### Package Contents
- ✅ React application (Alden + Dashboard)
- ✅ Voice interface and accessibility tools
- ✅ Documentation (`docs/public/`)
- ✅ License, README, SBOM files
- ✅ Electron runtime
- ✅ All required dependencies

## 🔧 Build Configuration

### Electron Builder Configuration
The build is configured in `package.json` under the `build` section:

```json
{
  "build": {
    "appId": "com.hearthlink.app",
    "productName": "Hearthlink",
    "directories": {
      "output": "dist"
    },
    "win": {
      "target": [
        {
          "target": "msi",
          "arch": ["x64"]
        }
      ],
      "icon": "assets/icon.ico",
      "artifactName": "HearthlinkSetup-v1.1.0.msi"
    },
    "msi": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

### Key Features
- **Customizable Installation**: Users can choose installation directory
- **Desktop Shortcut**: Automatic desktop shortcut creation
- **Start Menu Integration**: Proper Windows integration
- **Uninstall Support**: Clean removal capability
- **Silent Install**: Supports silent installation mode

## 🎯 Development Workflow

### Development Mode
```bash
# Start development server with Electron
npm run dev

# Start only React development server
npm run react-start

# Start only Electron
npm run electron-dev
```

### Production Build
```bash
# Build for production
npm run dist

# Build Windows MSI specifically
npm run dist-msi

# Build all platforms
npm run dist-all
```

## 🔒 Security Features

### Built-in Security
- **Context Isolation**: Prevents direct Node.js access from renderer
- **Content Security Policy**: Restricts resource loading
- **Preload Scripts**: Secure API exposure
- **External Link Protection**: Opens external links in default browser

### Code Signing
For production distribution, consider code signing:

```bash
# Install certificate
certutil -importpfx certificate.pfx

# Build with signing
npm run dist-msi -- --sign
```

## 📱 Application Features

### Core Functionality
- **AI Personas**: Alden (ADHD support) and Dashboard
- **Voice Commands**: Hands-free operation
- **Accessibility**: Screen reader support, high contrast, keyboard navigation
- **Documentation**: Built-in help system

### Keyboard Shortcuts
- `F1`: Open help
- `Ctrl+Shift+V`: Toggle voice interface
- `Ctrl+Shift+A`: Toggle accessibility panel
- `Ctrl+N`: New session
- `Ctrl+Q`: Exit application

### Voice Commands
- "New session" - Start fresh
- "Help" - Open user guide
- "Accessibility" - Open accessibility guide
- "Exit" or "Quit" - Close application

## 🐛 Troubleshooting

### Common Issues

#### Build Fails
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Electron Build Issues
```bash
# Install Windows build tools
npm install --global windows-build-tools

# Rebuild native dependencies
npm rebuild
```

#### MSI Creation Fails
- Ensure Windows SDK is installed
- Check for sufficient disk space (2GB+ recommended)
- Verify antivirus isn't blocking the build process

### Debug Mode
```bash
# Enable debug logging
set DEBUG=electron-builder
npm run dist-msi
```

## 📊 Distribution

### File Distribution
- **Direct Download**: Host MSI file on website
- **GitHub Releases**: Use GitHub's release system
- **Enterprise Distribution**: Use Group Policy or SCCM

### Installation Options
```bash
# Silent installation
msiexec /i HearthlinkSetup-v1.1.0.msi /quiet

# Custom installation directory
msiexec /i HearthlinkSetup-v1.1.0.msi INSTALLDIR="C:\Custom\Path"

# Uninstall
msiexec /x HearthlinkSetup-v1.1.0.msi /quiet
```

## 🔄 Updates

### Auto-Updater Configuration
The application includes auto-update capabilities:

```javascript
// In main.js
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();
```

### Update Channels
- **Stable**: Production releases
- **Beta**: Pre-release testing
- **Alpha**: Development builds

## 📈 Performance

### Optimization
- **Code Splitting**: Lazy loading of components
- **Asset Optimization**: Compressed images and resources
- **Tree Shaking**: Remove unused code
- **Caching**: Efficient resource caching

### Memory Usage
- **Typical**: 150-250 MB RAM
- **Peak**: 300-400 MB RAM
- **Idle**: 100-150 MB RAM

## 🧪 Testing

### Automated Testing
```bash
# Run all tests
npm test

# Run specific test suites
npm run test:unit
npm run test:integration
npm run test:e2e
```

### Manual Testing Checklist
- [ ] Application launches correctly
- [ ] Voice commands work
- [ ] Accessibility features function
- [ ] Documentation loads properly
- [ ] Uninstall process works
- [ ] Updates install correctly

## 📝 Release Notes

### Version 1.1.0
- Initial desktop release
- Voice command support
- Accessibility features
- Documentation integration
- Windows MSI packaging

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- Follow ESLint configuration
- Use Prettier for formatting
- Write meaningful commit messages
- Include tests for new features

## 📞 Support

### Getting Help
- **Documentation**: Check `/docs/public/` directory
- **Issues**: Report on GitHub Issues
- **Discussions**: Use GitHub Discussions
- **Email**: Contact development team

### System Requirements Verification
```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Check available disk space
dir

# Check Windows version
ver
```

---

**Note**: This build process creates a self-contained Windows application. For other platforms (macOS, Linux), additional configuration and testing is required. 