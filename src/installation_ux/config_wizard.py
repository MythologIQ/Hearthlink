"""
First Run Configuration Wizard

Guides users through first-time configuration of Hearthlink,
including workspace setup, privacy preferences, and theme selection.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class FirstRunConfigWizard:
    """
    First-time configuration wizard for Hearthlink setup.
    
    Provides a step-by-step guided configuration process for new users,
    including workspace setup, privacy preferences, and theme selection.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize Configuration Wizard.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Configuration steps
        self.config_steps = [
            'workspace_setup',
            'privacy_preferences', 
            'notification_settings',
            'theme_selection',
            'quick_tour'
        ]
        
        self._log("config_wizard_initialized", "system", None, "system", None, {})
    
    def run_configuration(self) -> Dict[str, Any]:
        """
        Run the complete configuration wizard.
        
        Returns:
            Dictionary with configuration results
        """
        try:
            user_preferences = {}
            
            print("\nLet's configure Hearthlink for your needs:")
            
            # Step 1: Workspace Setup
            workspace_config = self._workspace_setup()
            user_preferences.update(workspace_config)
            
            # Step 2: Privacy Preferences
            privacy_config = self._privacy_preferences()
            user_preferences.update(privacy_config)
            
            # Step 3: Notification Settings
            notification_config = self._notification_settings()
            user_preferences.update(notification_config)
            
            # Step 4: Theme Selection
            theme_config = self._theme_selection()
            user_preferences.update(theme_config)
            
            # Step 5: Quick Tour
            tour_config = self._quick_tour()
            user_preferences.update(tour_config)
            
            self._log("configuration_completed", "system", None, "configuration", 
                     {"steps_completed": len(self.config_steps)})
            
            return {
                "success": True,
                "installation_path": user_preferences.get("workspace_path"),
                "user_preferences": user_preferences
            }
            
        except Exception as e:
            self._log("configuration_failed", "system", None, "configuration", {}, "error", e)
            return {"success": False, "error": str(e)}
    
    def _workspace_setup(self) -> Dict[str, Any]:
        """Configure workspace location and settings."""
        print("\n📁 Workspace Setup")
        print("-" * 30)
        
        # Get default workspace path
        default_path = os.path.join(os.path.expanduser("~"), "Hearthlink")
        
        print(f"Where would you like to store your Hearthlink data?")
        print(f"Default: {default_path}")
        print("Press Enter to use default, or enter a custom path: ", end="")
        
        custom_path = input().strip()
        workspace_path = custom_path if custom_path else default_path
        
        # Create workspace directory
        try:
            Path(workspace_path).mkdir(parents=True, exist_ok=True)
            print(f"✅ Workspace created: {workspace_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create workspace: {str(e)}")
            workspace_path = "."  # Fallback to current directory
        
        return {
            "workspace_path": workspace_path,
            "workspace_auto_backup": True
        }
    
    def _privacy_preferences(self) -> Dict[str, Any]:
        """Configure privacy and data sharing preferences."""
        print("\n🔒 Privacy Preferences")
        print("-" * 30)
        
        preferences = {}
        
        print("How would you like to handle your data?")
        print("1. Strict privacy (local only)")
        print("2. Balanced (local + optional cloud backup)")
        print("3. Enhanced features (local + analytics)")
        
        while True:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                break
            print("Please enter 1, 2, or 3.")
        
        if choice == '1':
            preferences.update({
                "privacy_level": "strict",
                "data_sharing": False,
                "analytics": False,
                "cloud_backup": False
            })
        elif choice == '2':
            preferences.update({
                "privacy_level": "balanced",
                "data_sharing": False,
                "analytics": False,
                "cloud_backup": True
            })
        else:
            preferences.update({
                "privacy_level": "enhanced",
                "data_sharing": True,
                "analytics": True,
                "cloud_backup": True
            })
        
        print(f"✅ Privacy level set to: {preferences['privacy_level']}")
        return preferences
    
    def _notification_settings(self) -> Dict[str, Any]:
        """Configure notification preferences."""
        print("\n🔔 Notification Settings")
        print("-" * 30)
        
        preferences = {}
        
        print("When would you like to receive notifications?")
        print("1. Important updates only")
        print("2. Regular updates and reminders")
        print("3. All notifications")
        
        while True:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                break
            print("Please enter 1, 2, or 3.")
        
        if choice == '1':
            preferences.update({
                "notification_level": "important_only",
                "email_notifications": False,
                "desktop_notifications": True,
                "reminder_frequency": "weekly"
            })
        elif choice == '2':
            preferences.update({
                "notification_level": "regular",
                "email_notifications": True,
                "desktop_notifications": True,
                "reminder_frequency": "daily"
            })
        else:
            preferences.update({
                "notification_level": "all",
                "email_notifications": True,
                "desktop_notifications": True,
                "reminder_frequency": "daily"
            })
        
        print(f"✅ Notification level set to: {preferences['notification_level']}")
        return preferences
    
    def _theme_selection(self) -> Dict[str, Any]:
        """Configure visual theme and appearance."""
        print("\n🎨 Theme Selection")
        print("-" * 30)
        
        preferences = {}
        
        print("Choose your preferred theme:")
        print("1. Light theme")
        print("2. Dark theme")
        print("3. Auto (follows system)")
        
        while True:
            choice = input("Enter your choice (1-3): ").strip()
            if choice in ['1', '2', '3']:
                break
            print("Please enter 1, 2, or 3.")
        
        themes = {
            '1': 'light',
            '2': 'dark', 
            '3': 'auto'
        }
        
        preferences.update({
            "theme": themes[choice],
            "accent_color": "blue",
            "font_size": "medium"
        })
        
        print(f"✅ Theme set to: {preferences['theme']}")
        return preferences
    
    def _quick_tour(self) -> Dict[str, Any]:
        """Offer quick tour of key features."""
        print("\n🚀 Quick Tour")
        print("-" * 30)
        
        print("Would you like a quick tour of Hearthlink's key features?")
        print("This will help you get started quickly.")
        
        while True:
            choice = input("Take the tour? (y/n): ").strip().lower()
            if choice in ['y', 'n']:
                break
            print("Please enter y or n.")
        
        if choice == 'y':
            self._run_quick_tour()
            return {"quick_tour_completed": True}
        else:
            print("You can access the tour later from the Help menu.")
            return {"quick_tour_completed": False}
    
    def _run_quick_tour(self) -> None:
        """Run the quick tour of key features."""
        print("\n🎯 Quick Tour - Key Features")
        print("=" * 40)
        
        tour_steps = [
            ("🤖 AI Companions", "Meet your AI companions and learn their roles"),
            ("💬 Conversations", "Start conversations and manage your sessions"),
            ("🔍 Research", "Use Alice for research and exploration"),
            ("🛡️ Security", "Sentry keeps you safe and secure"),
            ("💾 Memory", "Vault stores and organizes your information"),
            ("🔗 Connections", "Synapse connects you to external tools and APIs")
        ]
        
        for i, (title, description) in enumerate(tour_steps, 1):
            print(f"\n{i}. {title}")
            print(f"   {description}")
            input("   Press Enter to continue...")
        
        print("\n✅ Tour completed! You're ready to start using Hearthlink.")
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any], result: str = "success", 
             error: Optional[Exception] = None):
        """Log configuration wizard events."""
        log_entry = {
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"Config Wizard: {action} - {result}")
        
        if error:
            self.logger.error(f"Config Wizard error: {str(error)}") 