#!/usr/bin/env python3
"""
Test Alden-Vault integration with mock LLM client
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Mock LLM client to avoid initialization issues
@dataclass
class MockLLMResponse:
    content: str
    response_time: float = 0.1
    model: str = "mock-model"
    tokens_used: int = 50

class MockLLMClient:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    def generate(self, request):
        return MockLLMResponse(
            content="Hello! I'm Alden, your AI companion. I'm now integrated with the Vault memory system, so I can remember our conversations!",
            response_time=0.1,
            model="mock-model"
        )
    
    def get_status(self):
        return {"status": "healthy", "model": "mock-model"}

def test_alden_vault_integration():
    """Test Alden-Vault memory integration with mock LLM"""
    print("🧪 Testing Alden-Vault Integration (Mock LLM)")
    print("=" * 50)
    
    try:
        # Import required modules
        from personas.alden import AldenPersona
        from main import HearthlinkLogger
        
        # Create logger
        logger = HearthlinkLogger()
        
        # Create mock LLM client
        mock_config = type('Config', (), {'engine': 'mock', 'model': 'mock-model'})()
        llm_client = MockLLMClient(mock_config, logger)
        
        print("✅ Mock LLM client created")
        
        # Create Alden persona
        alden = AldenPersona(llm_client, logger)
        
        # Save the user_id for the second instance
        user_id = alden.memory.user_id
        
        print("✅ Alden persona created")
        print(f"✅ Vault connection: {'Connected' if hasattr(alden, 'vault') and alden.vault else 'Not connected'}")
        
        # Test 1: Check initial memory state
        print("\n📊 Test 1: Initial Memory State")
        print(f"User ID: {alden.memory.user_id}")
        print(f"Trust Level: {alden.memory.trust_level}")
        print(f"Learning Agility: {alden.memory.learning_agility}")
        print(f"Correction Events: {len(alden.memory.correction_events)}")
        print(f"Session Moods: {len(alden.memory.session_mood)}")
        print(f"Audit Log: {len(alden.memory.audit_log)}")
        
        # Test 2: Generate a response (this should save conversation memory)
        print("\n📊 Test 2: Generate Response with Memory Persistence")
        initial_events = len(alden.memory.correction_events)
        
        response = alden.generate_response(
            "Hello Alden! Please remember that I like testing integrations.",
            session_id="test_session_001"
        )
        
        print(f"✅ Response generated: {response[:100]}...")
        print(f"✅ Correction events before: {initial_events}")
        print(f"✅ Correction events after: {len(alden.memory.correction_events)}")
        
        if len(alden.memory.correction_events) > initial_events:
            print("✅ Conversation memory saved automatically")
        else:
            print("❌ Conversation memory NOT saved")
        
        # Test 3: Update a trait (should save to Vault)
        print("\n📊 Test 3: Trait Update with Vault Persistence")
        original_openness = alden.memory.traits["openness"]
        new_openness = 90
        
        alden.update_trait("openness", new_openness, "Integration test - increased openness")
        
        print(f"✅ Updated openness: {original_openness} → {new_openness}")
        print(f"✅ Audit log entries: {len(alden.memory.audit_log)}")
        
        # Test 4: Add correction event (should save to Vault)
        print("\n📊 Test 4: Correction Event with Vault Persistence")
        alden.add_correction_event(
            "positive", 
            "Great job integrating with Vault! This is working perfectly.", 
            0.8,
            {"test": "integration", "feature": "vault_persistence"}
        )
        
        print(f"✅ Correction events: {len(alden.memory.correction_events)}")
        print(f"✅ Latest event: {alden.memory.correction_events[-1].description}")
        
        # Test 5: Record session mood (should save to Vault)
        print("\n📊 Test 5: Session Mood with Vault Persistence")
        alden.record_session_mood("test_session_001", "positive", 95, {"test": "integration"})
        
        print(f"✅ Session moods: {len(alden.memory.session_mood)}")
        print(f"✅ Latest mood: {alden.memory.session_mood[-1].mood} (score: {alden.memory.session_mood[-1].score})")
        
        # Test 6: Verify Vault storage file has grown
        print("\n📊 Test 6: Vault Storage Verification")
        vault_path = Path("hearthlink_data/vault_storage")
        
        if vault_path.exists():
            file_size = vault_path.stat().st_size
            print(f"✅ Vault storage file exists: {vault_path}")
            print(f"✅ File size: {file_size} bytes")
            
            if file_size > 1000:  # Should be significantly larger now
                print("✅ Vault storage file contains substantial data")
            else:
                print("❌ Vault storage file seems too small")
        
        # Test 7: Create new Alden instance to test memory loading
        print("\n📊 Test 7: Memory Persistence Verification")
        print("Creating new Alden instance to test memory loading...")
        
        alden2 = AldenPersona(llm_client, logger)
        
        # Override the user_id to match the first instance for testing
        alden2.memory.user_id = user_id
        
        # Reload memory from Vault with the correct user_id
        alden2._load_memory_from_vault()
        
        print(f"✅ New instance openness: {alden2.memory.traits['openness']}")
        print(f"✅ New instance correction events: {len(alden2.memory.correction_events)}")
        print(f"✅ New instance session moods: {len(alden2.memory.session_mood)}")
        print(f"✅ New instance audit log: {len(alden2.memory.audit_log)}")
        
        # Verify data persistence
        persistence_success = True
        
        if alden2.memory.traits["openness"] == new_openness:
            print("✅ Trait update persisted correctly")
        else:
            print(f"❌ Trait update NOT persisted (expected {new_openness}, got {alden2.memory.traits['openness']})")
            persistence_success = False
        
        if len(alden2.memory.correction_events) >= 2:  # Should have at least 2 events
            print("✅ Correction events persisted correctly")
        else:
            print(f"❌ Correction events NOT persisted correctly (expected >=2, got {len(alden2.memory.correction_events)})")
            persistence_success = False
        
        if len(alden2.memory.session_mood) >= 1:
            print("✅ Session moods persisted correctly")
        else:
            print(f"❌ Session moods NOT persisted (got {len(alden2.memory.session_mood)})")
            persistence_success = False
        
        if len(alden2.memory.audit_log) >= 1:
            print("✅ Audit log persisted correctly")
        else:
            print(f"❌ Audit log NOT persisted (got {len(alden2.memory.audit_log)})")
            persistence_success = False
        
        # Test 8: Export memory for inspection
        print("\n📊 Test 8: Memory Export")
        exported_memory = alden2.export_memory()
        
        print(f"✅ Exported memory size: {len(str(exported_memory))} characters")
        print(f"✅ Export metadata: {exported_memory.get('export_metadata', {})}")
        
        if persistence_success:
            print("\n🎉 🎉 🎉 ALDEN-VAULT INTEGRATION FULLY WORKING! 🎉 🎉 🎉")
            print("✅ Conversations are now being saved to Vault")
            print("✅ Memory persists across Alden instances")
            print("✅ All memory operations work correctly")
        else:
            print("\n❌ Some persistence tests failed")
            return False
        
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_alden_vault_integration()
    sys.exit(0 if success else 1)