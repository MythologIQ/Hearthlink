"""
Accessibility Manager - Accessibility Features System

Manages accessibility features and preferences for the installation UX,
including voiceover, screen reader support, and visual accommodations.
"""

import logging
from typing import Dict, Any, Optional

class AccessibilityManager:
    """
    Manages accessibility features and user preferences.
    
    Provides comprehensive accessibility support including voiceover,
    screen reader compatibility, visual accommodations, and user control features.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Accessibility Manager.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Accessibility settings
        self.voiceover_enabled = False
        self.animation_speed = "normal"
        self.high_contrast = False
        self.large_text = False
        self.screen_reader_mode = False
        self.keyboard_navigation = True
        
        self._log("accessibility_manager_initialized", "system", None, "system", None, {})
    
    def configure_from_preferences(self, preferences: Dict[str, Any]) -> bool:
        """
        Configure accessibility features based on user preferences.
        
        Args:
            preferences: Dictionary of user accessibility preferences
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.voiceover_enabled = preferences.get('voiceover', False)
            self.animation_speed = preferences.get('animation_speed', 'normal')
            self.high_contrast = preferences.get('high_contrast', False)
            self.large_text = preferences.get('large_text', False)
            self.screen_reader_mode = preferences.get('screen_reader', False)
            
            # Apply visual accommodations
            self._apply_visual_accommodations()
            
            self._log("accessibility_configured", "system", None, "accessibility", preferences)
            return True
            
        except Exception as e:
            self._log("accessibility_configuration_failed", "system", None, "accessibility", 
                     preferences, "error", e)
            return False
    
    def enable_voiceover(self, enabled: bool) -> bool:
        """
        Enable or disable voiceover narration.
        
        Args:
            enabled: Whether to enable voiceover
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.voiceover_enabled = enabled
            self._log("voiceover_toggled", "system", None, "accessibility", {"enabled": enabled})
            return True
            
        except Exception as e:
            self._log("voiceover_toggle_failed", "system", None, "accessibility", 
                     {"enabled": enabled}, "error", e)
            return False
    
    def adjust_animation_speed(self, speed: str) -> bool:
        """
        Adjust animation speed.
        
        Args:
            speed: Animation speed ('slow', 'normal', 'fast', 'disabled')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            valid_speeds = ['slow', 'normal', 'fast', 'disabled']
            if speed not in valid_speeds:
                self.logger.error(f"Invalid animation speed: {speed}")
                return False
            
            self.animation_speed = speed
            self._log("animation_speed_adjusted", "system", None, "accessibility", {"speed": speed})
            return True
            
        except Exception as e:
            self._log("animation_speed_adjustment_failed", "system", None, "accessibility", 
                     {"speed": speed}, "error", e)
            return False
    
    def announce_to_screen_reader(self, message: str) -> bool:
        """
        Announce message to screen reader if enabled.
        
        Args:
            message: Message to announce
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.screen_reader_mode:
                # In CLI mode, print with screen reader indicator
                print(f"[SR] {message}")
            
            self._log("screen_reader_announcement", "system", None, "accessibility", 
                     {"message_length": len(message)})
            return True
            
        except Exception as e:
            self._log("screen_reader_announcement_failed", "system", None, "accessibility", 
                     {"message": message}, "error", e)
            return False
    
    def get_accessibility_status(self) -> Dict[str, Any]:
        """
        Get current accessibility configuration status.
        
        Returns:
            Dictionary with current accessibility settings
        """
        return {
            'voiceover_enabled': self.voiceover_enabled,
            'animation_speed': self.animation_speed,
            'high_contrast': self.high_contrast,
            'large_text': self.large_text,
            'screen_reader_mode': self.screen_reader_mode,
            'keyboard_navigation': self.keyboard_navigation
        }
    
    def _apply_visual_accommodations(self) -> None:
        """Apply visual accommodations based on current settings."""
        try:
            if self.high_contrast:
                # In CLI mode, use high contrast text indicators
                print("\n[High Contrast Mode Enabled]")
            
            if self.large_text:
                # In CLI mode, use larger text indicators
                print("\n[Large Text Mode Enabled]")
            
            if self.animation_speed == 'disabled':
                print("\n[Animations Disabled]")
            
        except Exception as e:
            self.logger.error(f"Failed to apply visual accommodations: {str(e)}")
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log accessibility events."""
        log_entry = {
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"Accessibility Manager: {action} - {result}")
        
        if error:
            self.logger.error(f"Accessibility Manager error: {str(error)}") 