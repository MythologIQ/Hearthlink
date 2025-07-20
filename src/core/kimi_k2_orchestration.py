"""
Kimi K2 Multi-Agent Orchestration Extension

This module extends the Core orchestration system to support Kimi K2's
agentic capabilities including multi-step reasoning, tool calling, and
autonomous task execution.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from .core import Core, Participant, ParticipantType, SessionEvent, TurnStatus
from ..llm.KimiK2Backend import KimiK2Backend
from ..monitoring.TokenTracker import TokenTracker
from ..utils.errors import CoreError, AgenticWorkflowError, ToolCallError

class AgentCapabilityType(Enum):
    """Agent capability types for enhanced orchestration."""
    CONVERSATIONAL = "conversational"
    AGENTIC = "agentic"
    TOOL_CALLING = "tool_calling"
    REASONING = "reasoning"
    CODE_GENERATION = "code_generation"
    LONG_CONTEXT = "long_context"
    MULTI_STEP = "multi_step"
    AUTONOMOUS = "autonomous"

class WorkflowStatus(Enum):
    """Agentic workflow status."""
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_FOR_TOOLS = "waiting_for_tools"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class AgentCapabilities:
    """Agent capabilities metadata."""
    agent_id: str
    capabilities: List[AgentCapabilityType] = field(default_factory=list)
    max_tokens: int = 4096
    context_window: int = 4096
    tool_calling: bool = False
    streaming: bool = False
    cost_per_token: float = 0.0
    response_time_avg: float = 0.0
    success_rate: float = 1.0
    specialized_domains: List[str] = field(default_factory=list)

@dataclass
class AgenticWorkflow:
    """Agentic workflow representation."""
    workflow_id: str
    session_id: str
    agent_id: str
    task_description: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    status: WorkflowStatus = WorkflowStatus.PLANNING
    tools_used: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    intermediate_results: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ToolCall:
    """Tool call representation."""
    tool_id: str
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    executed_at: Optional[str] = None
    execution_time: Optional[float] = None

@dataclass
class EnhancedParticipant(Participant):
    """Enhanced participant with capabilities and workflow state."""
    capabilities: AgentCapabilities = field(default_factory=lambda: AgentCapabilities(""))
    current_workflow: Optional[str] = None
    workflow_history: List[str] = field(default_factory=list)
    context_memory: Dict[str, Any] = field(default_factory=dict)
    tool_permissions: List[str] = field(default_factory=list)
    backend_type: str = "default"

class KimiK2Orchestrator:
    """
    Enhanced orchestration system for Kimi K2 agentic capabilities.
    
    This class extends the Core orchestration system to support:
    - Multi-step agentic workflows
    - Tool calling and function execution
    - Context-aware agent coordination
    - Autonomous task execution
    """
    
    def __init__(self, core: Core, kimi_k2_backend: KimiK2Backend):
        """
        Initialize the Kimi K2 orchestrator.
        
        Args:
            core: Core orchestration instance
            kimi_k2_backend: Kimi K2 backend instance
        """
        self.core = core
        self.kimi_k2_backend = kimi_k2_backend
        self.workflows: Dict[str, AgenticWorkflow] = {}
        self.agent_capabilities: Dict[str, AgentCapabilities] = {}
        self.token_tracker = TokenTracker("kimi-k2-orchestrator")
        
        # Initialize default capabilities
        self._initialize_agent_capabilities()
        
        # Setup workflow management
        self._setup_workflow_management()
        
    def _initialize_agent_capabilities(self):
        """Initialize default agent capabilities."""
        
        # Kimi K2 capabilities
        self.agent_capabilities["kimi-k2"] = AgentCapabilities(
            agent_id="kimi-k2",
            capabilities=[
                AgentCapabilityType.CONVERSATIONAL,
                AgentCapabilityType.AGENTIC,
                AgentCapabilityType.TOOL_CALLING,
                AgentCapabilityType.REASONING,
                AgentCapabilityType.CODE_GENERATION,
                AgentCapabilityType.LONG_CONTEXT,
                AgentCapabilityType.MULTI_STEP,
                AgentCapabilityType.AUTONOMOUS
            ],
            max_tokens=8192,
            context_window=128000,
            tool_calling=True,
            streaming=True,
            cost_per_token=0.0015,  # Average cost
            specialized_domains=["coding", "reasoning", "analysis", "automation"]
        )
        
        # Alden capabilities (enhanced for comparison)
        self.agent_capabilities["alden"] = AgentCapabilities(
            agent_id="alden",
            capabilities=[
                AgentCapabilityType.CONVERSATIONAL,
                AgentCapabilityType.REASONING,
                AgentCapabilityType.CODE_GENERATION
            ],
            max_tokens=4096,
            context_window=8192,
            tool_calling=False,
            streaming=False,
            cost_per_token=0.003,
            specialized_domains=["productivity", "personal_assistance", "analysis"]
        )
        
        # Alice capabilities
        self.agent_capabilities["alice"] = AgentCapabilities(
            agent_id="alice",
            capabilities=[
                AgentCapabilityType.CONVERSATIONAL,
                AgentCapabilityType.REASONING
            ],
            max_tokens=4096,
            context_window=8192,
            tool_calling=False,
            streaming=False,
            cost_per_token=0.003,
            specialized_domains=["cognitive_analysis", "behavioral_analysis", "psychology"]
        )
        
    def _setup_workflow_management(self):
        """Setup workflow management system."""
        # Start workflow monitoring task
        asyncio.create_task(self._monitor_workflows())
        
    async def _monitor_workflows(self):
        """Monitor and manage active workflows."""
        while True:
            try:
                # Check for stalled workflows
                current_time = time.time()
                for workflow_id, workflow in self.workflows.items():
                    if workflow.status == WorkflowStatus.EXECUTING:
                        # Check if workflow has been running too long
                        created_time = datetime.fromisoformat(workflow.created_at).timestamp()
                        if current_time - created_time > 600:  # 10 minutes timeout
                            workflow.status = WorkflowStatus.FAILED
                            workflow.error_message = "Workflow timeout"
                            await self._handle_workflow_failure(workflow)
                
                # Sleep for monitoring interval
                await asyncio.sleep(10)
                
            except Exception as e:
                self.core.logger.error(f"Workflow monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def create_agentic_workflow(self, session_id: str, agent_id: str, 
                                    task_description: str, tools: Optional[List[str]] = None,
                                    context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new agentic workflow.
        
        Args:
            session_id: Session ID where workflow will run
            agent_id: Agent that will execute the workflow
            task_description: Description of the task to be performed
            tools: List of available tools
            context: Additional context for the workflow
            
        Returns:
            Workflow ID
        """
        workflow_id = f"workflow-{int(time.time())}-{len(self.workflows)}"
        
        # Check if agent has agentic capabilities
        if agent_id not in self.agent_capabilities:
            raise CoreError(f"Agent {agent_id} not found in capabilities registry")
        
        capabilities = self.agent_capabilities[agent_id]
        if AgentCapabilityType.AGENTIC not in capabilities.capabilities:
            raise CoreError(f"Agent {agent_id} does not support agentic workflows")
        
        # Create workflow
        workflow = AgenticWorkflow(
            workflow_id=workflow_id,
            session_id=session_id,
            agent_id=agent_id,
            task_description=task_description,
            context=context or {}
        )
        
        # Add tools if provided
        if tools:
            workflow.context["available_tools"] = tools
        
        self.workflows[workflow_id] = workflow
        
        # Log workflow creation
        self.core._log(
            "workflow_created",
            "system",
            session_id,
            "workflow",
            {
                "workflow_id": workflow_id,
                "agent_id": agent_id,
                "task_description": task_description,
                "tools": tools or []
            }
        )
        
        return workflow_id
    
    async def execute_agentic_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute an agentic workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            
        Returns:
            Execution result
        """
        if workflow_id not in self.workflows:
            raise CoreError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.EXECUTING
        
        try:
            # Execute workflow based on agent type
            if workflow.agent_id == "kimi-k2":
                result = await self._execute_kimi_k2_workflow(workflow)
            else:
                result = await self._execute_generic_workflow(workflow)
            
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now().isoformat()
            workflow.intermediate_results.append(result)
            
            return result
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            await self._handle_workflow_failure(workflow)
            raise
    
    async def _execute_kimi_k2_workflow(self, workflow: AgenticWorkflow) -> Dict[str, Any]:
        """Execute workflow using Kimi K2 backend."""
        
        # Prepare agentic request
        workflow_request = {
            "prompt": workflow.task_description,
            "systemMessage": "You are an advanced AI agent capable of autonomous task execution. Break down complex tasks into steps and execute them systematically.",
            "agentId": workflow.agent_id,
            "module": "agentic",
            "context": workflow.context,
            "tools": workflow.context.get("available_tools", []),
            "maxTokens": 8192,
            "temperature": 0.6
        }
        
        # Execute through Kimi K2 backend
        start_time = time.time()
        response = await self.kimi_k2_backend.executeAgenticWorkflow(workflow_request)
        execution_time = time.time() - start_time
        
        # Track usage
        self.token_tracker.trackUsage(
            response.usage,
            {
                "workflowId": workflow.workflow_id,
                "agentId": workflow.agent_id,
                "sessionId": workflow.session_id,
                "requestId": response.requestId
            }
        )
        
        # Process tool calls if any
        tool_results = []
        if response.toolCalls:
            for tool_call in response.toolCalls:
                tool_result = await self._execute_tool_call(tool_call, workflow)
                tool_results.append(tool_result)
        
        # Update workflow with results
        workflow.tools_used.extend([tc.function.name for tc in (response.toolCalls or [])])
        
        return {
            "content": response.content,
            "tool_calls": response.toolCalls,
            "tool_results": tool_results,
            "execution_time": execution_time,
            "tokens_used": response.usage.totalTokens,
            "cost_estimate": response.usage.totalTokens * self.agent_capabilities[workflow.agent_id].cost_per_token
        }
    
    async def _execute_generic_workflow(self, workflow: AgenticWorkflow) -> Dict[str, Any]:
        """Execute workflow using generic agent."""
        
        # For non-Kimi K2 agents, use standard LLM request
        request = {
            "prompt": workflow.task_description,
            "agentId": workflow.agent_id,
            "module": "workflow",
            "context": workflow.context
        }
        
        # Use core's LLM backend manager
        response = await self.core.llm_backend_manager.generate(request)
        
        return {
            "content": response.content,
            "execution_time": response.responseTime / 1000,  # Convert to seconds
            "tokens_used": response.usage.totalTokens,
            "cost_estimate": response.usage.totalTokens * self.agent_capabilities[workflow.agent_id].cost_per_token
        }
    
    async def _execute_tool_call(self, tool_call: Any, workflow: AgenticWorkflow) -> ToolCall:
        """Execute a tool call within a workflow."""
        
        tool_result = ToolCall(
            tool_id=tool_call.id,
            tool_name=tool_call.function.name,
            arguments=json.loads(tool_call.function.arguments),
            executed_at=datetime.now().isoformat()
        )
        
        start_time = time.time()
        
        try:
            # Execute tool through appropriate handler
            if tool_call.function.name == "code_execution":
                result = await self._execute_code_tool(tool_result.arguments)
            elif tool_call.function.name == "file_operation":
                result = await self._execute_file_tool(tool_result.arguments)
            elif tool_call.function.name == "web_search":
                result = await self._execute_web_search_tool(tool_result.arguments)
            else:
                # Generic tool execution
                result = await self._execute_generic_tool(tool_call.function.name, tool_result.arguments)
            
            tool_result.result = result
            tool_result.execution_time = time.time() - start_time
            
        except Exception as e:
            tool_result.error = str(e)
            tool_result.execution_time = time.time() - start_time
            
        return tool_result
    
    async def _execute_code_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code tool."""
        # Implementation would depend on your code execution environment
        return {"result": "Code execution not implemented yet"}
    
    async def _execute_file_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file operation tool."""
        # Implementation would depend on your file system access
        return {"result": "File operation not implemented yet"}
    
    async def _execute_web_search_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search tool."""
        # Implementation would depend on your search integration
        return {"result": "Web search not implemented yet"}
    
    async def _execute_generic_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic tool through plugin system."""
        # This would integrate with your Synapse plugin system
        return {"result": f"Tool {tool_name} execution not implemented yet"}
    
    async def _handle_workflow_failure(self, workflow: AgenticWorkflow):
        """Handle workflow failure."""
        
        # Log failure
        self.core._log(
            "workflow_failed",
            "system",
            workflow.session_id,
            "workflow_error",
            {
                "workflow_id": workflow.workflow_id,
                "agent_id": workflow.agent_id,
                "error": workflow.error_message,
                "steps_completed": workflow.current_step,
                "total_steps": len(workflow.steps)
            }
        )
        
        # Notify session participants
        await self._notify_workflow_failure(workflow)
    
    async def _notify_workflow_failure(self, workflow: AgenticWorkflow):
        """Notify session participants about workflow failure."""
        
        # Create session event
        event = SessionEvent(
            event_id=f"workflow-failure-{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            event_type="workflow_failure",
            participant_id=workflow.agent_id,
            content=f"Workflow failed: {workflow.error_message}",
            metadata={
                "workflow_id": workflow.workflow_id,
                "task_description": workflow.task_description
            }
        )
        
        # Add to session log
        if workflow.session_id in self.core.sessions:
            self.core.sessions[workflow.session_id].session_log.append(event)
    
    def get_agent_capabilities(self, agent_id: str) -> Optional[AgentCapabilities]:
        """Get capabilities for a specific agent."""
        return self.agent_capabilities.get(agent_id)
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowStatus]:
        """Get status of a specific workflow."""
        workflow = self.workflows.get(workflow_id)
        return workflow.status if workflow else None
    
    def get_active_workflows(self, session_id: Optional[str] = None) -> List[AgenticWorkflow]:
        """Get active workflows, optionally filtered by session."""
        workflows = []
        for workflow in self.workflows.values():
            if workflow.status in [WorkflowStatus.PLANNING, WorkflowStatus.EXECUTING, WorkflowStatus.WAITING_FOR_TOOLS]:
                if session_id is None or workflow.session_id == session_id:
                    workflows.append(workflow)
        return workflows
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        stats = {
            "total_workflows": len(self.workflows),
            "completed": len([w for w in self.workflows.values() if w.status == WorkflowStatus.COMPLETED]),
            "failed": len([w for w in self.workflows.values() if w.status == WorkflowStatus.FAILED]),
            "active": len([w for w in self.workflows.values() if w.status in [WorkflowStatus.EXECUTING, WorkflowStatus.PLANNING]]),
            "by_agent": {}
        }
        
        # Count by agent
        for workflow in self.workflows.values():
            if workflow.agent_id not in stats["by_agent"]:
                stats["by_agent"][workflow.agent_id] = {"total": 0, "completed": 0, "failed": 0}
            stats["by_agent"][workflow.agent_id]["total"] += 1
            if workflow.status == WorkflowStatus.COMPLETED:
                stats["by_agent"][workflow.agent_id]["completed"] += 1
            elif workflow.status == WorkflowStatus.FAILED:
                stats["by_agent"][workflow.agent_id]["failed"] += 1
        
        return stats
    
    async def pause_workflow(self, workflow_id: str):
        """Pause a workflow."""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].status = WorkflowStatus.PAUSED
    
    async def resume_workflow(self, workflow_id: str):
        """Resume a paused workflow."""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            if workflow.status == WorkflowStatus.PAUSED:
                workflow.status = WorkflowStatus.EXECUTING
                # Resume execution
                await self.execute_agentic_workflow(workflow_id)
    
    async def cancel_workflow(self, workflow_id: str):
        """Cancel a workflow."""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = "Workflow cancelled by user"
            workflow.completed_at = datetime.now().isoformat()
    
    def cleanup_old_workflows(self, max_age_hours: int = 24):
        """Clean up old workflows."""
        current_time = datetime.now()
        workflows_to_remove = []
        
        for workflow_id, workflow in self.workflows.items():
            created_time = datetime.fromisoformat(workflow.created_at)
            age_hours = (current_time - created_time).total_seconds() / 3600
            
            if age_hours > max_age_hours and workflow.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                workflows_to_remove.append(workflow_id)
        
        for workflow_id in workflows_to_remove:
            del self.workflows[workflow_id]
            
        return len(workflows_to_remove)