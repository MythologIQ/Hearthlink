#!/usr/bin/env python3
"""
Automatic Recovery Orchestrator

Complete automatic service recovery and restart mechanism that integrates:
- Service Watchdog (lightweight monitoring)
- Service Recovery Manager (comprehensive recovery)
- Circuit Breaker system (failure detection)
- Health Check system (service validation)
- Recovery Dashboard (monitoring UI)

This orchestrator provides intelligent, automated service recovery with
minimal downtime and comprehensive failure handling.
"""

import asyncio
import time
import threading
import json
import logging
import signal
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Import our existing components
try:
    from .service_watchdog import ServiceWatchdog
    from .service_recovery_manager import ServiceRecoveryManager, ServiceStatus, RecoveryAction
    from .circuit_breaker import CircuitBreakerManager, CircuitBreakerState
except ImportError:
    # Fallback imports for standalone execution
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from service_watchdog import ServiceWatchdog
    from service_recovery_manager import ServiceRecoveryManager, ServiceStatus, RecoveryAction

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automatic_recovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RecoveryStrategy(Enum):
    CONSERVATIVE = "conservative"  # Slow, careful recovery
    AGGRESSIVE = "aggressive"     # Fast, immediate recovery
    INTELLIGENT = "intelligent"   # AI-driven recovery decisions
    MAINTENANCE = "maintenance"   # Maintenance mode with reduced capacity

class SystemHealth(Enum):
    OPTIMAL = "optimal"           # All services healthy
    DEGRADED = "degraded"        # Some issues but functional
    CRITICAL = "critical"        # Major issues, limited functionality
    EMERGENCY = "emergency"      # System-wide failure

@dataclass
class RecoveryPolicy:
    max_concurrent_recoveries: int = 3
    recovery_timeout: int = 300  # 5 minutes
    escalation_threshold: int = 5
    cooldown_period: int = 120   # 2 minutes
    emergency_threshold: int = 10
    maintenance_mode_trigger: int = 15
    strategy: RecoveryStrategy = RecoveryStrategy.INTELLIGENT

@dataclass
class SystemMetrics:
    total_services: int
    healthy_services: int
    degraded_services: int
    failed_services: int
    recovering_services: int
    total_recoveries: int
    successful_recoveries: int
    failed_recoveries: int
    uptime_percentage: float
    last_incident: Optional[datetime]
    recovery_rate: float

