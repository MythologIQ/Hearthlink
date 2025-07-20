#!/usr/bin/env python3
"""
Simple test script to verify Vault memory storage works
Tests basic Vault operations independently
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_vault_operations():
    """Test basic Vault storage operations"""
    print("🧪 Testing Vault Memory Storage")
    print("=" * 40)
    
    try:
        # Import Vault modules
        from vault.vault import Vault
        from vault.schema import PersonaMemory
        from main import HearthlinkLogger
        
        # Create logger
        logger = HearthlinkLogger()
        
        # Vault configuration
        vault_config = {
            "encryption": {
                "key_env_var": "HEARTHLINK_VAULT_KEY",
                "key_file": "config/vault_key.bin"
            },
            "storage": {
                "file_path": "hearthlink_data/vault_storage"
            },
            "schema_version": "1.0.0"
        }
        
        print("✅ Creating Vault instance...")
        vault = Vault(vault_config, logger)
        
        # Test data
        test_user_id = "test-user-001"
        test_memory_data = {
            "persona_id": "alden",
            "user_id": test_user_id,
            "schema_version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "traits": {
                "openness": 75,
                "conscientiousness": 85,
                "extraversion": 45,
                "agreeableness": 90,
                "emotional_stability": 80
            },
            "motivation_style": "supportive",
            "trust_level": 0.82,
            "learning_agility": 6.2,
            "reflective_capacity": 12,
            "engagement": 16,
            "correction_events": [
                {
                    "type": "positive",
                    "timestamp": datetime.now().isoformat(),
                    "description": "Test positive feedback",
                    "impact_score": 0.5,
                    "context": {"test": "integration"}
                }
            ],
            "session_mood": [
                {
                    "session_id": "test_session_001",
                    "mood": "positive",
                    "score": 85,
                    "timestamp": datetime.now().isoformat(),
                    "context": {"test": "integration"}
                }
            ],
            "relationship_log": [],
            "user_tags": ["test", "integration"],
            "audit_log": [
                {
                    "action": "test_create",
                    "by": "test",
                    "timestamp": datetime.now().isoformat(),
                    "field": "traits",
                    "old_value": None,
                    "new_value": "test_data",
                    "reason": "integration_test"
                }
            ]
        }
        
        print("✅ Test data prepared")
        
        # Test 1: Create/update persona memory
        print("\n📊 Test 1: Create Persona Memory")
        vault.create_or_update_persona("alden", test_user_id, test_memory_data)
        print("✅ Persona memory created")
        
        # Test 2: Retrieve persona memory
        print("\n📊 Test 2: Retrieve Persona Memory")
        retrieved_memory = vault.get_persona("alden", test_user_id)
        
        if retrieved_memory:
            print("✅ Memory retrieved successfully")
            print(f"✅ Schema version: {retrieved_memory.get('schema_version')}")
            print(f"✅ Traits count: {len(retrieved_memory['data']['traits'])}")
            print(f"✅ Correction events: {len(retrieved_memory['data']['correction_events'])}")
            print(f"✅ Session moods: {len(retrieved_memory['data']['session_mood'])}")
            print(f"✅ Audit log: {len(retrieved_memory['data']['audit_log'])}")
        else:
            print("❌ Failed to retrieve memory")
            return False
        
        # Test 3: Update existing memory
        print("\n📊 Test 3: Update Existing Memory")
        updated_data = test_memory_data.copy()
        updated_data["traits"]["openness"] = 88  # Change openness
        updated_data["trust_level"] = 0.85  # Increase trust
        
        vault.create_or_update_persona("alden", test_user_id, updated_data)
        
        # Retrieve updated memory
        updated_memory = vault.get_persona("alden", test_user_id)
        
        if updated_memory:
            openness = updated_memory['data']['traits']['openness']
            trust = updated_memory['data']['trust_level']
            print(f"✅ Updated openness: {openness}")
            print(f"✅ Updated trust: {trust}")
            
            if openness == 88 and trust == 0.85:
                print("✅ Memory update successful")
            else:
                print("❌ Memory update failed")
                return False
        else:
            print("❌ Failed to retrieve updated memory")
            return False
        
        # Test 4: Export memory
        print("\n📊 Test 4: Export Memory")
        exported = vault.export_persona("alden", test_user_id)
        
        if exported:
            export_data = json.loads(exported)
            print(f"✅ Export successful, size: {len(exported)} characters")
            print(f"✅ Export contains traits: {'traits' in export_data.get('data', {})}")
        else:
            print("❌ Export failed")
            return False
        
        # Test 5: Check storage file
        print("\n📊 Test 5: Storage File Verification")
        storage_path = Path(vault_config["storage"]["file_path"])
        
        if storage_path.exists():
            file_size = storage_path.stat().st_size
            print(f"✅ Storage file exists: {storage_path}")
            print(f"✅ File size: {file_size} bytes")
            
            if file_size > 0:
                print("✅ Storage file contains data")
            else:
                print("❌ Storage file is empty")
                return False
        else:
            print("❌ Storage file does not exist")
            return False
        
        print("\n🎉 All Vault tests passed!")
        print("=" * 40)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Vault test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vault_operations()
    sys.exit(0 if success else 1)