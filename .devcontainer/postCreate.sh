#!/bin/bash
set -e

echo "🚀 Setting up Hearthlink development environment..."

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p hearthlink_data
mkdir -p config
mkdir -p src/api/__pycache__
mkdir -p src/core/__pycache__

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --user -r requirements.txt

# Install additional Python dev dependencies for API testing
echo "🔧 Installing additional Python development tools..."
pip install --user pytest pytest-asyncio httpx black isort

# Install Rust/Cargo dependencies and tauri-cli
echo "🦀 Installing Rust dependencies..."
cargo install tauri-cli@^2.0.0

# Verify Tauri setup
echo "✅ Verifying Tauri installation..."
cargo tauri --version

# Create basic configuration files if they don't exist
echo "⚙️ Setting up basic configuration..."

# Create basic core config if it doesn't exist
if [ ! -f "config/core_config.json" ]; then
    cat > config/core_config.json << 'EOF'
{
    "core": {
        "max_agents": 10,
        "session_timeout": 3600,
        "enable_breakout_rooms": true,
        "communal_memory": true
    },
    "api": {
        "host": "127.0.0.1",
        "port": 8000,
        "cors_origins": ["http://localhost:3005", "http://localhost:3000"],
        "enable_docs": true
    }
}
EOF
fi

# Create basic alden config if it doesn't exist
if [ ! -f "config/alden_config.json" ]; then
    cat > config/alden_config.json << 'EOF'
{
    "alden": {
        "personality": "helpful_assistant",
        "memory_enabled": true,
        "voice_enabled": false,
        "learning_mode": true
    },
    "api": {
        "host": "127.0.0.1",
        "port": 8888,
        "enable_cors": true
    }
}
EOF
fi

# Set up Python path and environment
echo "🌍 Setting up environment variables..."
export PYTHONPATH="/workspace/src:/workspace:$PYTHONPATH"

# Create a simple health check script for API testing
cat > test_api_health.py << 'EOF'
#!/usr/bin/env python3
"""Simple API health check for Codespaces verification"""
import requests
import sys
import time

def test_api_health(port=8000, max_retries=3):
    """Test if the Core API is responding"""
    url = f"http://127.0.0.1:{port}/health"
    
    for attempt in range(max_retries):
        try:
            print(f"🔍 Testing API health at {url} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ API is healthy! Response: {response.json()}")
                return True
            else:
                print(f"⚠️ API responded with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API connection failed: {e}")
            
        if attempt < max_retries - 1:
            time.sleep(2)
    
    print(f"❌ API health check failed after {max_retries} attempts")
    return False

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    success = test_api_health(port)
    sys.exit(0 if success else 1)
EOF

chmod +x test_api_health.py

# Run a quick verification
echo "🧪 Running quick verification..."
echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo "Python version: $(python3 --version)"
echo "pip version: $(pip --version)"
echo "Rust version: $(rustc --version)"
echo "Cargo version: $(cargo --version)"

# Test Python imports
echo "📋 Testing Python imports..."
python3 -c "
try:
    import fastapi, uvicorn, pydantic, requests
    print('✅ Core Python dependencies imported successfully')
except ImportError as e:
    print(f'❌ Python import error: {e}')
    exit(1)
"

echo ""
echo "🎉 Hearthlink development environment setup complete!"
echo ""
echo "🚀 Quick Start Commands:"
echo "  # Test API server:"
echo "  python -m uvicorn src.api.core_api:app --host 127.0.0.1 --port 8000 --reload"
echo ""
echo "  # Test API health (in another terminal):"
echo "  ./test_api_health.py"
echo "  # or with curl:"
echo "  curl -i http://127.0.0.1:8000/health"
echo ""
echo "  # Install frontend dependencies (if not already done):"
echo "  npm install"
echo ""
echo "  # Run React development server:"
echo "  npm run start:react"
echo ""
echo "  # Build Tauri native app:"
echo "  npm run tauri:build"
echo ""
echo "  # Run full environment validation:"
echo "  ./.devcontainer/validate_setup.py"
echo ""