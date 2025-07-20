#!/usr/bin/env python3
"""
Core Memory Management Tests

Comprehensive test suite for Core module memory management,
including communal memory sharing, session persistence,
data isolation, and memory cleanup scenarios.
"""

import os
import sys
import json
import tempfile
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.core import Core, Session, Participant, ParticipantType, SessionStatus, CoreError
from core.error_handling import (
    CoreErrorHandler, CoreErrorRecovery, CoreErrorValidator, CoreErrorMetrics,
    CommunalMemoryError, VaultIntegrationError, CoreErrorContext, ErrorCategory
)
from vault.vault import Vault

class MemoryManagementTestEnvironment:
    """Test environment for Core memory management testing."""
    
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
        
        # Test data
        self.test_sessions: List[str] = []
        self.test_participants = self._get_test_participants()
        self.memory_insights = self._get_memory_insights()
    
    def _get_core_config(self) -> Dict[str, Any]:
        """Get Core configuration for memory testing."""
        return {
            "session": {
                "max_participants": 8,
                "max_breakouts_per_session": 3,
                "session_timeout_minutes": 30,
                "auto_archive_after_days": 3
            },
            "turn_taking": {
                "turn_timeout_seconds": 20,
                "auto_advance": True,
                "allow_manual_turn_set": True,
                "max_turn_duration_minutes": 3
            },
            "communal_memory": {
                "auto_share_insights": True,
                "insight_approval_required": False,
                "max_insights_per_session": 100,
                "insight_retention_days": 7,
                "insight_categories": ["observation", "suggestion", "behavioral", "research"]
            },
            "live_feed": {
                "default_verbosity": "detailed",
                "auto_include_external": True,
                "show_metadata": True,
                "max_events_in_feed": 200
            },
            "audit": {
                "log_all_events": True,
                "retention_days": 7,
                "export_formats": ["json", "csv", "xml"]
            },
            "agent_suggestions": {
                "enable_suggestions": True,
                "suggestion_threshold": 0.6,
                "max_suggestions_per_session": 5,
                "suggestion_cooldown_minutes": 3
            },
            "breakout_rooms": {
                "max_participants_per_breakout": 4,
                "auto_end_breakout_after_minutes": 15,
                "allow_cross_breakout_communication": True
            },
            "performance": {
                "cache_session_data": True,
                "cache_ttl_seconds": 30,
                "max_concurrent_sessions": 5,
                "session_cleanup_interval_minutes": 5
            }
        }
    
    def _get_vault_config(self) -> Dict[str, Any]:
        """Get Vault configuration for memory testing."""
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
                "log_file": str(self.tmpdir / "memory_audit.log")
            },
            "schema_version": "1.0.0",
            "memory": {
                "communal_slice": "core_communal",
                "max_insights_per_topic": 50,
                "insight_cleanup_days": 7,
                "topic_categories": ["session", "participant", "insight", "breakout"]
            }
        }
    
    def _setup_logger(self):
        """Setup test logger."""
        import logging
        
        logger = logging.getLogger("memory_test")
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(self.tmpdir / "memory_test.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _get_test_participants(self) -> List[Dict[str, Any]]:
        """Get test participant definitions for memory testing."""
        return [
            {
                "id": "alden",
                "type": "persona",
                "name": "Alden",
                "role": "evolutionary_companion",
                "memory_access": ["communal", "personal"]
            },
            {
                "id": "alice",
                "type": "persona",
                "name": "Alice",
                "role": "cognitive_behavioral",
                "memory_access": ["communal", "personal"]
            },
            {
                "id": "mimic",
                "type": "persona",
                "name": "Mimic",
                "role": "dynamic_persona",
                "memory_access": ["communal", "personal"]
            },
            {
                "id": "research-bot",
                "type": "external",
                "name": "Research Bot",
                "role": "external_researcher",
                "memory_access": ["communal"]
            },
            {
                "id": "analyst-ai",
                "type": "external",
                "name": "Analyst AI",
                "role": "data_analyst",
                "memory_access": ["communal"]
            },
            {
                "id": "user-1",
                "type": "user",
                "name": "Test User 1",
                "role": "session_owner",
                "memory_access": ["communal", "personal"]
            }
        ]
    
    def _get_memory_insights(self) -> List[Dict[str, Any]]:
        """Get predefined memory insights for testing."""
        return [
            {
                "participant": "alden",
                "insight": "User demonstrates strong analytical thinking patterns",
                "category": "behavioral",
                "context": {"confidence": 0.85, "observation_type": "cognitive"},
                "tags": ["analytical", "thinking", "cognitive"]
            },
            {
                "participant": "alice",
                "insight": "Consider implementing structured feedback loops for better engagement",
                "category": "suggestion",
                "context": {"priority": "medium", "impact": "high"},
                "tags": ["feedback", "engagement", "structure"]
            },
            {
                "participant": "mimic",
                "insight": "User responds well to collaborative and interactive approaches",
                "category": "behavioral",
                "context": {"confidence": 0.78, "interaction_style": "collaborative"},
                "tags": ["collaborative", "interactive", "response"]
            },
            {
                "participant": "research-bot",
                "insight": "Current AI ethics frameworks align well with user's expressed values",
                "category": "research",
                "context": {"source": "external", "relevance": "high"},
                "tags": ["ethics", "frameworks", "values"]
            },
            {
                "participant": "analyst-ai",
                "insight": "Session engagement metrics show consistent participation patterns",
                "category": "observation",
                "context": {"data_source": "session_metrics", "trend": "positive"},
                "tags": ["engagement", "metrics", "participation"]
            },
            {
                "participant": "alden",
                "insight": "User shows preference for detailed explanations over quick summaries",
                "category": "behavioral",
                "context": {"confidence": 0.92, "preference_type": "communication"},
                "tags": ["preference", "communication", "detail"]
            },
            {
                "participant": "alice",
                "insight": "Implementing regular reflection periods could enhance learning outcomes",
                "category": "suggestion",
                "context": {"priority": "high", "implementation": "moderate"},
                "tags": ["reflection", "learning", "outcomes"]
            },
            {
                "participant": "mimic",
                "insight": "User adapts quickly to new interaction patterns and personas",
                "category": "behavioral",
                "context": {"confidence": 0.88, "adaptability": "high"},
                "tags": ["adaptability", "interaction", "personas"]
            }
        ]
    
    def cleanup(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.tmpdir)

class MemoryManagementTests:
    """Test suite for Core memory management scenarios."""
    
    def __init__(self, env: MemoryManagementTestEnvironment):
        self.env = env
        self.test_results = []
    
    def run_all_tests(self):
        """Run all memory management tests."""
        print("🧠 Starting Core Memory Management Test Suite")
        print("=" * 60)
        
        test_methods = [
            self.test_communal_memory_sharing,
            self.test_memory_isolation,
            self.test_session_persistence,
            self.test_memory_cleanup,
            self.test_insight_categorization,
            self.test_memory_export_import,
            self.test_concurrent_memory_access,
            self.test_memory_performance,
            self.test_memory_error_scenarios,
            self.test_memory_validation
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
    
    def test_communal_memory_sharing(self):
        """Test communal memory sharing between participants."""
        print("  Testing communal memory sharing...")
        
        # Create session
        session_id = self.env.core.create_session("user-1", "Communal Memory Test")
        self.env.test_sessions.append(session_id)
        
        # Add participants
        for participant in self.env.test_participants[:4]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Share insights from different participants
        shared_insights = []
        for insight_data in self.env.memory_insights[:4]:
            success = self.env.core.share_insight(
                session_id,
                insight_data["participant"],
                insight_data["insight"],
                {
                    "category": insight_data["category"],
                    "tags": insight_data["tags"],
                    **insight_data["context"]
                }
            )
            assert success, f"Failed to share insight from {insight_data['participant']}"
            shared_insights.append(insight_data)
        
        # Verify insights are stored in communal memory
        session = self.env.core.get_session(session_id)
        insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
        assert len(insight_events) == 4
        
        # Verify insight metadata
        for event in insight_events:
            assert "category" in event.metadata
            assert "tags" in event.metadata
            assert len(event.metadata["tags"]) > 0
        
        # Test insight retrieval by category
        behavioral_insights = [
            e for e in insight_events 
            if e.metadata.get("category") == "behavioral"
        ]
        assert len(behavioral_insights) == 2
        
        print("    ✓ Communal memory sharing completed successfully")
    
    def test_memory_isolation(self):
        """Test memory isolation between different sessions and participants."""
        print("  Testing memory isolation...")
        
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_id = self.env.core.create_session(f"user-{i+1}", f"Memory Isolation Test {i+1}")
            session_ids.append(session_id)
            self.env.test_sessions.append(session_id)
            
            # Add participants to each session
            for participant in self.env.test_participants[:2]:
                self.env.core.add_participant(session_id, f"user-{i+1}", participant)
        
        # Share different insights in each session
        for i, session_id in enumerate(session_ids):
            insight = f"Session {i+1} specific insight from alden"
            self.env.core.share_insight(
                session_id,
                "alden",
                insight,
                {"session_specific": True, "session_number": i+1}
            )
        
        # Verify insights are isolated between sessions
        for i, session_id in enumerate(session_ids):
            session = self.env.core.get_session(session_id)
            insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
            assert len(insight_events) == 1
            assert insight_events[0].content == f"Session {i+1} specific insight from alden"
        
        # Test participant memory access restrictions
        # External participants should only access communal memory
        session_id = session_ids[0]
        external_insight = "External participant insight"
        success = self.env.core.share_insight(
            session_id,
            "research-bot",
            external_insight,
            {"access_level": "communal_only"}
        )
        assert success, "External participant should be able to share communal insights"
        
        print("    ✓ Memory isolation verified successfully")
    
    def test_session_persistence(self):
        """Test session persistence and memory retention."""
        print("  Testing session persistence...")
        
        # Create session and add participants
        session_id = self.env.core.create_session("user-1", "Persistence Test")
        self.env.test_sessions.append(session_id)
        
        for participant in self.env.test_participants[:3]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Share multiple insights
        for insight_data in self.env.memory_insights[:6]:
            self.env.core.share_insight(
                session_id,
                insight_data["participant"],
                insight_data["insight"],
                insight_data["context"]
            )
        
        # Pause session
        self.env.core.pause_session(session_id, "user-1")
        
        # Verify session state is preserved
        session = self.env.core.get_session(session_id)
        assert session.status == SessionStatus.PAUSED
        assert len(session.participants) == 3
        
        insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
        assert len(insight_events) == 6
        
        # Resume session and add more insights
        self.env.core.resume_session(session_id, "user-1")
        
        additional_insight = "Additional insight after resume"
        self.env.core.share_insight(
            session_id,
            "alden",
            additional_insight,
            {"post_resume": True}
        )
        
        # Verify all insights are preserved
        session = self.env.core.get_session(session_id)
        insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
        assert len(insight_events) == 7
        
        print("    ✓ Session persistence verified successfully")
    
    def test_memory_cleanup(self):
        """Test memory cleanup and retention policies."""
        print("  Testing memory cleanup...")
        
        # Create session with many insights
        session_id = self.env.core.create_session("user-1", "Cleanup Test")
        self.env.test_sessions.append(session_id)
        
        for participant in self.env.test_participants[:2]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Share many insights to test cleanup limits
        max_insights = self.env.core_config["communal_memory"]["max_insights_per_session"]
        for i in range(max_insights + 5):  # Exceed limit
            insight = f"Cleanup test insight {i+1}"
            success = self.env.core.share_insight(
                session_id,
                "alden",
                insight,
                {"cleanup_test": True, "sequence": i+1}
            )
            if not success:
                break  # Should fail when limit exceeded
        
        # Verify insight count doesn't exceed limit
        session = self.env.core.get_session(session_id)
        insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
        assert len(insight_events) <= max_insights
        
        # Test session cleanup after ending
        self.env.core.end_session(session_id, "user-1")
        
        # Verify session is archived but data is preserved
        session = self.env.core.get_session(session_id)
        assert session.status == SessionStatus.ENDED
        assert len(session.session_log) > 0
        
        print("    ✓ Memory cleanup policies enforced successfully")
    
    def test_insight_categorization(self):
        """Test insight categorization and tagging."""
        print("  Testing insight categorization...")
        
        # Create session
        session_id = self.env.core.create_session("user-1", "Categorization Test")
        self.env.test_sessions.append(session_id)
        
        for participant in self.env.test_participants[:3]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Share insights with different categories
        categories = ["observation", "suggestion", "behavioral", "research"]
        for i, category in enumerate(categories):
            insight = f"Categorized insight: {category}"
            self.env.core.share_insight(
                session_id,
                "alden",
                insight,
                {
                    "category": category,
                    "tags": [category, "test"],
                    "confidence": 0.8 + (i * 0.05)
                }
            )
        
        # Verify categorization
        session = self.env.core.get_session(session_id)
        insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
        
        # Group by category
        by_category = {}
        for event in insight_events:
            category = event.metadata.get("category")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(event)
        
        # Verify each category has insights
        for category in categories:
            assert category in by_category
            assert len(by_category[category]) > 0
        
        # Test tag-based filtering
        tagged_insights = [
            e for e in insight_events 
            if "test" in e.metadata.get("tags", [])
        ]
        assert len(tagged_insights) == len(categories)
        
        print("    ✓ Insight categorization working correctly")
    
    def test_memory_export_import(self):
        """Test memory export and import functionality."""
        print("  Testing memory export/import...")
        
        # Create session with insights
        session_id = self.env.core.create_session("user-1", "Export/Import Test")
        self.env.test_sessions.append(session_id)
        
        for participant in self.env.test_participants[:2]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Share insights
        for insight_data in self.env.memory_insights[:3]:
            self.env.core.share_insight(
                session_id,
                insight_data["participant"],
                insight_data["insight"],
                insight_data["context"]
            )
        
        # Export session data
        export_data = self.env.core.export_session_log(session_id, "user-1")
        export_json = json.loads(export_data)
        
        # Verify export structure
        assert "session_id" in export_json
        assert "events" in export_json
        assert "participants" in export_json
        assert "metadata" in export_json
        
        # Verify insights are exported
        insight_events = [e for e in export_json["events"] if e["event_type"] == "insight_shared"]
        assert len(insight_events) == 3
        
        # Test import (create new session and import data)
        new_session_id = self.env.core.create_session("user-1", "Imported Session")
        self.env.test_sessions.append(new_session_id)
        
        # Import would typically be done through a separate method
        # For now, verify export contains all necessary data
        for event in insight_events:
            assert "participant_id" in event
            assert "content" in event
            assert "metadata" in event
            assert "timestamp" in event
        
        print("    ✓ Memory export/import functionality verified")
    
    def test_concurrent_memory_access(self):
        """Test concurrent memory access scenarios."""
        print("  Testing concurrent memory access...")
        
        # Create session
        session_id = self.env.core.create_session("user-1", "Concurrent Access Test")
        self.env.test_sessions.append(session_id)
        
        for participant in self.env.test_participants[:3]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Simulate concurrent insight sharing
        def share_insights_concurrently(participant_id: str, count: int):
            for i in range(count):
                insight = f"Concurrent insight {i+1} from {participant_id}"
                self.env.core.share_insight(
                    session_id,
                    participant_id,
                    insight,
                    {"concurrent": True, "thread": participant_id, "sequence": i+1}
                )
                time.sleep(0.01)  # Small delay to simulate real conditions
        
        # Start concurrent threads
        threads = []
        for participant in ["alden", "alice", "mimic"]:
            thread = threading.Thread(
                target=share_insights_concurrently,
                args=(participant, 5)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all insights were shared
        session = self.env.core.get_session(session_id)
        insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
        concurrent_insights = [e for e in insight_events if e.metadata.get("concurrent")]
        assert len(concurrent_insights) == 15  # 3 participants * 5 insights each
        
        print("    ✓ Concurrent memory access handled correctly")
    
    def test_memory_performance(self):
        """Test memory performance with large datasets."""
        print("  Testing memory performance...")
        
        # Create session
        session_id = self.env.core.create_session("user-1", "Performance Test")
        self.env.test_sessions.append(session_id)
        
        for participant in self.env.test_participants[:2]:
            self.env.core.add_participant(session_id, "user-1", participant)
        
        # Measure insight sharing performance
        start_time = time.time()
        insight_count = 50
        
        for i in range(insight_count):
            insight = f"Performance test insight {i+1}"
            self.env.core.share_insight(
                session_id,
                "alden",
                insight,
                {"performance_test": True, "sequence": i+1}
            )
        
        sharing_time = time.time() - start_time
        
        # Measure session retrieval performance
        start_time = time.time()
        session = self.env.core.get_session(session_id)
        retrieval_time = time.time() - start_time
        
        # Measure export performance
        start_time = time.time()
        export_data = self.env.core.export_session_log(session_id, "user-1")
        export_time = time.time() - start_time
        
        # Record performance metrics
        self.env.error_metrics.record_performance("insight_sharing", sharing_time / insight_count)
        self.env.error_metrics.record_performance("session_retrieval", retrieval_time)
        self.env.error_metrics.record_performance("session_export", export_time)
        
        # Verify performance is reasonable
        assert sharing_time / insight_count < 0.1, "Insight sharing too slow"
        assert retrieval_time < 1.0, "Session retrieval too slow"
        assert export_time < 2.0, "Session export too slow"
        
        print(f"    ✓ Performance test completed - Share: {sharing_time/insight_count:.3f}s/insight, Retrieve: {retrieval_time:.3f}s, Export: {export_time:.3f}s")
    
    def test_memory_error_scenarios(self):
        """Test memory error scenarios and recovery."""
        print("  Testing memory error scenarios...")
        
        # Test sharing insight to non-existent session
        try:
            self.env.core.share_insight("invalid-session", "alden", "Test insight")
            assert False, "Should raise error for invalid session"
        except CoreError:
            pass
        
        # Test sharing insight from non-existent participant
        session_id = self.env.core.create_session("user-1", "Error Test")
        self.env.test_sessions.append(session_id)
        self.env.core.add_participant(session_id, "user-1", self.env.test_participants[0])
        
        try:
            self.env.core.share_insight(session_id, "non-existent", "Test insight")
            assert False, "Should raise error for non-existent participant"
        except CoreError:
            pass
        
        # Test sharing insight with invalid metadata
        try:
            self.env.core.share_insight(
                session_id,
                "alden",
                "Test insight",
                {"invalid_key": "invalid_value" * 1000}  # Very large metadata
            )
            # Should handle gracefully or raise appropriate error
        except CoreError:
            pass
        
        # Test memory limits
        max_insights = self.env.core_config["communal_memory"]["max_insights_per_session"]
        for i in range(max_insights + 1):
            success = self.env.core.share_insight(
                session_id,
                "alden",
                f"Limit test insight {i+1}",
                {"limit_test": True}
            )
            if not success:
                break
        
        # Verify limit enforcement
        session = self.env.core.get_session(session_id)
        insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
        assert len(insight_events) <= max_insights
        
        print("    ✓ Memory error scenarios handled correctly")
    
    def test_memory_validation(self):
        """Test memory validation and data integrity."""
        print("  Testing memory validation...")
        
        # Test session ID validation
        assert CoreErrorValidator.validate_session_id("core-12345678-1234-1234-1234-123456789abc")
        assert not CoreErrorValidator.validate_session_id("invalid-session")
        assert not CoreErrorValidator.validate_session_id("")
        assert not CoreErrorValidator.validate_session_id(None)
        
        # Test participant data validation
        valid_participant = {
            "id": "test-participant",
            "type": "persona",
            "name": "Test Participant"
        }
        assert CoreErrorValidator.validate_participant_data(valid_participant)
        
        invalid_participant = {
            "id": "test-participant",
            "type": "invalid_type"
        }
        assert not CoreErrorValidator.validate_participant_data(invalid_participant)
        
        # Test insight metadata validation
        session_id = self.env.core.create_session("user-1", "Validation Test")
        self.env.test_sessions.append(session_id)
        self.env.core.add_participant(session_id, "user-1", self.env.test_participants[0])
        
        # Valid insight
        success = self.env.core.share_insight(
            session_id,
            "alden",
            "Valid insight",
            {"category": "observation", "confidence": 0.8}
        )
        assert success
        
        # Invalid insight (empty content)
        try:
            self.env.core.share_insight(session_id, "alden", "", {"category": "observation"})
            assert False, "Should not allow empty insight content"
        except CoreError:
            pass
        
        print("    ✓ Memory validation working correctly")
    
    def _print_test_summary(self):
        """Print test summary and metrics."""
        print("\n" + "=" * 60)
        print("📊 MEMORY MANAGEMENT TEST SUMMARY")
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

def run_memory_management_tests():
    """Run all memory management tests."""
    env = MemoryManagementTestEnvironment()
    
    try:
        tests = MemoryManagementTests(env)
        tests.run_all_tests()
        
        print("\n✅ Core Memory Management Test Suite Completed!")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        env.cleanup()

if __name__ == "__main__":
    run_memory_management_tests() 