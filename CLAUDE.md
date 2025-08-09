# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hearthlink is an advanced AI orchestration system that provides multi-agent collaboration, voice interaction capabilities, and comprehensive project management tools. It's built as a hybrid Electron/React application with Python backend services for AI functionality.

## Common Development Commands

### Development and Testing
```bash
# Install dependencies
npm install

# Start development mode (React + Electron)
npm run dev
npm run dev:enhanced

# Build application
npm run build

# Launch Electron application
npm run launch
npm start

# Start Tauri native version
npm run tauri:dev
npm run native

# Run tests
npm run test
npm run test:launcher

# Build executable
npm run build:exe
npm run build:exe-portable
npm run create-executable

# Start Alden backend service (for real AI functionality)
python start_alden_direct.py

# Performance optimization testing
python src/utils/performance_optimizer.py
python src/utils/memory_optimizer.py
```

### Python Backend Commands
```bash
# Activate virtual environment (from src/backend)
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install Python dependencies
pip install -r requirements.txt
pip install -r requirements_full.txt

# Run backend services
python src/main.py
python src/alden_backend.py
python src/run_services.py

# Run core tests
python run_core_tests.py
python run_synapse_tests.py
```

### Platform-Specific Launch Scripts
```bash
# Unix/Linux/macOS
./launch.sh
./hearthlink.sh
./start_hearthlink.sh

# Windows
launch.bat
build-and-launch.bat
hearthlink.bat
```

## Architecture Overview

### Frontend Stack
- **Framework**: React 18.2.0 + Electron 28.0.0
- **UI**: Custom MythologIQ-themed interface with Tailwind CSS
- **Routing**: React Router DOM for navigation
- **Icons**: Lucide React for UI elements
- **Build**: React Scripts with custom Electron integration

### Backend Stack
- **Runtime**: Python 3.10+ with FastAPI/Uvicorn
- **AI Integration**: Local LLM support via Ollama
- **Database**: SQLite for local data, PostgreSQL for production
- **Memory**: Redis for caching, Qdrant for vector storage
- **Knowledge Graph**: Neo4j integration planned

### Core Modules

#### 1. Core (src/core/)
**Purpose**: Central orchestration and session management
- Multi-agent conversation coordination
- Turn-taking and breakout room management
- Communal memory mediation
- Session lifecycle management
- API endpoints for session control

#### 2. Vault (src/vault/)
**Purpose**: Memory management and secure data storage
- Persona memory persistence
- Encrypted data storage
- Audit logging and compliance
- Multi-user data isolation

#### 3. Synapse (src/synapse/)
**Purpose**: Plugin management and external integrations
- Plugin execution sandbox
- External API gateway
- Security monitoring and traffic management
- Claude integration and browser preview

#### 4. Personas (src/personas/)
- **Alden**: Primary AI assistant and productivity companion
- **Alice**: Cognitive-behavioral analysis agent
- **Mimic**: Dynamic persona creation and management
- **Sentry**: Security monitoring and incident response

#### 5. Components (src/components/)
**UI Components**: React components for each module interface
- Launch page and navigation
- Module-specific interfaces (Alden, Core, Vault, etc.)
- Accessibility and help panels
- Project Command interface

## Key Configuration Files

### Package Configuration
- `package.json`: Main npm configuration with scripts and dependencies
- `package-lock.json`: Dependency lock file
- `requirements.txt`: Python dependencies (minimal)
- `requirements_full.txt`: Complete Python dependencies

### Build Configuration
- `main.js`: Electron main process entry point
- `launcher.js`: Electron launcher with asset loading
- `preload.js`: Electron preload script
- `tailwind.config.js`: Tailwind CSS configuration with MythologIQ theme

### Application Configuration
- `config/`: Module-specific configuration files
  - `alden_config.json`: Alden persona settings
  - `core_config.json`: Core orchestration settings
  - `vault_config.json`: Vault security and storage settings
  - `llm_config.json`: LLM backend configuration

## Development Guidelines

### File Organization
- **Frontend code**: `src/components/`, `src/assets/`, `public/`
- **Backend services**: `src/core/`, `src/vault/`, `src/synapse/`
- **Utilities**: `src/utils/`, `src/hooks/`
- **Configuration**: `config/`
- **Documentation**: `docs/`, `Archive/`
- **Tests**: `tests/`

