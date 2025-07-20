#!/usr/bin/env python3
"""
SuperClaude API Service
Enhanced Claude integration with advanced reasoning capabilities and tool integration
"""

import json
import os
import time
import uuid
import subprocess
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

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

# Circuit breaker configurations
CLAUDE_CLI_CB_CONFIG = CircuitBreakerConfig(
    failure_threshold=3,
    recovery_timeout=60,
    success_threshold=2,
    timeout=90,  # Longer timeout for CLI operations
    monitoring_window=300
)

CLAUDE_API_CB_CONFIG = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=45,
    success_threshold=3,
    timeout=60,
    monitoring_window=300
)

# Global state
sessions = {}
reasoning_modes = {
    "fast": {
        "context_limit": 4096,
        "temperature": 0.3,
        "max_tokens": 1000,
        "description": "Quick responses for simple queries"
    },
    "balanced": {
        "context_limit": 8192,
        "temperature": 0.7,
        "max_tokens": 2000,
        "description": "Optimal balance of speed and quality"
    },
    "deep": {
        "context_limit": 16384,
        "temperature": 0.5,
        "max_tokens": 4000,
        "description": "Thorough analysis and reasoning"
    },
    "creative": {
        "context_limit": 8192,
        "temperature": 0.9,
        "max_tokens": 2000,
        "description": "Creative and exploratory responses"
    }
}

class SuperClaudeSession:
    def __init__(self, session_id, reasoning_mode="balanced", tools_enabled=None, backend_preference="claude_code_cli"):
        self.session_id = session_id
        self.reasoning_mode = reasoning_mode
        self.tools_enabled = tools_enabled or []
        self.backend_preference = backend_preference
        self.current_backend = None
        self.conversation_history = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.token_usage = {"total": 0, "input": 0, "output": 0}
        
    def add_message(self, role, content, metadata=None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        self.last_activity = datetime.now()
        
    def get_context(self, limit=None):
        """Get conversation context with optional limit"""
        mode_config = reasoning_modes[self.reasoning_mode]
        max_length = limit or mode_config["context_limit"]
        
        # Simple context truncation (in a real implementation, you'd do smarter truncation)
        context = self.conversation_history[-10:]  # Last 10 messages
        return context
        
    def update_token_usage(self, input_tokens, output_tokens):
        """Update token usage tracking"""
        self.token_usage["input"] += input_tokens
        self.token_usage["output"] += output_tokens
        self.token_usage["total"] = self.token_usage["input"] + self.token_usage["output"]

class ClaudeCodeCLI:
    def __init__(self):
        self.cli_path = "claude"
        self.working_dir = os.getcwd()
        
    def _execute_cli_command(self, prompt, reasoning_mode="balanced", tools_enabled=None):
        """Internal CLI execution method (protected by circuit breaker)"""
        mode_config = reasoning_modes[reasoning_mode]
        
        # Build command with correct CLI options
        cmd = [
            self.cli_path,
            "--print",  # Use --print for non-interactive output
            "--output-format", "text"
        ]
        
        # Create enhanced prompt based on reasoning mode
        enhanced_prompt = self.enhance_prompt(prompt, reasoning_mode, tools_enabled)
        
        # Execute command synchronously
        process = subprocess.run(
            cmd + [enhanced_prompt],  # Pass prompt as argument
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.working_dir,
            timeout=CLAUDE_CLI_CB_CONFIG.timeout
        )
        
        if process.returncode == 0:
            response = process.stdout.decode().strip()
            return {
                "success": True,
                "response": response,
                "backend_used": "claude_code_cli",
                "reasoning_chain": f"Applied {reasoning_mode} reasoning mode",
                "tools_used": tools_enabled or [],
                "error": None
            }
        else:
            error_msg = process.stderr.decode().strip()
            raise Exception(f"Claude CLI error: {error_msg}")
        
    def execute_command(self, prompt, reasoning_mode="balanced", tools_enabled=None):
        """Execute Claude Code CLI command with circuit breaker protection"""
        try:
            # Use circuit breaker for CLI execution
            claude_cli_breaker = circuit_manager.get_or_create('claude_cli', CLAUDE_CLI_CB_CONFIG)
            result = claude_cli_breaker.call(self._execute_cli_command, prompt, reasoning_mode, tools_enabled)
            return result
            
        except CircuitBreakerOpenException:
            logger.warning("Claude CLI circuit breaker is open")
            return {
                "success": False,
                "response": None,
                "backend_used": "claude_code_cli",
                "error": "Claude CLI service is currently unavailable",
                "circuit_breaker_status": "open",
                "suggestion": "The CLI service is experiencing issues. Please try again later."
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "response": None,
                "backend_used": "claude_code_cli",
                "error": f"Request timed out ({CLAUDE_CLI_CB_CONFIG.timeout}s limit)"
            }
        except Exception as e:
            logger.error(f"Claude Code CLI execution failed: {e}")
            return {
                "success": False,
                "response": None,
                "backend_used": "claude_code_cli", 
                "error": str(e),
                "circuit_breaker_status": "error"
            }
    
    def enhance_prompt(self, prompt, reasoning_mode, tools_enabled):
        """Enhance prompt based on reasoning mode and tools"""
        mode_config = reasoning_modes[reasoning_mode]
        
        enhanced = f"""
# SuperClaude Enhanced Request

## Reasoning Mode: {reasoning_mode.title()}
{mode_config['description']}

## Available Tools:
{', '.join(tools_enabled) if tools_enabled else 'None'}

## Context Integration:
- Hearthlink ecosystem awareness: Active
- Alice cognitive insights: Available
- Mimic persona adaptation: Available

## User Request:
{prompt}

## Instructions:
Please provide a response that:
1. Uses {reasoning_mode} reasoning approach
2. Leverages available tools when appropriate
3. Considers the Hearthlink ecosystem context
4. Provides clear reasoning for your approach

"""
        return enhanced

class ClaudeAPIFallback:
    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.base_url = "https://api.anthropic.com"
        
    def execute_request(self, prompt, reasoning_mode="balanced", tools_enabled=None):
        """Execute Claude API request as fallback"""
        # This would implement the actual Claude API integration
        # For now, return a placeholder response
        return {
            "success": False,
            "response": None,
            "backend_used": "claude_api",
            "error": "Claude API fallback not implemented (API key required)"
        }

# Initialize backends
claude_cli = ClaudeCodeCLI()
claude_api = ClaudeAPIFallback()

def check_backend_availability():
    """Check which backends are available"""
    backends = {}
    
    # Check Claude Code CLI
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=5)
        backends['claude_code_cli'] = result.returncode == 0
    except:
        backends['claude_code_cli'] = False
    
    # Check Claude API
    backends['claude_api'] = bool(os.getenv('CLAUDE_API_KEY'))
    
    return backends

