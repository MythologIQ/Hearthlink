"""
Basic Test for Enhanced Synapse Integration
Tests the integration without external dependencies
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test imports to verify integration
try:
    from synapse.traffic_manager import SynapseTrafficManager, AgentPriority
    from synapse.sentry_siem import SentrySecurityOrchestrator, ThreatLevel
    print("✓ Traffic Manager import successful")
    print("✓ Security Orchestrator import successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

class TestEnhancedSynapseBasic(unittest.TestCase):
    
    def test_traffic_manager_initialization(self):
        """Test traffic manager can be initialized."""
        try:
            config = {"max_workers": 5}
            traffic_manager = SynapseTrafficManager(config)
            self.assertIsNotNone(traffic_manager)
            print("✓ Traffic Manager initialization successful")
        except Exception as e:
            print(f"✗ Traffic Manager initialization failed: {e}")
            self.fail(f"Traffic Manager initialization failed: {e}")
    
    def test_security_orchestrator_initialization(self):
        """Test security orchestrator can be initialized."""
        try:
            config = {"security_threshold": "MEDIUM"}
            security_orchestrator = SentrySecurityOrchestrator(config)
            self.assertIsNotNone(security_orchestrator)
            print("✓ Security Orchestrator initialization successful")
        except Exception as e:
            print(f"✗ Security Orchestrator initialization failed: {e}")
            self.fail(f"Security Orchestrator initialization failed: {e}")
    
    def test_agent_priority_enum(self):
        """Test agent priority enumeration."""
        self.assertEqual(AgentPriority.SYSTEM.value, 0)
        self.assertEqual(AgentPriority.ALDEN.value, 1)
        self.assertEqual(AgentPriority.INTERNAL.value, 2)
        self.assertEqual(AgentPriority.EXTERNAL.value, 3)
        print("✓ Agent Priority enumeration working correctly")
    
    def test_threat_level_enum(self):
        """Test threat level enumeration."""
        self.assertEqual(ThreatLevel.LOW.value, 1)
        self.assertEqual(ThreatLevel.MEDIUM.value, 2)
        self.assertEqual(ThreatLevel.HIGH.value, 3)
        self.assertEqual(ThreatLevel.CRITICAL.value, 4)
        print("✓ Threat Level enumeration working correctly")
    
    def test_integration_architecture(self):
        """Test the integration architecture is properly defined."""
        # Test that we can create both components
        config = {"max_workers": 3}
        traffic_manager = SynapseTrafficManager(config)
        
        security_config = {"security_threshold": "LOW"}  
        security_orchestrator = SentrySecurityOrchestrator(security_config)
        
        # Test that they have expected methods
        self.assertTrue(hasattr(traffic_manager, 'get_system_metrics'))
        self.assertTrue(hasattr(traffic_manager, 'submit_request'))
        self.assertTrue(hasattr(security_orchestrator, 'monitor_agent_transaction'))
        self.assertTrue(hasattr(security_orchestrator, 'get_security_report'))
        
        print("✓ Integration architecture properly defined")
    
    def test_component_cleanup(self):
        """Test components can be properly cleaned up."""
        config = {"max_workers": 2}
        traffic_manager = SynapseTrafficManager(config)
        
        security_config = {"security_threshold": "HIGH"}
        security_orchestrator = SentrySecurityOrchestrator(security_config)
        
        # Test cleanup methods exist
        self.assertTrue(hasattr(traffic_manager, 'shutdown'))
        self.assertTrue(hasattr(security_orchestrator, 'shutdown'))
        
        # Attempt cleanup
        traffic_manager.shutdown()
        security_orchestrator.shutdown()
        
        print("✓ Component cleanup successful")


if __name__ == '__main__':
    print("Running Enhanced Synapse Basic Integration Tests")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2)