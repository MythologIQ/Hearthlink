# Hearthlink Frequently Asked Questions

## General Questions

### What is Hearthlink?

Hearthlink is an advanced AI orchestration system that enables multi-agent collaboration, voice interaction, and comprehensive project management. It's designed with accessibility-first principles to provide an inclusive AI experience for users with diverse needs.

### Who is Hearthlink for?

- **Productivity enthusiasts** seeking AI-powered workflow optimization
- **Professionals** managing complex projects requiring multiple perspectives
- **Users with accessibility needs** requiring voice-first or keyboard-only interaction
- **Developers** interested in multi-agent AI systems
- **Organizations** needing secure, local-first AI solutions

### What makes Hearthlink different from other AI assistants?

- **Multi-agent collaboration** - Multiple AI personas working together
- **Accessibility-first design** - Built for users with diverse abilities
- **Voice-first interaction** - Comprehensive voice command system
- **Local-first architecture** - Your data stays on your machine
- **Modular design** - Choose the components you need

### Is Hearthlink free?

Hearthlink is open-source software available under an MIT license. The core application is free to use, modify, and distribute. Some advanced features or cloud integrations may have associated costs.

## Getting Started

### What are the system requirements?

**Minimum Requirements:**
- **OS**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **RAM**: 4GB (8GB recommended for better performance)
- **CPU**: Dual-core 2.0GHz (Quad-core recommended)
- **Storage**: 2GB free space (more for AI models)
- **Network**: Internet connection for initial setup and updates

**Recommended for Optimal Experience:**
- **RAM**: 16GB+ for large AI models
- **CPU**: 6+ cores for multi-agent sessions
- **GPU**: NVIDIA GPU for accelerated AI processing
- **Storage**: SSD for better performance

### How do I install Hearthlink?

1. **Download** the latest release from the official repository
2. **Extract** the files to your preferred location
3. **Run** the installer or launch script for your platform
4. **Follow** the setup wizard for initial configuration

For developers:
```bash
git clone https://github.com/WulfForge/Hearthlink.git
cd Hearthlink
npm install
npm run build
npm start
```

### Why won't Hearthlink start?

Common causes and solutions:

1. **Port conflicts**: Ensure ports 8000-8004 are available
2. **Missing dependencies**: Run `npm install` to install required packages
3. **Outdated Node.js**: Update to Node.js 18.x or higher
4. **File permissions**: Check that the installation directory has proper permissions
5. **Antivirus interference**: Add Hearthlink to antivirus exceptions

See the [Troubleshooting Guide](TROUBLESHOOTING.md) for detailed solutions.

## Features and Functionality

### What AI agents are available?

**Core Agents:**
- **Alden** - Primary productivity assistant for daily tasks and project management
- **Alice** - Cognitive analysis specialist for data insights and pattern recognition
- **Mimic** - Adaptive persona system for specialized domain expertise
- **Sentry** - Security monitoring and system health management

**Orchestration:**
- **Core** - Multi-agent session management and turn-taking coordination
- **Vault** - Memory management and secure data storage
- **Synapse** - Plugin management and external service integration

### How do multi-agent sessions work?

1. **Session Creation**: Start a new session in the Core module
2. **Agent Selection**: Choose which AI agents to include
3. **Turn Management**: Core coordinates speaking order and context sharing
4. **Memory Sharing**: Agents share insights through the Vault system
5. **Collaboration**: Multiple perspectives on complex problems
6. **Session Archive**: Complete conversation history saved for future reference

### Can I use my own AI models?

Yes! Hearthlink supports:

- **Local LLM integration** - Ollama, LM Studio, and other local providers
- **Custom API endpoints** - Connect to your preferred AI services
- **Model selection** - Choose models based on your hardware and needs
- **Hybrid deployment** - Mix local and cloud-based models

### What voice commands are supported?

**Navigation Commands:**
- "Help" - Open help documentation
- "Settings" - Open settings panel
- "Switch to [agent name]" - Change active agent
- "New session" - Start fresh conversation

**Agent Commands:**
- "Alden, help me with..." - Direct task to Alden
- "Alice, analyze..." - Request analysis from Alice
- "Core, start session with..." - Begin multi-agent collaboration

**System Commands:**
- "Check status" - System health overview
- "Save settings" - Save current configuration
- "Accessibility" - Open accessibility options
- "Quit" or "Exit" - Close application

## Privacy and Security

### Where is my data stored?

Hearthlink follows a **local-first** approach:

