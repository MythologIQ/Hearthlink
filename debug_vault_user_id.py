#!/usr/bin/env python3
"""
Debug script to understand the Vault user_id issue
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def debug_vault_user_id():
    """Debug Vault user_id handling"""
    print("🔍 Debugging Vault User ID Handling")
    print("=" * 40)
    
    try:
        from vault.vault import Vault
        from main import HearthlinkLogger
        
        # Test configuration
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
        
        logger = HearthlinkLogger()
        vault = Vault(vault_config, logger)
        
        # Test data
        test_user_id = "debug-user-001"
        test_memory_data = {
            "persona_id": "alden",
            "user_id": test_user_id,  # This should match the requesting user_id
            "traits": {"openness": 75},
            "correction_events": [],
            "session_mood": [],
            "audit_log": []
        }
        
        print(f"📊 Testing with user_id: {test_user_id}")
        print(f"📊 Memory data user_id: {test_memory_data['user_id']}")
        
        # Store memory
        print("\n1. Storing memory...")
        vault.create_or_update_persona("alden", test_user_id, test_memory_data)
        print("✅ Memory stored successfully")
        
        # Try to retrieve memory
        print("\n2. Retrieving memory...")
        retrieved = vault.get_persona("alden", test_user_id)
        
        if retrieved:
            print("✅ Memory retrieved successfully!")
            print(f"📊 Retrieved user_id: {retrieved.get('user_id')}")
            print(f"📊 Memory data user_id: {retrieved['data'].get('user_id')}")
        else:
            print("❌ Memory retrieval failed!")
            
            # Debug: Load all data and check what's stored
            print("\n3. Debug: Loading all Vault data...")
            all_data = vault._load_all()
            persona_memories = all_data.get("persona", {})
            
            print(f"📊 Stored personas: {list(persona_memories.keys())}")
            
            if "alden" in persona_memories:
                stored_mem = persona_memories["alden"]
                print(f"📊 Stored memory user_id: {stored_mem.get('user_id')}")
                print(f"📊 Stored memory data keys: {list(stored_mem.get('data', {}).keys())}")
                print(f"📊 Requesting user_id: {test_user_id}")
                
                if stored_mem.get('user_id') == test_user_id:
                    print("✅ User IDs match in storage!")
                else:
                    print(f"❌ User ID mismatch: stored='{stored_mem.get('user_id')}', requested='{test_user_id}'")
            else:
                print("❌ No 'alden' persona found in storage")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_vault_user_id()