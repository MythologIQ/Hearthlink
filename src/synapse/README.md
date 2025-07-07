# Synapse Plugin Gateway

## Overview

Synapse is the secure external gateway and protocol boundary for the Hearthlink system. It serves as the sole orchestrator and gatekeeper for all inbound/outbound traffic between Hearthlink, plugins, external LLMs, APIs, and web resources.

## Architecture

### Core Components

1. **Plugin Manager** (`plugin_manager.py`)
   - Main orchestrator for plugin lifecycle management
   - Handles registration, approval, execution, and revocation
   - Integrates all subsystems

2. **Manifest System** (`manifest.py`)
   - Plugin manifest validation and signing
   - Schema enforcement and risk assessment
   - Digital signature verification

3. **Permission Management** (`permissions.py`)
   - User approval workflows for plugin permissions
   - Permission dependency resolution
   - Risk-based permission assessment

4. **Sandbox Management** (`sandbox.py`)
   - Secure, isolated execution environments
   - Resource constraints and monitoring
   - Process isolation and cleanup

5. **Benchmarking System** (`benchmark.py`)
   - Performance evaluation and health checks
   - Risk scoring and performance tiering
   - Automated testing and recommendations

6. **Traffic Logger** (`traffic_logger.py`)
   - Comprehensive audit logging
   - Traffic analysis and monitoring
   - Export capabilities for compliance

7. **API Layer** (`api.py`)
   - RESTful API endpoints
   - FastAPI integration
   - Authentication and authorization

8. **Configuration Management** (`config.py`)
   - Configuration loading and validation
   - Environment variable support
   - Default configuration management

## Features

### Security
- **Manifest-based plugin loading** with digital signatures
- **Secure sandboxing** with resource constraints
- **Permission-based access control** with user approval
- **Comprehensive audit logging** for all operations
- **Risk assessment** and scoring for plugins

### Plugin Management
- **Plugin registration** with manifest validation
- **User approval workflows** for plugin installation
- **Permission management** with dependency resolution
- **Plugin execution** in isolated sandboxes
- **Performance benchmarking** and monitoring

### Monitoring & Compliance
- **Real-time traffic monitoring** with detailed logs
- **Performance metrics** and health checks
- **Export capabilities** for audit and compliance
- **System status monitoring** and reporting

### API Integration
- **RESTful API** for all operations
- **FastAPI** with automatic documentation
- **JWT-based authentication** (configurable)
- **Comprehensive error handling**

## Installation

### Prerequisites
- Python 3.8+
- FastAPI
- Pydantic
- Required system dependencies for sandboxing

### Setup
1. Install dependencies:
```bash
pip install fastapi uvicorn pydantic
```

2. Configure Synapse:
```python
from synapse.config import ConfigManager

config_manager = ConfigManager()
config = config_manager.load_config()
```

3. Initialize Synapse:
```python
from synapse.synapse import Synapse

synapse = Synapse(config)
```

## Usage

### Basic Plugin Management

```python
from synapse.synapse import Synapse

# Initialize Synapse
synapse = Synapse()

# Register a plugin
manifest_data = {
    "plugin_id": "my-plugin",
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "A test plugin",
    "author": "Developer",
    "requested_permissions": ["read_core"],
    "sandbox": True,
    "risk_tier": "low"
}

plugin_id = synapse.register_plugin(manifest_data, "user-123")

# Approve the plugin
synapse.approve_plugin(plugin_id, "user-123", "Testing purposes")

# Execute the plugin
payload = {"action": "test", "data": "hello world"}
result = synapse.execute_plugin(plugin_id, "user-123", payload)

print(f"Execution successful: {result.success}")
print(f"Output: {result.output}")
```

### Permission Management

```python
# Request permissions
permissions = ["read_core", "write_core", "network_access"]
request_id = synapse.request_permissions(plugin_id, "user-123", permissions)

# Approve permissions
synapse.approve_permissions(request_id, "user-123", "Approved for testing")

# Check permissions
has_permission = synapse.check_permission(plugin_id, "read_core")
print(f"Has read_core permission: {has_permission}")
```

### Connection Management

```python
# Request external connection
connection_id = synapse.request_connection(
    "external-agent-1",
    "data_processing",
    ["network_access"],
    "user-123"
)

# Approve connection
result = synapse.approve_connection(connection_id, "user-123")

# Close connection
synapse.close_connection(connection_id, "user-123")
```

### Monitoring and Analytics

```python
# Get traffic summary
summary = synapse.get_traffic_summary(hours=24)
print(f"Total events: {summary['total_events']}")

# Get system status
status = synapse.get_system_status()
print(f"Active plugins: {status['plugins']['active']}")

# Export traffic logs
exported_data = synapse.export_traffic_logs(format="json")
```

## API Endpoints

### Plugin Management
- `POST /api/synapse/plugin/register` - Register new plugin
- `POST /api/synapse/plugin/{id}/approve` - Approve plugin
- `POST /api/synapse/plugin/{id}/revoke` - Revoke plugin
- `POST /api/synapse/plugin/{id}/execute` - Execute plugin
- `GET /api/synapse/plugin/{id}/status` - Get plugin status
- `GET /api/synapse/plugins` - List plugins

