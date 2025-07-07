# Plugin Ecosystem Guide - Hearthlink

**Module:** `feature/plugin-ecosystem-expansion`  
**Implementation:** Enhanced Synapse plugin system  
**Status:** ✅ Complete Implementation  
**Documentation Status:** ✅ Complete  

---

## Overview

The Hearthlink Plugin Ecosystem provides a comprehensive, secure, and extensible framework for developing and managing AI companion plugins. This enhanced system supports multi-level permissions, live sandbox reloading, plugin lifecycle events, and automated audit logging with performance benchmarking.

## Key Features

### 🔐 **Multi-Level Permission System**
- **Granular Access Control:** Read, Write, Execute, Admin levels
- **Resource-Specific Permissions:** Vault, Core, Network, File System, System, API, Plugin, User data
- **Scope-Based Restrictions:** Limit permissions to specific resources
- **Auto-Approval:** Low-risk permissions automatically approved
- **Permission Dependencies:** Automatic resolution of required permissions

### 🔄 **Live Sandbox Reloading**
- **Hot Reloading:** Update plugins without restarting the system
- **File Watching:** Automatic detection of plugin changes
- **Sandbox Isolation:** Maintain security during reloads
- **Rollback Support:** Automatic rollback on reload failures
- **Version Tracking:** Track plugin versions across reloads

### 📊 **Plugin Lifecycle Events**
- **Event Tracking:** Complete lifecycle from registration to uninstallation
- **State Transitions:** Track plugin status changes
- **Audit Trail:** Comprehensive logging of all lifecycle events
- **Event Handlers:** Custom handlers for lifecycle events
- **Timeline View:** Visual representation of plugin history

### 🎯 **Automated Audit Logging**
- **Comprehensive Logging:** All plugin activities logged
- **Performance Metrics:** Execution time, error rates, resource usage
- **Security Events:** Permission changes, access attempts, violations
- **Risk Assessment:** Automated risk scoring for plugin activities
- **Compliance Reporting:** Generate compliance reports

### ⚡ **Performance Benchmarking**
- **Automated Testing:** Regular performance benchmarks
- **Resource Monitoring:** CPU, memory, disk usage tracking
- **Throughput Analysis:** Operations per second metrics
- **Performance Tiers:** Categorize plugins by performance
- **Optimization Recommendations:** Suggest performance improvements

---

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Plugin Ecosystem                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Manifest  │  │ Permissions │  │   Sandbox   │        │
│  │   System    │  │   Manager   │  │   Manager   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    Plugin   │  │  Benchmark  │  │    Audit    │        │
│  │   Manager   │  │   Manager   │  │   Logger    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Traffic   │  │  Lifecycle  │  │    File     │        │
│  │   Logger    │  │   Events    │  │   Watcher   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Plugin Registration:** Manifest validation → Permission assessment → Sandbox setup
2. **Plugin Execution:** Permission check → Sandbox execution → Result processing
3. **Live Reloading:** File change detection → Sandbox reload → State update
4. **Audit Logging:** Event capture → Risk assessment → Log storage
5. **Benchmarking:** Performance testing → Metrics collection → Tier classification

---

## Plugin Development

### Manifest Structure

```json
{
  "plugin_id": "my-awesome-plugin",
  "name": "My Awesome Plugin",
  "version": "1.0.0",
  "description": "A comprehensive plugin for awesome functionality",
  "author": "Plugin Developer",
  "manifest_version": "2.0.0",
  
  "requested_permissions": [
    {
      "permission": "vault_read",
      "level": "read",
      "scope": "user_data",
      "conditions": {
        "time_restriction": "business_hours",
        "user_consent": true
      }
    },
    {
      "permission": "network_read",
      "level": "read",
      "scope": "api.example.com",
      "conditions": {
        "rate_limit": 100
      }
    }
  ],
  
  "capabilities": [
    {
      "name": "data_analysis",
      "description": "Analyze user data and provide insights",
      "version": "1.0.0",
      "parameters": {
        "data_type": "string",
        "analysis_depth": "number"
      },
      "return_type": "object",
      "async_support": true,
      "batch_support": false
    }
  ],
  
  "lifecycle_hooks": {
    "registered": "on_registered",
    "approved": "on_approved",
    "activated": "on_activated",
    "reloaded": "on_reloaded",
    "revoked": "on_revoked"
  },
  
  "sandbox": true,
  "sandbox_config": {
    "timeout": 300,
    "memory_limit": 512,
    "network_access": ["api.example.com"],
    "file_access": ["/tmp/plugin_data"]
  },
  
  "risk_tier": "moderate",
  "security_scan": true,
  "code_review_required": false,
  "performance_monitoring": true,
  "resource_limits": {
    "max_execution_time": 300,
    "max_memory_usage": 512,
    "max_cpu_percent": 50
  },
  
  "approved_by_user": false,
  "auto_approve": false
}
```

