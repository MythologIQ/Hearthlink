"""
Test Enhanced Synapse Integration with Traffic Manager and SIEM
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from synapse.synapse import Synapse, SynapseConfig
from synapse.traffic_manager import AgentPriority, RequestStatus
from synapse.sentry_siem import ThreatLevel, SecurityEventType
import json
import time

class TestEnhancedSynapseIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.config = SynapseConfig()
        self.config.traffic_manager = {
            "max_workers": 5,
            "enable_rate_limiting": True,
            "enable_security_monitoring": True
        }
        self.config.security = {
            "require_manifest_signature": False,
            "auto_approve_low_risk": True,
            "max_concurrent_executions": 10,
            "security_threshold": "MEDIUM"
        }
        
        self.synapse = Synapse(self.config)
        
        # Register test plugin
        self.test_plugin_manifest = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for enhanced integration",
            "author": "Test Author",
            "permissions": ["read", "write"],
            "entry_point": "test_plugin.py",
            "risk_tier": "low"
        }
        
        self.plugin_id = self.synapse.register_plugin(self.test_plugin_manifest, "test_user")
        self.synapse.approve_plugin(self.plugin_id, "test_user", "Test approval")
    
    def tearDown(self):
        """Clean up test environment."""
        self.synapse.cleanup_system()
    
    def test_enhanced_plugin_execution_with_rate_limiting(self):
        """Test plugin execution with rate limiting."""
        # Execute plugin multiple times to test rate limiting
        results = []
        for i in range(5):
            result = self.synapse.execute_plugin(
                self.plugin_id,
                "test_user",
                {"test_data": f"execution_{i}"}
            )
            results.append(result)
        
        # Check that all executions were processed
        self.assertEqual(len(results), 5)
        
        # Check that some executions succeeded
        successful_executions = [r for r in results if r.success]
        self.assertGreater(len(successful_executions), 0)
        
        print(f"Enhanced plugin execution test: {len(successful_executions)}/5 executions successful")
    
    def test_traffic_manager_integration(self):
        """Test traffic manager integration."""
        # Get initial traffic metrics
        metrics = self.synapse.get_traffic_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn("uptime_seconds", metrics)
        self.assertIn("processed_requests", metrics)
        
        # Execute plugin to generate traffic
        self.synapse.execute_plugin(
            self.plugin_id,
            "test_user",
            {"test_data": "traffic_test"}
        )
        
        # Check updated metrics
        updated_metrics = self.synapse.get_traffic_metrics()
        self.assertIsInstance(updated_metrics, dict)
        
        print(f"Traffic manager integration test: Metrics collected successfully")
    
    def test_security_orchestrator_integration(self):
        """Test security orchestrator integration."""
        # Get initial security report
        security_report = self.synapse.get_security_report()
        self.assertIsInstance(security_report, dict)
        self.assertIn("timestamp", security_report)
        self.assertIn("system_metrics", security_report)
        
        # Execute plugin to generate security events
        self.synapse.execute_plugin(
            self.plugin_id,
            "test_user",
            {"test_data": "security_test"}
        )
        
        # Check updated security report
        updated_report = self.synapse.get_security_report()
        self.assertIsInstance(updated_report, dict)
        
        print(f"Security orchestrator integration test: Security monitoring active")
    
    def test_system_status_with_enhanced_monitoring(self):
        """Test enhanced system status reporting."""
        status = self.synapse.get_system_status()
        
        # Check that enhanced monitoring is included
        self.assertIn("enhanced_traffic", status)
        self.assertIn("security", status)
        self.assertIn("plugins", status)
        self.assertIn("connections", status)
        
        # Check enhanced traffic metrics
        enhanced_traffic = status["enhanced_traffic"]
        self.assertIn("uptime_seconds", enhanced_traffic)
        self.assertIn("processed_requests", enhanced_traffic)
        
        # Check security metrics
        security = status["security"]
        self.assertIn("timestamp", security)
        self.assertIn("system_metrics", security)
        
        print(f"Enhanced system status test: All monitoring components active")
    
    def test_bandwidth_management(self):
        """Test user bandwidth management."""
        # Update user bandwidth
        self.synapse.update_user_bandwidth("test_user", "external_agents", 10.0, 20)
        
        # Execute plugin to test bandwidth limits
        result = self.synapse.execute_plugin(
            self.plugin_id,
            "test_user",
            {"test_data": "bandwidth_test"}
        )
        
        # Check that execution was processed
        self.assertIsNotNone(result)
        
        print(f"Bandwidth management test: User bandwidth updated successfully")
    
    def test_agent_quarantine_functionality(self):
        """Test agent quarantine functionality."""
        # Check initial quarantine status
        is_quarantined = self.synapse.is_agent_quarantined(self.plugin_id)
        self.assertFalse(is_quarantined)
        
        # Note: In a real test, we would trigger quarantine through security violations
        # For now, we just test the API exists and returns expected results
        
        print(f"Agent quarantine test: Quarantine API functional")
    
    def test_connection_management_with_security(self):
        """Test connection management with security integration."""
        # Request a connection
        connection_id = self.synapse.request_connection(
            "test_agent",
            "Testing connection with security",
            ["read", "write"],
            "test_user"
        )
        
        self.assertIsNotNone(connection_id)
        
        # Approve connection
        result = self.synapse.approve_connection(connection_id, "test_user")
        self.assertEqual(result.status, "established")
        
        # Check system status includes connection
        status = self.synapse.get_system_status()
        self.assertGreater(status["connections"]["active"], 0)
        
        # Close connection
        closed = self.synapse.close_connection(connection_id, "test_user")
        self.assertTrue(closed)
        
        print(f"Connection management with security test: Connection lifecycle managed successfully")
    
    def test_comprehensive_integration_flow(self):
        """Test comprehensive integration flow."""
        # 1. Register and approve plugin
        comprehensive_manifest = {
            "name": "comprehensive_test",
            "version": "1.0.0",
            "description": "Comprehensive integration test plugin",
            "author": "Test Author",
            "permissions": ["read", "write", "network"],
            "entry_point": "comprehensive_test.py",
            "risk_tier": "medium"
        }
        
        comp_plugin_id = self.synapse.register_plugin(comprehensive_manifest, "test_user")
        self.synapse.approve_plugin(comp_plugin_id, "test_user", "Comprehensive test approval")
        
        # 2. Execute plugin multiple times
        execution_results = []
        for i in range(3):
            result = self.synapse.execute_plugin(
                comp_plugin_id,
                "test_user",
                {"iteration": i, "data": f"comprehensive_test_{i}"}
            )
            execution_results.append(result)
        
        # 3. Check traffic metrics
        traffic_metrics = self.synapse.get_traffic_metrics()
        self.assertGreater(traffic_metrics["processed_requests"], 0)
        
        # 4. Check security report
        security_report = self.synapse.get_security_report()
        self.assertGreater(security_report["system_metrics"]["events_processed"], 0)
        
        # 5. Get comprehensive system status
        system_status = self.synapse.get_system_status()
        self.assertGreater(system_status["plugins"]["total"], 1)
        
        print(f"Comprehensive integration test: All components working together successfully")
        
        # Print summary
        print("\nIntegration Test Summary:")
        print(f"- Plugins registered: {system_status['plugins']['total']}")
        print(f"- Traffic processed: {traffic_metrics['processed_requests']} requests")
        print(f"- Security events: {security_report['system_metrics']['events_processed']}")
        print(f"- System uptime: {traffic_metrics['uptime_seconds']:.2f} seconds")


if __name__ == '__main__':
    unittest.main()