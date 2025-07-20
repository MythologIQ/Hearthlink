# Hearthlink Development Operations Guide
## Source of Truth - v1.1.0

**Document Version:** 1.0.0  
**Last Updated:** July 13, 2025  
**Status:** Living Document  
**Maintained By:** DevOps Team  
**Stakeholders:** Engineering, QA, Operations, Security  

---

## 1. Introduction

### 1.1 Purpose
This guide provides comprehensive instructions for setting up development environments, building, testing, deploying, and operating Hearthlink. It serves as the definitive reference for all development and operational procedures.

### 1.2 Scope
- Development environment setup and configuration
- Build and deployment processes
- Testing strategies and automation
- Monitoring and observability
- Security and compliance operations
- Troubleshooting and maintenance procedures

### 1.3 Prerequisites
- Basic understanding of JavaScript/TypeScript, Python, and SQL
- Familiarity with Git, Docker, and command-line tools
- Understanding of desktop application development principles
- Knowledge of AI/ML concepts and local model deployment

---

## 2. Development Environment Setup

### 2.1 System Requirements

#### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.15+, or Ubuntu 20.04+
- **CPU**: Intel i5-8400 / AMD Ryzen 5 2600 or equivalent
- **RAM**: 8GB (16GB recommended for AI model development)
- **Storage**: 50GB free space (SSD recommended)
- **GPU**: Optional but recommended for AI model inference

#### Recommended Development Hardware
- **CPU**: Intel i7-10700K / AMD Ryzen 7 3700X or better
- **RAM**: 32GB for optimal AI model performance
- **Storage**: 100GB+ SSD space
- **GPU**: NVIDIA RTX 3060 or better (for local LLM inference)

### 2.2 Required Software

#### Core Development Tools
```bash
# Node.js and npm (LTS version)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python 3.10+
sudo apt-get install python3.10 python3.10-pip python3.10-venv

# Git
sudo apt-get install git

# Docker (optional, for containerized development)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

#### Platform-Specific Tools

**Windows:**
```powershell
# Install via Chocolatey
choco install nodejs python git vscode

# Windows Build Tools
npm install -g windows-build-tools
```

**macOS:**
```bash
# Install via Homebrew
brew install node python@3.10 git

# Xcode Command Line Tools
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
# Build essentials
sudo apt-get install build-essential

# Additional dependencies for Electron
sudo apt-get install libnss3-dev libatk-bridge2.0-dev libdrm2 libxkbcommon-dev libxcomposite-dev libxdamage-dev libxrandr-dev libgbm-dev libxss1 libasound2-dev
```

### 2.3 Project Setup

#### Clone Repository
```bash
git clone https://github.com/WulfForge/Hearthlink.git
cd Hearthlink

