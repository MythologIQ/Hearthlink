#!/usr/bin/env python3
"""
Hearthlink Session Manager
Persistent sessions and conversation history storage
Phase 1 implementation with SQLite backend
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from contextlib import asynccontextmanager

# Import our database manager
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.database_manager import get_database_manager, DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    IDLE = "idle" 
    EXPIRED = "expired"
    TERMINATED = "terminated"

class MessageRole(Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT = "agent"

@dataclass
class SessionConfig:
    """Session configuration"""
    default_expiry_hours: int = 24
    idle_timeout_minutes: int = 120  # 2 hours
    max_conversation_length: int = 1000
    auto_save_interval_seconds: int = 30
    memory_retention_days: int = 90
    enable_persistence: bool = True

@dataclass
class ConversationMessage:
    """Individual conversation message"""
    id: str
    session_id: str
    agent_id: str
    user_id: str
    role: MessageRole
    content: str
    timestamp: datetime
    message_type: str = "text"
    metadata: Dict[str, Any] = None
    memory_references: List[str] = None
    processing_time: float = None
    model_used: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.memory_references is None:
            self.memory_references = []

@dataclass
class SessionInfo:
    """Session information"""
    id: str
    user_id: str
    session_token: str
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    agent_context: Dict[str, Any]
    metadata: Dict[str, Any]
    conversation_count: int = 0
    current_turn: Optional[str] = None  # Current agent with turn
    turn_queue: List[str] = None  # Queue of agents waiting for turn
    
    def __post_init__(self):
        if self.agent_context is None:
            self.agent_context = {}
        if self.metadata is None:
            self.metadata = {}
        if self.turn_queue is None:
            self.turn_queue = []

class SessionManager:
    """Main session manager with persistent storage"""
    
    def __init__(self, db_manager: DatabaseManager = None, config: SessionConfig = None):
        self.db = db_manager or get_database_manager()
        self.config = config or SessionConfig()
        self._active_sessions: Dict[str, SessionInfo] = {}
        self._session_locks: Dict[str, asyncio.Lock] = {}
        
    async def create_session(self, user_id: str, agent_context: Dict = None, 
                           metadata: Dict = None, expires_in_hours: int = None) -> Tuple[str, str]:
        """Create a new session"""
        expires_hours = expires_in_hours or self.config.default_expiry_hours
        agent_context = agent_context or {}
        metadata = metadata or {}
        
        # Ensure user exists before creating session
        user = self.db.get_user(user_id)
        if not user:
            # Create user if it doesn't exist - make username unique
            import time
            timestamp = str(int(time.time() * 1000))[-6:]  # Last 6 digits of timestamp
            username = f"user_{user_id[:8]}_{timestamp}"  # Generate unique username
            self.db.create_user(username=username, user_id=user_id)
            logger.info(f"Auto-created user {username} ({user_id}) for session")
        
        # Add session creation metadata
        metadata.update({
            "created_by": "session_manager",
            "version": "1.0.0",
            "config": {
                "expires_in_hours": expires_hours,
                "idle_timeout_minutes": self.config.idle_timeout_minutes
            }
        })
        
        # Create session in database
        session_id, session_token = self.db.create_session(
            user_id=user_id,
            expires_in_hours=expires_hours,
            agent_context=agent_context,
            metadata=metadata
        )
        
        # Create session info
        session_info = SessionInfo(
            id=session_id,
            user_id=user_id,
            session_token=session_token,
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=expires_hours),
            agent_context=agent_context,
            metadata=metadata
        )
        
        # Store in active sessions
        self._active_sessions[session_token] = session_info
        self._session_locks[session_token] = asyncio.Lock()
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id, session_token
    
    async def get_session(self, session_token: str) -> Optional[SessionInfo]:
        """Get session by token"""
        # Check active sessions first
        if session_token in self._active_sessions:
            session = self._active_sessions[session_token]
            # Check if expired
            if datetime.now() > session.expires_at:
                session.status = SessionStatus.EXPIRED
                await self._deactivate_session(session_token)
                return None
            return session
        
        # Load from database
        session_data = self.db.get_session(session_token)
        if session_data:
            session_info = SessionInfo(
                id=session_data['id'],
                user_id=session_data['user_id'],
                session_token=session_data['session_token'],
                status=SessionStatus.ACTIVE if session_data['active'] else SessionStatus.TERMINATED,
                created_at=datetime.fromisoformat(session_data['created_at']),
                last_activity=datetime.fromisoformat(session_data['last_activity']),
                expires_at=datetime.fromisoformat(session_data['expires_at']),
                agent_context=session_data['agent_context'],
                metadata=session_data['metadata']
            )
            
            # Add to active sessions if still valid
            if session_info.status == SessionStatus.ACTIVE and datetime.now() <= session_info.expires_at:
                self._active_sessions[session_token] = session_info
                self._session_locks[session_token] = asyncio.Lock()
                return session_info
        
        return None
    
    async def update_session_activity(self, session_token: str, agent_context: Dict = None):
        """Update session activity timestamp"""
        session = await self.get_session(session_token)
        if not session:
            return False
        
        async with self._session_locks.get(session_token, asyncio.Lock()):
            # Update in memory
            session.last_activity = datetime.now()
            if agent_context:
                session.agent_context.update(agent_context)
            
            # Update in database
            self.db.update_session_activity(session.id, session.agent_context)
            
            logger.debug(f"Updated activity for session {session.id}")
            return True
    
    async def add_conversation_message(self, session_token: str, agent_id: str,
                                     role: MessageRole, content: str, 
                                     message_type: str = "text",
                                     metadata: Dict = None,
                                     memory_references: List[str] = None,
                                     processing_time: float = None,
                                     model_used: str = None) -> Optional[str]:
        """Add a message to the conversation with FOREIGN KEY validation"""
        session = await self.get_session(session_token)
        if not session:
            logger.warning(f"Attempted to add message to invalid session: {session_token}")
            return None
        
        async with self._session_locks.get(session_token, asyncio.Lock()):
            # Ensure agent exists before creating conversation
            await self._ensure_agent_exists(agent_id, session.user_id)
            
            # Create conversation message
            message = ConversationMessage(
                id=str(uuid.uuid4()),
                session_id=session.id,
                agent_id=agent_id,
                user_id=session.user_id,
                role=role,
                content=content,
                timestamp=datetime.now(),
                message_type=message_type,
                metadata=metadata or {},
                memory_references=memory_references or [],
                processing_time=processing_time,
                model_used=model_used
            )
            
            try:
                # Store in database
                conversation_id = self.db.store_conversation(
                    session_id=session.id,
                    agent_id=agent_id,
                    user_id=session.user_id,
                    message_type=message_type,
                    content=content,
                    role=role.value,
                    metadata=message.metadata,
                    memory_references=message.memory_references,
                    processing_time=processing_time,
                    model_used=model_used
                )
                
                # Update session activity
                session.conversation_count += 1
                await self.update_session_activity(session_token)
                
                logger.debug(f"Added {role.value} message to session {session.id}")
                return conversation_id
                
            except Exception as e:
                logger.error(f"Failed to store conversation message: {e}")
                # If FOREIGN KEY constraint still fails, log details and return None
                if "FOREIGN KEY constraint failed" in str(e):
                    logger.error(f"FOREIGN KEY constraint failed for agent_id={agent_id}, session_id={session.id}")
                return None
    
    async def _ensure_agent_exists(self, agent_id: str, user_id: str):
        """Ensure agent exists in database, create if missing"""
        try:
            # Check if agent exists
            agent = self.db.get_agent(agent_id)
            if agent:
                return  # Agent exists
            
            # Agent doesn't exist, create it
            logger.info(f"Auto-creating agent {agent_id} for user {user_id}")
            
            # Define agent configurations for common agents
            agent_configs = {
                "alden": {
                    "name": "Alden",
                    "persona_type": "assistant", 
                    "description": "Primary AI assistant",
                    "capabilities": ["conversation", "memory", "analysis", "rag"],
                    "personality_traits": {"openness": 0.8, "conscientiousness": 0.9}
                },
                "alice": {
                    "name": "Alice",
                    "persona_type": "cognitive_analyst",
                    "description": "Cognitive-behavioral analysis specialist", 
                    "capabilities": ["analysis", "psychology", "behavioral_assessment"],
                    "personality_traits": {"analytical": 0.95, "empathetic": 0.85}
                },
                "system": {
                    "name": "System",
                    "persona_type": "system",
                    "description": "System management agent",
                    "capabilities": ["system", "admin"],
                    "personality_traits": {"reliability": 1.0}
                }
            }
            
            # Get configuration for this agent or use default
            config = agent_configs.get(agent_id, {
                "name": agent_id.capitalize(),
                "persona_type": "dynamic",
                "description": f"Auto-created agent for {agent_id}",
                "capabilities": ["conversation"],
                "personality_traits": {}
            })
            
            # Create the agent
            created_agent_id = self.db.create_agent(
                user_id=user_id,
                name=config["name"],
                persona_type=config["persona_type"],
                description=config["description"],
                capabilities=config["capabilities"],
                personality_traits=config["personality_traits"]
            )
            
            # Update the agent ID to match the requested one if different
            if created_agent_id != agent_id:
                # This is a workaround for UUID generation in create_agent
                # We need to update the ID to match what was requested
                with self.db.transaction() as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE agents SET id = ? WHERE id = ?", (agent_id, created_agent_id))
            
            logger.info(f"Successfully created agent {agent_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to ensure agent {agent_id} exists: {e}")
            # Don't raise - let the conversation creation proceed with triggers handling it
    
    async def get_conversation_history(self, session_token: str, 
                                     limit: int = None) -> List[ConversationMessage]:
        """Get conversation history for a session"""
        session = await self.get_session(session_token)
        if not session:
            return []
        
        limit = limit or self.config.max_conversation_length
        
        # Get from database
        conversations = self.db.get_conversation_history(session.id, limit)
        
        # Convert to ConversationMessage objects
        messages = []
        for conv in conversations:
            message = ConversationMessage(
                id=conv['id'],
                session_id=conv['session_id'],
                agent_id=conv['agent_id'],
                user_id=conv['user_id'],
                role=MessageRole(conv['role']),
                content=conv['content'],
                timestamp=datetime.fromisoformat(conv['timestamp']),
                message_type=conv['message_type'],
                metadata=conv['metadata'],
                memory_references=conv['memory_references'],
                processing_time=conv.get('processing_time'),
                model_used=conv.get('model_used')
            )
            messages.append(message)
        
        return messages
    
    async def get_recent_context(self, session_token: str, 
                               message_count: int = 10) -> List[Dict]:
        """Get recent conversation context for AI processing"""
        messages = await self.get_conversation_history(session_token, message_count)
        
        # Convert to simple format for AI processing
        context = []
        for msg in messages[-message_count:]:  # Get last N messages
            context.append({
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "agent_id": msg.agent_id,
                "processing_time": msg.processing_time,
                "model_used": msg.model_used
            })
        
        return context
    
    async def extend_session(self, session_token: str, hours: int = 24) -> bool:
        """Extend session expiry time"""
        session = await self.get_session(session_token)
        if not session:
            return False
        
        async with self._session_locks.get(session_token, asyncio.Lock()):
            # Update expiry time
            session.expires_at = datetime.now() + timedelta(hours=hours)
            
            # Update in database (need to add this method to DatabaseManager)
            # For now, update activity which will help keep it alive
            await self.update_session_activity(session_token)
            
            logger.info(f"Extended session {session.id} by {hours} hours")
            return True
    
    async def terminate_session(self, session_token: str, reason: str = "user_request") -> bool:
        """Terminate a session"""
        session = await self.get_session(session_token)
        if not session:
            return False
        
        async with self._session_locks.get(session_token, asyncio.Lock()):
            # Update session status
            session.status = SessionStatus.TERMINATED
            session.metadata["termination_reason"] = reason
            session.metadata["terminated_at"] = datetime.now().isoformat()
            
            # Mark as inactive in database
            # (Would need to add this method to DatabaseManager)
            
            # Remove from active sessions
            await self._deactivate_session(session_token)
            
            logger.info(f"Terminated session {session.id}: {reason}")
            return True
    
    async def _deactivate_session(self, session_token: str):
        """Remove session from active memory"""
        if session_token in self._active_sessions:
            del self._active_sessions[session_token]
        if session_token in self._session_locks:
            del self._session_locks[session_token]
    
    async def cleanup_expired_sessions(self):
        """Cleanup expired sessions"""
        current_time = datetime.now()
        expired_tokens = []
        
        for token, session in self._active_sessions.items():
            if current_time > session.expires_at:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            await self.terminate_session(token, "expired")
        
        logger.info(f"Cleaned up {len(expired_tokens)} expired sessions")
        return len(expired_tokens)
    
    async def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[SessionInfo]:
        """Get all sessions for a user"""
        sessions = []
        
        # Get from active sessions
        for session in self._active_sessions.values():
            if session.user_id == user_id:
                if not active_only or session.status == SessionStatus.ACTIVE:
                    sessions.append(session)
        
        # Could also query database for historical sessions
        # This would require adding a method to DatabaseManager
        
        return sessions
    
    def get_session_stats(self) -> Dict:
        """Get session manager statistics"""
        active_count = len([s for s in self._active_sessions.values() 
                          if s.status == SessionStatus.ACTIVE])
        
        total_conversations = sum(s.conversation_count for s in self._active_sessions.values())
        
        return {
            "active_sessions": active_count,
            "total_sessions_in_memory": len(self._active_sessions),
            "total_conversations": total_conversations,
            "config": asdict(self.config),
            "uptime_seconds": (datetime.now() - datetime.now()).total_seconds() # Would track actual uptime
        }
    
    # Turn-taking functionality
    async def request_turn(self, session_token: str, agent_id: str) -> bool:
        """Request turn for an agent in the session"""
        if session_token not in self._active_sessions:
            return False
        
        session = self._active_sessions[session_token]
        
        # If no current turn holder, grant immediately
        if not session.current_turn:
            session.current_turn = agent_id
            logger.info(f"Turn granted to {agent_id} in session {session_token}")
            return True
        
        # If same agent already has turn, keep it
        if session.current_turn == agent_id:
            return True
        
        # Add to queue if not already there
        if agent_id not in session.turn_queue:
            session.turn_queue.append(agent_id)
            logger.info(f"Agent {agent_id} added to turn queue in session {session_token}")
        
        return False
    
    async def release_turn(self, session_token: str, agent_id: str) -> Optional[str]:
        """Release turn and pass to next agent in queue"""
        if session_token not in self._active_sessions:
            return None
        
        session = self._active_sessions[session_token]
        
        # Only the current turn holder can release
        if session.current_turn != agent_id:
            return None
        
        # Pass to next in queue
        if session.turn_queue:
            next_agent = session.turn_queue.pop(0)
            session.current_turn = next_agent
            logger.info(f"Turn passed from {agent_id} to {next_agent} in session {session_token}")
            return next_agent
        else:
            session.current_turn = None
            logger.info(f"Turn released by {agent_id} in session {session_token}")
            return None
    
    async def get_current_turn(self, session_token: str) -> Optional[str]:
        """Get current turn holder"""
        if session_token not in self._active_sessions:
            return None
        return self._active_sessions[session_token].current_turn
    
    # Context propagation functionality
    async def propagate_context(self, session_token: str, context_update: Dict[str, Any]) -> bool:
        """Propagate context changes across the session"""
        if session_token not in self._active_sessions:
            return False
        
        session = self._active_sessions[session_token]
        
        # Update agent context
        session.agent_context.update(context_update)
        
        # Persist to database
        try:
            # For now, we'll store it in memory; database method would be added later
            session.metadata['last_context_update'] = datetime.now().isoformat()
            logger.info(f"Context propagated in session {session_token}: {context_update}")
            return True
        except Exception as e:
            logger.error(f"Failed to propagate context: {e}")
            return False

# Conversation Helper Functions
class ConversationHelper:
    """Helper class for common conversation operations"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
    
    async def start_conversation(self, user_id: str, agent_id: str, 
                               initial_message: str = None) -> Tuple[str, str]:
        """Start a new conversation session"""
        # Create session
        session_id, session_token = await self.session_manager.create_session(
            user_id=user_id,
            agent_context={"primary_agent": agent_id},
            metadata={"conversation_type": "chat", "started_by": "user"}
        )
        
        # Add initial system message if provided
        if initial_message:
            await self.session_manager.add_conversation_message(
                session_token=session_token,
                agent_id=agent_id,  # Use the actual agent_id instead of "system"
                role=MessageRole.SYSTEM,
                content=initial_message,
                message_type="system_init"
            )
        
        return session_id, session_token
    
    async def send_user_message(self, session_token: str, user_message: str,
                              metadata: Dict = None) -> Optional[str]:
        """Send a user message"""
        session = await self.session_manager.get_session(session_token)
        if not session:
            return None
        
        # Get primary agent from context
        agent_id = session.agent_context.get("primary_agent", "unknown")
        
        return await self.session_manager.add_conversation_message(
            session_token=session_token,
            agent_id=agent_id,
            role=MessageRole.USER,
            content=user_message,
            metadata=metadata
        )
    
    async def send_agent_response(self, session_token: str, agent_id: str,
                                response: str, processing_time: float = None,
                                model_used: str = None, memory_refs: List[str] = None,
                                metadata: Dict = None) -> Optional[str]:
        """Send an agent response"""
        return await self.session_manager.add_conversation_message(
            session_token=session_token,
            agent_id=agent_id,
            role=MessageRole.ASSISTANT,
            content=response,
            processing_time=processing_time,
            model_used=model_used,
            memory_references=memory_refs,
            metadata=metadata
        )
    
    async def get_conversation_summary(self, session_token: str) -> Dict:
        """Get a summary of the conversation"""
        session = await self.session_manager.get_session(session_token)
        if not session:
            return {}
        
        messages = await self.session_manager.get_conversation_history(session_token)
        
        user_messages = [m for m in messages if m.role == MessageRole.USER]
        agent_messages = [m for m in messages if m.role == MessageRole.ASSISTANT]
        
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "agent_messages": len(agent_messages),
            "agents_involved": list(set(m.agent_id for m in messages)),
            "conversation_duration_minutes": (session.last_activity - session.created_at).total_seconds() / 60,
            "avg_processing_time": sum(m.processing_time for m in agent_messages if m.processing_time) / len(agent_messages) if agent_messages else 0
        }

