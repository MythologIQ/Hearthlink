#!/usr/bin/env python3
"""
UI Test Environment Setup
Enforces preconditions for UI testing including fresh session state, logging, and resource monitoring.
"""

import os
import sys
import time
import json
import logging
import psutil
from pathlib import Path
from datetime import datetime

class UITestEnvironment:
    """UI Test Environment Setup and Management"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.logs_dir = self.project_root / "logs" / "tests" / "ui"
        self.results_dir = self.project_root / "tests" / "results" / "ui"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup test logging to /logs/tests/ui/ with timestamp"""
        log_file = self.logs_dir / f"ui_test_{self.timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("UI_TEST_ENV")
        self.logger.info(f"UI Test Environment initialized at {self.timestamp}")
        
    def initialize_fresh_session_state(self):
        """Initialize with fresh session state for UI testing"""
        self.logger.info("Initializing fresh session state")
        
        # Clear any existing session data
        session_files = [
            ".session_cache",
            "session_state.json",
            "ui_state.json"
        ]
        
        for session_file in session_files:
            session_path = self.project_root / session_file
            if session_path.exists():
                session_path.unlink()
                self.logger.info(f"Cleared session file: {session_file}")
        
        # Reset UI context if needed
        self.reset_ui_context()
        
        self.logger.info("Fresh session state initialized")
        
    def reset_ui_context(self):
        """Reset UI context for idempotent testing"""
        self.logger.info("Resetting UI context")
        
        # Clear any UI-specific state
        ui_state_files = [
            "ui_context.json",
            "voice_state.json",
            "agent_state.json"
        ]
        
        for state_file in ui_state_files:
            state_path = self.project_root / state_file
            if state_path.exists():
                state_path.unlink()
                self.logger.info(f"Cleared UI state file: {state_file}")
                
    def monitor_resources(self, test_name):
        """Monitor system resources during UI testing"""
        self.logger.info(f"Starting resource monitoring for test: {test_name}")
        
        # Get initial resource state
        initial_cpu = psutil.cpu_percent(interval=1)
        initial_memory = psutil.virtual_memory().percent
        initial_disk = psutil.disk_usage('/').percent
        
        resource_data = {
            "test_name": test_name,
            "timestamp": self.timestamp,
            "initial_state": {
                "cpu_percent": initial_cpu,
                "memory_percent": initial_memory,
                "disk_percent": initial_disk
            },
            "monitoring_start": time.time()
        }
        
        return resource_data
        
    def finalize_resource_monitoring(self, resource_data):
        """Finalize resource monitoring and log results"""
        final_cpu = psutil.cpu_percent(interval=1)
        final_memory = psutil.virtual_memory().percent
        final_disk = psutil.disk_usage('/').percent
        
        resource_data["final_state"] = {
            "cpu_percent": final_cpu,
            "memory_percent": final_memory,
            "disk_percent": final_disk
        }
        resource_data["monitoring_end"] = time.time()
        resource_data["duration"] = resource_data["monitoring_end"] - resource_data["monitoring_start"]
        
        # Log resource usage
        self.logger.info(f"Resource monitoring completed for {resource_data['test_name']}")
        self.logger.info(f"CPU: {resource_data['initial_state']['cpu_percent']}% -> {final_cpu}%")
        self.logger.info(f"Memory: {resource_data['initial_state']['memory_percent']}% -> {final_memory}%")
        self.logger.info(f"Disk: {resource_data['initial_state']['disk_percent']}% -> {final_disk}%")
        
        return resource_data
        
    def save_test_results(self, test_name, results, resource_data=None):
        """Save test results to /tests/results/ui/ in JSON format"""
        result_file = self.results_dir / f"{test_name}_{self.timestamp}.json"
        
        test_result = {
            "test_name": test_name,
            "timestamp": self.timestamp,
            "results": results,
            "resource_data": resource_data,
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(self.project_root)
            }
        }
        
        with open(result_file, 'w') as f:
            json.dump(test_result, f, indent=2)
            
        self.logger.info(f"Test results saved to: {result_file}")
        return result_file
        
    def cleanup_environment(self):
        """Cleanup test environment"""
        self.logger.info("Cleaning up UI test environment")
        
        # Clear any temporary files created during testing
        temp_files = [
            "temp_ui_state.json",
            "test_session.json",
            "voice_test_log.json"
        ]
        
        for temp_file in temp_files:
            temp_path = self.project_root / temp_file
            if temp_path.exists():
                temp_path.unlink()
                self.logger.info(f"Cleared temp file: {temp_file}")
                
        self.logger.info("UI test environment cleanup completed")

def setup_ui_test_environment():
    """Setup UI test environment with all required preconditions"""
    env = UITestEnvironment()
    
    # Initialize fresh session state
    env.initialize_fresh_session_state()
    
    return env

if __name__ == "__main__":
    # Test the environment setup
    env = setup_ui_test_environment()
    print("UI Test Environment setup completed successfully")
    print(f"Logs directory: {env.logs_dir}")
    print(f"Results directory: {env.results_dir}") 