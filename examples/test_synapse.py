#!/usr/bin/env python3
"""
Test Script for Synapse Plugin Gateway

Demonstrates the functionality of the Synapse plugin gateway system.
"""

import json
import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from synapse.synapse import Synapse, SynapseConfig
from synapse.config import ConfigManager

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('synapse_test.log')
        ]
    )

def test_plugin_registration(synapse_instance: Synapse):
    """Test plugin registration."""
    print("\n=== Testing Plugin Registration ===")
    
    # Load example manifest
    manifest_path = Path(__file__).parent / "plugins" / "summarizer_manifest.json"
    
    with open(manifest_path, 'r') as f:
        manifest_data = json.load(f)
    
    try:
        # Register plugin
        plugin_id = synapse_instance.register_plugin(manifest_data, "test-user")
        print(f"✅ Plugin registered successfully: {plugin_id}")
        
        # Get plugin status
        status = synapse_instance.get_plugin_status(plugin_id)
        print(f"✅ Plugin status: {status.status}")
        
        return plugin_id
        
    except Exception as e:
        print(f"❌ Plugin registration failed: {e}")
        return None

def test_plugin_approval(synapse_instance: Synapse, plugin_id: str):
    """Test plugin approval."""
    print("\n=== Testing Plugin Approval ===")
    
    try:
        # Approve plugin
        success = synapse_instance.approve_plugin(plugin_id, "test-user", "Testing purposes")
        
        if success:
            print(f"✅ Plugin approved successfully: {plugin_id}")
            
            # Check status
            status = synapse_instance.get_plugin_status(plugin_id)
            print(f"✅ Plugin status: {status.status}")
            print(f"✅ Approved by user: {status.approved_by_user}")
        else:
            print(f"❌ Plugin approval failed: {plugin_id}")
            
    except Exception as e:
        print(f"❌ Plugin approval failed: {e}")

def test_plugin_execution(synapse_instance: Synapse, plugin_id: str):
    """Test plugin execution."""
    print("\n=== Testing Plugin Execution ===")
    
    # Test payload
    test_text = """
    Artificial intelligence is transforming the way we work and live. 
    Machine learning algorithms can now process vast amounts of data 
    to identify patterns and make predictions. Natural language processing 
    enables computers to understand and generate human language. 
    Computer vision allows machines to interpret visual information. 
    These technologies are being applied across industries from healthcare 
    to finance to transportation.
    """
    
    payload = {
        "action": "both",
        "text": test_text,
        "max_length": 150
    }
    
    try:
        # Execute plugin
        result = synapse_instance.execute_plugin(plugin_id, "test-user", payload)
        
        if result.success:
            print(f"✅ Plugin execution successful")
            print(f"✅ Execution time: {result.execution_time:.2f}s")
            print(f"✅ Output: {result.output}")
        else:
            print(f"❌ Plugin execution failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Plugin execution failed: {e}")

def test_permission_management(synapse_instance: Synapse, plugin_id: str):
    """Test permission management."""
    print("\n=== Testing Permission Management ===")
    
    try:
        # Request permissions
        permissions = ["read_core", "write_core", "network_access"]
        request_id = synapse_instance.request_permissions(plugin_id, "test-user", permissions)
        print(f"✅ Permission request created: {request_id}")
        
        # Get pending requests
        pending_requests = synapse_instance.get_pending_permission_requests()
        print(f"✅ Pending permission requests: {len(pending_requests)}")
        
        # Approve permissions
        success = synapse_instance.approve_permissions(request_id, "test-user", "Testing purposes")
        
        if success:
            print(f"✅ Permissions approved successfully")
            
            # Check permissions
            for permission in permissions:
                has_permission = synapse_instance.check_permission(plugin_id, permission)
                print(f"✅ Permission {permission}: {'Granted' if has_permission else 'Denied'}")
        else:
            print(f"❌ Permission approval failed")
            
    except Exception as e:
        print(f"❌ Permission management failed: {e}")

