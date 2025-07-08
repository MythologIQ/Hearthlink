"""
Persona Introducer - Voice and Animation System

Handles the introduction of Hearthlink personas with voice synthesis,
animations, and emotional resonance features.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

from .voice_synthesizer import VoiceSynthesizer
from .animation_engine import AnimationEngine

@dataclass
class PersonaIntro:
    """Persona introduction data."""
    name: str
    title: str
    description: str
    voice_message: str
    animation_type: str
    image_path: Optional[str] = None

class PersonaIntroducer:
    """
    Manages persona introductions with voice synthesis and animations.
    
    Provides emotionally resonant introductions for each Hearthlink persona,
    with accessibility features and customizable presentation options.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Persona Introducer.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize components
        self.voice_synthesizer = VoiceSynthesizer(self.logger)
        self.animation_engine = AnimationEngine(self.logger)
        
        # Persona definitions
        self.personas = self._define_personas()
        
        self._log("persona_introducer_initialized", "system", None, "system", None, {})
    
    def get_all_personas(self) -> List[PersonaIntro]:
        """Get all persona introductions."""
        return list(self.personas.values())
    
    def introduce_persona(self, persona_name: str) -> Optional[PersonaIntro]:
        """
        Introduce a specific persona with voice and animation.
        
        Args:
            persona_name: Name of the persona to introduce
            
        Returns:
            PersonaIntro object if successful, None otherwise
        """
        try:
            persona = self.personas.get(persona_name.lower())
            if not persona:
                self._log("persona_not_found", "system", None, "persona_intro", 
                         {"persona_name": persona_name}, "error")
                return None
            
            # Play voice introduction
            self.play_intro_voice(persona.name, persona.voice_message)
            
            # Show animation
            self.show_persona_animation(persona.name, persona.animation_type)
            
            self._log("persona_introduced", "system", None, "persona_intro", 
                     {"persona_name": persona_name})
            
            return persona
            
        except Exception as e:
            self._log("persona_introduction_failed", "system", None, "persona_intro", 
                     {"persona_name": persona_name}, "error", e)
            return None
    
    def play_intro_voice(self, persona_name: str, message: str) -> bool:
        """
        Play persona introduction voice message.
        
        Args:
            persona_name: Name of the persona
            message: Voice message to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.voice_synthesizer.speak_persona_intro(persona_name, message)
        except Exception as e:
            self._log("voice_playback_failed", "system", None, "persona_intro", 
                     {"persona_name": persona_name}, "error", e)
            return False
    
    def show_persona_animation(self, persona_name: str, animation_type: str) -> bool:
        """
        Show persona introduction animation.
        
        Args:
            persona_name: Name of the persona
            animation_type: Type of animation to show
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.animation_engine.play_persona_entrance(persona_name)
        except Exception as e:
            self._log("animation_playback_failed", "system", None, "persona_intro", 
                     {"persona_name": persona_name}, "error", e)
            return False
    
    def _define_personas(self) -> Dict[str, PersonaIntro]:
        """Define all persona introductions with emotional resonance."""
        return {
            "alden": PersonaIntro(
                name="Alden",
                title="The Wise Companion",
                description="Your empathetic, thoughtful companion who helps you think through problems, remember important things, and provides steady guidance in your digital life.",
                voice_message="Hello! I'm Alden, your wise companion. I'm here to help you think through problems, remember important things, and be a steady presence in your digital life.",
                animation_type="gentle_thoughtful",
                image_path="assets/Alden.png"
            ),
            "sentry": PersonaIntro(
                name="Sentry", 
                title="The Digital Guardian",
                description="Your vigilant protector who watches over your security, protects your privacy, and ensures everything runs smoothly and safely.",
                voice_message="I'm Sentry, your digital guardian. I watch over your security, protect your privacy, and ensure everything runs smoothly and safely.",
                animation_type="alert_protective",
                image_path="assets/Sentry.png"
            ),
            "alice": PersonaIntro(
                name="Alice",
                title="The Curious Researcher", 
                description="Your enthusiastic research partner who loves exploring, asking questions, and helping you discover new insights and connections.",
                voice_message="Hi there! I'm Alice, your research partner. I love exploring, asking questions, and helping you discover new insights and connections.",
                animation_type="energetic_curious",
                image_path="assets/Alice.png"
            ),
            "mimic": PersonaIntro(
                name="Mimic",
                title="The Adaptive Friend",
                description="Your flexible companion who adapts to your needs, learns your preferences, and becomes the perfect partner for any situation.",
                voice_message="I'm Mimic, your flexible friend. I adapt to your needs, learn your preferences, and become the companion you need for any situation.",
                animation_type="fluid_adaptable",
                image_path="assets/Mimic.png"
            ),
            "core": PersonaIntro(
                name="Core",
                title="The Conversation Conductor",
                description="Your organized orchestrator who helps everyone work together, manages your sessions, and keeps everything running smoothly.",
                voice_message="I'm Core, your conversation conductor. I help everyone work together, manage your sessions, and keep everything running smoothly.",
                animation_type="coordinated_flowing",
                image_path="assets/Core.png"
            ),
            "vault": PersonaIntro(
                name="Vault",
                title="The Memory Guardian",
                description="Your trustworthy memory keeper who safeguards your thoughts, experiences, and important information, keeping them organized and ready when you need them.",
                voice_message="I'm Vault, your memory guardian. I keep your thoughts, experiences, and important information safe, organized, and ready when you need them.",
                animation_type="solid_protective",
                image_path="assets/Vault.png"
            ),
            "synapse": PersonaIntro(
                name="Synapse",
                title="The Connection Specialist",
                description="Your dynamic connector who helps you reach out to the world, integrate with other tools, and expand your capabilities.",
                voice_message="I'm Synapse, your connection specialist. I help you reach out to the world, integrate with other tools, and expand your capabilities.",
                animation_type="dynamic_connecting",
                image_path="assets/Synapse.png"
            )
        }
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log persona introduction events."""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"Persona Introducer: {action} - {result}")
        
        if error:
            self.logger.error(f"Persona Introducer error: {str(error)}") 