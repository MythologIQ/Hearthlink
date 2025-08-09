"""
SPEC-2 Task Templates API - Vault-backed CRUD with Audit Logging

Provides endpoints for:
- Task template management with proprietary and fallback templates
- Full CRUD operations with Alden memory integration
- Vault-backed persistence with encryption
- Comprehensive audit logging
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid
import logging
from pathlib import Path

from src.vault.vault import VaultManager
from src.database.database_manager import DatabaseManager
from src.personas.alden import AldenPersona
from src.llm.local_llm_client import LocalLLMClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# API Router
router = APIRouter(prefix="/api/task-templates", tags=["task-templates"])

# Initialize services
vault_manager = VaultManager()
db_manager = DatabaseManager()
alden = AldenPersona()
llm_client = LocalLLMClient()

# Pydantic Models
class HabitTracker(BaseModel):
    frequency: str = Field(..., description="daily, weekly, monthly")
    target: int = Field(..., description="Target occurrences")
    streak: int = Field(default=0, description="Current streak")
    lastCompleted: Optional[datetime] = Field(default=None)

class Decision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Decision title")
    options: List[str] = Field(default_factory=list)
    selected: Optional[str] = Field(default=None)
    reasoning: str = Field(default="", description="Decision reasoning")
    timestamp: datetime = Field(default_factory=datetime.now)

class TaskTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    category: str = Field(..., description="Task category")
    
    # SPEC-2 Enhanced Fields
    mission: str = Field(default="", description="Mission statement")
    values: List[str] = Field(default_factory=list, description="Core values")
    habitTracker: HabitTracker = Field(default_factory=HabitTracker)
    
    # Template configuration
    priority: str = Field(default="medium", description="Default priority")
    estimatedTime: float = Field(default=1.0, description="Default estimated hours")
    assignedAgent: str = Field(default="alden", description="Default agent")
    tags: List[str] = Field(default_factory=list, description="Default tags")
    
    # Metadata
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)
    createdBy: str = Field(default="system")
    isSystem: bool = Field(default=False, description="System vs user template")
    isActive: bool = Field(default=True)

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    priority: str = Field(..., description="Task priority")
    estimatedTime: float = Field(..., description="Estimated hours")
    dueDate: Optional[datetime] = Field(default=None)
    tags: List[str] = Field(default_factory=list)
    assignedAgent: str = Field(..., description="Assigned agent")
    category: str = Field(..., description="Task category")
    
    # SPEC-2 Enhanced Fields
    mission: str = Field(default="", description="Mission statement")
    values: List[str] = Field(default_factory=list, description="Core values")
    habitTracker: HabitTracker = Field(default_factory=HabitTracker)
    decisions: List[Decision] = Field(default_factory=list)
    template: Optional[str] = Field(default=None, description="Source template ID")
    projectContext: Optional[str] = Field(default=None)
    memoryTags: List[str] = Field(default_factory=list)
    vaultPath: Optional[str] = Field(default=None)
    
    # Status fields
    status: str = Field(default="todo")
    progress: int = Field(default=0, description="Progress percentage")
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

class AuditEntry(BaseModel):
    operation: str = Field(..., description="CRUD operation")
    entityType: str = Field(..., description="Entity type")
    entityId: str = Field(..., description="Entity ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    agent: str = Field(..., description="Acting agent")
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token or token == "test-token":
        return {"user_id": "test-user", "agent": "alden"}
    
    # In production, validate JWT token
    try:
        # Mock validation for development
        return {"user_id": "authenticated-user", "agent": "alden"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# System Templates
SYSTEM_TEMPLATES = [
    TaskTemplate(
        id="alden-productivity",
        name="Alden Productivity Task",
        description="Vault-backed task with memory integration and habit tracking",
        category="productivity",
        mission="Enhance productivity through AI-assisted task management with persistent memory",
        values=["efficiency", "innovation", "learning"],
        habitTracker=HabitTracker(frequency="daily", target=1),
        priority="medium",
        estimatedTime=2.0,
        assignedAgent="alden",
        tags=["memory-integration", "vault-backed", "persistent", "alden-memory"],
        isSystem=True,
        createdBy="system"
    ),
    TaskTemplate(
        id="development-sprint",
        name="Development Sprint Task",
        description="Code development with performance tracking and decision support",
        category="development",
        mission="Deliver high-quality code solutions with comprehensive tracking",
        values=["quality", "innovation", "reliability"],
        habitTracker=HabitTracker(frequency="daily", target=2),
        priority="high",
        estimatedTime=4.0,
        assignedAgent="mimic",
        tags=["development", "sprint", "tracking", "quality"],
        isSystem=True,
        createdBy="system"
    ),
    TaskTemplate(
        id="memory-research",
        name="Memory Research Task",
        description="Research task with comprehensive Vault integration and knowledge tracking",
        category="research",
        mission="Advance memory integration capabilities through systematic research",
        values=["learning", "innovation", "sustainability"],
        habitTracker=HabitTracker(frequency="weekly", target=1),
        priority="medium",
        estimatedTime=6.0,
        assignedAgent="alice",
        tags=["research", "memory-research", "vault-integration", "knowledge"],
        isSystem=True,
        createdBy="system"
    ),
    TaskTemplate(
        id="security-audit",
        name="Security Audit Task",
        description="Comprehensive security analysis with Sentry integration",
        category="security",
        mission="Ensure system security through thorough analysis and monitoring",
        values=["security", "reliability", "user-focus"],
        habitTracker=HabitTracker(frequency="weekly", target=1),
        priority="high",
        estimatedTime=3.0,
        assignedAgent="sentry",
        tags=["security", "audit", "monitoring", "sentry"],
        isSystem=True,
        createdBy="system"
    ),
    TaskTemplate(
        id="steve-august-focus-formula",
        name="🧠 Steve August Focus Formula",
        description="Licensed ADHD coaching worksheet for weekly focus and productivity management",
        category="adhd-coaching",
        mission="ADHD-focused weekly productivity planning with executive function support",
        values=["focus", "self-care", "executive-function", "sustainability"],
        habitTracker=HabitTracker(frequency="weekly", target=1),
        priority="medium",
        estimatedTime=0.5,  # Time to complete the template, not the tasks within
        assignedAgent="alden",
        tags=["adhd-coaching", "weekly-planning", "steve-august", "focus-formula", "licensed"],
        isSystem=True,
        createdBy="system"
    )
]

# Endpoints

@router.get("/", response_model=List[TaskTemplate])
async def get_templates(
    category: Optional[str] = None,
    active_only: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Get all available task templates with optional filtering"""
    try:
        # Start with system templates
        templates = SYSTEM_TEMPLATES.copy()
        
        # Load user templates from Vault
        try:
            user_templates_data = await vault_manager.retrieve_memory(
                path=f"templates/user/{current_user['user_id']}",
                decrypt=True
            )
            if user_templates_data:
                user_templates = [TaskTemplate(**t) for t in user_templates_data.get('templates', [])]
                templates.extend(user_templates)
        except Exception as e:
            logger.warning(f"Failed to load user templates: {e}")
        
        # Apply filters
        if category:
            templates = [t for t in templates if t.category == category]
        
        if active_only:
            templates = [t for t in templates if t.isActive]
        
        logger.info(f"Retrieved {len(templates)} templates for user {current_user['user_id']}")
        return templates
        
    except Exception as e:
        logger.error(f"Failed to get templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve templates")

