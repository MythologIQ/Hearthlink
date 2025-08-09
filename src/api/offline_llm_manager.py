#!/usr/bin/env python3
"""
Offline-First Local LLM Redundancy Manager
Implements comprehensive offline capabilities with intelligent model management and failover
"""

import json
import os
import time
import hashlib
import subprocess
import threading
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import requests
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    EMERGENCY = "emergency"

class ModelPriority(Enum):
    PRIMARY = 1
    SECONDARY = 2
    EMERGENCY = 3
    CACHED = 4

@dataclass
class ModelConfig:
    name: str
    size_gb: float
    priority: ModelPriority
    endpoint: str
    local_path: Optional[str] = None
    last_used: Optional[datetime] = None
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    capabilities: List[str] = None

class OfflineLLMManager:
    """
    Manages offline-first LLM operations with intelligent redundancy
    """
    
    def __init__(self, config_path="config/offline_llm_config.json"):
        self.config_path = config_path
        self.data_dir = Path("hearthlink_data/offline_llm")
        self.cache_dir = self.data_dir / "model_cache"
        self.db_path = self.data_dir / "offline_llm.db"
        
        # Connection state management
        self.connection_state = ConnectionState.ONLINE
        self.last_online_check = datetime.now()
        self.check_interval = 30  # seconds
        
        # Model management
        self.models = {}
        self.active_model = None
        self.fallback_chain = []
        
        # Performance tracking
        self.performance_metrics = {}
        self.circuit_breakers = {}
        
        # Initialize system
        self._ensure_directories()
        self._init_database()
        self._load_config()
        self._start_monitoring()
        
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _init_database(self):
        """Initialize SQLite database for persistent storage"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Model metadata table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                name TEXT PRIMARY KEY,
                size_gb REAL,
                priority INTEGER,
                endpoint TEXT,
                local_path TEXT,
                last_used TIMESTAMP,
                success_rate REAL,
                avg_response_time REAL,
                capabilities TEXT,
                download_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT,
                response_time REAL,
                success BOOLEAN,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Connection state history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connection_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _load_config(self):
        """Load configuration and initialize models"""
        default_config = {
            "models": [
                {
                    "name": "llama3.2:1b",
                    "size_gb": 0.7,
                    "priority": 3,
                    "endpoint": "http://localhost:11434",
                    "capabilities": ["chat", "completion", "emergency"]
                },
                {
                    "name": "llama3.2:3b",
                    "size_gb": 2.0,
                    "priority": 2,
                    "endpoint": "http://localhost:11434",
                    "capabilities": ["chat", "completion", "reasoning"]
                },
                {
                    "name": "llama3.1-8b",
                    "size_gb": 4.7,
                    "priority": 1,
                    "endpoint": "http://localhost:11434",
                    "capabilities": ["chat", "completion", "reasoning", "coding"]
                }
            ],
            "fallback_endpoints": [
                "http://localhost:11434",
                "http://127.0.0.1:11434", 
                "http://localhost:11435",
                "http://localhost:8080"
            ],
            "cache_settings": {
                "max_cache_size_gb": 50,
                "auto_download": True,
                "cleanup_threshold": 0.9
            },
            "redundancy_settings": {
                "min_models_available": 1,
                "health_check_interval": 30,
                "max_failure_rate": 0.3,
                "circuit_breaker_threshold": 5
            }
        }
        
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        else:
            config = default_config
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        # Initialize models from config
        for model_data in config["models"]:
            model = ModelConfig(
                name=model_data["name"],
                size_gb=model_data["size_gb"],
                priority=ModelPriority(model_data["priority"]),
                endpoint=model_data["endpoint"],
                capabilities=model_data.get("capabilities", [])
            )
            self.models[model.name] = model
            
        self.fallback_endpoints = config["fallback_endpoints"]
        self.cache_settings = config["cache_settings"]
        self.redundancy_settings = config["redundancy_settings"]
        
        logger.info(f"Loaded {len(self.models)} models for offline redundancy")
        
    def _start_monitoring(self):
        """Start background monitoring threads"""
        
        def health_monitor():
            while True:
                self._check_system_health()
                time.sleep(self.redundancy_settings["health_check_interval"])
                
        def connection_monitor():
            while True:
                self._check_connection_state()
                time.sleep(self.check_interval)
                
        # Start monitoring threads
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        connection_thread = threading.Thread(target=connection_monitor, daemon=True)
        
        health_thread.start()
        connection_thread.start()
        
        logger.info("Started offline LLM monitoring systems")
        
    def _check_connection_state(self):
        """Check and update connection state"""
        try:
            # Test primary endpoint
            response = requests.get(f"{self.fallback_endpoints[0]}/api/version", timeout=5)
            if response.status_code == 200:
                if self.connection_state != ConnectionState.ONLINE:
                    self._update_connection_state(ConnectionState.ONLINE, "Primary endpoint restored")
                self.last_online_check = datetime.now()
            else:
                self._handle_connection_failure()
                
        except Exception as e:
            self._handle_connection_failure(str(e))
            
    def _handle_connection_failure(self, error_msg="Connection timeout"):
        """Handle connection failures with intelligent fallback"""
        
        # Try fallback endpoints
        for endpoint in self.fallback_endpoints[1:]:
            try:
                response = requests.get(f"{endpoint}/api/version", timeout=3)
                if response.status_code == 200:
                    self._update_connection_state(ConnectionState.DEGRADED, f"Using fallback: {endpoint}")
                    return
            except:
                continue
                
        # All endpoints failed - go offline
        time_since_online = datetime.now() - self.last_online_check
        if time_since_online > timedelta(minutes=5):
            self._update_connection_state(ConnectionState.OFFLINE, "All endpoints unreachable")
        else:
            self._update_connection_state(ConnectionState.DEGRADED, error_msg)
            
    def _update_connection_state(self, new_state: ConnectionState, details: str):
        """Update connection state and log to database"""
        if self.connection_state != new_state:
            logger.info(f"Connection state changed: {self.connection_state.value} -> {new_state.value} ({details})")
            self.connection_state = new_state
            
            # Log to database
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO connection_history (state, details) VALUES (?, ?)",
                (new_state.value, details)
            )
            conn.commit()
            conn.close()
            
            # Trigger appropriate actions
            self._handle_state_transition(new_state)
            
    def _handle_state_transition(self, new_state: ConnectionState):
        """Handle actions needed for state transitions"""
        if new_state == ConnectionState.OFFLINE:
            self._ensure_offline_models()
            self._switch_to_offline_mode()
        elif new_state == ConnectionState.ONLINE:
            self._sync_with_online_services()
            
    def _check_system_health(self):
        """Comprehensive system health check"""
        
        # Check available models
        available_models = self._get_available_models()
        if len(available_models) < self.redundancy_settings["min_models_available"]:
            logger.warning(f"Only {len(available_models)} models available (minimum: {self.redundancy_settings['min_models_available']})")
            self._ensure_offline_models()
            
        # Check disk space
        cache_size = self._get_cache_size()
        if cache_size > self.cache_settings["max_cache_size_gb"] * self.cache_settings["cleanup_threshold"]:
            self._cleanup_cache()
            
        # Update model performance metrics
        self._update_performance_metrics()
        
    def _get_available_models(self) -> List[str]:
        """Get list of currently available models"""
        available = []
        
        for model_name, model in self.models.items():
            if self._is_model_available(model):
                available.append(model_name)
                
        return available
        
    def _is_model_available(self, model: ModelConfig) -> bool:
        """Check if a specific model is available"""
        
        # Check if model exists locally
        if model.local_path and os.path.exists(model.local_path):
            return True
            
        # Check if model is available via endpoint
        if self.connection_state in [ConnectionState.ONLINE, ConnectionState.DEGRADED]:
            try:
                response = requests.get(f"{model.endpoint}/api/tags", timeout=3)
                if response.status_code == 200:
                    models_data = response.json()
                    model_names = [m.get("name", "") for m in models_data.get("models", [])]
                    return model.name in model_names
            except:
                pass
                
        return False
        
    def _ensure_offline_models(self):
        """Ensure critical models are available offline"""
        logger.info("Ensuring offline model availability...")
        
        # Prioritize emergency models
        emergency_models = [m for m in self.models.values() if m.priority == ModelPriority.EMERGENCY]
        
        for model in emergency_models:
            if not self._is_model_cached(model):
                logger.info(f"Downloading emergency model: {model.name}")
                self._download_model(model)
                
    def _is_model_cached(self, model: ModelConfig) -> bool:
        """Check if model is cached locally"""
        cache_path = self.cache_dir / f"{model.name}.gguf"
        return cache_path.exists()
        
    def _download_model(self, model: ModelConfig) -> bool:
        """Download model for offline use"""
        try:
            logger.info(f"Starting download of model: {model.name}")
            
            # Use ollama pull if available
            result = subprocess.run(
                ["ollama", "pull", model.name],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded model: {model.name}")
                
                # Update model local path
                model.local_path = str(self.cache_dir / f"{model.name}.gguf")
                self._update_model_in_db(model)
                return True
            else:
                logger.error(f"Failed to download model {model.name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading model {model.name}: {e}")
            return False
            
    def _switch_to_offline_mode(self):
        """Switch to offline-only operation"""
        logger.info("Switching to offline mode")
        
        # Find best available offline model
        offline_models = [m for m in self.models.values() if self._is_model_cached(m)]
        
        if offline_models:
            # Sort by priority and select best
            best_model = min(offline_models, key=lambda m: m.priority.value)
            self.active_model = best_model
            logger.info(f"Selected offline model: {best_model.name}")
        else:
            logger.error("No offline models available - system in emergency state")
            self.connection_state = ConnectionState.EMERGENCY
            
    def _sync_with_online_services(self):
        """Sync with online services when connection restored"""
        logger.info("Syncing with online services")
        
        # Update model list
        self._refresh_available_models()
        
        # Update performance metrics
        self._upload_offline_metrics()
        
    def generate_response(self, prompt: str, model_preference: Optional[str] = None) -> Dict[str, Any]:
        """Generate response with offline-first redundancy"""
        
        start_time = time.time()
        
        # Determine best model to use
        model = self._select_best_model(model_preference)
        if not model:
            return {
                "success": False,
                "error": "No models available",
                "offline_mode": True,
                "timestamp": datetime.now().isoformat()
            }
            
        try:
            # Generate response
            response = self._generate_with_model(model, prompt)
            response_time = time.time() - start_time
            
            # Log performance
            self._log_performance(model.name, response_time, True)
            
            return {
                "success": True,
                "response": response,
                "model_used": model.name,
                "response_time": response_time,
                "offline_mode": self.connection_state == ConnectionState.OFFLINE,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            self._log_performance(model.name, response_time, False, str(e))
            
            # Try fallback model
            fallback_model = self._get_fallback_model(model)
            if fallback_model:
                logger.info(f"Trying fallback model: {fallback_model.name}")
                return self.generate_response(prompt, fallback_model.name)
                
            return {
                "success": False,
                "error": str(e),
                "model_attempted": model.name,
                "offline_mode": self.connection_state == ConnectionState.OFFLINE,
                "timestamp": datetime.now().isoformat()
            }
            
    def _select_best_model(self, preference: Optional[str] = None) -> Optional[ModelConfig]:
        """Select the best available model"""
        
        # Use preference if specified and available
        if preference and preference in self.models:
            model = self.models[preference]
            if self._is_model_available(model):
                return model
                
        # If offline, use cached models only
        if self.connection_state == ConnectionState.OFFLINE:
            cached_models = [m for m in self.models.values() if self._is_model_cached(m)]
            if cached_models:
                return min(cached_models, key=lambda m: m.priority.value)
                
        # Use best available model by priority
        available_models = [m for m in self.models.values() if self._is_model_available(m)]
        if available_models:
            return min(available_models, key=lambda m: m.priority.value)
            
        return None
        
    def _generate_with_model(self, model: ModelConfig, prompt: str) -> str:
        """Generate response using specific model"""
        
        if self.connection_state == ConnectionState.OFFLINE and model.local_path:
            # Use local model
            return self._generate_offline(model, prompt)
        else:
            # Use online endpoint
            return self._generate_online(model, prompt)
            
    def _generate_offline(self, model: ModelConfig, prompt: str) -> str:
        """Generate response using offline model"""
        # This would integrate with local model inference
        # For now, return a placeholder
        return f"[Offline response from {model.name}] {prompt[:50]}..."
        
    def _generate_online(self, model: ModelConfig, prompt: str) -> str:
        """Generate response using online endpoint"""
        
        payload = {
            "model": model.name,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{model.endpoint}/api/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"API error: {response.status_code}")
            
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        available_models = self._get_available_models()
        cached_models = [m.name for m in self.models.values() if self._is_model_cached(m)]
        
        return {
            "connection_state": self.connection_state.value,
            "available_models": available_models,
            "cached_models": cached_models,
            "active_model": self.active_model.name if self.active_model else None,
            "cache_size_gb": self._get_cache_size(),
            "last_online_check": self.last_online_check.isoformat(),
            "redundancy_healthy": len(available_models) >= self.redundancy_settings["min_models_available"],
            "emergency_models_ready": len([m for m in self.models.values() if m.priority == ModelPriority.EMERGENCY and self._is_model_cached(m)]) > 0
        }
        
    def _get_cache_size(self) -> float:
        """Get total cache size in GB"""
        total_size = 0
        for file_path in self.cache_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024**3)  # Convert to GB
        
    def _log_performance(self, model_name: str, response_time: float, success: bool, error_msg: str = None):
        """Log performance metrics to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO performance_logs (model_name, response_time, success, error_message) VALUES (?, ?, ?, ?)",
            (model_name, response_time, success, error_msg)
        )
        conn.commit()
        conn.close()
        
    def _update_model_in_db(self, model: ModelConfig):
        """Update model information in database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO models 
            (name, size_gb, priority, endpoint, local_path, last_used, success_rate, avg_response_time, capabilities, download_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            model.name,
            model.size_gb,
            model.priority.value,
            model.endpoint,
            model.local_path,
            model.last_used.isoformat() if model.last_used else None,
            model.success_rate,
            model.avg_response_time,
            json.dumps(model.capabilities) if model.capabilities else None,
            "downloaded"
        ))
        conn.commit()
        conn.close()
        
    def _cleanup_cache(self):
        """Clean up old cached models"""
        logger.info("Cleaning up model cache")
        
        # Get model usage statistics
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT model_name, MAX(timestamp) as last_used, COUNT(*) as usage_count
            FROM performance_logs 
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY model_name
            ORDER BY last_used ASC
        ''')
        
        usage_stats = cursor.fetchall()
        conn.close()
        
        # Remove least used models if needed
        current_size = self._get_cache_size()
        max_size = self.cache_settings["max_cache_size_gb"]
        
        for model_name, last_used, usage_count in usage_stats:
            if current_size <= max_size * 0.8:  # Keep under 80% capacity
                break
                
            model = self.models.get(model_name)
            if model and model.priority != ModelPriority.EMERGENCY:
                cache_path = self.cache_dir / f"{model.name}.gguf"
                if cache_path.exists():
                    file_size = cache_path.stat().st_size / (1024**3)
                    cache_path.unlink()
                    current_size -= file_size
                    logger.info(f"Removed cached model: {model_name} ({file_size:.1f}GB)")
                    
    def _get_fallback_model(self, failed_model):
        """Get fallback model if current model fails"""
        available_models = [m for m in self.models.values() 
                          if self._is_model_available(m) and m.name != failed_model.name]
        
        if available_models:
            # Return next best priority model
            return min(available_models, key=lambda m: m.priority.value)
        return None
        
    def _refresh_available_models(self):
        """Refresh the list of available models from endpoints"""
        logger.info("Refreshing available models list")
        
        for endpoint in self.fallback_endpoints:
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                if response.status_code == 200:
                    models_data = response.json()
                    available_model_names = [m.get("name", "") for m in models_data.get("models", [])]
                    logger.info(f"Found {len(available_model_names)} models at {endpoint}")
                    break
            except:
                continue
                
    def _upload_offline_metrics(self):
        """Upload metrics collected during offline operation"""
        logger.info("Uploading offline metrics")
        
        # Read recent performance logs from database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM performance_logs 
            WHERE timestamp > datetime('now', '-1 hour')
            ORDER BY timestamp DESC
        ''')
        
        recent_logs = cursor.fetchall()
        conn.close()
        
        logger.info(f"Found {len(recent_logs)} recent performance logs")
        
    def _update_performance_metrics(self):
        """Update model performance metrics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Calculate success rates and average response times per model
        cursor.execute('''
            SELECT model_name, 
                   AVG(CASE WHEN success = 1 THEN 1.0 ELSE 0.0 END) as success_rate,
                   AVG(response_time) as avg_response_time,
                   COUNT(*) as total_requests
            FROM performance_logs 
            WHERE timestamp > datetime('now', '-24 hours')
            GROUP BY model_name
        ''')
        
        performance_data = cursor.fetchall()
        conn.close()
        
        # Update model configurations
        for model_name, success_rate, avg_response_time, total_requests in performance_data:
            if model_name in self.models:
                model = self.models[model_name]
                model.success_rate = success_rate or 0.0
                model.avg_response_time = avg_response_time or 0.0
                logger.debug(f"Updated metrics for {model_name}: {success_rate:.2f} success rate, {avg_response_time:.2f}s avg response time")

if __name__ == "__main__":
    # Test the offline manager
    manager = OfflineLLMManager()
    
    print("Offline LLM Manager Status:")
    status = manager.get_system_status()
    print(json.dumps(status, indent=2))
    
    # Test response generation
    response = manager.generate_response("Hello, how are you?")
    print("\nTest Response:")
    print(json.dumps(response, indent=2))