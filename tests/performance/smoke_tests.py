#!/usr/bin/env python3
"""
SPEC-2 Smoke Tests - Critical Path Validation
Tests core functionality to ensure system is operational before load testing
"""

import asyncio
import aiohttp
import json
import time
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmokeTestSuite:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.test_results = {}
        self.start_time = None
        
    async def setup(self):
        """Setup test environment"""
        self.session = aiohttp.ClientSession()
        self.start_time = time.time()
        logger.info("🚀 Starting SPEC-2 Smoke Tests")
        
    async def teardown(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.close()
        total_time = time.time() - self.start_time
        logger.info(f"⏱️ Total smoke test execution time: {total_time:.2f}s")
        
    async def test_health_endpoints(self) -> bool:
        """Test basic health endpoints"""
        logger.info("🔍 Testing health endpoints...")
        
        health_endpoints = [
            "/health",
            "/api/health", 
            "/api/templates/",
            "/api/vault/sync-status/test"
        ]
        
        results = []
        for endpoint in health_endpoints:
            try:
                start = time.time()
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    latency = (time.time() - start) * 1000
                    success = response.status < 400
                    results.append({
                        "endpoint": endpoint,
                        "status": response.status,
                        "latency_ms": latency,
                        "success": success
                    })
                    
                    if success:
                        logger.info(f"✅ {endpoint}: {response.status} ({latency:.1f}ms)")
                    else:
                        logger.warning(f"⚠️ {endpoint}: {response.status} ({latency:.1f}ms)")
                        
            except Exception as e:
                logger.error(f"❌ {endpoint}: {str(e)}")
                results.append({
                    "endpoint": endpoint,
                    "status": 0,
                    "latency_ms": 0,
                    "success": False,
                    "error": str(e)
                })
        
        self.test_results["health_endpoints"] = results
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        logger.info(f"📊 Health endpoints success rate: {success_rate:.1%}")
        
        return success_rate >= 0.8  # 80% success rate required
        
    async def test_task_creation_flow(self) -> bool:
        """Test SPEC-2 enhanced task creation flow"""
        logger.info("📝 Testing SPEC-2 task creation flow...")
        
        # Test data
        test_task = {
            "title": "Smoke Test Task",
            "description": "Automated smoke test for SPEC-2 functionality",
            "priority": "high",
            "estimatedTime": 1.0,
            "assignedAgent": "alden",
            "category": "testing",
            "mission": "Validate SPEC-2 task creation with enhanced fields",
            "values": ["efficiency", "reliability"],
            "habitTracker": {
                "frequency": "daily",
                "target": 1,
                "streak": 0
            },
            "decisions": [{
                "title": "Test Decision",
                "options": ["pass", "fail"],
                "reasoning": "Automated test decision"
            }],
            "memoryTags": ["smoke-test", "spec2-validation"]
        }
        
        test_steps = []
        
        # Step 1: Create task via templates API
        try:
            start = time.time()
            headers = {"Authorization": "Bearer test-token", "Content-Type": "application/json"}
            
            # Create a test template first
            template_data = {
                "name": "Smoke Test Template",
                "description": "Template for smoke testing",
                "category": "testing",
                "mission": test_task["mission"],
                "values": test_task["values"],
                "habitTracker": test_task["habitTracker"]
            }
            
            async with self.session.post(
                f"{self.base_url}/api/templates/",
                json=template_data,
                headers=headers
            ) as response:
                template_latency = (time.time() - start) * 1000
                template_success = response.status in [200, 201]
                template_id = None
                
                if template_success:
                    template_data = await response.json()
                    template_id = template_data.get("id")
                    logger.info(f"✅ Template created: {template_id} ({template_latency:.1f}ms)")
                else:
                    logger.warning(f"⚠️ Template creation failed: {response.status}")
                
                test_steps.append({
                    "step": "create_template",
                    "success": template_success,
                    "latency_ms": template_latency,
                    "status": response.status
                })
                
        except Exception as e:
            logger.error(f"❌ Template creation error: {e}")
            test_steps.append({
                "step": "create_template",
                "success": False,
                "error": str(e)
            })
            
        # Step 2: Store task in Vault
        try:
            start = time.time()
            vault_request = {
                "task": test_task,
                "vaultPath": f"tasks/smoke-test/{int(time.time())}",
                "encrypted": True,
                "memoryTags": test_task["memoryTags"],
                "syncAgents": ["alden", "alice"]
            }
            
            async with self.session.post(
                f"{self.base_url}/api/vault/tasks",
                json=vault_request,
                headers=headers
            ) as response:
                vault_latency = (time.time() - start) * 1000
                vault_success = response.status in [200, 201]
                
                if vault_success:
                    vault_data = await response.json()
                    task_id = vault_data.get("taskId")
                    logger.info(f"✅ Task stored in Vault: {task_id} ({vault_latency:.1f}ms)")
                else:
                    logger.warning(f"⚠️ Vault storage failed: {response.status}")
                
                test_steps.append({
                    "step": "vault_storage",
                    "success": vault_success,
                    "latency_ms": vault_latency,
                    "status": response.status
                })
                
        except Exception as e:
            logger.error(f"❌ Vault storage error: {e}")
            test_steps.append({
                "step": "vault_storage",
                "success": False,
                "error": str(e)
            })
            
        self.test_results["task_creation_flow"] = test_steps
        overall_success = all(step.get("success", False) for step in test_steps)
        logger.info(f"📊 Task creation flow success: {overall_success}")
        
        return overall_success
        
    async def test_memory_debug_endpoints(self) -> bool:
        """Test memory debug panel endpoints"""
        logger.info("🧠 Testing memory debug endpoints...")
        
        debug_endpoints = [
            "/api/debug/memory/slices",
            "/api/debug/memory/sync-status", 
            "/api/debug/vault/stats",
            "/api/debug/alden/memory"
        ]
        
        results = []
        headers = {"Authorization": "Bearer test-token"}
        
        for endpoint in debug_endpoints:
            try:
                start = time.time()
                async with self.session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                    latency = (time.time() - start) * 1000
                    success = response.status < 400
                    
                    if success:
                        data = await response.json()
                        data_size = len(json.dumps(data))
                        logger.info(f"✅ {endpoint}: {response.status} ({latency:.1f}ms, {data_size} bytes)")
                    else:
                        logger.warning(f"⚠️ {endpoint}: {response.status} ({latency:.1f}ms)")
                    
                    results.append({
                        "endpoint": endpoint,
                        "status": response.status,
                        "latency_ms": latency,
                        "success": success
                    })
                    
            except Exception as e:
                logger.error(f"❌ {endpoint}: {str(e)}")
                results.append({
                    "endpoint": endpoint,
                    "success": False,
                    "error": str(e)
                })
        
        self.test_results["memory_debug_endpoints"] = results
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        logger.info(f"📊 Memory debug endpoints success rate: {success_rate:.1%}")
        
        return success_rate >= 0.75  # 75% success rate (some endpoints may not be available)
        
    async def test_vault_operations(self) -> bool:
        """Test Vault operations performance"""
        logger.info("🔒 Testing Vault operations...")
        
        operations = []
        headers = {"Authorization": "Bearer test-token"}
        
        # Test recent memories retrieval
        try:
            start = time.time()
            async with self.session.get(f"{self.base_url}/api/vault/memories/recent", headers=headers) as response:
                latency = (time.time() - start) * 1000
                success = response.status < 400
                
                operations.append({
                    "operation": "recent_memories",
                    "latency_ms": latency,
                    "success": success,
                    "status": response.status
                })
                
                if success:
                    logger.info(f"✅ Recent memories: {response.status} ({latency:.1f}ms)")
                else:
                    logger.warning(f"⚠️ Recent memories failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Recent memories error: {e}")
            operations.append({
                "operation": "recent_memories",
                "success": False,
                "error": str(e)
            })
            
        # Test cross-agent memory
        try:
            start = time.time()
            params = {"query": "test", "agents": "alden,alice"}
            async with self.session.get(f"{self.base_url}/api/vault/cross-agent-memory", headers=headers, params=params) as response:
                latency = (time.time() - start) * 1000
                success = response.status < 400
                
                operations.append({
                    "operation": "cross_agent_memory",
                    "latency_ms": latency,
                    "success": success,
                    "status": response.status
                })
                
                if success:
                    logger.info(f"✅ Cross-agent memory: {response.status} ({latency:.1f}ms)")
                else:
                    logger.warning(f"⚠️ Cross-agent memory failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ Cross-agent memory error: {e}")
            operations.append({
                "operation": "cross_agent_memory",
                "success": False,
                "error": str(e)
            })
        
        self.test_results["vault_operations"] = operations
        success_rate = sum(1 for op in operations if op["success"]) / len(operations) if operations else 0
        logger.info(f"📊 Vault operations success rate: {success_rate:.1%}")
        
        return success_rate >= 0.5  # 50% success rate (some operations may not be available)
        
    async def generate_smoke_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive smoke test report"""
        logger.info("📊 Generating smoke test report...")
        
        # Calculate overall metrics
        total_tests = 0
        passed_tests = 0
        
        for test_category, results in self.test_results.items():
            if isinstance(results, list):
                for result in results:
                    total_tests += 1
                    if result.get("success", False):
                        passed_tests += 1
            elif isinstance(results, bool):
                total_tests += 1
                if results:
                    passed_tests += 1
        
        overall_success_rate = (passed_tests / total_tests) if total_tests > 0 else 0
        execution_time = time.time() - self.start_time
        
        report = {
            "smoke_test_report": {
                "timestamp": datetime.now().isoformat(),
                "spec_version": "SPEC-2-Tauri-Memory-Integration",
                "execution_time_seconds": execution_time,
                "overall_success_rate": overall_success_rate,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "status": "PASSED" if overall_success_rate >= 0.8 else "FAILED",
                "test_results": self.test_results,
                "performance_thresholds": {
                    "api_latency_threshold_ms": 500,
                    "vault_operation_threshold_ms": 1000,
                    "minimum_success_rate": 0.8
                },
                "recommendations": self._generate_recommendations()
            }
        }
        
        # Save report
        report_path = Path("smoke_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Smoke test report saved to: {report_path}")
        return report
        
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check latency issues
        for category, results in self.test_results.items():
            if isinstance(results, list):
                high_latency_count = sum(1 for r in results if r.get("latency_ms", 0) > 500)
                if high_latency_count > 0:
                    recommendations.append(f"High latency detected in {category}: {high_latency_count} requests > 500ms")
        
        # Check failure rates
        for category, results in self.test_results.items():
            if isinstance(results, list):
                failures = [r for r in results if not r.get("success", False)]
                if failures:
                    recommendations.append(f"Failures in {category}: {len(failures)} failed operations")
        
        if not recommendations:
            recommendations.append("All smoke tests passed within acceptable thresholds")
            
        return recommendations

async def run_smoke_tests():
    """Run the complete smoke test suite"""
    suite = SmokeTestSuite()
    
    try:
        await suite.setup()
        
        # Run all test suites
        test_results = []
        
        # Core health tests
        health_result = await suite.test_health_endpoints()
        test_results.append(("Health Endpoints", health_result))
        
        # SPEC-2 task creation flow
        task_flow_result = await suite.test_task_creation_flow()  
        test_results.append(("Task Creation Flow", task_flow_result))
        
        # Memory debug endpoints
        debug_result = await suite.test_memory_debug_endpoints()
        test_results.append(("Memory Debug Endpoints", debug_result))
        
        # Vault operations
        vault_result = await suite.test_vault_operations()
        test_results.append(("Vault Operations", vault_result))
        
        # Generate final report
        final_report = await suite.generate_smoke_test_report()
        
        # Print summary
        print("\n" + "="*60)
        print("🔥 SPEC-2 SMOKE TEST SUMMARY")
        print("="*60)
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:25} {status}")
        
        overall_status = final_report["smoke_test_report"]["status"]
        success_rate = final_report["smoke_test_report"]["overall_success_rate"]
        
        print(f"\nOverall Status: {'✅ PASSED' if overall_status == 'PASSED' else '❌ FAILED'}")
        print(f"Success Rate: {success_rate:.1%}")
        print(f"Execution Time: {final_report['smoke_test_report']['execution_time_seconds']:.2f}s")
        
        if final_report["smoke_test_report"]["recommendations"]:
            print(f"\n📋 Recommendations:")
            for rec in final_report["smoke_test_report"]["recommendations"]:
                print(f"• {rec}")
        
        return overall_status == "PASSED"
        
    except Exception as e:
        logger.error(f"💥 Smoke test suite failed: {e}")
        return False
        
    finally:
        await suite.teardown()

if __name__ == "__main__":
    success = asyncio.run(run_smoke_tests())
    sys.exit(0 if success else 1)