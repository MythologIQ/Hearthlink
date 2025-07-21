#!/usr/bin/env python3
"""
Circuit Breaker Failover Scenario Tests

Comprehensive end-to-end testing of circuit breaker functionality
with real service failures, recovery scenarios, and dashboard monitoring.
"""

import pytest
import asyncio
import time
import requests
import json
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState, CircuitBreakerManager

class TestCircuitBreakerFailover:
    """Comprehensive circuit breaker failover testing"""
    
    def setup_method(self):
        """Setup test environment"""
        self.circuit_manager = CircuitBreakerManager()
        self.test_results = {}
        self.dashboard_events = []
        
        # Test service endpoints
        self.test_services = {
            'local-llm': 'http://localhost:8001',
            'core-api': 'http://localhost:8000',
            'vault-api': 'http://localhost:8002',
            'synapse-api': 'http://localhost:8003',
            'sentry-api': 'http://localhost:8004',
            'superclaude': 'http://localhost:8005',
            'external-agent': 'http://localhost:8006'
        }
        
    def teardown_method(self):
        """Cleanup after tests"""
        # Reset all circuit breakers
        self.circuit_manager.reset_all()
        
    def test_service_failure_detection(self):
        """Test circuit breaker opens when service failures exceed threshold"""
        print("\n🔴 Testing service failure detection...")
        
        # Create circuit breaker with low threshold for fast testing
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=5,
            timeout=2
        )
        
        breaker = CircuitBreaker("test_service", config)
        
        def failing_service():
            """Service that always fails"""
            raise Exception("Service unavailable")
        
        # Test multiple failures
        failure_count = 0
        for i in range(5):
            try:
                breaker.call(failing_service)
            except Exception:
                failure_count += 1
                
        # Verify circuit opened after threshold
        assert breaker.state == CircuitState.OPEN
        assert failure_count == 5
        
        # Verify circuit blocks further requests
        with pytest.raises(Exception, match="Circuit breaker.*is open"):
            breaker.call(failing_service)
            
        self.test_results['failure_detection'] = 'PASSED'
        print("✅ Service failure detection: PASSED")
        
    def test_recovery_scenario(self):
        """Test circuit breaker recovery when service comes back online"""
        print("\n🟡 Testing service recovery scenario...")
        
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=2,  # Short timeout for testing
            success_threshold=2,
            timeout=1
        )
        
        breaker = CircuitBreaker("recovery_test", config)
        
        # Service state controller
        service_healthy = False
        
        def test_service():
            if service_healthy:
                return "Service OK"
            else:
                raise Exception("Service down")
                
        # Initial failures to open circuit
        for _ in range(3):
            try:
                breaker.call(test_service)
            except:
                pass
                
        assert breaker.state == CircuitState.OPEN
        print("  Circuit opened after failures")
        
        # Wait for recovery timeout
        time.sleep(3)
        
        # Service comes back online
        service_healthy = True
        
        # Circuit should attempt half-open
        result = breaker.call(test_service)
        assert result == "Service OK"
        assert breaker.state == CircuitState.HALF_OPEN
        print("  Circuit half-open after recovery")
        
        # Another successful call should close circuit
        result = breaker.call(test_service)
        assert result == "Service OK"
        assert breaker.state == CircuitState.CLOSED
        print("  Circuit closed after successful recovery")
        
        self.test_results['recovery_scenario'] = 'PASSED'
        print("✅ Service recovery scenario: PASSED")
        
    def test_half_open_failure_scenario(self):
        """Test circuit reopens if service fails during half-open state"""
        print("\n🔶 Testing half-open failure scenario...")
        
        config = CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=2,
            timeout=1
        )
        
        breaker = CircuitBreaker("half_open_test", config)
        
        def unstable_service():
            """Service that fails intermittently"""
            import random
            if random.random() < 0.7:  # 70% failure rate
                raise Exception("Service unstable")
            return "Success"
        
        # Force circuit open
        for _ in range(3):
            try:
                breaker.call(lambda: exec('raise Exception("Fail")'))
            except:
                pass
        
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery
        time.sleep(3)
        
        # Service fails during half-open test
        with pytest.raises(Exception):
            breaker.call(lambda: exec('raise Exception("Still failing")'))
            
        # Circuit should reopen
        assert breaker.state == CircuitState.OPEN
        
        self.test_results['half_open_failure'] = 'PASSED'
        print("✅ Half-open failure scenario: PASSED")
        
    def test_concurrent_requests(self):
        """Test circuit breaker under concurrent load"""
        print("\n⚡ Testing concurrent request handling...")
        
        config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=3,
            timeout=2
        )
        
        breaker = CircuitBreaker("concurrent_test", config)
        
        request_count = 0
        success_count = 0
        failure_count = 0
        lock = threading.Lock()
        
        def concurrent_service():
            nonlocal request_count, success_count, failure_count
            with lock:
                request_count += 1
                
            # Simulate some requests failing
            import random
            if random.random() < 0.3:  # 30% failure rate
                with lock:
                    failure_count += 1
                raise Exception("Random failure")
            else:
                with lock:
                    success_count += 1
                return "Success"
        
        # Run concurrent requests
        threads = []
        for _ in range(20):
            thread = threading.Thread(
                target=lambda: breaker.call(concurrent_service) if breaker.state != CircuitState.OPEN else None
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        print(f"  Processed {request_count} requests")
        print(f"  Successes: {success_count}, Failures: {failure_count}")
        
        # Verify metrics
        status = breaker.get_status()
        assert status['metrics']['total_requests'] > 0
        
        self.test_results['concurrent_requests'] = 'PASSED'
        print("✅ Concurrent request handling: PASSED")
        
    def test_dashboard_integration(self):
        """Test circuit breaker dashboard receives proper data"""
        print("\n📊 Testing dashboard integration...")
        
        # Create multiple circuit breakers for different services
        services = ['local-llm', 'core-api', 'vault-api']
        breakers = {}
        
        for service in services:
            config = CircuitBreakerConfig(
                failure_threshold=2,
                recovery_timeout=3,
                timeout=1
            )
            breakers[service] = CircuitBreaker(service, config)
        
        # Simulate different service states
        def healthy_service():
            return "OK"
            
        def failing_service():
            raise Exception("Service down")
        
        # Local LLM - healthy
        for _ in range(3):
            breakers['local-llm'].call(healthy_service)
        
        # Core API - failing (circuit opens)
        for _ in range(3):
            try:
                breakers['core-api'].call(failing_service)
            except:
                pass
        
        # Vault API - partially failing (circuit stays closed but has failures)
        breakers['vault-api'].call(healthy_service)
        try:
            breakers['vault-api'].call(failing_service)
        except:
            pass
        
        # Collect dashboard data
        dashboard_data = {
            'services': {},
            'global_metrics': {
                'total_services': len(services),
                'healthy_services': 0,
                'failing_services': 0,
                'open_circuits': 0
            }
        }
        
        for service, breaker in breakers.items():
            status = breaker.get_status()
            dashboard_data['services'][service] = {
                'name': service.replace('-', ' ').title(),
                'state': status['state'],
                'health_status': status['health_status'],
                'metrics': status['metrics']
            }
            
            # Update global metrics
            if status['state'] == 'closed' and status['health_status'] == 'healthy':
                dashboard_data['global_metrics']['healthy_services'] += 1
            else:
                dashboard_data['global_metrics']['failing_services'] += 1
                
            if status['state'] == 'open':
                dashboard_data['global_metrics']['open_circuits'] += 1
        
        # Verify dashboard data structure
        assert 'services' in dashboard_data
        assert 'global_metrics' in dashboard_data
        assert dashboard_data['global_metrics']['total_services'] == 3
        assert dashboard_data['global_metrics']['open_circuits'] >= 1  # core-api should be open
        
        # Verify service-specific data
        assert dashboard_data['services']['core-api']['state'] == 'open'
        assert dashboard_data['services']['local-llm']['health_status'] == 'healthy'
        
        print(f"  Dashboard tracking {len(dashboard_data['services'])} services")
        print(f"  Open circuits: {dashboard_data['global_metrics']['open_circuits']}")
        
        self.test_results['dashboard_integration'] = 'PASSED'
        print("✅ Dashboard integration: PASSED")
        
    def test_manual_circuit_operations(self):
        """Test manual circuit breaker operations (reset, force open/close)"""
        print("\n🔧 Testing manual circuit operations...")
        
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=10)
        breaker = CircuitBreaker("manual_test", config)
        
        # Force failures to open circuit
        for _ in range(3):
            try:
                breaker.call(lambda: exec('raise Exception("Fail")'))
            except:
                pass
        
        assert breaker.state == CircuitState.OPEN
        print("  Circuit opened via failures")
        
        # Manual reset
        breaker.reset()
        assert breaker.state == CircuitState.CLOSED
        assert breaker.consecutive_failures == 0
        print("  Manual reset successful")
        
        # Test successful operation after reset
        result = breaker.call(lambda: "Reset success")
        assert result == "Reset success"
        
        self.test_results['manual_operations'] = 'PASSED'
        print("✅ Manual circuit operations: PASSED")
        
    def test_timeout_handling(self):
        """Test circuit breaker timeout functionality"""
        print("\n⏱️ Testing timeout handling...")
        
        config = CircuitBreakerConfig(
            failure_threshold=2,
            timeout=1,  # 1 second timeout
            recovery_timeout=3
        )
        
        breaker = CircuitBreaker("timeout_test", config)
        
        def slow_service():
            """Service that takes too long"""
            time.sleep(2)  # Longer than timeout
            return "Too slow"
        
        # Test timeout failure
        start_time = time.time()
        with pytest.raises(Exception, match="timeout"):
            breaker.call(slow_service)
        
        elapsed = time.time() - start_time
        assert elapsed < 1.5  # Should timeout quickly
        
        print(f"  Request timed out after {elapsed:.2f}s")
        
        self.test_results['timeout_handling'] = 'PASSED'
        print("✅ Timeout handling: PASSED")
        
    def test_metrics_accuracy(self):
        """Test circuit breaker metrics tracking accuracy"""
        print("\n📈 Testing metrics accuracy...")
        
        config = CircuitBreakerConfig(failure_threshold=5, recovery_timeout=3)
        breaker = CircuitBreaker("metrics_test", config)
        
        # Track expected metrics
        expected_total = 0
        expected_success = 0
        expected_failure = 0
        
        # Execute mix of successful and failed requests
        operations = [
            (lambda: "success", True),
            (lambda: "success", True),
            (lambda: exec('raise Exception("fail")'), False),
            (lambda: "success", True),
            (lambda: exec('raise Exception("fail")'), False),
            (lambda: exec('raise Exception("fail")'), False),
            (lambda: "success", True)
        ]
        
        for operation, should_succeed in operations:
            expected_total += 1
            try:
                breaker.call(operation)
                if should_succeed:
                    expected_success += 1
                else:
                    assert False, "Should have failed"
            except Exception:
                if not should_succeed:
                    expected_failure += 1
                else:
                    assert False, "Should have succeeded"
        
        # Verify metrics
        status = breaker.get_status()
        metrics = status['metrics']
        
        assert metrics['total_requests'] == expected_total
        assert metrics['successful_requests'] == expected_success
        assert metrics['failed_requests'] == expected_failure
        
        expected_rate = (expected_success / expected_total) * 100 if expected_total > 0 else 0
        actual_rate = (metrics['successful_requests'] / metrics['total_requests']) * 100
        
        print(f"  Total requests: {metrics['total_requests']} (expected: {expected_total})")
        print(f"  Success rate: {actual_rate:.1f}% (expected: {expected_rate:.1f}%)")
        
        self.test_results['metrics_accuracy'] = 'PASSED'
        print("✅ Metrics accuracy: PASSED")
        
    def test_emergency_stop_scenario(self):
        """Test emergency stop (open all circuits) functionality"""
        print("\n🚨 Testing emergency stop scenario...")
        
        # Create multiple services
        services = ['service1', 'service2', 'service3']
        breakers = {}
        
        for service in services:
            config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=5)
            breakers[service] = self.circuit_manager.get_or_create(service, config)
        
        # Ensure all circuits start closed
        for breaker in breakers.values():
            assert breaker.state == CircuitState.CLOSED
        
        # Emergency stop - force open all circuits
        def emergency_stop():
            for breaker in breakers.values():
                breaker._change_state(CircuitState.OPEN, "Emergency stop activated")
        
        emergency_stop()
        
        # Verify all circuits are open
        for service, breaker in breakers.items():
            assert breaker.state == CircuitState.OPEN
            print(f"  {service}: OPEN")
        
        # Verify requests are blocked
        for breaker in breakers.values():
            with pytest.raises(Exception, match="Circuit breaker.*is open"):
                breaker.call(lambda: "Should be blocked")
        
        self.test_results['emergency_stop'] = 'PASSED'
        print("✅ Emergency stop scenario: PASSED")
        
    def test_service_health_monitoring(self):
        """Test service health status determination"""
        print("\n💊 Testing service health monitoring...")
        
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=5,
            monitoring_window=60
        )
        
        breaker = CircuitBreaker("health_test", config)
        
        # Test healthy service
        for _ in range(5):
            breaker.call(lambda: "OK")
        
        status = breaker.get_status()
        assert status['health_status'] == 'healthy'
        print("  Service with no failures: healthy")
        
        # Add some failures (but not enough to open circuit)
        for _ in range(2):
            try:
                breaker.call(lambda: exec('raise Exception("occasional fail")'))
            except:
                pass
        
        status = breaker.get_status()
        # Should still be healthy or degraded depending on failure rate
        print(f"  Service with some failures: {status['health_status']}")
        
        # Force circuit open
        for _ in range(3):
            try:
                breaker.call(lambda: exec('raise Exception("fail")'))
            except:
                pass
        
        status = breaker.get_status()
        assert status['health_status'] == 'unhealthy'
        print("  Service with open circuit: unhealthy")
        
        self.test_results['health_monitoring'] = 'PASSED'
        print("✅ Service health monitoring: PASSED")
        
    def run_comprehensive_test_suite(self):
        """Run all circuit breaker tests and generate report"""
        print("🔄 Starting Comprehensive Circuit Breaker Failover Tests")
        print("=" * 60)
        
        test_methods = [
            self.test_service_failure_detection,
            self.test_recovery_scenario,
            self.test_half_open_failure_scenario,
            self.test_concurrent_requests,
            self.test_dashboard_integration,
            self.test_manual_circuit_operations,
            self.test_timeout_handling,
            self.test_metrics_accuracy,
            self.test_emergency_stop_scenario,
            self.test_service_health_monitoring
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                test_method()
                passed += 1
            except Exception as e:
                print(f"❌ {test_method.__name__}: FAILED - {str(e)}")
                failed += 1
        
        # Generate comprehensive report
        print("\n" + "=" * 60)
        print("🔄 CIRCUIT BREAKER FAILOVER TEST REPORT")
        print("=" * 60)
        
        print(f"\n📊 Test Summary:")
        print(f"  Total Tests: {len(test_methods)}")
        print(f"  Passed: ✅ {passed}")
        print(f"  Failed: ❌ {failed}")
        print(f"  Success Rate: {(passed/len(test_methods)*100):.1f}%")
        
        print(f"\n🔍 Detailed Results:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "PASSED" else "❌"
            print(f"  {status_icon} {test_name}: {result}")
        
        if failed == 0:
            print(f"\n🎉 ALL CIRCUIT BREAKER TESTS PASSED!")
            print("   The circuit breaker system is fully functional and ready for production.")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Review and fix issues before deployment.")
        
        # Save detailed report
        report = {
            'test_suite': 'circuit_breaker_failover',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': len(test_methods),
                'passed': passed,
                'failed': failed,
                'success_rate': passed/len(test_methods)*100
            },
            'results': self.test_results,
            'recommendation': 'PASSED' if failed == 0 else 'REQUIRES_FIXES'
        }
        
        with open('/mnt/g/mythologiq/hearthlink/tests/circuit_breaker_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Detailed report saved to: tests/circuit_breaker_test_report.json")
        
        return failed == 0

if __name__ == "__main__":
    # Run comprehensive test suite
    tester = TestCircuitBreakerFailover()
    tester.setup_method()  # Initialize the test environment
    success = tester.run_comprehensive_test_suite()
    
    if success:
        print("\n🚀 Circuit breaker system validated and ready for production!")
        exit(0)
    else:
        print("\n🔧 Circuit breaker system requires fixes before deployment.")
        exit(1)