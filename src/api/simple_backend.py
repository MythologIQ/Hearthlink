#!/usr/bin/env python3
"""
Simple Backend for Hearthlink Services
Handles basic task delegation and service status
"""

import json
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Service status
service_status = {
    'claude-code': {'available': False, 'capabilities': ['code_generation', 'code_analysis', 'debugging']},
    'ollama': {'available': False, 'capabilities': ['ai_response', 'chat', 'generation']},
    'google-ai': {'available': False, 'capabilities': ['ai_response', 'research', 'analysis']}
}

# Task history
task_history = []

def check_ollama_connection():
    """Check if Ollama is available"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return len(data.get('models', [])) > 0
    except:
        pass
    return False

def generate_ollama_response(prompt, model='llama3'):
    """Generate response using Ollama"""
    try:
        payload = {
            'model': model,
            'prompt': prompt,
            'stream': False
        }
        response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('response', '')
    except Exception as e:
        print(f"Ollama generation error: {e}")
    return None

@app.route('/api/project/services', methods=['GET'])
def get_services():
    """Get available services"""
    return jsonify(service_status)

@app.route('/api/project/delegate', methods=['POST'])
def delegate_task():
    """Delegate a task to appropriate service"""
    data = request.json
    task_type = data.get('task_type')
    task_description = data.get('task_description')
    context = data.get('context', {})
    
    if not task_type or not task_description:
        return jsonify({'success': False, 'error': 'Task type and description required'}), 400
    
    # Route to Ollama for AI responses
    if task_type == 'ai_response' and service_status['ollama']['available']:
        try:
            response = generate_ollama_response(task_description)
            
            if response:
                task_record = {
                    'id': f"task_{len(task_history) + 1}",
                    'task_type': task_type,
                    'description': task_description,
                    'service_used': 'ollama',
                    'response': response,
                    'success': True,
                    'timestamp': f"{len(task_history) + 1}"
                }
                task_history.append(task_record)
                return jsonify(task_record)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # For other task types, return simulated response
    # Simulation removed - implement proper error handling
    raise NotImplementedError("This feature requires proper implementation")
    
    task_history.append(# Simulation removed - implement proper error handling)
    return jsonify(# Simulation removed - implement proper error handling)

@app.route('/api/project/stats', methods=['GET'])
def get_stats():
    """Get task delegation statistics"""
    return jsonify({
        'total_tasks': len(task_history),
        'successful_tasks': len([t for t in task_history if t.get('success', False)]),
        'failed_tasks': len([t for t in task_history if not t.get('success', True)]),
        'services_used': {},
        'average_response_time': 0
    })

# Settings management
settings_data = {
    'general': {
        'theme': 'starcraft',
        'language': 'en',
        'autoSave': True,
        'notifications': True,
        'voiceEnabled': True,
        'startupModule': 'alden'
    },
    'apis': {
        'googleAiKey': '',
        'claudeCodePath': '',
        'ollamaUrl': 'http://localhost:11434',
        'customEndpoints': []
    },
    'voice': {
        'enabled': True,
        'sensitivity': 0.7,
        'language': 'en-US',
        'wakeWord': 'alden',
        'routingMode': 'smart'
    },
    'security': {
        'encryptionEnabled': True,
        'auditLogging': True,
        'sessionTimeout': 30,
        'autoLock': False
    }
}

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    return jsonify(settings_data)

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save settings"""
    global settings_data
    try:
        new_settings = request.json
        settings_data.update(new_settings)
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/test/<service>', methods=['POST'])
def test_service(service):
    """Test service connection"""
    if service == 'ollama':
        available = check_ollama_connection()
        return jsonify({
            'success': available,
            'details': 'Ollama connection successful' if available else 'Ollama not available'
        })
    elif service == 'claude-code':
        return jsonify({
            'success': False,
            'details': 'Claude Code CLI not configured'
        })
    elif service == 'google-ai':
        return jsonify({
            'success': False,
            'details': 'Google AI API key not configured'
        })
    else:
        return jsonify({'success': False, 'details': 'Unknown service'}), 400

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall service status"""
    # Check Ollama connection
    ollama_available = check_ollama_connection()
    service_status['ollama']['available'] = ollama_available
    
    return jsonify({
        'services': service_status,
        'ready': any(s['available'] for s in service_status.values()),
        'timestamp': len(task_history)
    })

if __name__ == '__main__':
    print("Starting Hearthlink Simple Backend...")
    print("Endpoints available:")
    print("  GET  /api/status - Service status")
    print("  GET  /api/project/services - Available services")
    print("  POST /api/project/delegate - Task delegation")
    print("  GET  /api/project/stats - Task statistics")
    print("\nStarting server on port 8003...")
    app.run(host='0.0.0.0', port=8003, debug=True)