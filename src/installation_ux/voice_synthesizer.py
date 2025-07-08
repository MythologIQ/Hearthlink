"""
Voice Synthesizer - Text-to-Speech System

Provides text-to-speech functionality with persona-specific voice profiles
for emotionally resonant persona introductions.
"""

import logging
from typing import Dict, Any, Optional

class VoiceSynthesizer:
    """
    Text-to-speech synthesizer with persona-specific voice profiles.
    
    Provides emotionally resonant voice synthesis for persona introductions,
    with accessibility features and customizable voice characteristics.
    """
    
    def __init__(self, logger=None):
        """
        Initialize Voice Synthesizer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Voice profiles for each persona
        self.voice_profiles = {
            'alden': {
                'rate': 150,
                'volume': 0.8,
                'voice_id': 'male_warm',
                'description': 'Warm, gentle, slightly older-sounding male voice'
            },
            'sentry': {
                'rate': 160,
                'volume': 0.9,
                'voice_id': 'female_confident',
                'description': 'Clear, confident, reassuring female voice'
            },
            'alice': {
                'rate': 170,
                'volume': 0.85,
                'voice_id': 'female_enthusiastic',
                'description': 'Bright, enthusiastic, inquisitive female voice'
            },
            'mimic': {
                'rate': 155,
                'volume': 0.8,
                'voice_id': 'neutral_adaptable',
                'description': 'Versatile, adaptable, warm voice'
            },
            'core': {
                'rate': 145,
                'volume': 0.85,
                'voice_id': 'male_authoritative',
                'description': 'Calm, organized, authoritative voice'
            },
            'vault': {
                'rate': 140,
                'volume': 0.9,
                'voice_id': 'male_deep',
                'description': 'Deep, trustworthy, secure voice'
            },
            'synapse': {
                'rate': 165,
                'volume': 0.8,
                'voice_id': 'female_efficient',
                'description': 'Quick, efficient, helpful voice'
            }
        }
        
        # Initialize TTS engine
        self.tts_engine = None
        self._initialize_tts_engine()
        
        self._log("voice_synthesizer_initialized", "system", None, "system", None, {})
    
    def speak_persona_intro(self, persona_name: str, message: str) -> bool:
        """
        Speak persona introduction with appropriate voice profile.
        
        Args:
            persona_name: Name of the persona
            message: Message to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profile = self.voice_profiles.get(persona_name.lower(), {})
            
            if not self.tts_engine:
                self.logger.warning("TTS engine not available, skipping voice synthesis")
                return False
            
            # Configure voice properties
            self.tts_engine.setProperty('rate', profile.get('rate', 150))
            self.tts_engine.setProperty('volume', profile.get('volume', 0.8))
            
            # Speak the message
            self.tts_engine.say(message)
            self.tts_engine.runAndWait()
            
            self._log("voice_synthesis_completed", "system", None, "voice_synthesis", 
                     {"persona_name": persona_name, "message_length": len(message)})
            
            return True
            
        except Exception as e:
            self._log("voice_synthesis_failed", "system", None, "voice_synthesis", 
                     {"persona_name": persona_name}, "error", e)
            return False
    
    def _initialize_tts_engine(self) -> bool:
        """Initialize the text-to-speech engine."""
        try:
            # Try to import pyttsx3
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            
            # Configure default properties
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.8)
            
            self._log("tts_engine_initialized", "system", None, "system", None, {})
            return True
            
        except ImportError:
            self.logger.warning("pyttsx3 not available - voice synthesis disabled")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS engine: {str(e)}")
            return False
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log voice synthesis events."""
        log_entry = {
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"Voice Synthesizer: {action} - {result}")
        
        if error:
            self.logger.error(f"Voice Synthesizer error: {str(error)}") 