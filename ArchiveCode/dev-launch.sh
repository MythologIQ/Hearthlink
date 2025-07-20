#!/bin/bash

# Hearthlink Development Launch Script
echo "================================"
echo "  HEARTHLINK DEVELOPMENT LAUNCH"
echo "================================"
echo ""

# Navigate to script directory
cd "$(dirname "$0")"

# Kill any existing processes
echo "[DEV] Killing existing processes..."
pkill -f "node.*react-scripts" 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true
echo "[DEV] Processes killed"

# Start React development server in background
echo "[DEV] Starting React development server..."
npm run start:react &
REACT_PID=$!

# Wait for React server to start
echo "[DEV] Waiting for React development server to start..."
sleep 10

# Check if React server is running
if ! pgrep -f "react-scripts" > /dev/null; then
    echo "[ERROR] React development server failed to start"
    exit 1
fi

# Set development environment
export NODE_ENV=development
export ELECTRON_IS_DEV=1

# Start Electron
echo "[DEV] Starting Electron with development server..."
echo "[DEV] This will show the actual updated UI"
echo ""
./node_modules/.bin/electron .

echo "[DEV] Electron closed"
echo ""
echo "Press any key to close React server and exit..."
read -n 1 -s

# Kill React server
echo "[DEV] Stopping React server..."
kill $REACT_PID 2>/dev/null || true
pkill -f "node.*react-scripts" 2>/dev/null || true
echo "[DEV] React server stopped"