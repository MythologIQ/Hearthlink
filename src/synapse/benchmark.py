"""
Benchmark Management System

Provides performance benchmarking and health checks for plugins.
Assigns performance tiers and risk scores based on real-time usage.
"""

import time
import statistics
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

from .manifest import BenchmarkResult

class PerformanceTier(Enum):
    """Plugin performance tiers."""
    STABLE = "stable"
    BETA = "beta"
    RISKY = "risky"
    UNSTABLE = "unstable"

@dataclass
class BenchmarkConfig:
    """Benchmark configuration."""
    test_duration: int = 30  # seconds
    max_concurrent_tests: int = 3
    response_time_threshold: float = 1000.0  # ms
    error_rate_threshold: float = 0.05  # 5%
    cpu_usage_threshold: float = 80.0  # percent
    memory_usage_threshold: float = 512.0  # MB
    throughput_threshold: float = 10.0  # requests per second

@dataclass
class BenchmarkTest:
    """Individual benchmark test."""
    test_id: str
    plugin_id: str
    test_type: str
    start_time: str
    end_time: Optional[str] = None
    duration: float = 0.0
    response_time: float = 0.0
    success: bool = False
    error_message: Optional[str] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    throughput: float = 0.0

@dataclass
class BenchmarkSummary:
    """Benchmark test summary."""
    plugin_id: str
    test_count: int
    success_count: int
    avg_response_time: float
    error_rate: float
    avg_cpu_usage: float
    avg_memory_usage: float
    avg_throughput: float
    performance_tier: PerformanceTier
    risk_score: int
    last_updated: str
    recommendations: List[str] = field(default_factory=list)

