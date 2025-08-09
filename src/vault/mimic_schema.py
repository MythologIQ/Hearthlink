#!/usr/bin/env python3
"""
Mimic Persona Vault Schema - Memory slice definitions for Mimic personas

Defines the schema for Mimic persona memory slices in the Vault,
including data structures, validation rules, and migration utilities.

References:
- hearthlink_system_documentation_master.md: Mimic persona specification
- vault.py: Vault storage implementation

Author: Hearthlink Development Team
Version: 1.0.0
"""

import os
import sys
import json
import uuid
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vault.schema import PersonaMemory, AuditLogEntry


class MimicSchemaError(Exception):
    """Base exception for Mimic schema errors."""
    pass


class SchemaValidationError(MimicSchemaError):
    """Exception raised when schema validation fails."""
    pass


class SchemaMigrationError(MimicSchemaError):
    """Exception raised when schema migration fails."""
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
    
    def validate(self) -> None:
        """Validate trait values."""
        for trait_name, trait_value in asdict(self).items():
            if not isinstance(trait_value, int) or trait_value < 0 or trait_value > 100:
                raise SchemaValidationError(f"Invalid trait value for {trait_name}: {trait_value}")


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
    
    def validate(self) -> None:
        """Validate growth stats."""
        if self.sessions_completed < 0:
            raise SchemaValidationError("sessions_completed cannot be negative")
        if self.unique_tasks < 0:
            raise SchemaValidationError("unique_tasks cannot be negative")
        if self.repeat_tasks < 0:
            raise SchemaValidationError("repeat_tasks cannot be negative")
        if self.usage_streak < 0:
            raise SchemaValidationError("usage_streak cannot be negative")
        if self.total_usage_time < 0.0:
            raise SchemaValidationError("total_usage_time cannot be negative")
        if self.growth_rate < -1.0 or self.growth_rate > 1.0:
            raise SchemaValidationError("growth_rate must be between -1.0 and 1.0")
        if self.skill_decay_rate < 0.0 or self.skill_decay_rate > 1.0:
            raise SchemaValidationError("skill_decay_rate must be between 0.0 and 1.0")


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
    
    def validate(self) -> None:
        """Validate performance record."""
        if not self.session_id:
            raise SchemaValidationError("session_id is required")
        if not self.task:
            raise SchemaValidationError("task is required")
        if self.score < 0 or self.score > 100:
            raise SchemaValidationError("score must be between 0 and 100")
        if not self.user_feedback:
            raise SchemaValidationError("user_feedback is required")
        if self.duration < 0.0:
            raise SchemaValidationError("duration cannot be negative")
        if not self.timestamp:
            raise SchemaValidationError("timestamp is required")


@dataclass
class TopicScore:
    """Topic relevance score for knowledge indexing."""
    topic: str
    score: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    
    def validate(self) -> None:
        """Validate topic score."""
        if not self.topic:
            raise SchemaValidationError("topic is required")
        if self.score < 0.0 or self.score > 1.0:
            raise SchemaValidationError("score must be between 0.0 and 1.0")
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise SchemaValidationError("confidence must be between 0.0 and 1.0")
        if self.usage_count < 0:
            raise SchemaValidationError("usage_count cannot be negative")
        if not self.last_updated:
            raise SchemaValidationError("last_updated is required")


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
    
    def validate(self) -> None:
        """Validate knowledge summary."""
        if not self.doc_id:
            raise SchemaValidationError("doc_id is required")
        if not self.summary:
            raise SchemaValidationError("summary is required")
        if self.relevance_score < 0.0 or self.relevance_score > 1.0:
            raise SchemaValidationError("relevance_score must be between 0.0 and 1.0")
        if self.access_count < 0:
            raise SchemaValidationError("access_count cannot be negative")
        if not self.created_at:
            raise SchemaValidationError("created_at is required")


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
    
    def validate(self) -> None:
        """Validate plugin extension."""
        if not self.plugin_id:
            raise SchemaValidationError("plugin_id is required")
        if not self.name:
            raise SchemaValidationError("name is required")
        if not self.version:
            raise SchemaValidationError("version is required")
        if self.performance_impact < -1.0 or self.performance_impact > 1.0:
            raise SchemaValidationError("performance_impact must be between -1.0 and 1.0")
        if self.usage_count < 0:
            raise SchemaValidationError("usage_count cannot be negative")


@dataclass
class ArchivedSession:
    """Archived session information."""
    session_id: str
    archived_at: str
    reason: str
    summary: Optional[str] = None
    performance_score: Optional[float] = None
    
    def validate(self) -> None:
        """Validate archived session."""
        if not self.session_id:
            raise SchemaValidationError("session_id is required")
        if not self.archived_at:
            raise SchemaValidationError("archived_at is required")
        if not self.reason:
            raise SchemaValidationError("reason is required")
        if self.performance_score is not None and (self.performance_score < 0.0 or self.performance_score > 1.0):
            raise SchemaValidationError("performance_score must be between 0.0 and 1.0")


