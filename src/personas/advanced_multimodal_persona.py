#!/usr/bin/env python3
"""
Advanced Multimodal Persona System

Enhanced persona modeling with multi-modal input processing, dynamic user adaptation,
and integrated learning from behavioral analysis feedback loops.

Features:
- Multi-modal input processing (text, audio, visual, environmental)
- Dynamic user adaptation based on behavioral patterns
- Integrated learning from behavioral analysis
- Real-time persona adjustment and feedback loops
- Advanced pattern recognition and prediction

References:
- docs/PERSONA_GUIDE.md: Persona specification and integration patterns
- docs/PLATINUM_BLOCKERS.md: Ethical safety rails and compliance
- Process Refinement SOP: Development and documentation standards

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import traceback
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import re
from collections import defaultdict, Counter

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError
from llm.local_llm_client import LocalLLMClient, LLMRequest, LLMResponse, LLMError
from core.behavioral_analysis import (
    BehavioralAnalysis, TextAnalysis, BehavioralInsight, 
    AdaptiveFeedback, ExternalSignal, SignalType, BehavioralPattern
)


class AdvancedPersonaError(HearthlinkError):
    """Base exception for advanced persona errors."""
    pass


class MultimodalInputError(AdvancedPersonaError):
    """Exception raised when multimodal input processing fails."""
    pass


class AdaptationError(AdvancedPersonaError):
    """Exception raised when user adaptation fails."""
    pass


class LearningLoopError(AdvancedPersonaError):
    """Exception raised when learning feedback loop fails."""
    pass


class InputModality(Enum):
    """Supported input modalities."""
    TEXT = "text"
    AUDIO = "audio"
    VISUAL = "visual"
    ENVIRONMENTAL = "environmental"
    BEHAVIORAL = "behavioral"
    SENSORY = "sensory"


class AdaptationType(Enum):
    """Types of user adaptation."""
    PERSONALITY_SHIFT = "personality_shift"
    COMMUNICATION_STYLE = "communication_style"
    RESPONSE_PATTERN = "response_pattern"
    ENGAGEMENT_LEVEL = "engagement_level"
    LEARNING_PREFERENCE = "learning_preference"
    EMOTIONAL_SUPPORT = "emotional_support"


@dataclass
class MultimodalInput:
    """Multi-modal input data."""
    input_id: str
    modality: InputModality
    timestamp: str
    data: Dict[str, Any]
    confidence: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserAdaptation:
    """User adaptation data."""
    adaptation_id: str
    adaptation_type: AdaptationType
    timestamp: str
    trigger: str
    old_state: Dict[str, Any]
    new_state: Dict[str, Any]
    confidence: float
    evidence: List[str]
    impact_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningFeedback:
    """Learning feedback from behavioral analysis."""
    feedback_id: str
    source: str  # "behavioral_analysis", "user_correction", "system_observation"
    timestamp: str
    feedback_type: str
    description: str
    target_aspect: str
    suggested_change: Dict[str, Any]
    confidence: float
    priority: str  # "low", "medium", "high", "critical"
    status: str = "pending"  # "pending", "applied", "rejected", "tested"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonaState:
    """Current persona state with adaptation history."""
    persona_id: str
    user_id: str
    timestamp: str
    
    # Core personality traits (Big Five + additional)
    personality_traits: Dict[str, float] = field(default_factory=lambda: {
        "openness": 0.7,
        "conscientiousness": 0.8,
        "extraversion": 0.5,
        "agreeableness": 0.9,
        "neuroticism": 0.3,
        "adaptability": 0.8,
        "empathy": 0.9,
        "curiosity": 0.7
    })
    
    # Communication style
    communication_style: Dict[str, float] = field(default_factory=lambda: {
        "formality": 0.6,
        "directness": 0.7,
        "supportiveness": 0.9,
        "humor": 0.5,
        "detail_level": 0.7
    })
    
    # Engagement patterns
    engagement_patterns: Dict[str, float] = field(default_factory=lambda: {
        "response_frequency": 0.8,
        "question_asking": 0.7,
        "active_listening": 0.9,
        "follow_up": 0.8
    })
    
    # Learning preferences
    learning_preferences: Dict[str, float] = field(default_factory=lambda: {
        "visual_learning": 0.6,
        "auditory_learning": 0.7,
        "kinesthetic_learning": 0.5,
        "social_learning": 0.8,
        "independent_learning": 0.7
    })
    
    # Adaptation history
    adaptations: List[UserAdaptation] = field(default_factory=list)
    learning_feedback: List[LearningFeedback] = field(default_factory=list)
    
    # Metadata
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedMultimodalPersona:
    """
    Advanced multimodal persona system with dynamic user adaptation
    and integrated learning from behavioral analysis.
    """
    
    def __init__(self, 
                 persona_id: str,
                 llm_client: LocalLLMClient, 
                 behavioral_analysis: BehavioralAnalysis,
                 logger: Optional[HearthlinkLogger] = None):
        """
        Initialize advanced multimodal persona.
        
        Args:
            persona_id: Unique persona identifier
            llm_client: Configured LLM client
            behavioral_analysis: Behavioral analysis instance
            logger: Optional logger instance
            
        Raises:
            AdvancedPersonaError: If persona initialization fails
        """
        try:
            self.persona_id = persona_id
            self.llm_client = llm_client
            self.behavioral_analysis = behavioral_analysis
            self.logger = logger or HearthlinkLogger()
            
            # Initialize persona state
            self.state = PersonaState(
                persona_id=persona_id,
                user_id="default",
                timestamp=datetime.now().isoformat()
            )
            
            # Input processors
            self.input_processors: Dict[InputModality, Callable] = {}
            self._setup_input_processors()
            
            # Adaptation strategies
            self.adaptation_strategies: Dict[AdaptationType, Callable] = {}
            self._setup_adaptation_strategies()
            
            # Learning feedback processors
            self.feedback_processors: Dict[str, Callable] = {}
            self._setup_feedback_processors()
            
            # Validation
            self._validate_initialization()
            
            self._log("advanced_persona_initialized", "system", None, "system", {
                "persona_id": persona_id,
                "modalities": [m.value for m in InputModality],
                "adaptation_types": [a.value for a in AdaptationType]
            })
            
        except Exception as e:
            raise AdvancedPersonaError(f"Failed to initialize advanced persona: {str(e)}") from e
    
    def _setup_input_processors(self):
        """Setup input processors for different modalities."""
        self.input_processors = {
            InputModality.TEXT: self._process_text_input,
            InputModality.AUDIO: self._process_audio_input,
            InputModality.VISUAL: self._process_visual_input,
            InputModality.ENVIRONMENTAL: self._process_environmental_input,
            InputModality.BEHAVIORAL: self._process_behavioral_input,
            InputModality.SENSORY: self._process_sensory_input
        }
    
    def _setup_adaptation_strategies(self):
        """Setup adaptation strategies for different adaptation types."""
        self.adaptation_strategies = {
            AdaptationType.PERSONALITY_SHIFT: self._adapt_personality,
            AdaptationType.COMMUNICATION_STYLE: self._adapt_communication_style,
            AdaptationType.RESPONSE_PATTERN: self._adapt_response_pattern,
            AdaptationType.ENGAGEMENT_LEVEL: self._adapt_engagement_level,
            AdaptationType.LEARNING_PREFERENCE: self._adapt_learning_preference,
            AdaptationType.EMOTIONAL_SUPPORT: self._adapt_emotional_support
        }
    
    def _setup_feedback_processors(self):
        """Setup feedback processors for different feedback sources."""
        self.feedback_processors = {
            "behavioral_analysis": self._process_behavioral_feedback,
            "user_correction": self._process_user_correction,
            "system_observation": self._process_system_observation
        }
    
    def _validate_initialization(self):
        """Validate persona initialization."""
        if not isinstance(self.llm_client, LocalLLMClient):
            raise AdvancedPersonaError("LLM client must be LocalLLMClient instance")
        
        if not isinstance(self.behavioral_analysis, BehavioralAnalysis):
            raise AdvancedPersonaError("Behavioral analysis must be BehavioralAnalysis instance")
    
    def process_multimodal_input(self, inputs: List[MultimodalInput], 
                                user_id: str, 
                                session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process multi-modal inputs and generate adaptive response.
        
        Args:
            inputs: List of multimodal inputs
            user_id: User identifier
            session_id: Optional session identifier
            
        Returns:
            Dict containing processed inputs and adaptation recommendations
        """
        try:
            self.state.user_id = user_id
            self.state.timestamp = datetime.now().isoformat()
            
            processed_inputs = []
            adaptation_recommendations = []
            
            # Process each input modality
            for input_data in inputs:
                processor = self.input_processors.get(input_data.modality)
                if processor:
                    processed = processor(input_data, user_id, session_id)
                    processed_inputs.append(processed)
                    
                    # Check for adaptation triggers
                    adaptations = self._check_adaptation_triggers(processed, user_id)
                    adaptation_recommendations.extend(adaptations)
            
            # Apply behavioral analysis
            behavioral_insights = self._apply_behavioral_analysis(processed_inputs, user_id, session_id)
            
            # Generate response with current state
            response = self._generate_adaptive_response(processed_inputs, behavioral_insights, user_id, session_id)
            
            result = {
                "processed_inputs": processed_inputs,
                "adaptation_recommendations": adaptation_recommendations,
                "behavioral_insights": behavioral_insights,
                "response": response,
                "current_state": asdict(self.state)
            }
            
            self._log("multimodal_input_processed", user_id, session_id, "input_processing", {
                "input_count": len(inputs),
                "modalities": [i.modality.value for i in inputs],
                "adaptations": len(adaptation_recommendations)
            })
            
            return result
            
        except Exception as e:
            self._log("multimodal_input_error", user_id, session_id, "error", {
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            raise MultimodalInputError(f"Failed to process multimodal input: {str(e)}") from e
    
    def apply_learning_feedback(self, feedback: LearningFeedback) -> bool:
        """
        Apply learning feedback to persona state.
        
        Args:
            feedback: Learning feedback to apply
            
        Returns:
            True if feedback was successfully applied
        """
        try:
            processor = self.feedback_processors.get(feedback.source)
            if processor:
                success = processor(feedback)
                if success:
                    feedback.status = "applied"
                    self.state.learning_feedback.append(feedback)
                    
                    self._log("learning_feedback_applied", self.state.user_id, None, "learning", {
                        "feedback_id": feedback.feedback_id,
                        "feedback_type": feedback.feedback_type,
                        "target_aspect": feedback.target_aspect
                    })
                    
                    return True
            
            feedback.status = "rejected"
            return False
            
        except Exception as e:
            self._log("learning_feedback_error", self.state.user_id, None, "error", {
                "error": str(e),
                "feedback_id": feedback.feedback_id
            })
            raise LearningLoopError(f"Failed to apply learning feedback: {str(e)}") from e
    
    def adapt_to_user(self, adaptation_type: AdaptationType, 
                     trigger: str, 
                     evidence: List[str],
                     user_id: str) -> bool:
        """
        Adapt persona to user based on specified adaptation type.
        
        Args:
            adaptation_type: Type of adaptation to apply
            trigger: What triggered the adaptation
            evidence: Evidence supporting the adaptation
            user_id: User identifier
            
        Returns:
            True if adaptation was successfully applied
        """
        try:
            strategy = self.adaptation_strategies.get(adaptation_type)
            if not strategy:
                raise AdaptationError(f"No strategy for adaptation type: {adaptation_type}")
            
            # Store old state
            old_state = {
                "personality_traits": self.state.personality_traits.copy(),
                "communication_style": self.state.communication_style.copy(),
                "engagement_patterns": self.state.engagement_patterns.copy(),
                "learning_preferences": self.state.learning_preferences.copy()
            }
            
            # Apply adaptation
            success = strategy(trigger, evidence, user_id)
            
            if success:
                # Create adaptation record
                adaptation = UserAdaptation(
                    adaptation_id=str(uuid.uuid4()),
                    adaptation_type=adaptation_type,
                    timestamp=datetime.now().isoformat(),
                    trigger=trigger,
                    old_state=old_state,
                    new_state={
                        "personality_traits": self.state.personality_traits.copy(),
                        "communication_style": self.state.communication_style.copy(),
                        "engagement_patterns": self.state.engagement_patterns.copy(),
                        "learning_preferences": self.state.learning_preferences.copy()
                    },
                    confidence=0.8,  # Could be calculated based on evidence
                    evidence=evidence,
                    impact_score=0.7  # Could be calculated based on change magnitude
                )
                
                self.state.adaptations.append(adaptation)
                
                self._log("user_adaptation_applied", user_id, None, "adaptation", {
                    "adaptation_type": adaptation_type.value,
                    "trigger": trigger,
                    "evidence_count": len(evidence)
                })
                
                return True
            
            return False
            
        except Exception as e:
            self._log("user_adaptation_error", user_id, None, "error", {
                "error": str(e),
                "adaptation_type": adaptation_type.value
            })
            raise AdaptationError(f"Failed to adapt to user: {str(e)}") from e
    
    def _process_text_input(self, input_data: MultimodalInput, 
                           user_id: str, 
                           session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process text input using behavioral analysis."""
        try:
            text = input_data.data.get("text", "")
            
            # Use behavioral analysis for text processing
            text_analysis = self.behavioral_analysis.analyze_text(text)
            
            return {
                "modality": InputModality.TEXT.value,
                "text": text,
                "sentiment_score": text_analysis.sentiment_score,
                "emotion_labels": text_analysis.emotion_labels,
                "complexity_score": text_analysis.complexity_score,
                "engagement_indicators": text_analysis.engagement_indicators,
                "behavioral_markers": text_analysis.behavioral_markers,
                "confidence": text_analysis.confidence,
                "timestamp": input_data.timestamp
            }
            
        except Exception as e:
            raise MultimodalInputError(f"Failed to process text input: {str(e)}") from e
    
    def _process_audio_input(self, input_data: MultimodalInput, 
                            user_id: str, 
                            session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process audio input (placeholder for future implementation)."""
        try:
            # Placeholder for audio processing
            audio_data = input_data.data.get("audio", {})
            
            return {
                "modality": InputModality.AUDIO.value,
                "audio_features": audio_data.get("features", {}),
                "duration": audio_data.get("duration", 0),
                "confidence": input_data.confidence,
                "timestamp": input_data.timestamp,
                "status": "placeholder"
            }
            
        except Exception as e:
            raise MultimodalInputError(f"Failed to process audio input: {str(e)}") from e
    
    def _process_visual_input(self, input_data: MultimodalInput, 
                             user_id: str, 
                             session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process visual input (placeholder for future implementation)."""
        try:
            # Placeholder for visual processing
            visual_data = input_data.data.get("visual", {})
            
            return {
                "modality": InputModality.VISUAL.value,
                "visual_features": visual_data.get("features", {}),
                "image_metadata": visual_data.get("metadata", {}),
                "confidence": input_data.confidence,
                "timestamp": input_data.timestamp,
                "status": "placeholder"
            }
            
        except Exception as e:
            raise MultimodalInputError(f"Failed to process visual input: {str(e)}") from e
    
    def _process_environmental_input(self, input_data: MultimodalInput, 
                                    user_id: str, 
                                    session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process environmental input."""
        try:
            env_data = input_data.data.get("environmental", {})
            
            return {
                "modality": InputModality.ENVIRONMENTAL.value,
                "location": env_data.get("location", "unknown"),
                "time_of_day": env_data.get("time_of_day", "unknown"),
                "context": env_data.get("context", "unknown"),
                "confidence": input_data.confidence,
                "timestamp": input_data.timestamp
            }
            
        except Exception as e:
            raise MultimodalInputError(f"Failed to process environmental input: {str(e)}") from e
    
    def _process_behavioral_input(self, input_data: MultimodalInput, 
                                 user_id: str, 
                                 session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process behavioral input."""
        try:
            behavioral_data = input_data.data.get("behavioral", {})
            
            return {
                "modality": InputModality.BEHAVIORAL.value,
                "behavior_type": behavioral_data.get("type", "unknown"),
                "behavior_data": behavioral_data.get("data", {}),
                "confidence": input_data.confidence,
                "timestamp": input_data.timestamp
            }
            
        except Exception as e:
            raise MultimodalInputError(f"Failed to process behavioral input: {str(e)}") from e
    
    def _process_sensory_input(self, input_data: MultimodalInput, 
                              user_id: str, 
                              session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process sensory input (placeholder for future implementation)."""
        try:
            # Placeholder for sensory processing
            sensory_data = input_data.data.get("sensory", {})
            
            return {
                "modality": InputModality.SENSORY.value,
                "sensory_type": sensory_data.get("type", "unknown"),
                "sensory_data": sensory_data.get("data", {}),
                "confidence": input_data.confidence,
                "timestamp": input_data.timestamp,
                "status": "placeholder"
            }
            
        except Exception as e:
            raise MultimodalInputError(f"Failed to process sensory input: {str(e)}") from e
    
    def _check_adaptation_triggers(self, processed_input: Dict[str, Any], 
                                  user_id: str) -> List[Dict[str, Any]]:
        """Check for adaptation triggers in processed input."""
        adaptations = []
        
        # Example adaptation triggers
        if processed_input.get("modality") == InputModality.TEXT.value:
            sentiment = processed_input.get("sentiment_score", 0)
            
            # Adapt communication style based on sentiment
            if sentiment < -0.5:
                adaptations.append({
                    "type": AdaptationType.COMMUNICATION_STYLE.value,
                    "trigger": "negative_sentiment",
                    "evidence": ["low_sentiment_score"],
                    "priority": "high"
                })
            elif sentiment > 0.5:
                adaptations.append({
                    "type": AdaptationType.ENGAGEMENT_LEVEL.value,
                    "trigger": "positive_sentiment",
                    "evidence": ["high_sentiment_score"],
                    "priority": "medium"
                })
        
        return adaptations
    
    def _apply_behavioral_analysis(self, processed_inputs: List[Dict[str, Any]], 
                                  user_id: str, 
                                  session_id: Optional[str] = None) -> List[BehavioralInsight]:
        """Apply behavioral analysis to processed inputs."""
        try:
            # Convert processed inputs to behavioral analysis format
            analyses = []
            for input_data in processed_inputs:
                if input_data.get("modality") == InputModality.TEXT.value:
                    analyses.append({
                        "type": "text_analysis",
                        "data": input_data
                    })
            
            # Generate behavioral insights
            insights = self.behavioral_analysis.generate_behavioral_insights(
                analyses, user_id, session_id
            )
            
            return insights
            
        except Exception as e:
            self._log("behavioral_analysis_error", user_id, session_id, "error", {
                "error": str(e)
            })
            return []
    
    def _generate_adaptive_response(self, processed_inputs: List[Dict[str, Any]], 
                                   behavioral_insights: List[BehavioralInsight],
                                   user_id: str, 
                                   session_id: Optional[str] = None) -> str:
        """Generate adaptive response based on current state and inputs."""
        try:
            # Build context from current state and inputs
            context = {
                "personality_traits": self.state.personality_traits,
                "communication_style": self.state.communication_style,
                "engagement_patterns": self.state.engagement_patterns,
                "learning_preferences": self.state.learning_preferences,
                "recent_adaptations": len(self.state.adaptations),
                "behavioral_insights": len(behavioral_insights)
            }
            
            # Create prompt based on current state
            prompt = self._build_adaptive_prompt(processed_inputs, behavioral_insights, context)
            
            # Generate response using LLM
            request = LLMRequest(
                prompt=prompt,
                max_tokens=500,
                temperature=0.7,
                context=context
            )
            
            response = self.llm_client.generate_response(request)
            
            return response.content
            
        except Exception as e:
            self._log("adaptive_response_error", user_id, session_id, "error", {
                "error": str(e)
            })
            return "I'm having trouble generating a response right now. Please try again."
    
    def _build_adaptive_prompt(self, processed_inputs: List[Dict[str, Any]], 
                              behavioral_insights: List[BehavioralInsight],
                              context: Dict[str, Any]) -> str:
        """Build adaptive prompt based on current state and inputs."""
        prompt_parts = []
        
        # Add personality context
        prompt_parts.append(f"You are an AI assistant with the following personality traits:")
        for trait, value in context["personality_traits"].items():
            prompt_parts.append(f"- {trait}: {value:.2f}")
        
        # Add communication style
        prompt_parts.append(f"\nCommunication style:")
        for style, value in context["communication_style"].items():
            prompt_parts.append(f"- {style}: {value:.2f}")
        
        # Add behavioral insights
        if behavioral_insights:
            prompt_parts.append(f"\nRecent behavioral insights:")
            for insight in behavioral_insights[:3]:  # Limit to 3 most recent
                prompt_parts.append(f"- {insight.description}")
        
        # Add user inputs
        text_inputs = [i for i in processed_inputs if i.get("modality") == InputModality.TEXT.value]
        if text_inputs:
            prompt_parts.append(f"\nUser input: {text_inputs[-1].get('text', '')}")
        
        prompt_parts.append(f"\nGenerate a response that reflects your current personality and communication style.")
        
        return "\n".join(prompt_parts)
    
    # Adaptation strategy implementations
    def _adapt_personality(self, trigger: str, evidence: List[str], user_id: str) -> bool:
        """Adapt personality traits based on trigger and evidence."""
        try:
            # Example personality adaptation logic
            if "negative_sentiment" in trigger:
                # Increase empathy and supportiveness
                self.state.personality_traits["empathy"] = min(1.0, self.state.personality_traits["empathy"] + 0.1)
                self.state.personality_traits["agreeableness"] = min(1.0, self.state.personality_traits["agreeableness"] + 0.05)
            
            return True
            
        except Exception as e:
            return False
    
    def _adapt_communication_style(self, trigger: str, evidence: List[str], user_id: str) -> bool:
        """Adapt communication style based on trigger and evidence."""
        try:
            # Example communication style adaptation
            if "negative_sentiment" in trigger:
                # Increase supportiveness and formality
                self.state.communication_style["supportiveness"] = min(1.0, self.state.communication_style["supportiveness"] + 0.1)
                self.state.communication_style["formality"] = min(1.0, self.state.communication_style["formality"] + 0.05)
            
            return True
            
        except Exception as e:
            return False
    
    def _adapt_response_pattern(self, trigger: str, evidence: List[str], user_id: str) -> bool:
        """Adapt response patterns based on trigger and evidence."""
        try:
            # Example response pattern adaptation
            if "high_engagement" in trigger:
                # Increase response frequency and detail level
                self.state.engagement_patterns["response_frequency"] = min(1.0, self.state.engagement_patterns["response_frequency"] + 0.1)
                self.state.communication_style["detail_level"] = min(1.0, self.state.communication_style["detail_level"] + 0.1)
            
            return True
            
        except Exception as e:
            return False
    
    def _adapt_engagement_level(self, trigger: str, evidence: List[str], user_id: str) -> bool:
        """Adapt engagement level based on trigger and evidence."""
        try:
            # Example engagement adaptation
            if "positive_sentiment" in trigger:
                # Increase engagement patterns
                self.state.engagement_patterns["question_asking"] = min(1.0, self.state.engagement_patterns["question_asking"] + 0.1)
                self.state.engagement_patterns["follow_up"] = min(1.0, self.state.engagement_patterns["follow_up"] + 0.1)
            
            return True
            
        except Exception as e:
            return False
    
    def _adapt_learning_preference(self, trigger: str, evidence: List[str], user_id: str) -> bool:
        """Adapt learning preferences based on trigger and evidence."""
        try:
            # Example learning preference adaptation
            if "visual_learning" in trigger:
                # Increase visual learning preference
                self.state.learning_preferences["visual_learning"] = min(1.0, self.state.learning_preferences["visual_learning"] + 0.1)
            
            return True
            
        except Exception as e:
            return False
    
    def _adapt_emotional_support(self, trigger: str, evidence: List[str], user_id: str) -> bool:
        """Adapt emotional support level based on trigger and evidence."""
        try:
            # Example emotional support adaptation
            if "emotional_distress" in trigger:
                # Increase empathy and emotional support
                self.state.personality_traits["empathy"] = min(1.0, self.state.personality_traits["empathy"] + 0.15)
                self.state.communication_style["supportiveness"] = min(1.0, self.state.communication_style["supportiveness"] + 0.15)
            
            return True
            
        except Exception as e:
            return False
    
    # Feedback processor implementations
    def _process_behavioral_feedback(self, feedback: LearningFeedback) -> bool:
        """Process feedback from behavioral analysis."""
        try:
            # Apply behavioral analysis feedback
            if feedback.target_aspect == "communication_style":
                # Update communication style based on feedback
                suggested_changes = feedback.suggested_change
                for key, value in suggested_changes.items():
                    if key in self.state.communication_style:
                        self.state.communication_style[key] = value
            
            return True
            
        except Exception as e:
            return False
    
    def _process_user_correction(self, feedback: LearningFeedback) -> bool:
        """Process feedback from user corrections."""
        try:
            # Apply user correction feedback
            if feedback.target_aspect == "personality_traits":
                # Update personality traits based on user correction
                suggested_changes = feedback.suggested_change
                for key, value in suggested_changes.items():
                    if key in self.state.personality_traits:
                        self.state.personality_traits[key] = value
            
            return True
            
        except Exception as e:
            return False
    
    def _process_system_observation(self, feedback: LearningFeedback) -> bool:
        """Process feedback from system observations."""
        try:
            # Apply system observation feedback
            if feedback.target_aspect == "engagement_patterns":
                # Update engagement patterns based on system observation
                suggested_changes = feedback.suggested_change
                for key, value in suggested_changes.items():
                    if key in self.state.engagement_patterns:
                        self.state.engagement_patterns[key] = value
            
            return True
            
        except Exception as e:
            return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get current persona state."""
        return asdict(self.state)
    
    def export_state(self) -> Dict[str, Any]:
        """Export persona state for persistence."""
        return {
            "persona_id": self.persona_id,
            "state": asdict(self.state),
            "version": "1.0.0",
            "exported_at": datetime.now().isoformat()
        }
    
    def _log(self, action: str, user_id: str, session_id: Optional[str], 
             event_type: str, details: Dict[str, Any]):
        """Log persona events."""
        try:
            if self.logger:
                self.logger.logger.info(f"Advanced Persona {action}", extra={
                    "event_type": event_type,
                    "user_id": user_id,
                    "session_id": session_id,
                    "persona_id": self.persona_id,
                    "details": details
                })
        except Exception:
            pass  # Don't let logging errors break persona functionality


def create_advanced_multimodal_persona(persona_id: str,
                                      llm_config: Dict[str, Any],
                                      behavioral_analysis: BehavioralAnalysis,
                                      logger: Optional[HearthlinkLogger] = None) -> AdvancedMultimodalPersona:
    """
    Factory function to create advanced multimodal persona.
    
    Args:
        persona_id: Unique persona identifier
        llm_config: LLM client configuration
        behavioral_analysis: Behavioral analysis instance
        logger: Optional logger instance
        
    Returns:
        Configured AdvancedMultimodalPersona instance
    """
    try:
        # Create LLM client
        llm_client = LocalLLMClient(llm_config)
        
        # Create advanced persona
        persona = AdvancedMultimodalPersona(
            persona_id=persona_id,
            llm_client=llm_client,
            behavioral_analysis=behavioral_analysis,
            logger=logger
        )
        
        return persona
        
    except Exception as e:
        raise AdvancedPersonaError(f"Failed to create advanced multimodal persona: {str(e)}") from e 