### Permission Levels

#### **Read Level**
- **Purpose:** View-only access to resources
- **Risk:** Low
- **Auto-approval:** Usually automatic
- **Examples:** Reading vault data, viewing system status

#### **Write Level**
- **Purpose:** Modify existing resources
- **Risk:** Moderate
- **Auto-approval:** Sometimes automatic
- **Examples:** Updating vault data, modifying configurations

#### **Execute Level**
- **Purpose:** Execute code or commands
- **Risk:** High
- **Auto-approval:** Rarely automatic
- **Examples:** Running system commands, executing scripts

#### **Admin Level**
- **Purpose:** Full administrative access
- **Risk:** Critical
- **Auto-approval:** Never automatic
- **Examples:** System administration, user management

### Permission Types

#### **Vault Permissions**
- `vault_read`: Read vault data
- `vault_write`: Write vault data
- `vault_admin`: Full vault administration

#### **Core Permissions**
- `core_read`: Read core system data
- `core_write`: Write core system data
- `core_admin`: Core system administration

#### **Network Permissions**
- `network_read`: Read network data
- `network_write`: Write network data
- `network_admin`: Network administration

#### **File System Permissions**
- `file_read`: Read files
- `file_write`: Write files
- `file_execute`: Execute files
- `file_admin`: File system administration

#### **System Permissions**
- `system_read`: Read system information
- `system_write`: Write system data
- `system_execute`: Execute system commands
- `system_admin`: System administration

#### **API Permissions**
- `api_read`: Read API data
- `api_write`: Write API data
- `api_admin`: API administration

#### **Plugin Permissions**
- `plugin_read`: Read plugin data
- `plugin_write`: Write plugin data
- `plugin_admin`: Plugin administration

#### **User Data Permissions**
- `user_read`: Read user data
- `user_write`: Write user data
- `user_admin`: User data administration

---

## Plugin Lifecycle

### 1. Registration
```python
# Register a new plugin
manifest_data = {
    "plugin_id": "my-plugin",
    "name": "My Plugin",
    "version": "1.0.0",
    "description": "A sample plugin",
    "author": "Developer",
    "requested_permissions": [
        {"permission": "vault_read", "level": "read"}
    ]
}

plugin_id = plugin_manager.register_plugin(manifest_data, user_id)
```

### 2. Approval
```python
# Approve plugin for execution
success = plugin_manager.approve_plugin(plugin_id, user_id, "Testing approved")
```

### 3. Activation
```python
# Plugin becomes active and ready for execution
# This happens automatically after approval
```

### 4. Execution
```python
# Execute plugin
payload = {"action": "analyze", "data": "sample_data"}
result = plugin_manager.execute_plugin(plugin_id, user_id, payload)
```

### 5. Reloading
```python
# Reload plugin (live update)
success = plugin_manager.reload_plugin(plugin_id, user_id, "Bug fix update")
```

### 6. Revocation
```python
# Revoke plugin
success = plugin_manager.revoke_plugin(plugin_id, user_id, "Security concerns")
```

---

## Live Sandbox Reloading

### How It Works

