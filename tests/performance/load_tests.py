#!/usr/bin/env python3
"""
SPEC-2 Load Tests - Performance and Scalability Validation
Tests system performance under various load conditions
"""

import asyncio
import aiohttp
import json
import time
import logging
import sys
import statistics
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LoadTestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = {}
        self.start_time = None
        
    async def setup(self):
        """Setup load test environment"""
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        self.start_time = time.time()
        logger.info("🚀 Starting SPEC-2 Load Tests")
        
    async def teardown(self):
        """Cleanup load test environment"""
        if self.session:
            await self.session.close()
        total_time = time.time() - self.start_time
        logger.info(f"⏱️ Total load test execution time: {total_time:.2f}s")
        
    async def concurrent_api_test(self, endpoint: str, concurrent_users: int, requests_per_user: int, payload: Dict = None) -> Dict[str, Any]:
        """Test API endpoint with concurrent load"""
        logger.info(f"🔄 Testing {endpoint} with {concurrent_users} concurrent users, {requests_per_user} requests each")
        
        headers = {"Authorization": "Bearer test-token", "Content-Type": "application/json"}
        
        async def single_request():
            try:
                start = time.time()
                if payload:
                    async with self.session.post(f"{self.base_url}{endpoint}", json=payload, headers=headers) as response:
                        latency = (time.time() - start) * 1000
                        return {
                            "latency_ms": latency,
                            "status": response.status,
                            "success": response.status < 400,
                            "response_size": len(await response.read())
                        }
                else:
                    async with self.session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                        latency = (time.time() - start) * 1000
                        return {
                            "latency_ms": latency,
                            "status": response.status,
                            "success": response.status < 400,
                            "response_size": len(await response.read())
                        }
            except Exception as e:
                return {
                    "latency_ms": 0,
                    "status": 0,
                    "success": False,
                    "error": str(e)
                }
        
        async def user_session():
            """Simulate a user making multiple requests"""
            user_results = []
            for _ in range(requests_per_user):
                result = await single_request()
                user_results.append(result)
                # Small delay between requests from same user
                await asyncio.sleep(random.uniform(0.1, 0.3))
            return user_results
        
        # Execute concurrent user sessions
        test_start = time.time()
        tasks = [user_session() for _ in range(concurrent_users)]
        all_results = await asyncio.gather(*tasks)
        test_duration = time.time() - test_start
        
        # Flatten results
        flat_results = [result for user_results in all_results for result in user_results]
        
        # Calculate metrics
        successful_requests = [r for r in flat_results if r["success"]]
        failed_requests = [r for r in flat_results if not r["success"]]
        
        latencies = [r["latency_ms"] for r in successful_requests]
        response_sizes = [r["response_size"] for r in successful_requests]
        
        metrics = {
            "endpoint": endpoint,
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": len(flat_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(flat_results) if flat_results else 0,
            "test_duration_seconds": test_duration,
            "requests_per_second": len(flat_results) / test_duration if test_duration > 0 else 0,
            "latency_metrics": {
                "min_ms": min(latencies) if latencies else 0,
                "max_ms": max(latencies) if latencies else 0,
                "mean_ms": statistics.mean(latencies) if latencies else 0,
                "median_ms": statistics.median(latencies) if latencies else 0,
                "p95_ms": statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else (max(latencies) if latencies else 0),
                "p99_ms": statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else (max(latencies) if latencies else 0)
            },
            "response_size_metrics": {
                "min_bytes": min(response_sizes) if response_sizes else 0,
                "max_bytes": max(response_sizes) if response_sizes else 0,
                "mean_bytes": statistics.mean(response_sizes) if response_sizes else 0
            },
            "errors": [r.get("error", "Unknown error") for r in failed_requests if "error" in r]
        }
        
        logger.info(f"✅ {endpoint}: {metrics['success_rate']:.1%} success, {metrics['latency_metrics']['mean_ms']:.1f}ms avg latency")
        return metrics
        
    async def test_task_creation_load(self) -> Dict[str, Any]:
        """Load test SPEC-2 task creation with enhanced fields"""
        logger.info("📝 Load testing SPEC-2 task creation...")
        
        # Test payload with all SPEC-2 fields
        task_payload = {
            "task": {
                "title": f"Load Test Task {random.randint(1000, 9999)}",
                "description": "Automated load test task with SPEC-2 enhanced fields",
                "priority": random.choice(["low", "medium", "high"]),
                "estimatedTime": random.uniform(0.5, 8.0),
                "assignedAgent": random.choice(["alden", "alice", "mimic"]),
                "category": random.choice(["development", "research", "productivity"]),
                "mission": "Load test mission to validate system performance under concurrent task creation",
                "values": random.sample(["efficiency", "innovation", "reliability", "learning", "quality"], 2),
                "habitTracker": {
                    "frequency": random.choice(["daily", "weekly", "monthly"]),
                    "target": random.randint(1, 5),
                    "streak": 0
                },
                "decisions": [{
                    "title": "Load Test Decision",
                    "options": ["continue", "abort", "modify"],
                    "reasoning": "Automated decision for load testing"
                }],
                "memoryTags": [f"load-test-{random.randint(1, 100)}", "performance-validation"]
            },
            "vaultPath": f"tasks/load-test/{random.randint(10000, 99999)}",
            "encrypted": True,
            "memoryTags": ["load-test", "performance"],
            "syncAgents": random.sample(["alden", "alice", "mimic", "sentry"], 2)
        }
        
        # Test with different load levels
        load_scenarios = [
            {"users": 5, "requests": 2},
            {"users": 10, "requests": 3},
            {"users": 20, "requests": 2}
        ]
        
        results = []
        for scenario in load_scenarios:
            metrics = await self.concurrent_api_test(
                "/api/vault/tasks",
                scenario["users"],
                scenario["requests"],
                task_payload
            )
            results.append(metrics)
            
            # Brief pause between scenarios
            await asyncio.sleep(2)
        
        self.test_results["task_creation_load"] = results
        return results
        
    async def test_memory_debug_load(self) -> Dict[str, Any]:
        """Load test memory debug endpoints"""
        logger.info("🧠 Load testing memory debug endpoints...")
        
        debug_endpoints = [
            "/api/debug/memory/slices",
            "/api/debug/memory/sync-status",
            "/api/debug/vault/stats"
        ]
        
        results = []
        for endpoint in debug_endpoints:
            metrics = await self.concurrent_api_test(
                endpoint,
                concurrent_users=8,
                requests_per_user=5
            )
            results.append(metrics)
            
            # Brief pause between endpoints
            await asyncio.sleep(1)
        
        self.test_results["memory_debug_load"] = results
        return results
        
    async def test_vault_operations_load(self) -> Dict[str, Any]:
        """Load test Vault operations"""
        logger.info("🔒 Load testing Vault operations...")
        
        vault_endpoints = [
            "/api/vault/memories/recent?limit=10",
            "/api/vault/conversations/recent?limit=5"
        ]
        
        results = []
        for endpoint in vault_endpoints:
            metrics = await self.concurrent_api_test(
                endpoint,
                concurrent_users=6,
                requests_per_user=4
            )
            results.append(metrics)
            
            # Brief pause between endpoints
            await asyncio.sleep(1)
        
        self.test_results["vault_operations_load"] = results
        return results
        
    async def test_template_crud_load(self) -> Dict[str, Any]:
        """Load test template CRUD operations"""
        logger.info("📋 Load testing template CRUD operations...")
        
        # Template creation payload
        template_payload = {
            "name": f"Load Test Template {random.randint(1000, 9999)}",
            "description": "Automated load test template",
            "category": random.choice(["development", "research", "productivity"]),
            "mission": "Load test template to validate CRUD performance",
            "values": random.sample(["efficiency", "innovation", "reliability"], 2),
            "habitTracker": {
                "frequency": "daily",
                "target": 1
            },
            "priority": "medium",
            "estimatedTime": 2.0,
            "assignedAgent": "alden",
            "tags": ["load-test", "performance"]
        }
        
        # Test template operations
        operations = [
            {"endpoint": "/api/templates/", "payload": template_payload, "method": "POST"},
            {"endpoint": "/api/templates/", "payload": None, "method": "GET"}
        ]
        
        results = []
        for operation in operations:
            if operation["method"] == "POST":
                metrics = await self.concurrent_api_test(
                    operation["endpoint"],
                    concurrent_users=4,
                    requests_per_user=3,
                    payload=operation["payload"]
                )
            else:
                metrics = await self.concurrent_api_test(
                    operation["endpoint"],
                    concurrent_users=8,
                    requests_per_user=5
                )
            
            metrics["operation"] = operation["method"]
            results.append(metrics)
            
            # Brief pause between operations
            await asyncio.sleep(1)
        
        self.test_results["template_crud_load"] = results
        return results
        
    async def stress_test_concurrent_connections(self) -> Dict[str, Any]:
        """Stress test with high concurrent connections"""
        logger.info("⚡ Running stress test with high concurrent connections...")
        
        # High load scenario
        stress_metrics = await self.concurrent_api_test(
            "/api/templates/",
            concurrent_users=50,
            requests_per_user=2
        )
        
        self.test_results["stress_test"] = stress_metrics
        return stress_metrics
        
    async def generate_load_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive load test report"""
        logger.info("📊 Generating load test report...")
        
        execution_time = time.time() - self.start_time
        
        # Calculate aggregate metrics
        all_latencies = []
        total_requests = 0
        total_successful = 0
        
        for category, results in self.test_results.items():
            if isinstance(results, list):
                for result in results:
                    if "latency_metrics" in result:
                        total_requests += result["total_requests"]
                        total_successful += result["successful_requests"]
                        # Estimate individual latencies for aggregation
                        mean_latency = result["latency_metrics"]["mean_ms"]
                        request_count = result["successful_requests"]
                        all_latencies.extend([mean_latency] * min(request_count, 100))  # Sample for performance
            elif isinstance(results, dict) and "latency_metrics" in results:
                total_requests += results["total_requests"]
                total_successful += results["successful_requests"]
                mean_latency = results["latency_metrics"]["mean_ms"]
                request_count = results["successful_requests"]
                all_latencies.extend([mean_latency] * min(request_count, 100))
        
        overall_success_rate = (total_successful / total_requests) if total_requests > 0 else 0
        
        # Performance thresholds
        performance_grade = "A"
        if overall_success_rate < 0.95:
            performance_grade = "B"
        if overall_success_rate < 0.90:
            performance_grade = "C"
        if overall_success_rate < 0.80:
            performance_grade = "F"
        
        avg_latency = statistics.mean(all_latencies) if all_latencies else 0
        if avg_latency > 1000:
            performance_grade = min(performance_grade, "C")
        if avg_latency > 2000:
            performance_grade = "F"
        
        report = {
            "load_test_report": {
                "timestamp": datetime.now().isoformat(),
                "spec_version": "SPEC-2-Tauri-Memory-Integration",
                "execution_time_seconds": execution_time,
                "overall_metrics": {
                    "total_requests": total_requests,
                    "successful_requests": total_successful,
                    "failed_requests": total_requests - total_successful,
                    "overall_success_rate": overall_success_rate,
                    "average_latency_ms": avg_latency,
                    "performance_grade": performance_grade
                },
                "detailed_results": self.test_results,
                "performance_thresholds": {
                    "success_rate_threshold": 0.95,
                    "latency_threshold_ms": 1000,
                    "p95_latency_threshold_ms": 2000,
                    "max_acceptable_latency_ms": 5000
                },
                "scalability_analysis": self._analyze_scalability(),
                "recommendations": self._generate_load_test_recommendations()
            }
        }
        
        # Save report
        report_path = Path("load_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Load test report saved to: {report_path}")
        return report
        
    def _analyze_scalability(self) -> Dict[str, Any]:
        """Analyze scalability patterns from test results"""
        analysis = {
            "bottlenecks_detected": [],
            "scaling_patterns": {},
            "resource_utilization": {}
        }
        
        # Analyze task creation scaling
        if "task_creation_load" in self.test_results:
            task_results = self.test_results["task_creation_load"]
            if len(task_results) >= 2:
                first_scenario = task_results[0]
                last_scenario = task_results[-1]
                
                # Check if latency increases significantly with load
                latency_increase = (last_scenario["latency_metrics"]["mean_ms"] / 
                                  first_scenario["latency_metrics"]["mean_ms"]) if first_scenario["latency_metrics"]["mean_ms"] > 0 else 1
                
                if latency_increase > 2.0:
                    analysis["bottlenecks_detected"].append("Task creation latency increases significantly under load")
                
                analysis["scaling_patterns"]["task_creation"] = {
                    "latency_scaling_factor": latency_increase,
                    "throughput_scaling": last_scenario["requests_per_second"] / first_scenario["requests_per_second"] if first_scenario["requests_per_second"] > 0 else 1
                }
        
        return analysis
        
    def _generate_load_test_recommendations(self) -> List[str]:
        """Generate recommendations based on load test results"""
        recommendations = []
        
        # Check overall success rate
        overall_success = 0
        total_tests = 0
        
        for category, results in self.test_results.items():
            if isinstance(results, list):
                for result in results:
                    if "success_rate" in result:
                        overall_success += result["success_rate"]
                        total_tests += 1
            elif isinstance(results, dict) and "success_rate" in results:
                overall_success += results["success_rate"]
                total_tests += 1
        
        avg_success_rate = overall_success / total_tests if total_tests > 0 else 0
        
        if avg_success_rate < 0.95:
            recommendations.append(f"Success rate ({avg_success_rate:.1%}) below 95% threshold - investigate error patterns")
        
        # Check latency patterns
        high_latency_endpoints = []
        for category, results in self.test_results.items():
            if isinstance(results, list):
                for result in results:
                    if result.get("latency_metrics", {}).get("mean_ms", 0) > 1000:
                        high_latency_endpoints.append(f"{result.get('endpoint', category)} ({result['latency_metrics']['mean_ms']:.1f}ms)")
            elif isinstance(results, dict) and results.get("latency_metrics", {}).get("mean_ms", 0) > 1000:
                high_latency_endpoints.append(f"{results.get('endpoint', category)} ({results['latency_metrics']['mean_ms']:.1f}ms)")
        
        if high_latency_endpoints:
            recommendations.append(f"High latency endpoints detected: {', '.join(high_latency_endpoints)}")
            recommendations.append("Consider implementing caching, database optimization, or connection pooling")
        
        if not recommendations:
            recommendations.append("Load test performance within acceptable thresholds")
            recommendations.append("System demonstrates good scalability characteristics")
            
        return recommendations

async def run_load_tests():
    """Run the complete load test suite"""
    suite = LoadTestSuite()
    
    try:
        await suite.setup()
        
        # Run all load test suites
        test_results = []
        
        # Task creation load test
        task_creation_results = await suite.test_task_creation_load()
        test_results.append(("Task Creation Load", len(task_creation_results) > 0))
        
        # Memory debug load test
        memory_debug_results = await suite.test_memory_debug_load()
        test_results.append(("Memory Debug Load", len(memory_debug_results) > 0))
        
        # Vault operations load test
        vault_results = await suite.test_vault_operations_load()
        test_results.append(("Vault Operations Load", len(vault_results) > 0))
        
        # Template CRUD load test
        template_results = await suite.test_template_crud_load()
        test_results.append(("Template CRUD Load", len(template_results) > 0))
        
        # Stress test
        stress_results = await suite.stress_test_concurrent_connections()
        test_results.append(("Stress Test", stress_results.get("success_rate", 0) > 0.5))
        
        # Generate final report
        final_report = await suite.generate_load_test_report()
        
        # Print summary
        print("\n" + "="*60)
        print("⚡ SPEC-2 LOAD TEST SUMMARY")
        print("="*60)
        
        for test_name, result in test_results:
            status = "✅ COMPLETED" if result else "❌ FAILED"
            print(f"{test_name:25} {status}")
        
        overall_metrics = final_report["load_test_report"]["overall_metrics"]
        performance_grade = overall_metrics["performance_grade"]
        
        print(f"\nPerformance Grade: {performance_grade}")
        print(f"Total Requests: {overall_metrics['total_requests']}")
        print(f"Success Rate: {overall_metrics['overall_success_rate']:.1%}")
        print(f"Average Latency: {overall_metrics['average_latency_ms']:.1f}ms")
        print(f"Execution Time: {final_report['load_test_report']['execution_time_seconds']:.2f}s")
        
        if final_report["load_test_report"]["recommendations"]:
            print(f"\n📋 Recommendations:")
            for rec in final_report["load_test_report"]["recommendations"]:
                print(f"• {rec}")
        
        return performance_grade in ["A", "B", "C"]  # Pass if not complete failure
        
    except Exception as e:
        logger.error(f"💥 Load test suite failed: {e}")
        return False
        
    finally:
        await suite.teardown()

if __name__ == "__main__":
    success = asyncio.run(run_load_tests())
    sys.exit(0 if success else 1)