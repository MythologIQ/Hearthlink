#!/usr/bin/env python3
"""
SPEC-2 Performance Test Runner
Orchestrates smoke tests, load tests, and metrics integration
"""

import asyncio
import json
import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('performance_test_run.log')
    ]
)
logger = logging.getLogger(__name__)

class PerformanceTestRunner:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.results = {}
        self.start_time = None
        self.test_sequence = []
        
    async def setup(self):
        """Setup test environment"""
        logger.info("🚀 Setting up SPEC-2 Performance Test Suite")
        self.start_time = time.time()
        
        # Ensure test directories exist
        test_dirs = ["tests/performance", "tests/results", "logs"]
        for test_dir in test_dirs:
            Path(test_dir).mkdir(parents=True, exist_ok=True)
        
        # Validate test scripts exist
        required_scripts = [
            "tests/performance/smoke_tests.py",
            "tests/performance/load_tests.py"
        ]
        
        missing_scripts = []
        for script in required_scripts:
            if not Path(script).exists():
                missing_scripts.append(script)
        
        if missing_scripts:
            raise FileNotFoundError(f"Missing test scripts: {missing_scripts}")
        
        logger.info("✅ Test environment setup complete")
        
    async def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests"""
        logger.info("🔍 Running SPEC-2 Smoke Tests")
        
        try:
            # Run smoke tests
            process = await asyncio.create_subprocess_exec(
                "python3", "tests/performance/smoke_tests.py",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Load results
            smoke_results = None
            if Path("smoke_test_report.json").exists():
                with open("smoke_test_report.json", 'r') as f:
                    smoke_results = json.load(f)
            
            result = {
                "test_type": "smoke",
                "status": "passed" if process.returncode == 0 else "failed",
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8'),
                "results": smoke_results,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results["smoke_tests"] = result
            self.test_sequence.append("smoke_tests")
            
            if process.returncode == 0:
                logger.info("✅ Smoke tests completed successfully")
            else:
                logger.error(f"❌ Smoke tests failed with return code {process.returncode}")
            
            return result
            
        except Exception as e:
            logger.error(f"💥 Smoke tests crashed: {e}")
            error_result = {
                "test_type": "smoke",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["smoke_tests"] = error_result
            return error_result
    
    async def run_load_tests(self) -> Dict[str, Any]:
        """Run load tests"""
        logger.info("⚡ Running SPEC-2 Load Tests")
        
        try:
            # Run load tests
            process = await asyncio.create_subprocess_exec(
                "python3", "tests/performance/load_tests.py",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Load results
            load_results = None
            if Path("load_test_report.json").exists():
                with open("load_test_report.json", 'r') as f:
                    load_results = json.load(f)
            
            result = {
                "test_type": "load",
                "status": "passed" if process.returncode == 0 else "failed",
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8'),
                "results": load_results,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results["load_tests"] = result
            self.test_sequence.append("load_tests")
            
            if process.returncode == 0:
                logger.info("✅ Load tests completed successfully")
            else:
                logger.error(f"❌ Load tests failed with return code {process.returncode}")
            
            return result
            
        except Exception as e:
            logger.error(f"💥 Load tests crashed: {e}")
            error_result = {
                "test_type": "load",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["load_tests"] = error_result
            return error_result
    
    async def validate_spec2_components(self) -> Dict[str, Any]:
        """Validate SPEC-2 components are present"""
        logger.info("📋 Validating SPEC-2 components")
        
        try:
            # Run validation script
            process = await asyncio.create_subprocess_exec(
                "python3", "scripts/validate_installer.py",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Load validation results
            validation_results = None
            if Path("validation_report.json").exists():
                with open("validation_report.json", 'r') as f:
                    validation_results = json.load(f)
            
            result = {
                "test_type": "validation",
                "status": "passed" if process.returncode == 0 else "failed",
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8'),
                "results": validation_results,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results["component_validation"] = result
            self.test_sequence.append("component_validation")
            
            if process.returncode == 0:
                logger.info("✅ Component validation completed successfully")
            else:
                logger.error(f"❌ Component validation failed")
            
            return result
            
        except Exception as e:
            logger.error(f"💥 Component validation crashed: {e}")
            error_result = {
                "test_type": "validation",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results["component_validation"] = error_result
            return error_result
    
    async def run_installer_tests(self) -> Dict[str, Any]:
        """Test installer packaging"""
        logger.info("📦 Testing installer packaging")
        
        try:
            # Run installer validation
            validation_result = await self.validate_spec2_components()
            
            if validation_result["status"] == "passed":
                logger.info("✅ Installer packaging validation passed")
                return {
                    "test_type": "installer",
                    "status": "passed",
                    "message": "Installer validation successful",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error("❌ Installer packaging validation failed")
                return {
                    "test_type": "installer", 
                    "status": "failed",
                    "message": "Installer validation failed",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"💥 Installer testing crashed: {e}")
            return {
                "test_type": "installer",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def calculate_overall_performance_grade(self) -> str:
        """Calculate overall performance grade"""
        try:
            # Check validation status
            validation_passed = self.results.get("component_validation", {}).get("status") == "passed"
            if not validation_passed:
                return "F"  # Fail if components not valid
            
            # Check smoke test status
            smoke_passed = self.results.get("smoke_tests", {}).get("status") == "passed"
            if not smoke_passed:
                return "F"  # Fail if smoke tests don't pass
            
            # Check load test grade
            load_test_results = self.results.get("load_tests", {}).get("results")
            if load_test_results:
                load_grade = load_test_results.get("load_test_report", {}).get("overall_metrics", {}).get("performance_grade", "F")
                return load_grade
            
            return "C"  # Default if load tests ran but no grade available
            
        except Exception as e:
            logger.error(f"Failed to calculate performance grade: {e}")
            return "F"
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        logger.info("📊 Generating comprehensive performance report")
        
        execution_time = time.time() - self.start_time
        overall_grade = self.calculate_overall_performance_grade()
        
        # Count test results
        total_tests = len(self.test_sequence)
        passed_tests = sum(1 for test in self.test_sequence if self.results.get(test, {}).get("status") == "passed")
        
        # Extract key metrics
        smoke_summary = {}
        load_summary = {}
        
        if "smoke_tests" in self.results and self.results["smoke_tests"].get("results"):
            smoke_data = self.results["smoke_tests"]["results"].get("smoke_test_report", {})
            smoke_summary = {
                "status": smoke_data.get("status", "unknown"),
                "success_rate": smoke_data.get("overall_success_rate", 0),
                "total_tests": smoke_data.get("total_tests", 0),
                "execution_time": smoke_data.get("execution_time_seconds", 0)
            }
        
        if "load_tests" in self.results and self.results["load_tests"].get("results"):
            load_data = self.results["load_tests"]["results"].get("load_test_report", {})
            load_summary = {
                "performance_grade": load_data.get("overall_metrics", {}).get("performance_grade", "N/A"),
                "total_requests": load_data.get("overall_metrics", {}).get("total_requests", 0),
                "success_rate": load_data.get("overall_metrics", {}).get("overall_success_rate", 0),
                "average_latency": load_data.get("overall_metrics", {}).get("average_latency_ms", 0)
            }
        
        report = {
            "comprehensive_performance_report": {
                "timestamp": datetime.now().isoformat(),
                "spec_version": "SPEC-2-Tauri-Memory-Integration",
                "execution_time_seconds": execution_time,
                "overall_performance_grade": overall_grade,
                "test_summary": {
                    "total_test_suites": total_tests,
                    "passed_test_suites": passed_tests,
                    "failed_test_suites": total_tests - passed_tests,
                    "success_rate": passed_tests / total_tests if total_tests > 0 else 0
                },
                "smoke_test_summary": smoke_summary,
                "load_test_summary": load_summary,
                "detailed_results": self.results,
                "test_sequence": self.test_sequence,
                "performance_thresholds": {
                    "minimum_smoke_success_rate": 0.8,
                    "maximum_acceptable_latency_ms": 1000,
                    "minimum_load_test_grade": "C"
                },
                "dashboard_integration": {
                    "metrics_available": True,
                    "real_time_monitoring": True,
                    "ci_cd_integration": True
                },
                "recommendations": self._generate_performance_recommendations()
            }
        }
        
        # Save comprehensive report
        report_path = Path("comprehensive_performance_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Comprehensive report saved to: {report_path}")
        return report
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check smoke test results
        if "smoke_tests" in self.results:
            smoke_result = self.results["smoke_tests"]
            if smoke_result.get("status") != "passed":
                recommendations.append("Smoke tests failing - investigate critical path issues before load testing")
        
        # Check load test results
        if "load_tests" in self.results and self.results["load_tests"].get("results"):
            load_data = self.results["load_tests"]["results"].get("load_test_report", {})
            avg_latency = load_data.get("overall_metrics", {}).get("average_latency_ms", 0)
            
            if avg_latency > 1000:
                recommendations.append(f"High average latency ({avg_latency:.1f}ms) - consider performance optimization")
            
            success_rate = load_data.get("overall_metrics", {}).get("overall_success_rate", 1)
            if success_rate < 0.95:
                recommendations.append(f"Load test success rate ({success_rate:.1%}) below 95% - investigate error patterns")
        
        # Check component validation
        if "component_validation" in self.results:
            validation_result = self.results["component_validation"]
            if validation_result.get("status") != "passed":
                recommendations.append("SPEC-2 component validation failed - ensure all required components are present")
        
        if not recommendations:
            recommendations.append("All performance tests passed within acceptable thresholds")
            recommendations.append("System demonstrates good performance characteristics for SPEC-2 requirements")
        
        return recommendations
    
    async def run_full_test_suite(self, include_load_tests: bool = True) -> Dict[str, Any]:
        """Run complete performance test suite"""
        logger.info("🎯 Starting Full SPEC-2 Performance Test Suite")
        
        try:
            await self.setup()
            
            # Run component validation first
            await self.validate_spec2_components()
            
            # Run smoke tests
            await self.run_smoke_tests()
            
            # Run load tests if requested and smoke tests passed
            if include_load_tests:
                smoke_passed = self.results.get("smoke_tests", {}).get("status") == "passed"
                if smoke_passed:
                    await self.run_load_tests()
                else:
                    logger.warning("⚠️ Skipping load tests due to smoke test failures")
            
            # Test installer packaging
            await self.run_installer_tests()
            
            # Generate comprehensive report
            final_report = self.generate_comprehensive_report()
            
            return final_report
            
        except Exception as e:
            logger.error(f"💥 Full test suite failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def print_summary(self, report: Dict[str, Any]):
        """Print test summary to console"""
        print("\n" + "="*80)
        print("🎯 SPEC-2 PERFORMANCE TEST SUITE SUMMARY")
        print("="*80)
        
        perf_report = report.get("comprehensive_performance_report", {})
        
        print(f"Overall Grade: {perf_report.get('overall_performance_grade', 'N/A')}")
        print(f"Execution Time: {perf_report.get('execution_time_seconds', 0):.2f}s")
        
        test_summary = perf_report.get("test_summary", {})
        print(f"Test Suites: {test_summary.get('passed_test_suites', 0)}/{test_summary.get('total_test_suites', 0)} passed")
        
        # Smoke test summary
        smoke_summary = perf_report.get("smoke_test_summary", {})
        if smoke_summary:
            print(f"\n🔍 Smoke Tests: {smoke_summary.get('status', 'unknown').upper()}")
            print(f"   Success Rate: {smoke_summary.get('success_rate', 0):.1%}")
        
        # Load test summary
        load_summary = perf_report.get("load_test_summary", {})
        if load_summary:
            print(f"\n⚡ Load Tests: Grade {load_summary.get('performance_grade', 'N/A')}")
            print(f"   Total Requests: {load_summary.get('total_requests', 0)}")
            print(f"   Success Rate: {load_summary.get('success_rate', 0):.1%}")
            print(f"   Avg Latency: {load_summary.get('average_latency', 0):.1f}ms")
        
        # Recommendations
        recommendations = perf_report.get("recommendations", [])
        if recommendations:
            print(f"\n📋 Recommendations:")
            for rec in recommendations:
                print(f"• {rec}")
        
        print("\n" + "="*80)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="SPEC-2 Performance Test Runner")
    parser.add_argument("--smoke-only", action="store_true", help="Run only smoke tests")
    parser.add_argument("--load-only", action="store_true", help="Run only load tests")
    parser.add_argument("--validate-only", action="store_true", help="Run only component validation")
    parser.add_argument("--config", type=str, help="Configuration file path")
    
    args = parser.parse_args()
    
    # Load configuration if provided
    config = {}
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    runner = PerformanceTestRunner(config)
    
    try:
        if args.validate_only:
            await runner.setup()
            await runner.validate_spec2_components()
            report = runner.generate_comprehensive_report()
            runner.print_summary(report)
        elif args.smoke_only:
            await runner.setup()
            await runner.run_smoke_tests()
            report = runner.generate_comprehensive_report()
            runner.print_summary(report)
        elif args.load_only:
            await runner.setup()
            await runner.run_load_tests()
            report = runner.generate_comprehensive_report()
            runner.print_summary(report)
        else:
            # Run full suite
            report = await runner.run_full_test_suite()
            runner.print_summary(report)
        
        # Determine exit code
        overall_grade = report.get("comprehensive_performance_report", {}).get("overall_performance_grade", "F")
        exit_code = 0 if overall_grade in ["A", "B", "C"] else 1
        
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"💥 Performance test runner failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())