# MCP Agent Resource Policy

## Purpose

This document defines the scoped resource permissions for all agents in the Hearthlink system using the Model Context Protocol (MCP). It establishes explicit boundaries for agent access to system resources including disk, network, workspace, and other sensitive areas.

## 1. Policy Overview

### 1.1 Zero Trust Principle
- All agents operate under the principle of least privilege
- No agent has default access to any resource
- All access must be explicitly granted and logged
- Resource access is scoped, time-limited, and auditable

### 1.2 MCP Integration
- All resource access requests flow through MCP
- Sentry validates and logs all resource access
- Access decisions are policy-driven and user-reviewable
- Violations trigger immediate security alerts

## 2. Agent Resource Permissions

### 2.1 Sentry - System Guardian

**Role:** Security monitoring, audit logging, policy enforcement

**Resource Permissions:**
- **Disk Access:**
  - READ: System logs, audit trails, configuration files
  - WRITE: Security logs, incident reports, policy updates
  - DENY: User data, application code, temporary files
- **Network Access:**
  - READ: System network status, connection logs
  - WRITE: Security alerts, incident notifications
  - DENY: External API calls, data exfiltration
- **Workspace Access:**
  - READ: System configuration, policy definitions
  - WRITE: Security policies, access control rules
  - DENY: User workspaces, application data
- **Memory Access:**
  - READ: Security events, audit logs
  - WRITE: Security metrics, threat indicators
  - DENY: User memory, persona data

**MCP Context:**
```json
{
  "mcp_version": "1.0.0",
  "agent_id": "sentry",
  "resource_scope": "security_monitoring",
  "permissions": {
    "disk": ["read:logs", "write:security_logs"],
    "network": ["read:status", "write:alerts"],
    "workspace": ["read:config", "write:policies"],
    "memory": ["read:events", "write:metrics"]
  },
  "audit_required": true,
  "timeout_seconds": 300
}
```

### 2.2 Alden - Evolutionary Companion

**Role:** User interaction, goal management, habit tracking

**Resource Permissions:**
- **Disk Access:**
  - READ: User workspace, goal files, habit logs
  - WRITE: Progress updates, reflection notes
  - DENY: System files, other user data, configuration
- **Network Access:**
  - READ: User preferences, learning resources
  - WRITE: Progress reports, goal updates
  - DENY: External APIs, data sharing
- **Workspace Access:**
  - READ: User workspace, personal files
  - WRITE: Goal tracking, habit logs
  - DENY: System workspace, other users
- **Memory Access:**
  - READ: Personal memory slice, habit history
  - WRITE: Progress updates, learning insights
  - DENY: Other persona memory, system memory

**MCP Context:**
```json
{
  "mcp_version": "1.0.0",
  "agent_id": "alden",
  "resource_scope": "user_companion",
  "permissions": {
    "disk": ["read:user_workspace", "write:progress"],
    "network": ["read:preferences", "write:reports"],
    "workspace": ["read:user_files", "write:goals"],
    "memory": ["read:personal", "write:insights"]
  },
  "user_consent_required": true,
  "timeout_seconds": 600
}
```

### 2.3 Alice - Behavioral Analysis

**Role:** Behavioral analysis, feedback generation, coaching

**Resource Permissions:**
- **Disk Access:**
  - READ: User interaction logs, behavioral data
  - WRITE: Analysis reports, feedback notes
  - DENY: System files, raw user data
- **Network Access:**
  - READ: Behavioral research, coaching resources
  - WRITE: Analysis results, recommendations
  - DENY: External APIs, data sharing
- **Workspace Access:**
  - READ: Analysis workspace, behavioral logs
  - WRITE: Reports, feedback documents
  - DENY: User personal workspace, system files
- **Memory Access:**
  - READ: Behavioral patterns, interaction history
  - WRITE: Analysis insights, coaching feedback
  - DENY: Personal user data, other persona memory

