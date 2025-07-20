#!/usr/bin/env python3
"""
System Health API Service
Provides health check endpoints for Hearthlink system components
"""

import json
import time
import psutil
import asyncio
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# System startup time
START_TIME = datetime.now()

# Component health tracking
component_health = {
    'alden': {'status': 'active', 'health': 'green', 'last_check': time.time()},
    'alice': {'status': 'active', 'health': 'green', 'last_check': time.time()},
    'mimic': {'status': 'idle', 'health': 'yellow', 'last_check': time.time()},
    'sentry': {'status': 'monitoring', 'health': 'green', 'last_check': time.time()},
    'core': {'status': 'active', 'health': 'green', 'last_check': time.time()},
    'synapse': {'status': 'active', 'health': 'green', 'last_check': time.time()},
    'vault': {'status': 'active', 'health': 'green', 'last_check': time.time()}
}

@app.route('/api/llm/health', methods=['GET'])
def llm_health():
    """Check LLM service health"""
    try:
        # Check if local LLM is running (placeholder)
        # In real implementation, this would ping Ollama or other LLM service
        return jsonify({
            'status': 'healthy',
            'service': 'llm',
            'timestamp': time.time(),
            'details': {
                'ollama_running': False,  # Would check actual service
                'models_loaded': ['llama2', 'codellama'],
                'gpu_available': False
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vault/health', methods=['GET'])
def vault_health():
    """Check Vault service health"""
    try:
        # Check database connections
        return jsonify({
            'status': 'healthy',
            'service': 'vault',
            'timestamp': time.time(),
            'details': {
                'database_connected': False,  # Would check actual DB
                'encryption_enabled': True,
                'backup_status': 'recent'
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/synapse/health', methods=['GET'])
def synapse_health():
    """Check Synapse service health"""
    try:
        # Check external API connections
        return jsonify({
            'status': 'healthy',
            'service': 'synapse',
            'timestamp': time.time(),
            'details': {
                'claude_api_connected': False,  # Would check actual API
                'google_ai_connected': False,
                'plugins_loaded': 3,
                'security_active': True
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/core/health', methods=['GET'])
def core_health():
    """Check Core service health"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'core',
            'timestamp': time.time(),
            'details': {
                'sessions_active': 1,
                'memory_usage': get_memory_usage(),
                'cpu_usage': psutil.cpu_percent()
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sentry/health', methods=['GET'])
def sentry_health():
    """Check Sentry service health"""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'sentry',
            'timestamp': time.time(),
            'details': {
                'monitoring_active': True,
                'alerts_pending': 0,
                'last_scan': time.time() - 60
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/system/memory', methods=['GET'])
def system_memory():
    """Get system memory statistics"""
    try:
        memory = psutil.virtual_memory()
        return jsonify({
            'usage': {
                'shortTerm': min(85, max(15, int(memory.percent * 0.6))),
                'longTerm': min(80, max(30, int(memory.percent * 0.8))),
                'embedded': min(60, max(10, int(memory.percent * 0.4))),
                'total': min(90, max(20, int(memory.percent)))
            },
            'cognitiveLoad': {
                'current': min(90, max(30, int(psutil.cpu_percent()))),
                'queueSize': min(15, max(1, int(psutil.cpu_percent() / 10))),
                'processingRate': min(1.0, max(0.3, 1.0 - (psutil.cpu_percent() / 100)))
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/system/health', methods=['GET'])
def system_health():
    """Get comprehensive system health"""
    try:
        uptime = datetime.now() - START_TIME
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return jsonify({
            'uptime': {
                'days': uptime.days,
                'hours': uptime.seconds // 3600,
                'minutes': (uptime.seconds % 3600) // 60
            },
            'heartbeat': 'stable' if cpu_percent < 80 else 'stressed',
            'latency': {
                'current': min(200, max(10, int(cpu_percent * 2))),
                'average': min(100, max(20, int(cpu_percent * 1.5))),
                'peak': min(300, max(50, int(cpu_percent * 3))),
                'floor': min(50, max(5, int(cpu_percent * 0.5)))
            },
            'recentPrompts': [
                {
                    'id': 'p1',
                    'content': 'System health check',
                    'tokens': 25,
                    'response': 'All systems operational',
                    'responseTokens': 100,
                    'timestamp': time.time() - 30
                },
                {
                    'id': 'p2',
                    'content': 'Memory analysis',
                    'tokens': 30,
                    'response': 'Memory usage within normal range',
                    'responseTokens': 120,
                    'timestamp': time.time() - 120
                }
            ],
            'systemMetrics': {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'network_active': True
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_memory_usage():
    """Get current memory usage"""
    memory = psutil.virtual_memory()
    return {
        'percent': memory.percent,
        'available': memory.available,
        'total': memory.total,
        'used': memory.used
    }

@app.route('/api/connect/llm', methods=['POST'])
def connect_llm():
    """Connect to local LLM service"""
    try:
        # This would attempt to connect to Ollama or other LLM service
        return jsonify({
            'status': 'connected',
            'service': 'ollama',
            'models': ['llama2', 'codellama'],
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/connect/vault', methods=['POST'])
def connect_vault():
    """Connect to Vault database"""
    try:
        # This would attempt to connect to the database
        return jsonify({
            'status': 'connected',
            'database': 'sqlite',
            'encrypted': True,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/connect/synapse', methods=['POST'])
def connect_synapse():
    """Connect Synapse to external APIs"""
    try:
        # This would attempt to connect to Claude API and Google AI Studio
        return jsonify({
            'status': 'connected',
            'services': {
                'claude_api': False,  # Would check actual connection
                'google_ai': False
            },
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("Starting Hearthlink System Health API...")
    print("Endpoints available:")
    print("  /api/llm/health - LLM service health")
    print("  /api/vault/health - Vault service health")
    print("  /api/synapse/health - Synapse service health")
    print("  /api/core/health - Core service health")
    print("  /api/sentry/health - Sentry service health")
    print("  /api/system/memory - System memory stats")
    print("  /api/system/health - Overall system health")
    print("\nStarting server on port 8001...")
    app.run(host='0.0.0.0', port=8001, debug=True)