"""
LLM Integration Module

Provides unified interface for local LLM engines including:
- Ollama
- LM Studio  
- Custom endpoints

Author: Hearthlink Development Team
Version: 1.0.0
"""

from .local_llm_client import (
    LocalLLMClient,
    LLMConfig,
    LLMRequest,
    LLMResponse,
    LLMError,
    LLMConnectionError,
    LLMResponseError,
    create_llm_client
)

__all__ = [
    'LocalLLMClient',
    'LLMConfig', 
    'LLMRequest',
    'LLMResponse',
    'LLMError',
    'LLMConnectionError',
    'LLMResponseError',
    'create_llm_client'
] 