# Core Module - Communication Switch & Context Moderator

## Overview

The Core module is the central orchestration component of Hearthlink, responsible for managing multi-agent conversational interactions, roundtables, agent performance challenges, and context switching. It ensures that all agent participation is user-controlled and provides comprehensive session management with turn-taking, breakout rooms, and communal memory mediation.

## Key Features

### 🎯 Session Management
- **Session Creation**: Create new collaborative sessions with defined topics
- **Participant Management**: Add/remove personas and external agents
- **State Transitions**: Pause, resume, and end sessions with full audit trails
- **Session Registry**: Track all live and archived sessions

### 🔄 Turn-Taking Coordination
- **Structured Turn-Taking**: Coordinate speaking order among participants
- **Manual Control**: User can manually set or advance turns
- **Automatic Progression**: Configurable auto-advance with timeout handling
- **Turn State Tracking**: Monitor current turn and completion status

### 🏠 Breakout Rooms
- **Topic-Specific Sessions**: Create focused discussion groups
- **Participant Subsets**: Select specific participants for breakouts
- **Parent Session Integration**: All breakout activity tied to main session
- **Lifecycle Management**: Create, manage, and end breakout rooms

### 🧠 Communal Memory Mediation
- **Insight Sharing**: Participants can share insights to communal memory
- **Context Preservation**: Maintain context and metadata with insights
- **Vault Integration**: Secure storage and retrieval of shared knowledge
- **Audit Trail**: Complete logging of all communal memory operations

### 📊 Live Feed & Logging
- **Real-Time Events**: Stream session events to live feed
- **Configurable Verbosity**: Adjust detail level of live feed
- **Hidden Responses**: Support for suppressed responses in logs
- **Export Capabilities**: Export session logs in multiple formats

## Architecture

### Core Components

```python
class Core:
    """Main orchestration class for multi-agent sessions."""
    
    def __init__(self, config: Dict[str, Any], vault: Vault, logger=None):
        # Initialize session registry, turn managers, and event callbacks
```

### Data Models

#### Session
```python
@dataclass
class Session:
    session_id: str
    created_by: str
    created_at: str
    topic: str
    participants: List[Participant]
    session_log: List[SessionEvent]
    breakouts: List[BreakoutRoom]
    live_feed_settings: LiveFeedSettings
    status: SessionStatus
    current_turn: Optional[str]
    turn_order: List[str]
    communal_memory_id: Optional[str]
    audit_log: List[Dict[str, Any]]
```

#### Participant
```python
@dataclass
class Participant:
    id: str
    type: ParticipantType  # persona, external, user
    name: str
    role: Optional[str]
    joined_at: str
    left_at: Optional[str]
    turn_order: Optional[int]
    is_active: bool
```

#### SessionEvent
```python
@dataclass
class SessionEvent:
    event_id: str
    timestamp: str
    event_type: str  # join, leave, response, breakout_create, etc.
    participant_id: Optional[str]
    content: Optional[str]
    metadata: Dict[str, Any]
```

## Usage Examples

### Basic Session Management

```python
from src.core.core import Core
from src.vault.vault import Vault

# Initialize Core with Vault
vault = Vault(vault_config)
core = Core(core_config, vault)

# Create session
session_id = core.create_session("user-123", "AI Ethics Discussion")

# Add participants
alden_data = {
    "id": "alden",
    "type": "persona",
    "name": "Alden",
    "role": "evolutionary_companion"
}
core.add_participant(session_id, "user-123", alden_data)

# Start turn-taking
core.start_turn_taking(session_id, "user-123")

# Advance turns
next_turn = core.advance_turn(session_id, "user-123")
```

### Breakout Room Management

```python
# Create breakout room
breakout_id = core.create_breakout(
    session_id, 
    "user-123", 
    "AI Ethics Deep Dive", 
    ["alice", "research-bot"]
)

# End breakout room
core.end_breakout(session_id, "user-123", breakout_id)
```

### Communal Memory Sharing

```python
# Share insight to communal memory
core.share_insight(
    session_id,
    "alden",
    "The user shows strong analytical thinking patterns",
    {"context": "observation", "confidence": 0.85}
)
```

### Session Export

```python
# Export session log
export_data = core.export_session_log(session_id, "user-123", include_hidden=False)
session_data = json.loads(export_data)
```

## API Endpoints

The Core module provides a comprehensive REST API through FastAPI:

### Session Management
- `POST /api/core/session` - Create new session
- `GET /api/core/session/{session_id}` - Get session information
- `GET /api/core/sessions` - Get all active sessions
- `DELETE /api/core/session/{session_id}` - End session

### Participant Management
- `POST /api/core/session/{session_id}/participants` - Add participant
- `DELETE /api/core/session/{session_id}/participants/{participant_id}` - Remove participant
- `GET /api/core/session/{session_id}/participants` - Get session participants

### Turn-Taking
- `POST /api/core/session/{session_id}/turn-taking/start` - Start turn-taking
- `POST /api/core/session/{session_id}/turn-taking/advance` - Advance turn

