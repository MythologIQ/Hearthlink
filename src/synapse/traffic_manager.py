"""
Enhanced Synapse Traffic Manager with Rate Limiting and Priority Queuing

Implements adaptive priority queuing with user-configurable budgets
as recommended in ClaudeDesktopInsights.md architectural analysis.
"""

import time
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import deque
import threading
import uuid
from log_handling.agent_token_tracker import log_agent_token_usage, AgentType


class AgentPriority(Enum):
    """Agent priority levels for queuing."""
    ALDEN = 1           # Highest priority - local primary agent
    INTERNAL = 2        # Internal agents (Alice, Mimic, Sentry)
    EXTERNAL = 3        # External agents (Gemini, Trae, Claude Code)
    SYSTEM = 0          # System operations - highest priority


class RequestStatus(Enum):
    """Request processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    RATE_LIMITED = "rate_limited"
    REJECTED = "rejected"


@dataclass
class TokenBucket:
    """Token bucket for rate limiting."""
    rate: float  # Tokens per second
    burst: int   # Maximum tokens
    tokens: float = 0
    last_refill: float = field(default_factory=time.time)
    
    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from bucket."""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.burst, self.tokens + (elapsed * self.rate))
        self.last_refill = now


@dataclass
class QueuedRequest:
    """Queued request with priority and metadata."""
    request_id: str
    agent_type: str
    priority: AgentPriority
    payload: Dict[str, Any]
    submitted_at: datetime
    status: RequestStatus = RequestStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class TrafficMetrics:
    """Traffic analytics metrics."""
    requests_per_second: float = 0.0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    queue_depth: int = 0
    rate_limit_hits: int = 0
    total_requests: int = 0
    
    def update(self, response_time: float, success: bool):
        """Update metrics with new request data."""
        self.total_requests += 1
        if not success:
            self.error_rate = (self.error_rate + 1) / self.total_requests
        self.avg_response_time = (self.avg_response_time + response_time) / 2


class UserBandwidthManager:
    """Manages user-configurable bandwidth budgets."""
    
    def __init__(self):
        self.user_budgets: Dict[str, Dict[str, TokenBucket]] = {}
        self.default_budgets = {
            'alden': {'rate': 100, 'burst': 200},
            'internal_agents': {'rate': 50, 'burst': 100},
            'external_agents': {'rate': 20, 'burst': 40},
            'system': {'rate': 1000, 'burst': 1000}
        }
    
    def get_user_budget(self, user_id: str, agent_type: str) -> TokenBucket:
        """Get token bucket for user and agent type."""
        if user_id not in self.user_budgets:
            self.user_budgets[user_id] = {}
        
        if agent_type not in self.user_budgets[user_id]:
            config = self.default_budgets.get(agent_type, self.default_budgets['external_agents'])
            self.user_budgets[user_id][agent_type] = TokenBucket(
                rate=config['rate'],
                burst=config['burst'],
                tokens=config['burst']
            )
        
        return self.user_budgets[user_id][agent_type]
    
    def update_user_budget(self, user_id: str, agent_type: str, rate: float, burst: int):
        """Update user's budget for specific agent type."""
        if user_id not in self.user_budgets:
            self.user_budgets[user_id] = {}
        
        self.user_budgets[user_id][agent_type] = TokenBucket(
            rate=rate,
            burst=burst,
            tokens=burst
        )


