"""
RAG/CAG Enhanced Vault System for Hearthlink
Implements Retrieval-Augmented Generation and Chain-of-Thought Augmentation
"""

import os
import json
import numpy as np
import hashlib
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import threading
from sentence_transformers import SentenceTransformer
import logging

from .vault_enhanced import VaultEnhanced, VaultError

@dataclass
class MemorySlice:
    """Enhanced memory slice with RAG/CAG capabilities"""
    slice_id: str
    content: str
    memory_type: str  # 'episodic', 'semantic', 'procedural', 'working'
    created_at: str
    last_accessed: str
    embedding_vector: Optional[List[float]]
    relevance_score: float
    metadata: Dict[str, Any]
    parent_slice_id: Optional[str] = None
    reasoning_chain: Optional[List[str]] = None
    retrieval_count: int = 0

@dataclass
class RetrievalResult:
    """Result from RAG retrieval operation"""
    memories: List[MemorySlice]
    similarity_scores: List[float]
    total_relevance: float
    retrieval_time_ms: int
    query_embedding: List[float]

@dataclass
class ReasoningChain:
    """Chain-of-thought reasoning result"""
    chain_id: str
    initial_query: str
    reasoning_steps: List[Dict[str, Any]]
    final_conclusion: str
    confidence_score: float
    supporting_memories: List[str]
    created_at: str

