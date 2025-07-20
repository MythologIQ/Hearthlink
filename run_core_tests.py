#!/usr/bin/env python3
"""
Core Test Runner

Simple test runner for Core module tests with comprehensive reporting.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def run_test_suite(test_module: str, test_name: str) -> Dict[str, Any]:
    """Run a specific test suite and return results."""
    try:
        print(f"\n🚀 Running {test_name}...")
        start_time = time.time()
        
        # Import and run test module
        if test_module == "multi_agent":
            from tests.test_core_multi_agent import run_multi_agent_tests
            run_multi_agent_tests()
        elif test_module == "memory_management":
            from tests.test_core_memory_management import run_memory_management_tests
            run_memory_management_tests()
        else:
            raise ValueError(f"Unknown test module: {test_module}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "test_suite": test_name,
            "status": "PASSED",
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "test_suite": test_name,
            "status": "FAILED",
            "error": str(e),
            "duration": 0,
            "timestamp": datetime.now().isoformat()
        }

def run_all_tests() -> Dict[str, Any]:
    """Run all Core test suites."""
    print("🧪 Core Module Test Suite")
    print("=" * 50)
    
    test_suites = [
        ("multi_agent", "Multi-Agent Session Tests"),
        ("memory_management", "Memory Management Tests")
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_module, test_name in test_suites:
        result = run_test_suite(test_module, test_name)
        results.append(result)
        
        if result["status"] == "PASSED":
            print(f"✅ {test_name} - PASSED ({result['duration']:.2f}s)")
        else:
            print(f"❌ {test_name} - FAILED: {result.get('error', 'Unknown error')}")
    
    total_duration = time.time() - total_start_time
    
    # Generate summary
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    success_rate = (passed / len(results)) * 100 if results else 0
    
    summary = {
        "test_run": {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "passed": passed,
            "failed": failed,
            "success_rate": success_rate,
            "total_duration": total_duration
        },
        "results": results
    }
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Test Suites: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Total Duration: {total_duration:.2f}s")
    
    # Print failed tests
    failed_tests = [r for r in results if r["status"] == "FAILED"]
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test in failed_tests:
            print(f"  {test['test_suite']}: {test.get('error', 'Unknown error')}")
    
    return summary

def save_results(summary: Dict[str, Any], output_file: str = "core_test_results.json"):
    """Save test results to file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"⚠️  Failed to save results: {e}")

def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        # Run specific test suite
        test_module = sys.argv[1]
        test_name = {
            "multi_agent": "Multi-Agent Session Tests",
            "memory_management": "Memory Management Tests"
        }.get(test_module, test_module)
        
        result = run_test_suite(test_module, test_name)
        summary = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": 1,
                "passed": 1 if result["status"] == "PASSED" else 0,
                "failed": 1 if result["status"] == "FAILED" else 0,
                "success_rate": 100 if result["status"] == "PASSED" else 0,
                "total_duration": result["duration"]
            },
            "results": [result]
        }
    else:
        # Run all tests
        summary = run_all_tests()
    
    # Save results
    save_results(summary)
    
    # Exit with appropriate code
    if summary["test_run"]["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 