### Breakout Rooms
- `POST /api/core/session/{session_id}/breakout` - Create breakout room
- `DELETE /api/core/session/{session_id}/breakout/{breakout_id}` - End breakout room

### Communal Memory
- `POST /api/core/session/{session_id}/insights` - Share insight

### Session Control
- `POST /api/core/session/{session_id}/pause` - Pause session
- `POST /api/core/session/{session_id}/resume` - Resume session
- `GET /api/core/session/{session_id}/log` - Export session log

## Configuration

### Core Configuration

```json
{
  "session": {
    "max_participants": 10,
    "max_breakouts_per_session": 5,
    "session_timeout_minutes": 480,
    "auto_archive_after_days": 30
  },
  "turn_taking": {
    "turn_timeout_seconds": 300,
    "auto_advance": true,
    "allow_manual_turn_set": true,
    "max_turn_duration_minutes": 10
  },
  "communal_memory": {
    "auto_share_insights": false,
    "insight_approval_required": true,
    "max_insights_per_session": 100,
    "insight_retention_days": 90
  },
  "live_feed": {
    "default_verbosity": "default",
    "auto_include_external": true,
    "show_metadata": false,
    "max_events_in_feed": 1000
  }
}
```

## Integration

### With Vault Module
- **Communal Memory**: Core uses Vault for secure storage of shared insights
- **Audit Logging**: All Core operations are logged through Vault's audit system
- **Data Persistence**: Session data and communal memory persist across restarts

### With Sentry Module
- **Security Monitoring**: Sentry monitors all Core operations for security events
- **Policy Enforcement**: Core respects Sentry's security policies
- **Incident Response**: Security incidents trigger appropriate Core responses

### With Persona Modules
- **Alden Integration**: Evolutionary companion participates in sessions
- **Alice Integration**: Cognitive-behavioral analysis during sessions
- **Mimic Integration**: Dynamic persona creation and management

### With Synapse Module
- **External Agents**: Core manages external agents introduced through Synapse
- **Plugin Integration**: Plugins can participate in Core sessions
- **API Gateway**: Synapse provides external API access to Core functionality

## Security & Privacy

### Access Control
- **User Authorization**: All operations require valid user authentication
- **Participant Isolation**: Participants can only access their assigned sessions
- **Audit Trail**: Complete logging of all session activities

### Data Protection
- **Encrypted Storage**: All session data encrypted through Vault
- **Secure Communication**: API endpoints use secure protocols
- **Privacy Controls**: User controls all data sharing and export

### Compliance
- **GDPR Compliance**: User data export and deletion capabilities
- **Audit Requirements**: Comprehensive audit trails for compliance
- **Data Retention**: Configurable data retention policies

## Testing

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Module interaction testing
- **API Tests**: REST endpoint testing
- **Performance Tests**: Load and stress testing

### Running Tests
```bash
# Run Core module tests
python test_core.py

# Run with specific test
python -m pytest test_core.py::test_session_creation
```

## Performance Considerations

### Scalability
- **Session Limits**: Configurable maximum concurrent sessions
- **Participant Limits**: Maximum participants per session
- **Memory Management**: Efficient session data caching
- **Cleanup Processes**: Automatic session cleanup and archiving

### Optimization
- **Caching**: In-memory caching for frequently accessed data
- **Batch Operations**: Efficient bulk operations for multiple participants
- **Lazy Loading**: Load session data on demand
- **Connection Pooling**: Efficient database connection management

## Error Handling

### Exception Types
- `CoreError`: Base exception for Core module errors
- `SessionNotFoundError`: Session does not exist
- `ParticipantNotFoundError`: Participant not found in session
- `InvalidOperationError`: Operation not allowed in current state

### Error Recovery
- **Graceful Degradation**: Continue operation when possible
- **State Recovery**: Automatic recovery from partial failures
- **User Notification**: Clear error messages for users
- **Logging**: Comprehensive error logging for debugging

## Future Enhancements

### Planned Features
- **Real-Time Collaboration**: WebSocket support for live updates
- **Advanced Analytics**: Session performance and engagement metrics
- **Machine Learning**: AI-powered session optimization
- **Multi-User Support**: Collaborative sessions across multiple users

### Integration Roadmap
- **External APIs**: Integration with third-party collaboration tools
- **Mobile Support**: Mobile-optimized session management
- **Voice Integration**: Voice-based session participation
- **Video Support**: Video conferencing integration

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python test_core.py`
4. Run example: `python examples/core_example.py`

### Code Standards
- **Type Hints**: All functions include type annotations
- **Documentation**: Comprehensive docstrings for all methods
- **Error Handling**: Proper exception handling and logging
- **Testing**: Unit tests for all functionality

### Pull Request Process
1. Create feature branch
2. Implement changes with tests
3. Update documentation
4. Submit pull request with description
5. Code review and approval process

## License

This module is part of the Hearthlink project and follows the same licensing terms as the main project. 