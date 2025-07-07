#!/usr/bin/env python3
"""
Mimic Integration with Core - Session Orchestration Integration

Integrates Mimic personas with Core session orchestration, enabling:
- Mimic personas to participate in multi-agent sessions
- Dynamic persona selection based on session context
- Performance tracking across sessions
- Knowledge sharing between personas and sessions

References:
- hearthlink_system_documentation_master.md: Core integration specifications
- PLATINUM_BLOCKERS.md: Security and compliance requirements

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import traceback
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.core import Core, Session, Participant, SessionEvent, ParticipantType
from personas.mimic import MimicPersona, MimicError, PerformanceTier
from main import HearthlinkLogger, HearthlinkError


class MimicIntegrationError(HearthlinkError):
    """Base exception for Mimic integration errors."""
    pass


class SessionIntegrationError(MimicIntegrationError):
    """Exception raised when session integration fails."""
    pass


class PersonaSelectionError(MimicIntegrationError):
    """Exception raised when persona selection fails."""
    pass


class KnowledgeSharingError(MimicIntegrationError):
    """Exception raised when knowledge sharing fails."""
    pass


@dataclass
class PersonaRecommendation:
    """Persona recommendation for session participation."""
    persona_id: str
    persona_name: str
    role: str
    confidence_score: float  # 0.0-1.0
    reasoning: str
    performance_tier: str
    relevant_knowledge: List[str] = field(default_factory=list)
    estimated_contribution: str = ""


@dataclass
class SessionInsight:
    """Insight generated during session participation."""
    insight_id: str
    session_id: str
    persona_id: str
    insight_type: str  # "knowledge", "strategy", "observation", "recommendation"
    content: str
    relevance_score: float  # 0.0-1.0
    timestamp: str
    context: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)


class MimicCoreIntegration:
    """
    Integration layer between Mimic personas and Core session orchestration.
    
    Enables Mimic personas to participate in multi-agent sessions,
    provides dynamic persona selection, and manages knowledge sharing.
    """
    
    def __init__(self, core: Core, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize Mimic-Core integration.
        
        Args:
            core: Core session orchestration instance
            logger: Optional logger instance
            
        Raises:
            MimicIntegrationError: If integration initialization fails
        """
        try:
            self.core = core
            self.logger = logger or HearthlinkLogger()
            
            # Mimic persona registry
            self.mimic_personas: Dict[str, MimicPersona] = {}
            
            # Session participation tracking
            self.session_participants: Dict[str, List[str]] = {}  # session_id -> persona_ids
            
            # Knowledge sharing registry
            self.shared_insights: Dict[str, List[SessionInsight]] = {}  # session_id -> insights
            
            # Performance tracking
            self.session_performance: Dict[str, Dict[str, Any]] = {}  # session_id -> performance_data
            
            self.logger.logger.info("Mimic-Core integration initialized successfully")
            
        except Exception as e:
            self._log_error_context("initialization", str(e), traceback.format_exc())
            raise MimicIntegrationError(f"Failed to initialize Mimic-Core integration: {str(e)}") from e
    
    def _log_error_context(self, operation: str, error_message: str, traceback_str: str) -> None:
        """Log error context for debugging."""
        error_context = {
            "operation": operation,
            "error_message": error_message,
            "traceback": traceback_str,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.logger.error(f"Mimic integration error: {operation} - {error_message}", extra=error_context)
    
    def register_mimic_persona(self, persona: MimicPersona) -> None:
        """
        Register a Mimic persona for session participation.
        
        Args:
            persona: Mimic persona instance to register
            
        Raises:
            MimicIntegrationError: If registration fails
        """
        try:
            persona_id = persona.memory.persona_id
            self.mimic_personas[persona_id] = persona
            
            self.logger.logger.info(f"Registered Mimic persona: {persona_id}")
            
        except Exception as e:
            self._log_error_context("persona_registration", str(e), traceback.format_exc())
            raise MimicIntegrationError(f"Failed to register persona: {str(e)}") from e
    
    def unregister_mimic_persona(self, persona_id: str) -> None:
        """
        Unregister a Mimic persona from session participation.
        
        Args:
            persona_id: ID of persona to unregister
            
        Raises:
            MimicIntegrationError: If unregistration fails
        """
        try:
            if persona_id in self.mimic_personas:
                del self.mimic_personas[persona_id]
                self.logger.logger.info(f"Unregistered Mimic persona: {persona_id}")
            else:
                self.logger.logger.warning(f"Persona {persona_id} not found in registry")
                
        except Exception as e:
            self._log_error_context("persona_unregistration", str(e), traceback.format_exc())
            raise MimicIntegrationError(f"Failed to unregister persona: {str(e)}") from e
    
    def recommend_personas_for_session(self, session_topic: str, 
                                     session_context: Dict[str, Any],
                                     max_recommendations: int = 5) -> List[PersonaRecommendation]:
        """
        Recommend Mimic personas for session participation.
        
        Args:
            session_topic: Session topic/theme
            session_context: Session context and requirements
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of persona recommendations
            
        Raises:
            PersonaSelectionError: If recommendation generation fails
        """
        try:
            recommendations = []
            
            for persona_id, persona in self.mimic_personas.items():
                # Calculate relevance score
                relevance_score = self._calculate_session_relevance(persona, session_topic, session_context)
                
                if relevance_score > 0.3:  # Minimum relevance threshold
                    recommendation = PersonaRecommendation(
                        persona_id=persona_id,
                        persona_name=persona.memory.persona_name,
                        role=persona.memory.role,
                        confidence_score=relevance_score,
                        reasoning=self._generate_recommendation_reasoning(persona, session_topic, session_context),
                        performance_tier=persona.get_performance_tier().value,
                        relevant_knowledge=self._get_relevant_knowledge(persona, session_topic),
                        estimated_contribution=self._estimate_contribution(persona, session_context)
                    )
                    recommendations.append(recommendation)
            
            # Sort by confidence score and limit results
            recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
            return recommendations[:max_recommendations]
            
        except Exception as e:
            self._log_error_context("persona_recommendation", str(e), traceback.format_exc())
            raise PersonaSelectionError(f"Failed to generate persona recommendations: {str(e)}") from e
    
    def _calculate_session_relevance(self, persona: MimicPersona, session_topic: str, 
                                   session_context: Dict[str, Any]) -> float:
        """Calculate relevance score for persona in session context."""
        try:
            relevance_score = 0.0
            
            # Role-based relevance
            if persona.memory.role.lower() in session_topic.lower():
                relevance_score += 0.4
            
            # Knowledge-based relevance
            knowledge_relevance = self._calculate_knowledge_relevance(persona, session_topic)
            relevance_score += knowledge_relevance * 0.3
            
            # Performance-based relevance
            performance_tier = persona.get_performance_tier()
            if performance_tier in [PerformanceTier.STABLE, PerformanceTier.EXCELLENT]:
                relevance_score += 0.2
            elif performance_tier == PerformanceTier.BETA:
                relevance_score += 0.1
            
            # Context-based relevance
            if session_context.get("requires_creativity") and persona.memory.core_traits.creativity > 70:
                relevance_score += 0.1
            if session_context.get("requires_precision") and persona.memory.core_traits.precision > 70:
                relevance_score += 0.1
            
            return min(1.0, relevance_score)
            
        except Exception as e:
            return 0.0
    
    def _calculate_knowledge_relevance(self, persona: MimicPersona, session_topic: str) -> float:
        """Calculate knowledge relevance for session topic."""
        try:
            # Check relevance index
            topic_relevance = 0.0
            for topic_score in persona.memory.relevance_index:
                if topic_score.topic.lower() in session_topic.lower():
                    topic_relevance = max(topic_relevance, topic_score.score)
            
            # Check custom knowledge
            knowledge_relevance = 0.0
            for knowledge in persona.memory.custom_knowledge:
                if any(tag.lower() in session_topic.lower() for tag in knowledge.tags):
                    knowledge_relevance = max(knowledge_relevance, knowledge.relevance_score)
            
            return max(topic_relevance, knowledge_relevance)
            
        except Exception as e:
            return 0.0
    
    def _generate_recommendation_reasoning(self, persona: MimicPersona, session_topic: str,
                                         session_context: Dict[str, Any]) -> str:
        """Generate reasoning for persona recommendation."""
        try:
            reasoning_parts = []
            
            # Role-based reasoning
            if persona.memory.role.lower() in session_topic.lower():
                reasoning_parts.append(f"Role '{persona.memory.role}' matches session topic")
            
            # Performance-based reasoning
            performance_tier = persona.get_performance_tier()
            if performance_tier in [PerformanceTier.STABLE, PerformanceTier.EXCELLENT]:
                reasoning_parts.append(f"High performance tier: {performance_tier.value}")
            
            # Knowledge-based reasoning
            relevant_knowledge = self._get_relevant_knowledge(persona, session_topic)
            if relevant_knowledge:
                reasoning_parts.append(f"Has relevant knowledge: {', '.join(relevant_knowledge[:3])}")
            
            # Trait-based reasoning
            if session_context.get("requires_creativity") and persona.memory.core_traits.creativity > 70:
                reasoning_parts.append("High creativity trait matches requirements")
            if session_context.get("requires_precision") and persona.memory.core_traits.precision > 70:
                reasoning_parts.append("High precision trait matches requirements")
            
            return "; ".join(reasoning_parts) if reasoning_parts else "General suitability"
            
        except Exception as e:
            return "Suitable for session participation"
    
    def _get_relevant_knowledge(self, persona: MimicPersona, session_topic: str) -> List[str]:
        """Get relevant knowledge topics for session."""
        try:
            relevant_topics = []
            
            # Check relevance index
            for topic_score in persona.memory.relevance_index:
                if topic_score.score > 0.6 and topic_score.topic.lower() in session_topic.lower():
                    relevant_topics.append(topic_score.topic)
            
            # Check custom knowledge tags
            for knowledge in persona.memory.custom_knowledge:
                if any(tag.lower() in session_topic.lower() for tag in knowledge.tags):
                    relevant_topics.extend(knowledge.tags)
            
            return list(set(relevant_topics))  # Remove duplicates
            
        except Exception as e:
            return []
    
    def _estimate_contribution(self, persona: MimicPersona, session_context: Dict[str, Any]) -> str:
        """Estimate persona's potential contribution to session."""
        try:
            contributions = []
            
            # Role-based contribution
            contributions.append(f"Provide {persona.memory.role} expertise")
            
            # Trait-based contribution
            if persona.memory.core_traits.creativity > 70:
                contributions.append("Creative problem solving")
            if persona.memory.core_traits.precision > 70:
                contributions.append("Detailed analysis")
            if persona.memory.core_traits.empathy > 70:
                contributions.append("User perspective insights")
            
            # Knowledge-based contribution
            if persona.memory.custom_knowledge:
                contributions.append("Share specialized knowledge")
            
            return "; ".join(contributions[:3])  # Limit to top 3 contributions
            
        except Exception as e:
            return "General session support"
    
    def add_persona_to_session(self, session_id: str, persona_id: str, 
                              user_id: str) -> bool:
        """
        Add a Mimic persona to a Core session.
        
        Args:
            session_id: Core session identifier
            persona_id: Mimic persona identifier
            user_id: User adding the persona
            
        Returns:
            bool: Success status
            
        Raises:
            SessionIntegrationError: If session integration fails
        """
        try:
            # Validate persona exists
            if persona_id not in self.mimic_personas:
                raise SessionIntegrationError(f"Persona {persona_id} not found")
            
            persona = self.mimic_personas[persona_id]
            
            # Create participant data for Core
            participant_data = {
                "id": persona_id,
                "type": "persona",
                "name": persona.memory.persona_name,
                "role": persona.memory.role,
                "metadata": {
                    "persona_type": "mimic",
                    "performance_tier": persona.get_performance_tier().value,
                    "core_traits": asdict(persona.memory.core_traits)
                }
            }
            
            # Add to Core session
            success = self.core.add_participant(session_id, user_id, participant_data)
            
            if success:
                # Track participation
                if session_id not in self.session_participants:
                    self.session_participants[session_id] = []
                self.session_participants[session_id].append(persona_id)
                
                # Initialize session performance tracking
                if session_id not in self.session_performance:
                    self.session_performance[session_id] = {
                        "participants": {},
                        "insights": [],
                        "start_time": datetime.now().isoformat()
                    }
                
                self.logger.logger.info(f"Added persona {persona_id} to session {session_id}")
            
            return success
            
        except Exception as e:
            self._log_error_context("session_integration", str(e), traceback.format_exc())
            raise SessionIntegrationError(f"Failed to add persona to session: {str(e)}") from e
    
    def remove_persona_from_session(self, session_id: str, persona_id: str, 
                                   user_id: str) -> bool:
        """
        Remove a Mimic persona from a Core session.
        
        Args:
            session_id: Core session identifier
            persona_id: Mimic persona identifier
            user_id: User removing the persona
            
        Returns:
            bool: Success status
            
        Raises:
            SessionIntegrationError: If session integration fails
        """
        try:
            # Remove from Core session
            success = self.core.remove_participant(session_id, user_id, persona_id)
            
            if success:
                # Update tracking
                if session_id in self.session_participants:
                    if persona_id in self.session_participants[session_id]:
                        self.session_participants[session_id].remove(persona_id)
                
                self.logger.logger.info(f"Removed persona {persona_id} from session {session_id}")
            
            return success
            
        except Exception as e:
            self._log_error_context("session_integration", str(e), traceback.format_exc())
            raise SessionIntegrationError(f"Failed to remove persona from session: {str(e)}") from e
    
    def share_insight_in_session(self, session_id: str, persona_id: str, 
                                insight_type: str, content: str,
                                relevance_score: float = 0.5,
                                context: Optional[Dict[str, Any]] = None,
                                tags: Optional[List[str]] = None) -> bool:
        """
        Share an insight from a Mimic persona in a Core session.
        
        Args:
            session_id: Core session identifier
            persona_id: Mimic persona identifier
            insight_type: Type of insight
            content: Insight content
            relevance_score: Relevance score (0.0-1.0)
            context: Optional context information
            tags: Optional tags
            
        Returns:
            bool: Success status
            
        Raises:
            KnowledgeSharingError: If knowledge sharing fails
        """
        try:
            # Validate persona is in session
            if session_id not in self.session_participants or persona_id not in self.session_participants[session_id]:
                raise KnowledgeSharingError(f"Persona {persona_id} not in session {session_id}")
            
            # Create insight
            insight = SessionInsight(
                insight_id=f"insight-{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                persona_id=persona_id,
                insight_type=insight_type,
                content=content,
                relevance_score=relevance_score,
                timestamp=datetime.now().isoformat(),
                context=context or {},
                tags=tags or []
            )
            
            # Share with Core session
            success = self.core.share_insight(session_id, persona_id, content, context or {})
            
            if success:
                # Track insight
                if session_id not in self.shared_insights:
                    self.shared_insights[session_id] = []
                self.shared_insights[session_id].append(insight)
                
                # Update session performance
                if session_id in self.session_performance:
                    if persona_id not in self.session_performance[session_id]["participants"]:
                        self.session_performance[session_id]["participants"][persona_id] = {
                            "insights_shared": 0,
                            "total_relevance": 0.0
                        }
                    
                    self.session_performance[session_id]["participants"][persona_id]["insights_shared"] += 1
                    self.session_performance[session_id]["participants"][persona_id]["total_relevance"] += relevance_score
                
                self.logger.logger.info(f"Shared insight from persona {persona_id} in session {session_id}")
            
            return success
            
        except Exception as e:
            self._log_error_context("knowledge_sharing", str(e), traceback.format_exc())
            raise KnowledgeSharingError(f"Failed to share insight: {str(e)}") from e
    
    def record_session_performance(self, session_id: str, persona_id: str,
                                 task: str, score: int, user_feedback: str,
                                 success: bool, duration: float,
                                 context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record performance for a persona in a session.
        
        Args:
            session_id: Core session identifier
            persona_id: Mimic persona identifier
            task: Task description
            score: Performance score (0-100)
            user_feedback: User feedback
            success: Whether task was successful
            duration: Task duration in seconds
            context: Optional context information
            
        Raises:
            SessionIntegrationError: If performance recording fails
        """
        try:
            # Validate persona is in session
            if session_id not in self.session_participants or persona_id not in self.session_participants[session_id]:
                raise SessionIntegrationError(f"Persona {persona_id} not in session {session_id}")
            
            # Get persona instance
            if persona_id not in self.mimic_personas:
                raise SessionIntegrationError(f"Persona {persona_id} not found")
            
            persona = self.mimic_personas[persona_id]
            
            # Record performance
            persona.record_performance(
                session_id=session_id,
                task=task,
                score=score,
                user_feedback=user_feedback,
                success=success,
                duration=duration,
                context=context
            )
            
            # Update session performance tracking
            if session_id in self.session_performance:
                if persona_id not in self.session_performance[session_id]["participants"]:
                    self.session_performance[session_id]["participants"][persona_id] = {
                        "tasks_completed": 0,
                        "total_score": 0,
                        "successful_tasks": 0
                    }
                
                participant_perf = self.session_performance[session_id]["participants"][persona_id]
                participant_perf["tasks_completed"] += 1
                participant_perf["total_score"] += score
                if success:
                    participant_perf["successful_tasks"] += 1
            
            self.logger.logger.info(f"Recorded performance for persona {persona_id} in session {session_id}")
            
        except Exception as e:
            self._log_error_context("performance_recording", str(e), traceback.format_exc())
            raise SessionIntegrationError(f"Failed to record session performance: {str(e)}") from e
    
    def get_session_insights(self, session_id: str) -> List[SessionInsight]:
        """
        Get insights shared in a session.
        
        Args:
            session_id: Core session identifier
            
        Returns:
            List of session insights
        """
        try:
            return self.shared_insights.get(session_id, [])
        except Exception as e:
            self.logger.logger.error(f"Failed to get session insights: {str(e)}")
            return []
    
    def get_session_performance_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get performance summary for a session.
        
        Args:
            session_id: Core session identifier
            
        Returns:
            Session performance summary
        """
        try:
            if session_id not in self.session_performance:
                return {"error": "Session not found"}
            
            performance = self.session_performance[session_id]
            summary = {
                "session_id": session_id,
                "start_time": performance["start_time"],
                "participants": {},
                "total_insights": len(self.shared_insights.get(session_id, [])),
                "average_relevance": 0.0
            }
            
            # Calculate participant summaries
            total_relevance = 0.0
            for persona_id, perf_data in performance["participants"].items():
                if persona_id in self.mimic_personas:
                    persona = self.mimic_personas[persona_id]
                    participant_summary = {
                        "persona_name": persona.memory.persona_name,
                        "role": persona.memory.role,
                        "performance_tier": persona.get_performance_tier().value,
                        "tasks_completed": perf_data.get("tasks_completed", 0),
                        "average_score": perf_data.get("total_score", 0) / max(perf_data.get("tasks_completed", 1), 1),
                        "success_rate": perf_data.get("successful_tasks", 0) / max(perf_data.get("tasks_completed", 1), 1),
                        "insights_shared": perf_data.get("insights_shared", 0),
                        "average_relevance": perf_data.get("total_relevance", 0.0) / max(perf_data.get("insights_shared", 1), 1)
                    }
                    summary["participants"][persona_id] = participant_summary
                    total_relevance += perf_data.get("total_relevance", 0.0)
            
            # Calculate overall average relevance
            total_insights = sum(p.get("insights_shared", 0) for p in performance["participants"].values())
            if total_insights > 0:
                summary["average_relevance"] = total_relevance / total_insights
            
            return summary
            
        except Exception as e:
            self.logger.logger.error(f"Failed to get session performance summary: {str(e)}")
            return {"error": f"Failed to generate summary: {str(e)}"}
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active sessions with Mimic personas.
        
        Returns:
            List of active session IDs
        """
        try:
            return list(self.session_participants.keys())
        except Exception as e:
            self.logger.logger.error(f"Failed to get active sessions: {str(e)}")
            return []
    
    def cleanup_session(self, session_id: str) -> None:
        """
        Clean up session data when session ends.
        
        Args:
            session_id: Core session identifier
        """
        try:
            # Remove session tracking
            if session_id in self.session_participants:
                del self.session_participants[session_id]
            
            if session_id in self.session_performance:
                del self.session_performance[session_id]
            
            if session_id in self.shared_insights:
                del self.shared_insights[session_id]
            
            self.logger.logger.info(f"Cleaned up session {session_id}")
            
        except Exception as e:
            self.logger.logger.error(f"Failed to cleanup session {session_id}: {str(e)}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get integration status and statistics.
        
        Returns:
            Integration status information
        """
        try:
            return {
                "registered_personas": len(self.mimic_personas),
                "active_sessions": len(self.session_participants),
                "total_insights_shared": sum(len(insights) for insights in self.shared_insights.values()),
                "persona_performance_tiers": {
                    persona_id: persona.get_performance_tier().value
                    for persona_id, persona in self.mimic_personas.items()
                },
                "session_participation": {
                    session_id: len(persona_ids)
                    for session_id, persona_ids in self.session_participants.items()
                }
            }
            
        except Exception as e:
            self.logger.logger.error(f"Failed to get integration status: {str(e)}")
            return {"error": f"Failed to get status: {str(e)}"}


def create_mimic_integration(core: Core, logger: Optional[HearthlinkLogger] = None) -> MimicCoreIntegration:
    """
    Factory function to create Mimic-Core integration instance.
    
    Args:
        core: Core session orchestration instance
        logger: Optional logger instance
        
    Returns:
        MimicCoreIntegration: Configured integration instance
        
    Raises:
        MimicIntegrationError: If integration creation fails
    """
    try:
        integration = MimicCoreIntegration(core, logger)
        return integration
        
    except Exception as e:
        raise MimicIntegrationError(f"Failed to create Mimic-Core integration: {str(e)}") from e 