### Permission Management
- `POST /api/synapse/plugin/{id}/permissions/request` - Request permissions
- `POST /api/synapse/permissions/{id}/approve` - Approve permissions
- `POST /api/synapse/permissions/{id}/deny` - Deny permissions
- `GET /api/synapse/permissions/pending` - Get pending requests

### Connection Management
- `POST /api/synapse/connection/request` - Request connection
- `POST /api/synapse/connection/{id}/approve` - Approve connection
- `POST /api/synapse/connection/{id}/close` - Close connection

### Monitoring
- `GET /api/synapse/traffic/logs` - Get traffic logs
- `GET /api/synapse/traffic/summary` - Get traffic summary
- `GET /api/synapse/traffic/export` - Export traffic logs
- `GET /api/synapse/system/status` - Get system status

### Benchmarking
- `POST /api/synapse/plugin/{id}/benchmark` - Run benchmark
- `GET /api/synapse/plugin/{id}/benchmark` - Get benchmark summary

## Configuration

### Configuration File
Synapse uses JSON configuration files. Default location: `~/.hearthlink/synapse_config.json`

```json
{
  "sandbox": {
    "max_cpu_percent": 50.0,
    "max_memory_mb": 512,
    "max_disk_mb": 100,
    "max_execution_time": 300
  },
  "benchmark": {
    "test_duration": 30,
    "response_time_threshold": 1000.0
  },
  "traffic": {
    "max_entries": 10000,
    "retention_days": 30
  },
  "security": {
    "require_manifest_signature": true,
    "auto_approve_low_risk": false,
    "max_concurrent_executions": 10
  },
  "api_host": "localhost",
  "api_port": 8000
}
```

### Environment Variables
- `SYNAPSE_SANDBOX_MAX_CPU` - Maximum CPU percentage
- `SYNAPSE_SANDBOX_MAX_MEMORY` - Maximum memory in MB
- `SYNAPSE_API_HOST` - API host
- `SYNAPSE_API_PORT` - API port
- `SYNAPSE_LOG_LEVEL` - Logging level

## Plugin Development

### Plugin Manifest
All plugins must include a manifest file:

```json
{
  "plugin_id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "description": "Plugin description",
  "author": "Author Name",
  "manifest_version": "1.0.0",
  "requested_permissions": ["read_core", "write_core"],
  "sandbox": true,
  "risk_tier": "low"
}
```

### Plugin Implementation
Plugins should:
- Read JSON input from stdin
- Process the request
- Output JSON response to stdout
- Handle errors gracefully

Example plugin structure:
```python
#!/usr/bin/env python3
import json
import sys

def main():
    # Read input
    input_data = sys.stdin.read()
    request = json.loads(input_data)
    
    # Process request
    result = process_request(request)
    
    # Output result
    print(json.dumps(result))

def process_request(request):
    # Plugin logic here
    return {"success": True, "result": "processed"}

if __name__ == "__main__":
    main()
```

## Security Considerations

### Sandboxing
- All plugins run in isolated sandboxes
- Resource limits are enforced
- Network access is restricted
- File system access is controlled

### Permission Model
- All permissions require explicit user approval
- Permission dependencies are automatically resolved
- Risk assessment is performed for permission combinations
- Permissions can be revoked at any time

### Audit Logging
- All operations are logged with timestamps
- User actions are tracked
- Plugin executions are monitored
- Export capabilities for compliance

### Manifest Signing
- Plugin manifests can be digitally signed
- Signature verification prevents tampering
- Unsigned manifests require user override

## Testing

### Running Tests
```bash
# Run the test script
python examples/test_synapse.py

# Test the API
uvicorn src.synapse.api:app --reload
```

### Test Coverage
The test script covers:
- Plugin registration and approval
- Permission management
- Plugin execution
- Benchmarking
- Traffic monitoring
- Connection management
- System status

## Troubleshooting

### Common Issues

1. **Plugin execution fails**
   - Check plugin manifest validity
   - Verify permissions are granted
   - Check sandbox resource limits

2. **Permission denied**
   - Ensure user has approved permissions
   - Check permission dependencies
   - Verify plugin is approved

3. **API connection issues**
   - Check API host and port configuration
   - Verify authentication tokens
   - Check firewall settings

### Logging
Synapse provides comprehensive logging:
- Plugin operations
- Permission changes
- Traffic events
- System status
- Error conditions

Logs are written to both console and file (if configured).

## Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies
3. Run tests to verify setup
4. Follow coding standards

### Code Standards
- Use type hints
- Follow PEP 8
- Include docstrings
- Write unit tests
- Update documentation

## License

This implementation is part of the Hearthlink project and follows the same licensing terms.

## Support

For issues and questions:
1. Check the documentation
2. Review the test examples
3. Check the logs for error details
4. Create an issue with detailed information 