class BenchmarkManager:
    """Manages plugin benchmarking and performance evaluation."""
    
    def __init__(self, config: BenchmarkConfig, logger=None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Benchmark results storage
        self.benchmark_results: Dict[str, List[BenchmarkTest]] = {}
        self.benchmark_summaries: Dict[str, BenchmarkSummary] = {}
        
        # Active benchmarks
        self.active_benchmarks: Dict[str, Dict[str, Any]] = {}
        
        # Performance tier thresholds
        self.tier_thresholds = {
            PerformanceTier.STABLE: {
                "response_time": 500.0,
                "error_rate": 0.01,
                "cpu_usage": 50.0,
                "memory_usage": 256.0
            },
            PerformanceTier.BETA: {
                "response_time": 1000.0,
                "error_rate": 0.05,
                "cpu_usage": 70.0,
                "memory_usage": 384.0
            },
            PerformanceTier.RISKY: {
                "response_time": 2000.0,
                "error_rate": 0.10,
                "cpu_usage": 85.0,
                "memory_usage": 512.0
            }
        }
    
    def start_benchmark(self, plugin_id: str, test_type: str = "performance") -> str:
        """
        Start a benchmark test for a plugin.
        
        Args:
            plugin_id: Plugin to benchmark
            test_type: Type of benchmark test
            
        Returns:
            Test ID
        """
        import uuid
        test_id = f"bench-{uuid.uuid4().hex[:8]}"
        
        # Check if plugin is already being benchmarked
        if plugin_id in self.active_benchmarks:
            raise ValueError(f"Plugin {plugin_id} is already being benchmarked")
        
        # Create test record
        test = BenchmarkTest(
            test_id=test_id,
            plugin_id=plugin_id,
            test_type=test_type,
            start_time=datetime.now().isoformat()
        )
        
        # Initialize results storage
        if plugin_id not in self.benchmark_results:
            self.benchmark_results[plugin_id] = []
        
        self.benchmark_results[plugin_id].append(test)
        
        # Record active benchmark
        self.active_benchmarks[plugin_id] = {
            "test_id": test_id,
            "test_type": test_type,
            "start_time": datetime.now().isoformat(),
            "status": "running"
        }
        
        self.logger.info(f"Benchmark started: {test_id} for {plugin_id}")
        return test_id
    
    def complete_benchmark(self, test_id: str, results: Dict[str, Any]) -> bool:
        """
        Complete a benchmark test.
        
        Args:
            test_id: Test to complete
            results: Benchmark results
            
        Returns:
            Success status
        """
        # Find the test
        test = None
        plugin_id = None
        
        for pid, tests in self.benchmark_results.items():
            for t in tests:
                if t.test_id == test_id:
                    test = t
                    plugin_id = pid
                    break
            if test:
                break
        
        if not test:
            self.logger.error(f"Benchmark test not found: {test_id}")
            return False
        
        # Update test with results
        test.end_time = datetime.now().isoformat()
        test.duration = results.get("duration", 0.0)
        test.response_time = results.get("response_time", 0.0)
        test.success = results.get("success", False)
        test.error_message = results.get("error_message")
        test.cpu_usage = results.get("cpu_usage", 0.0)
        test.memory_usage = results.get("memory_usage", 0.0)
        test.throughput = results.get("throughput", 0.0)
        
        # Remove from active benchmarks
        if plugin_id in self.active_benchmarks:
            del self.active_benchmarks[plugin_id]
        
        # Update summary
        self._update_benchmark_summary(plugin_id)
        
        self.logger.info(f"Benchmark completed: {test_id}")
        return True
    
    def run_benchmark(self, plugin_id: str, test_function: Callable, 
                     test_params: Optional[Dict[str, Any]] = None) -> BenchmarkSummary:
        """
        Run a complete benchmark test.
        
        Args:
            plugin_id: Plugin to benchmark
            test_function: Function to execute for testing
            test_params: Optional parameters for test function
            
        Returns:
            Benchmark summary
        """
        test_id = self.start_benchmark(plugin_id)
        
        try:
            # Run the test function
            start_time = time.time()
            
            if test_params:
                result = test_function(**test_params)
            else:
                result = test_function()
            
            duration = time.time() - start_time
            
            # Collect metrics (simplified - in real implementation, you'd collect actual metrics)
            results = {
                "duration": duration,
                "response_time": duration * 1000,  # Convert to ms
                "success": True,
                "cpu_usage": 25.0,  # Simulated
                "memory_usage": 128.0,  # Simulated
                "throughput": 1.0 / duration if duration > 0 else 0.0
            }
            
            self.complete_benchmark(test_id, results)
            
            return self.get_benchmark_summary(plugin_id)
            
        except Exception as e:
            # Record failure
            results = {
                "duration": 0.0,
                "response_time": 0.0,
                "success": False,
                "error_message": str(e),
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "throughput": 0.0
            }
            
            self.complete_benchmark(test_id, results)
            raise
    
    def get_benchmark_summary(self, plugin_id: str) -> Optional[BenchmarkSummary]:
        """Get benchmark summary for a plugin."""
        return self.benchmark_summaries.get(plugin_id)
    
    def get_recent_benchmarks(self, plugin_id: str, hours: int = 24) -> List[BenchmarkTest]:
        """Get recent benchmark tests for a plugin."""
        if plugin_id not in self.benchmark_results:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_tests = []
        
        for test in self.benchmark_results[plugin_id]:
            test_time = datetime.fromisoformat(test.start_time)
            if test_time >= cutoff_time:
                recent_tests.append(test)
        
        return recent_tests
    
    def get_performance_tier(self, plugin_id: str) -> PerformanceTier:
        """Get current performance tier for a plugin."""
        summary = self.get_benchmark_summary(plugin_id)
        if not summary:
            return PerformanceTier.UNSTABLE
        
        return summary.performance_tier
    
    def get_risk_score(self, plugin_id: str) -> int:
        """Get current risk score for a plugin."""
        summary = self.get_benchmark_summary(plugin_id)
        if not summary:
            return 100  # Maximum risk if no data
        
        return summary.risk_score
    
    def list_benchmarked_plugins(self) -> List[str]:
        """List all plugins that have benchmark data."""
        return list(self.benchmark_summaries.keys())
    
    def export_benchmark_data(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Export benchmark data for a plugin."""
        if plugin_id not in self.benchmark_results:
            return None
        
        return {
            "plugin_id": plugin_id,
            "summary": asdict(self.benchmark_summaries.get(plugin_id, {})),
            "tests": [asdict(test) for test in self.benchmark_results[plugin_id]],
            "exported_at": datetime.now().isoformat()
        }
    
    def _update_benchmark_summary(self, plugin_id: str):
        """Update benchmark summary for a plugin."""
        if plugin_id not in self.benchmark_results:
            return
        
        tests = self.benchmark_results[plugin_id]
        if not tests:
            return
        
        # Calculate metrics from recent tests (last 24 hours)
        recent_tests = self.get_recent_benchmarks(plugin_id, 24)
        if not recent_tests:
            return
        
        # Calculate averages
        response_times = [t.response_time for t in recent_tests if t.success]
        cpu_usage = [t.cpu_usage for t in recent_tests]
        memory_usage = [t.memory_usage for t in recent_tests]
        throughput = [t.throughput for t in recent_tests if t.throughput > 0]
        
        success_count = sum(1 for t in recent_tests if t.success)
        error_rate = 1.0 - (success_count / len(recent_tests)) if recent_tests else 1.0
        
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        avg_cpu_usage = statistics.mean(cpu_usage) if cpu_usage else 0.0
        avg_memory_usage = statistics.mean(memory_usage) if memory_usage else 0.0
        avg_throughput = statistics.mean(throughput) if throughput else 0.0
        
        # Determine performance tier
        performance_tier = self._determine_performance_tier(
            avg_response_time, error_rate, avg_cpu_usage, avg_memory_usage
        )
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            avg_response_time, error_rate, avg_cpu_usage, avg_memory_usage
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            avg_response_time, error_rate, avg_cpu_usage, avg_memory_usage
        )
        
        # Create summary
        summary = BenchmarkSummary(
            plugin_id=plugin_id,
            test_count=len(recent_tests),
            success_count=success_count,
            avg_response_time=avg_response_time,
            error_rate=error_rate,
            avg_cpu_usage=avg_cpu_usage,
            avg_memory_usage=avg_memory_usage,
            avg_throughput=avg_throughput,
            performance_tier=performance_tier,
            risk_score=risk_score,
            last_updated=datetime.now().isoformat(),
            recommendations=recommendations
        )
        
        self.benchmark_summaries[plugin_id] = summary
    
    def _determine_performance_tier(self, response_time: float, error_rate: float,
                                  cpu_usage: float, memory_usage: float) -> PerformanceTier:
        """Determine performance tier based on metrics."""
        # Check stable tier
        stable_thresholds = self.tier_thresholds[PerformanceTier.STABLE]
        if (response_time <= stable_thresholds["response_time"] and
            error_rate <= stable_thresholds["error_rate"] and
            cpu_usage <= stable_thresholds["cpu_usage"] and
            memory_usage <= stable_thresholds["memory_usage"]):
            return PerformanceTier.STABLE
        
        # Check beta tier
        beta_thresholds = self.tier_thresholds[PerformanceTier.BETA]
        if (response_time <= beta_thresholds["response_time"] and
            error_rate <= beta_thresholds["error_rate"] and
            cpu_usage <= beta_thresholds["cpu_usage"] and
            memory_usage <= beta_thresholds["memory_usage"]):
            return PerformanceTier.BETA
        
        # Check risky tier
        risky_thresholds = self.tier_thresholds[PerformanceTier.RISKY]
        if (response_time <= risky_thresholds["response_time"] and
            error_rate <= risky_thresholds["error_rate"] and
            cpu_usage <= risky_thresholds["cpu_usage"] and
            memory_usage <= risky_thresholds["memory_usage"]):
            return PerformanceTier.RISKY
        
        return PerformanceTier.UNSTABLE
    
    def _calculate_risk_score(self, response_time: float, error_rate: float,
                            cpu_usage: float, memory_usage: float) -> int:
        """Calculate risk score (0-100) based on metrics."""
        risk_score = 0
        
        # Response time risk (0-25 points)
        if response_time > 2000:
            risk_score += 25
        elif response_time > 1000:
            risk_score += 15
        elif response_time > 500:
            risk_score += 5
        
        # Error rate risk (0-25 points)
        if error_rate > 0.10:
            risk_score += 25
        elif error_rate > 0.05:
            risk_score += 15
        elif error_rate > 0.01:
            risk_score += 5
        
        # CPU usage risk (0-25 points)
        if cpu_usage > 80:
            risk_score += 25
        elif cpu_usage > 60:
            risk_score += 15
        elif cpu_usage > 40:
            risk_score += 5
        
        # Memory usage risk (0-25 points)
        if memory_usage > 512:
            risk_score += 25
        elif memory_usage > 384:
            risk_score += 15
        elif memory_usage > 256:
            risk_score += 5
        
        return min(100, risk_score)
    
    def _generate_recommendations(self, response_time: float, error_rate: float,
                                cpu_usage: float, memory_usage: float) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        if response_time > 1000:
            recommendations.append("Consider optimizing response time")
        
        if error_rate > 0.05:
            recommendations.append("High error rate detected - review error handling")
        
        if cpu_usage > 70:
            recommendations.append("High CPU usage - consider resource optimization")
        
        if memory_usage > 384:
            recommendations.append("High memory usage - consider memory optimization")
        
        if not recommendations:
            recommendations.append("Performance is within acceptable ranges")
        
        return recommendations 