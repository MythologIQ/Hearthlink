"""
Hearthlink Unified Logging Module

Provides centralized exception logging and audit trail functionality
for all Hearthlink modules (Core, Vault, Synapse, Sentry, etc.).
"""

from .exception_handler import ExceptionHandler, LogLevel, LogContext

__all__ = [
    'ExceptionHandler',
    'LogLevel', 
    'LogContext'
] 