#!/usr/bin/env python3
"""
Core API Service
Provides REST API endpoints for Core orchestration functionality
"""

import json
import os
import time
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from pathlib import Path

# Import core modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.core import Core, Session, Participant, SessionStatus, ParticipantType
    from vault.vault import Vault
except ImportError as e:
    raise ImportError("Core module is required but not available. Please check installation.")

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
core_instance = None
sessions_data = {}
agents_data = {}
projects_data = {}
services_data = {}
orchestration_logs = []

def update_agent_statuses():
    """Update agent statuses based on real service health checks"""
    global agents_data
    
    # Check LLM service health (affects Alden, Alice, Mimic)
    llm_healthy = False
    try:
        response = requests.get('http://localhost:8001/api/health', timeout=2)
        llm_healthy = response.status_code == 200
    except:
        llm_healthy = False
    
    # Update agent statuses based on LLM health
    for agent_id in ['alden', 'alice', 'mimic']:
        if agent_id in agents_data:
            if llm_healthy:
                agents_data[agent_id]['status'] = 'active'
            else:
                agents_data[agent_id]['status'] = 'offline'
    
    # Sentry depends on both its service health AND LLM being available to monitor
    if 'sentry' in agents_data:
        try:
            response = requests.get('http://localhost:8004/api/sentry/health', timeout=2)
            sentry_healthy = response.status_code == 200
            # Sentry is only "active" if both healthy AND has something to monitor (LLM)
            agents_data['sentry']['status'] = 'active' if (sentry_healthy and llm_healthy) else 'offline'
        except:
            agents_data['sentry']['status'] = 'offline'

def update_service_statuses():
    """Update service statuses based on real health checks"""
    global services_data
    
    service_endpoints = {
        'vault': 'http://localhost:8002/api/vault/health',
        'alden': 'http://localhost:8001/api/health', 
        'synapse': 'http://localhost:8003/api/synapse/health',
        'sentry': 'http://localhost:8004/api/sentry/health'
    }
    
    for service_id, endpoint in service_endpoints.items():
        if service_id in services_data:
            try:
                response = requests.get(endpoint, timeout=2)
                if response.status_code == 200:
                    services_data[service_id]['status'] = 'running'
                    services_data[service_id]['health'] = 'healthy'
                else:
                    services_data[service_id]['status'] = 'error'
                    services_data[service_id]['health'] = 'unhealthy'
            except:
                services_data[service_id]['status'] = 'offline'
                services_data[service_id]['health'] = 'unhealthy'

