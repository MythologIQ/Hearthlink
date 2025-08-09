#!/usr/bin/env python3
"""
Synapse API Server
Runs the FastAPI Synapse API server
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to import synapse modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from synapse.api import app, initialize_synapse

if __name__ == "__main__":
    print("Starting Hearthlink Synapse API...")
    print("Endpoints available:")
    print("  GET  /api/synapse/health - Health check")
    print("  POST /api/synapse/plugin/register - Register plugin")
    print("  POST /api/synapse/plugin/{plugin_id}/approve - Approve plugin")
    print("  POST /api/synapse/plugin/{plugin_id}/execute - Execute plugin")
    print("  GET  /api/synapse/plugin/{plugin_id}/status - Get plugin status")
    print("  GET  /api/synapse/plugins - List plugins")
    print("  POST /api/synapse/plugin/{plugin_id}/permissions/request - Request permissions")
    print("  POST /api/synapse/permissions/{request_id}/approve - Approve permissions")
    print("  GET  /api/synapse/permissions/pending - Get pending permissions")
    print("  POST /api/synapse/connection/request - Request connection")
    print("  POST /api/synapse/connection/{connection_id}/approve - Approve connection")
    print("  GET  /api/synapse/traffic/logs - Get traffic logs")
    print("  GET  /api/synapse/traffic/summary - Get traffic summary")
    print("  GET  /api/synapse/system/status - Get system status")
    print("\\nInitializing Synapse...")
    
    # Initialize Synapse before starting the server
    initialize_synapse()
    
    print("\\nStarting server on port 8003...")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")
    except KeyboardInterrupt:
        print("\\nShutting down Synapse API...")