- **Primary storage**: All data stored locally on your machine
- **Encrypted storage**: Sensitive data encrypted at rest
- **No cloud requirement**: Works completely offline after initial setup
- **User control**: You decide what data (if any) to share with external services
- **Audit trails**: Complete logging of all data access and modifications

### Is my conversation data private?

Yes, absolutely:

- **Local processing**: Conversations processed on your machine
- **No external transmission**: Data doesn't leave your device unless you explicitly configure external integrations
- **Encrypted storage**: Conversation history encrypted locally
- **User-controlled sharing**: You choose what to share with external AI services
- **Memory management**: Granular control over what data is retained

### How secure is Hearthlink?

Security features include:

- **Sentry monitoring**: Real-time security monitoring and threat detection
- **Sandbox execution**: External plugins run in secure sandboxes
- **Audit logging**: Complete audit trail of all system activities
- **Access controls**: Granular permissions for different system components
- **Emergency protocols**: Kill switches and emergency shutdown procedures
- **Regular updates**: Security patches and updates delivered regularly

### Can I use Hearthlink in a corporate environment?

Yes, Hearthlink is designed for enterprise use:

- **Air-gapped deployment**: Can run completely disconnected from the internet
- **Compliance support**: Built-in auditing and logging for regulatory requirements
- **Data sovereignty**: All data remains under your organization's control
- **Custom integrations**: API-first design for integration with existing systems
- **Security monitoring**: Comprehensive security monitoring and alerting

## Technical Questions

### What ports does Hearthlink use?

**Standard Port Configuration:**
- **8000**: Core API service
- **8001**: Local LLM API service
- **8002**: Vault API service
- **8003**: Synapse API service
- **8004**: Sentry monitoring service

These ports are configurable in the settings if conflicts occur.

### Can I change the AI models Hearthlink uses?

Yes, Hearthlink supports multiple AI backends:

**Local Models (Recommended):**
- **Ollama integration** - Popular local LLM platform
- **LM Studio** - User-friendly local model interface
- **Custom endpoints** - Connect to any OpenAI-compatible API

**Cloud Models:**
- **OpenAI API** - GPT models via API
- **Anthropic Claude** - Claude models via API
- **Custom services** - Any REST API compatible service

### How much system resources does Hearthlink use?

Resource usage depends on configuration:

**Minimal Setup** (Basic features only):
- **CPU**: 5-10% baseline
- **RAM**: 1-2GB
- **Storage**: 500MB

**Standard Setup** (3B-8B models):
- **CPU**: 15-30% during AI processing
- **RAM**: 4-8GB
- **Storage**: 2-5GB

**Advanced Setup** (13B+ models, multiple agents):
- **CPU**: 50-80% during intensive processing
- **RAM**: 12-32GB
- **Storage**: 10-50GB

### Why is my AI response slow?

Performance factors:

1. **Model size**: Larger models provide better quality but slower responses
2. **System resources**: Insufficient RAM or CPU affects performance
3. **Model loading**: First request may be slow as models load into memory
4. **Concurrent sessions**: Multiple active agents share resources
5. **Hardware acceleration**: GPU acceleration significantly improves speed

**Optimization tips:**
- Use smaller models for better speed
- Ensure adequate RAM for chosen models
- Enable GPU acceleration if available
- Limit concurrent agent sessions

## Accessibility Questions

### Is Hearthlink accessible for users with disabilities?

Yes, accessibility is a core design principle:

**Vision Accessibility:**
- **Screen reader support** - NVDA, JAWS, VoiceOver, Orca compatibility
- **High contrast mode** - Enhanced visibility options
- **Customizable fonts** - Adjustable size and family
- **Keyboard navigation** - Complete keyboard accessibility

**Hearing Accessibility:**
- **Visual feedback** - All audio has visual equivalents
- **Closed captions** - Visual display of voice commands and responses
- **Text alternatives** - Complete text-based interaction mode

**Motor Accessibility:**
- **Voice control** - Comprehensive voice command system
- **Keyboard shortcuts** - Extensive keyboard navigation
- **Switch support** - Compatible with assistive input devices
- **Adjustable timing** - Customizable interaction timeouts

### Can I use Hearthlink without a mouse?

Absolutely! Complete keyboard navigation is supported:

- **Tab navigation** - Move between all interactive elements
- **Arrow key navigation** - Navigate within components
- **Keyboard shortcuts** - Quick access to all major features
- **Voice commands** - Hands-free operation
- **Focus indicators** - Clear visual focus management

### Does Hearthlink support screen readers?

Yes, comprehensive screen reader support:

- **ARIA labels** - Descriptive labels for all elements
- **Semantic markup** - Proper HTML structure
- **Live regions** - Dynamic content announcements
- **Role announcements** - Clear element type identification
- **Focus management** - Logical reading order

