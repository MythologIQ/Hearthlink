#!/usr/bin/env python3
"""
Quick test of session management functionality
"""

import asyncio
import sys
import os
sys.path.append('src')

from core.session_manager import SessionManager, ConversationHelper, MessageRole

async def test_session_basic():
    """Test basic session functionality"""
    print("Testing session management...")
    
    # Initialize
    session_manager = SessionManager()
    
    # Get existing user and agent
    demo_user = session_manager.db.get_user_by_username("demo_user")
    if not demo_user:
        print("Demo user not found")
        return False
        
    user_id = demo_user['id']
    print(f"Using user: {user_id}")
    
    agents = session_manager.db.get_user_agents(user_id)
    if not agents:
        print("No agents found")
        return False
        
    agent_id = agents[0]['id']
    print(f"Using agent: {agent_id}")
    
    # Create session
    session_id, session_token = await session_manager.create_session(
        user_id=user_id,
        agent_context={"primary_agent": agent_id}
    )
    print(f"Created session: {session_id}")
    
    # Add a message
    message_id = await session_manager.add_conversation_message(
        session_token=session_token,
        agent_id=agent_id,
        role=MessageRole.USER,
        content="Hello, this is a test message",
        message_type="text"
    )
    print(f"Added message: {message_id}")
    
    # Get conversation history
    messages = await session_manager.get_conversation_history(session_token)
    print(f"Retrieved {len(messages)} messages")
    
    # Add another message
    response_id = await session_manager.add_conversation_message(
        session_token=session_token,
        agent_id=agent_id,
        role=MessageRole.ASSISTANT,
        content="Hello! I received your test message.",
        message_type="text"
    )
    print(f"Added response: {response_id}")
    
    # Get updated history
    messages = await session_manager.get_conversation_history(session_token)
    print(f"Final conversation has {len(messages)} messages")
    
    for msg in messages:
        print(f"  {msg.role.value}: {msg.content}")
    
    # Get stats
    stats = session_manager.get_session_stats()
    print(f"Session stats: {stats}")
    
    return True

if __name__ == "__main__":
    async def main():
        try:
            success = await test_session_basic()
            if success:
                print("\n✅ Session management test completed successfully!")
            else:
                print("\n❌ Session management test failed!")
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(main())