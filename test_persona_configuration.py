#!/usr/bin/env python3
"""
Test Script - Persona Configuration System

Demonstrates the persona configuration system functionality including
voice preferences, microphone/sound checks, and fallback handling.
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from installation_ux import (
    PersonaConfigurationWizard,
    PersonaConfigurationUIFlows,
    UIMode,
    FallbackHandler,
    IssueType
)

def setup_logging():
    """Setup logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def test_persona_configuration_wizard():
    """Test the PersonaConfigurationWizard."""
    print("\n" + "="*60)
    print("🧪 Testing PersonaConfigurationWizard")
    print("="*60)
    
    logger = setup_logging()
    wizard = PersonaConfigurationWizard(logger)
    
    # Test complete configuration
    print("\nRunning complete configuration...")
    result = wizard.run_complete_configuration()
    
    if result['success']:
        print("✅ Configuration completed successfully!")
        print(f"Audio system: {'✅' if result['audio_system']['success'] else '❌'}")
        print(f"Voice preferences: {'✅' if result['voice_preferences']['success'] else '❌'}")
        print(f"Sound check: {'✅' if result['sound_check']['success'] else '❌'}")
        print(f"Persona configs: {'✅' if result['persona_configs']['success'] else '❌'}")
        print(f"Interaction setup: {'✅' if result['interaction_preferences']['success'] else '❌'}")
        print(f"Fallback mode: {result['fallback_mode']}")
    else:
        print("❌ Configuration failed!")
        print(f"Error: {result['error']}")
    
    return result

def test_ui_flows():
    """Test the PersonaConfigurationUIFlows."""
    print("\n" + "="*60)
    print("🧪 Testing PersonaConfigurationUIFlows")
    print("="*60)
    
    logger = setup_logging()
    ui_flows = PersonaConfigurationUIFlows(ui_mode=UIMode.CLI, logger=logger)
    
    # Test complete flow
    print("\nRunning complete UI flow...")
    result = ui_flows.run_complete_flow()
    
    if result['success']:
        print("✅ UI flow completed successfully!")
        print(f"Steps completed: {len(result['completed_steps'])}")
        print(f"Accessibility enabled: {result['accessibility_enabled']}")
        print(f"User responses: {len(result['user_responses'])}")
        
        # Show step results
        for step_name, step_result in result['results'].items():
            status = "✅" if step_result['success'] else "❌"
            print(f"  {step_name}: {status}")
    else:
        print("❌ UI flow failed!")
        print(f"Error: {result['error']}")
    
    return result

def test_fallback_handler():
    """Test the FallbackHandler."""
    print("\n" + "="*60)
    print("🧪 Testing FallbackHandler")
    print("="*60)
    
    logger = setup_logging()
    fallback_handler = FallbackHandler(logger)
    
    # Test audio failure handling
    print("\nTesting audio failure handling...")
    audio_error = {
        "error": "No audio output devices detected",
        "context": "audio_system_check"
    }
    audio_result = fallback_handler.handle_audio_failure(audio_error)
    
    if audio_result['success']:
        print("✅ Audio failure handled successfully!")
        print(f"Issue type: {audio_result['issue_type']}")
        print(f"Solution applied: {audio_result['solution_applied']}")
        print(f"Fallback level: {audio_result['fallback_level']}")
        print("User instructions:")
        for instruction in audio_result['user_instructions']:
            print(f"  • {instruction}")
    else:
        print("❌ Audio failure handling failed!")
        print(f"Error: {audio_result['error']}")
    
    # Test microphone failure handling
    print("\nTesting microphone failure handling...")
    mic_error = {
        "error": "Microphone permission denied",
        "context": "microphone_test"
    }
    mic_result = fallback_handler.handle_microphone_failure(mic_error)
    
    if mic_result['success']:
        print("✅ Microphone failure handled successfully!")
        print(f"Issue type: {mic_result['issue_type']}")
        print(f"Solution applied: {mic_result['solution_applied']}")
        print(f"Fallback level: {mic_result['fallback_level']}")
    else:
        print("❌ Microphone failure handling failed!")
        print(f"Error: {mic_result['error']}")
    
    # Test accessibility needs handling
    print("\nTesting accessibility needs handling...")
    accessibility_needs = {
        "screen_reader": True,
        "keyboard_navigation": True,
        "high_contrast": False,
        "voice_guidance": True
    }
    accessibility_result = fallback_handler.handle_accessibility_needs(accessibility_needs)
    
    if accessibility_result['success']:
        print("✅ Accessibility needs handled successfully!")
        print(f"Required features: {accessibility_result['required_features']}")
        print(f"Solutions applied: {len(accessibility_result['solutions_applied'])}")
        print(f"Accessibility enabled: {accessibility_result['accessibility_enabled']}")
    else:
        print("❌ Accessibility needs handling failed!")
        print(f"Error: {accessibility_result['error']}")
    
    return {
        "audio_result": audio_result,
        "mic_result": mic_result,
        "accessibility_result": accessibility_result
    }

def test_issue_detection():
    """Test issue detection and resolution."""
    print("\n" + "="*60)
    print("🧪 Testing Issue Detection and Resolution")
    print("="*60)
    
    logger = setup_logging()
    fallback_handler = FallbackHandler(logger)
    
    # Test issue detection
    print("\nDetecting and resolving issues...")
    context = {
        "platform": "windows",
        "python_version": "3.11.0",
        "audio_enabled": True,
        "microphone_enabled": True
    }
    
    result = fallback_handler.detect_and_resolve_issues(context)
    
    if result['success']:
        print("✅ Issue detection completed successfully!")
        print(f"Issues detected: {result['issues_detected']}")
        print(f"Issues resolved: {result['issues_resolved']}")
        print(f"Fallback mode: {result['fallback_mode']}")
        
        # Show verification results
        verification = result['verification_results']
        print(f"Success rate: {verification['success_rate']:.1%}")
        print(f"Can continue: {verification['can_continue']}")
    else:
        print("❌ Issue detection failed!")
        print(f"Error: {result['error']}")
    
    return result

def main():
    """Main test function."""
    print("🎯 Persona Configuration System Test")
    print("="*60)
    print("This test demonstrates the persona configuration system")
    print("including voice preferences, microphone/sound checks,")
    print("and fallback handling for common hardware issues.")
    print("="*60)
    
    try:
        # Test PersonaConfigurationWizard
        wizard_result = test_persona_configuration_wizard()
        
        # Test PersonaConfigurationUIFlows
        ui_result = test_ui_flows()
        
        # Test FallbackHandler
        fallback_result = test_fallback_handler()
        
        # Test issue detection
        detection_result = test_issue_detection()
        
        # Summary
        print("\n" + "="*60)
        print("📊 Test Summary")
        print("="*60)
        
        tests = [
            ("PersonaConfigurationWizard", wizard_result),
            ("PersonaConfigurationUIFlows", ui_result),
            ("FallbackHandler", fallback_result),
            ("Issue Detection", detection_result)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, result in tests:
            if result.get('success', False):
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Persona configuration system is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the error messages above.")
        
        return passed == total
        
    except Exception as e:
        print(f"❌ Test execution failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 