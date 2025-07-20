#!/usr/bin/env python3
"""
Mimic — Dynamic Persona & Adaptive Agent

Generator, manager, and optimizer of user-curated, character-rich synthetic personas
for specialized tasks, research, or entertainment. Mimic adapts to user-defined goals
and evolves each persona in direct relation to real usage—the more a persona is used,
the more skilled and valuable it becomes.

References:
- hearthlink_system_documentation_master.md: Mimic persona specification
- PLATINUM_BLOCKERS.md: Ethical safety rails and dependency mitigation
- appendix_h_developer_qa_platinum_checklists.md: QA requirements for error handling

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
import traceback
import hashlib
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import HearthlinkLogger, HearthlinkError
from llm.local_llm_client import LocalLLMClient, LLMRequest, LLMResponse, LLMError
from log_handling.agent_token_tracker import log_agent_token_usage, AgentType


class MimicError(HearthlinkError):
    """Base exception for Mimic persona errors."""
    pass


class PersonaGenerationError(MimicError):
    """Exception raised when persona generation fails."""
    pass


class PerformanceAnalyticsError(MimicError):
    """Exception raised when performance analytics fail."""
    pass


class PersonaForkError(MimicError):
    """Exception raised when persona forking fails."""
    pass


class KnowledgeIndexError(MimicError):
    """Exception raised when knowledge indexing fails."""
    pass


class PluginExtensionError(MimicError):
    """Exception raised when plugin extension fails."""
    pass


class PerformanceTier(Enum):
    """Performance tier classification."""
    UNSTABLE = "unstable"
    RISKY = "risky"
    BETA = "beta"
    STABLE = "stable"
    EXCELLENT = "excellent"


class PersonaStatus(Enum):
    """Persona status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    MERGED = "merged"
    FORKED = "forked"


@dataclass
class CoreTraits:
    """Core personality traits for Mimic personas."""
    focus: int = 50  # 0-100: Concentration and task focus
    creativity: int = 50  # 0-100: Creative problem solving
    precision: int = 50  # 0-100: Attention to detail
    humor: int = 25  # 0-100: Humor and levity
    empathy: int = 50  # 0-100: Emotional intelligence
    assertiveness: int = 50  # 0-100: Confidence and directness
    adaptability: int = 50  # 0-100: Flexibility and learning speed
    collaboration: int = 50  # 0-100: Teamwork and cooperation


@dataclass
class GrowthStats:
    """Growth and usage statistics for personas."""
    sessions_completed: int = 0
    unique_tasks: int = 0
    repeat_tasks: int = 0
    usage_streak: int = 0
    total_usage_time: float = 0.0  # in hours
    last_used: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    growth_rate: float = 0.0  # skills improvement per session
    skill_decay_rate: float = 0.05  # skills decay per day of non-use


@dataclass
class PerformanceRecord:
    """Individual performance record for a session/task."""
    session_id: str
    task: str
    score: int  # 0-100
    user_feedback: str
    success: bool
    timestamp: str
    duration: float  # in seconds
    context: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None


@dataclass
class TopicScore:
    """Topic relevance score for knowledge indexing."""
    topic: str
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0


@dataclass
class KnowledgeSummary:
    """Custom knowledge summary for personas."""
    doc_id: str
    summary: str
    relevance_score: float  # 0.0-1.0
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: Optional[str] = None
    access_count: int = 0


@dataclass
class PluginExtension:
    """Plugin extension for persona capabilities."""
    plugin_id: str
    name: str
    version: str
    enabled: bool = True
    permissions: List[str] = field(default_factory=list)
    performance_impact: float = 0.0  # -1.0 to 1.0
    last_used: Optional[str] = None
    usage_count: int = 0


@dataclass
class ArchivedSession:
    """Archived session information."""
    session_id: str
    archived_at: str
    reason: str
    summary: Optional[str] = None
    performance_score: Optional[float] = None