# Set up git hooks
git config core.hooksPath .githooks
chmod +x .githooks/*
```

#### Environment Configuration
```bash
# Copy environment template
cp .env.example .env.local

# Edit configuration
nano .env.local
```

#### Essential Environment Variables
```bash
# .env.local
NODE_ENV=development
REACT_APP_ALDEN_BACKEND_URL=http://localhost:8888
HEARTHLINK_DB_PATH=./hearthlink_data/hearthlink.db
HEARTHLINK_LOG_LEVEL=DEBUG
LLM_BACKEND_TYPE=ollama
LLM_MODEL_PATH=llama2:7b-chat
HEARTHLINK_ENCRYPTION_KEY=<generate_32_byte_key>
```

#### Install Dependencies
```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements_dev.txt

# Install pre-commit hooks
pre-commit install
```

### 2.4 IDE Configuration

#### Visual Studio Code (Recommended)
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.defaultInterpreterPath": "./venv/bin/python",
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "files.associations": {
    "*.md": "markdown"
  },
  "eslint.workingDirectories": ["./"],
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

#### Recommended VS Code Extensions
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-eslint",
    "ms-python.pylint",
    "ms-python.mypy-type-checker",
    "github.copilot",
    "ms-vscode.vscode-json"
  ]
}
```

### 2.5 AI Model Setup

#### Ollama Installation and Configuration
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull llama2:7b-chat
ollama pull codellama:7b
ollama pull mistral:7b

# Start Ollama service
ollama serve
```

#### Alternative: llama.cpp Setup
```bash
# Clone and build llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make

# Download and convert models
wget https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.q4_0.bin
```

#### GPU Acceleration (NVIDIA)
```bash
# Install NVIDIA drivers and CUDA
sudo apt install nvidia-driver-525
wget https://developer.download.nvidia.com/compute/cuda/12.2/local_installers/cuda_12.2.0_535.54.03_linux.run
sudo sh cuda_12.2.0_535.54.03_linux.run

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 3. Build and Development Workflow

### 3.1 Development Commands

#### Frontend Development
```bash
# Start React development server
npm run start:react

# Build React application
npm run build

# Type checking
npm run type-check

# Linting and formatting
npm run lint
npm run lint:fix
npm run format
```

#### Backend Development
```bash
# Activate Python environment
source venv/bin/activate

# Start FastAPI development server
python simple_alden_backend.py

# Run with auto-reload
uvicorn simple_alden_backend:app --reload --port 8888

# Type checking
mypy src/

# Linting and formatting
black src/
isort src/
flake8 src/
```

#### Electron Development
```bash
# Start Electron in development mode
npm run electron-dev

# Start full development environment
npm run dev

# Build Electron application
npm run electron-pack

# Create distributable packages
npm run dist
npm run dist-win
npm run dist-msi
```

### 3.2 Database Development

#### Database Initialization
```bash
# Initialize database with schema
python setup_alden_simple.py

# Run database migrations
python scripts/migrate_database.py

# Seed development data
python scripts/seed_development_data.py
```

#### Database Management
```bash
# Backup database
cp hearthlink_data/hearthlink.db hearthlink_data/backup_$(date +%Y%m%d_%H%M%S).db

# Reset database (development only)
rm hearthlink_data/hearthlink.db
python setup_alden_simple.py

# Database inspection
sqlite3 hearthlink_data/hearthlink.db
.schema
.tables
SELECT COUNT(*) FROM memory_slices;
```

### 3.3 Testing Workflow

#### Running Tests
```bash
# Frontend tests
npm test
npm run test:coverage
npm run test:watch

# Backend tests
pytest
pytest --cov=src --cov-report=html
pytest -v tests/

# End-to-end tests
npm run test:e2e

# Integration tests
npm run test:integration
```

#### Test Categories
```bash
# Unit tests only
pytest tests/unit/
npm test -- --testPathPattern=unit

# Integration tests
pytest tests/integration/
npm test -- --testPathPattern=integration

# Performance tests
pytest tests/performance/
npm run test:performance

# Security tests
pytest tests/security/
npm run test:security
```

### 3.4 Code Quality Checks

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

#### Quality Gate Checks
```bash
# Complete quality check
npm run quality-check

# This runs:
# - TypeScript compilation
# - ESLint
# - Prettier
# - Jest tests
# - Python type checking
# - Python linting
# - Security scanning
```

---

## 4. Build and Packaging

### 4.1 Production Build Process

#### Frontend Build
```bash
# Clean previous builds
npm run clean

# Build React application for production
npm run build

# Verify build
ls -la build/
du -sh build/
```

#### Backend Packaging
```bash
# Create Python package
python setup.py sdist bdist_wheel

# Create standalone executable (optional)
pip install pyinstaller
pyinstaller --onefile simple_alden_backend.py
```

#### Electron Packaging
```bash
# Build for current platform
npm run dist

# Build for specific platforms
npm run dist-win    # Windows
npm run dist-mac    # macOS
npm run dist-linux  # Linux

# Build for all platforms (requires additional setup)
npm run dist-all
```

### 4.2 Release Process

#### Version Management
```bash
# Update version numbers
npm version patch   # 1.1.0 -> 1.1.1
npm version minor   # 1.1.0 -> 1.2.0
npm version major   # 1.1.0 -> 2.0.0

# Update Python version
# Edit setup.py, __init__.py, and other version files
```

#### Release Checklist
```bash
# 1. Update version numbers
npm version patch

# 2. Update changelog
nano CHANGELOG.md

# 3. Run full test suite
npm run test:all
pytest

# 4. Build all platforms
npm run dist-all

# 5. Create release notes
# Document new features, bug fixes, breaking changes

# 6. Tag release
git tag -a v1.1.1 -m "Release version 1.1.1"
git push origin v1.1.1

# 7. Upload release artifacts
# Use GitHub Releases or internal distribution system
```

### 4.3 Continuous Integration

#### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x]
        python-version: [3.10, 3.11]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          npm ci
          pip install -r requirements.txt
          pip install -r requirements_dev.txt
      
      - name: Run tests
        run: |
          npm test -- --coverage --watchAll=false
          pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  build:
    needs: test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build application
        run: npm run dist
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: hearthlink-${{ matrix.os }}
          path: dist/
```

### 4.4 Docker Development

#### Development Docker Setup
```dockerfile
# Dockerfile.dev
FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache python3 py3-pip make g++

# Copy package files
COPY package*.json ./
COPY requirements*.txt ./

# Install dependencies
RUN npm ci
RUN pip3 install -r requirements.txt

# Copy source code
COPY . .

# Expose ports
EXPOSE 3000 8888

# Start development servers
CMD ["npm", "run", "dev"]
```

#### Docker Compose for Development
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  hearthlink-dev:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
      - "8888:8888"
    volumes:
      - .:/app
      - /app/node_modules
      - /app/venv
    environment:
      - NODE_ENV=development
      - HEARTHLINK_DB_PATH=/app/data/hearthlink.db
    command: npm run dev

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    
volumes:
  ollama_data:
```

#### Development with Docker
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Run commands in container
docker-compose exec hearthlink-dev npm test
docker-compose exec hearthlink-dev python -m pytest

# Stop and clean up
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml down -v  # Remove volumes
```

---

## 5. Testing and Quality Assurance

### 5.1 Testing Strategy

#### Test Pyramid
```
                E2E Tests (5%)
           ┌─────────────────────┐
           │   User Journeys     │
           │   Full Integration  │
           └─────────────────────┘
           
         Integration Tests (25%)
      ┌─────────────────────────────┐
      │    API Integration          │
      │    Component Integration    │
      │    Database Tests           │
      └─────────────────────────────┘
      
      Unit Tests (70%)
   ┌─────────────────────────────────┐
   │     Pure Functions              │
   │     Component Logic             │
   │     Service Classes             │
   └─────────────────────────────────┘
```

#### Frontend Testing
```typescript
// Example component test
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AldenEnhancedInterface from '../AldenEnhancedInterface';

describe('AldenEnhancedInterface', () => {
  const mockProps = {
    accessibilitySettings: {
      voiceFeedback: true,
      highContrast: false
    },
    onVoiceCommand: jest.fn()
  };

  test('renders and handles user input', async () => {
    const user = userEvent.setup();
    
    render(<AldenEnhancedInterface {...mockProps} />);
    
    const input = screen.getByPlaceholderText(/ask me anything/i);
    const sendButton = screen.getByRole('button', { name: /transmit/i });
    
    await user.type(input, 'Hello Alden');
    await user.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/hello/i)).toBeInTheDocument();
    });
  });
});
```

#### Backend Testing
```python
# Example API test
import pytest
from fastapi.testclient import TestClient
from simple_alden_backend import app

@pytest.fixture
def client():
    return TestClient(app)

def test_agent_query(client):
    response = client.post('/api/agents/alden/query', json={
        'query': 'Hello',
        'session_id': 'test_session',
        'user_id': 'test_user'
    })
    
    assert response.status_code == 200
    data = response.json()
    assert 'response' in data
    assert 'confidence' in data
    assert data['confidence'] > 0

def test_memory_creation(client):
    response = client.post('/api/memory/alden', json={
        'user_id': 'test_user',
        'slice_type': 'episodic',
        'content': 'Test memory',
        'importance': 0.8
    })
    
    assert response.status_code == 201
    assert 'memory' in response.json()['data']
```

### 5.2 Automated Testing

#### Test Configuration
```json
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapping: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/serviceWorker.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

#### Python Test Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --cov=src
    --cov-branch
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

### 5.3 Performance Testing

#### Frontend Performance
```typescript
// Performance testing with Lighthouse
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';

describe('Performance Tests', () => {
  test('Lighthouse performance audit', async () => {
    const chrome = await chromeLauncher.launch({chromeFlags: ['--headless']});
    const options = {logLevel: 'info', output: 'json', port: chrome.port};
    
    const runnerResult = await lighthouse('http://localhost:3000', options);
    
    const performanceScore = runnerResult.lhr.categories.performance.score * 100;
    expect(performanceScore).toBeGreaterThan(80);
    
    await chrome.kill();
  });
});
```

#### Load Testing
```python
# Locust load testing
from locust import HttpUser, task, between

class HearthlinkUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Setup user session
        response = self.client.post('/api/auth/session', json={
            'user_id': f'user_{self.environment.runner.user_count}'
        })
        self.session_token = response.json()['data']['session_token']
        self.client.headers.update({
            'Authorization': f'Bearer {self.session_token}'
        })
    
    @task(3)
    def query_agent(self):
        self.client.post('/api/agents/alden/query', json={
            'query': 'What should I focus on today?',
            'session_id': 'load_test_session',
            'user_id': f'user_{self.environment.runner.user_count}'
        })
    
    @task(1)
    def search_memories(self):
        self.client.post('/api/memory/alden/search', json={
            'query': 'productivity tips',
            'user_id': f'user_{self.environment.runner.user_count}'
        })
```

---

## 6. Deployment and Operations

### 6.1 Production Deployment

#### Desktop Application Distribution

**Windows Distribution:**
```bash
# Build Windows installer
npm run dist-win

# Sign the executable (requires code signing certificate)
signtool sign /f certificate.p12 /p password /t http://timestamp.digicert.com dist/HearthlinkSetup-v1.1.0.msi

# Upload to distribution platform
# - GitHub Releases
# - Microsoft Store
# - Internal distribution server
```

**macOS Distribution:**
```bash
# Build macOS application
npm run dist-mac

# Sign and notarize (requires Apple Developer account)
codesign --force --verify --verbose --sign "Developer ID Application: Your Name" dist/Hearthlink.app
xcrun notarytool submit dist/Hearthlink.dmg --keychain-profile "notarytool-profile" --wait

# Upload to distribution platform
# - GitHub Releases  
# - Mac App Store
# - Direct download
```

**Linux Distribution:**
```bash
# Build Linux packages
npm run dist-linux

# Create AppImage
npm run dist-linux-appimage

# Create Snap package
snapcraft

# Upload to distribution platforms
# - GitHub Releases
# - Snap Store
# - Flatpak
# - Package repositories
```

#### Backend Service Deployment

For server-side deployments (future enterprise features):

```dockerfile
# Dockerfile.prod
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY simple_alden_backend.py .

# Create non-root user
RUN useradd --create-home --shell /bin/bash hearthlink
USER hearthlink

# Expose port
EXPOSE 8888

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8888/api/status || exit 1

# Start application
CMD ["python", "simple_alden_backend.py"]
```

### 6.2 Configuration Management

#### Production Configuration
```bash
# Production environment variables
export NODE_ENV=production
export HEARTHLINK_LOG_LEVEL=INFO
export HEARTHLINK_DB_PATH=/opt/hearthlink/data/hearthlink.db
export LLM_BACKEND_TYPE=ollama
export HEARTHLINK_ENCRYPTION_KEY=$(cat /opt/hearthlink/secrets/encryption.key)
```

#### Configuration Validation
```python
# config_validator.py
import os
import sys
from pathlib import Path

def validate_production_config():
    """Validate production configuration"""
    required_vars = [
        'HEARTHLINK_DB_PATH',
        'HEARTHLINK_ENCRYPTION_KEY',
        'LLM_BACKEND_TYPE'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Validate database path is writable
    db_path = Path(os.getenv('HEARTHLINK_DB_PATH'))
    if not db_path.parent.exists():
        print(f"Database directory does not exist: {db_path.parent}")
        sys.exit(1)
    
    # Validate encryption key length
    encryption_key = os.getenv('HEARTHLINK_ENCRYPTION_KEY')
    if len(encryption_key) < 32:
        print("Encryption key must be at least 32 characters")
        sys.exit(1)
    
    print("Configuration validation passed")

if __name__ == "__main__":
    validate_production_config()
```

### 6.3 Monitoring and Observability

#### Application Metrics
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import functools

# Define metrics
REQUEST_COUNT = Counter('hearthlink_requests_total', 
                       'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('hearthlink_request_duration_seconds',
                            'HTTP request duration')
ACTIVE_SESSIONS = Gauge('hearthlink_active_sessions',
                       'Number of active user sessions')
MEMORY_COUNT = Gauge('hearthlink_memory_slices_total',
                    'Total number of memory slices')

def track_requests(func):
    """Decorator to track request metrics"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(method='POST', endpoint=func.__name__).inc()
            return result
        finally:
            REQUEST_DURATION.observe(time.time() - start_time)
    return wrapper

# Start metrics server
def start_metrics_server(port=8000):
    start_http_server(port)
    print(f"Metrics server started on port {port}")
```

#### Health Checks
```python
# health_check.py
from fastapi import FastAPI, HTTPException
import sqlite3
import time
import psutil

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    checks = {
        'database': check_database(),
        'memory_usage': check_memory_usage(),
        'disk_space': check_disk_space(),
        'llm_backend': check_llm_backend()
    }
    
    all_healthy = all(check['status'] == 'healthy' for check in checks.values())
    
    return {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'timestamp': time.time(),
        'checks': checks
    }

def check_database():
    """Check database connectivity"""
    try:
        conn = sqlite3.connect('hearthlink_data/hearthlink.db')
        conn.execute('SELECT 1')
        conn.close()
        return {'status': 'healthy', 'message': 'Database accessible'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'Database error: {str(e)}'}

def check_memory_usage():
    """Check system memory usage"""
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        return {'status': 'warning', 'message': f'High memory usage: {memory.percent}%'}
    return {'status': 'healthy', 'message': f'Memory usage: {memory.percent}%'}

def check_disk_space():
    """Check available disk space"""
    disk = psutil.disk_usage('/')
    if disk.percent > 85:
        return {'status': 'warning', 'message': f'Low disk space: {disk.percent}% used'}
    return {'status': 'healthy', 'message': f'Disk usage: {disk.percent}%'}

def check_llm_backend():
    """Check LLM backend availability"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            return {'status': 'healthy', 'message': 'LLM backend accessible'}
        else:
            return {'status': 'unhealthy', 'message': 'LLM backend not responding'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': f'LLM backend error: {str(e)}'}
```

#### Logging Configuration
```python
# logging_config.py
import logging
import sys
from pathlib import Path

def setup_logging(log_level='INFO', log_file=None):
    """Configure application logging"""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Specific logger configurations
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    
    return root_logger
```

---

## 7. Security Operations

### 7.1 Security Scanning

#### Code Security Scanning
```bash
# Install security scanning tools
npm install -g audit-ci
pip install safety bandit

# Frontend security scan
npm audit
audit-ci --moderate

# Python security scan
safety check
bandit -r src/

# Dependency vulnerability scan
npm run security-check
```

#### Container Security Scanning
```bash
# Scan Docker images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/src anchore/grype:latest \
  hearthlink:latest

# Trivy security scanner
trivy image hearthlink:latest
```

### 7.2 Secrets Management

#### Development Secrets
```bash
# Generate encryption keys
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Store in environment or secure file
echo "HEARTHLINK_ENCRYPTION_KEY=gAAAAABh..." >> .env.local

# Never commit secrets to version control
echo ".env.local" >> .gitignore
```

#### Production Secrets Management
```bash
# Use environment variables or external secret management
export HEARTHLINK_ENCRYPTION_KEY=$(cat /etc/secrets/encryption.key)

# Or use secret management services
# - AWS Secrets Manager
# - Azure Key Vault
# - HashiCorp Vault
# - Kubernetes Secrets
```

### 7.3 Security Monitoring

#### Security Event Logging
```python
# security_logger.py
import logging
import json
from datetime import datetime

security_logger = logging.getLogger('security')

def log_security_event(event_type, user_id, details, severity='INFO'):
    """Log security-related events"""
    event = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'severity': severity,
        'details': details
    }
    
    security_logger.log(
        getattr(logging, severity),
        json.dumps(event)
    )

# Usage examples
log_security_event('authentication_success', 'user_123', {'method': 'session_token'})
log_security_event('unauthorized_access_attempt', 'unknown', {'endpoint': '/api/admin'}, 'WARNING')
log_security_event('memory_access', 'user_123', {'agent_id': 'alden', 'memory_count': 5})
```

---

## 8. Backup and Recovery

### 8.1 Data Backup Strategy

#### Automated Backup Script
```bash
#!/bin/bash
# backup.sh - Automated backup script

BACKUP_DIR="/opt/hearthlink/backups"
DB_PATH="/opt/hearthlink/data/hearthlink.db"
CONFIG_DIR="/opt/hearthlink/config"
DATE=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p "$BACKUP_DIR/$DATE"

# Backup database
cp "$DB_PATH" "$BACKUP_DIR/$DATE/hearthlink_$DATE.db"

# Backup configuration
tar -czf "$BACKUP_DIR/$DATE/config_$DATE.tar.gz" -C "$CONFIG_DIR" .

# Backup logs (last 7 days)
find /opt/hearthlink/logs -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/$DATE/" \;

# Compress backup
tar -czf "$BACKUP_DIR/hearthlink_backup_$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"
rm -rf "$BACKUP_DIR/$DATE"

# Clean old backups (keep last 30 days)
find "$BACKUP_DIR" -name "hearthlink_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/hearthlink_backup_$DATE.tar.gz"
```

#### Database Backup with SQLite
```python
# database_backup.py
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

def backup_database(source_db, backup_dir):
    """Create a backup of the SQLite database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(backup_dir) / f"hearthlink_backup_{timestamp}.db"
    
    # Ensure backup directory exists
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create backup using SQLite backup API
    source_conn = sqlite3.connect(source_db)
    backup_conn = sqlite3.connect(backup_path)
    
    source_conn.backup(backup_conn)
    
    source_conn.close()
    backup_conn.close()
    
    print(f"Database backup created: {backup_path}")
    return backup_path

def verify_backup(backup_path):
    """Verify backup integrity"""
    try:
        conn = sqlite3.connect(backup_path)
        conn.execute("PRAGMA integrity_check")
        result = conn.fetchone()
        conn.close()
        
        if result[0] == "ok":
            print(f"Backup verification successful: {backup_path}")
            return True
        else:
            print(f"Backup verification failed: {backup_path}")
            return False
    except Exception as e:
        print(f"Backup verification error: {e}")
        return False
```

### 8.2 Disaster Recovery

#### Recovery Procedures
```bash
#!/bin/bash
# restore.sh - Disaster recovery script

BACKUP_FILE="$1"
RESTORE_DIR="/opt/hearthlink"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

# Stop Hearthlink services
systemctl stop hearthlink

# Create restoration point
cp -r "$RESTORE_DIR" "$RESTORE_DIR.pre-restore.$(date +%Y%m%d_%H%M%S)"

# Extract backup
tar -xzf "$BACKUP_FILE" -C /tmp/
BACKUP_TIMESTAMP=$(basename "$BACKUP_FILE" .tar.gz | sed 's/hearthlink_backup_//')

# Restore database
cp "/tmp/hearthlink_$BACKUP_TIMESTAMP.db" "$RESTORE_DIR/data/hearthlink.db"

# Restore configuration
tar -xzf "/tmp/config_$BACKUP_TIMESTAMP.tar.gz" -C "$RESTORE_DIR/config/"

# Set permissions
chown -R hearthlink:hearthlink "$RESTORE_DIR"
chmod 600 "$RESTORE_DIR/data/hearthlink.db"

# Verify restoration
python /opt/hearthlink/scripts/verify_installation.py

# Start services
systemctl start hearthlink

echo "Restoration completed from $BACKUP_FILE"
```

---

## 9. Troubleshooting Guide

### 9.1 Common Issues

#### Frontend Issues

**Issue: React application won't start**
```bash
# Symptoms
npm start fails with dependency errors

# Diagnosis
npm ls  # Check for dependency conflicts
npm audit  # Check for vulnerabilities

# Solutions
rm -rf node_modules package-lock.json
npm install  # Reinstall dependencies
npm run build  # Test build process
```

**Issue: Electron app crashes on startup**
```bash
# Diagnosis
# Check main process logs in terminal
# Check renderer process logs in DevTools

# Solutions
# 1. Clear Electron cache
rm -rf ~/Library/Application\ Support/Hearthlink  # macOS
rm -rf ~/.config/Hearthlink  # Linux
rm -rf %APPDATA%\Hearthlink  # Windows

# 2. Rebuild native modules
npm run electron-rebuild

# 3. Check for conflicting processes
lsof -i :3000  # Check if port is in use
```

#### Backend Issues

**Issue: FastAPI server won't start**
```bash
# Symptoms
uvicorn fails to start, port binding errors

# Diagnosis
python simple_alden_backend.py --log-level debug
netstat -tulpn | grep 8888  # Check port usage

# Solutions
# 1. Kill existing processes
lsof -ti:8888 | xargs kill -9

# 2. Change port
export HEARTHLINK_BACKEND_PORT=8889

# 3. Check Python dependencies
pip check
pip install -r requirements.txt --force-reinstall
```

**Issue: Database connection errors**
```bash
# Symptoms
SQLite database locked or corrupted

# Diagnosis
sqlite3 hearthlink_data/hearthlink.db ".schema"
sqlite3 hearthlink_data/hearthlink.db "PRAGMA integrity_check;"

# Solutions
# 1. Check file permissions
ls -la hearthlink_data/
chmod 644 hearthlink_data/hearthlink.db

# 2. Restore from backup
cp hearthlink_data/backup_20250713_100000.db hearthlink_data/hearthlink.db

# 3. Rebuild database
python setup_alden_simple.py
```

#### AI/LLM Issues

**Issue: Ollama connection failures**
```bash
# Symptoms
LLM backend unavailable, timeout errors

# Diagnosis
curl http://localhost:11434/api/tags
ollama list

# Solutions
# 1. Restart Ollama service
ollama serve

# 2. Pull required models
ollama pull llama2:7b-chat

# 3. Check system resources
nvidia-smi  # Check GPU usage
htop  # Check CPU and memory
```

### 9.2 Diagnostic Tools

#### System Diagnostics Script
```python
#!/usr/bin/env python3
# diagnose.py - System diagnostic tool

import os
import sys
import sqlite3
import requests
import psutil
from pathlib import Path

def check_system_requirements():
    """Check system requirements"""
    print("=== System Requirements ===")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 10):
        print("❌ Python 3.10+ required")
    else:
        print("✅ Python version OK")
    
    # Check memory
    memory = psutil.virtual_memory()
    memory_gb = memory.total / (1024**3)
    print(f"System memory: {memory_gb:.1f} GB")
    if memory_gb < 8:
        print("⚠️  Minimum 8GB RAM recommended")
    else:
        print("✅ Memory OK")
    
    # Check disk space
    disk = psutil.disk_usage('.')
    free_gb = disk.free / (1024**3)
    print(f"Free disk space: {free_gb:.1f} GB")
    if free_gb < 10:
        print("❌ Insufficient disk space")
    else:
        print("✅ Disk space OK")

def check_dependencies():
    """Check required dependencies"""
    print("\n=== Dependencies ===")
    
    # Check Node.js
    try:
        result = os.popen('node --version').read().strip()
        print(f"Node.js: {result}")
        print("✅ Node.js available")
    except:
        print("❌ Node.js not found")
    
    # Check npm packages
    if Path('package.json').exists():
        result = os.popen('npm ls --depth=0').read()
        if 'missing' in result:
            print("❌ Missing npm packages")
        else:
            print("✅ npm packages OK")
    
    # Check Python packages
    try:
        import fastapi, sqlite3, uvicorn
        print("✅ Python packages OK")
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")

def check_configuration():
    """Check configuration files"""
    print("\n=== Configuration ===")
    
    # Check environment variables
    required_vars = ['HEARTHLINK_DB_PATH', 'HEARTHLINK_LOG_LEVEL']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: not set")
    
    # Check database
    db_path = os.getenv('HEARTHLINK_DB_PATH', './hearthlink_data/hearthlink.db')
    if Path(db_path).exists():
        try:
            conn = sqlite3.connect(db_path)
            conn.execute('SELECT COUNT(*) FROM agents')
            conn.close()
            print(f"✅ Database accessible: {db_path}")
        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print(f"❌ Database not found: {db_path}")

def check_services():
    """Check running services"""
    print("\n=== Services ===")
    
    # Check Ollama
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Ollama running ({len(models.get('models', []))} models)")
        else:
            print("❌ Ollama not responding")
    except:
        print("❌ Ollama not available")
    
    # Check Hearthlink backend
    try:
        response = requests.get('http://localhost:8888/api/status', timeout=5)
        if response.status_code == 200:
            print("✅ Hearthlink backend running")
        else:
            print("❌ Hearthlink backend not responding")
    except:
        print("❌ Hearthlink backend not available")

if __name__ == "__main__":
    print("Hearthlink System Diagnostics")
    print("=" * 50)
    
    check_system_requirements()
    check_dependencies()
    check_configuration()
    check_services()
    
    print("\n=== Summary ===")
    print("If any issues are marked with ❌, please resolve them before proceeding.")
    print("Issues marked with ⚠️  are warnings and may not prevent operation.")
```

### 9.3 Performance Troubleshooting

#### Performance Profiling
```python
# performance_profiler.py
import cProfile
import pstats
import time
from functools import wraps

def profile_function(func):
    """Decorator to profile function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        profiler.disable()
        
        # Print execution time
        print(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        
        # Print profiling stats
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 functions
        
        return result
    return wrapper

# Usage
@profile_function
def slow_memory_search(query):
    # Your function implementation
    pass
```

#### Memory Usage Monitoring
```python
# memory_monitor.py
import psutil
import matplotlib.pyplot as plt
from collections import deque
import time
import threading

class MemoryMonitor:
    def __init__(self, duration=300):  # 5 minutes
        self.duration = duration
        self.memory_usage = deque(maxlen=duration)
        self.timestamps = deque(maxlen=duration)
        self.running = False
    
    def start_monitoring(self):
        """Start memory monitoring thread"""
        self.running = True
        thread = threading.Thread(target=self._monitor)
        thread.daemon = True
        thread.start()
    
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.running = False
    
    def _monitor(self):
        """Monitor memory usage"""
        while self.running:
            memory = psutil.virtual_memory()
            self.memory_usage.append(memory.percent)
            self.timestamps.append(time.time())
            time.sleep(1)
    
    def plot_usage(self):
        """Plot memory usage over time"""
        plt.figure(figsize=(12, 6))
        plt.plot(list(self.timestamps), list(self.memory_usage))
        plt.title('Memory Usage Over Time')
        plt.xlabel('Time')
        plt.ylabel('Memory Usage (%)')
        plt.grid(True)
        plt.show()

# Usage
monitor = MemoryMonitor()
monitor.start_monitoring()
# ... run your application ...
monitor.plot_usage()
```

---

## 10. Maintenance and Updates

### 10.1 Regular Maintenance Tasks

#### Daily Maintenance
```bash
#!/bin/bash
# daily_maintenance.sh

echo "Starting daily maintenance..."

# Check disk space
df -h | grep -E "/$|/opt/hearthlink"

# Check log file sizes
find /opt/hearthlink/logs -name "*.log" -size +100M -exec ls -lh {} \;

# Rotate logs if needed
logrotate /etc/logrotate.d/hearthlink

# Check system health
curl -f http://localhost:8888/api/status || echo "Backend health check failed"

# Database maintenance
python /opt/hearthlink/scripts/database_maintenance.py

echo "Daily maintenance completed"
```

#### Weekly Maintenance
```bash
#!/bin/bash
# weekly_maintenance.sh

echo "Starting weekly maintenance..."

# Full system backup
/opt/hearthlink/scripts/backup.sh

# Database optimization
sqlite3 /opt/hearthlink/data/hearthlink.db "VACUUM;"
sqlite3 /opt/hearthlink/data/hearthlink.db "ANALYZE;"

# Update AI models (if configured)
ollama pull llama2:7b-chat

# Check for security updates
npm audit
safety check

# Performance metrics review
python /opt/hearthlink/scripts/performance_report.py

echo "Weekly maintenance completed"
```

#### Monthly Maintenance
```bash
#!/bin/bash
# monthly_maintenance.sh

echo "Starting monthly maintenance..."

# Deep database analysis
python /opt/hearthlink/scripts/database_analysis.py

# Archive old logs
find /opt/hearthlink/logs -name "*.log" -mtime +30 -exec gzip {} \;
find /opt/hearthlink/logs -name "*.gz" -mtime +90 -delete

# Security audit
bandit -r /opt/hearthlink/src/
npm audit --audit-level=moderate

# System performance review
python /opt/hearthlink/scripts/monthly_performance_report.py

# Update documentation
git pull origin main

echo "Monthly maintenance completed"
```

### 10.2 Update Procedures

#### Application Updates
```bash
#!/bin/bash
# update_application.sh

VERSION="$1"
if [ -z "$VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

echo "Updating Hearthlink to version $VERSION..."

# Create backup before update
/opt/hearthlink/scripts/backup.sh

# Stop services
systemctl stop hearthlink

# Download and verify update
wget "https://releases.hearthlink.com/v$VERSION/hearthlink-$VERSION.tar.gz"
wget "https://releases.hearthlink.com/v$VERSION/hearthlink-$VERSION.tar.gz.sha256"

# Verify checksum
sha256sum -c "hearthlink-$VERSION.tar.gz.sha256"

# Extract update
tar -xzf "hearthlink-$VERSION.tar.gz" -C /tmp/

# Apply update
cp -r "/tmp/hearthlink-$VERSION/"* /opt/hearthlink/

# Update database schema if needed
python /opt/hearthlink/scripts/migrate_database.py

# Restart services
systemctl start hearthlink

# Verify update
curl -f http://localhost:8888/api/status

echo "Update to version $VERSION completed"
```

#### Dependency Updates
```bash
#!/bin/bash
# update_dependencies.sh

echo "Updating dependencies..."

# Update npm packages
npm update
npm audit fix

# Update Python packages
pip list --outdated
pip install -r requirements.txt --upgrade

# Update AI models
ollama list
ollama pull llama2:7b-chat

# Run tests after updates
npm test
pytest

echo "Dependencies updated successfully"
```

### 10.3 Rollback Procedures

#### Application Rollback
```bash
#!/bin/bash
# rollback_application.sh

BACKUP_FILE="$1"
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

echo "Rolling back Hearthlink from backup: $BACKUP_FILE"

# Stop services
systemctl stop hearthlink

# Create current state backup
/opt/hearthlink/scripts/backup.sh "pre-rollback"

# Restore from backup
/opt/hearthlink/scripts/restore.sh "$BACKUP_FILE"

# Verify rollback
curl -f http://localhost:8888/api/status

echo "Rollback completed"
```

---

## 11. Documentation and Knowledge Management

### 11.1 Documentation Standards

#### Code Documentation
```typescript
/**
 * Processes a user query through the specified AI agent
 * 
 * @param agentId - The ID of the agent to process the query ('alden', 'alice', etc.)
 * @param query - The user's natural language query
 * @param sessionId - The current conversation session ID
 * @param options - Additional options for query processing
 * @returns Promise resolving to the agent's response
 * 
 * @example
 * ```typescript
 * const response = await processQuery('alden', 'Help me plan my day', 'sess_123', {
 *   includeMemory: true,
 *   maxMemories: 10
 * });
 * ```
 * 
 * @throws {ValidationError} When query parameters are invalid
 * @throws {AgentNotFoundError} When the specified agent doesn't exist
 * @throws {ProcessingError} When agent processing fails
 */
