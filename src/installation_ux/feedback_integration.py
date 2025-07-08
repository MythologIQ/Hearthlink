"""
Feedback Integration - Seamless User Experience Tracking

Integrates feedback collection into installation and onboarding processes,
providing real-time user experience tracking and continuous improvement.
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone

from .feedback_collection_system import (
    FeedbackCollectionSystem, FeedbackType, FeedbackSeverity, 
    InstallationFeedback, OnboardingFeedback, UserFeedback
)

class FeedbackIntegration:
    """
    Seamless feedback integration for installation and onboarding processes.
    
    Provides real-time user experience tracking and automatic feedback collection
    throughout the installation and onboarding journey.
    """
    
    def __init__(self, feedback_system: FeedbackCollectionSystem):
        """
        Initialize Feedback Integration.
        
        Args:
            feedback_system: Feedback collection system instance
        """
        self.feedback_system = feedback_system
        self.current_session = None
        self.session_start_time = None
        self.step_timings = {}
        self.user_actions = []
        
    def start_session(self, user_id: str) -> str:
        """
        Start a new feedback session.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Session ID
        """
        self.current_session = str(uuid.uuid4())
        self.session_start_time = time.time()
        self.step_timings = {}
        self.user_actions = []
        
        self.feedback_system._log("session_started", user_id, self.current_session, "session", {
            "session_id": self.current_session,
            "start_time": datetime.now(timezone.utc).isoformat()
        })
        
        return self.current_session
    
    def end_session(self, user_id: str) -> Dict[str, Any]:
        """
        End the current feedback session.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Session summary
        """
        if not self.current_session:
            return {"error": "No active session"}
        
        session_duration = time.time() - self.session_start_time
        
        summary = {
            "session_id": self.current_session,
            "duration": session_duration,
            "steps_completed": len(self.step_timings),
            "user_actions": len(self.user_actions),
            "start_time": datetime.fromtimestamp(self.session_start_time, timezone.utc).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat()
        }
        
        self.feedback_system._log("session_ended", user_id, self.current_session, "session", summary)
        
        # Reset session
        self.current_session = None
        self.session_start_time = None
        self.step_timings = {}
        self.user_actions = []
        
        return summary
    
    def track_installation_step(self, user_id: str, step_name: str, 
                              success: bool, error_message: Optional[str] = None,
                              suggestions: Optional[List[str]] = None) -> str:
        """
        Track an installation step and collect feedback.
        
        Args:
            user_id: Unique user identifier
            step_name: Name of the installation step
            success: Whether the step was successful
            error_message: Error message if failed
            suggestions: User suggestions for improvement
            
        Returns:
            Feedback ID
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        # Calculate step duration
        step_start_time = self.step_timings.get(step_name, {}).get("start_time", time.time())
        step_duration = time.time() - step_start_time
        
        # Collect feedback
        feedback_id = self.feedback_system.collect_installation_feedback(
            user_id=user_id,
            session_id=self.current_session,
            installation_step=step_name,
            success=success,
            duration_seconds=step_duration,
            error_message=error_message,
            suggestions=suggestions
        )
        
        # Update step timing
        self.step_timings[step_name] = {
            "start_time": step_start_time,
            "end_time": time.time(),
            "duration": step_duration,
            "success": success,
            "feedback_id": feedback_id
        }
        
        return feedback_id
    
    def start_installation_step(self, step_name: str):
        """Mark the start of an installation step."""
        self.step_timings[step_name] = {
            "start_time": time.time(),
            "end_time": None,
            "duration": None,
            "success": None,
            "feedback_id": None
        }
    
    def track_onboarding_experience(self, user_id: str, persona_name: str,
                                  introduction_rating: int, clarity_rating: int,
                                  helpfulness_rating: int, emotional_response: str,
                                  suggestions: Optional[List[str]] = None,
                                  skipped_steps: Optional[List[str]] = None) -> str:
        """
        Track onboarding experience and collect feedback.
        
        Args:
            user_id: Unique user identifier
            persona_name: Name of the persona
            introduction_rating: Rating of introduction (1-5)
            clarity_rating: Rating of clarity (1-5)
            helpfulness_rating: Rating of helpfulness (1-5)
            emotional_response: User's emotional response
            suggestions: User suggestions for improvement
            skipped_steps: Steps that were skipped
            
        Returns:
            Feedback ID
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        # Calculate completion time
        completion_time = time.time() - self.session_start_time if self.session_start_time else None
        
        # Collect feedback
        feedback_id = self.feedback_system.collect_onboarding_feedback(
            user_id=user_id,
            session_id=self.current_session,
            persona_name=persona_name,
            introduction_rating=introduction_rating,
            clarity_rating=clarity_rating,
            helpfulness_rating=helpfulness_rating,
            emotional_response=emotional_response,
            suggestions=suggestions,
            completion_time=completion_time,
            skipped_steps=skipped_steps
        )
        
        return feedback_id
    
    def track_user_action(self, action: str, details: Optional[Dict[str, Any]] = None):
        """Track user actions during the session."""
        if not self.current_session:
            return
        
        action_entry = {
            "timestamp": time.time(),
            "action": action,
            "details": details or {}
        }
        
        self.user_actions.append(action_entry)
    
    def collect_general_feedback(self, user_id: str, title: str, description: str,
                               feedback_type: FeedbackType, severity: FeedbackSeverity,
                               suggestions: Optional[List[str]] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Collect general feedback during the session.
        
        Args:
            user_id: Unique user identifier
            title: Feedback title
            description: Feedback description
            feedback_type: Type of feedback
            severity: Severity level
            suggestions: User suggestions
            metadata: Additional metadata
            
        Returns:
            Feedback ID
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        # Add session metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "session_id": self.current_session,
            "session_duration": time.time() - self.session_start_time if self.session_start_time else 0,
            "steps_completed": len(self.step_timings),
            "user_actions_count": len(self.user_actions)
        })
        
        return self.feedback_system.collect_general_feedback(
            user_id=user_id,
            session_id=self.current_session,
            title=title,
            description=description,
            feedback_type=feedback_type,
            severity=severity,
            suggestions=suggestions,
            metadata=metadata
        )
    
    def report_issue(self, user_id: str, title: str, description: str,
                    severity: FeedbackSeverity, steps_to_reproduce: Optional[List[str]] = None,
                    expected_behavior: Optional[str] = None, actual_behavior: Optional[str] = None) -> str:
        """
        Report an issue during the session.
        
        Args:
            user_id: Unique user identifier
            title: Issue title
            description: Issue description
            severity: Issue severity
            steps_to_reproduce: Steps to reproduce
            expected_behavior: Expected behavior
            actual_behavior: Actual behavior
            
        Returns:
            GitHub issue ID
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")
        
        # Add session context to description
        session_context = f"\n\n**Session Context:**\n- Session ID: {self.current_session}\n"
        session_context += f"- Session Duration: {time.time() - self.session_start_time:.2f} seconds\n"
        session_context += f"- Steps Completed: {len(self.step_timings)}\n"
        session_context += f"- User Actions: {len(self.user_actions)}\n"
        
        enhanced_description = description + session_context
        
        return self.feedback_system.report_issue(
            user_id=user_id,
            session_id=self.current_session,
            title=title,
            description=enhanced_description,
            severity=severity,
            steps_to_reproduce=steps_to_reproduce,
            expected_behavior=expected_behavior,
            actual_behavior=actual_behavior
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session summary."""
        if not self.current_session:
            return {"error": "No active session"}
        
        return {
            "session_id": self.current_session,
            "duration": time.time() - self.session_start_time if self.session_start_time else 0,
            "steps": self.step_timings,
            "user_actions": self.user_actions,
            "start_time": datetime.fromtimestamp(self.session_start_time, timezone.utc).isoformat() if self.session_start_time else None
        }

class InstallationFeedbackTracker:
    """
    Specialized tracker for installation process feedback.
    
    Provides step-by-step tracking and automatic feedback collection
    for the installation process.
    """
    
    def __init__(self, feedback_integration: FeedbackIntegration):
        """
        Initialize Installation Feedback Tracker.
        
        Args:
            feedback_integration: Feedback integration instance
        """
        self.feedback_integration = feedback_integration
        self.installation_steps = []
        self.current_step = None
        
    def start_installation(self, user_id: str) -> str:
        """
        Start installation tracking.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Session ID
        """
        session_id = self.feedback_integration.start_session(user_id)
        self.installation_steps = []
        return session_id
    
    def track_step(self, user_id: str, step_name: str, step_description: str,
                  success: bool, error_message: Optional[str] = None,
                  suggestions: Optional[List[str]] = None) -> str:
        """
        Track an installation step.
        
        Args:
            user_id: Unique user identifier
            step_name: Name of the step
            step_description: Description of the step
            success: Whether the step was successful
            error_message: Error message if failed
            suggestions: User suggestions
            
        Returns:
            Feedback ID
        """
        # Start timing the step
        self.feedback_integration.start_installation_step(step_name)
        
        # Track the step
        feedback_id = self.feedback_integration.track_installation_step(
            user_id=user_id,
            step_name=step_name,
            success=success,
            error_message=error_message,
            suggestions=suggestions
        )
        
        # Record step details
        step_info = {
            "name": step_name,
            "description": step_description,
            "success": success,
            "feedback_id": feedback_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.installation_steps.append(step_info)
        
        return feedback_id
    
    def end_installation(self, user_id: str) -> Dict[str, Any]:
        """
        End installation tracking.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Installation summary
        """
        session_summary = self.feedback_integration.end_session(user_id)
        
        installation_summary = {
            "session_summary": session_summary,
            "installation_steps": self.installation_steps,
            "total_steps": len(self.installation_steps),
            "successful_steps": len([s for s in self.installation_steps if s["success"]]),
            "failed_steps": len([s for s in self.installation_steps if not s["success"]])
        }
        
        return installation_summary

class OnboardingFeedbackTracker:
    """
    Specialized tracker for onboarding experience feedback.
    
    Provides comprehensive tracking and feedback collection for
    the onboarding experience with each persona.
    """
    
    def __init__(self, feedback_integration: FeedbackIntegration):
        """
        Initialize Onboarding Feedback Tracker.
        
        Args:
            feedback_integration: Feedback integration instance
        """
        self.feedback_integration = feedback_integration
        self.onboarding_experiences = []
        self.current_persona = None
        
    def start_onboarding(self, user_id: str) -> str:
        """
        Start onboarding tracking.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Session ID
        """
        session_id = self.feedback_integration.start_session(user_id)
        self.onboarding_experiences = []
        return session_id
    
    def track_persona_experience(self, user_id: str, persona_name: str,
                               introduction_rating: int, clarity_rating: int,
                               helpfulness_rating: int, emotional_response: str,
                               suggestions: Optional[List[str]] = None,
                               skipped_steps: Optional[List[str]] = None) -> str:
        """
        Track experience with a specific persona.
        
        Args:
            user_id: Unique user identifier
            persona_name: Name of the persona
            introduction_rating: Rating of introduction (1-5)
            clarity_rating: Rating of clarity (1-5)
            helpfulness_rating: Rating of helpfulness (1-5)
            emotional_response: User's emotional response
            suggestions: User suggestions
            skipped_steps: Steps that were skipped
            
        Returns:
            Feedback ID
        """
        feedback_id = self.feedback_integration.track_onboarding_experience(
            user_id=user_id,
            persona_name=persona_name,
            introduction_rating=introduction_rating,
            clarity_rating=clarity_rating,
            helpfulness_rating=helpfulness_rating,
            emotional_response=emotional_response,
            suggestions=suggestions,
            skipped_steps=skipped_steps
        )
        
        # Record experience details
        experience_info = {
            "persona_name": persona_name,
            "introduction_rating": introduction_rating,
            "clarity_rating": clarity_rating,
            "helpfulness_rating": helpfulness_rating,
            "emotional_response": emotional_response,
            "feedback_id": feedback_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.onboarding_experiences.append(experience_info)
        
        return feedback_id
    
    def end_onboarding(self, user_id: str) -> Dict[str, Any]:
        """
        End onboarding tracking.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Onboarding summary
        """
        session_summary = self.feedback_integration.end_session(user_id)
        
        # Calculate average ratings
        if self.onboarding_experiences:
            avg_introduction = sum(e["introduction_rating"] for e in self.onboarding_experiences) / len(self.onboarding_experiences)
            avg_clarity = sum(e["clarity_rating"] for e in self.onboarding_experiences) / len(self.onboarding_experiences)
            avg_helpfulness = sum(e["helpfulness_rating"] for e in self.onboarding_experiences) / len(self.onboarding_experiences)
        else:
            avg_introduction = avg_clarity = avg_helpfulness = 0
        
        onboarding_summary = {
            "session_summary": session_summary,
            "onboarding_experiences": self.onboarding_experiences,
            "total_personas": len(self.onboarding_experiences),
            "average_ratings": {
                "introduction": avg_introduction,
                "clarity": avg_clarity,
                "helpfulness": avg_helpfulness
            }
        }
        
        return onboarding_summary

class FeedbackUI:
    """
    User interface components for feedback collection.
    
    Provides user-friendly interfaces for collecting feedback
    during installation and onboarding processes.
    """
    
    def __init__(self, feedback_integration: FeedbackIntegration):
        """
        Initialize Feedback UI.
        
        Args:
            feedback_integration: Feedback integration instance
        """
        self.feedback_integration = feedback_integration
    
    def show_installation_feedback_prompt(self, step_name: str, success: bool, 
                                        error_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Show installation feedback prompt to user.
        
        Args:
            step_name: Name of the installation step
            success: Whether the step was successful
            error_message: Error message if failed
            
        Returns:
            User feedback response
        """
        print(f"\n{'='*60}")
        print(f"📋 Installation Feedback: {step_name}")
        print(f"{'='*60}")
        
        if success:
            print("✅ Installation step completed successfully!")
        else:
            print("❌ Installation step encountered an issue.")
            if error_message:
                print(f"Error: {error_message}")
        
        print("\nPlease provide feedback to help us improve:")
        
        # Collect suggestions
        suggestions = []
        print("\n💡 Suggestions for improvement (press Enter when done):")
        while True:
            suggestion = input("Suggestion: ").strip()
            if not suggestion:
                break
            suggestions.append(suggestion)
        
        return {
            "success": success,
            "suggestions": suggestions,
            "error_message": error_message
        }
    
    def show_onboarding_feedback_prompt(self, persona_name: str) -> Dict[str, Any]:
        """
        Show onboarding feedback prompt for a persona.
        
        Args:
            persona_name: Name of the persona
            
        Returns:
            User feedback response
        """
        print(f"\n{'='*60}")
        print(f"🌟 Onboarding Feedback: {persona_name}")
        print(f"{'='*60}")
        
        print("Please rate your experience with this AI companion:")
        
        # Collect ratings
        introduction_rating = self._get_rating("Introduction clarity and warmth (1-5): ")
        clarity_rating = self._get_rating("Overall clarity of communication (1-5): ")
        helpfulness_rating = self._get_rating("Helpfulness and usefulness (1-5): ")
        
        # Collect emotional response
        print("\n💭 How did this companion make you feel?")
        emotional_response = input("Emotional response: ").strip()
        
        # Collect suggestions
        suggestions = []
        print("\n💡 Suggestions for improvement (press Enter when done):")
        while True:
            suggestion = input("Suggestion: ").strip()
            if not suggestion:
                break
            suggestions.append(suggestion)
        
        return {
            "introduction_rating": introduction_rating,
            "clarity_rating": clarity_rating,
            "helpfulness_rating": helpfulness_rating,
            "emotional_response": emotional_response,
            "suggestions": suggestions
        }
    
    def show_issue_report_prompt(self) -> Dict[str, Any]:
        """
        Show issue report prompt.
        
        Returns:
            Issue report data
        """
        print(f"\n{'='*60}")
        print("🐛 Report an Issue")
        print(f"{'='*60}")
        
        title = input("Issue title: ").strip()
        description = input("Issue description: ").strip()
        
        print("\nSeverity level:")
        print("1. Low - Minor inconvenience")
        print("2. Medium - Some impact on functionality")
        print("3. High - Significant impact on functionality")
        print("4. Critical - System unusable")
        
        severity_choice = input("Choose severity (1-4): ").strip()
        severity_map = {
            "1": FeedbackSeverity.LOW,
            "2": FeedbackSeverity.MEDIUM,
            "3": FeedbackSeverity.HIGH,
            "4": FeedbackSeverity.CRITICAL
        }
        severity = severity_map.get(severity_choice, FeedbackSeverity.MEDIUM)
        
        steps_to_reproduce = []
        print("\nSteps to reproduce (press Enter when done):")
        while True:
            step = input("Step: ").strip()
            if not step:
                break
            steps_to_reproduce.append(step)
        
        expected_behavior = input("\nExpected behavior: ").strip()
        actual_behavior = input("Actual behavior: ").strip()
        
        return {
            "title": title,
            "description": description,
            "severity": severity,
            "steps_to_reproduce": steps_to_reproduce,
            "expected_behavior": expected_behavior,
            "actual_behavior": actual_behavior
        }
    
    def _get_rating(self, prompt: str) -> int:
        """Get a rating from user input."""
        while True:
            try:
                rating = int(input(prompt))
                if 1 <= rating <= 5:
                    return rating
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
    
    def show_feedback_summary(self, summary: Dict[str, Any]):
        """Show feedback summary to user."""
        print(f"\n{'='*60}")
        print("📊 Feedback Summary")
        print(f"{'='*60}")
        
        if "installation_steps" in summary:
            print(f"Installation Steps: {summary['total_steps']}")
            print(f"Successful: {summary['successful_steps']}")
            print(f"Failed: {summary['failed_steps']}")
        
        if "onboarding_experiences" in summary:
            print(f"Personas Experienced: {summary['total_personas']}")
            avg_ratings = summary.get('average_ratings', {})
            if avg_ratings:
                print(f"Average Introduction Rating: {avg_ratings.get('introduction', 0):.1f}/5")
                print(f"Average Clarity Rating: {avg_ratings.get('clarity', 0):.1f}/5")
                print(f"Average Helpfulness Rating: {avg_ratings.get('helpfulness', 0):.1f}/5")
        
        print(f"\nThank you for your feedback! It helps us improve Hearthlink for everyone.")
        print(f"{'='*60}") 