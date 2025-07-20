"""
Alden Backend with LLM Integration, RAG, CAG, and Memory Systems
Enhanced with Neo4j Knowledge Graphing and Secure Database Connectivity
"""

import json
import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

# Database and LLM imports
import asyncpg
import neo4j
import redis
import ollama
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import spacy

# Security imports
import bcrypt
import jwt
from cryptography.fernet import Fernet

# Web framework
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configurations
def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from JSON file with error handling"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', config_file)
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file {config_file} not found")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file {config_file}")
        return {}

DB_CONFIG = load_config('database_config.json')
LLM_CONFIG = load_config('llm_config.json')

@dataclass
class MemorySlice:
    """Represents a memory slice with metadata"""
    id: str
    content: str
    slice_type: str  # episodic, semantic, procedural
    timestamp: datetime
    importance: float
    context: Dict[str, Any]
    embeddings: Optional[List[float]] = None
    relationships: Optional[List[str]] = None

@dataclass
class ConversationContext:
    """Maintains conversation context with memory integration"""
    session_id: str
    user_id: str
    conversation_history: List[Dict[str, Any]]
    active_memory_slices: List[MemorySlice]
    context_embeddings: Optional[List[float]] = None
    last_updated: datetime = datetime.now()

class DatabaseManager:
    """Manages all database connections and operations"""
    
    def __init__(self):
        self.neo4j_driver = None
        self.postgres_pool = None
        self.redis_client = None
        self.qdrant_client = None
        self.cipher_suite = None
        
    async def initialize(self):
        """Initialize all database connections"""
        try:
            # Neo4j for knowledge graphs
            if DB_CONFIG.get('neo4j'):
                neo4j_config = DB_CONFIG['neo4j']
                self.neo4j_driver = neo4j.AsyncGraphDatabase.driver(
                    neo4j_config['uri'],
                    auth=(neo4j_config['user'], neo4j_config['password'])
                )
                logger.info("Neo4j connection established")
            
            # PostgreSQL for structured data
            if DB_CONFIG.get('postgresql'):
                pg_config = DB_CONFIG['postgresql']
                self.postgres_pool = await asyncpg.create_pool(
                    host=pg_config['host'],
                    port=pg_config['port'],
                    database=pg_config['database'],
                    user=pg_config['user'],
                    password=pg_config['password'],
                    max_size=pg_config['max_connections']
                )
                logger.info("PostgreSQL connection pool established")
            
            # Redis for caching and sessions
            if DB_CONFIG.get('redis'):
                redis_config = DB_CONFIG['redis']
                self.redis_client = redis.Redis(
                    host=redis_config['host'],
                    port=redis_config['port'],
                    password=redis_config['password'],
                    db=redis_config['db']
                )
                logger.info("Redis connection established")
            
            # Qdrant for vector storage
            if DB_CONFIG.get('vector_database'):
                vector_config = DB_CONFIG['vector_database']
                self.qdrant_client = QdrantClient(
                    host=vector_config['host'],
                    port=vector_config['port'],
                    api_key=vector_config.get('api_key')
                )
                logger.info("Qdrant connection established")
            
            # Initialize encryption
            if DB_CONFIG.get('security', {}).get('encryption_key'):
                key = DB_CONFIG['security']['encryption_key'].encode()
                self.cipher_suite = Fernet(key)
                logger.info("Encryption initialized")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def close(self):
        """Close all database connections"""
        if self.neo4j_driver:
            await self.neo4j_driver.close()
        if self.postgres_pool:
            await self.postgres_pool.close()
        if self.redis_client:
            await self.redis_client.close()

