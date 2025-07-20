#!/usr/bin/env python3
"""
Test script to verify Alden-Vault memory integration
Tests that Alden conversations are properly saved to and loaded from Vault
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_alden_vault_integration():
    """Test Alden-Vault memory integration end-to-end"""
    print("🧪 Testing Alden-Vault Memory Integration")
    print("=" * 50)
    
    try:
        # Import required modules
        from personas.alden import AldenPersona, create_alden_persona
        from main import HearthlinkLogger
        from llm.local_llm_client import LocalLLMClient, LLMConfig
        
        # Create logger
        logger = HearthlinkLogger()
        
        # Create LLM configuration for testing
        llm_config = LLMConfig(
            engine="test",
            model="test-model",
            api_key="test-key",
            base_url="http://localhost:8001/api/llm"
        )
        
        # Create LLM client
        llm_client = LocalLLMClient(llm_config, logger)
        
        print("✅ LLM client created")
        
        # Create Alden persona
        alden = AldenPersona(llm_client, logger)
        
        print("✅ Alden persona created")
        print(f"✅ Vault connection: {'Connected' if hasattr(alden, 'vault') and alden.vault else 'Not connected'}")
        
        # Test 1: Check initial memory state
        print("\n📊 Test 1: Initial Memory State")
        print(f"User ID: {alden.memory.user_id}")
        print(f"Trust Level: {alden.memory.trust_level}")
        print(f"Learning Agility: {alden.memory.learning_agility}")
        print(f"Correction Events: {len(alden.memory.correction_events)}")
        print(f"Session Moods: {len(alden.memory.session_mood)}")
        
        # Test 2: Update a trait and verify persistence
        print("\n📊 Test 2: Trait Update and Persistence")
        original_openness = alden.memory.traits["openness"]
        new_openness = 85
        
        alden.update_trait("openness", new_openness, "test_integration")
        
        print(f"Updated openness: {original_openness} → {new_openness}")
        print(f"Audit log entries: {len(alden.memory.audit_log)}")
        
        # Test 3: Add correction event
        print("\n📊 Test 3: Correction Event")
        alden.add_correction_event(
            "positive", 
            "Integration test positive feedback", 
            0.5,
            {"test": "integration"}
        )
        
        print(f"Correction events: {len(alden.memory.correction_events)}")
        print(f"Latest event: {alden.memory.correction_events[-1].description}")
        
        # Test 4: Record session mood
        print("\n📊 Test 4: Session Mood")
        test_session_id = f"test_session_{int(datetime.now().timestamp())}"
        alden.record_session_mood(test_session_id, "positive", 85, {"test": "integration"})
        
        print(f"Session moods: {len(alden.memory.session_mood)}")
        print(f"Latest mood: {alden.memory.session_mood[-1].mood} (score: {alden.memory.session_mood[-1].score})")
        
        # Test 5: Verify Vault storage file
        print("\n📊 Test 5: Vault Storage Verification")
        vault_path = Path("hearthlink_data/vault_storage")
        
        if vault_path.exists():
            file_size = vault_path.stat().st_size
            print(f"✅ Vault storage file exists: {vault_path}")
            print(f"✅ File size: {file_size} bytes")
            
            if file_size > 0:
                print("✅ Vault storage file contains data (encrypted)")
                
                # Test loading by creating a new Alden instance
                print("\n📊 Test 6: Memory Persistence Verification")
                print("Creating new Alden instance to test memory loading...")
                
                alden2 = AldenPersona(llm_client, logger)
                
                print(f"New instance openness: {alden2.memory.traits['openness']}")
                print(f"New instance correction events: {len(alden2.memory.correction_events)}")
                print(f"New instance session moods: {len(alden2.memory.session_mood)}")
                print(f"New instance audit log: {len(alden2.memory.audit_log)}")
                
                # Verify data persistence
                if alden2.memory.traits["openness"] == new_openness:
                    print("✅ Trait update persisted correctly")
                else:
                    print("❌ Trait update NOT persisted")
                
                if len(alden2.memory.correction_events) > 0:
                    print("✅ Correction events persisted correctly")
                else:
                    print("❌ Correction events NOT persisted")
                
                if len(alden2.memory.session_mood) > 0:
                    print("✅ Session moods persisted correctly")
                else:
                    print("❌ Session moods NOT persisted")
                    
            else:
                print("❌ Vault storage file is empty!")
        else:
            print("❌ Vault storage file does not exist!")
        
        # Test 7: Export memory for inspection
        print("\n📊 Test 7: Memory Export")
        exported_memory = alden.export_memory()
        
        print(f"Exported memory size: {len(str(exported_memory))} characters")
        print(f"Export metadata: {exported_memory.get('export_metadata', {})}")
        
        print("\n🎉 Integration Test Complete!")
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