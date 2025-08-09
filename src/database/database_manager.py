#!/usr/bin/env python3
"""
Hearthlink Database Manager
SQLite-based database layer with schema management, migrations, and ORM-like interface
Phase 1 implementation focused on local-first functionality
"""

import sqlite3
import json
import os
import uuid
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_path: str = os.environ.get('HEARTHLINK_DB_PATH', os.environ.get('DATABASE_PATH', "hearthlink_data/hearthlink.db"))
    backup_path: str = "hearthlink_data/backups"
    pool_size: int = 10
    timeout: float = 30.0
    enable_wal: bool = True
    enable_foreign_keys: bool = True
    auto_backup: bool = True
    backup_interval_hours: int = 24

class DatabaseSchema:
    """Database schema definitions and migrations"""
    
    CURRENT_VERSION = 1
    
    @staticmethod
    def get_schema_version_1() -> List[str]:
        """Initial schema for Phase 1"""
        return [
            """CREATE TABLE IF NOT EXISTS schema_info (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferences TEXT DEFAULT '{}',
                security_settings TEXT DEFAULT '{}',
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )""",
            
            """CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                persona_type TEXT NOT NULL,
                description TEXT,
                capabilities TEXT DEFAULT '[]',
                config TEXT DEFAULT '{}',
                personality_traits TEXT DEFAULT '{}',
                trust_level REAL DEFAULT 0.82,
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS memory_slices (
                id TEXT PRIMARY KEY,
                agent_id TEXT REFERENCES agents(id) ON DELETE CASCADE,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                slice_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                confidence REAL DEFAULT 1.0,
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )""",
            
            """CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                session_token TEXT UNIQUE NOT NULL,
                agent_context TEXT DEFAULT '{}',
                conversation_history TEXT DEFAULT '[]',
                active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                metadata TEXT DEFAULT '{}'
            )""",
            
            """CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                agent_id TEXT REFERENCES agents(id) ON DELETE CASCADE,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                role TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}',
                memory_references TEXT DEFAULT '[]',
                processing_time REAL,
                model_used TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS alden_personality (
                id TEXT PRIMARY KEY,
                agent_id TEXT REFERENCES agents(id) ON DELETE CASCADE,
                trait_name TEXT NOT NULL,
                trait_value REAL NOT NULL,
                trait_confidence REAL DEFAULT 1.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_reason TEXT,
                previous_value REAL,
                UNIQUE(agent_id, trait_name)
            )""",
            
            """CREATE TABLE IF NOT EXISTS cognitive_analytics (
                id TEXT PRIMARY KEY,
                agent_id TEXT REFERENCES agents(id) ON DELETE CASCADE,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                measurement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context TEXT DEFAULT '{}',
                aggregation_period TEXT DEFAULT 'instant'
            )""",
            
            # Indexes for performance
            """CREATE INDEX IF NOT EXISTS idx_memory_slices_user_agent ON memory_slices(user_id, agent_id)""",
            """CREATE INDEX IF NOT EXISTS idx_memory_slices_type_importance ON memory_slices(slice_type, importance DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_memory_slices_created_at ON memory_slices(created_at DESC)""",
            """CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id, timestamp)""",
            """CREATE INDEX IF NOT EXISTS idx_sessions_user_active ON sessions(user_id, active, last_activity)""",
            """CREATE INDEX IF NOT EXISTS idx_agents_user_active ON agents(user_id, active)""",
            """CREATE INDEX IF NOT EXISTS idx_cognitive_analytics_agent_time ON cognitive_analytics(agent_id, measurement_timestamp)""",
            
            # Insert schema version
            """INSERT OR REPLACE INTO schema_info (version, description) VALUES (1, 'Initial Phase 1 schema')"""
        ]

