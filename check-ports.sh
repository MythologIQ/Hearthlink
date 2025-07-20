#!/bin/bash

echo "🔍 Hearthlink Port Usage Check"
echo "==============================="
echo

# Function to check a single port
check_port() {
    local port=$1
    local service_name=$2
    
    echo -n "Port $port ($service_name): "
    
    # Try multiple methods to check port usage
    if command -v lsof >/dev/null 2>&1; then
        if lsof -i :$port >/dev/null 2>&1; then
            echo "🔴 IN USE"
            lsof -i :$port | grep -v COMMAND
        else
            echo "🟢 AVAILABLE"
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tuln | grep ":$port " >/dev/null; then
            echo "🔴 IN USE"
            ss -tuln | grep ":$port "
        else
            echo "🟢 AVAILABLE"
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -tuln | grep ":$port " >/dev/null; then
            echo "🔴 IN USE"
            netstat -tuln | grep ":$port "
        else
            echo "🟢 AVAILABLE"
        fi
    else
        echo "❓ CANNOT CHECK (no port checking tools available)"
    fi
    echo
}

# Check all Hearthlink ports
echo "📡 Checking Hearthlink service ports..."
echo
check_port 3000 "React Dev Server"
check_port 3001 "Static Asset Server"
check_port 3008 "Alternative Static Server"
check_port 8000 "Core API"
check_port 8001 "LLM API"
check_port 8002 "Vault API"
check_port 8003 "Synapse API"
check_port 8004 "Sentry API"

echo "🔍 Checking for Hearthlink processes..."
echo
ps aux | grep -E "(hearthlink|react-scripts|concurrently)" | grep -v grep || echo "No Hearthlink processes found"

echo
echo "✅ Port check complete!"
echo
echo "💡 If ports are in use:"
echo "   Run: ./fix-port-conflict.sh"
echo "   Then: npm start"