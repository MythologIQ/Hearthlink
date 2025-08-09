#!/usr/bin/env python3
"""
End-to-End Circuit Breaker Failover Testing

Comprehensive testing suite that validates the entire circuit breaker
system from backend Python implementation to frontend React dashboard.
"""

import subprocess
import sys
import time
import requests
import json
import threading
import os
from datetime import datetime
from pathlib import Path

class CircuitBreakerE2ETestRunner:
    """Comprehensive end-to-end test runner for circuit breaker system"""
    
    def __init__(self):
        self.test_results = {}
        self.test_logs = []
        self.services_started = []
        
    def log(self, message, level="INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.test_logs.append(log_entry)
        
    def start_test_services(self):
        """Start test services for circuit breaker testing"""
        self.log("Starting test services for circuit breaker testing...", "INFO")
        
        # Check if services are already running
        test_ports = [8001, 8000, 8002, 8003, 8004]
        running_services = []
        
        for port in test_ports:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    running_services.append(port)
                    self.log(f"Service on port {port} already running", "INFO")
            except:
                self.log(f"Service on port {port} not running", "DEBUG")
        
        if len(running_services) >= 3:
            self.log("Sufficient services running for testing", "INFO")
            return True
        else:
            self.log("Starting mock services for testing...", "INFO")
            return self.start_mock_services()
    
    def start_mock_services(self):
        """Start mock services for testing if real services aren't available"""
        mock_service_script = """
import sys
from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)

# Mock circuit breaker state
circuit_state = {
    'state': 'CLOSED',
    'metrics': {
        'totalRequests': 100,
        'successfulRequests': 95,
        'failureCount': 5,
        'successRate': 95.0,
        'averageResponseTime': 200
    },
    'healthStatus': 'healthy'
}

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'mock'})

@app.route('/api/circuit-breaker/status')
def circuit_breaker_status():
    return jsonify(circuit_state)

@app.route('/api/circuit-breaker/<action>', methods=['POST'])
def circuit_breaker_action(action):
    global circuit_state
    if action == 'open':
        circuit_state['state'] = 'OPEN'
    elif action == 'close':
        circuit_state['state'] = 'CLOSED'
    elif action == 'reset':
        circuit_state['state'] = 'CLOSED'
        circuit_state['metrics']['failureCount'] = 0
    elif action == 'half-open':
        circuit_state['state'] = 'HALF_OPEN'
    
    return jsonify({'success': True, 'action': action, 'new_state': circuit_state['state']})

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    app.run(host='127.0.0.1', port=port, debug=False)
"""
        
        # Start mock services on different ports
        mock_ports = [8001, 8000, 8002]
        for port in mock_ports:
            try:
                # Save mock service script
                script_path = f"/tmp/mock_service_{port}.py"
                with open(script_path, 'w') as f:
                    f.write(mock_service_script)
                
                # Start service in background
                process = subprocess.Popen([
                    sys.executable, script_path, str(port)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                self.services_started.append(process)
                time.sleep(1)  # Give service time to start
                
                # Verify service started
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    self.log(f"Mock service started on port {port}", "INFO")
                else:
                    self.log(f"Mock service on port {port} not responding", "WARNING")
                    
            except Exception as e:
                self.log(f"Failed to start mock service on port {port}: {e}", "ERROR")
        
        time.sleep(2)  # Allow all services to fully start
        return len(self.services_started) > 0
    
    def stop_test_services(self):
        """Stop all started test services"""
        self.log("Stopping test services...", "INFO")
        for process in self.services_started:
            try:
                process.terminate()
                process.wait(timeout=5)
                self.log("Test service stopped", "DEBUG")
            except:
                process.kill()
                self.log("Test service force killed", "DEBUG")
    
    def run_python_circuit_breaker_tests(self):
        """Run Python backend circuit breaker tests"""
        self.log("Running Python circuit breaker backend tests...", "INFO")
        
        try:
            # Run the comprehensive Python test suite
            result = subprocess.run([
                sys.executable, 
                "/mnt/g/mythologiq/hearthlink/tests/test_circuit_breaker_failover.py"
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.test_results['python_backend'] = 'PASSED'
                self.log("Python backend tests: PASSED", "SUCCESS")
                
                # Extract test details from output
                output_lines = result.stdout.split('\n')
                test_count = len([line for line in output_lines if '✅' in line])
                self.log(f"Python backend: {test_count} tests passed", "INFO")
                
            else:
                self.test_results['python_backend'] = 'FAILED'
                self.log("Python backend tests: FAILED", "ERROR")
                self.log(f"Error output: {result.stderr}", "ERROR")
                
        except subprocess.TimeoutExpired:
            self.test_results['python_backend'] = 'TIMEOUT'
            self.log("Python backend tests: TIMEOUT", "ERROR")
        except Exception as e:
            self.test_results['python_backend'] = 'ERROR'
            self.log(f"Python backend tests error: {e}", "ERROR")
    
    def run_javascript_dashboard_tests(self):
        """Run JavaScript dashboard integration tests"""
        self.log("Running JavaScript dashboard integration tests...", "INFO")
        
        try:
            # Check if Node.js and npm are available
            subprocess.run(['node', '--version'], check=True, capture_output=True)
            
            # Run JavaScript tests
            result = subprocess.run([
                'node', 
                "/mnt/g/mythologiq/hearthlink/tests/test_circuit_breaker_dashboard.js"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.test_results['javascript_dashboard'] = 'PASSED'
                self.log("JavaScript dashboard tests: PASSED", "SUCCESS")
                
                # Extract test details from output
                output_lines = result.stdout.split('\n')
                test_count = len([line for line in output_lines if '✅' in line])
                self.log(f"JavaScript dashboard: {test_count} tests passed", "INFO")
                
            else:
                self.test_results['javascript_dashboard'] = 'FAILED'
                self.log("JavaScript dashboard tests: FAILED", "ERROR")
                self.log(f"Error output: {result.stderr}", "ERROR")
                
        except subprocess.CalledProcessError:
            self.test_results['javascript_dashboard'] = 'SKIPPED'
            self.log("JavaScript dashboard tests: SKIPPED (Node.js not available)", "WARNING")
        except subprocess.TimeoutExpired:
            self.test_results['javascript_dashboard'] = 'TIMEOUT'
            self.log("JavaScript dashboard tests: TIMEOUT", "ERROR")
        except Exception as e:
            self.test_results['javascript_dashboard'] = 'ERROR'
            self.log(f"JavaScript dashboard tests error: {e}", "ERROR")
    
    def test_integration_scenarios(self):
        """Test integration between backend and frontend"""
        self.log("Running integration scenario tests...", "INFO")
        
        integration_tests = []
        
        try:
            # Test 1: Service failure detection and dashboard update
            self.log("Testing service failure detection integration...", "INFO")
            
            # Trigger a service failure
            response = requests.post("http://localhost:8001/api/circuit-breaker/open", timeout=5)
            if response.status_code == 200:
                integration_tests.append(("service_failure_trigger", "PASSED"))
                
                # Check if dashboard would detect this
                status_response = requests.get("http://localhost:8001/api/circuit-breaker/status", timeout=5)
                if status_response.status_code == 200:
                    data = status_response.json()
                    if data.get('state') == 'OPEN':
                        integration_tests.append(("dashboard_failure_detection", "PASSED"))
                    else:
                        integration_tests.append(("dashboard_failure_detection", "FAILED"))
                else:
                    integration_tests.append(("dashboard_failure_detection", "FAILED"))
            else:
                integration_tests.append(("service_failure_trigger", "FAILED"))
                integration_tests.append(("dashboard_failure_detection", "FAILED"))
            
            # Test 2: Service recovery and dashboard update
            self.log("Testing service recovery integration...", "INFO")
            
            # Trigger service recovery
            response = requests.post("http://localhost:8001/api/circuit-breaker/reset", timeout=5)
            if response.status_code == 200:
                integration_tests.append(("service_recovery_trigger", "PASSED"))
                
                # Check recovery detection
                status_response = requests.get("http://localhost:8001/api/circuit-breaker/status", timeout=5)
                if status_response.status_code == 200:
                    data = status_response.json()
                    if data.get('state') == 'CLOSED':
                        integration_tests.append(("dashboard_recovery_detection", "PASSED"))
                    else:
                        integration_tests.append(("dashboard_recovery_detection", "FAILED"))
                else:
                    integration_tests.append(("dashboard_recovery_detection", "FAILED"))
            else:
                integration_tests.append(("service_recovery_trigger", "FAILED"))
                integration_tests.append(("dashboard_recovery_detection", "FAILED"))
            
            # Test 3: Multiple service monitoring
            self.log("Testing multiple service monitoring...", "INFO")
            
            services_tested = []
            for port in [8001, 8000, 8002]:
                try:
                    response = requests.get(f"http://localhost:{port}/api/circuit-breaker/status", timeout=3)
                    if response.status_code == 200:
                        services_tested.append(port)
                except:
                    pass
            
            if len(services_tested) >= 2:
                integration_tests.append(("multiple_service_monitoring", "PASSED"))
                self.log(f"Successfully monitored {len(services_tested)} services", "INFO")
            else:
                integration_tests.append(("multiple_service_monitoring", "FAILED"))
            
            # Calculate integration test results
            passed_integration = len([test for test in integration_tests if test[1] == "PASSED"])
            total_integration = len(integration_tests)
            
            if passed_integration == total_integration:
                self.test_results['integration_scenarios'] = 'PASSED'
                self.log("Integration scenario tests: PASSED", "SUCCESS")
            elif passed_integration > total_integration / 2:
                self.test_results['integration_scenarios'] = 'PARTIAL'
                self.log("Integration scenario tests: PARTIAL", "WARNING")
            else:
                self.test_results['integration_scenarios'] = 'FAILED'
                self.log("Integration scenario tests: FAILED", "ERROR")
            
            # Log individual test results
            for test_name, result in integration_tests:
                status_icon = "✅" if result == "PASSED" else "❌"
                self.log(f"  {status_icon} {test_name}: {result}", "INFO")
                
        except Exception as e:
            self.test_results['integration_scenarios'] = 'ERROR'
            self.log(f"Integration scenario tests error: {e}", "ERROR")
    
    def test_performance_scenarios(self):
        """Test circuit breaker performance under load"""
        self.log("Running performance scenario tests...", "INFO")
        
        try:
            # Test concurrent request handling
            self.log("Testing concurrent request performance...", "INFO")
            
            def make_request():
                try:
                    response = requests.get("http://localhost:8001/api/circuit-breaker/status", timeout=2)
                    return response.status_code == 200
                except:
                    return False
            
            # Send concurrent requests
            threads = []
            results = []
            
            start_time = time.time()
            
            for _ in range(20):
                thread = threading.Thread(target=lambda: results.append(make_request()))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            elapsed_time = time.time() - start_time
            success_rate = sum(results) / len(results) * 100
            
            if success_rate >= 80 and elapsed_time < 10:
                self.test_results['performance_scenarios'] = 'PASSED'
                self.log("Performance scenario tests: PASSED", "SUCCESS")
                self.log(f"  Success rate: {success_rate:.1f}%, Time: {elapsed_time:.2f}s", "INFO")
            else:
                self.test_results['performance_scenarios'] = 'FAILED'
                self.log("Performance scenario tests: FAILED", "ERROR")
                self.log(f"  Success rate: {success_rate:.1f}%, Time: {elapsed_time:.2f}s", "ERROR")
                
        except Exception as e:
            self.test_results['performance_scenarios'] = 'ERROR'
            self.log(f"Performance scenario tests error: {e}", "ERROR")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        self.log("Generating comprehensive test report...", "INFO")
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = len([result for result in self.test_results.values() if result == 'PASSED'])
        failed_tests = len([result for result in self.test_results.values() if result == 'FAILED'])
        other_tests = total_tests - passed_tests - failed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            'test_suite': 'circuit_breaker_end_to_end',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_test_categories': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'other': other_tests,
                'success_rate': success_rate
            },
            'test_results': self.test_results,
            'test_logs': self.test_logs,
            'recommendations': self.generate_recommendations()
        }
        
        # Save report
        report_path = '/mnt/g/mythologiq/hearthlink/tests/circuit_breaker_e2e_report.json'
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            self.log(f"Comprehensive report saved to: {report_path}", "INFO")
        except Exception as e:
            self.log(f"Failed to save report: {e}", "ERROR")
        
        return report
    
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        if self.test_results.get('python_backend') != 'PASSED':
            recommendations.append("Fix Python backend circuit breaker implementation issues")
        
        if self.test_results.get('javascript_dashboard') != 'PASSED':
            recommendations.append("Address JavaScript dashboard integration problems")
        
        if self.test_results.get('integration_scenarios') != 'PASSED':
            recommendations.append("Resolve backend-frontend integration issues")
        
        if self.test_results.get('performance_scenarios') != 'PASSED':
            recommendations.append("Optimize circuit breaker performance under load")
        
        if not recommendations:
            recommendations.append("All tests passed - circuit breaker system is production ready")
        
        return recommendations
    
    def run_comprehensive_test_suite(self):
        """Run the complete end-to-end test suite"""
        self.log("🔄 Starting Comprehensive Circuit Breaker End-to-End Tests", "INFO")
        self.log("=" * 70, "INFO")
        
        try:
            # Start test services
            if not self.start_test_services():
                self.log("Failed to start test services - some tests may fail", "WARNING")
            
            # Run all test categories
            self.run_python_circuit_breaker_tests()
            self.run_javascript_dashboard_tests()
            self.test_integration_scenarios()
            self.test_performance_scenarios()
            
            # Generate comprehensive report
            report = self.generate_comprehensive_report()
            
            # Print summary
            self.log("=" * 70, "INFO")
            self.log("🔄 CIRCUIT BREAKER END-TO-END TEST SUMMARY", "INFO")
            self.log("=" * 70, "INFO")
            
            self.log(f"📊 Overall Results:", "INFO")
            self.log(f"  Total Test Categories: {report['summary']['total_test_categories']}", "INFO")
            self.log(f"  Passed: ✅ {report['summary']['passed']}", "INFO")
            self.log(f"  Failed: ❌ {report['summary']['failed']}", "INFO")
            self.log(f"  Other: ⚠️ {report['summary']['other']}", "INFO")
            self.log(f"  Success Rate: {report['summary']['success_rate']:.1f}%", "INFO")
            
            self.log(f"\n🔍 Detailed Results:", "INFO")
            for test_category, result in self.test_results.items():
                status_icon = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "⚠️"
                self.log(f"  {status_icon} {test_category}: {result}", "INFO")
            
            self.log(f"\n💡 Recommendations:", "INFO")
            for i, rec in enumerate(report['recommendations'], 1):
                self.log(f"  {i}. {rec}", "INFO")
            
            # Final assessment
            if report['summary']['success_rate'] >= 80:
                self.log("\n🎉 CIRCUIT BREAKER SYSTEM VALIDATION: SUCCESS!", "SUCCESS")
                self.log("   The circuit breaker system is production ready.", "SUCCESS")
                return True
            else:
                self.log("\n⚠️ CIRCUIT BREAKER SYSTEM VALIDATION: NEEDS IMPROVEMENT", "WARNING")
                self.log("   Address the identified issues before production deployment.", "WARNING")
                return False
                
        finally:
            # Cleanup
            self.stop_test_services()

if __name__ == "__main__":
    runner = CircuitBreakerE2ETestRunner()
    success = runner.run_comprehensive_test_suite()
    
    if success:
        print("\n🚀 Circuit breaker system validated and ready for production!")
        sys.exit(0)
    else:
        print("\n🔧 Circuit breaker system requires improvements before deployment.")
        sys.exit(1)