# Singleton session manager
_session_manager = None

def get_session_manager(config: SessionConfig = None) -> SessionManager:
    """Get singleton session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(config=config)
    return _session_manager

# Demo and testing
async def demo_session_management():
    """Demo session management functionality"""
    # Initialize
    session_manager = get_session_manager()
    helper = ConversationHelper(session_manager)
    
    # Get or create demo user
    demo_user = session_manager.db.get_user_by_username("demo_user")
    if demo_user:
        user_id = demo_user['id']
        print(f"Using existing user: {user_id}")
    else:
        user_id = session_manager.db.create_user("demo_user", "demo@hearthlink.ai")
        print(f"Created new user: {user_id}")
    
    # Get or create demo agent
    agents = session_manager.db.get_user_agents(user_id)
    alden_agent = next((a for a in agents if a['name'] == 'Alden'), None)
    if alden_agent:
        agent_id = alden_agent['id']
        print(f"Using existing agent: {agent_id}")
    else:
        agent_id = session_manager.db.create_agent(
            user_id=user_id,
            name="Alden",
            persona_type="assistant",
            description="Primary AI assistant"
        )
        print(f"Created new agent: {agent_id}")
    
    # Create a conversation
    print("Creating conversation...")
    session_id, session_token = await helper.start_conversation(
        user_id=user_id,
        agent_id=agent_id,
        initial_message="Starting new conversation with Alden"
    )
    print(f"Created session: {session_id}")
    
    # Send user message
    print("Sending user message...")
    await helper.send_user_message(
        session_token=session_token,
        user_message="Hello, can you help me with a task?",
        metadata={"input_method": "text"}
    )
    
    # Send agent response
    print("Sending agent response...")
    await helper.send_agent_response(
        session_token=session_token,
        agent_id=agent_id,
        response="Hello! I'd be happy to help you with your task. What would you like to work on?",
        processing_time=1.2,
        model_used="llama3:latest",
        metadata={"confidence": 0.95}
    )
    
    # Get conversation history
    print("Getting conversation history...")
    messages = await session_manager.get_conversation_history(session_token)
    print(f"Found {len(messages)} messages")
    
    # Get conversation summary
    print("Getting conversation summary...")
    summary = await helper.get_conversation_summary(session_token)
    print("Summary:", json.dumps(summary, indent=2))
    
    # Get session stats
    print("Session stats:", json.dumps(session_manager.get_session_stats(), indent=2))
    
    return session_token

if __name__ == "__main__":
    # Run demo
    import asyncio
    
    async def main():
        try:
            session_token = await demo_session_management()
            print(f"Demo completed successfully. Session token: {session_token}")
        except Exception as e:
            print(f"Demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())