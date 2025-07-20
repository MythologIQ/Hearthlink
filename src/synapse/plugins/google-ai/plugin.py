#!/usr/bin/env python3
"""
Google AI External Agent Plugin
Provides integration with Google AI API for external agent capabilities
"""

import os
import json
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

class GoogleAIAgent:
    """Google AI external agent implementation."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_key = os.getenv('GOOGLE_AI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-1.5-flash"
        
        # File access configuration
        self.workspace_dir = Path("./workspace")
        self.outputs_dir = Path("./outputs")
        self.allowed_paths = [
            Path("/tmp/hearthlink"),
            Path("./hearthlink_data"),
            self.workspace_dir,
            self.outputs_dir
        ]
        
        # Ensure directories exist
        for path in self.allowed_paths:
            path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a request through Google AI.
        
        Args:
            request: Request payload containing message and options
            
        Returns:
            Response dictionary with result and metadata
        """
        try:
            action = request.get('action', 'generate')
            
            if action == 'generate':
                return self._generate_response(request)
            elif action == 'write_file':
                return self._write_file(request)
            elif action == 'read_file':
                return self._read_file(request)
            elif action == 'list_files':
                return self._list_files(request)
            elif action == 'status':
                return self._get_status()
            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Google AI agent error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_response(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate text response using Google AI API."""
        
        if not self.api_key:
            return {
                'success': False,
                'error': 'Google AI API key not configured',
                'timestamp': datetime.now().isoformat()
            }
        
        message = request.get('message', '')
        if not message:
            return {
                'success': False,
                'error': 'Message is required',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Prepare API request
            url = f"{self.base_url}/models/{self.model}:generateContent"
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }
            
            payload = {
                'contents': [{
                    'parts': [{'text': message}]
                }],
                'generationConfig': {
                    'temperature': request.get('temperature', 0.7),
                    'maxOutputTokens': request.get('max_tokens', 1000),
                    'topP': request.get('top_p', 0.8),
                    'topK': request.get('top_k', 40)
                }
            }
            
            # Make API request
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract generated text
                candidates = result.get('candidates', [])
                if candidates and 'content' in candidates[0]:
                    parts = candidates[0]['content'].get('parts', [])
                    if parts and 'text' in parts[0]:
                        generated_text = parts[0]['text']
                        
                        return {
                            'success': True,
                            'response': generated_text,
                            'model': self.model,
                            'agent_type': 'external',
                            'provider': 'google_ai',
                            'usage': result.get('usageMetadata', {}),
                            'timestamp': datetime.now().isoformat()
                        }
                        
                return {
                    'success': False,
                    'error': 'No valid response from Google AI',
                    'raw_response': result,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Google AI API error: {response.status_code}',
                    'details': response.text,
                    'timestamp': datetime.now().isoformat()
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _write_file(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to a file in allowed workspace."""
        
        file_path = request.get('file_path', '')
        content = request.get('content', '')
        
        if not file_path or not content:
            return {
                'success': False,
                'error': 'file_path and content are required',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Resolve and validate path
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.workspace_dir / target_path
            
            # Security check - ensure path is in allowed directories
            path_allowed = False
            for allowed_path in self.allowed_paths:
                try:
                    target_path.resolve().relative_to(allowed_path.resolve())
                    path_allowed = True
                    break
                except ValueError:
                    continue
            
            if not path_allowed:
                return {
                    'success': False,
                    'error': f'File path not in allowed directories: {target_path}',
                    'allowed_paths': [str(p) for p in self.allowed_paths],
                    'timestamp': datetime.now().isoformat()
                }
            
            # Create parent directories if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'message': f'File written successfully: {target_path}',
                'file_path': str(target_path),
                'size_bytes': len(content.encode('utf-8')),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'File write error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _read_file(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Read content from a file in allowed workspace."""
        
        file_path = request.get('file_path', '')
        
        if not file_path:
            return {
                'success': False,
                'error': 'file_path is required',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Resolve and validate path
            target_path = Path(file_path)
            if not target_path.is_absolute():
                target_path = self.workspace_dir / target_path
            
            # Security check
            path_allowed = False
            for allowed_path in self.allowed_paths:
                try:
                    target_path.resolve().relative_to(allowed_path.resolve())
                    path_allowed = True
                    break
                except ValueError:
                    continue
            
            if not path_allowed:
                return {
                    'success': False,
                    'error': f'File path not in allowed directories: {target_path}',
                    'timestamp': datetime.now().isoformat()
                }
            
            if not target_path.exists():
                return {
                    'success': False,
                    'error': f'File not found: {target_path}',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Read file
            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'success': True,
                'content': content,
                'file_path': str(target_path),
                'size_bytes': len(content.encode('utf-8')),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'File read error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _list_files(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """List files in workspace directory."""
        
        directory = request.get('directory', str(self.workspace_dir))
        
        try:
            target_dir = Path(directory)
            if not target_dir.is_absolute():
                target_dir = self.workspace_dir / target_dir
            
            # Security check
            path_allowed = False
            for allowed_path in self.allowed_paths:
                try:
                    target_dir.resolve().relative_to(allowed_path.resolve())
                    path_allowed = True
                    break
                except ValueError:
                    continue
            
            if not path_allowed:
                return {
                    'success': False,
                    'error': f'Directory not in allowed paths: {target_dir}',
                    'timestamp': datetime.now().isoformat()
                }
            
            if not target_dir.exists():
                return {
                    'success': False,
                    'error': f'Directory not found: {target_dir}',
                    'timestamp': datetime.now().isoformat()
                }
            
            # List files
            files = []
            for item in target_dir.iterdir():
                files.append({
                    'name': item.name,
                    'path': str(item),
                    'is_file': item.is_file(),
                    'is_directory': item.is_dir(),
                    'size_bytes': item.stat().st_size if item.is_file() else 0,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            
            return {
                'success': True,
                'directory': str(target_dir),
                'files': files,
                'count': len(files),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Directory listing error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_status(self) -> Dict[str, Any]:
        """Get agent status and capabilities."""
        
        return {
            'success': True,
            'agent_id': 'google-ai',
            'status': 'active',
            'api_key_configured': bool(self.api_key),
            'model': self.model,
            'capabilities': [
                'text_generation',
                'file_operations',
                'workspace_access'
            ],
            'workspace_paths': [str(p) for p in self.allowed_paths],
            'file_access_enabled': True,
            'timestamp': datetime.now().isoformat()
        }

# Plugin entry point
def create_agent(config: Dict[str, Any] = None) -> GoogleAIAgent:
    """Create and return Google AI agent instance."""
    return GoogleAIAgent(config)

if __name__ == "__main__":
    # Test the agent
    agent = GoogleAIAgent()
    
    # Test status
    print("=== Agent Status ===")
    status = agent.execute({'action': 'status'})
    print(json.dumps(status, indent=2))
    
    # Test file operations
    print("\n=== File Write Test ===")
    write_result = agent.execute({
        'action': 'write_file',
        'file_path': 'test_output.txt',
        'content': 'Hello from Google AI External Agent!\nThis is a test of file writing capabilities.'
    })
    print(json.dumps(write_result, indent=2))
    
    print("\n=== File Read Test ===")
    read_result = agent.execute({
        'action': 'read_file',
        'file_path': 'test_output.txt'
    })
    print(json.dumps(read_result, indent=2))
    
    print("\n=== File List Test ===")
    list_result = agent.execute({
        'action': 'list_files'
    })
    print(json.dumps(list_result, indent=2))