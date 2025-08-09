#!/usr/bin/env python3
"""
Settings API Service
Handles system settings persistence and API connections testing
"""

import json
import os
import subprocess
import requests
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3005', 'http://127.0.0.1:3005', 'app://*'], supports_credentials=True)

# Settings file path
SETTINGS_FILE = Path("hearthlink_data/settings.json")

# Default settings
DEFAULT_SETTINGS = {
    "general": {
        "theme": "starcraft",
        "language": "en",
        "autoSave": True,
        "notifications": True,
        "voiceEnabled": True,
        "startupModule": "alden"
    },
    "apis": {
        "googleAiKey": "",
        "claudeCodePath": "",
        "ollamaUrl": "http://localhost:11434",
        "customEndpoints": []
    },
    "localLLM": {
        "enabled": False,
        "provider": "ollama",
        "endpoint": "http://localhost:11434",
        "dualLLMMode": True,
        "profiles": {
            "low": {
                "enabled": True,
                "model": "llama3.2:3b",
                "parameterRange": "2-3B",
                "roles": ["routing", "simple_tasks"],
                "temperature": 0.7,
                "contextLength": 16384,
                "priority": 1
            },
            "mid": {
                "enabled": True,
                "model": "llama3.1:8b",
                "parameterRange": "7-9B",
                "roles": ["reasoning", "coding", "complex_tasks"],
                "temperature": 0.7,
                "contextLength": 32768,
                "priority": 2
            }
        },
        "roleAssignments": {
            "routing": "low",
            "reasoning": "mid",
            "coding": "mid",
            "multimodal": "mid",
            "simple_tasks": "low",
            "complex_tasks": "mid"
        },
        "streaming": True,
        "autoStart": False,
        "fallbackEnabled": True,
        "healthCheckInterval": 30000
    },
    "agents": {
        "alden": {"enabled": True, "priority": 1},
        "alice": {"enabled": True, "priority": 2},
        "mimic": {"enabled": True, "priority": 3},
        "sentry": {"enabled": True, "priority": 4},
        "core": {"enabled": True, "priority": 0}
    },
    "voice": {
        "enabled": True,
        "sensitivity": 0.7,
        "language": "en-US",
        "wakeWord": "alden",
        "routingMode": "smart"
    },
    "security": {
        "encryptionEnabled": True,
        "auditLogging": True,
        "sessionTimeout": 30,
        "autoLock": False
    },
    "performance": {
        "maxMemoryUsage": 4096,
        "cachingEnabled": True,
        "preloadModules": True,
        "backgroundSync": True
    }
}

def load_settings():
    """Load settings from file"""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_settings = DEFAULT_SETTINGS.copy()
                for category, values in settings.items():
                    if category in merged_settings:
                        merged_settings[category].update(values)
                    else:
                        merged_settings[category] = values
                return merged_settings
    except Exception as e:
        print(f"Error loading settings: {e}")
    
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    try:
        # Ensure data directory exists
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    settings = load_settings()
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        new_settings = request.json
        if save_settings(new_settings):
            return jsonify({'success': True, 'message': 'Settings saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save settings'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/test/google-ai', methods=['POST'])
def test_google_ai():
    """Test Google AI API connection"""
    try:
        data = request.json
        api_key = data.get('googleAiKey')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'Google AI API key not provided'
            })
        
        # Test with a simple request
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
            json={
                'contents': [{'parts': [{'text': 'Hello'}]}],
                'generationConfig': {'maxOutputTokens': 5}
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'details': 'Google AI API connection successful'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'API returned status {response.status_code}'
            })
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Connection failed: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        })

@app.route('/api/test/claude-code', methods=['POST'])
def test_claude_code():
    """Test Claude Code CLI connection"""
    try:
        data = request.json
        cli_path = data.get('claudeCodePath')
        
        if not cli_path:
            # Check if we're in Claude Code environment
            if os.environ.get('CLAUDE_CODE') == 'true':
                return jsonify({
                    'success': True,
                    'details': 'Claude Code CLI environment detected'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Claude Code CLI path not provided'
                })
        
        # Test if the CLI exists and is executable
        if not os.path.exists(cli_path):
            return jsonify({
                'success': False,
                'error': 'Claude Code CLI not found at specified path'
            })
        
        # Test with version command
        result = subprocess.run(
            [cli_path, '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'details': f'Claude Code CLI found: {result.stdout.strip()}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'CLI test failed: {result.stderr.strip()}'
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'CLI test timed out'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        })

@app.route('/api/test/ollama', methods=['POST'])
def test_ollama():
    """Test Ollama connection"""
    try:
        data = request.json
        ollama_url = data.get('ollamaUrl', 'http://localhost:11434')
        
        # Test connection to Ollama
        response = requests.get(f'{ollama_url}/api/tags', timeout=5)
        
        if response.status_code == 200:
            models_data = response.json()
            model_count = len(models_data.get('models', []))
            return jsonify({
                'success': True,
                'details': f'Ollama connected - {model_count} models available'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Ollama returned status {response.status_code}'
            })
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Connection failed: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        })

@app.route('/api/test/local-llm', methods=['POST'])
def test_local_llm():
    """Test Local LLM connection"""
    try:
        data = request.json
        settings = data.get('localLLM', {})
        endpoint = settings.get('endpoint', 'http://localhost:11434')
        provider = settings.get('provider', 'ollama')
        
        if provider == 'ollama':
            # Test connection to Ollama
            response = requests.get(f'{endpoint}/api/version', timeout=5)
            
            if response.status_code == 200:
                version_data = response.json()
                return jsonify({
                    'success': True,
                    'details': f'Connected to Ollama: {version_data.get("version", "Unknown version")}'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Ollama returned status {response.status_code}'
                })
        else:
            # Generic endpoint test
            response = requests.get(f'{endpoint}/api/version', timeout=5)
            
            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'details': f'Connected to {provider} service'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Service returned status {response.status_code}'
                })
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Connection failed: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}'
        })

@app.route('/api/models/ollama', methods=['GET'])
def get_ollama_models():
    """Get available Ollama models"""
    try:
        settings = load_settings()
        ollama_url = settings.get('apis', {}).get('ollamaUrl', 'http://localhost:11434')
        
        response = requests.get(f'{ollama_url}/api/tags', timeout=5)
        
        if response.status_code == 200:
            models_data = response.json()
            models = [{
                'name': model['name'],
                'size': model.get('size', 0),
                'modified': model.get('modified_at', '')
            } for model in models_data.get('models', [])]
            
            return jsonify({
                'success': True,
                'models': models
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Ollama returned status {response.status_code}'
            })
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Connection failed: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get models: {str(e)}'
        })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'settings-api',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("Starting Hearthlink Settings API...")
    print("Endpoints available:")
    print("  GET  /api/settings - Get current settings")
    print("  POST /api/settings - Update settings")
    print("  POST /api/test/google-ai - Test Google AI API")
    print("  POST /api/test/claude-code - Test Claude Code CLI")
    print("  POST /api/test/ollama - Test Ollama connection")
    print("  POST /api/test/local-llm - Test Local LLM connection")
    print("  GET  /api/models/ollama - Get available Ollama models")
    print("  GET  /api/health - Health check")
    print("\\nStarting server on port 8003...")
    app.run(host='0.0.0.0', port=8003, debug=True)