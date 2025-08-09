#!/usr/bin/env python3
"""
Database Migration v1.1: Fix FOREIGN KEY Constraints
Addresses Phase 1.5 integration blocker - conversation schema constraints
"""

import sqlite3
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class DatabaseMigrationV11:
    """Migration to fix FOREIGN KEY constraint issues"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.version = "1.1"
        
    def apply_migration(self) -> bool:
        """Apply migration with proper FOREIGN KEY handling"""
        try:
            logger.info("Starting migration v1.1: FOREIGN KEY constraint fixes")
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                cursor = conn.cursor()
                
                # Step 1: Create default system agents for common agent_ids
                self._create_default_agents(cursor)
                
                # Step 2: Fix orphaned conversations by creating missing agents
                self._fix_orphaned_conversations(cursor)
                
                # Step 3: Add constraint validation triggers
                self._add_validation_triggers(cursor)
                
                # Step 4: Update schema version
                cursor.execute("""
                    INSERT OR REPLACE INTO schema_info (version, description) 
                    VALUES (?, ?)
                """, (2, "v1.1 - Fixed FOREIGN KEY constraints and added validation"))
                
                conn.commit()
                
            logger.info("Migration v1.1 completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration v1.1 failed: {e}")
            return False
    
    def _create_default_agents(self, cursor: sqlite3.Cursor):
        """Create default system agents for common agent_ids"""
        default_agents = [
            {
                "id": "alden",
                "name": "Alden",
                "persona_type": "assistant",
                "description": "Primary AI assistant",
                "capabilities": ["conversation", "memory", "analysis", "rag", "handoff"],
                "personality_traits": {"openness": 0.8, "conscientiousness": 0.9}
            },
            {
                "id": "alice", 
                "name": "Alice",
                "persona_type": "cognitive_analyst",
                "description": "Cognitive-behavioral analysis specialist",
                "capabilities": ["analysis", "psychology", "behavioral_assessment"],
                "personality_traits": {"analytical": 0.95, "empathetic": 0.85}
            },
            {
                "id": "system",
                "name": "System",
                "persona_type": "system",
                "description": "System management agent",
                "capabilities": ["system", "admin", "monitoring"],
                "personality_traits": {"reliability": 1.0}
            }
        ]
        
        # Get system user or create one
        cursor.execute("SELECT id FROM users WHERE username = 'system'")
        system_user = cursor.fetchone()
        
        if not system_user:
            system_user_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, username, email, preferences)
                VALUES (?, ?, ?, ?)
            """, (system_user_id, "system", "system@hearthlink.internal", "{}"))
            logger.info(f"Created system user: {system_user_id}")
        else:
            system_user_id = system_user[0]
        
        # Create agents
        for agent_config in default_agents:
            cursor.execute("SELECT id FROM agents WHERE id = ?", (agent_config["id"],))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute("""
                    INSERT INTO agents (
                        id, user_id, name, persona_type, description,
                        capabilities, config, personality_traits, active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent_config["id"],
                    system_user_id,
                    agent_config["name"],
                    agent_config["persona_type"],
                    agent_config["description"],
                    json.dumps(agent_config["capabilities"]),
                    json.dumps({}),
                    json.dumps(agent_config["personality_traits"]),
                    1
                ))
                logger.info(f"Created default agent: {agent_config['name']} ({agent_config['id']})")
    
    def _fix_orphaned_conversations(self, cursor: sqlite3.Cursor):
        """Fix conversations that reference non-existent agents"""
        # Find conversations with missing agents
        cursor.execute("""
            SELECT DISTINCT c.agent_id, c.user_id
            FROM conversations c
            LEFT JOIN agents a ON c.agent_id = a.id
            WHERE a.id IS NULL
        """)
        
        orphaned_agents = cursor.fetchall()
        
        for agent_id, user_id in orphaned_agents:
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            user_exists = cursor.fetchone()
            
            if not user_exists:
                # Create missing user
                cursor.execute("""
                    INSERT INTO users (id, username, email, preferences)
                    VALUES (?, ?, ?, ?)
                """, (user_id, f"user_{agent_id}", f"{agent_id}@hearthlink.local", "{}"))
                logger.info(f"Created missing user: {user_id}")
            
            # Create missing agent  
            cursor.execute("""
                INSERT INTO agents (
                    id, user_id, name, persona_type, description,
                    capabilities, config, personality_traits, active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_id,
                user_id,
                agent_id.capitalize(),
                "dynamic",
                f"Dynamically created agent for {agent_id}",
                json.dumps(["conversation"]),
                json.dumps({}),
                json.dumps({}),
                1
            ))
            logger.info(f"Created missing agent: {agent_id} for user {user_id}")
    
    def _add_validation_triggers(self, cursor: sqlite3.Cursor):
        """Add triggers to prevent FOREIGN KEY constraint violations"""
        
        # Trigger to auto-create agents on conversation insert if missing
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS auto_create_agent_on_conversation
            BEFORE INSERT ON conversations
            WHEN NEW.agent_id NOT IN (SELECT id FROM agents)
            BEGIN
                INSERT OR IGNORE INTO agents (
                    id, user_id, name, persona_type, description,
                    capabilities, config, personality_traits, active
                ) VALUES (
                    NEW.agent_id,
                    NEW.user_id, 
                    NEW.agent_id,
                    'auto_created',
                    'Auto-created agent for conversation',
                    '["conversation"]',
                    '{}',
                    '{}',
                    1
                );
            END;
        """)
        
        # Trigger to validate session references
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS validate_conversation_session
            BEFORE INSERT ON conversations
            WHEN NEW.session_id NOT IN (SELECT id FROM sessions)
            BEGIN
                SELECT RAISE(ABORT, 'Invalid session_id reference');
            END;
        """)
        
        logger.info("Added validation triggers for FOREIGN KEY constraints")
    
    def rollback_migration(self) -> bool:
        """Rollback migration (best effort)"""
        try:
            logger.info("Rolling back migration v1.1")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Remove triggers
                cursor.execute("DROP TRIGGER IF EXISTS auto_create_agent_on_conversation")
                cursor.execute("DROP TRIGGER IF EXISTS validate_conversation_session")
                
                # Note: We don't remove auto-created agents as they may have valid data
                # This is a conservative approach to avoid data loss
                
                # Revert schema version
                cursor.execute("""
                    DELETE FROM schema_info WHERE version = 2
                """)
                
                conn.commit()
                
            logger.info("Migration v1.1 rollback completed")
            return True
            
        except Exception as e:
            logger.error(f"Migration v1.1 rollback failed: {e}")
            return False

def apply_migration_v11(db_path: str) -> bool:
    """Apply migration v1.1 to fix FOREIGN KEY constraints"""
    migration = DatabaseMigrationV11(db_path)
    return migration.apply_migration()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "hearthlink_data/hearthlink.db"
    
    success = apply_migration_v11(db_path)
    print(f"Migration {'succeeded' if success else 'failed'}")