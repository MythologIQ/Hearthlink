#!/usr/bin/env python3
"""
Core Multi-Agent Session Tests

Comprehensive test suite for Core module multi-agent orchestration,
including session management, turn-taking, breakout rooms, and
communal memory management with various scenarios and edge cases.
"""

import os
import sys
import json
import tempfile
import time
import threading
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.core import Core, Session, Participant, ParticipantType, SessionStatus, CoreError
from core.error_handling import (
    CoreErrorHandler, CoreErrorRecovery, CoreErrorValidator, CoreErrorMetrics,
    SessionNotFoundError, ParticipantNotFoundError, InvalidOperationError,
    TurnTakingError, BreakoutRoomError, CommunalMemoryError, VaultIntegrationError
)
from vault.vault import Vault

class MultiAgentTestEnvironment:
    """Test environment for multi-agent Core testing."""
    
    def __init__(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.core_config = self._get_core_config()
        self.vault_config = self._get_vault_config()
        self.logger = self._setup_logger()
        
        # Initialize modules
        self.vault = Vault(self.vault_config, self.logger)
        self.core = Core(self.core_config, self.vault, self.logger)
        
        # Initialize error handling
        self.error_handler = CoreErrorHandler(self.logger)
        self.error_metrics = CoreErrorMetrics()
        
        # Setup error recovery strategies
        self._setup_error_recovery()
        
        # Test data
        self.test_sessions: List[str] = []
        self.test_participants = self._get_test_participants()
    
    def _get_core_config(self) -> Dict[str, Any]:
        """Get Core configuration for testing."""
        return {
            "session": {
                "max_participants": 10,
                "max_breakouts_per_session": 5,
                "session_timeout_minutes": 60,
                "auto_archive_after_days": 7
            },
            "turn_taking": {
                "turn_timeout_seconds": 30,
                "auto_advance": True,
                "allow_manual_turn_set": True,
                "max_turn_duration_minutes": 5
            },
            "communal_memory": {
                "auto_share_insights": False,
                "insight_approval_required": True,
                "max_insights_per_session": 50,
                "insight_retention_days": 30
            },
            "live_feed": {
                "default_verbosity": "default",
                "auto_include_external": True,
                "show_metadata": False,
                "max_events_in_feed": 100
            },
            "audit": {
                "log_all_events": True,
                "retention_days": 30,
                "export_formats": ["json", "csv"]
            },
            "agent_suggestions": {
                "enable_suggestions": True,
                "suggestion_threshold": 0.7,
                "max_suggestions_per_session": 3,
                "suggestion_cooldown_minutes": 5
            },
            "breakout_rooms": {
                "max_participants_per_breakout": 6,
                "auto_end_breakout_after_minutes": 30,
                "allow_cross_breakout_communication": False
            },
            "performance": {
                "cache_session_data": True,
                "cache_ttl_seconds": 60,
                "max_concurrent_sessions": 10,
                "session_cleanup_interval_minutes": 10
            }
        }
    
    def _get_vault_config(self) -> Dict[str, Any]:
        """Get Vault configuration for testing."""
        return {
            "encryption": {
                "algorithm": "AES-256",
                "key_file": str(self.tmpdir / "vault.key"),
                "key_env_var": None
            },
            "storage": {
                "type": "file",
                "file_path": str(self.tmpdir / "vault.db")
            },
            "audit": {
                "log_file": str(self.tmpdir / "audit.log")
            },
            "schema_version": "1.0.0"
        }
    
    def _setup_logger(self):
        """Setup test logger."""
        import logging
        
        logger = logging.getLogger("core_test")
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(self.tmpdir / "core_test.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _setup_error_recovery(self):
        """Setup error recovery strategies."""
        self.error_handler.register_recovery_strategy(
            ErrorCategory.SESSION_MANAGEMENT,
            CoreErrorRecovery.session_management_recovery
        )
        self.error_handler.register_recovery_strategy(
            ErrorCategory.PARTICIPANT_MANAGEMENT,
            CoreErrorRecovery.participant_management_recovery
        )
        self.error_handler.register_recovery_strategy(
            ErrorCategory.TURN_TAKING,
            CoreErrorRecovery.turn_taking_recovery
        )
        self.error_handler.register_recovery_strategy(
            ErrorCategory.VAULT_INTEGRATION,
            CoreErrorRecovery.vault_integration_recovery
        )
    
    def _get_test_participants(self) -> List[Dict[str, Any]]:
        """Get test participant definitions."""
        return [
            {
                "id": "alden",
                "type": "persona",
                "name": "Alden",
                "role": "evolutionary_companion"
            },
            {
                "id": "alice",
                "type": "persona",
                "name": "Alice",
                "role": "cognitive_behavioral"
            },
            {
                "id": "mimic",
                "type": "persona",
                "name": "Mimic",
                "role": "dynamic_persona"
            },
            {
                "id": "research-bot",
                "type": "external",
                "name": "Research Bot",
                "role": "external_researcher"
            },
            {
                "id": "analyst-ai",
                "type": "external",
                "name": "Analyst AI",
                "role": "data_analyst"
            },
            {
                "id": "user-1",
                "type": "user",
                "name": "Test User 1",
                "role": "session_owner"
            }
        ]
    
    def cleanup(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.tmpdir)

class MultiAgentSessionTests:
    """Test suite for multi-agent session scenarios."""
    
    def __init__(self, env: MultiAgentTestEnvironment):
        self.env = env
        self.test_results = []
    
    def run_all_tests(self):
        """Run all multi-agent session tests."""
        print("🚀 Starting Multi-Agent Session Test Suite")
        print("=" * 60)
        
        test_methods = [
            self.test_basic_multi_agent_session,
            self.test_turn_taking_with_multiple_agents,
            self.test_breakout_room_scenarios,
            self.test_communal_memory_sharing,
            self.test_concurrent_session_management,
            self.test_error_scenarios,
            self.test_performance_scenarios,
            self.test_memory_management,
            self.test_session_lifecycle,
            self.test_edge_cases
        ]
        
        for test_method in test_methods:
            try:
                print(f"\n📋 Running: {test_method.__name__}")
                test_method()
                self.test_results.append({
                    "test": test_method.__name__,
                    "status": "PASSED",
                    "timestamp": datetime.now().isoformat()
                })
                print(f"✅ {test_method.__name__} - PASSED")
            except Exception as e:
                self.test_results.append({
                    "test": test_method.__name__,
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                print(f"❌ {test_method.__name__} - FAILED: {e}")
                self.env.logger.error(f"Test {test_method.__name__} failed: {e}")
        
        self._print_test_summary()
    
    def test_basic_multi_agent_session(self):
        """Test basic multi-agent session creation and management."""
        print("  Testing basic multi-agent session...")
        
        # Create session
        session_id = self.env.core.create_session("user-1", "AI Ethics Roundtable")
        self.env.test_sessions.append(session_id)
        
        # Add multiple participants
        for participant in self.env.test_participants[:4]:  # Add first 4 participants
            success = self.env.core.add_participant(session_id, "user-1", participant)
            assert success, f"Failed to add participant {participant['id']}"
        
        # Verify session state
        session = self.env.core.get_session(session_id)
        assert session is not None
        assert len(session.participants) == 4
        assert session.status == SessionStatus.ACTIVE
        
        # Test participant roles
        alden = next(p for p in session.participants if p.id == "alden")
        assert alden.role == "evolutionary_companion"
        
        print("    ✓ Basic multi-agent session created successfully")
    
    def test_turn_taking_with_multiple_agents(self):
        """Test turn-taking coordination with multiple agents."""
        print("  Testing turn-taking with multiple agents...")
        
        # Create session with participants
        session_id = self.env.core.create_session("user-1", "Turn-Taking Test")
        self.env.test_sessions.append(session_id)
        
        # Add participants
        for participant in self.env.test_participants[:3]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Start turn-taking
        success = self.env.core.start_turn_taking(session_id, "user-1")
        assert success, "Failed to start turn-taking"
        
        session = self.env.core.get_session(session_id)
        assert session.current_turn is not None
        assert len(session.turn_order) == 3
        
        # Simulate turn progression
        turns_completed = []
        for i in range(len(session.turn_order)):
            current_turn = session.current_turn
            turns_completed.append(current_turn)
            
            # Share insight during turn
            insight = f"Insight from {current_turn} during turn {i+1}"
            self.env.core.share_insight(session_id, current_turn, insight, {"turn": i+1})
            
            # Advance turn
            next_turn = self.env.core.advance_turn(session_id, "user-1")
            if next_turn is None:
                break
        
        # Verify all participants had turns
        assert len(turns_completed) == 3
        assert len(set(turns_completed)) == 3  # All unique
        
        print("    ✓ Turn-taking with multiple agents completed successfully")
    
    def test_breakout_room_scenarios(self):
        """Test various breakout room scenarios."""
        print("  Testing breakout room scenarios...")
        
        # Create main session
        session_id = self.env.core.create_session("user-1", "Breakout Room Test")
        self.env.test_sessions.append(session_id)
        
        # Add participants
        for participant in self.env.test_participants[:5]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Create breakout room
        breakout_id = self.env.core.create_breakout(
            session_id, "user-1", "AI Ethics Deep Dive", ["alice", "research-bot"]
        )
        
        # Verify breakout creation
        session = self.env.core.get_session(session_id)
        assert len(session.breakouts) == 1
        breakout = session.breakouts[0]
        assert breakout.topic == "AI Ethics Deep Dive"
        assert breakout.participants == ["alice", "research-bot"]
        
        # Simulate breakout activity
        for participant in ["alice", "research-bot"]:
            insight = f"Breakout insight from {participant}"
            self.env.core.share_insight(session_id, participant, insight, {"breakout_id": breakout_id})
        
        # Create second breakout
        breakout_id_2 = self.env.core.create_breakout(
            session_id, "user-1", "Technical Discussion", ["mimic", "analyst-ai"]
        )
        
        # End first breakout
        success = self.env.core.end_breakout(session_id, "user-1", breakout_id)
        assert success, "Failed to end breakout"
        
        # Verify breakout ended
        session = self.env.core.get_session(session_id)
        ended_breakout = next(b for b in session.breakouts if b.breakout_id == breakout_id)
        assert ended_breakout.ended_at is not None
        
        print("    ✓ Breakout room scenarios completed successfully")
    
    def test_communal_memory_sharing(self):
        """Test communal memory sharing between agents."""
        print("  Testing communal memory sharing...")
        
        # Create session
        session_id = self.env.core.create_session("user-1", "Communal Memory Test")
        self.env.test_sessions.append(session_id)
        
        # Add participants
        for participant in self.env.test_participants[:4]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Share insights from different participants
        insights = [
            {
                "participant": "alden",
                "insight": "User shows strong analytical thinking patterns",
                "context": {"type": "observation", "confidence": 0.85}
            },
            {
                "participant": "alice",
                "insight": "Consider implementing structured feedback loops",
                "context": {"type": "suggestion", "priority": "medium"}
            },
            {
                "participant": "mimic",
                "insight": "User responds well to collaborative approaches",
                "context": {"type": "behavioral_insight", "category": "interaction"}
            },
            {
                "participant": "research-bot",
                "insight": "Current AI ethics frameworks align with user values",
                "context": {"type": "research_finding", "source": "external"}
            }
        ]
        
        # Share insights
        for insight_data in insights:
            success = self.env.core.share_insight(
                session_id,
                insight_data["participant"],
                insight_data["insight"],
                insight_data["context"]
            )
            assert success, f"Failed to share insight from {insight_data['participant']}"
        
        # Verify insights in session log
        session = self.env.core.get_session(session_id)
        insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
        assert len(insight_events) == 4
        
        # Export session to verify communal memory
        export_data = self.env.core.export_session_log(session_id, "user-1")
        export_json = json.loads(export_data)
        assert len(export_json["events"]) >= 4
        
        print("    ✓ Communal memory sharing completed successfully")
    
    def test_concurrent_session_management(self):
        """Test concurrent session management scenarios."""
        print("  Testing concurrent session management...")
        
        # Create multiple sessions concurrently
        session_ids = []
        for i in range(3):
            topic = f"Concurrent Session {i+1}"
            session_id = self.env.core.create_session(f"user-{i+1}", topic)
            session_ids.append(session_id)
            self.env.test_sessions.append(session_id)
        
        # Add participants to each session
        for session_id in session_ids:
            for participant in self.env.test_participants[:2]:
                self.env.core.add_participant(session_id, "user-1", participant)
        
        # Verify all sessions exist and are active
        active_sessions = self.env.core.get_active_sessions()
        assert len(active_sessions) >= 3
        
        # Test session operations across multiple sessions
        for session_id in session_ids:
            # Start turn-taking
            self.env.core.start_turn_taking(session_id, "user-1")
            
            # Share insights
            self.env.core.share_insight(session_id, "alden", f"Insight in session {session_id}")
        
        print("    ✓ Concurrent session management completed successfully")
    
    def test_error_scenarios(self):
        """Test various error scenarios and recovery."""
        print("  Testing error scenarios...")
        
        # Test invalid session ID
        try:
            self.env.core.get_session("invalid-session")
            assert False, "Should raise error for invalid session"
        except CoreError:
            pass
        
        # Test adding participant to non-existent session
        try:
            self.env.core.add_participant("invalid-session", "user-1", self.env.test_participants[0])
            assert False, "Should raise error for invalid session"
        except CoreError:
            pass
        
        # Test removing non-existent participant
        session_id = self.env.core.create_session("user-1", "Error Test")
        self.env.test_sessions.append(session_id)
        self.env.core.add_participant(session_id, "user-1", self.env.test_participants[0])
        
        try:
            self.env.core.remove_participant(session_id, "user-1", "non-existent")
            assert False, "Should raise error for non-existent participant"
        except CoreError:
            pass
        
        # Test invalid turn-taking
        try:
            self.env.core.start_turn_taking(session_id, "user-1")
            self.env.core.advance_turn(session_id, "user-1")  # Should work
            self.env.core.advance_turn(session_id, "user-1")  # Should work
            self.env.core.advance_turn(session_id, "user-1")  # Should return None (complete)
        except CoreError:
            pass
        
        print("    ✓ Error scenarios handled correctly")
    
    def test_performance_scenarios(self):
        """Test performance scenarios with multiple operations."""
        print("  Testing performance scenarios...")
        
        # Create session with many participants
        session_id = self.env.core.create_session("user-1", "Performance Test")
        self.env.test_sessions.append(session_id)
        
        # Add many participants
        start_time = time.time()
        for participant in self.env.test_participants:
            self.env.core.add_participant(session_id, "user-1", participant)
        add_time = time.time() - start_time
        
        # Test turn-taking performance
        self.env.core.start_turn_taking(session_id, "user-1")
        
        start_time = time.time()
        for i in range(len(self.env.test_participants)):
            self.env.core.advance_turn(session_id, "user-1")
        turn_time = time.time() - start_time
        
        # Test insight sharing performance
        start_time = time.time()
        for i in range(10):
            self.env.core.share_insight(session_id, "alden", f"Performance insight {i}")
        insight_time = time.time() - start_time
        
        # Record performance metrics
        self.env.error_metrics.record_performance("add_participants", add_time)
        self.env.error_metrics.record_performance("turn_taking", turn_time)
        self.env.error_metrics.record_performance("insight_sharing", insight_time)
        
        print(f"    ✓ Performance test completed - Add: {add_time:.3f}s, Turn: {turn_time:.3f}s, Insight: {insight_time:.3f}s")
    
    def test_memory_management(self):
        """Test memory management and cleanup."""
        print("  Testing memory management...")
        
        # Create multiple sessions
        session_ids = []
        for i in range(5):
            session_id = self.env.core.create_session(f"user-{i+1}", f"Memory Test {i+1}")
            session_ids.append(session_id)
            self.env.test_sessions.append(session_id)
            
            # Add participants and share insights
            for participant in self.env.test_participants[:2]:
                self.env.core.add_participant(session_id, f"user-{i+1}", participant)
                self.env.core.share_insight(session_id, participant["id"], f"Memory test insight {i}")
        
        # End some sessions
        for session_id in session_ids[:2]:
            self.env.core.end_session(session_id, "user-1")
        
        # Verify active sessions
        active_sessions = self.env.core.get_active_sessions()
        assert len(active_sessions) >= 3  # At least 3 should still be active
        
        # Test session export for memory verification
        for session_id in session_ids[2:]:  # Export active sessions
            export_data = self.env.core.export_session_log(session_id, "user-1")
            export_json = json.loads(export_data)
            assert len(export_json["events"]) > 0
        
        print("    ✓ Memory management test completed successfully")
    
    def test_session_lifecycle(self):
        """Test complete session lifecycle."""
        print("  Testing session lifecycle...")
        
        # Create session
        session_id = self.env.core.create_session("user-1", "Lifecycle Test")
        self.env.test_sessions.append(session_id)
        
        # Add participants
        for participant in self.env.test_participants[:3]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Start turn-taking
        self.env.core.start_turn_taking(session_id, "user-1")
        
        # Simulate some activity
        for i in range(2):
            current_turn = self.env.core.get_session(session_id).current_turn
            self.env.core.share_insight(session_id, current_turn, f"Lifecycle insight {i}")
            self.env.core.advance_turn(session_id, "user-1")
        
        # Pause session
        self.env.core.pause_session(session_id, "user-1")
        session = self.env.core.get_session(session_id)
        assert session.status == SessionStatus.PAUSED
        
        # Resume session
        self.env.core.resume_session(session_id, "user-1")
        session = self.env.core.get_session(session_id)
        assert session.status == SessionStatus.ACTIVE
        
        # End session
        self.env.core.end_session(session_id, "user-1")
        session = self.env.core.get_session(session_id)
        assert session.status == SessionStatus.ENDED
        
        print("    ✓ Session lifecycle test completed successfully")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("  Testing edge cases...")
        
        # Test session with maximum participants
        session_id = self.env.core.create_session("user-1", "Edge Case Test")
        self.env.test_sessions.append(session_id)
        
        # Add participants up to limit
        max_participants = self.env.core_config["session"]["max_participants"]
        for i in range(min(max_participants, len(self.env.test_participants))):
            participant = self.env.test_participants[i]
            success = self.env.core.add_participant(session_id, "user-1", participant)
            assert success, f"Failed to add participant {i+1}"
        
        # Test turn-taking with single participant
        single_session_id = self.env.core.create_session("user-1", "Single Participant Test")
        self.env.test_sessions.append(single_session_id)
        self.env.core.add_participant(single_session_id, "user-1", self.env.test_participants[0])
        
        self.env.core.start_turn_taking(single_session_id, "user-1")
        next_turn = self.env.core.advance_turn(single_session_id, "user-1")
        assert next_turn is None, "Single participant turn-taking should complete immediately"
        
        # Test empty session operations
        empty_session_id = self.env.core.create_session("user-1", "Empty Session Test")
        self.env.test_sessions.append(empty_session_id)
        
        # Try to start turn-taking with no participants
        try:
            self.env.core.start_turn_taking(empty_session_id, "user-1")
            # Should handle gracefully
        except CoreError:
            pass
        
        print("    ✓ Edge cases handled correctly")
    
    def _print_test_summary(self):
        """Print test summary and metrics."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["status"] == "PASSED")
        failed = sum(1 for result in self.test_results if result["status"] == "FAILED")
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        # Print error summary
        error_summary = self.env.error_handler.get_error_summary()
        print(f"\nError Summary:")
        print(f"Total Errors: {error_summary['total_errors']}")
        for category, count in error_summary['errors_by_category'].items():
            if count > 0:
                print(f"  {category}: {count}")
        
        # Print performance summary
        performance_summary = self.env.error_metrics.get_performance_summary()
        if performance_summary:
            print(f"\nPerformance Summary:")
            for operation, metrics in performance_summary.items():
                print(f"  {operation}:")
                print(f"    Avg: {metrics['avg_duration']:.3f}s")
                print(f"    Min: {metrics['min_duration']:.3f}s")
                print(f"    Max: {metrics['max_duration']:.3f}s")
                print(f"    Total: {metrics['total_operations']}")
        
        # Print failed tests
        failed_tests = [result for result in self.test_results if result["status"] == "FAILED"]
        if failed_tests:
            print(f"\nFailed Tests:")
            for test in failed_tests:
                print(f"  {test['test']}: {test.get('error', 'Unknown error')}")

def run_multi_agent_tests():
    """Run all multi-agent session tests."""
    env = MultiAgentTestEnvironment()
    
    try:
        tests = MultiAgentSessionTests(env)
        tests.run_all_tests()
        
        print("\n✅ Multi-Agent Session Test Suite Completed!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        env.cleanup()

if __name__ == "__main__":
    run_multi_agent_tests() 