#!/usr/bin/env python3
"""
External Agent API Service
Manages external agent registration, communication, and file operations
"""

import json
import os
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

# Import circuit breaker
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from circuit_breaker import CircuitBreakerConfig, CircuitBreakerManager, CircuitBreakerOpenException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize circuit breaker manager
circuit_manager = CircuitBreakerManager()

# Circuit breaker configuration for external agents
EXTERNAL_AGENT_CB_CONFIG = CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=30,
    success_threshold=2,
    timeout=45,
    monitoring_window=180
)

class ExternalAgentManager:
    """Manages external agent plugins and communication."""
    
    def __init__(self):
        self.plugins_dir = Path("src/synapse/plugins")
        self.agents = {}
        self.agent_instances = {}
        
        # Discover and load external agents
        self._discover_agents()
        
    def _discover_agents(self):
        """Discover and register external agent plugins."""
        logger.info("Discovering external agent plugins...")
        
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return
            
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir():
                manifest_path = plugin_dir / "manifest.json"
                plugin_path = plugin_dir / "plugin.py"
                
                if manifest_path.exists() and plugin_path.exists():
                    try:
                        # Load manifest
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                        
                        # Check if it's an external agent
                        if manifest.get('type') == 'external_agent':
                            agent_id = manifest['plugin_id']
                            self.agents[agent_id] = {
                                'manifest': manifest,
                                'plugin_path': plugin_path,
                                'status': 'registered'
                            }
                            
                            logger.info(f"Registered external agent: {agent_id}")
                            
                    except Exception as e:
                        logger.error(f"Failed to load plugin {plugin_dir.name}: {e}")
        
        logger.info(f"Discovered {len(self.agents)} external agents")
        
    def get_agent_instance(self, agent_id: str):
        """Get or create agent instance."""
        if agent_id not in self.agents:
            return None
            
        if agent_id in self.agent_instances:
            return self.agent_instances[agent_id]
            
        try:
            # Load plugin module
            plugin_path = self.agents[agent_id]['plugin_path']
            spec = importlib.util.spec_from_file_location(f"{agent_id}_plugin", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Create agent instance
            if hasattr(module, 'create_agent'):
                instance = module.create_agent()
                self.agent_instances[agent_id] = instance
                self.agents[agent_id]['status'] = 'active'
                return instance
            else:
                logger.error(f"Plugin {agent_id} missing create_agent function")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create agent instance for {agent_id}: {e}")
            return None
    
    def _execute_agent_request_internal(self, agent_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal agent execution method (protected by circuit breaker)"""
        instance = self.get_agent_instance(agent_id)
        if not instance:
            raise Exception(f'Agent {agent_id} not available')
        
        result = instance.execute(request_data)
        if not result.get('success', False):
            raise Exception(f"Agent execution failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    def execute_agent_request(self, agent_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request through an external agent with circuit breaker protection."""
        try:
            # Use circuit breaker for agent execution
            agent_breaker = circuit_manager.get_or_create(f'external_agent_{agent_id}', EXTERNAL_AGENT_CB_CONFIG)
            result = agent_breaker.call(self._execute_agent_request_internal, agent_id, request_data)
            
            # Add circuit breaker status to result
            result['circuit_breaker_status'] = 'healthy'
            return result
            
        except CircuitBreakerOpenException:
            logger.warning(f"Circuit breaker for agent {agent_id} is open")
            return {
                'success': False,
                'error': f'External agent {agent_id} is currently unavailable',
                'circuit_breaker_status': 'open',
                'suggestion': 'The agent service is experiencing issues. Please try again later.',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Agent {agent_id} execution error: {e}")
            return {
                'success': False,
                'error': str(e),
                'circuit_breaker_status': 'error',
                'timestamp': datetime.now().isoformat()
            }

# Initialize manager
agent_manager = ExternalAgentManager()

@app.route('/api/external-agents', methods=['GET'])
def list_external_agents():
    """List all registered external agents."""
    try:
        agents_info = []
        
        for agent_id, agent_data in agent_manager.agents.items():
            manifest = agent_data['manifest']
            agents_info.append({
                'agent_id': agent_id,
                'name': manifest.get('name', agent_id),
                'version': manifest.get('version', '1.0.0'),
                'description': manifest.get('description', ''),
                'type': manifest.get('type', 'external_agent'),
                'capabilities': manifest.get('capabilities', []),
                'permissions': manifest.get('permissions', []),
                'status': agent_data.get('status', 'unknown'),
                'file_access_enabled': 'FILE_SYSTEM' in manifest.get('permissions', [])
            })
        
        return jsonify({
            'success': True,
            'agents': agents_info,
            'count': len(agents_info),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"List agents error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/external-agents/<agent_id>/status', methods=['GET'])
def get_agent_status(agent_id: str):
    """Get status of a specific external agent."""
    try:
        if agent_id not in agent_manager.agents:
            return jsonify({
                'success': False,
                'error': f'Agent {agent_id} not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Get status from agent instance
        result = agent_manager.execute_agent_request(agent_id, {'action': 'status'})
        
        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'status_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Agent status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/external-agents/<agent_id>/execute', methods=['POST'])
def execute_agent_action(agent_id: str):
    """Execute an action through an external agent."""
    try:
        if agent_id not in agent_manager.agents:
            return jsonify({
                'success': False,
                'error': f'Agent {agent_id} not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        request_data = request.get_json()
        if not request_data:
            return jsonify({
                'success': False,
                'error': 'Request data is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Execute action through agent
        result = agent_manager.execute_agent_request(agent_id, request_data)
        
        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/external-agents/<agent_id>/generate', methods=['POST'])
def generate_with_agent(agent_id: str):
    """Generate response using external agent."""
    try:
        if agent_id not in agent_manager.agents:
            return jsonify({
                'success': False,
                'error': f'Agent {agent_id} not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Execute generation request
        request_data = {
            'action': 'generate',
            'message': message,
            'temperature': data.get('temperature', 0.7),
            'max_tokens': data.get('max_tokens', 1000)
        }
        
        result = agent_manager.execute_agent_request(agent_id, request_data)
        
        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'generation_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/external-agents/<agent_id>/files/write', methods=['POST'])
def write_file_with_agent(agent_id: str):
    """Write a file using external agent."""
    try:
        if agent_id not in agent_manager.agents:
            return jsonify({
                'success': False,
                'error': f'Agent {agent_id} not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        data = request.get_json()
        file_path = data.get('file_path', '')
        content = data.get('content', '')
        
        if not file_path or not content:
            return jsonify({
                'success': False,
                'error': 'file_path and content are required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Execute file write request
        request_data = {
            'action': 'write_file',
            'file_path': file_path,
            'content': content
        }
        
        result = agent_manager.execute_agent_request(agent_id, request_data)
        
        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'file_operation_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"File write error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/external-agents/<agent_id>/files/read', methods=['POST'])
def read_file_with_agent(agent_id: str):
    """Read a file using external agent."""
    try:
        if agent_id not in agent_manager.agents:
            return jsonify({
                'success': False,
                'error': f'Agent {agent_id} not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        data = request.get_json()
        file_path = data.get('file_path', '')
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': 'file_path is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Execute file read request
        request_data = {
            'action': 'read_file',
            'file_path': file_path
        }
        
        result = agent_manager.execute_agent_request(agent_id, request_data)
        
        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'file_operation_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"File read error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/external-agents/<agent_id>/files/list', methods=['GET', 'POST'])
def list_files_with_agent(agent_id: str):
    """List files using external agent."""
    try:
        if agent_id not in agent_manager.agents:
            return jsonify({
                'success': False,
                'error': f'Agent {agent_id} not found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        directory = None
        if request.method == 'POST':
            data = request.get_json()
            directory = data.get('directory') if data else None
        
        # Execute file list request
        request_data = {'action': 'list_files'}
        if directory:
            request_data['directory'] = directory
        
        result = agent_manager.execute_agent_request(agent_id, request_data)
        
        return jsonify({
            'success': True,
            'agent_id': agent_id,
            'file_list_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"File list error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/external-agents/circuit-breakers/status', methods=['GET'])
def get_circuit_breakers_status():
    """Get status of all external agent circuit breakers"""
    try:
        return jsonify(circuit_manager.get_all_status())
    except Exception as e:
        logger.error(f"Circuit breaker status error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/external-agents/circuit-breakers/<service_name>/reset', methods=['POST'])
def reset_circuit_breaker(service_name: str):
    """Reset a specific external agent circuit breaker"""
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

@app.route('/api/external-agents/circuit-breakers/reset-all', methods=['POST'])
def reset_all_circuit_breakers():
    """Reset all external agent circuit breakers"""
    try:
        circuit_manager.reset_all()
        return jsonify({
            'status': 'success',
            'message': 'All external agent circuit breakers reset successfully',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Reset all circuit breakers error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    logger.info("Starting External Agent API Service...")
    logger.info("Available endpoints:")
    logger.info("  GET  /api/external-agents - List all external agents")
    logger.info("  GET  /api/external-agents/<id>/status - Get agent status")
    logger.info("  POST /api/external-agents/<id>/execute - Execute agent action")
    logger.info("  POST /api/external-agents/<id>/generate - Generate response")
    logger.info("  POST /api/external-agents/<id>/files/write - Write file")
    logger.info("  POST /api/external-agents/<id>/files/read - Read file")
    logger.info("  GET/POST /api/external-agents/<id>/files/list - List files")
    logger.info("  GET  /api/external-agents/circuit-breakers/status - Circuit breaker status")
    logger.info("  POST /api/external-agents/circuit-breakers/<service>/reset - Reset circuit breaker")
    logger.info("  POST /api/external-agents/circuit-breakers/reset-all - Reset all circuit breakers")
    
    app.run(host='0.0.0.0', port=8006, debug=True)