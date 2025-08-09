#!/usr/bin/env python3
"""
Performance Optimization Service for Hearthlink
Handles LLM response caching, prompt optimization, and system performance tuning
"""

import asyncio
import json
import hashlib
import logging
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
import concurrent.futures

class ResponseCache:
    """Intelligent caching system for LLM responses"""
    
    def __init__(self, cache_db_path: str = "/mnt/g/mythologiq/hearthlink/hearthlink_data/response_cache.db"):
        self.cache_db_path = cache_db_path
        self.setup_cache_db()
        self.logger = logging.getLogger("response_cache")
    
    def setup_cache_db(self):
        """Create cache database with optimized schema"""
        conn = sqlite3.connect(self.cache_db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS response_cache (
                hash_key TEXT PRIMARY KEY,
                prompt_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                model_used TEXT NOT NULL,
                response_time REAL NOT NULL,
                created_at INTEGER NOT NULL,
                last_used INTEGER NOT NULL,
                use_count INTEGER DEFAULT 1,
                expires_at INTEGER,
                UNIQUE(hash_key)
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_expires ON response_cache(expires_at);
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cache_last_used ON response_cache(last_used DESC);
        """)
        
        conn.commit()
        conn.close()
    
    def generate_cache_key(self, prompt: str, model: str, context: Dict[str, Any] = None) -> str:
        """Generate a cache key for the given prompt and context"""
        context_str = json.dumps(context or {}, sort_keys=True)
        cache_input = f"{prompt}|{model}|{context_str}"
        return hashlib.sha256(cache_input.encode()).hexdigest()
    
    def get_cached_response(self, prompt: str, model: str, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if available and valid"""
        cache_key = self.generate_cache_key(prompt, model, context)
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM response_cache 
                WHERE hash_key = ? AND (expires_at IS NULL OR expires_at > ?)
            """, (cache_key, int(time.time())))
            
            row = cursor.fetchone()
            
            if row:
                # Update usage statistics
                conn.execute("""
                    UPDATE response_cache 
                    SET last_used = ?, use_count = use_count + 1 
                    WHERE hash_key = ?
                """, (int(time.time()), cache_key))
                conn.commit()
                
                result = {
                    "response": row["response_text"],
                    "confidence": row["confidence"],
                    "model": row["model_used"],
                    "response_time": row["response_time"],
                    "cached": True,
                    "cache_hit": True,
                    "use_count": row["use_count"] + 1
                }
                
                self.logger.info(f"Cache HIT for prompt: {prompt[:50]}...")
                return result
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Cache retrieval error: {e}")
        
        return None
    
    def cache_response(self, prompt: str, response: str, model: str, response_time: float, 
                      confidence: float = 1.0, context: Dict[str, Any] = None, ttl_hours: int = 24):
        """Cache a response for future use"""
        cache_key = self.generate_cache_key(prompt, model, context)
        
        try:
            conn = sqlite3.connect(self.cache_db_path)
            
            expires_at = int(time.time()) + (ttl_hours * 3600) if ttl_hours > 0 else None
            
            conn.execute("""
                INSERT OR REPLACE INTO response_cache 
                (hash_key, prompt_text, response_text, confidence, model_used, response_time, 
                 created_at, last_used, expires_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_key, prompt, response, confidence, model, response_time,
                int(time.time()), int(time.time()), expires_at
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cached response for prompt: {prompt[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Cache storage error: {e}")
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            
            # Remove expired entries
            cursor = conn.execute("DELETE FROM response_cache WHERE expires_at IS NOT NULL AND expires_at < ?", 
                                (int(time.time()),))
            
            expired_count = cursor.rowcount
            
            # Remove old entries if cache is too large (keep only 1000 most recent)
            conn.execute("""
                DELETE FROM response_cache WHERE hash_key NOT IN (
                    SELECT hash_key FROM response_cache 
                    ORDER BY last_used DESC LIMIT 1000
                )
            """)
            
            conn.commit()
            conn.close()
            
            if expired_count > 0:
                self.logger.info(f"Cleaned up {expired_count} expired cache entries")
            
        except Exception as e:
            self.logger.error(f"Cache cleanup error: {e}")


class PromptOptimizer:
    """Optimizes prompts for better performance and accuracy"""
    
    def __init__(self):
        self.logger = logging.getLogger("prompt_optimizer")
        
        # Common optimizations
        self.optimizations = {
            "conciseness": {
                "patterns": [
                    (r"Could you please tell me", "Tell me"),
                    (r"I would like to know", "What is"),  
                    (r"Can you help me understand", "Explain"),
                ],
                "weight": 0.8
            },
            "specificity": {
                "patterns": [
                    (r"something", "specific details"),
                    (r"things", "specific items"),
                    (r"stuff", "information"),
                ],
                "weight": 0.9
            }
        }
    
    def optimize_prompt(self, prompt: str, context: Dict[str, Any] = None) -> Tuple[str, float]:
        """Optimize a prompt for better LLM performance"""
        original_prompt = prompt
        optimization_score = 1.0
        
        try:
            # Apply conciseness optimizations
            for pattern, replacement in self.optimizations["conciseness"]["patterns"]:
                import re
                if re.search(pattern, prompt, re.IGNORECASE):
                    prompt = re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)
                    optimization_score *= self.optimizations["conciseness"]["weight"]
            
            # Apply specificity optimizations  
            for pattern, replacement in self.optimizations["specificity"]["patterns"]:
                if re.search(pattern, prompt, re.IGNORECASE):
                    prompt = re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)
                    optimization_score *= self.optimizations["specificity"]["weight"]
            
            # Add context-aware optimizations
            if context and context.get("persona") == "alden":
                # Alden-specific optimizations
                if len(prompt) > 200:
                    prompt = prompt[:200] + "..."
                    optimization_score *= 0.9
                    
                # Add time context for better responses
                if "time" in prompt.lower() or "when" in prompt.lower():
                    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
                    prompt = f"Current time: {current_time}. {prompt}"
            
            if prompt != original_prompt:
                self.logger.info(f"Optimized prompt: {original_prompt[:50]}... -> {prompt[:50]}...")
            
            return prompt, optimization_score
            
        except Exception as e:
            self.logger.error(f"Prompt optimization error: {e}")
            return original_prompt, 1.0


class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self):
        self.cache = ResponseCache()
        self.prompt_optimizer = PromptOptimizer()
        self.logger = logging.getLogger("performance_optimizer")
        self.setup_logging()
        
        # Performance metrics
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
            "total_response_time": 0.0,
            "optimizations_applied": 0
        }
    
    def setup_logging(self):
        """Setup logging for performance optimization"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def optimize_llm_request(self, prompt: str, model: str = "llama3.2:3b", 
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize an LLM request with caching and prompt optimization"""
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        try:
            # Step 1: Check cache first
            cached_response = self.cache.get_cached_response(prompt, model, context)
            if cached_response:
                self.metrics["cache_hits"] += 1
                elapsed_time = time.time() - start_time
                self.metrics["total_response_time"] += elapsed_time
                return cached_response
            
            self.metrics["cache_misses"] += 1
            
            # Step 2: Optimize prompt
            optimized_prompt, optimization_score = self.prompt_optimizer.optimize_prompt(prompt, context)
            if optimized_prompt != prompt:
                self.metrics["optimizations_applied"] += 1
            
            # Step 3: Make optimized request to Alden backend
            response_data = await self._make_optimized_request(optimized_prompt, context)
            
            # Step 4: Calculate performance metrics
            elapsed_time = time.time() - start_time
            self.metrics["total_response_time"] += elapsed_time
            
            # Step 5: Cache the response if it's good
            if response_data.get("status") == "success":
                confidence = optimization_score * 0.9  # Slightly reduce confidence for cached responses
                self.cache.cache_response(
                    prompt=prompt,
                    response=response_data.get("response", ""),
                    model=model,
                    response_time=elapsed_time,
                    confidence=confidence,
                    context=context,
                    ttl_hours=24
                )
            
            # Step 6: Add performance metadata
            response_data.update({
                "cached": False,
                "cache_hit": False,
                "optimized": optimized_prompt != prompt,
                "optimization_score": optimization_score,
                "response_time": elapsed_time,
                "performance_optimized": True
            })
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"LLM optimization error: {e}")
            elapsed_time = time.time() - start_time
            self.metrics["total_response_time"] += elapsed_time
            
            return {
                "status": "error",
                "error": str(e),
                "response_time": elapsed_time,
                "cached": False,
                "performance_optimized": False
            }
    
    async def _make_optimized_request(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make an optimized request to the Alden backend"""
        try:
            payload = {
                "message": prompt,
                "user_id": context.get("user_id", "performance_optimizer"),
                "session_id": context.get("session_id", f"perf_{int(time.time())}"),
                "context": context or {}
            }
            
            # Create request with timeout
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                "http://localhost:8888/conversation",
                data=data,
                headers={"Content-Type": "application/json"}
            )
            
            # Make the request with timeout in a thread pool to keep it async
            def make_request():
                try:
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.status == 200:
                            return json.loads(response.read().decode('utf-8'))
                        else:
                            raise Exception(f"Backend returned status {response.status}")
                except urllib.error.URLError as e:
                    raise Exception(f"Backend request failed: {str(e)}")
            
            # Run in executor to maintain async behavior
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, make_request)
                return result
                        
        except Exception as e:
            raise Exception(f"Backend request failed: {str(e)}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        total_requests = self.metrics["total_requests"]
        
        metrics = {
            "total_requests": total_requests,
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "cache_hit_rate": (self.metrics["cache_hits"] / total_requests) if total_requests > 0 else 0,
            "average_response_time": (self.metrics["total_response_time"] / total_requests) if total_requests > 0 else 0,
            "optimizations_applied": self.metrics["optimizations_applied"],
            "optimization_rate": (self.metrics["optimizations_applied"] / total_requests) if total_requests > 0 else 0
        }
        
        return metrics
    
    async def cleanup_and_optimize(self):
        """Perform periodic cleanup and optimization"""
        try:
            # Clean up expired cache entries
            self.cache.cleanup_expired()
            
            # Reset metrics periodically (keep last 1000 requests in memory)
            if self.metrics["total_requests"] > 1000:
                scale_factor = 0.9
                for key in ["cache_hits", "cache_misses", "total_requests", "optimizations_applied"]:
                    self.metrics[key] = int(self.metrics[key] * scale_factor)
                self.metrics["total_response_time"] *= scale_factor
            
            self.logger.info("Performance optimization cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")


# Global optimizer instance
performance_optimizer = PerformanceOptimizer()


async def main():
    """Test the performance optimization system"""
    
    # Test cases
    test_prompts = [
        "What time is it right now?",
        "Could you please tell me what the current time is?",  # Should be optimized
        "What time is it right now?",  # Should hit cache
        "Tell me about artificial intelligence",
        "Can you help me understand how AI works?",  # Should be optimized
    ]
    
    print("🚀 Testing Performance Optimization System")
    print("=" * 50)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}")
        result = await performance_optimizer.optimize_llm_request(
            prompt=prompt,
            context={"persona": "alden", "user_id": "test_user"}
        )
        
        print(f"  ✅ Response: {result.get('response', 'N/A')[:100]}...")
        print(f"  ⚡ Cached: {result.get('cached', False)}")
        print(f"  🔧 Optimized: {result.get('optimized', False)}")
        print(f"  ⏱️ Time: {result.get('response_time', 0):.3f}s")
    
    # Show performance metrics
    print("\n" + "=" * 50)
    print("📊 Performance Metrics:")
    metrics = performance_optimizer.get_performance_metrics()
    for key, value in metrics.items():
        if "rate" in key or "time" in key:
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())