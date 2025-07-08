"""
Installation UX - Main Orchestrator

Coordinates the complete installation and onboarding experience,
including persona introductions, accessibility features, and system checks.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

from .persona_introducer import PersonaIntroducer
from .accessibility_manager import AccessibilityManager
from .av_compatibility_checker import AVCompatibilityChecker
from .audio_system_checker import AudioSystemChecker
from .config_wizard import FirstRunConfigWizard

@dataclass
class InstallationResult:
    """Result of installation process."""
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    installation_path: Optional[str] = None
    config_path: Optional[str] = None
    completion_time: Optional[datetime] = None

@dataclass
class PersonaIntro:
    """Persona introduction data."""
    name: str
    title: str
    description: str
    voice_message: str
    animation_type: str
    image_path: Optional[str] = None

class InstallationUX:
    """
    Main orchestrator for Hearthlink installation and onboarding experience.
    
    Provides a delightful, accessible, and emotionally resonant installation
    process that introduces users to their AI companions and configures
    the system according to their preferences.
    """
    
    def __init__(self, config: Dict[str, Any] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize Installation UX system.
        
        Args:
            config: Configuration dictionary
            logger: Optional logger instance
        """
        self.config = config or {}
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.persona_introducer = PersonaIntroducer(self.logger)
        self.accessibility_manager = AccessibilityManager(self.logger)
        self.av_checker = AVCompatibilityChecker(self.logger)
        self.audio_checker = AudioSystemChecker(self.logger)
        self.config_wizard = FirstRunConfigWizard(self.logger)
        
        # Installation state
        self.installation_path = None
        self.user_preferences = {}
        self.installation_log = []
        
        self._log("installation_ux_initialized", "system", None, "system", None, {})
    
    def run_installation(self) -> InstallationResult:
        """
        Run the complete installation and onboarding process.
        
        Returns:
            InstallationResult with success status and details
        """
        try:
            self._log("installation_started", "system", None, "installation", {})
            
            # Step 1: Welcome and accessibility preferences
            self._log("step_1_started", "system", None, "installation", {"step": "welcome"})
            if not self._show_welcome_screen():
                return InstallationResult(success=False, errors=["User cancelled at welcome screen"])
            
            # Step 2: System compatibility check
            self._log("step_2_started", "system", None, "installation", {"step": "compatibility"})
            compatibility_result = self._check_system_compatibility()
            if not compatibility_result.get("compatible", False):
                return InstallationResult(
                    success=False, 
                    errors=[f"System compatibility check failed: {compatibility_result.get('reason', 'Unknown')}"]
                )
            
            # Step 2.5: Audio system check (new step)
            self._log("step_2_5_started", "system", None, "installation", {"step": "audio_check"})
            audio_result = self._check_audio_system()
            if not audio_result.get("overall_success", False):
                self._log("audio_warning", "system", None, "installation", 
                         {"warning": "Audio system check failed or incomplete"})
            
            # Step 3: AV compatibility check and resolution
            self._log("step_3_started", "system", None, "installation", {"step": "av_check"})
            av_result = self._handle_av_compatibility()
            if not av_result.get("resolved", False):
                self._log("av_warning", "system", None, "installation", 
                         {"warning": "AV compatibility not fully resolved"})
            
            # Step 4: Persona introductions
            self._log("step_4_started", "system", None, "installation", {"step": "personas"})
            if not self.user_preferences.get("skip_personas", False):
                if not self._introduce_personas():
                    return InstallationResult(success=False, errors=["Persona introduction failed"])
            
            # Step 5: First-time configuration
            self._log("step_5_started", "system", None, "installation", {"step": "configuration"})
            config_result = self._run_first_time_configuration()
            if not config_result.get("success", False):
                return InstallationResult(
                    success=False, 
                    errors=[f"Configuration failed: {config_result.get('error', 'Unknown')}"]
                )
            
            # Step 6: Complete installation
            self._log("step_6_started", "system", None, "installation", {"step": "completion"})
            completion_result = self._complete_installation()
            if not completion_result.get("success", False):
                return InstallationResult(
                    success=False, 
                    errors=[f"Installation completion failed: {completion_result.get('error', 'Unknown')}"]
                )
            
            # Installation successful
            self._log("installation_completed", "system", None, "installation", {
                "installation_path": self.installation_path,
                "config_path": config_result.get("config_path")
            })
            
            return InstallationResult(
                success=True,
                installation_path=self.installation_path,
                config_path=config_result.get("config_path"),
                completion_time=datetime.now(),
                warnings=av_result.get("warnings", [])
            )
            
        except Exception as e:
            self._log("installation_failed", "system", None, "installation", {}, "error", e)
            return InstallationResult(success=False, errors=[f"Installation failed: {str(e)}"])
    
    def _show_welcome_screen(self) -> bool:
        """Show welcome screen and collect accessibility preferences."""
        try:
            # In CLI mode, show welcome message
            print("\n" + "="*60)
            print("🎉 Welcome to Hearthlink! 🎉")
            print("="*60)
            print("Your AI companions are ready to meet you.")
            print("\nLet's make sure your experience is comfortable and accessible.")
            
            # Collect accessibility preferences
            preferences = self._collect_accessibility_preferences()
            self.user_preferences.update(preferences)
            
            # Configure accessibility manager
            self.accessibility_manager.configure_from_preferences(preferences)
            
            return True
            
        except Exception as e:
            self._log("welcome_screen_failed", "system", None, "installation", {}, "error", e)
            return False
    
    def _collect_accessibility_preferences(self) -> Dict[str, Any]:
        """Collect accessibility preferences from user."""
        preferences = {}
        
        print("\nAccessibility Preferences:")
        print("1. Enable voiceover narration? (y/n): ", end="")
        preferences["voiceover"] = input().lower().startswith('y')
        
        print("2. Reduce animations? (y/n): ", end="")
        preferences["reduce_animations"] = input().lower().startswith('y')
        
        print("3. High contrast mode? (y/n): ", end="")
        preferences["high_contrast"] = input().lower().startswith('y')
        
        print("4. Large text? (y/n): ", end="")
        preferences["large_text"] = input().lower().startswith('y')
        
        print("5. Skip persona introductions? (y/n): ", end="")
        preferences["skip_personas"] = input().lower().startswith('y')
        
        return preferences
    
    def _check_system_compatibility(self) -> Dict[str, Any]:
        """Check system compatibility requirements."""
        try:
            # Check Python version
            if sys.version_info < (3, 8):
                return {"compatible": False, "reason": "Python 3.8 or higher required"}
            
            # Check available disk space (minimum 500MB)
            disk_usage = self._check_disk_space()
            if disk_usage < 500 * 1024 * 1024:  # 500MB in bytes
                return {"compatible": False, "reason": "Insufficient disk space (500MB required)"}
            
            # Check required dependencies
            missing_deps = self._check_required_dependencies()
            if missing_deps:
                return {"compatible": False, "reason": f"Missing dependencies: {', '.join(missing_deps)}"}
            
            return {"compatible": True}
            
        except Exception as e:
            self._log("compatibility_check_failed", "system", None, "installation", {}, "error", e)
            return {"compatible": False, "reason": f"Compatibility check failed: {str(e)}"}
    
    def _check_disk_space(self) -> int:
        """Check available disk space in bytes."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            return free
        except Exception:
            return 0
    
    def _check_required_dependencies(self) -> List[str]:
        """Check for required Python dependencies."""
        required_deps = [
            "cryptography",
            "requests", 
            "psutil",
            "pyttsx3"  # For voice synthesis
        ]
        
        missing = []
        for dep in required_deps:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        return missing
    
    def _handle_av_compatibility(self) -> Dict[str, Any]:
        """Handle antivirus compatibility checking and resolution."""
        try:
            print("\n🛡️  Antivirus Compatibility Check")
            print("=" * 40)
            
            # Check for AV software
            detected_av = self.av_checker.check_all_av_software()
            
            if not detected_av:
                print("✅ No antivirus software detected - proceeding normally.")
                return {"resolved": True, "warnings": []}
            
            print(f"⚠️  Detected {len(detected_av)} antivirus software:")
            for av in detected_av:
                print(f"   • {av.name}")
            
            # Provide exclusion instructions
            print("\n📋 To ensure smooth operation, please add Hearthlink to your antivirus exclusions:")
            
            for av in detected_av:
                print(f"\n{av.name} Instructions:")
                instructions = self.av_checker.generate_exclusion_instructions(av.name)
                for instruction in instructions:
                    print(f"   {instruction}")
            
            print("\nPress Enter when you've completed the exclusions, or 's' to skip: ", end="")
            user_input = input().lower().strip()
            
            if user_input == 's':
                return {"resolved": False, "warnings": ["AV exclusions skipped - may cause issues"]}
            
            return {"resolved": True, "warnings": []}
            
        except Exception as e:
            self._log("av_compatibility_failed", "system", None, "installation", {}, "error", e)
            return {"resolved": False, "warnings": [f"AV check failed: {str(e)}"]}
    
    def _check_audio_system(self) -> Dict[str, Any]:
        """Check audio system compatibility and configuration."""
        try:
            print("\n🎵 Audio System Check")
            print("=" * 30)
            print("Let's make sure your audio is working properly for voice interactions.")
            
            # Run comprehensive audio check
            audio_results = self.audio_checker.run_comprehensive_audio_check()
            
            # Display results
            print(f"\n📊 Audio Check Results:")
            
            # Microphone results
            mic_result = audio_results["microphone"]
            if mic_result.success:
                print(f"✅ Microphone: Working ({mic_result.details.get('quality_score', 0):.1%} quality)")
            else:
                print(f"❌ Microphone: {mic_result.error_message or 'Failed'}")
            
            # Speaker results
            speaker_result = audio_results["speaker"]
            if speaker_result.success:
                print(f"✅ Speakers: Working")
            else:
                print(f"❌ Speakers: {speaker_result.error_message or 'Failed'}")
            
            # Voice synthesis results
            tts_result = audio_results["voice_synthesis"]
            if tts_result.success:
                print(f"✅ Voice Synthesis: Working ({', '.join(tts_result.details.get('available_methods', []))})")
            else:
                print(f"⚠️  Voice Synthesis: {tts_result.error_message or 'Limited'}")
            
            # Display recommendations
            if audio_results.get("recommendations"):
                print(f"\n💡 Recommendations:")
                for rec in audio_results["recommendations"]:
                    print(f"   • {rec}")
            
            # Store audio configuration
            self.user_preferences["audio_config"] = audio_results
            
            return audio_results
            
        except Exception as e:
            self._log("audio_check_failed", "system", None, "installation", {}, "error", e)
            return {"overall_success": False, "error": str(e)}
    
    def _introduce_personas(self) -> bool:
        """Introduce all core personas to the user."""
        try:
            print("\n" + "="*60)
            print("🤖 Meet Your AI Companions")
            print("="*60)
            
            personas = self.persona_introducer.get_all_personas()
            
            for persona in personas:
                print(f"\n{persona.name} - {persona.title}")
                print("-" * 40)
                print(persona.description)
                
                # Play voice introduction if enabled
                if self.user_preferences.get("voiceover", False):
                    self.persona_introducer.play_intro_voice(persona.name, persona.voice_message)
                
                # Show animation if enabled
                if not self.user_preferences.get("reduce_animations", False):
                    self.persona_introducer.show_persona_animation(persona.name, persona.animation_type)
                
                # Wait for user to continue
                input("\nPress Enter to continue...")
            
            print("\n" + "="*60)
            print("🌟 Together, we're your Hearthlink team!")
            print("We're here to support you, protect you, and help you achieve your goals.")
            print("="*60)
            
            return True
            
        except Exception as e:
            self._log("persona_introduction_failed", "system", None, "installation", {}, "error", e)
            return False
    
    def _run_first_time_configuration(self) -> Dict[str, Any]:
        """Run first-time configuration wizard."""
        try:
            print("\n" + "="*60)
            print("⚙️  First-Time Configuration")
            print("="*60)
            
            config_result = self.config_wizard.run_configuration()
            
            if config_result.get("success", False):
                self.installation_path = config_result.get("installation_path")
                self.user_preferences.update(config_result.get("user_preferences", {}))
            
            return config_result
            
        except Exception as e:
            self._log("configuration_failed", "system", None, "installation", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _complete_installation(self) -> Dict[str, Any]:
        """Complete the installation process."""
        try:
            # Create installation directory if needed
            if self.installation_path:
                Path(self.installation_path).mkdir(parents=True, exist_ok=True)
            
            # Save user preferences
            config_path = os.path.join(self.installation_path or ".", "user_preferences.json")
            with open(config_path, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
            
            # Create installation log
            log_path = os.path.join(self.installation_path or ".", "installation_log.json")
            with open(log_path, 'w') as f:
                json.dump(self.installation_log, f, indent=2)
            
            print("\n" + "="*60)
            print("🎉 Installation Complete!")
            print("="*60)
            print("Welcome to Hearthlink!")
            print("Your AI companions are ready to help you.")
            print("\nConfiguration saved to:", config_path)
            print("="*60)
            
            return {
                "success": True,
                "config_path": config_path,
                "log_path": log_path
            }
            
        except Exception as e:
            self._log("completion_failed", "system", None, "installation", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log installation events with audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.installation_log.append(log_entry)
        self.logger.info(f"Installation UX: {action} - {result}")
        
        if error:
            self.logger.error(f"Installation UX error: {str(error)}")
    
    def _check_audio_system(self) -> Dict[str, Any]:
        """Check audio system compatibility and configuration."""
        try:
            print("\n🎵 Audio System Check")
            print("=" * 30)
            print("Let's make sure your audio is working properly for voice interactions.")
            
            # Run comprehensive audio check
            audio_results = self.audio_checker.run_comprehensive_audio_check()
            
            # Display results
            print(f"\n📊 Audio Check Results:")
            
            # Microphone results
            mic_result = audio_results["microphone"]
            if mic_result.success:
                print(f"✅ Microphone: Working ({mic_result.details.get('quality_score', 0):.1%} quality)")
            else:
                print(f"❌ Microphone: {mic_result.error_message or 'Failed'}")
            
            # Speaker results
            speaker_result = audio_results["speaker"]
            if speaker_result.success:
                print(f"✅ Speakers: Working")
            else:
                print(f"❌ Speakers: {speaker_result.error_message or 'Failed'}")
            
            # Voice synthesis results
            tts_result = audio_results["voice_synthesis"]
            if tts_result.success:
                print(f"✅ Voice Synthesis: Working ({', '.join(tts_result.details.get('available_methods', []))})")
            else:
                print(f"⚠️  Voice Synthesis: {tts_result.error_message or 'Limited'}")
            
            # Display recommendations
            if audio_results.get("recommendations"):
                print(f"\n💡 Recommendations:")
                for rec in audio_results["recommendations"]:
                    print(f"   • {rec}")
            
            # Store audio configuration
            self.user_preferences["audio_config"] = audio_results
            
            return audio_results
            
        except Exception as e:
            self._log("audio_check_failed", "system", None, "installation", {}, "error", e)
            return {"overall_success": False, "error": str(e)} 