class TrafficAnalytics:
    """Comprehensive traffic analytics for security monitoring."""
    
    def __init__(self):
        self.metrics: Dict[str, TrafficMetrics] = {}
        self.request_history: deque = deque(maxlen=1000)
        self.anomaly_threshold = 2.0  # Standard deviations
        self.lock = threading.Lock()
    
    def record_request(self, agent_type: str, request_id: str, success: bool, response_time: float):
        """Record request for analytics."""
        with self.lock:
            if agent_type not in self.metrics:
                self.metrics[agent_type] = TrafficMetrics()
            
            self.metrics[agent_type].update(response_time, success)
            self.request_history.append({
                'timestamp': datetime.now(),
                'agent_type': agent_type,
                'request_id': request_id,
                'success': success,
                'response_time': response_time
            })
    
    def detect_anomaly(self, agent_type: str, current_rate: float) -> bool:
        """Detect traffic anomalies for security monitoring."""
        if agent_type not in self.metrics:
            return False
        
        baseline = self.metrics[agent_type].requests_per_second
        if baseline == 0:
            return False
        
        # Check if current rate exceeds threshold
        return abs(current_rate - baseline) > (baseline * self.anomaly_threshold)
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report for Sentry integration."""
        with self.lock:
            report = {
                'timestamp': datetime.now().isoformat(),
                'agent_metrics': {},
                'anomalies': [],
                'total_requests': sum(m.total_requests for m in self.metrics.values()),
                'overall_error_rate': sum(m.error_rate for m in self.metrics.values()) / len(self.metrics) if self.metrics else 0
            }
            
            for agent_type, metrics in self.metrics.items():
                report['agent_metrics'][agent_type] = {
                    'requests_per_second': metrics.requests_per_second,
                    'avg_response_time': metrics.avg_response_time,
                    'error_rate': metrics.error_rate,
                    'rate_limit_hits': metrics.rate_limit_hits
                }
                
                # Check for anomalies
                if self.detect_anomaly(agent_type, metrics.requests_per_second):
                    report['anomalies'].append({
                        'agent_type': agent_type,
                        'anomaly_type': 'traffic_spike',
                        'current_rate': metrics.requests_per_second,
                        'severity': 'high' if metrics.requests_per_second > 100 else 'medium'
                    })
            
            return report


class SynapseTrafficManager:
    """
    Enhanced traffic manager with adaptive priority queuing and rate limiting.
    
    Implements the architecture recommended in ClaudeDesktopInsights.md for
    handling multi-agent traffic with security and performance considerations.
    """
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Core components
        self.bandwidth_manager = UserBandwidthManager()
        self.traffic_analytics = TrafficAnalytics()
        
        # Priority queues for different agent types
        self.priority_queues: Dict[AgentPriority, deque] = {
            AgentPriority.SYSTEM: deque(),
            AgentPriority.ALDEN: deque(),
            AgentPriority.INTERNAL: deque(),
            AgentPriority.EXTERNAL: deque()
        }
        
        # Global rate limiters
        self.global_rate_limiters: Dict[str, TokenBucket] = {
            'alden': TokenBucket(rate=100, burst=200),
            'internal_agents': TokenBucket(rate=50, burst=100),
            'external_agents': TokenBucket(rate=20, burst=40),
            'system': TokenBucket(rate=1000, burst=1000)
        }
        
        # Processing state
        self.processing_requests: Dict[str, QueuedRequest] = {}
        self.active_workers = 0
        self.max_workers = config.get('max_workers', 10)
        
        # Metrics
        self.start_time = datetime.now()
        self.processed_requests = 0
        
        # Start background processing
        self.running = True
        self.processing_thread = threading.Thread(target=self._process_queue_worker)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def get_agent_priority(self, agent_type: str) -> AgentPriority:
        """Determine priority for agent type."""
        agent_type_lower = agent_type.lower()
        
        if agent_type_lower == 'alden':
            return AgentPriority.ALDEN
        elif agent_type_lower in ['alice', 'mimic', 'sentry']:
            return AgentPriority.INTERNAL
        elif agent_type_lower == 'system':
            return AgentPriority.SYSTEM
        else:
            return AgentPriority.EXTERNAL
    
    async def submit_request(self, request_id: str, agent_type: str, payload: Dict[str, Any], 
                           user_id: str = "default") -> Dict[str, Any]:
        """Submit request for processing with rate limiting and priority queuing."""
        try:
            # Get user's rate limit budget
            user_bucket = self.bandwidth_manager.get_user_budget(user_id, agent_type)
            
            # Check user-specific rate limit
            if not user_bucket.consume(1):
                self.traffic_analytics.metrics.setdefault(agent_type, TrafficMetrics()).rate_limit_hits += 1
                return {
                    'success': False,
                    'error': 'User rate limit exceeded',
                    'status': RequestStatus.RATE_LIMITED.value,
                    'retry_after': 1.0 / user_bucket.rate
                }
            
            # Check global rate limit
            if not self.global_rate_limiters[agent_type].consume(1):
                self.traffic_analytics.metrics.setdefault(agent_type, TrafficMetrics()).rate_limit_hits += 1
                return {
                    'success': False,
                    'error': 'Global rate limit exceeded',
                    'status': RequestStatus.RATE_LIMITED.value,
                    'retry_after': 1.0 / self.global_rate_limiters[agent_type].rate
                }
            
            # Create queued request
            priority = self.get_agent_priority(agent_type)
            queued_request = QueuedRequest(
                request_id=request_id,
                agent_type=agent_type,
                priority=priority,
                payload=payload,
                submitted_at=datetime.now()
            )
            
            # Add to appropriate priority queue
            self.priority_queues[priority].append(queued_request)
            
            # Update queue depth metric
            total_queue_depth = sum(len(q) for q in self.priority_queues.values())
            self.traffic_analytics.metrics.setdefault(agent_type, TrafficMetrics()).queue_depth = total_queue_depth
            
            self.logger.info(f"Request {request_id} queued for {agent_type} with priority {priority.name}")
            
            return {
                'success': True,
                'request_id': request_id,
                'status': RequestStatus.PENDING.value,
                'queue_position': len(self.priority_queues[priority]),
                'estimated_wait_time': self._estimate_wait_time(priority)
            }
            
        except Exception as e:
            self.logger.error(f"Error submitting request {request_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': RequestStatus.REJECTED.value
            }
    
    def _estimate_wait_time(self, priority: AgentPriority) -> float:
        """Estimate wait time based on queue depth and processing rate."""
        # Count requests ahead in queue
        ahead_count = 0
        for p in AgentPriority:
            if p.value <= priority.value:
                ahead_count += len(self.priority_queues[p])
        
        # Estimate based on average processing time
        avg_processing_time = 0.5  # 500ms average
        return ahead_count * avg_processing_time
    
    def _process_queue_worker(self):
        """Background worker to process queued requests."""
        while self.running:
            try:
                # Get next request from highest priority queue
                request = self._get_next_request()
                
                if request:
                    self._process_request(request)
                else:
                    # No requests available, sleep briefly
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Error in queue worker: {e}")
                time.sleep(1)
    
    def _get_next_request(self) -> Optional[QueuedRequest]:
        """Get next request from priority queues."""
        for priority in AgentPriority:
            if self.priority_queues[priority]:
                return self.priority_queues[priority].popleft()
        return None
    
    def _process_request(self, request: QueuedRequest):
        """Process individual request."""
        start_time = time.time()
        
        try:
            # Mark as processing
            request.status = RequestStatus.PROCESSING
            self.processing_requests[request.request_id] = request
            
            # Simulate processing (in real implementation, this would call the actual agent)
            # This is where the actual plugin execution would happen
            time.sleep(0.1)  # Simulate processing time
            
            # Mark as completed
            request.status = RequestStatus.COMPLETED
            processing_time = time.time() - start_time
            
            # Log token usage (estimate based on request payload size)
            try:
                estimated_tokens = len(str(request.payload)) // 4  # Rough estimate
                if estimated_tokens > 0:
                    # Map agent types to AgentType enum
                    agent_type_mapping = {
                        'alden': AgentType.ALDEN,
                        'mimic': AgentType.MIMIC,
                        'alice': AgentType.ALICE,
                        'gemini': AgentType.GEMINI,
                        'claude': AgentType.CLAUDE,
                        'system': AgentType.SYSTEM
                    }
                    
                    agent_type_enum = agent_type_mapping.get(request.agent_type.lower(), AgentType.EXTERNAL_GPT)
                    
                    log_agent_token_usage(
                        agent_name=request.agent_type,
                        agent_type=agent_type_enum,
                        tokens_used=estimated_tokens,
                        task_description=f"Traffic managed request: {request.request_id}",
                        module="traffic_manager",
                        request_id=request.request_id,
                        response_time_ms=int(processing_time * 1000),
                        success=True
                    )
            except Exception as token_error:
                self.logger.warning(f"Failed to log token usage for request {request.request_id}: {token_error}")
            
            # Record analytics
            self.traffic_analytics.record_request(
                request.agent_type,
                request.request_id,
                True,
                processing_time
            )
            
            self.processed_requests += 1
            self.logger.info(f"Request {request.request_id} completed in {processing_time:.3f}s")
            
        except Exception as e:
            # Handle processing error
            request.status = RequestStatus.REJECTED
            processing_time = time.time() - start_time
            
            # Log failed token usage attempt
            try:
                estimated_tokens = len(str(request.payload)) // 4
                if estimated_tokens > 0:
                    agent_type_mapping = {
                        'alden': AgentType.ALDEN,
                        'mimic': AgentType.MIMIC,
                        'alice': AgentType.ALICE,
                        'gemini': AgentType.GEMINI,
                        'claude': AgentType.CLAUDE,
                        'system': AgentType.SYSTEM
                    }
                    
                    agent_type_enum = agent_type_mapping.get(request.agent_type.lower(), AgentType.EXTERNAL_GPT)
                    
                    log_agent_token_usage(
                        agent_name=request.agent_type,
                        agent_type=agent_type_enum,
                        tokens_used=estimated_tokens,
                        task_description=f"Failed traffic managed request: {request.request_id}",
                        module="traffic_manager",
                        request_id=request.request_id,
                        response_time_ms=int(processing_time * 1000),
                        success=False,
                        error_message=str(e)
                    )
            except Exception as token_error:
                self.logger.warning(f"Failed to log token usage for failed request {request.request_id}: {token_error}")
            
            self.traffic_analytics.record_request(
                request.agent_type,
                request.request_id,
                False,
                processing_time
            )
            
            self.logger.error(f"Request {request.request_id} failed: {e}")
            
        finally:
            # Remove from processing
            self.processing_requests.pop(request.request_id, None)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'processed_requests': self.processed_requests,
            'requests_per_second': self.processed_requests / uptime if uptime > 0 else 0,
            'active_workers': self.active_workers,
            'max_workers': self.max_workers,
            'queue_depths': {
                priority.name: len(queue) for priority, queue in self.priority_queues.items()
            },
            'processing_requests': len(self.processing_requests),
            'agent_metrics': {
                agent_type: {
                    'requests_per_second': metrics.requests_per_second,
                    'avg_response_time': metrics.avg_response_time,
                    'error_rate': metrics.error_rate,
                    'rate_limit_hits': metrics.rate_limit_hits
                }
                for agent_type, metrics in self.traffic_analytics.metrics.items()
            }
        }
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get security report for Sentry integration."""
        return self.traffic_analytics.get_security_report()
    
    def update_user_budget(self, user_id: str, agent_type: str, rate: float, burst: int):
        """Update user's bandwidth budget."""
        self.bandwidth_manager.update_user_budget(user_id, agent_type, rate, burst)
        self.logger.info(f"Updated budget for user {user_id}, agent {agent_type}: {rate}req/s, {burst} burst")
    
    def shutdown(self):
        """Gracefully shutdown the traffic manager."""
        self.running = False
        if self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5)
        self.logger.info("Traffic manager shutdown complete")