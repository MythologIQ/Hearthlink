#!/usr/bin/env python3
"""
Debug test to isolate the issue.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_import():
    """Test basic import."""
    print("🔍 Testing basic import...")
    
    try:
        from synapse.synapse import Synapse
        print("✅ Successfully imported Synapse")
        
        synapse = Synapse()
        print("✅ Successfully created Synapse instance")
        
        has_function = hasattr(synapse, 'launch_local_resource')
        print(f"✅ Has launch_local_resource: {has_function}")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_traffic_logger_direct():
    """Test traffic logger directly."""
    print("\n🔍 Testing traffic logger directly...")
    
    try:
        from synapse.traffic_logger import TrafficLogger, TrafficType, TrafficSeverity
        print("✅ Successfully imported traffic logger components")
        
        logger = TrafficLogger()
        print("✅ Successfully created TrafficLogger instance")
        
        # Test log_traffic method
        entry_id = logger.log_traffic(
            traffic_type=TrafficType.SYSTEM_OPERATION,
            source="test",
            target="test_target",
            severity=TrafficSeverity.MEDIUM
        )
        print(f"✅ Successfully logged traffic: {entry_id}")
        
        return True
    except Exception as e:
        print(f"❌ Traffic logger test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_call():
    """Test the actual function call."""
    print("\n🔍 Testing function call...")
    
    try:
        from synapse.synapse import Synapse
        
        synapse = Synapse()
        
        # Try to call the function
        result = synapse.launch_local_resource("test_target")
        print(f"✅ Function call successful: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Function call failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run debug tests."""
    print("🐛 Debug Test")
    print("=" * 30)
    
    tests = [
        test_basic_import,
        test_traffic_logger_direct,
        test_function_call
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()