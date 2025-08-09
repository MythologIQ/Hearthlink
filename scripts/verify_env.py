#!/usr/bin/env python3
"""
Hearthlink Environment Verification Script
Validates environment configuration and ensures all required variables are present
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any
import re

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from utils.env_loader import EnvironmentLoader
except ImportError:
    print("⚠️  Warning: Could not import env_loader, using basic validation")
    EnvironmentLoader = None

try:
    import jsonschema
except ImportError:
    print("⚠️  Warning: jsonschema not available, JSON schema validation disabled")
    jsonschema = None

class EnvironmentVerifier:
    """Comprehensive environment verification"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / '.env'
        self.env_example_file = self.project_root / '.env.example'
        self.config_schema_file = self.project_root / 'config' / 'schema.json'
        self.config_files = {
            'core': self.project_root / 'config' / 'core_config.json',
            'vault': self.project_root / 'config' / 'vault_config.json', 
            'synapse': self.project_root / 'config' / 'synapse_config.json'
        }
        self.errors = []
        self.warnings = []
        self.strict_mode = False
        
        # Expected environment variable patterns
        self.variable_patterns = {
            'ports': re.compile(r'^(PORT|.*_PORT)$'),
            'passwords': re.compile(r'^.*PASSWORD.*$'),
            'secrets': re.compile(r'^.*SECRET.*$'),
            'keys': re.compile(r'^.*KEY.*$'),
            'urls': re.compile(r'^.*URL.*$'),
            'hosts': re.compile(r'^.*HOST.*$')
        }
        
        # Deprecated environment files that should not exist
        self.deprecated_files = [
            '.env.local',
            '.env.development', 
            '.env.production',
            '.env.pgvector',
            'deploy/.env.production'
        ]
    
    def check_file_existence(self) -> bool:
        """Check that required files exist and deprecated files don't"""
        success = True
        
        # Check required files
        if not self.env_example_file.exists():
            self.errors.append(f"Required file missing: {self.env_example_file}")
            success = False
        
        if not self.env_file.exists():
            self.warnings.append(f"Environment file missing: {self.env_file}")
            self.warnings.append("Copy .env.example to .env and fill in your values")
        
        # Check for deprecated files
        for deprecated_file in self.deprecated_files:
            deprecated_path = self.project_root / deprecated_file
            if deprecated_path.exists():
                self.warnings.append(f"Deprecated environment file found: {deprecated_file}")
                self.warnings.append(f"Consider removing {deprecated_file} - variables should be in .env")
        
        return success
    
    def parse_env_file(self, file_path: Path) -> Dict[str, str]:
        """Parse environment file and return variables"""
        variables = {}
        
        if not file_path.exists():
            return variables
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse variable assignment
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        variables[key] = value
                    else:
                        self.warnings.append(f"Invalid line format in {file_path.name}:{line_num}: {line}")
        
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
        
        return variables
    
    def validate_variable_formats(self, variables: Dict[str, str]) -> bool:
        """Validate variable formats and values"""
        success = True
        
        for key, value in variables.items():
            # Check for placeholder values
            placeholder_indicators = [
                'your_', 'your-', 'replace_', 'change_', 'example_',
                'localhost', 'password', 'secret', 'key_here'
            ]
            
            if any(indicator in value.lower() for indicator in placeholder_indicators):
                if not key.startswith('REACT_APP_HEARTHLINK_API') and 'localhost' not in key:
                    self.warnings.append(f"Variable {key} appears to have placeholder value: {value}")
            
            # Validate specific variable types
            if self.variable_patterns['ports'].match(key):
                try:
                    port = int(value)
                    if not (1 <= port <= 65535):
                        self.errors.append(f"Invalid port number for {key}: {port}")
                        success = False
                except ValueError:
                    self.errors.append(f"Port variable {key} must be a number: {value}")
                    success = False
            
            # Check for empty required-looking variables
            if any(pattern in key.upper() for pattern in ['SECRET', 'KEY', 'PASSWORD']):
                if not value or len(value) < 8:
                    self.warnings.append(f"Security variable {key} appears too short or empty")
        
        return success
    
    def check_variable_completeness(self) -> bool:
        """Check that .env has all variables from .env.example"""
        success = True
        
        if not self.env_file.exists():
            return True  # Skip if no .env file
        
        example_vars = self.parse_env_file(self.env_example_file)
        actual_vars = self.parse_env_file(self.env_file)
        
        example_keys = set(example_vars.keys())
        actual_keys = set(actual_vars.keys())
        
        missing_vars = example_keys - actual_keys
        extra_vars = actual_keys - example_keys
        
        if missing_vars:
            self.warnings.append(f"Variables in .env.example but not in .env: {', '.join(sorted(missing_vars))}")
        
        if extra_vars:
            self.warnings.append(f"Variables in .env but not in .env.example: {', '.join(sorted(extra_vars))}")
        
        return success
    
    def validate_with_loader(self) -> bool:
        """Use the environment loader for advanced validation"""
        if not EnvironmentLoader:
            return True
        
        success = True
        
        try:
            loader = EnvironmentLoader()
            
            # Validate each service group
            service_groups = ['core', 'frontend', 'database', 'ai_services', 'security']
            
            for group in service_groups:
                missing_vars = loader.validate_required_vars(group)
                if missing_vars:
                    self.errors.append(f"Missing required {group} variables: {', '.join(missing_vars)}")
                    success = False
            
            # Test configuration retrieval
            try:
                loader.get_database_config()
                loader.get_api_keys()
                loader.get_security_config()
                loader.get_service_config()
            except Exception as e:
                self.errors.append(f"Error loading configuration: {e}")
                success = False
                
        except Exception as e:
            self.errors.append(f"Environment loader validation failed: {e}")
            success = False
        
        return success
    
    def check_security_issues(self, variables: Dict[str, str]) -> bool:
        """Check for common security issues"""
        success = True
        
        # Check for weak secrets
        security_vars = [k for k in variables.keys() if any(term in k.upper() for term in ['SECRET', 'KEY', 'PASSWORD'])]
        
        for var in security_vars:
            value = variables[var]
            
            # Check length
            if len(value) < 16:
                self.warnings.append(f"Security variable {var} should be at least 16 characters long")
            
            # Check for common weak values
            weak_values = ['password', '123456', 'secret', 'admin', 'test']
            if value.lower() in weak_values:
                self.errors.append(f"Security variable {var} uses weak value: {value}")
                success = False
        
        return success
    
    def load_config_schema(self) -> Dict[str, Any]:
        """Load the JSON configuration schema"""
        if not self.config_schema_file.exists():
            self.errors.append(f"Configuration schema file missing: {self.config_schema_file}")
            return {}
        
        try:
            with open(self.config_schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            return schema
        except Exception as e:
            self.errors.append(f"Error loading configuration schema: {e}")
            return {}
    
    def validate_config_files(self) -> bool:
        """Validate configuration files against JSON schema"""
        if not jsonschema:
            self.warnings.append("JSON schema validation skipped - jsonschema package not available")
            return True
        
        success = True
        schema = self.load_config_schema()
        
        if not schema:
            return False
        
        # Validate each configuration file
        for module_name, config_file in self.config_files.items():
            if not config_file.exists():
                if self.strict_mode:
                    self.errors.append(f"Required configuration file missing: {config_file}")
                    success = False
                else:
                    self.warnings.append(f"Configuration file missing: {config_file}")
                continue
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Validate against the corresponding schema section
                if module_name in schema.get('properties', {}):
                    # Create a standalone schema with definitions for validation
                    module_schema = {
                        "type": "object",
                        "definitions": schema.get('definitions', {}),
                        "properties": schema['properties'][module_name].get('properties', {}),
                        "required": schema['properties'][module_name].get('required', [])
                    }
                    
                    try:
                        jsonschema.validate(config_data, module_schema)
                    except jsonschema.ValidationError as e:
                        # Try validating just the structure without strict schema
                        self.warnings.append(f"Schema validation issue for {module_name}: {e.message}")
                        continue
                    print(f"✅ {module_name.title()} configuration valid")
                else:
                    self.warnings.append(f"No schema definition found for {module_name} module")
                
            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid JSON in {config_file}: {e}")
                success = False
            except jsonschema.ValidationError as e:
                self.errors.append(f"Schema validation failed for {module_name}: {e.message}")
                success = False
            except Exception as e:
                self.errors.append(f"Error validating {config_file}: {e}")
                success = False
        
        return success
    
    def validate_cross_service_config_alignment(self) -> bool:
        """Validate that configuration values are aligned across services"""
        success = True
        
        # Load all config files
        configs = {}
        for module_name, config_file in self.config_files.items():
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        configs[module_name] = json.load(f)
                except Exception as e:
                    self.warnings.append(f"Could not load {module_name} config for alignment check: {e}")
        
        # Check alignment between services
        alignment_checks = [
            # Check that Core and frontend URLs are consistent
            {
                'core_path': ['api', 'base_url'],
                'synapse_path': ['api', 'base_url'],
                'description': 'API base URLs should be consistent'
            },
            # Check that security levels align
            {
                'core_path': ['security', 'default_level'],
                'vault_path': ['security', 'default_level'], 
                'synapse_path': ['security', 'default_security_level'],
                'description': 'Security levels should be aligned'
            },
            # Check schema versions
            {
                'core_path': ['schema_version'],
                'vault_path': ['schema_version'],
                'synapse_path': ['schema_version'],
                'description': 'Schema versions should match'
            }
        ]
        
        for check in alignment_checks:
            values = {}
            for path_key, path in check.items():
                if path_key == 'description':
                    continue
                    
                module = path_key.split('_')[0]  # Extract module name
                if module in configs:
                    value = self._get_nested_value(configs[module], path)
                    if value is not None:
                        values[module] = value
            
            if len(values) > 1:
                unique_values = set(str(v) for v in values.values())
                if len(unique_values) > 1:
                    if self.strict_mode:
                        self.errors.append(f"Configuration alignment issue: {check['description']} - Found values: {values}")
                        success = False
                    else:
                        self.warnings.append(f"Configuration alignment issue: {check['description']} - Found values: {values}")
        
        return success
    
    def _get_nested_value(self, data: Dict, path: List[str]) -> Any:
        """Get nested value from dictionary using path"""
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def validate_required_env_vars_strict(self) -> bool:
        """Strict validation of required environment variables"""
        success = True
        
        # Define strictly required variables for Phase 1.5
        required_groups = {
            'core': [
                'CORE_API_PORT',
                'CORE_API_HOST',
                'DATABASE_PATH'
            ],
            'vault': [
                'VAULT_STORAGE_PATH',
                'VAULT_ENCRYPTION_KEY',
                'SECRET_KEY'
            ],
            'synapse': [
                'SYNAPSE_API_PORT',
                'SYNAPSE_PLUGIN_PATH'
            ],
            'frontend': [
                'REACT_APP_HEARTHLINK_API_URL',
                'PORT'
            ],
            'security': [
                'SECRET_KEY',
                'SESSION_SECRET'
            ]
        }
        
        # Load environment variables
        env_vars = dict(os.environ)
        if self.env_file.exists():
            file_vars = self.parse_env_file(self.env_file)
            env_vars.update(file_vars)
        
        # Check each group
        for group_name, required_vars in required_groups.items():
            missing_vars = []
            for var in required_vars:
                if var not in env_vars or not env_vars[var].strip():
                    missing_vars.append(var)
            
            if missing_vars:
                self.errors.append(f"Missing required {group_name} environment variables: {', '.join(missing_vars)}")
                success = False
        
        # Type validation for critical variables
        type_checks = {
            'CORE_API_PORT': ('int', 'Port numbers must be integers'),
            'SYNAPSE_API_PORT': ('int', 'Port numbers must be integers'),
            'PORT': ('int', 'Port numbers must be integers'),
            'VAULT_ENCRYPTION_KEY': ('min_length_32', 'Encryption key must be at least 32 characters'),
            'SECRET_KEY': ('min_length_32', 'Secret key must be at least 32 characters'),
            'SESSION_SECRET': ('min_length_32', 'Session secret must be at least 32 characters')
        }
        
        for var, (check_type, error_msg) in type_checks.items():
            if var in env_vars:
                value = env_vars[var]
                
                if check_type == 'int':
                    try:
                        int(value)
                    except ValueError:
                        self.errors.append(f"{var}: {error_msg}")
                        success = False
                
                elif check_type == 'min_length_32':
                    if len(value) < 32:
                        self.errors.append(f"{var}: {error_msg}")
                        success = False
        
        return success
    
    def run_verification(self, check_example_only: bool = False, strict_mode: bool = False) -> bool:
        """Run complete verification"""
        print("🔍 Hearthlink Environment Verification")
        if strict_mode:
            print("🔒 Running in STRICT MODE - all issues treated as errors")
        print("=" * 50)
        
        self.strict_mode = strict_mode
        success = True
        
        # Check file existence
        if not self.check_file_existence():
            success = False
        
        # Parse environment files
        example_vars = self.parse_env_file(self.env_example_file)
        actual_vars = self.parse_env_file(self.env_file) if not check_example_only else {}
        
        # Validate .env.example format
        if example_vars:
            print(f"✅ Parsed {len(example_vars)} variables from .env.example")
            if not self.validate_variable_formats(example_vars):
                success = False
        
        # Validate actual .env if it exists and not checking example only
        if actual_vars and not check_example_only:
            print(f"✅ Parsed {len(actual_vars)} variables from .env")
            
            if not self.validate_variable_formats(actual_vars):
                success = False
            
            if not self.check_security_issues(actual_vars):
                success = False
            
            if not self.check_variable_completeness():
                success = False
        
        # Advanced validation with environment loader
        if not check_example_only and not self.validate_with_loader():
            success = False
        
        # Phase 1.5 Configuration Schema Validation
        print("\n🔧 Configuration Schema Validation")
        if not self.validate_config_files():
            success = False
        if not self.validate_cross_service_config_alignment():
            success = False
        
        # Strict mode validation
        if strict_mode:
            print("\n🔒 Strict Mode Validation")
            if not self.validate_required_env_vars_strict():
                success = False
        
        # Print results
        self.print_results()
        
        return success
    
    def print_results(self):
        """Print verification results"""
        print("\n" + "=" * 50)
        
        if self.errors:
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if not self.errors and not self.warnings:
            print("✅ Environment configuration is valid!")
        elif not self.errors:
            print("✅ Environment configuration is valid (with warnings)")
        else:
            print("❌ Environment configuration has errors")
        
        print("=" * 50)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Verify Hearthlink environment configuration')
    parser.add_argument('--check-example', action='store_true', 
                       help='Only validate .env.example format (for CI)')
    parser.add_argument('--strict', action='store_true',
                       help='Enable strict mode - all issues treated as errors')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    verifier = EnvironmentVerifier()
    success = verifier.run_verification(
        check_example_only=args.check_example,
        strict_mode=args.strict
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()