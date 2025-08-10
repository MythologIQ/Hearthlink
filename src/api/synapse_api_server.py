#!/usr/bin/env python3
"""
Synapse API Server

FastAPI-based REST API server for Synapse plugin gateway module.
Provides standalone HTTP endpoints for plugin management and external integrations.

Usage:
    python src/api/synapse_api_server.py --host 127.0.0.1 --port 8002

References:
    - src/synapse/api.py: API endpoint implementations
    - src/synapse/synapse.py: Synapse orchestration logic

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    # Import Synapse module components
    from synapse.api import app, initialize_synapse
    from synapse.synapse import SynapseConfig
    
except ImportError as e:
    print(f"Required dependencies not installed: {e}")
    print("Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/synapse_api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    try:
        # Load configuration if available
        config_path = Path("config/synapse_config.json")
        config = None
        if config_path.exists():
            import json
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                config = SynapseConfig(**config_data)
        
        # Initialize Synapse with configuration
        initialize_synapse(config)
        
        # Add additional health check endpoint
        @app.get("/health")
        async def health_check():
            """Health check endpoint for service monitoring."""
            return {
                "status": "healthy", 
                "service": "synapse-api",
                "version": "1.0.0",
                "timestamp": None  # Would need timestamp utility
            }
        
        logger.info("Synapse API application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Synapse API application: {e}")
        raise

def main():
    """Main entry point for Synapse API server."""
    parser = argparse.ArgumentParser(description="Synapse API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8002, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    try:
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create FastAPI app
        synapse_app = create_app()
        
        logger.info(f"Starting Synapse API server on {args.host}:{args.port}")
        
        # Run server
        uvicorn.run(
            synapse_app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Synapse API server stopped by user")
    except Exception as e:
        logger.error(f"Synapse API server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()