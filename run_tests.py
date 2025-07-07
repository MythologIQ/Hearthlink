#!/usr/bin/env python3
"""
Alden Test Runner

Executes comprehensive error handling and integration tests for Alden persona.
Provides detailed reporting and exit codes for CI/CD integration.

Author: Hearthlink Development Team
Version: 1.0.0
"""

import sys
import argparse
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from test_alden_error_handling import TestSuite, TestResult


def run_basic_tests():
    """Run basic functionality tests."""
    print("🧪 Running Basic Functionality Tests...")
    print("=" * 50)
    
    from test_alden_error_handling import (
        test_llm_client_initialization,
        test_alden_persona_initialization,
        test_alden_response_generation,
        test_alden_memory_export
    )
    
    test_suite = TestSuite()
    
    test_suite.run_test(test_llm_client_initialization, "LLM Client Initialization")
    test_suite.run_test(test_alden_persona_initialization, "Alden Persona Initialization")
    test_suite.run_test(test_alden_response_generation, "Alden Response Generation")
    test_suite.run_test(test_alden_memory_export, "Alden Memory Export")
    
    return test_suite


def run_error_handling_tests():
    """Run error handling tests."""
    print("\n🧪 Running Error Handling Tests...")
    print("=" * 50)
    
    from test_alden_error_handling import (
        test_llm_client_error_handling,
        test_llm_client_response_validation,
        test_alden_persona_validation,
        test_alden_response_generation_errors,
        test_error_logging
    )
    
    test_suite = TestSuite()
    
    test_suite.run_test(test_llm_client_error_handling, "LLM Client Error Handling")
    test_suite.run_test(test_llm_client_response_validation, "LLM Client Response Validation")
    test_suite.run_test(test_alden_persona_validation, "Alden Persona Validation")
    test_suite.run_test(test_alden_response_generation_errors, "Alden Response Generation Errors")
    test_suite.run_test(test_error_logging, "Error Logging")
    
    return test_suite


def run_memory_management_tests():
    """Run memory management tests."""
    print("\n🧪 Running Memory Management Tests...")
    print("=" * 50)
    
    from test_alden_error_handling import (
        test_alden_trait_management,
        test_alden_correction_events,
        test_alden_mood_recording,
        test_alden_status_check
    )
    
    test_suite = TestSuite()
    
    test_suite.run_test(test_alden_trait_management, "Alden Trait Management")
    test_suite.run_test(test_alden_correction_events, "Alden Correction Events")
    test_suite.run_test(test_alden_mood_recording, "Alden Mood Recording")
    test_suite.run_test(test_alden_status_check, "Alden Status Check")
    
    return test_suite


def run_all_tests():
    """Run all tests."""
    print("🚀 Starting Comprehensive Alden Test Suite")
    print("=" * 60)
    print(f"Test Run Started: {datetime.now().isoformat()}")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all test categories
    basic_suite = run_basic_tests()
    error_suite = run_error_handling_tests()
    memory_suite = run_memory_management_tests()
    
    # Combine results
    all_results = basic_suite.results + error_suite.results + memory_suite.results
    total_tests = basic_suite.test_count + error_suite.test_count + memory_suite.test_count
    total_passed = basic_suite.passed_count + error_suite.passed_count + memory_suite.passed_count
    total_failed = basic_suite.failed_count + error_suite.failed_count + memory_suite.failed_count
    
    # Print comprehensive summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%")
    print(f"Total Duration: {time.time() - start_time:.2f}s")
    
    if total_failed > 0:
        print("\nFAILED TESTS:")
        for result in all_results:
            if not result.success:
                print(f"  - {result.test_name}: {result.error}")
                if result.details.get("traceback"):
                    print(f"    Traceback: {result.details['traceback'][:200]}...")
    
    print("=" * 60)
    
    return total_failed == 0


def run_specific_test(test_name: str):
    """Run a specific test by name."""
    print(f"🧪 Running Specific Test: {test_name}")
    print("=" * 50)
    
    # Import all test functions
    from test_alden_error_handling import (
        test_llm_client_initialization,
        test_llm_client_error_handling,
        test_llm_client_response_validation,
        test_alden_persona_initialization,
        test_alden_persona_validation,
        test_alden_response_generation,
        test_alden_response_generation_errors,
        test_alden_trait_management,
        test_alden_correction_events,
        test_alden_mood_recording,
        test_alden_memory_export,
        test_alden_status_check,
        test_error_logging,
        test_circuit_breaker
    )
    
    # Map test names to functions
    test_functions = {
        "llm_client_initialization": test_llm_client_initialization,
        "llm_client_error_handling": test_llm_client_error_handling,
        "llm_client_response_validation": test_llm_client_response_validation,
        "alden_persona_initialization": test_alden_persona_initialization,
        "alden_persona_validation": test_alden_persona_validation,
        "alden_response_generation": test_alden_response_generation,
        "alden_response_generation_errors": test_alden_response_generation_errors,
        "alden_trait_management": test_alden_trait_management,
        "alden_correction_events": test_alden_correction_events,
        "alden_mood_recording": test_alden_mood_recording,
        "alden_memory_export": test_alden_memory_export,
        "alden_status_check": test_alden_status_check,
        "error_logging": test_error_logging,
        "circuit_breaker": test_circuit_breaker
    }
    
    if test_name not in test_functions:
        print(f"❌ Unknown test: {test_name}")
        print("Available tests:")
        for name in test_functions.keys():
            print(f"  - {name}")
        return False
    
    test_suite = TestSuite()
    test_suite.run_test(test_functions[test_name], test_name)
    test_suite.print_summary()
    
    return test_suite.failed_count == 0


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="Alden Test Runner - Comprehensive Error Handling and Integration Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --basic            # Run basic functionality tests
  python run_tests.py --errors           # Run error handling tests
  python run_tests.py --memory           # Run memory management tests
  python run_tests.py --test alden_response_generation  # Run specific test
        """
    )
    
    parser.add_argument("--basic", action="store_true", 
                       help="Run basic functionality tests only")
    parser.add_argument("--errors", action="store_true", 
                       help="Run error handling tests only")
    parser.add_argument("--memory", action="store_true", 
                       help="Run memory management tests only")
    parser.add_argument("--test", type=str, 
                       help="Run a specific test by name")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose output")
    
    args = parser.parse_args()
    
    try:
        success = False
        
        if args.test:
            success = run_specific_test(args.test)
        elif args.basic:
            test_suite = run_basic_tests()
            test_suite.print_summary()
            success = test_suite.failed_count == 0
        elif args.errors:
            test_suite = run_error_handling_tests()
            test_suite.print_summary()
            success = test_suite.failed_count == 0
        elif args.memory:
            test_suite = run_memory_management_tests()
            test_suite.print_summary()
            success = test_suite.failed_count == 0
        else:
            success = run_all_tests()
        
        if success:
            print("\n✅ All tests passed successfully!")
            print("\nNext steps:")
            print("1. Run integration tests with actual LLM engines")
            print("2. Test API endpoints with real requests")
            print("3. Verify error logs contain expected information")
            print("4. Test recovery mechanisms in production-like conditions")
        else:
            print("\n❌ Some tests failed!")
            print("Please review the failed tests and fix any issues.")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 