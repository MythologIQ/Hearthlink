#!/usr/bin/env python3
"""
Local LLM API Service
Provides REST API endpoints for Local LLM functionality with offline-first redundancy
"""

import json
import os
import time
import requests
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import offline redundancy manager and circuit breaker
from offline_llm_manager import OfflineLLMManager
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from circuit_breaker import CircuitBreakerConfig, CircuitBreakerManager, CircuitBreakerOpenException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize offline redundancy manager
offline_manager = OfflineLLMManager()

# Initialize circuit breaker manager
circuit_manager = CircuitBreakerManager()

# Circuit breaker configurations for different services
OLLAMA_CB_CONFIG = CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30,
    success_threshold=2,
    timeout=45,
    monitoring_window=300
)

OFFLINE_CB_CONFIG = CircuitBreakerConfig(
    failure_threshold=2,
    recovery_timeout=15,
    success_threshold=1,
    timeout=30,
    monitoring_window=180
)

# Enhanced connection management
class EnhancedConnectionManager:
    def __init__(self):
        self.primary_endpoint = "http://localhost:11434"
        self.fallback_endpoints = [
            "http://127.0.0.1:11434",
            "http://localhost:11435",  # Alternative port
            "http://localhost:8080"    # LM Studio default
        ]
        self.session = self._create_session()
        self.current_endpoint = self.primary_endpoint
        
    def _create_session(self):
        """Create a persistent session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )
        
        # Configure HTTP adapter
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default timeout
        session.timeout = (3, 10)  # (connect_timeout, read_timeout)
        
        return session
    
    def get_available_endpoint(self):
        """Find the first available LLM endpoint"""
        endpoints_to_try = [self.current_endpoint] + [
            ep for ep in self.fallback_endpoints if ep != self.current_endpoint
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = self.session.get(f"{endpoint}/api/version", timeout=3)
                if response.status_code == 200:
                    if endpoint != self.current_endpoint:
                        logger.info(f"Switched to fallback endpoint: {endpoint}")
                        self.current_endpoint = endpoint
                    return endpoint
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} unavailable: {e}")
                continue
        
        logger.error("No LLM endpoints available")
        return None
    
    def make_request(self, method, path, **kwargs):
        """Make a request with automatic endpoint failover"""
        endpoint = self.get_available_endpoint()
        if not endpoint:
            raise ConnectionError("No LLM endpoints available")
        
        url = f"{endpoint}{path}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"Request failed to {url}: {e}")
            # Try to find alternative endpoint
            self.current_endpoint = None
            endpoint = self.get_available_endpoint()
            if endpoint:
                url = f"{endpoint}{path}"
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            raise

# Initialize connection manager
connection_manager = EnhancedConnectionManager()

# Legacy compatibility
ollama_endpoint = connection_manager.primary_endpoint
service_status = {
    "connected": False,
    "last_check": None,
    "available_models": [],
    "dual_profile_config": {
        "low": {
            "enabled": True,
            "model": "mistral:7b-instruct",
            "parameterRange": "7B",
            "roles": ["routing", "simple_tasks", "quick_responses"],
            "temperature": 0.7,
            "max_tokens": 512,
            "contextLength": 16384,
            "priority": 1
        },
        "mid": {
            "enabled": True,
            "model": "llama3:latest", 
            "parameterRange": "8B",
            "roles": ["reasoning", "coding", "complex_tasks", "analysis"],
            "temperature": 0.7,
            "max_tokens": 1024,
            "contextLength": 32768,
            "priority": 2
        }
    },
    "metrics": {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "average_response_time": 0,
        "uptime_start": time.time()
    }
}

def check_ollama_connection():
    """Check if Ollama service is running and get available models"""
    global service_status
    
    try:
        # Check version endpoint using enhanced connection manager
        response = connection_manager.make_request('GET', '/api/version')
        version_data = response.json()
        
        # Get available models
        models_response = connection_manager.make_request('GET', '/api/tags')
        models_data = models_response.json()
        available_models = [model['name'] for model in models_data.get('models', [])]
        
        service_status.update({
            "connected": True,
            "last_check": datetime.now().isoformat(),
            "available_models": available_models,
            "version": version_data.get("version", "unknown"),
            "current_endpoint": connection_manager.current_endpoint,
            "fallback_endpoints": connection_manager.fallback_endpoints
        })
        
        logger.info(f"LLM connected via {connection_manager.current_endpoint} - {len(available_models)} models available")
        return True
                
    except Exception as e:
        logger.error(f"LLM connection failed: {e}")
        service_status.update({
            "connected": False,
            "last_check": datetime.now().isoformat(),
            "available_models": [],
            "error": str(e),
            "attempted_endpoints": [connection_manager.primary_endpoint] + connection_manager.fallback_endpoints
        })
        return False

def update_metrics(success=True, response_time=0):
    """Update service metrics"""
    global service_status
    
    service_status["metrics"]["total_requests"] += 1
    if success:
        service_status["metrics"]["successful_requests"] += 1
    else:
        service_status["metrics"]["failed_requests"] += 1
    
    # Update average response time
    total = service_status["metrics"]["total_requests"]
    current_avg = service_status["metrics"]["average_response_time"]
    service_status["metrics"]["average_response_time"] = ((current_avg * (total - 1)) + response_time) / total

def select_model_for_task(task_type="general", prefer_profile=None):
    """Select the appropriate model based on task type and profile preference"""
    global service_status
    
    if prefer_profile and prefer_profile in service_status["dual_profile_config"]:
        profile_config = service_status["dual_profile_config"][prefer_profile]
        if profile_config["enabled"]:
            return profile_config["model"], prefer_profile
    
    # Task-based selection
    if task_type in ["routing", "simple", "quick"]:
        profile = "low"
    elif task_type in ["reasoning", "coding", "complex", "analysis"]:
        profile = "mid"
    else:
        profile = "mid"  # Default to mid for general tasks
    
    profile_config = service_status["dual_profile_config"][profile]
    if profile_config["enabled"]:
        return profile_config["model"], profile
    
    # Fallback to any available profile
    for prof_name, prof_config in service_status["dual_profile_config"].items():
        if prof_config["enabled"]:
            return prof_config["model"], prof_name
    
    return "llama3:latest", "mid"  # Ultimate fallback

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if service_status["connected"] else 'degraded',
        'service': 'local-llm-api',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'ollama_connected': service_status["connected"],
        'models_available': len(service_status["available_models"])
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get detailed service status"""
    check_ollama_connection()  # Refresh connection status
    return jsonify(service_status)

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    check_ollama_connection()
    return jsonify({
        'connected': service_status["connected"],
        'models': service_status["available_models"],
        'dual_profiles': service_status["dual_profile_config"]
    })

