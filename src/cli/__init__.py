"""
CLI Module

Contains command-line interface implementations for Hearthlink:
- Alden CLI: Interactive CLI for Alden persona
- Future: Core CLI, Vault CLI, etc.

Author: Hearthlink Development Team
Version: 1.0.0
"""

from .alden_cli import (
    AldenCLI,
    create_alden_cli
)

__all__ = [
    'AldenCLI',
    'create_alden_cli'
] 