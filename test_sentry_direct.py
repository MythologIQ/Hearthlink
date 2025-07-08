#!/usr/bin/env python3
"""
Direct test of Sentry persona implementation.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Mock the problematic imports first
import sys
from unittest.mock import Mock

# Create mock modules
mock_main = Mock()
mock_main.HearthlinkLogger = Mock
mock_main.HearthlinkError = Exception

mock_llm = Mock()
mock_llm.LocalLLMClient = Mock
mock_llm.LLMRequest = Mock
mock_llm.LLMResponse = Mock
mock_llm.LLMError = Exception

mock_enterprise_siem = Mock()
mock_enterprise_rbac = Mock()
mock_enterprise_monitoring = Mock()

# Patch the modules
sys.modules['main'] = mock_main
sys.modules['llm.local_llm_client'] = mock_llm
sys.modules['src.enterprise.siem_monitoring'] = mock_enterprise_siem
sys.modules['src.enterprise.rbac_abac_security'] = mock_enterprise_rbac
sys.modules['src.enterprise.advanced_monitoring'] = mock_enterprise_monitoring

try:
    # Now import Sentry directly
    from personas.sentry import SentryPersona, EventType, OverrideReason, RiskEvent
    
    print("✓ Sentry imports successful")
    
    # Create mock LLM client
    class MockLLMClient:
        def __init__(self, config):
            self.config = config
        
        def generate_response(self, prompt):
            return "Mock response"
    
    # Create mock logger
    class MockLogger:
        def info(self, msg):
            print(f"INFO: {msg}")
        
        def error(self, msg):
            print(f"ERROR: {msg}")
        
        def warning(self, msg):
            print(f"WARNING: {msg}")
        
        def debug(self, msg):
            print(f"DEBUG: {msg}")
    
    # Test Sentry creation
    print("\nTesting Sentry persona creation...")
    
    llm_client = MockLLMClient({"model": "test"})
    logger = MockLogger()
    
    sentry = SentryPersona(llm_client, logger)
    print("✓ Sentry persona created successfully")
    
    # Test event monitoring
    print("\nTesting event monitoring...")
    risk_event = sentry.monitor_event(
        EventType.PLUGIN_PERMISSION_ESCALATION,
        "test-origin",
        {"plugin_id": "test-plugin", "permission_level": "admin"}
    )
    print(f"✓ Risk event created: {risk_event.event_id}")
    print(f"  Risk score: {risk_event.risk_score}")
    print(f"  Recommended action: {risk_event.recommended_action}")
    
    # Test override
    print("\nTesting event override...")
    override = sentry.override_event(
        risk_event.event_id,
        "test-user",
        OverrideReason.BUSINESS_NEED,
        "Testing override functionality"
    )
    print(f"✓ Override created: {override.override_id}")
    
    # Test kill switch
    print("\nTesting kill switch...")
    kill_event = sentry.activate_kill_switch(
        "test-target",
        "plugin",
        "Security threat detected",
        "test-user"
    )
    print(f"✓ Kill switch activated: {kill_event.kill_id}")
    
    # Test dashboard
    print("\nTesting dashboard...")
    dashboard = sentry.get_risk_dashboard()
    print(f"✓ Dashboard data retrieved")
    print(f"  Current risk score: {dashboard['current_risk_score']}")
    print(f"  Total events: {dashboard['statistics']['total_events']}")
    print(f"  Total overrides: {dashboard['statistics']['total_overrides']}")
    print(f"  Total kills: {dashboard['statistics']['total_kills']}")
    
    # Test audit export
    print("\nTesting audit export...")
    audit_log = sentry.export_audit_log()
    print(f"✓ Audit log exported")
    print(f"  Risk events: {len(audit_log['risk_events'])}")
    print(f"  Override events: {len(audit_log['override_events'])}")
    print(f"  Kill switch events: {len(audit_log['kill_switch_events'])}")
    
    print("\n🎉 All Sentry tests passed successfully!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc() 