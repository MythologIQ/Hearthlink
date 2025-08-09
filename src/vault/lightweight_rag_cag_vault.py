"""
Lightweight RAG/CAG Enhanced Vault System for Hearthlink
Implements Retrieval-Augmented Generation and Chain-of-Thought Augmentation
Without heavy ML dependencies - uses text similarity instead of embeddings
"""

import os
import json
import hashlib
import re
from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import threading
from collections import Counter
import math

from .vault_enhanced import VaultEnhanced, VaultError

@dataclass
class MemorySlice:
    """Enhanced memory slice with RAG/CAG capabilities"""
    slice_id: str
    content: str
    memory_type: str  # 'episodic', 'semantic', 'procedural', 'working'
    created_at: str
    last_accessed: str
    keywords: List[str]
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
    query_keywords: List[str]

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

class LightweightRAGCAGVault(VaultEnhanced):
    """
    Lightweight Enhanced Vault with RAG and CAG capabilities
    Uses TF-IDF and keyword matching instead of neural embeddings
    """
    
    def __init__(self, config: Dict[str, Any], logger=None):
        super().__init__(config, logger)
        
        # RAG/CAG specific configuration
        self.max_retrieval_results = config.get("rag_config", {}).get("max_results", 10)
        self.similarity_threshold = config.get("rag_config", {}).get("similarity_threshold", 0.3)
        self.keyword_boost = config.get("rag_config", {}).get("keyword_boost", 1.5)
        
        # Initialize vector database (SQLite with text operations)
        self._init_vector_db()
        
        # Reasoning chain cache
        self.reasoning_chains: Dict[str, ReasoningChain] = {}
        self.chain_lock = threading.RLock()
        
        # Simple stopwords list
        self.stopwords = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those'
        ])

    def _log_message(self, level: str, message: str):
        """Helper method to handle logger compatibility"""
        if not self.logger:
            return
        
        if hasattr(self.logger, 'logger'):
            # HearthlinkLogger
            if level == 'info':
                self.logger.logger.info(message)
            elif level == 'warning':
                self.logger.logger.warning(message)
            elif level == 'error':
                self.logger.logger.error(message)
        else:
            # Standard logger
            if level == 'info':
                self.logger.info(message)
            elif level == 'warning':
                self.logger.warning(message)
            elif level == 'error':
                self.logger.error(message)

    def _init_vector_db(self):
        """Initialize SQLite database for text-based operations"""
        try:
            vector_db_path = self.config.get("storage", {}).get("vector_db_path", 
                                                               str(self.storage_path.parent / "text_vectors.db"))
            self.vector_db_path = Path(vector_db_path)
            self.vector_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create database schema
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_slices (
                        slice_id TEXT PRIMARY KEY,
                        persona_id TEXT,
                        user_id TEXT,
                        content TEXT,
                        memory_type TEXT,
                        keywords TEXT,  -- JSON string of keywords
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
                conn.execute("CREATE INDEX IF NOT EXISTS idx_slices_persona ON memory_slices(persona_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_slices_type ON memory_slices(memory_type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_slices_score ON memory_slices(relevance_score)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_chains_persona ON reasoning_chains(persona_id)")
                
                # Full-text search for content
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                        slice_id, content, keywords
                    )
                """)
                
                conn.commit()
                
            self._log_message('info', f"Text-based vector database initialized at {vector_db_path}")
                
        except Exception as e:
            self._log_message('error', f"Failed to initialize vector database: {e}")
            raise VaultError(f"Vector database initialization failed: {e}")

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using simple NLP techniques"""
        try:
            # Convert to lowercase and split into words
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Remove stopwords
            filtered_words = [w for w in words if w not in self.stopwords]
            
            # Count frequency and return top keywords
            word_counts = Counter(filtered_words)
            
            # Return top 10 most frequent words as keywords
            keywords = [word for word, count in word_counts.most_common(10)]
            
            return keywords
            
        except Exception as e:
            self._log_message('warning', f"Keyword extraction failed: {e}")
            return []

    def _calculate_text_similarity(self, text1: str, text2: str, keywords1: List[str], keywords2: List[str]) -> float:
        """Calculate similarity between two texts using TF-IDF-like approach"""
        try:
            # Keyword overlap similarity
            set1, set2 = set(keywords1), set(keywords2)
            keyword_similarity = len(set1.intersection(set2)) / max(len(set1.union(set2)), 1)
            
            # Simple word overlap
            words1 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower()))
            words2 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower()))
            word_similarity = len(words1.intersection(words2)) / max(len(words1.union(words2)), 1)
            
            # Combine similarities with keyword boost
            combined_similarity = (keyword_similarity * self.keyword_boost + word_similarity) / (self.keyword_boost + 1)
            
            return combined_similarity
            
        except Exception as e:
            self._log_message('warning', f"Similarity calculation failed: {e}")
            return 0.0

    def store_memory_slice(self, persona_id: str, user_id: str, content: str, 
                          memory_type: str = "episodic", 
                          metadata: Dict[str, Any] = None) -> str:
        """Store a memory slice with keyword extraction"""
        slice_id = f"slice_{hashlib.md5(f'{persona_id}_{user_id}_{content}_{datetime.now().isoformat()}'.encode()).hexdigest()[:12]}"
        
        try:
            # Extract keywords
            keywords = self._extract_keywords(content)
            
            # Create memory slice
            memory_slice = MemorySlice(
                slice_id=slice_id,
                content=content,
                memory_type=memory_type,
                created_at=datetime.now().isoformat(),
                last_accessed=datetime.now().isoformat(),
                keywords=keywords,
                relevance_score=0.5,  # Initial relevance
                metadata=metadata or {},
                retrieval_count=0
            )
            
            # Store in database
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                # Store in main table
                conn.execute("""
                    INSERT OR REPLACE INTO memory_slices 
                    (slice_id, persona_id, user_id, content, memory_type, 
                     keywords, relevance_score, created_at, last_accessed, 
                     retrieval_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    slice_id, persona_id, user_id, content, memory_type,
                    json.dumps(keywords),
                    memory_slice.relevance_score,
                    memory_slice.created_at,
                    memory_slice.last_accessed,
                    memory_slice.retrieval_count,
                    json.dumps(memory_slice.metadata)
                ))
                
                # Store in FTS table for full-text search
                conn.execute("""
                    INSERT OR REPLACE INTO memory_fts (slice_id, content, keywords)
                    VALUES (?, ?, ?)
                """, (slice_id, content, ' '.join(keywords)))
                
                conn.commit()
            
            self._log("store_memory_slice", user_id, persona_id, "memory_slice", slice_id, 
                     {"content_length": len(content), "memory_type": memory_type, "keywords_count": len(keywords)})
            
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
        RAG: Retrieve memories similar to query using text similarity
        """
        start_time = datetime.now()
        
        try:
            # Extract query keywords
            query_keywords = self._extract_keywords(query)
            
            max_results = max_results or self.max_retrieval_results
            min_similarity = min_similarity or self.similarity_threshold
            
            # Build base query
            query_sql = """
                SELECT slice_id, persona_id, user_id, content, memory_type,
                       keywords, relevance_score, created_at, last_accessed,
                       retrieval_count, metadata
                FROM memory_slices 
                WHERE persona_id = ? AND user_id = ?
            """
            query_params = [persona_id, user_id]
            
            if memory_types:
                placeholders = ','.join(['?' for _ in memory_types])
                query_sql += f" AND memory_type IN ({placeholders})"
                query_params.extend(memory_types)
            
            # First, try FTS search for exact matches
            fts_results = set()
            if query_keywords:
                fts_query = ' OR '.join(query_keywords)
                with sqlite3.connect(str(self.vector_db_path)) as conn:
                    cursor = conn.execute("""
                        SELECT slice_id FROM memory_fts 
                        WHERE memory_fts MATCH ?
                        LIMIT ?
                    """, (fts_query, max_results * 2))
                    fts_results = set(row[0] for row in cursor.fetchall())
            
            # Get all candidate memories
            with sqlite3.connect(str(self.vector_db_path)) as conn:
                cursor = conn.execute(query_sql, query_params)
                rows = cursor.fetchall()
            
            # Calculate similarities and rank
            similar_memories = []
            similarity_scores = []
            
            for row in rows:
                try:
                    stored_keywords = json.loads(row[5]) if row[5] else []
                    
                    # Calculate text similarity
                    similarity = self._calculate_text_similarity(query, row[3], query_keywords, stored_keywords)
                    
                    # Boost similarity if found in FTS search
                    if row[0] in fts_results:
                        similarity = min(1.0, similarity * 1.2)
                    
                    # Boost based on relevance score
                    boosted_similarity = similarity * (0.5 + row[6] * 0.5)
                    
                    if boosted_similarity >= min_similarity:
                        memory_slice = MemorySlice(
                            slice_id=row[0],
                            content=row[3],
                            memory_type=row[4],
                            created_at=row[7],
                            last_accessed=row[8],
                            keywords=stored_keywords,
                            relevance_score=row[6],
                            metadata=json.loads(row[10]) if row[10] else {},
                            retrieval_count=row[9]
                        )
                        
                        similar_memories.append(memory_slice)
                        similarity_scores.append(boosted_similarity)
                        
                except Exception as e:
                    self._log_message('warning', f"Error processing memory slice {row[0]}: {e}")
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
                query_keywords=query_keywords
            )
            
            self._log("retrieve_similar_memories", user_id, persona_id, "retrieval", None,
                     {"query_length": len(query), "results_count": len(similar_memories), 
                      "retrieval_time_ms": retrieval_time, "query_keywords": len(query_keywords)})
            
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
                        UPDATE memory_slices 
                        SET retrieval_count = retrieval_count + 1,
                            last_accessed = ?
                        WHERE slice_id = ?
                    """, (datetime.now().isoformat(), slice_id))
                conn.commit()
        except Exception as e:
            self._log_message('warning', f"Failed to update retrieval counts: {e}")

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
            query_keywords = self._extract_keywords(query)
            reasoning_steps.append({
                "step": 1,
                "type": "query_analysis",
                "description": "Analyzing query and extracting key concepts",
                "input": query,
                "output": f"Extracted {len(query_keywords)} key concepts: {', '.join(query_keywords[:5])}",
                "confidence": 0.9,
                "concepts": query_keywords
            })
            confidence_scores.append(0.9)
            
            # Step 2: Memory retrieval analysis
            if context_memories:
                memory_types = [m.memory_type for m in context_memories]
                type_distribution = Counter(memory_types)
                reasoning_steps.append({
                    "step": 2,
                    "type": "memory_retrieval",
                    "description": "Retrieved and analyzed relevant memories",
                    "input": f"Query: {query}",
                    "output": f"Found {len(context_memories)} relevant memories: {dict(type_distribution)}",
                    "confidence": min(0.8, sum(m.relevance_score for m in context_memories) / len(context_memories)),
                    "memory_distribution": dict(type_distribution)
                })
                confidence_scores.append(reasoning_steps[-1]["confidence"])
            
            # Step 3: Pattern recognition
            patterns = self._identify_patterns(context_memories, query_keywords)
            reasoning_steps.append({
                "step": 3,
                "type": "pattern_recognition",
                "description": "Identifying patterns and relationships in retrieved memories",
                "input": [m.content[:50] + "..." for m in context_memories[:3]],
                "output": f"Identified {len(patterns)} patterns in memory context",
                "confidence": 0.7,
                "patterns": patterns
            })
            confidence_scores.append(0.7)
            
            # Step 4: Logical inference
            inference = self._perform_logical_inference(query, query_keywords, context_memories, patterns)
            reasoning_steps.append({
                "step": 4,
                "type": "logical_inference",
                "description": "Performing logical inference based on patterns and context",
                "input": {"query": query, "patterns": len(patterns), "memories": len(context_memories)},
                "output": inference["conclusion"],
                "confidence": inference["confidence"],
                "reasoning_elements": inference["reasoning_elements"]
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
                      "confidence_score": overall_confidence, "query_keywords": len(query_keywords)})
            
            return reasoning_chain
            
        except Exception as e:
            self._log("generate_reasoning_chain", user_id, persona_id, "reasoning_chain", chain_id,
                     {"query_length": len(query)}, result="failure", error=e)
            raise VaultError(f"Reasoning chain generation failed: {e}")

    def _identify_patterns(self, memories: List[MemorySlice], query_keywords: List[str]) -> List[Dict[str, Any]]:
        """Identify patterns in retrieved memories"""
        patterns = []
        
        try:
            if not memories:
                return patterns
            
            # Pattern 1: Memory type distribution
            type_counts = Counter(m.memory_type for m in memories)
            if type_counts:
                dominant_type = type_counts.most_common(1)[0]
                patterns.append({
                    "type": "memory_type_distribution",
                    "description": f"Dominant memory type: {dominant_type[0]} ({dominant_type[1]} instances)",
                    "data": dict(type_counts),
                    "confidence": 0.8
                })
            
            # Pattern 2: Keyword overlap analysis
            all_keywords = []
            for memory in memories:
                all_keywords.extend(memory.keywords)
            
            keyword_counts = Counter(all_keywords)
            common_keywords = keyword_counts.most_common(5)
            
            # Find keywords that overlap with query
            query_overlap = [kw for kw, count in common_keywords if kw in query_keywords]
            
            if common_keywords:
                patterns.append({
                    "type": "keyword_clustering",
                    "description": f"Common themes: {', '.join([kw for kw, _ in common_keywords[:3]])}",
                    "data": {
                        "common_keywords": dict(common_keywords),
                        "query_overlap": query_overlap,
                        "overlap_ratio": len(query_overlap) / max(len(query_keywords), 1)
                    },
                    "confidence": 0.7
                })
            
            # Pattern 3: Temporal clustering
            if len(memories) > 1:
                timestamps = []
                for memory in memories:
                    try:
                        ts = datetime.fromisoformat(memory.created_at.replace('Z', ''))
                        timestamps.append(ts)
                    except:
                        continue
                
                if len(timestamps) > 1:
                    timestamps.sort()
                    time_deltas = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                                 for i in range(len(timestamps)-1)]
                    avg_delta = sum(time_deltas) / len(time_deltas)
                    
                    patterns.append({
                        "type": "temporal_clustering",
                        "description": f"Average time between memories: {avg_delta/3600:.1f} hours",
                        "data": {
                            "average_delta_hours": avg_delta/3600,
                            "memory_span_hours": (timestamps[-1] - timestamps[0]).total_seconds()/3600,
                            "memory_count": len(timestamps)
                        },
                        "confidence": 0.6
                    })
            
            # Pattern 4: Relevance score clustering
            relevance_scores = [m.relevance_score for m in memories]
            if relevance_scores:
                avg_relevance = sum(relevance_scores) / len(relevance_scores)
                high_relevance_count = sum(1 for score in relevance_scores if score > 0.7)
                
                patterns.append({
                    "type": "relevance_distribution",
                    "description": f"Average relevance: {avg_relevance:.2f} ({high_relevance_count} high-relevance memories)",
                    "data": {
                        "average_relevance": avg_relevance,
                        "high_relevance_count": high_relevance_count,
                        "total_memories": len(memories)
                    },
                    "confidence": 0.8
                })
            
        except Exception as e:
            self._log_message('warning', f"Pattern identification error: {e}")
        
        return patterns

    def _perform_logical_inference(self, query: str, query_keywords: List[str], 
                                 memories: List[MemorySlice], 
                                 patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform logical inference based on query, memories, and patterns"""
        try:
            confidence = 0.4
            conclusions = []
            
            # Inference based on memory types
            if memories:
                memory_types = Counter(m.memory_type for m in memories)
                
                if memory_types["episodic"] > 0:
                    conclusions.append(f"Found {memory_types['episodic']} episodic memories providing specific experience context")
                    confidence += 0.1
                
                if memory_types["semantic"] > 0:
                    conclusions.append(f"Retrieved {memory_types['semantic']} semantic memories with conceptual knowledge")
                    confidence += 0.1
                
                if memory_types["procedural"] > 0:
                    conclusions.append(f"Identified {memory_types['procedural']} procedural memories suggesting actionable approaches")
                    confidence += 0.1
            
            # Inference based on patterns
            for pattern in patterns:
                if pattern["type"] == "keyword_clustering":
                    overlap_ratio = pattern["data"].get("overlap_ratio", 0)
                    if overlap_ratio > 0.5:
                        conclusions.append(f"Strong thematic alignment with {overlap_ratio:.1%} keyword overlap")
                        confidence += 0.15
                    elif overlap_ratio > 0.2:
                        conclusions.append(f"Moderate thematic connection with {overlap_ratio:.1%} keyword overlap")
                        confidence += 0.05
                
                if pattern["type"] == "relevance_distribution":
                    avg_relevance = pattern["data"]["average_relevance"]
                    if avg_relevance > 0.7:
                        conclusions.append("High-quality memory context supports strong inference")
                        confidence += 0.1
                    elif avg_relevance > 0.5:
                        conclusions.append("Moderate-quality memory context provides useful insights")
                        confidence += 0.05
                
                if pattern["type"] == "temporal_clustering":
                    span_hours = pattern["data"]["memory_span_hours"]
                    if span_hours < 24:
                        conclusions.append("Recent memory cluster suggests immediate relevance")
                        confidence += 0.1
                    elif span_hours < 168:  # 1 week
                        conclusions.append("Weekly memory pattern indicates ongoing relevance")
                        confidence += 0.05
            
            # Generate final conclusion based on analysis
            if conclusions:
                if len(memories) > 5:
                    memory_quality = "comprehensive"
                elif len(memories) > 2:
                    memory_quality = "sufficient"
                else:
                    memory_quality = "limited"
                
                final_conclusion = (f"Analysis of {len(memories)} {memory_quality} memories for query '{query[:50]}...' reveals: " + 
                                  "; ".join(conclusions[:3]))
                
                if len(query_keywords) > 3:
                    final_conclusion += f". Query complexity ({len(query_keywords)} key concepts) matches memory diversity."
                
            else:
                final_conclusion = f"Limited context available for query '{query[:50]}...'. Consider refining query or adding more relevant memories."
                confidence = 0.2
            
            return {
                "conclusion": final_conclusion,
                "confidence": min(confidence, 1.0),
                "reasoning_elements": conclusions
            }
            
        except Exception as e:
            self._log_message('warning', f"Logical inference error: {e}")
            return {
                "conclusion": f"Unable to perform complete inference for query: {query[:50]}...",
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
            self._log_message('warning', f"Failed to store reasoning chain: {e}")

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
            self._log_message('warning', f"Failed to retrieve reasoning chain {chain_id}: {e}")
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
                
                # Clean up memory slices with very low relevance scores (< 0.2) and no recent access
                old_cutoff = datetime.now() - timedelta(days=7)
                cursor = conn.execute("""
                    DELETE FROM memory_slices 
                    WHERE relevance_score < 0.2 
                    AND last_accessed < ? 
                    AND retrieval_count = 0
                """, (old_cutoff.isoformat(),))
                deleted_memories = cursor.rowcount
                
                # Update relevance scores based on retrieval patterns
                cursor = conn.execute("""
                    UPDATE memory_slices 
                    SET relevance_score = CASE 
                        WHEN retrieval_count > 10 THEN MIN(1.0, relevance_score + 0.1)
                        WHEN retrieval_count > 5 THEN MIN(1.0, relevance_score + 0.05)
                        WHEN retrieval_count = 0 AND last_accessed < ? THEN MAX(0.2, relevance_score - 0.05)
                        ELSE relevance_score
                    END
                """, (old_cutoff.isoformat(),))
                updated_scores = cursor.rowcount
                
                # Clean up FTS table to match memory_slices
                conn.execute("""
                    DELETE FROM memory_fts 
                    WHERE slice_id NOT IN (SELECT slice_id FROM memory_slices)
                """)
                
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
                    FROM memory_slices 
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
                    FROM memory_slices 
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
                "timestamp": datetime.now().isoformat(),
                "rag_enabled": True,
                "cag_enabled": True
            }
            
        except Exception as e:
            self._log_message('warning', f"Failed to get memory statistics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}