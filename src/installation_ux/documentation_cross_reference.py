"""
Documentation Cross-Reference System - Continuous Improvement

Automatically updates documentation based on user feedback and lessons learned,
ensuring continuous improvement of installation and onboarding processes.
"""

import re
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict

from feedback_collection_system import FeedbackType, FeedbackSeverity

@dataclass
class DocumentationUpdate:
    """Documentation update entry."""
    update_id: str
    timestamp: datetime
    feedback_id: str
    document_path: str
    section: str
    update_type: str  # "addition", "modification", "clarification", "fix"
    description: str
    changes: List[str]
    impact: str
    status: str  # "pending", "applied", "reviewed"

@dataclass
class LessonLearned:
    """Lesson learned from user feedback."""
    lesson_id: str
    timestamp: datetime
    feedback_ids: List[str]
    category: str
    title: str
    description: str
    impact: str
    recommendations: List[str]
    documentation_updates: List[str]
    status: str  # "identified", "implemented", "verified"

class DocumentationCrossReference:
    """
    Documentation cross-reference system for continuous improvement.
    
    Analyzes user feedback to identify lessons learned and automatically
    suggests documentation updates for continuous improvement.
    """
    
    def __init__(self, docs_directory: str = "docs"):
        """
        Initialize Documentation Cross-Reference System.
        
        Args:
            docs_directory: Path to documentation directory
        """
        self.docs_directory = Path(docs_directory)
        self.lessons_learned_file = self.docs_directory / "LESSONS_LEARNED.md"
        self.feedback_insights_file = self.docs_directory / "FEEDBACK_INSIGHTS.md"
        self.documentation_updates_file = self.docs_directory / "DOCUMENTATION_UPDATES.md"
        
        # Load existing data
        self.lessons_learned = self._load_lessons_learned()
        self.documentation_updates = self._load_documentation_updates()
        self.feedback_insights = self._load_feedback_insights()
        
        # Documentation mapping
        self.doc_mapping = {
            "installation": ["process_refinement.md", "INSTALLATION_GUIDE.md"],
            "onboarding": ["PERSONA_ONBOARDING_DOCUMENTATION.md", "process_refinement.md"],
            "persona_introduction": ["PERSONA_ONBOARDING_DOCUMENTATION.md"],
            "usability": ["process_refinement.md", "FEATURE_WISHLIST.md"],
            "bug_report": ["process_refinement.md", "PLATINUM_BLOCKERS.md"],
            "feature_request": ["FEATURE_WISHLIST.md", "process_refinement.md"]
        }
    
    def analyze_feedback_for_lessons(self, feedback_data: Dict[str, Any]) -> List[LessonLearned]:
        """
        Analyze feedback data to identify lessons learned.
        
        Args:
            feedback_data: Feedback data from collection system
            
        Returns:
            List of lessons learned
        """
        lessons = []
        
        # Analyze installation feedback
        installation_lessons = self._analyze_installation_feedback(feedback_data)
        lessons.extend(installation_lessons)
        
        # Analyze onboarding feedback
        onboarding_lessons = self._analyze_onboarding_feedback(feedback_data)
        lessons.extend(onboarding_lessons)
        
        # Analyze general feedback
        general_lessons = self._analyze_general_feedback(feedback_data)
        lessons.extend(general_lessons)
        
        # Save lessons learned
        self._save_lessons_learned(lessons)
        
        return lessons
    
    def generate_documentation_updates(self, lessons_learned: List[LessonLearned]) -> List[DocumentationUpdate]:
        """
        Generate documentation updates based on lessons learned.
        
        Args:
            lessons_learned: List of lessons learned
            
        Returns:
            List of documentation updates
        """
        updates = []
        
        for lesson in lessons_learned:
            lesson_updates = self._generate_updates_for_lesson(lesson)
            updates.extend(lesson_updates)
        
        # Save documentation updates
        self._save_documentation_updates(updates)
        
        return updates
    
    def update_documentation_with_insights(self, feedback_analytics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update documentation with insights from feedback analytics.
        
        Args:
            feedback_analytics: Analytics data from feedback system
            
        Returns:
            Summary of updates made
        """
        insights = self._extract_insights_from_analytics(feedback_analytics)
        
        # Update process refinement document
        process_updates = self._update_process_refinement(insights)
        
        # Update onboarding documentation
        onboarding_updates = self._update_onboarding_documentation(insights)
        
        # Update feature wishlist
        wishlist_updates = self._update_feature_wishlist(insights)
        
        # Save insights
        self._save_feedback_insights(insights)
        
        return {
            "process_refinement_updates": process_updates,
            "onboarding_updates": onboarding_updates,
            "wishlist_updates": wishlist_updates,
            "insights_generated": len(insights)
        }
    
    def cross_reference_feedback_in_documentation(self, feedback_id: str, 
                                                feedback_type: FeedbackType,
                                                feedback_content: Dict[str, Any]) -> List[str]:
        """
        Cross-reference feedback in relevant documentation.
        
        Args:
            feedback_id: Feedback identifier
            feedback_type: Type of feedback
            feedback_content: Feedback content
            
        Returns:
            List of documentation files that should be updated
        """
        relevant_docs = self.doc_mapping.get(feedback_type.value, [])
        cross_references = []
        
        for doc_name in relevant_docs:
            doc_path = self.docs_directory / doc_name
            if doc_path.exists():
                cross_references.append(str(doc_path))
                
                # Add feedback reference to documentation
                self._add_feedback_reference(doc_path, feedback_id, feedback_content)
        
        return cross_references
    
    def _analyze_installation_feedback(self, feedback_data: Dict[str, Any]) -> List[LessonLearned]:
        """Analyze installation feedback for lessons learned."""
        lessons = []
        
        installation_data = feedback_data.get("installation", {})
        
        # Analyze common errors
        common_errors = installation_data.get("common_errors", {})
        if common_errors:
            error_lesson = LessonLearned(
                lesson_id=f"lesson_installation_errors_{int(time.time())}",
                timestamp=datetime.now(timezone.utc),
                feedback_ids=[],
                category="installation",
                title="Common Installation Errors Identified",
                description=f"Analysis of {len(common_errors)} common installation errors",
                impact="High - Affects user onboarding success",
                recommendations=[
                    "Improve error handling in installation steps",
                    "Add more detailed error messages",
                    "Provide troubleshooting guides for common issues"
                ],
                documentation_updates=[
                    "Update installation guide with troubleshooting section",
                    "Add error resolution steps to process refinement"
                ],
                status="identified"
            )
            lessons.append(error_lesson)
        
        # Analyze step success rates
        step_success_rates = installation_data.get("step_success_rates", {})
        problematic_steps = []
        
        for step, data in step_success_rates.items():
            success_rate = data.get("success", 0) / max(data.get("total", 1), 1)
            if success_rate < 0.8:  # Less than 80% success rate
                problematic_steps.append({
                    "step": step,
                    "success_rate": success_rate,
                    "total_attempts": data.get("total", 0)
                })
        
        if problematic_steps:
            step_lesson = LessonLearned(
                lesson_id=f"lesson_problematic_steps_{int(time.time())}",
                timestamp=datetime.now(timezone.utc),
                feedback_ids=[],
                category="installation",
                title="Problematic Installation Steps Identified",
                description=f"Found {len(problematic_steps)} steps with low success rates",
                impact="Medium - Affects installation completion",
                recommendations=[
                    "Review and simplify problematic installation steps",
                    "Add more detailed instructions for complex steps",
                    "Provide alternative installation methods"
                ],
                documentation_updates=[
                    "Update installation guide with clearer instructions",
                    "Add troubleshooting for specific problematic steps"
                ],
                status="identified"
            )
            lessons.append(step_lesson)
        
        return lessons
    
    def _analyze_onboarding_feedback(self, feedback_data: Dict[str, Any]) -> List[LessonLearned]:
        """Analyze onboarding feedback for lessons learned."""
        lessons = []
        
        onboarding_data = feedback_data.get("onboarding", {})
        
        # Analyze low ratings
        average_ratings = onboarding_data.get("average_ratings", {})
        low_rating_areas = []
        
        for rating_type, ratings in average_ratings.items():
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                if avg_rating < 3.5:  # Below 3.5/5
                    low_rating_areas.append({
                        "area": rating_type,
                        "average_rating": avg_rating,
                        "total_ratings": len(ratings)
                    })
        
        if low_rating_areas:
            rating_lesson = LessonLearned(
                lesson_id=f"lesson_low_ratings_{int(time.time())}",
                timestamp=datetime.now(timezone.utc),
                feedback_ids=[],
                category="onboarding",
                title="Low Onboarding Ratings Identified",
                description=f"Found {len(low_rating_areas)} areas with low user ratings",
                impact="High - Affects user satisfaction and adoption",
                recommendations=[
                    "Review and improve persona introduction scripts",
                    "Enhance clarity and helpfulness of onboarding content",
                    "Gather more detailed feedback on specific issues"
                ],
                documentation_updates=[
                    "Update persona onboarding documentation",
                    "Revise introduction scripts based on feedback"
                ],
                status="identified"
            )
            lessons.append(rating_lesson)
        
        # Analyze emotional responses
        emotional_responses = onboarding_data.get("emotional_responses", {})
        negative_emotions = []
        
        negative_keywords = ["confused", "frustrated", "overwhelmed", "disappointed", "annoyed"]
        for emotion, count in emotional_responses.items():
            if any(keyword in emotion.lower() for keyword in negative_keywords):
                negative_emotions.append({
                    "emotion": emotion,
                    "count": count
                })
        
        if negative_emotions:
            emotion_lesson = LessonLearned(
                lesson_id=f"lesson_negative_emotions_{int(time.time())}",
                timestamp=datetime.now(timezone.utc),
                feedback_ids=[],
                category="onboarding",
                title="Negative Emotional Responses Identified",
                description=f"Found {len(negative_emotions)} negative emotional responses",
                impact="High - Affects user emotional connection",
                recommendations=[
                    "Review and improve emotional tone of introductions",
                    "Add more reassuring and supportive language",
                    "Provide better emotional support during onboarding"
                ],
                documentation_updates=[
                    "Update persona introduction scripts for better emotional impact",
                    "Add emotional support guidelines to onboarding documentation"
                ],
                status="identified"
            )
            lessons.append(emotion_lesson)
        
        return lessons
    
    def _analyze_general_feedback(self, feedback_data: Dict[str, Any]) -> List[LessonLearned]:
        """Analyze general feedback for lessons learned."""
        lessons = []
        
        general_data = feedback_data.get("general", {})
        
        # Analyze common suggestions
        common_suggestions = general_data.get("common_suggestions", {})
        if common_suggestions:
            suggestion_lesson = LessonLearned(
                lesson_id=f"lesson_common_suggestions_{int(time.time())}",
                timestamp=datetime.now(timezone.utc),
                feedback_ids=[],
                category="general",
                title="Common User Suggestions Identified",
                description=f"Analysis of {len(common_suggestions)} common user suggestions",
                impact="Medium - Indicates user needs and preferences",
                recommendations=[
                    "Prioritize most frequently suggested improvements",
                    "Consider implementing high-impact suggestions",
                    "Communicate planned improvements to users"
                ],
                documentation_updates=[
                    "Update feature wishlist with user suggestions",
                    "Add user feedback summary to process refinement"
                ],
                status="identified"
            )
            lessons.append(suggestion_lesson)
        
        # Analyze feedback by severity
        feedback_by_severity = general_data.get("feedback_by_severity", {})
        high_severity_count = feedback_by_severity.get("high", 0) + feedback_by_severity.get("critical", 0)
        
        if high_severity_count > 0:
            severity_lesson = LessonLearned(
                lesson_id=f"lesson_high_severity_{int(time.time())}",
                timestamp=datetime.now(timezone.utc),
                feedback_ids=[],
                category="general",
                title="High Severity Issues Identified",
                description=f"Found {high_severity_count} high/critical severity issues",
                impact="Critical - Requires immediate attention",
                recommendations=[
                    "Prioritize resolution of high severity issues",
                    "Implement immediate fixes for critical issues",
                    "Establish escalation process for high severity feedback"
                ],
                documentation_updates=[
                    "Update platinum blockers documentation",
                    "Add high severity issue tracking to process refinement"
                ],
                status="identified"
            )
            lessons.append(severity_lesson)
        
        return lessons
    
    def _generate_updates_for_lesson(self, lesson: LessonLearned) -> List[DocumentationUpdate]:
        """Generate documentation updates for a specific lesson."""
        updates = []
        
        for doc_update in lesson.documentation_updates:
            update = DocumentationUpdate(
                update_id=f"update_{lesson.lesson_id}_{int(time.time())}",
                timestamp=datetime.now(timezone.utc),
                feedback_id="",  # Will be populated from lesson feedback_ids
                document_path=doc_update,
                section="Lessons Learned",
                update_type="addition",
                description=f"Update based on lesson: {lesson.title}",
                changes=[
                    f"Add lesson learned: {lesson.title}",
                    f"Impact: {lesson.impact}",
                    f"Recommendations: {', '.join(lesson.recommendations)}"
                ],
                impact=lesson.impact,
                status="pending"
            )
            updates.append(update)
        
        return updates
    
    def _extract_insights_from_analytics(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract insights from feedback analytics."""
        insights = []
        
        # Installation insights
        if "installation" in analytics:
            installation_data = analytics["installation"]
            
            if installation_data.get("successful_attempts", 0) > 0:
                success_rate = installation_data["successful_attempts"] / installation_data["total_attempts"]
                insights.append({
                    "category": "installation",
                    "insight": f"Installation success rate: {success_rate:.1%}",
                    "impact": "High" if success_rate < 0.9 else "Medium",
                    "recommendation": "Improve installation process" if success_rate < 0.9 else "Monitor for trends"
                })
        
        # Onboarding insights
        if "onboarding" in analytics:
            onboarding_data = analytics["onboarding"]
            
            avg_ratings = onboarding_data.get("average_ratings", {})
            for rating_type, ratings in avg_ratings.items():
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
                    insights.append({
                        "category": "onboarding",
                        "insight": f"Average {rating_type} rating: {avg_rating:.1f}/5",
                        "impact": "High" if avg_rating < 3.5 else "Medium",
                        "recommendation": f"Improve {rating_type} in onboarding" if avg_rating < 3.5 else "Maintain quality"
                    })
        
        return insights
    
    def _update_process_refinement(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Update process refinement document with insights."""
        updates = []
        
        process_refinement_path = self.docs_directory / "process_refinement.md"
        if not process_refinement_path.exists():
            return updates
        
        # Read current content
        with open(process_refinement_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add insights section if it doesn't exist
        if "## User Feedback Insights" not in content:
            insights_section = "\n\n## User Feedback Insights\n\n"
            insights_section += "This section is automatically updated based on user feedback analysis.\n\n"
            
            for insight in insights:
                insights_section += f"### {insight['category'].title()} Insight\n"
                insights_section += f"- **Insight**: {insight['insight']}\n"
                insights_section += f"- **Impact**: {insight['impact']}\n"
                insights_section += f"- **Recommendation**: {insight['recommendation']}\n\n"
            
            content += insights_section
            updates.append("Added User Feedback Insights section")
        
        # Write updated content
        with open(process_refinement_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return updates
    
    def _update_onboarding_documentation(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Update onboarding documentation with insights."""
        updates = []
        
        onboarding_doc_path = self.docs_directory / "PERSONA_ONBOARDING_DOCUMENTATION.md"
        if not onboarding_doc_path.exists():
            return updates
        
        # Read current content
        with open(onboarding_doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add feedback-based improvements section
        if "## Feedback-Based Improvements" not in content:
            improvements_section = "\n\n## Feedback-Based Improvements\n\n"
            improvements_section += "This section tracks improvements made based on user feedback.\n\n"
            
            onboarding_insights = [i for i in insights if i['category'] == 'onboarding']
            for insight in onboarding_insights:
                improvements_section += f"### {insight['insight']}\n"
                improvements_section += f"- **Recommendation**: {insight['recommendation']}\n"
                improvements_section += f"- **Status**: Under review\n\n"
            
            content += improvements_section
            updates.append("Added Feedback-Based Improvements section")
        
        # Write updated content
        with open(onboarding_doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return updates
    
    def _update_feature_wishlist(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Update feature wishlist with insights."""
        updates = []
        
        wishlist_path = self.docs_directory / "FEATURE_WISHLIST.md"
        if not wishlist_path.exists():
            return updates
        
        # Read current content
        with open(wishlist_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add user-requested features section
        if "## User-Requested Features" not in content:
            features_section = "\n\n## User-Requested Features\n\n"
            features_section += "Features requested by users through feedback system.\n\n"
            
            general_insights = [i for i in insights if i['category'] == 'general']
            for insight in general_insights:
                features_section += f"### {insight['insight']}\n"
                features_section += f"- **Priority**: {insight['impact']}\n"
                features_section += f"- **Status**: Under consideration\n\n"
            
            content += features_section
            updates.append("Added User-Requested Features section")
        
        # Write updated content
        with open(wishlist_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return updates
    
    def _add_feedback_reference(self, doc_path: Path, feedback_id: str, feedback_content: Dict[str, Any]):
        """Add feedback reference to documentation."""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add feedback reference section if it doesn't exist
            if "## Feedback References" not in content:
                feedback_section = "\n\n## Feedback References\n\n"
                feedback_section += "References to user feedback that influenced this documentation.\n\n"
                content += feedback_section
            
            # Add specific feedback reference
            feedback_entry = f"\n### Feedback {feedback_id}\n"
            feedback_entry += f"- **Type**: {feedback_content.get('type', 'Unknown')}\n"
            feedback_entry += f"- **Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n"
            feedback_entry += f"- **Impact**: {feedback_content.get('impact', 'Medium')}\n\n"
            
            # Insert before the end of the feedback section
            feedback_marker = "## Feedback References"
            if feedback_marker in content:
                parts = content.split(feedback_marker)
                content = parts[0] + feedback_marker + parts[1] + feedback_entry + parts[2] if len(parts) > 2 else parts[0] + feedback_marker + parts[1] + feedback_entry
            
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            print(f"Failed to add feedback reference to {doc_path}: {e}")
    
    def _load_lessons_learned(self) -> List[LessonLearned]:
        """Load lessons learned from file."""
        if self.lessons_learned_file.exists():
            try:
                with open(self.lessons_learned_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [LessonLearned(**lesson) for lesson in data]
            except Exception as e:
                print(f"Failed to load lessons learned: {e}")
        return []
    
    def _load_documentation_updates(self) -> List[DocumentationUpdate]:
        """Load documentation updates from file."""
        if self.documentation_updates_file.exists():
            try:
                with open(self.documentation_updates_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [DocumentationUpdate(**update) for update in data]
            except Exception as e:
                print(f"Failed to load documentation updates: {e}")
        return []
    
    def _load_feedback_insights(self) -> List[Dict[str, Any]]:
        """Load feedback insights from file."""
        if self.feedback_insights_file.exists():
            try:
                with open(self.feedback_insights_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load feedback insights: {e}")
        return []
    
    def _save_lessons_learned(self, lessons: List[LessonLearned]):
        """Save lessons learned to file."""
        try:
            with open(self.lessons_learned_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(lesson) for lesson in lessons], f, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save lessons learned: {e}")
    
    def _save_documentation_updates(self, updates: List[DocumentationUpdate]):
        """Save documentation updates to file."""
        try:
            with open(self.documentation_updates_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(update) for update in updates], f, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save documentation updates: {e}")
    
    def _save_feedback_insights(self, insights: List[Dict[str, Any]]):
        """Save feedback insights to file."""
        try:
            with open(self.feedback_insights_file, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, default=str)
        except Exception as e:
            print(f"Failed to save feedback insights: {e}") 