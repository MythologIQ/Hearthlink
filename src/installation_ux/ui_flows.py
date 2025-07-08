"""
UI Flows - Persona Configuration Interface

Provides comprehensive UI flow scripts for first-time persona configuration,
including visual layouts, interaction prompts, accessibility features, and
fallback handling for common hardware issues.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

class UIMode(Enum):
    """UI display modes."""
    CLI = "cli"
    GUI = "gui"
    WEB = "web"
    ACCESSIBLE = "accessible"

class FlowStep(Enum):
    """Configuration flow steps."""
    WELCOME = "welcome"
    AUDIO_CHECK = "audio_check"
    VOICE_PREFERENCES = "voice_preferences"
    MICROPHONE_TEST = "microphone_test"
    PERSONA_CONFIG = "persona_config"
    INTERACTION_SETUP = "interaction_setup"
    COMPLETION = "completion"

@dataclass
class UIFlowStep:
    """UI flow step definition."""
    step_id: FlowStep
    title: str
    description: str
    duration_estimate: int  # seconds
    required: bool
    ui_elements: List[str]
    accessibility_features: List[str]
    fallback_options: List[str]

@dataclass
class UIPrompt:
    """UI prompt definition."""
    prompt_id: str
    title: str
    message: str
    options: List[str]
    default_option: Optional[str]
    help_text: Optional[str]
    accessibility_announcement: Optional[str]

class PersonaConfigurationUIFlows:
    """
    Comprehensive UI flow system for persona configuration.
    
    Provides visual layouts, interaction prompts, accessibility features,
    and fallback handling for different UI modes and hardware configurations.
    """
    
    def __init__(self, ui_mode: UIMode = UIMode.CLI, logger: Optional[logging.Logger] = None):
        """
        Initialize UI Flows system.
        
        Args:
            ui_mode: UI display mode (CLI, GUI, WEB, ACCESSIBLE)
            logger: Optional logger instance
        """
        self.ui_mode = ui_mode
        self.logger = logger or logging.getLogger(__name__)
        
        # Flow state
        self.current_step = FlowStep.WELCOME
        self.completed_steps = set()
        self.user_responses = {}
        self.accessibility_enabled = False
        
        # Initialize flow definitions
        self.flow_steps = self._define_flow_steps()
        self.prompts = self._define_prompts()
        
        self._log("ui_flows_initialized", "system", None, "system", {"ui_mode": ui_mode.value})
    
    def run_complete_flow(self) -> Dict[str, Any]:
        """
        Run the complete UI configuration flow.
        
        Returns:
            Dictionary with flow results and user responses
        """
        try:
            self._log("ui_flow_started", "system", None, "ui_flow", {"mode": self.ui_mode.value})
            
            # Step 1: Welcome and Setup
            welcome_result = self._run_welcome_step()
            if not welcome_result['success']:
                return {"success": False, "error": "Welcome step failed"}
            
            # Step 2: Audio System Check
            audio_result = self._run_audio_check_step()
            if not audio_result['success']:
                self._handle_audio_failure(audio_result)
            
            # Step 3: Voice Preferences
            voice_result = self._run_voice_preferences_step()
            if not voice_result['success']:
                return {"success": False, "error": "Voice preferences step failed"}
            
            # Step 4: Microphone Test
            mic_result = self._run_microphone_test_step()
            if not mic_result['success']:
                self._handle_microphone_failure(mic_result)
            
            # Step 5: Persona Configuration
            persona_result = self._run_persona_config_step()
            if not persona_result['success']:
                return {"success": False, "error": "Persona configuration step failed"}
            
            # Step 6: Interaction Setup
            interaction_result = self._run_interaction_setup_step()
            if not interaction_result['success']:
                return {"success": False, "error": "Interaction setup step failed"}
            
            # Step 7: Completion
            completion_result = self._run_completion_step()
            
            return {
                "success": True,
                "completed_steps": list(self.completed_steps),
                "user_responses": self.user_responses,
                "accessibility_enabled": self.accessibility_enabled,
                "results": {
                    "welcome": welcome_result,
                    "audio_check": audio_result,
                    "voice_preferences": voice_result,
                    "microphone_test": mic_result,
                    "persona_config": persona_result,
                    "interaction_setup": interaction_result,
                    "completion": completion_result
                }
            }
            
        except Exception as e:
            self._log("ui_flow_failed", "system", None, "ui_flow", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _define_flow_steps(self) -> Dict[FlowStep, UIFlowStep]:
        """Define all flow steps with their properties."""
        return {
            FlowStep.WELCOME: UIFlowStep(
                step_id=FlowStep.WELCOME,
                title="Welcome to Hearthlink",
                description="Let's configure your AI companions to work perfectly for you",
                duration_estimate=60,
                required=True,
                ui_elements=["welcome_message", "accessibility_toggle", "continue_button"],
                accessibility_features=["screen_reader", "keyboard_navigation", "high_contrast"],
                fallback_options=["skip_accessibility", "minimal_setup"]
            ),
            FlowStep.AUDIO_CHECK: UIFlowStep(
                step_id=FlowStep.AUDIO_CHECK,
                title="Audio System Check",
                description="Checking your audio devices and system compatibility",
                duration_estimate=120,
                required=True,
                ui_elements=["progress_bar", "device_list", "test_buttons", "status_indicators"],
                accessibility_features=["audio_announcements", "visual_indicators", "error_descriptions"],
                fallback_options=["skip_audio", "text_only_mode", "manual_setup"]
            ),
            FlowStep.VOICE_PREFERENCES: UIFlowStep(
                step_id=FlowStep.VOICE_PREFERENCES,
                title="Voice Preferences",
                description="Choose how your AI companions will speak to you",
                duration_estimate=180,
                required=True,
                ui_elements=["voice_samples", "preference_sliders", "preview_buttons", "persona_cards"],
                accessibility_features=["voice_preview", "descriptive_labels", "keyboard_shortcuts"],
                fallback_options=["default_voices", "minimal_voice", "text_only"]
            ),
            FlowStep.MICROPHONE_TEST: UIFlowStep(
                step_id=FlowStep.MICROPHONE_TEST,
                title="Microphone Test",
                description="Test your microphone to ensure voice interaction works",
                duration_estimate=90,
                required=False,
                ui_elements=["mic_visualizer", "record_button", "playback_controls", "volume_meter"],
                accessibility_features=["audio_feedback", "visual_indicators", "voice_guidance"],
                fallback_options=["skip_microphone", "manual_test", "assume_working"]
            ),
            FlowStep.PERSONA_CONFIG: UIFlowStep(
                step_id=FlowStep.PERSONA_CONFIG,
                title="Persona Configuration",
                description="Customize each AI companion's personality and behavior",
                duration_estimate=300,
                required=False,
                ui_elements=["persona_grid", "config_panels", "preview_buttons", "reset_options"],
                accessibility_features=["persona_descriptions", "config_announcements", "navigation_help"],
                fallback_options=["default_configs", "skip_customization", "basic_setup"]
            ),
            FlowStep.INTERACTION_SETUP: UIFlowStep(
                step_id=FlowStep.INTERACTION_SETUP,
                title="Interaction Preferences",
                description="Set up how you want to interact with your AI companions",
                duration_estimate=120,
                required=True,
                ui_elements=["interaction_options", "notification_settings", "adaptation_sliders"],
                accessibility_features=["option_descriptions", "setting_announcements", "help_text"],
                fallback_options=["default_interactions", "minimal_settings", "basic_preferences"]
            ),
            FlowStep.COMPLETION: UIFlowStep(
                step_id=FlowStep.COMPLETION,
                title="Configuration Complete",
                description="Your AI companions are ready to help you",
                duration_estimate=30,
                required=True,
                ui_elements=["success_message", "summary_display", "launch_button", "help_links"],
                accessibility_features=["completion_announcement", "summary_readout", "navigation_help"],
                fallback_options=["minimal_completion", "skip_summary", "direct_launch"]
            )
        }
    
    def _define_prompts(self) -> Dict[str, UIPrompt]:
        """Define all UI prompts with their properties."""
        return {
            "welcome_accessibility": UIPrompt(
                prompt_id="welcome_accessibility",
                title="Accessibility Setup",
                message="Would you like to enable accessibility features for a better experience?",
                options=["Yes, enable accessibility", "No, standard mode", "Tell me more"],
                default_option="Yes, enable accessibility",
                help_text="Accessibility features include screen reader support, keyboard navigation, and voice guidance.",
                accessibility_announcement="Accessibility setup screen. Choose whether to enable accessibility features."
            ),
            "voice_style_selection": UIPrompt(
                prompt_id="voice_style_selection",
                title="Voice Style",
                message="How would you like your AI companions to speak?",
                options=[
                    "Warm & Gentle - Calm and empathetic",
                    "Clear & Professional - Clear and organized", 
                    "Enthusiastic & Friendly - Energetic and positive",
                    "Calm & Reassuring - Steady and reliable",
                    "Efficient & Direct - Quick and focused"
                ],
                default_option="Warm & Gentle - Calm and empathetic",
                help_text="You can change this later in settings. Each style has different characteristics.",
                accessibility_announcement="Voice style selection. Choose how your AI companions will speak to you."
            ),
            "microphone_test_consent": UIPrompt(
                prompt_id="microphone_test_consent",
                title="Microphone Test",
                message="Would you like to test your microphone? This helps ensure voice interaction works properly.",
                options=["Yes, test microphone", "Skip microphone test", "Test later"],
                default_option="Yes, test microphone",
                help_text="The test will record a short audio sample to verify your microphone is working.",
                accessibility_announcement="Microphone test consent. Choose whether to test your microphone."
            ),
            "persona_customization": UIPrompt(
                prompt_id="persona_customization",
                title="Persona Customization",
                message="Would you like to customize each AI companion individually?",
                options=["Yes, customize each", "Use default settings", "Customize some"],
                default_option="Use default settings",
                help_text="Individual customization allows you to set different voices and behaviors for each companion.",
                accessibility_announcement="Persona customization choice. Choose whether to customize each AI companion."
            ),
            "interaction_level": UIPrompt(
                prompt_id="interaction_level",
                title="Interaction Level",
                message="How would you like your AI companions to interact with you?",
                options=[
                    "Conversational - Natural and chatty",
                    "Efficient - Quick and focused",
                    "Detailed - Thorough and comprehensive",
                    "Minimal - Brief and essential only",
                    "Adaptive - Changes based on context"
                ],
                default_option="Adaptive - Changes based on context",
                help_text="This affects how your companions respond and communicate with you.",
                accessibility_announcement="Interaction level selection. Choose how your AI companions should interact."
            )
        }
    
    def _run_welcome_step(self) -> Dict[str, Any]:
        """Run the welcome step."""
        try:
            step = self.flow_steps[FlowStep.WELCOME]
            self._display_step_header(step)
            
            # Display welcome message
            self._display_welcome_message()
            
            # Check accessibility preferences
            accessibility_result = self._handle_accessibility_setup()
            self.accessibility_enabled = accessibility_result.get('enabled', False)
            
            # Store user response
            self.user_responses['accessibility_enabled'] = self.accessibility_enabled
            
            self.completed_steps.add(FlowStep.WELCOME)
            
            return {
                "success": True,
                "accessibility_enabled": self.accessibility_enabled,
                "user_choice": accessibility_result.get('choice', 'default')
            }
            
        except Exception as e:
            self._log("welcome_step_failed", "system", None, "ui_flow", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _run_audio_check_step(self) -> Dict[str, Any]:
        """Run the audio check step."""
        try:
            step = self.flow_steps[FlowStep.AUDIO_CHECK]
            self._display_step_header(step)
            
            # Simulate audio system check
            self._display_progress("Checking audio system...", 0)
            time.sleep(1)
            
            self._display_progress("Detecting audio devices...", 25)
            time.sleep(1)
            
            self._display_progress("Testing audio output...", 50)
            time.sleep(1)
            
            self._display_progress("Testing audio input...", 75)
            time.sleep(1)
            
            self._display_progress("Audio check complete!", 100)
            
            # Simulate device detection results
            devices = {
                "output": ["Default Speakers", "Built-in Speakers"],
                "input": ["Default Microphone", "Built-in Microphone"]
            }
            
            self._display_audio_results(devices)
            
            self.completed_steps.add(FlowStep.AUDIO_CHECK)
            
            return {
                "success": True,
                "devices_found": devices,
                "audio_working": True
            }
            
        except Exception as e:
            self._log("audio_check_step_failed", "system", None, "ui_flow", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _run_voice_preferences_step(self) -> Dict[str, Any]:
        """Run the voice preferences step."""
        try:
            step = self.flow_steps[FlowStep.VOICE_PREFERENCES]
            self._display_step_header(step)
            
            # Get voice style preference
            voice_prompt = self.prompts["voice_style_selection"]
            voice_choice = self._display_prompt(voice_prompt)
            
            # Store user response
            self.user_responses['voice_style'] = voice_choice
            
            # Display voice preview (simulated)
            self._display_voice_preview(voice_choice)
            
            self.completed_steps.add(FlowStep.VOICE_PREFERENCES)
            
            return {
                "success": True,
                "voice_style": voice_choice,
                "preview_played": True
            }
            
        except Exception as e:
            self._log("voice_preferences_step_failed", "system", None, "ui_flow", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _run_microphone_test_step(self) -> Dict[str, Any]:
        """Run the microphone test step."""
        try:
            step = self.flow_steps[FlowStep.MICROPHONE_TEST]
            self._display_step_header(step)
            
            # Check if user wants to test microphone
            mic_prompt = self.prompts["microphone_test_consent"]
            mic_choice = self._display_prompt(mic_prompt)
            
            if mic_choice == "Skip microphone test":
                self.user_responses['microphone_skipped'] = True
                return {"success": True, "microphone_skipped": True}
            
            # Simulate microphone test
            self._display_microphone_test()
            
            # Simulate test results
            test_result = {
                "success": True,
                "volume_level": 0.8,
                "clarity": "good",
                "background_noise": "low"
            }
            
            self._display_microphone_results(test_result)
            
            self.user_responses['microphone_test'] = test_result
            self.completed_steps.add(FlowStep.MICROPHONE_TEST)
            
            return {
                "success": True,
                "test_result": test_result
            }
            
        except Exception as e:
            self._log("microphone_test_step_failed", "system", None, "ui_flow", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _run_persona_config_step(self) -> Dict[str, Any]:
        """Run the persona configuration step."""
        try:
            step = self.flow_steps[FlowStep.PERSONA_CONFIG]
            self._display_step_header(step)
            
            # Check if user wants individual customization
            persona_prompt = self.prompts["persona_customization"]
            persona_choice = self._display_prompt(persona_prompt)
            
            if persona_choice == "Use default settings":
                self.user_responses['persona_customization'] = "default"
                return {"success": True, "customization": "default"}
            
            # Simulate individual persona configuration
            personas = ["Alden", "Sentry", "Alice", "Mimic", "Core", "Vault", "Synapse"]
            persona_configs = {}
            
            for persona in personas:
                config = self._configure_single_persona_ui(persona)
                persona_configs[persona] = config
            
            self.user_responses['persona_configs'] = persona_configs
            self.completed_steps.add(FlowStep.PERSONA_CONFIG)
            
            return {
                "success": True,
                "personas_configured": len(persona_configs),
                "configs": persona_configs
            }
            
        except Exception as e:
            self._log("persona_config_step_failed", "system", None, "ui_flow", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _run_interaction_setup_step(self) -> Dict[str, Any]:
        """Run the interaction setup step."""
        try:
            step = self.flow_steps[FlowStep.INTERACTION_SETUP]
            self._display_step_header(step)
            
            # Get interaction level preference
            interaction_prompt = self.prompts["interaction_level"]
            interaction_choice = self._display_prompt(interaction_prompt)
            
            # Get notification preferences
            notification_choice = self._get_notification_preferences()
            
            # Get adaptation preferences
            adaptation_choice = self._get_adaptation_preferences()
            
            interaction_config = {
                "interaction_level": interaction_choice,
                "notifications": notification_choice,
                "adaptation": adaptation_choice
            }
            
            self.user_responses['interaction_config'] = interaction_config
            self.completed_steps.add(FlowStep.INTERACTION_SETUP)
            
            return {
                "success": True,
                "interaction_config": interaction_config
            }
            
        except Exception as e:
            self._log("interaction_setup_step_failed", "system", None, "ui_flow", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _run_completion_step(self) -> Dict[str, Any]:
        """Run the completion step."""
        try:
            step = self.flow_steps[FlowStep.COMPLETION]
            self._display_step_header(step)
            
            # Display completion message
            self._display_completion_message()
            
            # Display configuration summary
            self._display_configuration_summary()
            
            self.completed_steps.add(FlowStep.COMPLETION)
            
            return {
                "success": True,
                "configuration_complete": True
            }
            
        except Exception as e:
            self._log("completion_step_failed", "system", None, "ui_flow", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    # UI Display Methods (CLI Implementation)
    def _display_step_header(self, step: UIFlowStep) -> None:
        """Display step header."""
        print(f"\n{'='*60}")
        print(f"📋 {step.title}")
        print(f"{'='*60}")
        print(f"{step.description}")
        print(f"Estimated time: {step.duration_estimate} seconds")
        
        if self.accessibility_enabled:
            print("♿ Accessibility features enabled")
    
    def _display_welcome_message(self) -> None:
        """Display welcome message."""
        print("\n🎉 Welcome to Hearthlink!")
        print("Your AI companions are ready to meet you.")
        print("\nThis setup will help us configure your experience to be:")
        print("• Comfortable and accessible")
        print("• Personalized to your preferences")
        print("• Optimized for your system")
        print("• Ready for immediate use")
    
    def _handle_accessibility_setup(self) -> Dict[str, Any]:
        """Handle accessibility setup."""
        prompt = self.prompts["welcome_accessibility"]
        choice = self._display_prompt(prompt)
        
        enabled = choice.startswith("Yes")
        
        if enabled:
            print("\n♿ Accessibility features enabled:")
            print("• Screen reader support")
            print("• Keyboard navigation")
            print("• Voice guidance")
            print("• High contrast options")
        
        return {
            "enabled": enabled,
            "choice": choice
        }
    
    def _display_progress(self, message: str, percentage: int) -> None:
        """Display progress bar."""
        bar_length = 40
        filled_length = int(bar_length * percentage // 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"\r{message} [{bar}] {percentage}%", end='', flush=True)
        
        if percentage == 100:
            print()  # New line when complete
    
    def _display_audio_results(self, devices: Dict[str, List[str]]) -> None:
        """Display audio check results."""
        print("\n✅ Audio System Check Complete!")
        print(f"\nOutput devices found: {len(devices['output'])}")
        for device in devices['output']:
            print(f"  • {device}")
        
        print(f"\nInput devices found: {len(devices['input'])}")
        for device in devices['input']:
            print(f"  • {device}")
    
    def _display_prompt(self, prompt: UIPrompt) -> str:
        """Display a prompt and get user response."""
        print(f"\n{prompt.title}")
        print(f"{prompt.message}")
        
        if prompt.help_text:
            print(f"\n💡 {prompt.help_text}")
        
        print("\nOptions:")
        for i, option in enumerate(prompt.options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = input(f"\nChoose option (1-{len(prompt.options)}): ").strip()
                choice_num = int(choice)
                if 1 <= choice_num <= len(prompt.options):
                    return prompt.options[choice_num - 1]
                else:
                    print(f"Please choose 1-{len(prompt.options)}")
            except (ValueError, KeyboardInterrupt):
                if prompt.default_option:
                    print(f"Using default: {prompt.default_option}")
                    return prompt.default_option
                else:
                    print("Please enter a valid choice")
    
    def _display_voice_preview(self, voice_style: str) -> None:
        """Display voice preview (simulated)."""
        print(f"\n🎤 Voice Preview: {voice_style}")
        print("Playing voice sample... (simulated)")
        time.sleep(2)
        print("✅ Voice preview complete!")
    
    def _display_microphone_test(self) -> None:
        """Display microphone test interface."""
        print("\n🎙️  Microphone Test")
        print("Please speak for 3 seconds when prompted...")
        input("Press Enter when ready to record...")
        
        print("Recording... (simulated)")
        for i in range(3, 0, -1):
            print(f"  {i}...", end='', flush=True)
            time.sleep(1)
        print("\nRecording complete!")
    
    def _display_microphone_results(self, results: Dict[str, Any]) -> None:
        """Display microphone test results."""
        print("\n✅ Microphone Test Results:")
        print(f"  • Volume Level: {results['volume_level']:.1f}")
        print(f"  • Clarity: {results['clarity']}")
        print(f"  • Background Noise: {results['background_noise']}")
    
    def _configure_single_persona_ui(self, persona_name: str) -> Dict[str, Any]:
        """Configure a single persona via UI."""
        print(f"\n🤖 Configuring {persona_name}...")
        
        # Simulate configuration options
        config = {
            "voice_style": "default",
            "interaction_style": "adaptive",
            "volume": 0.8,
            "speech_rate": 1.0
        }
        
        print(f"✅ {persona_name} configured with default settings")
        return config
    
    def _get_notification_preferences(self) -> str:
        """Get notification preferences."""
        print("\n🔔 Notification Preferences:")
        print("1. Important notifications only")
        print("2. Regular updates and reminders")
        print("3. All notifications and suggestions")
        
        while True:
            try:
                choice = input("Choose notification level (1-3): ").strip()
                if choice == "1":
                    return "important_only"
                elif choice == "2":
                    return "regular_updates"
                elif choice == "3":
                    return "all_notifications"
                else:
                    print("Please choose 1-3")
            except (ValueError, KeyboardInterrupt):
                return "important_only"
    
    def _get_adaptation_preferences(self) -> str:
        """Get adaptation preferences."""
        print("\n🔄 Adaptation Preferences:")
        print("1. High - Quick adaptation to your style")
        print("2. Medium - Gradual adaptation over time")
        print("3. Low - Minimal adaptation, consistent behavior")
        
        while True:
            try:
                choice = input("Choose adaptation level (1-3): ").strip()
                if choice == "1":
                    return "high"
                elif choice == "2":
                    return "medium"
                elif choice == "3":
                    return "low"
                else:
                    print("Please choose 1-3")
            except (ValueError, KeyboardInterrupt):
                return "medium"
    
    def _display_completion_message(self) -> None:
        """Display completion message."""
        print("\n🎉 Configuration Complete!")
        print("Your AI companions are ready to help you.")
        print("\nWhat's next:")
        print("• Launch Hearthlink to start using your companions")
        print("• Explore the documentation for detailed guides")
        print("• Customize settings further in the preferences")
    
    def _display_configuration_summary(self) -> None:
        """Display configuration summary."""
        print("\n📋 Configuration Summary:")
        print(f"  • Steps completed: {len(self.completed_steps)}")
        print(f"  • Accessibility: {'Enabled' if self.accessibility_enabled else 'Disabled'}")
        print(f"  • Voice style: {self.user_responses.get('voice_style', 'Default')}")
        print(f"  • Microphone: {'Tested' if 'microphone_test' in self.user_responses else 'Skipped'}")
        print(f"  • Personas: {'Customized' if 'persona_configs' in self.user_responses else 'Default settings'}")
    
    def _handle_audio_failure(self, audio_result: Dict[str, Any]) -> None:
        """Handle audio system failure."""
        print("\n⚠️  Audio system check failed")
        print("Continuing with fallback mode...")
        print("• Voice features will be disabled")
        print("• Text-only mode will be used")
        print("• You can enable audio later in settings")
    
    def _handle_microphone_failure(self, mic_result: Dict[str, Any]) -> None:
        """Handle microphone test failure."""
        print("\n⚠️  Microphone test failed")
        print("Continuing without voice input...")
        print("• Voice commands will be disabled")
        print("• Text input will be used instead")
        print("• You can test microphone later in settings")
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log UI flow events."""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"UI Flows: {action} - {result}")
        
        if error:
            self.logger.error(f"UI Flows error: {str(error)}") 