class ConnectionPool:
    """Simple SQLite connection pool"""
    
    def __init__(self, db_path: str, pool_size: int = 10, timeout: float = 30.0):
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._connections = []
        self._lock = threading.Lock()
        self._init_pool()
    
    def _init_pool(self):
        """Initialize connection pool"""
        for _ in range(self.pool_size):
            conn = self._create_connection()
            self._connections.append(conn)
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.timeout,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        return conn
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool"""
        with self._lock:
            if self._connections:
                conn = self._connections.pop()
            else:
                conn = self._create_connection()
        
        try:
            yield conn
        finally:
            with self._lock:
                if len(self._connections) < self.pool_size:
                    self._connections.append(conn)
                else:
                    conn.close()

class DatabaseManager:
    """Main database manager with ORM-like interface"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self._setup_database()
        self.pool = ConnectionPool(
            self.config.db_path,
            self.config.pool_size,
            self.config.timeout
        )
        self.schema = DatabaseSchema()
        
    def _setup_database(self):
        """Setup database and ensure directory exists"""
        db_path = Path(self.config.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        backup_path = Path(self.config.backup_path)
        backup_path.mkdir(parents=True, exist_ok=True)
    
    def initialize_schema(self):
        """Initialize database schema"""
        logger.info("Initializing database schema...")
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Apply schema
            for statement in self.schema.get_schema_version_1():
                try:
                    cursor.execute(statement)
                except Exception as e:
                    logger.error(f"Error executing schema statement: {e}")
                    logger.error(f"Statement: {statement}")
                    raise
            
            conn.commit()
        
        logger.info("Database schema initialized successfully")
    
    def get_schema_version(self) -> int:
        """Get current schema version"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(version) FROM schema_info")
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0
        except sqlite3.OperationalError:
            return 0
    
    @contextmanager
    def transaction(self):
        """Transaction context manager"""
        with self.pool.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    
    # User Management
    def create_user(self, username: str, email: str = None, preferences: Dict = None, user_id: str = None) -> str:
        """Create a new user"""
        if user_id is None:
            user_id = str(uuid.uuid4())
        preferences = preferences or {}
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (id, username, email, preferences)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, email, json.dumps(preferences)))
        
        logger.info(f"Created user: {username} ({user_id})")
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user['preferences'] = json.loads(user['preferences'])
                user['security_settings'] = json.loads(user['security_settings'])
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            if row:
                user = dict(row)
                user['preferences'] = json.loads(user['preferences'])
                user['security_settings'] = json.loads(user['security_settings'])
                return user
        return None
    
    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET preferences = ? WHERE id = ?
            """, (json.dumps(preferences), user_id))
    
    def update_username(self, user_id: str, username: str):
        """Update user's username"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET username = ? WHERE id = ?
            """, (username, user_id))
        logger.info(f"Updated username for user {user_id} to: {username}")
    
    # Agent Management
    def create_agent(self, user_id: str, name: str, persona_type: str, 
                    description: str = None, capabilities: List = None,
                    config: Dict = None, personality_traits: Dict = None) -> str:
        """Create a new agent"""
        agent_id = str(uuid.uuid4())
        capabilities = capabilities or []
        config = config or {}
        personality_traits = personality_traits or {}
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agents (
                    id, user_id, name, persona_type, description,
                    capabilities, config, personality_traits
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_id, user_id, name, persona_type, description,
                json.dumps(capabilities), json.dumps(config),
                json.dumps(personality_traits)
            ))
        
        logger.info(f"Created agent: {name} ({agent_id}) for user {user_id}")
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent by ID"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM agents WHERE id = ?
            """, (agent_id,))
            
            row = cursor.fetchone()
            if row:
                agent = dict(row)
                agent['capabilities'] = json.loads(agent['capabilities'])
                agent['config'] = json.loads(agent['config'])
                agent['personality_traits'] = json.loads(agent['personality_traits'])
                return agent
        return None
    
    def get_user_agents(self, user_id: str, active_only: bool = True) -> List[Dict]:
        """Get all agents for a user"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM agents WHERE user_id = ?"
            params = [user_id]
            
            if active_only:
                query += " AND active = 1"
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            agents = []
            for row in cursor.fetchall():
                agent = dict(row)
                agent['capabilities'] = json.loads(agent['capabilities'])
                agent['config'] = json.loads(agent['config'])
                agent['personality_traits'] = json.loads(agent['personality_traits'])
                agents.append(agent)
        
        return agents
    
    def update_agent_activity(self, agent_id: str):
        """Update agent last activity timestamp"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agents SET 
                    last_activity = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (agent_id,))
    
    # Memory Management
    def store_memory(self, agent_id: str, user_id: str, slice_type: str,
                    content: str, importance: float = 0.5, confidence: float = 1.0,
                    tags: List[str] = None, metadata: Dict = None) -> str:
        """Store a memory slice"""
        memory_id = str(uuid.uuid4())
        tags = tags or []
        metadata = metadata or {}
        
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memory_slices (
                    id, agent_id, user_id, slice_type, content,
                    importance, confidence, tags, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory_id, agent_id, user_id, slice_type, content,
                importance, confidence, json.dumps(tags),
                json.dumps(metadata)
            ))
        
        logger.debug(f"Stored memory: {slice_type} for agent {agent_id}")
        return memory_id
    
    def search_memories(self, agent_id: str, user_id: str, query: str = None,
                       slice_type: str = None, min_importance: float = 0.0,
                       limit: int = 10, offset: int = 0) -> List[Dict]:
        """Search for memories with various filters"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = """
                SELECT id, content, slice_type, importance, confidence,
                       tags, metadata, created_at, accessed_at, access_count
                FROM memory_slices 
                WHERE agent_id = ? AND user_id = ? AND importance >= ?
            """
            params = [agent_id, user_id, min_importance]
            
            if query:
                sql += " AND content LIKE ?"
                params.append(f"%{query}%")
            
            if slice_type:
                sql += " AND slice_type = ?"
                params.append(slice_type)
            
            sql += " ORDER BY importance DESC, created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(sql, params)
            
            memories = []
            for row in cursor.fetchall():
                memory = dict(row)
                memory['tags'] = json.loads(memory['tags'])
                memory['metadata'] = json.loads(memory['metadata'])
                memories.append(memory)
        
        # Update access count for returned memories
        if memories:
            memory_ids = [m['id'] for m in memories]
            self._update_memory_access(memory_ids)
        
        return memories
    
    def _update_memory_access(self, memory_ids: List[str]):
        """Update memory access statistics"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            placeholders = ','.join(['?'] * len(memory_ids))
            cursor.execute(f"""
                UPDATE memory_slices SET 
                    accessed_at = CURRENT_TIMESTAMP,
                    access_count = access_count + 1
                WHERE id IN ({placeholders})
            """, memory_ids)
    
    def get_memory_stats(self, agent_id: str, user_id: str) -> Dict:
        """Get memory statistics for an agent"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_memories,
                    AVG(importance) as avg_importance,
                    AVG(confidence) as avg_confidence,
                    COUNT(DISTINCT slice_type) as memory_types,
                    MAX(created_at) as latest_memory
                FROM memory_slices 
                WHERE agent_id = ? AND user_id = ?
            """, (agent_id, user_id))
            
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    # Session Management
    def create_session(self, user_id: str, expires_in_hours: int = 24,
                      agent_context: Dict = None, metadata: Dict = None) -> Tuple[str, str]:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        session_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        agent_context = agent_context or {}
        metadata = metadata or {}
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (
                    id, user_id, session_token, agent_context,
                    expires_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id, user_id, session_token,
                json.dumps(agent_context), expires_at,
                json.dumps(metadata)
            ))
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id, session_token
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Get session by token"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions 
                WHERE session_token = ? AND active = 1 AND expires_at > CURRENT_TIMESTAMP
            """, (session_token,))
            
            row = cursor.fetchone()
            if row:
                session = dict(row)
                session['agent_context'] = json.loads(session['agent_context'])
                session['conversation_history'] = json.loads(session['conversation_history'])
                session['metadata'] = json.loads(session['metadata'])
                return session
        return None
    
    def update_session_activity(self, session_id: str, agent_context: Dict = None):
        """Update session last activity"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            if agent_context:
                cursor.execute("""
                    UPDATE sessions SET 
                        last_activity = CURRENT_TIMESTAMP,
                        agent_context = ?
                    WHERE id = ?
                """, (json.dumps(agent_context), session_id))
            else:
                cursor.execute("""
                    UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE id = ?
                """, (session_id,))
    
    # Conversation Management
    def store_conversation(self, session_id: str, agent_id: str, user_id: str,
                          message_type: str, content: str, role: str,
                          metadata: Dict = None, memory_references: List[str] = None,
                          processing_time: float = None, model_used: str = None) -> str:
        """Store a conversation message"""
        conv_id = str(uuid.uuid4())
        metadata = metadata or {}
        memory_references = memory_references or []
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (
                    id, session_id, agent_id, user_id, message_type,
                    content, role, metadata, memory_references
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conv_id, session_id, agent_id, user_id, message_type,
                content, role, json.dumps(metadata),
                json.dumps(memory_references)
            ))
        
        return conv_id
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE session_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (session_id, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conv = dict(row)
                conv['metadata'] = json.loads(conv['metadata'])
                conv['memory_references'] = json.loads(conv['memory_references'])
                conversations.append(conv)
            
            return conversations
    
    # Personality Management
    def update_personality_trait(self, agent_id: str, trait_name: str,
                                trait_value: float, trait_confidence: float = 1.0,
                                update_reason: str = None):
        """Update an agent's personality trait"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            
            # Get current value for history
            cursor.execute("""
                SELECT trait_value FROM alden_personality 
                WHERE agent_id = ? AND trait_name = ?
            """, (agent_id, trait_name))
            
            current = cursor.fetchone()
            previous_value = current[0] if current else None
            
            # Update or insert trait
            cursor.execute("""
                INSERT OR REPLACE INTO alden_personality (
                    id, agent_id, trait_name, trait_value, trait_confidence,
                    update_reason, previous_value
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()), agent_id, trait_name, trait_value,
                trait_confidence, update_reason, previous_value
            ))
    
    def get_personality_profile(self, agent_id: str) -> Dict:
        """Get complete personality profile for an agent"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT trait_name, trait_value, trait_confidence, last_updated
                FROM alden_personality 
                WHERE agent_id = ?
                ORDER BY trait_name
            """, (agent_id,))
            
            profile = {}
            for row in cursor.fetchall():
                profile[row['trait_name']] = {
                    'value': row['trait_value'],
                    'confidence': row['trait_confidence'],
                    'last_updated': row['last_updated']
                }
            
            return profile
    
    # Analytics
    def record_metric(self, agent_id: str, user_id: str, metric_name: str,
                     metric_value: float, metric_unit: str = None,
                     context: Dict = None, aggregation_period: str = 'instant'):
        """Record a cognitive analytics metric"""
        metric_id = str(uuid.uuid4())
        context = context or {}
        
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cognitive_analytics (
                    id, agent_id, user_id, metric_name, metric_value,
                    metric_unit, context, aggregation_period
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric_id, agent_id, user_id, metric_name, metric_value,
                metric_unit, json.dumps(context), aggregation_period
            ))
    
    def get_metrics(self, agent_id: str, metric_name: str = None,
                   hours_back: int = 24) -> List[Dict]:
        """Get metrics for analysis"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            sql = """
                SELECT * FROM cognitive_analytics 
                WHERE agent_id = ? AND measurement_timestamp > ?
            """
            params = [agent_id, cutoff_time]
            
            if metric_name:
                sql += " AND metric_name = ?"
                params.append(metric_name)
            
            sql += " ORDER BY measurement_timestamp DESC"
            
            cursor.execute(sql, params)
            
            metrics = []
            for row in cursor.fetchall():
                metric = dict(row)
                metric['context'] = json.loads(metric['context'])
                metrics.append(metric)
            
            return metrics
    
    # Database Maintenance
    def vacuum_database(self):
        """Optimize database by running VACUUM"""
        logger.info("Running database VACUUM...")
        with self.pool.get_connection() as conn:
            conn.execute("VACUUM")
        logger.info("Database VACUUM completed")
    
    def backup_database(self, backup_name: str = None) -> str:
        """Create a backup of the database"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"hearthlink_backup_{timestamp}.db"
        
        backup_path = Path(self.config.backup_path) / backup_name
        
        # SQLite backup using the backup API
        with sqlite3.connect(self.config.db_path) as source:
            with sqlite3.connect(str(backup_path)) as backup:
                source.backup(backup)
        
        logger.info(f"Database backed up to: {backup_path}")
        return str(backup_path)
    
    def get_database_stats(self) -> Dict:
        """Get general database statistics"""
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Table row counts
            tables = ['users', 'agents', 'memory_slices', 'sessions', 
                     'conversations', 'alden_personality', 'cognitive_analytics']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]
            
            # Database file size
            db_path = Path(self.config.db_path)
            if db_path.exists():
                stats['database_size_mb'] = round(db_path.stat().st_size / (1024 * 1024), 2)
            
            # Schema version
            stats['schema_version'] = self.get_schema_version()
            
            return stats

