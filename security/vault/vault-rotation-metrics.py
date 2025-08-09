#!/usr/bin/env python3
"""
Vault Key Rotation Metrics Exporter
Prometheus metrics and health monitoring for the rotation service
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
from aiohttp import web
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
vault_rotation_total = Counter('vault_key_rotations_total', 'Total number of key rotations', ['key_name', 'key_type', 'status'])
vault_rotation_duration = Histogram('vault_key_rotation_duration_seconds', 'Time taken for key rotations', ['key_name', 'key_type'])
vault_keys_managed = Gauge('vault_keys_managed_total', 'Total number of keys under management')
vault_rotation_failures = Counter('vault_key_rotation_failures_total', 'Total number of rotation failures', ['key_name', 'error_type'])
vault_service_uptime = Gauge('vault_rotation_service_uptime_seconds', 'Service uptime in seconds')
vault_next_rotation = Gauge('vault_key_next_rotation_seconds', 'Seconds until next key rotation', ['key_name', 'key_type'])
vault_compliance_violations = Counter('vault_compliance_violations_total', 'Total compliance violations', ['key_name', 'violation_type'])
vault_rollbacks = Counter('vault_key_rollbacks_total', 'Total number of key rollbacks', ['key_name', 'reason'])
vault_grace_period_active = Gauge('vault_key_grace_period_active', 'Keys currently in grace period', ['key_name'])
vault_vault_connection_status = Gauge('vault_connection_status', 'Vault connection status (1=connected, 0=disconnected)')

class VaultRotationMetrics:
    """Metrics collector and exporter for Vault rotation service"""
    
    def __init__(self, rotation_service_url: str = "http://localhost:8001"):
        self.rotation_service_url = rotation_service_url
        self.service_start_time = time.time()
        self.app = web.Application()
        self.setup_routes()
        
        # Metrics storage
        self.metrics_cache = {}
        self.last_update = None
        
    def setup_routes(self):
        """Setup HTTP routes for metrics and health"""
        self.app.router.add_get('/metrics', self.metrics_handler)
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/status', self.status_handler)
        self.app.router.add_get('/keys', self.keys_handler)
    
    async def metrics_handler(self, request):
        """Prometheus metrics endpoint"""
        try:
            # Update metrics from rotation service
            await self.update_metrics()
            
            # Update service uptime
            vault_service_uptime.set(time.time() - self.service_start_time)
            
            # Generate Prometheus metrics
            metrics_output = generate_latest()
            
            return web.Response(
                text=metrics_output.decode('utf-8'),
                content_type=CONTENT_TYPE_LATEST
            )
            
        except Exception as error:
            logger.error(f"Failed to generate metrics: {error}")
            return web.Response(
                text=f"# Error generating metrics: {error}\n",
                content_type=CONTENT_TYPE_LATEST,
                status=500
            )
    
    async def health_handler(self, request):
        """Health check endpoint"""
        try:
            # Check rotation service health
            service_health = await self.check_rotation_service_health()
            
            # Check Vault connectivity
            vault_health = await self.check_vault_health()
            
            overall_status = "healthy" if service_health and vault_health else "unhealthy"
            status_code = 200 if overall_status == "healthy" else 503
            
            health_data = {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - self.service_start_time,
                "checks": {
                    "rotation_service": "healthy" if service_health else "unhealthy",
                    "vault_connection": "healthy" if vault_health else "unhealthy"
                },
                "version": "1.0.0",
                "service": "vault-key-rotation-metrics"
            }
            
            return web.json_response(health_data, status=status_code)
            
        except Exception as error:
            logger.error(f"Health check failed: {error}")
            return web.json_response(
                {
                    "status": "unhealthy",
                    "error": str(error),
                    "timestamp": datetime.now().isoformat()
                },
                status=500
            )
    
    async def status_handler(self, request):
        """Detailed status endpoint"""
        try:
            status_data = await self.get_rotation_service_status()
            
            return web.json_response({
                "rotation_service": status_data,
                "metrics_exporter": {
                    "uptime_seconds": time.time() - self.service_start_time,
                    "last_metrics_update": self.last_update,
                    "metrics_cache_size": len(self.metrics_cache)
                },
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as error:
            logger.error(f"Status check failed: {error}")
            return web.json_response({"error": str(error)}, status=500)
    
    async def keys_handler(self, request):
        """Keys management endpoint"""
        try:
            keys_data = await self.get_managed_keys()
            
            return web.json_response({
                "keys": keys_data,
                "total_keys": len(keys_data),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as error:
            logger.error(f"Keys data retrieval failed: {error}")
            return web.json_response({"error": str(error)}, status=500)
    
    async def update_metrics(self):
        """Update Prometheus metrics from rotation service"""
        try:
            # Get service status
            status_data = await self.get_rotation_service_status()
            
            if status_data:
                # Update basic metrics
                metrics = status_data.get("metrics", {})
                
                vault_keys_managed.set(metrics.get("keys_managed", 0))
                
                # Update rotation metrics
                for key_name, rotation_count in metrics.get("rotation_counts", {}).items():
                    vault_rotation_total.labels(
                        key_name=key_name,
                        key_type="unknown",  # Would need to get from service
                        status="completed"
                    ).inc(rotation_count)
                
                # Update failure metrics
                for key_name, failure_count in metrics.get("failure_counts", {}).items():
                    vault_rotation_failures.labels(
                        key_name=key_name,
                        error_type="rotation_failed"
                    ).inc(failure_count)
                
                # Update Vault connection status
                vault_connected = status_data.get("vault_connected", False)
                vault_vault_connection_status.set(1 if vault_connected else 0)
            
            # Get detailed key information
            keys_data = await self.get_managed_keys()
            if keys_data:
                for key_info in keys_data:
                    key_name = key_info.get("name", "unknown")
                    key_type = key_info.get("type", "unknown")
                    
                    # Update next rotation timing
                    next_rotation = key_info.get("next_rotation_seconds", 0)
                    vault_next_rotation.labels(
                        key_name=key_name,
                        key_type=key_type
                    ).set(next_rotation)
                    
                    # Update grace period status
                    in_grace_period = key_info.get("in_grace_period", False)
                    vault_grace_period_active.labels(key_name=key_name).set(1 if in_grace_period else 0)
            
            self.last_update = datetime.now().isoformat()
            
        except Exception as error:
            logger.error(f"Failed to update metrics: {error}")
    
    async def check_rotation_service_health(self) -> bool:
        """Check if rotation service is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.rotation_service_url}/health", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def check_vault_health(self) -> bool:
        """Check Vault connectivity through rotation service"""
        try:
            status_data = await self.get_rotation_service_status()
            return status_data.get("vault_connected", False) if status_data else False
        except Exception:
            return False
    
    async def get_rotation_service_status(self) -> Optional[Dict[str, Any]]:
        """Get status from rotation service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.rotation_service_url}/status", timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
            return None
        except Exception as error:
            logger.error(f"Failed to get rotation service status: {error}")
            return None
    
    async def get_managed_keys(self) -> List[Dict[str, Any]]:
        """Get managed keys information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.rotation_service_url}/keys", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("keys", [])
            return []
        except Exception as error:
            logger.error(f"Failed to get managed keys: {error}")
            return []
    
    async def start_metrics_collection(self):
        """Start periodic metrics collection"""
        while True:
            try:
                await self.update_metrics()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as error:
                logger.error(f"Metrics collection error: {error}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 9100):
        """Start the metrics server"""
        # Start metrics collection task
        asyncio.create_task(self.start_metrics_collection())
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"🚀 Vault rotation metrics server started on {host}:{port}")
        logger.info(f"Metrics endpoint: http://{host}:{port}/metrics")
        logger.info(f"Health endpoint: http://{host}:{port}/health")
        
        # Keep server running
        try:
            while True:
                await asyncio.sleep(3600)  # Sleep for an hour
        except KeyboardInterrupt:
            logger.info("Shutting down metrics server...")
        finally:
            await runner.cleanup()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vault Key Rotation Metrics Exporter")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=9100, help="Port to bind to")
    parser.add_argument("--rotation-service-url", default="http://localhost:8001", 
                       help="URL of the rotation service")
    
    args = parser.parse_args()
    
    # Initialize metrics exporter
    metrics_exporter = VaultRotationMetrics(args.rotation_service_url)
    
    # Start server
    await metrics_exporter.start_server(args.host, args.port)


if __name__ == "__main__":
    asyncio.run(main())