## Troubleshooting

### The interface shows "Service Unavailable" errors

This typically indicates backend services aren't running:

1. **Check status lights** - Look for red indicators in the interface
2. **Restart services** - Use the "Check Service Status" button in Settings
3. **Check ports** - Ensure ports 8000-8004 aren't blocked
4. **Review logs** - Check the diagnostics panel for specific errors
5. **Restart application** - Complete restart often resolves service issues

### Voice commands aren't working

Common voice issues and solutions:

1. **Browser permissions** - Ensure microphone access is granted
2. **Supported browsers** - Use Chrome, Firefox, or Edge
3. **HTTPS requirement** - Voice API requires secure connection
4. **Microphone test** - Test microphone in Settings → Voice
5. **Network issues** - Voice recognition may require internet connection

### Settings won't save

Settings persistence issues:

1. **Service status** - Ensure settings API service (port 8001) is running
2. **File permissions** - Check write permissions in application directory
3. **Local storage** - Browser localStorage may be full or disabled
4. **Service restart** - Restart the settings API service
5. **Manual backup** - Export settings as backup before troubleshooting

### High CPU or memory usage

Performance optimization:

1. **Reduce active agents** - Fewer agents use fewer resources
2. **Smaller models** - Choose appropriate model size for your hardware
3. **Close unused sessions** - Archive old sessions to free memory
4. **Check background processes** - Other applications may compete for resources
5. **Hardware upgrade** - Consider more RAM or faster CPU for heavy usage

## Integration and Development

### Can I integrate Hearthlink with other applications?

Yes, Hearthlink provides extensive integration options:

- **REST APIs** - Full API access to all system components
- **Plugin system** - Develop custom plugins with Synapse
- **Webhook support** - Real-time event notifications
- **CLI interface** - Command-line access for automation
- **File system integration** - Direct file system access for data exchange

### How do I develop plugins for Hearthlink?

Plugin development with Synapse:

1. **Create plugin manifest** - Define plugin metadata and permissions
2. **Implement plugin logic** - Python, JavaScript, or other supported languages
3. **Test in sandbox** - Safe testing environment provided
4. **Security review** - Automated security scanning
5. **Installation** - Deploy through Synapse plugin manager

See the [Developer Guide](../docs/internal/DEVELOPER_GUIDE.md) for detailed instructions.

### Can I contribute to Hearthlink development?

Absolutely! Hearthlink is open-source:

- **GitHub repository** - Source code and issue tracking
- **Contribution guidelines** - How to submit pull requests
- **Community discussions** - Feature requests and architectural decisions
- **Documentation contributions** - Help improve user and developer docs
- **Testing and feedback** - Beta testing and bug reports

## Support and Community

### Where can I get help?

Multiple support channels available:

**Self-Service:**
- **Built-in help** - Press F1 from anywhere in the application
- **Documentation** - Comprehensive guides and references
- **FAQ** - This document for common questions
- **Troubleshooting guide** - Step-by-step problem solving

**Community Support:**
- **User forums** - Community-driven support and tips
- **Discord server** - Real-time chat with users and developers
- **GitHub discussions** - Technical discussions and feature requests
- **Reddit community** - r/Hearthlink for general discussion

**Official Support:**
- **Email support** - support@hearthlink.app for technical issues
- **Bug reports** - GitHub issue tracker for bugs and feature requests
- **Enterprise support** - Dedicated support for business users

### How can I stay updated on new features?

Stay informed about Hearthlink development:

- **Release notes** - Detailed changelog for each version
- **Developer blog** - Technical insights and roadmap updates
- **Social media** - Follow @Hearthlink for announcements
- **Newsletter** - Monthly updates on features and community
- **GitHub releases** - Automatic notifications for new versions

### Is there a user community?

Yes, active community across multiple platforms:

- **Forums** - Structured discussions and support
- **Discord** - Real-time chat and voice channels
- **Reddit** - General discussion and sharing
- **GitHub** - Technical discussions and development
- **Local meetups** - Regional user groups in major cities

---

*Don't see your question here? Check the complete documentation or ask in the community forums. We're always happy to help!*

## Quick Links

- **[User Guide](USER_GUIDE.md)** - Complete feature documentation
- **[Accessibility Guide](ACCESSIBILITY.md)** - Comprehensive accessibility features
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Detailed problem solving
- **[Quick Start Guide](QUICK_START.md)** - Get started in 5 minutes
- **GitHub Repository** - Source code and latest releases
- **Community Forums** - User support and discussions