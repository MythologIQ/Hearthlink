#!/usr/bin/env python3
"""
Concurrent Agents Benchmark for Memory Sync Service
Tests multi-agent conflict resolution under load
"""

import asyncio
import json
import time
import argparse
import statistics
from typing import Dict, List, Any
import aiohttp
import random
from concurrent.futures import ThreadPoolExecutor
import threading

class ConcurrentAgentsBenchmark:
    def __init__(self, memory_sync_url: str = "http://localhost:8003"):
        self.memory_sync_url = memory_sync_url
        self.agents = ['alden', 'alice', 'sentry', 'mimic']
        self.results = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'operation_times': [],
            'agent_stats': {agent: {'operations': 0, 'conflicts': 0, 'avg_time': 0} for agent in self.agents}
        }
        self.lock = threading.Lock()
        
    async def create_memory_operation(self, session: aiohttp.ClientSession, agent_id: str, memory_id: str, operation_type: str = "create") -> Dict[str, Any]:
        """Create a memory sync operation"""
        
        sync_data = {
            'agentId': agent_id,
            'memoryId': memory_id,
            'operation': operation_type,
            'content': f'Test memory content from {agent_id} - {random.randint(1000, 9999)}',
            'importance': random.uniform(0.1, 1.0),
            'metadata': {
                'sessionId': f'sess_{random.randint(100, 999)}',
                'userId': f'user_{random.randint(10, 99)}',
                'timestamp': time.time()
            }
        }
        
        start_time = time.perf_counter()
        
        try:
            async with session.post(f"{self.memory_sync_url}/api/sync-memory", json=sync_data) as response:
                end_time = time.perf_counter()
                operation_time = (end_time - start_time) * 1000  # milliseconds
                
                result = await response.json()
                
                with self.lock:
                    self.results['total_operations'] += 1
                    self.results['operation_times'].append(operation_time)
                    self.results['agent_stats'][agent_id]['operations'] += 1
                    
                    if response.status == 200:
                        self.results['successful_operations'] += 1
                        
                        # Check if conflict was detected
                        if result.get('status') == 'conflict_pending':
                            self.results['conflicts_detected'] += 1
                            self.results['agent_stats'][agent_id]['conflicts'] += 1
                        elif result.get('conflictId'):
                            self.results['conflicts_resolved'] += 1
                            
                    else:
                        self.results['failed_operations'] += 1
                        
                return {
                    'success': response.status == 200,
                    'operation_time': operation_time,
                    'agent_id': agent_id,
                    'memory_id': memory_id,
                    'result': result
                }
                
        except Exception as e:
            end_time = time.perf_counter()
            operation_time = (end_time - start_time) * 1000
            
            with self.lock:
                self.results['total_operations'] += 1
                self.results['failed_operations'] += 1
                self.results['operation_times'].append(operation_time)
                
            return {
                'success': False,
                'operation_time': operation_time,
                'agent_id': agent_id,
                'memory_id': memory_id,
                'error': str(e)
            }
            
    async def create_conflict_scenario(self, session: aiohttp.ClientSession, memory_id: str) -> List[Dict[str, Any]]:
        """Create a deliberate conflict scenario with multiple agents"""
        
        # Select 2-3 agents to create conflict
        conflicting_agents = random.sample(self.agents, random.randint(2, 3))
        
        # Create simultaneous operations on the same memory
        tasks = []
        for agent in conflicting_agents:
            task = self.create_memory_operation(session, agent, memory_id, "update")
            tasks.append(task)
            
        # Execute operations simultaneously
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if not isinstance(r, Exception)]
        
    async def run_concurrent_operations(self, num_operations: int, conflict_rate: float = 0.3) -> None:
        """Run concurrent memory operations with configurable conflict rate"""
        
        print(f"Running {num_operations} concurrent operations with {conflict_rate*100}% conflict rate...")
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            
            # Check if memory sync service is available
            try:
                async with session.get(f"{self.memory_sync_url}/health") as response:
                    if response.status != 200:
                        raise Exception(f"Memory sync service unhealthy: {response.status}")
                    print("✅ Memory sync service is healthy")
            except Exception as e:
                print(f"❌ Memory sync service unavailable: {e}")
                return
                
            tasks = []
            memory_ids = [f"mem_{i}" for i in range(1, num_operations // 4 + 1)]  # Reuse memory IDs to create conflicts
            
            for i in range(num_operations):
                if random.random() < conflict_rate:
                    # Create conflict scenario
                    memory_id = random.choice(memory_ids[:len(memory_ids)//2])  # Use common memory IDs
                    task = self.create_conflict_scenario(session, memory_id)
                else:
                    # Create normal operation
                    agent_id = random.choice(self.agents)
                    memory_id = f"unique_mem_{i}_{random.randint(1000, 9999)}"
                    task = self.create_memory_operation(session, agent_id, memory_id)
                    
                tasks.append(task)
                
                # Batch operations to avoid overwhelming the service
                if len(tasks) >= 50:
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []
                    
                    # Small delay between batches
                    await asyncio.sleep(0.1)
                    
            # Process remaining tasks
            if tasks:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
    async def monitor_service_health(self, session: aiohttp.ClientSession, duration: int) -> Dict[str, Any]:
        """Monitor memory sync service health during benchmark"""
        
        health_data = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                async with session.get(f"{self.memory_sync_url}/health") as response:
                    if response.status == 200:
                        health_info = await response.json()
                        health_data.append({
                            'timestamp': time.time(),
                            'status': health_info.get('status'),
                            'active_conflicts': health_info.get('activeConflicts', 0),
                            'active_syncs': health_info.get('activeSyncs', 0),
                            'uptime': health_info.get('uptime', 0)
                        })
                        
            except Exception as e:
                health_data.append({
                    'timestamp': time.time(),
                    'status': 'error',
                    'error': str(e)
                })
                
            await asyncio.sleep(5)  # Check every 5 seconds
            
        return {
            'health_checks': len(health_data),
            'healthy_checks': len([h for h in health_data if h.get('status') == 'healthy']),
            'max_active_conflicts': max([h.get('active_conflicts', 0) for h in health_data]),
            'max_active_syncs': max([h.get('active_syncs', 0) for h in health_data]),
            'health_data': health_data
        }
        
    async def get_final_metrics(self) -> Dict[str, Any]:
        """Get final metrics from memory sync service"""
        
        try:
            connector = aiohttp.TCPConnector(limit=10)
            timeout = aiohttp.ClientTimeout(total=10)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(f"{self.memory_sync_url}/api/metrics") as response:
                    if response.status == 200:
                        return await response.json()
                        
        except Exception as e:
            print(f"Failed to get final metrics: {e}")
            
        return {}
        
    def calculate_final_results(self, health_data: Dict[str, Any], service_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final benchmark results"""
        
        # Calculate agent statistics
        for agent_id in self.agents:
            agent_times = [t for i, t in enumerate(self.results['operation_times']) 
                          if i < len(self.results['operation_times'])]  # Simplified for demo
            if agent_times:
                self.results['agent_stats'][agent_id]['avg_time'] = statistics.mean(agent_times)
                
        # Overall statistics
        operation_times = self.results['operation_times']
        
        final_results = {
            'benchmark_summary': {
                'total_operations': self.results['total_operations'],
                'successful_operations': self.results['successful_operations'],
                'failed_operations': self.results['failed_operations'],
                'success_rate': (self.results['successful_operations'] / max(self.results['total_operations'], 1)) * 100,
                'conflicts_detected': self.results['conflicts_detected'],
                'conflicts_resolved': self.results['conflicts_resolved'],
                'conflict_resolution_rate': (self.results['conflicts_resolved'] / max(self.results['conflicts_detected'], 1)) * 100
            },
            'performance_stats': {
                'avg_operation_time': statistics.mean(operation_times) if operation_times else 0,
                'min_operation_time': min(operation_times) if operation_times else 0,
                'max_operation_time': max(operation_times) if operation_times else 0,
                'p50_operation_time': sorted(operation_times)[len(operation_times)//2] if operation_times else 0,
                'p95_operation_time': sorted(operation_times)[int(len(operation_times)*0.95)] if operation_times else 0,
                'p99_operation_time': sorted(operation_times)[int(len(operation_times)*0.99)] if operation_times else 0,
                'operations_per_second': len(operation_times) / (sum(operation_times) / 1000) if operation_times else 0
            },
            'agent_breakdown': self.results['agent_stats'],
            'service_health': health_data,
            'service_metrics': service_metrics,
            'timestamp': time.time()
        }
        
        return final_results

async def main():
    parser = argparse.ArgumentParser(description='Concurrent Agents Benchmark')
    parser.add_argument('--agents', type=int, default=4, help='Number of concurrent agents')
    parser.add_argument('--operations', type=int, default=1000, help='Total number of operations')
    parser.add_argument('--conflict-rate', type=float, default=0.3, help='Conflict rate (0.0-1.0)')
    parser.add_argument('--output', default='concurrent-agents-results.json', help='Output file')
    parser.add_argument('--memory-sync-url', default='http://localhost:8003', help='Memory sync service URL')
    
    args = parser.parse_args()
    
    benchmark = ConcurrentAgentsBenchmark(args.memory_sync_url)
    
    print(f"🚀 Starting Concurrent Agents Benchmark")
    print(f"   Operations: {args.operations}")
    print(f"   Conflict Rate: {args.conflict_rate * 100}%")
    print(f"   Memory Sync URL: {args.memory_sync_url}")
    
    start_time = time.time()
    
    # Start health monitoring
    connector = aiohttp.TCPConnector(limit=10)
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        # Estimate benchmark duration (rough calculation)
        estimated_duration = max(args.operations // 50, 30)  # At least 30 seconds
        
        # Run benchmark and health monitoring concurrently
        benchmark_task = benchmark.run_concurrent_operations(args.operations, args.conflict_rate)
        health_task = benchmark.monitor_service_health(session, estimated_duration + 10)
        
        await asyncio.gather(benchmark_task, health_task, return_exceptions=True)
        
    # Get final service metrics
    service_metrics = await benchmark.get_final_metrics()
    
    # Wait a bit for final metrics
    await asyncio.sleep(2)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n✅ Benchmark completed in {duration:.2f} seconds")
    
    # Calculate and save results
    health_data = await benchmark.monitor_service_health(
        aiohttp.ClientSession(), 0  # Just get current state
    ) if hasattr(benchmark, 'health_data') else {}
    
    results = benchmark.calculate_final_results(health_data, service_metrics)
    results['benchmark_duration'] = duration
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
        
    # Print summary
    print(f"\n📊 Benchmark Results:")
    print(f"   Total Operations: {results['benchmark_summary']['total_operations']}")
    print(f"   Success Rate: {results['benchmark_summary']['success_rate']:.1f}%")
    print(f"   Conflicts Detected: {results['benchmark_summary']['conflicts_detected']}")
    print(f"   Conflicts Resolved: {results['benchmark_summary']['conflicts_resolved']}")
    print(f"   Avg Operation Time: {results['performance_stats']['avg_operation_time']:.3f}ms")
    print(f"   Operations/Second: {results['performance_stats']['operations_per_second']:.1f}")
    
    print(f"\n💾 Results saved to: {args.output}")

if __name__ == "__main__":
    asyncio.run(main())