class RAGCAGVault(VaultEnhanced):
    """
    Enhanced Vault with RAG (Retrieval-Augmented Generation) and 
    CAG (Chain-of-Thought Augmentation) capabilities
    """
    
    def __init__(self, config: Dict[str, Any], logger=None):
        super().__init__(config, logger)
        
        # RAG/CAG specific configuration
        self.embedding_model_name = config.get("rag_config", {}).get("embedding_model", "all-MiniLM-L6-v2")
        self.max_retrieval_results = config.get("rag_config", {}).get("max_results", 10)
        self.similarity_threshold = config.get("rag_config", {}).get("similarity_threshold", 0.7)
        self.vector_dimension = config.get("rag_config", {}).get("vector_dimension", 384)
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            if logger:
                logger.info(f"Initialized embedding model: {self.embedding_model_name}")
        except Exception as e:
            if logger:
                logger.warning(f"Failed to load embedding model {self.embedding_model_name}, using fallback: {e}")
            self.embedding_model = None
        
        # Initialize vector database (SQLite with vector operations)
        self._init_vector_db()
        
        # Reasoning chain cache
        self.reasoning_chains: Dict[str, ReasoningChain] = {}
        self.chain_lock = threading.RLock()

    def _init_vector_db(self):
        """Initialize SQLite database for vector operations"""
        try:
            vector_db_path = self.config.get("storage", {}).get("vector_db_path", 
                                                               str(self.storage_path.parent / "vectors.db"))
            self.vector_db_path = Path(vector_db_path)
            self.vector_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create vector database schema
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_vectors (
                        slice_id TEXT PRIMARY KEY,
                        persona_id TEXT,
                        user_id TEXT,
                        content TEXT,
                        memory_type TEXT,
                        embedding_vector TEXT,  -- JSON string of vector
                        relevance_score REAL,
                        created_at TEXT,
                        last_accessed TEXT,
                        retrieval_count INTEGER DEFAULT 0,
                        metadata TEXT  -- JSON string
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS reasoning_chains (
                        chain_id TEXT PRIMARY KEY,
                        persona_id TEXT,
                        user_id TEXT,
                        initial_query TEXT,
                        reasoning_steps TEXT,  -- JSON string
                        final_conclusion TEXT,
                        confidence_score REAL,
                        supporting_memories TEXT,  -- JSON string
                        created_at TEXT
                    )
                """)
                
                # Create indexes for performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_vectors_persona ON memory_vectors(persona_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_vectors_type ON memory_vectors(memory_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_vectors_score ON memory_vectors(relevance_score)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_chains_persona ON reasoning_chains(persona_id)")
                
                conn.commit()
                
            if self.logger:
                self.logger.info(f"Vector database initialized at {vector_db_path}")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize vector database: {e}")
            raise VaultError(f"Vector database initialization failed: {e}")

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text"""
        if not self.embedding_model:
            return None
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to generate embedding: {e}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        except:
            return 0.0

    def store_memory_slice(self, persona_id: str, user_id: str, content: str, 
                          memory_type: str = "episodic", 
                          metadata: Dict[str, Any] = None) -> str:
        """Store a memory slice with vector embedding"""
        slice_id = f"slice_{hashlib.md5(f'{persona_id}_{user_id}_{content}_{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}"
        
        try:
            # Generate embedding
            embedding = self._generate_embedding(content)
            
            # Create memory slice
            memory_slice = MemorySlice(
                slice_id=slice_id,
                content=content,
                memory_type=memory_type,
                created_at=datetime.now().isoformat(),
                last_accessed=datetime.now().isoformat(),
                embedding_vector=embedding,
                relevance_score=0.5,  # Initial relevance
                metadata=metadata or {},
                retrieval_count=0
            )
            
            # Store in vector database
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memory_vectors 
                    (slice_id, persona_id, user_id, content, memory_type, 
                     embedding_vector, relevance_score, created_at, last_accessed, 
                     retrieval_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    slice_id, persona_id, user_id, content, memory_type,
                    json.dumps(embedding) if embedding else None,
                    memory_slice.relevance_score,
                    memory_slice.created_at,
                    memory_slice.last_accessed,
                    memory_slice.retrieval_count,
                    json.dumps(memory_slice.metadata)
                ))
                conn.commit()
            
            self._log("store_memory_slice", user_id, persona_id, "memory_slice", slice_id, 
                     {"content_length": len(content), "memory_type": memory_type})
            
            return slice_id
            
        except Exception as e:
            self._log("store_memory_slice", user_id, persona_id, "memory_slice", slice_id, 
                     {"content_length": len(content)}, result="failure", error=e)
            raise VaultError(f"Failed to store memory slice: {e}")

    def retrieve_similar_memories(self, query: str, persona_id: str, user_id: str,
                                 memory_types: List[str] = None,
                                 max_results: int = None,
                                 min_similarity: float = None) -> RetrievalResult:
        """
        RAG: Retrieve memories similar to query using semantic search
        """
        start_time = datetime.now()
        
        try:
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return RetrievalResult(
                    memories=[], 
                    similarity_scores=[], 
                    total_relevance=0.0,
                    retrieval_time_ms=0,
                    query_embedding=[]
                )
            
            max_results = max_results or self.max_retrieval_results
            min_similarity = min_similarity or self.similarity_threshold
            
            # Build query
            query_sql = """
                SELECT slice_id, persona_id, user_id, content, memory_type,
                       embedding_vector, relevance_score, created_at, last_accessed,
                       retrieval_count, metadata
                FROM memory_vectors 
                WHERE persona_id = ? AND user_id = ? AND embedding_vector IS NOT NULL
            """
            query_params = [persona_id, user_id]
            
            if memory_types:
                placeholders = ','.join(['?' for _ in memory_types])
                query_sql += f" AND memory_type IN ({placeholders})"
                query_params.extend(memory_types)
            
            # Retrieve candidate memories
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                cursor = conn.execute(query_sql, query_params)
                rows = cursor.fetchall()
            
            # Calculate similarities and rank
            similar_memories = []
            similarity_scores = []
            
            for row in rows:
                try:
                    stored_embedding = json.loads(row[5]) if row[5] else None
                    if stored_embedding:
                        similarity = self._cosine_similarity(query_embedding, stored_embedding)
                        
                        if similarity >= min_similarity:
                            memory_slice = MemorySlice(
                                slice_id=row[0],
                                content=row[3],
                                memory_type=row[4],
                                created_at=row[7],
                                last_accessed=row[8],
                                embedding_vector=stored_embedding,
                                relevance_score=row[6],
                                metadata=json.loads(row[10]) if row[10] else {},
                                retrieval_count=row[9]
                            )
                            
                            similar_memories.append(memory_slice)
                            similarity_scores.append(similarity)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Error processing memory slice {row[0]}: {e}")
                    continue
            
            # Sort by similarity score
            if similar_memories:
                sorted_pairs = sorted(zip(similar_memories, similarity_scores), 
                                    key=lambda x: x[1], reverse=True)
                similar_memories, similarity_scores = zip(*sorted_pairs)
                similar_memories = list(similar_memories[:max_results])
                similarity_scores = list(similarity_scores[:max_results])
                
                # Update retrieval counts
                self._update_retrieval_counts([m.slice_id for m in similar_memories])
            
            # Calculate retrieval time
            retrieval_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            result = RetrievalResult(
                memories=similar_memories,
                similarity_scores=similarity_scores,
                total_relevance=sum(similarity_scores) if similarity_scores else 0.0,
                retrieval_time_ms=retrieval_time,
                query_embedding=query_embedding
            )
            
            self._log("retrieve_similar_memories", user_id, persona_id, "retrieval", None,
                     {"query_length": len(query), "results_count": len(similar_memories), 
                      "retrieval_time_ms": retrieval_time})
            
            return result
            
        except Exception as e:
            self._log("retrieve_similar_memories", user_id, persona_id, "retrieval", None,
                     {"query_length": len(query)}, result="failure", error=e)
            raise VaultError(f"Memory retrieval failed: {e}")

    def _update_retrieval_counts(self, slice_ids: List[str]):
        """Update retrieval counts for accessed memories"""
        try:
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                for slice_id in slice_ids:
                    conn.execute("""
                        UPDATE memory_vectors 
                        SET retrieval_count = retrieval_count + 1,
                            last_accessed = ?
                        WHERE slice_id = ?
                    """, (datetime.now().isoformat(), slice_id))
                conn.commit()
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to update retrieval counts: {e}")

    def generate_reasoning_chain(self, query: str, persona_id: str, user_id: str,
                               context_memories: List[MemorySlice] = None) -> ReasoningChain:
        """
        CAG: Generate chain-of-thought reasoning based on query and retrieved memories
        """
        chain_id = f"chain_{hashlib.md5(f'{persona_id}_{user_id}_{query}_{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}"
        
        try:
            # If no context provided, retrieve relevant memories
            if context_memories is None:
                retrieval_result = self.retrieve_similar_memories(query, persona_id, user_id)
                context_memories = retrieval_result.memories
            
            # Build reasoning chain steps
            reasoning_steps = []
            confidence_scores = []
            
            # Step 1: Query analysis
            reasoning_steps.append({
                "step": 1,
                "type": "query_analysis",
                "description": "Analyzing query and identifying key concepts",
                "input": query,
                "output": f"Identified {len(context_memories)} relevant memories for reasoning",
                "confidence": 0.9
            })
            confidence_scores.append(0.9)
            
            # Step 2: Memory integration
            if context_memories:
                memory_contents = [m.content for m in context_memories]
                reasoning_steps.append({
                    "step": 2,
                    "type": "memory_integration",
                    "description": "Integrating relevant memories into reasoning context",
                    "input": memory_contents,
                    "output": f"Integrated {len(context_memories)} memories into reasoning context",
                    "confidence": min(0.8, sum(m.relevance_score for m in context_memories) / len(context_memories))
                })
                confidence_scores.append(reasoning_steps[-1]["confidence"])
            
            # Step 3: Pattern recognition
            patterns = self._identify_patterns(context_memories)
            reasoning_steps.append({
                "step": 3,
                "type": "pattern_recognition",
                "description": "Identifying patterns and relationships in retrieved memories",
                "input": [m.content[:100] + "..." for m in context_memories],
                "output": f"Identified {len(patterns)} patterns in memory context",
                "confidence": 0.7,
                "patterns": patterns
            })
            confidence_scores.append(0.7)
            
            # Step 4: Logical inference
            inference = self._perform_logical_inference(query, context_memories, patterns)
            reasoning_steps.append({
                "step": 4,
                "type": "logical_inference",
                "description": "Performing logical inference based on patterns and context",
                "input": {"query": query, "patterns": patterns},
                "output": inference["conclusion"],
                "confidence": inference["confidence"]
            })
            confidence_scores.append(inference["confidence"])
            
            # Calculate overall confidence
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            # Create reasoning chain
            reasoning_chain = ReasoningChain(
                chain_id=chain_id,
                initial_query=query,
                reasoning_steps=reasoning_steps,
                final_conclusion=inference["conclusion"],
                confidence_score=overall_confidence,
                supporting_memories=[m.slice_id for m in context_memories],
                created_at=datetime.now().isoformat()
            )
            
            # Store reasoning chain
            with self.chain_lock:
                self.reasoning_chains[chain_id] = reasoning_chain
            
            # Persist to database
            self._store_reasoning_chain(reasoning_chain, persona_id, user_id)
            
            self._log("generate_reasoning_chain", user_id, persona_id, "reasoning_chain", chain_id,
                     {"query_length": len(query), "context_memories": len(context_memories),
                      "confidence_score": overall_confidence})
            
            return reasoning_chain
            
        except Exception as e:
            self._log("generate_reasoning_chain", user_id, persona_id, "reasoning_chain", chain_id,
                     {"query_length": len(query)}, result="failure", error=e)
            raise VaultError(f"Reasoning chain generation failed: {e}")

    def _identify_patterns(self, memories: List[MemorySlice]) -> List[Dict[str, Any]]:
        """Identify patterns in retrieved memories"""
        patterns = []
        
        try:
            if not memories:
                return patterns
            
            # Pattern 1: Memory type distribution
            type_counts = {}
            for memory in memories:
                type_counts[memory.memory_type] = type_counts.get(memory.memory_type, 0) + 1
            
            if type_counts:
                dominant_type = max(type_counts.items(), key=lambda x: x[1])
                patterns.append({
                    "type": "memory_type_distribution",
                    "description": f"Dominant memory type: {dominant_type[0]} ({dominant_type[1]} instances)",
                    "data": type_counts
                })
            
            # Pattern 2: Temporal clustering
            timestamps = [datetime.fromisoformat(m.created_at.replace('Z', '+00:00').replace('+00:00', '')) for m in memories]
            if len(timestamps) > 1:
                time_deltas = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
                avg_delta = sum(time_deltas) / len(time_deltas)
                patterns.append({
                    "type": "temporal_clustering",
                    "description": f"Average time between memories: {avg_delta:.1f} seconds",
                    "data": {"average_delta_seconds": avg_delta, "memory_count": len(memories)}
                })
            
            # Pattern 3: Content similarity clustering
            if len(memories) > 2:
                content_similarities = []
                for i in range(len(memories)):
                    for j in range(i+1, len(memories)):
                        if memories[i].embedding_vector and memories[j].embedding_vector:
                            sim = self._cosine_similarity(memories[i].embedding_vector, memories[j].embedding_vector)
                            content_similarities.append(sim)
                
                if content_similarities:
                    avg_similarity = sum(content_similarities) / len(content_similarities)
                    patterns.append({
                        "type": "content_similarity",
                        "description": f"Average content similarity: {avg_similarity:.3f}",
                        "data": {"average_similarity": avg_similarity, "comparisons": len(content_similarities)}
                    })
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Pattern identification error: {e}")
        
        return patterns

    def _perform_logical_inference(self, query: str, memories: List[MemorySlice], 
                                 patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform logical inference based on query, memories, and patterns"""
        try:
            # Simple rule-based inference for now
            # In a production system, this would be more sophisticated
            
            confidence = 0.5
            conclusions = []
            
            # Inference based on memory types
            if memories:
                memory_types = [m.memory_type for m in memories]
                if "episodic" in memory_types:
                    conclusions.append("Based on episodic memories, specific experiences are relevant")
                    confidence += 0.1
                
                if "semantic" in memory_types:
                    conclusions.append("Semantic knowledge provides contextual understanding")
                    confidence += 0.1
                
                if "procedural" in memory_types:
                    conclusions.append("Procedural knowledge suggests actionable approaches")
                    confidence += 0.1
            
            # Inference based on patterns
            for pattern in patterns:
                if pattern["type"] == "content_similarity" and pattern["data"]["average_similarity"] > 0.8:
                    conclusions.append("High content similarity suggests consistent context")
                    confidence += 0.1
                
                if pattern["type"] == "temporal_clustering" and pattern["data"]["average_delta_seconds"] < 3600:
                    conclusions.append("Temporal clustering suggests related sequence of events")
                    confidence += 0.1
            
            # Generate final conclusion
            if conclusions:
                final_conclusion = f"Analysis of {len(memories)} relevant memories reveals: " + "; ".join(conclusions)
            else:
                final_conclusion = f"Limited context available for query: '{query[:100]}...'"
                confidence = 0.3
            
            return {
                "conclusion": final_conclusion,
                "confidence": min(confidence, 1.0),
                "reasoning_elements": conclusions
            }
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Logical inference error: {e}")
            return {
                "conclusion": f"Unable to perform inference for query: {query[:100]}...",
                "confidence": 0.1,
                "reasoning_elements": []
            }

    def _store_reasoning_chain(self, chain: ReasoningChain, persona_id: str, user_id: str):
        """Store reasoning chain in database"""
        try:
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO reasoning_chains
                    (chain_id, persona_id, user_id, initial_query, reasoning_steps,
                     final_conclusion, confidence_score, supporting_memories, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chain.chain_id, persona_id, user_id, chain.initial_query,
                    json.dumps(chain.reasoning_steps), chain.final_conclusion,
                    chain.confidence_score, json.dumps(chain.supporting_memories),
                    chain.created_at
                ))
                conn.commit()
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to store reasoning chain: {e}")

    def get_reasoning_chain(self, chain_id: str) -> Optional[ReasoningChain]:
        """Retrieve stored reasoning chain"""
        try:
            with self.chain_lock:
                if chain_id in self.reasoning_chains:
                    return self.reasoning_chains[chain_id]
            
            # Load from database
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                cursor = conn.execute("""
                    SELECT initial_query, reasoning_steps, final_conclusion,
                           confidence_score, supporting_memories, created_at
                    FROM reasoning_chains WHERE chain_id = ?
                """, (chain_id,))
                row = cursor.fetchone()
                
                if row:
                    chain = ReasoningChain(
                        chain_id=chain_id,
                        initial_query=row[0],
                        reasoning_steps=json.loads(row[1]),
                        final_conclusion=row[2],
                        confidence_score=row[3],
                        supporting_memories=json.loads(row[4]),
                        created_at=row[5]
                    )
                    
                    with self.chain_lock:
                        self.reasoning_chains[chain_id] = chain
                    
                    return chain
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to retrieve reasoning chain {chain_id}: {e}")
            return None

    def optimize_memory_storage(self) -> Dict[str, Any]:
        """Optimize memory storage by consolidating and cleaning up old entries"""
        try:
            start_time = datetime.now()
            
            # Clean up old reasoning chains (older than 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            deleted_chains = 0
            
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                cursor = conn.execute("""
                    DELETE FROM reasoning_chains 
                    WHERE created_at < ?
                """, (cutoff_date.isoformat(),))
                deleted_chains = cursor.rowcount
                
                # Clean up memory slices with very low relevance scores (< 0.1) and no recent access
                old_cutoff = datetime.now() - timedelta(days=7)
                cursor = conn.execute("""
                    DELETE FROM memory_vectors 
                    WHERE relevance_score < 0.1 
                    AND last_accessed < ? 
                    AND retrieval_count = 0
                """, (old_cutoff.isoformat(),))
                deleted_memories = cursor.rowcount
                
                # Update relevance scores based on retrieval patterns
                conn.execute("""
                    UPDATE memory_vectors 
                    SET relevance_score = CASE 
                        WHEN retrieval_count > 10 THEN MIN(1.0, relevance_score + 0.1)
                        WHEN retrieval_count > 5 THEN MIN(1.0, relevance_score + 0.05)
                        WHEN retrieval_count = 0 AND last_accessed < ? THEN MAX(0.1, relevance_score - 0.05)
                        ELSE relevance_score
                    END
                """, (old_cutoff.isoformat(),))
                updated_scores = cursor.rowcount
                
                conn.commit()
            
            # Clear in-memory caches
            with self.chain_lock:
                old_chains = [k for k, v in self.reasoning_chains.items() 
                            if datetime.fromisoformat(v.created_at) < cutoff_date]
                for chain_id in old_chains:
                    del self.reasoning_chains[chain_id]
            
            # Calculate optimization results
            optimization_time = (datetime.now() - start_time).total_seconds()
            
            results = {
                "deleted_chains": deleted_chains,
                "deleted_memories": deleted_memories,
                "updated_scores": updated_scores,
                "optimization_time_seconds": optimization_time,
                "timestamp": datetime.now().isoformat(),
                "cache_cleared": len(old_chains)
            }
            
            self._log("optimize_memory_storage", "system", None, "optimization", None, results)
            
            return results
            
        except Exception as e:
            self._log("optimize_memory_storage", "system", None, "optimization", None, {},
                     result="failure", error=e)
            raise VaultError(f"Memory optimization failed: {e}")

    def get_memory_statistics(self, persona_id: str, user_id: str) -> Dict[str, Any]:
        """Get comprehensive memory statistics for a persona"""
        try:
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                # Memory slice statistics
                cursor = conn.execute("""
                    SELECT memory_type, COUNT(*), AVG(relevance_score), 
                           AVG(retrieval_count), MAX(last_accessed)
                    FROM memory_vectors 
                    WHERE persona_id = ? AND user_id = ?
                    GROUP BY memory_type
                """, (persona_id, user_id))
                
                memory_stats = {}
                for row in cursor.fetchall():
                    memory_stats[row[0]] = {
                        "count": row[1],
                        "avg_relevance": round(row[2], 3) if row[2] else 0.0,
                        "avg_retrieval_count": round(row[3], 1) if row[3] else 0.0,
                        "last_accessed": row[4]
                    }
                
                # Total statistics
                cursor = conn.execute("""
                    SELECT COUNT(*), AVG(relevance_score), SUM(retrieval_count)
                    FROM memory_vectors 
                    WHERE persona_id = ? AND user_id = ?
                """, (persona_id, user_id))
                
                total_row = cursor.fetchone()
                total_stats = {
                    "total_slices": total_row[0] if total_row[0] else 0,
                    "avg_relevance": round(total_row[1], 3) if total_row[1] else 0.0,
                    "total_retrievals": total_row[2] if total_row[2] else 0
                }
                
                # Reasoning chain statistics
                cursor = conn.execute("""
                    SELECT COUNT(*), AVG(confidence_score)
                    FROM reasoning_chains
                    WHERE persona_id = ? AND user_id = ?
                """, (persona_id, user_id))
                
                chain_row = cursor.fetchone()
                chain_stats = {
                    "total_chains": chain_row[0] if chain_row[0] else 0,
                    "avg_confidence": round(chain_row[1], 3) if chain_row[1] else 0.0
                }
            
            return {
                "memory_by_type": memory_stats,
                "totals": total_stats,
                "reasoning_chains": chain_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to get memory statistics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}