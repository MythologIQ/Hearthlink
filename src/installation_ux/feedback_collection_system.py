"""
Feedback Collection System - User Experience Analytics

Provides comprehensive feedback collection, logging, and analysis for user installations
and onboarding experiences. Integrates with GitHub Issues for bug reports and feature requests.
"""

import json
import time
import logging
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from pathlib import Path

class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    INSTALLATION = "installation"
    ONBOARDING = "onboarding"
    PERSONA_INTRO = "persona_introduction"
    USABILITY = "usability"
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"

class FeedbackSeverity(Enum):
    """Severity levels for feedback."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FeedbackStatus(Enum):
    """Status of feedback processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class UserFeedback:
    """Complete user feedback entry."""
    feedback_id: str
    user_id: str
    session_id: str
    feedback_type: FeedbackType
    severity: FeedbackSeverity
    status: FeedbackStatus
    timestamp: datetime
    title: str
    description: str
    user_experience: str
    suggestions: List[str]
    metadata: Dict[str, Any]
    github_issue_id: Optional[str] = None
    tags: List[str] = None

@dataclass
class InstallationFeedback:
    """Specific feedback for installation process."""
    feedback_id: str
    user_id: str
    session_id: str
    installation_step: str
    success: bool
    duration_seconds: float
    error_message: Optional[str] = None
    system_info: Dict[str, Any] = None
    user_actions: List[str] = None
    suggestions: List[str] = None

@dataclass
class OnboardingFeedback:
    """Specific feedback for onboarding experience."""
    feedback_id: str
    user_id: str
    session_id: str
    persona_name: str
    introduction_rating: int  # 1-5 scale
    clarity_rating: int  # 1-5 scale
    helpfulness_rating: int  # 1-5 scale
    emotional_response: str
    suggestions: List[str] = None
    completion_time: float = None
    skipped_steps: List[str] = None