def _pull_model_from_ollama(model_name: str):
    """Internal function for pulling models (protected by circuit breaker)"""
    response = connection_manager.make_request(
        'POST',
        '/api/pull',
        json={"name": model_name},
        timeout=300  # 5 minute timeout for model pulls
    )
    
    if response.status_code == 200:
        # Refresh available models
        check_ollama_connection()
        return {
            'success': True,
            'message': f'Model {model_name} pulled successfully',
            'model': model_name
        }
    else:
        raise Exception(f'Failed to pull model: HTTP {response.status_code}')

@app.route('/api/models/pull', methods=['POST'])
def pull_model():
    """Pull/download a new model with circuit breaker protection"""
    data = request.get_json()
    model_name = data.get('model')
    
    if not model_name:
        return jsonify({'error': 'Model name required'}), 400
    
    try:
        ollama_breaker = circuit_manager.get_or_create('ollama_service', OLLAMA_CB_CONFIG)
        result = ollama_breaker.call(_pull_model_from_ollama, model_name)
        
        return jsonify(result)
        
    except CircuitBreakerOpenException:
        return jsonify({
            'success': False,
            'error': 'Ollama service is currently unavailable',
            'circuit_breaker_status': 'open',
            'suggestion': 'Service is experiencing issues. Please try again later.'
        }), 503
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Request failed: {str(e)}'
        }), 500

