# Hearthlink IPC Integration

This document describes the Inter-Process Communication (IPC) bridge between the Electron frontend and Python backend in Hearthlink.

## Overview

The IPC integration enables seamless communication between:
- **Electron Main Process**: Handles UI and system interactions
- **Python Backend**: Implements Core, Vault, Synapse, and AI persona logic
- **React Frontend**: Provides the user interface components

## Architecture

```
┌─────────────────┐    IPC Bridge    ┌─────────────────┐
│   Electron      │ ◄──────────────► │   Python        │
│   Main Process  │                  │   Backend       │
│                 │                  │                 │
│   ┌─────────────┤                  │   ┌─────────────┤
│   │ React UI    │                  │   │ Core        │
│   │ Components  │                  │   │ Vault       │
│   │             │                  │   │ Synapse     │
│   └─────────────┘                  │   │ Personas    │
└─────────────────┘                  └─────────────────┘
```

## IPC Communication Protocol

### Message Format

All IPC messages use JSON format:

```json
{
  "id": "unique_message_id",
  "type": "command_type",
  "payload": {
    "key": "value"
  }
}
```

### Response Format

```json
{
  "id": "original_message_id",
  "success": true,
  "data": {
    "result": "data"
  }
}
```

Or for errors:

```json
{
  "id": "original_message_id",
  "success": false,
  "error": "error_message"
}
```

## Available IPC Commands

### Voice Commands

**Command Type**: `voice_command`

**Payload**:
```json
{
  "command": "string"
}
```

**Usage**:
```javascript
const response = await window.electronAPI.sendVoiceCommand("Hello Alden");
```

### Core Session Management

#### Create Session
**Command Type**: `core_create_session`

**Payload**:
```json
{
  "userId": "string",
  "topic": "string",
  "participants": [
    {
      "id": "string",
      "name": "string",
      "type": "persona",
      "role": "string"
    }
  ]
}
```

**Usage**:
```javascript
const response = await window.electronAPI.createSession(
  "user-001",
  "AI Conference",
  [
    { id: "alden", name: "Alden", type: "persona", role: "Executive Function" },
    { id: "alice", name: "Alice", type: "persona", role: "Behavioral Analysis" }
  ]
);
```

#### Get Session
**Command Type**: `core_get_session`

**Payload**:
```json
{
  "sessionId": "string"
}
```

**Usage**:
```javascript
const response = await window.electronAPI.getSession("session-123");
```

#### Add Participant
**Command Type**: `core_add_participant`

**Payload**:
```json
{
  "sessionId": "string",
  "userId": "string",
  "participantData": {
    "id": "string",
    "name": "string",
    "type": "persona",
    "role": "string"
  }
}
```

#### Start Turn-Taking
**Command Type**: `core_start_turn_taking`

**Payload**:
```json
{
  "sessionId": "string",
  "userId": "string",
  "turnOrder": ["participant1", "participant2"]
}
```

#### Advance Turn
**Command Type**: `core_advance_turn`

**Payload**:
```json
{
  "sessionId": "string",
  "userId": "string"
}
```

### Vault Operations

#### Get Persona Memory
**Command Type**: `vault_get_persona_memory`

**Payload**:
```json
{
  "personaId": "string",
  "userId": "string"
}
```

#### Update Persona Memory
**Command Type**: `vault_update_persona_memory`

**Payload**:
```json
{
  "personaId": "string",
  "userId": "string",
  "data": {}
}
```

### Synapse Plugin Operations

#### Execute Plugin
**Command Type**: `synapse_execute_plugin`

**Payload**:
```json
{
  "pluginId": "string",
  "payload": {},
  "userId": "string"
}
```

#### List Plugins
**Command Type**: `synapse_list_plugins`

**Payload**: `{}`

## Frontend Integration

### Using IPC in React Components

```javascript
import React, { useState, useEffect } from 'react';

function MyComponent() {
  const [sessions, setSessions] = useState([]);
  
  const createSession = async () => {
    try {
      const response = await window.electronAPI.createSession(
        "user-001",
        "My Conference",
        [
          { id: "alden", name: "Alden", type: "persona", role: "Executive Function" }
        ]
      );
      
      if (response.success) {
        console.log("Session created:", response.data.sessionId);
        // Update UI state
      } else {
        console.error("Failed to create session:", response.error);
      }
    } catch (error) {
      console.error("IPC error:", error);
    }
  };
  
  return (
    <div>
      <button onClick={createSession}>Create Session</button>
    </div>
  );
}
```

