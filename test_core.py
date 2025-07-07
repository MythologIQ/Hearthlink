import os
import json
import tempfile
import shutil
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from src.core.core import Core, Session, Participant, ParticipantType, SessionStatus, CoreError
from src.vault.vault import Vault

class DummyLogger:
    def info(self, msg, extra=None):
        print(f"[INFO] {msg} {extra if extra else ''}")
    def error(self, msg, extra=None):
        print(f"[ERROR] {msg} {extra if extra else ''}")

def get_test_config():
    return {
        "session": {
            "max_participants": 5,
            "max_breakouts_per_session": 3,
            "session_timeout_minutes": 60,
            "auto_archive_after_days": 7
        },
        "turn_taking": {
            "turn_timeout_seconds": 60,
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
            "max_participants_per_breakout": 4,
            "auto_end_breakout_after_minutes": 30,
            "allow_cross_breakout_communication": False
        },
        "performance": {
            "cache_session_data": True,
            "cache_ttl_seconds": 60,
            "max_concurrent_sessions": 5,
            "session_cleanup_interval_minutes": 10
        }
    }

def get_vault_config(tmpdir):
    return {
        "encryption": {
            "algorithm": "AES-256",
            "key_file": str(tmpdir / "vault.key"),
            "key_env_var": None
        },
        "storage": {
            "type": "file",
            "file_path": str(tmpdir / "vault.db")
        },
        "audit": {
            "log_file": str(tmpdir / "audit.log")
        },
        "schema_version": "1.0.0"
    }

def test_session_creation(core, user_id):
    """Test basic session creation."""
    print("Testing session creation...")
    
    # Create session
    topic = "Test Session"
    session_id = core.create_session(user_id, topic)
    assert session_id is not None
    assert session_id.startswith("core-")
    
    # Verify session exists
    session = core.get_session(session_id)
    assert session is not None
    assert session.topic == topic
    assert session.created_by == user_id
    assert session.status == SessionStatus.ACTIVE
    assert len(session.participants) == 0
    
    return session_id

def test_participant_management(core, session_id, user_id):
    """Test adding and removing participants."""
    print("Testing participant management...")
    
    # Add persona participants
    alden_data = {
        "id": "alden",
        "type": "persona",
        "name": "Alden",
        "role": "evolutionary_companion"
    }
    alice_data = {
        "id": "alice",
        "type": "persona",
        "name": "Alice",
        "role": "cognitive_behavioral"
    }
    
    success = core.add_participant(session_id, user_id, alden_data)
    assert success
    
    success = core.add_participant(session_id, user_id, alice_data)
    assert success
    
    # Verify participants added
    session = core.get_session(session_id)
    assert len(session.participants) == 2
    assert any(p.id == "alden" for p in session.participants)
    assert any(p.id == "alice" for p in session.participants)
    
    # Remove participant
    success = core.remove_participant(session_id, user_id, "alice")
    assert success
    
    # Verify participant removed
    session = core.get_session(session_id)
    assert len(session.participants) == 2  # Still 2, but alice is inactive
    alice = next(p for p in session.participants if p.id == "alice")
    assert not alice.is_active
    assert alice.left_at is not None

def test_turn_taking(core, session_id, user_id):
    """Test turn-taking functionality."""
    print("Testing turn-taking...")
    
    # Add participants for turn-taking
    participants = [
        {"id": "alden", "type": "persona", "name": "Alden"},
        {"id": "alice", "type": "persona", "name": "Alice"},
        {"id": "mimic", "type": "persona", "name": "Mimic"}
    ]
    
    for participant_data in participants:
        core.add_participant(session_id, user_id, participant_data)
    
    # Start turn-taking
    success = core.start_turn_taking(session_id, user_id)
    assert success
    
    session = core.get_session(session_id)
    assert session.current_turn is not None
    assert len(session.turn_order) == 3
    
    # Advance turns
    first_turn = session.current_turn
    second_turn = core.advance_turn(session_id, user_id)
    assert second_turn is not None
    assert second_turn != first_turn
    
    third_turn = core.advance_turn(session_id, user_id)
    assert third_turn is not None
    assert third_turn != first_turn
    assert third_turn != second_turn
    
    # Complete turn-taking
    final_turn = core.advance_turn(session_id, user_id)
    assert final_turn is None  # Turn-taking complete
    
    # Test manual turn setting
    success = core.set_current_turn(session_id, user_id, "alice")
    assert success
    
    session = core.get_session(session_id)
    assert session.current_turn == "alice"