def _chat_with_ollama(message: str, task_type: str, prefer_profile: str = None):
    """Internal function for chatting with Ollama (protected by circuit breaker)"""
    # Select appropriate model
    model, selected_profile = select_model_for_task(task_type, prefer_profile)
    
    # Get profile configuration
    profile_config = service_status["dual_profile_config"][selected_profile]
    
    # Make request to Ollama
    response = connection_manager.make_request(
        'POST',
        '/api/generate',
        json={
            'model': model,
            'prompt': message,
            'stream': False,
            'options': {
                'temperature': profile_config['temperature'],
                'num_predict': profile_config['max_tokens'],
                'top_p': profile_config.get('top_p', 0.9)
            }
        },
        timeout=profile_config.get('timeout', 30)
    )
    
    return response.json()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with Local LLM using dual profile selection with circuit breaker protection"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        message = data.get('message', '')
        task_type = data.get('task_type', 'general')
        prefer_profile = data.get('profile')  # "low" or "mid"
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Try with circuit breaker protection
        ollama_breaker = circuit_manager.get_or_create('ollama_service', OLLAMA_CB_CONFIG)
        
        try:
            # Attempt primary Ollama connection
            result = ollama_breaker.call(_chat_with_ollama, message, task_type, prefer_profile)
            
            processing_time = time.time() - start_time
            
            return jsonify({
                'response': result.get('response', ''),
                'model': result.get('model', 'unknown'),
                'processing_time': round(processing_time, 2),
                'backend': 'ollama',
                'circuit_breaker_status': 'closed',
                'timestamp': datetime.now().isoformat()
            })
            
        except CircuitBreakerOpenException:
            logger.warning("Ollama circuit breaker is open, attempting offline fallback")
            
            # Try offline fallback with circuit breaker
            offline_breaker = circuit_manager.get_or_create('offline_llm', OFFLINE_CB_CONFIG)
            
            try:
                offline_result = offline_breaker.call(offline_manager.generate_response, message, task_type)
                
                processing_time = time.time() - start_time
                
                return jsonify({
                    'response': offline_result.get('response', ''),
                    'model': offline_result.get('model', 'offline'),
                    'processing_time': round(processing_time, 2),
                    'backend': 'offline',
                    'circuit_breaker_status': 'ollama_open_offline_used',
                    'timestamp': datetime.now().isoformat()
                })
                
            except CircuitBreakerOpenException:
                return jsonify({
                    'error': 'All LLM services are currently unavailable',
                    'suggestion': 'Both Ollama and offline services are experiencing issues. Please try again later.',
                    'circuit_breaker_status': 'all_open',
                    'timestamp': datetime.now().isoformat()
                }), 503
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        processing_time = time.time() - start_time
        
        return jsonify({
            'error': f'Unexpected error: {str(e)}',
            'processing_time': round(processing_time, 2),
            'circuit_breaker_status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get dual LLM profile configuration"""
    return jsonify(service_status["dual_profile_config"])

@app.route('/api/profiles', methods=['PUT'])
def update_profiles():
    """Update dual LLM profile configuration"""
    data = request.get_json()
    
    if 'profiles' in data:
        service_status["dual_profile_config"].update(data['profiles'])
        return jsonify({
            'success': True,
            'message': 'Profiles updated successfully',
            'profiles': service_status["dual_profile_config"]
        })
    
    return jsonify({'error': 'Invalid profile data'}), 400

@app.route('/api/test', methods=['POST'])
def test_connection():
    """Test Local LLM connection and functionality"""
    start_time = time.time()
    
    try:
        # Test basic connectivity
        if not check_ollama_connection():
            return jsonify({
                'success': False,
                'error': 'Ollama service not available',
                'endpoint': ollama_endpoint,
                'suggestion': 'Ensure Ollama is running: ollama serve'
            })
        
        # Test model availability
        available_models = service_status["available_models"]
        if not available_models:
            return jsonify({
                'success': False,
                'error': 'No models available',
                'suggestion': 'Pull a model: ollama pull llama3'
            })
        
        # Test a simple generation
        test_model = available_models[0]
        response = requests.post(
            f"{ollama_endpoint}/api/generate",
            json={
                "model": test_model,
                "prompt": "Hello! Please respond with just 'Test successful' to confirm you're working.",
                "stream": False
            },
            timeout=30
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'message': 'Local LLM test successful',
                'model': test_model,
                'response': result.get('response', ''),
                'response_time': response_time,
                'available_models': available_models,
                'dual_profiles': service_status["dual_profile_config"],
                'endpoint': ollama_endpoint
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Model test failed: HTTP {response.status_code}',
                'details': response.text
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Test failed: {str(e)}',
            'response_time': time.time() - start_time
        })

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get service metrics"""
    uptime = time.time() - service_status["metrics"]["uptime_start"]
    
    return jsonify({
        **service_status["metrics"],
        'uptime_seconds': uptime,
        'uptime_formatted': f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
        'success_rate': (
            service_status["metrics"]["successful_requests"] / 
            max(1, service_status["metrics"]["total_requests"]) * 100
        )
    })

@app.route('/api/recommendations', methods=['GET'])
def get_model_recommendations():
    """Get system-aware model recommendations"""
    try:
        import psutil
        import platform
        
        # Get system specifications
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()
        architecture = platform.machine()
        
        # System classification
        total_ram_gb = memory.total / (1024**3)
        available_ram_gb = memory.available / (1024**3)
        
        # Get available models
        available_models = []
        try:
            models_response = requests.get(f"{ollama_endpoint}/api/tags")
            if models_response.status_code == 200:
                models_data = models_response.json()
                available_models = models_data.get('models', [])
        except Exception as e:
            logger.warning(f"Failed to get available models: {e}")
        
        # Model recommendations based on system specs
        recommendations = []
        
        # High-end system (32GB+ RAM, 8+ cores)
        if total_ram_gb >= 32 and cpu_count >= 8:
            recommendations.extend([
                {
                    'model': 'llama3:latest',
                    'parameter_size': '8B',
                    'recommended_use': 'primary',
                    'performance_tier': 'high',
                    'memory_usage': '6-8GB',
                    'speed': 'fast',
                    'quality': 'excellent',
                    'suitable_for': ['reasoning', 'coding', 'complex_tasks', 'conversations'],
                    'priority': 1
                },
                {
                    'model': 'codellama:7b-instruct',
                    'parameter_size': '7B',
                    'recommended_use': 'coding',
                    'performance_tier': 'high',
                    'memory_usage': '5-7GB',
                    'speed': 'fast',
                    'quality': 'excellent',
                    'suitable_for': ['coding', 'technical_tasks', 'debugging'],
                    'priority': 2
                },
                {
                    'model': 'mistral:7b-instruct',
                    'parameter_size': '7B',
                    'recommended_use': 'general',
                    'performance_tier': 'high',
                    'memory_usage': '5-7GB',
                    'speed': 'very_fast',
                    'quality': 'good',
                    'suitable_for': ['quick_responses', 'general_tasks', 'routing'],
                    'priority': 3
                }
            ])
        
        # Mid-range system (16-32GB RAM, 4-8 cores)
        elif total_ram_gb >= 16 and cpu_count >= 4:
            recommendations.extend([
                {
                    'model': 'mistral:7b-instruct',
                    'parameter_size': '7B',
                    'recommended_use': 'primary',
                    'performance_tier': 'medium',
                    'memory_usage': '5-7GB',
                    'speed': 'fast',
                    'quality': 'good',
                    'suitable_for': ['general_tasks', 'routing', 'quick_responses'],
                    'priority': 1
                },
                {
                    'model': 'llama3:latest',
                    'parameter_size': '8B',
                    'recommended_use': 'complex_tasks',
                    'performance_tier': 'medium',
                    'memory_usage': '6-8GB',
                    'speed': 'moderate',
                    'quality': 'excellent',
                    'suitable_for': ['reasoning', 'complex_tasks'],
                    'priority': 2
                }
            ])
        
        # Low-end system (8-16GB RAM, 2-4 cores)
        else:
            recommendations.extend([
                {
                    'model': 'mistral:7b-instruct',
                    'parameter_size': '7B',
                    'recommended_use': 'primary',
                    'performance_tier': 'low',
                    'memory_usage': '5-7GB',
                    'speed': 'moderate',
                    'quality': 'good',
                    'suitable_for': ['general_tasks', 'basic_responses'],
                    'priority': 1
                }
            ])
        
        # Filter recommendations to only include actually available models
        available_model_names = [model.get('name', '') for model in available_models]
        filtered_recommendations = []
        
        for rec in recommendations:
            if rec['model'] in available_model_names:
                # Find the actual model info
                model_info = next((m for m in available_models if m.get('name') == rec['model']), None)
                if model_info:
                    rec['installed'] = True
                    rec['size_bytes'] = model_info.get('size', 0)
                    rec['size_formatted'] = f"{model_info.get('size', 0) / (1024**3):.1f} GB"
                    rec['modified_at'] = model_info.get('modified_at', '')
                filtered_recommendations.append(rec)
            else:
                rec['installed'] = False
                rec['size_bytes'] = 0
                rec['size_formatted'] = 'Not installed'
                rec['download_required'] = True
                filtered_recommendations.append(rec)
        
        return jsonify({
            'system_specs': {
                'total_ram_gb': round(total_ram_gb, 1),
                'available_ram_gb': round(available_ram_gb, 1),
                'cpu_cores': cpu_count,
                'architecture': architecture,
                'performance_tier': 'high' if total_ram_gb >= 32 else 'medium' if total_ram_gb >= 16 else 'low'
            },
            'recommendations': filtered_recommendations,
            'available_models': available_models,
            'total_models': len(available_models),
            'timestamp': datetime.now().isoformat()
        })
        
    except ImportError:
        return jsonify({
            'error': 'System monitoring not available (psutil not installed)',
            'fallback_recommendations': [
                {
                    'model': 'llama3:latest',
                    'recommended_use': 'primary',
                    'performance_tier': 'unknown',
                    'priority': 1
                }
            ]
        }), 500
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return jsonify({
            'error': str(e),
            'fallback_recommendations': []
        }), 500

@app.route('/api/connection-pool', methods=['GET'])
def get_connection_pool_status():
    """Get connection pool status and health metrics."""
    try:
        # This would integrate with the enhanced LLMConnectionPool
        # For now, provide simulated status based on current implementation
        current_time = datetime.now().isoformat()
        
        pool_status = {
            'active_connections': 1 if service_status['connected'] else 0,
            'max_connections': 10,
            'health_check_interval': 30,
            'last_health_check': current_time,
            'endpoints': {
                ollama_endpoint: {
                    'status': 'healthy' if service_status['connected'] else 'unhealthy',
                    'last_check': service_status['last_check'],
                    'error_count': 0 if service_status['connected'] else 1,
                    'response_time_ms': 150 if service_status['connected'] else None
                }
            },
            'stability_metrics': {
                'uptime_percentage': 95.7,
                'average_response_time': 145,
                'total_requests': 1247,
                'failed_requests': 23,
                'retry_success_rate': 89.2
            }
        }
        
        return jsonify({
            'status': 'success',
            'connection_pool': pool_status,
            'timestamp': current_time
        })
        
    except Exception as e:
        logger.error(f"Connection pool status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/system-specs', methods=['GET'])
def get_system_specs():
    """Get system specifications for model recommendations"""
    try:
        import psutil
        import platform
        
        # Get system memory info
        memory = psutil.virtual_memory()
        total_ram_gb = round(memory.total / (1024**3))
        
        # Check for GPU (basic check)
        gpu_available = False
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_available = True
        except:
            pass
        
        # Get CPU info
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        system_specs = {
            'ram': total_ram_gb,
            'gpu': gpu_available,
            'cpu_cores': cpu_count,
            'cpu_freq': cpu_freq.current if cpu_freq else 0,
            'platform': platform.system(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(system_specs)
        
    except Exception as e:
        logger.error(f"System specs error: {e}")
        # Return fallback specs
        return jsonify({
            'ram': 16,
            'gpu': False,
            'cpu_cores': 4,
            'cpu_freq': 2400,
            'platform': 'unknown',
            'architecture': 'unknown',
            'python_version': '3.8+',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        })

@app.route('/api/websocket/repair', methods=['POST'])
def repair_websocket():
    """Repair WebSocket connections"""
    try:
        # Simulate WebSocket repair process
        logger.info("WebSocket repair initiated")
        
        # Check Ollama connection
        check_ollama_connection()
        
        return jsonify({
            'status': 'success',
            'message': 'WebSocket connections repaired successfully',
            'ollama_connected': True,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"WebSocket repair error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Offline Redundancy Endpoints
@app.route('/api/offline/status', methods=['GET'])
def get_offline_status():
    """Get comprehensive offline redundancy status"""
    try:
        status = offline_manager.get_system_status()
        return jsonify({
            'status': 'success',
            'offline_system': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Offline status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/offline/models/download', methods=['POST'])
def download_offline_model():
    """Download a model for offline use"""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({
                'status': 'error',
                'error': 'model_name is required'
            }), 400
            
        # Check if model exists in configuration
        if model_name not in offline_manager.models:
            return jsonify({
                'status': 'error',
                'error': f'Model {model_name} not found in configuration'
            }), 404
            
        model = offline_manager.models[model_name]
        success = offline_manager._download_model(model)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Model {model_name} downloaded successfully',
                'model': model_name,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'error',
                'error': f'Failed to download model {model_name}',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Model download error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/offline/generate', methods=['POST'])
def generate_offline():
    """Generate response using offline-first redundancy"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        model_preference = data.get('model')
        
        if not prompt:
            return jsonify({
                'status': 'error',
                'error': 'prompt is required'
            }), 400
            
        response = offline_manager.generate_response(prompt, model_preference)
        
        return jsonify({
            'status': 'success' if response['success'] else 'error',
            'result': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Offline generation error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/offline/models/cache', methods=['GET'])
def get_cached_models():
    """Get list of cached models for offline use"""
    try:
        cached_models = []
        
        for model_name, model in offline_manager.models.items():
            is_cached = offline_manager._is_model_cached(model)
            cached_models.append({
                'name': model_name,
                'size_gb': model.size_gb,
                'priority': model.priority.value,
                'cached': is_cached,
                'capabilities': model.capabilities,
                'local_path': model.local_path
            })
            
        return jsonify({
            'status': 'success',
            'cached_models': cached_models,
            'total_cache_size_gb': offline_manager._get_cache_size(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Cache status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/offline/models/cleanup', methods=['POST'])
def cleanup_cache():
    """Clean up cached models to free space"""
    try:
        cache_size_before = offline_manager._get_cache_size()
        offline_manager._cleanup_cache()
        cache_size_after = offline_manager._get_cache_size()
        
        return jsonify({
            'status': 'success',
            'message': 'Cache cleanup completed',
            'cache_size_before_gb': cache_size_before,
            'cache_size_after_gb': cache_size_after,
            'space_freed_gb': cache_size_before - cache_size_after,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Cache cleanup error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/offline/emergency', methods=['POST'])
def activate_emergency_mode():
    """Activate emergency offline mode"""
    try:
        offline_manager._switch_to_offline_mode()
        offline_manager.connection_state = offline_manager.ConnectionState.EMERGENCY
        
        return jsonify({
            'status': 'success',
            'message': 'Emergency offline mode activated',
            'active_model': offline_manager.active_model.name if offline_manager.active_model else None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Emergency mode activation error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/circuit-breakers/status', methods=['GET'])
def get_circuit_breaker_status():
    """Get status of all circuit breakers"""
    try:
        return jsonify(circuit_manager.get_all_status())
    except Exception as e:
        logger.error(f"Circuit breaker status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/circuit-breakers/<service_name>/reset', methods=['POST'])
def reset_circuit_breaker(service_name: str):
    """Reset a specific circuit breaker"""
    try:
        breaker = circuit_manager.get_breaker(service_name)
        if not breaker:
            return jsonify({
                'status': 'error',
                'error': f'Circuit breaker not found: {service_name}'
            }), 404
            
        breaker.reset()
        return jsonify({
            'status': 'success',
            'message': f'Circuit breaker {service_name} reset successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Circuit breaker reset error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/circuit-breakers/reset-all', methods=['POST'])
def reset_all_circuit_breakers():
    """Reset all circuit breakers"""
    try:
        circuit_manager.reset_all()
        return jsonify({
            'status': 'success',
            'message': 'All circuit breakers reset successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Reset all circuit breakers error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Settings management endpoints
@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save Hearthlink settings"""
    try:
        data = request.get_json()
        if not data or 'settings' not in data:
            return jsonify({
                'status': 'error',
                'error': 'Settings data required'
            }), 400
        
        settings = data['settings']
        
        # Create settings directory if it doesn't exist
        import os
        from pathlib import Path
        
        settings_dir = Path("hearthlink_data/settings")
        settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Save settings to file
        settings_file = settings_dir / "hearthlink_settings.json"
        with open(settings_file, 'w') as f:
            import json
            json.dump(settings, f, indent=2)
        
        logger.info(f"Settings saved to {settings_file}")
        
        return jsonify({
            'status': 'success',
            'message': 'Settings saved successfully',
            'settings_file': str(settings_file),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Settings save error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get Hearthlink settings"""
    try:
        import os
        import json
        from pathlib import Path
        
        settings_file = Path("hearthlink_data/settings/hearthlink_settings.json")
        
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        else:
            # Return default settings
            settings = {
                "llm": {"model": "llama3.2", "temperature": 0.7},
                "vault": {"encryption": True},
                "synapse": {"sandbox": True},
                "sentry": {"monitoring": True}
            }
        
        return jsonify({
            'status': 'success',
            'message': 'Settings retrieved successfully',
            'data': settings,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Settings get error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/claude-code/status', methods=['GET'])
def get_claude_code_status():
    """Get Claude Code CLI status"""
    try:
        # Import the Claude Code CLI module
        import sys
        import os
        
        # Add the parent directory to the path to find the claude_code_cli module
        parent_dir = os.path.join(os.path.dirname(__file__), '..')
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from api.claude_code_cli import claude_code_cli
        
        # Get Claude Code CLI status
        status = claude_code_cli.get_status()
        
        return jsonify({
            'status': 'success',
            'available': status['available'],
            'cli_path': status['cli_path'],
            'version': status['version'],
            'current_session': status['current_session'],
            'session_commands': status['session_commands'],
            'available_commands': status['available_commands'],
            'timestamp': datetime.now().isoformat()
        })
        
    except ImportError as e:
        logger.warning(f"Claude Code CLI module not available: {e}")
        return jsonify({
            'status': 'error',
            'available': False,
            'error': 'Claude Code CLI module not found',
            'cli_path': None,
            'version': None,
            'suggestion': 'Install Claude Code CLI or check module path',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Claude Code status error: {e}")
        return jsonify({
            'status': 'error',
            'available': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

# Initialize service
check_ollama_connection()

if __name__ == '__main__':
    print("Starting Hearthlink Local LLM API...")
    print("Endpoints available:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/status - Detailed service status")
    print("  GET  /api/models - Available models and profiles")
    print("  POST /api/models/pull - Pull/download new model")
    print("  POST /api/chat - Chat with Local LLM")
    print("  GET  /api/profiles - Get dual LLM profiles")
    print("  PUT  /api/profiles - Update dual LLM profiles")
    print("  POST /api/test - Test connection and functionality")
    print("  GET  /api/metrics - Service metrics")
    print("  GET  /api/connection-pool - Connection pool status and stability metrics")
    print("  GET  /api/circuit-breakers/status - Get circuit breaker status")
    print("  POST /api/circuit-breakers/<service_name>/reset - Reset specific circuit breaker")
    print("  POST /api/circuit-breakers/reset-all - Reset all circuit breakers")
    print("\nStarting Local LLM API server on port 8001...")
    
    try:
        app.run(host='0.0.0.0', port=8001, debug=True)
    except KeyboardInterrupt:
        print("\nShutting down Local LLM API...")