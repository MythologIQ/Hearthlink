#!/bin/bash

echo "🔧 Hearthlink Port Conflict Resolution Script"
echo "============================================="
echo

# Function to kill processes by pattern
kill_processes() {
    local pattern="$1"
    local description="$2"
    
    echo "🔍 Looking for $description processes..."
    pids=$(ps aux | grep -i "$pattern" | grep -v grep | awk '{print $2}')
    
    if [ -n "$pids" ]; then
        echo "📝 Found processes: $pids"
        for pid in $pids; do
            echo "🛑 Stopping process $pid..."
            kill -TERM "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null
        done
        sleep 2
        echo "✅ $description processes stopped"
    else
        echo "ℹ️  No $description processes found"
    fi
    echo
}

# Stop all Hearthlink-related processes
echo "🛑 Stopping all Hearthlink services..."
echo

kill_processes "hearthlink" "Hearthlink main"
kill_processes "react-scripts" "React development server"
kill_processes "concurrently" "Concurrently process manager"
kill_processes "npm.*start" "NPM start processes"
kill_processes "node.*start" "Node.js start processes"
kill_processes "electron" "Electron processes"

# Stop Python backend services
echo "🐍 Stopping Python backend services..."
kill_processes "simple_alden_backend" "Simple Alden backend"
kill_processes "core_api" "Core API"
kill_processes "synapse_api" "Synapse API"
kill_processes "sentry_api" "Sentry API"
kill_processes "external_agent_api" "External Agent API"
kill_processes "local_llm_api" "Local LLM API"

# Stop MCP filesystem server
echo "🔗 Stopping MCP filesystem server..."
kill_processes "mcp-server-filesystem" "MCP filesystem server"

# Check for processes using common Hearthlink ports
echo "🔍 Checking for processes using Hearthlink ports..."
for port in 3000 3001 3008 8000 8001 8002 8003 8004; do
    echo "Checking port $port..."
    # Try different methods to find processes using the port
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti :$port 2>/dev/null | xargs -r kill -9 2>/dev/null
    elif command -v fuser >/dev/null 2>&1; then
        fuser -k $port/tcp 2>/dev/null
    fi
done

echo
echo "⏳ Waiting for processes to fully terminate..."
sleep 3

echo
echo "✅ Port conflict resolution complete!"
echo
echo "🚀 You can now restart Hearthlink with:"
echo "   npm start"
echo "   or"
echo "   npm run dev"
echo
echo "🔍 To check port usage in the future:"
echo "   ./check-ports.sh"
echo