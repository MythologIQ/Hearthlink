#!/usr/bin/env python3
"""
Vault API Service
Provides REST API endpoints for Vault interface
"""

import json
import os
import traceback
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from typing import Dict, Any, Optional, List

import sys
import os

# Add the parent directory to the path so we can import from other directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.vault_connector import VaultConnector
from vault.vault import Vault

app = Flask(__name__)
CORS(app)

# Initialize Vault services
vault_connector = None
vault_service = None

def initialize_vault():
    """Initialize Vault services"""
    global vault_connector, vault_service
    
    try:
        # Initialize vault connector
        vault_connector = VaultConnector()
        
        # Initialize vault service
        vault_config = {
            "encryption": {
                "key_file": "hearthlink_data/vault.key",
                "key_env_var": "VAULT_KEY"
            },
            "storage": {
                "type": "file",
                "file_path": "hearthlink_data/vault_storage"
            }
        }
        
        vault_service = Vault(vault_config)
        print("Vault services initialized successfully")
        
    except Exception as e:
        print(f"Failed to initialize Vault services: {e}")
        traceback.print_exc()

@app.route('/api/vault/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        if vault_connector and vault_service:
            return jsonify({
                'status': 'healthy',
                'service': 'vault-api',
                'version': '1.0.0',
                'connection': vault_connector.connected if vault_connector else False
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'service': 'vault-api',
                'error': 'Vault services not initialized'
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'vault-api',
            'error': str(e)
        }), 503

@app.route('/api/vault/stats', methods=['GET'])
def get_vault_stats():
    """Get vault statistics"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        # Get statistics from vault connector
        stats = vault_connector.get_stats()
        
        # Enhanced stats for the interface
        enhanced_stats = {
            'totalMemories': stats.get('total_memories', 0),
            'personaMemories': stats.get('persona_memories', 0),
            'communalMemories': stats.get('communal_memories', 0),
            'storageUsed': stats.get('storage_used', 0),
            'lastBackup': stats.get('last_backup'),
            'integrityStatus': stats.get('integrity_status', 'verified'),
            'encryptionStatus': 'enabled' if vault_connector.cipher_suite else 'disabled'
        }
        
        return jsonify(enhanced_stats)
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get vault stats: {str(e)}'
        }), 500

@app.route('/api/vault/memories', methods=['GET'])
def get_memories():
    """Get memories with optional filtering"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        # Get query parameters
        persona_id = request.args.get('persona_id')
        memory_type = request.args.get('type')
        search_query = request.args.get('search')
        limit = int(request.args.get('limit', 100))
        
        # If search query is provided, use search_memories
        if search_query:
            filters = {}
            if persona_id:
                filters['persona_id'] = persona_id
            if memory_type:
                filters['memory_type'] = memory_type
            
            memories = vault_connector.search_memories(
                query=search_query,
                filters=filters,
                limit=limit
            )
        else:
            # Use get_memories for regular retrieval
            memories = vault_connector.get_memories(
                persona_id=persona_id,
                memory_type=memory_type,
                limit=limit
            )
        
        return jsonify({
            'memories': memories,
            'count': len(memories)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get memories: {str(e)}'
        }), 500

@app.route('/api/vault/memories', methods=['POST'])
def create_memory():
    """Create a new memory"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        data = request.json
        
        # Validate required fields
        required_fields = ['persona_id', 'memory_type', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create memory
        memory_id = vault_connector.create_memory(
            persona_id=data['persona_id'],
            memory_type=data['memory_type'],
            content=data['content'],
            metadata=data.get('metadata', {}),
            user_id=data.get('user_id', 'system')
        )
        
        return jsonify({
            'success': True,
            'memory_id': memory_id,
            'message': 'Memory created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to create memory: {str(e)}'
        }), 500

@app.route('/api/vault/memories/<memory_id>', methods=['GET'])
def get_memory(memory_id):
    """Get a specific memory"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        memory = vault_connector.get_memory(memory_id)
        
        if memory:
            return jsonify(memory)
        else:
            return jsonify({'error': 'Memory not found'}), 404
            
    except Exception as e:
        return jsonify({
            'error': f'Failed to get memory: {str(e)}'
        }), 500

@app.route('/api/vault/memories/<memory_id>', methods=['PUT'])
def update_memory(memory_id):
    """Update a memory"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        data = request.json
        
        success = vault_connector.update_memory(
            memory_id=memory_id,
            content=data.get('content'),
            metadata=data.get('metadata'),
            user_id=data.get('user_id', 'system')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Memory updated successfully'
            })
        else:
            return jsonify({'error': 'Memory not found'}), 404
            
    except Exception as e:
        return jsonify({
            'error': f'Failed to update memory: {str(e)}'
        }), 500

@app.route('/api/vault/memories/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """Delete a memory"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        user_id = request.args.get('user_id', 'system')
        
        success = vault_connector.delete_memory(memory_id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Memory deleted successfully'
            })
        else:
            return jsonify({'error': 'Memory not found'}), 404
            
    except Exception as e:
        return jsonify({
            'error': f'Failed to delete memory: {str(e)}'
        }), 500

