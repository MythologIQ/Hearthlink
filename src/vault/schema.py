from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

@dataclass
class AuditLogEntry:
    timestamp: str
    action: str
    user_id: str
    persona_id: Optional[str] = None
    memory_type: str = "persona"  # or "communal"
    key: Optional[str] = None
    details: Optional[Dict[str, Any]] = field(default_factory=dict)
    result: str = "success"

@dataclass
class PersonaMemory:
    persona_id: str
    user_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    schema_version: str = "1.0.0"
    audit_log: List[AuditLogEntry] = field(default_factory=list)

@dataclass
class CommunalMemory:
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    schema_version: str = "1.0.0"
    audit_log: List[AuditLogEntry] = field(default_factory=list) 