export async function processQuery(
  agentId: string,
  query: string,
  sessionId: string,
  options: QueryOptions = {}
): Promise<QueryResponse> {
  // Implementation
}
```

#### API Documentation Generation
```bash
# Generate API documentation
npx typedoc --out docs/api src/
python -m pydoc-markdown -p src -o docs/api/python

# Update OpenAPI specification
python scripts/generate_openapi.py > docs/api/openapi.json

# Generate changelog
conventional-changelog -i CHANGELOG.md -s
```

### 11.2 Knowledge Base Maintenance

#### Technical Decision Log
```markdown
# Technical Decision Log

## 2025-07-13: Switch to FastAPI from Flask
**Decision**: Migrate backend from Flask to FastAPI  
**Rationale**: Better async support, automatic validation, OpenAPI integration  
**Impact**: Improved performance, better developer experience  
**Migration**: Completed in version 1.1.0  

## 2025-07-10: Implement SQLite WAL mode
**Decision**: Enable Write-Ahead Logging for SQLite  
**Rationale**: Better concurrent access, improved performance  
**Impact**: Reduced database lock contention  
**Configuration**: `PRAGMA journal_mode = WAL`  
```

#### Best Practices Documentation
```markdown
# Development Best Practices

## Code Style
- Use TypeScript for all frontend code
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Write tests for all public functions

