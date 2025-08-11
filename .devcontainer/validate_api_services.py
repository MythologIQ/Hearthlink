#!/usr/bin/env python3
"""
API Services Validation for Codespaces
Verifies all backend services can start and respond to health checks
"""

import requests
import subprocess
import time
import sys
import json
from concurrent.futures import ThreadPoolExecutor
import signal
import os

class APIValidator:
    def __init__(self):
        self.services = {
            'core': {'port': 8000, 'script': 'src/api/core_api.py'},
            'vault': {'port': 8001, 'script': 'src/vault/vault_api_server.py'},
            'synapse': {'port': 8002, 'script': 'src/api/synapse_api_server.py'},
            'alden': {'port': 8888, 'script': 'src/api/alden_api.py'}
        }
        self.processes = {}
        
    def start_service(self, name, config):
        """Start a single service"""
        print(f"🚀 Starting {name} service...")
        try:
            process = subprocess.Popen([
                'python3', config['script'],
                '--host', '127.0.0.1',
                '--port', str(config['port'])
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes[name] = process
            time.sleep(2)  # Give service time to start
            
            if process.poll() is None:
                print(f"✅ {name} service started on port {config['port']}")
                return True
            else:
                print(f"❌ {name} service failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {name}: {e}")
            return False
    
    def check_health(self, name, port):
        """Check service health endpoint"""
        url = f"http://127.0.0.1:{port}/health"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} health check passed")
                return True
            else:
                print(f"❌ {name} health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ {name} health check error: {e}")
            return False
    
    def cleanup(self):
        """Stop all services"""
        print("🧹 Cleaning up services...")
        for name, process in self.processes.items():
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print(f"✅ {name} service stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"🔨 {name} service force killed")
    
    def run_validation(self):
        """Run complete validation suite"""
        print("📡 Hearthlink API Services Validation")
        print("=" * 50)
        
        results = {}
        
        # Start all services
        for name, config in self.services.items():
            results[name] = self.start_service(name, config)
        
        # Wait for startup
        time.sleep(5)
        
        # Health checks
        health_results = {}
        for name, config in self.services.items():
            if results[name]:
                health_results[name] = self.check_health(name, config['port'])
            else:
                health_results[name] = False
        
        # Summary
        print("\n📊 Validation Summary:")
        print("-" * 30)
        
        all_passed = True
        for name in self.services:
            startup = "✅" if results[name] else "❌"
            health = "✅" if health_results[name] else "❌"
            print(f"{name:8} | Startup: {startup} | Health: {health}")
            
            if not (results[name] and health_results[name]):
                all_passed = False
        
        if all_passed:
            print("\n🎉 All services validated successfully!")
            return 0
        else:
            print("\n⚠️  Some services failed validation")
            return 1

def main():
    validator = APIValidator()
    
    def signal_handler(signum, frame):
        print("\n🛑 Received interrupt signal")
        validator.cleanup()
        sys.exit(1)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        exit_code = validator.run_validation()
        return exit_code
    finally:
        validator.cleanup()

if __name__ == "__main__":
    sys.exit(main())