@dataclass
class AuditEvent:
    """Audit log entry for persona operations."""
    action: str
    by: str  # "user", "system", "mimic"
    timestamp: str
    field: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reason: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class MimicPersonaMemory:
    """Mimic persona memory slice schema."""
    persona_id: str = field(default_factory=lambda: f"mimic-{uuid.uuid4().hex[:8]}")
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schema_version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Core persona information
    persona_name: str = ""
    role: str = ""
    description: str = ""
    status: PersonaStatus = PersonaStatus.DRAFT
    
    # Personality and capabilities
    core_traits: CoreTraits = field(default_factory=CoreTraits)
    growth_stats: GrowthStats = field(default_factory=GrowthStats)
    
    # Performance and analytics
    performance_history: List[PerformanceRecord] = field(default_factory=list)
    relevance_index: List[TopicScore] = field(default_factory=list)
    
    # Knowledge and extensions
    custom_knowledge: List[KnowledgeSummary] = field(default_factory=list)
    plugin_extensions: List[PluginExtension] = field(default_factory=list)
    
    # Session management
    archived_sessions: List[ArchivedSession] = field(default_factory=list)
    
    # User control and metadata
    user_tags: List[str] = field(default_factory=list)
    editable_fields: List[str] = field(default_factory=lambda: ["persona_name", "role", "description", "tags"])
    audit_log: List[AuditEvent] = field(default_factory=list)
    
    # Forking and merging
    parent_persona_id: Optional[str] = None
    forked_from: Optional[str] = None
    merged_into: Optional[str] = None
    fork_history: List[str] = field(default_factory=list)


