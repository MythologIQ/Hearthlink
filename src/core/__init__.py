"""
Core Module

Orchestrator for multi-agent conversational interaction, roundtables, 
agent performance challenges, and context switching.
"""

from .core import Core, Session, Participant, ParticipantType, SessionStatus, CoreError
from .error_handling import (
    CoreErrorHandler, CoreErrorRecovery, CoreErrorValidator, CoreErrorMetrics,
    SessionNotFoundError, ParticipantNotFoundError, InvalidOperationError,
    TurnTakingError, BreakoutRoomError, CommunalMemoryError, VaultIntegrationError,
    ErrorCategory, ErrorSeverity
)
from .behavioral_analysis import (
    BehavioralAnalysis, ExternalSignal, SignalType, BehavioralInsight,
    AdaptiveFeedback, BehavioralReport, BehavioralAnalysisError
)

__all__ = [
    'Core', 'Session', 'Participant', 'ParticipantType', 'SessionStatus', 'CoreError',
    'CoreErrorHandler', 'CoreErrorRecovery', 'CoreErrorValidator', 'CoreErrorMetrics',
    'SessionNotFoundError', 'ParticipantNotFoundError', 'InvalidOperationError',
    'TurnTakingError', 'BreakoutRoomError', 'CommunalMemoryError', 'VaultIntegrationError',
    'ErrorCategory', 'ErrorSeverity',
    'BehavioralAnalysis', 'ExternalSignal', 'SignalType', 'BehavioralInsight',
    'AdaptiveFeedback', 'BehavioralReport', 'BehavioralAnalysisError'
] 