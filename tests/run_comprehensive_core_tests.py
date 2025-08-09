#!/usr/bin/env python3
"""
Comprehensive Core Test Runner

This script runs all Core module tests with comprehensive logging,
metrics collection, and detailed reporting. It provides a single entry
point for complete Core system validation.

Usage:
    python tests/run_comprehensive_core_tests.py
    python tests/run_comprehensive_core_tests.py --verbose
    python tests/run_comprehensive_core_tests.py --output-json results.json
"""

import os
import sys
import json
import time
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import test modules
from test_core_memory_management import run_memory_management_tests, MemoryManagementTestEnvironment
from test_core_multi_agent import run_multi_agent_tests, MultiAgentTestEnvironment

class CoreTestRunner:
    """Comprehensive Core test runner with logging and metrics."""
    
    def __init__(self, verbose: bool = False, output_file: Optional[str] = None):
        self.verbose = verbose
        self.output_file = output_file
        self.start_time = time.time()
        self.test_results = []
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup comprehensive test logger."""
        logger = logging.getLogger("core_test_runner")
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Detailed formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler for detailed logs
        log_file = Path(__file__).parent / "core_test_results.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def run_all_tests(self):
        """Run all Core tests with comprehensive logging."""
        self.logger.info("🚀 Starting Comprehensive Core Test Suite")
        self.logger.info("=" * 80)
        
        test_suites = [
            ("Memory Management", self._run_memory_management_tests),
            ("Multi-Agent Orchestration", self._run_multi_agent_tests),
            ("Error Handling", self._run_error_handling_tests),
            ("Performance", self._run_performance_tests),
            ("Integration", self._run_integration_tests)
        ]
        
        for suite_name, test_method in test_suites:
            self.logger.info(f"\n📋 Starting {suite_name} Test Suite")
            self.logger.info("-" * 60)
            
            suite_start_time = time.time()
            try:
                test_method()
                suite_duration = time.time() - suite_start_time
                
                self.test_results.append({
                    "suite": suite_name,
                    "status": "PASSED",
                    "duration": suite_duration,
                    "timestamp": datetime.now().isoformat()
                })
                
                self.logger.info(f"✅ {suite_name} Test Suite - PASSED ({suite_duration:.2f}s)")
                
            except Exception as e:
                suite_duration = time.time() - suite_start_time
                
                self.test_results.append({
                    "suite": suite_name,
                    "status": "FAILED",
                    "error": str(e),
                    "duration": suite_duration,
                    "timestamp": datetime.now().isoformat()
                })
                
                self.logger.error(f"❌ {suite_name} Test Suite - FAILED ({suite_duration:.2f}s)")
                self.logger.error(f"Error: {e}")
                
                if self.verbose:
                    self.logger.error(traceback.format_exc())
        
        self._generate_test_report()
    
    def _run_memory_management_tests(self):
        """Run memory management test suite."""
        self.logger.info("Running memory management tests...")
        
        # Create test environment
        env = MemoryManagementTestEnvironment()
        
        try:
            # Import and run tests
            from test_core_memory_management import MemoryManagementTests
            
            tests = MemoryManagementTests(env)
            tests.run_all_tests()
            
            # Log results
            passed = sum(1 for result in tests.test_results if result["status"] == "PASSED")
            failed = sum(1 for result in tests.test_results if result["status"] == "FAILED")
            
            self.logger.info(f"Memory Management Tests: {passed} passed, {failed} failed")
            
            if failed > 0:
                failed_tests = [r for r in tests.test_results if r["status"] == "FAILED"]
                for test in failed_tests:
                    self.logger.error(f"  Failed: {test['test']} - {test.get('error', 'Unknown error')}")
                    
        finally:
            env.cleanup()
    
    def _run_multi_agent_tests(self):
        """Run multi-agent orchestration test suite."""
        self.logger.info("Running multi-agent orchestration tests...")
        
        # Create test environment
        env = MultiAgentTestEnvironment()
        
        try:
            # Import and run tests
            from test_core_multi_agent import MultiAgentTests
            
            tests = MultiAgentTests(env)
            tests.run_all_tests()
            
            # Log results
            passed = sum(1 for result in tests.test_results if result["status"] == "PASSED")
            failed = sum(1 for result in tests.test_results if result["status"] == "FAILED")
            
            self.logger.info(f"Multi-Agent Tests: {passed} passed, {failed} failed")
            
            if failed > 0:
                failed_tests = [r for r in tests.test_results if r["status"] == "FAILED"]
                for test in failed_tests:
                    self.logger.error(f"  Failed: {test['test']} - {test.get('error', 'Unknown error')}")
                    
        finally:
            env.cleanup()
    
    def _run_error_handling_tests(self):
        """Run error handling and recovery tests."""
        self.logger.info("Running error handling tests...")
        
        # Import Core error handling modules
        from core.error_handling import (
            CoreErrorHandler, CoreErrorRecovery, CoreErrorValidator, CoreErrorMetrics
        )
        
        # Test error handler initialization
        logger = logging.getLogger("error_test")
        error_handler = CoreErrorHandler(logger)
        error_metrics = CoreErrorMetrics()
        
        # Test error validation
        test_cases = [
            ("valid_session_id", "core-12345678-1234-1234-1234-123456789abc", True),
            ("invalid_session_id", "invalid-session", False),
            ("empty_session_id", "", False),
            ("none_session_id", None, False)
        ]
        
        for test_name, session_id, expected in test_cases:
            result = CoreErrorValidator.validate_session_id(session_id)
            if result != expected:
                raise AssertionError(f"Error validation failed for {test_name}")
            
            self.logger.debug(f"✓ {test_name}: {result}")
        
        # Test participant validation
        valid_participant = {
            "id": "test-participant",
            "type": "persona",
            "name": "Test Participant"
        }
        
        if not CoreErrorValidator.validate_participant_data(valid_participant):
            raise AssertionError("Valid participant validation failed")
        
        invalid_participant = {
            "id": "test-participant",
            "type": "invalid_type"
        }
        
        if CoreErrorValidator.validate_participant_data(invalid_participant):
            raise AssertionError("Invalid participant validation should have failed")
        
        self.logger.info("✓ Error handling tests completed successfully")
    
    def _run_performance_tests(self):
        """Run performance benchmarks."""
        self.logger.info("Running performance tests...")
        
        # Create minimal test environment
        import tempfile
        from core.core import Core
        from vault.vault import Vault
        
        tmpdir = Path(tempfile.mkdtemp())
        
        try:
            # Setup basic configuration
            core_config = {
                "session": {"max_participants": 10},
                "communal_memory": {"max_insights_per_session": 100},
                "performance": {"cache_session_data": True}
            }
            
            vault_config = {
                "encryption": {"algorithm": "AES-256", "key_file": str(tmpdir / "vault.key")},
                "storage": {"type": "file", "file_path": str(tmpdir / "vault.db")}
            }
            
            logger = logging.getLogger("performance_test")
            vault = Vault(vault_config, logger)
            core = Core(core_config, vault, logger)
            
            # Performance test: Session creation
            start_time = time.time()
            session_ids = []
            for i in range(10):
                session_id = core.create_session(f"user-{i}", f"Performance Test Session {i}")
                session_ids.append(session_id)
            
            session_creation_time = time.time() - start_time
            
            # Performance test: Participant addition
            start_time = time.time()
            test_participant = {
                "id": "test-participant",
                "type": "persona",
                "name": "Test Participant"
            }
            
            for session_id in session_ids:
                core.add_participant(session_id, "user-1", test_participant)
            
            participant_addition_time = time.time() - start_time
            
            # Performance test: Session retrieval
            start_time = time.time()
            for session_id in session_ids:
                session = core.get_session(session_id)
                assert session is not None
            
            session_retrieval_time = time.time() - start_time
            
            # Log performance metrics
            self.logger.info(f"Performance Metrics:")
            self.logger.info(f"  Session Creation: {session_creation_time:.3f}s (10 sessions)")
            self.logger.info(f"  Participant Addition: {participant_addition_time:.3f}s (10 participants)")
            self.logger.info(f"  Session Retrieval: {session_retrieval_time:.3f}s (10 retrievals)")
            
            # Verify performance is reasonable
            if session_creation_time > 5.0:
                raise AssertionError("Session creation performance is too slow")
            if participant_addition_time > 5.0:
                raise AssertionError("Participant addition performance is too slow")
            if session_retrieval_time > 2.0:
                raise AssertionError("Session retrieval performance is too slow")
            
            self.logger.info("✓ Performance tests completed successfully")
            
        finally:
            import shutil
            shutil.rmtree(tmpdir)
    
    def _run_integration_tests(self):
        """Run integration tests between Core and other modules."""
        self.logger.info("Running integration tests...")
        
        # Test Core-Vault integration
        import tempfile
        from core.core import Core
        from vault.vault import Vault
        
        tmpdir = Path(tempfile.mkdtemp())
        
        try:
            # Setup configuration
            core_config = {
                "session": {"max_participants": 5},
                "communal_memory": {"auto_share_insights": True},
                "audit": {"log_all_events": True}
            }
            
            vault_config = {
                "encryption": {"algorithm": "AES-256", "key_file": str(tmpdir / "vault.key")},
                "storage": {"type": "file", "file_path": str(tmpdir / "vault.db")},
                "audit": {"log_file": str(tmpdir / "integration_audit.log")}
            }
            
            logger = logging.getLogger("integration_test")
            vault = Vault(vault_config, logger)
            core = Core(core_config, vault, logger)
            
            # Test session creation and Vault integration
            session_id = core.create_session("user-1", "Integration Test Session")
            
            # Test participant addition
            test_participant = {
                "id": "integration-participant",
                "type": "persona",
                "name": "Integration Test Participant"
            }
            
            core.add_participant(session_id, "user-1", test_participant)
            
            # Test insight sharing and Vault storage
            success = core.share_insight(
                session_id,
                "integration-participant",
                "Integration test insight",
                {"category": "test", "integration": True}
            )
            
            if not success:
                raise AssertionError("Insight sharing failed in integration test")
            
            # Test session retrieval
            session = core.get_session(session_id)
            if not session:
                raise AssertionError("Session retrieval failed in integration test")
            
            # Verify insights were stored
            insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
            if len(insight_events) != 1:
                raise AssertionError("Insight storage failed in integration test")
            
            # Test session export
            export_data = core.export_session_log(session_id, "user-1")
            if not export_data:
                raise AssertionError("Session export failed in integration test")
            
            # Test audit logging
            audit_file = tmpdir / "integration_audit.log"
            if not audit_file.exists():
                raise AssertionError("Audit logging failed in integration test")
            
            self.logger.info("✓ Integration tests completed successfully")
            
        finally:
            import shutil
            shutil.rmtree(tmpdir)
    
    def _generate_test_report(self):
        """Generate comprehensive test report."""
        total_duration = time.time() - self.start_time
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("📊 COMPREHENSIVE CORE TEST REPORT")
        self.logger.info("=" * 80)
        
        # Summary statistics
        total_suites = len(self.test_results)
        passed_suites = sum(1 for result in self.test_results if result["status"] == "PASSED")
        failed_suites = sum(1 for result in self.test_results if result["status"] == "FAILED")
        
        self.logger.info(f"Test Execution Summary:")
        self.logger.info(f"  Total Test Suites: {total_suites}")
        self.logger.info(f"  Passed: {passed_suites}")
        self.logger.info(f"  Failed: {failed_suites}")
        self.logger.info(f"  Success Rate: {(passed_suites/total_suites*100):.1f}%")
        self.logger.info(f"  Total Duration: {total_duration:.2f}s")
        
        # Detailed results
        self.logger.info(f"\nDetailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            self.logger.info(f"  {status_icon} {result['suite']}: {result['status']} ({result['duration']:.2f}s)")
            
            if result["status"] == "FAILED":
                self.logger.error(f"    Error: {result.get('error', 'Unknown error')}")
        
        # Performance summary
        self.logger.info(f"\nPerformance Summary:")
        suite_durations = [(r['suite'], r['duration']) for r in self.test_results]
        suite_durations.sort(key=lambda x: x[1], reverse=True)
        
        for suite, duration in suite_durations:
            self.logger.info(f"  {suite}: {duration:.2f}s")
        
        # System information
        self.logger.info(f"\nSystem Information:")
        self.logger.info(f"  Python Version: {sys.version}")
        self.logger.info(f"  Platform: {sys.platform}")
        self.logger.info(f"  Test Time: {datetime.now().isoformat()}")
        
        # Save JSON report if requested
        if self.output_file:
            self._save_json_report()
        
        # Final status
        if failed_suites == 0:
            self.logger.info("\n🎉 ALL CORE TESTS PASSED!")
        else:
            self.logger.error(f"\n⚠️  {failed_suites} TEST SUITE(S) FAILED")
            
        return failed_suites == 0
    
    def _save_json_report(self):
        """Save detailed test report as JSON."""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": time.time() - self.start_time,
            "summary": {
                "total_suites": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["status"] == "PASSED"),
                "failed": sum(1 for r in self.test_results if r["status"] == "FAILED")
            },
            "results": self.test_results,
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": str(Path.cwd())
            }
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.logger.info(f"📄 Detailed report saved to: {self.output_file}")

def main():
    """Main entry point for comprehensive Core tests."""
    parser = argparse.ArgumentParser(description="Run comprehensive Core module tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--output-json", "-o", help="Save JSON report to file")
    parser.add_argument("--quick", "-q", action="store_true", help="Run quick tests only")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = CoreTestRunner(verbose=args.verbose, output_file=args.output_json)
    
    try:
        # Run tests
        success = runner.run_all_tests()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()