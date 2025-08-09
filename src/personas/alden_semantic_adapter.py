#!/usr/bin/env python3
"""
Alden Semantic Adapter - Phase 2 Integration
Integrates Alden persona with production semantic retrieval endpoints
"""

import os
import sys
import json
import uuid
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from personas.alden import AldenPersona, PersonaError
from embedding.semantic_embedding_service import SemanticMemoryManager
from database.pgvector_client import PGVectorClient
from llm.local_llm_client import LocalLLMClient, LLMRequest, LLMResponse
from log_handling.agent_token_tracker import log_agent_token_usage, AgentType

logger = logging.getLogger(__name__)

@dataclass
class SemanticContext:
    """Enhanced context with semantic memory retrieval"""
    query: str
    retrieved_memories: List[Dict[str, Any]]
    similarity_scores: List[float]
    reasoning_chain: Optional[Dict[str, Any]]
    retrieval_time_ms: int
    memory_types_used: List[str]
    total_memories_available: int

@dataclass
class AldenResponse:
    """Enhanced Alden response with semantic context"""
    content: str
    semantic_context: Optional[SemanticContext]
    confidence_score: float
    response_time_ms: int
    model_used: str
    memory_stored: bool
    session_id: str
    user_id: str
    timestamp: str

class AldenSemanticAdapter:
    """
    Enhanced Alden adapter that integrates with production semantic retrieval endpoints.
    
    Provides:
    - Real-time semantic memory retrieval during conversations
    - Automatic memory storage with embeddings
    - Reasoning chain generation for complex queries
    - Performance monitoring and optimization
    """
    
    def __init__(
        self,
        llm_client: LocalLLMClient,
        semantic_vault_url: str = "http://localhost:8082",
        vault_auth_token: str = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize enhanced Alden adapter
        
        Args:
            llm_client: Configured LLM client
            semantic_vault_url: Base URL for semantic vault API
            vault_auth_token: Authorization token for vault API
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.semantic_vault_url = semantic_vault_url.rstrip('/')
        self.vault_auth_token = vault_auth_token or os.getenv('VAULT_AUTH_TOKEN', 'test_token_123')
        
        # Initialize base Alden persona
        self.alden = AldenPersona(llm_client, logger)
        
        # Initialize semantic memory manager for direct access
        self.semantic_manager: Optional[SemanticMemoryManager] = None
        self.direct_mode = False  # Whether to use direct semantic access vs API
        
        # Performance tracking
        self.stats = {
            "total_interactions": 0,
            "semantic_retrievals": 0,
            "memory_stores": 0,
            "avg_retrieval_time_ms": 0.0,
            "avg_response_time_ms": 0.0,
            "cache_hits": 0
        }
        
        # Response cache for similar queries
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_max_size = 100
        
        self.logger.info("Alden Semantic Adapter initialized", extra={
            "semantic_vault_url": self.semantic_vault_url,
            "direct_mode": self.direct_mode,
            "cache_size": self.cache_max_size
        })
    
    async def initialize_semantic_manager(self) -> bool:
        """Initialize direct semantic memory manager if possible"""
        try:
            self.semantic_manager = SemanticMemoryManager()
            success = await self.semantic_manager.initialize()
            
            if success:
                self.direct_mode = True
                self.logger.info("Direct semantic memory manager initialized")
                return True
            else:
                self.logger.warning("Failed to initialize direct semantic manager, using API mode")
                return False
                
        except Exception as e:
            self.logger.warning(f"Could not initialize direct semantic manager: {e}")
            return False
    
    def _get_cache_key(self, query: str, user_id: str) -> str:
        """Generate cache key for query"""
        import hashlib
        return hashlib.md5(f"{query}:{user_id}".encode()).hexdigest()[:16]
    
    def _manage_cache(self):
        """Manage response cache size"""
        if len(self.response_cache) >= self.cache_max_size:
            # Remove oldest 20% of entries
            remove_count = max(1, self.cache_max_size // 5)
            oldest_keys = list(self.response_cache.keys())[:remove_count]
            for key in oldest_keys:
                del self.response_cache[key]
    
    async def _retrieve_semantic_memories_api(
        self,
        query: str,
        user_id: str,
        persona_id: str = "alden",
        memory_types: Optional[List[str]] = None,
        limit: int = 5,
        min_similarity: float = 0.3
    ) -> Optional[Dict[str, Any]]:
        """Retrieve memories using semantic vault API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.vault_auth_token}",
                "Content-Type": "application/json"
            }
            
            request_data = {
                "query": query,
                "persona_id": persona_id,
                "user_id": user_id,
                "agent_id": "alden",
                "memory_types": memory_types,
                "limit": limit,
                "min_similarity": min_similarity
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.semantic_vault_url}/api/semantic/retrieve",
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Semantic API error {response.status}: {error_text}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories via API: {e}")
            return None
    
    async def _retrieve_semantic_memories_direct(
        self,
        query: str,
        user_id: str,
        persona_id: str = "alden",
        memory_types: Optional[List[str]] = None,
        limit: int = 5,
        min_similarity: float = 0.3
    ) -> Optional[List[Dict[str, Any]]]:
        """Retrieve memories using direct semantic manager"""
        if not self.semantic_manager:
            return None
        
        try:
            memories = await self.semantic_manager.semantic_retrieve(
                query_text=query,
                persona_id=persona_id,
                user_id=user_id,
                memory_types=memory_types,
                limit=limit,
                min_similarity=min_similarity
            )
            
            # Convert to API-compatible format
            return [
                {
                    "slice_id": memory.slice_id,
                    "content": memory.content,
                    "memory_type": memory.memory_type,
                    "keywords": memory.keywords,
                    "relevance_score": memory.relevance_score,
                    "created_at": memory.created_at,
                    "retrieval_count": memory.retrieval_count,
                    "metadata": memory.metadata
                }
                for memory in memories
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memories directly: {e}")
            return None
    
    async def _store_memory_api(
        self,
        slice_id: str,
        content: str,
        user_id: str,
        persona_id: str = "alden",
        memory_type: str = "episodic",
        keywords: List[str] = None,
        relevance_score: float = 0.8,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Store memory using semantic vault API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.vault_auth_token}",
                "Content-Type": "application/json"
            }
            
            request_data = {
                "slice_id": slice_id,
                "persona_id": persona_id,
                "user_id": user_id,
                "agent_id": "alden",
                "content": content,
                "memory_type": memory_type,
                "keywords": keywords or [],
                "relevance_score": relevance_score,
                "metadata": metadata
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.semantic_vault_url}/api/semantic/store",
                    headers=headers,
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Memory store API error {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Failed to store memory via API: {e}")
            return False
    
    async def _store_memory_direct(
        self,
        slice_id: str,
        content: str,
        user_id: str,
        persona_id: str = "alden",
        memory_type: str = "episodic",
        keywords: List[str] = None,
        relevance_score: float = 0.8,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Store memory using direct semantic manager"""
        if not self.semantic_manager:
            return False
        
        try:
            success = await self.semantic_manager.store_memory_with_embedding(
                slice_id=slice_id,
                persona_id=persona_id,
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                keywords=keywords or [],
                relevance_score=relevance_score,
                metadata=metadata
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to store memory directly: {e}")
            return False
    
    async def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for hybrid search"""
        # Simple keyword extraction - could be enhanced with NLP libraries
        import re
        
        # Remove common stop words
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'do', 'how', 'their',
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
            'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more', 'go', 'no',
            'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who', 'oil', 'sit',
            'now', 'find', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'
        }
        
        # Extract words, convert to lowercase, filter by length and stop words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Return top 10 most frequent keywords
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]
    
    async def generate_enhanced_response(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        use_semantic_retrieval: bool = True,
        store_conversation: bool = True
    ) -> AldenResponse:
        """
        Generate enhanced Alden response with semantic memory integration
        
        Args:
            user_message: User's message
            session_id: Optional session identifier
            user_id: User identifier (defaults to Alden's user_id)
            context: Optional additional context
            use_semantic_retrieval: Whether to use semantic memory retrieval
            store_conversation: Whether to store this conversation in memory
            
        Returns:
            AldenResponse with semantic context and metadata
        """
        start_time = datetime.now()
        session_id = session_id or f"session_{uuid.uuid4()}"
        effective_user_id = user_id or self.alden.memory.user_id
        
        # Check cache first
        cache_key = self._get_cache_key(user_message, effective_user_id)
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            cached_response["session_id"] = session_id  # Update session
            self.stats["cache_hits"] += 1
            self.logger.info("Returned cached response", extra={"cache_key": cache_key})
            return AldenResponse(**cached_response)
        
        semantic_context = None
        retrieval_time_ms = 0
        
        try:
            # Step 1: Semantic memory retrieval (if enabled)
            if use_semantic_retrieval:
                retrieval_start = datetime.now()
                
                if self.direct_mode and self.semantic_manager:
                    # Use direct semantic manager
                    retrieved_memories = await self._retrieve_semantic_memories_direct(
                        query=user_message,
                        user_id=effective_user_id,
                        persona_id="alden",
                        limit=5,
                        min_similarity=0.2
                    )
                    
                    similarity_scores = [mem.get("relevance_score", 0.0) for mem in (retrieved_memories or [])]
                    
                else:
                    # Use API endpoint
                    api_response = await self._retrieve_semantic_memories_api(
                        query=user_message,
                        user_id=effective_user_id,
                        persona_id="alden",
                        limit=5,
                        min_similarity=0.2
                    )
                    
                    if api_response and api_response.get("status") == "success":
                        retrieved_memories = api_response.get("memories", [])
                        similarity_scores = [mem.get("relevance_score", 0.0) for mem in retrieved_memories]
                        retrieval_time_ms = api_response.get("query_time_ms", 0)
                    else:
                        retrieved_memories = []
                        similarity_scores = []
                
                retrieval_time_ms = int((datetime.now() - retrieval_start).total_seconds() * 1000)
                self.stats["semantic_retrievals"] += 1
                
                # Create semantic context
                if retrieved_memories:
                    semantic_context = SemanticContext(
                        query=user_message,
                        retrieved_memories=retrieved_memories,
                        similarity_scores=similarity_scores,
                        reasoning_chain=None,  # Could be enhanced later
                        retrieval_time_ms=retrieval_time_ms,
                        memory_types_used=list(set(mem.get("memory_type", "unknown") for mem in retrieved_memories)),
                        total_memories_available=len(retrieved_memories)
                    )
                    
                    self.logger.info(f"Retrieved {len(retrieved_memories)} semantic memories", extra={
                        "retrieval_time_ms": retrieval_time_ms,
                        "query_length": len(user_message)
                    })
            
            # Step 2: Enhance context with retrieved memories
            enhanced_context = context or {}
            if semantic_context and semantic_context.retrieved_memories:
                # Add memory context to the conversation
                memory_context = "\n\nRelevant memories from previous conversations:\n"
                for i, memory in enumerate(semantic_context.retrieved_memories[:3]):  # Top 3 most relevant
                    memory_context += f"{i+1}. {memory['content'][:200]}...\n"
                
                enhanced_context["semantic_memories"] = memory_context
                enhanced_context["memory_count"] = len(semantic_context.retrieved_memories)
            
            # Step 3: Generate Alden's response using enhanced context
            enhanced_context["user_id"] = effective_user_id
            response_metadata = self.alden.generate_response(
                user_message=user_message,
                session_id=session_id,
                context=enhanced_context,
                return_metadata=True
            )
            
            if not isinstance(response_metadata, dict):
                # Fallback if metadata format unexpected
                response_content = str(response_metadata)
                response_metadata = {
                    "content": response_content,
                    "model": "unknown",
                    "response_time": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Step 4: Store conversation in semantic memory (if enabled)
            memory_stored = False
            if store_conversation:
                slice_id = f"slice_{session_id}_{int(datetime.now().timestamp())}"
                conversation_content = f"User: {user_message}\nAlden: {response_metadata['content']}"
                keywords = await self._extract_keywords(f"{user_message} {response_metadata['content']}")
                
                metadata = {
                    "session_id": session_id,
                    "user_id": effective_user_id,
                    "response_time_ms": int((response_metadata.get("response_time", 0)) * 1000),
                    "model_used": response_metadata.get("model", "unknown"),
                    "semantic_context_used": semantic_context is not None,
                    "memories_retrieved": len(semantic_context.retrieved_memories) if semantic_context else 0
                }
                
                if self.direct_mode and self.semantic_manager:
                    memory_stored = await self._store_memory_direct(
                        slice_id=slice_id,
                        content=conversation_content,
                        user_id=effective_user_id,
                        persona_id="alden",
                        memory_type="episodic",
                        keywords=keywords,
                        relevance_score=0.8,
                        metadata=metadata
                    )
                else:
                    memory_stored = await self._store_memory_api(
                        slice_id=slice_id,
                        content=conversation_content,
                        user_id=effective_user_id,
                        persona_id="alden",
                        memory_type="episodic",
                        keywords=keywords,
                        relevance_score=0.8,
                        metadata=metadata
                    )
                
                if memory_stored:
                    self.stats["memory_stores"] += 1
            
            # Step 5: Calculate metrics and create response
            total_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            confidence_score = 0.8  # Base confidence, could be enhanced with semantic similarity
            
            if semantic_context and semantic_context.similarity_scores:
                # Boost confidence based on semantic similarity
                avg_similarity = sum(semantic_context.similarity_scores) / len(semantic_context.similarity_scores)
                confidence_score = min(1.0, confidence_score + (avg_similarity * 0.2))
            
            # Create enhanced response
            alden_response = AldenResponse(
                content=response_metadata["content"],
                semantic_context=semantic_context,
                confidence_score=confidence_score,
                response_time_ms=total_time_ms,
                model_used=response_metadata.get("model", "unknown"),
                memory_stored=memory_stored,
                session_id=session_id,
                user_id=effective_user_id,
                timestamp=datetime.now().isoformat()
            )
            
            # Update statistics
            self.stats["total_interactions"] += 1
            self.stats["avg_response_time_ms"] = (
                (self.stats["avg_response_time_ms"] * (self.stats["total_interactions"] - 1) + total_time_ms) /
                self.stats["total_interactions"]
            )
            
            if retrieval_time_ms > 0:
                self.stats["avg_retrieval_time_ms"] = (
                    (self.stats["avg_retrieval_time_ms"] * (self.stats["semantic_retrievals"] - 1) + retrieval_time_ms) /
                    self.stats["semantic_retrievals"]
                )
            
            # Cache successful response
            self._manage_cache()
            self.response_cache[cache_key] = {
                "content": alden_response.content,
                "semantic_context": semantic_context,
                "confidence_score": confidence_score,
                "response_time_ms": total_time_ms,
                "model_used": alden_response.model_used,
                "memory_stored": memory_stored,
                "session_id": session_id,
                "user_id": effective_user_id,
                "timestamp": alden_response.timestamp
            }
            
            # Log successful interaction
            self.logger.info("Enhanced Alden response generated", extra={
                "response_time_ms": total_time_ms,
                "retrieval_time_ms": retrieval_time_ms,
                "memories_used": len(semantic_context.retrieved_memories) if semantic_context else 0,
                "confidence_score": confidence_score,
                "memory_stored": memory_stored
            })
            
            return alden_response
            
        except Exception as e:
            self.logger.error(f"Failed to generate enhanced response: {e}")
            
            # Fallback to basic Alden response
            try:
                basic_response = self.alden.generate_response(
                    user_message=user_message,
                    session_id=session_id,
                    context={"user_id": effective_user_id}
                )
                
                return AldenResponse(
                    content=str(basic_response),
                    semantic_context=None,
                    confidence_score=0.5,
                    response_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    model_used="fallback",
                    memory_stored=False,
                    session_id=session_id,
                    user_id=effective_user_id,
                    timestamp=datetime.now().isoformat()
                )
                
            except Exception as fallback_error:
                self.logger.error(f"Fallback response also failed: {fallback_error}")
                raise PersonaError(f"Both enhanced and fallback responses failed: {e}")
    
    async def get_semantic_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics including semantic memory performance"""
        try:
            # Get basic Alden statistics
            alden_stats = self.alden.get_status()
            
            # Get semantic vault statistics if available
            semantic_stats = None
            if self.direct_mode and self.semantic_manager:
                semantic_stats = await self.semantic_manager.get_comprehensive_statistics()
            else:
                # Try API endpoint
                try:
                    headers = {"Authorization": f"Bearer {self.vault_auth_token}"}
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"{self.semantic_vault_url}/api/semantic/statistics",
                            headers=headers,
                            timeout=aiohttp.ClientTimeout(total=15)
                        ) as response:
                            if response.status == 200:
                                api_response = await response.json()
                                semantic_stats = api_response.get("statistics", {})
                except Exception as api_error:
                    self.logger.warning(f"Could not fetch semantic stats via API: {api_error}")
            
            return {
                "adapter_stats": self.stats,
                "alden_persona_stats": alden_stats,
                "semantic_memory_stats": semantic_stats,
                "cache_stats": {
                    "cache_size": len(self.response_cache),
                    "cache_max_size": self.cache_max_size,
                    "cache_hit_rate": self.stats["cache_hits"] / max(1, self.stats["total_interactions"]) * 100
                },
                "configuration": {
                    "direct_mode": self.direct_mode,
                    "semantic_vault_url": self.semantic_vault_url,
                    "vault_connected": semantic_stats is not None
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get semantic statistics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all components"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        try:
            # Check base Alden persona
            alden_status = self.alden.get_status()
            health_status["components"]["alden_persona"] = {
                "status": "healthy" if "error" not in alden_status else "unhealthy",
                "details": alden_status
            }
            
            # Check semantic manager (direct mode)
            if self.direct_mode and self.semantic_manager:
                try:
                    semantic_health = await self.semantic_manager.get_comprehensive_statistics()
                    db_health = semantic_health.get("database_health", {})
                    health_status["components"]["semantic_manager"] = {
                        "status": db_health.get("status", "unknown"),
                        "details": db_health
                    }
                except Exception as sem_error:
                    health_status["components"]["semantic_manager"] = {
                        "status": "unhealthy",
                        "error": str(sem_error)
                    }
            
            # Check semantic vault API
            try:
                headers = {"Authorization": f"Bearer {self.vault_auth_token}"}
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.semantic_vault_url}/api/semantic/health",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            api_health = await response.json()
                            health_status["components"]["semantic_vault_api"] = {
                                "status": api_health.get("status", "unknown"),
                                "details": api_health
                            }
                        else:
                            health_status["components"]["semantic_vault_api"] = {
                                "status": "unhealthy",
                                "http_status": response.status
                            }
            except Exception as api_error:
                health_status["components"]["semantic_vault_api"] = {
                    "status": "offline",
                    "error": str(api_error)
                }
            
            # Overall health assessment
            component_statuses = [comp["status"] for comp in health_status["components"].values()]
            if "unhealthy" in component_statuses:
                health_status["status"] = "degraded"
            elif "offline" in component_statuses:
                health_status["status"] = "degraded"
            elif all(status == "healthy" for status in component_statuses):
                health_status["status"] = "healthy"
            else:
                health_status["status"] = "partial"
            
            return health_status
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.semantic_manager:
            await self.semantic_manager.cleanup()
        
        # Clear cache
        self.response_cache.clear()
        
        self.logger.info("Alden Semantic Adapter cleanup completed")

# Factory function
async def create_alden_semantic_adapter(
    llm_config: Dict[str, Any],
    semantic_vault_url: str = "http://localhost:8082",
    vault_auth_token: str = None,
    enable_direct_mode: bool = True,
    logger: Optional[logging.Logger] = None
) -> AldenSemanticAdapter:
    """
    Factory function to create enhanced Alden semantic adapter
    
    Args:
        llm_config: LLM configuration dictionary
        semantic_vault_url: Base URL for semantic vault API
        vault_auth_token: Authorization token for vault API
        enable_direct_mode: Whether to try direct semantic manager initialization
        logger: Optional logger instance
        
    Returns:
        AldenSemanticAdapter: Configured adapter
    """
    try:
        from llm.local_llm_client import create_llm_client
        llm_client = create_llm_client(llm_config, logger)
        
        adapter = AldenSemanticAdapter(
            llm_client=llm_client,
            semantic_vault_url=semantic_vault_url,
            vault_auth_token=vault_auth_token,
            logger=logger
        )
        
        # Try to initialize direct mode if requested
        if enable_direct_mode:
            await adapter.initialize_semantic_manager()
        
        return adapter
        
    except Exception as e:
        raise PersonaError(f"Failed to create Alden semantic adapter: {str(e)}") from e

# Test function for development
async def test_semantic_adapter():
    """Test the semantic adapter functionality"""
    print("🧪 Testing Alden Semantic Adapter")
    print("=" * 40)
    
    # Load environment variables
    env_file = Path(__file__).parent.parent.parent / ".env.pgvector"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    try:
        # Mock LLM client for testing
        class MockLLMClient:
            def __init__(self):
                self.config = type('Config', (), {
                    'engine': 'mock',
                    'model': 'mock-model'
                })()
            
            def generate(self, request):
                return type('Response', (), {
                    'content': f"Mock response to: {request.prompt[:50]}...",
                    'model': 'mock-model',
                    'response_time': 0.1,
                    'timestamp': datetime.now().isoformat(),
                    'usage': {},
                    'finish_reason': 'stop'
                })()
            
            def get_status(self):
                return {"status": "healthy", "model": "mock-model"}
        
        # Create adapter
        adapter = AldenSemanticAdapter(
            llm_client=MockLLMClient(),
            semantic_vault_url="http://localhost:8082",
            vault_auth_token="test_token_123"
        )
        
        # Try to initialize semantic manager
        print("📡 Initializing semantic manager...")
        initialized = await adapter.initialize_semantic_manager()
        print(f"   Direct mode: {'✅ Enabled' if initialized else '❌ API mode only'}")
        
        # Test enhanced response generation
        print("\n🤖 Testing enhanced response generation...")
        
        test_messages = [
            "What did we discuss about machine learning yesterday?",
            "Help me plan my day today",
            "What are some good productivity tips?"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n  Test {i}: {message}")
            
            try:
                response = await adapter.generate_enhanced_response(
                    user_message=message,
                    session_id=f"test_session_{i}",
                    use_semantic_retrieval=True,
                    store_conversation=True
                )
                
                print(f"    Response: {response.content[:100]}...")
                print(f"    Confidence: {response.confidence_score:.2f}")
                print(f"    Response time: {response.response_time_ms}ms")
                print(f"    Memory stored: {'✅' if response.memory_stored else '❌'}")
                
                if response.semantic_context:
                    print(f"    Memories retrieved: {response.semantic_context.total_memories_available}")
                    print(f"    Retrieval time: {response.semantic_context.retrieval_time_ms}ms")
                
            except Exception as e:
                print(f"    ❌ Failed: {e}")
        
        # Test statistics
        print("\n📊 Testing statistics...")
        stats = await adapter.get_semantic_statistics()
        
        print(f"  Total interactions: {stats['adapter_stats']['total_interactions']}")
        print(f"  Semantic retrievals: {stats['adapter_stats']['semantic_retrievals']}")
        print(f"  Memory stores: {stats['adapter_stats']['memory_stores']}")
        print(f"  Cache hit rate: {stats['cache_stats']['cache_hit_rate']:.1f}%")
        
        # Test health check
        print("\n🏥 Testing health check...")
        health = await adapter.health_check()
        print(f"  Overall status: {health['status']}")
        
        for component, status in health['components'].items():
            print(f"  {component}: {status['status']}")
        
        # Cleanup
        await adapter.cleanup()
        
        print("\n✅ Semantic adapter test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Semantic adapter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run test
    success = asyncio.run(test_semantic_adapter())
    sys.exit(0 if success else 1)