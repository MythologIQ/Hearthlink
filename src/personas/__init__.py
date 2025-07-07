"""
Personas Module

Contains persona implementations for Hearthlink:
- Alden: Primary local agent/persona
- Future: Alice, Mimic, Sentry, etc.

Author: Hearthlink Development Team
Version: 1.0.0
"""

from .alden import (
    AldenPersona,
    AldenPersonaMemory,
    PersonaError,
    PersonaMemoryError,
    MotivationStyle,
    CorrectionEvent,
    SessionMood,
    RelationshipEvent,
    AuditEvent,
    create_alden_persona
)

__all__ = [
    'AldenPersona',
    'AldenPersonaMemory',
    'PersonaError',
    'PersonaMemoryError', 
    'MotivationStyle',
    'CorrectionEvent',
    'SessionMood',
    'RelationshipEvent',
    'AuditEvent',
    'create_alden_persona'
] 