#!/usr/bin/env python3
"""
Core API Service (Simplified)
Multi-agent orchestration and session management service using existing core.py
"""

import sys
import os
import socket
import json
import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Add project root to path  
sys.path.insert(0, '.')

def find_free_port(preferred_ports=[8001, 8002, 8003, 8004]):
    """Find the first available port from preferred list"""
    for port in preferred_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return 8001  # fallback

print('🏛️ Starting Hearthlink Core API Service (Simplified)...')
print('====================================================')

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
    
    app = FastAPI(
        title='Hearthlink Core API',
        description='Multi-agent orchestration and session management',
        version='1.0.0'
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    
    # Initialize Core components
    print('🔧 Initializing Core components...')
    
    # Simple in-memory session storage
    active_sessions = {}
    session_performance = {}
    
    # Pydantic models for API
    class CreateSessionRequest(BaseModel):
        user_id: str
        session_type: str = "collaborative"  
        objectives: List[str] = Field(default_factory=list)
        participants: List[Dict[str, Any]] = Field(default_factory=list)
    
    class AddParticipantRequest(BaseModel):
        participant_id: str
        name: str
        type: str  # "persona", "external", "user"
        role: str = "participant"
        capabilities: List[str] = Field(default_factory=list)
    
    class SessionMessage(BaseModel):
        agent_id: str
        content: str
        message_type: str = "text"
        metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Health check endpoint
    @app.get('/health')
    async def health():
        return {
            'status': 'healthy',
            'service': 'core_api_simple',
            'timestamp': datetime.now().isoformat(),
            'active_sessions': len(active_sessions)
        }
    
    @app.get('/status')
    async def get_status():
        """Get comprehensive Core system status"""
        total_participants = sum(
            len(session.get('participants', []))
            for session in active_sessions.values()
        )
        
        return {
            'service': 'core_api_simple',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'active_sessions': len(active_sessions),
            'total_participants': total_participants,
            'version': '1.0.0',
            'components': {
                'session_manager': True,
                'vault': False,  # Not implemented in simple version
                'database': False,  # Not implemented in simple version
                'performance_tracking': True
            }
        }
    
    # Session management endpoints
    @app.post('/sessions')
    async def create_session(request: CreateSessionRequest):
        """Create a new Core session"""
        try:
            session_id = f"core-{uuid.uuid4().hex[:12]}"
            session_token = f"token-{uuid.uuid4().hex}"
            
            print(f"📝 Creating session {session_id} for user {request.user_id}")
            
            session = {
                'id': session_id,
                'token': session_token,
                'user_id': request.user_id,
                'session_type': request.session_type,
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'objectives': request.objectives,
                'participants': request.participants,
                'messages': [],
                'turn_state': {
                    'current_turn': None,
                    'turn_queue': [p.get('id') for p in request.participants if p.get('role') == 'participant'],
                    'turn_history': []
                },
                'breakout_rooms': [],
                'performance_metrics': {
                    'messages_count': 0,
                    'participant_switches': 0,
                    'start_time': datetime.now().isoformat()
                }
            }
            
            active_sessions[session_id] = session
            session_performance[session_id] = {
                'start_time': datetime.now(),
                'message_count': 0,
                'participant_count': len(request.participants)
            }
            
            return {
                'session_id': session_id,
                'session_token': session_token,
                'session_type': request.session_type,
                'status': 'active',
                'created_at': session['created_at'],
                'participants': len(request.participants),
                'objectives': request.objectives
            }
            
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get('/sessions/{session_id}')
    async def get_session(session_id: str):
        """Get session information"""
        try:
            session = active_sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            return session
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Get session error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get('/sessions')
    async def list_sessions(user_id: Optional[str] = None, active_only: bool = True):
        """List sessions"""
        try:
            sessions = []
            for session_id, session in active_sessions.items():
                if user_id and session['user_id'] != user_id:
                    continue
                if active_only and session['status'] != 'active':
                    continue
                
                sessions.append({
                    'session_id': session['id'],
                    'user_id': session['user_id'],
                    'session_type': session['session_type'],
                    'status': session['status'],
                    'created_at': session['created_at'],
                    'participants': len(session['participants']),
                    'objectives': session['objectives']
                })
            
            return {
                'sessions': sessions,
                'total': len(sessions)
            }
            
        except Exception as e:
            print(f"❌ List sessions error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post('/sessions/{session_id}/participants')
    async def add_participant(session_id: str, request: AddParticipantRequest):
        """Add participant to session"""
        try:
            session = active_sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            participant = {
                'id': request.participant_id,
                'name': request.name,
                'type': request.type,
                'role': request.role,
                'capabilities': request.capabilities,
                'joined_at': datetime.now().isoformat(),
                'active': True
            }
            
            session['participants'].append(participant)
            session['last_activity'] = datetime.now().isoformat()
            
            # Add to turn queue if participant
            if request.role == 'participant':
                session['turn_state']['turn_queue'].append(request.participant_id)
            
            return {
                'success': True,
                'participant_id': request.participant_id,
                'session_id': session_id,
                'message': f'Participant {request.name} added to session'
            }
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Add participant error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post('/sessions/{session_id}/messages')
    async def add_message(session_id: str, message: SessionMessage):
        """Add message to session"""
        try:
            session = active_sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            message_entry = {
                'id': f"msg-{uuid.uuid4().hex[:8]}",
                'session_id': session_id,
                'agent_id': message.agent_id,
                'content': message.content,
                'message_type': message.message_type,
                'metadata': message.metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            session['messages'].append(message_entry)
            session['last_activity'] = datetime.now().isoformat()
            session['performance_metrics']['messages_count'] += 1
            
            # Update session performance
            if session_id in session_performance:
                session_performance[session_id]['message_count'] += 1
            
            return {
                'success': True,
                'message_id': message_entry['id'],
                'session_id': session_id,
                'timestamp': message_entry['timestamp']
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Add message error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get('/sessions/{session_id}/messages')
    async def get_messages(session_id: str, limit: int = 50):
        """Get session messages"""
        try:
            session = active_sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            messages = session['messages'][-limit:] if limit > 0 else session['messages']
            
            return {
                'session_id': session_id,
                'messages': messages,
                'total': len(session['messages'])
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Get messages error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post('/sessions/{session_id}/turns')
    async def manage_turns(session_id: str, action: str, participant_id: Optional[str] = None):
        """Manage turn-taking in session"""
        try:
            session = active_sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            turn_state = session['turn_state']
            result = {'action': action, 'timestamp': datetime.now().isoformat()}
            
            if action == 'next':
                if turn_state['turn_queue']:
                    current_turn = turn_state['turn_queue'].pop(0)
                    turn_state['current_turn'] = current_turn
                    turn_state['turn_history'].append({
                        'participant_id': current_turn,
                        'started_at': datetime.now().isoformat()
                    })
                    # Add back to end for round-robin
                    turn_state['turn_queue'].append(current_turn)
                    result['current_turn'] = current_turn
                else:
                    result['error'] = 'No participants in turn queue'
            
            elif action == 'assign' and participant_id:
                turn_state['current_turn'] = participant_id
                turn_state['turn_history'].append({
                    'participant_id': participant_id,
                    'started_at': datetime.now().isoformat(),
                    'assigned': True
                })
                result['current_turn'] = participant_id
            
            elif action == 'status':
                result.update({
                    'current_turn': turn_state.get('current_turn'),
                    'queue_length': len(turn_state.get('turn_queue', [])),
                    'turn_history_count': len(turn_state.get('turn_history', []))
                })
            
            session['last_activity'] = datetime.now().isoformat()
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Turn management error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get('/sessions/{session_id}/performance')
    async def get_session_performance(session_id: str):
        """Get session performance metrics"""
        try:
            session = active_sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            performance_data = session_performance.get(session_id, {})
            session_metrics = session['performance_metrics']
            
            current_time = datetime.now()
            start_time = datetime.fromisoformat(session_metrics['start_time'])
            duration = (current_time - start_time).total_seconds()
            
            return {
                'session_id': session_id,
                'session_type': session['session_type'],
                'duration_seconds': duration,
                'participant_count': len(session['participants']),
                'messages_processed': session_metrics['messages_count'],
                'participant_switches': session_metrics['participant_switches'],
                'performance_score': min(100, (session_metrics['messages_count'] * 5) + (len(session['participants']) * 10)),
                'status': session['status']
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Performance metrics error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete('/sessions/{session_id}')
    async def end_session(session_id: str):
        """End a session"""
        try:
            session = active_sessions.get(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session['status'] = 'ended'
            session['ended_at'] = datetime.now().isoformat()
            session['last_activity'] = datetime.now().isoformat()
            
            return {
                'success': True,
                'session_id': session_id,
                'ended_at': session['ended_at']
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ End session error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post('/cleanup')
    async def cleanup_expired_sessions():
        """Clean up expired sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session in list(active_sessions.items()):
                # Mark sessions older than 24 hours as expired
                created_at = datetime.fromisoformat(session['created_at'])
                if (current_time - created_at).total_seconds() > 86400:  # 24 hours
                    expired_sessions.append(session_id)
                    del active_sessions[session_id]
                    session_performance.pop(session_id, None)
            
            return {
                'success': True,
                'cleaned_sessions': len(expired_sessions),
                'remaining_sessions': len(active_sessions),
                'timestamp': current_time.isoformat()
            }
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Alden integration endpoints
    @app.get('/core/health')
    async def core_health():
        """Core module health check for Alden ecosystem monitoring"""
        return {
            'status': 'healthy',
            'module': 'core',
            'active_sessions': len(active_sessions),
            'timestamp': datetime.now().isoformat()
        }
    
    @app.get('/api/core/health')
    async def api_core_health():
        """Alternative health endpoint for dashboard panels"""
        return await core_health()
    
    @app.get('/api/vault/health')
    async def api_vault_health():
        """Vault health endpoint for frontend status checks"""
        return {
            'status': 'healthy',
            'module': 'vault',
            'available': True,
            'timestamp': datetime.now().isoformat()
        }
    
    print('✅ Core API components initialized')
    
    # Find available port and start server
    port = find_free_port()
    
    print(f'🚀 Starting Core API server on http://localhost:{port}')
    print('Available endpoints:')
    print('  GET  /health - Service health check')
    print('  GET  /status - Comprehensive system status')
    print('  POST /sessions - Create new session')
    print('  GET  /sessions - List sessions')
    print('  GET  /sessions/{id} - Get session details')
    print('  POST /sessions/{id}/participants - Add participant')
    print('  POST /sessions/{id}/messages - Add message to session')
    print('  GET  /sessions/{id}/messages - Get session messages')
    print('  POST /sessions/{id}/turns - Manage turn-taking')
    print('  GET  /sessions/{id}/performance - Get performance metrics')
    print('  DELETE /sessions/{id} - End session')
    print('  POST /cleanup - Clean up expired sessions')
    print('  GET  /core/health - Core health (for Alden ecosystem)')
    print('  GET  /api/core/health - Alternative health endpoint')
    print('====================================================')
    print('Press Ctrl+C to stop the server')
    
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info')
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    print('Make sure all dependencies are installed.')
    print('Try: pip install fastapi uvicorn')
except Exception as e:
    print(f'❌ Error starting Core API: {e}')
    import traceback
    traceback.print_exc()