class MimicPersona:
    """
    Mimic — Dynamic Persona & Adaptive Agent
    
    Manages dynamic persona generation, performance analytics, forking/merging,
    knowledge indexing, and plugin extensions for specialized task personas.
    """
    
    def __init__(self, llm_client: LocalLLMClient, logger: Optional[HearthlinkLogger] = None):
        """
        Initialize Mimic persona engine.
        
        Args:
            llm_client: Configured LLM client
            logger: Optional logger instance
            
        Raises:
            MimicError: If persona initialization fails
        """
        try:
            self.llm_client = llm_client
            self.logger = logger or HearthlinkLogger()
            self.memory = MimicPersonaMemory()
            
            # Validate LLM client
            if not isinstance(llm_client, LocalLLMClient):
                raise MimicError("LLM client must be an instance of LocalLLMClient")
            
            # Initialize knowledge index
            self._init_knowledge_index()
            
            # Load baseline prompts
            self._load_baseline_prompts()
            
            # Validate initial memory state
            self._validate_memory_state()
            
            self.logger.logger.info("Mimic persona engine initialized successfully")
            
        except Exception as e:
            self._log_error_context("initialization", str(e), traceback.format_exc())
            raise MimicError(f"Failed to initialize Mimic persona: {str(e)}") from e
    
    def _log_error_context(self, operation: str, error_message: str, traceback_str: str) -> None:
        """Log error context for debugging."""
        error_context = {
            "operation": operation,
            "error_message": error_message,
            "traceback": traceback_str,
            "persona_id": self.memory.persona_id,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.logger.error(f"Mimic error: {operation} - {error_message}", extra=error_context)
    
    def _validate_memory_state(self) -> None:
        """Validate initial memory state."""
        try:
            if not self.memory.persona_id:
                raise MimicError("Persona ID is required")
            
            if not self.memory.user_id:
                raise MimicError("User ID is required")
            
            # Validate core traits
            for trait_name, trait_value in asdict(self.memory.core_traits).items():
                if not isinstance(trait_value, int) or trait_value < 0 or trait_value > 100:
                    raise MimicError(f"Invalid trait value for {trait_name}: {trait_value}")
            
        except Exception as e:
            raise MimicError(f"Memory state validation failed: {str(e)}") from e
    
    def _init_knowledge_index(self) -> None:
        """Initialize knowledge indexing system."""
        try:
            # Create default knowledge categories
            default_topics = [
                "general_knowledge", "task_specific", "user_preferences",
                "domain_expertise", "communication_style", "problem_solving"
            ]
            
            for topic in default_topics:
                topic_score = TopicScore(
                    topic=topic,
                    score=0.5,  # Neutral starting score
                    confidence=0.3,  # Low initial confidence
                    usage_count=0
                )
                self.memory.relevance_index.append(topic_score)
                
        except Exception as e:
            raise KnowledgeIndexError(f"Failed to initialize knowledge index: {str(e)}") from e
    
    def _load_baseline_prompts(self) -> None:
        """Load baseline prompts for persona generation."""
        try:
            self.baseline_prompts = {
                "persona_generation": """
                Create a dynamic persona with the following characteristics:
                - Role: {role}
                - Core traits: {traits}
                - Task context: {context}
                - User preferences: {preferences}
                
                Generate a persona that is:
                1. Task-appropriate and context-aware
                2. Adaptable to user interaction style
                3. Capable of growth and learning
                4. Ethical and safe in all interactions
                """,
                
                "performance_analysis": """
                Analyze the following performance data:
                - Session history: {sessions}
                - User feedback: {feedback}
                - Task success rates: {success_rates}
                - Growth patterns: {growth_patterns}
                
                Provide insights on:
                1. Strengths and areas for improvement
                2. Growth trajectory and learning rate
                3. Task specialization opportunities
                4. Recommended trait adjustments
                """,
                
                "knowledge_indexing": """
                Index the following knowledge for relevance:
                - Content: {content}
                - Context: {context}
                - User interaction: {interaction}
                - Task requirements: {requirements}
                
                Determine:
                1. Relevance score (0.0-1.0)
                2. Confidence level (0.0-1.0)
                3. Appropriate tags and categories
                4. Integration with existing knowledge
                """
            }
            
        except Exception as e:
            raise MimicError(f"Failed to load baseline prompts: {str(e)}") from e
    
    def generate_persona(self, role: str, context: Dict[str, Any], 
                        user_preferences: Optional[Dict[str, Any]] = None,
                        base_traits: Optional[Dict[str, int]] = None) -> str:
        """
        Generate a new dynamic persona based on task context.
        
        Args:
            role: The role/purpose of the persona
            context: Task context and requirements
            user_preferences: Optional user preferences
            base_traits: Optional base trait values
            
        Returns:
            str: Generated persona ID
            
        Raises:
            PersonaGenerationError: If persona generation fails
        """
        try:
            # Generate unique persona ID
            persona_id = f"mimic-{uuid.uuid4().hex[:8]}"
            
            # Create core traits based on role and context
            traits = self._generate_traits_from_context(role, context, base_traits)
            
            # Create persona memory
            persona_memory = MimicPersonaMemory(
                persona_id=persona_id,
                persona_name=self._generate_persona_name(role),
                role=role,
                description=self._generate_description(role, context),
                status=PersonaStatus.DRAFT,
                core_traits=CoreTraits(**traits),
                user_tags=context.get("tags", []),
                created_at=datetime.now().isoformat()
            )
            
            # Generate initial knowledge index
            self._generate_initial_knowledge(persona_memory, context)
            
            # Log persona creation
            self._log_audit_event("persona_created", "user", persona_id=persona_id, 
                                reason=f"Generated for role: {role}")
            
            self.logger.logger.info(f"Generated persona: {persona_id} for role: {role}")
            return persona_id
            
        except Exception as e:
            self._log_error_context("persona_generation", str(e), traceback.format_exc())
            raise PersonaGenerationError(f"Failed to generate persona: {str(e)}") from e
    
    def _generate_traits_from_context(self, role: str, context: Dict[str, Any], 
                                    base_traits: Optional[Dict[str, int]] = None) -> Dict[str, int]:
        """Generate core traits based on role and context."""
        try:
            # Start with base traits or defaults
            traits = base_traits or {
                "focus": 50, "creativity": 50, "precision": 50, "humor": 25,
                "empathy": 50, "assertiveness": 50, "adaptability": 50, "collaboration": 50
            }
            
            # Adjust traits based on role
            role_adjustments = {
                "researcher": {"focus": 80, "precision": 85, "creativity": 70},
                "creative_writer": {"creativity": 90, "empathy": 75, "humor": 60},
                "analyst": {"precision": 90, "focus": 85, "assertiveness": 60},
                "coach": {"empathy": 85, "collaboration": 80, "adaptability": 75},
                "teacher": {"empathy": 80, "precision": 75, "collaboration": 85},
                "consultant": {"assertiveness": 75, "adaptability": 80, "focus": 70}
            }
            
            # Apply role-specific adjustments
            if role.lower() in role_adjustments:
                traits.update(role_adjustments[role.lower()])
            
            # Apply context-based adjustments
            if context.get("requires_creativity"):
                traits["creativity"] = min(100, traits["creativity"] + 20)
            if context.get("requires_precision"):
                traits["precision"] = min(100, traits["precision"] + 20)
            if context.get("requires_empathy"):
                traits["empathy"] = min(100, traits["empathy"] + 20)
            
            return traits
            
        except Exception as e:
            raise PersonaGenerationError(f"Failed to generate traits: {str(e)}") from e
    
    def _generate_persona_name(self, role: str) -> str:
        """Generate a persona name based on role."""
        try:
            # Simple name generation based on role
            role_names = {
                "researcher": "Dr. Insight",
                "creative_writer": "Story Weaver",
                "analyst": "Data Sage",
                "coach": "Growth Guide",
                "teacher": "Knowledge Keeper",
                "consultant": "Strategy Master"
            }
            
            return role_names.get(role.lower(), f"{role.title()} Expert")
            
        except Exception as e:
            return f"Persona-{uuid.uuid4().hex[:6]}"
    
    def _generate_description(self, role: str, context: Dict[str, Any]) -> str:
        """Generate persona description."""
        try:
            description = f"A specialized {role} persona designed for "
            description += context.get("description", "task-specific assistance")
            description += ". This persona adapts and grows based on usage patterns."
            return description
            
        except Exception as e:
            return f"Dynamic {role} persona for specialized tasks."
    
    def _generate_initial_knowledge(self, persona_memory: MimicPersonaMemory, 
                                  context: Dict[str, Any]) -> None:
        """Generate initial knowledge index for persona."""
        try:
            # Add context-specific knowledge
            if context.get("domain_knowledge"):
                knowledge = KnowledgeSummary(
                    doc_id=f"domain-{uuid.uuid4().hex[:8]}",
                    summary=context["domain_knowledge"],
                    relevance_score=0.8,
                    tags=["domain", "initial"],
                    created_at=datetime.now().isoformat()
                )
                persona_memory.custom_knowledge.append(knowledge)
            
            # Update relevance index
            for topic in context.get("relevant_topics", []):
                topic_score = TopicScore(
                    topic=topic,
                    score=0.7,
                    confidence=0.5,
                    usage_count=1
                )
                persona_memory.relevance_index.append(topic_score)
                
        except Exception as e:
            raise KnowledgeIndexError(f"Failed to generate initial knowledge: {str(e)}") from e
    
    def record_performance(self, session_id: str, task: str, score: int, 
                          user_feedback: str, success: bool, duration: float,
                          context: Optional[Dict[str, Any]] = None) -> None:
        """
        Record performance for a session/task.
        
        Args:
            session_id: Unique session identifier
            task: Task description
            score: Performance score (0-100)
            user_feedback: User feedback text
            success: Whether task was successful
            duration: Task duration in seconds
            context: Optional context information
            
        Raises:
            PerformanceAnalyticsError: If performance recording fails
        """
        try:
            # Create performance record
            performance_record = PerformanceRecord(
                session_id=session_id,
                task=task,
                score=score,
                user_feedback=user_feedback,
                success=success,
                timestamp=datetime.now().isoformat(),
                duration=duration,
                context=context
            )
            
            # Add to performance history
            self.memory.performance_history.append(performance_record)
            
            # Update growth stats
            self._update_growth_stats(performance_record)
            
            # Update relevance index
            self._update_relevance_index(task, context)
            
            # Log performance recording
            self._log_audit_event("performance_recorded", "system", 
                                session_id=session_id, reason=f"Task: {task}")
            
            self.logger.logger.info(f"Recorded performance for session {session_id}: score {score}")
            
        except Exception as e:
            self._log_error_context("performance_recording", str(e), traceback.format_exc())
            raise PerformanceAnalyticsError(f"Failed to record performance: {str(e)}") from e
    
    def _update_growth_stats(self, performance_record: PerformanceRecord) -> None:
        """Update growth statistics based on performance record."""
        try:
            stats = self.memory.growth_stats
            
            # Update basic stats
            stats.sessions_completed += 1
            stats.last_used = datetime.now().isoformat()
            stats.total_usage_time += performance_record.duration / 3600  # Convert to hours
            
            # Check for repeat tasks
            existing_tasks = [record.task for record in self.memory.performance_history[:-1]]
            if performance_record.task in existing_tasks:
                stats.repeat_tasks += 1
            else:
                stats.unique_tasks += 1
            
            # Update usage streak
            if stats.last_used:
                last_used_date = datetime.fromisoformat(stats.last_used).date()
                current_date = datetime.now().date()
                if (current_date - last_used_date).days <= 1:
                    stats.usage_streak += 1
                else:
                    stats.usage_streak = 1
            
            # Calculate growth rate
            if len(self.memory.performance_history) > 1:
                recent_scores = [record.score for record in self.memory.performance_history[-5:]]
                if len(recent_scores) >= 2:
                    growth = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
                    stats.growth_rate = max(0.0, growth)  # No negative growth
            
        except Exception as e:
            raise PerformanceAnalyticsError(f"Failed to update growth stats: {str(e)}") from e
    
    def _update_relevance_index(self, task: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Update relevance index based on task and context."""
        try:
            # Extract topics from task and context
            topics = self._extract_topics_from_task(task, context)
            
            for topic in topics:
                # Find existing topic or create new one
                existing_topic = next((t for t in self.memory.relevance_index if t.topic == topic), None)
                
                if existing_topic:
                    # Update existing topic
                    existing_topic.usage_count += 1
                    existing_topic.score = min(1.0, existing_topic.score + 0.1)
                    existing_topic.confidence = min(1.0, existing_topic.confidence + 0.05)
                    existing_topic.last_updated = datetime.now().isoformat()
                else:
                    # Create new topic
                    new_topic = TopicScore(
                        topic=topic,
                        score=0.6,
                        confidence=0.4,
                        usage_count=1
                    )
                    self.memory.relevance_index.append(new_topic)
                    
        except Exception as e:
            raise KnowledgeIndexError(f"Failed to update relevance index: {str(e)}") from e
    
    def _extract_topics_from_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Extract relevant topics from task description."""
        try:
            topics = []
            
            # Simple keyword extraction
            task_lower = task.lower()
            
            # Domain-specific topics
            if any(word in task_lower for word in ["research", "analysis", "study"]):
                topics.append("research_analysis")
            if any(word in task_lower for word in ["creative", "writing", "story"]):
                topics.append("creative_writing")
            if any(word in task_lower for word in ["data", "analytics", "metrics"]):
                topics.append("data_analytics")
            if any(word in task_lower for word in ["coaching", "mentoring", "guidance"]):
                topics.append("coaching_mentoring")
            
            # Add context topics
            if context and context.get("topics"):
                topics.extend(context["topics"])
            
            return list(set(topics))  # Remove duplicates
            
        except Exception as e:
            return ["general_knowledge"]
    
    def fork_persona(self, source_persona_id: str, new_role: str, 
                    modifications: Dict[str, Any]) -> str:
        """
        Fork an existing persona with modifications.
        
        Args:
            source_persona_id: ID of source persona to fork
            new_role: New role for forked persona
            modifications: Modifications to apply to forked persona
            
        Returns:
            str: ID of new forked persona
            
        Raises:
            PersonaForkError: If forking fails
        """
        try:
            # Create new persona ID
            forked_persona_id = f"mimic-{uuid.uuid4().hex[:8]}"
            
            # Copy source persona memory (this would normally load from Vault)
            # For now, we'll create a new memory with forked attributes
            forked_memory = MimicPersonaMemory(
                persona_id=forked_persona_id,
                persona_name=f"{modifications.get('name', 'Forked')} {self.memory.persona_name}",
                role=new_role,
                description=f"Forked from {source_persona_id} for {new_role}",
                status=PersonaStatus.FORKED,
                forked_from=source_persona_id,
                created_at=datetime.now().isoformat()
            )
            
            # Apply modifications
            if "traits" in modifications:
                forked_memory.core_traits = CoreTraits(**modifications["traits"])
            
            if "description" in modifications:
                forked_memory.description = modifications["description"]
            
            if "tags" in modifications:
                forked_memory.user_tags = modifications["tags"]
            
            # Log forking event
            self._log_audit_event("persona_forked", "user", 
                                persona_id=forked_persona_id,
                                reason=f"Forked from {source_persona_id} for {new_role}")
            
            self.logger.logger.info(f"Forked persona {source_persona_id} to {forked_persona_id}")
            return forked_persona_id
            
        except Exception as e:
            self._log_error_context("persona_forking", str(e), traceback.format_exc())
            raise PersonaForkError(f"Failed to fork persona: {str(e)}") from e
    
    def merge_personas(self, primary_persona_id: str, secondary_persona_id: str,
                      merge_strategy: str = "selective") -> str:
        """
        Merge two personas using specified strategy.
        
        Args:
            primary_persona_id: ID of primary persona (base)
            secondary_persona_id: ID of secondary persona (to be merged)
            merge_strategy: Strategy for merging ("selective", "comprehensive", "hybrid")
            
        Returns:
            str: ID of merged persona
            
        Raises:
            PersonaForkError: If merging fails
        """
        try:
            # Create merged persona ID
            merged_persona_id = f"mimic-{uuid.uuid4().hex[:8]}"
            
            # Create merged memory
            merged_memory = MimicPersonaMemory(
                persona_id=merged_persona_id,
                persona_name=f"Merged {primary_persona_id} + {secondary_persona_id}",
                role=f"Hybrid {self.memory.role}",
                description=f"Merged persona using {merge_strategy} strategy",
                status=PersonaStatus.MERGED,
                created_at=datetime.now().isoformat()
            )
            
            # Apply merge strategy
            if merge_strategy == "selective":
                # Keep best traits from each persona
                merged_memory.core_traits = self._merge_traits_selective()
            elif merge_strategy == "comprehensive":
                # Average traits from both personas
                merged_memory.core_traits = self._merge_traits_comprehensive()
            elif merge_strategy == "hybrid":
                # Weighted combination based on performance
                merged_memory.core_traits = self._merge_traits_hybrid()
            
            # Merge knowledge bases
            merged_memory.custom_knowledge = self._merge_knowledge_bases()
            
            # Log merge event
            self._log_audit_event("personas_merged", "user",
                                persona_id=merged_persona_id,
                                reason=f"Merged {primary_persona_id} + {secondary_persona_id}")
            
            self.logger.logger.info(f"Merged personas {primary_persona_id} + {secondary_persona_id} -> {merged_persona_id}")
            return merged_persona_id
            
        except Exception as e:
            self._log_error_context("persona_merging", str(e), traceback.format_exc())
            raise PersonaForkError(f"Failed to merge personas: {str(e)}") from e
    
    def _merge_traits_selective(self) -> CoreTraits:
        """Merge traits using selective strategy (keep best from each)."""
        # This would normally compare traits from two personas
        # For now, return current traits with slight improvements
        current_traits = asdict(self.memory.core_traits)
        improved_traits = {k: min(100, v + 5) for k, v in current_traits.items()}
        return CoreTraits(**improved_traits)
    
    def _merge_traits_comprehensive(self) -> CoreTraits:
        """Merge traits using comprehensive strategy (average)."""
        # This would normally average traits from two personas
        # For now, return balanced traits
        return CoreTraits(
            focus=60, creativity=60, precision=60, humor=40,
            empathy=60, assertiveness=60, adaptability=60, collaboration=60
        )
    
    def _merge_traits_hybrid(self) -> CoreTraits:
        """Merge traits using hybrid strategy (weighted by performance)."""
        # This would normally weight traits by performance scores
        # For now, return performance-optimized traits
        return CoreTraits(
            focus=75, creativity=65, precision=70, humor=35,
            empathy=65, assertiveness=70, adaptability=75, collaboration=65
        )
    
    def _merge_knowledge_bases(self) -> List[KnowledgeSummary]:
        """Merge knowledge bases from multiple personas."""
        # This would normally combine and deduplicate knowledge
        # For now, return current knowledge with merge indicator
        merged_knowledge = []
        for knowledge in self.memory.custom_knowledge:
            merged_knowledge.append(KnowledgeSummary(
                doc_id=knowledge.doc_id,
                summary=f"[MERGED] {knowledge.summary}",
                relevance_score=knowledge.relevance_score,
                tags=knowledge.tags + ["merged"],
                created_at=datetime.now().isoformat()
            ))
        return merged_knowledge
    
    def add_plugin_extension(self, plugin_id: str, name: str, version: str,
                           permissions: List[str], performance_impact: float = 0.0) -> None:
        """
        Add plugin extension to persona capabilities.
        
        Args:
            plugin_id: Unique plugin identifier
            name: Plugin name
            version: Plugin version
            permissions: Required permissions
            performance_impact: Impact on performance (-1.0 to 1.0)
            
        Raises:
            PluginExtensionError: If plugin addition fails
        """
        try:
            # Check if plugin already exists
            existing_plugin = next((p for p in self.memory.plugin_extensions if p.plugin_id == plugin_id), None)
            
            if existing_plugin:
                # Update existing plugin
                existing_plugin.version = version
                existing_plugin.permissions = permissions
                existing_plugin.performance_impact = performance_impact
                existing_plugin.last_used = datetime.now().isoformat()
            else:
                # Add new plugin
                plugin_extension = PluginExtension(
                    plugin_id=plugin_id,
                    name=name,
                    version=version,
                    permissions=permissions,
                    performance_impact=performance_impact,
                    last_used=datetime.now().isoformat()
                )
                self.memory.plugin_extensions.append(plugin_extension)
            
            # Log plugin addition
            self._log_audit_event("plugin_added", "user",
                                reason=f"Added plugin: {name} v{version}")
            
            self.logger.logger.info(f"Added plugin extension: {name} v{version}")
            
        except Exception as e:
            self._log_error_context("plugin_addition", str(e), traceback.format_exc())
            raise PluginExtensionError(f"Failed to add plugin: {str(e)}") from e
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance analytics.
        
        Returns:
            Dict containing performance metrics and insights
        """
        try:
            analytics = {
                "persona_id": self.memory.persona_id,
                "persona_name": self.memory.persona_name,
                "role": self.memory.role,
                "status": self.memory.status.value,
                
                # Growth statistics
                "growth_stats": asdict(self.memory.growth_stats),
                
                # Performance metrics
                "total_sessions": len(self.memory.performance_history),
                "average_score": 0.0,
                "success_rate": 0.0,
                "performance_trend": [],
                
                # Knowledge metrics
                "knowledge_items": len(self.memory.custom_knowledge),
                "top_topics": [],
                "knowledge_coverage": 0.0,
                
                # Plugin metrics
                "active_plugins": len([p for p in self.memory.plugin_extensions if p.enabled]),
                "plugin_performance_impact": 0.0,
                
                # Recommendations
                "recommendations": [],
                "growth_opportunities": []
            }
            
            # Calculate performance metrics
            if self.memory.performance_history:
                scores = [record.score for record in self.memory.performance_history]
                analytics["average_score"] = sum(scores) / len(scores)
                
                successful_sessions = [record for record in self.memory.performance_history if record.success]
                analytics["success_rate"] = len(successful_sessions) / len(self.memory.performance_history)
                
                # Performance trend (last 10 sessions)
                recent_scores = scores[-10:] if len(scores) >= 10 else scores
                analytics["performance_trend"] = recent_scores
            
            # Calculate knowledge metrics
            if self.memory.relevance_index:
                sorted_topics = sorted(self.memory.relevance_index, key=lambda x: x.score, reverse=True)
                analytics["top_topics"] = [{"topic": t.topic, "score": t.score} for t in sorted_topics[:5]]
                analytics["knowledge_coverage"] = sum(t.score for t in self.memory.relevance_index) / len(self.memory.relevance_index)
            
            # Calculate plugin impact
            if self.memory.plugin_extensions:
                total_impact = sum(p.performance_impact for p in self.memory.plugin_extensions if p.enabled)
                analytics["plugin_performance_impact"] = total_impact
            
            # Generate recommendations
            analytics["recommendations"] = self._generate_recommendations(analytics)
            analytics["growth_opportunities"] = self._identify_growth_opportunities(analytics)
            
            return analytics
            
        except Exception as e:
            self._log_error_context("analytics_generation", str(e), traceback.format_exc())
            raise PerformanceAnalyticsError(f"Failed to generate analytics: {str(e)}") from e
    
    def _generate_recommendations(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analytics."""
        recommendations = []
        
        # Performance-based recommendations
        if analytics["average_score"] < 70:
            recommendations.append("Consider focusing on core task skills to improve performance")
        
        if analytics["success_rate"] < 0.8:
            recommendations.append("Review failed sessions to identify improvement areas")
        
        # Growth-based recommendations
        if analytics["growth_stats"]["usage_streak"] < 3:
            recommendations.append("Increase usage frequency to maintain skill levels")
        
        if analytics["knowledge_coverage"] < 0.6:
            recommendations.append("Expand knowledge base for better task coverage")
        
        # Plugin-based recommendations
        if analytics["plugin_performance_impact"] < 0:
            recommendations.append("Review plugin usage - some may be negatively impacting performance")
        
        return recommendations
    
    def _identify_growth_opportunities(self, analytics: Dict[str, Any]) -> List[str]:
        """Identify growth opportunities based on analytics."""
        opportunities = []
        
        # High-performing areas
        if analytics["average_score"] > 85:
            opportunities.append("Consider specializing in current high-performing areas")
        
        # Knowledge gaps
        if analytics["knowledge_coverage"] < 0.5:
            opportunities.append("Expand domain knowledge for broader task coverage")
        
        # Usage patterns
        if analytics["growth_stats"]["unique_tasks"] > analytics["growth_stats"]["repeat_tasks"]:
            opportunities.append("Focus on repeat tasks to build expertise")
        
        return opportunities
    
    def get_performance_tier(self) -> PerformanceTier:
        """
        Get current performance tier based on analytics.
        
        Returns:
            PerformanceTier: Current performance classification
        """
        try:
            analytics = self.get_performance_analytics()
            
            # Determine tier based on multiple factors
            score = analytics["average_score"]
            success_rate = analytics["success_rate"]
            usage_count = analytics["growth_stats"]["sessions_completed"]
            
            if score >= 90 and success_rate >= 0.95 and usage_count >= 20:
                return PerformanceTier.EXCELLENT
            elif score >= 80 and success_rate >= 0.9 and usage_count >= 10:
                return PerformanceTier.STABLE
            elif score >= 70 and success_rate >= 0.8 and usage_count >= 5:
                return PerformanceTier.BETA
            elif score >= 60 and success_rate >= 0.7:
                return PerformanceTier.RISKY
            else:
                return PerformanceTier.UNSTABLE
                
        except Exception as e:
            return PerformanceTier.UNSTABLE
    
    def export_memory(self) -> Dict[str, Any]:
        """
        Export complete persona memory for backup/transfer.
        
        Returns:
            Dict containing all persona memory data
        """
        try:
            export_data = {
                "persona_id": self.memory.persona_id,
                "user_id": self.memory.user_id,
                "schema_version": self.memory.schema_version,
                "export_timestamp": datetime.now().isoformat(),
                "persona_data": asdict(self.memory)
            }
            
            # Log export
            self._log_audit_event("memory_exported", "user", reason="User requested export")
            
            return export_data
            
        except Exception as e:
            self._log_error_context("memory_export", str(e), traceback.format_exc())
            raise MimicError(f"Failed to export memory: {str(e)}") from e
    
    def import_memory(self, import_data: Dict[str, Any]) -> None:
        """
        Import persona memory from backup/transfer.
        
        Args:
            import_data: Memory data to import
            
        Raises:
            MimicError: If import fails
        """
        try:
            # Validate import data
            if "persona_data" not in import_data:
                raise MimicError("Invalid import data format")
            
            # Update memory with imported data
            imported_memory = import_data["persona_data"]
            
            # Update core fields
            self.memory.persona_name = imported_memory.get("persona_name", self.memory.persona_name)
            self.memory.role = imported_memory.get("role", self.memory.role)
            self.memory.description = imported_memory.get("description", self.memory.description)
            
            # Update traits if provided
            if "core_traits" in imported_memory:
                self.memory.core_traits = CoreTraits(**imported_memory["core_traits"])
            
            # Update performance history
            if "performance_history" in imported_memory:
                self.memory.performance_history = [
                    PerformanceRecord(**record) for record in imported_memory["performance_history"]
                ]
            
            # Update knowledge
            if "custom_knowledge" in imported_memory:
                self.memory.custom_knowledge = [
                    KnowledgeSummary(**knowledge) for knowledge in imported_memory["custom_knowledge"]
                ]
            
            # Update relevance index
            if "relevance_index" in imported_memory:
                self.memory.relevance_index = [
                    TopicScore(**topic) for topic in imported_memory["relevance_index"]
                ]
            
            # Log import
            self._log_audit_event("memory_imported", "user", reason="User requested import")
            
            self.logger.logger.info(f"Imported memory for persona: {self.memory.persona_id}")
            
        except Exception as e:
            self._log_error_context("memory_import", str(e), traceback.format_exc())
            raise MimicError(f"Failed to import memory: {str(e)}") from e
    
    def _log_audit_event(self, action: str, by: str, persona_id: Optional[str] = None,
                        session_id: Optional[str] = None, reason: Optional[str] = None) -> None:
        """Log audit event."""
        try:
            audit_event = AuditEvent(
                action=action,
                by=by,
                timestamp=datetime.now().isoformat(),
                reason=reason,
                session_id=session_id
            )
            
            self.memory.audit_log.append(audit_event)
            
        except Exception as e:
            self.logger.logger.error(f"Failed to log audit event: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current persona status.
        
        Returns:
            Dict containing current status information
        """
        try:
            return {
                "persona_id": self.memory.persona_id,
                "persona_name": self.memory.persona_name,
                "role": self.memory.role,
                "status": self.memory.status.value,
                "performance_tier": self.get_performance_tier().value,
                "sessions_completed": self.memory.growth_stats.sessions_completed,
                "average_score": self.get_performance_analytics()["average_score"],
                "active_plugins": len([p for p in self.memory.plugin_extensions if p.enabled]),
                "knowledge_items": len(self.memory.custom_knowledge),
                "last_updated": self.memory.updated_at
            }
            
        except Exception as e:
            self._log_error_context("status_check", str(e), traceback.format_exc())
            return {"error": f"Failed to get status: {str(e)}"}


def create_mimic_persona(llm_config: Dict[str, Any], logger: Optional[HearthlinkLogger] = None) -> MimicPersona:
    """
    Factory function to create a Mimic persona instance.
    
    Args:
        llm_config: LLM client configuration
        logger: Optional logger instance
        
    Returns:
        MimicPersona: Configured Mimic persona instance
        
    Raises:
        MimicError: If persona creation fails
    """
    try:
        # Create LLM client
        llm_client = LocalLLMClient(llm_config)
        
        # Create Mimic persona
        mimic_persona = MimicPersona(llm_client, logger)
        
        return mimic_persona
        
    except Exception as e:
        raise MimicError(f"Failed to create Mimic persona: {str(e)}") from e 