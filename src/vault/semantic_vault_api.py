#!/usr/bin/env python3
"""
Semantic Vault API - Extension for Semantic Memory Retrieval
Adds semantic and hybrid search endpoints to the existing Vault service
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from embedding.semantic_embedding_service import SemanticMemoryManager, SemanticEmbeddingService
from database.pgvector_client import PGVectorClient
from log_handling.agent_token_tracker import log_agent_token_usage

logger = logging.getLogger(__name__)

# Request/Response Models
class SemanticRetrieveRequest(BaseModel):
    """Request model for semantic memory retrieval."""
    query: str
    persona_id: str
    user_id: str
    agent_id: str
    memory_types: Optional[List[str]] = None
    limit: int = 10
    min_similarity: float = 0.7
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    @validator('persona_id')
    def persona_id_must_be_valid(cls, v):
        valid_personas = ['alden', 'alice', 'mimic', 'sentry', 'core']
        if v not in valid_personas:
            raise ValueError(f'Invalid persona ID: {v}. Must be one of: {", ".join(valid_personas)}')
        return v
    
    @validator('agent_id')
    def agent_id_must_be_valid(cls, v):
        valid_agents = ['claude', 'alden', 'mimic', 'alice', 'sentry', 'core', 'user']
        if v not in valid_agents:
            raise ValueError(f'Invalid agent ID: {v}. Must be one of: {", ".join(valid_agents)}')
        return v
    
    @validator('limit')
    def limit_must_be_reasonable(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v
    
    @validator('min_similarity')
    def similarity_must_be_valid(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Minimum similarity must be between 0.0 and 1.0')
        return v

class HybridRetrieveRequest(BaseModel):
    """Request model for hybrid memory retrieval."""
    query: str
    keywords: List[str]
    persona_id: str
    user_id: str
    agent_id: str
    memory_types: Optional[List[str]] = None
    limit: int = 10
    keyword_weight: float = 0.3
    semantic_weight: float = 0.7
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    @validator('keywords')
    def keywords_must_not_be_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Keywords list cannot be empty')
        return [kw.strip() for kw in v if kw.strip()]
    
    @validator('keyword_weight', 'semantic_weight')
    def weights_must_be_valid(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Weights must be between 0.0 and 1.0')
        return v

class StoreMemoryRequest(BaseModel):
    """Request model for storing memory with embedding."""
    slice_id: str
    persona_id: str
    user_id: str
    agent_id: str
    content: str
    memory_type: str
    keywords: List[str]
    relevance_score: float = 0.5
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('slice_id')
    def slice_id_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Slice ID cannot be empty')
        # Check format: slice_[hex]
        if not v.startswith('slice_') or len(v) < 8:
            raise ValueError('Slice ID must follow format: slice_[identifier]')
        return v.strip()
    
    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()
    
    @validator('memory_type')
    def memory_type_must_be_valid(cls, v):
        valid_types = ['episodic', 'semantic', 'procedural', 'working']
        if v not in valid_types:
            raise ValueError(f'Invalid memory type: {v}. Must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('relevance_score')
    def relevance_score_must_be_valid(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Relevance score must be between 0.0 and 1.0')
        return v

class SemanticVaultAPI:
    """
    Semantic Vault API service that extends the base Vault with semantic memory capabilities.
    
    Provides endpoints for:
    - Semantic memory retrieval using vector embeddings
    - Hybrid retrieval combining keywords and semantics
    - Memory storage with automatic embedding generation
    - Memory statistics and health checks
    """
    
    def __init__(self, auth_tokens: List[str], config: Dict[str, Any] = None):
        """
        Initialize semantic vault API
        
        Args:
            auth_tokens: List of valid authorization tokens
            config: Configuration dictionary
        """
        self.auth_tokens = set(auth_tokens)
        self.config = config or {}
        
        # Initialize semantic memory manager
        self.memory_manager: Optional[SemanticMemoryManager] = None
        self.initialized = False
        
        # Create FastAPI app
        self.app = self._create_app()
        
        logger.info("Semantic Vault API initialized", extra={
            'auth_tokens_count': len(self.auth_tokens),
            'config_keys': list(self.config.keys())
        })
    
    async def initialize(self) -> bool:
        """Initialize the semantic memory manager"""
        try:
            if self.memory_manager is None:
                # Create components with environment configuration
                embedding_service = SemanticEmbeddingService(
                    model_name=os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
                    device='auto',
                    logger=logger
                )
                
                pgvector_client = PGVectorClient(logger=logger)
                
                self.memory_manager = SemanticMemoryManager(
                    embedding_service=embedding_service,
                    pgvector_client=pgvector_client,
                    logger=logger
                )
            
            # Initialize the manager
            success = await self.memory_manager.initialize()
            self.initialized = success
            
            if success:
                logger.info("Semantic memory manager initialized successfully")
            else:
                logger.error("Failed to initialize semantic memory manager")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize semantic vault API: {e}")
            self.initialized = False
            return False
    
    def _create_app(self) -> FastAPI:
        """Create FastAPI application with semantic memory endpoints"""
        app = FastAPI(
            title="Hearthlink Semantic Vault API",
            description="Semantic memory retrieval and storage for Hearthlink",
            version="1.0.0"
        )
        
        # Security
        security = HTTPBearer()
        
        async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
            """Verify authorization token"""
            if credentials.credentials not in self.auth_tokens:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authorization token"
                )
            return credentials.credentials
        
        async def ensure_initialized():
            """Ensure the semantic memory manager is initialized"""
            if not self.initialized:
                initialized = await self.initialize()
                if not initialized:
                    raise HTTPException(
                        status_code=503,
                        detail="Semantic memory system not available"
                    )
        
        @app.get("/api/semantic/health")
        async def semantic_health():
            """Health check for semantic memory system"""
            try:
                if not self.initialized:
                    return {
                        "status": "uninitialized",
                        "timestamp": datetime.now().isoformat(),
                        "error": "Semantic memory manager not initialized"
                    }
                
                # Get comprehensive statistics
                stats = await self.memory_manager.get_comprehensive_statistics()
                
                return {
                    "status": "healthy" if stats.get("database_health", {}).get("status") == "healthy" else "degraded",
                    "timestamp": datetime.now().isoformat(),
                    "statistics": stats
                }
                
            except Exception as e:
                logger.error(f"Semantic health check failed: {e}")
                return {
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e)
                }
        
        @app.post("/api/semantic/retrieve")
        async def semantic_retrieve(
            request: SemanticRetrieveRequest,
            token: str = Depends(verify_token),
            background_tasks: BackgroundTasks = BackgroundTasks()
        ):
            """
            Perform semantic memory retrieval using vector similarity
            
            Returns memories most semantically similar to the query text.
            """
            await ensure_initialized()
            
            start_time = time.time()
            
            try:
                # Log agent token usage
                background_tasks.add_task(
                    log_agent_token_usage,
                    request.agent_id,
                    "semantic_retrieve",
                    {
                        "query_length": len(request.query),
                        "persona_id": request.persona_id,
                        "limit": request.limit
                    }
                )
                
                # Perform semantic retrieval
                memories = await self.memory_manager.semantic_retrieve(
                    query_text=request.query,
                    persona_id=request.persona_id,
                    user_id=request.user_id,
                    memory_types=request.memory_types,
                    limit=request.limit,
                    min_similarity=request.min_similarity
                )
                
                query_time = int((time.time() - start_time) * 1000)
                
                # Format response
                response = {
                    "status": "success",
                    "query": request.query,
                    "results_count": len(memories),
                    "query_time_ms": query_time,
                    "min_similarity": request.min_similarity,
                    "memories": [
                        {
                            "slice_id": memory.slice_id,
                            "content": memory.content,
                            "memory_type": memory.memory_type,
                            "keywords": memory.keywords,
                            "relevance_score": memory.relevance_score,
                            "created_at": memory.created_at,
                            "last_accessed": memory.last_accessed,
                            "retrieval_count": memory.retrieval_count,
                            "metadata": memory.metadata
                        }
                        for memory in memories
                    ],
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Semantic retrieve completed: {len(memories)} results in {query_time}ms", extra={
                    'agent_id': request.agent_id,
                    'persona_id': request.persona_id,
                    'query_length': len(request.query),
                    'results_count': len(memories)
                })
                
                return response
                
            except Exception as e:
                logger.error(f"Semantic retrieve failed: {e}", extra={
                    'agent_id': request.agent_id,
                    'persona_id': request.persona_id,
                    'query': request.query[:100],  # First 100 chars for logging
                    'error': str(e)
                })
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Semantic retrieval failed: {str(e)}"
                )
        
        @app.post("/api/semantic/hybrid")
        async def hybrid_retrieve(
            request: HybridRetrieveRequest,
            token: str = Depends(verify_token),
            background_tasks: BackgroundTasks = BackgroundTasks()
        ):
            """
            Perform hybrid memory retrieval combining keyword matching and semantic similarity
            
            Combines traditional keyword matching with vector similarity for more robust retrieval.
            """
            await ensure_initialized()
            
            start_time = time.time()
            
            try:
                # Log agent token usage
                background_tasks.add_task(
                    log_agent_token_usage,
                    request.agent_id,
                    "hybrid_retrieve",
                    {
                        "query_length": len(request.query),
                        "keywords_count": len(request.keywords),
                        "persona_id": request.persona_id,
                        "limit": request.limit
                    }
                )
                
                # Perform hybrid retrieval
                memories = await self.memory_manager.hybrid_retrieve(
                    query_text=request.query,
                    query_keywords=request.keywords,
                    persona_id=request.persona_id,
                    user_id=request.user_id,
                    memory_types=request.memory_types,
                    limit=request.limit,
                    keyword_weight=request.keyword_weight,
                    semantic_weight=request.semantic_weight
                )
                
                query_time = int((time.time() - start_time) * 1000)
                
                # Format response
                response = {
                    "status": "success",
                    "query": request.query,
                    "keywords": request.keywords,
                    "results_count": len(memories),
                    "query_time_ms": query_time,
                    "keyword_weight": request.keyword_weight,
                    "semantic_weight": request.semantic_weight,
                    "memories": [
                        {
                            "slice_id": memory.slice_id,
                            "content": memory.content,
                            "memory_type": memory.memory_type,
                            "keywords": memory.keywords,
                            "relevance_score": memory.relevance_score,
                            "created_at": memory.created_at,
                            "last_accessed": memory.last_accessed,
                            "retrieval_count": memory.retrieval_count,
                            "metadata": memory.metadata
                        }
                        for memory in memories
                    ],
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info(f"Hybrid retrieve completed: {len(memories)} results in {query_time}ms", extra={
                    'agent_id': request.agent_id,
                    'persona_id': request.persona_id,
                    'query_length': len(request.query),
                    'keywords_count': len(request.keywords),
                    'results_count': len(memories)
                })
                
                return response
                
            except Exception as e:
                logger.error(f"Hybrid retrieve failed: {e}", extra={
                    'agent_id': request.agent_id,
                    'persona_id': request.persona_id,
                    'query': request.query[:100],
                    'keywords': request.keywords[:10],  # First 10 keywords
                    'error': str(e)
                })
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Hybrid retrieval failed: {str(e)}"
                )
        
        @app.post("/api/semantic/store")
        async def store_memory(
            request: StoreMemoryRequest,
            token: str = Depends(verify_token),
            background_tasks: BackgroundTasks = BackgroundTasks()
        ):
            """
            Store memory with automatic embedding generation
            
            Generates vector embeddings for the content and stores in semantic memory.
            """
            await ensure_initialized()
            
            start_time = time.time()
            
            try:
                # Log agent token usage
                background_tasks.add_task(
                    log_agent_token_usage,
                    request.agent_id,
                    "store_memory",
                    {
                        "content_length": len(request.content),
                        "memory_type": request.memory_type,
                        "keywords_count": len(request.keywords),
                        "persona_id": request.persona_id
                    }
                )
                
                # Store memory with embedding
                success = await self.memory_manager.store_memory_with_embedding(
                    slice_id=request.slice_id,
                    persona_id=request.persona_id,
                    user_id=request.user_id,
                    content=request.content,
                    memory_type=request.memory_type,
                    keywords=request.keywords,
                    relevance_score=request.relevance_score,
                    metadata=request.metadata
                )
                
                store_time = int((time.time() - start_time) * 1000)
                
                if success:
                    response = {
                        "status": "success",
                        "slice_id": request.slice_id,
                        "content_length": len(request.content),
                        "memory_type": request.memory_type,
                        "keywords_count": len(request.keywords),
                        "store_time_ms": store_time,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    logger.info(f"Memory stored successfully: {request.slice_id} in {store_time}ms", extra={
                        'agent_id': request.agent_id,
                        'persona_id': request.persona_id,
                        'slice_id': request.slice_id,
                        'memory_type': request.memory_type,
                        'content_length': len(request.content)
                    })
                    
                    return response
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to store memory in database"
                    )
                
            except Exception as e:
                logger.error(f"Store memory failed: {e}", extra={
                    'agent_id': request.agent_id,
                    'persona_id': request.persona_id,
                    'slice_id': request.slice_id,
                    'error': str(e)
                })
                
                raise HTTPException(
                    status_code=500,
                    detail=f"Memory storage failed: {str(e)}"
                )
        
        @app.get("/api/semantic/statistics")
        async def get_statistics(
            persona_id: str = "alden",
            user_id: str = "00000000-0000-0000-0000-000000000000",
            token: str = Depends(verify_token)
        ):
            """Get comprehensive semantic memory statistics"""
            await ensure_initialized()
            
            try:
                stats = await self.memory_manager.get_comprehensive_statistics()
                
                return {
                    "status": "success",
                    "persona_id": persona_id,
                    "user_id": user_id,
                    "statistics": stats,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Get statistics failed: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Statistics retrieval failed: {str(e)}"
                )
        
        return app
    
    def run(self, host: str = "0.0.0.0", port: int = 8082):
        """Run the semantic vault API server"""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)

# Factory function
def create_semantic_vault_api(auth_tokens: List[str], config: Dict[str, Any] = None) -> SemanticVaultAPI:
    """
    Factory function to create Semantic Vault API
    
    Args:
        auth_tokens: List of valid authorization tokens
        config: Optional configuration dictionary
        
    Returns:
        SemanticVaultAPI instance
    """
    return SemanticVaultAPI(auth_tokens, config)

# Test client for development
async def test_semantic_api():
    """Test the semantic API endpoints"""
    print("🧪 Testing Semantic Vault API")
    print("=" * 35)
    
    # Create API instance
    api = SemanticVaultAPI(auth_tokens=["test_token_123"])
    
    # Initialize
    print("📡 Initializing semantic memory manager...")
    initialized = await api.initialize()
    
    if not initialized:
        print("❌ Failed to initialize - check database connection")
        return False
    
    print("✅ Initialized successfully")
    
    # Test storing a memory
    print("\n💾 Testing memory storage...")
    
    store_request = StoreMemoryRequest(
        slice_id="slice_test_api_001",
        persona_id="alden",
        user_id="12345678-1234-5678-9012-123456789012",
        agent_id="user",
        content="User asked about the weather forecast for tomorrow and planning outdoor activities.",
        memory_type="episodic",
        keywords=["weather", "forecast", "outdoor", "activities", "planning"],
        relevance_score=0.8,
        metadata={"source": "api_test", "priority": "normal"}
    )
    
    success = await api.memory_manager.store_memory_with_embedding(
        slice_id=store_request.slice_id,
        persona_id=store_request.persona_id,
        user_id=store_request.user_id,
        content=store_request.content,
        memory_type=store_request.memory_type,
        keywords=store_request.keywords,
        relevance_score=store_request.relevance_score,
        metadata=store_request.metadata
    )
    
    if success:
        print(f"✅ Stored memory: {store_request.slice_id}")
    else:
        print(f"❌ Failed to store memory: {store_request.slice_id}")
    
    # Test semantic retrieval
    print("\n🔍 Testing semantic retrieval...")
    
    query = "What did the user ask about weather and outdoor activities?"
    memories = await api.memory_manager.semantic_retrieve(
        query_text=query,
        persona_id="alden",
        user_id="12345678-1234-5678-9012-123456789012",
        limit=5,
        min_similarity=0.1
    )
    
    print(f"Query: {query}")
    print(f"Found {len(memories)} memories:")
    
    for i, memory in enumerate(memories):
        print(f"   {i+1}. {memory.slice_id}: {memory.content[:60]}...")
    
    # Test hybrid retrieval
    print("\n🔄 Testing hybrid retrieval...")
    
    hybrid_memories = await api.memory_manager.hybrid_retrieve(
        query_text=query,
        query_keywords=["weather", "outdoor", "forecast"],
        persona_id="alden",
        user_id="12345678-1234-5678-9012-123456789012",
        limit=5
    )
    
    print(f"Found {len(hybrid_memories)} hybrid memories:")
    for i, memory in enumerate(hybrid_memories):
        print(f"   {i+1}. {memory.slice_id}: {memory.content[:60]}...")
    
    # Get statistics
    print("\n📊 Testing statistics...")
    stats = await api.memory_manager.get_comprehensive_statistics()
    
    print("Database Health:", stats.get("database_health", {}).get("status", "unknown"))
    print("Embedding Service:")
    embedding_stats = stats.get("embedding_service", {})
    for key in ["embeddings_generated", "cache_hit_rate", "model_name"]:
        if key in embedding_stats:
            print(f"   {key}: {embedding_stats[key]}")
    
    # Cleanup
    await api.memory_manager.cleanup()
    
    print("\n✅ Semantic API test completed successfully")
    return True

if __name__ == "__main__":
    # Load environment variables
    env_file = Path(__file__).parent.parent.parent / ".env.pgvector"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Run test
    asyncio.run(test_semantic_api())