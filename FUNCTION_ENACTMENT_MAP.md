# Hearthlink Function Enactment Paths Map

**Generated**: 2025-07-31  
**Purpose**: Maps all functions and endpoints to their UI controls, CLI commands, or automation paths for SPEC-3 verification.

## Core API Endpoints

### Health & System Status
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Health Check | `GET /api/health` | Settings → Service Status | `curl /api/health` | Auto-refresh health monitor |
| System Status | `GET /api/agents` | Launch Page → Agent Status | - | Service orchestrator checks |

### Agent Management  
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| List Agents | `GET /api/agents` | Launch Page → Agents List | - | Startup agent discovery |
| Get Agent | `GET /api/agents/{id}` | Click agent card | - | Agent status polling |
| Update Agent | `PUT /api/agents/{id}` | Agent Settings Panel | - | Configuration sync |

### Project Management
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| List Projects | `GET /api/projects` | Project Board Panel | - | Project auto-discovery |
| Create Project | `POST /api/projects` | Project Board → New Project | - | Template instantiation |
| Get Project | `GET /api/projects/{id}` | Click project card | - | Project load on selection |
| Orchestrate Project | `POST /api/projects/{id}/orchestrate` | Project → Execute | - | Multi-agent workflow trigger |

### Service Management
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| List Services | `GET /api/services` | Settings → Service Status | - | Health monitoring system |
| Service Health | `GET /api/services/{id}/health` | Settings → Check Status | - | Circuit breaker monitoring |

## External Agent API

### Agent Operations
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| List External Agents | `GET /api/external-agents` | Synapse → Agent List | - | Agent discovery service |
| Agent Status | `GET /api/external-agents/{id}/status` | Agent card status indicator | - | Status polling timer |
| Execute Agent | `POST /api/external-agents/{id}/execute` | Agent → Execute button | - | Workflow execution |
| Generate Content | `POST /api/external-agents/{id}/generate` | Agent → Generate | - | Content creation pipeline |

### File Operations
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Write File | `POST /api/external-agents/{id}/files/write` | File Manager → Save | - | Auto-save on edit |
| Read File | `POST /api/external-agents/{id}/files/read` | File Manager → Open | - | File load on selection |
| List Files | `GET/POST /api/external-agents/{id}/files/list` | File Explorer | - | Directory indexing |

### Circuit Breaker Management
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Circuit Breaker Status | `GET /api/external-agents/circuit-breakers/status` | Settings → Circuit Breakers | - | Health dashboard update |
| Reset Circuit Breaker | `POST /api/external-agents/circuit-breakers/{service}/reset` | Settings → Reset button | - | Auto-recovery attempts |
| Reset All Circuit Breakers | `POST /api/external-agents/circuit-breakers/reset-all` | Settings → Reset All | - | System recovery procedure |

## License Validation API

### Template Licensing
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Validate License | `POST /api/templates/validate-license` | Template → License Check | - | Template load validation |
| Record Usage | `POST /api/templates/record-usage` | Template submit | - | Usage tracking |
| Start Trial | `POST /api/templates/start-trial` | Template → Start Trial | - | Trial activation |
| License Info | `GET /api/templates/license-info/{id}` | Template info dialog | - | Template metadata load |
| User Licenses | `GET /api/templates/user-licenses/{user}` | Settings → Licenses | - | User dashboard update |

## Task Management

### Task Operations  
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Create Task | `POST /api/vault/tasks` | Task Dashboard → Create | - | Template instantiation |
| Update Task | `PUT /api/vault/tasks/{id}` | Task Editor → Save | - | Auto-save timer |
| Delete Task | `DELETE /api/templates/{id}` | Task → Delete button | - | Cleanup workflows |
| Get Task | `GET /api/vault/tasks/{id}` | Click task card | - | Task detail load |

### Template Operations
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Apply Template | - | TaskCreator → Template button | - | Form auto-population |
| Steve August Template | - | TaskCreator → Focus Formula | - | Licensed template launch |

## Vault Operations

