#!/bin/bash

# Test script for Hearthlink port management functionality
# This script demonstrates the enhanced port conflict resolution

echo "🧪 Testing Hearthlink Port Management System"
echo "=============================================="
echo

# Test 1: Check port availability
echo "1. Testing port availability check..."
./start_hearthlink.sh --check-ports
echo

# Test 2: Show help for port management
echo "2. Port management options:"
./start_hearthlink.sh --help | grep -A 10 "Port Management:"
echo

# Test 3: Simulate port conflict and demonstrate auto-resolution
echo "3. To test port conflict resolution:"
echo "   a) Start a service on port 3001: python3 -m http.server 3001"
echo "   b) Run: ./start_hearthlink.sh --auto-ports --verbose"
echo "   c) Hearthlink will automatically find alternative ports"
echo

# Test 4: Demonstrate cleanup functionality
echo "4. To clean up existing Hearthlink processes:"
echo "   ./start_hearthlink.sh --cleanup-ports"
echo

# Test 5: Force port resolution
echo "5. To force terminate conflicting processes:"
echo "   ./start_hearthlink.sh --force-ports --auto-ports"
echo

echo "✅ Port management system ready!"
echo "The enhanced launcher now handles:"
echo "  • Automatic port conflict detection"
echo "  • Interactive process termination"
echo "  • Alternative port discovery"
echo "  • Graceful process cleanup"
echo "  • Force termination options"
echo

echo "Common usage patterns:"
echo "  ./start_hearthlink.sh                    # Normal launch with conflict detection"
echo "  ./start_hearthlink.sh --cleanup-ports    # Clean up and launch"
echo "  ./start_hearthlink.sh --auto-ports       # Auto-resolve any conflicts"
echo "  ./start_hearthlink.sh --force-ports      # Force terminate conflicts"