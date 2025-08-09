#!/usr/bin/env python3
"""
Hearthlink Environment Loader
Centralized environment variable loading with validation and type conversion
"""

import os
import sys
from pathlib import Path
from typing import Optional, Any, Dict, List, Union
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class EnvironmentLoader:
    """Centralized environment variable loader with validation"""
    
    # Required environment variables grouped by service
    REQUIRED_VARS = {
        'core': [
            'NODE_ENV',
            'DATABASE_URL',
            'JWT_SECRET',
            'ENCRYPTION_KEY'
        ],
        'frontend': [
            'PORT',
            'REACT_APP_HEARTHLINK_API'
        ],
        'database': [
            'POSTGRES_HOST',
            'POSTGRES_PORT',
            'POSTGRES_DB',
            'POSTGRES_USER'
        ],
        'ai_services': [
            'ANTHROPIC_API_KEY'
        ],
        'security': [
            'JWT_SECRET',
            'ENCRYPTION_KEY',
            'SESSION_SECRET'
        ]
    }
    
    # Optional variables with defaults
    DEFAULTS = {
        'NODE_ENV': 'development',
        'DEBUG': 'true',
        'LOG_LEVEL': 'info',
        'PORT': '3005',
        'API_PORT': '8000',
        'API_HOST': 'localhost',
        'CORS_ORIGIN': 'http://localhost:3005',
        'POSTGRES_PORT': '5432',
        'REDIS_PORT': '6379',
        'JWT_EXPIRES_IN': '24h',
        'EMBEDDING_DIMENSION': '384',
        'DEFAULT_SIMILARITY_THRESHOLD': '0.7',
        'DEFAULT_MAX_RESULTS': '10',
        'HEALTH_CHECK_INTERVAL': '30000',
        'HEALTH_CHECK_TIMEOUT': '5000'
    }
    
    def __init__(self, env_file_path: Optional[str] = None):
        """Initialize environment loader
        
        Args:
            env_file_path: Optional path to .env file. Defaults to project root/.env
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.env_file = env_file_path or self.project_root / '.env'
        self.env_vars: Dict[str, str] = {}
        self.load_environment()
    
    def load_environment(self) -> None:
        """Load environment variables from .env file and system environment"""
        try:
            # Load from .env file if it exists
            if self.env_file.exists():
                load_dotenv(self.env_file, override=True)
                logger.info(f"Loaded environment from {self.env_file}")
            else:
                logger.warning(f"Environment file not found: {self.env_file}")
            
            # Cache all environment variables
            self.env_vars = dict(os.environ)
            
            # Apply defaults for missing values
            self._apply_defaults()
            
        except Exception as e:
            logger.error(f"Failed to load environment: {e}")
            raise
    
    def _apply_defaults(self) -> None:
        """Apply default values for missing environment variables"""
        for key, default_value in self.DEFAULTS.items():
            if key not in self.env_vars or not self.env_vars[key]:
                self.env_vars[key] = default_value
                os.environ[key] = default_value
    
    def get(self, key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        """Get environment variable with optional default and validation
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether the variable is required
            
        Returns:
            Environment variable value or default
            
        Raises:
            ValueError: If required variable is missing
        """
        value = self.env_vars.get(key, default)
        
        if required and not value:
            raise ValueError(f"Required environment variable '{key}' is missing")
        
        return value
    
    def get_int(self, key: str, default: Optional[int] = None, required: bool = False) -> Optional[int]:
        """Get environment variable as integer"""
        value = self.get(key, str(default) if default is not None else None, required)
        
        if value is None:
            return None
        
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}")
            return default
    
    def get_bool(self, key: str, default: Optional[bool] = None, required: bool = False) -> Optional[bool]:
        """Get environment variable as boolean"""
        value = self.get(key, str(default).lower() if default is not None else None, required)
        
        if value is None:
            return None
        
        return value.lower() in ('true', '1', 'yes', 'on')
    
    def get_float(self, key: str, default: Optional[float] = None, required: bool = False) -> Optional[float]:
        """Get environment variable as float"""
        value = self.get(key, str(default) if default is not None else None, required)
        
        if value is None:
            return None
        
        try:
            return float(value)
        except ValueError:
            logger.warning(f"Invalid float value for {key}: {value}")
            return default
    
    def get_list(self, key: str, separator: str = ',', default: Optional[List[str]] = None, 
                 required: bool = False) -> Optional[List[str]]:
        """Get environment variable as list of strings"""
        value = self.get(key, separator.join(default) if default else None, required)
        
        if value is None:
            return None
        
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    def validate_required_vars(self, service_group: Optional[str] = None) -> List[str]:
        """Validate that required environment variables are present
        
        Args:
            service_group: Optional service group to validate ('core', 'frontend', etc.)
            
        Returns:
            List of missing required variables
        """
        missing_vars = []
        
        if service_group:
            required_vars = self.REQUIRED_VARS.get(service_group, [])
        else:
            # Validate all required variables
            required_vars = []
            for group_vars in self.REQUIRED_VARS.values():
                required_vars.extend(group_vars)
        
        for var in required_vars:
            if not self.get(var):
                missing_vars.append(var)
        
        return missing_vars
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            'database_url': self.get('DATABASE_URL', required=True),
            'postgres': {
                'host': self.get('POSTGRES_HOST', 'localhost'),
                'port': self.get_int('POSTGRES_PORT', 5432),
                'database': self.get('POSTGRES_DB', 'hearthlink'),
                'user': self.get('POSTGRES_USER', 'hearthlink_user'),
                'password': self.get('POSTGRES_PASSWORD')
            },
            'pgvector': {
                'host': self.get('PGVECTOR_HOST', 'localhost'),
                'port': self.get_int('PGVECTOR_PORT', 5432),
                'database': self.get('PGVECTOR_DATABASE', 'hearthlink_vectors'),
                'user': self.get('PGVECTOR_USER', 'hearthlink_user'),
                'password': self.get('PGVECTOR_PASSWORD'),
                'url': self.get('PGVECTOR_URL')
            },
            'redis': {
                'host': self.get('REDIS_HOST', 'localhost'),
                'port': self.get_int('REDIS_PORT', 6379),
                'password': self.get('REDIS_PASSWORD')
            },
            'neo4j': {
                'uri': self.get('NEO4J_URI', 'bolt://localhost:7687'),
                'user': self.get('NEO4J_USER', 'neo4j'),
                'password': self.get('NEO4J_PASSWORD')
            }
        }
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get external API keys configuration"""
        return {
            'anthropic': self.get('ANTHROPIC_API_KEY'),
            'openai': self.get('OPENAI_API_KEY'),
            'google': self.get('GOOGLE_API_KEY'),
            'gemini': self.get('REACT_APP_GEMINI_API_KEY'),
            'elevenlabs': self.get('ELEVENLABS_API_KEY'),
            'whisper': self.get('WHISPER_API_KEY'),
            'sentry': self.get('SENTRY_DSN')
        }
    
    def get_security_config(self) -> Dict[str, str]:
        """Get security configuration"""
        return {
            'jwt_secret': self.get('JWT_SECRET', required=True),
            'jwt_expires_in': self.get('JWT_EXPIRES_IN', '24h'),
            'refresh_token_secret': self.get('REFRESH_TOKEN_SECRET'),
            'encryption_key': self.get('ENCRYPTION_KEY', required=True),
            'session_secret': self.get('SESSION_SECRET'),
            'cors_origin': self.get('CORS_ORIGIN', 'http://localhost:3005')
        }
    
    def get_service_config(self) -> Dict[str, Any]:
        """Get service configuration"""
        return {
            'node_env': self.get('NODE_ENV', 'development'),
            'debug': self.get_bool('DEBUG', True),
            'log_level': self.get('LOG_LEVEL', 'info'),
            'frontend_port': self.get_int('PORT', 3005),
            'api_port': self.get_int('API_PORT', 8000),
            'api_host': self.get('API_HOST', 'localhost'),
            'health_check_interval': self.get_int('HEALTH_CHECK_INTERVAL', 30000),
            'health_check_timeout': self.get_int('HEALTH_CHECK_TIMEOUT', 5000)
        }
    
    def print_summary(self) -> None:
        """Print environment configuration summary"""
        print("\n" + "="*60)
        print("HEARTHLINK ENVIRONMENT CONFIGURATION")
        print("="*60)
        
        config = self.get_service_config()
        print(f"Environment: {config['node_env']}")
        print(f"Debug Mode: {config['debug']}")
        print(f"Log Level: {config['log_level']}")
        print(f"Frontend Port: {config['frontend_port']}")
        print(f"API Port: {config['api_port']}")
        
        # Validate required variables
        missing_vars = self.validate_required_vars()
        if missing_vars:
            print(f"\n⚠️  Missing Required Variables: {', '.join(missing_vars)}")
        else:
            print("\n✅ All required variables are configured")
        
        print("="*60 + "\n")

# Global environment loader instance
env_loader = EnvironmentLoader()

# Convenience functions for direct access
def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get environment variable"""
    return env_loader.get(key, default, required)

def get_env_int(key: str, default: Optional[int] = None, required: bool = False) -> Optional[int]:
    """Get environment variable as integer"""
    return env_loader.get_int(key, default, required)

def get_env_bool(key: str, default: Optional[bool] = None, required: bool = False) -> Optional[bool]:
    """Get environment variable as boolean"""
    return env_loader.get_bool(key, default, required)

def validate_environment(service_group: Optional[str] = None) -> bool:
    """Validate environment configuration"""
    missing_vars = env_loader.validate_required_vars(service_group)
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

if __name__ == "__main__":
    # Print environment summary when run directly
    env_loader.print_summary()