class AutomaticRecoveryOrchestrator:
    """
    Complete automatic service recovery orchestration system
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.policy = RecoveryPolicy(**self.config.get('recovery_policy', {}))
        
        # Initialize components
        self.watchdog = ServiceWatchdog()
        self.recovery_manager = ServiceRecoveryManager()
        self.circuit_breakers = {}
        
        # State tracking
        self.system_health = SystemHealth.OPTIMAL
        self.recovery_queue = asyncio.Queue()
        self.active_recoveries = set()
        self.recovery_history = []
        self.metrics = self._initialize_metrics()
        
        # Control flags
        self.orchestrator_running = False
        self.maintenance_mode = False
        self.emergency_mode = False
        self.shutdown_requested = False
        
        # Event callbacks
        self.event_callbacks = {
            'service_failure': [],
            'recovery_started': [],
            'recovery_completed': [],
            'system_health_changed': [],
            'emergency_triggered': []
        }
        
        logger.info("Automatic Recovery Orchestrator initialized")
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'recovery_policy': {
                'strategy': 'intelligent',
                'max_concurrent_recoveries': 3,
                'recovery_timeout': 300,
                'escalation_threshold': 5,
                'cooldown_period': 120
            },
            'health_thresholds': {
                'optimal': 0.95,
                'degraded': 0.70,
                'critical': 0.50,
                'emergency': 0.25
            },
            'notification_settings': {
                'enabled': True,
                'email_alerts': False,
                'webhook_url': None
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_metrics(self) -> SystemMetrics:
        """Initialize system metrics"""
        return SystemMetrics(
            total_services=len(self.recovery_manager.services),
            healthy_services=0,
            degraded_services=0,
            failed_services=0,
            recovering_services=0,
            total_recoveries=0,
            successful_recoveries=0,
            failed_recoveries=0,
            uptime_percentage=100.0,
            last_incident=None,
            recovery_rate=0.0
        )
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """Register callback for specific events"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
        
    def _emit_event(self, event_type: str, data: Dict):
        """Emit event to registered callbacks"""
        for callback in self.event_callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in event callback {callback}: {e}")
    
    async def assess_system_health(self) -> SystemHealth:
        """Assess overall system health"""
        service_statuses = []
        
        # Collect health from all services
        for service_id in self.recovery_manager.services:
            try:
                health = await self.recovery_manager.check_service_health(service_id)
                service_statuses.append(health.status)
            except Exception as e:
                logger.error(f"Error checking health for {service_id}: {e}")
                service_statuses.append(ServiceStatus.FAILED)
        
        # Calculate health percentages
        total = len(service_statuses)
        healthy = sum(1 for s in service_statuses if s == ServiceStatus.HEALTHY)
        health_ratio = healthy / total if total > 0 else 0
        
        # Update metrics
        self.metrics.total_services = total
        self.metrics.healthy_services = healthy
        self.metrics.degraded_services = sum(1 for s in service_statuses if s == ServiceStatus.UNHEALTHY)
        self.metrics.failed_services = sum(1 for s in service_statuses if s == ServiceStatus.FAILED)
        self.metrics.recovering_services = sum(1 for s in service_statuses if s == ServiceStatus.RECOVERING)
        
        # Determine system health
        thresholds = self.config['health_thresholds']
        
        if health_ratio >= thresholds['optimal']:
            new_health = SystemHealth.OPTIMAL
        elif health_ratio >= thresholds['degraded']:
            new_health = SystemHealth.DEGRADED
        elif health_ratio >= thresholds['critical']:
            new_health = SystemHealth.CRITICAL
        else:
            new_health = SystemHealth.EMERGENCY
        
        # Emit health change event if changed
        if new_health != self.system_health:
            old_health = self.system_health
            self.system_health = new_health
            self._emit_event('system_health_changed', {
                'old_health': old_health.value,
                'new_health': new_health.value,
                'health_ratio': health_ratio,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info(f"System health changed: {old_health.value} -> {new_health.value} (ratio: {health_ratio:.2f})")
        
        return new_health
    
    async def detect_service_failures(self) -> List[str]:
        """Detect failed services that need recovery"""
        failed_services = []
        
        for service_id in self.recovery_manager.services:
            try:
                health = await self.recovery_manager.check_service_health(service_id)
                
                # Check if service needs recovery
                needs_recovery = (
                    health.status in [ServiceStatus.FAILED, ServiceStatus.UNHEALTHY] or
                    health.error_count >= 3 or
                    (health.response_time > 10000 and health.response_time > 0)
                )
                
                if needs_recovery and service_id not in self.active_recoveries:
                    failed_services.append(service_id)
                    
            except Exception as e:
                logger.error(f"Error detecting failure for {service_id}: {e}")
                if service_id not in self.active_recoveries:
                    failed_services.append(service_id)
        
        return failed_services
    
    async def queue_recovery(self, service_id: str, priority: int = 1):
        """Queue a service for recovery"""
        recovery_item = {
            'service_id': service_id,
            'priority': priority,
            'queued_at': datetime.now(),
            'attempts': 0
        }
        
        await self.recovery_queue.put(recovery_item)
        logger.info(f"Queued {service_id} for recovery (priority: {priority})")
    
    async def execute_recovery(self, recovery_item: Dict) -> bool:
        """Execute recovery for a specific service"""
        service_id = recovery_item['service_id']
        
        # Add to active recoveries
        self.active_recoveries.add(service_id)
        
        try:
            config = self.recovery_manager.services[service_id]
            
            # Emit recovery started event
            self._emit_event('recovery_started', {
                'service_id': service_id,
                'service_name': config.name,
                'timestamp': datetime.now().isoformat(),
                'attempt': recovery_item['attempts'] + 1
            })
            
            logger.info(f"Starting recovery for {config.name} (attempt {recovery_item['attempts'] + 1})")
            
            # Determine recovery strategy
            strategy = self._select_recovery_strategy(service_id)
            
            # Execute recovery based on strategy
            if strategy == RecoveryAction.RESTART:
                success = await self.recovery_manager.restart_service(service_id)
            elif strategy == RecoveryAction.HEAL:
                success = await self.recovery_manager.heal_service(service_id)
            elif strategy == RecoveryAction.FAILOVER:
                success = await self.recovery_manager.failover_service(service_id)
            else:
                success = await self.recovery_manager.restart_service(service_id)
            
            # Update metrics
            self.metrics.total_recoveries += 1
            if success:
                self.metrics.successful_recoveries += 1
            else:
                self.metrics.failed_recoveries += 1
            
            # Calculate recovery rate
            if self.metrics.total_recoveries > 0:
                self.metrics.recovery_rate = self.metrics.successful_recoveries / self.metrics.total_recoveries
            
            # Log recovery completion
            self.recovery_history.append({
                'timestamp': datetime.now().isoformat(),
                'service_id': service_id,
                'service_name': config.name,
                'strategy': strategy.value if hasattr(strategy, 'value') else str(strategy),
                'success': success,
                'attempt': recovery_item['attempts'] + 1
            })
            
            # Emit recovery completed event
            self._emit_event('recovery_completed', {
                'service_id': service_id,
                'service_name': config.name,
                'success': success,
                'strategy': strategy.value if hasattr(strategy, 'value') else str(strategy),
                'timestamp': datetime.now().isoformat()
            })
            
            if success:
                logger.info(f"✅ Successfully recovered {config.name}")
            else:
                logger.error(f"❌ Failed to recover {config.name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error during recovery of {service_id}: {e}")
            self.metrics.failed_recoveries += 1
            return False
        finally:
            # Remove from active recoveries
            self.active_recoveries.discard(service_id)
    
    def _select_recovery_strategy(self, service_id: str) -> RecoveryAction:
        """Select appropriate recovery strategy for service"""
        config = self.recovery_manager.services[service_id]
        
        # Check policy strategy
        if self.policy.strategy == RecoveryStrategy.CONSERVATIVE:
            # Always try healing first for conservative approach
            if RecoveryAction.HEAL in (config.recovery_actions or []):
                return RecoveryAction.HEAL
            return RecoveryAction.RESTART
            
        elif self.policy.strategy == RecoveryStrategy.AGGRESSIVE:
            # Always restart for aggressive approach
            return RecoveryAction.RESTART
            
        elif self.policy.strategy == RecoveryStrategy.INTELLIGENT:
            # Use intelligent selection based on service history
            service_health = self.recovery_manager.service_health.get(service_id, {})
            error_count = service_health.get('error_count', 0)
            restart_count = service_health.get('restart_count', 0)
            
            # If many errors but few restarts, try healing
            if error_count >= 3 and restart_count < 2:
                if RecoveryAction.HEAL in (config.recovery_actions or []):
                    return RecoveryAction.HEAL
            
            # If critical service, consider failover
            if config.critical and restart_count >= 2:
                if RecoveryAction.FAILOVER in (config.recovery_actions or []):
                    return RecoveryAction.FAILOVER
            
            # Default to restart
            return RecoveryAction.RESTART
        
        else:
            # Maintenance mode - gentle recovery
            if RecoveryAction.HEAL in (config.recovery_actions or []):
                return RecoveryAction.HEAL
            return RecoveryAction.RESTART
    
    async def recovery_worker(self):
        """Worker coroutine that processes recovery queue"""
        logger.info("Recovery worker started")
        
        while self.orchestrator_running and not self.shutdown_requested:
            try:
                # Check if we can handle more recoveries
                if len(self.active_recoveries) >= self.policy.max_concurrent_recoveries:
                    await asyncio.sleep(1)
                    continue
                
                # Get next recovery item with timeout
                try:
                    recovery_item = await asyncio.wait_for(
                        self.recovery_queue.get(), 
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                # Check cooldown period
                service_id = recovery_item['service_id']
                if self._is_in_cooldown(service_id):
                    # Re-queue for later
                    await asyncio.sleep(1)
                    await self.recovery_queue.put(recovery_item)
                    continue
                
                # Execute recovery
                recovery_item['attempts'] += 1
                success = await self.execute_recovery(recovery_item)
                
                # Handle failed recovery
                if not success:
                    if recovery_item['attempts'] < 3:
                        # Re-queue with higher priority
                        recovery_item['priority'] += 1
                        await asyncio.sleep(5)  # Brief delay before retry
                        await self.recovery_queue.put(recovery_item)
                    else:
                        logger.error(f"Giving up on {service_id} after {recovery_item['attempts']} attempts")
                        
                        # Check if this triggers emergency mode
                        if self._should_trigger_emergency():
                            await self._trigger_emergency_mode()
                
            except Exception as e:
                logger.error(f"Error in recovery worker: {e}")
                await asyncio.sleep(1)
    
    def _is_in_cooldown(self, service_id: str) -> bool:
        """Check if service is in cooldown period"""
        for history_item in reversed(self.recovery_history[-10:]):  # Check last 10
            if (history_item['service_id'] == service_id and 
                history_item.get('success', False)):
                
                recovery_time = datetime.fromisoformat(history_item['timestamp'])
                cooldown_end = recovery_time + timedelta(seconds=self.policy.cooldown_period)
                
                if datetime.now() < cooldown_end:
                    return True
                break
        
        return False
    
    def _should_trigger_emergency(self) -> bool:
        """Check if emergency mode should be triggered"""
        # Count recent failures
        recent_failures = 0
        cutoff_time = datetime.now() - timedelta(minutes=10)
        
        for history_item in reversed(self.recovery_history[-20:]):  # Check last 20
            if datetime.fromisoformat(history_item['timestamp']) < cutoff_time:
                break
            if not history_item.get('success', False):
                recent_failures += 1
        
        return recent_failures >= self.policy.emergency_threshold
    
    async def _trigger_emergency_mode(self):
        """Trigger emergency mode"""
        if self.emergency_mode:
            return
            
        self.emergency_mode = True
        logger.critical("🚨 EMERGENCY MODE TRIGGERED - System-wide service failure detected!")
        
        self._emit_event('emergency_triggered', {
            'timestamp': datetime.now().isoformat(),
            'trigger_reason': 'multiple_recovery_failures',
            'failed_services': list(self.active_recoveries),
            'system_health': self.system_health.value
        })
        
        # Emergency recovery actions
        try:
            # Stop all non-critical services
            for service_id, config in self.recovery_manager.services.items():
                if not config.critical:
                    logger.info(f"Emergency stopping non-critical service: {config.name}")
                    await self.recovery_manager._stop_service(service_id)
            
            # Focus recovery on critical services only
            critical_services = [
                service_id for service_id, config in self.recovery_manager.services.items()
                if config.critical
            ]
            
            logger.info(f"Focusing emergency recovery on critical services: {critical_services}")
            
            # Clear recovery queue and re-queue only critical services
            while not self.recovery_queue.empty():
                try:
                    self.recovery_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            # Queue critical services for recovery
            for service_id in critical_services:
                await self.queue_recovery(service_id, priority=10)
            
        except Exception as e:
            logger.error(f"Error during emergency mode activation: {e}")
    
    async def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Monitoring loop started")
        
        while self.orchestrator_running and not self.shutdown_requested:
            try:
                # Assess system health
                await self.assess_system_health()
                
                # Detect service failures
                failed_services = await self.detect_service_failures()
                
                # Queue failed services for recovery
                for service_id in failed_services:
                    config = self.recovery_manager.services[service_id]
                    priority = 5 if config.critical else 1
                    await self.queue_recovery(service_id, priority)
                
                # Check if we should exit emergency mode
                if (self.emergency_mode and 
                    self.system_health in [SystemHealth.OPTIMAL, SystemHealth.DEGRADED]):
                    self.emergency_mode = False
                    logger.info("✅ Exiting emergency mode - system health improved")
                
                # Sleep between monitoring cycles
                await asyncio.sleep(10)  # Monitor every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def start_orchestrator(self):
        """Start the automatic recovery orchestrator"""
        if self.orchestrator_running:
            logger.warning("Orchestrator is already running")
            return
        
        logger.info("🚀 Starting Automatic Recovery Orchestrator")
        self.orchestrator_running = True
        
        # Start all components
        try:
            # Start watchdog
            self.watchdog.start()
            
            # Start recovery manager monitoring
            self.recovery_manager.start_monitoring()
            
            # Start orchestrator tasks
            await asyncio.gather(
                self.monitoring_loop(),
                self.recovery_worker(),
                return_exceptions=True
            )
            
        except Exception as e:
            logger.error(f"Error starting orchestrator: {e}")
            await self.stop_orchestrator()
    
    async def stop_orchestrator(self):
        """Stop the automatic recovery orchestrator"""
        if not self.orchestrator_running:
            return
        
        logger.info("🛑 Stopping Automatic Recovery Orchestrator")
        self.shutdown_requested = True
        self.orchestrator_running = False
        
        # Stop components
        try:
            self.watchdog.stop()
            self.recovery_manager.stop_monitoring()
        except Exception as e:
            logger.error(f"Error stopping components: {e}")
        
        logger.info("Orchestrator stopped")
    
    def get_orchestrator_status(self) -> Dict:
        """Get comprehensive orchestrator status"""
        return {
            'orchestrator': {
                'running': self.orchestrator_running,
                'emergency_mode': self.emergency_mode,
                'maintenance_mode': self.maintenance_mode,
                'system_health': self.system_health.value,
                'active_recoveries': len(self.active_recoveries),
                'queue_size': self.recovery_queue.qsize(),
                'uptime': time.time() - getattr(self, 'start_time', time.time())
            },
            'metrics': asdict(self.metrics),
            'recent_recoveries': self.recovery_history[-10:],
            'components': {
                'watchdog': self.watchdog.get_status(),
                'recovery_manager': self.recovery_manager.get_service_status()
            },
            'policy': asdict(self.policy)
        }
    
    def generate_status_report(self) -> str:
        """Generate comprehensive status report"""
        status = self.get_orchestrator_status()
        
        report = f"""
Automatic Recovery Orchestrator Status Report
Generated: {datetime.now().isoformat()}

=== System Overview ===
System Health: {status['orchestrator']['system_health'].upper()}
Emergency Mode: {status['orchestrator']['emergency_mode']}
Orchestrator Running: {status['orchestrator']['running']}
Active Recoveries: {status['orchestrator']['active_recoveries']}
Recovery Queue: {status['orchestrator']['queue_size']} pending

=== Metrics ===
Total Services: {status['metrics']['total_services']}
Healthy: {status['metrics']['healthy_services']}
Degraded: {status['metrics']['degraded_services']}
Failed: {status['metrics']['failed_services']}
Recovering: {status['metrics']['recovering_services']}

Recovery Success Rate: {status['metrics']['recovery_rate']:.1%}
Total Recoveries: {status['metrics']['total_recoveries']}
Successful: {status['metrics']['successful_recoveries']}
Failed: {status['metrics']['failed_recoveries']}

=== Recent Recovery Actions ==="""
        
        for recovery in status['recent_recoveries']:
            status_icon = "✅" if recovery['success'] else "❌"
            report += f"\n  {status_icon} {recovery['timestamp']}: {recovery['service_name']} ({recovery['strategy']})"
        
        report += f"""

=== Component Status ===
Watchdog Services: {status['components']['watchdog']['summary']['healthy']}/{status['components']['watchdog']['summary']['total']} healthy
Recovery Manager: {status['components']['recovery_manager']['global_stats']['healthy_services']}/{status['components']['recovery_manager']['global_stats']['total_services']} healthy
"""
        
        return report

# Global orchestrator instance
orchestrator = AutomaticRecoveryOrchestrator()

# Convenience functions
async def start_automatic_recovery():
    """Start the automatic recovery system"""
    await orchestrator.start_orchestrator()

async def stop_automatic_recovery():
    """Stop the automatic recovery system"""
    await orchestrator.stop_orchestrator()

def get_recovery_status():
    """Get current recovery system status"""
    return orchestrator.get_orchestrator_status()

def force_service_recovery(service_id: str):
    """Force recovery of a specific service"""
    return asyncio.create_task(orchestrator.queue_recovery(service_id, priority=10))

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatic Recovery Orchestrator')
    parser.add_argument('--start', action='store_true', help='Start orchestrator')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--test', action='store_true', help='Test recovery system')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    if args.config:
        orchestrator = AutomaticRecoveryOrchestrator(args.config)
    
    if args.start:
        print("Starting Automatic Recovery Orchestrator...")
        print("Press Ctrl+C to stop")
        
        def signal_handler(signum, frame):
            print("\nShutting down...")
            asyncio.create_task(orchestrator.stop_orchestrator())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            orchestrator.start_time = time.time()
            asyncio.run(orchestrator.start_orchestrator())
        except KeyboardInterrupt:
            print("\nShutdown complete")
    
    elif args.status:
        status = orchestrator.get_orchestrator_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.report:
        print(orchestrator.generate_status_report())
    
    elif args.test:
        async def test_orchestrator():
            print("Testing orchestrator components...")
            
            # Test health assessment
            health = await orchestrator.assess_system_health()
            print(f"System health: {health.value}")
            
            # Test failure detection
            failures = await orchestrator.detect_service_failures()
            print(f"Failed services detected: {failures}")
            
            # Test recovery queueing
            if failures:
                await orchestrator.queue_recovery(failures[0])
                print(f"Queued {failures[0]} for recovery")
            
            print("Test complete")
        
        asyncio.run(test_orchestrator())
    
    else:
        parser.print_help()