@dataclass
class AuditEvent:
    """Audit log entry."""
    action: str
    by: str  # "user", "system", "mimic"
    timestamp: str
    field: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    reason: Optional[str] = None
    session_id: Optional[str] = None
    
    def validate(self) -> None:
        """Validate audit event."""
        if not self.action:
            raise SchemaValidationError("action is required")
        if not self.by:
            raise SchemaValidationError("by is required")
        if not self.timestamp:
            raise SchemaValidationError("timestamp is required")


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
    
    def validate(self) -> None:
        """Validate complete Mimic persona memory."""
        try:
            # Validate required fields
            if not self.persona_id:
                raise SchemaValidationError("persona_id is required")
            if not self.user_id:
                raise SchemaValidationError("user_id is required")
            if not self.schema_version:
                raise SchemaValidationError("schema_version is required")
            if not self.created_at:
                raise SchemaValidationError("created_at is required")
            if not self.updated_at:
                raise SchemaValidationError("updated_at is required")
            
            # Validate core traits
            self.core_traits.validate()
            
            # Validate growth stats
            self.growth_stats.validate()
            
            # Validate performance history
            for record in self.performance_history:
                record.validate()
            
            # Validate relevance index
            for topic in self.relevance_index:
                topic.validate()
            
            # Validate custom knowledge
            for knowledge in self.custom_knowledge:
                knowledge.validate()
            
            # Validate plugin extensions
            for plugin in self.plugin_extensions:
                plugin.validate()
            
            # Validate archived sessions
            for session in self.archived_sessions:
                session.validate()
            
            # Validate audit log
            for event in self.audit_log:
                event.validate()
            
        except Exception as e:
            raise SchemaValidationError(f"Memory validation failed: {str(e)}") from e
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary for storage."""
        try:
            data = asdict(self)
            
            # Convert enums to strings
            data["status"] = self.status.value
            
            return data
            
        except Exception as e:
            raise SchemaValidationError(f"Failed to convert memory to dict: {str(e)}") from e
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MimicPersonaMemory':
        """Create memory from dictionary."""
        try:
            # Convert string back to enum
            if "status" in data and isinstance(data["status"], str):
                data["status"] = PersonaStatus(data["status"])
            
            # Create memory instance
            memory = cls(**data)
            
            # Validate the memory
            memory.validate()
            
            return memory
            
        except Exception as e:
            raise SchemaValidationError(f"Failed to create memory from dict: {str(e)}") from e


class MimicSchemaManager:
    """
    Schema manager for Mimic persona memory slices.
    
    Handles schema validation, migration, and version management.
    """
    
    def __init__(self, logger=None):
        """
        Initialize schema manager.
        
        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.current_version = "1.0.0"
        self.supported_versions = ["1.0.0"]
    
    def validate_memory(self, memory_data: Dict[str, Any]) -> bool:
        """
        Validate memory data against current schema.
        
        Args:
            memory_data: Memory data to validate
            
        Returns:
            bool: True if valid
            
        Raises:
            SchemaValidationError: If validation fails
        """
        try:
            # Create memory instance from data
            memory = MimicPersonaMemory.from_dict(memory_data)
            
            # Validate the memory
            memory.validate()
            
            return True
            
        except Exception as e:
            raise SchemaValidationError(f"Memory validation failed: {str(e)}") from e
    
    def migrate_memory(self, memory_data: Dict[str, Any], target_version: str = None) -> Dict[str, Any]:
        """
        Migrate memory data to target schema version.
        
        Args:
            memory_data: Memory data to migrate
            target_version: Target schema version (defaults to current)
            
        Returns:
            Dict: Migrated memory data
            
        Raises:
            SchemaMigrationError: If migration fails
        """
        try:
            target_version = target_version or self.current_version
            
            # Check if migration is needed
            current_version = memory_data.get("schema_version", "0.0.0")
            if current_version == target_version:
                return memory_data
            
            # Perform migration
            migrated_data = memory_data.copy()
            
            if current_version == "0.0.0" and target_version == "1.0.0":
                # Migration from pre-1.0.0 to 1.0.0
                migrated_data = self._migrate_to_1_0_0(memory_data)
            else:
                raise SchemaMigrationError(f"Migration from {current_version} to {target_version} not supported")
            
            # Update schema version
            migrated_data["schema_version"] = target_version
            migrated_data["updated_at"] = datetime.now().isoformat()
            
            # Validate migrated data
            self.validate_memory(migrated_data)
            
            self.logger.info(f"Migrated memory from {current_version} to {target_version}")
            return migrated_data
            
        except Exception as e:
            raise SchemaMigrationError(f"Memory migration failed: {str(e)}") from e
    
    def _migrate_to_1_0_0(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate memory data to version 1.0.0."""
        try:
            migrated_data = memory_data.copy()
            
            # Add missing fields with defaults
            if "schema_version" not in migrated_data:
                migrated_data["schema_version"] = "1.0.0"
            
            if "status" not in migrated_data:
                migrated_data["status"] = PersonaStatus.DRAFT.value
            
            if "core_traits" not in migrated_data:
                migrated_data["core_traits"] = asdict(CoreTraits())
            
            if "growth_stats" not in migrated_data:
                migrated_data["growth_stats"] = asdict(GrowthStats())
            
            if "performance_history" not in migrated_data:
                migrated_data["performance_history"] = []
            
            if "relevance_index" not in migrated_data:
                migrated_data["relevance_index"] = []
            
            if "custom_knowledge" not in migrated_data:
                migrated_data["custom_knowledge"] = []
            
            if "plugin_extensions" not in migrated_data:
                migrated_data["plugin_extensions"] = []
            
            if "archived_sessions" not in migrated_data:
                migrated_data["archived_sessions"] = []
            
            if "user_tags" not in migrated_data:
                migrated_data["user_tags"] = []
            
            if "editable_fields" not in migrated_data:
                migrated_data["editable_fields"] = ["persona_name", "role", "description", "tags"]
            
            if "audit_log" not in migrated_data:
                migrated_data["audit_log"] = []
            
            if "parent_persona_id" not in migrated_data:
                migrated_data["parent_persona_id"] = None
            
            if "forked_from" not in migrated_data:
                migrated_data["forked_from"] = None
            
            if "merged_into" not in migrated_data:
                migrated_data["merged_into"] = None
            
            if "fork_history" not in migrated_data:
                migrated_data["fork_history"] = []
            
            return migrated_data
            
        except Exception as e:
            raise SchemaMigrationError(f"Migration to 1.0.0 failed: {str(e)}") from e
    
    def create_memory_slice(self, persona_id: str, user_id: str, **kwargs) -> MimicPersonaMemory:
        """
        Create a new Mimic persona memory slice.
        
        Args:
            persona_id: Persona identifier
            user_id: User identifier
            **kwargs: Additional memory fields
            
        Returns:
            MimicPersonaMemory: New memory slice
        """
        try:
            memory = MimicPersonaMemory(
                persona_id=persona_id,
                user_id=user_id,
                **kwargs
            )
            
            # Validate the new memory
            memory.validate()
            
            return memory
            
        except Exception as e:
            raise SchemaValidationError(f"Failed to create memory slice: {str(e)}") from e
    
    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get schema information.
        
        Returns:
            Dict containing schema information
        """
        return {
            "current_version": self.current_version,
            "supported_versions": self.supported_versions,
            "schema_fields": [
                "persona_id", "user_id", "schema_version", "created_at", "updated_at",
                "persona_name", "role", "description", "status",
                "core_traits", "growth_stats", "performance_history", "relevance_index",
                "custom_knowledge", "plugin_extensions", "archived_sessions",
                "user_tags", "editable_fields", "audit_log",
                "parent_persona_id", "forked_from", "merged_into", "fork_history"
            ],
            "required_fields": [
                "persona_id", "user_id", "schema_version", "created_at", "updated_at"
            ]
        }


# Global schema manager instance
schema_manager = MimicSchemaManager()


def validate_mimic_memory(memory_data: Dict[str, Any]) -> bool:
    """
    Validate Mimic persona memory data.
    
    Args:
        memory_data: Memory data to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        SchemaValidationError: If validation fails
    """
    return schema_manager.validate_memory(memory_data)


def migrate_mimic_memory(memory_data: Dict[str, Any], target_version: str = None) -> Dict[str, Any]:
    """
    Migrate Mimic persona memory data.
    
    Args:
        memory_data: Memory data to migrate
        target_version: Target schema version
        
    Returns:
        Dict: Migrated memory data
        
    Raises:
        SchemaMigrationError: If migration fails
    """
    return schema_manager.migrate_memory(memory_data, target_version)


def create_mimic_memory_slice(persona_id: str, user_id: str, **kwargs) -> MimicPersonaMemory:
    """
    Create a new Mimic persona memory slice.
    
    Args:
        persona_id: Persona identifier
        user_id: User identifier
        **kwargs: Additional memory fields
        
    Returns:
        MimicPersonaMemory: New memory slice
    """
    return schema_manager.create_memory_slice(persona_id, user_id, **kwargs) 