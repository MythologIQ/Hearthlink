#!/bin/bash

# Test Integration UI Launcher
echo "🚀 Starting Hearthlink IPC Integration Test..."

# Set environment variables
export HEARTHLINK_VAULT_KEY="yFLl9T3j6l_rsrgSIHMDqr5O_vt62MdpkJuhIEuilAM="
export PYTHON_PATH=python3

# Launch the test Electron app
echo "📱 Launching Electron test app..."
electron test_electron_ipc.js