1. **File Watching:** Monitor plugin files for changes
2. **Change Detection:** Detect modifications to plugin code
3. **Validation:** Validate updated plugin manifest
4. **Sandbox Reload:** Reload plugin in isolated environment
5. **State Update:** Update plugin status and metadata
6. **Rollback:** Automatic rollback on failure

### Configuration

```python
# Enable live reloading for a plugin
manifest_data = {
    # ... other manifest fields ...
    "manifest_version": "2.0.0",  # Required for live reloading
    "sandbox": True,
    "sandbox_config": {
        "live_reload": True,
        "watch_paths": ["src/", "config/"],
        "reload_timeout": 30
    }
}
```

### File Watching

```python
# Set up file watcher for plugin
plugin_manager._setup_file_watcher(plugin_id, manifest)

# Watch specific paths
watch_paths = [
    f"plugins/{plugin_id}/src/",
    f"plugins/{plugin_id}/config/",
    f"plugins/{plugin_id}/manifest.json"
]
```

### Reload Events

```python
# Get reload events for a plugin
reload_events = plugin_manager.get_reload_events(plugin_id)

for event in reload_events:
    print(f"Reload: {event.reason} - Success: {event.success}")
    print(f"Previous: {event.previous_version} -> New: {event.new_version}")
```

---

## Audit Logging

### Event Types

#### **Lifecycle Events**
- `registered`: Plugin registration
- `approved`: Plugin approval
- `activated`: Plugin activation
- `suspended`: Plugin suspension
- `updated`: Plugin update
- `reloaded`: Plugin reload
- `revoked`: Plugin revocation
- `uninstalled`: Plugin uninstallation

#### **Permission Events**
- `permission_requested`: Permission request
- `permission_approved`: Permission approval
- `permission_denied`: Permission denial
- `permission_revoked`: Permission revocation

#### **Execution Events**
- `execution_started`: Execution start
- `execution_completed`: Execution completion
- `execution_failed`: Execution failure
- `execution_timeout`: Execution timeout

#### **Security Events**
- `access_denied`: Access denied
- `permission_violation`: Permission violation
- `security_scan`: Security scan result
- `risk_assessment`: Risk assessment

### Audit Log Structure

```json
{
  "event_id": "audit-12345678",
  "timestamp": "2024-01-01T00:00:00Z",
  "user_id": "user123",
  "plugin_id": "my-plugin",
  "event_type": "execution_completed",
  "details": {
    "execution_time": 1.5,
    "success": true,
    "output_size": 1024
  },
  "risk_score": 25,
  "resolution": "completed"
}
```

### Querying Audit Logs

```python
# Get audit events for a plugin
audit_events = plugin_manager.get_plugin_manifest(plugin_id).audit_log

# Filter by event type
security_events = [e for e in audit_events if e.event_type.startswith("security_")]

# Filter by time range
recent_events = [
    e for e in audit_events 
    if datetime.fromisoformat(e.timestamp) > datetime.now() - timedelta(hours=24)
]
```

---

## Performance Benchmarking

### Benchmark Metrics

#### **Response Time**
- **Target:** < 1000ms for typical operations
- **Measurement:** Average response time across multiple executions
- **Tier Classification:**
  - **Excellent:** < 500ms
  - **Good:** 500-1000ms
  - **Acceptable:** 1000-2000ms
  - **Poor:** > 2000ms

#### **Error Rate**
- **Target:** < 1% error rate
- **Measurement:** Percentage of failed executions
- **Tier Classification:**
  - **Excellent:** < 0.1%
  - **Good:** 0.1-1%
  - **Acceptable:** 1-5%
  - **Poor:** > 5%

#### **Resource Usage**
- **CPU Usage:** Percentage of CPU utilization
- **Memory Usage:** Memory consumption in MB
- **Disk Usage:** Disk space usage in MB

#### **Throughput**
- **Operations per Second:** Number of operations completed per second
- **Concurrent Operations:** Number of simultaneous operations supported

### Benchmark Configuration

