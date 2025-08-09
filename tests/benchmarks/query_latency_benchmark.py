#!/usr/bin/env python3
"""
Query Latency Benchmark for Semantic Retrieval System
Measures query response times under various conditions
"""

import asyncio
import json
import time
import statistics
import argparse
from typing import List, Dict, Any
import psycopg2
import redis
from sentence_transformers import SentenceTransformer
import numpy as np

class QueryLatencyBenchmark:
    def __init__(self, postgres_config: Dict[str, Any], redis_config: Dict[str, Any]):
        self.postgres_config = postgres_config
        self.redis_config = redis_config
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.query_times = []
        
    def setup_test_data(self, num_records: int = 10000):
        """Setup test data for benchmarking"""
        print(f"Setting up {num_records} test records...")
        
        conn = psycopg2.connect(**self.postgres_config)
        cur = conn.cursor()
        
        # Create test table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_memories (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                embedding VECTOR(384),
                agent_id VARCHAR(50),
                importance FLOAT DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        
        # Clear existing test data
        cur.execute("DELETE FROM benchmark_memories")
        
        # Generate test data
        test_queries = [
            "User wants to schedule a meeting",
            "Database connection error occurred", 
            "System performance is degrading",
            "New feature request submitted",
            "Security vulnerability detected",
            "Memory usage is high",
            "API response time increased",
            "User authentication failed",
            "Data backup completed successfully",
            "Configuration update required"
        ] * (num_records // 10 + 1)
        
        batch_size = 100
        for i in range(0, num_records, batch_size):
            batch = test_queries[i:i+batch_size]
            
            # Generate embeddings
            embeddings = self.model.encode(batch)
            
            # Insert batch
            for j, (content, embedding) in enumerate(zip(batch, embeddings)):
                agent_id = ['alden', 'alice', 'sentry', 'mimic'][j % 4]
                importance = np.random.uniform(0.1, 1.0)
                
                cur.execute("""
                    INSERT INTO benchmark_memories (content, embedding, agent_id, importance)
                    VALUES (%s, %s, %s, %s)
                """, (content, embedding.tolist(), agent_id, importance))
                
            if i % 1000 == 0:
                print(f"Inserted {i + len(batch)} records...")
                
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Test data setup complete: {num_records} records")
        
    def benchmark_semantic_search(self, query: str, top_k: int = 10) -> float:
        """Benchmark semantic search query"""
        start_time = time.perf_counter()
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Connect to database
            conn = psycopg2.connect(**self.postgres_config)
            cur = conn.cursor()
            
            # Perform semantic search
            cur.execute("""
                SELECT content, agent_id, importance,
                       embedding <-> %s as distance
                FROM benchmark_memories
                ORDER BY embedding <-> %s
                LIMIT %s
            """, (query_embedding.tolist(), query_embedding.tolist(), top_k))
            
            results = cur.fetchall()
            
            cur.close()
            conn.close()
            
            end_time = time.perf_counter()
            query_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            return query_time
            
        except Exception as e:
            print(f"Query failed: {e}")
            return -1
            
    def benchmark_hybrid_search(self, query: str, top_k: int = 10) -> float:
        """Benchmark hybrid search (semantic + keyword)"""
        start_time = time.perf_counter()
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Connect to database
            conn = psycopg2.connect(**self.postgres_config)
            cur = conn.cursor()
            
            # Perform hybrid search
            cur.execute("""
                SELECT content, agent_id, importance,
                       (embedding <-> %s) * 0.7 + 
                       (1 - similarity(content, %s)) * 0.3 as hybrid_score
                FROM benchmark_memories
                WHERE content %% %s
                ORDER BY hybrid_score
                LIMIT %s
            """, (query_embedding.tolist(), query, query, top_k))
            
            results = cur.fetchall()
            
            cur.close()
            conn.close()
            
            end_time = time.perf_counter()
            query_time = (end_time - start_time) * 1000
            
            return query_time
            
        except Exception as e:
            print(f"Hybrid query failed: {e}")
            return -1
            
    def benchmark_filtered_search(self, query: str, agent_id: str, min_importance: float, top_k: int = 10) -> float:
        """Benchmark filtered semantic search"""
        start_time = time.perf_counter()
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])[0]
            
            # Connect to database
            conn = psycopg2.connect(**self.postgres_config)
            cur = conn.cursor()
            
            # Perform filtered search
            cur.execute("""
                SELECT content, agent_id, importance,
                       embedding <-> %s as distance
                FROM benchmark_memories
                WHERE agent_id = %s AND importance >= %s
                ORDER BY embedding <-> %s
                LIMIT %s
            """, (query_embedding.tolist(), agent_id, min_importance, query_embedding.tolist(), top_k))
            
            results = cur.fetchall()
            
            cur.close()
            conn.close()
            
            end_time = time.perf_counter()
            query_time = (end_time - start_time) * 1000
            
            return query_time
            
        except Exception as e:
            print(f"Filtered query failed: {e}")
            return -1
            
    def run_benchmark(self, num_queries: int = 1000) -> Dict[str, Any]:
        """Run comprehensive query latency benchmark"""
        print(f"Running query latency benchmark with {num_queries} queries...")
        
        test_queries = [
            "schedule meeting tomorrow",
            "database performance issues",
            "user authentication error",
            "system memory usage high",
            "API endpoint response slow",
            "security vulnerability found",
            "backup process failed",
            "configuration needs update",
            "new feature implementation",
            "error handling improvement"
        ]
        
        agents = ['alden', 'alice', 'sentry', 'mimic']
        
        # Benchmark different query types
        semantic_times = []
        hybrid_times = []
        filtered_times = []
        
        print("Running semantic search benchmark...")
        for i in range(num_queries // 3):
            query = test_queries[i % len(test_queries)]
            query_time = self.benchmark_semantic_search(query)
            if query_time > 0:
                semantic_times.append(query_time)
                
        print("Running hybrid search benchmark...")
        for i in range(num_queries // 3):
            query = test_queries[i % len(test_queries)]
            query_time = self.benchmark_hybrid_search(query)
            if query_time > 0:
                hybrid_times.append(query_time)
                
        print("Running filtered search benchmark...")
        for i in range(num_queries // 3):
            query = test_queries[i % len(test_queries)]
            agent = agents[i % len(agents)]
            importance = 0.5
            query_time = self.benchmark_filtered_search(query, agent, importance)
            if query_time > 0:
                filtered_times.append(query_time)
                
        # Calculate statistics
        def calculate_stats(times: List[float]) -> Dict[str, float]:
            if not times:
                return {"count": 0, "avg": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}
                
            times.sort()
            return {
                "count": len(times),
                "avg": statistics.mean(times),
                "min": min(times),
                "max": max(times),
                "p50": times[int(len(times) * 0.5)],
                "p95": times[int(len(times) * 0.95)],
                "p99": times[int(len(times) * 0.99)]
            }
            
        results = {
            "timestamp": time.time(),
            "total_queries": len(semantic_times) + len(hybrid_times) + len(filtered_times),
            "semantic_search": calculate_stats(semantic_times),
            "hybrid_search": calculate_stats(hybrid_times), 
            "filtered_search": calculate_stats(filtered_times),
            "overall_stats": {
                "avg_query_time": statistics.mean(semantic_times + hybrid_times + filtered_times) if semantic_times or hybrid_times or filtered_times else 0,
                "p95_query_time": sorted(semantic_times + hybrid_times + filtered_times)[int(len(semantic_times + hybrid_times + filtered_times) * 0.95)] if semantic_times or hybrid_times or filtered_times else 0,
                "p99_query_time": sorted(semantic_times + hybrid_times + filtered_times)[int(len(semantic_times + hybrid_times + filtered_times) * 0.99)] if semantic_times or hybrid_times or filtered_times else 0,
                "queries_per_second": (len(semantic_times) + len(hybrid_times) + len(filtered_times)) / (sum(semantic_times + hybrid_times + filtered_times) / 1000) if semantic_times or hybrid_times or filtered_times else 0
            }
        }
        
        return results
        
    def cleanup(self):
        """Cleanup test data"""
        print("Cleaning up test data...")
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS benchmark_memories")
            conn.commit()
            cur.close()
            conn.close()
            print("Cleanup complete")
        except Exception as e:
            print(f"Cleanup error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Query Latency Benchmark')
    parser.add_argument('--output', default='query-latency-results.json', help='Output file for results')
    parser.add_argument('--queries', type=int, default=1000, help='Number of queries to benchmark')
    parser.add_argument('--records', type=int, default=10000, help='Number of test records to create')
    parser.add_argument('--skip-setup', action='store_true', help='Skip test data setup')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup test data after benchmark')
    
    args = parser.parse_args()
    
    # Configuration
    postgres_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'hearthlink_test_semantic',
        'user': 'postgres',
        'password': 'hearthlink_test_pass'
    }
    
    redis_config = {
        'host': 'localhost',
        'port': 6379,
        'password': 'redis_test_pass',
        'db': 2
    }
    
    # Run benchmark
    benchmark = QueryLatencyBenchmark(postgres_config, redis_config)
    
    try:
        if not args.skip_setup:
            benchmark.setup_test_data(args.records)
            
        results = benchmark.run_benchmark(args.queries)
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nBenchmark Results:")
        print(f"Total Queries: {results['total_queries']}")
        print(f"Average Query Time: {results['overall_stats']['avg_query_time']:.3f}ms")
        print(f"P95 Query Time: {results['overall_stats']['p95_query_time']:.3f}ms")
        print(f"P99 Query Time: {results['overall_stats']['p99_query_time']:.3f}ms")
        print(f"Queries per Second: {results['overall_stats']['queries_per_second']:.1f}")
        
        print(f"\nResults saved to: {args.output}")
        
    finally:
        if args.cleanup:
            benchmark.cleanup()

if __name__ == "__main__":
    main()