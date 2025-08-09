"""
SPEC-2 Vault Tasks API - Encrypted Task Storage with Memory Integration

Provides endpoints for:
- Vault-backed task persistence with encryption
- Memory-tagged task storage for LLM context
- Cross-agent task sharing and synchronization
- Real-time task status updates with Alden integration
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import uuid
import logging
import asyncio

from src.vault.vault import VaultManager
from src.personas.alden import AldenPersona
from src.llm.local_llm_client import LocalLLMClient
from src.log_handling.agent_token_tracker import AgentTokenTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# API Router
router = APIRouter(prefix="/api/vault", tags=["vault-tasks"])

# Initialize services
vault_manager = VaultManager()
alden = AldenPersona()
llm_client = LocalLLMClient()
token_tracker = AgentTokenTracker()

# Pydantic Models
class VaultTaskRequest(BaseModel):
    task: Dict[str, Any] = Field(..., description="Complete task object")
    vaultPath: str = Field(..., description="Vault storage path")
    encrypted: bool = Field(default=True, description="Encrypt task data")
    memoryTags: List[str] = Field(default_factory=list, description="Memory tags for LLM context")
    syncAgents: List[str] = Field(default_factory=list, description="Agents to sync with")

class VaultTaskResponse(BaseModel):
    taskId: str = Field(..., description="Task ID")
    vaultPath: str = Field(..., description="Vault storage path")
    encrypted: bool = Field(..., description="Encryption status")
    memoryTags: List[str] = Field(..., description="Applied memory tags")
    syncStatus: Dict[str, str] = Field(..., description="Agent sync status")
    timestamp: datetime = Field(default_factory=datetime.now)

class TaskQuery(BaseModel):
    query: str = Field(..., description="Semantic query for tasks")
    userId: str = Field(..., description="User ID for filtering")
    agents: List[str] = Field(default_factory=list, description="Filter by agents")
    categories: List[str] = Field(default_factory=list, description="Filter by categories")
    dateRange: Optional[Dict[str, datetime]] = Field(default=None)
    limit: int = Field(default=10, description="Maximum results")

class MemoryRetrievalRequest(BaseModel):
    query: str = Field(..., description="Memory query")
    userId: str = Field(..., description="User ID")
    maxResults: int = Field(default=5, description="Maximum results")
    similarityThreshold: float = Field(default=0.7, description="Similarity threshold")
    contextWindow: int = Field(default=2000, description="Context window in tokens")

class TaskSyncStatus(BaseModel):
    taskId: str = Field(..., description="Task ID")
    agent: str = Field(..., description="Agent name")
    status: str = Field(..., description="Sync status")
    lastSync: datetime = Field(default_factory=datetime.now)
    conflictCount: int = Field(default=0, description="Number of conflicts")

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if not token or token == "test-token":
        return {"user_id": "test-user", "agent": "alden"}
    
    # In production, validate JWT token
    try:
        return {"user_id": "authenticated-user", "agent": "alden"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# Main Endpoints

@router.post("/tasks", response_model=VaultTaskResponse)
async def store_task_in_vault(
    request: VaultTaskRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Store a task in Vault with encryption and memory tagging"""
    try:
        task = request.task
        task_id = task.get('id', str(uuid.uuid4()))
        
        # Prepare task metadata
        task_metadata = {
            "type": "task",
            "user_id": current_user['user_id'],
            "agent": task.get('assignedAgent', 'alden'),
            "category": task.get('category', 'general'),
            "priority": task.get('priority', 'medium'),
            "created": datetime.now().isoformat(),
            "memory_tags": request.memoryTags,
            "encrypted": request.encrypted
        }
        
        # Store in Vault
        storage_result = await vault_manager.store_memory(
            content=task,
            path=request.vaultPath,
            encrypt=request.encrypted,
            metadata=task_metadata
        )
        
        # Process memory tags for LLM context
        if request.memoryTags:
            background_tasks.add_task(
                _process_memory_tags,
                task_id,
                request.memoryTags,
                task,
                current_user
            )
        
        # Sync with specified agents
        sync_status = {}
        if request.syncAgents:
            for agent in request.syncAgents:
                sync_status[agent] = "queued"
                background_tasks.add_task(
                    _sync_task_with_agent,
                    task_id,
                    agent,
                    task,
                    request.vaultPath
                )
        
        # Notify Alden of task storage
        background_tasks.add_task(
            _notify_alden_task_stored,
            task_id,
            task,
            current_user
        )
        
        logger.info(f"Stored task {task_id} in vault at {request.vaultPath}")
        
        return VaultTaskResponse(
            taskId=task_id,
            vaultPath=request.vaultPath,
            encrypted=request.encrypted,
            memoryTags=request.memoryTags,
            syncStatus=sync_status,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Failed to store task in vault: {e}")
        raise HTTPException(status_code=500, detail="Failed to store task")

@router.get("/tasks/{task_id}")
async def get_task_from_vault(
    task_id: str,
    decrypt: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """Retrieve a task from Vault"""
    try:
        # Try multiple possible paths
        possible_paths = [
            f"tasks/{current_user['agent']}/{task_id}",
            f"tasks/{current_user['user_id']}/{task_id}",
            f"tasks/shared/{task_id}"
        ]
        
        for path in possible_paths:
            try:
                task_data = await vault_manager.retrieve_memory(
                    path=path,
                    decrypt=decrypt
                )
                if task_data:
                    logger.info(f"Retrieved task {task_id} from vault path {path}")
                    return {
                        "task": task_data,
                        "vaultPath": path,
                        "encrypted": decrypt,
                        "retrievedAt": datetime.now().isoformat()
                    }
            except Exception as e:
                logger.debug(f"Failed to retrieve from path {path}: {e}")
                continue
        
        raise HTTPException(status_code=404, detail="Task not found in vault")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve task")

@router.put("/tasks/{task_id}")
async def update_task_in_vault(
    task_id: str,
    request: VaultTaskRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Update a task in Vault"""
    try:
        # Get existing task first
        existing_task_response = await get_task_from_vault(task_id, current_user=current_user)
        existing_path = existing_task_response['vaultPath']
        
        # Update task metadata
        updated_task = request.task
        updated_task['updated'] = datetime.now().isoformat()
        
        # Store updated task
        await vault_manager.store_memory(
            content=updated_task,
            path=existing_path,
            encrypt=request.encrypted,
            metadata={
                "type": "task",
                "user_id": current_user['user_id'],
                "agent": updated_task.get('assignedAgent', 'alden'),
                "category": updated_task.get('category', 'general'),
                "priority": updated_task.get('priority', 'medium'),
                "updated": datetime.now().isoformat(),
                "memory_tags": request.memoryTags,
                "encrypted": request.encrypted
            }
        )
        
        # Update memory tags
        if request.memoryTags:
            background_tasks.add_task(
                _process_memory_tags,
                task_id,
                request.memoryTags,
                updated_task,
                current_user
            )
        
        # Log update with Alden
        background_tasks.add_task(
            _notify_alden_task_updated,
            task_id,
            updated_task,
            current_user
        )
        
        logger.info(f"Updated task {task_id} in vault")
        return {"message": "Task updated successfully", "taskId": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update task")

@router.post("/tasks/query")
async def query_tasks_semantic(
    query: TaskQuery,
    current_user: dict = Depends(get_current_user)
):
    """Semantically query tasks using LLM-enhanced search"""
    try:
        # Build search parameters
        search_paths = [
            f"tasks/{current_user['user_id']}/*",
            f"tasks/{current_user['agent']}/*",
            f"tasks/shared/*"
        ]
        
        # Retrieve candidate tasks
        candidate_tasks = []
        for path_pattern in search_paths:
            try:
                tasks = await vault_manager.search_memories(
                    path_pattern=path_pattern,
                    metadata_filter={
                        "type": "task",
                        "user_id": query.userId
                    }
                )
                candidate_tasks.extend(tasks)
            except Exception as e:
                logger.debug(f"Search failed for pattern {path_pattern}: {e}")
        
        # Apply filters
        filtered_tasks = _apply_task_filters(candidate_tasks, query)
        
        # Use LLM for semantic ranking
        if filtered_tasks and query.query.strip():
            ranked_tasks = await _semantic_rank_tasks(
                filtered_tasks,
                query.query,
                current_user
            )
        else:
            ranked_tasks = filtered_tasks
        
        # Limit results
        results = ranked_tasks[:query.limit]
        
        logger.info(f"Found {len(results)} tasks for query: {query.query[:50]}...")
        
        return {
            "query": query.query,
            "totalFound": len(ranked_tasks),
            "returned": len(results),
            "tasks": results,
            "searchTimestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to query tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to query tasks")

@router.get("/memories/recent")
async def get_recent_memories(
    limit: int = 10,
    query: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get recent task memories for context"""
    try:
        # Search recent task-related memories
        recent_memories = await vault_manager.search_memories(
            path_pattern=f"tasks/{current_user['user_id']}/*",
            metadata_filter={"type": "task"},
            limit=limit,
            sort_by="created",
            sort_order="desc"
        )
        
        # Filter by query if provided
        if query and query.strip():
            filtered_memories = []
            query_lower = query.lower()
            for memory in recent_memories:
                memory_text = json.dumps(memory).lower()
                if query_lower in memory_text:
                    filtered_memories.append(memory)
            recent_memories = filtered_memories
        
        logger.info(f"Retrieved {len(recent_memories)} recent memories")
        return recent_memories
        
    except Exception as e:
        logger.error(f"Failed to get recent memories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recent memories")

@router.get("/conversations/recent")
async def get_recent_conversations(
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Get recent task-related conversations"""
    try:
        # Search for conversation memories
        conversations = await vault_manager.search_memories(
            path_pattern=f"conversations/{current_user['user_id']}/*",
            metadata_filter={"type": "conversation"},
            limit=limit,
            sort_by="created",
            sort_order="desc"
        )
        
        # Filter for task-related conversations
        task_conversations = []
        for conv in conversations:
            if any(keyword in json.dumps(conv).lower() 
                   for keyword in ['task', 'todo', 'project', 'work', 'assignment']):
                task_conversations.append(conv)
        
        logger.info(f"Retrieved {len(task_conversations)} recent task conversations")
        return task_conversations
        
    except Exception as e:
        logger.error(f"Failed to get recent conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations")

@router.get("/cross-agent-memory")
async def get_cross_agent_memory(
    query: str,
    agents: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Get memory consistency across multiple agents"""
    try:
        agent_memories = {}
        
        for agent in agents:
            try:
                memories = await vault_manager.search_memories(
                    path_pattern=f"agents/{agent}/memories/*",
                    metadata_filter={"type": "agent_memory"},
                    limit=5
                )
                
                # Filter by query relevance
                relevant_memories = []
                query_lower = query.lower()
                for memory in memories:
                    memory_text = json.dumps(memory).lower()
                    if query_lower in memory_text:
                        relevant_memories.append(memory)
                
                agent_memories[f"{agent}_memory"] = relevant_memories
            except Exception as e:
                logger.warning(f"Failed to get memories for agent {agent}: {e}")
                agent_memories[f"{agent}_memory"] = []
        
        # Calculate consistency score
        consistency_score = _calculate_memory_consistency(agent_memories)
        
        return {
            **agent_memories,
            "consistency_score": consistency_score,
            "query": query,
            "agents": agents,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get cross-agent memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cross-agent memory")

@router.get("/sync-status/{task_id}")
async def get_task_sync_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get synchronization status for a task across agents"""
    try:
        sync_data = await vault_manager.retrieve_memory(
            path=f"sync/tasks/{task_id}",
            decrypt=True
        )
        
        if not sync_data:
            return {"taskId": task_id, "syncStatus": {}, "lastChecked": datetime.now().isoformat()}
        
        return {
            "taskId": task_id,
            "syncStatus": sync_data.get("agents", {}),
            "lastSync": sync_data.get("lastSync"),
            "conflictCount": sync_data.get("conflictCount", 0),
            "lastChecked": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get sync status for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sync status")

# Helper Functions

async def _process_memory_tags(task_id: str, memory_tags: List[str], task: Dict, current_user: dict):
    """Process memory tags for LLM context integration"""
    try:
        # Create memory entry for each tag
        for tag in memory_tags:
            memory_content = {
                "task_id": task_id,
                "tag": tag,
                "task_title": task.get('title', ''),
                "task_description": task.get('description', ''),
                "category": task.get('category', ''),
                "agent": task.get('assignedAgent', 'alden'),
                "created": datetime.now().isoformat()
            }
            
            await vault_manager.store_memory(
                content=memory_content,
                path=f"memory_tags/{tag}/{task_id}",
                encrypt=True,
                metadata={
                    "type": "memory_tag",
                    "tag": tag,
                    "task_id": task_id,
                    "user_id": current_user['user_id']
                }
            )
        
        logger.info(f"Processed {len(memory_tags)} memory tags for task {task_id}")
        
    except Exception as e:
        logger.error(f"Failed to process memory tags: {e}")

async def _sync_task_with_agent(task_id: str, agent: str, task: Dict, vault_path: str):
    """Sync task with specified agent"""
    try:
        # Create agent-specific task copy
        agent_task_path = f"agents/{agent}/tasks/{task_id}"
        
        await vault_manager.store_memory(
            content=task,
            path=agent_task_path,
            encrypt=True,
            metadata={
                "type": "agent_task",
                "agent": agent,
                "original_path": vault_path,
                "task_id": task_id,
                "synced": datetime.now().isoformat()
            }
        )
        
        # Update sync status
        await _update_sync_status(task_id, agent, "synced")
        
        logger.info(f"Synced task {task_id} with agent {agent}")
        
    except Exception as e:
        logger.error(f"Failed to sync task {task_id} with agent {agent}: {e}")
        await _update_sync_status(task_id, agent, "failed")

async def _update_sync_status(task_id: str, agent: str, status: str):
    """Update synchronization status for a task and agent"""
    try:
        sync_path = f"sync/tasks/{task_id}"
        
        # Get existing sync data
        sync_data = await vault_manager.retrieve_memory(
            path=sync_path,
            decrypt=True
        ) or {"agents": {}, "conflictCount": 0}
        
        # Update agent status
        sync_data["agents"][agent] = {
            "status": status,
            "lastSync": datetime.now().isoformat()
        }
        sync_data["lastSync"] = datetime.now().isoformat()
        
        # Store updated sync data
        await vault_manager.store_memory(
            content=sync_data,
            path=sync_path,
            encrypt=True,
            metadata={
                "type": "sync_status",
                "task_id": task_id,
                "agents": list(sync_data["agents"].keys())
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to update sync status: {e}")

async def _notify_alden_task_stored(task_id: str, task: Dict, current_user: dict):
    """Notify Alden of task storage"""
    try:
        notification = {
            "type": "task_stored",
            "task_id": task_id,
            "task_title": task.get('title', ''),
            "category": task.get('category', ''),
            "priority": task.get('priority', ''),
            "user_id": current_user['user_id'],
            "timestamp": datetime.now().isoformat()
        }
        
        await vault_manager.store_memory(
            content=notification,
            path=f"notifications/alden/{uuid.uuid4()}",
            encrypt=True,
            metadata={
                "type": "task_notification",
                "agent": "alden",
                "priority": "normal"
            }
        )
        
    except Exception as e:
        logger.warning(f"Failed to notify Alden: {e}")

async def _notify_alden_task_updated(task_id: str, task: Dict, current_user: dict):
    """Notify Alden of task update"""
    try:
        notification = {
            "type": "task_updated",
            "task_id": task_id,
            "task_title": task.get('title', ''),
            "status": task.get('status', ''),
            "progress": task.get('progress', 0),
            "user_id": current_user['user_id'],
            "timestamp": datetime.now().isoformat()
        }
        
        await vault_manager.store_memory(
            content=notification,
            path=f"notifications/alden/{uuid.uuid4()}",
            encrypt=True,
            metadata={
                "type": "task_update_notification",
                "agent": "alden",
                "priority": "low"
            }
        )
        
    except Exception as e:
        logger.warning(f"Failed to notify Alden of update: {e}")

def _apply_task_filters(tasks: List[Dict], query: TaskQuery) -> List[Dict]:
    """Apply filters to task list"""
    filtered = tasks
    
    # Filter by agents
    if query.agents:
        filtered = [t for t in filtered if t.get('assignedAgent') in query.agents]
    
    # Filter by categories
    if query.categories:
        filtered = [t for t in filtered if t.get('category') in query.categories]
    
    # Filter by date range
    if query.dateRange:
        start_date = query.dateRange.get('start')
        end_date = query.dateRange.get('end')
        if start_date or end_date:
            date_filtered = []
            for task in filtered:
                task_date_str = task.get('created') or task.get('updated')
                if task_date_str:
                    try:
                        task_date = datetime.fromisoformat(task_date_str.replace('Z', '+00:00'))
                        if start_date and task_date < start_date:
                            continue
                        if end_date and task_date > end_date:
                            continue
                        date_filtered.append(task)
                    except Exception:
                        # Skip tasks with invalid dates
                        continue
            filtered = date_filtered
    
    return filtered

async def _semantic_rank_tasks(tasks: List[Dict], query: str, current_user: dict) -> List[Dict]:
    """Use LLM to semantically rank tasks by relevance"""
    try:
        if not tasks or not query.strip():
            return tasks
        
        # Prepare task summaries for LLM
        task_summaries = []
        for i, task in enumerate(tasks):
            summary = f"Task {i}: {task.get('title', '')} - {task.get('description', '')[:100]}"
            task_summaries.append(summary)
        
        # Create LLM prompt for ranking
        prompt = f\"\"\"Rank these tasks by relevance to the query: "{query}"
        
Tasks:
{chr(10).join(task_summaries)}

Return only the task indices in order of relevance (most relevant first), separated by commas.
Example: 2,0,1,3\"\"\"\n        \n        # Get LLM ranking\n        try:\n            response = await llm_client.generate_response(\n                prompt=prompt,\n                max_tokens=100,\n                temperature=0.1\n            )\n            \n            # Parse ranking\n            ranking_str = response.strip()\n            indices = [int(x.strip()) for x in ranking_str.split(',') if x.strip().isdigit()]\n            \n            # Reorder tasks based on ranking\n            ranked_tasks = []\n            for idx in indices:\n                if 0 <= idx < len(tasks):\n                    ranked_tasks.append(tasks[idx])\n            \n            # Add any remaining tasks not in ranking\n            remaining_tasks = [t for i, t in enumerate(tasks) if i not in indices]\n            ranked_tasks.extend(remaining_tasks)\n            \n            return ranked_tasks\n            \n        except Exception as e:\n            logger.warning(f\"LLM ranking failed, using original order: {e}\")\n            return tasks\n            \n    except Exception as e:\n        logger.error(f\"Failed to rank tasks semantically: {e}\")\n        return tasks\n\ndef _calculate_memory_consistency(agent_memories: Dict[str, List]) -> float:\n    \"\"\"Calculate consistency score across agent memories\"\"\"\n    try:\n        if not agent_memories or len(agent_memories) < 2:\n            return 1.0\n        \n        # Simple consistency calculation based on memory overlap\n        all_memories = []\n        for memories in agent_memories.values():\n            all_memories.extend([json.dumps(m, sort_keys=True) for m in memories])\n        \n        if not all_memories:\n            return 1.0\n        \n        # Calculate uniqueness ratio (lower = more consistent)\n        unique_memories = set(all_memories)\n        consistency = 1.0 - (len(unique_memories) / len(all_memories))\n        \n        return max(0.0, min(1.0, consistency))\n        \n    except Exception as e:\n        logger.error(f\"Failed to calculate memory consistency: {e}\")\n        return 0.5\n\n# Export router\n__all__ = [\"router\"]"