@router.get("/{template_id}", response_model=TaskTemplate)
async def get_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific template by ID"""
    try:
        # Check system templates first
        for template in SYSTEM_TEMPLATES:
            if template.id == template_id:
                return template
        
        # Check user templates in Vault
        user_templates_data = await vault_manager.retrieve_memory(
            path=f"templates/user/{current_user['user_id']}",
            decrypt=True
        )
        
        if user_templates_data:
            for template_data in user_templates_data.get('templates', []):
                if template_data.get('id') == template_id:
                    return TaskTemplate(**template_data)
        
        raise HTTPException(status_code=404, detail="Template not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve template")

@router.post("/", response_model=TaskTemplate)
async def create_template(
    template: TaskTemplate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new task template"""
    try:
        # Set metadata
        template.id = str(uuid.uuid4())
        template.created = datetime.now()
        template.updated = datetime.now()
        template.createdBy = current_user['user_id']
        template.isSystem = False
        
        # Store in Vault
        await _store_user_template(template, current_user['user_id'])
        
        # Log audit entry
        await _log_audit_entry(AuditEntry(
            operation="CREATE",
            entityType="template",
            entityId=template.id,
            agent=current_user['agent'],
            metadata={
                "name": template.name,
                "category": template.category,
                "mission": template.mission[:100] if template.mission else ""
            }
        ))
        
        # Notify Alden of new template
        await _notify_alden_template_created(template, current_user)
        
        logger.info(f"Created template {template.id} for user {current_user['user_id']}")
        return template
        
    except Exception as e:
        logger.error(f"Failed to create template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create template")

