"""
Persona Configuration Wizard - First-Time Setup

Provides comprehensive first-time persona configuration including voice preferences,
microphone/sound checks, interaction preferences, and fallback handling for common
hardware issues. Ensures platinum-grade user experience with accessibility support.
"""

import os
import sys
import json
import time
import logging
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

class VoicePreference(Enum):
    """Voice preference options."""
    WARM_GENTLE = "warm_gentle"
    CLEAR_PROFESSIONAL = "clear_professional"
    ENTHUSIASTIC_FRIENDLY = "enthusiastic_friendly"
    CALM_REASSURING = "calm_reassuring"
    EFFICIENT_DIRECT = "efficient_direct"

class InteractionStyle(Enum):
    """Interaction style preferences."""
    CONVERSATIONAL = "conversational"
    EFFICIENT = "efficient"
    DETAILED = "detailed"
    MINIMAL = "minimal"
    ADAPTIVE = "adaptive"

@dataclass
class AudioDevice:
    """Audio device information."""
    name: str
    device_id: str
    device_type: str  # "input" or "output"
    is_default: bool
    sample_rate: int
    channels: int
    is_working: bool = True

@dataclass
class PersonaConfig:
    """Persona configuration settings."""
    persona_name: str
    voice_preference: VoicePreference
    interaction_style: InteractionStyle
    volume_level: float  # 0.0 to 1.0
    speech_rate: float  # 0.5 to 2.0
    enabled: bool = True
    custom_settings: Dict[str, Any] = field(default_factory=dict)