@app.route('/api/superclaude/status', methods=['GET'])
def get_status():
    """Get SuperClaude service status"""
    backends = check_backend_availability()
    
    # Determine current backend
    if backends.get('claude_code_cli'):
        current_backend = 'claude_code_cli'
        status = 'connected'
    elif backends.get('claude_api'):
        current_backend = 'claude_api'
        status = 'connected'
    else:
        current_backend = None
        status = 'error'
    
    return jsonify({
        'status': status,
        'current_backend': current_backend,
        'available_backends': backends,
        'active_sessions': len(sessions),
        'reasoning_modes': list(reasoning_modes.keys()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/superclaude/session', methods=['POST'])
def create_session():
    """Create a new SuperClaude session"""
    data = request.get_json()
    
    session_id = str(uuid.uuid4())
    reasoning_mode = data.get('reasoning_mode', 'balanced')
    tools_enabled = data.get('tools_enabled', [])
    backend_preference = data.get('backend_preference', 'claude_code_cli')
    
    # Validate reasoning mode
    if reasoning_mode not in reasoning_modes:
        return jsonify({'error': 'Invalid reasoning mode'}), 400
    
    # Check backend availability
    backends = check_backend_availability()
    if backend_preference in backends and backends[backend_preference]:
        backend_used = backend_preference
    elif backends.get('claude_code_cli'):
        backend_used = 'claude_code_cli'
    elif backends.get('claude_api'):
        backend_used = 'claude_api'
    else:
        return jsonify({'error': 'No Claude backends available'}), 503
    
    # Create session
    session = SuperClaudeSession(
        session_id=session_id,
        reasoning_mode=reasoning_mode,
        tools_enabled=tools_enabled,
        backend_preference=backend_preference
    )
    session.current_backend = backend_used
    sessions[session_id] = session
    
    logger.info(f"Created SuperClaude session {session_id} with {backend_used}")
    
    return jsonify({
        'session_id': session_id,
        'backend_used': backend_used,
        'reasoning_mode': reasoning_mode,
        'tools_enabled': tools_enabled,
        'status': 'initialized'
    })

@app.route('/api/superclaude/chat', methods=['POST'])
def chat():
    """Process a chat message with SuperClaude"""
    data = request.get_json()
    
    session_id = data.get('session_id')
    message = data.get('message')
    reasoning_mode = data.get('reasoning_mode')
    tools_enabled = data.get('tools_enabled', [])
    context = data.get('context', {})
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    session = sessions[session_id]
    
    # Update session parameters if provided
    if reasoning_mode and reasoning_mode in reasoning_modes:
        session.reasoning_mode = reasoning_mode
    if tools_enabled is not None:
        session.tools_enabled = tools_enabled
    
    # Add user message to history
    session.add_message('user', message)
    
    start_time = time.time()
    
    try:
        # Execute request based on current backend
        if session.current_backend == 'claude_code_cli':
            result = claude_cli.execute_command(
                message, 
                session.reasoning_mode, 
                session.tools_enabled
            )
        elif session.current_backend == 'claude_api':
            result = claude_api.execute_request(
                message,
                session.reasoning_mode,
                session.tools_enabled
            )
        else:
            return jsonify({'error': 'No backend available'}), 503
        
        response_time = time.time() - start_time
        
        if result['success']:
            # Add assistant response to history
            session.add_message('assistant', result['response'], {
                'reasoning_mode': session.reasoning_mode,
                'tools_used': result.get('tools_used', []),
                'backend_used': result['backend_used']
            })
            
            # Update token usage (estimated)
            estimated_input_tokens = len(message.split()) * 1.3
            estimated_output_tokens = len(result['response'].split()) * 1.3
            session.update_token_usage(int(estimated_input_tokens), int(estimated_output_tokens))
            
            return jsonify({
                'response': result['response'],
                'reasoning_chain': result.get('reasoning_chain'),
                'tools_used': result.get('tools_used', []),
                'backend_used': result['backend_used'],
                'response_time': round(response_time, 2),
                'token_usage': session.token_usage,
                'circuit_breaker_status': result.get('circuit_breaker_status', 'healthy'),
                'session_info': {
                    'messages_count': len(session.conversation_history),
                    'reasoning_mode': session.reasoning_mode,
                    'tools_enabled': session.tools_enabled
                }
            })
        else:
            return jsonify({
                'error': result['error'],
                'backend_used': result['backend_used'],
                'circuit_breaker_status': result.get('circuit_breaker_status', 'error')
            }), 500
            
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/superclaude/sessions', methods=['GET'])
def list_sessions():
    """List active SuperClaude sessions"""
    session_list = []
    for session_id, session in sessions.items():
        session_list.append({
            'session_id': session_id,
            'reasoning_mode': session.reasoning_mode,
            'tools_enabled': session.tools_enabled,
            'current_backend': session.current_backend,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'message_count': len(session.conversation_history),
            'token_usage': session.token_usage
        })
    
    return jsonify({'sessions': session_list})

@app.route('/api/superclaude/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a SuperClaude session"""
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Deleted SuperClaude session {session_id}")
        return jsonify({'status': 'deleted'})
    else:
        return jsonify({'error': 'Session not found'}), 404

# Cleanup old sessions periodically
@app.before_request
def cleanup_sessions():
    """Clean up old inactive sessions"""
    current_time = datetime.now()
    session_timeout = 3600  # 1 hour
    
    expired_sessions = []
    for session_id, session in sessions.items():
        if (current_time - session.last_activity).total_seconds() > session_timeout:
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del sessions[session_id]
        logger.info(f"Cleaned up expired session {session_id}")

@app.route('/api/superclaude/circuit-breakers/status', methods=['GET'])
def get_circuit_breakers_status():
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

@app.route('/api/superclaude/circuit-breakers/<service_name>/reset', methods=['POST'])
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

if __name__ == '__main__':
    logger.info("Starting SuperClaude API Service...")
    logger.info("Endpoints available:")
    logger.info("  GET  /api/superclaude/status - Service status")
    logger.info("  POST /api/superclaude/session - Create session")
    logger.info("  POST /api/superclaude/chat - Chat with SuperClaude")
    logger.info("  GET  /api/superclaude/sessions - List sessions")
    logger.info("  DELETE /api/superclaude/session/<id> - Delete session")
    logger.info("  GET  /api/superclaude/circuit-breakers/status - Circuit breaker status")
    logger.info("  POST /api/superclaude/circuit-breakers/<service>/reset - Reset circuit breaker")
    
    # Check initial backend availability
    backends = check_backend_availability()
    logger.info(f"Available backends: {backends}")
    
    try:
        app.run(host='0.0.0.0', port=8005, debug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down SuperClaude API Service...")