def test_benchmarking(synapse_instance: Synapse, plugin_id: str):
    """Test benchmarking functionality."""
    print("\n=== Testing Benchmarking ===")
    
    try:
        # Run benchmark
        def test_function(**params):
            import time
            time.sleep(0.1)  # Simulate work
            return {"result": "benchmark_test"}
        
        benchmark_result = synapse_instance.run_benchmark(plugin_id, test_function)
        
        if benchmark_result:
            print(f"✅ Benchmark completed successfully")
            print(f"✅ Performance tier: {benchmark_result.get('performance_tier', 'unknown')}")
            print(f"✅ Risk score: {benchmark_result.get('risk_score', 'unknown')}")
        else:
            print(f"❌ Benchmark failed")
            
    except Exception as e:
        print(f"❌ Benchmarking failed: {e}")

def test_traffic_monitoring(synapse_instance: Synapse):
    """Test traffic monitoring."""
    print("\n=== Testing Traffic Monitoring ===")
    
    try:
        # Get traffic summary
        summary = synapse_instance.get_traffic_summary(hours=1)
        
        print(f"✅ Traffic summary retrieved")
        print(f"✅ Total events: {summary.get('total_events', 0)}")
        print(f"✅ Error count: {summary.get('error_count', 0)}")
        
        # Get traffic statistics
        stats = synapse_instance.get_traffic_statistics()
        
        print(f"✅ Traffic statistics retrieved")
        print(f"✅ Total events: {stats.get('total_events', 0)}")
        print(f"✅ Active connections: {stats.get('active_connections', 0)}")
        
    except Exception as e:
        print(f"❌ Traffic monitoring failed: {e}")

def test_system_status(synapse_instance: Synapse):
    """Test system status."""
    print("\n=== Testing System Status ===")
    
    try:
        # Get system status
        status = synapse_instance.get_system_status()
        
        print(f"✅ System status retrieved")
        print(f"✅ Total plugins: {status.get('plugins', {}).get('total', 0)}")
        print(f"✅ Active connections: {status.get('connections', {}).get('active', 0)}")
        print(f"✅ Active sandboxes: {status.get('sandboxes', {}).get('active', 0)}")
        
    except Exception as e:
        print(f"❌ System status failed: {e}")

def test_connection_management(synapse_instance: Synapse):
    """Test connection management."""
    print("\n=== Testing Connection Management ===")
    
    try:
        # Request connection
        connection_id = synapse_instance.request_connection(
            "external-agent-1", 
            "data_processing", 
            ["network_access", "read_core"], 
            "test-user"
        )
        print(f"✅ Connection request created: {connection_id}")
        
        # Approve connection
        result = synapse_instance.approve_connection(connection_id, "test-user")
        
        if result.status == "established":
            print(f"✅ Connection established successfully")
            
            # Close connection
            success = synapse_instance.close_connection(connection_id, "test-user")
            
            if success:
                print(f"✅ Connection closed successfully")
            else:
                print(f"❌ Connection close failed")
        else:
            print(f"❌ Connection establishment failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Connection management failed: {e}")

def main():
    """Main test function."""
    print("🚀 Starting Synapse Plugin Gateway Test")
    
    # Setup logging
    setup_logging()
    
    # Create Synapse instance
    config = SynapseConfig()
    synapse_instance = Synapse(config)
    
    print("✅ Synapse instance created")
    
    # Run tests
    plugin_id = test_plugin_registration(synapse_instance)
    
    if plugin_id:
        test_plugin_approval(synapse_instance, plugin_id)
        test_permission_management(synapse_instance, plugin_id)
        test_plugin_execution(synapse_instance, plugin_id)
        test_benchmarking(synapse_instance, plugin_id)
    
    test_traffic_monitoring(synapse_instance)
    test_system_status(synapse_instance)
    test_connection_management(synapse_instance)
    
    # Cleanup
    print("\n=== Cleanup ===")
    synapse_instance.cleanup_system()
    print("✅ System cleanup completed")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main() 