```python
# Configure benchmarking
benchmark_config = {
    "test_duration": 30,  # seconds
    "response_time_threshold": 1000.0,  # milliseconds
    "error_rate_threshold": 0.01,  # 1%
    "resource_limits": {
        "max_cpu_percent": 50,
        "max_memory_mb": 512,
        "max_disk_mb": 100
    }
}
```

### Running Benchmarks

```python
# Manual benchmark
benchmark_result = plugin_manager._run_plugin_benchmark(plugin_id, payload)

# Automatic benchmark (every 10 executions)
if plugin_manager._should_run_benchmark(plugin_id):
    benchmark_summary = plugin_manager._run_plugin_benchmark(plugin_id, payload)
```

### Performance Tiers

#### **Platinum Tier**
- Response time: < 500ms
- Error rate: < 0.1%
- Resource usage: Optimal
- Throughput: High

#### **Gold Tier**
- Response time: 500-1000ms
- Error rate: 0.1-1%
- Resource usage: Good
- Throughput: Good

#### **Silver Tier**
- Response time: 1000-2000ms
- Error rate: 1-5%
- Resource usage: Acceptable
- Throughput: Acceptable

#### **Bronze Tier**
- Response time: > 2000ms
- Error rate: > 5%
- Resource usage: High
- Throughput: Low

---

## Security Features

### Sandbox Isolation

```python
# Sandbox configuration
sandbox_config = {
    "max_cpu_percent": 50.0,
    "max_memory_mb": 512,
    "max_disk_mb": 100,
    "max_execution_time": 300,
    "network_access": ["api.example.com"],
    "file_access": ["/tmp/plugin_data"],
    "system_commands": ["ls", "cat"]
}
```

### Permission Validation

```python
# Check permissions before execution
def _check_execution_permissions(self, plugin_id: str, payload: Dict[str, Any]) -> bool:
    # Check basic execution permission
    if not self.permission_manager.check_permission(plugin_id, "plugin_execute", "execute"):
        return False
    
    # Check payload-specific permissions
    if "vault_access" in payload:
        if not self.permission_manager.check_permission(plugin_id, "vault_read", "read"):
            return False
    
    return True
```

### Risk Assessment

```python
# Risk scoring algorithm
def _assess_enhanced_permission_risk(self, permissions: List[Dict[str, Any]]) -> int:
    total_risk = 0
    
    for perm in permissions:
        permission = perm['permission']
        level = perm.get('level', 'read')
        
        if permission in self.risk_thresholds:
            level_thresholds = self.risk_thresholds[permission]
            level_key = self._get_risk_level_key(level)
            risk_score = level_thresholds.get(level_key, 50)
            total_risk += risk_score
    
    return min(total_risk, 100)  # Cap at 100
```

---

## API Reference

### Plugin Manager Methods

#### **Registration & Lifecycle**
```python
# Register plugin
plugin_id = plugin_manager.register_plugin(manifest_data, user_id)

# Approve plugin
success = plugin_manager.approve_plugin(plugin_id, user_id, reason)

# Reload plugin
success = plugin_manager.reload_plugin(plugin_id, user_id, reason)

# Revoke plugin
success = plugin_manager.revoke_plugin(plugin_id, user_id, reason)
```

#### **Execution**
```python
# Execute plugin
result = plugin_manager.execute_plugin(plugin_id, user_id, payload, session_id, timeout)

# Check plugin status
status = plugin_manager.get_plugin_status(plugin_id)

# List plugins
plugins = plugin_manager.list_plugins(status_filter="active")
```

#### **Information**
```python
# Get plugin manifest
manifest = plugin_manager.get_plugin_manifest(plugin_id)

# Get reload events
reload_events = plugin_manager.get_reload_events(plugin_id)

# Register lifecycle handler
plugin_manager.register_lifecycle_handler("approved", my_handler)
```

### Permission Manager Methods

#### **Permission Management**
```python
# Request permissions
request_id = permission_manager.request_permissions(plugin_id, user_id, permissions)

# Approve permissions
success = permission_manager.approve_permissions(request_id, user_id, reason)

# Check permission
has_permission = permission_manager.check_permission(plugin_id, permission, level, scope)

# Get plugin permissions
permissions = permission_manager.get_plugin_permissions(plugin_id)
```