@router.put("/{template_id}", response_model=TaskTemplate)
async def update_template(
    template_id: str,
    template_update: TaskTemplate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing template"""
    try:
        # Get existing template
        existing_template = await get_template(template_id, current_user)
        
        # Prevent updating system templates
        if existing_template.isSystem:
            raise HTTPException(status_code=403, detail="Cannot modify system templates")
        
        # Update fields
        template_update.id = template_id
        template_update.created = existing_template.created
        template_update.updated = datetime.now()
        template_update.createdBy = existing_template.createdBy
        template_update.isSystem = False
        
        # Store updated template
        await _store_user_template(template_update, current_user['user_id'])
        
        # Log audit entry
        await _log_audit_entry(AuditEntry(
            operation="UPDATE",
            entityType="template",
            entityId=template_id,
            agent=current_user['agent'],
            metadata={
                "name": template_update.name,
                "category": template_update.category,
                "changes": "template updated"
            }
        ))
        
        logger.info(f"Updated template {template_id} for user {current_user['user_id']}")
        return template_update
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update template")

@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a template (soft delete)"""
    try:
        # Get existing template
        existing_template = await get_template(template_id, current_user)
        
        # Prevent deleting system templates
        if existing_template.isSystem:
            raise HTTPException(status_code=403, detail="Cannot delete system templates")
        
        # Soft delete by setting isActive to False
        existing_template.isActive = False
        existing_template.updated = datetime.now()
        
        # Store updated template
        await _store_user_template(existing_template, current_user['user_id'])
        
        # Log audit entry
        await _log_audit_entry(AuditEntry(
            operation="DELETE",
            entityType="template",
            entityId=template_id,
            agent=current_user['agent'],
            metadata={
                "name": existing_template.name,
                "category": existing_template.category,
                "action": "soft_delete"
            }
        ))
        
        logger.info(f"Deleted template {template_id} for user {current_user['user_id']}")
        return {"message": "Template deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete template")

@router.post("/audit", status_code=201)
async def log_audit_entry(
    audit_entry: AuditEntry,
    current_user: dict = Depends(get_current_user)
):
    """Log an audit entry for CRUD operations"""
    try:
        await _log_audit_entry(audit_entry)
        return {"message": "Audit entry logged successfully"}
        
    except Exception as e:
        logger.error(f"Failed to log audit entry: {e}")
        raise HTTPException(status_code=500, detail="Failed to log audit entry")

@router.get("/audit/{entity_id}")
async def get_audit_trail(
    entity_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get audit trail for a specific entity"""
    try:
        audit_data = await vault_manager.retrieve_memory(
            path=f"audit/templates/{entity_id}",
            decrypt=True
        )
        
        if not audit_data:
            return {"audit_trail": []}
        
        return {"audit_trail": audit_data.get('entries', [])}
        
    except Exception as e:
        logger.error(f"Failed to get audit trail for {entity_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit trail")

# Helper Functions

async def _store_user_template(template: TaskTemplate, user_id: str):
    """Store user template in Vault"""
    try:
        # Get existing user templates
        existing_data = await vault_manager.retrieve_memory(
            path=f"templates/user/{user_id}",
            decrypt=True
        ) or {"templates": []}
        
        # Update or add template
        templates = existing_data.get("templates", [])
        template_dict = template.dict()
        
        # Find and update existing template
        updated = False
        for i, existing_template in enumerate(templates):
            if existing_template.get("id") == template.id:
                templates[i] = template_dict
                updated = True
                break
        
        # Add new template if not found
        if not updated:
            templates.append(template_dict)
        
        # Store updated templates
        await vault_manager.store_memory(
            content={
                "templates": templates,
                "updated": datetime.now().isoformat()
            },
            path=f"templates/user/{user_id}",
            encrypt=True,
            metadata={
                "type": "user_templates",
                "user_id": user_id,
                "template_count": len(templates)
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to store user template: {e}")
        raise

async def _log_audit_entry(audit_entry: AuditEntry):
    """Log audit entry to Vault"""
    try:
        audit_path = f"audit/templates/{audit_entry.entityId}"
        
        # Get existing audit entries
        existing_data = await vault_manager.retrieve_memory(
            path=audit_path,
            decrypt=True
        ) or {"entries": []}
        
        # Add new entry
        entries = existing_data.get("entries", [])
        entries.append(audit_entry.dict())
        
        # Keep only last 100 entries per entity
        if len(entries) > 100:
            entries = entries[-100:]
        
        # Store updated audit trail
        await vault_manager.store_memory(
            content={"entries": entries},
            path=audit_path,
            encrypt=True,
            metadata={
                "type": "audit_trail",
                "entity_id": audit_entry.entityId,
                "entity_type": audit_entry.entityType,
                "last_operation": audit_entry.operation
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to log audit entry: {e}")
        raise

async def _notify_alden_template_created(template: TaskTemplate, current_user: dict):
    """Notify Alden persona of new template creation"""
    try:
        # Create notification for Alden's memory
        notification = {
            "type": "template_created",
            "template_id": template.id,
            "template_name": template.name,
            "category": template.category,
            "mission": template.mission,
            "created_by": current_user['user_id'],
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in Alden's notification stream
        await vault_manager.store_memory(
            content=notification,
            path=f"notifications/alden/{uuid.uuid4()}",
            encrypt=True,
            metadata={
                "type": "template_notification",
                "agent": "alden",
                "priority": "low"
            }
        )
        
        logger.info(f"Notified Alden of template creation: {template.id}")
        
    except Exception as e:
        logger.warning(f"Failed to notify Alden of template creation: {e}")

# Export router
__all__ = ["router"]