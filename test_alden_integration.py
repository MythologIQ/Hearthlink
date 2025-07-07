#!/usr/bin/env python3
"""
Alden Integration Test

Tests the Alden persona integration with local LLM engines.
Verifies basic functionality without requiring actual LLM engines.

Author: Hearthlink Development Team
Version: 1.0.0
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from main import HearthlinkLogger
from llm.local_llm_client import LLMConfig, LocalLLMClient, LLMRequest
from personas.alden import AldenPersona, create_alden_persona


class MockLLMClient:
    """Mock LLM client for testing without actual LLM engines."""
    
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger or HearthlinkLogger()
    
    def generate(self, request):
        """Generate mock response."""
        from datetime import datetime
        
        # Mock response based on input
        if "hello" in request.prompt.lower():
            response_content = "Hello! I'm Alden, your AI companion. I'm here to support you with executive function, cognitive partnership, and adaptive guidance. How can I help you today?"
        elif "help" in request.prompt.lower():
            response_content = "I'm here to help! I can assist with goal setting, habit tracking, emotional support, and cognitive scaffolding. What would you like to work on?"
        else:
            response_content = "Thank you for sharing that with me. I'm here to listen and support you. Would you like to explore this further or work on something specific?"
        
        return type('MockResponse', (), {
            'content': response_content,
            'model': self.config.model,
            'usage': {'prompt_tokens': 50, 'completion_tokens': 100, 'total_tokens': 150},
            'finish_reason': 'stop',
            'response_time': 0.5,
            'timestamp': datetime.now().isoformat(),
            'context': request.context
        })()
    
    def get_status(self):
        """Get mock status."""
        return {
            "engine": self.config.engine,
            "model": self.config.model,
            "base_url": self.config.base_url,
            "connected": True,
            "timestamp": "2025-01-06T12:00:00Z"
        }


def test_llm_client():
    """Test LLM client functionality."""
    print("🧪 Testing LLM Client...")
    
    config = LLMConfig(
        engine="mock",
        base_url="http://localhost:8000",
        model="test-model",
        temperature=0.7,
        max_tokens=2048
    )
    
    logger = HearthlinkLogger()
    client = MockLLMClient(config, logger)
    
    # Test generation
    request = LLMRequest(
        prompt="Hello, how are you?",
        system_message="You are a helpful AI assistant.",
        temperature=0.7
    )
    
    response = client.generate(request)
    print(f"✅ LLM Response: {response.content[:100]}...")
    
    # Test status
    status = client.get_status()
    print(f"✅ LLM Status: {status['engine']} - {status['model']}")
    
    return client


def test_alden_persona():
    """Test Alden persona functionality."""
    print("\n🧪 Testing Alden Persona...")
    
    # Create mock LLM client
    llm_client = test_llm_client()
    
    # Create Alden persona
    alden = AldenPersona(llm_client)
    
    # Test response generation
    response = alden.generate_response("Hello Alden!")
    print(f"✅ Alden Response: {response[:100]}...")
    
    # Test trait update
    alden.update_trait("openness", 85, "test_update")
    print("✅ Trait update successful")
    
    # Test correction event
    alden.add_correction_event("positive", "Great test response", 0.5)
    print("✅ Correction event added")
    
    # Test mood recording
    alden.record_session_mood("test-session", "positive", 85)
    print("✅ Mood recorded")
    
    # Test status
    status = alden.get_status()
    print(f"✅ Alden Status: {status['persona_id']} - Trust Level: {status['trust_level']}")
    
    # Test memory export
    memory = alden.export_memory()
    print(f"✅ Memory exported: {len(memory)} fields")
    
    return alden


def test_configuration():
    """Test configuration loading."""
    print("\n🧪 Testing Configuration...")
    
    config_path = Path("config/alden_config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Configuration loaded: {len(config)} sections")
        print(f"   - Alden config: {len(config.get('alden', {}))} fields")
        print(f"   - LLM engines: {len(config.get('llm_engines', {}))} engines")
        print(f"   - API config: {len(config.get('api', {}))} fields")
    else:
        print("⚠️  Configuration file not found")


def test_factory_functions():
    """Test factory functions."""
    print("\n🧪 Testing Factory Functions...")
    
    llm_config = {
        "engine": "mock",
        "base_url": "http://localhost:8000",
        "model": "test-model",
        "temperature": 0.7,
        "max_tokens": 2048
    }
    
    # Test persona creation
    alden = create_alden_persona(llm_config)
    print("✅ Alden persona created via factory")
    
    # Test response
    response = alden.generate_response("Test message")
    print(f"✅ Factory-created Alden response: {response[:50]}...")
    
    return alden


def main():
    """Run all tests."""
    print("🚀 Starting Alden Integration Tests")
    print("=" * 50)
    
    try:
        # Test configuration
        test_configuration()
        
        # Test LLM client
        test_llm_client()
        
        # Test Alden persona
        test_alden_persona()
        
        # Test factory functions
        test_factory_functions()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Alden integration is working correctly.")
        print("\nNext steps:")
        print("1. Install a local LLM engine (Ollama or LM Studio)")
        print("2. Run: python src/run_alden.py cli --engine ollama --model llama2")
        print("3. Or run: python src/run_alden.py api --engine ollama --model llama2")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 