## Git Workflow
- Use feature branches for all development
- Write clear, descriptive commit messages
- Include issue numbers in commit messages
- Squash commits before merging to main

## Performance Guidelines
- Keep bundle sizes under 2MB
- Optimize images and assets
- Use code splitting for large components
- Profile performance regularly

## Security Guidelines
- Never commit secrets to version control
- Validate all user inputs
- Use parameterized SQL queries
- Encrypt sensitive data at rest
```

---

## 12. Appendices

### Appendix A: Environment Setup Scripts

#### Complete Development Setup
```bash
#!/bin/bash
# setup_dev_environment.sh - Complete development environment setup

set -e

echo "Setting up Hearthlink development environment..."

# Check system requirements
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Please install Python 3.10+ first."
    exit 1
fi

# Clone repository if not already cloned
if [ ! -d ".git" ]; then
    echo "Cloning Hearthlink repository..."
    git clone https://github.com/WulfForge/Hearthlink.git .
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Set up Python virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements_dev.txt

# Install pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

# Set up environment variables
if [ ! -f ".env.local" ]; then
    echo "Creating environment configuration..."
    cp .env.example .env.local
    echo "Please edit .env.local with your configuration"
fi

# Initialize database
echo "Initializing database..."
python setup_alden_simple.py