### Error Handling

Always handle IPC errors gracefully:

```javascript
try {
  const response = await window.electronAPI.someCommand(params);
  
  if (response.success) {
    // Handle successful response
    console.log("Success:", response.data);
  } else {
    // Handle backend error
    console.error("Backend error:", response.error);
    // Show user-friendly error message
  }
} catch (error) {
  // Handle IPC communication error
  console.error("Communication error:", error);
  // Fallback behavior
}
```

## Backend Implementation

### Python IPC Handler

The Python backend implements an `IPCHandler` class that:
1. Listens for JSON commands on stdin
2. Processes commands using the appropriate modules
3. Sends JSON responses to stdout

### Module Integration

The IPC handler initializes and manages:
- **Core**: Session orchestration and turn-taking
- **Vault**: Secure memory storage
- **Synapse**: Plugin execution and management

### Error Handling

The backend includes comprehensive error handling:
- Invalid JSON parsing
- Unknown command types
- Module-specific errors
- Exception recovery

## Configuration

### Environment Variables

- `PYTHON_PATH`: Path to Python executable (default: "python")
- `PYTHONPATH`: Set automatically to include src directory

### Startup Process

1. Electron main process starts
2. Python backend process spawns with `--ipc` flag
3. Python backend signals readiness with "HEARTHLINK_READY"
4. IPC communication channel established

## Testing

### Running Integration Tests

```bash
# Run the integration test suite
node test_integration.js
```

### Test Coverage

The integration tests cover:
- Voice command processing
- Core session management
- Synapse plugin operations
- Error handling
- Invalid command handling

### Test Results

Results are saved to `test_results.json` with:
- Timestamp
- Pass/fail summary
- Detailed results for each test

## Security Considerations

### Data Validation

- All input data is validated before processing
- JSON parsing errors are handled gracefully
- Command types are whitelisted

### Process Isolation

- Python backend runs in separate process
- Communication only through stdin/stdout
- No direct file system access from frontend

### Error Information

- Sensitive information is not exposed in error messages
- Errors are logged securely in the backend

## Multi-Agent Conference System

The integration enables a sophisticated multi-agent conference system:

### Features

1. **Session Management**: Create and manage conference sessions
2. **Participant Management**: Add AI personas to sessions
3. **Turn-Taking**: Structured conversation flow
4. **Real-time Updates**: Live session state synchronization

### UI Components

- **ConferenceSystem**: Main conference interface
- **Session Creation**: Form to create new sessions
- **Participant Selection**: Choose AI personas
- **Turn Management**: Control conversation flow
- **Session Display**: View active sessions and participants

### AI Persona Integration

Supported personas:
- **Alden**: Executive Function Partner
- **Alice**: Behavioral Analysis
- **Mimic**: Dynamic Persona
- **Sentry**: Security & Compliance

## Troubleshooting

### Common Issues

1. **Python Backend Not Starting**
   - Check Python installation and PATH
   - Verify PYTHONPATH includes src directory
   - Check for module import errors

2. **IPC Communication Timeout**
   - Ensure Python backend is ready
   - Check for JSON parsing errors
   - Verify command format

3. **Module Initialization Errors**
   - Check dependencies are installed
   - Verify module configurations
   - Review error logs

### Debug Mode

Enable debug logging by setting `NODE_ENV=development`:

```bash
NODE_ENV=development npm start
```

### Log Files

- **Electron logs**: Console output
- **Python logs**: `logs/hearthlink.log`
- **Test results**: `test_results.json`

## Future Enhancements

### Planned Features

1. **Real-time Messaging**: WebSocket integration
2. **Plugin Hot-loading**: Dynamic plugin management
3. **Advanced Security**: Authentication and authorization
4. **Performance Monitoring**: IPC performance metrics
5. **Distributed Sessions**: Multi-node conference support

### API Extensions

1. **Streaming Responses**: For long-running operations
2. **Event Subscriptions**: Real-time notifications
3. **Batch Operations**: Multiple commands in single request
4. **Command Queuing**: Reliable message delivery

## Contributing

When adding new IPC commands:

1. Add command type to Python handler
2. Implement handler method
3. Add frontend API wrapper
4. Update documentation
5. Add integration tests
6. Test error scenarios

## License

This integration is part of the Hearthlink project and follows the same MIT license terms.