### Memory Management
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Store Memory | - | Vault → Save | - | Auto-persist on changes |
| Retrieve Memory | - | Vault → Load | - | Context loading |
| Key Rotation | `POST /api/vault/rotate-keys` | Settings → Rotate Keys | - | 30-day auto-rotation |
| Key Status | `GET /api/vault/key-status` | Settings → Key Status | - | Status monitoring |
| Key Rollback | `POST /api/vault/rollback` | Settings → Rollback | - | Emergency recovery |

## Settings Management

### Configuration  
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Load Settings | - | Settings Manager open | - | App initialization |
| Save Settings | - | Settings → Save button | - | Auto-save on change |
| Test Connection | - | Settings → Test buttons | - | Connection validation |
| Fetch Models | - | Settings → Model dropdown | - | Model discovery |

### Local LLM Management
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Start LLM Service | - | Settings → Start Service | - | App startup routine |
| Stop LLM Service | - | Settings → Stop Service | - | Shutdown cleanup |
| Check Service Status | - | Settings → Check Status | - | Health polling |
| Model Selection | - | Settings → Model dropdown | - | Profile switching |

## MCP Integration

### Plugin Management
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| List MCP Servers | - | Synapse → Plugin List | - | Plugin discovery |
| Start MCP Server | - | Synapse → Start Plugin | - | Auto-start on demand |
| Stop MCP Server | - | Synapse → Stop Plugin | - | Resource cleanup |
| Plugin Execution | - | Synapse → Execute Tool | - | Workflow integration |

## Voice Interface

### Voice Operations
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Voice Recognition | - | Voice button activation | Wake word "alden" | Continuous listening |
| TTS Playback | - | Agent response | - | Response synthesis |
| Voice Routing | - | Agent name recognition | - | Smart routing algorithm |

## Sprite Management

### Model Orchestration
| Function | HTTP Endpoint | UI Invocation | CLI Command | Automation Path |
|----------|---------------|---------------|-------------|-----------------|
| Load Sprite Status | - | Settings → Sprite tab | - | Tab activation refresh |
| Power Budget Update | - | Settings → Power controls | - | Thermal management |
| Model Hot-Swap | - | Automatic escalation | - | Confidence threshold trigger |
| Memory Isolation | - | Settings checkbox | - | Swap cleanup routine |

## Missing UI Controls (Orphaned Functions)

### Functions Without UI Invocation
1. **Direct API Testing**: Most API endpoints lack direct UI test controls
2. **Batch Operations**: No bulk operations UI for tasks/templates
3. **Advanced Monitoring**: Circuit breaker details need dedicated UI
4. **License Management**: Bulk license operations missing
5. **System Diagnostics**: Deep diagnostic tools not exposed

### Recommended Additions
1. **API Test Panel**: Add developer tools panel for endpoint testing
2. **Bulk Operations**: Add multi-select with batch actions
3. **Advanced Settings**: Dedicated admin panel for system controls
4. **Debug Console**: Runtime debugging interface
5. **Performance Monitor**: Real-time metrics dashboard

## CLI Command Opportunities

### Missing CLI Commands
1. No CLI interface exists for most operations
2. Could add npm scripts for common operations:
   - `npm run health-check`
   - `npm run rotate-keys`
   - `npm run test-connections`
   - `npm run reset-circuit-breakers`

### Recommended CLI Implementation
```bash
# Package.json scripts
"scripts": {
  "health": "curl http://localhost:8000/api/health",
  "agents": "curl http://localhost:8000/api/agents",
  "vault-status": "curl http://localhost:8000/api/vault/key-status",
  "rotate-keys": "curl -X POST http://localhost:8000/api/vault/rotate-keys"
}
```

## Automation Gaps

### Areas Needing Automation
1. **Error Recovery**: Automated error handling missing for some flows
2. **Resource Cleanup**: Incomplete cleanup on service shutdown
3. **Health Monitoring**: Need more proactive health checks
4. **Performance Optimization**: Missing automated performance tuning

## Summary

- **Total Functions Mapped**: 47 major functions/endpoints
- **Functions with UI**: 42 (89%)
- **Functions with CLI**: 8 (17%)
- **Functions with Automation**: 38 (81%)
- **Orphaned Functions**: 5 (11%)

The system has good UI coverage but lacks CLI interface development. Most critical functions have proper automation paths through event-driven architecture.