"""
Synapse Configuration Management

Handles configuration loading, validation, and management for the Synapse plugin gateway.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field, asdict
import logging

@dataclass
class SandboxConfig:
    """Sandbox configuration."""
    max_cpu_percent: float = 50.0
    max_memory_mb: int = 512
    max_disk_mb: int = 100
    max_execution_time: int = 300
    max_processes: int = 5
    allowed_network_hosts: list = field(default_factory=list)
    allowed_file_paths: list = field(default_factory=list)
    read_only_paths: list = field(default_factory=list)

@dataclass
class BenchmarkConfig:
    """Benchmark configuration."""
    test_duration: int = 30
    max_concurrent_tests: int = 3
    response_time_threshold: float = 1000.0
    error_rate_threshold: float = 0.05
    cpu_usage_threshold: float = 80.0
    memory_usage_threshold: float = 512.0
    throughput_threshold: float = 10.0

@dataclass
class TrafficConfig:
    """Traffic logging configuration."""
    max_entries: int = 10000
    retention_days: int = 30
    log_level: str = "INFO"
    enable_audit_log: bool = True
    export_formats: list = field(default_factory=lambda: ["json", "csv"])

@dataclass
class SecurityConfig:
    """Security configuration."""
    require_manifest_signature: bool = True
    auto_approve_low_risk: bool = False
    max_concurrent_executions: int = 10
    require_user_approval: bool = True
    session_timeout_minutes: int = 60
    max_plugin_size_mb: int = 50

@dataclass
class SynapseConfig:
    """Complete Synapse configuration."""
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    traffic: TrafficConfig = field(default_factory=TrafficConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Plugin directories
    plugin_directories: list = field(default_factory=lambda: ["./plugins"])
    
    # API configuration
    api_host: str = "localhost"
    api_port: int = 8000
    api_debug: bool = False
    
    # Logging configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "sandbox": asdict(self.sandbox),
            "benchmark": asdict(self.benchmark),
            "traffic": asdict(self.traffic),
            "security": asdict(self.security),
            "plugin_directories": self.plugin_directories,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "api_debug": self.api_debug,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "log_format": self.log_format
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SynapseConfig':
        """Create configuration from dictionary."""
        config = cls()
        
        if "sandbox" in data:
            config.sandbox = SandboxConfig(**data["sandbox"])
        if "benchmark" in data:
            config.benchmark = BenchmarkConfig(**data["benchmark"])
        if "traffic" in data:
            config.traffic = TrafficConfig(**data["traffic"])
        if "security" in data:
            config.security = SecurityConfig(**data["security"])
        
        # Update other fields
        for field_name in ["plugin_directories", "api_host", "api_port", "api_debug", 
                          "log_level", "log_file", "log_format"]:
            if field_name in data:
                setattr(config, field_name, data[field_name])
        
        return config

class ConfigManager:
    """Manages Synapse configuration loading and validation."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> SynapseConfig:
        """
        Load configuration from file.
        
        Returns:
            Synapse configuration
        """
        config_path = Path(self.config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                config = SynapseConfig.from_dict(config_data)
                self.logger.info(f"Configuration loaded from {config_path}")
                return config
                
            except Exception as e:
                self.logger.warning(f"Failed to load configuration from {config_path}: {e}")
                self.logger.info("Using default configuration")
        
        # Return default configuration
        return SynapseConfig()
    
    def save_config(self, config: SynapseConfig) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            
        Returns:
            Success status
        """
        try:
            config_path = Path(self.config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            self.logger.info(f"Configuration saved to {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            return False
    
    def create_default_config(self) -> bool:
        """
        Create default configuration file.
        
        Returns:
            Success status
        """
        config = SynapseConfig()
        return self.save_config(config)
    
    def validate_config(self, config: SynapseConfig) -> tuple[bool, list[str]]:
        """
        Validate configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate sandbox configuration
        if config.sandbox.max_cpu_percent <= 0 or config.sandbox.max_cpu_percent > 100:
            errors.append("Invalid max_cpu_percent: must be between 0 and 100")
        
        if config.sandbox.max_memory_mb <= 0:
            errors.append("Invalid max_memory_mb: must be positive")
        
        if config.sandbox.max_execution_time <= 0:
            errors.append("Invalid max_execution_time: must be positive")
        
        # Validate benchmark configuration
        if config.benchmark.test_duration <= 0:
            errors.append("Invalid test_duration: must be positive")
        
        if config.benchmark.response_time_threshold <= 0:
            errors.append("Invalid response_time_threshold: must be positive")
        
        # Validate traffic configuration
        if config.traffic.max_entries <= 0:
            errors.append("Invalid max_entries: must be positive")
        
        if config.traffic.retention_days <= 0:
            errors.append("Invalid retention_days: must be positive")
        
        # Validate security configuration
        if config.security.max_concurrent_executions <= 0:
            errors.append("Invalid max_concurrent_executions: must be positive")
        
        if config.security.session_timeout_minutes <= 0:
            errors.append("Invalid session_timeout_minutes: must be positive")
        
        # Validate API configuration
        if config.api_port <= 0 or config.api_port > 65535:
            errors.append("Invalid api_port: must be between 1 and 65535")
        
        return len(errors) == 0, errors
    
    def get_environment_config(self) -> Dict[str, Any]:
        """
        Get configuration from environment variables.
        
        Returns:
            Environment configuration
        """
        config = {}
        
        # Sandbox configuration
        if os.getenv("SYNAPSE_SANDBOX_MAX_CPU"):
            config.setdefault("sandbox", {})["max_cpu_percent"] = float(os.getenv("SYNAPSE_SANDBOX_MAX_CPU"))
        
        if os.getenv("SYNAPSE_SANDBOX_MAX_MEMORY"):
            config.setdefault("sandbox", {})["max_memory_mb"] = int(os.getenv("SYNAPSE_SANDBOX_MAX_MEMORY"))
        
        if os.getenv("SYNAPSE_SANDBOX_MAX_EXECUTION_TIME"):
            config.setdefault("sandbox", {})["max_execution_time"] = int(os.getenv("SYNAPSE_SANDBOX_MAX_EXECUTION_TIME"))
        
        # API configuration
        if os.getenv("SYNAPSE_API_HOST"):
            config["api_host"] = os.getenv("SYNAPSE_API_HOST")
        
        if os.getenv("SYNAPSE_API_PORT"):
            config["api_port"] = int(os.getenv("SYNAPSE_API_PORT"))
        
        if os.getenv("SYNAPSE_API_DEBUG"):
            config["api_debug"] = os.getenv("SYNAPSE_API_DEBUG").lower() == "true"
        
        # Logging configuration
        if os.getenv("SYNAPSE_LOG_LEVEL"):
            config["log_level"] = os.getenv("SYNAPSE_LOG_LEVEL")
        
        if os.getenv("SYNAPSE_LOG_FILE"):
            config["log_file"] = os.getenv("SYNAPSE_LOG_FILE")
        
        return config
    
    def merge_configs(self, base_config: SynapseConfig, env_config: Dict[str, Any]) -> SynapseConfig:
        """
        Merge base configuration with environment configuration.
        
        Args:
            base_config: Base configuration
            env_config: Environment configuration
            
        Returns:
            Merged configuration
        """
        config = SynapseConfig.from_dict(base_config.to_dict())
        
        # Merge sandbox configuration
        if "sandbox" in env_config:
            for key, value in env_config["sandbox"].items():
                if hasattr(config.sandbox, key):
                    setattr(config.sandbox, key, value)
        
        # Merge other configurations
        for key, value in env_config.items():
            if key != "sandbox" and hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        # Try to use XDG config directory
        xdg_config_home = os.getenv("XDG_CONFIG_HOME")
        if xdg_config_home:
            return os.path.join(xdg_config_home, "hearthlink", "synapse_config.json")
        
        # Fall back to user home directory
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".hearthlink", "synapse_config.json")

