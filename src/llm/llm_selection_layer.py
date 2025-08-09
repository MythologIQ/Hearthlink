#!/usr/bin/env python3
"""
LLM Selection Layer - Runtime Model Configuration
Implements dynamic model selection and runtime configuration for Llama 3.5 micro and other models
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.local_llm_client import LocalLLMClient, LLMConfig, LLMRequest, LLMResponse, create_llm_client
from log_handling.agent_token_tracker import log_agent_token_usage, AgentType

logger = logging.getLogger(__name__)

class ModelTier(Enum):
    """Available model performance tiers"""
    MICRO = "micro"      # Ultra-fast, minimal resource (Llama 3.5 micro)
    SMALL = "small"      # Fast, moderate resource (Llama 3.2 3B)
    MEDIUM = "medium"    # Balanced performance/resource (Llama 3.2 8B)
    LARGE = "large"      # High performance, high resource (Llama 3.1 70B)

class ModelStatus(Enum):
    """Model availability status"""
    AVAILABLE = "available"
    LOADING = "loading"
    UNAVAILABLE = "unavailable"
    ERROR = "error"

@dataclass
class ModelInfo:
    """Information about available models"""
    name: str
    tier: ModelTier
    status: ModelStatus
    resource_usage: Dict[str, Any]  # Memory, CPU, GPU requirements
    capabilities: List[str]
    version: str
    last_health_check: Optional[str] = None
    error_message: Optional[str] = None
    performance_metrics: Optional[Dict[str, float]] = None

@dataclass
class SelectionCriteria:
    """Criteria for model selection"""
    preferred_tier: Optional[ModelTier] = None
    max_resource_usage: Optional[Dict[str, Any]] = None
    required_capabilities: List[str] = None
    performance_requirements: Optional[Dict[str, float]] = None
    fallback_allowed: bool = True

@dataclass
class ModelSwapEvent:
    """Event logged when models are swapped"""
    timestamp: str
    from_model: str
    to_model: str
    reason: str
    initiated_by: str  # "user", "system", "performance", "error"
    swap_time_ms: int
    success: bool
    error_message: Optional[str] = None

class LLMSelectionLayer:
    """
    Dynamic LLM selection and configuration layer
    
    Provides:
    - Runtime model switching between Llama 3.5 micro and other models
    - Performance-based automatic model selection
    - Hot-swapping without downtime
    - Resource usage monitoring and optimization
    - Model health checking and fallback management
    """
    
    def __init__(self, config_path: str = None, logger: Optional[logging.Logger] = None):
        """
        Initialize LLM Selection Layer
        
        Args:
            config_path: Path to model configuration file
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config_path = config_path or str(Path(__file__).parent.parent.parent / "config" / "llm_selection_config.json")
        
        # Model registry and status
        self.available_models: Dict[str, ModelInfo] = {}
        self.current_model: Optional[str] = None
        self.current_client: Optional[LocalLLMClient] = None
        
        # Selection and fallback configuration
        self.default_selection_criteria = SelectionCriteria(
            preferred_tier=ModelTier.MICRO,
            fallback_allowed=True,
            required_capabilities=["chat", "instruct"]
        )
        
        # Performance tracking
        self.model_performance: Dict[str, Dict[str, float]] = {}
        self.swap_history: List[ModelSwapEvent] = []
        self.health_check_interval = 300  # 5 minutes
        
        # Threading for background tasks
        self._health_check_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Load configuration
        self._load_configuration()
        
        # Initialize models
        asyncio.create_task(self._initialize_models())
        
        self.logger.info("LLM Selection Layer initialized", extra={
            "config_path": self.config_path,
            "available_models": len(self.available_models),
            "default_tier": self.default_selection_criteria.preferred_tier.value
        })
    
    def _load_configuration(self):
        """Load model configuration from file"""
        try:
            config_file = Path(self.config_path)
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Load model definitions
                for model_name, model_config in config_data.get("models", {}).items():
                    model_info = ModelInfo(
                        name=model_name,
                        tier=ModelTier(model_config.get("tier", "small")),
                        status=ModelStatus.UNAVAILABLE,
                        resource_usage=model_config.get("resource_usage", {}),
                        capabilities=model_config.get("capabilities", []),
                        version=model_config.get("version", "unknown"),
                        performance_metrics=model_config.get("performance_metrics", {})
                    )
                    self.available_models[model_name] = model_info
                
                # Load selection criteria
                if "default_criteria" in config_data:
                    criteria_data = config_data["default_criteria"]
                    self.default_selection_criteria = SelectionCriteria(
                        preferred_tier=ModelTier(criteria_data.get("preferred_tier", "micro")),
                        max_resource_usage=criteria_data.get("max_resource_usage"),
                        required_capabilities=criteria_data.get("required_capabilities", ["chat", "instruct"]),
                        performance_requirements=criteria_data.get("performance_requirements"),
                        fallback_allowed=criteria_data.get("fallback_allowed", True)
                    )
                
                self.logger.info(f"Loaded configuration from {config_file}")
                
            else:
                # Create default configuration
                self._create_default_configuration()
                
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default model configuration"""
        try:
            # Default Llama 3.5 micro configuration
            self.available_models = {
                "llama-3.5-micro": ModelInfo(
                    name="llama-3.5-micro",
                    tier=ModelTier.MICRO,
                    status=ModelStatus.UNAVAILABLE,
                    resource_usage={
                        "memory_mb": 512,
                        "cpu_cores": 1,
                        "gpu_memory_mb": 0
                    },
                    capabilities=["chat", "instruct", "completion"],
                    version="3.5-micro",
                    performance_metrics={
                        "tokens_per_second": 50.0,
                        "response_time_ms": 200.0,
                        "accuracy_score": 0.85
                    }
                ),
                "llama-3.2-3b": ModelInfo(
                    name="llama-3.2-3b",
                    tier=ModelTier.SMALL,
                    status=ModelStatus.UNAVAILABLE,
                    resource_usage={
                        "memory_mb": 2048,
                        "cpu_cores": 2,
                        "gpu_memory_mb": 4096
                    },
                    capabilities=["chat", "instruct", "completion", "reasoning"],
                    version="3.2-3b",
                    performance_metrics={
                        "tokens_per_second": 25.0,
                        "response_time_ms": 400.0,
                        "accuracy_score": 0.90
                    }
                ),
                "llama-3.2-8b": ModelInfo(
                    name="llama-3.2-8b",
                    tier=ModelTier.MEDIUM,
                    status=ModelStatus.UNAVAILABLE,
                    resource_usage={
                        "memory_mb": 4096,
                        "cpu_cores": 4,
                        "gpu_memory_mb": 8192
                    },
                    capabilities=["chat", "instruct", "completion", "reasoning", "analysis"],
                    version="3.2-8b",
                    performance_metrics={
                        "tokens_per_second": 15.0,
                        "response_time_ms": 600.0,
                        "accuracy_score": 0.95
                    }
                )
            }
            
            # Save default configuration
            config_data = {
                "models": {
                    name: {
                        "tier": info.tier.value,
                        "resource_usage": info.resource_usage,
                        "capabilities": info.capabilities,
                        "version": info.version,
                        "performance_metrics": info.performance_metrics
                    }
                    for name, info in self.available_models.items()
                },
                "default_criteria": {
                    "preferred_tier": self.default_selection_criteria.preferred_tier.value,
                    "required_capabilities": self.default_selection_criteria.required_capabilities,
                    "fallback_allowed": self.default_selection_criteria.fallback_allowed
                }
            }
            
            # Ensure config directory exists
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Created default configuration at {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to create default configuration: {e}")
    
    async def _initialize_models(self):
        """Initialize and health check all available models"""
        try:
            for model_name, model_info in self.available_models.items():
                await self._check_model_availability(model_name)
                
                # Small delay between model checks
                await asyncio.sleep(1)
            
            # Select initial model
            await self._select_initial_model()
            
            # Start health check thread
            self._start_health_check_thread()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {e}")
    
    async def _check_model_availability(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        if model_name not in self.available_models:
            return False
        
        model_info = self.available_models[model_name]
        
        try:
            # Set status to loading
            model_info.status = ModelStatus.LOADING
            model_info.last_health_check = datetime.now().isoformat()
            
            # Create test LLM config for this model
            test_config = LLMConfig(
                engine="ollama",  # Assuming Ollama for local models
                model=model_name,
                base_url="http://localhost:11434",
                timeout=30,
                max_tokens=100,
                temperature=0.7
            )
            
            # Try to create client and test connection
            test_client = create_llm_client(test_config)
            
            # Simple test request
            test_request = LLMRequest(
                prompt="Test connection",
                system_message="Respond with 'OK' if you can understand this.",
                max_tokens=10,
                temperature=0.1
            )
            
            # Test with timeout
            try:
                response = test_client.generate(test_request)
                if response and response.content:
                    model_info.status = ModelStatus.AVAILABLE
                    model_info.error_message = None
                    self.logger.info(f"Model {model_name} is available")
                    return True
                else:
                    raise Exception("Empty response from model")
                    
            except Exception as test_error:
                raise Exception(f"Model test failed: {test_error}")
                
        except Exception as e:
            model_info.status = ModelStatus.UNAVAILABLE
            model_info.error_message = str(e)
            self.logger.warning(f"Model {model_name} unavailable: {e}")
            return False
    
    async def _select_initial_model(self):
        """Select initial model based on availability and criteria"""
        try:
            available_models = [
                name for name, info in self.available_models.items()
                if info.status == ModelStatus.AVAILABLE
            ]
            
            if not available_models:
                self.logger.warning("No models available for initial selection")
                return
            
            # Select based on default criteria
            selected_model = await self.select_optimal_model(self.default_selection_criteria)
            
            if selected_model:
                await self.switch_model(selected_model, "system", "initial_selection")
            else:
                # Fallback to first available model
                await self.switch_model(available_models[0], "system", "fallback_selection")
                
        except Exception as e:
            self.logger.error(f"Failed to select initial model: {e}")
    
    def _start_health_check_thread(self):
        """Start background health check thread"""
        def health_check_worker():
            while not self._shutdown_event.is_set():
                try:
                    # Run health checks
                    asyncio.run(self._periodic_health_check())
                    
                    # Wait for next check or shutdown
                    self._shutdown_event.wait(timeout=self.health_check_interval)
                    
                except Exception as e:
                    self.logger.error(f"Health check worker error: {e}")
                    time.sleep(60)  # Wait a minute before retrying
        
        self._health_check_thread = threading.Thread(
            target=health_check_worker,
            name="LLM-HealthCheck",
            daemon=True
        )
        self._health_check_thread.start()
    
    async def _periodic_health_check(self):
        """Perform periodic health checks on all models"""
        for model_name in list(self.available_models.keys()):
            try:
                await self._check_model_availability(model_name)
            except Exception as e:
                self.logger.error(f"Health check failed for {model_name}: {e}")
        
        # Check if current model is still available
        if self.current_model and self.available_models[self.current_model].status != ModelStatus.AVAILABLE:
            self.logger.warning(f"Current model {self.current_model} became unavailable")
            
            # Try to switch to a fallback model
            fallback_model = await self.select_optimal_model(self.default_selection_criteria)
            if fallback_model and fallback_model != self.current_model:
                await self.switch_model(fallback_model, "system", "health_check_fallback")
    
    async def select_optimal_model(self, criteria: SelectionCriteria) -> Optional[str]:
        """
        Select the optimal model based on given criteria
        
        Args:
            criteria: Selection criteria
            
        Returns:
            Model name or None if no suitable model found
        """
        try:
            available_models = [
                (name, info) for name, info in self.available_models.items()
                if info.status == ModelStatus.AVAILABLE
            ]
            
            if not available_models:
                return None
            
            # Filter by required capabilities
            if criteria.required_capabilities:
                available_models = [
                    (name, info) for name, info in available_models
                    if all(cap in info.capabilities for cap in criteria.required_capabilities)
                ]
            
            # Filter by resource constraints
            if criteria.max_resource_usage:
                filtered_models = []
                for name, info in available_models:
                    meets_constraints = True
                    for resource, max_value in criteria.max_resource_usage.items():
                        if resource in info.resource_usage:
                            if info.resource_usage[resource] > max_value:
                                meets_constraints = False
                                break
                    if meets_constraints:
                        filtered_models.append((name, info))
                available_models = filtered_models
            
            if not available_models:
                if criteria.fallback_allowed:
                    # Return any available model as fallback
                    fallback_models = [
                        (name, info) for name, info in self.available_models.items()
                        if info.status == ModelStatus.AVAILABLE
                    ]
                    if fallback_models:
                        return fallback_models[0][0]
                return None
            
            # Prefer models by tier
            if criteria.preferred_tier:
                preferred_models = [
                    (name, info) for name, info in available_models
                    if info.tier == criteria.preferred_tier
                ]
                
                if preferred_models:
                    available_models = preferred_models
            
            # Select based on performance metrics
            if criteria.performance_requirements:
                scored_models = []
                for name, info in available_models:
                    score = 0.0
                    metric_count = 0
                    
                    for metric, min_value in criteria.performance_requirements.items():
                        if info.performance_metrics and metric in info.performance_metrics:
                            if info.performance_metrics[metric] >= min_value:
                                score += info.performance_metrics[metric]
                            metric_count += 1
                    
                    if metric_count > 0:
                        scored_models.append((name, info, score / metric_count))
                
                if scored_models:
                    # Sort by score and return best
                    scored_models.sort(key=lambda x: x[2], reverse=True)
                    return scored_models[0][0]
            
            # Default selection: prefer micro tier, then by resource efficiency
            model_priorities = {
                ModelTier.MICRO: 4,
                ModelTier.SMALL: 3,
                ModelTier.MEDIUM: 2,
                ModelTier.LARGE: 1
            }
            
            available_models.sort(
                key=lambda x: (
                    model_priorities.get(x[1].tier, 0),
                    -x[1].resource_usage.get("memory_mb", 0)  # Prefer lower memory usage
                ),
                reverse=True
            )
            
            return available_models[0][0]
            
        except Exception as e:
            self.logger.error(f"Failed to select optimal model: {e}")
            return None
    
    async def switch_model(self, model_name: str, initiated_by: str = "user", reason: str = "manual") -> bool:
        """
        Switch to a different model at runtime
        
        Args:
            model_name: Name of model to switch to
            initiated_by: Who initiated the switch
            reason: Reason for the switch
            
        Returns:
            Success status
        """
        start_time = datetime.now()
        
        try:
            if model_name not in self.available_models:
                raise ValueError(f"Unknown model: {model_name}")
            
            model_info = self.available_models[model_name]
            
            if model_info.status != ModelStatus.AVAILABLE:
                raise ValueError(f"Model {model_name} is not available (status: {model_info.status.value})")
            
            if self.current_model == model_name:
                self.logger.info(f"Already using model {model_name}")
                return True
            
            old_model = self.current_model
            
            # Create new LLM client configuration
            new_config = LLMConfig(
                engine="ollama",
                model=model_name,
                base_url="http://localhost:11434",
                timeout=30,
                max_tokens=4000,
                temperature=0.7
            )
            
            # Create new client
            new_client = create_llm_client(new_config)
            
            # Test new client with a simple request
            test_request = LLMRequest(
                prompt="Hello",
                system_message="Respond briefly to confirm you are working.",
                max_tokens=20,
                temperature=0.1
            )
            
            test_response = new_client.generate(test_request)
            if not test_response or not test_response.content:
                raise Exception("New model failed test request")
            
            # Switch is successful
            old_client = self.current_client
            self.current_client = new_client
            self.current_model = model_name
            
            # Log swap event
            swap_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            swap_event = ModelSwapEvent(
                timestamp=datetime.now().isoformat(),
                from_model=old_model or "none",
                to_model=model_name,
                reason=reason,
                initiated_by=initiated_by,
                swap_time_ms=swap_time_ms,
                success=True
            )
            
            self.swap_history.append(swap_event)
            
            # Keep only last 100 swap events
            if len(self.swap_history) > 100:
                self.swap_history = self.swap_history[-100:]
            
            self.logger.info(f"Successfully switched from {old_model} to {model_name}", extra={
                "swap_time_ms": swap_time_ms,
                "initiated_by": initiated_by,
                "reason": reason
            })
            
            return True
            
        except Exception as e:
            # Log failed swap event
            swap_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            swap_event = ModelSwapEvent(
                timestamp=datetime.now().isoformat(),
                from_model=self.current_model or "none",
                to_model=model_name,
                reason=reason,
                initiated_by=initiated_by,
                swap_time_ms=swap_time_ms,
                success=False,
                error_message=str(e)
            )
            
            self.swap_history.append(swap_event)
            
            self.logger.error(f"Failed to switch to model {model_name}: {e}")
            return False
    
    def get_current_model_info(self) -> Optional[ModelInfo]:
        """Get information about the currently active model"""
        if self.current_model and self.current_model in self.available_models:
            return self.available_models[self.current_model]
        return None
    
    def get_available_models(self) -> Dict[str, ModelInfo]:
        """Get all available model information"""
        return self.available_models.copy()
    
    def get_model_performance_stats(self, model_name: str = None) -> Dict[str, Any]:
        """Get performance statistics for a model or all models"""
        if model_name:
            return self.model_performance.get(model_name, {})
        return self.model_performance.copy()
    
    def get_swap_history(self, limit: int = 10) -> List[ModelSwapEvent]:
        """Get recent model swap history"""
        return self.swap_history[-limit:] if self.swap_history else []
    
    async def generate_with_current_model(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Generate response using currently selected model"""
        if not self.current_client:
            self.logger.error("No model currently selected")
            return None
        
        try:
            # Track performance
            start_time = datetime.now()
            
            response = self.current_client.generate(request)
            
            # Update performance metrics
            if self.current_model:
                if self.current_model not in self.model_performance:
                    self.model_performance[self.current_model] = {
                        "total_requests": 0,
                        "total_tokens": 0,
                        "avg_response_time_ms": 0.0,
                        "success_rate": 1.0,
                        "errors": 0
                    }
                
                stats = self.model_performance[self.current_model]
                stats["total_requests"] += 1
                
                if response:
                    response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
                    tokens_used = getattr(response, 'tokens_used', len(response.content.split()) * 1.3)
                    
                    stats["total_tokens"] += tokens_used
                    stats["avg_response_time_ms"] = (
                        (stats["avg_response_time_ms"] * (stats["total_requests"] - 1) + response_time_ms) /
                        stats["total_requests"]
                    )
                    stats["success_rate"] = (stats["total_requests"] - stats["errors"]) / stats["total_requests"]
                else:
                    stats["errors"] += 1
                    stats["success_rate"] = (stats["total_requests"] - stats["errors"]) / stats["total_requests"]
            
            return response
            
        except Exception as e:
            self.logger.error(f"Generation failed with current model: {e}")
            
            # Update error statistics
            if self.current_model and self.current_model in self.model_performance:
                self.model_performance[self.current_model]["errors"] += 1
            
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the selection layer"""
        current_info = self.get_current_model_info()
        
        return {
            "current_model": self.current_model,
            "current_model_info": asdict(current_info) if current_info else None,
            "available_models": {
                name: {
                    "tier": info.tier.value,
                    "status": info.status.value,
                    "capabilities": info.capabilities,
                    "resource_usage": info.resource_usage,
                    "last_health_check": info.last_health_check,
                    "error_message": info.error_message
                }
                for name, info in self.available_models.items()
            },
            "performance_stats": self.model_performance,
            "recent_swaps": [asdict(event) for event in self.get_swap_history(5)],
            "selection_criteria": asdict(self.default_selection_criteria),
            "health_check_interval": self.health_check_interval,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the selection layer and cleanup resources"""
        try:
            # Signal shutdown to health check thread
            self._shutdown_event.set()
            
            # Wait for health check thread to finish
            if self._health_check_thread and self._health_check_thread.is_alive():
                self._health_check_thread.join(timeout=10)
            
            # Cleanup current client
            self.current_client = None
            self.current_model = None
            
            self.logger.info("LLM Selection Layer shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

# Factory function
async def create_llm_selection_layer(
    config_path: str = None,
    preferred_tier: ModelTier = ModelTier.MICRO,
    logger: Optional[logging.Logger] = None
) -> LLMSelectionLayer:
    """
    Factory function to create and initialize LLM Selection Layer
    
    Args:
        config_path: Path to configuration file
        preferred_tier: Preferred model tier
        logger: Optional logger instance
        
    Returns:
        Initialized LLMSelectionLayer
    """
    selection_layer = LLMSelectionLayer(config_path, logger)
    
    # Update default criteria
    selection_layer.default_selection_criteria.preferred_tier = preferred_tier
    
    # Wait a moment for initialization to complete
    await asyncio.sleep(2)
    
    return selection_layer

# Test function
async def test_llm_selection_layer():
    """Test the LLM Selection Layer functionality"""
    logger.debug("🧪 Testing LLM Selection Layer")
    logger.debug("=" * 40)
    
    try:
        # Create selection layer
        selection_layer = await create_llm_selection_layer(
            preferred_tier=ModelTier.MICRO
        )
        
        logger.debug(f"✅ Selection layer created")
        
        # Get status
        status = selection_layer.get_status()
        logger.debug(f"📊 Status:")
        logger.debug(f"   Current model: {status['current_model']}")
        logger.debug(f"   Available models: {len(status['available_models'])}")
        
        for name, info in status['available_models'].items():
            logger.debug(f"   - {name}: {info['status']} ({info['tier']})")
        
        # Test model selection
        logger.debug(f"\n🔄 Testing model selection:")
        
        criteria = SelectionCriteria(
            preferred_tier=ModelTier.MICRO,
            required_capabilities=["chat"],
            fallback_allowed=True
        )
        
        optimal_model = await selection_layer.select_optimal_model(criteria)
        logger.debug(f"   Optimal model for micro tier: {optimal_model}")
        
        # Test model switching (if we have multiple models)
        available_models = [
            name for name, info in status['available_models'].items()
            if info['status'] == 'available'
        ]
        
        if len(available_models) > 1:
            target_model = available_models[1]  # Switch to second available model
            logger.debug(f"   Attempting to switch to: {target_model}")
            
            success = await selection_layer.switch_model(target_model, "test", "functionality_test")
            logger.debug(f"   Switch result: {'✅ Success' if success else '❌ Failed'}")
            
            # Get updated status
            updated_status = selection_layer.get_status()
            logger.debug(f"   New current model: {updated_status['current_model']}")
        
        # Test generation with current model
        if selection_layer.current_client:
            logger.debug(f"\n🤖 Testing generation with current model:")
            
            test_request = LLMRequest(
                prompt="What is 2+2?",
                system_message="Answer briefly and concisely.",
                max_tokens=20,
                temperature=0.1
            )
            
            response = await selection_layer.generate_with_current_model(test_request)
            
            if response:
                logger.debug(f"   Response: {response.content}")
                logger.debug(f"   Model: {response.model}")
                logger.debug(f"   Response time: {response.response_time:.3f}s")
            else:
                logger.debug(f"   ❌ No response received")
        
        # Show performance stats
        logger.debug(f"\n📈 Performance statistics:")
        perf_stats = selection_layer.get_model_performance_stats()
        
        for model, stats in perf_stats.items():
            logger.debug(f"   {model}:")
            logger.debug(f"     Requests: {stats.get('total_requests', 0)}")
            logger.debug(f"     Avg response time: {stats.get('avg_response_time_ms', 0):.1f}ms")
            logger.debug(f"     Success rate: {stats.get('success_rate', 0)*100:.1f}%")
        
        # Show swap history
        swap_history = selection_layer.get_swap_history(3)
        if swap_history:
            logger.debug(f"\n🔄 Recent model swaps:")
            for swap in swap_history:
                status_icon = "✅" if swap.success else "❌"
                logger.debug(f"   {status_icon} {swap.from_model} → {swap.to_model} ({swap.reason}, {swap.swap_time_ms}ms)")
        
        # Cleanup
        await selection_layer.shutdown()
        
        logger.debug(f"\n✅ LLM Selection Layer test completed successfully!")
        return True
        
    except Exception as e:
        logger.debug(f"\n❌ LLM Selection Layer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run test
    success = asyncio.run(test_llm_selection_layer())
    sys.exit(0 if success else 1)