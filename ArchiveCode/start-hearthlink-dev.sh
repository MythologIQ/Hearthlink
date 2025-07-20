#!/bin/bash
# Quick development startup script for Hearthlink

echo "🚀 Starting Hearthlink Development Environment"
echo "=============================================="

# Check if we're in the right directory
if [[ ! -f "package.json" ]]; then
    echo "❌ Not in Hearthlink project directory"
    exit 1
fi

# Start Python backend if exists and not running
if [[ -f "requirements.txt" ]] && ! pgrep -f "python.*main.py" > /dev/null; then
    echo "🐍 Starting Python backend..."
    if [[ -d "venv" ]]; then
        source venv/bin/activate
    fi
    
    # Check if main Python file exists
    if [[ -f "main.py" ]]; then
        python main.py &
        BACKEND_PID=$!
        echo "Backend started with PID: $BACKEND_PID"
    elif [[ -f "src/main.py" ]]; then
        python src/main.py &
        BACKEND_PID=$!
        echo "Backend started with PID: $BACKEND_PID"
    else
        echo "⚠️ Python backend files found but no main.py located"
    fi
fi

# Start Electron app in development mode
echo "⚡ Starting Electron application..."
npm run dev &
ELECTRON_PID=$!

# Setup cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down development environment..."
    
    if [[ -n "$BACKEND_PID" ]]; then
        echo "Stopping Python backend..."
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [[ -n "$ELECTRON_PID" ]]; then
        echo "Stopping Electron app..."
        kill $ELECTRON_PID 2>/dev/null
    fi
    
    # Kill any remaining processes
    pkill -f "electron.*hearthlink" 2>/dev/null
    pkill -f "react-scripts" 2>/dev/null
    
    echo "✅ Development environment stopped"
}

# Register cleanup function
trap cleanup EXIT

echo ""
echo "✅ Hearthlink development environment running!"
echo "🌐 Electron app should open automatically"
echo "🔧 Python backend running (if configured)"
echo ""
echo "Available during development:"
echo "  ./hearthlink-claude.sh status    # Check system status"
echo "  ./hearthlink-claude.sh backend   # Integrate Python backend"
echo "  ./hearthlink-claude.sh conference # Build conference UI"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