# Mock data for demonstration
def initialize_mock_data():
    global agents_data, projects_data, services_data
    
    # Initialize agents
    agents_data = {
        'alden': {
            'id': 'alden',
            'name': 'Alden',
            'type': 'primary',
            'status': 'active',
            'load': 65,
            'tasks': 12,
            'capabilities': ['conversation', 'reasoning', 'memory'],
            'performance': {'efficiency': 94, 'accuracy': 98, 'responsiveness': 96},
            'lastActivity': datetime.now().isoformat()
        },
        'alice': {
            'id': 'alice',
            'name': 'Alice',
            'type': 'specialist',
            'status': 'active',
            'load': 32,
            'tasks': 5,
            'capabilities': ['analysis', 'problem-solving', 'optimization'],
            'performance': {'efficiency': 91, 'accuracy': 96, 'responsiveness': 94},
            'lastActivity': datetime.now().isoformat()
        },
        'mimic': {
            'id': 'mimic',
            'name': 'Mimic',
            'type': 'adaptive',
            'status': 'idle',
            'load': 78,
            'tasks': 8,
            'capabilities': ['adaptation', 'learning', 'pattern-recognition'],
            'performance': {'efficiency': 88, 'accuracy': 93, 'responsiveness': 91},
            'lastActivity': datetime.now().isoformat()
        },
        'sentry': {
            'id': 'sentry',
            'name': 'Sentry',
            'type': 'monitor',
            'status': 'monitoring',
            'load': 25,
            'tasks': 3,
            'capabilities': ['monitoring', 'security', 'alerting'],
            'performance': {'efficiency': 96, 'accuracy': 99, 'responsiveness': 98},
            'lastActivity': datetime.now().isoformat()
        },
    }
    
    # Initialize services
    services_data = {
        'vault': {
            'id': 'vault',
            'name': 'Vault Memory System',
            'status': 'running',
            'health': 'healthy',
            'uptime': time.time() - 86400,  # 1 day ago
            'endpoint': 'http://localhost:8002',
            'version': '1.0.0'
        },
        'alden': {
            'id': 'alden',
            'name': 'Alden LLM Service',
            'status': 'running',
            'health': 'healthy',
            'uptime': time.time() - 82800,  # 23 hours ago
            'endpoint': 'http://localhost:8001',
            'version': '1.0.0'
        },
        'synapse': {
            'id': 'synapse',
            'name': 'Synapse Gateway',
            'status': 'running',
            'health': 'healthy',
            'uptime': time.time() - 79200,  # 22 hours ago
            'endpoint': 'http://localhost:8003',
            'version': '1.0.0'
        },
        'sentry': {
            'id': 'sentry',
            'name': 'Sentry Monitor',
            'status': 'running',
            'health': 'healthy',
            'uptime': time.time() - 75600,  # 21 hours ago
            'endpoint': 'http://localhost:8004',
            'version': '1.0.0'
        }
    }
    
    # Initialize projects
    projects_data = {
        'project_1': {
            'id': 'project_1',
            'name': 'Hearthlink Core Development',
            'description': 'Developing the core orchestration system',
            'status': 'active',
            'progress': 85,
            'assignedAgents': ['alden', 'alice', 'sentry'],
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'tasks': [
                {
                    'id': 'task_1',
                    'name': 'API Integration',
                    'status': 'completed',
                    'assignee': 'alden',
                    'progress': 100
                },
                {
                    'id': 'task_2',
                    'name': 'Error Handling',
                    'status': 'in_progress',
                    'assignee': 'alice',
                    'progress': 70
                },
                {
                    'id': 'task_3',
                    'name': 'System Monitoring',
                    'status': 'pending',
                    'assignee': 'sentry',
                    'progress': 0
                }
            ]
        },
        'project_2': {
            'id': 'project_2',
            'name': 'Voice Interface Enhancement',
            'description': 'Improving voice interaction capabilities',
            'status': 'planning',
            'progress': 25,
            'assignedAgents': ['alden', 'mimic'],
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'tasks': [
                {
                    'id': 'task_4',
                    'name': 'Voice Recognition',
                    'status': 'pending',
                    'assignee': 'alden',
                    'progress': 0
                },
                {
                    'id': 'task_5',
                    'name': 'Adaptive Responses',
                    'status': 'pending',
                    'assignee': 'mimic',
                    'progress': 0
                }
            ]
        }
    }

def add_orchestration_log(message, type='info', agent='system'):
    """Add entry to orchestration logs"""
    global orchestration_logs
    
    log_entry = {
        'id': len(orchestration_logs) + 1,
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'type': type,
        'agent': agent
    }
    orchestration_logs.insert(0, log_entry)
    
    # Keep only last 100 logs
    if len(orchestration_logs) > 100:
        orchestration_logs = orchestration_logs[:100]
    
    logger.info(f"Orchestration log: {type.upper()} - {message}")

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'core-api',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'uptime': time.time() - start_time if 'start_time' in globals() else 0
    })

@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get all agents with their current status"""
    # Update agent statuses based on real service health
    update_agent_statuses()
    
    # Filter out services that are not agents
    actual_agents = {k: v for k, v in agents_data.items() if v['type'] != 'service'}
    
    return jsonify({
        'agents': list(actual_agents.values()),
        'count': len(actual_agents)
    })

@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get specific agent information"""
    if agent_id not in agents_data:
        return jsonify({'error': 'Agent not found'}), 404
    
    return jsonify(agents_data[agent_id])

