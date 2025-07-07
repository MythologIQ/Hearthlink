#!/usr/bin/env python3
"""
Core Module Example - Demonstration of Core orchestration functionality.

This example shows how to use the Core module for:
- Session creation and management
- Participant management
- Turn-taking coordination
- Breakout room creation
- Communal memory sharing
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.core import Core, SessionStatus, ParticipantType
from vault.vault import Vault

def setup_test_environment():
    """Setup test environment with temporary files."""
    tmpdir = Path(tempfile.mkdtemp())
    
    # Core configuration
    core_config = {
        "session": {
            "max_participants": 10,
            "max_breakouts_per_session": 5,
            "session_timeout_minutes": 480,
            "auto_archive_after_days": 30
        },
        "turn_taking": {
            "turn_timeout_seconds": 300,
            "auto_advance": True,
            "allow_manual_turn_set": True,
            "max_turn_duration_minutes": 10
        },
        "communal_memory": {
            "auto_share_insights": False,
            "insight_approval_required": True,
            "max_insights_per_session": 100,
            "insight_retention_days": 90
        },
        "live_feed": {
            "default_verbosity": "default",
            "auto_include_external": True,
            "show_metadata": False,
            "max_events_in_feed": 1000
        },
        "audit": {
            "log_all_events": True,
            "retention_days": 365,
            "export_formats": ["json", "csv", "syslog"]
        },
        "agent_suggestions": {
            "enable_suggestions": True,
            "suggestion_threshold": 0.7,
            "max_suggestions_per_session": 5,
            "suggestion_cooldown_minutes": 15
        },
        "breakout_rooms": {
            "max_participants_per_breakout": 6,
            "auto_end_breakout_after_minutes": 60,
            "allow_cross_breakout_communication": False
        },
        "performance": {
            "cache_session_data": True,
            "cache_ttl_seconds": 300,
            "max_concurrent_sessions": 20,
            "session_cleanup_interval_minutes": 30
        }
    }
    
    # Vault configuration
    vault_config = {
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
    
    return tmpdir, core_config, vault_config

def demonstrate_session_creation(core, user_id):
    """Demonstrate session creation and basic management."""
    print("\n" + "="*60)
    print("SESSION CREATION & MANAGEMENT")
    print("="*60)
    
    # Create a new session
    topic = "AI Ethics Roundtable Discussion"
    print(f"Creating session: {topic}")
    
    session_id = core.create_session(user_id, topic)
    print(f"Session created with ID: {session_id}")
    
    # Get session summary
    summary = core.get_session_summary(session_id)
    print(f"Session summary: {json.dumps(summary, indent=2)}")
    
    return session_id

def demonstrate_participant_management(core, session_id, user_id):
    """Demonstrate adding and managing participants."""
    print("\n" + "="*60)
    print("PARTICIPANT MANAGEMENT")
    print("="*60)
    
    # Define participants
    participants = [
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
        }
    ]
    
    # Add participants
    for participant_data in participants:
        print(f"Adding participant: {participant_data['name']} ({participant_data['role']})")
        success = core.add_participant(session_id, user_id, participant_data)
        if success:
            print(f"  ✓ {participant_data['name']} added successfully")
        else:
            print(f"  ✗ Failed to add {participant_data['name']}")
    
    # Get updated session summary
    summary = core.get_session_summary(session_id)
    print(f"\nUpdated session summary:")
    print(f"  Participants: {summary['participant_count']}")
    print(f"  Status: {summary['status']}")

def demonstrate_turn_taking(core, session_id, user_id):
    """Demonstrate turn-taking functionality."""
    print("\n" + "="*60)
    print("TURN-TAKING COORDINATION")
    print("="*60)
    
    # Start turn-taking
    print("Starting turn-taking...")
    success = core.start_turn_taking(session_id, user_id)
    if success:
        print("✓ Turn-taking started")
    else:
        print("✗ Failed to start turn-taking")
        return
    
    # Get current turn
    session = core.get_session(session_id)
    print(f"Current turn: {session.current_turn}")
    print(f"Turn order: {session.turn_order}")
    
    # Simulate turn progression
    print("\nSimulating turn progression:")
    for i in range(len(session.turn_order)):
        current_participant = session.current_turn
        print(f"  Turn {i+1}: {current_participant}")
        
        # Share an insight during this turn
        insight = f"Insight from {current_participant} during turn {i+1}"
        core.share_insight(session_id, current_participant, insight, {"turn": i+1})
        print(f"    Shared insight: {insight}")
        
        # Advance to next turn
        next_turn = core.advance_turn(session_id, user_id)
        if next_turn:
            print(f"    → Next turn: {next_turn}")
        else:
            print(f"    → Turn-taking complete")
            break
    
    print("\n✓ Turn-taking demonstration complete")

def demonstrate_breakout_rooms(core, session_id, user_id):
    """Demonstrate breakout room functionality."""
    print("\n" + "="*60)
    print("BREAKOUT ROOM MANAGEMENT")
    print("="*60)
    
    # Create breakout room for AI ethics discussion
    breakout_topic = "AI Ethics Deep Dive"
    breakout_participants = ["alice", "research-bot"]
    
    print(f"Creating breakout room: {breakout_topic}")
    print(f"Participants: {', '.join(breakout_participants)}")
    
    breakout_id = core.create_breakout(session_id, user_id, breakout_topic, breakout_participants)
    print(f"Breakout room created with ID: {breakout_id}")
    
    # Simulate activity in breakout room
    print("\nSimulating breakout room activity:")
    for participant in breakout_participants:
        insight = f"Breakout insight from {participant} on {breakout_topic}"
        core.share_insight(session_id, participant, insight, {"breakout_id": breakout_id})
        print(f"  {participant}: {insight}")
    
    # End breakout room
    print(f"\nEnding breakout room: {breakout_id}")
    success = core.end_breakout(session_id, user_id, breakout_id)
    if success:
        print("✓ Breakout room ended successfully")
    else:
        print("✗ Failed to end breakout room")
    
    # Get session summary to see breakout count
    summary = core.get_session_summary(session_id)
    print(f"Active breakouts: {summary['breakout_count']}")

def demonstrate_communal_memory(core, session_id, user_id):
    """Demonstrate communal memory sharing."""
    print("\n" + "="*60)
    print("COMMUNAL MEMORY SHARING")
    print("="*60)
    
    # Share insights from different participants
    insights = [
        {
            "participant": "alden",
            "insight": "The user demonstrates strong analytical thinking patterns",
            "context": {"type": "observation", "confidence": 0.85}
        },
        {
            "participant": "alice",
            "insight": "Consider implementing structured feedback loops for better engagement",
            "context": {"type": "suggestion", "priority": "medium"}
        },
        {
            "participant": "mimic",
            "insight": "User responds well to collaborative problem-solving approaches",
            "context": {"type": "behavioral_insight", "category": "interaction_style"}
        },
        {
            "participant": "research-bot",
            "insight": "Current AI ethics frameworks align with user's expressed values",
            "context": {"type": "research_finding", "source": "external_analysis"}
        }
    ]
    
    print("Sharing insights to communal memory:")
    for insight_data in insights:
        participant = insight_data["participant"]
        insight = insight_data["insight"]
        context = insight_data["context"]
        
        print(f"\n{participant}:")
        print(f"  Insight: {insight}")
        print(f"  Context: {context}")
        
        success = core.share_insight(session_id, participant, insight, context)
        if success:
            print(f"  ✓ Insight shared successfully")
        else:
            print(f"  ✗ Failed to share insight")

def demonstrate_session_export(core, session_id, user_id):
    """Demonstrate session export functionality."""
    print("\n" + "="*60)
    print("SESSION EXPORT")
    print("="*60)
    
    # Export session log
    print("Exporting session log...")
    export_data = core.export_session_log(session_id, user_id, include_hidden=False)
    
    if export_data:
        export_json = json.loads(export_data)
        
        print(f"Session export summary:")
        print(f"  Session ID: {export_json['session_id']}")
        print(f"  Topic: {export_json['topic']}")
        print(f"  Events: {len(export_json['events'])}")
        print(f"  Participants: {len(export_json['participants'])}")
        print(f"  Breakouts: {len(export_json['breakouts'])}")
        print(f"  Audit entries: {len(export_json['audit_log'])}")
        
        # Show some event types
        event_types = {}
        for event in export_json['events']:
            event_type = event['event_type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print(f"\nEvent breakdown:")
        for event_type, count in event_types.items():
            print(f"  {event_type}: {count}")
        
        print("\n✓ Session export completed")
    else:
        print("✗ Failed to export session")

def demonstrate_session_lifecycle(core, session_id, user_id):
    """Demonstrate complete session lifecycle."""
    print("\n" + "="*60)
    print("SESSION LIFECYCLE")
    print("="*60)
    
    # Pause session
    print("Pausing session...")
    success = core.pause_session(session_id, user_id)
    if success:
        print("✓ Session paused")
    else:
        print("✗ Failed to pause session")
    
    # Resume session
    print("Resuming session...")
    success = core.resume_session(session_id, user_id)
    if success:
        print("✓ Session resumed")
    else:
        print("✗ Failed to resume session")
    
    # End session
    print("Ending session...")
    success = core.end_session(session_id, user_id)
    if success:
        print("✓ Session ended")
    else:
        print("✗ Failed to end session")
    
    # Verify session status
    session = core.get_session(session_id)
    print(f"Final session status: {session.status.value}")

def main():
    """Main demonstration function."""
    print("🚀 Hearthlink Core Module Demonstration")
    print("="*60)
    
    # Setup environment
    tmpdir, core_config, vault_config = setup_test_environment()
    
    try:
        # Initialize modules
        print("Initializing Core and Vault modules...")
        vault = Vault(vault_config)
        core = Core(core_config, vault)
        
        user_id = "demo-user"
        
        # Run demonstrations
        session_id = demonstrate_session_creation(core, user_id)
        demonstrate_participant_management(core, session_id, user_id)
        demonstrate_turn_taking(core, session_id, user_id)
        demonstrate_breakout_rooms(core, session_id, user_id)
        demonstrate_communal_memory(core, session_id, user_id)
        demonstrate_session_export(core, session_id, user_id)
        demonstrate_session_lifecycle(core, session_id, user_id)
        
        print("\n" + "="*60)
        print("✅ Core Module Demonstration Complete!")
        print("="*60)
        
        print("\nKey Features Demonstrated:")
        print("  • Session creation and management")
        print("  • Participant addition and removal")
        print("  • Turn-taking coordination")
        print("  • Breakout room creation and management")
        print("  • Communal memory sharing")
        print("  • Session export and logging")
        print("  • Session lifecycle management")
        
        print("\nThe Core module successfully orchestrates multi-agent")
        print("conversations with proper state management, turn-taking,")
        print("and communal memory mediation.")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print(f"\nCleaning up temporary files...")
        import shutil
        shutil.rmtree(tmpdir)

if __name__ == "__main__":
    main() 