### Coding Standards
- **React**: Functional components with hooks
- **Python**: Type hints and comprehensive error handling
- **Styling**: Tailwind CSS with MythologIQ theme colors
- **API**: RESTful endpoints with FastAPI
- **Logging**: Structured JSON logging for all modules

### Asset Management
- **Icons/Images**: `src/assets/` and `public/assets/`
- **Fonts**: Inter and Orbitron font families
- **Theme**: MythologIQ blue/gold color scheme
- **Protocol**: Custom `app://` protocol for secure asset serving

## Common Development Tasks

### Adding New Components
1. Create component file in `src/components/`
2. Add corresponding CSS file for styling
3. Import and integrate in `App.js`
4. Update navigation in launcher interface

### Backend Service Integration
1. Create new module in `src/` directory
2. Add API endpoints in module's `api.py`
3. Update main backend router
4. Add configuration to `config/` directory

### Plugin Development
1. Create plugin manifest following Synapse specifications
2. Implement plugin in appropriate language
3. Test in Synapse sandbox environment
4. Deploy through Synapse plugin manager

### Database Operations
1. Update schema files in `database/init/`
2. Create migration scripts if needed
3. Test with local SQLite first
4. Update Vault module for data persistence

## Testing Strategy

### Frontend Testing
- Component testing with React Testing Library
- Electron integration tests
- Asset loading validation tests
- Navigation and routing tests

### Backend Testing
- Unit tests for each module (Core, Vault, Synapse)
- API endpoint testing
- Database integration tests
- Security and permission tests

### Integration Testing
- End-to-end workflow tests
- Multi-agent session tests
- Voice interaction compliance tests
- External API integration tests

## Deployment and Distribution

### Electron Build Process
1. Build React application: `npm run build`
2. Package with Electron Builder: `npm run electron-pack`
3. Create executable: `npm run create-executable`
4. Result: `hearthlink.exe` in project root

### Production Deployment
- Docker containers for backend services
- Nginx configuration for web deployment
- Environment-specific configuration management
- Database migration and backup procedures

## Security Considerations

### Code Security
- Input validation on all API endpoints
- Secure file handling and path validation
- Encrypted storage for sensitive data
- Audit logging for all operations

### AI Safety
- Sandbox execution for external plugins
- Token usage tracking and limits
- User consent for data sharing
- Emergency kill switch functionality

### Data Privacy
- Local-first data storage approach
- User-controlled data retention policies
- GDPR compliance features
- Secure session management

## Common Issues and Solutions

### Build Issues
- Clear `node_modules` and reinstall dependencies
- Check Node.js version compatibility (18+)
- Verify Python environment setup
- Ensure all asset files are present

### Electron Asset Loading
- Verify `app://` protocol registration
- Check static server on port 3001
- Validate asset manifest and paths
- Run asset loading tests

### Backend Connection Issues
- Verify Python backend is running
- Check port availability (8000 for API)
- Validate environment variables
- Review database connections

### Performance Optimization
- Monitor memory usage in long sessions
- Implement caching for frequently accessed data (now automated via performance optimizer)
- Optimize database queries
- Use connection pooling for external services
- Run memory consolidation: `python src/utils/memory_optimizer.py`
- Enable response caching: Performance optimizer provides 20%+ cache hit rates
- Use prompt optimization for faster LLM responses

### Alden Integration Issues
- Ensure Alden backend is running on port 8888: `python start_alden_direct.py`
- Check time awareness functionality works correctly
- Verify voice interface integrates with real backend (fallback to Sprite Service)
- Confirm memory persistence is working with consolidated database

## Voice Interaction System

### Voice Routing Compliance
- Local agents: Fully conversational with name-based addressing
- External agents: Disabled by default, require explicit permission
- Misroute recovery: Alden handles all voice misroutes
- Authentication: Secure mode activation for system modifications

### Agent Management
- Multi-agent support for concurrent interactions
- Voice HUD for real-time input display
- Agent deference through three interaction styles
- Permission-based access control

This documentation should help you navigate and contribute to the Hearthlink codebase effectively. The project emphasizes user privacy, AI safety, and modular architecture throughout its design.