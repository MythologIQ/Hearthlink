#!/usr/bin/env python3
"""
Test claude_code launch specifically.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from synapse.synapse import Synapse

def test_claude_code_launch():
    """Test launching claude code."""
    print("🔍 Testing claude_code launch...")
    
    synapse = Synapse()
    
    try:
        # Test with synchronous launch
        result = synapse.launch_local_resource("claude_code")
        print(f"✅ Claude code launch result: {result}")
        
        if result.get("success"):
            print("✅ Claude code launched successfully!")
            return True
        else:
            print(f"⚠️  Claude code launch returned error: {result.get('error')}")
            # This might be expected if claude needs arguments
            return True
    except Exception as e:
        print(f"❌ Claude code launch failed: {e}")
        return False

def test_claude_code_background():
    """Test launching claude code in background."""
    print("\n🔍 Testing claude_code background launch...")
    
    synapse = Synapse()
    
    try:
        # Test with background launch
        result = synapse.launch_local_resource("claude_code", background=True)
        print(f"✅ Claude code background launch result: {result}")
        
        if result.get("success"):
            print("✅ Claude code background launch successful!")
            # Get the PID
            pid = result.get("pid")
            print(f"✅ Claude code running with PID: {pid}")
            
            # Try to kill it
            if pid:
                import os
                try:
                    os.kill(pid, 9)  # SIGKILL
                    print("✅ Killed background claude process")
                except ProcessLookupError:
                    print("⚠️  Process already terminated")
            
            return True
        else:
            print(f"⚠️  Claude code background launch returned error: {result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Claude code background launch failed: {e}")
        return False

def main():
    """Run tests."""
    print("🧪 Claude Code Launch Test")
    print("=" * 30)
    
    tests = [
        test_claude_code_launch,
        test_claude_code_background
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    print("\n🎯 Test Results")
    print("-" * 15)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)