@app.route('/api/agents/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update agent status or configuration"""
    if agent_id not in agents_data:
        return jsonify({'error': 'Agent not found'}), 404
    
    data = request.get_json()
    agents_data[agent_id].update(data)
    agents_data[agent_id]['lastActivity'] = datetime.now().isoformat()
    
    add_orchestration_log(f"Agent {agent_id} updated", 'info', agent_id)
    
    return jsonify(agents_data[agent_id])

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get all services status"""
    # Update service statuses based on real health checks
    update_service_statuses()
    
    return jsonify({
        'services': list(services_data.values()),
        'count': len(services_data)
    })

@app.route('/api/services/<service_id>/health', methods=['GET'])
def check_service_health(service_id):
    """Check specific service health"""
    if service_id not in services_data:
        return jsonify({'error': 'Service not found'}), 404
    
    service = services_data[service_id]
    
    # Simulate health check
    health_status = {
        'service_id': service_id,
        'status': service['status'],
        'health': service['health'],
        'uptime': time.time() - service['uptime'],
        'last_check': datetime.now().isoformat(),
        'response_time': 0.05  # Mock response time
    }
    
    return jsonify(health_status)

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects"""
    return jsonify({
        'projects': list(projects_data.values()),
        'count': len(projects_data)
    })

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    data = request.get_json()
    
    project_id = f"project_{int(time.time())}"
    project = {
        'id': project_id,
        'name': data.get('name', 'New Project'),
        'description': data.get('description', ''),
        'type': data.get('type', 'general'),
        'status': 'pending',
        'progress': 0,
        'assignedAgents': [data.get('assigned_agent', 'alden')],
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        'tasks': []
    }
    
    projects_data[project_id] = project
    
    add_orchestration_log(f"Created new project: {project['name']}", 'info', 'core')
    
    return jsonify({
        'success': True,
        'project_id': project_id,
        'project': project
    })

@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get specific project"""
    if project_id not in projects_data:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify(projects_data[project_id])

@app.route('/api/projects/<project_id>/orchestrate', methods=['POST'])
def start_project_orchestration(project_id):
    """Start orchestration for a project"""
    if project_id not in projects_data:
        return jsonify({'error': 'Project not found'}), 404
    
    project = projects_data[project_id]
    project['status'] = 'active'
    project['updated'] = datetime.now().isoformat()
    
    add_orchestration_log(f"Started orchestration for project: {project['name']}", 'info', 'core')
    
    # Simulate task delegation
    for task in project['tasks']:
        if task['status'] == 'pending':
            add_orchestration_log(f"Delegating task '{task['name']}' to {task['assignee']}", 'info', 'core')
    
    return jsonify({
        'success': True,
        'message': f"Orchestration started for {project['name']}",
        'project': project
    })

@app.route('/api/projects/<project_id>/tasks/<task_id>/delegate', methods=['POST'])
def delegate_task(project_id, task_id):
    """Delegate a specific task to an agent"""
    if project_id not in projects_data:
        return jsonify({'error': 'Project not found'}), 404
    
    project = projects_data[project_id]
    task = next((t for t in project['tasks'] if t['id'] == task_id), None)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    task['status'] = 'in_progress'
    project['updated'] = datetime.now().isoformat()
    
    add_orchestration_log(f"Task '{task['name']}' delegated to {task['assignee']}", 'success', 'core')
    
    return jsonify({
        'success': True,
        'message': f"Task delegated to {task['assignee']}",
        'task': task
    })

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all active sessions"""
    return jsonify({
        'sessions': list(sessions_data.values()),
        'count': len(sessions_data)
    })

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new session"""
    data = request.get_json()
    
    session_id = f"session_{int(time.time())}"
    session = {
        'id': session_id,
        'topic': data.get('topic', 'General Discussion'),
        'type': data.get('type', 'conference'),
        'participants': [],
        'status': 'active',
        'created': datetime.now().isoformat(),
        'messages': []
    }
    
    sessions_data[session_id] = session
    
    add_orchestration_log(f"Created new session: {session['topic']}", 'info', 'core')
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'session': session
    })

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    if session_id not in sessions_data:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(sessions_data[session_id])

@app.route('/api/sessions/<session_id>/join', methods=['POST'])
def join_session(session_id):
    """Join a session"""
    if session_id not in sessions_data:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.get_json()
    participant = {
        'id': data.get('participant_id'),
        'name': data.get('name'),
        'type': data.get('type', 'user'),
        'joined_at': datetime.now().isoformat()
    }
    
    sessions_data[session_id]['participants'].append(participant)
    
    add_orchestration_log(f"Participant {participant['name']} joined session {session_id}", 'info', 'core')
    
    return jsonify({
        'success': True,
        'message': f"Joined session {session_id}",
        'participant': participant
    })

@app.route('/api/sessions/<session_id>/message', methods=['POST'])
def send_session_message(session_id):
    """Send message to session"""
    if session_id not in sessions_data:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.get_json()
    message = {
        'id': f"msg_{int(time.time())}",
        'sender': data.get('sender'),
        'content': data.get('content'),
        'timestamp': datetime.now().isoformat(),
        'type': data.get('type', 'message')
    }
    
    sessions_data[session_id]['messages'].append(message)
    
    return jsonify({
        'success': True,
        'message': message
    })

@app.route('/api/orchestration/status', methods=['GET'])
def get_orchestration_status():
    """Get current orchestration status"""
    active_projects = len([p for p in projects_data.values() if p['status'] == 'active'])
    active_sessions = len([s for s in sessions_data.values() if s['status'] == 'active'])
    active_agents = len([a for a in agents_data.values() if a['status'] == 'active'])
    
    return jsonify({
        'status': 'active' if active_projects > 0 else 'idle',
        'active_projects': active_projects,
        'active_sessions': active_sessions,
        'active_agents': active_agents,
        'total_logs': len(orchestration_logs),
        'last_activity': orchestration_logs[0]['timestamp'] if orchestration_logs else None
    })

@app.route('/api/orchestration/logs', methods=['GET'])
def get_orchestration_logs():
    """Get orchestration logs"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        'logs': orchestration_logs[:limit],
        'total': len(orchestration_logs)
    })

