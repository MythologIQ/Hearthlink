#!/usr/bin/env python3
"""
Service Recovery Manager

Comprehensive automatic service recovery and restart mechanisms
for all Hearthlink services including circuit breaker integration.
"""

import asyncio
import time
import threading
import subprocess
import psutil
import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import signal
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('service_recovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"
    FAILED = "failed"
    UNKNOWN = "unknown"
    STARTING = "starting"
    STOPPING = "stopping"

class RecoveryAction(Enum):
    RESTART = "restart"
    HEAL = "heal"
    SCALE = "scale"
    FAILOVER = "failover"
    EMERGENCY_STOP = "emergency_stop"

@dataclass
class ServiceConfig:
    name: str
    port: int
    process_name: str
    start_command: List[str]
    health_endpoint: str
    max_restart_attempts: int = 3
    restart_delay: int = 5
    health_check_interval: int = 30
    timeout: int = 10
    critical: bool = False
    dependencies: List[str] = None
    recovery_actions: List[RecoveryAction] = None

@dataclass
class ServiceHealth:
    name: str
    status: ServiceStatus
    last_check: datetime
    response_time: float
    error_count: int
    restart_count: int
    last_restart: Optional[datetime]
    uptime: float
    memory_usage: float
    cpu_usage: float
    
class ServiceRecoveryManager:
    """
    Comprehensive service recovery and restart management system
    """
    
    def __init__(self):
        self.services = self._initialize_services()
        self.service_health = {}
        self.recovery_history = []
        self.monitoring_active = False
        self.recovery_thread = None
        self.circuit_breaker_integration = True
        
        # Recovery policies
        self.global_recovery_policy = {
            'max_concurrent_restarts': 2,
            'cooldown_period': 60,  # seconds
            'escalation_threshold': 5,  # failures before escalation
            'emergency_shutdown_threshold': 10
        }
        
        logger.info("Service Recovery Manager initialized")
        
    def _initialize_services(self) -> Dict[str, ServiceConfig]:
        """Initialize service configurations"""
        return {
            'local_llm': ServiceConfig(
                name='Local LLM API',
                port=8001,
                process_name='local_llm_api',
                start_command=['python3', 'src/api/local_llm_api.py'],
                health_endpoint='http://localhost:8001/health',
                critical=True,
                recovery_actions=[RecoveryAction.RESTART, RecoveryAction.HEAL]
            ),
            'core_api': ServiceConfig(
                name='Core API',
                port=8000,
                process_name='core_api',
                start_command=['python3', 'src/api/core_api.py'],
                health_endpoint='http://localhost:8000/health',
                critical=True,
                dependencies=['local_llm'],
                recovery_actions=[RecoveryAction.RESTART, RecoveryAction.FAILOVER]
            ),
            'vault_api': ServiceConfig(
                name='Vault API',
                port=8002,
                process_name='vault_api',
                start_command=['python3', 'src/api/vault_api.py'],
                health_endpoint='http://localhost:8002/health',
                critical=True,
                recovery_actions=[RecoveryAction.RESTART, RecoveryAction.HEAL]
            ),
            'synapse_api': ServiceConfig(
                name='Synapse API',
                port=8003,
                process_name='synapse_api_server',
                start_command=['python3', 'src/api/synapse_api_server.py'],
                health_endpoint='http://localhost:8003/health',
                critical=False,
                recovery_actions=[RecoveryAction.RESTART]
            ),
            'sentry_api': ServiceConfig(
                name='Sentry API',
                port=8004,
                process_name='sentry_api',
                start_command=['python3', 'src/api/sentry_api.py'],
                health_endpoint='http://localhost:8004/health',
                critical=False,
                recovery_actions=[RecoveryAction.RESTART]
            ),
            'superclaude_api': ServiceConfig(
                name='SuperClaude API',
                port=8005,
                process_name='superclaude_api',
                start_command=['python3', 'src/api/superclaude_api.py'],
                health_endpoint='http://localhost:8005/health',
                critical=False,
                recovery_actions=[RecoveryAction.RESTART]
            ),
            'external_agent_api': ServiceConfig(
                name='External Agent API',
                port=8006,
                process_name='external_agent_api',
                start_command=['python3', 'src/api/external_agent_api.py'],
                health_endpoint='http://localhost:8006/health',
                critical=False,
                recovery_actions=[RecoveryAction.RESTART]
            )
        }
    
    async def check_service_health(self, service_id: str) -> ServiceHealth:
        """Check health of a specific service"""
        config = self.services[service_id]
        start_time = time.time()
        
        try:
            # Check if process is running
            process_running = self._is_process_running(config.process_name)
            
            if not process_running:
                return ServiceHealth(
                    name=config.name,
                    status=ServiceStatus.FAILED,
                    last_check=datetime.now(),
                    response_time=0,
                    error_count=self.service_health.get(service_id, {}).get('error_count', 0) + 1,
                    restart_count=self.service_health.get(service_id, {}).get('restart_count', 0),
                    last_restart=self.service_health.get(service_id, {}).get('last_restart'),
                    uptime=0,
                    memory_usage=0,
                    cpu_usage=0
                )
            
            # Check health endpoint
            response = requests.get(
                config.health_endpoint,
                timeout=config.timeout
            )
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Get process metrics
            process_info = self._get_process_info(config.port)
            
            if response.status_code == 200:
                return ServiceHealth(
                    name=config.name,
                    status=ServiceStatus.HEALTHY,
                    last_check=datetime.now(),
                    response_time=response_time,
                    error_count=0,  # Reset on successful check
                    restart_count=self.service_health.get(service_id, {}).get('restart_count', 0),
                    last_restart=self.service_health.get(service_id, {}).get('last_restart'),
                    uptime=process_info.get('uptime', 0),
                    memory_usage=process_info.get('memory_percent', 0),
                    cpu_usage=process_info.get('cpu_percent', 0)
                )
            else:
                raise Exception(f"Health check failed with status {response.status_code}")
                
        except Exception as error:
            response_time = (time.time() - start_time) * 1000
            error_count = self.service_health.get(service_id, {}).get('error_count', 0) + 1
            
            # Determine status based on error count and type
            if error_count >= 5:
                status = ServiceStatus.FAILED
            elif error_count >= 2:
                status = ServiceStatus.UNHEALTHY
            else:
                status = ServiceStatus.UNKNOWN
            
            logger.warning(f"Health check failed for {config.name}: {error}")
            
            return ServiceHealth(
                name=config.name,
                status=status,
                last_check=datetime.now(),
                response_time=response_time,
                error_count=error_count,
                restart_count=self.service_health.get(service_id, {}).get('restart_count', 0),
                last_restart=self.service_health.get(service_id, {}).get('last_restart'),
                uptime=0,
                memory_usage=0,
                cpu_usage=0
            )
    
    def _is_process_running(self, process_name: str) -> bool:
        """Check if a process is running by name"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if process_name in ' '.join(proc.info['cmdline'] or []):
                    return True
            return False
        except:
            return False
    
    def _get_process_info(self, port: int) -> Dict:
        """Get process information for service on specific port"""
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    try:
                        proc = psutil.Process(conn.pid)
                        return {
                            'pid': conn.pid,
                            'uptime': time.time() - proc.create_time(),
                            'memory_percent': proc.memory_percent(),
                            'cpu_percent': proc.cpu_percent()
                        }
                    except psutil.NoSuchProcess:
                        continue
            return {}
        except:
            return {}
    
    async def restart_service(self, service_id: str) -> bool:
        """Restart a specific service"""
        config = self.services[service_id]
        logger.info(f"Attempting to restart {config.name}")
        
        try:
            # Stop existing process
            await self._stop_service(service_id)
            
            # Wait for graceful shutdown
            await asyncio.sleep(config.restart_delay)
            
            # Start service
            success = await self._start_service(service_id)
            
            if success:
                # Update restart count
                if service_id in self.service_health:
                    self.service_health[service_id]['restart_count'] += 1
                    self.service_health[service_id]['last_restart'] = datetime.now()
                
                # Log recovery action
                self.recovery_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'service': config.name,
                    'action': 'restart',
                    'success': True
                })
                
                logger.info(f"Successfully restarted {config.name}")
                
                # Wait for service to fully start
                await asyncio.sleep(5)
                
                return True
            else:
                logger.error(f"Failed to restart {config.name}")
                return False
                
        except Exception as error:
            logger.error(f"Error restarting {config.name}: {error}")
            return False
    
    async def _stop_service(self, service_id: str) -> bool:
        """Stop a service gracefully"""
        config = self.services[service_id]
        
        try:
            # Find and kill process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if config.process_name in cmdline or str(config.port) in cmdline:
                    try:
                        process = psutil.Process(proc.info['pid'])
                        process.terminate()
                        
                        # Wait for graceful termination
                        try:
                            process.wait(timeout=10)
                        except psutil.TimeoutExpired:
                            # Force kill if needed
                            process.kill()
                            
                        logger.info(f"Stopped process {proc.info['pid']} for {config.name}")
                        return True
                    except psutil.NoSuchProcess:
                        continue
                        
            return True  # No process found, consider it stopped
            
        except Exception as error:
            logger.error(f"Error stopping {config.name}: {error}")
            return False
    
    async def _start_service(self, service_id: str) -> bool:
        """Start a service"""
        config = self.services[service_id]
        
        try:
            # Change to correct directory
            original_dir = os.getcwd()
            
            # Start the process
            process = subprocess.Popen(
                config.start_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=original_dir
            )
            
            # Give process time to start
            await asyncio.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"Started {config.name} with PID {process.pid}")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"Failed to start {config.name}: {stderr.decode()}")
                return False
                
        except Exception as error:
            logger.error(f"Error starting {config.name}: {error}")
            return False
    
    async def heal_service(self, service_id: str) -> bool:
        """Attempt to heal a service without restarting"""
        config = self.services[service_id]
        logger.info(f"Attempting to heal {config.name}")
        
        try:
            # Try health endpoint reset
            if hasattr(self, f'_heal_{service_id}'):
                heal_method = getattr(self, f'_heal_{service_id}')
                return await heal_method()
            
            # Generic healing: clear caches, reset connections
            healing_endpoints = [
                f'{config.health_endpoint.replace("/health", "/reset")}',
                f'{config.health_endpoint.replace("/health", "/clear-cache")}',
                f'{config.health_endpoint.replace("/health", "/reconnect")}'
            ]
            
            for endpoint in healing_endpoints:
                try:
                    response = requests.post(endpoint, timeout=5)
                    if response.status_code == 200:
                        logger.info(f"Healing action successful for {config.name}")
                        break
                except:
                    continue
            
            # Wait and check if healing worked
            await asyncio.sleep(5)
            health = await self.check_service_health(service_id)
            
            return health.status == ServiceStatus.HEALTHY
            
        except Exception as error:
            logger.error(f"Error healing {config.name}: {error}")
            return False
    
    async def execute_recovery_action(self, service_id: str, action: RecoveryAction) -> bool:
        """Execute a specific recovery action"""
        config = self.services[service_id]
        
        logger.info(f"Executing {action.value} for {config.name}")
        
        if action == RecoveryAction.RESTART:
            return await self.restart_service(service_id)
        elif action == RecoveryAction.HEAL:
            return await self.heal_service(service_id)
        elif action == RecoveryAction.FAILOVER:
            return await self.failover_service(service_id)
        elif action == RecoveryAction.EMERGENCY_STOP:
            return await self.emergency_stop_service(service_id)
        else:
            logger.warning(f"Unknown recovery action: {action}")
            return False
    
    async def failover_service(self, service_id: str) -> bool:
        """Implement failover for critical services"""
        config = self.services[service_id]
        logger.info(f"Implementing failover for {config.name}")
        
        # For now, failover is equivalent to restart with enhanced monitoring
        # In a production environment, this would switch to backup instances
        
        success = await self.restart_service(service_id)
        
        if success:
            # Enhanced monitoring after failover
            for _ in range(3):
                await asyncio.sleep(10)
                health = await self.check_service_health(service_id)
                if health.status == ServiceStatus.HEALTHY:
                    logger.info(f"Failover successful for {config.name}")
                    return True
            
            logger.warning(f"Failover completed but service still unhealthy: {config.name}")
        
        return success
    
    async def emergency_stop_service(self, service_id: str) -> bool:
        """Emergency stop for a service"""
        config = self.services[service_id]
        logger.critical(f"Emergency stop for {config.name}")
        
        try:
            # Force kill all related processes
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if (config.process_name in cmdline or 
                    str(config.port) in cmdline or
                    config.name.lower().replace(' ', '_') in cmdline):
                    try:
                        process = psutil.Process(proc.info['pid'])
                        process.kill()
                        killed_count += 1
                        logger.info(f"Emergency killed PID {proc.info['pid']}")
                    except psutil.NoSuchProcess:
                        continue
            
            logger.critical(f"Emergency stop completed for {config.name}, killed {killed_count} processes")
            return True
            
        except Exception as error:
            logger.error(f"Error in emergency stop for {config.name}: {error}")
            return False
    
    async def monitor_services(self):
        """Main monitoring loop"""
        logger.info("Starting service monitoring")
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Check all services
                tasks = []
                for service_id in self.services:
                    tasks.append(self.check_service_health(service_id))
                
                health_results = await asyncio.gather(*tasks)
                
                # Update health tracking
                for i, service_id in enumerate(self.services):
                    self.service_health[service_id] = asdict(health_results[i])
                
                # Determine recovery actions
                await self._determine_recovery_actions()
                
                # Log status
                healthy_count = sum(1 for h in health_results if h.status == ServiceStatus.HEALTHY)
                logger.info(f"Service health check: {healthy_count}/{len(self.services)} services healthy")
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as error:
                logger.error(f"Error in monitoring loop: {error}")
                await asyncio.sleep(10)  # Shorter wait on error
    
    async def _determine_recovery_actions(self):
        """Determine and execute recovery actions based on service health"""
        recovery_tasks = []
        
        for service_id, health_data in self.service_health.items():
            config = self.services[service_id]
            health = ServiceHealth(**health_data)
            
            # Skip if already recovering
            if health.status == ServiceStatus.RECOVERING:
                continue
            
            # Determine if recovery is needed
            needs_recovery = (
                health.status in [ServiceStatus.UNHEALTHY, ServiceStatus.FAILED] or
                health.error_count >= 3 or
                (health.response_time > 5000 and health.response_time > 0)
            )
            
            if needs_recovery:
                # Check restart limits
                if health.restart_count >= config.max_restart_attempts:
                    if config.critical:
                        logger.critical(f"{config.name} exceeded restart limit - escalating")
                        recovery_tasks.append(self.execute_recovery_action(service_id, RecoveryAction.EMERGENCY_STOP))
                    else:
                        logger.warning(f"{config.name} exceeded restart limit - disabling")
                        continue
                
                # Check cooldown period
                if (health.last_restart and 
                    datetime.now() - health.last_restart < timedelta(seconds=self.global_recovery_policy['cooldown_period'])):
                    continue
                
                # Update status to recovering
                self.service_health[service_id]['status'] = ServiceStatus.RECOVERING.value
                
                # Select recovery action
                recovery_action = self._select_recovery_action(service_id, health)
                recovery_tasks.append(self.execute_recovery_action(service_id, recovery_action))
        
        # Execute recovery actions (with concurrency limit)
        if recovery_tasks:
            # Limit concurrent recoveries
            max_concurrent = self.global_recovery_policy['max_concurrent_restarts']
            for i in range(0, len(recovery_tasks), max_concurrent):
                batch = recovery_tasks[i:i + max_concurrent]
                await asyncio.gather(*batch)
                if i + max_concurrent < len(recovery_tasks):
                    await asyncio.sleep(5)  # Brief pause between batches
    
    def _select_recovery_action(self, service_id: str, health: ServiceHealth) -> RecoveryAction:
        """Select appropriate recovery action based on service state"""
        config = self.services[service_id]
        
        # If service is completely failed, restart
        if health.status == ServiceStatus.FAILED:
            return RecoveryAction.RESTART
        
        # If high error count, try healing first
        if health.error_count >= 3 and RecoveryAction.HEAL in (config.recovery_actions or []):
            return RecoveryAction.HEAL
        
        # If critical service and failing, try failover
        if config.critical and RecoveryAction.FAILOVER in (config.recovery_actions or []):
            return RecoveryAction.FAILOVER
        
        # Default to restart
        return RecoveryAction.RESTART
    
    def start_monitoring(self):
        """Start the monitoring system in a separate thread"""
        if self.recovery_thread and self.recovery_thread.is_alive():
            logger.warning("Monitoring already active")
            return
        
        self.recovery_thread = threading.Thread(
            target=lambda: asyncio.run(self.monitor_services()),
            daemon=True
        )
        self.recovery_thread.start()
        logger.info("Service recovery monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        if self.recovery_thread:
            self.recovery_thread.join(timeout=10)
        logger.info("Service recovery monitoring stopped")
    
    def get_service_status(self) -> Dict:
        """Get current status of all services"""
        return {
            'services': self.service_health,
            'monitoring_active': self.monitoring_active,
            'recovery_history': self.recovery_history[-10:],  # Last 10 actions
            'global_stats': {
                'total_services': len(self.services),
                'healthy_services': sum(1 for h in self.service_health.values() 
                                      if h.get('status') == ServiceStatus.HEALTHY.value),
                'total_restarts': sum(h.get('restart_count', 0) for h in self.service_health.values()),
                'last_check': max([h.get('last_check', '') for h in self.service_health.values()], default='Never')
            }
        }
    
    def generate_recovery_report(self) -> str:
        """Generate a comprehensive recovery report"""
        status = self.get_service_status()
        
        report = f"""
Service Recovery Manager Report
Generated: {datetime.now().isoformat()}

=== Global Statistics ===
Total Services: {status['global_stats']['total_services']}
Healthy Services: {status['global_stats']['healthy_services']}
Total Restarts: {status['global_stats']['total_restarts']}
Monitoring Active: {status['monitoring_active']}

=== Service Details ===
"""
        
        for service_id, health in status['services'].items():
            config = self.services[service_id]
            report += f"""
{config.name}:
  Status: {health.get('status', 'Unknown')}
  Error Count: {health.get('error_count', 0)}
  Restart Count: {health.get('restart_count', 0)}
  Response Time: {health.get('response_time', 0):.2f}ms
  Memory Usage: {health.get('memory_usage', 0):.1f}%
  CPU Usage: {health.get('cpu_usage', 0):.1f}%
"""
        
        report += f"""
=== Recent Recovery Actions ===
"""
        for action in status['recovery_history']:
            report += f"  {action['timestamp']}: {action['action']} {action['service']} - {'Success' if action['success'] else 'Failed'}\n"
        
        return report

# Global instance
recovery_manager = ServiceRecoveryManager()

def start_service_recovery():
    """Start the global service recovery system"""
    recovery_manager.start_monitoring()

def stop_service_recovery():
    """Stop the global service recovery system"""
    recovery_manager.stop_monitoring()

def get_recovery_status():
    """Get current recovery system status"""
    return recovery_manager.get_service_status()

if __name__ == "__main__":
    # Test the recovery system
    import argparse
    
    parser = argparse.ArgumentParser(description='Service Recovery Manager')
    parser.add_argument('--start', action='store_true', help='Start monitoring')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--test', action='store_true', help='Test recovery on a service')
    
    args = parser.parse_args()
    
    if args.start:
        print("Starting Service Recovery Manager...")
        recovery_manager.start_monitoring()
        try:
            while True:
                time.sleep(10)
                status = recovery_manager.get_service_status()
                print(f"Monitoring: {status['global_stats']['healthy_services']}/{status['global_stats']['total_services']} services healthy")
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            recovery_manager.stop_monitoring()
    
    elif args.status:
        status = recovery_manager.get_service_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.report:
        print(recovery_manager.generate_recovery_report())
    
    elif args.test:
        async def test_recovery():
            print("Testing service recovery...")
            health = await recovery_manager.check_service_health('local_llm')
            print(f"Local LLM Health: {health}")
            
            if health.status != ServiceStatus.HEALTHY:
                print("Attempting recovery...")
                success = await recovery_manager.restart_service('local_llm')
                print(f"Recovery success: {success}")
        
        asyncio.run(test_recovery())
    
    else:
        parser.print_help()