class FeedbackCollectionSystem:
    """
    Comprehensive feedback collection and analysis system.
    
    Collects user feedback from installations and onboarding experiences,
    integrates with GitHub Issues, and provides analytics for continuous improvement.
    """
    
    def __init__(self, config_path: Optional[str] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize Feedback Collection System.
        
        Args:
            config_path: Path to configuration file
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize storage
        self.feedback_storage = self._initialize_storage()
        
        # GitHub integration
        self.github_client = self._initialize_github_client()
        
        # Analytics tracking
        self.analytics = {}
        
        self._log("feedback_collection_system_initialized", "system", None, "system", {})
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load feedback collection configuration."""
        default_config = {
            "storage": {
                "feedback_file": "feedback_data.json",
                "analytics_file": "feedback_analytics.json",
                "backup_interval": 3600  # 1 hour
            },
            "github": {
                "enabled": False,
                "repository": "your-org/hearthlink",
                "token": None,
                "labels": {
                    "bug": "bug",
                    "enhancement": "enhancement",
                    "documentation": "documentation",
                    "feedback": "feedback"
                }
            },
            "feedback": {
                "auto_github_issues": True,
                "min_severity_for_github": FeedbackSeverity.MEDIUM,
                "collect_system_info": True,
                "anonymize_data": True
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_storage(self) -> Dict[str, Any]:
        """Initialize feedback storage."""
        storage_dir = Path("feedback_data")
        storage_dir.mkdir(exist_ok=True)
        
        feedback_file = storage_dir / self.config["storage"]["feedback_file"]
        analytics_file = storage_dir / self.config["storage"]["analytics_file"]
        
        return {
            "feedback_file": feedback_file,
            "analytics_file": analytics_file,
            "feedback_data": self._load_feedback_data(feedback_file),
            "analytics_data": self._load_analytics_data(analytics_file)
        }
    
    def _initialize_github_client(self) -> Optional[Any]:
        """Initialize GitHub client for issue creation."""
        if not self.config["github"]["enabled"]:
            return None
        
        try:
            # Simple GitHub API client
            return {
                "token": self.config["github"]["token"],
                "repo": self.config["github"]["repository"],
                "labels": self.config["github"]["labels"]
            }
        except Exception as e:
            self.logger.warning(f"Failed to initialize GitHub client: {e}")
            return None
    
    def collect_installation_feedback(self, user_id: str, session_id: str, 
                                    installation_step: str, success: bool,
                                    duration_seconds: float, error_message: Optional[str] = None,
                                    suggestions: Optional[List[str]] = None) -> str:
        """
        Collect feedback from installation process.
        
        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            installation_step: Current installation step
            success: Whether the step was successful
            duration_seconds: Time taken for the step
            error_message: Error message if failed
            suggestions: User suggestions for improvement
            
        Returns:
            Feedback ID
        """
        try:
            feedback_id = self._generate_feedback_id()
            
            # Collect system information
            system_info = self._collect_system_info() if self.config["feedback"]["collect_system_info"] else {}
            
            feedback = InstallationFeedback(
                feedback_id=feedback_id,
                user_id=user_id,
                session_id=session_id,
                installation_step=installation_step,
                success=success,
                duration_seconds=duration_seconds,
                error_message=error_message,
                system_info=system_info,
                user_actions=[],
                suggestions=suggestions or []
            )
            
            # Store feedback
            self._store_feedback(feedback_id, asdict(feedback))
            
            # Update analytics
            self._update_installation_analytics(feedback)
            
            # Create GitHub issue if needed
            if not success and self.config["feedback"]["auto_github_issues"]:
                self._create_github_issue(feedback, FeedbackType.INSTALLATION)
            
            self._log("installation_feedback_collected", user_id, session_id, "feedback", 
                     {"feedback_id": feedback_id, "step": installation_step, "success": success})
            
            return feedback_id
            
        except Exception as e:
            self._log("installation_feedback_failed", user_id, session_id, "feedback", 
                     {"step": installation_step}, "error", e)
            raise
    
    def collect_onboarding_feedback(self, user_id: str, session_id: str, persona_name: str,
                                  introduction_rating: int, clarity_rating: int, 
                                  helpfulness_rating: int, emotional_response: str,
                                  suggestions: Optional[List[str]] = None,
                                  completion_time: Optional[float] = None,
                                  skipped_steps: Optional[List[str]] = None) -> str:
        """
        Collect feedback from onboarding experience.
        
        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            persona_name: Name of the persona
            introduction_rating: Rating of introduction (1-5)
            clarity_rating: Rating of clarity (1-5)
            helpfulness_rating: Rating of helpfulness (1-5)
            emotional_response: User's emotional response
            suggestions: User suggestions for improvement
            completion_time: Time to complete onboarding
            skipped_steps: Steps that were skipped
            
        Returns:
            Feedback ID
        """
        try:
            feedback_id = self._generate_feedback_id()
            
            feedback = OnboardingFeedback(
                feedback_id=feedback_id,
                user_id=user_id,
                session_id=session_id,
                persona_name=persona_name,
                introduction_rating=introduction_rating,
                clarity_rating=clarity_rating,
                helpfulness_rating=helpfulness_rating,
                emotional_response=emotional_response,
                suggestions=suggestions or [],
                completion_time=completion_time,
                skipped_steps=skipped_steps or []
            )
            
            # Store feedback
            self._store_feedback(feedback_id, asdict(feedback))
            
            # Update analytics
            self._update_onboarding_analytics(feedback)
            
            # Create GitHub issue for low ratings
            if (introduction_rating <= 2 or clarity_rating <= 2 or helpfulness_rating <= 2) and \
               self.config["feedback"]["auto_github_issues"]:
                self._create_github_issue(feedback, FeedbackType.ONBOARDING)
            
            self._log("onboarding_feedback_collected", user_id, session_id, "feedback", 
                     {"feedback_id": feedback_id, "persona": persona_name})
            
            return feedback_id
            
        except Exception as e:
            self._log("onboarding_feedback_failed", user_id, session_id, "feedback", 
                     {"persona": persona_name}, "error", e)
            raise
    
    def collect_general_feedback(self, user_id: str, session_id: str, title: str,
                               description: str, feedback_type: FeedbackType,
                               severity: FeedbackSeverity, suggestions: Optional[List[str]] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Collect general user feedback.
        
        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            title: Feedback title
            description: Detailed feedback description
            feedback_type: Type of feedback
            severity: Severity level
            suggestions: User suggestions
            metadata: Additional metadata
            
        Returns:
            Feedback ID
        """
        try:
            feedback_id = self._generate_feedback_id()
            
            feedback = UserFeedback(
                feedback_id=feedback_id,
                user_id=user_id,
                session_id=session_id,
                feedback_type=feedback_type,
                severity=severity,
                status=FeedbackStatus.PENDING,
                timestamp=datetime.now(timezone.utc),
                title=title,
                description=description,
                user_experience=description,
                suggestions=suggestions or [],
                metadata=metadata or {},
                tags=[]
            )
            
            # Store feedback
            self._store_feedback(feedback_id, asdict(feedback))
            
            # Update analytics
            self._update_general_analytics(feedback)
            
            # Create GitHub issue if needed
            if (severity.value in [FeedbackSeverity.HIGH.value, FeedbackSeverity.CRITICAL.value] or
                feedback_type in [FeedbackType.BUG_REPORT, FeedbackType.FEATURE_REQUEST]) and \
               self.config["feedback"]["auto_github_issues"]:
                self._create_github_issue(feedback, feedback_type)
            
            self._log("general_feedback_collected", user_id, session_id, "feedback", 
                     {"feedback_id": feedback_id, "type": feedback_type.value, "severity": severity.value})
            
            return feedback_id
            
        except Exception as e:
            self._log("general_feedback_failed", user_id, session_id, "feedback", 
                     {"type": feedback_type.value}, "error", e)
            raise
    
    def report_issue(self, user_id: str, session_id: str, title: str, description: str,
                    severity: FeedbackSeverity, steps_to_reproduce: Optional[List[str]] = None,
                    expected_behavior: Optional[str] = None, actual_behavior: Optional[str] = None,
                    system_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Report an issue directly to GitHub Issues.
        
        Args:
            user_id: Unique user identifier
            session_id: Session identifier
            title: Issue title
            description: Issue description
            severity: Issue severity
            steps_to_reproduce: Steps to reproduce the issue
            expected_behavior: Expected behavior
            actual_behavior: Actual behavior
            system_info: System information
            
        Returns:
            GitHub issue ID
        """
        try:
            # Collect system information if not provided
            if not system_info and self.config["feedback"]["collect_system_info"]:
                system_info = self._collect_system_info()
            
            # Create detailed issue description
            issue_description = self._format_issue_description(
                description, steps_to_reproduce, expected_behavior, 
                actual_behavior, system_info, user_id, session_id
            )
            
            # Create GitHub issue
            issue_id = self._create_github_issue_direct(
                title, issue_description, severity, FeedbackType.BUG_REPORT
            )
            
            # Store feedback locally
            feedback_id = self.collect_general_feedback(
                user_id, session_id, title, description, FeedbackType.BUG_REPORT,
                severity, metadata={"github_issue_id": issue_id, "system_info": system_info}
            )
            
            self._log("issue_reported", user_id, session_id, "github_issue", 
                     {"feedback_id": feedback_id, "github_issue_id": issue_id})
            
            return issue_id
            
        except Exception as e:
            self._log("issue_report_failed", user_id, session_id, "github_issue", 
                     {"title": title}, "error", e)
            raise
    
    def get_feedback_analytics(self, feedback_type: Optional[FeedbackType] = None,
                             time_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Get analytics for collected feedback.
        
        Args:
            feedback_type: Filter by feedback type
            time_range: Filter by time range
            
        Returns:
            Analytics data
        """
        try:
            analytics = self.storage["analytics_data"].copy()
            
            # Filter by type if specified
            if feedback_type:
                analytics = {k: v for k, v in analytics.items() 
                           if k.startswith(feedback_type.value)}
            
            # Filter by time range if specified
            if time_range:
                start_time = time_range.get("start")
                end_time = time_range.get("end")
                if start_time or end_time:
                    analytics = self._filter_analytics_by_time(analytics, start_time, end_time)
            
            return analytics
            
        except Exception as e:
            self._log("analytics_retrieval_failed", "system", None, "analytics", 
                     {"feedback_type": feedback_type.value if feedback_type else None}, "error", e)
            return {}
    
    def generate_improvement_report(self) -> Dict[str, Any]:
        """
        Generate improvement report based on collected feedback.
        
        Returns:
            Improvement report with actionable insights
        """
        try:
            report = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "summary": {},
                "installation_issues": [],
                "onboarding_improvements": [],
                "usability_insights": [],
                "documentation_updates": [],
                "github_issues_created": 0
            }
            
            # Analyze installation feedback
            installation_data = self._analyze_installation_feedback()
            report["installation_issues"] = installation_data["issues"]
            report["summary"]["installation_success_rate"] = installation_data["success_rate"]
            
            # Analyze onboarding feedback
            onboarding_data = self._analyze_onboarding_feedback()
            report["onboarding_improvements"] = onboarding_data["improvements"]
            report["summary"]["average_onboarding_rating"] = onboarding_data["average_rating"]
            
            # Analyze general feedback
            general_data = self._analyze_general_feedback()
            report["usability_insights"] = general_data["insights"]
            report["documentation_updates"] = general_data["documentation_needs"]
            
            # Count GitHub issues
            report["github_issues_created"] = self._count_github_issues()
            
            return report
            
        except Exception as e:
            self._log("improvement_report_generation_failed", "system", None, "analytics", {}, "error", e)
            return {"error": str(e)}
    
    def _generate_feedback_id(self) -> str:
        """Generate unique feedback ID."""
        timestamp = str(time.time())
        random_component = str(hash(timestamp) % 10000)
        return f"feedback_{timestamp}_{random_component}"
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for feedback."""
        import platform
        import sys
        
        return {
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _store_feedback(self, feedback_id: str, feedback_data: Dict[str, Any]) -> None:
        """Store feedback data."""
        self.storage["feedback_data"][feedback_id] = feedback_data
        self._save_feedback_data()
    
    def _update_installation_analytics(self, feedback: InstallationFeedback) -> None:
        """Update installation analytics."""
        analytics = self.storage["analytics_data"]
        
        if "installation" not in analytics:
            analytics["installation"] = {
                "total_attempts": 0,
                "successful_attempts": 0,
                "failed_attempts": 0,
                "average_duration": 0,
                "step_success_rates": {},
                "common_errors": {}
            }
        
        analytics["installation"]["total_attempts"] += 1
        
        if feedback.success:
            analytics["installation"]["successful_attempts"] += 1
        else:
            analytics["installation"]["failed_attempts"] += 1
            if feedback.error_message:
                error_key = feedback.error_message[:50]
                analytics["installation"]["common_errors"][error_key] = \
                    analytics["installation"]["common_errors"].get(error_key, 0) + 1
        
        # Update step success rate
        step = feedback.installation_step
        if step not in analytics["installation"]["step_success_rates"]:
            analytics["installation"]["step_success_rates"][step] = {"success": 0, "total": 0}
        
        analytics["installation"]["step_success_rates"][step]["total"] += 1
        if feedback.success:
            analytics["installation"]["step_success_rates"][step]["success"] += 1
        
        # Update average duration
        current_avg = analytics["installation"]["average_duration"]
        total_attempts = analytics["installation"]["total_attempts"]
        analytics["installation"]["average_duration"] = \
            (current_avg * (total_attempts - 1) + feedback.duration_seconds) / total_attempts
        
        self._save_analytics_data()
    
    def _update_onboarding_analytics(self, feedback: OnboardingFeedback) -> None:
        """Update onboarding analytics."""
        analytics = self.storage["analytics_data"]
        
        if "onboarding" not in analytics:
            analytics["onboarding"] = {
                "total_feedback": 0,
                "average_ratings": {},
                "persona_ratings": {},
                "emotional_responses": {},
                "completion_times": [],
                "skipped_steps": {}
            }
        
        analytics["onboarding"]["total_feedback"] += 1
        
        # Update average ratings
        ratings = ["introduction", "clarity", "helpfulness"]
        for rating_type in ratings:
            rating_value = getattr(feedback, f"{rating_type}_rating")
            if rating_type not in analytics["onboarding"]["average_ratings"]:
                analytics["onboarding"]["average_ratings"][rating_type] = []
            analytics["onboarding"]["average_ratings"][rating_type].append(rating_value)
        
        # Update persona-specific ratings
        persona = feedback.persona_name
        if persona not in analytics["onboarding"]["persona_ratings"]:
            analytics["onboarding"]["persona_ratings"][persona] = {
                "total": 0,
                "average_introduction": 0,
                "average_clarity": 0,
                "average_helpfulness": 0
            }
        
        persona_data = analytics["onboarding"]["persona_ratings"][persona]
        persona_data["total"] += 1
        
        # Update emotional responses
        emotion = feedback.emotional_response
        if emotion not in analytics["onboarding"]["emotional_responses"]:
            analytics["onboarding"]["emotional_responses"][emotion] = 0
        analytics["onboarding"]["emotional_responses"][emotion] += 1
        
        # Update completion times
        if feedback.completion_time:
            analytics["onboarding"]["completion_times"].append(feedback.completion_time)
        
        # Update skipped steps
        for step in feedback.skipped_steps or []:
            if step not in analytics["onboarding"]["skipped_steps"]:
                analytics["onboarding"]["skipped_steps"][step] = 0
            analytics["onboarding"]["skipped_steps"][step] += 1
        
        self._save_analytics_data()
    
    def _update_general_analytics(self, feedback: UserFeedback) -> None:
        """Update general feedback analytics."""
        analytics = self.storage["analytics_data"]
        
        if "general" not in analytics:
            analytics["general"] = {
                "total_feedback": 0,
                "feedback_by_type": {},
                "feedback_by_severity": {},
                "common_suggestions": {},
                "github_issues_created": 0
            }
        
        analytics["general"]["total_feedback"] += 1
        
        # Update feedback by type
        feedback_type = feedback.feedback_type.value
        if feedback_type not in analytics["general"]["feedback_by_type"]:
            analytics["general"]["feedback_by_type"][feedback_type] = 0
        analytics["general"]["feedback_by_type"][feedback_type] += 1
        
        # Update feedback by severity
        severity = feedback.severity.value
        if severity not in analytics["general"]["feedback_by_severity"]:
            analytics["general"]["feedback_by_severity"][severity] = 0
        analytics["general"]["feedback_by_severity"][severity] += 1
        
        # Update common suggestions
        for suggestion in feedback.suggestions:
            suggestion_key = suggestion[:50]
            if suggestion_key not in analytics["general"]["common_suggestions"]:
                analytics["general"]["common_suggestions"][suggestion_key] = 0
            analytics["general"]["common_suggestions"][suggestion_key] += 1
        
        self._save_analytics_data()
    
    def _create_github_issue(self, feedback: Union[InstallationFeedback, OnboardingFeedback, UserFeedback], 
                           feedback_type: FeedbackType) -> Optional[str]:
        """Create GitHub issue from feedback."""
        if not self.github_client:
            return None
        
        try:
            title = self._format_issue_title(feedback, feedback_type)
            description = self._format_issue_description_from_feedback(feedback, feedback_type)
            labels = self._get_issue_labels(feedback_type, getattr(feedback, 'severity', FeedbackSeverity.MEDIUM))
            
            issue_id = self._create_github_issue_direct(title, description, labels)
            
            # Update feedback with GitHub issue ID
            if hasattr(feedback, 'feedback_id'):
                self.storage["feedback_data"][feedback.feedback_id]["github_issue_id"] = issue_id
                self._save_feedback_data()
            
            return issue_id
            
        except Exception as e:
            self.logger.error(f"Failed to create GitHub issue: {e}")
            return None
    
    def _create_github_issue_direct(self, title: str, description: str, 
                                  severity: FeedbackSeverity, feedback_type: FeedbackType) -> str:
        """Create GitHub issue directly."""
        if not self.github_client:
            raise Exception("GitHub integration not configured")
        
        labels = self._get_issue_labels(feedback_type, severity)
        
        issue_data = {
            "title": title,
            "body": description,
            "labels": labels
        }
        
        headers = {
            "Authorization": f"token {self.github_client['token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"https://api.github.com/repos/{self.github_client['repo']}/issues"
        
        response = requests.post(url, json=issue_data, headers=headers)
        response.raise_for_status()
        
        issue_response = response.json()
        return str(issue_response["number"])
    
    def _format_issue_title(self, feedback: Union[InstallationFeedback, OnboardingFeedback, UserFeedback], 
                          feedback_type: FeedbackType) -> str:
        """Format issue title from feedback."""
        if feedback_type == FeedbackType.INSTALLATION:
            return f"Installation Issue: {feedback.installation_step}"
        elif feedback_type == FeedbackType.ONBOARDING:
            return f"Onboarding Feedback: {feedback.persona_name}"
        else:
            return getattr(feedback, 'title', f"{feedback_type.value.title()} Feedback")
    
    def _format_issue_description(self, description: str, steps_to_reproduce: Optional[List[str]] = None,
                                expected_behavior: Optional[str] = None, actual_behavior: Optional[str] = None,
                                system_info: Optional[Dict[str, Any]] = None, user_id: str = None,
                                session_id: str = None) -> str:
        """Format issue description."""
        issue_body = f"## Description\n{description}\n\n"
        
        if steps_to_reproduce:
            issue_body += "## Steps to Reproduce\n"
            for i, step in enumerate(steps_to_reproduce, 1):
                issue_body += f"{i}. {step}\n"
            issue_body += "\n"
        
        if expected_behavior:
            issue_body += f"## Expected Behavior\n{expected_behavior}\n\n"
        
        if actual_behavior:
            issue_body += f"## Actual Behavior\n{actual_behavior}\n\n"
        
        if system_info:
            issue_body += "## System Information\n"
            for key, value in system_info.items():
                issue_body += f"- **{key}**: {value}\n"
            issue_body += "\n"
        
        if user_id or session_id:
            issue_body += "## User Information\n"
            if user_id:
                issue_body += f"- **User ID**: {user_id}\n"
            if session_id:
                issue_body += f"- **Session ID**: {session_id}\n"
            issue_body += "\n"
        
        issue_body += f"---\n*Reported via Hearthlink Feedback System at {datetime.now(timezone.utc).isoformat()}*"
        
        return issue_body
    
    def _format_issue_description_from_feedback(self, feedback: Union[InstallationFeedback, OnboardingFeedback, UserFeedback], 
                                              feedback_type: FeedbackType) -> str:
        """Format issue description from feedback object."""
        if feedback_type == FeedbackType.INSTALLATION:
            return self._format_installation_issue_description(feedback)
        elif feedback_type == FeedbackType.ONBOARDING:
            return self._format_onboarding_issue_description(feedback)
        else:
            return self._format_general_issue_description(feedback)
    
    def _format_installation_issue_description(self, feedback: InstallationFeedback) -> str:
        """Format installation issue description."""
        description = f"## Installation Issue\n\n"
        description += f"**Step**: {feedback.installation_step}\n"
        description += f"**Success**: {'Yes' if feedback.success else 'No'}\n"
        description += f"**Duration**: {feedback.duration_seconds:.2f} seconds\n\n"
        
        if feedback.error_message:
            description += f"**Error Message**: {feedback.error_message}\n\n"
        
        if feedback.suggestions:
            description += "**User Suggestions**:\n"
            for suggestion in feedback.suggestions:
                description += f"- {suggestion}\n"
            description += "\n"
        
        if feedback.system_info:
            description += "**System Information**:\n"
            for key, value in feedback.system_info.items():
                description += f"- **{key}**: {value}\n"
            description += "\n"
        
        description += f"---\n*Reported via Hearthlink Feedback System at {datetime.now(timezone.utc).isoformat()}*"
        
        return description
    
    def _format_onboarding_issue_description(self, feedback: OnboardingFeedback) -> str:
        """Format onboarding issue description."""
        description = f"## Onboarding Feedback\n\n"
        description += f"**Persona**: {feedback.persona_name}\n"
        description += f"**Introduction Rating**: {feedback.introduction_rating}/5\n"
        description += f"**Clarity Rating**: {feedback.clarity_rating}/5\n"
        description += f"**Helpfulness Rating**: {feedback.helpfulness_rating}/5\n"
        description += f"**Emotional Response**: {feedback.emotional_response}\n\n"
        
        if feedback.completion_time:
            description += f"**Completion Time**: {feedback.completion_time:.2f} seconds\n\n"
        
        if feedback.skipped_steps:
            description += "**Skipped Steps**:\n"
            for step in feedback.skipped_steps:
                description += f"- {step}\n"
            description += "\n"
        
        if feedback.suggestions:
            description += "**User Suggestions**:\n"
            for suggestion in feedback.suggestions:
                description += f"- {suggestion}\n"
            description += "\n"
        
        description += f"---\n*Reported via Hearthlink Feedback System at {datetime.now(timezone.utc).isoformat()}*"
        
        return description
    
    def _format_general_issue_description(self, feedback: UserFeedback) -> str:
        """Format general issue description."""
        description = f"## {feedback.feedback_type.value.title()} Feedback\n\n"
        description += f"**Title**: {feedback.title}\n"
        description += f"**Severity**: {feedback.severity.value}\n"
        description += f"**Description**: {feedback.description}\n\n"
        
        if feedback.suggestions:
            description += "**User Suggestions**:\n"
            for suggestion in feedback.suggestions:
                description += f"- {suggestion}\n"
            description += "\n"
        
        if feedback.metadata:
            description += "**Additional Information**:\n"
            for key, value in feedback.metadata.items():
                description += f"- **{key}**: {value}\n"
            description += "\n"
        
        description += f"---\n*Reported via Hearthlink Feedback System at {datetime.now(timezone.utc).isoformat()}*"
        
        return description
    
    def _get_issue_labels(self, feedback_type: FeedbackType, severity: FeedbackSeverity) -> List[str]:
        """Get GitHub issue labels."""
        labels = []
        
        # Add type label
        if feedback_type == FeedbackType.BUG_REPORT:
            labels.append(self.github_client["labels"]["bug"])
        elif feedback_type == FeedbackType.FEATURE_REQUEST:
            labels.append(self.github_client["labels"]["enhancement"])
        else:
            labels.append(self.github_client["labels"]["feedback"])
        
        # Add severity label
        labels.append(f"severity-{severity.value}")
        
        # Add type-specific label
        labels.append(f"type-{feedback_type.value}")
        
        return labels
    
    def _load_feedback_data(self, file_path: Path) -> Dict[str, Any]:
        """Load feedback data from file."""
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load feedback data: {e}")
        return {}
    
    def _load_analytics_data(self, file_path: Path) -> Dict[str, Any]:
        """Load analytics data from file."""
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load analytics data: {e}")
        return {}
    
    def _save_feedback_data(self) -> None:
        """Save feedback data to file."""
        try:
            with open(self.storage["feedback_file"], 'w') as f:
                json.dump(self.storage["feedback_data"], f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save feedback data: {e}")
    
    def _save_analytics_data(self) -> None:
        """Save analytics data to file."""
        try:
            with open(self.storage["analytics_file"], 'w') as f:
                json.dump(self.storage["analytics_data"], f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save analytics data: {e}")
    
    def _log(self, action: str, user_id: str, session_id, event_type: str, 
             details: Dict[str, Any], result: str = "success", error=None):
        """Log feedback collection events."""
        log_entry = {
            "timestamp": time.time(),
            "action": action,
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "details": details,
            "result": result if not error else f"error: {str(error)}"
        }
        
        self.logger.info(f"Feedback Collection: {action} - {result}")
        
        if error:
            self.logger.error(f"Feedback Collection error: {str(error)}") 