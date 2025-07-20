"""
Enhanced Core Module with Kimi K2 Orchestration Integration

This module extends the base Core module to support Kimi K2's agentic capabilities
while maintaining backward compatibility with existing functionality.
"""

import asyncio
from typing import Dict, Any, Optional, List
from .core import Core, Participant, ParticipantType, SessionEvent
from .kimi_k2_orchestration import KimiK2Orchestrator, AgentCapabilities, AgentCapabilityType
from ..llm.KimiK2Backend import KimiK2Backend
from ..llm.LLMBackendManager import LLMBackendManager, LLMRequest
from ..utils.errors import CoreError

class EnhancedCore(Core):
    """
    Enhanced Core module with Kimi K2 orchestration support.
    
    Extends the base Core module to provide:
    - Agentic workflow management
    - Enhanced agent capabilities
    - Tool calling coordination
    - Multi-step task execution
    """
    
    def __init__(self, config: Dict[str, Any], vault, logger=None):
        """
        Initialize Enhanced Core with Kimi K2 orchestration.
        
        Args:
            config: Configuration dictionary
            vault: Vault instance for memory management
            logger: Optional logger instance
        """
        super().__init__(config, vault, logger)
        
        # Initialize LLM backend manager
        self.llm_backend_manager = self._initialize_llm_backend_manager()
        
        # Initialize Kimi K2 orchestrator
        self.kimi_k2_orchestrator = None
        self._initialize_kimi_k2_orchestrator()
        
        # Enhanced agent registry
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        
        # Agent delegation tracking
        self.agent_delegations: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize enhanced features
        self._initialize_enhanced_features()
    
    def _initialize_llm_backend_manager(self) -> LLMBackendManager:
        """Initialize LLM backend manager."""
        try:
            # Load backend configuration
            backend_config = self.config.get("llm_backends", {})
            
            # Create backend manager
            return LLMBackendManager(backend_config)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM backend manager: {e}")
            raise CoreError(f"LLM backend initialization failed: {e}")
    
    def _initialize_kimi_k2_orchestrator(self):
        """Initialize Kimi K2 orchestrator if backend is available."""
        try:
            # Check if Kimi K2 backend is available
            if self.llm_backend_manager and 'kimi-k2' in self.llm_backend_manager.getAvailableBackends():
                kimi_k2_backend = self.llm_backend_manager.backends.get('kimi-k2')
                if kimi_k2_backend:
                    self.kimi_k2_orchestrator = KimiK2Orchestrator(self, kimi_k2_backend)
                    self.logger.info("Kimi K2 orchestrator initialized successfully")
                else:
                    self.logger.warning("Kimi K2 backend not available")
            else:
                self.logger.info("Kimi K2 backend not configured")
        except Exception as e:
            self.logger.error(f"Failed to initialize Kimi K2 orchestrator: {e}")
    
    def _initialize_enhanced_features(self):
        """Initialize enhanced features."""
        # Register default agents
        self._register_default_agents()
        
        # Setup agent delegation system
        self._setup_agent_delegation()
        
        # Setup enhanced event handling
        self._setup_enhanced_event_handling()
    
    def _register_default_agents(self):
        """Register default agents with their capabilities."""
        
        # Register Alden
        self.agent_registry["alden"] = {
            "type": ParticipantType.PERSONA,
            "name": "Alden",
            "role": "productivity_assistant",
            "capabilities": [
                AgentCapabilityType.CONVERSATIONAL,
                AgentCapabilityType.REASONING,
                AgentCapabilityType.CODE_GENERATION
            ],
            "backend": "claude-code",
            "specializations": ["productivity", "analysis", "assistance"]
        }
        
        # Register Alice
        self.agent_registry["alice"] = {
            "type": ParticipantType.PERSONA,
            "name": "Alice",
            "role": "cognitive_analyst",
            "capabilities": [
                AgentCapabilityType.CONVERSATIONAL,
                AgentCapabilityType.REASONING
            ],
            "backend": "claude-code",
            "specializations": ["psychology", "cognitive_analysis", "behavior"]
        }
        
        # Register Kimi K2 if available
        if self.kimi_k2_orchestrator:
            self.agent_registry["kimi-k2"] = {
                "type": ParticipantType.PERSONA,
                "name": "Kimi K2",
                "role": "agentic_assistant",
                "capabilities": [
                    AgentCapabilityType.CONVERSATIONAL,
                    AgentCapabilityType.AGENTIC,
                    AgentCapabilityType.TOOL_CALLING,
                    AgentCapabilityType.REASONING,
                    AgentCapabilityType.CODE_GENERATION,
                    AgentCapabilityType.LONG_CONTEXT,
                    AgentCapabilityType.MULTI_STEP,
                    AgentCapabilityType.AUTONOMOUS
                ],
                "backend": "kimi-k2",
                "specializations": ["automation", "complex_reasoning", "tool_usage", "agentic_workflows"]
            }
    
    def _setup_agent_delegation(self):
        """Setup agent delegation system."""
        # Initialize delegation tracking for each agent
        for agent_id in self.agent_registry:
            self.agent_delegations[agent_id] = []
    
    def _setup_enhanced_event_handling(self):
        """Setup enhanced event handling for agentic workflows."""
        # Add workflow event handlers
        self.event_callbacks.append(self._handle_workflow_events)
    
    async def _handle_workflow_events(self, event: SessionEvent):
        """Handle workflow-related events."""
        if event.event_type.startswith("workflow_"):
            # Update session participants about workflow progress
            await self._notify_workflow_progress(event)
    
    async def _notify_workflow_progress(self, event: SessionEvent):
        """Notify session participants about workflow progress."""
        # Implementation would depend on your notification system
        pass
    
    async def create_agentic_session(self, user_id: str, topic: str, 
                                   primary_agent: str = "kimi-k2",
                                   tools: Optional[List[str]] = None) -> str:
        """
        Create a session optimized for agentic workflows.
        
        Args:
            user_id: User creating the session
            topic: Session topic
            primary_agent: Primary agent for agentic tasks
            tools: Available tools for the session
            
        Returns:
            Session ID
        """
        # Create regular session
        session_id = self.create_session(user_id, topic)
        
        # Add primary agent
        if primary_agent in self.agent_registry:
            agent_data = self.agent_registry[primary_agent].copy()
            agent_data["tools"] = tools or []
            await self.add_participant(session_id, user_id, agent_data)
        
        # Mark session as agentic
        session = self.sessions[session_id]
        session.audit_log.append({
            "action": "agentic_session_created",
            "timestamp": session.created_at,
            "primary_agent": primary_agent,
            "tools": tools or []
        })
        
        return session_id
    
    async def execute_agentic_task(self, session_id: str, user_id: str, 
                                 task_description: str, agent_id: str = "kimi-k2",
                                 tools: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute an agentic task within a session.
        
        Args:
            session_id: Session ID
            user_id: User requesting the task
            task_description: Description of the task
            agent_id: Agent to execute the task
            tools: Available tools for the task
            
        Returns:
            Task execution result
        """
        # Validate session and agent
        if session_id not in self.sessions:
            raise CoreError(f"Session {session_id} not found")
        
        if agent_id not in self.agent_registry:
            raise CoreError(f"Agent {agent_id} not found")
        
        # Check if agent has agentic capabilities
        agent_capabilities = self.agent_registry[agent_id]["capabilities"]
        if AgentCapabilityType.AGENTIC not in agent_capabilities:
            raise CoreError(f"Agent {agent_id} does not support agentic tasks")
        
        # Create workflow if Kimi K2 orchestrator is available
        if self.kimi_k2_orchestrator and agent_id == "kimi-k2":
            workflow_id = await self.kimi_k2_orchestrator.create_agentic_workflow(
                session_id, agent_id, task_description, tools
            )
            
            # Execute workflow
            result = await self.kimi_k2_orchestrator.execute_agentic_workflow(workflow_id)
            
            # Log task execution
            await self._log_agentic_task(session_id, user_id, task_description, agent_id, result)
            
            return {
                "workflow_id": workflow_id,
                "result": result,
                "agent_id": agent_id,
                "task_description": task_description
            }
        else:
            # Fallback to regular LLM generation
            request = LLMRequest(
                prompt=task_description,
                agentId=agent_id,
                module="agentic",
                context={"tools": tools or []},
                preferredBackend=self.agent_registry[agent_id]["backend"]
            )
            
            response = await self.llm_backend_manager.generate(request)
            
            # Log task execution
            await self._log_agentic_task(session_id, user_id, task_description, agent_id, response)
            
            return {
                "result": response,
                "agent_id": agent_id,
                "task_description": task_description
            }
    
    async def _log_agentic_task(self, session_id: str, user_id: str, 
                               task_description: str, agent_id: str, result: Any):
        """Log agentic task execution."""
        
        # Create session event
        event = SessionEvent(
            event_id=f"agentic-task-{int(asyncio.get_event_loop().time())}",
            timestamp=self._get_timestamp(),
            event_type="agentic_task_completed",
            participant_id=agent_id,
            content=task_description,
            metadata={
                "result_summary": str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
                "tokens_used": getattr(result, "usage", {}).get("totalTokens", 0),
                "execution_time": getattr(result, "responseTime", 0)
            }
        )
        
        # Add to session log
        self.sessions[session_id].session_log.append(event)
        
        # Log through core logging system
        self._log(
            "agentic_task_executed",
            user_id,
            session_id,
            "agentic_task",
            {
                "task_description": task_description,
                "agent_id": agent_id,
                "success": True
            }
        )
    
    async def delegate_to_optimal_agent(self, session_id: str, user_id: str, 
                                      task_description: str, 
                                      task_type: str = "general") -> Dict[str, Any]:
        """
        Delegate a task to the most optimal agent based on capabilities.
        
        Args:
            session_id: Session ID
            user_id: User requesting delegation
            task_description: Task to be performed
            task_type: Type of task (agentic, reasoning, coding, etc.)
            
        Returns:
            Delegation result
        """
        # Determine optimal agent
        optimal_agent = self._select_optimal_agent(task_type, task_description)
        
        if not optimal_agent:
            raise CoreError("No suitable agent found for task")
        
        # Track delegation
        delegation_record = {
            "timestamp": self._get_timestamp(),
            "task_type": task_type,
            "task_description": task_description,
            "selected_agent": optimal_agent,
            "reason": self._get_delegation_reason(optimal_agent, task_type)
        }
        
        self.agent_delegations[optimal_agent].append(delegation_record)
        
        # Execute task with optimal agent
        if self._is_agentic_task(task_type):
            result = await self.execute_agentic_task(
                session_id, user_id, task_description, optimal_agent
            )
        else:
            # Regular task execution
            request = LLMRequest(
                prompt=task_description,
                agentId=optimal_agent,
                module="delegation",
                preferredBackend=self.agent_registry[optimal_agent]["backend"]
            )
            
            response = await self.llm_backend_manager.generate(request)
            result = {"result": response, "agent_id": optimal_agent}
        
        # Log delegation
        self._log(
            "task_delegated",
            user_id,
            session_id,
            "delegation",
            {
                "task_type": task_type,
                "selected_agent": optimal_agent,
                "delegation_reason": delegation_record["reason"]
            }
        )
        
        return result
    
    def _select_optimal_agent(self, task_type: str, task_description: str) -> Optional[str]:
        """Select the optimal agent for a task."""
        
        # Task type to capability mapping
        task_capabilities = {
            "agentic": [AgentCapabilityType.AGENTIC, AgentCapabilityType.AUTONOMOUS],
            "coding": [AgentCapabilityType.CODE_GENERATION],
            "reasoning": [AgentCapabilityType.REASONING],
            "analysis": [AgentCapabilityType.REASONING],
            "tool_usage": [AgentCapabilityType.TOOL_CALLING],
            "multi_step": [AgentCapabilityType.MULTI_STEP],
            "long_context": [AgentCapabilityType.LONG_CONTEXT]
        }
        
        required_capabilities = task_capabilities.get(task_type, [AgentCapabilityType.CONVERSATIONAL])
        
        # Score agents based on capabilities
        agent_scores = {}
        for agent_id, agent_info in self.agent_registry.items():
            score = 0
            agent_capabilities = agent_info["capabilities"]
            
            # Check required capabilities
            for capability in required_capabilities:
                if capability in agent_capabilities:
                    score += 2
            
            # Check specializations
            for specialization in agent_info["specializations"]:
                if specialization in task_description.lower():
                    score += 1
            
            # Prefer Kimi K2 for agentic tasks
            if task_type == "agentic" and agent_id == "kimi-k2":
                score += 3
            
            agent_scores[agent_id] = score
        
        # Return agent with highest score
        if agent_scores:
            return max(agent_scores, key=agent_scores.get)
        
        return None
    
    def _get_delegation_reason(self, agent_id: str, task_type: str) -> str:
        """Get reason for agent delegation."""
        agent_info = self.agent_registry[agent_id]
        
        if task_type == "agentic" and agent_id == "kimi-k2":
            return "Kimi K2 selected for superior agentic capabilities"
        elif task_type == "coding" and AgentCapabilityType.CODE_GENERATION in agent_info["capabilities"]:
            return f"{agent_info['name']} selected for code generation capabilities"
        elif task_type == "reasoning":
            return f"{agent_info['name']} selected for reasoning capabilities"
        else:
            return f"{agent_info['name']} selected as best match for task type"
    
    def _is_agentic_task(self, task_type: str) -> bool:
        """Check if task requires agentic capabilities."""
        agentic_task_types = ["agentic", "multi_step", "tool_usage", "autonomous"]
        return task_type in agentic_task_types
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_agent_capabilities_summary(self) -> Dict[str, Any]:
        """Get summary of all agent capabilities."""
        summary = {}
        
        for agent_id, agent_info in self.agent_registry.items():
            summary[agent_id] = {
                "name": agent_info["name"],
                "role": agent_info["role"],
                "capabilities": [cap.value for cap in agent_info["capabilities"]],
                "specializations": agent_info["specializations"],
                "backend": agent_info["backend"],
                "delegation_count": len(self.agent_delegations.get(agent_id, []))
            }
        
        return summary
    
    def get_workflow_status_summary(self) -> Dict[str, Any]:
        """Get summary of workflow status."""
        if not self.kimi_k2_orchestrator:
            return {"error": "Kimi K2 orchestrator not available"}
        
        return self.kimi_k2_orchestrator.get_workflow_stats()
    
    def get_enhanced_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get enhanced session information including agentic capabilities."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Get base session info
        base_info = {
            "session_id": session_id,
            "topic": session.topic,
            "status": session.status.value,
            "created_at": session.created_at,
            "participants": [
                {
                    "id": p.id,
                    "name": p.name,
                    "type": p.type.value,
                    "role": p.role,
                    "capabilities": self.agent_registry.get(p.id, {}).get("capabilities", [])
                }
                for p in session.participants
            ]
        }
        
        # Add agentic information
        if self.kimi_k2_orchestrator:
            active_workflows = self.kimi_k2_orchestrator.get_active_workflows(session_id)
            base_info["active_workflows"] = len(active_workflows)
            base_info["workflow_details"] = [
                {
                    "workflow_id": w.workflow_id,
                    "agent_id": w.agent_id,
                    "status": w.status.value,
                    "task_description": w.task_description
                }
                for w in active_workflows
            ]
        
        return base_info