**MCP Context:**
```json
{
  "mcp_version": "1.0.0",
  "agent_id": "alice",
  "resource_scope": "behavioral_analysis",
  "permissions": {
    "disk": ["read:interaction_logs", "write:analysis_reports"],
    "network": ["read:research", "write:recommendations"],
    "workspace": ["read:analysis_workspace", "write:reports"],
    "memory": ["read:behavioral_patterns", "write:insights"]
  },
  "data_anonymization_required": true,
  "timeout_seconds": 900
}
```

### 2.4 Mimic - Dynamic Persona

**Role:** Persona generation, performance analytics, knowledge management

**Resource Permissions:**
- **Disk Access:**
  - READ: Persona templates, knowledge bases
  - WRITE: Generated personas, performance data
  - DENY: User personal data, system files
- **Network Access:**
  - READ: Knowledge resources, research materials
  - WRITE: Performance reports, analytics
  - DENY: External APIs, data sharing
- **Workspace Access:**
  - READ: Persona workspace, knowledge index
  - WRITE: Generated content, analytics
  - DENY: User personal workspace, system files
- **Memory Access:**
  - READ: Persona memory, knowledge base
  - WRITE: Generated insights, performance data
  - DENY: User personal memory, other persona data

**MCP Context:**
```json
{
  "mcp_version": "1.0.0",
  "agent_id": "mimic",
  "resource_scope": "persona_generation",
  "permissions": {
    "disk": ["read:templates", "write:generated_content"],
    "network": ["read:knowledge_resources", "write:analytics"],
    "workspace": ["read:persona_workspace", "write:content"],
    "memory": ["read:persona_memory", "write:insights"]
  },
  "content_validation_required": true,
  "timeout_seconds": 1200
}
```

### 2.5 Core - Session Orchestration

**Role:** Multi-agent session management, turn-taking, communal memory

**Resource Permissions:**
- **Disk Access:**
  - READ: Session configurations, agent manifests
  - WRITE: Session logs, communal memory
  - DENY: User personal data, system files
- **Network Access:**
  - READ: Agent status, session state
  - WRITE: Session events, coordination data
  - DENY: External APIs, data sharing
- **Workspace Access:**
  - READ: Session workspace, agent configurations
  - WRITE: Session data, coordination logs
  - DENY: User personal workspace, system files
- **Memory Access:**
  - READ: Communal memory, session context
  - WRITE: Session insights, coordination data
  - DENY: Personal persona memory, user data

**MCP Context:**
```json
{
  "mcp_version": "1.0.0",
  "agent_id": "core",
  "resource_scope": "session_orchestration",
  "permissions": {
    "disk": ["read:session_config", "write:session_logs"],
    "network": ["read:agent_status", "write:session_events"],
    "workspace": ["read:session_workspace", "write:coordination"],
    "memory": ["read:communal_memory", "write:session_insights"]
  },
  "session_boundary_required": true,
  "timeout_seconds": 1800
}
```

### 2.6 Vault - Memory Management

**Role:** Secure storage, memory encryption, data persistence

**Resource Permissions:**
- **Disk Access:**
  - READ: Encrypted memory files, backup data
  - WRITE: Memory slices, audit logs
  - DENY: System files, user personal data
- **Network Access:**
  - READ: Backup services, sync status
  - WRITE: Backup data, sync logs
  - DENY: External APIs, data sharing
- **Workspace Access:**
  - READ: Vault workspace, memory index
  - WRITE: Memory data, audit trails
  - DENY: User workspace, system files
- **Memory Access:**
  - READ: All memory slices (encrypted)
  - WRITE: Memory updates, audit logs
  - DENY: Decrypted data access

**MCP Context:**
```json
{
  "mcp_version": "1.0.0",
  "agent_id": "vault",
  "resource_scope": "memory_management",
  "permissions": {
    "disk": ["read:encrypted_memory", "write:memory_slices"],
    "network": ["read:backup_services", "write:backup_data"],
    "workspace": ["read:vault_workspace", "write:memory_data"],
    "memory": ["read:all_slices", "write:memory_updates"]
  },
  "encryption_required": true,
  "audit_required": true,
  "timeout_seconds": 3600
}
```

