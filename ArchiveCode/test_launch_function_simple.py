#!/usr/bin/env python3
"""
Simple test to verify launch_local_resource function exists and basic functionality.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from synapse.synapse import Synapse

def test_function_exists():
    """Test if the function exists."""
    print("🔍 Testing if launch_local_resource function exists...")
    
    synapse = Synapse()
    has_function = hasattr(synapse, 'launch_local_resource')
    
    print(f"✅ Function exists: {has_function}")
    return has_function

def test_function_with_invalid_target():
    """Test function with invalid target to check error handling."""
    print("\n🔍 Testing function with invalid target...")
    
    synapse = Synapse()
    
    try:
        result = synapse.launch_local_resource("invalid_target")
        print(f"✅ Function executed with error handling: {result}")
        
        # Check if it's a proper error response
        if isinstance(result, dict) and "error" in result:
            print("✅ Error handling works correctly")
            return True
        else:
            print("❌ Error handling doesn't work as expected")
            return False
    except Exception as e:
        print(f"❌ Function threw unexpected exception: {e}")
        return False

def test_function_with_dev_container():
    """Test function with dev_container (placeholder implementation)."""
    print("\n🔍 Testing function with dev_container...")
    
    synapse = Synapse()
    
    try:
        result = synapse.launch_local_resource("dev_container")
        print(f"✅ Function executed for dev_container: {result}")
        
        # Check if it's a proper response
        if isinstance(result, dict) and "target" in result:
            print("✅ dev_container target works correctly")
            return True
        else:
            print("❌ dev_container target doesn't work as expected")
            return False
    except Exception as e:
        print(f"❌ Function threw unexpected exception: {e}")
        return False

def test_claude_code_without_binary():
    """Test claude_code target without having the binary installed."""
    print("\n🔍 Testing claude_code target (expect error without binary)...")
    
    synapse = Synapse()
    
    try:
        result = synapse.launch_local_resource("claude_code")
        print(f"✅ Function executed for claude_code: {result}")
        
        # Should return an error since claude-code is not installed
        if isinstance(result, dict) and "error" in result:
            print("✅ claude_code target correctly handles missing binary")
            return True
        else:
            print("❌ claude_code target should have returned an error")
            return False
    except Exception as e:
        print(f"❌ Function threw unexpected exception: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Simple launch_local_resource Function Test")
    print("=" * 50)
    
    tests = [
        test_function_exists,
        test_function_with_invalid_target,
        test_function_with_dev_container,
        test_claude_code_without_binary
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n🎯 Test Results Summary")
    print("-" * 30)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Function is operational.")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)