@app.route('/api/vault/audit-log', methods=['GET'])
def get_audit_log():
    """Get audit log entries"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        # Get query parameters
        limit = int(request.args.get('limit', 100))
        user_id = request.args.get('user_id')
        action = request.args.get('action')
        
        # Get audit log entries
        audit_entries = vault_connector.get_audit_log(
            limit=limit,
            user_id=user_id,
            action=action
        )
        
        return jsonify({
            'audit_log': audit_entries,
            'count': len(audit_entries)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get audit log: {str(e)}'
        }), 500

@app.route('/api/vault/backup', methods=['POST'])
def create_backup():
    """Create a backup of the vault"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        backup_path = vault_connector.create_backup()
        
        return jsonify({
            'success': True,
            'backup_path': backup_path,
            'message': 'Backup created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to create backup: {str(e)}'
        }), 500

@app.route('/api/vault/integrity', methods=['GET'])
def check_integrity():
    """Check vault integrity"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        integrity_result = vault_connector.check_integrity()
        
        return jsonify({
            'integrity_status': integrity_result['status'],
            'details': integrity_result.get('details', {}),
            'last_check': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to check integrity: {str(e)}'
        }), 500

@app.route('/api/vault/search', methods=['POST'])
def search_memories():
    """Search memories"""
    try:
        if not vault_connector:
            return jsonify({'error': 'Vault not initialized'}), 503
        
        data = request.json
        query = data.get('query', '')
        filters = data.get('filters', {})
        limit = data.get('limit', 100)
        
        results = vault_connector.search_memories(
            query=query,
            filters=filters,
            limit=limit
        )
        
        return jsonify({
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to search memories: {str(e)}'
        }), 500

# Initialize vault services on startup
initialize_vault()

if __name__ == '__main__':
    print("Starting Hearthlink Vault API...")
    print("Endpoints available:")
    print("  GET  /api/vault/health - Health check")
    print("  GET  /api/vault/stats - Get vault statistics")
    print("  GET  /api/vault/memories - Get memories")
    print("  POST /api/vault/memories - Create memory")
    print("  GET  /api/vault/memories/<id> - Get specific memory")
    print("  PUT  /api/vault/memories/<id> - Update memory")
    print("  DELETE /api/vault/memories/<id> - Delete memory")
    print("  GET  /api/vault/audit-log - Get audit log")
    print("  POST /api/vault/backup - Create backup")
    print("  GET  /api/vault/integrity - Check integrity")
    print("  POST /api/vault/search - Search memories")
    print("\\nStarting server on port 8002...")
    app.run(host='0.0.0.0', port=8002, debug=True)