"""
Unit Tests for Audio System Checker

Comprehensive testing of audio input/output testing and configuration
for Hearthlink installation and onboarding experience.
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from installation_ux.audio_system_checker import (
    AudioSystemChecker, 
    AudioDevice, 
    AudioTestResult
)

class TestAudioSystemChecker(unittest.TestCase):
    """Test cases for AudioSystemChecker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.audio_checker = AudioSystemChecker()
        self.test_config = {
            "sample_rate": 44100,
            "channels": 1,
            "format": "int16"
        }
    
    def test_initialization(self):
        """Test AudioSystemChecker initialization."""
        self.assertIsNotNone(self.audio_checker)
        self.assertIsNotNone(self.audio_checker.logger)
    
    @patch('installation_ux.audio_system_checker.AUDIO_AVAILABLE', False)
    def test_initialization_no_audio_library(self):
        """Test initialization when audio libraries are not available."""
        checker = AudioSystemChecker()
        self.assertIsNone(checker.audio)
        self.assertIsNone(checker.recognizer)
    
    @patch('installation_ux.audio_system_checker.STT_AVAILABLE', False)
    def test_initialization_no_stt_library(self):
        """Test initialization when speech recognition library is not available."""
        checker = AudioSystemChecker()
        self.assertIsNone(checker.recognizer)
    
    def test_audio_device_dataclass(self):
        """Test AudioDevice dataclass."""
        device = AudioDevice(
            name="Test Microphone",
            device_id=1,
            device_type="input",
            sample_rate=44100,
            channels=1,
            is_default=True
        )
        
        self.assertEqual(device.name, "Test Microphone")
        self.assertEqual(device.device_id, 1)
        self.assertEqual(device.device_type, "input")
        self.assertEqual(device.sample_rate, 44100)
        self.assertEqual(device.channels, 1)
        self.assertTrue(device.is_default)
    
    def test_audio_test_result_dataclass(self):
        """Test AudioTestResult dataclass."""
        result = AudioTestResult(
            test_name="test_microphone",
            success=True,
            details={"quality_score": 0.8},
            recommendations=["Test recommendation"]
        )
        
        self.assertEqual(result.test_name, "test_microphone")
        self.assertTrue(result.success)
        self.assertEqual(result.details["quality_score"], 0.8)
        self.assertEqual(result.recommendations, ["Test recommendation"])
    
    @patch('installation_ux.audio_system_checker.AUDIO_AVAILABLE', False)
    def test_check_microphone_access_no_audio_library(self):
        """Test microphone check when audio library is not available."""
        result = self.audio_checker.check_microphone_access()
        
        self.assertFalse(result.success)
        self.assertEqual(result.test_name, "microphone_access")
        self.assertIn("Audio library not available", result.error_message)
        self.assertIn("Install PyAudio", result.recommendations[0])
    
    @patch('installation_ux.audio_system_checker.AUDIO_AVAILABLE', True)
    @patch('pyaudio.PyAudio')
    def test_check_microphone_access_success(self, mock_pyaudio):
        """Test successful microphone access check."""
        # Mock PyAudio
        mock_audio = Mock()
        mock_pyaudio.return_value = mock_audio
        
        # Mock device info
        mock_audio.get_default_input_device_info.return_value = {'index': 0}
        mock_audio.get_device_info.return_value = {
            'name': 'Test Microphone',
            'defaultSampleRate': 44100,
            'maxInputChannels': 1
        }
        
        # Mock audio stream
        mock_stream = Mock()
        mock_audio.open.return_value = mock_stream
        mock_stream.read.return_value = b'\x00\x00' * 512  # Mock audio data
        
        result = self.audio_checker.check_microphone_access()
        
        self.assertTrue(result.success)
        self.assertEqual(result.test_name, "microphone_access")
        self.assertIn("Test Microphone", result.details["device_name"])
        self.assertEqual(result.details["sample_rate"], 44100)
        self.assertEqual(result.details["channels"], 1)
    
    @patch('installation_ux.audio_system_checker.AUDIO_AVAILABLE', True)
    @patch('pyaudio.PyAudio')
    def test_check_speaker_output_no_audio_library(self, mock_pyaudio):
        """Test speaker check when audio library is not available."""
        mock_pyaudio.side_effect = Exception("PyAudio not available")
        
        result = self.audio_checker.check_speaker_output()
        
        self.assertFalse(result.success)
        self.assertEqual(result.test_name, "speaker_output")
        self.assertIn("PyAudio not available", result.error_message)
    
    @patch('installation_ux.audio_system_checker.AUDIO_AVAILABLE', True)
    @patch('pyaudio.PyAudio')
    @patch('builtins.input', return_value='y')
    def test_check_speaker_output_success(self, mock_input, mock_pyaudio):
        """Test successful speaker output check."""
        # Mock PyAudio
        mock_audio = Mock()
        mock_pyaudio.return_value = mock_audio
        
        # Mock device info
        mock_audio.get_default_output_device_info.return_value = {'index': 0}
        mock_audio.get_device_info.return_value = {
            'name': 'Test Speakers',
            'defaultSampleRate': 44100,
            'maxOutputChannels': 2
        }
        
        # Mock audio stream
        mock_stream = Mock()
        mock_audio.open.return_value = mock_stream
        
        result = self.audio_checker.check_speaker_output()
        
        self.assertTrue(result.success)
        self.assertEqual(result.test_name, "speaker_output")
        self.assertIn("Test Speakers", result.details["device_name"])
        self.assertTrue(result.details["user_confirmed"])
    
    @patch('installation_ux.audio_system_checker.platform.system')
    def test_test_voice_synthesis_windows(self, mock_platform):
        """Test voice synthesis on Windows."""
        mock_platform.return_value = "Windows"
        
        # Mock win32com.client.Dispatch
        with patch('installation_ux.audio_system_checker.win32com.client.Dispatch', create=True) as mock_dispatch:
            mock_speaker = Mock()
            mock_dispatch.return_value = mock_speaker
            
            result = self.audio_checker.test_voice_synthesis()
            
            self.assertTrue(result.success)
            self.assertEqual(result.test_name, "voice_synthesis")
            self.assertIn("Windows SAPI", result.details["available_methods"])
    
    @patch('installation_ux.audio_system_checker.platform.system')
    def test_test_voice_synthesis_macos(self, mock_platform):
        """Test voice synthesis on macOS."""
        mock_platform.return_value = "Darwin"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = self.audio_checker.test_voice_synthesis()
            
            self.assertTrue(result.success)
            self.assertEqual(result.test_name, "voice_synthesis")
            self.assertIn("macOS say", result.details["available_methods"])
    
    @patch('installation_ux.audio_system_checker.platform.system')
    def test_test_voice_synthesis_linux(self, mock_platform):
        """Test voice synthesis on Linux."""
        mock_platform.return_value = "Linux"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            result = self.audio_checker.test_voice_synthesis()
            
            self.assertTrue(result.success)
            self.assertEqual(result.test_name, "voice_synthesis")
            self.assertIn("Linux espeak", result.details["available_methods"])
    
    @patch('installation_ux.audio_system_checker.AUDIO_AVAILABLE', True)
    @patch('pyaudio.PyAudio')
    def test_get_audio_devices(self, mock_pyaudio):
        """Test getting audio devices."""
        # Mock PyAudio
        mock_audio = Mock()
        mock_pyaudio.return_value = mock_audio
        
        # Mock device count and info
        mock_audio.get_device_count.return_value = 2
        mock_audio.get_device_info.side_effect = [
            {
                'name': 'Test Microphone',
                'maxInputChannels': 1,
                'maxOutputChannels': 0,
                'defaultSampleRate': 44100
            },
            {
                'name': 'Test Speakers',
                'maxInputChannels': 0,
                'maxOutputChannels': 2,
                'defaultSampleRate': 44100
            }
        ]
        mock_audio.get_default_input_device_info.return_value = {'index': 0}
        mock_audio.get_default_output_device_info.return_value = {'index': 1}
        
        devices = self.audio_checker.get_audio_devices()
        
        self.assertIn('input', devices)
        self.assertIn('output', devices)
        self.assertEqual(len(devices['input']), 1)
        self.assertEqual(len(devices['output']), 1)
        self.assertEqual(devices['input'][0].name, 'Test Microphone')
        self.assertEqual(devices['output'][0].name, 'Test Speakers')
    
    def test_configure_audio_devices(self):
        """Test audio device configuration."""
        # Mock get_audio_devices
        mock_devices = {
            'input': [
                AudioDevice('Test Mic 1', 0, 'input', 44100, 1, True),
                AudioDevice('Test Mic 2', 1, 'input', 44100, 1, False)
            ],
            'output': [
                AudioDevice('Test Speakers 1', 0, 'output', 44100, 2, True),
                AudioDevice('Test Speakers 2', 1, 'output', 44100, 2, False)
            ]
        }
        
        with patch.object(self.audio_checker, 'get_audio_devices', return_value=mock_devices):
            config = self.audio_checker.configure_audio_devices()
            
            self.assertTrue(config['success'])
            self.assertEqual(config['input_device'], 'Test Mic 1')
            self.assertEqual(config['output_device'], 'Test Speakers 1')
            self.assertEqual(config['sample_rate'], 44100)
            self.assertEqual(config['channels'], 1)
    
    def test_configure_audio_devices_with_specific_devices(self):
        """Test audio device configuration with specific device IDs."""
        # Mock get_audio_devices
        mock_devices = {
            'input': [
                AudioDevice('Test Mic 1', 0, 'input', 44100, 1, True),
                AudioDevice('Test Mic 2', 1, 'input', 44100, 1, False)
            ],
            'output': [
                AudioDevice('Test Speakers 1', 0, 'output', 44100, 2, True),
                AudioDevice('Test Speakers 2', 1, 'output', 44100, 2, False)
            ]
        }
        
        with patch.object(self.audio_checker, 'get_audio_devices', return_value=mock_devices):
            config = self.audio_checker.configure_audio_devices(input_device_id=1, output_device_id=1)
            
            self.assertTrue(config['success'])
            self.assertEqual(config['input_device'], 'Test Mic 2')
            self.assertEqual(config['output_device'], 'Test Speakers 2')
    
    @patch('installation_ux.audio_system_checker.platform.system')
    def test_check_audio_compatibility(self, mock_platform):
        """Test audio compatibility check."""
        mock_platform.return_value = "Windows"
        
        result = self.audio_checker.check_audio_compatibility()
        
        self.assertEqual(result.test_name, "audio_compatibility")
        self.assertIn("platform", result.details)
        self.assertEqual(result.details["platform"], "Windows")
    
    def test_calculate_audio_quality(self):
        """Test audio quality calculation."""
        # Test high quality audio
        quality = self.audio_checker._calculate_audio_quality(5000, 500, 10000)
        self.assertGreaterEqual(quality, 0.8)
        
        # Test low quality audio
        quality = self.audio_checker._calculate_audio_quality(500, 2000, 2000)
        self.assertLess(quality, 0.3)
        
        # Test boundary conditions
        quality = self.audio_checker._calculate_audio_quality(0, 0, 0)
        self.assertEqual(quality, 0)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        results = {
            "microphone": AudioTestResult(
                "microphone_access", False, {}, 
                error_message="Failed", 
                recommendations=["Check microphone"]
            ),
            "speaker": AudioTestResult(
                "speaker_output", True, {}, 
                recommendations=["Speaker working"]
            ),
            "voice_synthesis": AudioTestResult(
                "voice_synthesis", False, {}, 
                error_message="No TTS", 
                recommendations=["Install TTS"]
            ),
            "devices": {"input": [], "output": []},
            "compatibility": AudioTestResult(
                "audio_compatibility", True, {}, 
                recommendations=[]
            )
        }
        
        recommendations = self.audio_checker._generate_recommendations(results)
        
        self.assertIn("Check microphone", recommendations)
        self.assertIn("Install TTS", recommendations)
        self.assertIn("No audio input devices detected", recommendations[0])
        self.assertIn("No audio output devices detected", recommendations[3])
    
    def test_run_comprehensive_audio_check(self):
        """Test comprehensive audio check."""
        # Mock individual test methods
        with patch.object(self.audio_checker, 'check_microphone_access') as mock_mic:
            with patch.object(self.audio_checker, 'check_speaker_output') as mock_speaker:
                with patch.object(self.audio_checker, 'test_voice_synthesis') as mock_tts:
                    with patch.object(self.audio_checker, 'get_audio_devices') as mock_devices:
                        with patch.object(self.audio_checker, 'check_audio_compatibility') as mock_comp:
                            # Set up mock returns
                            mock_mic.return_value = AudioTestResult("mic", True, {})
                            mock_speaker.return_value = AudioTestResult("speaker", True, {})
                            mock_tts.return_value = AudioTestResult("tts", True, {})
                            mock_devices.return_value = {"input": [], "output": []}
                            mock_comp.return_value = AudioTestResult("comp", True, {})
                            
                            results = self.audio_checker.run_comprehensive_audio_check()
                            
                            self.assertTrue(results["overall_success"])
                            self.assertIn("microphone", results)
                            self.assertIn("speaker", results)
                            self.assertIn("voice_synthesis", results)
                            self.assertIn("devices", results)
                            self.assertIn("compatibility", results)
                            self.assertIn("recommendations", results)
    
    def test_run_comprehensive_audio_check_failure(self):
        """Test comprehensive audio check with failures."""
        # Mock individual test methods with failures
        with patch.object(self.audio_checker, 'check_microphone_access') as mock_mic:
            with patch.object(self.audio_checker, 'check_speaker_output') as mock_speaker:
                # Set up mock returns with failures
                mock_mic.return_value = AudioTestResult("mic", False, {}, error_message="Failed")
                mock_speaker.return_value = AudioTestResult("speaker", False, {}, error_message="Failed")
                
                results = self.audio_checker.run_comprehensive_audio_check()
                
                self.assertFalse(results["overall_success"])
                self.assertIn("recommendations", results)
    
    def test_log_method(self):
        """Test logging method."""
        # Test successful log
        self.audio_checker._log("test_action", "user123", "session456", "test_event", {"key": "value"})
        
        # Test error log
        test_error = Exception("Test error")
        self.audio_checker._log("test_error", "user123", "session456", "test_event", {}, "error", test_error)
        
        # Verify logger was called (basic check)
        self.assertIsNotNone(self.audio_checker.logger)

if __name__ == '__main__':
    unittest.main() 