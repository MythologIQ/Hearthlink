#!/usr/bin/env python3
"""
LLM Connector Service
Handles connections to local LLM services (Ollama, etc.)
"""

import json
import requests
import asyncio
from typing import Dict, List, Optional

class LLMConnector:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.connected = False
        self.available_models = []
        
    async def check_ollama_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                self.available_models = [model['name'] for model in models_data.get('models', [])]
                self.connected = True
                return True
        except requests.exceptions.RequestException:
            pass
        
        self.connected = False
        return False
    
    async def install_model(self, model_name: str) -> bool:
        """Install a model via Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minute timeout for model downloads
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    async def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about a specific model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/show",
                json={"name": model_name},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return None
    
    async def generate_response(self, model_name: str, prompt: str) -> Optional[str]:
        """Generate a response using the specified model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('response', '')
        except requests.exceptions.RequestException:
            pass
        return None
    
    def get_status(self) -> Dict:
        """Get current LLM connector status"""
        return {
            'connected': self.connected,
            'ollama_url': self.ollama_url,
            'available_models': self.available_models,
            'model_count': len(self.available_models)
        }

# Global connector instance
llm_connector = LLMConnector()

async def initialize_llm_services():
    """Initialize LLM services"""
    print("Initializing LLM services...")
    
    # Check Ollama connection
    ollama_connected = await llm_connector.check_ollama_connection()
    if ollama_connected:
        print(f"✓ Ollama connected - {len(llm_connector.available_models)} models available")
        for model in llm_connector.available_models:
            print(f"  - {model}")
    else:
        print("✗ Ollama not connected")
        print("  To install Ollama: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  Then run: ollama serve")
    
    # Recommend models to install
    recommended_models = ["llama2", "codellama", "mistral"]
    for model in recommended_models:
        if model not in llm_connector.available_models:
            print(f"  Recommended: ollama pull {model}")
    
    return ollama_connected

if __name__ == '__main__':
    asyncio.run(initialize_llm_services())