@app.route('/api/system/metrics', methods=['GET'])
def get_system_metrics():
    """Get system performance metrics"""
    return jsonify({
        'cpu': 45 + (time.time() % 10),  # Simulate varying CPU
        'memory': 62 + (time.time() % 8),  # Simulate varying memory
        'network': 38 + (time.time() % 15),  # Simulate varying network
        'storage': 71 + (time.time() % 5),  # Simulate varying storage
        'uptime': f"{int((time.time() - start_time) // 3600)}h {int(((time.time() - start_time) % 3600) // 60)}m",
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system/memory', methods=['GET'])
def get_system_memory():
    """Get system memory usage statistics"""
    try:
        # Get real memory statistics
        import psutil
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Calculate memory usage percentages
        short_term = min(85, max(15, memory.percent * 0.6))  # Working memory
        long_term = min(90, max(40, (memory.used / memory.total) * 100 * 0.8))  # Stored memory
        embedded = min(40, max(10, swap.percent * 0.5))  # Embedded/cached memory
        
        return jsonify({
            'usage': {
                'shortTerm': round(short_term, 1),
                'longTerm': round(long_term, 1), 
                'embedded': round(embedded, 1),
                'total': round((short_term + long_term + embedded) / 3, 1)
            },
            'cognitiveLoad': {
                'current': round(memory.percent, 1),
                'queueSize': max(1, min(10, round(memory.percent / 10))),
                'processingRate': round(max(0.5, min(1.0, (100 - memory.percent) / 100)), 2)
            },
            'systemMemory': {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent
            },
            'timestamp': datetime.now().isoformat()
        })
    except ImportError:
        # Fallback if psutil is not available
        logger.warning("psutil not available, using simulated memory data")
        return jsonify({
            'usage': {
                'shortTerm': round(35 + (time.time() % 25), 1),
                'longTerm': round(60 + (time.time() % 20), 1),
                'embedded': round(25 + (time.time() % 15), 1),
                'total': round(45 + (time.time() % 20), 1)
            },
            'cognitiveLoad': {
                'current': round(65 + (time.time() % 30), 1),
                'queueSize': max(1, round(7 + (time.time() % 5))),
                'processingRate': round(0.85 + (time.time() % 0.3), 2)
            },
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/system/health', methods=['GET'])
def get_system_health():
    """Get overall system health metrics"""
    try:
        import psutil
        
        # Get system information
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        # Get CPU and memory info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate health status
        health_score = 100
        if cpu_percent > 80:
            health_score -= 20
        if memory.percent > 85:
            health_score -= 20
        if disk.percent > 90:
            health_score -= 15
        
        health_status = 'excellent' if health_score > 85 else 'good' if health_score > 70 else 'fair' if health_score > 50 else 'poor'
        
        return jsonify({
            'status': health_status,
            'score': health_score,
            'uptime': {
                'seconds': uptime_seconds,
                'formatted': f"{int(uptime_seconds // 86400)}d {int((uptime_seconds % 86400) // 3600)}h {int((uptime_seconds % 3600) // 60)}m"
            },
            'resources': {
                'cpu': round(cpu_percent, 1),
                'memory': round(memory.percent, 1),
                'disk': round(disk.percent, 1)
            },
            'heartbeat': 'stable',
            'latency': {
                'current': round(45 + (time.time() % 30), 1),
                'average': round(52 + (time.time() % 20), 1),
                'peak': round(120 + (time.time() % 40), 1),
                'floor': round(28 + (time.time() % 10), 1)
            },
            'timestamp': datetime.now().isoformat()
        })
    except ImportError:
        logger.warning("psutil not available, using simulated health data")
        return jsonify({
            'status': 'good',
            'score': 78,
            'uptime': {
                'seconds': time.time() - start_time,
                'formatted': f"{int((time.time() - start_time) // 3600)}h {int(((time.time() - start_time) % 3600) // 60)}m"
            },
            'resources': {
                'cpu': round(45 + (time.time() % 30), 1),
                'memory': round(62 + (time.time() % 25), 1),
                'disk': round(71 + (time.time() % 20), 1)
            },
            'heartbeat': 'stable',
            'latency': {
                'current': round(45 + (time.time() % 30), 1),
                'average': round(52 + (time.time() % 20), 1),
                'peak': round(120 + (time.time() % 40), 1),
                'floor': round(28 + (time.time() % 10), 1)
            },
            'timestamp': datetime.now().isoformat()
        })

# Initialize mock data on startup
initialize_mock_data()
start_time = time.time()

if __name__ == '__main__':
    print("Starting Hearthlink Core API...")
    print("Endpoints available:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/agents - Get all agents")
    print("  GET  /api/agents/<id> - Get specific agent")
    print("  PUT  /api/agents/<id> - Update agent")
    print("  GET  /api/services - Get all services")
    print("  GET  /api/services/<id>/health - Check service health")
    print("  GET  /api/projects - Get all projects")
    print("  GET  /api/projects/<id> - Get specific project")
    print("  POST /api/projects/<id>/orchestrate - Start project orchestration")
    print("  POST /api/projects/<id>/tasks/<task_id>/delegate - Delegate task")
    print("  GET  /api/sessions - Get all sessions")
    print("  POST /api/sessions - Create new session")
    print("  GET  /api/sessions/<id> - Get session details")
    print("  POST /api/sessions/<id>/join - Join session")
    print("  POST /api/sessions/<id>/message - Send session message")
    print("  GET  /api/orchestration/status - Get orchestration status")
    print("  GET  /api/orchestration/logs - Get orchestration logs")
    print("  GET  /api/system/metrics - Get system metrics")
    print("\nStarting server on port 8000...")
    
    try:
        app.run(host='0.0.0.0', port=8000, debug=True)
    except KeyboardInterrupt:
        print("\nShutting down Core API...")