# Singleton instance
_db_manager = None

def get_database_manager(config: DatabaseConfig = None) -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(config)
        _db_manager.initialize_schema()
    return _db_manager

# Convenience functions
def initialize_database(config: DatabaseConfig = None):
    """Initialize the database with default configuration"""
    db_manager = get_database_manager(config)
    logger.info("Hearthlink SQLite database initialized successfully")
    return db_manager

if __name__ == "__main__":
    # Demo usage
    db = initialize_database()
    
    # Try to create a test user or get existing one
    try:
        user_id = db.create_user("demo_user", "demo@hearthlink.ai")
        print(f"Created new user: {user_id}")
    except sqlite3.IntegrityError:
        # User already exists, get their ID
        user = db.get_user_by_username("demo_user")
        user_id = user['id'] if user else None
        print(f"Using existing user: {user_id}")
    
    if user_id:
        # Get or create Alden agent
        agents = db.get_user_agents(user_id)
        alden_agent = next((a for a in agents if a['name'] == 'Alden'), None)
        
        if not alden_agent:
            agent_id = db.create_agent(
                user_id=user_id,
                name="Alden",
                persona_type="assistant",
                description="Primary AI assistant",
                capabilities=["conversation", "memory", "analysis"],
                personality_traits={"openness": 0.8, "conscientiousness": 0.9}
            )
            print(f"Created new agent: {agent_id}")
        else:
            agent_id = alden_agent['id']
            print(f"Using existing agent: {agent_id}")
        
        # Store a test memory
        memory_id = db.store_memory(
            agent_id=agent_id,
            user_id=user_id,
            slice_type="episodic",
            content="Database manager test run completed successfully",
            importance=0.8,
            tags=["test", "database", "success"]
        )
        print(f"Stored memory: {memory_id}")
        
        # Print stats
        print("\nDatabase Stats:", json.dumps(db.get_database_stats(), indent=2))
        
        # Test memory search
        memories = db.search_memories(agent_id, user_id, "test", limit=5)
        print(f"\nFound {len(memories)} test memories")
    else:
        print("Could not create or find demo user")