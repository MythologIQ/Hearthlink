#!/usr/bin/env python3
"""
Voice Routing Compliance Test Suite
Validates all voice routing requirements from VOICE_ACCESS_POLICY.md
"""

import unittest
import time
import json
import os
from unittest.mock import Mock, patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class VoiceRoutingComplianceTestSuite(unittest.TestCase):
    """Comprehensive voice routing compliance test suite."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.chrome_options = Options()
        cls.chrome_options.add_argument("--headless")
        cls.chrome_options.add_argument("--no-sandbox")
        cls.chrome_options.add_argument("--disable-dev-shm-usage")
        cls.chrome_options.add_argument("--disable-gpu")
        cls.chrome_options.add_argument("--window-size=1920,1080")
        
        # Test configuration
        cls.base_url = "http://localhost:3000"
        cls.timeout = 10
        cls.test_results = []
        
        # Voice policy test data
        cls.local_agents = ['alden', 'alice', 'mimic', 'sentry']
        cls.external_agents = ['gemini-cli', 'google-api', 'trae-cli']
        
    def setUp(self):
        """Set up for each individual test."""
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, self.timeout)
        self.actions = ActionChains(self.driver)
        
    def tearDown(self):
        """Clean up after each test."""
        if hasattr(self, 'driver'):
            self.driver.quit()
            
    def log_test_result(self, test_name, status, details=""):
        """Log test results for reporting."""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        })

    # ==================== VOICE ACCESS STATES TESTS ====================
    
    def test_voice_interaction_enabled_state(self):
        """Test Voice Interaction Enabled state compliance"""
        test_name = "Voice Access - Enabled State Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Verify voice interface is active
            voice_interface = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "voice-interface"))
            )
            self.assertTrue(voice_interface.is_displayed())
            
            # Verify local agent interaction is available
            local_agent_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-agent-type='local']")
            self.assertGreater(len(local_agent_elements), 0, "No local agent elements found")
            
            # Verify universal voice HUD is active
            voice_hud = self.driver.find_element(By.CLASS_NAME, "voice-interface")
            self.assertTrue(voice_hud.is_displayed(), "Voice HUD not visible")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_voice_interaction_disabled_state(self):
        """Test Voice Interaction Disabled state compliance"""
        test_name = "Voice Access - Disabled State Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Check for voice settings
            voice_settings = self.driver.find_elements(By.CLASS_NAME, "voice-settings")
            if voice_settings:
                # Test disabled state
                disabled_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-voice-enabled='false']")
                self.assertGreater(len(disabled_elements), 0, "No voice disabled state found")
            
            # Verify microphone inactive when disabled
            microphone_elements = self.driver.find_elements(By.CLASS_NAME, "microphone")
            if microphone_elements:
                for mic in microphone_elements:
                    self.assertFalse(mic.is_enabled(), "Microphone not disabled when voice is disabled")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== LOCAL AGENT VOICE INTERACTION TESTS ====================
    
    def test_local_agent_conversational_mode(self):
        """Test local agents conversational mode compliance"""
        test_name = "Local Agents - Conversational Mode Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Test each local agent
            for agent in self.local_agents:
                # Check for agent selection
                agent_elements = self.driver.find_elements(By.CSS_SELECTOR, f"[data-agent='{agent}']")
                self.assertGreater(len(agent_elements), 0, f"No {agent} agent elements found")
                
                # Check for name addressing capability
                name_elements = self.driver.find_elements(By.CSS_SELECTOR, f"[data-agent-name='{agent}']")
                self.assertGreater(len(name_elements), 0, f"No name addressing for {agent}")
                
                # Check for voice HUD selection
                hud_selection = self.driver.find_elements(By.CLASS_NAME, "voice-hud-selection")
                self.assertGreater(len(hud_selection), 0, f"No voice HUD selection for {agent}")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_agent_delegation_protocol(self):
        """Test agent deference protocol compliance"""
        test_name = "Local Agents - Delegation Protocol Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for agent deference messages
            deference_elements = self.driver.find_elements(By.CLASS_NAME, "agent-deference")
            self.assertGreater(len(deference_elements), 0, "No agent deference protocol found")
            
            # Check for "better question for" responses
            better_question_elements = self.driver.find_elements(By.CLASS_NAME, "better-question-response")
            self.assertGreater(len(better_question_elements), 0, "No better question responses found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== EXTERNAL AGENT VOICE PERMISSIONS TESTS ====================
    
    def test_external_agent_default_disabled(self):
        """Test external agents disabled by default compliance"""
        test_name = "External Agents - Default Disabled Compliance"
        try:
            self.driver.get(f"{self.base_url}/settings/external-agents")
            
            # Check for default disabled state
            disabled_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-enabled='false']")
            self.assertGreater(len(disabled_elements), 0, "External agents not disabled by default")
            
            # Check for security indicators
            security_elements = self.driver.find_elements(By.CLASS_NAME, "security-indicator")
            self.assertGreater(len(security_elements), 0, "No security indicators found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_external_agent_permission_layers(self):
        """Test external agent permission layers compliance"""
        test_name = "External Agents - Permission Layers Compliance"
        try:
            self.driver.get(f"{self.base_url}/core/external-agents")
            
            # Check for explicit user activation
            activation_elements = self.driver.find_elements(By.CLASS_NAME, "explicit-activation")
            self.assertGreater(len(activation_elements), 0, "No explicit activation controls found")
            
            # Check for Core connection requirement
            core_connection_elements = self.driver.find_elements(By.CLASS_NAME, "core-connection")
            self.assertGreater(len(core_connection_elements), 0, "No Core connection indicators found")
            
            # Check for active session tracking
            session_tracking_elements = self.driver.find_elements(By.CLASS_NAME, "session-tracking")
            self.assertGreater(len(session_tracking_elements), 0, "No session tracking found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== VOICE ROUTING LOGIC TESTS ====================
    
    def test_agent_agnostic_mode(self):
        """Test Agent Agnostic Mode compliance"""
        test_name = "Voice Routing - Agent Agnostic Mode Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for agnostic mode
            agnostic_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-routing-mode='agnostic']")
            self.assertGreater(len(agnostic_elements), 0, "No agent agnostic mode found")
            
            # Check for system listening indicators
            listening_elements = self.driver.find_elements(By.CLASS_NAME, "system-listening")
            self.assertGreater(len(listening_elements), 0, "No system listening indicators found")
            
            # Check for agent name detection
            name_detection_elements = self.driver.find_elements(By.CLASS_NAME, "agent-name-detection")
            self.assertGreater(len(name_detection_elements), 0, "No agent name detection found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_isolated_mode_pinned_agent(self):
        """Test Isolated Mode (Pinned Agent) compliance"""
        test_name = "Voice Routing - Isolated Mode Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for isolated mode controls
            isolated_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-routing-mode='isolated']")
            self.assertGreater(len(isolated_elements), 0, "No isolated mode found")
            
            # Check for pinned agent indicators
            pinned_elements = self.driver.find_elements(By.CLASS_NAME, "pinned-agent")
            self.assertGreater(len(pinned_elements), 0, "No pinned agent indicators found")
            
            # Check for access prevention mechanisms
            prevention_elements = self.driver.find_elements(By.CLASS_NAME, "access-prevention")
            self.assertGreater(len(prevention_elements), 0, "No access prevention mechanisms found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_safety_reinforcement(self):
        """Test Safety Reinforcement compliance"""
        test_name = "Voice Routing - Safety Reinforcement Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for routing confirmation
            routing_confirmation_elements = self.driver.find_elements(By.CLASS_NAME, "routing-confirmation")
            self.assertGreater(len(routing_confirmation_elements), 0, "No routing confirmation found")
            
            # Check for voice confirmation messages
            voice_confirmation_elements = self.driver.find_elements(By.CLASS_NAME, "voice-confirmation")
            self.assertGreater(len(voice_confirmation_elements), 0, "No voice confirmation found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== VOICE AUTHENTICATION TESTS ====================
    
    def test_secure_mode_activation(self):
        """Test Secure Mode Activation compliance"""
        test_name = "Voice Auth - Secure Mode Activation Compliance"
        try:
            self.driver.get(f"{self.base_url}/core/dev-mode")
            
            # Check for activation phrase
            activation_elements = self.driver.find_elements(By.CLASS_NAME, "activation-phrase")
            self.assertGreater(len(activation_elements), 0, "No activation phrase found")
            
            # Check for challenge phrase
            challenge_elements = self.driver.find_elements(By.CLASS_NAME, "challenge-phrase")
            self.assertGreater(len(challenge_elements), 0, "No challenge phrase found")
            
            # Check for PIN entry
            pin_elements = self.driver.find_elements(By.CLASS_NAME, "pin-entry")
            self.assertGreater(len(pin_elements), 0, "No PIN entry found")
            
            # Check for Dev Mode UI
            dev_mode_elements = self.driver.find_elements(By.CLASS_NAME, "dev-mode-ui")
            self.assertGreater(len(dev_mode_elements), 0, "No Dev Mode UI found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== OFFLINE MODE TESTS ====================
    
    def test_offline_mode_behavior(self):
        """Test Offline Mode behavior compliance"""
        test_name = "Offline Mode - Behavior Compliance"
        try:
            self.driver.get(f"{self.base_url}/voice-hud?mode=offline")
            
            # Check for local agents remaining functional
            local_functional_elements = self.driver.find_elements(By.CLASS_NAME, "local-functional")
            self.assertGreater(len(local_functional_elements), 0, "Local agents not functional in offline mode")
            
            # Check for conversational intelligence maintained
            intelligence_elements = self.driver.find_elements(By.CLASS_NAME, "conversational-intelligence")
            self.assertGreater(len(intelligence_elements), 0, "Conversational intelligence not maintained")
            
            # Check for command mode available
            command_elements = self.driver.find_elements(By.CLASS_NAME, "command-mode")
            self.assertGreater(len(command_elements), 0, "Command mode not available")
            
            # Check for external agent access disabled
            external_disabled_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-external-disabled='true']")
            self.assertGreater(len(external_disabled_elements), 0, "External agents not disabled in offline mode")
            
            # Check for user alert
            alert_elements = self.driver.find_elements(By.CLASS_NAME, "offline-alert")
            self.assertGreater(len(alert_elements), 0, "No offline mode alert found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== FALLBACK & ERROR STATES TESTS ====================
    
    def test_voice_misrouting_prevention(self):
        """Test Voice Misrouting Prevention compliance"""
        test_name = "Fallback - Voice Misrouting Prevention Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for misrouting prevention
            prevention_elements = self.driver.find_elements(By.CLASS_NAME, "misrouting-prevention")
            self.assertGreater(len(prevention_elements), 0, "No misrouting prevention found")
            
            # Check for external engagement prompts
            engagement_elements = self.driver.find_elements(By.CLASS_NAME, "external-engagement")
            self.assertGreater(len(engagement_elements), 0, "No external engagement prompts found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_agent_deference_protocol_fallback(self):
        """Test Agent Deference Protocol fallback compliance"""
        test_name = "Fallback - Agent Deference Protocol Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for local agent responses
            local_response_elements = self.driver.find_elements(By.CLASS_NAME, "local-agent-response")
            self.assertGreater(len(local_response_elements), 0, "No local agent responses found")
            
            # Check for suboptimal task handling
            suboptimal_elements = self.driver.find_elements(By.CLASS_NAME, "suboptimal-handling")
            self.assertGreater(len(suboptimal_elements), 0, "No suboptimal task handling found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== LOGGING & TRANSPARENCY TESTS ====================
    
    def test_voice_session_logging(self):
        """Test Voice Session Logging compliance"""
        test_name = "Logging - Voice Session Logging Compliance"
        try:
            self.driver.get(f"{self.base_url}/vault/voice-logs")
            
            # Check for session transcripts
            transcript_elements = self.driver.find_elements(By.CLASS_NAME, "session-transcript")
            self.assertGreater(len(transcript_elements), 0, "No session transcripts found")
            
            # Check for command triggers
            trigger_elements = self.driver.find_elements(By.CLASS_NAME, "command-trigger")
            self.assertGreater(len(trigger_elements), 0, "No command triggers found")
            
            # Check for private mode handling
            private_elements = self.driver.find_elements(By.CLASS_NAME, "private-mode")
            self.assertGreater(len(private_elements), 0, "No private mode handling found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_external_agent_logging(self):
        """Test External Agent Voice Interaction Logging compliance"""
        test_name = "Logging - External Agent Logging Compliance"
        try:
            self.driver.get(f"{self.base_url}/vault/external-logs")
            
            # Check for agent identity logging
            identity_elements = self.driver.find_elements(By.CLASS_NAME, "agent-identity")
            self.assertGreater(len(identity_elements), 0, "No agent identity logging found")
            
            # Check for duration logging
            duration_elements = self.driver.find_elements(By.CLASS_NAME, "duration-logging")
            self.assertGreater(len(duration_elements), 0, "No duration logging found")
            
            # Check for purpose and routed command summary
            purpose_elements = self.driver.find_elements(By.CLASS_NAME, "purpose-summary")
            self.assertGreater(len(purpose_elements), 0, "No purpose summary found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== AGENT IDENTITY & CONFIRMATION TESTS ====================
    
    def test_agent_identity_display(self):
        """Test Agent Identity Display compliance"""
        test_name = "Agent Identity - Display Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Check for agent identity display
            identity_elements = self.driver.find_elements(By.CLASS_NAME, "agent-identity")
            self.assertGreater(len(identity_elements), 0, "No agent identity display found")
            
            # Check for routing confirmation display
            confirmation_elements = self.driver.find_elements(By.CLASS_NAME, "routing-confirmation")
            self.assertGreater(len(confirmation_elements), 0, "No routing confirmation display found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_agent_confirmation_messages(self):
        """Test Agent Confirmation Messages compliance"""
        test_name = "Agent Identity - Confirmation Messages Compliance"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for confirmation message elements
            confirmation_elements = self.driver.find_elements(By.CLASS_NAME, "agent-confirmation")
            self.assertGreater(len(confirmation_elements), 0, "No agent confirmation messages found")
            
            # Check for "You're speaking with" messages
            speaking_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-confirmation-type='speaking']")
            self.assertGreater(len(speaking_elements), 0, "No 'speaking with' confirmation messages found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== VAULT LOGGING TESTS ====================
    
    def test_vault_session_logging(self):
        """Test Vault Session Logging compliance"""
        test_name = "Vault Logging - Session Logging Compliance"
        try:
            self.driver.get(f"{self.base_url}/vault")
            
            # Check for voice session logging
            voice_session_elements = self.driver.find_elements(By.CLASS_NAME, "voice-session-log")
            self.assertGreater(len(voice_session_elements), 0, "No voice session logging found")
            
            # Check for session data structure
            session_data_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-session-type='voice']")
            self.assertGreater(len(session_data_elements), 0, "No voice session data structure found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_vault_audit_trail(self):
        """Test Vault Audit Trail compliance"""
        test_name = "Vault Logging - Audit Trail Compliance"
        try:
            self.driver.get(f"{self.base_url}/vault/audit")
            
            # Check for voice event logging
            voice_event_elements = self.driver.find_elements(By.CLASS_NAME, "voice-event-log")
            self.assertGreater(len(voice_event_elements), 0, "No voice event logging found")
            
            # Check for audit trail structure
            audit_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-audit-type='voice']")
            self.assertGreater(len(audit_elements), 0, "No voice audit trail structure found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== EDGE CASE TESTS ====================
    
    def test_edge_case_voice_timeout(self):
        """Test edge case: Voice timeout handling"""
        test_name = "Edge Case - Voice Timeout Handling"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for voice timeout handling
            timeout_elements = self.driver.find_elements(By.CLASS_NAME, "voice-timeout")
            self.assertGreater(len(timeout_elements), 0, "No voice timeout handling found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_edge_case_voice_recognition_failure(self):
        """Test edge case: Voice recognition failure"""
        test_name = "Edge Case - Voice Recognition Failure"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for recognition failure handling
            failure_elements = self.driver.find_elements(By.CLASS_NAME, "recognition-failure")
            self.assertGreater(len(failure_elements), 0, "No recognition failure handling found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_edge_case_multiple_agent_conflict(self):
        """Test edge case: Multiple agent conflict resolution"""
        test_name = "Edge Case - Multiple Agent Conflict Resolution"
        try:
            self.driver.get(f"{self.base_url}")
            
            # Activate voice interface
            voice_toggle = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "voice-toggle"))
            )
            voice_toggle.click()
            
            # Check for conflict resolution
            conflict_elements = self.driver.find_elements(By.CLASS_NAME, "conflict-resolution")
            self.assertGreater(len(conflict_elements), 0, "No conflict resolution found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== POLICY COMPLIANCE SUMMARY TESTS ====================
    
    def test_voice_policy_compliance_summary(self):
        """Test Voice Policy Compliance Summary Table"""
        test_name = "Policy Compliance - Summary Table Compliance"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Check for all policy compliance scenarios
            scenarios = [
                "voice-enabled-general",
                "voice-disabled",
                "dev-mode-activation",
                "offline-mode",
                "pinned-agent-active"
            ]
            
            for scenario in scenarios:
                scenario_elements = self.driver.find_elements(By.CSS_SELECTOR, f"[data-scenario='{scenario}']")
                self.assertGreater(len(scenario_elements), 0, f"No {scenario} scenario found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== TEST REPORTING ====================
    
    @classmethod
    def tearDownClass(cls):
        """Generate comprehensive voice routing compliance test report."""
        report = {
            "test_suite": "Hearthlink Voice Routing Compliance Test Suite",
            "timestamp": time.time(),
            "total_tests": len(cls.test_results),
            "passed": len([r for r in cls.test_results if r["status"] == "PASSED"]),
            "failed": len([r for r in cls.test_results if r["status"] == "FAILED"]),
            "results": cls.test_results,
            "policy_compliance": {
                "voice_access_states": "tested",
                "local_agent_interaction": "tested", 
                "external_agent_permissions": "tested",
                "voice_routing_logic": "tested",
                "voice_authentication": "tested",
                "offline_mode": "tested",
                "fallback_error_states": "tested",
                "logging_transparency": "tested",
                "agent_identity_confirmation": "tested",
                "vault_logging": "tested"
            }
        }
        
        # Save report to file
        with open("tests/voice_routing_compliance_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n🎙️ Voice Routing Compliance Test Suite Summary:")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed']}")
        print(f"Failed: {report['failed']}")
        print(f"Success Rate: {(report['passed']/report['total_tests']*100):.1f}%")
        print(f"Policy Compliance Areas: {len(report['policy_compliance'])}")
        print(f"Results saved to: tests/voice_routing_compliance_results.json")

def run_voice_routing_compliance_test_suite():
    """Run the voice routing compliance test suite."""
    print("🎙️ Starting Hearthlink Voice Routing Compliance Test Suite")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [method for method in dir(VoiceRoutingComplianceTestSuite) 
                   if method.startswith('test_')]
    
    for method in test_methods:
        suite.addTest(VoiceRoutingComplianceTestSuite(method))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_voice_routing_compliance_test_suite()
    exit(0 if success else 1) 