class LLMManager:
    """Manages LLM interactions with RAG and CAG capabilities"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_model = None
        self.nlp = None
        
    async def initialize(self):
        """Initialize LLM components"""
        try:
            # Load embedding model
            if LLM_CONFIG.get('embedding_model'):
                embedding_config = LLM_CONFIG['embedding_model']
                self.embedding_model = SentenceTransformer(
                    embedding_config['model']
                )
                logger.info("Embedding model loaded")
            
            # Load NLP model for entity extraction
            if LLM_CONFIG.get('knowledge_graph', {}).get('entity_extraction'):
                entity_config = LLM_CONFIG['knowledge_graph']['entity_extraction']
                self.nlp = spacy.load(entity_config['model'])
                logger.info("NLP model loaded")
                
        except Exception as e:
            logger.error(f"LLM initialization failed: {e}")
            raise

    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        try:
            if self.embedding_model:
                embeddings = self.embedding_model.encode(text)
                return embeddings.tolist()
            return []
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    async def rag_query(self, query: str, context: ConversationContext) -> Tuple[str, List[MemorySlice]]:
        """Perform RAG query with memory integration"""
        try:
            # Generate query embeddings
            query_embeddings = await self.generate_embeddings(query)
            
            # Retrieve relevant memory slices
            relevant_slices = await self.retrieve_relevant_memories(
                query_embeddings, context
            )
            
            # Build context for LLM
            context_text = self.build_context_text(relevant_slices, context)
            
            # Generate response with Ollama
            response = await self.generate_llm_response(query, context_text)
            
            return response, relevant_slices
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return "I'm experiencing technical difficulties. Please try again.", []

    async def retrieve_relevant_memories(self, 
                                       query_embeddings: List[float], 
                                       context: ConversationContext) -> List[MemorySlice]:
        """Retrieve relevant memory slices using vector similarity"""
        try:
            if not self.db_manager.qdrant_client or not query_embeddings:
                return []
            
            # Search vector database
            rag_config = LLM_CONFIG.get('rag_config', {})
            search_result = self.db_manager.qdrant_client.search(
                collection_name=DB_CONFIG['vector_database']['collection_name'],
                query_vector=query_embeddings,
                limit=rag_config.get('max_retrieved_chunks', 5),
                score_threshold=rag_config.get('similarity_threshold', 0.7)
            )
            
            # Convert to memory slices
            memory_slices = []
            for result in search_result:
                memory_slice = MemorySlice(
                    id=result.id,
                    content=result.payload.get('content', ''),
                    slice_type=result.payload.get('slice_type', 'semantic'),
                    timestamp=datetime.fromisoformat(result.payload.get('timestamp', datetime.now().isoformat())),
                    importance=result.score,
                    context=result.payload.get('context', {}),
                    embeddings=query_embeddings
                )
                memory_slices.append(memory_slice)
            
            return memory_slices
            
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return []

    def build_context_text(self, memory_slices: List[MemorySlice], context: ConversationContext) -> str:
        """Build context text from memory slices and conversation history"""
        context_parts = []
        
        # Add relevant memory slices
        if memory_slices:
            context_parts.append("=== RELEVANT MEMORY SLICES ===")
            for slice in memory_slices:
                context_parts.append(f"[{slice.slice_type.upper()}] {slice.content}")
        
        # Add recent conversation history
        if context.conversation_history:
            context_parts.append("=== RECENT CONVERSATION ===")
            for msg in context.conversation_history[-5:]:  # Last 5 messages
                context_parts.append(f"{msg['role']}: {msg['content']}")
        
        return "\n".join(context_parts)

    async def generate_llm_response(self, query: str, context_text: str) -> str:
        """Generate LLM response using Ollama"""
        try:
            llm_config = LLM_CONFIG.get('local_llm', {})
            
            # Build prompt with context
            prompt = f"""You are Alden, an advanced AI assistant with persistent memory and knowledge graphs.
            
Context Information:
{context_text}

Current Query: {query}

