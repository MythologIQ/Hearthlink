#!/usr/bin/env python3
"""
Core API Server

FastAPI-based REST API server for Core orchestration module.
Provides standalone HTTP endpoints for session management and multi-agent coordination.

Usage:
    python src/api/core_api.py --host 127.0.0.1 --port 8000

References:
    - src/core/api.py: API endpoint implementations
    - src/core/core.py: Core orchestration logic

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
    
    # Import Core module components
    from core.core import Core
    from core.api import CoreAPI
    
except ImportError as e:
    print(f"Required dependencies not installed: {e}")
    print("Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/core_api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Initialize Core module
    try:
        # Load configuration if available
        config_path = Path("config/core_config.json")
        config = {}
        if config_path.exists():
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        # Create Core instance
        core = Core(config, logger)
        
        # Create Core API wrapper
        core_api = CoreAPI(core)
        app = core_api.get_app()
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            """Health check endpoint for service monitoring."""
            return {
                "status": "healthy",
                "service": "core-api",
                "version": "1.0.0",
                "timestamp": core._get_timestamp()
            }
        
        logger.info("Core API application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Core API application: {e}")
        raise

def main():
    """Main entry point for Core API server."""
    parser = argparse.ArgumentParser(description="Core API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to") 
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    try:
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create FastAPI app
        app = create_app()
        
        logger.info(f"Starting Core API server on {args.host}:{args.port}")
        
        # Run server
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("Core API server stopped by user")
    except Exception as e:
        logger.error(f"Core API server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()