# Default configuration
DEFAULT_CONFIG = {
    "sandbox": {
        "max_cpu_percent": 50.0,
        "max_memory_mb": 512,
        "max_disk_mb": 100,
        "max_execution_time": 300,
        "max_processes": 5,
        "allowed_network_hosts": [],
        "allowed_file_paths": [],
        "read_only_paths": []
    },
    "benchmark": {
        "test_duration": 30,
        "max_concurrent_tests": 3,
        "response_time_threshold": 1000.0,
        "error_rate_threshold": 0.05,
        "cpu_usage_threshold": 80.0,
        "memory_usage_threshold": 512.0,
        "throughput_threshold": 10.0
    },
    "traffic": {
        "max_entries": 10000,
        "retention_days": 30,
        "log_level": "INFO",
        "enable_audit_log": True,
        "export_formats": ["json", "csv"]
    },
    "security": {
        "require_manifest_signature": True,
        "auto_approve_low_risk": False,
        "max_concurrent_executions": 10,
        "require_user_approval": True,
        "session_timeout_minutes": 60,
        "max_plugin_size_mb": 50
    },
    "plugin_directories": ["./plugins"],
    "api_host": "localhost",
    "api_port": 8000,
    "api_debug": False,
    "log_level": "INFO",
    "log_file": None,
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 