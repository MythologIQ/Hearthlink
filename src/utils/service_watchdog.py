#!/usr/bin/env python3
"""
Service Watchdog

Lightweight monitoring and auto-restart daemon for Hearthlink services.
Integrates with circuit breaker system and service recovery manager.
"""

import time
import asyncio
import threading
import subprocess
import signal
import sys
import json
import logging
from typing import Dict, List
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServiceWatchdog:
    """
    Lightweight service watchdog for automatic service management
    """
    
    def __init__(self):
        self.services = {
            'local_llm': {
                'command': ['python3', 'src/api/local_llm_api.py'],
                'port': 8001,
                'critical': True,
                'restart_delay': 5,
                'max_failures': 3
            },
            'core_api': {
                'command': ['python3', 'src/api/core_api.py'],
                'port': 8000,
                'critical': True,
                'restart_delay': 5,
                'max_failures': 3
            },
            'vault_api': {
                'command': ['python3', 'src/api/vault_api.py'],
                'port': 8002,
                'critical': True,
                'restart_delay': 5,
                'max_failures': 3
            },
            'synapse_api': {
                'command': ['python3', 'src/api/synapse_api_server.py'],
                'port': 8003,
                'critical': False,
                'restart_delay': 5,
                'max_failures': 5
            },
            'sentry_api': {
                'command': ['python3', 'src/api/sentry_api.py'],
                'port': 8004,
                'critical': False,
                'restart_delay': 5,
                'max_failures': 5
            }
        }
        
        self.processes = {}
        self.failure_counts = {}
        self.running = False
        self.shutdown_requested = False
        
    def is_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
            return result == 0
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        
        try:
            # Check if already running
            if service_name in self.processes:
                proc = self.processes[service_name]
                if proc.poll() is None:  # Still running
                    logger.info(f"{service_name} is already running")
                    return True
            
            # Start the service
            logger.info(f"Starting {service_name}...")
            process = subprocess.Popen(
                service['command'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            self.processes[service_name] = process
            
            # Give it time to start
            time.sleep(2)
            
            # Check if it started successfully
            if process.poll() is None and self.is_port_in_use(service['port']):
                logger.info(f"✅ {service_name} started successfully (PID: {process.pid})")
                self.failure_counts[service_name] = 0
                return True
            else:
                logger.error(f"❌ {service_name} failed to start")
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logger.error(f"Error: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.processes:
            logger.info(f"{service_name} is not running")
            return True
        
        try:
            process = self.processes[service_name]
            if process.poll() is None:  # Still running
                logger.info(f"Stopping {service_name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing {service_name}")
                    process.kill()
                    process.wait()
                
                logger.info(f"✅ {service_name} stopped")
            
            del self.processes[service_name]
            return True
            
        except Exception as e:
            logger.error(f"Error stopping {service_name}: {e}")
            return False
    
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        logger.info(f"Restarting {service_name}...")
        
        # Stop first
        self.stop_service(service_name)
        
        # Wait for restart delay
        service = self.services[service_name]
        time.sleep(service['restart_delay'])
        
        # Start again
        return self.start_service(service_name)
    
    def check_service_health(self, service_name: str) -> bool:
        """Check if a service is healthy"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        
        # Check if process is running
        if service_name in self.processes:
            proc = self.processes[service_name]
            if proc.poll() is not None:  # Process died
                return False
        else:
            return False
        
        # Check if port is responding
        return self.is_port_in_use(service['port'])
    
    def monitor_services(self):
        """Main monitoring loop"""
        logger.info("🔍 Starting service monitoring...")
        
        while self.running and not self.shutdown_requested:
            try:
                for service_name in self.services:
                    if not self.check_service_health(service_name):
                        self.handle_service_failure(service_name)
                
                # Sleep between checks
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def handle_service_failure(self, service_name: str):
        """Handle a service failure"""
        service = self.services[service_name]
        
        # Increment failure count
        self.failure_counts[service_name] = self.failure_counts.get(service_name, 0) + 1
        failure_count = self.failure_counts[service_name]
        
        logger.warning(f"⚠️ {service_name} is unhealthy (failure #{failure_count})")
        
        # Check if we should attempt restart
        if failure_count <= service['max_failures']:
            logger.info(f"🔄 Attempting to restart {service_name}")
            
            if self.restart_service(service_name):
                logger.info(f"✅ Successfully restarted {service_name}")
            else:
                logger.error(f"❌ Failed to restart {service_name}")
        else:
            if service['critical']:
                logger.critical(f"🚨 Critical service {service_name} exceeded failure limit!")
                # Could trigger emergency protocols here
            else:
                logger.error(f"💀 Service {service_name} exceeded failure limit, giving up")
    
    def start_all_services(self):
        """Start all services"""
        logger.info("🚀 Starting all services...")
        
        success_count = 0
        for service_name in self.services:
            if self.start_service(service_name):
                success_count += 1
        
        logger.info(f"✅ Started {success_count}/{len(self.services)} services")
        return success_count == len(self.services)
    
    def stop_all_services(self):
        """Stop all services"""
        logger.info("🛑 Stopping all services...")
        
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
        
        logger.info("✅ All services stopped")
    
    def get_status(self) -> Dict:
        """Get current status of all services"""
        status = {
            'watchdog_running': self.running,
            'services': {},
            'summary': {
                'total': len(self.services),
                'running': 0,
                'healthy': 0,
                'failed': 0
            }
        }
        
        for service_name in self.services:
            is_healthy = self.check_service_health(service_name)
            is_running = service_name in self.processes and self.processes[service_name].poll() is None
            
            status['services'][service_name] = {
                'running': is_running,
                'healthy': is_healthy,
                'failure_count': self.failure_counts.get(service_name, 0),
                'pid': self.processes[service_name].pid if service_name in self.processes else None,
                'critical': self.services[service_name]['critical']
            }
            
            if is_running:
                status['summary']['running'] += 1
            if is_healthy:
                status['summary']['healthy'] += 1
            else:
                status['summary']['failed'] += 1
        
        return status
    
    def start(self):
        """Start the watchdog"""
        if self.running:
            logger.warning("Watchdog is already running")
            return
        
        logger.info("🐕 Starting Service Watchdog")
        self.running = True
        
        # Start all services first
        self.start_all_services()
        
        # Start monitoring in background thread
        self.monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🐕 Watchdog started and monitoring")
    
    def stop(self):
        """Stop the watchdog"""
        if not self.running:
            return
        
        logger.info("🛑 Stopping Service Watchdog")
        self.shutdown_requested = True
        self.running = False
        
        # Stop all services
        self.stop_all_services()
        
        # Wait for monitor thread to finish
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        
        logger.info("🐕 Watchdog stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def run_daemon(self):
        """Run as a daemon process"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            self.start()
            
            # Keep running until shutdown
            while self.running and not self.shutdown_requested:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.stop()

def create_watchdog_service():
    """Create a systemd service file for the watchdog"""
    service_content = f"""[Unit]
Description=Hearthlink Service Watchdog
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'hearthlink')}
WorkingDirectory={Path.cwd()}
ExecStart=/usr/bin/python3 {Path.cwd()}/src/utils/service_watchdog.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path('/etc/systemd/system/hearthlink-watchdog.service')
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Created systemd service: {service_file}")
        print("To enable and start:")
        print("  sudo systemctl daemon-reload")
        print("  sudo systemctl enable hearthlink-watchdog")
        print("  sudo systemctl start hearthlink-watchdog")
        
    except PermissionError:
        print("❌ Permission denied. Run with sudo to create systemd service.")
        print("Or manually create the service file:")
        print(service_content)

if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Hearthlink Service Watchdog')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--start', action='store_true', help='Start all services')
    parser.add_argument('--stop', action='store_true', help='Stop all services')
    parser.add_argument('--restart', help='Restart specific service')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--create-service', action='store_true', help='Create systemd service')
    
    args = parser.parse_args()
    
    watchdog = ServiceWatchdog()
    
    if args.daemon:
        watchdog.run_daemon()
    
    elif args.start:
        watchdog.start_all_services()
    
    elif args.stop:
        watchdog.stop_all_services()
    
    elif args.restart:
        if watchdog.restart_service(args.restart):
            print(f"✅ Restarted {args.restart}")
        else:
            print(f"❌ Failed to restart {args.restart}")
    
    elif args.status:
        status = watchdog.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.create_service:
        create_watchdog_service()
    
    else:
        parser.print_help()