#!/usr/bin/env python3
"""
Hearthlink Service Orchestrator
Unified service management with dynamic port allocation and conflict resolution
"""

import os
import sys
import time
import json
import signal
import psutil
import subprocess
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceConfig:
    """Service configuration"""
    def __init__(self, name: str, script_path: str, port: int, 
                 health_endpoint: str = None, dependencies: List[str] = None):
        self.name = name
        self.script_path = script_path
        self.port = port
        self.health_endpoint = health_endpoint or f"http://localhost:{port}/status"
        self.dependencies = dependencies or []
        self.process = None
        self.restart_count = 0
        self.last_restart = None

class ServiceOrchestrator:
    """Main service orchestrator with conflict resolution"""
    
    def __init__(self):
        self.services: Dict[str, ServiceConfig] = {}
        self.running = False
        self.port_registry: Dict[int, str] = {}
        
        # Define service configurations
        self._setup_services()
    
    def _setup_services(self):
        """Setup service configurations with dynamic port allocation"""
        
        # Core services with fixed ports
        base_services = [
            ServiceConfig(
                name="local_llm_api",
                script_path="src/api/local_llm_api.py", 
                port=8001,
                health_endpoint="http://localhost:8001/status"
            ),
            ServiceConfig(
                name="simple_alden_backend",
                script_path="simple_alden_backend.py",
                port=8888,
                health_endpoint="http://localhost:8888/status"
            ),
            ServiceConfig(
                name="synapse_api",
                script_path="src/api/synapse_api_server.py",
                port=8002,
                health_endpoint="http://localhost:8002/status"
            )
        ]
        
        # Add services to registry
        for service in base_services:
            self.services[service.name] = service
            self.port_registry[service.port] = service.name
    
    def find_available_port(self, start_port: int = 8000, end_port: int = 9000) -> int:
        """Find an available port in the given range"""
        for port in range(start_port, end_port):
            if not self._is_port_occupied(port) and port not in self.port_registry:
                return port
        raise RuntimeError(f"No available ports found in range {start_port}-{end_port}")
    
    def _is_port_occupied(self, port: int) -> bool:
        """Check if a port is currently occupied"""
        try:
            for conn in psutil.net_connections():
                if hasattr(conn, 'laddr') and conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
        except Exception:
            # Fallback: try to bind to the port
            import socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', port))
                sock.close()
                return False
            except OSError:
                return True
        return False
    
    def kill_conflicting_processes(self):
        """Kill processes that might conflict with our services"""
        logger.info("Checking for conflicting processes...")
        
        conflicts_found = False
        try:
            # Get all network connections first
            connections = psutil.net_connections()
            port_to_pid = {}
            
            for conn in connections:
                if hasattr(conn, 'laddr') and conn.laddr.port in self.port_registry and conn.status == 'LISTEN':
                    port_to_pid[conn.laddr.port] = conn.pid
            
            # Kill processes using our target ports
            for port, pid in port_to_pid.items():
                if pid:
                    try:
                        proc = psutil.Process(pid)
                        cmdline = ' '.join(proc.cmdline()) if proc.cmdline() else ''
                        
                        # Don't kill if it's already our service
                        service_name = self.port_registry[port]
                        if service_name in cmdline or 'service_orchestrator' in cmdline:
                            continue
                            
                        logger.warning(f"Killing conflicting process PID {pid} on port {port}")
                        logger.warning(f"Command: {cmdline}")
                        
                        proc.terminate()
                        conflicts_found = True
                        
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            if conflicts_found:
                logger.info("Waiting 3 seconds for processes to terminate...")
                time.sleep(3)
                
                # Force kill any remaining processes
                for port, pid in port_to_pid.items():
                    if pid and self._is_port_occupied(port):
                        try:
                            proc = psutil.Process(pid)
                            logger.warning(f"Force killing PID {pid}")
                            proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                            
        except Exception as e:
            logger.warning(f"Error in process cleanup: {e}, continuing anyway...")
            pass
    
    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        
        # Check if already running
        if service.process and service.process.poll() is None:
            logger.info(f"Service {service_name} already running")
            return True
        
        # Check if port is available
        if self._is_port_occupied(service.port):
            logger.error(f"Port {service.port} is occupied, cannot start {service_name}")
            return False
        
        # Start the service
        logger.info(f"Starting {service_name} on port {service.port}...")
        
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()
            
            service.process = subprocess.Popen([
                sys.executable, service.script_path
            ], env=env, cwd=os.getcwd())
            
            service.last_restart = datetime.now()
            service.restart_count += 1
            
            # Wait a moment for startup
            time.sleep(2)
            
            # Check if process is still running
            if service.process.poll() is None:
                logger.info(f"✅ {service_name} started successfully (PID {service.process.pid})")
                return True
            else:
                logger.error(f"❌ {service_name} failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start {service_name}: {e}")
            return False
    
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.services:
            return False
        
        service = self.services[service_name]
        
        if service.process:
            logger.info(f"Stopping {service_name}...")
            try:
                service.process.terminate()
                service.process.wait(timeout=5)
                logger.info(f"✅ {service_name} stopped")
                return True
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {service_name}")
                service.process.kill()
                return True
            except Exception as e:
                logger.error(f"Error stopping {service_name}: {e}")
                return False
        
        return True
    
    def start_all_services(self):
        """Start all services in dependency order"""
        logger.info("🚀 Starting Hearthlink Service Orchestrator")
        
        # Kill conflicting processes first
        self.kill_conflicting_processes()
        
        # Start services
        service_order = ["local_llm_api", "simple_alden_backend", "synapse_api"]
        
        for service_name in service_order:
            if not self.start_service(service_name):
                logger.error(f"Failed to start {service_name}, continuing with others...")
                continue
            
            # Brief pause between services
            time.sleep(1)
        
        logger.info("🎯 Service startup complete")
        self.running = True
    
    def stop_all_services(self):
        """Stop all services"""
        logger.info("🛑 Stopping all services...")
        self.running = False
        
        for service_name in self.services:
            self.stop_service(service_name)
        
        logger.info("✅ All services stopped")
    
    def get_service_status(self) -> Dict:
        """Get status of all services"""
        status = {
            "orchestrator_running": self.running,
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        for name, service in self.services.items():
            service_status = {
                "running": service.process and service.process.poll() is None,
                "port": service.port,
                "restart_count": service.restart_count,
                "last_restart": service.last_restart.isoformat() if service.last_restart else None,
                "pid": service.process.pid if service.process and service.process.poll() is None else None
            }
            status["services"][name] = service_status
        
        return status
    
    def health_check_loop(self):
        """Continuous health checking and auto-restart"""
        while self.running:
            try:
                for name, service in self.services.items():
                    if service.process and service.process.poll() is not None:
                        logger.warning(f"Service {name} has died, attempting restart...")
                        self.start_service(name)
                
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(5)
    
    def run(self):
        """Main orchestrator run loop"""
        try:
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Start all services
            self.start_all_services()
            
            # Start health check in background
            health_thread = threading.Thread(target=self.health_check_loop, daemon=True)
            health_thread.start()
            
            # Print status
            self.print_status()
            
            # Keep running
            logger.info("🔄 Orchestrator running. Press Ctrl+C to stop.")
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop_all_services()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        self.running = False
    
    def print_status(self):
        """Print current service status"""
        print("\n" + "="*60)
        print("🎮 HEARTHLINK SERVICE ORCHESTRATOR")
        print("="*60)
        
        status = self.get_service_status()
        for name, service_info in status["services"].items():
            status_icon = "✅" if service_info["running"] else "❌"
            port = service_info["port"]
            pid = service_info["pid"] or "N/A"
            print(f"{status_icon} {name:<20} Port: {port:<5} PID: {pid}")
        
        print("="*60)
        print("🌐 Service URLs:")
        print(f"   LLM API:           http://localhost:8001")
        print(f"   Alden Backend:     http://localhost:8888") 
        print(f"   Synapse API:       http://localhost:8002")
        print(f"   React Dev Server:  http://localhost:3005 (separate)")
        print("="*60)

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        orchestrator = ServiceOrchestrator()
        
        if command == "start":
            orchestrator.run()
        elif command == "stop":
            orchestrator.stop_all_services()
        elif command == "status":
            orchestrator.print_status()
        elif command == "clean":
            orchestrator.kill_conflicting_processes()
            print("🧹 Cleaned up conflicting processes")
        else:
            print("Usage: python service_orchestrator.py [start|stop|status|clean]")
    else:
        # Default: start orchestrator
        orchestrator = ServiceOrchestrator()
        orchestrator.run()

if __name__ == "__main__":
    main()