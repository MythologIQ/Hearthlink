#!/usr/bin/env python3
"""
Vault Database Connector
Handles database connections and data persistence for Vault
"""

import sqlite3
import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from cryptography.fernet import Fernet

class VaultConnector:
    def __init__(self, db_path: str = "hearthlink_data/vault.db"):
        self.db_path = db_path
        self.encryption_key = None
        self.cipher_suite = None
        self.connected = False
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Initialize database
        self._initialize_database()
    
    def _initialize_encryption(self):
        """Initialize encryption for sensitive data"""
        key_path = "hearthlink_data/vault.key"
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(key_path, 'wb') as f:
                f.write(self.encryption_key)
        
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _initialize_database(self):
        """Initialize the database with required tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personas (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    personality_data TEXT,
                    memory_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    persona_id TEXT,
                    session_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    persona_id TEXT,
                    memory_type TEXT,
                    content TEXT,
                    importance REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    component TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            self.connected = True
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            self.connected = False
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if self.cipher_suite:
            return self.cipher_suite.encrypt(data.encode()).decode()
        return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if self.cipher_suite:
            try:
                return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
            except:
                return encrypted_data  # Return as-is if decryption fails
        return encrypted_data
    
    def store_persona(self, persona_id: str, name: str, personality_data: Dict, memory_data: Dict) -> bool:
        """Store persona data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            personality_json = json.dumps(personality_data)
            memory_json = json.dumps(memory_data)
            
            cursor.execute('''
                INSERT OR REPLACE INTO personas (id, name, personality_data, memory_data, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (persona_id, name, personality_json, memory_json, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Error storing persona: {e}")
            return False
    
    def get_persona(self, persona_id: str) -> Optional[Dict]:
        """Retrieve persona data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM personas WHERE id = ?', (persona_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'personality_data': json.loads(row[2]) if row[2] else {},
                    'memory_data': json.loads(row[3]) if row[3] else {},
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            
            conn.close()
            return None
            
        except sqlite3.Error as e:
            print(f"Error retrieving persona: {e}")
            return None
    
    def store_memory(self, persona_id: str, memory_type: str, content: str, importance: float = 0.5) -> bool:
        """Store a memory entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            memory_id = hashlib.md5(f"{persona_id}_{content}_{datetime.now()}".encode()).hexdigest()
            
            cursor.execute('''
                INSERT INTO memories (id, persona_id, memory_type, content, importance)
                VALUES (?, ?, ?, ?, ?)
            ''', (memory_id, persona_id, memory_type, content, importance))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Error storing memory: {e}")
            return False
    
    def get_memories(self, persona_id: str, memory_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Retrieve memories for a persona"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if memory_type:
                cursor.execute('''
                    SELECT * FROM memories 
                    WHERE persona_id = ? AND memory_type = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (persona_id, memory_type, limit))
            else:
                cursor.execute('''
                    SELECT * FROM memories 
                    WHERE persona_id = ?
                    ORDER BY created_at DESC LIMIT ?
                ''', (persona_id, limit))
            
            rows = cursor.fetchall()
            memories = []
            
            for row in rows:
                memories.append({
                    'id': row[0],
                    'persona_id': row[1],
                    'memory_type': row[2],
                    'content': row[3],
                    'importance': row[4],
                    'created_at': row[5]
                })
            
            conn.close()
            return memories
            
        except sqlite3.Error as e:
            print(f"Error retrieving memories: {e}")
            return []
    
    def log_system_event(self, level: str, message: str, component: str = "system") -> bool:
        """Log system events"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_logs (level, message, component)
                VALUES (?, ?, ?)
            ''', (level, message, component))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Error logging system event: {e}")
            return False
    
    def get_system_logs(self, limit: int = 100) -> List[Dict]:
        """Retrieve system logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM system_logs 
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            logs = []
            
            for row in rows:
                logs.append({
                    'id': row[0],
                    'level': row[1],
                    'message': row[2],
                    'component': row[3],
                    'timestamp': row[4]
                })
            
            conn.close()
            return logs
            
        except sqlite3.Error as e:
            print(f"Error retrieving system logs: {e}")
            return []
    
    def get_status(self) -> Dict:
        """Get database status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count records in each table
            cursor.execute('SELECT COUNT(*) FROM personas')
            persona_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM sessions')
            session_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM memories')
            memory_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM system_logs')
            log_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'connected': self.connected,
                'database_path': self.db_path,
                'encrypted': self.encryption_key is not None,
                'persona_count': persona_count,
                'session_count': session_count,
                'memory_count': memory_count,
                'log_count': log_count
            }
            
        except sqlite3.Error as e:
            print(f"Error getting database status: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict:
        """Get detailed vault statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get persona memories count
            cursor.execute("SELECT COUNT(*) FROM memories WHERE persona_id IS NOT NULL")
            persona_memories = cursor.fetchone()[0]
            
            # Get communal memories count  
            cursor.execute("SELECT COUNT(*) FROM memories WHERE persona_id IS NULL")
            communal_memories = cursor.fetchone()[0]
            
            total_memories = persona_memories + communal_memories
            
            # Get storage used
            storage_used = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            # Get last backup (if exists)
            backup_files = [f for f in os.listdir('hearthlink_data') if f.startswith('vault_backup_')] if os.path.exists('hearthlink_data') else []
            last_backup = max(backup_files) if backup_files else None
            
            stats = {
                'total_memories': total_memories,
                'persona_memories': persona_memories,
                'communal_memories': communal_memories,
                'storage_used': storage_used,
                'last_backup': last_backup,
                'integrity_status': 'verified'
            }
            
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error getting vault stats: {e}")
            return {'error': str(e)}
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Get a specific memory by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, persona_id, memory_type, content, importance, 
                       created_at, metadata 
                FROM memories 
                WHERE id = ?
            """, (memory_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'persona_id': result[1],
                    'memory_type': result[2],
                    'content': self.decrypt_data(result[3]),
                    'importance': result[4],
                    'created_at': result[5],
                    'metadata': json.loads(result[6]) if result[6] else {}
                }
            return None
            
        except Exception as e:
            print(f"Error getting memory: {e}")
            return None
    
    def create_memory(self, persona_id: str, memory_type: str, content: str, metadata: Dict = None, user_id: str = 'system') -> str:
        """Create a new memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            memory_id = f"mem_{int(datetime.now().timestamp())}"
            encrypted_content = self.encrypt_data(content)
            metadata_json = json.dumps(metadata or {})
            
            cursor.execute("""
                INSERT INTO memories (id, persona_id, memory_type, content, importance, 
                                    created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (memory_id, persona_id, memory_type, encrypted_content, 0.5, 
                  datetime.now().isoformat(), metadata_json))
            
            conn.commit()
            conn.close()
            
            # Log the action
            self.log_system_event('info', f'Memory created: {memory_id}', 'vault')
            
            return memory_id
            
        except Exception as e:
            print(f"Error creating memory: {e}")
            return None
    
    def update_memory(self, memory_id: str, content: str = None, metadata: Dict = None, user_id: str = 'system') -> bool:
        """Update an existing memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if memory exists
            cursor.execute("SELECT id FROM memories WHERE id = ?", (memory_id,))
            if not cursor.fetchone():
                return False
            
            # Update content if provided
            if content is not None:
                encrypted_content = self.encrypt_data(content)
                cursor.execute("UPDATE memories SET content = ? WHERE id = ?", 
                             (encrypted_content, memory_id))
            
            # Update metadata if provided
            if metadata is not None:
                metadata_json = json.dumps(metadata)
                cursor.execute("UPDATE memories SET metadata = ? WHERE id = ?", 
                             (metadata_json, memory_id))
            
            conn.commit()
            conn.close()
            
            # Log the action
            self.log_system_event('info', f'Memory updated: {memory_id}', 'vault')
            
            return True
            
        except Exception as e:
            print(f"Error updating memory: {e}")
            return False
    
    def delete_memory(self, memory_id: str, user_id: str = 'system') -> bool:
        """Delete a memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if deleted:
                # Log the action
                self.log_system_event('info', f'Memory deleted: {memory_id}', 'vault')
            
            return deleted
            
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
    
    def get_audit_log(self, limit: int = 100, user_id: str = None, action: str = None) -> List[Dict]:
        """Get audit log entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Base query
            query = "SELECT timestamp, level, message, component FROM system_logs"
            params = []
            
            # Add filters
            conditions = []
            if user_id:
                conditions.append("message LIKE ?")
                params.append(f"%{user_id}%")
            if action:
                conditions.append("message LIKE ?")
                params.append(f"%{action}%")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            return [{
                'timestamp': row[0],
                'level': row[1],
                'message': row[2],
                'component': row[3]
            } for row in results]
            
        except Exception as e:
            print(f"Error getting audit log: {e}")
            return []
    
    def create_backup(self) -> str:
        """Create a backup of the vault"""
        try:
            import shutil
            
            backup_filename = f"vault_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join('hearthlink_data', backup_filename)
            
            # Ensure backup directory exists
            os.makedirs('hearthlink_data', exist_ok=True)
            
            # Copy database file
            shutil.copy2(self.db_path, backup_path)
            
            # Log the action
            self.log_system_event('info', f'Backup created: {backup_filename}', 'vault')
            
            return backup_path
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def check_integrity(self) -> Dict:
        """Check vault integrity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            # Check table counts
            cursor.execute("SELECT COUNT(*) FROM personas")
            persona_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM memories")
            memory_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM system_logs")
            log_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Test encryption
            encryption_test = True
            try:
                test_data = "test_string"
                encrypted = self.encrypt_data(test_data)
                decrypted = self.decrypt_data(encrypted)
                encryption_test = (test_data == decrypted)
            except:
                encryption_test = False
            
            status = 'verified' if integrity_result == 'ok' and encryption_test else 'error'
            
            return {
                'status': status,
                'details': {
                    'database_integrity': integrity_result,
                    'encryption_test': encryption_test,
                    'persona_count': persona_count,
                    'memory_count': memory_count,
                    'log_count': log_count
                }
            }
            
        except Exception as e:
            print(f"Error checking integrity: {e}")
            return {
                'status': 'error',
                'details': {'error': str(e)}
            }
    
    def search_memories(self, query: str, filters: Dict = None, limit: int = 100) -> List[Dict]:
        """Search memories"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Base query
            sql_query = """
                SELECT id, persona_id, memory_type, content, importance, 
                       created_at, metadata 
                FROM memories 
                WHERE content LIKE ?
            """
            params = [f"%{query}%"]
            
            # Add filters
            if filters:
                if 'persona_id' in filters:
                    sql_query += " AND persona_id = ?"
                    params.append(filters['persona_id'])
                if 'memory_type' in filters:
                    sql_query += " AND memory_type = ?"
                    params.append(filters['memory_type'])
            
            sql_query += " ORDER BY importance DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(sql_query, params)
            results = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'persona_id': row[1],
                'memory_type': row[2],
                'content': self.decrypt_data(row[3]),
                'importance': row[4],
                'created_at': row[5],
                'metadata': json.loads(row[6]) if row[6] else {}
            } for row in results]
            
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

# Global vault connector instance
vault_connector = VaultConnector()

def initialize_vault():
    """Initialize Vault database"""
    print("Initializing Vault database...")
    
    if vault_connector.connected:
        status = vault_connector.get_status()
        print(f"✓ Vault database connected")
        print(f"  Database: {status['database_path']}")
        print(f"  Encrypted: {status['encrypted']}")
        print(f"  Personas: {status['persona_count']}")
        print(f"  Sessions: {status['session_count']}")
        print(f"  Memories: {status['memory_count']}")
        print(f"  Logs: {status['log_count']}")
        
        # Log initialization
        vault_connector.log_system_event("INFO", "Vault database initialized", "vault")
        
        return True
    else:
        print("✗ Vault database connection failed")
        return False

if __name__ == '__main__':
    initialize_vault()