def test_breakout_rooms(core, session_id, user_id):
    """Test breakout room functionality."""
    print("Testing breakout rooms...")
    
    # Add participants
    participants = [
        {"id": "alden", "type": "persona", "name": "Alden"},
        {"id": "alice", "type": "persona", "name": "Alice"},
        {"id": "mimic", "type": "persona", "name": "Mimic"}
    ]
    
    for participant_data in participants:
        core.add_participant(session_id, user_id, participant_data)
    
    # Create breakout room
    breakout_topic = "AI Ethics Discussion"
    breakout_participants = ["alice", "mimic"]
    breakout_id = core.create_breakout(session_id, user_id, breakout_topic, breakout_participants)
    assert breakout_id is not None
    assert breakout_id.startswith(session_id)
    
    # Verify breakout created
    session = core.get_session(session_id)
    assert len(session.breakouts) == 1
    breakout = session.breakouts[0]
    assert breakout.topic == breakout_topic
    assert breakout.participants == breakout_participants
    assert breakout.ended_at is None
    
    # End breakout
    success = core.end_breakout(session_id, user_id, breakout_id)
    assert success
    
    # Verify breakout ended
    session = core.get_session(session_id)
    breakout = next(b for b in session.breakouts if b.breakout_id == breakout_id)
    assert breakout.ended_at is not None

def test_communal_memory(core, session_id, user_id):
    """Test communal memory functionality."""
    print("Testing communal memory...")
    
    # Add participant
    alden_data = {"id": "alden", "type": "persona", "name": "Alden"}
    core.add_participant(session_id, user_id, alden_data)
    
    # Share insights
    insight1 = "The user shows strong analytical thinking patterns"
    success = core.share_insight(session_id, "alden", insight1, {"context": "analysis"})
    assert success
    
    insight2 = "Consider implementing more structured feedback loops"
    success = core.share_insight(session_id, "alden", insight2, {"context": "suggestion"})
    assert success
    
    # Verify insights in session log
    session = core.get_session(session_id)
    insight_events = [e for e in session.session_log if e.event_type == "insight_shared"]
    assert len(insight_events) == 2
    assert insight_events[0].content == insight1
    assert insight_events[1].content == insight2

def test_session_state_management(core, session_id, user_id):
    """Test session state transitions."""
    print("Testing session state management...")
    
    # Pause session
    success = core.pause_session(session_id, user_id)
    assert success
    
    session = core.get_session(session_id)
    assert session.status == SessionStatus.PAUSED
    
    # Resume session
    success = core.resume_session(session_id, user_id)
    assert success
    
    session = core.get_session(session_id)
    assert session.status == SessionStatus.ACTIVE
    
    # End session
    success = core.end_session(session_id, user_id)
    assert success
    
    session = core.get_session(session_id)
    assert session.status == SessionStatus.ENDED

def test_export_functionality(core, session_id, user_id):
    """Test session export functionality."""
    print("Testing export functionality...")
    
    # Add some activity to session
    alden_data = {"id": "alden", "type": "persona", "name": "Alden"}
    core.add_participant(session_id, user_id, alden_data)
    core.share_insight(session_id, "alden", "Test insight")
    
    # Export session log
    export_data = core.export_session_log(session_id, user_id)
    assert export_data is not None
    
    # Parse export
    export_json = json.loads(export_data)
    assert export_json["session_id"] == session_id
    assert "events" in export_json
    assert "participants" in export_json
    assert "audit_log" in export_json
    
    # Verify events included
    events = export_json["events"]
    assert len(events) > 0
    assert any(e["event_type"] == "join" for e in events)
    assert any(e["event_type"] == "insight_shared" for e in events)

