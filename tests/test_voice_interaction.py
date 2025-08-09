#!/usr/bin/env python3
"""
Voice Interaction Test Suite for Hearthlink
Tests all voice policy requirements from VOICE_ACCESS_POLICY.md
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

class VoiceInteractionTestSuite(unittest.TestCase):
    """Comprehensive voice interaction test suite."""
    
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
        """Test Voice Interaction Enabled state"""
        test_name = "Voice Access - Enabled State"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test local agent interaction
            local_agents = self.driver.find_elements(By.CSS_SELECTOR, "[data-agent-type='local']")
            self.assertGreater(len(local_agents), 0, "No local agent elements found")
            
            # Test external agent permissions
            external_agents = self.driver.find_elements(By.CSS_SELECTOR, "[data-agent-type='external']")
            self.assertGreater(len(external_agents), 0, "No external agent elements found")
            
            # Test universal voice HUD
            voice_hud = self.driver.find_element(By.CLASS_NAME, "voice-hud")
            self.assertTrue(voice_hud.is_displayed(), "Voice HUD not visible")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_voice_interaction_disabled_state(self):
        """Test Voice Interaction Disabled state"""
        test_name = "Voice Access - Disabled State"
        try:
            self.driver.get(f"{self.base_url}/settings/voice")
            
            # Test voice HUD inactive state
            voice_hud = self.driver.find_element(By.CLASS_NAME, "voice-hud")
            inactive_class = voice_hud.get_attribute("class")
            self.assertIn("inactive", inactive_class, "Voice HUD not properly disabled")
            
            # Test microphone inactive
            microphone = self.driver.find_element(By.CLASS_NAME, "microphone")
            self.assertFalse(microphone.is_enabled(), "Microphone not disabled")
            
            # Test no voice parsing
            parsing_elements = self.driver.find_elements(By.CLASS_NAME, "voice-parsing")
            self.assertEqual(len(parsing_elements), 0, "Voice parsing still active when disabled")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== LOCAL AGENT VOICE INTERACTION TESTS ====================
    
    def test_local_agent_conversational_mode(self):
        """Test local agents (Alden, Alice, Mimic, Sentry) conversational mode"""
        test_name = "Local Agents - Conversational Mode"
        try:
            # Test each local agent
            local_agents = ["alden", "alice", "mimic", "sentry"]
            
            for agent in local_agents:
                self.driver.get(f"{self.base_url}/voice-hud?agent={agent}")
                
                # Test conversational interface
                conversation_elements = self.driver.find_elements(By.CLASS_NAME, "conversation-interface")
                self.assertGreater(len(conversation_elements), 0, f"No conversation interface for {agent}")
                
                # Test name addressing
                name_elements = self.driver.find_elements(By.CSS_SELECTOR, f"[data-agent-name='{agent}']")
                self.assertGreater(len(name_elements), 0, f"No name addressing for {agent}")
                
                # Test voice HUD selection
                hud_selection = self.driver.find_elements(By.CLASS_NAME, "voice-hud-selection")
                self.assertGreater(len(hud_selection), 0, f"No voice HUD selection for {agent}")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_agent_delegation_protocol(self):
        """Test agent deference protocol when addressed"""
        test_name = "Local Agents - Delegation Protocol"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test agent deference messages
            deference_elements = self.driver.find_elements(By.CLASS_NAME, "agent-deference")
            self.assertGreater(len(deference_elements), 0, "No agent deference protocol found")
            
            # Test "better question for" responses
            better_question_elements = self.driver.find_elements(By.CLASS_NAME, "better-question-response")
            self.assertGreater(len(better_question_elements), 0, "No better question responses found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== EXTERNAL AGENT VOICE PERMISSIONS TESTS ====================
    
    def test_external_agent_default_disabled(self):
        """Test external agents disabled by default"""
        test_name = "External Agents - Default Disabled"
        try:
            self.driver.get(f"{self.base_url}/settings/external-agents")
            
            # Test default disabled state
            disabled_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-enabled='false']")
            self.assertGreater(len(disabled_elements), 0, "External agents not disabled by default")
            
            # Test security indicators
            security_elements = self.driver.find_elements(By.CLASS_NAME, "security-indicator")
            self.assertGreater(len(security_elements), 0, "No security indicators found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_external_agent_permission_layers(self):
        """Test external agent permission layers"""
        test_name = "External Agents - Permission Layers"
        try:
            self.driver.get(f"{self.base_url}/core/external-agents")
            
            # Test explicit user activation
            activation_elements = self.driver.find_elements(By.CLASS_NAME, "explicit-activation")
            self.assertGreater(len(activation_elements), 0, "No explicit activation controls found")
            
            # Test Core connection requirement
            core_connection_elements = self.driver.find_elements(By.CLASS_NAME, "core-connection")
            self.assertGreater(len(core_connection_elements), 0, "No Core connection indicators found")
            
            # Test active session tracking
            session_tracking_elements = self.driver.find_elements(By.CLASS_NAME, "session-tracking")
            self.assertGreater(len(session_tracking_elements), 0, "No session tracking found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== VOICE ROUTING LOGIC TESTS ====================
    
    def test_agent_agnostic_mode(self):
        """Test Agent Agnostic Mode"""
        test_name = "Voice Routing - Agent Agnostic Mode"
        try:
            self.driver.get(f"{self.base_url}/voice-hud?mode=agnostic")
            
            # Test system listening for any active agent
            listening_elements = self.driver.find_elements(By.CLASS_NAME, "system-listening")
            self.assertGreater(len(listening_elements), 0, "No system listening indicators found")
            
            # Test agent name detection
            name_detection_elements = self.driver.find_elements(By.CLASS_NAME, "agent-name-detection")
            self.assertGreater(len(name_detection_elements), 0, "No agent name detection found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_isolated_mode_pinned_agent(self):
        """Test Isolated Mode (Pinned Agent)"""
        test_name = "Voice Routing - Isolated Mode"
        try:
            self.driver.get(f"{self.base_url}/voice-hud?mode=isolated&agent=alden")
            
            # Test pinned agent routing
            pinned_elements = self.driver.find_elements(By.CLASS_NAME, "pinned-agent")
            self.assertGreater(len(pinned_elements), 0, "No pinned agent indicators found")
            
            # Test prevention of accidental access
            prevention_elements = self.driver.find_elements(By.CLASS_NAME, "access-prevention")
            self.assertGreater(len(prevention_elements), 0, "No access prevention mechanisms found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_safety_reinforcement(self):
        """Test Safety Reinforcement"""
        test_name = "Voice Routing - Safety Reinforcement"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test Core routing confirmation
            routing_confirmation_elements = self.driver.find_elements(By.CLASS_NAME, "routing-confirmation")
            self.assertGreater(len(routing_confirmation_elements), 0, "No routing confirmation found")
            
            # Test agent routing confirmation in voice response
            voice_confirmation_elements = self.driver.find_elements(By.CLASS_NAME, "voice-confirmation")
            self.assertGreater(len(voice_confirmation_elements), 0, "No voice confirmation found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== VOICE AUTHENTICATION TESTS ====================
    
    def test_secure_mode_activation(self):
        """Test Secure Mode Activation"""
        test_name = "Voice Auth - Secure Mode Activation"
        try:
            self.driver.get(f"{self.base_url}/core/dev-mode")
            
            # Test activation phrase
            activation_elements = self.driver.find_elements(By.CLASS_NAME, "activation-phrase")
            self.assertGreater(len(activation_elements), 0, "No activation phrase found")
            
            # Test challenge phrase
            challenge_elements = self.driver.find_elements(By.CLASS_NAME, "challenge-phrase")
            self.assertGreater(len(challenge_elements), 0, "No challenge phrase found")
            
            # Test PIN entry
            pin_elements = self.driver.find_elements(By.CLASS_NAME, "pin-entry")
            self.assertGreater(len(pin_elements), 0, "No PIN entry found")
            
            # Test Dev Mode UI
            dev_mode_elements = self.driver.find_elements(By.CLASS_NAME, "dev-mode-ui")
            self.assertGreater(len(dev_mode_elements), 0, "No Dev Mode UI found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_voiceprint_optional(self):
        """Test Voiceprint (Optional)"""
        test_name = "Voice Auth - Voiceprint Optional"
        try:
            self.driver.get(f"{self.base_url}/settings/voiceprint")
            
            # Test voice biometric enrollment
            enrollment_elements = self.driver.find_elements(By.CLASS_NAME, "voice-enrollment")
            self.assertGreater(len(enrollment_elements), 0, "No voice enrollment found")
            
            # Test internal agent security
            security_elements = self.driver.find_elements(By.CLASS_NAME, "internal-security")
            self.assertGreater(len(security_elements), 0, "No internal security found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== OFFLINE MODE TESTS ====================
    
    def test_offline_mode_behavior(self):
        """Test Offline Mode / No Internet behavior"""
        test_name = "Offline Mode - Behavior"
        try:
            self.driver.get(f"{self.base_url}/voice-hud?mode=offline")
            
            # Test local agents remain functional
            local_functional_elements = self.driver.find_elements(By.CLASS_NAME, "local-functional")
            self.assertGreater(len(local_functional_elements), 0, "Local agents not functional in offline mode")
            
            # Test conversational intelligence maintained
            intelligence_elements = self.driver.find_elements(By.CLASS_NAME, "conversational-intelligence")
            self.assertGreater(len(intelligence_elements), 0, "Conversational intelligence not maintained")
            
            # Test command mode available
            command_elements = self.driver.find_elements(By.CLASS_NAME, "command-mode")
            self.assertGreater(len(command_elements), 0, "Command mode not available")
            
            # Test external agent access disabled
            external_disabled_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-external-disabled='true']")
            self.assertGreater(len(external_disabled_elements), 0, "External agents not disabled in offline mode")
            
            # Test user alert
            alert_elements = self.driver.find_elements(By.CLASS_NAME, "offline-alert")
            self.assertGreater(len(alert_elements), 0, "No offline mode alert found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== FALLBACK & ERROR STATES TESTS ====================
    
    def test_voice_misrouting_prevention(self):
        """Test Voice Misrouting Prevention"""
        test_name = "Fallback - Voice Misrouting Prevention"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test misrouting prevention prompts
            prevention_elements = self.driver.find_elements(By.CLASS_NAME, "misrouting-prevention")
            self.assertGreater(len(prevention_elements), 0, "No misrouting prevention found")
            
            # Test external agent engagement prompts
            engagement_elements = self.driver.find_elements(By.CLASS_NAME, "external-engagement")
            self.assertGreater(len(engagement_elements), 0, "No external engagement prompts found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_agent_deference_protocol(self):
        """Test Agent Deference Protocol"""
        test_name = "Fallback - Agent Deference Protocol"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test local agent responses
            local_response_elements = self.driver.find_elements(By.CLASS_NAME, "local-agent-response")
            self.assertGreater(len(local_response_elements), 0, "No local agent responses found")
            
            # Test suboptimal task handling
            suboptimal_elements = self.driver.find_elements(By.CLASS_NAME, "suboptimal-handling")
            self.assertGreater(len(suboptimal_elements), 0, "No suboptimal task handling found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== LOGGING & TRANSPARENCY TESTS ====================
    
    def test_voice_session_logging(self):
        """Test Voice Session Logging"""
        test_name = "Logging - Voice Session Logging"
        try:
            self.driver.get(f"{self.base_url}/vault/voice-logs")
            
            # Test session transcripts
            transcript_elements = self.driver.find_elements(By.CLASS_NAME, "session-transcript")
            self.assertGreater(len(transcript_elements), 0, "No session transcripts found")
            
            # Test command triggers
            trigger_elements = self.driver.find_elements(By.CLASS_NAME, "command-trigger")
            self.assertGreater(len(trigger_elements), 0, "No command triggers found")
            
            # Test private mode handling
            private_elements = self.driver.find_elements(By.CLASS_NAME, "private-mode")
            self.assertGreater(len(private_elements), 0, "No private mode handling found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_external_agent_logging(self):
        """Test External Agent Voice Interaction Logging"""
        test_name = "Logging - External Agent Logging"
        try:
            self.driver.get(f"{self.base_url}/vault/external-logs")
            
            # Test agent identity logging
            identity_elements = self.driver.find_elements(By.CLASS_NAME, "agent-identity")
            self.assertGreater(len(identity_elements), 0, "No agent identity logging found")
            
            # Test duration logging
            duration_elements = self.driver.find_elements(By.CLASS_NAME, "duration-logging")
            self.assertGreater(len(duration_elements), 0, "No duration logging found")
            
            # Test purpose and routed command summary
            purpose_elements = self.driver.find_elements(By.CLASS_NAME, "purpose-summary")
            self.assertGreater(len(purpose_elements), 0, "No purpose summary found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== EDGE CASE TESTS ====================
    
    def test_edge_case_voice_timeout(self):
        """Test edge case: Voice timeout handling"""
        test_name = "Edge Case - Voice Timeout"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test voice timeout handling
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
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test recognition failure handling
            failure_elements = self.driver.find_elements(By.CLASS_NAME, "recognition-failure")
            self.assertGreater(len(failure_elements), 0, "No recognition failure handling found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    def test_edge_case_multiple_agent_conflict(self):
        """Test edge case: Multiple agent conflict resolution"""
        test_name = "Edge Case - Multiple Agent Conflict"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test conflict resolution
            conflict_elements = self.driver.find_elements(By.CLASS_NAME, "conflict-resolution")
            self.assertGreater(len(conflict_elements), 0, "No conflict resolution found")
            
            self.log_test_result(test_name, "PASSED")
            
        except Exception as e:
            self.log_test_result(test_name, "FAILED", str(e))
            raise

    # ==================== VOICE POLICY COMPLIANCE TESTS ====================
    
    def test_voice_policy_compliance_summary(self):
        """Test Voice Policy Compliance Summary Table"""
        test_name = "Policy Compliance - Summary Table"
        try:
            self.driver.get(f"{self.base_url}/voice-hud")
            
            # Test all policy compliance scenarios
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
        """Generate comprehensive voice interaction test report."""
        report = {
            "test_suite": "Hearthlink Voice Interaction Test Suite",
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
                "logging_transparency": "tested"
            }
        }
        
        # Save report to file
        with open("tests/voice_interaction_test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n🎙️ Voice Interaction Test Suite Summary:")
        print(f"Total Tests: {report['total_tests']}")
        print(f"Passed: {report['passed']}")
        print(f"Failed: {report['failed']}")
        print(f"Success Rate: {(report['passed']/report['total_tests']*100):.1f}%")
        print(f"Policy Compliance: {len(report['policy_compliance'])} areas tested")
        print(f"Results saved to: tests/voice_interaction_test_results.json")

def run_voice_interaction_test_suite():
    """Run the voice interaction test suite."""
    print("🎙️ Starting Hearthlink Voice Interaction Test Suite")
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [method for method in dir(VoiceInteractionTestSuite) 
                   if method.startswith('test_')]
    
    for method in test_methods:
        suite.addTest(VoiceInteractionTestSuite(method))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_voice_interaction_test_suite()
    exit(0 if success else 1) 