### 2.7 Synapse - External Gateway

**Role:** Plugin management, external connections, API mediation

**Resource Permissions:**
- **Disk Access:**
  - READ: Plugin manifests, configuration files
  - WRITE: Plugin logs, execution data
  - DENY: User data, system files
- **Network Access:**
  - READ: External APIs, plugin endpoints
  - WRITE: API calls, plugin responses
  - DENY: Unauthorized endpoints, data exfiltration
- **Workspace Access:**
  - READ: Plugin workspace, sandbox environment
  - WRITE: Plugin execution, sandbox data
  - DENY: User workspace, system files
- **Memory Access:**
  - READ: Plugin context, execution state
  - WRITE: Plugin results, execution logs
  - DENY: User memory, persona data

**MCP Context:**
```json
{
  "mcp_version": "1.0.0",
  "agent_id": "synapse",
  "resource_scope": "external_gateway",
  "permissions": {
    "disk": ["read:plugin_manifests", "write:plugin_logs"],
    "network": ["read:external_apis", "write:api_calls"],
    "workspace": ["read:plugin_workspace", "write:execution_data"],
    "memory": ["read:plugin_context", "write:plugin_results"]
  },
  "sandbox_required": true,
  "risk_assessment_required": true,
  "timeout_seconds": 300
}
```

## 3. Resource Access Patterns

### 3.1 Request Flow
1. **Agent Request:** Agent sends MCP request with resource access intent
2. **Sentry Validation:** Sentry validates request against agent permissions
3. **Policy Check:** RBAC/ABAC policies evaluate access decision
4. **Resource Access:** If approved, resource access is granted with scope
5. **Audit Logging:** All access is logged with full context
6. **Timeout:** Access automatically expires after timeout period

### 3.2 Violation Handling
1. **Immediate Block:** Unauthorized access is immediately blocked
2. **Alert Generation:** Security alert is generated and logged
3. **Incident Creation:** Security incident is created for investigation
4. **User Notification:** User is notified of security violation
5. **Agent Suspension:** Agent may be suspended pending investigation

### 3.3 Audit Requirements
- All resource access requests must be logged
- Access decisions must include policy references
- Violations must trigger security alerts
- Audit logs must be tamper-evident
- Logs must be retained for compliance

## 4. Implementation Guidelines

### 4.1 MCP Integration
- All resource access must use MCP protocol
- Requests must include agent identity and scope
- Responses must include access decision and audit trail
- Timeouts must be enforced automatically

### 4.2 Security Controls
- Encryption required for sensitive data access
- Sandboxing required for external connections
- User consent required for personal data access
- Risk assessment required for new connections

### 4.3 Monitoring Requirements
- Real-time monitoring of all resource access
- Anomaly detection for unusual access patterns
- Automated alerting for policy violations
- Regular security metrics reporting

## 5. Compliance and Governance

### 5.1 Policy Enforcement
- All agents must comply with resource policies
- Policy violations result in immediate action
- Regular policy reviews and updates required
- User override capabilities for emergency access

### 5.2 Audit and Reporting
- Comprehensive audit trails for all access
- Regular security reports and metrics
- Compliance reporting for regulatory requirements
- Incident response procedures and documentation

### 5.3 Continuous Improvement
- Regular policy effectiveness reviews
- Threat modeling and risk assessment updates
- Security control enhancements based on incidents
- User feedback integration for policy refinement

## 6. References

- [MCP Full Specification](../docs/appendix_e_model_context_protocol_mcp_full_specification.md)
- [Enterprise Security Features](../docs/ENTERPRISE_FEATURES.md)
- [RBAC/ABAC Security Implementation](../src/enterprise/rbac_abac_security.py)
- [SIEM Monitoring Implementation](../src/enterprise/siem_monitoring.py)
- [Process Refinement SOP](../docs/process_refinement.md)

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-27  
**Next Review:** 2025-04-27  
**Owner:** Hearthlink Security Team 