def test_session_summary(core, session_id, user_id):
    """Test session summary functionality."""
    print("Testing session summary...")
    
    # Add participants
    participants = [
        {"id": "alden", "type": "persona", "name": "Alden"},
        {"id": "alice", "type": "persona", "name": "Alice"}
    ]
    
    for participant_data in participants:
        core.add_participant(session_id, user_id, participant_data)
    
    # Get summary
    summary = core.get_session_summary(session_id)
    assert summary is not None
    assert summary["session_id"] == session_id
    assert summary["participant_count"] == 2
    assert summary["status"] == SessionStatus.ACTIVE.value
    assert "created_at" in summary

def test_error_handling(core, user_id):
    """Test error handling scenarios."""
    print("Testing error handling...")
    
    # Test invalid session ID
    try:
        core.get_session("invalid-session")
        assert False, "Should raise error for invalid session"
    except CoreError:
        pass
    
    # Test adding participant to non-existent session
    try:
        core.add_participant("invalid-session", user_id, {"id": "test", "type": "persona", "name": "Test"})
        assert False, "Should raise error for invalid session"
    except CoreError:
        pass
    
    # Test removing non-existent participant
    session_id = core.create_session(user_id, "Error Test")
    try:
        core.remove_participant(session_id, user_id, "non-existent")
        assert False, "Should raise error for non-existent participant"
    except CoreError:
        pass

def test_event_callbacks(core, session_id, user_id):
    """Test event callback functionality."""
    print("Testing event callbacks...")
    
    events_received = []
    
    def event_callback(event):
        events_received.append(event)
    
    # Register callback
    core.register_event_callback(event_callback)
    
    # Perform actions that should trigger events
    alden_data = {"id": "alden", "type": "persona", "name": "Alden"}
    core.add_participant(session_id, user_id, alden_data)
    core.share_insight(session_id, "alden", "Test insight")
    
    # Verify events were received
    assert len(events_received) >= 2
    assert any(e["action"] == "add_participant" for e in events_received)
    assert any(e["action"] == "share_insight" for e in events_received)

def test_concurrent_sessions(core, user_id):
    """Test multiple concurrent sessions."""
    print("Testing concurrent sessions...")
    
    # Create multiple sessions
    session_ids = []
    for i in range(3):
        topic = f"Concurrent Session {i+1}"
        session_id = core.create_session(user_id, topic)
        session_ids.append(session_id)
    
    # Verify all sessions exist
    for session_id in session_ids:
        session = core.get_session(session_id)
        assert session is not None
        assert session.status == SessionStatus.ACTIVE
    
    # Get active sessions
    active_sessions = core.get_active_sessions()
    assert len(active_sessions) >= 3
    
    # Verify all created sessions are in active list
    active_session_ids = [s.session_id for s in active_sessions]
    for session_id in session_ids:
        assert session_id in active_session_ids

def run_all_core_tests():
    """Run all Core module tests."""
    tmpdir = Path(tempfile.mkdtemp())
    try:
        config = get_test_config()
        vault_config = get_vault_config(tmpdir)
        logger = DummyLogger()
        
        # Initialize Vault and Core
        vault = Vault(vault_config, logger)
        core = Core(config, vault, logger)
        
        user_id = "test-user"
        
        print("🚀 Starting Core Module Test Suite")
        print("=" * 50)
        
        # Run tests
        session_id = test_session_creation(core, user_id)
        test_participant_management(core, session_id, user_id)
        test_turn_taking(core, session_id, user_id)
        test_breakout_rooms(core, session_id, user_id)
        test_communal_memory(core, session_id, user_id)
        test_session_state_management(core, session_id, user_id)
        test_export_functionality(core, session_id, user_id)
        test_session_summary(core, session_id, user_id)
        test_error_handling(core, user_id)
        test_event_callbacks(core, session_id, user_id)
        test_concurrent_sessions(core, user_id)
        
        print("✅ All Core module tests passed!")
        
    finally:
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    run_all_core_tests() 