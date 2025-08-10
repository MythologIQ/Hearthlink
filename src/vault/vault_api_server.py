#!/usr/bin/env python3
"""
Vault API Server

FastAPI-based REST API server for Vault memory management module.
Provides standalone HTTP endpoints for secure memory storage and retrieval.

Usage:
    python src/vault/vault_api_server.py --host 127.0.0.1 --port 8001

References:
    - src/vault/vault.py: Vault storage implementation
    - src/vault/schema.py: Data schemas

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Depends, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    
    # Import Vault module components
    from vault.vault import Vault, VaultError
    
except ImportError as e:
    print(f"Required dependencies not installed: {e}")
    print("Install with: pip install fastapi uvicorn cryptography")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/vault_api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class PersonaMemoryRequest(BaseModel):
    """Request model for persona memory operations."""
    memory_data: Dict[str, Any] = Field(..., description="Memory data to store")

class CommunalMemoryRequest(BaseModel):
    """Request model for communal memory operations."""
    memory_data: Dict[str, Any] = Field(..., description="Memory data to store")

class ImportDataRequest(BaseModel):
    """Request model for data import."""
    import_data: str = Field(..., description="JSON data to import")

class VaultResponse(BaseModel):
    """Standard Vault API response."""
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message") 
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="Hearthlink Vault API",
        description="API for secure memory storage and management",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    try:
        # Load configuration
        config_path = Path("config/vault_config.json")
        config = {
            "encryption": {
                "key_env_var": "HEARTHLINK_VAULT_KEY",
                "key_file": "hearthlink_data/vault_key"
            },
            "storage": {
                "file_path": "hearthlink_data/vault_storage"
            },
            "schema_version": "1.0.0"
        }
        
        if config_path.exists():
            import json
            with open(config_path, 'r') as f:
                config.update(json.load(f))
        
        # Create Vault instance
        vault = Vault(config, logger)
        
        def get_vault() -> Vault:
            """Dependency to get Vault instance."""
            return vault
        
        def get_user_id(request: Request) -> str:
            """Extract user ID from request."""
            # TODO: Implement proper authentication
            return request.headers.get("X-User-ID", "default-user")
        
        # Persona Memory Endpoints
        @app.post("/api/vault/persona/{persona_id}", response_model=VaultResponse)
        async def create_or_update_persona(
            persona_id: str,
            request: PersonaMemoryRequest,
            user_id: str = Depends(get_user_id),
            vault_instance: Vault = Depends(get_vault)
        ):
            """Create or update persona memory."""
            try:
                vault_instance.create_or_update_persona(persona_id, user_id, request.memory_data)
                return VaultResponse(
                    status="success",
                    message="Persona memory updated successfully",
                    data={"persona_id": persona_id}
                )
            except VaultError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Persona memory update error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @app.get("/api/vault/persona/{persona_id}", response_model=VaultResponse)
        async def get_persona(
            persona_id: str,
            user_id: str = Depends(get_user_id),
            vault_instance: Vault = Depends(get_vault)
        ):
            """Get persona memory."""
            try:
                memory = vault_instance.get_persona(persona_id, user_id)
                if memory:
                    return VaultResponse(
                        status="success",
                        message="Persona memory retrieved",
                        data=memory
                    )
                else:
                    raise HTTPException(status_code=404, detail="Persona memory not found")
            except VaultError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Persona memory retrieval error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @app.delete("/api/vault/persona/{persona_id}", response_model=VaultResponse)
        async def delete_persona(
            persona_id: str,
            user_id: str = Depends(get_user_id),
            vault_instance: Vault = Depends(get_vault)
        ):
            """Delete persona memory."""
            try:
                vault_instance.delete_persona(persona_id, user_id)
                return VaultResponse(
                    status="success",
                    message="Persona memory deleted successfully",
                    data={"persona_id": persona_id}
                )
            except VaultError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Persona memory deletion error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        # Communal Memory Endpoints
        @app.post("/api/vault/communal/{memory_id}", response_model=VaultResponse)
        async def create_or_update_communal(
            memory_id: str,
            request: CommunalMemoryRequest,
            user_id: str = Depends(get_user_id),
            vault_instance: Vault = Depends(get_vault)
        ):
            """Create or update communal memory."""
            try:
                vault_instance.create_or_update_communal(memory_id, request.memory_data, user_id)
                return VaultResponse(
                    status="success",
                    message="Communal memory updated successfully",
                    data={"memory_id": memory_id}
                )
            except VaultError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Communal memory update error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @app.get("/api/vault/communal/{memory_id}", response_model=VaultResponse)
        async def get_communal(
            memory_id: str,
            user_id: str = Depends(get_user_id),
            vault_instance: Vault = Depends(get_vault)
        ):
            """Get communal memory."""
            try:
                memory = vault_instance.get_communal(memory_id, user_id)
                if memory:
                    return VaultResponse(
                        status="success",
                        message="Communal memory retrieved",
                        data=memory
                    )
                else:
                    raise HTTPException(status_code=404, detail="Communal memory not found")
            except VaultError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Communal memory retrieval error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @app.delete("/api/vault/communal/{memory_id}", response_model=VaultResponse)
        async def delete_communal(
            memory_id: str,
            user_id: str = Depends(get_user_id),
            vault_instance: Vault = Depends(get_vault)
        ):
            """Delete communal memory."""
            try:
                vault_instance.delete_communal(memory_id, user_id)
                return VaultResponse(
                    status="success",
                    message="Communal memory deleted successfully",
                    data={"memory_id": memory_id}
                )
            except VaultError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Communal memory deletion error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        # Export/Import Endpoints
        @app.get("/api/vault/persona/{persona_id}/export", response_model=VaultResponse)
        async def export_persona(
            persona_id: str,
            user_id: str = Depends(get_user_id),
            vault_instance: Vault = Depends(get_vault)
        ):
            """Export persona memory."""
            try:
                export_data = vault_instance.export_persona(persona_id, user_id)
                if export_data:
                    return VaultResponse(
                        status="success",
                        message="Persona memory exported",
                        data={"export_data": export_data}
                    )
                else:
                    raise HTTPException(status_code=404, detail="Persona memory not found")
            except VaultError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Persona memory export error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @app.post("/api/vault/persona/{persona_id}/import", response_model=VaultResponse)
        async def import_persona(
            persona_id: str,
            request: ImportDataRequest,
            user_id: str = Depends(get_user_id),
            vault_instance: Vault = Depends(get_vault)
        ):
            """Import persona memory."""
            try:
                vault_instance.import_persona(persona_id, user_id, request.import_data)
                return VaultResponse(
                    status="success",
                    message="Persona memory imported successfully",
                    data={"persona_id": persona_id}
                )
            except VaultError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Persona memory import error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        # Audit Log Endpoint
        @app.get("/api/vault/audit", response_model=VaultResponse)
        async def get_audit_log(
            vault_instance: Vault = Depends(get_vault)
        ):
            """Get audit log."""
            try:
                audit_log = vault_instance.export_audit_log()
                return VaultResponse(
                    status="success",
                    message="Audit log retrieved",
                    data={"audit_log": audit_log}
                )
            except Exception as e:
                logger.error(f"Audit log retrieval error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        # Health Check Endpoint
        @app.get("/health")
        async def health_check():
            """Health check endpoint for service monitoring."""
            return {
                "status": "healthy",
                "service": "vault-api",
                "version": "1.0.0"
            }
        
        logger.info("Vault API application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create Vault API application: {e}")
        raise

def main():
    """Main entry point for Vault API server."""
    parser = argparse.ArgumentParser(description="Vault API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    try:
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Ensure hearthlink_data directory exists
        data_dir = Path("hearthlink_data")
        data_dir.mkdir(exist_ok=True)
        
        # Create FastAPI app
        app = create_app()
        
        logger.info(f"Starting Vault API server on {args.host}:{args.port}")
        
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
        logger.info("Vault API server stopped by user")
    except Exception as e:
        logger.error(f"Vault API server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()