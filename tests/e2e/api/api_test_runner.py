"""
E2E API Test Runner - Semantic Pipeline Validation

Orchestrates API smoke tests with clear assertions and sample reports.
Provides utilities for test execution, reporting, and CI/CD integration.
"""

import asyncio
import json
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import requests
import subprocess
import sys


class APITestRunner:
    """Orchestrates API testing with comprehensive reporting"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.test_results = []
        self.start_time = time.time()
        self.session = requests.Session()
        self._setup_session()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default test configuration"""
        return {
            'api_base_url': 'http://localhost:8002',
            'performance_threshold_ms': 500,
            'timeout_s': 30,
            'max_retries': 3,
            'test_user_id': 'api-test-runner',
            'report_dir': 'tests/e2e/reports',
            'verbose': True
        }
    
    def _setup_session(self):
        """Configure HTTP session for API testing"""
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._get_auth_token()}',
            'User-Agent': 'HearthlinkAPITestRunner/1.0'
        })
    
    def _get_auth_token(self) -> str:
        """Get authentication token for API testing"""
        # In production, this would retrieve from secure storage
        return "api-test-runner-token-67890"
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        if self.config['verbose']:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] {level}: {message}")
    
    async def check_system_health(self) -> bool:
        """Check if all required services are healthy"""
        self.log("🏥 Checking system health...")
        
        health_endpoints = [
            '/api/health',
            '/api/semantic/health',
            '/api/llm/health',
            '/api/vault/health'
        ]
        
        healthy_services = 0
        for endpoint in health_endpoints:
            try:
                response = self.session.get(
                    f"{self.config['api_base_url']}{endpoint}",
                    timeout=5
                )
                if response.status_code == 200:
                    healthy_services += 1
                    self.log(f"✅ {endpoint} - healthy")
                else:
                    self.log(f"⚠️ {endpoint} - status {response.status_code}")
            except Exception as e:
                self.log(f"❌ {endpoint} - {str(e)}")
        
        all_healthy = healthy_services == len(health_endpoints)
        self.log(f"System health: {healthy_services}/{len(health_endpoints)} services healthy")
        return all_healthy
    
    def run_pytest_tests(self) -> Dict[str, Any]:
        """Run pytest-based API tests"""
        self.log("🧪 Running pytest API tests...")
        
        pytest_cmd = [
            sys.executable, '-m', 'pytest',
            'tests/e2e/api/test_semantic_pipeline.py',
            '-v',
            '--tb=short',
            '--json-report',
            '--json-report-file=tests/e2e/reports/pytest-api-report.json'
        ]
        
        try:
            result = subprocess.run(pytest_cmd, capture_output=True, text=True, timeout=300)
            
            # Parse pytest JSON report if available
            pytest_report_path = Path('tests/e2e/reports/pytest-api-report.json')
            pytest_results = {}
            
            if pytest_report_path.exists():
                with open(pytest_report_path, 'r') as f:
                    pytest_results = json.load(f)
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'pytest_results': pytest_results,
                'duration_s': pytest_results.get('duration', 0)
            }
            
        except subprocess.TimeoutExpired:
            self.log("❌ Pytest tests timed out after 5 minutes")
            return {
                'success': False,
                'error': 'timeout',
                'duration_s': 300
            }
        except Exception as e:
            self.log(f"❌ Error running pytest: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'duration_s': 0
            }
    
    def run_direct_api_tests(self) -> List[Dict[str, Any]]:
        """Run direct API tests for core functionality"""
        self.log("🎯 Running direct API tests...")
        
        direct_tests = [
            self._test_semantic_retrieve_basic,
            self._test_llm_infer_basic,
            self._test_semantic_store_basic,
            self._test_complete_pipeline,
            self._test_error_handling,
            self._test_performance_stress
        ]
        
        results = []
        for test_func in direct_tests:
            try:
                self.log(f"Running {test_func.__name__}...")
                result = test_func()
                results.append(result)
                
                status = "✅ PASS" if result['passed'] else "❌ FAIL"
                self.log(f"{status} {result['test_name']}: {result['latency_ms']}ms")
                
            except Exception as e:
                error_result = {
                    'test_name': test_func.__name__,
                    'passed': False,
                    'latency_ms': 0,
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }
                results.append(error_result)
                self.log(f"❌ ERROR {test_func.__name__}: {str(e)}")
        
        return results
    
    def _test_semantic_retrieve_basic(self) -> Dict[str, Any]:
        """Test basic semantic retrieve functionality"""
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{self.config['api_base_url']}/api/semantic/retrieve",
                json={
                    'query': 'artificial intelligence machine learning',
                    'user_id': self.config['test_user_id'],
                    'max_results': 5,
                    'similarity_threshold': 0.7
                },
                timeout=self.config['timeout_s']
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            passed = (
                response.status_code == 200 and
                'results' in response.json() and
                isinstance(response.json()['results'], list) and
                latency_ms < self.config['performance_threshold_ms']
            )
            
            return {
                'test_name': 'Semantic Retrieve Basic',
                'passed': passed,
                'latency_ms': latency_ms,
                'status_code': response.status_code,
                'response_size': len(response.content),
                'results_count': len(response.json().get('results', []))
            }
            
        except Exception as e:
            return {
                'test_name': 'Semantic Retrieve Basic',
                'passed': False,
                'latency_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }
    
    def _test_llm_infer_basic(self) -> Dict[str, Any]:
        """Test basic LLM inference functionality"""
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{self.config['api_base_url']}/api/llm/infer",
                json={
                    'prompt': 'Explain the concept of neural networks in simple terms',
                    'user_id': self.config['test_user_id'],
                    'agent': 'alden',
                    'max_tokens': 150,
                    'context': ['Neural networks are inspired by biological neurons']
                },
                timeout=self.config['timeout_s']
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            response_data = response.json()
            
            passed = (
                response.status_code == 200 and
                'response' in response_data and
                len(response_data['response']) > 10 and
                latency_ms < self.config['performance_threshold_ms']
            )
            
            return {
                'test_name': 'LLM Infer Basic',
                'passed': passed,
                'latency_ms': latency_ms,
                'status_code': response.status_code,
                'response_length': len(response_data.get('response', '')),
                'tokens_used': response_data.get('tokens_used', 0)
            }
            
        except Exception as e:
            return {
                'test_name': 'LLM Infer Basic',
                'passed': False,
                'latency_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }
    
    def _test_semantic_store_basic(self) -> Dict[str, Any]:
        """Test basic semantic store functionality"""
        start_time = time.time()
        
        try:
            test_content = f"API test memory stored at {datetime.now().isoformat()}"
            
            response = self.session.post(
                f"{self.config['api_base_url']}/api/semantic/store",
                json={
                    'content': test_content,
                    'user_id': self.config['test_user_id'],
                    'metadata': {
                        'type': 'api_test',
                        'source': 'test_runner',
                        'timestamp': datetime.now().isoformat()
                    }
                },
                timeout=self.config['timeout_s']
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            response_data = response.json()
            
            passed = (
                response.status_code == 200 and
                'memory_id' in response_data and
                response_data['memory_id'] is not None and
                latency_ms < self.config['performance_threshold_ms']
            )
            
            return {
                'test_name': 'Semantic Store Basic',
                'passed': passed,
                'latency_ms': latency_ms,
                'status_code': response.status_code,
                'memory_id': response_data.get('memory_id', 'None'),
                'content_length': len(test_content)
            }
            
        except Exception as e:
            return {
                'test_name': 'Semantic Store Basic',
                'passed': False,
                'latency_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }
    
    def _test_complete_pipeline(self) -> Dict[str, Any]:
        """Test complete retrieve → infer → store pipeline"""
        pipeline_start = time.time()
        
        try:
            # Step 1: Retrieve
            retrieve_response = self.session.post(
                f"{self.config['api_base_url']}/api/semantic/retrieve",
                json={
                    'query': 'Python programming best practices',
                    'user_id': self.config['test_user_id'],
                    'max_results': 3
                },
                timeout=self.config['timeout_s']
            )
            
            if retrieve_response.status_code != 200:
                raise Exception(f"Retrieve failed: {retrieve_response.status_code}")
            
            context = [result.get('content', '') for result in retrieve_response.json().get('results', [])]
            
            # Step 2: Infer
            infer_response = self.session.post(
                f"{self.config['api_base_url']}/api/llm/infer",
                json={
                    'prompt': 'What are the most important Python best practices?',
                    'user_id': self.config['test_user_id'],
                    'agent': 'alden',
                    'context': context[:3],  # Limit context size
                    'max_tokens': 200
                },
                timeout=self.config['timeout_s']
            )
            
            if infer_response.status_code != 200:
                raise Exception(f"Infer failed: {infer_response.status_code}")
            
            inference_result = infer_response.json().get('response', '')
            
            # Step 3: Store
            store_response = self.session.post(
                f"{self.config['api_base_url']}/api/semantic/store",
                json={
                    'content': f"Pipeline test: User asked about Python best practices. Retrieved {len(context)} context items. Response: {inference_result[:100]}...",
                    'user_id': self.config['test_user_id'],
                    'metadata': {
                        'type': 'pipeline_test',
                        'context_items': len(context),
                        'inference_length': len(inference_result)
                    }
                },
                timeout=self.config['timeout_s']
            )
            
            if store_response.status_code != 200:
                raise Exception(f"Store failed: {store_response.status_code}")
            
            total_latency = int((time.time() - pipeline_start) * 1000)
            
            passed = (
                len(context) >= 0 and  # Allow empty context
                len(inference_result) > 10 and
                store_response.json().get('memory_id') is not None and
                total_latency < (self.config['performance_threshold_ms'] * 3)  # 3x threshold for pipeline
            )
            
            return {
                'test_name': 'Complete Pipeline',
                'passed': passed,
                'latency_ms': total_latency,
                'context_items': len(context),
                'inference_length': len(inference_result),
                'memory_stored': store_response.json().get('memory_id') is not None
            }
            
        except Exception as e:
            return {
                'test_name': 'Complete Pipeline',
                'passed': False,
                'latency_ms': int((time.time() - pipeline_start) * 1000),
                'error': str(e)
            }
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test API error handling with invalid inputs"""
        start_time = time.time()
        
        try:
            # Test with invalid/empty inputs
            error_tests = [
                {
                    'endpoint': '/api/semantic/retrieve',
                    'payload': {'query': '', 'user_id': ''},
                    'expected_status': [400, 422]
                },
                {
                    'endpoint': '/api/llm/infer',
                    'payload': {'prompt': '', 'user_id': '', 'agent': 'invalid_agent'},
                    'expected_status': [400, 422]
                },
                {
                    'endpoint': '/api/semantic/store',
                    'payload': {'content': '', 'user_id': ''},
                    'expected_status': [400, 422]
                }
            ]
            
            handled_gracefully = 0
            total_tests = len(error_tests)
            
            for test in error_tests:
                try:
                    response = self.session.post(
                        f"{self.config['api_base_url']}{test['endpoint']}",
                        json=test['payload'],
                        timeout=5
                    )
                    
                    if response.status_code in test['expected_status']:
                        handled_gracefully += 1
                    elif response.status_code == 500:
                        # Server error - not graceful
                        pass
                    else:
                        # Unexpected status, but not a crash
                        handled_gracefully += 0.5
                        
                except requests.exceptions.RequestException:
                    # Network error - still counts as handled if server is up
                    pass
            
            latency_ms = int((time.time() - start_time) * 1000)
            grace_rate = handled_gracefully / total_tests
            
            return {
                'test_name': 'Error Handling',
                'passed': grace_rate >= 0.8,  # 80% of errors handled gracefully
                'latency_ms': latency_ms,
                'graceful_handling_rate': f"{grace_rate:.2%}",
                'tests_passed': f"{handled_gracefully}/{total_tests}"
            }
            
        except Exception as e:
            return {
                'test_name': 'Error Handling',
                'passed': False,
                'latency_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }
    
    def _test_performance_stress(self) -> Dict[str, Any]:
        """Test performance under moderate load"""
        start_time = time.time()
        
        try:
            # Send multiple concurrent requests
            import threading
            import queue
            
            results_queue = queue.Queue()
            num_threads = 5
            requests_per_thread = 3
            
            def stress_worker(worker_id):
                worker_results = []
                for i in range(requests_per_thread):
                    try:
                        req_start = time.time()
                        response = self.session.post(
                            f"{self.config['api_base_url']}/api/semantic/retrieve",
                            json={
                                'query': f'stress test query {worker_id}-{i}',
                                'user_id': f'{self.config["test_user_id"]}-{worker_id}',
                                'max_results': 2
                            },
                            timeout=10
                        )
                        req_latency = int((time.time() - req_start) * 1000)
                        
                        worker_results.append({
                            'success': response.status_code == 200,
                            'latency_ms': req_latency
                        })
                    except Exception as e:
                        worker_results.append({
                            'success': False,
                            'latency_ms': 10000,  # Penalty for failure
                            'error': str(e)
                        })
                
                results_queue.put(worker_results)
            
            # Launch stress test threads
            threads = []
            for i in range(num_threads):
                thread = threading.Thread(target=stress_worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join(timeout=30)
            
            # Collect results
            all_results = []
            while not results_queue.empty():
                worker_results = results_queue.get()
                all_results.extend(worker_results)
            
            total_latency = int((time.time() - start_time) * 1000)
            successful_requests = sum(1 for r in all_results if r['success'])
            total_requests = len(all_results)
            avg_request_latency = sum(r['latency_ms'] for r in all_results) // total_requests if total_requests > 0 else 0
            
            success_rate = successful_requests / total_requests if total_requests > 0 else 0
            
            passed = (
                success_rate >= 0.9 and  # 90% success rate
                avg_request_latency < self.config['performance_threshold_ms'] * 2  # Allow 2x threshold under load
            )
            
            return {
                'test_name': 'Performance Stress',
                'passed': passed,
                'latency_ms': total_latency,
                'success_rate': f"{success_rate:.2%}",
                'avg_request_latency_ms': avg_request_latency,
                'total_requests': total_requests,
                'successful_requests': successful_requests
            }
            
        except Exception as e:
            return {
                'test_name': 'Performance Stress',
                'passed': False,
                'latency_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }
    
    def generate_comprehensive_report(self, pytest_results: Dict, direct_results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_execution_time = time.time() - self.start_time
        
        # Combine all results
        all_tests = direct_results.copy()
        
        # Add pytest results if available
        if pytest_results.get('success') and pytest_results.get('pytest_results'):
            pytest_data = pytest_results['pytest_results']
            for test in pytest_data.get('tests', []):
                all_tests.append({
                    'test_name': test.get('nodeid', 'Unknown Pytest Test'),
                    'passed': test.get('outcome') == 'passed',
                    'latency_ms': int(test.get('duration', 0) * 1000),
                    'source': 'pytest'
                })
        
        # Calculate summary statistics
        total_tests = len(all_tests)
        passed_tests = sum(1 for t in all_tests if t['passed'])
        avg_latency = sum(t['latency_ms'] for t in all_tests) // total_tests if total_tests > 0 else 0
        max_latency = max(t['latency_ms'] for t in all_tests) if all_tests else 0
        performance_violations = sum(1 for t in all_tests if t['latency_ms'] > self.config['performance_threshold_ms'])
        
        report = {
            'summary': {
                'test_suite': 'E2E API Semantic Pipeline Validation',
                'execution_timestamp': datetime.now().isoformat(),
                'total_execution_time_s': int(total_execution_time),
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': total_tests - passed_tests,
                'pass_rate': f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%",
                'avg_latency_ms': avg_latency,
                'max_latency_ms': max_latency,
                'performance_threshold_ms': self.config['performance_threshold_ms'],
                'performance_violations': performance_violations,
                'build_should_pass': passed_tests == total_tests and performance_violations == 0
            },
            'test_environment': {
                'api_base_url': self.config['api_base_url'],
                'timeout_s': self.config['timeout_s'],
                'test_user_id': self.config['test_user_id']
            },
            'detailed_results': {
                'direct_api_tests': direct_results,
                'pytest_results': pytest_results
            },
            'performance_analysis': {
                'latency_distribution': self._calculate_latency_distribution(all_tests),
                'slowest_tests': sorted(all_tests, key=lambda x: x['latency_ms'], reverse=True)[:5]
            },
            'recommendations': self._generate_recommendations(all_tests)
        }
        
        return report
    
    def _calculate_latency_distribution(self, tests: List[Dict]) -> Dict[str, int]:
        """Calculate latency distribution buckets"""
        latencies = [t['latency_ms'] for t in tests]
        
        distribution = {
            'under_100ms': sum(1 for l in latencies if l < 100),
            '100_250ms': sum(1 for l in latencies if 100 <= l < 250),
            '250_500ms': sum(1 for l in latencies if 250 <= l < 500),
            '500_1000ms': sum(1 for l in latencies if 500 <= l < 1000),
            'over_1000ms': sum(1 for l in latencies if l >= 1000)
        }
        
        return distribution
    
    def _generate_recommendations(self, tests: List[Dict]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [t for t in tests if not t['passed']]
        slow_tests = [t for t in tests if t['latency_ms'] > self.config['performance_threshold_ms']]
        
        if failed_tests:
            recommendations.append(f"❌ {len(failed_tests)} tests failed - investigate error handling and service stability")
        
        if slow_tests:
            recommendations.append(f"⚡ {len(slow_tests)} tests exceeded performance threshold - optimize slow endpoints")
        
        if not failed_tests and not slow_tests:
            recommendations.append("✅ All tests passed with good performance - system is ready for production")
        
        return recommendations
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run complete test suite and generate report"""
        self.log("🚀 Starting E2E API Test Suite")
        
        # Check system health first
        if not await self.check_system_health():
            self.log("⚠️ Some services are unhealthy - proceeding with tests anyway")
        
        # Run pytest tests
        pytest_results = self.run_pytest_tests()
        
        # Run direct API tests
        direct_results = self.run_direct_api_tests()
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report(pytest_results, direct_results)
        
        # Save report
        report_dir = Path(self.config['report_dir'])
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"api-test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        self._print_test_summary(report)
        
        self.log(f"📄 Full report saved to: {report_file}")
        
        return report
    
    def _print_test_summary(self, report: Dict[str, Any]):
        """Print test summary to console"""
        summary = report['summary']
        
        print(f"\n{'='*70}")
        print("🎯 E2E API SEMANTIC PIPELINE TEST SUMMARY")
        print('='*70)
        print(f"📊 Tests: {summary['total_tests']} total, {summary['passed']} passed, {summary['failed']} failed")
        print(f"📈 Pass Rate: {summary['pass_rate']}")
        print(f"⏱️  Average Latency: {summary['avg_latency_ms']}ms")
        print(f"🚀 Max Latency: {summary['max_latency_ms']}ms")
        print(f"⚡ Performance Violations: {summary['performance_violations']}/{summary['total_tests']}")
        print(f"🕐 Total Execution Time: {summary['total_execution_time_s']}s")
        
        if summary['failed'] > 0:
            print(f"\n❌ BUILD SHOULD FAIL - {summary['failed']} tests failed")
        elif summary['performance_violations'] > 0:
            print(f"\n⚠️ BUILD WARNING - {summary['performance_violations']} performance violations")
        else:
            print("\n✅ BUILD SHOULD PASS - All tests successful")
        
        if report['recommendations']:
            print("\n📋 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        print('='*70)


async def main():
    """Main entry point for API test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='E2E API Test Runner')
    parser.add_argument('--api-url', default='http://localhost:8002', help='API base URL')
    parser.add_argument('--threshold', type=int, default=500, help='Performance threshold in ms')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--user-id', default='api-test-runner', help='Test user ID')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    config = {
        'api_base_url': args.api_url,
        'performance_threshold_ms': args.threshold,
        'timeout_s': args.timeout,
        'test_user_id': args.user_id,
        'verbose': args.verbose,
        'report_dir': 'tests/e2e/reports'
    }
    
    runner = APITestRunner(config)
    report = await runner.run_full_test_suite()
    
    # Set exit code based on results
    if not report['summary']['build_should_pass']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())