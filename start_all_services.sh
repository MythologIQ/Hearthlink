#!/bin/bash
# Hearthlink All Services Startup Script

echo "=============================================="
echo "HEARTHLINK SERVICES STARTUP"
echo "=============================================="

# Kill any existing services
echo "Stopping existing services..."
pkill -f "simple_backend.py"
pkill -f "npm.*start"

# Start backend service
echo "Starting backend service..."
cd /mnt/g/mythologiq/hearthlink
python3 src/api/simple_backend.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Test backend connection
echo "Testing backend connection..."
if curl -s http://localhost:8003/api/status > /dev/null; then
    echo "✓ Backend service started successfully"
else
    echo "✗ Backend service failed to start"
    exit 1
fi

# Start React development server
echo "Starting React development server..."
npm start &
REACT_PID=$!

echo ""
echo "=============================================="
echo "SERVICES STATUS"
echo "=============================================="
echo "Backend API: http://localhost:8003"
echo "React App: http://localhost:3000"
echo "Ollama: http://localhost:11434"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "React PID: $REACT_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo "=============================================="

# Wait for user interrupt
trap 'echo "Stopping services..."; kill $BACKEND_PID $REACT_PID; exit 0' INT
wait