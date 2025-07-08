"""
Animation Engine - Visual Animation System

Provides smooth, accessible animations for persona introductions
with support for reduced motion and accessibility preferences.
"""

import time
import logging
from typing import Dict, Any, Optional

class AnimationEngine:
    """
    Animation engine for persona introductions and visual effects.
    
    Provides smooth, accessible animations with support for reduced motion
    and various accessibility preferences.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Animation Engine.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Animation settings
        self.animation_speed = "normal"
        self.animations_enabled = True
        
        # Animation definitions for each persona
        self.animation_definitions = {
            'gentle_thoughtful': {
                'duration': 1.5,
                'type': 'fade_in_scale',
                'description': 'Gentle fade-in with subtle scaling'
            },
            'alert_protective': {
                'duration': 1.2,
                'type': 'slide_in_alert',
                'description': 'Confident slide-in with alert stance'
            },
            'energetic_curious': {
                'duration': 1.0,
                'type': 'bounce_in',
                'description': 'Energetic bounce-in with curiosity'
            },
            'fluid_adaptable': {
                'duration': 1.8,
                'type': 'morph_in',
                'description': 'Fluid morphing entrance'
            },
            'coordinated_flowing': {
                'duration': 1.3,
                'type': 'flow_in',
                'description': 'Coordinated flowing entrance'
            },
            'solid_protective': {
                'duration': 1.6,
                'type': 'solid_fade',
                'description': 'Solid, protective fade-in'
            },
            'dynamic_connecting': {
                'duration': 1.1,
                'type': 'connect_in',
                'description': 'Dynamic connecting entrance'
            }
        }
        
        self._log("animation_engine_initialized", "system", None, "system", None, {})
    
    def play_persona_entrance(self, persona_name: str) -> bool:
        """
        Play persona entrance animation.
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.animations_enabled:
                return True
            
            # Get animation definition
            animation_def = self.animation_definitions.get(persona_name.lower(), {})
            if not animation_def:
                self.logger.warning(f"No animation definition found for persona: {persona_name}")
                return True
            
            # Calculate duration based on speed setting
            base_duration = animation_def.get('duration', 1.0)
            duration = self._calculate_duration(base_duration)
            
            # In CLI mode, simulate animation with text effects
            self._play_cli_animation(persona_name, animation_def, duration)
            
            self._log("animation_completed", "system", None, "animation", 
                     {"persona_name": persona_name, "animation_type": animation_def.get('type')})
            
            return True
            
        except Exception as e:
            self._log("animation_failed", "system", None, "animation", 
                     {"persona_name": persona_name}, "error", e)
            return False
    
    def play_persona_idle(self, persona_name: str) -> bool:
        """
        Play persona idle animation loop.
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.animations_enabled:
                return True
            
            # In CLI mode, show subtle idle indicator
            print("  ✨", end="", flush=True)
            time.sleep(0.5)
            print("\b \b", end="", flush=True)
            
            return True
            
        except Exception as e:
            self._log("idle_animation_failed", "system", None, "animation", 
                     {"persona_name": persona_name}, "error", e)
            return False
    
    def set_animation_speed(self, speed: str) -> bool:
        """
        Set animation speed.
        
        Args:
            speed: Animation speed ('slow', 'normal', 'fast', 'disabled')
            
        Returns:
            True if successful, False otherwise
        """
        valid_speeds = ['slow', 'normal', 'fast', 'disabled']
        if speed not in valid_speeds:
            self.logger.error(f"Invalid animation speed: {speed}")
            return False
        
        self.animation_speed = speed
        self.animations_enabled = speed != 'disabled'
        
        self._log("animation_speed_changed", "system", None, "animation", {"speed": speed})
        return True
    
    def _calculate_duration(self, base_duration: float) -> float:
        """Calculate animation duration based on speed setting."""
        speed_multipliers = {
            'slow': 2.0,
            'normal': 1.0,
            'fast': 0.5,
            'disabled': 0.0
        }
        
        multiplier = speed_multipliers.get(self.animation_speed, 1.0)
        return base_duration * multiplier
    
    def _play_cli_animation(self, persona_name: str, animation_def: Dict[str, Any], duration: float) -> None:
        """Play animation in CLI mode with text effects."""
        animation_type = animation_def.get('type', 'fade_in')
        description = animation_def.get('description', 'Entrance animation')
        
        # Simple CLI animation simulation
        print(f"\n🎭 {persona_name} - {description}")
        
        # Simulate animation timing
        steps = 5
        step_duration = duration / steps
        
        for i in range(steps):
            progress = (i + 1) / steps
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            print(f"\r  [{bar}] {int(progress * 100)}%", end="", flush=True)
            time.sleep(step_duration)
        
        print()  # New line after animation
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log animation events."""
        log_entry = {
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"Animation Engine: {action} - {result}")
        
        if error:
            self.logger.error(f"Animation Engine error: {str(error)}") 