#### **Audit & Reporting**
```python
# Get pending requests
pending = permission_manager.get_pending_requests()

# Get plugin grants
grants = permission_manager.get_plugin_grants(plugin_id)

# Export permissions
data = permission_manager.export_permissions()

# Import permissions
success = permission_manager.import_permissions(data)
```

---

## Best Practices

### Plugin Development

1. **Start with Minimal Permissions**
   - Request only the permissions you need
   - Use the lowest permission level possible
   - Scope permissions to specific resources

2. **Implement Proper Error Handling**
   - Handle all potential errors gracefully
   - Provide meaningful error messages
   - Log errors for debugging

3. **Optimize Performance**
   - Minimize execution time
   - Use efficient algorithms
   - Implement caching where appropriate

4. **Follow Security Guidelines**
   - Validate all inputs
   - Sanitize outputs
   - Avoid direct system access

### Manifest Design

1. **Clear Descriptions**
   - Provide detailed descriptions of functionality
   - Explain why permissions are needed
   - Document any limitations or requirements

2. **Version Management**
   - Use semantic versioning
   - Document breaking changes
   - Maintain backward compatibility

3. **Capability Definition**
   - Define clear capabilities
   - Document parameters and return types
   - Specify async/batch support

### Testing & Validation

1. **Comprehensive Testing**
   - Test all functionality
   - Test error conditions
   - Test performance under load

2. **Security Testing**
   - Test permission boundaries
   - Test input validation
   - Test sandbox isolation

3. **Performance Testing**
   - Benchmark critical operations
   - Test resource usage
   - Test concurrent execution

---

## Troubleshooting

### Common Issues

#### **Permission Denied**
```python
# Check plugin permissions
permissions = permission_manager.get_plugin_permissions(plugin_id)
print(f"Plugin permissions: {permissions}")

# Check specific permission
has_permission = permission_manager.check_permission(plugin_id, "vault_read", "read")
print(f"Has vault_read permission: {has_permission}")
```

#### **Plugin Not Found**
```python
# Check if plugin is registered
manifest = plugin_manager.get_plugin_manifest(plugin_id)
if not manifest:
    print(f"Plugin {plugin_id} not found")

# Check plugin status
status = plugin_manager.get_plugin_status(plugin_id)
print(f"Plugin status: {status.status}")
```

#### **Execution Failed**
```python
# Check execution result
result = plugin_manager.execute_plugin(plugin_id, user_id, payload)
if not result.success:
    print(f"Execution failed: {result.error}")
    print(f"Execution time: {result.execution_time}")

# Check sandbox result
if result.sandbox_result:
    print(f"Sandbox success: {result.sandbox_result.success}")
    print(f"Sandbox error: {result.sandbox_result.error}")
```

#### **Reload Failed**
```python
# Check reload events
reload_events = plugin_manager.get_reload_events(plugin_id)
for event in reload_events:
    if not event.success:
        print(f"Reload failed: {event.details.get('error')}")
        print(f"Reason: {event.reason}")
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug plugin manager
plugin_manager.logger.setLevel(logging.DEBUG)

# Debug specific plugin
manifest = plugin_manager.get_plugin_manifest(plugin_id)
print(f"Manifest: {manifest.to_json()}")
```

---

## Future Enhancements

### Planned Features

1. **Plugin Marketplace**
   - Centralized plugin repository
   - Plugin discovery and installation
   - Rating and review system

2. **Advanced Analytics**
   - Usage analytics
   - Performance trends
   - User behavior insights

3. **Plugin Dependencies**
   - Plugin-to-plugin dependencies
   - Automatic dependency resolution
   - Version compatibility checking

4. **Enhanced Security**
   - Code signing verification
   - Vulnerability scanning
   - Threat detection

5. **Distributed Execution**
   - Multi-node plugin execution
   - Load balancing
   - Fault tolerance

---

**Documentation Version:** 2.0.0  
**Last Updated:** 2025-07-07  
**Next Review:** Phase 5 completion 