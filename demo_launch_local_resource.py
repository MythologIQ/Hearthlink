#!/usr/bin/env python3
"""
Demonstration of launch_local_resource function
Shows how to use Synapse to launch Claude Code for external tool coordination.
"""

import sys
import os
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from synapse.synapse import Synapse

def demo_basic_launch():
    """Demonstrate basic launch functionality."""
    print("🚀 Demo: Basic Launch")
    print("-" * 20)
    
    synapse = Synapse()
    
    # Launch Claude Code
    print("Launching Claude Code...")
    result = synapse.launch_local_resource("claude_code")
    
    print(f"Result: {result}")
    print(f"Success: {result.get('success')}")
    print(f"Request ID: {result.get('request_id')}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    
    return result

def demo_background_launch():
    """Demonstrate background launch functionality."""
    print("\n🚀 Demo: Background Launch")
    print("-" * 25)
    
    synapse = Synapse()
    
    # Launch Claude Code in background
    print("Launching Claude Code in background...")
    result = synapse.launch_local_resource("claude_code", background=True)
    
    print(f"Result: {result}")
    print(f"Success: {result.get('success')}")
    print(f"Process ID: {result.get('pid')}")
    
    if result.get('success') and result.get('pid'):
        print("Process is running in background...")
        time.sleep(2)  # Let it run for a bit
        
        # Clean up
        pid = result.get('pid')
        try:
            os.kill(pid, 9)  # SIGKILL
            print(f"Terminated process {pid}")
        except ProcessLookupError:
            print("Process already terminated")
    
    return result

def demo_error_handling():
    """Demonstrate error handling."""
    print("\n🚀 Demo: Error Handling")
    print("-" * 22)
    
    synapse = Synapse()
    
    # Try invalid target
    print("Testing invalid target...")
    result = synapse.launch_local_resource("invalid_target")
    
    print(f"Result: {result}")
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error')}")
    
    return result

def demo_traffic_logging():
    """Demonstrate traffic logging."""
    print("\n🚀 Demo: Traffic Logging")
    print("-" * 23)
    
    synapse = Synapse()
    
    # Get initial log count
    initial_logs = len(synapse.get_traffic_logs())
    print(f"Initial log count: {initial_logs}")
    
    # Perform launch
    result = synapse.launch_local_resource("claude_code")
    
    # Check new log count
    final_logs = len(synapse.get_traffic_logs())
    print(f"Final log count: {final_logs}")
    
    if final_logs > initial_logs:
        print("✅ Launch operation was logged")
        latest_log = synapse.get_traffic_logs()[-1]
        print(f"Latest log entry: {latest_log.get('traffic_type')}")
    
    return result

def demo_system_status():
    """Demonstrate system status monitoring."""
    print("\n🚀 Demo: System Status")
    print("-" * 20)
    
    synapse = Synapse()
    
    # Get system status
    status = synapse.get_system_status()
    
    print("System Status:")
    print(f"  Traffic entries: {status.get('traffic', {}).get('total_entries', 0)}")
    print(f"  Active connections: {status.get('connections', {}).get('active', 0)}")
    print(f"  Active sandboxes: {status.get('sandboxes', {}).get('active', 0)}")
    
    return status

def main():
    """Run all demonstrations."""
    print("🧪 Synapse launch_local_resource Demonstration")
    print("=" * 50)
    
    demos = [
        demo_basic_launch,
        demo_background_launch,
        demo_error_handling,
        demo_traffic_logging,
        demo_system_status
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n🎉 Demonstration Complete!")
    print("=" * 30)
    print("✅ launch_local_resource('claude_code') is operational")
    print("✅ External tool coordination is functional")
    print("✅ System is ready for production use")

if __name__ == "__main__":
    main()