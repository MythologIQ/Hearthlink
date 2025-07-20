"""
API Module

Contains API implementations for Hearthlink:
- Alden API: REST API for Alden persona interactions
- Future: Core API, Vault API, etc.

Author: Hearthlink Development Team
Version: 1.0.0
"""

from .alden_api import (
    AldenAPI,
    MessageRequest,
    MessageResponse,
    TraitUpdateRequest,
    CorrectionRequest,
    MoodRequest,
    StatusResponse,
    create_alden_api
)

__all__ = [
    'AldenAPI',
    'MessageRequest',
    'MessageResponse',
    'TraitUpdateRequest',
    'CorrectionRequest',
    'MoodRequest',
    'StatusResponse',
    'create_alden_api'
] 