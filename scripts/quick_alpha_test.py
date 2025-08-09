#!/usr/bin/env python3
"""
Quick Alpha Readiness Test - Focused validation of core blockers
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

async def test_database_constraints():
    """Test database FOREIGN KEY constraints"""
    print("🗄️ Testing Database Constraints...")
    
    try:
        from database.database_manager import get_database_manager
        from core.session_manager import get_session_manager, MessageRole
        
        db = get_database_manager()
        session_manager = get_session_manager()
        
        # Test schema version
        schema_version = db.get_schema_version()
        print(f"   Schema version: {schema_version}")
        
        # Test session creation
        user_id = "quick_test_user"
        session_id, session_token = await session_manager.create_session(
            user_id=user_id,
            agent_context={"primary_agent": "alden"},
            metadata={"test": "quick_alpha"}
        )
        
        if session_id and session_token:
            print("   ✅ Session creation: PASSED")
            
            # Test message creation (FK constraints)
            message_id = await session_manager.add_conversation_message(
                session_token=session_token,
                agent_id="alden",
                role=MessageRole.USER,
                content="Quick alpha test message"
            )
            
            if message_id:
                print("   ✅ Message creation with FK: PASSED")
                return True
            else:
                print("   ❌ Message creation with FK: FAILED")
        else:
            print("   ❌ Session creation: FAILED")
            
        return False
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def test_configuration_alignment():
    """Test configuration schema alignment"""
    print("⚙️ Testing Configuration Alignment...")
    
    try:
        # Check config files exist
        project_root = Path(__file__).parent.parent
        config_files = [
            'config/schema.json',
            'config/core_config.json',
            'config/vault_config.json',
            'config/synapse_config.json'
        ]
        
        missing_files = []
        for file in config_files:
            if not (project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"   ❌ Missing config files: {missing_files}")
            return False
        
        # Check schema structure
        schema_path = project_root / 'config' / 'schema.json'
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        required_sections = ['core', 'vault', 'synapse']
        missing_sections = []
        for section in required_sections:
            if section not in schema.get('properties', {}):
                missing_sections.append(section)
        
        if missing_sections:
            print(f"   ❌ Missing schema sections: {missing_sections}")
            return False
        
        print("   ✅ Configuration files: PRESENT")
        print("   ✅ Schema structure: VALID")
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

async def test_handoff_system():
    """Test handoff system basic functionality"""
    print("🔁 Testing Handoff System...")
    
    try:
        from synapse.agent_handoff import get_handoff_manager, HandoffPriority
        from core.session_manager import get_session_manager, MessageRole
        
        handoff_manager = get_handoff_manager()
        session_manager = get_session_manager()
        
        # Create test session
        user_id = "handoff_quick_test"
        session_id, session_token = await session_manager.create_session(
            user_id=user_id,
            agent_context={"primary_agent": "alden"},
            metadata={"test": "handoff_quick"}
        )
        
        if not session_id:
            print("   ❌ Session creation failed")
            return False
        
        # Add basic conversation
        await session_manager.add_conversation_message(
            session_token=session_token,
            agent_id="alden",
            role=MessageRole.USER,
            content="Quick handoff test"
        )
        
        # Test handoff initiation
        handoff_id = await handoff_manager.initiate_handoff(
            source_agent_id="alden",
            target_agent_id="alice",
            session_token=session_token,
            reason="Quick alpha test",
            priority=HandoffPriority.HIGH,
            tags=["quick_test", "alpha"]
        )
        
        if handoff_id:
            print("   ✅ Handoff initiation: PASSED")
            
            # Brief wait for processing
            await asyncio.sleep(0.5)
            
            # Check status
            status = await handoff_manager.get_handoff_status(handoff_id)
            if status:
                print("   ✅ Handoff status tracking: PASSED")
                return True
            else:
                print("   ❌ Handoff status tracking: FAILED")
        else:
            print("   ❌ Handoff initiation: FAILED")
        
        return False
        
    except Exception as e:
        print(f"   ❌ Handoff test failed: {e}")
        return False

async def main():
    """Run quick alpha readiness test"""
    print("🚀 Quick Alpha Readiness Test")
    print("=" * 50)
    print(f"Start time: {datetime.now().isoformat()}")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Database constraints
    results['database'] = await test_database_constraints()
    
    # Test 2: Configuration alignment  
    results['configuration'] = test_configuration_alignment()
    
    # Test 3: Handoff system
    results['handoff'] = await test_handoff_system()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.title()}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 QUICK ALPHA TEST: ALL CORE SYSTEMS FUNCTIONAL")
        print("✅ Primary blockers appear resolved")
    else:
        print("⚠️ QUICK ALPHA TEST: SOME ISSUES DETECTED")
        print("❌ Review failing systems")
    
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)