Please provide a helpful, contextual response based on your memory and the current query. 
Be concise but thorough, and reference relevant context when appropriate."""

            # Call Ollama
            response = ollama.generate(
                model=llm_config.get('model', 'llama3.2:latest'),
                prompt=prompt,
                options={
                    'temperature': llm_config.get('temperature', 0.7),
                    'top_p': llm_config.get('top_p', 0.9),
                    'num_predict': llm_config.get('max_tokens', 4096)
                }
            )
            
            return response['response']
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return "I'm having trouble generating a response. Please check my LLM configuration."

    async def store_memory_slice(self, memory_slice: MemorySlice):
        """Store memory slice in vector database and Neo4j"""
        try:
            # Store in vector database
            if self.db_manager.qdrant_client and memory_slice.embeddings:
                point = PointStruct(
                    id=memory_slice.id,
                    vector=memory_slice.embeddings,
                    payload={
                        'content': memory_slice.content,
                        'slice_type': memory_slice.slice_type,
                        'timestamp': memory_slice.timestamp.isoformat(),
                        'importance': memory_slice.importance,
                        'context': memory_slice.context
                    }
                )
                
                self.db_manager.qdrant_client.upsert(
                    collection_name=DB_CONFIG['vector_database']['collection_name'],
                    points=[point]
                )
            
            # Store in Neo4j knowledge graph
            if self.db_manager.neo4j_driver:
                await self.store_in_knowledge_graph(memory_slice)
                
        except Exception as e:
            logger.error(f"Memory storage failed: {e}")

    async def store_in_knowledge_graph(self, memory_slice: MemorySlice):
        """Store memory slice in Neo4j knowledge graph"""
        try:
            async with self.db_manager.neo4j_driver.session() as session:
                # Create memory node
                await session.run(
                    """
                    MERGE (m:MemorySlice {id: $id})
                    SET m.content = $content,
                        m.slice_type = $slice_type,
                        m.timestamp = $timestamp,
                        m.importance = $importance
                    """,
                    id=memory_slice.id,
                    content=memory_slice.content,
                    slice_type=memory_slice.slice_type,
                    timestamp=memory_slice.timestamp.isoformat(),
                    importance=memory_slice.importance
                )
                
                # Extract and store entities
                if self.nlp:
                    entities = self.extract_entities(memory_slice.content)
                    for entity in entities:
                        await session.run(
                            """
                            MERGE (e:Entity {name: $name, type: $type})
                            MERGE (m:MemorySlice {id: $memory_id})
                            MERGE (m)-[:CONTAINS]->(e)
                            """,
                            name=entity['text'],
                            type=entity['label'],
                            memory_id=memory_slice.id
                        )
                
        except Exception as e:
            logger.error(f"Knowledge graph storage failed: {e}")

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extract entities from text using spaCy"""
        try:
            doc = self.nlp(text)
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            return entities
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []

class AldenBackend:
    """Main Alden backend with integrated AI capabilities"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm_manager = LLMManager(self.db_manager)
        self.contexts: Dict[str, ConversationContext] = {}
        
    async def initialize(self):
        """Initialize all components"""
        await self.db_manager.initialize()
        await self.llm_manager.initialize()
        logger.info("Alden backend initialized successfully")

    async def process_query(self, query: str, session_id: str, user_id: str = "default") -> Dict[str, Any]:
        """Process user query with full AI capabilities"""
        try:
            # Get or create context
            context = self.get_or_create_context(session_id, user_id)
            
            # Add query to conversation history
            context.conversation_history.append({
                'role': 'user',
                'content': query,
                'timestamp': datetime.now().isoformat()
            })
            
            # Generate response with RAG
            response, relevant_memories = await self.llm_manager.rag_query(query, context)
            
            # Add response to conversation history
            context.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Create and store memory slice
            memory_slice = MemorySlice(
                id=f"mem_{datetime.now().timestamp()}",
                content=f"Q: {query}\nA: {response}",
                slice_type="episodic",
                timestamp=datetime.now(),
                importance=0.7,
                context={'session_id': session_id, 'user_id': user_id}
            )
            
            # Generate embeddings for memory slice
            memory_slice.embeddings = await self.llm_manager.generate_embeddings(memory_slice.content)
            
            # Store memory slice
            await self.llm_manager.store_memory_slice(memory_slice)
            
            return {
                'response': response,
                'session_id': session_id,
                'relevant_memories': [asdict(mem) for mem in relevant_memories],
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                'response': "I'm experiencing technical difficulties. Please try again.",
                'session_id': session_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }

    def get_or_create_context(self, session_id: str, user_id: str) -> ConversationContext:
        """Get existing context or create new one"""
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                conversation_history=[],
                active_memory_slices=[]
            )
        return self.contexts[session_id]

# FastAPI application
app = FastAPI(title="Alden Backend", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global backend instance
alden_backend = AldenBackend()

@app.on_event("startup")
async def startup_event():
    """Initialize backend on startup"""
    await alden_backend.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await alden_backend.db_manager.close()

# API Models
class QueryRequest(BaseModel):
    query: str
    session_id: str
    user_id: str = "default"

class QueryResponse(BaseModel):
    response: str
    session_id: str
    relevant_memories: List[Dict[str, Any]]
    timestamp: str
    status: str

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query with AI capabilities"""
    result = await alden_backend.process_query(
        request.query, 
        request.session_id, 
        request.user_id
    )
    return QueryResponse(**result)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/status")
async def get_status():
    """Get backend status"""
    return {
        "llm_available": LLM_CONFIG.get('local_llm') is not None,
        "database_available": DB_CONFIG.get('postgresql') is not None,
        "vector_db_available": DB_CONFIG.get('vector_database') is not None,
        "knowledge_graph_available": DB_CONFIG.get('neo4j') is not None,
        "active_sessions": len(alden_backend.contexts),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)