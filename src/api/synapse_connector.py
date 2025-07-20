#!/usr/bin/env python3
"""
Synapse API Connector
Handles connections to external APIs (Claude, Google AI Studio, etc.)
"""

import os
import json
import requests
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

class SynapseConnector:
    def __init__(self):
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.google_ai_key = os.getenv('GOOGLE_AI_KEY')
        self.claude_connected = False
        self.google_ai_connected = False
        self.connection_status = {}
        
    async def test_claude_connection(self) -> bool:
        """Test connection to Claude API"""
        if not self.claude_api_key:
            print("Claude API key not found. Set CLAUDE_API_KEY environment variable.")
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.claude_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Test with a simple request
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json={
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 10,
                    'messages': [{'role': 'user', 'content': 'Test'}]
                },
                timeout=10
            )
            
            self.claude_connected = response.status_code == 200
            self.connection_status['claude'] = {
                'connected': self.claude_connected,
                'status_code': response.status_code,
                'last_check': datetime.now().isoformat()
            }
            
            return self.claude_connected
            
        except requests.exceptions.RequestException as e:
            print(f"Claude API connection error: {e}")
            self.claude_connected = False
            self.connection_status['claude'] = {
                'connected': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
            return False
    
    async def test_google_ai_connection(self) -> bool:
        """Test connection to Google AI Studio API"""
        if not self.google_ai_key:
            print("Google AI API key not found. Set GOOGLE_AI_KEY environment variable.")
            return False
        
        try:
            # Test with Gemini API
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.google_ai_key}',
                json={
                    'contents': [{'parts': [{'text': 'Test'}]}],
                    'generationConfig': {'maxOutputTokens': 10}
                },
                timeout=10
            )
            
            self.google_ai_connected = response.status_code == 200
            self.connection_status['google_ai'] = {
                'connected': self.google_ai_connected,
                'status_code': response.status_code,
                'last_check': datetime.now().isoformat()
            }
            
            return self.google_ai_connected
            
        except requests.exceptions.RequestException as e:
            print(f"Google AI API connection error: {e}")
            self.google_ai_connected = False
            self.connection_status['google_ai'] = {
                'connected': False,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
            return False
    
    async def call_claude_api(self, message: str, model: str = 'claude-3-sonnet-20240229') -> Optional[str]:
        """Make a request to Claude API"""
        if not self.claude_connected:
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.claude_api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json={
                    'model': model,
                    'max_tokens': 1000,
                    'messages': [{'role': 'user', 'content': message}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('content', [{}])[0].get('text', '')
            
        except requests.exceptions.RequestException as e:
            print(f"Claude API call error: {e}")
        
        return None
    
    async def call_google_ai_api(self, message: str, model: str = 'gemini-pro') -> Optional[str]:
        """Make a request to Google AI API"""
        if not self.google_ai_connected:
            return None
        
        try:
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.google_ai_key}',
                json={
                    'contents': [{'parts': [{'text': message}]}],
                    'generationConfig': {'maxOutputTokens': 1000}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                candidates = data.get('candidates', [])
                if candidates:
                    content = candidates[0].get('content', {})
                    parts = content.get('parts', [])
                    if parts:
                        return parts[0].get('text', '')
            
        except requests.exceptions.RequestException as e:
            print(f"Google AI API call error: {e}")
        
        return None
    
    def get_connection_status(self) -> Dict:
        """Get current connection status"""
        return {
            'claude_connected': self.claude_connected,
            'google_ai_connected': self.google_ai_connected,
            'connection_details': self.connection_status,
            'api_keys_configured': {
                'claude': self.claude_api_key is not None,
                'google_ai': self.google_ai_key is not None
            }
        }
    
    def get_available_models(self) -> Dict:
        """Get available models from each service"""
        models = {
            'claude': [],
            'google_ai': []
        }
        
        if self.claude_connected:
            models['claude'] = [
                'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307',
                'claude-3-opus-20240229'
            ]
        
        if self.google_ai_connected:
            models['google_ai'] = [
                'gemini-pro',
                'gemini-pro-vision'
            ]
        
        return models
    
    async def setup_api_keys(self, claude_key: Optional[str] = None, google_key: Optional[str] = None) -> bool:
        """Setup API keys"""
        if claude_key:
            self.claude_api_key = claude_key
            os.environ['CLAUDE_API_KEY'] = claude_key
            
        if google_key:
            self.google_ai_key = google_key
            os.environ['GOOGLE_AI_KEY'] = google_key
        
        # Test connections after setting keys
        await self.test_claude_connection()
        await self.test_google_ai_connection()
        
        return self.claude_connected or self.google_ai_connected

# Global synapse connector instance
synapse_connector = SynapseConnector()

async def initialize_synapse():
    """Initialize Synapse connections"""
    print("Initializing Synapse connections...")
    
    # Test Claude connection
    claude_result = await synapse_connector.test_claude_connection()
    if claude_result:
        print("✓ Claude API connected")
    else:
        print("✗ Claude API not connected")
        print("  Set CLAUDE_API_KEY environment variable")
    
    # Test Google AI connection
    google_result = await synapse_connector.test_google_ai_connection()
    if google_result:
        print("✓ Google AI API connected")
    else:
        print("✗ Google AI API not connected")
        print("  Set GOOGLE_AI_KEY environment variable")
    
    # Show available models
    models = synapse_connector.get_available_models()
    if models['claude']:
        print(f"  Claude models: {', '.join(models['claude'])}")
    if models['google_ai']:
        print(f"  Google AI models: {', '.join(models['google_ai'])}")
    
    return claude_result or google_result

if __name__ == '__main__':
    asyncio.run(initialize_synapse())