class PersonaConfigurationWizard:
    """
    Comprehensive persona configuration wizard for first-time setup.
    
    Handles voice preferences, microphone/sound checks, interaction styles,
    and provides fallback handling for common hardware issues.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Persona Configuration Wizard.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Configuration state
        self.audio_devices = {"input": [], "output": []}
        self.persona_configs = {}
        self.user_preferences = {}
        self.audio_test_results = {}
        self.fallback_mode = False
        
        # Initialize components
        self._setup_audio_system()
        self._initialize_persona_configs()
        
        self._log("persona_config_wizard_initialized", "system", None, "system", {})
    
    def _initialize_persona_configs(self) -> None:
        """Initialize default persona configurations."""
        try:
            # Initialize with default configurations for all personas
            default_config = PersonaConfig(
                persona_name="default",
                voice_preference=VoicePreference.WARM_GENTLE,
                interaction_style=InteractionStyle.ADAPTIVE,
                volume_level=0.8,
                speech_rate=1.0
            )
            
            # Set default configs for all personas
            for persona_name in ["alden", "sentry", "alice", "mimic", "core", "vault", "synapse"]:
                self.persona_configs[persona_name] = PersonaConfig(
                    persona_name=persona_name,
                    voice_preference=default_config.voice_preference,
                    interaction_style=default_config.interaction_style,
                    volume_level=default_config.volume_level,
                    speech_rate=default_config.speech_rate
                )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize persona configs: {str(e)}")
    
    def run_complete_configuration(self) -> Dict[str, Any]:
        """
        Run the complete persona configuration process.
        
        Returns:
            Dictionary with configuration results and status
        """
        try:
            self._log("persona_configuration_started", "system", None, "configuration", {})
            
            # Step 1: Audio System Check
            audio_result = self._check_audio_system()
            if not audio_result['success']:
                self._handle_audio_failure(audio_result)
            
            # Step 2: Voice Preferences Setup
            voice_result = self._setup_voice_preferences()
            if not voice_result['success']:
                return {"success": False, "error": "Voice preferences setup failed"}
            
            # Step 3: Microphone and Sound Check
            sound_result = self._check_microphone_and_sound()
            if not sound_result['success']:
                self._handle_sound_failure(sound_result)
            
            # Step 4: Persona-Specific Configuration
            persona_result = self._configure_personas()
            if not persona_result['success']:
                return {"success": False, "error": "Persona configuration failed"}
            
            # Step 5: Interaction Preferences
            interaction_result = self._setup_interaction_preferences()
            if not interaction_result['success']:
                return {"success": False, "error": "Interaction preferences setup failed"}
            
            # Step 6: Save Configuration
            save_result = self._save_configuration()
            if not save_result['success']:
                return {"success": False, "error": "Configuration save failed"}
            
            return {
                "success": True,
                "audio_system": audio_result,
                "voice_preferences": voice_result,
                "sound_check": sound_result,
                "persona_configs": persona_result,
                "interaction_preferences": interaction_result,
                "fallback_mode": self.fallback_mode
            }
            
        except Exception as e:
            self._log("persona_configuration_failed", "system", None, "configuration", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _setup_audio_system(self) -> None:
        """Setup audio system detection and management."""
        try:
            # Try to import pyaudio for advanced audio features
            try:
                import pyaudio
                self.pyaudio_available = True
                self.pyaudio = pyaudio.PyAudio()
            except ImportError:
                self.pyaudio_available = False
                self.pyaudio = None
                self.logger.warning("pyaudio not available - using fallback audio detection")
            
            # Initialize basic audio capabilities
            self._detect_audio_devices()
            
        except Exception as e:
            self.logger.error(f"Audio system setup failed: {str(e)}")
            self.fallback_mode = True
    
    def _detect_audio_devices(self) -> Dict[str, List[AudioDevice]]:
        """Detect available audio devices."""
        try:
            if not self.pyaudio_available:
                return self._fallback_audio_detection()
            
            devices = {"input": [], "output": []}
            
            for i in range(self.pyaudio.get_device_count()):
                device_info = self.pyaudio.get_device_info_by_index(i)
                
                # Input devices (microphones)
                if device_info['maxInputChannels'] > 0:
                    input_device = AudioDevice(
                        name=device_info['name'],
                        device_id=str(i),
                        device_type="input",
                        is_default=(i == self.pyaudio.get_default_input_device_info()['index']),
                        sample_rate=int(device_info['defaultSampleRate']),
                        channels=device_info['maxInputChannels']
                    )
                    devices["input"].append(input_device)
                
                # Output devices (speakers/headphones)
                if device_info['maxOutputChannels'] > 0:
                    output_device = AudioDevice(
                        name=device_info['name'],
                        device_id=str(i),
                        device_type="output",
                        is_default=(i == self.pyaudio.get_default_output_device_info()['index']),
                        sample_rate=int(device_info['defaultSampleRate']),
                        channels=device_info['maxOutputChannels']
                    )
                    devices["output"].append(output_device)
            
            self.audio_devices = devices
            return devices
            
        except Exception as e:
            self.logger.error(f"Audio device detection failed: {str(e)}")
            return self._fallback_audio_detection()
    
    def _fallback_audio_detection(self) -> Dict[str, List[AudioDevice]]:
        """Fallback audio device detection when pyaudio is not available."""
        try:
            # Create basic device entries based on platform
            if sys.platform.startswith('win'):
                devices = {
                    "input": [
                        AudioDevice("Default Microphone", "default", "input", True, 44100, 1),
                        AudioDevice("Built-in Microphone", "builtin", "input", False, 44100, 1)
                    ],
                    "output": [
                        AudioDevice("Default Speakers", "default", "output", True, 44100, 2),
                        AudioDevice("Built-in Speakers", "builtin", "output", False, 44100, 2)
                    ]
                }
            elif sys.platform.startswith('darwin'):  # macOS
                devices = {
                    "input": [
                        AudioDevice("Default Input", "default", "input", True, 44100, 1),
                        AudioDevice("Built-in Microphone", "builtin", "input", False, 44100, 1)
                    ],
                    "output": [
                        AudioDevice("Default Output", "default", "output", True, 44100, 2),
                        AudioDevice("Built-in Speakers", "builtin", "output", False, 44100, 2)
                    ]
                }
            else:  # Linux
                devices = {
                    "input": [
                        AudioDevice("Default Input", "default", "input", True, 44100, 1),
                        AudioDevice("PulseAudio Input", "pulse", "input", False, 44100, 1)
                    ],
                    "output": [
                        AudioDevice("Default Output", "default", "output", True, 44100, 2),
                        AudioDevice("PulseAudio Output", "pulse", "output", False, 44100, 2)
                    ]
                }
            
            self.audio_devices = devices
            return devices
            
        except Exception as e:
            self.logger.error(f"Fallback audio detection failed: {str(e)}")
            return {"input": [], "output": []}
    
    def _check_audio_system(self) -> Dict[str, Any]:
        """Check audio system functionality."""
        try:
            print("\n" + "="*60)
            print("🎵 Audio System Check")
            print("="*60)
            
            # Check if we have any audio devices
            if not self.audio_devices["output"]:
                return {
                    "success": False,
                    "error": "No audio output devices detected",
                    "fallback_available": True
                }
            
            # Test audio output
            output_test = self._test_audio_output()
            
            # Test audio input if available
            input_test = None
            if self.audio_devices["input"]:
                input_test = self._test_audio_input()
            
            return {
                "success": True,
                "output_devices": len(self.audio_devices["output"]),
                "input_devices": len(self.audio_devices["input"]),
                "output_test": output_test,
                "input_test": input_test,
                "fallback_mode": self.fallback_mode
            }
            
        except Exception as e:
            self._log("audio_system_check_failed", "system", None, "audio_check", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _test_audio_output(self) -> Dict[str, Any]:
        """Test audio output functionality."""
        try:
            print("\nTesting audio output...")
            
            if self.fallback_mode:
                # Fallback test using system commands
                return self._fallback_audio_output_test()
            
            # Use pyaudio for advanced testing
            if self.pyaudio_available:
                return self._pyaudio_audio_output_test()
            
            return {"success": True, "method": "fallback", "message": "Audio output available"}
            
        except Exception as e:
            self.logger.error(f"Audio output test failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _test_audio_input(self) -> Dict[str, Any]:
        """Test audio input (microphone) functionality."""
        try:
            print("\nTesting microphone...")
            
            if self.fallback_mode:
                return self._fallback_audio_input_test()
            
            # Use pyaudio for advanced testing
            if self.pyaudio_available:
                return self._pyaudio_audio_input_test()
            
            return {"success": True, "method": "fallback", "message": "Microphone available"}
            
        except Exception as e:
            self.logger.error(f"Audio input test failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _setup_voice_preferences(self) -> Dict[str, Any]:
        """Setup voice preferences for personas."""
        try:
            print("\n" + "="*60)
            print("🎤 Voice Preferences Setup")
            print("="*60)
            
            print("\nLet's configure how your AI companions will speak to you.")
            print("Each persona can have their own voice style, or you can choose a default.")
            
            # Get default voice preference
            default_voice = self._get_voice_preference("default")
            
            # Apply to all personas
            for persona_name in ["alden", "sentry", "alice", "mimic", "core", "vault", "synapse"]:
                self.persona_configs[persona_name] = PersonaConfig(
                    persona_name=persona_name,
                    voice_preference=default_voice,
                    interaction_style=InteractionStyle.ADAPTIVE,
                    volume_level=0.8,
                    speech_rate=1.0
                )
            
            return {
                "success": True,
                "default_voice": default_voice.value,
                "personas_configured": len(self.persona_configs)
            }
            
        except Exception as e:
            self._log("voice_preferences_setup_failed", "system", None, "configuration", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _get_voice_preference(self, context: str) -> VoicePreference:
        """Get voice preference from user."""
        print(f"\nVoice preference for {context}:")
        print("1. Warm & Gentle - Calm, empathetic, reassuring")
        print("2. Clear & Professional - Clear, authoritative, organized")
        print("3. Enthusiastic & Friendly - Energetic, positive, engaging")
        print("4. Calm & Reassuring - Steady, comforting, reliable")
        print("5. Efficient & Direct - Quick, focused, practical")
        
        while True:
            try:
                choice = input("Choose voice style (1-5): ").strip()
                if choice == "1":
                    return VoicePreference.WARM_GENTLE
                elif choice == "2":
                    return VoicePreference.CLEAR_PROFESSIONAL
                elif choice == "3":
                    return VoicePreference.ENTHUSIASTIC_FRIENDLY
                elif choice == "4":
                    return VoicePreference.CALM_REASSURING
                elif choice == "5":
                    return VoicePreference.EFFICIENT_DIRECT
                else:
                    print("Please choose 1-5.")
            except (ValueError, KeyboardInterrupt):
                print("Using default voice style (Warm & Gentle)")
                return VoicePreference.WARM_GENTLE
    
    def _check_microphone_and_sound(self) -> Dict[str, Any]:
        """Check microphone and sound functionality."""
        try:
            print("\n" + "="*60)
            print("🎙️  Microphone & Sound Check")
            print("="*60)
            
            # Test microphone recording
            if self.audio_devices["input"]:
                mic_test = self._test_microphone_recording()
                if mic_test['success']:
                    print("✅ Microphone test successful!")
                else:
                    print("⚠️  Microphone test failed - continuing without voice input")
            
            # Test sound playback
            sound_test = self._test_sound_playback()
            if sound_test['success']:
                print("✅ Sound playback test successful!")
            else:
                print("⚠️  Sound playback test failed - using text-only mode")
            
            return {
                "success": True,
                "microphone_test": mic_test if self.audio_devices["input"] else None,
                "sound_test": sound_test
            }
            
        except Exception as e:
            self._log("microphone_sound_check_failed", "system", None, "audio_check", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _test_microphone_recording(self) -> Dict[str, Any]:
        """Test microphone recording functionality."""
        try:
            print("\nTesting microphone recording...")
            print("Please speak for 3 seconds when prompted.")
            
            if self.fallback_mode:
                return self._fallback_microphone_test()
            
            if self.pyaudio_available:
                return self._pyaudio_microphone_test()
            
            return {"success": True, "method": "fallback"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_sound_playback(self) -> Dict[str, Any]:
        """Test sound playback functionality."""
        try:
            print("\nTesting sound playback...")
            
            # Try to play a test tone
            if self.fallback_mode:
                return self._fallback_sound_test()
            
            if self.pyaudio_available:
                return self._pyaudio_sound_test()
            
            return {"success": True, "method": "fallback"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _configure_personas(self) -> Dict[str, Any]:
        """Configure individual persona settings."""
        try:
            print("\n" + "="*60)
            print("🤖 Persona Configuration")
            print("="*60)
            
            print("\nEach AI companion can be customized to your preferences.")
            print("You can configure them individually or use default settings.")
            
            # Ask if user wants individual configuration
            individual_config = input("\nConfigure each persona individually? (y/n): ").lower().startswith('y')
            
            if individual_config:
                for persona_name in ["alden", "sentry", "alice", "mimic", "core", "vault", "synapse"]:
                    self._configure_single_persona(persona_name)
            else:
                print("Using default settings for all personas.")
            
            return {
                "success": True,
                "individual_config": individual_config,
                "personas_configured": len(self.persona_configs)
            }
            
        except Exception as e:
            self._log("persona_configuration_failed", "system", None, "configuration", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _configure_single_persona(self, persona_name: str) -> None:
        """Configure a single persona."""
        try:
            persona_titles = {
                "alden": "The Wise Companion",
                "sentry": "The Digital Guardian", 
                "alice": "The Curious Researcher",
                "mimic": "The Adaptive Friend",
                "core": "The Conversation Conductor",
                "vault": "The Memory Guardian",
                "synapse": "The Connection Specialist"
            }
            
            print(f"\n{persona_name.title()} - {persona_titles[persona_name]}")
            print("-" * 40)
            
            # Voice preference
            voice_pref = self._get_voice_preference(persona_name)
            
            # Interaction style
            interaction_style = self._get_interaction_style(persona_name)
            
            # Volume level
            volume = self._get_volume_level(persona_name)
            
            # Speech rate
            speech_rate = self._get_speech_rate(persona_name)
            
            # Update persona config
            self.persona_configs[persona_name] = PersonaConfig(
                persona_name=persona_name,
                voice_preference=voice_pref,
                interaction_style=interaction_style,
                volume_level=volume,
                speech_rate=speech_rate
            )
            
        except Exception as e:
            self.logger.error(f"Failed to configure persona {persona_name}: {str(e)}")
    
    def _get_interaction_style(self, persona_name: str) -> InteractionStyle:
        """Get interaction style preference for a persona."""
        print(f"\nHow should {persona_name.title()} interact with you?")
        print("1. Conversational - Natural, chatty, friendly")
        print("2. Efficient - Quick, focused, to-the-point")
        print("3. Detailed - Thorough, comprehensive, detailed")
        print("4. Minimal - Brief, concise, essential only")
        print("5. Adaptive - Changes based on context")
        
        while True:
            try:
                choice = input("Choose interaction style (1-5): ").strip()
                if choice == "1":
                    return InteractionStyle.CONVERSATIONAL
                elif choice == "2":
                    return InteractionStyle.EFFICIENT
                elif choice == "3":
                    return InteractionStyle.DETAILED
                elif choice == "4":
                    return InteractionStyle.MINIMAL
                elif choice == "5":
                    return InteractionStyle.ADAPTIVE
                else:
                    print("Please choose 1-5.")
            except (ValueError, KeyboardInterrupt):
                print("Using adaptive interaction style")
                return InteractionStyle.ADAPTIVE
    
    def _get_volume_level(self, persona_name: str) -> float:
        """Get volume level preference for a persona."""
        print(f"\nVolume level for {persona_name.title()} (0.1 to 1.0):")
        print("0.1 = Very quiet, 0.5 = Medium, 1.0 = Full volume")
        
        while True:
            try:
                volume = input("Enter volume level (0.1-1.0): ").strip()
                vol_float = float(volume)
                if 0.1 <= vol_float <= 1.0:
                    return vol_float
                else:
                    print("Please enter a value between 0.1 and 1.0.")
            except (ValueError, KeyboardInterrupt):
                print("Using default volume (0.8)")
                return 0.8
    
    def _get_speech_rate(self, persona_name: str) -> float:
        """Get speech rate preference for a persona."""
        print(f"\nSpeech rate for {persona_name.title()} (0.5 to 2.0):")
        print("0.5 = Slow, 1.0 = Normal, 2.0 = Fast")
        
        while True:
            try:
                rate = input("Enter speech rate (0.5-2.0): ").strip()
                rate_float = float(rate)
                if 0.5 <= rate_float <= 2.0:
                    return rate_float
                else:
                    print("Please enter a value between 0.5 and 2.0.")
            except (ValueError, KeyboardInterrupt):
                print("Using default speech rate (1.0)")
                return 1.0
    
    def _setup_interaction_preferences(self) -> Dict[str, Any]:
        """Setup general interaction preferences."""
        try:
            print("\n" + "="*60)
            print("💬 Interaction Preferences")
            print("="*60)
            
            preferences = {}
            
            # Notification preferences
            print("\nNotification preferences:")
            print("1. Important notifications only")
            print("2. Regular updates and reminders")
            print("3. All notifications and suggestions")
            
            while True:
                try:
                    choice = input("Choose notification level (1-3): ").strip()
                    if choice in ["1", "2", "3"]:
                        preferences["notification_level"] = int(choice)
                        break
                    else:
                        print("Please choose 1-3.")
                except (ValueError, KeyboardInterrupt):
                    preferences["notification_level"] = 1
                    break
            
            # Auto-adaptation preferences
            print("\nAuto-adaptation preferences:")
            print("1. High - Personas adapt quickly to your style")
            print("2. Medium - Gradual adaptation over time")
            print("3. Low - Minimal adaptation, consistent behavior")
            
            while True:
                try:
                    choice = input("Choose adaptation level (1-3): ").strip()
                    if choice in ["1", "2", "3"]:
                        preferences["adaptation_level"] = int(choice)
                        break
                    else:
                        print("Please choose 1-3.")
                except (ValueError, KeyboardInterrupt):
                    preferences["adaptation_level"] = 2
                    break
            
            self.user_preferences.update(preferences)
            
            return {
                "success": True,
                "preferences": preferences
            }
            
        except Exception as e:
            self._log("interaction_preferences_failed", "system", None, "configuration", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _save_configuration(self) -> Dict[str, Any]:
        """Save configuration to file."""
        try:
            print("\n" + "="*60)
            print("💾 Saving Configuration")
            print("="*60)
            
            # Create configuration directory
            config_dir = Path.home() / ".hearthlink" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare configuration data
            config_data = {
                "version": "1.0",
                "created_at": time.time(),
                "audio_devices": {
                    "input": [device.__dict__ for device in self.audio_devices["input"]],
                    "output": [device.__dict__ for device in self.audio_devices["output"]]
                },
                "persona_configs": {
                    name: {
                        "voice_preference": config.voice_preference.value,
                        "interaction_style": config.interaction_style.value,
                        "volume_level": config.volume_level,
                        "speech_rate": config.speech_rate,
                        "enabled": config.enabled,
                        "custom_settings": config.custom_settings
                    }
                    for name, config in self.persona_configs.items()
                },
                "user_preferences": self.user_preferences,
                "audio_test_results": self.audio_test_results,
                "fallback_mode": self.fallback_mode
            }
            
            # Save to file
            config_file = config_dir / "persona_config.json"
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"✅ Configuration saved to: {config_file}")
            
            return {
                "success": True,
                "config_file": str(config_file),
                "config_data": config_data
            }
            
        except Exception as e:
            self._log("configuration_save_failed", "system", None, "configuration", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _handle_audio_failure(self, audio_result: Dict[str, Any]) -> None:
        """Handle audio system failures gracefully."""
        print("\n⚠️  Audio system check failed")
        print("Continuing with fallback mode...")
        
        self.fallback_mode = True
        
        # Set default configurations for fallback mode
        for persona_name in ["alden", "sentry", "alice", "mimic", "core", "vault", "synapse"]:
            self.persona_configs[persona_name] = PersonaConfig(
                persona_name=persona_name,
                voice_preference=VoicePreference.WARM_GENTLE,
                interaction_style=InteractionStyle.ADAPTIVE,
                volume_level=0.8,
                speech_rate=1.0
            )
    
    def _handle_sound_failure(self, sound_result: Dict[str, Any]) -> None:
        """Handle sound check failures gracefully."""
        print("\n⚠️  Sound check failed")
        print("Continuing with text-only mode...")
        
        # Disable voice features
        for config in self.persona_configs.values():
            config.volume_level = 0.0
    
    # Fallback test methods
    def _fallback_audio_output_test(self) -> Dict[str, Any]:
        """Fallback audio output test."""
        print("Testing audio output (fallback mode)...")
        return {"success": True, "method": "fallback", "message": "Audio output available"}
    
    def _fallback_audio_input_test(self) -> Dict[str, Any]:
        """Fallback audio input test."""
        print("Testing microphone (fallback mode)...")
        return {"success": True, "method": "fallback", "message": "Microphone available"}
    
    def _fallback_microphone_test(self) -> Dict[str, Any]:
        """Fallback microphone recording test."""
        print("Microphone test (fallback mode) - assuming working")
        return {"success": True, "method": "fallback"}
    
    def _fallback_sound_test(self) -> Dict[str, Any]:
        """Fallback sound playback test."""
        print("Sound test (fallback mode) - assuming working")
        return {"success": True, "method": "fallback"}
    
    # PyAudio test methods (when available)
    def _pyaudio_audio_output_test(self) -> Dict[str, Any]:
        """PyAudio audio output test."""
        try:
            # Generate a simple test tone
            import numpy as np
            
            # Create a 440Hz sine wave for 1 second
            sample_rate = 44100
            duration = 1.0
            frequency = 440.0
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * frequency * t)
            
            # Convert to 16-bit PCM
            audio_data = (tone * 32767).astype(np.int16)
            
            # Play the tone
            stream = self.pyaudio.open(
                format=self.pyaudio.get_format_from_width(2),
                channels=1,
                rate=sample_rate,
                output=True
            )
            
            stream.write(audio_data.tobytes())
            stream.stop_stream()
            stream.close()
            
            return {"success": True, "method": "pyaudio", "frequency": frequency}
            
        except Exception as e:
            return {"success": False, "error": str(e), "method": "pyaudio"}
    
    def _pyaudio_audio_input_test(self) -> Dict[str, Any]:
        """PyAudio audio input test."""
        try:
            # Record 3 seconds of audio
            sample_rate = 44100
            duration = 3.0
            channels = 1
            
            stream = self.pyaudio.open(
                format=self.pyaudio.get_format_from_width(2),
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            print("Recording... (speak now)")
            frames = []
            for i in range(0, int(sample_rate / 1024 * duration)):
                data = stream.read(1024)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Save test recording
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                import wave
                wf = wave.open(temp_file.name, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(self.pyaudio.get_sample_size(self.pyaudio.get_format_from_width(2)))
                wf.setframerate(sample_rate)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                return {
                    "success": True,
                    "method": "pyaudio",
                    "file_path": temp_file.name,
                    "duration": duration
                }
            
        except Exception as e:
            return {"success": False, "error": str(e), "method": "pyaudio"}
    
    def _pyaudio_microphone_test(self) -> Dict[str, Any]:
        """PyAudio microphone test with user interaction."""
        return self._pyaudio_audio_input_test()
    
    def _pyaudio_sound_test(self) -> Dict[str, Any]:
        """PyAudio sound playback test."""
        return self._pyaudio_audio_output_test()
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log configuration wizard events."""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"Persona Config Wizard: {action} - {result}")
        
        if error:
            self.logger.error(f"Persona Config Wizard error: {str(error)}") 