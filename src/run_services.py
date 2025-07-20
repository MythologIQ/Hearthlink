#!/usr/bin/env python3
"""
Hearthlink Services Runner

Starts both Synapse Claude Gateway and Vault Service in parallel.
This provides the complete Phase 2 + Phase 3 infrastructure.
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from synapse.claude_gateway import create_claude_gateway
from vault.vault_service import create_vault_service


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ServiceManager:
    """Manages multiple Hearthlink services."""
    
    def __init__(self):
        self.services = {}
        self.running = False
        
    async def start_services(self):
        """Start all services."""
        logger.info("Starting Hearthlink services...")
        
        # Load configuration from environment
        config = self._load_config()
        
        try:
            # Create services
            claude_gateway = create_claude_gateway(config.get('claude_gateway', {}))
            vault_service = create_vault_service(config.get('vault_service', {}))
            
            # Start services in parallel
            self.running = True
            
            tasks = [
                asyncio.create_task(self._run_service(
                    "Claude Gateway", 
                    claude_gateway.run, 
                    "0.0.0.0", 
                    8080
                )),
                asyncio.create_task(self._run_service(
                    "Vault Service", 
                    vault_service.run, 
                    "0.0.0.0", 
                    8081
                ))
            ]
            
            # Wait for services to start
            await asyncio.sleep(2)
            logger.info("All services started successfully")
            
            # Keep running until shutdown
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
        except Exception as e:
            logger.error(f"Service startup failed: {e}")
        finally:
            self.running = False
            logger.info("All services stopped")
    
    async def _run_service(self, name: str, run_func, host: str, port: int):
        """Run a single service."""
        try:
            logger.info(f"Starting {name} on {host}:{port}")
            await asyncio.get_event_loop().run_in_executor(
                None, run_func, host, port
            )
        except Exception as e:
            logger.error(f"{name} failed: {e}")
            raise
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {
            'claude_gateway': {
                'claude_api_key': os.getenv('CLAUDE_API_KEY'),
                'claude_base_url': os.getenv('CLAUDE_BASE_URL', 'https://api.anthropic.com'),
                'vault_auth_token': os.getenv('VAULT_AUTH_TOKEN'),
                'vault_base_url': os.getenv('VAULT_BASE_URL', 'http://localhost:8081'),
                'allowed_origins': os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
            },
            'vault_service': {
                'vault_root': os.getenv('VAULT_ROOT', './vault_data'),
                'auth_tokens': os.getenv('VAULT_AUTH_TOKENS', '').split(',') if os.getenv('VAULT_AUTH_TOKENS') else [],
                'allowed_origins': os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
            }
        }
        
        # Generate default tokens if none provided
        if not config['vault_service']['auth_tokens'] or config['vault_service']['auth_tokens'] == ['']:
            import secrets
            default_token = secrets.token_urlsafe(32)
            config['vault_service']['auth_tokens'] = [default_token]
            config['claude_gateway']['vault_auth_token'] = default_token
            
            logger.warning(f"Generated default vault token: {default_token}")
            logger.warning("Set VAULT_AUTH_TOKENS environment variable for production use")
        
        # Ensure Claude API key is set
        if not config['claude_gateway']['claude_api_key']:
            logger.error("CLAUDE_API_KEY environment variable is required")
            sys.exit(1)
        
        return config
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.running = False
            # Create new event loop for shutdown if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Cancel all tasks
            for task in asyncio.all_tasks(loop):
                task.cancel()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main entry point."""
    service_manager = ServiceManager()
    service_manager.setup_signal_handlers()
    
    try:
        await service_manager.start_services()
    except KeyboardInterrupt:
        logger.info("Shutdown complete")


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    # Check required environment variables
    required_env = ['CLAUDE_API_KEY']
    missing_env = [var for var in required_env if not os.getenv(var)]
    
    if missing_env:
        logger.error(f"Missing required environment variables: {', '.join(missing_env)}")
        logger.info("Example setup:")
        logger.info("  export CLAUDE_API_KEY='your-claude-api-key'")
        logger.info("  export VAULT_AUTH_TOKENS='your-vault-token'")
        sys.exit(1)
    
    # Print startup banner
    print("=" * 60)
    print("🚀 HEARTHLINK SERVICES STARTING")
    print("=" * 60)
    print("Services:")
    print("  • Claude Gateway:  http://localhost:8080")
    print("  • Vault Service:   http://localhost:8081")
    print("=" * 60)
    print()
    
    # Run services
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Services stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)