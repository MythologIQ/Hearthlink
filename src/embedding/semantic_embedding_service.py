#!/usr/bin/env python3
"""
Semantic Embedding Service for Hearthlink Memory System
Provides text-to-vector embedding generation using sentence transformers
"""

import os
import sys
import json
import asyncio
import logging
import hashlib
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    import torch
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install sentence-transformers torch numpy")
    sys.exit(1)

# Import our PGVector client
from database.pgvector_client import PGVectorClient, SemanticMemorySlice

@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    text: str
    embedding: List[float]
    model_name: str
    embedding_dimension: int
    generation_time_ms: int
    text_hash: str

class SemanticEmbeddingService:
    """Service for generating and managing text embeddings"""
    
    def __init__(
        self, 
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        cache_size: int = 1000,
        device: str = None,
        logger: logging.Logger = None
    ):
        """
        Initialize embedding service
        
        Args:
            model_name: HuggingFace model name
            cache_size: Number of embeddings to cache in memory
            device: Torch device ('cpu', 'cuda', 'auto')
            logger: Optional logger instance
        """
        self.model_name = model_name
        self.cache_size = cache_size
        self.logger = logger or logging.getLogger(__name__)
        
        # Set device
        if device == "auto" or device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.logger.info(f"Using device: {self.device}")
        
        # Initialize model
        self.model = None
        self.embedding_dimension = None
        
        # Embedding cache
        self.embedding_cache: Dict[str, EmbeddingResult] = {}
        
        # Statistics
        self.stats = {
            "embeddings_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_generation_time_ms": 0,
            "average_generation_time_ms": 0.0
        }
    
    def _load_model(self) -> bool:
        """Load the sentence transformer model"""
        try:
            self.logger.info(f"Loading embedding model: {self.model_name}")
            start_time = time.time()
            
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            
            load_time = int((time.time() - start_time) * 1000)
            self.logger.info(
                f"Model loaded successfully in {load_time}ms. "
                f"Embedding dimension: {self.embedding_dimension}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            return False
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text caching"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
    
    def _manage_cache(self):
        """Remove old entries if cache is full"""
        if len(self.embedding_cache) >= self.cache_size:
            # Remove oldest 20% of entries
            remove_count = max(1, self.cache_size // 5)
            oldest_keys = list(self.embedding_cache.keys())[:remove_count]
            
            for key in oldest_keys:
                del self.embedding_cache[key]
                
            self.logger.debug(f"Removed {remove_count} entries from embedding cache")
    
    async def generate_embedding(self, text: str, use_cache: bool = True) -> EmbeddingResult:
        """
        Generate embedding for text
        
        Args:
            text: Input text
            use_cache: Whether to use/store in cache
            
        Returns:
            EmbeddingResult with embedding and metadata
        """
        if not self.model:
            if not self._load_model():
                raise Exception("Failed to load embedding model")
        
        text_hash = self._get_text_hash(text)
        
        # Check cache first
        if use_cache and text_hash in self.embedding_cache:
            self.stats["cache_hits"] += 1
            return self.embedding_cache[text_hash]
        
        # Generate embedding
        start_time = time.time()
        
        try:
            # Run model inference in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding_array = await loop.run_in_executor(
                None, 
                lambda: self.model.encode([text], convert_to_numpy=True)
            )
            
            # Extract embedding and convert to list
            embedding = embedding_array[0].tolist()
            generation_time = int((time.time() - start_time) * 1000)
            
            # Create result
            result = EmbeddingResult(
                text=text,
                embedding=embedding,
                model_name=self.model_name,
                embedding_dimension=len(embedding),
                generation_time_ms=generation_time,
                text_hash=text_hash
            )
            
            # Update statistics
            self.stats["embeddings_generated"] += 1
            self.stats["cache_misses"] += 1
            self.stats["total_generation_time_ms"] += generation_time
            self.stats["average_generation_time_ms"] = (
                self.stats["total_generation_time_ms"] / self.stats["embeddings_generated"]
            )
            
            # Cache result
            if use_cache:
                self._manage_cache()
                self.embedding_cache[text_hash] = result
            
            self.logger.debug(
                f"Generated embedding for text ({len(text)} chars) in {generation_time}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def generate_embeddings_batch(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        use_cache: bool = True
    ) -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            use_cache: Whether to use/store in cache
            
        Returns:
            List of EmbeddingResult objects
        """
        if not self.model:
            if not self._load_model():
                raise Exception("Failed to load embedding model")
        
        results = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_results = []
            texts_to_embed = []
            cached_results = {}
            
            # Check cache for each text
            for j, text in enumerate(batch_texts):
                text_hash = self._get_text_hash(text)
                
                if use_cache and text_hash in self.embedding_cache:
                    cached_results[j] = self.embedding_cache[text_hash]
                    self.stats["cache_hits"] += 1
                else:
                    texts_to_embed.append((j, text))
            
            # Generate embeddings for uncached texts
            if texts_to_embed:
                start_time = time.time()
                
                try:
                    # Run batch inference
                    loop = asyncio.get_event_loop()
                    text_list = [text for _, text in texts_to_embed]
                    embeddings_array = await loop.run_in_executor(
                        None,
                        lambda: self.model.encode(text_list, convert_to_numpy=True)
                    )
                    
                    generation_time = int((time.time() - start_time) * 1000)
                    avg_time_per_embedding = generation_time // len(texts_to_embed)
                    
                    # Process results
                    for k, (original_idx, text) in enumerate(texts_to_embed):
                        embedding = embeddings_array[k].tolist()
                        text_hash = self._get_text_hash(text)
                        
                        result = EmbeddingResult(
                            text=text,
                            embedding=embedding,
                            model_name=self.model_name,
                            embedding_dimension=len(embedding),
                            generation_time_ms=avg_time_per_embedding,
                            text_hash=text_hash
                        )
                        
                        cached_results[original_idx] = result
                        
                        # Cache result
                        if use_cache:
                            self._manage_cache()
                            self.embedding_cache[text_hash] = result
                    
                    # Update statistics
                    self.stats["embeddings_generated"] += len(texts_to_embed)
                    self.stats["cache_misses"] += len(texts_to_embed)
                    self.stats["total_generation_time_ms"] += generation_time
                    self.stats["average_generation_time_ms"] = (
                        self.stats["total_generation_time_ms"] / self.stats["embeddings_generated"]
                    )
                    
                    self.logger.debug(
                        f"Generated {len(texts_to_embed)} embeddings in {generation_time}ms "
                        f"(avg: {avg_time_per_embedding}ms per embedding)"
                    )
                    
                except Exception as e:
                    self.logger.error(f"Failed to generate batch embeddings: {e}")
                    raise
            
            # Collect results in original order
            for j in range(len(batch_texts)):
                results.append(cached_results[j])
        
        return results
    
    async def embed_memory_slice(
        self, 
        slice_id: str,
        persona_id: str,
        user_id: str,
        content: str,
        memory_type: str,
        keywords: List[str],
        relevance_score: float = 0.5,
        metadata: Dict[str, Any] = None
    ) -> SemanticMemorySlice:
        """
        Generate embedding and create memory slice object
        
        Args:
            slice_id: Unique slice identifier
            persona_id: Persona identifier
            user_id: User identifier
            content: Memory content text
            memory_type: Type of memory (episodic, semantic, procedural, working)
            keywords: Extracted keywords
            relevance_score: Relevance score (0.0-1.0)
            metadata: Additional metadata
            
        Returns:
            SemanticMemorySlice with embedding
        """
        # Generate embedding for content
        embedding_result = await self.generate_embedding(content)
        
        # Create memory slice
        now = datetime.now().isoformat()
        memory_slice = SemanticMemorySlice(
            slice_id=slice_id,
            persona_id=persona_id,
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            keywords=keywords,
            embedding=embedding_result.embedding,
            relevance_score=relevance_score,
            created_at=now,
            last_accessed=now,
            retrieval_count=0,
            metadata=metadata or {}
        )
        
        return memory_slice
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get embedding service statistics"""
        return {
            **self.stats,
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "device": self.device,
            "cache_size": len(self.embedding_cache),
            "cache_max_size": self.cache_size,
            "cache_hit_rate": (
                self.stats["cache_hits"] / 
                max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
            ) * 100,
            "model_loaded": self.model is not None
        }
    
    def clear_cache(self):
        """Clear embedding cache"""
        self.embedding_cache.clear()
        self.logger.info("Embedding cache cleared")

# Integration service that combines embedding generation with PGVector storage
class SemanticMemoryManager:
    """High-level service that manages semantic memory with embeddings"""
    
    def __init__(
        self,
        embedding_service: SemanticEmbeddingService = None,
        pgvector_client: PGVectorClient = None,
        logger: logging.Logger = None
    ):
        """
        Initialize semantic memory manager
        
        Args:
            embedding_service: Embedding service instance
            pgvector_client: PGVector client instance
            logger: Optional logger
        """
        self.embedding_service = embedding_service or SemanticEmbeddingService()
        self.pgvector_client = pgvector_client or PGVectorClient()
        self.logger = logger or logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize both embedding service and database connection"""
        try:
            # Connect to database
            db_connected = await self.pgvector_client.connect()
            if not db_connected:
                return False
            
            # Load embedding model
            if not self.embedding_service.model:
                model_loaded = self.embedding_service._load_model()
                if not model_loaded:
                    return False
            
            self.logger.info("Semantic memory manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize semantic memory manager: {e}")
            return False
    
    async def store_memory_with_embedding(
        self,
        slice_id: str,
        persona_id: str,
        user_id: str,
        content: str,
        memory_type: str,
        keywords: List[str],
        relevance_score: float = 0.5,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Generate embedding and store memory slice in database
        
        Args:
            slice_id: Unique slice identifier
            persona_id: Persona identifier
            user_id: User identifier
            content: Memory content
            memory_type: Memory type
            keywords: Keywords for hybrid search
            relevance_score: Relevance score
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Create memory slice with embedding
            memory_slice = await self.embedding_service.embed_memory_slice(
                slice_id=slice_id,
                persona_id=persona_id,
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                keywords=keywords,
                relevance_score=relevance_score,
                metadata=metadata
            )
            
            # Store in database
            success = await self.pgvector_client.store_memory_slice(memory_slice)
            
            if success:
                self.logger.info(f"Stored memory slice with embedding: {slice_id}")
            else:
                self.logger.error(f"Failed to store memory slice: {slice_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to store memory with embedding: {e}")
            return False
    
    async def semantic_retrieve(
        self,
        query_text: str,
        persona_id: str,
        user_id: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[SemanticMemorySlice]:
        """
        Perform semantic retrieval using query text
        
        Args:
            query_text: Query text
            persona_id: Persona identifier
            user_id: User identifier
            memory_types: Optional memory type filter
            limit: Maximum results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar memory slices
        """
        try:
            # Generate embedding for query
            query_embedding_result = await self.embedding_service.generate_embedding(query_text)
            
            # Perform semantic search
            search_result = await self.pgvector_client.semantic_search(
                query_embedding=query_embedding_result.embedding,
                persona_id=persona_id,
                user_id=user_id,
                memory_types=memory_types,
                limit=limit,
                min_similarity=min_similarity
            )
            
            self.logger.info(
                f"Semantic retrieval returned {len(search_result.memories)} results "
                f"in {search_result.query_time_ms}ms"
            )
            
            return search_result.memories
            
        except Exception as e:
            self.logger.error(f"Semantic retrieval failed: {e}")
            return []
    
    async def hybrid_retrieve(
        self,
        query_text: str,
        query_keywords: List[str],
        persona_id: str,
        user_id: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> List[SemanticMemorySlice]:
        """
        Perform hybrid retrieval combining keywords and semantics
        
        Args:
            query_text: Query text
            query_keywords: Query keywords
            persona_id: Persona identifier
            user_id: User identifier
            memory_types: Optional memory type filter
            limit: Maximum results
            keyword_weight: Weight for keyword matching
            semantic_weight: Weight for semantic similarity
            
        Returns:
            List of relevant memory slices
        """
        try:
            # Generate embedding for query
            query_embedding_result = await self.embedding_service.generate_embedding(query_text)
            
            # Perform hybrid search
            search_result = await self.pgvector_client.hybrid_search(
                query_text=query_text,
                query_embedding=query_embedding_result.embedding,
                query_keywords=query_keywords,
                persona_id=persona_id,
                user_id=user_id,
                memory_types=memory_types,
                limit=limit,
                keyword_weight=keyword_weight,
                semantic_weight=semantic_weight
            )
            
            self.logger.info(
                f"Hybrid retrieval returned {len(search_result.memories)} results "
                f"in {search_result.query_time_ms}ms"
            )
            
            return search_result.memories
            
        except Exception as e:
            self.logger.error(f"Hybrid retrieval failed: {e}")
            return []
    
    async def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components"""
        try:
            # Get embedding statistics
            embedding_stats = self.embedding_service.get_statistics()
            
            # Get database statistics (example persona/user)
            db_stats = await self.pgvector_client.get_memory_statistics("alden", "00000000-0000-0000-0000-000000000000")
            
            # Get database health
            db_health = await self.pgvector_client.health_check()
            
            return {
                "embedding_service": embedding_stats,
                "database": db_stats,
                "database_health": db_health,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive statistics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.pgvector_client:
            await self.pgvector_client.disconnect()
        
        if self.embedding_service:
            self.embedding_service.clear_cache()

# Test and CLI functions
async def test_embedding_service():
    """Test the embedding service functionality"""
    print("🧠 Testing Semantic Embedding Service")
    print("=" * 40)
    
    # Initialize service
    embedding_service = SemanticEmbeddingService()
    
    # Test single embedding
    print("\n📝 Testing single embedding generation...")
    test_text = "This is a test memory about artificial intelligence and natural language processing."
    
    result = await embedding_service.generate_embedding(test_text)
    
    print(f"✅ Generated embedding:")
    print(f"   Text: {result.text[:50]}...")
    print(f"   Dimension: {result.embedding_dimension}")
    print(f"   Model: {result.model_name}")
    print(f"   Generation time: {result.generation_time_ms}ms")
    print(f"   First 5 dimensions: {result.embedding[:5]}")
    
    # Test batch embedding
    print("\n📝 Testing batch embedding generation...")
    test_texts = [
        "Memory about machine learning algorithms",
        "Conversation about weather and climate",
        "Discussion on programming languages",
        "Planning a vacation trip"
    ]
    
    batch_results = await embedding_service.generate_embeddings_batch(test_texts)
    
    print(f"✅ Generated {len(batch_results)} embeddings in batch")
    for i, result in enumerate(batch_results):
        print(f"   {i+1}. {result.text[:30]}... -> {result.generation_time_ms}ms")
    
    # Test cache
    print("\n🗄️ Testing embedding cache...")
    cached_result = await embedding_service.generate_embedding(test_text)
    
    print(f"✅ Cache test:")
    print(f"   Same embedding: {cached_result.embedding[:3] == result.embedding[:3]}")
    print(f"   Generation time: {cached_result.generation_time_ms}ms (should be 0 for cache hit)")
    
    # Print statistics
    print("\n📊 Embedding Service Statistics:")
    stats = embedding_service.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

async def test_full_integration():
    """Test full integration with PGVector database"""
    print("🔗 Testing Full Semantic Memory Integration")
    print("=" * 45)
    
    # Initialize manager
    manager = SemanticMemoryManager()
    
    # Initialize components
    print("📡 Initializing semantic memory manager...")
    initialized = await manager.initialize()
    
    if not initialized:
        print("❌ Failed to initialize semantic memory manager")
        return False
    
    print("✅ Manager initialized successfully")
    
    # Test memory storage
    print("\n💾 Testing memory storage with embedding...")
    
    test_memories = [
        {
            "slice_id": "slice_test_001",
            "content": "User asked about machine learning algorithms and their applications in natural language processing.",
            "memory_type": "episodic",
            "keywords": ["machine learning", "algorithms", "nlp", "applications"]
        },
        {
            "slice_id": "slice_test_002", 
            "content": "Discussion about the weather patterns and climate change effects on global ecosystems.",
            "memory_type": "semantic",
            "keywords": ["weather", "climate change", "ecosystems", "global"]
        },
        {
            "slice_id": "slice_test_003",
            "content": "Planning a vacation trip to Japan, discussing travel routes and cultural experiences.",
            "memory_type": "procedural", 
            "keywords": ["vacation", "japan", "travel", "culture"]
        }
    ]
    
    for memory in test_memories:
        success = await manager.store_memory_with_embedding(
            slice_id=memory["slice_id"],
            persona_id="test_persona",
            user_id="12345678-1234-5678-9012-123456789012",
            content=memory["content"],
            memory_type=memory["memory_type"],
            keywords=memory["keywords"],
            relevance_score=0.8
        )
        
        if success:
            print(f"✅ Stored: {memory['slice_id']}")
        else:
            print(f"❌ Failed to store: {memory['slice_id']}")
    
    # Test semantic retrieval
    print("\n🔍 Testing semantic retrieval...")
    
    query = "Tell me about artificial intelligence and machine learning"
    results = await manager.semantic_retrieve(
        query_text=query,
        persona_id="test_persona",
        user_id="12345678-1234-5678-9012-123456789012",
        limit=5,
        min_similarity=0.1
    )
    
    print(f"Query: {query}")
    print(f"Found {len(results)} similar memories:")
    
    for i, memory in enumerate(results):
        print(f"   {i+1}. {memory.slice_id}: {memory.content[:60]}...")
        print(f"       Type: {memory.memory_type}, Score: {memory.relevance_score}")
    
    # Test hybrid retrieval
    print("\n🔍 Testing hybrid retrieval...")
    
    hybrid_results = await manager.hybrid_retrieve(
        query_text=query,
        query_keywords=["AI", "machine learning", "algorithms"],
        persona_id="test_persona",
        user_id="12345678-1234-5678-9012-123456789012",
        limit=5
    )
    
    print(f"Found {len(hybrid_results)} hybrid matches:")
    for i, memory in enumerate(hybrid_results):
        print(f"   {i+1}. {memory.slice_id}: {memory.content[:60]}...")
    
    # Get statistics
    print("\n📊 Comprehensive Statistics:")
    stats = await manager.get_comprehensive_statistics()
    
    print("Embedding Service:")
    for key, value in stats.get("embedding_service", {}).items():
        print(f"   {key}: {value}")
    
    print("Database Health:")
    for key, value in stats.get("database_health", {}).items():
        print(f"   {key}: {value}")
    
    # Cleanup
    await manager.cleanup()
    
    return True

if __name__ == "__main__":
    import sys
    
    # Load environment variables
    env_file = Path(__file__).parent.parent.parent / ".env.pgvector"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Run tests based on command line argument
    if len(sys.argv) > 1 and sys.argv[1] == "integration":
        asyncio.run(test_full_integration())
    else:
        asyncio.run(test_embedding_service())