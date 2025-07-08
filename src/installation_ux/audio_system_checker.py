"""
Audio System Checker - Installation UX Audio Testing

Comprehensive audio input/output testing and configuration for
Hearthlink installation and onboarding experience.
"""

import os
import sys
import time
import logging
import platform
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

try:
    import pyaudio
    import wave
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

@dataclass
class AudioDevice:
    """Audio device information."""
    name: str
    device_id: int
    device_type: str  # 'input' or 'output'
    sample_rate: int
    channels: int
    is_default: bool = False

@dataclass
class AudioTestResult:
    """Result of audio system test."""
    test_name: str
    success: bool
    details: Dict[str, Any]
    error_message: Optional[str] = None
    recommendations: List[str] = None

class AudioSystemChecker:
    """
    Comprehensive audio input/output testing and configuration.
    
    Provides thorough testing of microphone access, speaker output,
    voice synthesis capabilities, and audio device configuration
    for optimal Hearthlink experience.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Audio System Checker.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.audio = None
        self.recognizer = None
        
        # Initialize audio components if available
        if AUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
            except Exception as e:
                self.logger.warning(f"PyAudio initialization failed: {e}")
        
        if STT_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
            except Exception as e:
                self.logger.warning(f"Speech recognition initialization failed: {e}")
        
        self._log("audio_checker_initialized", "system", None, "system", {
            "audio_available": AUDIO_AVAILABLE,
            "stt_available": STT_AVAILABLE,
            "platform": platform.system()
        })
    
    def run_comprehensive_audio_check(self) -> Dict[str, Any]:
        """
        Run comprehensive audio system check.
        
        Returns:
            Dictionary with all audio test results
        """
        try:
            self._log("comprehensive_audio_check_started", "system", None, "audio_check", {})
            
            results = {
                "microphone": self.check_microphone_access(),
                "speaker": self.check_speaker_output(),
                "voice_synthesis": self.test_voice_synthesis(),
                "devices": self.get_audio_devices(),
                "compatibility": self.check_audio_compatibility(),
                "recommendations": []
            }
            
            # Generate recommendations based on results
            results["recommendations"] = self._generate_recommendations(results)
            
            # Overall success determination
            critical_tests = [results["microphone"], results["speaker"]]
            results["overall_success"] = all(test.success for test in critical_tests)
            
            self._log("comprehensive_audio_check_completed", "system", None, "audio_check", {
                "overall_success": results["overall_success"],
                "test_count": len(results) - 2  # Exclude recommendations and overall_success
            })
            
            return results
            
        except Exception as e:
            self._log("comprehensive_audio_check_failed", "system", None, "audio_check", {}, "error", e)
            return {
                "overall_success": False,
                "error": str(e),
                "recommendations": ["Audio system check failed. Please check your audio hardware and drivers."]
            }
    
    def check_microphone_access(self) -> AudioTestResult:
        """
        Test microphone access and quality.
        
        Returns:
            AudioTestResult with microphone test results
        """
        try:
            if not AUDIO_AVAILABLE:
                return AudioTestResult(
                    test_name="microphone_access",
                    success=False,
                    details={"error": "PyAudio not available"},
                    error_message="Audio library not available",
                    recommendations=["Install PyAudio: pip install pyaudio"]
                )
            
            # Get default input device
            default_input = self.audio.get_default_input_device_info()
            device_info = self.audio.get_device_info(default_input['index'])
            
            # Test microphone recording
            sample_rate = int(device_info['defaultSampleRate'])
            channels = int(device_info['maxInputChannels'])
            
            # Record a short test audio
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=1024
            )
            
            print("🎤 Testing microphone... Please speak for 3 seconds.")
            frames = []
            for _ in range(0, int(sample_rate / 1024 * 3)):  # 3 seconds
                data = stream.read(1024)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            
            # Analyze audio quality
            audio_data = b''.join(frames)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Calculate audio metrics
            volume_level = np.abs(audio_array).mean()
            noise_level = np.std(audio_array)
            dynamic_range = np.max(audio_array) - np.min(audio_array)
            
            quality_score = self._calculate_audio_quality(volume_level, noise_level, dynamic_range)
            
            details = {
                "device_name": device_info['name'],
                "sample_rate": sample_rate,
                "channels": channels,
                "volume_level": float(volume_level),
                "noise_level": float(noise_level),
                "dynamic_range": float(dynamic_range),
                "quality_score": quality_score
            }
            
            success = quality_score > 0.3  # Minimum quality threshold
            
            recommendations = []
            if quality_score < 0.5:
                recommendations.append("Consider using a better microphone for optimal voice interaction")
            if volume_level < 1000:
                recommendations.append("Increase microphone volume for better voice detection")
            if noise_level > 500:
                recommendations.append("Reduce background noise for clearer voice input")
            
            return AudioTestResult(
                test_name="microphone_access",
                success=success,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return AudioTestResult(
                test_name="microphone_access",
                success=False,
                details={"error": str(e)},
                error_message=f"Microphone test failed: {str(e)}",
                recommendations=["Check microphone permissions and hardware connections"]
            )
    
    def check_speaker_output(self) -> AudioTestResult:
        """
        Test speaker output and volume levels.
        
        Returns:
            AudioTestResult with speaker test results
        """
        try:
            if not AUDIO_AVAILABLE:
                return AudioTestResult(
                    test_name="speaker_output",
                    success=False,
                    details={"error": "PyAudio not available"},
                    error_message="Audio library not available",
                    recommendations=["Install PyAudio: pip install pyaudio"]
                )
            
            # Get default output device
            default_output = self.audio.get_default_output_device_info()
            device_info = self.audio.get_device_info(default_output['index'])
            
            # Generate test tone
            sample_rate = int(device_info['defaultSampleRate'])
            channels = int(device_info['maxOutputChannels'])
            
            # Create a simple test tone (440 Hz sine wave)
            duration = 2  # seconds
            frequency = 440  # Hz
            samples = int(sample_rate * duration)
            
            # Generate sine wave
            t = np.linspace(0, duration, samples, False)
            tone = np.sin(2 * np.pi * frequency * t) * 0.3  # 30% volume
            
            # Convert to 16-bit PCM
            audio_data = (tone * 32767).astype(np.int16)
            
            # Play test tone
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                output=True
            )
            
            print("🔊 Testing speakers... You should hear a test tone.")
            stream.write(audio_data.tobytes())
            stream.stop_stream()
            stream.close()
            
            # Ask user for confirmation
            print("Did you hear the test tone clearly? (y/n): ", end="")
            user_response = input().lower().strip()
            
            success = user_response.startswith('y')
            
            details = {
                "device_name": device_info['name'],
                "sample_rate": sample_rate,
                "channels": channels,
                "user_confirmed": success
            }
            
            recommendations = []
            if not success:
                recommendations.append("Check speaker connections and volume settings")
                recommendations.append("Ensure speakers are set as default audio output")
            
            return AudioTestResult(
                test_name="speaker_output",
                success=success,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return AudioTestResult(
                test_name="speaker_output",
                success=False,
                details={"error": str(e)},
                error_message=f"Speaker test failed: {str(e)}",
                recommendations=["Check speaker hardware and audio drivers"]
            )
    
    def test_voice_synthesis(self) -> AudioTestResult:
        """
        Test voice synthesis capabilities.
        
        Returns:
            AudioTestResult with voice synthesis test results
        """
        try:
            # Test basic text-to-speech capabilities
            test_message = "Hello! I'm testing voice synthesis for Hearthlink."
            
            # Try different TTS methods
            tts_methods = []
            
            # Method 1: Platform-specific TTS
            if platform.system() == "Windows":
                try:
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    speaker.Speak(test_message)
                    tts_methods.append("Windows SAPI")
                except:
                    pass
            
            elif platform.system() == "Darwin":  # macOS
                try:
                    import subprocess
                    subprocess.run(["say", test_message], check=True)
                    tts_methods.append("macOS say")
                except:
                    pass
            
            elif platform.system() == "Linux":
                try:
                    import subprocess
                    subprocess.run(["espeak", test_message], check=True)
                    tts_methods.append("Linux espeak")
                except:
                    pass
            
            # Method 2: pyttsx3 (cross-platform)
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(test_message)
                engine.runAndWait()
                tts_methods.append("pyttsx3")
            except:
                pass
            
            success = len(tts_methods) > 0
            
            details = {
                "available_methods": tts_methods,
                "platform": platform.system(),
                "test_message": test_message
            }
            
            recommendations = []
            if not success:
                recommendations.append("Install text-to-speech library: pip install pyttsx3")
                if platform.system() == "Linux":
                    recommendations.append("Install espeak: sudo apt-get install espeak")
            
            return AudioTestResult(
                test_name="voice_synthesis",
                success=success,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return AudioTestResult(
                test_name="voice_synthesis",
                success=False,
                details={"error": str(e)},
                error_message=f"Voice synthesis test failed: {str(e)}",
                recommendations=["Check TTS library installation and system audio"]
            )
    
    def get_audio_devices(self) -> Dict[str, List[AudioDevice]]:
        """
        Get list of available audio devices.
        
        Returns:
            Dictionary with 'input' and 'output' device lists
        """
        try:
            if not AUDIO_AVAILABLE:
                return {"input": [], "output": []}
            
            devices = {"input": [], "output": []}
            
            for i in range(self.audio.get_device_count()):
                try:
                    device_info = self.audio.get_device_info(i)
                    
                    device = AudioDevice(
                        name=device_info['name'],
                        device_id=i,
                        device_type='input' if device_info['maxInputChannels'] > 0 else 'output',
                        sample_rate=int(device_info['defaultSampleRate']),
                        channels=max(device_info['maxInputChannels'], device_info['maxOutputChannels']),
                        is_default=i in [self.audio.get_default_input_device_info()['index'], 
                                       self.audio.get_default_output_device_info()['index']]
                    )
                    
                    if device.device_type == 'input':
                        devices['input'].append(device)
                    else:
                        devices['output'].append(device)
                        
                except Exception as e:
                    self.logger.warning(f"Error getting device info for device {i}: {e}")
                    continue
            
            return devices
            
        except Exception as e:
            self.logger.error(f"Error getting audio devices: {e}")
            return {"input": [], "output": []}
    
    def configure_audio_devices(self, input_device_id: Optional[int] = None, 
                               output_device_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Configure audio input/output devices.
        
        Args:
            input_device_id: Preferred input device ID
            output_device_id: Preferred output device ID
            
        Returns:
            Dictionary with configuration results
        """
        try:
            devices = self.get_audio_devices()
            
            # Validate device selections
            input_device = None
            output_device = None
            
            if input_device_id is not None:
                input_device = next((d for d in devices['input'] if d.device_id == input_device_id), None)
            
            if output_device_id is not None:
                output_device = next((d for d in devices['output'] if d.device_id == output_device_id), None)
            
            # Use defaults if not specified
            if input_device is None and devices['input']:
                input_device = next((d for d in devices['input'] if d.is_default), devices['input'][0])
            
            if output_device is None and devices['output']:
                output_device = next((d for d in devices['output'] if d.is_default), devices['output'][0])
            
            configuration = {
                "input_device": input_device.name if input_device else None,
                "output_device": output_device.name if output_device else None,
                "sample_rate": input_device.sample_rate if input_device else 44100,
                "channels": 1,  # Mono for voice
                "success": input_device is not None and output_device is not None
            }
            
            self._log("audio_devices_configured", "system", None, "audio_config", configuration)
            
            return configuration
            
        except Exception as e:
            self._log("audio_device_configuration_failed", "system", None, "audio_config", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def check_audio_compatibility(self) -> AudioTestResult:
        """
        Check overall audio system compatibility.
        
        Returns:
            AudioTestResult with compatibility assessment
        """
        try:
            compatibility_issues = []
            recommendations = []
            
            # Check platform compatibility
            platform_issues = self._check_platform_compatibility()
            if platform_issues:
                compatibility_issues.extend(platform_issues)
            
            # Check library availability
            if not AUDIO_AVAILABLE:
                compatibility_issues.append("PyAudio library not available")
                recommendations.append("Install PyAudio: pip install pyaudio")
            
            if not STT_AVAILABLE:
                compatibility_issues.append("Speech recognition library not available")
                recommendations.append("Install SpeechRecognition: pip install SpeechRecognition")
            
            # Check audio permissions
            permission_issues = self._check_audio_permissions()
            if permission_issues:
                compatibility_issues.extend(permission_issues)
            
            success = len(compatibility_issues) == 0
            
            details = {
                "platform": platform.system(),
                "audio_available": AUDIO_AVAILABLE,
                "stt_available": STT_AVAILABLE,
                "compatibility_issues": compatibility_issues
            }
            
            return AudioTestResult(
                test_name="audio_compatibility",
                success=success,
                details=details,
                recommendations=recommendations
            )
            
        except Exception as e:
            return AudioTestResult(
                test_name="audio_compatibility",
                success=False,
                details={"error": str(e)},
                error_message=f"Compatibility check failed: {str(e)}",
                recommendations=["Check system audio configuration"]
            )
    
    def _calculate_audio_quality(self, volume_level: float, noise_level: float, 
                                dynamic_range: float) -> float:
        """Calculate audio quality score from metrics."""
        # Normalize metrics to 0-1 range
        volume_score = min(volume_level / 5000, 1.0)  # Target: 5000
        noise_score = max(0, 1 - (noise_level / 1000))  # Target: <1000
        range_score = min(dynamic_range / 10000, 1.0)  # Target: 10000
        
        # Weighted average
        quality_score = (volume_score * 0.4 + noise_score * 0.4 + range_score * 0.2)
        return max(0, min(1, quality_score))
    
    def _check_platform_compatibility(self) -> List[str]:
        """Check platform-specific compatibility issues."""
        issues = []
        
        if platform.system() == "Windows":
            # Windows-specific checks
            pass
        elif platform.system() == "Darwin":
            # macOS-specific checks
            pass
        elif platform.system() == "Linux":
            # Linux-specific checks
            try:
                import subprocess
                subprocess.run(["which", "pulseaudio"], check=True, capture_output=True)
            except:
                issues.append("PulseAudio not found - may affect audio functionality")
        
        return issues
    
    def _check_audio_permissions(self) -> List[str]:
        """Check audio permissions and access."""
        issues = []
        
        # Platform-specific permission checks
        if platform.system() == "Darwin":  # macOS
            # Check microphone permissions
            try:
                import subprocess
                result = subprocess.run(["osascript", "-e", 
                                       "tell application \"System Events\" to get properties of process \"Python\""], 
                                      capture_output=True, text=True)
                if "not authorized" in result.stderr.lower():
                    issues.append("Microphone permission not granted")
            except:
                pass
        
        return issues
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Microphone recommendations
        if not results["microphone"].success:
            recommendations.extend(results["microphone"].recommendations or [])
        
        # Speaker recommendations
        if not results["speaker"].success:
            recommendations.extend(results["speaker"].recommendations or [])
        
        # Voice synthesis recommendations
        if not results["voice_synthesis"].success:
            recommendations.extend(results["voice_synthesis"].recommendations or [])
        
        # Compatibility recommendations
        if not results["compatibility"].success:
            recommendations.extend(results["compatibility"].recommendations or [])
        
        # General recommendations
        if len(results["devices"]["input"]) == 0:
            recommendations.append("No audio input devices detected - check microphone connections")
        
        if len(results["devices"]["output"]) == 0:
            recommendations.append("No audio output devices detected - check speaker connections")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log audio system events."""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        if self.logger:
            if error:
                self.logger.error(f"Audio System Checker: {action} - {str(error)}")
            else:
                self.logger.info(f"Audio System Checker: {action}")
        
        # Could integrate with main logging system here 