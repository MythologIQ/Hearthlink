#!/usr/bin/env python3
"""
Hearthlink REST API Server
MVP API for agent profiles and token management
"""

import os
import json
import uuid
import secrets
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import threading

class HearthlinkAPIServer:
    def __init__(self, port=8080, data_dir="./api_data"):
        self.port = port
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend
        
        # Database setup
        self.db_path = self.data_dir / "hearthlink.db"
        self.init_database()
        
        # Setup routes
        self.setup_routes()
    
    def init_database(self):
        """Initialize SQLite database with agent and token tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agent profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                capabilities TEXT,  -- JSON string
                config TEXT,        -- JSON string
                created_at TEXT,
                updated_at TEXT,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # API tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tokens (
                id TEXT PRIMARY KEY,
                agent_id TEXT,
                token_hash TEXT UNIQUE,
                permissions TEXT,   -- JSON string
                expires_at TEXT,
                created_at TEXT,
                last_used TEXT,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[API] Database initialized: {self.db_path}")
    
    def setup_routes(self):
        """Setup all API routes."""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({
                "status": "healthy",
                "service": "hearthlink-api",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/agents', methods=['POST'])
        def create_agent():
            """Create a new agent profile."""
            data = request.get_json()
            
            if not data or 'name' not in data:
                return jsonify({"error": "Agent name is required"}), 400
            
            agent_id = str(uuid.uuid4())
            agent = {
                "id": agent_id,
                "name": data['name'],
                "description": data.get('description', ''),
                "capabilities": json.dumps(data.get('capabilities', [])),
                "config": json.dumps(data.get('config', {})),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "active": True
            }
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO agents (id, name, description, capabilities, config, created_at, updated_at, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    agent['id'], agent['name'], agent['description'], 
                    agent['capabilities'], agent['config'], 
                    agent['created_at'], agent['updated_at'], agent['active']
                ))
                
                conn.commit()
                conn.close()
                
                # Return agent without internal database fields
                response_agent = {
                    "id": agent['id'],
                    "name": agent['name'],
                    "description": agent['description'],
                    "capabilities": json.loads(agent['capabilities']),
                    "config": json.loads(agent['config']),
                    "created_at": agent['created_at'],
                    "active": agent['active']
                }
                
                return jsonify(response_agent), 201
                
            except Exception as e:
                return jsonify({"error": f"Failed to create agent: {str(e)}"}), 500
        
        @self.app.route('/api/agents', methods=['GET'])
        def list_agents():
            """List all agent profiles."""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM agents WHERE active = 1')
                rows = cursor.fetchall()
                
                agents = []
                for row in rows:
                    agents.append({
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "capabilities": json.loads(row[3]),
                        "config": json.loads(row[4]),
                        "created_at": row[5],
                        "updated_at": row[6],
                        "active": bool(row[7])
                    })
                
                conn.close()
                return jsonify({"agents": agents})
                
            except Exception as e:
                return jsonify({"error": f"Failed to list agents: {str(e)}"}), 500
        
        @self.app.route('/api/agents/<agent_id>', methods=['GET'])
        def get_agent(agent_id):
            """Get specific agent profile."""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM agents WHERE id = ? AND active = 1', (agent_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({"error": "Agent not found"}), 404
                
                agent = {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "capabilities": json.loads(row[3]),
                    "config": json.loads(row[4]),
                    "created_at": row[5],
                    "updated_at": row[6],
                    "active": bool(row[7])
                }
                
                conn.close()
                return jsonify(agent)
                
            except Exception as e:
                return jsonify({"error": f"Failed to get agent: {str(e)}"}), 500
        
        @self.app.route('/api/agents/<agent_id>/tokens', methods=['POST'])
        def create_token(agent_id):
            """Generate API token for agent."""
            data = request.get_json() or {}
            
            # Verify agent exists
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('SELECT id FROM agents WHERE id = ? AND active = 1', (agent_id,))
                if not cursor.fetchone():
                    return jsonify({"error": "Agent not found"}), 404
                
                # Generate token
                token = secrets.token_urlsafe(32)
                token_hash = hashlib.sha256(token.encode()).hexdigest()
                token_id = str(uuid.uuid4())
                
                # Default permissions
                permissions = data.get('permissions', {
                    "read": True,
                    "write": True,
                    "execute": True
                })
                
                # Default expiry (30 days)
                expires_days = data.get('expires_days', 30)
                expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()
                
                cursor.execute('''
                    INSERT INTO tokens (id, agent_id, token_hash, permissions, expires_at, created_at, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    token_id, agent_id, token_hash, json.dumps(permissions),
                    expires_at, datetime.now().isoformat(), True
                ))
                
                conn.commit()
                conn.close()
                
                return jsonify({
                    "token_id": token_id,
                    "token": token,  # Only returned once!
                    "agent_id": agent_id,
                    "permissions": permissions,
                    "expires_at": expires_at,
                    "created_at": datetime.now().isoformat()
                }), 201
                
            except Exception as e:
                return jsonify({"error": f"Failed to create token: {str(e)}"}), 500
        
        @self.app.route('/api/tokens', methods=['GET'])
        def list_tokens():
            """List all active tokens (without token values)."""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT t.id, t.agent_id, t.permissions, t.expires_at, 
                           t.created_at, t.last_used, a.name as agent_name
                    FROM tokens t
                    JOIN agents a ON t.agent_id = a.id
                    WHERE t.active = 1
                    ORDER BY t.created_at DESC
                ''')
                
                rows = cursor.fetchall()
                tokens = []
                
                for row in rows:
                    tokens.append({
                        "token_id": row[0],
                        "agent_id": row[1],
                        "agent_name": row[6],
                        "permissions": json.loads(row[2]),
                        "expires_at": row[3],
                        "created_at": row[4],
                        "last_used": row[5]
                    })
                
                conn.close()
                return jsonify({"tokens": tokens})
                
            except Exception as e:
                return jsonify({"error": f"Failed to list tokens: {str(e)}"}), 500
        
        @self.app.route('/api/auth/verify', methods=['POST'])
        def verify_token():
            """Verify API token and return agent info."""
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "Invalid authorization header"}), 401
            
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT t.id, t.agent_id, t.permissions, t.expires_at, a.name, a.capabilities
                    FROM tokens t
                    JOIN agents a ON t.agent_id = a.id
                    WHERE t.token_hash = ? AND t.active = 1 AND a.active = 1
                ''', (token_hash,))
                
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({"error": "Invalid token"}), 401
                
                # Check if token expired
                expires_at = datetime.fromisoformat(row[3])
                if datetime.now() > expires_at:
                    return jsonify({"error": "Token expired"}), 401
                
                # Update last_used
                cursor.execute(
                    'UPDATE tokens SET last_used = ? WHERE id = ?',
                    (datetime.now().isoformat(), row[0])
                )
                conn.commit()
                conn.close()
                
                return jsonify({
                    "valid": True,
                    "agent_id": row[1],
                    "agent_name": row[4],
                    "permissions": json.loads(row[2]),
                    "capabilities": json.loads(row[5])
                })
                
            except Exception as e:
                return jsonify({"error": f"Token verification failed: {str(e)}"}), 500
        
        @self.app.route('/api/execute', methods=['POST'])
        def execute_command():
            """Execute command through authenticated agent."""
            # Verify token first
            auth_response = verify_token()
            if auth_response[1] != 200:  # Not successful
                return auth_response
            
            auth_data = auth_response[0].get_json()
            
            data = request.get_json()
            if not data or 'command' not in data:
                return jsonify({"error": "Command is required"}), 400
            
            command = data['command']
            payload = data.get('payload', {})
            
            # Log the execution
            print(f"[API] Agent {auth_data['agent_name']} executing: {command}")
            
            # For MVP, return success with basic response
            return jsonify({
                "success": True,
                "agent_id": auth_data['agent_id'],
                "agent_name": auth_data['agent_name'],
                "command": command,
                "result": f"Command '{command}' executed successfully",
                "timestamp": datetime.now().isoformat()
            })
    
    def run(self, debug=False):
        """Run the API server."""
        print(f"[API] Starting Hearthlink API Server on port {self.port}")
        print(f"[API] Database: {self.db_path}")
        print(f"[API] Endpoints available:")
        print(f"  POST /api/agents          - Create agent profile")
        print(f"  GET  /api/agents          - List agents")
        print(f"  GET  /api/agents/<id>     - Get agent")
        print(f"  POST /api/agents/<id>/tokens - Generate token")
        print(f"  GET  /api/tokens          - List tokens")
        print(f"  POST /api/auth/verify     - Verify token")
        print(f"  POST /api/execute         - Execute command")
        
        self.app.run(host='0.0.0.0', port=self.port, debug=debug, threaded=True)

def main():
    """Main entry point for API server."""
    server = HearthlinkAPIServer(port=8080)
    server.run(debug=True)

if __name__ == "__main__":
    main()