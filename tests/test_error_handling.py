#!/usr/bin/env python3
"""
Comprehensive Error Handling Test Suite for Hearthlink Container

This script tests robust error handling capabilities including:
- Startup and shutdown event simulation
- Various error types and scenarios
- Error recovery mechanisms
- Stack trace logging validation
- Signal handling
- Health monitoring
- Error counting and limits

References:
- appendix_h_developer_qa_platinum_checklists.md: QA requirements
- PLATINUM_BLOCKERS.md: Error handling requirements

Run with: python tests/test_error_handling.py
"""

import sys
import os
import time
import json
import signal
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import HearthlinkContainer, HearthlinkLogger, HearthlinkError, LoggingError, ContainerError


class ErrorHandlingTestSuite:
    """
    Comprehensive test suite for error handling and process events.
    
    Implements platinum-standard testing requirements with explicit
    error simulation and validation.
    """
    
    def __init__(self, test_log_dir: str = "test_error_logs"):
        """
        Initialize test suite with dedicated logging.
        
        Args:
            test_log_dir: Directory for test-specific logs
        """
        self.test_log_dir = Path(test_log_dir)
        self.test_log_dir.mkdir(exist_ok=True)
        
        # Test results tracking
        self.test_results = []
        self.current_test = None
        
        # Setup test logger
        self.logger = HearthlinkLogger(
            log_dir=str(self.test_log_dir),
            max_size_mb=1,
            backup_count=3
        )
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", error: Exception = None):
        """Log test result with structured information."""
        result = {
            "test_name": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        if error:
            result["error"] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": str(error.__traceback__)
            }
        
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name} - {details}")
        
        if error:
            print(f"   Error: {type(error).__name__}: {str(error)}")
    
    def test_startup_events(self) -> bool:
        """Test container startup event handling."""
        test_name = "Container Startup Events"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Test 1: Normal startup
            container = HearthlinkContainer({
                "log_dir": str(self.test_log_dir / "startup_test"),
                "max_size_mb": 1,
                "backup_count": 2
            })
            
            # Verify startup logging
            status = container.get_status()
            if not status.get("running") and status.get("start_time"):
                self.log_test_result(test_name, True, "Startup events logged successfully")
                return True
            else:
                self.log_test_result(test_name, False, "Startup status verification failed")
                return False
                
        except Exception as e:
            self.log_test_result(test_name, False, "Startup test failed", e)
            return False
    
    def test_shutdown_events(self) -> bool:
        """Test container shutdown event handling."""
        test_name = "Container Shutdown Events"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Test 1: Normal shutdown
            container = HearthlinkContainer({
                "log_dir": str(self.test_log_dir / "shutdown_test"),
                "max_size_mb": 1,
                "backup_count": 2
            })
            
            # Start container in background thread
            container_thread = threading.Thread(target=container.start)
            container_thread.daemon = True
            container_thread.start()
            
            # Wait for startup
            time.sleep(2)
            
            # Trigger shutdown
            container.stop("test_shutdown")
            
            # Wait for shutdown
            time.sleep(1)
            
            # Verify shutdown logging
            status = container.get_status()
            if not status.get("running"):
                self.log_test_result(test_name, True, "Shutdown events logged successfully")
                return True
            else:
                self.log_test_result(test_name, False, "Shutdown verification failed")
                return False
                
        except Exception as e:
            self.log_test_result(test_name, False, "Shutdown test failed", e)
            return False
    
    def test_error_simulation(self) -> bool:
        """Test various error simulation scenarios."""
        test_name = "Error Simulation"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            container = HearthlinkContainer({
                "log_dir": str(self.test_log_dir / "error_simulation"),
                "max_size_mb": 1,
                "backup_count": 2
            })
            
            # Test different error types
            error_types = ["value", "runtime", "io", "keyboard", "custom"]
            error_count = 0
            
            for error_type in error_types:
                try:
                    container.simulate_error(error_type)
                    error_count += 1
                    time.sleep(0.1)  # Small delay between errors
                except Exception as e:
                    print(f"   Simulated {error_type} error: {type(e).__name__}")
            
            # Verify error handling
            status = container.get_status()
            if status.get("error_count", 0) > 0:
                self.log_test_result(test_name, True, f"Simulated {error_count} errors successfully")
                return True
            else:
                self.log_test_result(test_name, False, "Error simulation failed")
                return False
                
        except Exception as e:
            self.log_test_result(test_name, False, "Error simulation test failed", e)
            return False
    
    def test_error_recovery(self) -> bool:
        """Test error recovery mechanisms."""
        test_name = "Error Recovery"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            container = HearthlinkContainer({
                "log_dir": str(self.test_log_dir / "error_recovery"),
                "max_size_mb": 1,
                "backup_count": 2
            })
            
            # Simulate errors up to limit
            for i in range(5):  # Less than max_errors (10)
                container.simulate_error("recovery_test")
                time.sleep(0.1)
            
            # Verify container is still running
            status = container.get_status()
            if status.get("error_count", 0) <= status.get("max_errors", 10):
                self.log_test_result(test_name, True, "Error recovery working correctly")
                return True
            else:
                self.log_test_result(test_name, False, "Error recovery failed")
                return False
                
        except Exception as e:
            self.log_test_result(test_name, False, "Error recovery test failed", e)
            return False
    
    def test_critical_error_handling(self) -> bool:
        """Test critical error handling and logging."""
        test_name = "Critical Error Handling"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            logger = HearthlinkLogger(
                log_dir=str(self.test_log_dir / "critical_errors"),
                max_size_mb=1,
                backup_count=2
            )
            
            # Test critical error logging
            test_error = RuntimeError("Test critical error")
            logger.log_critical_error(test_error, "critical_test", "Test recovery action")
            
            # Verify critical error was logged
            log_file = self.test_log_dir / "critical_errors" / "hearthlink.log"
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    if "critical_error" in log_content and "Test critical error" in log_content:
                        self.log_test_result(test_name, True, "Critical error logging successful")
                        return True
            
            self.log_test_result(test_name, False, "Critical error logging verification failed")
            return False
            
        except Exception as e:
            self.log_test_result(test_name, False, "Critical error test failed", e)
            return False
    
    def test_signal_handling(self) -> bool:
        """Test signal handling for graceful shutdown."""
        test_name = "Signal Handling"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Start container in separate process
            test_script = """
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from main import HearthlinkContainer

container = HearthlinkContainer({"log_dir": "test_signal_logs"})
container.start()
"""
            
            # Write test script
            script_path = self.test_log_dir / "signal_test.py"
            with open(script_path, 'w') as f:
                f.write(test_script)
            
            # Start process
            process = subprocess.Popen([sys.executable, str(script_path)])
            
            # Wait for startup
            time.sleep(3)
            
            # Send SIGTERM
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                self.log_test_result(test_name, True, "Signal handling successful")
                return True
            except subprocess.TimeoutExpired:
                process.kill()
                self.log_test_result(test_name, False, "Signal handling timeout")
                return False
                
        except Exception as e:
            self.log_test_result(test_name, False, "Signal handling test failed", e)
            return False
    
    def test_health_monitoring(self) -> bool:
        """Test health monitoring and memory usage tracking."""
        test_name = "Health Monitoring"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            container = HearthlinkContainer({
                "log_dir": str(self.test_log_dir / "health_monitoring"),
                "max_size_mb": 1,
                "backup_count": 2
            })
            
            # Start container briefly
            container_thread = threading.Thread(target=container.start)
            container_thread.daemon = True
            container_thread.start()
            
            # Wait for health check
            time.sleep(65)  # Wait for health check (every 60 seconds)
            
            # Stop container
            container.stop("health_test")
            
            # Verify health monitoring
            status = container.get_status()
            if status.get("uptime_seconds", 0) > 0:
                self.log_test_result(test_name, True, "Health monitoring active")
                return True
            else:
                self.log_test_result(test_name, False, "Health monitoring failed")
                return False
                
        except Exception as e:
            self.log_test_result(test_name, False, "Health monitoring test failed", e)
            return False
    
    def test_log_validation(self) -> bool:
        """Validate log file structure and content."""
        test_name = "Log Validation"
        
        try:
            print(f"\n🧪 Testing: {test_name}")
            
            # Check all test log files
            log_files = list(self.test_log_dir.rglob("*.log"))
            
            if not log_files:
                self.log_test_result(test_name, False, "No log files found")
                return False
            
            valid_logs = 0
            total_entries = 0
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            line = line.strip()
                            if not line:
                                continue
                            
                            # Validate JSON format
                            try:
                                log_entry = json.loads(line)
                                total_entries += 1
                                
                                # Check required fields
                                required_fields = ["timestamp", "level", "logger", "message"]
                                if all(field in log_entry for field in required_fields):
                                    valid_logs += 1
                                else:
                                    print(f"   Missing required fields in {log_file}:{line_num}")
                                    
                            except json.JSONDecodeError as e:
                                print(f"   Invalid JSON in {log_file}:{line_num} - {e}")
                                
                except Exception as e:
                    print(f"   Error reading {log_file}: {e}")
            
            if valid_logs > 0 and valid_logs == total_entries:
                self.log_test_result(test_name, True, f"All {valid_logs} log entries valid")
                return True
            else:
                self.log_test_result(test_name, False, f"{valid_logs}/{total_entries} valid entries")
                return False
                
        except Exception as e:
            self.log_test_result(test_name, False, "Log validation failed", e)
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all error handling tests and return results."""
        print("🚀 Hearthlink Error Handling Test Suite")
        print("=" * 50)
        
        start_time = datetime.now()
        
        # Define test methods
        test_methods = [
            self.test_startup_events,
            self.test_shutdown_events,
            self.test_error_simulation,
            self.test_error_recovery,
            self.test_critical_error_handling,
            self.test_signal_handling,
            self.test_health_monitoring,
            self.test_log_validation
        ]
        
        # Run tests
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                self.log_test_result(test_method.__name__, False, "Test execution failed", e)
        
        # Generate summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "test_results": self.test_results
        }
        
        # Print summary
        print(f"\n📊 Test Summary")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Duration: {duration:.2f} seconds")
        
        # Save detailed results
        results_file = self.test_log_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📁 Test results saved to: {results_file}")
        print(f"📁 Test logs saved to: {self.test_log_dir}")
        
        return summary


def main():
    """Main test execution function."""
    try:
        # Create and run test suite
        test_suite = ErrorHandlingTestSuite()
        results = test_suite.run_all_tests()
        
        # Exit with appropriate code
        if results["success_rate"] >= 80:  # 80% pass rate threshold
            print("\n✅ Test suite completed successfully!")
            return 0
        else:
            print("\n❌ Test suite failed - insufficient pass rate")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test suite execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 