# Install and set up Ollama
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

echo "Pulling AI models..."
ollama pull llama2:7b-chat

# Run initial tests
echo "Running initial tests..."
npm test -- --watchAll=false
pytest tests/

echo "Development environment setup complete!"
echo "To start development:"
echo "1. source venv/bin/activate"
echo "2. npm run dev"
```

### Appendix B: Deployment Templates

#### Docker Compose Production
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  hearthlink-backend:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "8888:8888"
    volumes:
      - hearthlink_data:/app/data
      - hearthlink_logs:/app/logs
    environment:
      - NODE_ENV=production
      - HEARTHLINK_LOG_LEVEL=INFO
      - HEARTHLINK_DB_PATH=/app/data/hearthlink.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - hearthlink-backend
    restart: unless-stopped

volumes:
  hearthlink_data:
  hearthlink_logs:
  ollama_data:
```

### Appendix C: Monitoring Configuration

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'hearthlink'
    static_configs:
      - targets: ['localhost:8888']
    metrics_path: '/metrics'
    scrape_interval: 10s
    
  - job_name: 'system'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 15s

rule_files:
  - "hearthlink_alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Hearthlink Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(hearthlink_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph", 
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(hearthlink_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

---

**Document Control**
- **Version**: 1.0.0
- **Classification**: Internal Use
- **Review Cycle**: Monthly during active development
- **Next Review**: August 13, 2025
- **Owner**: DevOps Team
- **Approvers**: Engineering Leadership, Operations Team

---

*This Development Operations Guide serves as the comprehensive reference for all development, deployment, and operational procedures for Hearthlink. All team members should follow the processes and standards defined herein to ensure consistent, reliable, and secure operations.*