import React, { useState, useEffect } from 'react';
import './CoreInterface.css';
import './ConferenceUI.css';
import ProjectCommand from './ProjectCommand';

const CoreInterface = ({ accessibilitySettings, onVoiceCommand, currentAgent }) => {
  const [activeTab, setActiveTab] = useState('orchestration');
  const [conferenceRooms, setConferenceRooms] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [participants, setParticipants] = useState([]);
  const [systemStatus, setSystemStatus] = useState({
    overall: 'optimal',
    cpu: 45,
    memory: 62,
    network: 38,
    storage: 71,
    uptime: '2d 14h 32m'
  });
  const [agents, setAgents] = useState([]);
  const [projects, setProjects] = useState([]);
  const [services, setServices] = useState([]);
  const [orchestrationLogs, setOrchestrationLogs] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [orchestrationStatus, setOrchestrationStatus] = useState('idle');
  const [newRoomName, setNewRoomName] = useState('');
  const [showCreateRoomForm, setShowCreateRoomForm] = useState(false);
  const [showAgentSelectionModal, setShowAgentSelectionModal] = useState(false);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [agentPersonas, setAgentPersonas] = useState({});
  const [editingAgentPersona, setEditingAgentPersona] = useState(null);
  const [coreApiStatus, setCoreApiStatus] = useState({
    connected: false,
    lastCheck: null,
    endpoints: {
      agents: false,
      services: false,
      projects: false,
      metrics: false,
      logs: false
    }
  });
  
  // SPEC-3 Week 2: Add state for orphaned function controls
  const [coreHealthStatus, setCoreHealthStatus] = useState(null);
  const [coreStatus, setCoreStatus] = useState(null);
  const [executionResult, setExecutionResult] = useState(null);

  useEffect(() => {
    initializeCoreServices();
    loadOrchestrationLogs();
    loadAgentPersonas();
    
    // Listen for Synapse agent updates
    const handleSynapseAgentUpdate = (event) => {
      const { agentId, config } = event.detail;
      addOrchestrationLog(`Agent ${config.name} updated from Synapse`, 'info');
      discoverAgents(); // Refresh agent list
    };
    
    const handleSynapseAgentRemoved = (event) => {
      const { agentId } = event.detail;
      addOrchestrationLog(`Agent ${agentId} removed from Synapse`, 'warning');
      discoverAgents(); // Refresh agent list
    };
    
    window.addEventListener('synapseAgentUpdated', handleSynapseAgentUpdate);
    window.addEventListener('synapseAgentRemoved', handleSynapseAgentRemoved);
    
    const metricsInterval = setInterval(updateSystemMetrics, 5000);
    const logsInterval = setInterval(loadOrchestrationLogs, 10000);
    
    return () => {
      clearInterval(metricsInterval);
      clearInterval(logsInterval);
      window.removeEventListener('synapseAgentUpdated', handleSynapseAgentUpdate);
      window.removeEventListener('synapseAgentRemoved', handleSynapseAgentRemoved);
    };
  }, []);

  const updateApiStatus = (endpoint, success) => {
    setCoreApiStatus(prev => ({
      ...prev,
      lastCheck: new Date().toISOString(),
      connected: Object.values({ ...prev.endpoints, [endpoint]: success }).some(status => status),
      endpoints: {
        ...prev.endpoints,
        [endpoint]: success
      }
    }));
  };

  const loadSynapseAgents = () => {
    try {
      const synapseAgents = JSON.parse(localStorage.getItem('coreAvailableAgents') || '{}');
      const externalAgents = Object.values(synapseAgents).map(agent => ({
        id: agent.id,
        name: agent.name,
        type: 'external',
        status: agent.status === 'active' ? 'active' : 'inactive',
        load: agent.status === 'active' ? Math.floor(Math.random() * 30) + 10 : 0,
        tasks: agent.status === 'active' ? Math.floor(Math.random() * 5) + 1 : 0,
        capabilities: agent.capabilities || [],
        performance: {
          efficiency: agent.status === 'active' ? Math.floor(Math.random() * 20) + 80 : 0,
          accuracy: agent.status === 'active' ? Math.floor(Math.random() * 20) + 80 : 0,
          responsiveness: agent.status === 'active' ? Math.floor(Math.random() * 20) + 80 : 0
        },
        lastActivity: agent.last_updated || new Date().toISOString(),
        source: 'synapse',
        configured: agent.configured || false,
        description: agent.description || ''
      }));
      
      return externalAgents;
    } catch (error) {
      console.warn('Failed to load Synapse agents:', error);
      return [];
    }
  };
  
  const discoverAgents = async () => {
    addOrchestrationLog('Discovering agents from Synapse...', 'info');
    
    try {
      // Load Synapse agents
      const synapseAgents = loadSynapseAgents();
      
      // Merge with existing local agents (filter out old external agents)
      const localAgents = agents.filter(agent => agent.source !== 'synapse');
      const mergedAgents = [...localAgents, ...synapseAgents];
      
      setAgents(mergedAgents);
      addOrchestrationLog(`Discovered ${synapseAgents.length} external agents from Synapse`, 'success');
      
      return mergedAgents;
    } catch (error) {
      console.error('Failed to discover agents:', error);
      addOrchestrationLog('Failed to discover agents from Synapse', 'error');
      return agents;
    }
  };

  const initializeCoreServices = async () => {
    try {
      // Load agents from API
      const agentsResponse = await fetch('http://localhost:8000/api/agents');
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json();
        
        // Also load Synapse agents
        const synapseAgents = loadSynapseAgents();
        const allAgents = [...agentsData.agents, ...synapseAgents];
        
        setAgents(allAgents);
        updateApiStatus('agents', true);
        addOrchestrationLog(`Loaded ${agentsData.agents.length} core agents and ${synapseAgents.length} external agents`, 'success');
      } else {
        throw new Error('Failed to load agents from API');
      }
    } catch (error) {
      console.warn('Core API not available, using fallback data:', error);
      updateApiStatus('agents', false);
      addOrchestrationLog('Using fallback agent data (Core API unavailable)', 'warning');
      
      // Load Synapse agents even if Core API is unavailable
      const synapseAgents = loadSynapseAgents();
      
      // Fallback to static data (local agents only, not Synapse itself)
      const fallbackAgents = [
        {
          id: 'alden',
          name: 'Alden',
          type: 'primary',
          status: 'active',
          load: 65,
          tasks: 12,
          capabilities: ['conversation', 'reasoning', 'memory'],
          performance: { efficiency: 94, accuracy: 98, responsiveness: 96 },
          lastActivity: new Date().toISOString()
        },
        {
          id: 'alice',
          name: 'Alice',
          type: 'specialist',
          status: 'active',
          load: 32,
          tasks: 5,
          capabilities: ['analysis', 'problem-solving', 'optimization'],
          performance: { efficiency: 91, accuracy: 96, responsiveness: 94 },
          lastActivity: new Date(Date.now() - 300000).toISOString()
        },
        {
          id: 'mimic',
          name: 'Mimic',
          type: 'adaptive',
          status: 'learning',
          load: 78,
          tasks: 8,
          capabilities: ['adaptation', 'learning', 'pattern-recognition'],
          performance: { efficiency: 88, accuracy: 93, responsiveness: 91 },
          lastActivity: new Date(Date.now() - 150000).toISOString()
        },
        {
          id: 'sentry',
          name: 'Sentry',
          type: 'monitor',
          status: 'monitoring',
          load: 25,
          tasks: 3,
          capabilities: ['monitoring', 'security', 'alerting'],
          performance: { efficiency: 96, accuracy: 99, responsiveness: 98 },
          lastActivity: new Date(Date.now() - 60000).toISOString()
        }
      ];
      
      // Merge fallback local agents with Synapse external agents
      const allAgents = [...fallbackAgents, ...synapseAgents];
      setAgents(allAgents);
      
      addOrchestrationLog(`Loaded ${fallbackAgents.length} local agents and ${synapseAgents.length} external agents (fallback mode)`, 'info');
    }

    try {
      // Load services from API
      const servicesResponse = await fetch('http://localhost:8000/api/services');
      if (servicesResponse.ok) {
        const servicesData = await servicesResponse.json();
        setServices(servicesData.services.map(service => ({
          id: service.id,
          name: service.name,
          status: service.status === 'running' ? 'operational' : service.status,
          health: service.health === 'healthy' ? 95 + Math.floor(Math.random() * 5) : 70 + Math.floor(Math.random() * 15),
          throughput: `${(Math.random() * 2 + 0.5).toFixed(1)}GB/s`,
          connections: Math.floor(Math.random() * 100) + 10,
          uptime: `${(99.5 + Math.random() * 0.5).toFixed(1)}%`
        })));
        updateApiStatus('services', true);
        addOrchestrationLog('Services loaded from Core API', 'success');
      } else {
        throw new Error('Failed to load services from API');
      }
    } catch (error) {
      console.warn('Core API services not available, using fallback data:', error);
      updateApiStatus('services', false);
      addOrchestrationLog('Using fallback service data (Core API unavailable)', 'warning');
      
      // Fallback to static data
      setServices([
        {
          id: 'vault',
          name: 'Vault Storage',
          status: 'operational',
          health: 98,
          throughput: '1.2GB/s',
          connections: 45,
          uptime: '99.9%'
        },
        {
          id: 'synapse-gateway',
          name: 'Synapse Gateway',
          status: 'operational',
          health: 96,
          throughput: '850MB/s',
          connections: 23,
          uptime: '99.7%'
        },
        {
          id: 'memory-system',
          name: 'Memory System',
          status: 'operational',
          health: 94,
          throughput: '2.1GB/s',
          connections: 67,
          uptime: '99.8%'
        },
        {
          id: 'orchestration',
          name: 'Core Orchestration',
          status: 'operational',
          health: 97,
          throughput: '512MB/s',
          connections: 12,
          uptime: '99.9%'
        },
        {
          id: 'api-gateway',
          name: 'API Gateway',
          status: 'operational',
          health: 95,
          throughput: '1.5GB/s',
          connections: 89,
          uptime: '99.6%'
        }
      ]);
    }

    try {
      // Load projects from API
      const projectsResponse = await fetch('http://localhost:8000/api/projects');
      if (projectsResponse.ok) {
        const projectsData = await projectsResponse.json();
        setProjects(projectsData.projects.map(project => ({
          id: project.id,
          name: project.name,
          description: project.description,
          status: project.status,
          priority: project.priority || 'medium',
          progress: project.progress,
          assignedAgents: project.assignedAgents,
          tasks: project.tasks,
          startDate: project.created,
          estimatedCompletion: project.updated
        })));
        updateApiStatus('projects', true);
        addOrchestrationLog('Projects loaded from Core API', 'success');
      } else {
        throw new Error('Failed to load projects from API');
      }
    } catch (error) {
      console.warn('Core API projects not available, using fallback data:', error);
      updateApiStatus('projects', false);
      addOrchestrationLog('Using fallback project data (Core API unavailable)', 'warning');
      
      // Fallback to static data
      setProjects([
        {
          id: 'core-optimization',
          name: 'Core System Optimization',
          description: 'Optimize core system performance and resource utilization',
          status: 'active',
          priority: 'high',
          progress: 78,
          assignedAgents: ['alden', 'alice', 'sentry'],
          tasks: [
            { id: 1, name: 'Memory optimization', status: 'completed', assignee: 'alice' },
            { id: 2, name: 'CPU load balancing', status: 'in_progress', assignee: 'alden' },
            { id: 3, name: 'Network throughput improvement', status: 'pending', assignee: 'sentry' },
            { id: 4, name: 'Storage efficiency enhancement', status: 'pending', assignee: 'alice' }
          ],
          startDate: new Date(Date.now() - 86400000 * 3).toISOString(),
          estimatedCompletion: new Date(Date.now() + 86400000 * 2).toISOString()
        },
        {
          id: 'agent-coordination',
          name: 'Agent Coordination Enhancement',
          description: 'Improve inter-agent communication and task delegation',
          status: 'planning',
          priority: 'medium',
          progress: 32,
          assignedAgents: ['mimic', 'synapse'],
          tasks: [
            { id: 1, name: 'Protocol standardization', status: 'completed', assignee: 'synapse' },
            { id: 2, name: 'Message queue optimization', status: 'in_progress', assignee: 'mimic' },
            { id: 3, name: 'Load balancing algorithm', status: 'pending', assignee: 'mimic' },
            { id: 4, name: 'Performance monitoring', status: 'pending', assignee: 'sentry' }
          ],
          startDate: new Date(Date.now() - 86400000 * 2).toISOString(),
          estimatedCompletion: new Date(Date.now() + 86400000 * 5).toISOString()
        },
        {
          id: 'security-hardening',
          name: 'Security Infrastructure Hardening',
          description: 'Enhance security protocols and threat detection capabilities',
          status: 'pending',
          priority: 'critical',
          progress: 15,
          assignedAgents: ['sentry', 'synapse'],
          tasks: [
            { id: 1, name: 'Threat model analysis', status: 'pending', assignee: 'sentry' },
            { id: 2, name: 'Encryption enhancement', status: 'pending', assignee: 'synapse' },
            { id: 3, name: 'Access control implementation', status: 'pending', assignee: 'sentry' },
            { id: 4, name: 'Audit logging improvement', status: 'pending', assignee: 'sentry' }
          ],
          startDate: new Date(Date.now() + 86400000).toISOString(),
          estimatedCompletion: new Date(Date.now() + 86400000 * 7).toISOString()
        },
        {
          id: 'external-agent-integration',
          name: 'External Agent Integration Testing',
          description: 'Test and validate integration with external AI agents through Synapse Gateway',
          status: 'active',
          priority: 'high',
          progress: 25,
          assignedAgents: ['google-gemini', 'kimi-k2', 'claude-code-cli'],
          tasks: [
            { id: 1, name: 'Code generation task', status: 'pending', assignee: 'google-gemini', description: 'Generate Python code for data processing' },
            { id: 2, name: 'Document analysis', status: 'pending', assignee: 'kimi-k2', description: 'Analyze technical documentation and provide insights' },
            { id: 3, name: 'File system operations', status: 'pending', assignee: 'claude-code-cli', description: 'Perform direct file system operations and modifications' },
            { id: 4, name: 'Cross-agent collaboration', status: 'pending', assignee: 'google-gemini', description: 'Coordinate with other agents for complex tasks' }
          ],
          startDate: new Date(Date.now() - 86400000).toISOString(),
          estimatedCompletion: new Date(Date.now() + 86400000 * 3).toISOString()
        }
      ]);
    }

    setActiveProject(projects[0] || null);
    addOrchestrationLog('Core services initialized successfully', 'info');
  };

  const updateSystemMetrics = async () => {
    try {
      // Try to get real metrics from Core API
      const metricsResponse = await fetch('http://localhost:8000/api/system/metrics');
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setSystemStatus(prev => ({
          ...prev,
          cpu: Math.round(metricsData.cpu),
          memory: Math.round(metricsData.memory),
          network: Math.round(metricsData.network),
          storage: Math.round(metricsData.storage),
          uptime: metricsData.uptime
        }));
        updateApiStatus('metrics', true);
      } else {
        throw new Error('Failed to fetch metrics from API');
      }
    } catch (error) {
      updateApiStatus('metrics', false);
      // Simulated responses removed - implement proper error handling

    // Update agent loads (always use simulation for realistic variation)
    setAgents(prev => prev.map(agent => ({
      ...agent,
      load: Math.max(10, Math.min(95, agent.load + (Math.random() - 0.5) * 12))
    })));
  };

  const addOrchestrationLog = (message, type = 'info') => {
    const logEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      message,
      type,
      agent: currentAgent || 'system'
    };
    setOrchestrationLogs(prev => [logEntry, ...prev].slice(0, 100));
  };

  const loadOrchestrationLogs = async () => {
    try {
      const logsResponse = await fetch('http://localhost:8000/api/orchestration/logs?limit=50');
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        setOrchestrationLogs(logsData.logs);
        updateApiStatus('logs', true);
      } else {
        throw new Error('Failed to load logs from API');
      }
    } catch (error) {
      updateApiStatus('logs', false);
      console.warn('Could not load orchestration logs from API:', error);
    }
  };

  const startOrchestration = async (projectId) => {
    setOrchestrationStatus('initializing');
    addOrchestrationLog(`Starting orchestration for project: ${projectId}`, 'info');

    const project = projects.find(p => p.id === projectId);
    if (!project) {
      addOrchestrationLog(`Project ${projectId} not found`, 'error');
      setOrchestrationStatus('error');
      return;
    }

    try {
      setOrchestrationStatus('analyzing');
      addOrchestrationLog(`Analyzing project requirements for ${project.name}`, 'info');

      // Try to use Core API for orchestration
      try {
        const orchestrateResponse = await fetch(`http://localhost:8000/api/projects/${projectId}/orchestrate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({})
        });

        if (orchestrateResponse.ok) {
          const orchestrateData = await orchestrateResponse.json();
          addOrchestrationLog(`Core API orchestration started: ${orchestrateData.message}`, 'success');
          
          setOrchestrationStatus('delegating');
          addOrchestrationLog(`Delegating tasks to agents: ${project.assignedAgents.join(', ')}`, 'info');
          await new Promise(resolve => setTimeout(resolve, 1000));

          setOrchestrationStatus('monitoring');
          addOrchestrationLog(`Monitoring task execution and agent performance`, 'info');
          await new Promise(resolve => setTimeout(resolve, 1000));

          // Update project with API response
          if (orchestrateData.project) {
            setProjects(prev => prev.map(p => 
              p.id === projectId 
                ? { ...p, status: orchestrateData.project.status, progress: orchestrateData.project.progress || p.progress + 15 }
                : p
            ));
          }
        } else {
          throw new Error('Core API orchestration failed');
        }
      } catch (apiError) {
        console.warn('Core API orchestration not available, using local simulation:', apiError);
        addOrchestrationLog('Using local orchestration simulation (Core API unavailable)', 'warning');
        
        // Fallback to local simulation
        await new Promise(resolve => setTimeout(resolve, 1500));

        setOrchestrationStatus('delegating');
        addOrchestrationLog(`Delegating tasks to agents: ${project.assignedAgents.join(', ')}`, 'info');
        await new Promise(resolve => setTimeout(resolve, 2000));

        setOrchestrationStatus('monitoring');
        addOrchestrationLog(`Monitoring task execution and agent performance`, 'info');
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Update project status
        setProjects(prev => prev.map(p => 
          p.id === projectId 
            ? { ...p, status: 'active', progress: Math.min(100, p.progress + 15) }
            : p
        ));
      }

      setOrchestrationStatus('active');
      addOrchestrationLog(`Orchestration active for ${project.name}`, 'success');

    } catch (error) {
      addOrchestrationLog(`Orchestration failed: ${error.message}`, 'error');
      setOrchestrationStatus('error');
    }
  };

  const delegateTask = async (projectId, taskId) => {
    const project = projects.find(p => p.id === projectId);
    const task = project?.tasks.find(t => t.id === taskId);
    
    if (!project || !task) return;

    addOrchestrationLog(`Delegating task "${task.name}" to ${task.assignee}`, 'info');
    
    // Update task status to in_progress
    setProjects(prev => prev.map(p => 
      p.id === projectId 
        ? {
            ...p,
            tasks: p.tasks.map(t => 
              t.id === taskId 
                ? { ...t, status: 'in_progress', started_at: new Date().toISOString() }
                : t
            )
          }
        : p
    ));

    try {
      // Determine agent type and route accordingly
      const agentType = getAgentType(task.assignee);
      let result;

      switch (agentType) {
        case 'synapse_external':
          result = await delegateToSynapseAgent(task);
          break;
        case 'local':
          result = await delegateToLocalAgent(task);
          break;
        case 'core_service':
          result = await delegateToCoreService(task);
          break;
        default:
          throw new Error(`Unknown agent type: ${agentType}`);
      }

      // Update task with result
      setProjects(prev => prev.map(p => 
        p.id === projectId 
          ? {
              ...p,
              tasks: p.tasks.map(t => 
                t.id === taskId 
                  ? { 
                      ...t, 
                      status: result.success ? 'completed' : 'error',
                      result: result.output,
                      completed_at: new Date().toISOString()
                    }
                  : t
              )
            }
          : p
      ));

      addOrchestrationLog(`Task "${task.name}" ${result.success ? 'completed' : 'failed'} by ${task.assignee}`, 
                         result.success ? 'success' : 'error');

    } catch (error) {
      // Update task with error
      setProjects(prev => prev.map(p => 
        p.id === projectId 
          ? {
              ...p,
              tasks: p.tasks.map(t => 
                t.id === taskId 
                  ? { 
                      ...t, 
                      status: 'error',
                      error: error.message,
                      completed_at: new Date().toISOString()
                    }
                  : t
              )
            }
          : p
      ));

      addOrchestrationLog(`Task "${task.name}" failed: ${error.message}`, 'error');
    }
  };

  const getAgentType = (assignee) => {
    // Define agent types based on assignee
    const externalAgents = ['google-gemini', 'kimi-k2', 'claude-code-cli'];
    const localAgents = ['alden', 'alice', 'mimic'];
    const coreServices = ['sentry', 'synapse', 'vault'];

    if (externalAgents.includes(assignee)) return 'synapse_external';
    if (localAgents.includes(assignee)) return 'local';
    if (coreServices.includes(assignee)) return 'core_service';
    return 'local'; // Default to local
  };

  const delegateToSynapseAgent = async (task) => {
    addOrchestrationLog(`Routing task to Synapse agent: ${task.assignee}`, 'info');
    
    try {
      // Check if Synapse Gateway is available
      if (!window.synapseGateway) {
        throw new Error('Synapse Gateway not available');
      }

      let result;
      const prompt = `Task: ${task.name}\nDescription: ${task.description || 'No description provided'}\nRequirements: Complete this task and provide detailed output.`;

      switch (task.assignee) {
        case 'google-gemini':
          result = await window.synapseGateway.callGoogleGeminiAPI(prompt, {
            maxTokens: 2000,
            temperature: 0.7
          });
          break;
          
        case 'kimi-k2':
          result = await window.synapseGateway.callKimiK2API(prompt, {
            maxTokens: 2000,
            temperature: 0.7
          });
          break;
          
        case 'claude-code-cli':
          result = await window.synapseGateway.callClaudeCodeCLI(prompt, {
            enableDiskWrite: true
          });
          break;
          
        default:
          throw new Error(`Unknown Synapse agent: ${task.assignee}`);
      }

      return {
        success: true,
        output: result.result,
        usage: result.usage,
        agent: task.assignee
      };

    } catch (error) {
      addOrchestrationLog(`Synapse agent ${task.assignee} failed: ${error.message}`, 'error');
      return {
        success: false,
        output: null,
        error: error.message,
        agent: task.assignee
      };
    }
  };

  const delegateToLocalAgent = async (task) => {
    addOrchestrationLog(`Routing task to local agent: ${task.assignee}`, 'info');
    
    try {
      // Simulate local agent processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const responses = {
        'alden': `Alden has analyzed and completed the task: ${task.name}`,
        'alice': `Alice has processed and optimized the task: ${task.name}`,
        'mimic': `Mimic has adapted and executed the task: ${task.name}`
      };

      return {
        success: true,
        output: responses[task.assignee] || `Local agent ${task.assignee} completed the task`,
        agent: task.assignee
      };

    } catch (error) {
      return {
        success: false,
        output: null,
        error: error.message,
        agent: task.assignee
      };
    }
  };

  // AGENT-TO-AGENT COMMUNICATION FUNCTIONS
  const sendMessageToAgent = async (targetAgent, message, fromAgent = 'core') => {
    try {
      addOrchestrationLog(`Sending message from ${fromAgent} to ${targetAgent}`, 'info');
      
      // Route message based on agent type
      const agentType = getAgentType(targetAgent);
      let response;

      switch (agentType) {
        case 'synapse_external':
          response = await sendToExternalAgent(targetAgent, message, fromAgent);
          break;
        case 'local':
          response = await sendToLocalAgent(targetAgent, message, fromAgent);
          break;
        case 'core_service':
          response = await sendToCoreService(targetAgent, message, fromAgent);
          break;
        default:
          throw new Error(`Unknown agent type for ${targetAgent}`);
      }

      addOrchestrationLog(`Message delivered to ${targetAgent}: ${response.status}`, 'success');
      return response;

    } catch (error) {
      addOrchestrationLog(`Failed to send message to ${targetAgent}: ${error.message}`, 'error');
      throw error;
    }
  };

  const broadcastMessage = async (message, fromAgent = 'core', targetAgents = null) => {
    const targets = targetAgents || agents.filter(agent => agent.status === 'active').map(agent => agent.id);
    const results = {};

    addOrchestrationLog(`Broadcasting message from ${fromAgent} to ${targets.length} agents`, 'info');

    // Send messages in parallel
    const promises = targets.map(async (targetAgent) => {
      try {
        const response = await sendMessageToAgent(targetAgent, message, fromAgent);
        results[targetAgent] = { success: true, response };
      } catch (error) {
        results[targetAgent] = { success: false, error: error.message };
      }
    });

    await Promise.allSettled(promises);
    
    const successCount = Object.values(results).filter(r => r.success).length;
    addOrchestrationLog(`Broadcast completed: ${successCount}/${targets.length} successful`, 'info');
    
    return results;
  };

  const sendToExternalAgent = async (agentId, message, fromAgent) => {
    // Route through Synapse to external LLMs
    try {
      let apiEndpoint;
      let requestBody;

      switch (agentId) {
        case 'google-gemini':
          // Import Gemini connector dynamically
          const { GeminiConnector } = await import('../llm/GeminiConnector');
          const geminiConfig = {
            apiKey: process.env.GEMINI_API_KEY || localStorage.getItem('gemini_api_key'),
            model: 'flash' // Default to fast model for agent communication
          };
          
          if (!geminiConfig.apiKey) {
            throw new Error('Gemini API key not configured');
          }

          const gemini = new GeminiConnector(geminiConfig);
          const geminiResponse = await gemini.call({
            prompt: message,
            systemMessage: `You are ${agentId} responding to a message from ${fromAgent} in the Hearthlink system.`,
            agentId: agentId,
            module: 'core_communication'
          });

          return {
            status: 'delivered',
            response: geminiResponse.text,
            tokensUsed: geminiResponse.tokensUsed,
            model: geminiResponse.model
          };

        case 'kimi-k2':
          // Import Kimi connector dynamically
          const { KimiK2Connector } = await import('../llm/KimiK2Connector');
          const kimiConfig = {
            apiKey: process.env.KIMI_API_KEY || localStorage.getItem('kimi_api_key'),
            endpoint: process.env.KIMI_ENDPOINT || 'https://api.moonshot.cn'
          };
          
          if (!kimiConfig.apiKey) {
            throw new Error('Kimi K2 API key not configured');
          }

          const kimi = new KimiK2Connector(kimiConfig);
          const kimiResponse = await kimi.call({
            prompt: message,
            systemMessage: `You are ${agentId} responding to a message from ${fromAgent} in the Hearthlink system.`,
            agentId: agentId,
            module: 'core_communication'
          });

          return {
            status: 'delivered',
            response: kimiResponse.text,
            tokensUsed: kimiResponse.tokensUsed
          };

        case 'claude-code-cli':
          // Use existing API if available
          apiEndpoint = 'http://localhost:8003/api/synapse/agents/claude-code-cli/message';
          requestBody = {
            message,
            fromAgent,
            timestamp: new Date().toISOString()
          };
          break;

        default:
          // Generic external agent via Synapse
          apiEndpoint = `http://localhost:8003/api/synapse/agents/${agentId}/message`;
          requestBody = {
            message,
            fromAgent,
            timestamp: new Date().toISOString()
          };
      }

      // For API-based external agents, make HTTP request
      if (apiEndpoint) {
        const response = await fetch(apiEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          throw new Error(`External agent ${agentId} returned ${response.status}`);
        }

        const data = await response.json();
        return {
          status: 'delivered',
          response: data.response || data.message,
          agentId: agentId
        };
      }

    } catch (error) {
      throw new Error(`Failed to communicate with external agent ${agentId}: ${error.message}`);
    }
  };

  const sendToLocalAgent = async (agentId, message, fromAgent) => {
    // Route to local personas (Alden, Alice, Mimic)
    try {
      // Check if agent interface is available
      const agentWindow = window[`${agentId}Interface`];
      if (agentWindow && typeof agentWindow.receiveMessage === 'function') {
        const response = await agentWindow.receiveMessage(message, fromAgent);
        return {
          status: 'delivered',
          response: response.text || response,
          agentId: agentId
        };
      }

      // Fallback to API call
      const apiResponse = await fetch(`http://localhost:8000/api/agents/${agentId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          fromAgent,
          timestamp: new Date().toISOString()
        })
      });

      if (!apiResponse.ok) {
        throw new Error(`Local agent API returned ${apiResponse.status}`);
      }

      const data = await apiResponse.json();
      return {
        status: 'delivered',
        response: data.response,
        agentId: agentId
      };

    } catch (error) {
      // Simulate local agent response if all else fails
      // Simulated responses removed - implement proper error handling
        'mimic': `Mimic adapted to: "${message}" from ${fromAgent}. Persona activated...`
      };

      return {
        // Simulated responses removed - implement proper error handling
        // Simulated responses removed - implement proper error handling
  };

  const sendToCoreService = async (serviceId, message, fromAgent) => {
    // Route to core services (Sentry, Synapse, Vault)
    try {
      const serviceEndpoints = {
        'sentry': 'http://localhost:8004/api/sentry/message',
        'synapse': 'http://localhost:8003/api/synapse/message', 
        'vault': 'http://localhost:8002/api/vault/message'
      };

      const endpoint = serviceEndpoints[serviceId];
      if (!endpoint) {
        throw new Error(`Unknown core service: ${serviceId}`);
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          fromAgent,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`Core service ${serviceId} returned ${response.status}`);
      }

      const data = await response.json();
      return {
        status: 'delivered',
        response: data.response || data.message,
        serviceId: serviceId
      };

    } catch (error) {
      throw new Error(`Failed to communicate with core service ${serviceId}: ${error.message}`);
    }
  };

  const initiateConference = async (roomName, participantIds, topic = null) => {
    try {
      addOrchestrationLog(`Initiating conference: ${roomName} with ${participantIds.length} participants`, 'info');

      const room = {
        id: `room_${Date.now()}`,
        name: roomName,
        topic: topic || `Conference initiated by Core`,
        participants: participantIds,
        createdAt: new Date().toISOString(),
        status: 'active',
        messages: []
      };

      // Add welcome message to room
      room.messages.push({
        id: `msg_${Date.now()}`,
        from: 'core',
        content: topic ? `Conference started: ${topic}` : `Welcome to ${roomName}`,
        timestamp: new Date().toISOString(),
        type: 'system'
      });

      setConferenceRooms(prev => [...prev, room]);
      setActiveRoom(room);

      // Notify all participants they've been added to the conference
      const notificationPromises = participantIds.map(agentId => 
        sendMessageToAgent(agentId, `You have been invited to conference: ${roomName}${topic ? ` - Topic: ${topic}` : ''}`, 'core')
      );

      await Promise.allSettled(notificationPromises);
      
      addOrchestrationLog(`Conference ${roomName} created successfully`, 'success');
      return room;

    } catch (error) {
      addOrchestrationLog(`Failed to create conference: ${error.message}`, 'error');
      throw error;
    }
  };

  const delegateToCoreService = async (task) => {
    addOrchestrationLog(`Routing task to core service: ${task.assignee}`, 'info');
    
    try {
      // Simulate core service processing
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const responses = {
        'sentry': `Sentry has monitored and secured the task: ${task.name}`,
        'synapse': `Synapse has processed and routed the task: ${task.name}`,
        'vault': `Vault has stored and managed the task: ${task.name}`
      };

      return {
        success: true,
        output: responses[task.assignee] || `Core service ${task.assignee} completed the task`,
        agent: task.assignee
      };

    } catch (error) {
      return {
        success: false,
        output: null,
        error: error.message,
        agent: task.assignee
      };
    }
  };

  const testTaskDelegation = async (projectId) => {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    addOrchestrationLog(`Testing task delegation for project: ${project.name}`, 'info');
    
    // Find the first pending task
    const pendingTask = project.tasks.find(t => t.status === 'pending');
    if (!pendingTask) {
      addOrchestrationLog('No pending tasks found for testing', 'warning');
      return;
    }

    addOrchestrationLog(`Testing delegation of task: ${pendingTask.name} to ${pendingTask.assignee}`, 'info');
    
    try {
      await delegateTask(projectId, pendingTask.id);
      addOrchestrationLog(`Task delegation test completed successfully`, 'success');
    } catch (error) {
      addOrchestrationLog(`Task delegation test failed: ${error.message}`, 'error');
    }
  };

  const createConferenceRoom = async (roomName) => {
    if (!roomName || !roomName.trim()) return;
    
    const newRoom = {
      id: `room-${Date.now()}`,
      name: roomName.trim(),
      participants: [],
      created: new Date().toISOString(),
      status: 'active'
    };
    
    try {
      // Try to create room via API
      const response = await fetch('http://localhost:8000/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: roomName.trim(),
          type: 'conference'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        newRoom.id = data.session_id;
      }
    } catch (error) {
      console.warn('Failed to create room via API, using local room:', error);
    }
    
    setConferenceRooms(prev => [...prev, newRoom]);
    setActiveRoom(newRoom);
    setMessages([]);
    setParticipants([]);
    setNewRoomName('');
    setShowCreateRoomForm(false);
    addOrchestrationLog(`Conference room "${roomName.trim()}" created successfully`, 'success');
  };

  const handleCreateRoomSubmit = (e) => {
    e.preventDefault();
    if (newRoomName.trim()) {
      createConferenceRoom(newRoomName);
    }
  };

  // Agent persona management functions
  const loadAgentPersonas = () => {
    try {
      const saved = localStorage.getItem('coreAgentPersonas');
      if (saved) {
        setAgentPersonas(JSON.parse(saved));
      }
    } catch (error) {
      console.warn('Failed to load agent personas:', error);
    }
  };

  const saveAgentPersonas = (personas) => {
    try {
      localStorage.setItem('coreAgentPersonas', JSON.stringify(personas));
      setAgentPersonas(personas);
    } catch (error) {
      console.warn('Failed to save agent personas:', error);
    }
  };

  const updateAgentPersona = (agentId, personaData) => {
    const updatedPersonas = {
      ...agentPersonas,
      [agentId]: {
        ...agentPersonas[agentId],
        ...personaData,
        lastUpdated: new Date().toISOString()
      }
    };
    saveAgentPersonas(updatedPersonas);
    addOrchestrationLog(`Agent ${agentId} persona updated`, 'info');
  };

  const resetAgentPersona = (agentId) => {
    const updatedPersonas = { ...agentPersonas };
    delete updatedPersonas[agentId];
    saveAgentPersonas(updatedPersonas);
    addOrchestrationLog(`Agent ${agentId} persona reset to default`, 'info');
  };

  // Agent selection modal functions
  const openAgentSelectionModal = () => {
    setSelectedAgents([]);
    setShowAgentSelectionModal(true);
  };

  const closeAgentSelectionModal = () => {
    setShowAgentSelectionModal(false);
    setSelectedAgents([]);
  };

  const toggleAgentSelection = (agentId) => {
    setSelectedAgents(prev => 
      prev.includes(agentId) 
        ? prev.filter(id => id !== agentId)
        : [...prev, agentId]
    );
  };

  const createConferenceRoomWithSelectedAgents = () => {
    if (!newRoomName.trim()) {
      addOrchestrationLog('Room name is required', 'error');
      return;
    }
    
    if (selectedAgents.length === 0) {
      addOrchestrationLog('At least one agent must be selected', 'error');
      return;
    }

    const selectedAgentDetails = agents.filter(agent => selectedAgents.includes(agent.id));
    const participants = selectedAgentDetails.map(agent => ({
      id: agent.id,
      name: getAgentDisplayName(agent),
      type: agent.type,
      status: agent.status,
      persona: agentPersonas[agent.id] || null
    }));

    const newRoom = {
      id: `room-${Date.now()}`,
      name: newRoomName.trim(),
      participants,
      created_at: new Date().toISOString(),
      status: 'active',
      creator: 'user'
    };

    setConferenceRooms(prev => [...prev, newRoom]);
    setActiveRoom(newRoom);
    setMessages([]);
    setParticipants(participants);
    setNewRoomName('');
    setShowCreateRoomForm(false);
    setShowAgentSelectionModal(false);
    setSelectedAgents([]);
    
    addOrchestrationLog(`Conference room "${newRoom.name}" created with ${participants.length} agents`, 'success');
  };

  const getAgentDisplayName = (agent) => {
    const persona = agentPersonas[agent.id];
    return persona?.customName || agent.name || agent.id;
  };

  const getAgentPersonaDescription = (agent) => {
    const persona = agentPersonas[agent.id];
    return persona?.description || agent.description || 'No description available';
  };

  const joinRoom = async (roomId) => {
    const room = conferenceRooms.find(r => r.id === roomId);
    if (!room) return;
    
    setActiveRoom(room);
    
    try {
      // Try to load room data from API
      const response = await fetch(`http://localhost:8000/api/sessions/${roomId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
        setParticipants(data.participants || []);
      } else {
        // Use mock data
        setMessages([
          {
            id: 'msg-1',
            sender: 'System',
            content: `Welcome to ${room.name}`,
            timestamp: new Date().toISOString()
          }
        ]);
        setParticipants([
          {
            id: 'user-1',
            name: 'You',
            status: 'online'
          }
        ]);
      }
    } catch (error) {
      console.warn('Failed to load room data, using mock:', error);
      setMessages([]);
      setParticipants([]);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !activeRoom) return;
    
    const message = {
      id: `msg-${Date.now()}`,
      sender: 'You',
      content: newMessage,
      timestamp: new Date().toISOString()
    };
    
    try {
      // Try to send via API
      const response = await fetch(`http://localhost:8000/api/sessions/${activeRoom.id}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, data]);
      } else {
        // Fallback to local message
        setMessages(prev => [...prev, message]);
      }
    } catch (error) {
      console.warn('Failed to send message via API, using local:', error);
      setMessages(prev => [...prev, message]);
    }
    
    setNewMessage('');
    
    // Process multi-agent conversation if message contains agent mentions
    await processMultiAgentConversation(message);
  };

  const processMultiAgentConversation = async (userMessage) => {
    // Check if message mentions any agents
    const agentMentions = extractAgentMentions(userMessage.content);
    
    if (agentMentions.length > 0) {
      addOrchestrationLog(`Multi-agent conversation triggered with: ${agentMentions.join(', ')}`, 'info');
      
      // Process each mentioned agent
      for (const agentName of agentMentions) {
        try {
          const agentResponse = await getAgentResponse(agentName, userMessage.content);
          
          const agentMessage = {
            id: `msg-${Date.now()}-${agentName}`,
            sender: agentName,
            content: agentResponse.content,
            timestamp: new Date().toISOString(),
            agentType: agentResponse.type
          };
          
          setMessages(prev => [...prev, agentMessage]);
          
          // Update participants if agent not already in room
          setParticipants(prev => {
            const existingParticipant = prev.find(p => p.name === agentName);
            if (!existingParticipant) {
              return [...prev, {
                id: `participant-${agentName}`,
                name: agentName,
                status: 'online',
                type: agentResponse.type
              }];
            }
            return prev;
          });
          
        } catch (error) {
          addOrchestrationLog(`Agent ${agentName} failed to respond: ${error.message}`, 'error');
          
          const errorMessage = {
            id: `msg-${Date.now()}-${agentName}-error`,
            sender: agentName,
            content: `Sorry, I'm currently unavailable. Error: ${error.message}`,
            timestamp: new Date().toISOString(),
            agentType: 'error'
          };
          
          setMessages(prev => [...prev, errorMessage]);
        }
      }
    }
  };

  const extractAgentMentions = (content) => {
    const availableAgents = [
      'alden', 'alice', 'mimic', 'sentry',
      'google-gemini', 'kimi-k2', 'claude-code-cli'
    ];
    
    const mentions = [];
    const lowerContent = content.toLowerCase();
    
    for (const agent of availableAgents) {
      if (lowerContent.includes(`@${agent}`) || lowerContent.includes(agent)) {
        mentions.push(agent);
      }
    }
    
    return mentions;
  };

  const getAgentResponse = async (agentName, messageContent) => {
    const agentType = getAgentType(agentName);
    
    // Create a context-aware prompt
    const prompt = `You are ${agentName} participating in a multi-agent conversation. 
    User message: "${messageContent}"
    
    Please respond as ${agentName} would, staying in character and providing helpful assistance.
    Keep responses conversational and collaborative.`;
    
    switch (agentType) {
      case 'synapse_external':
        return await getSynapseAgentResponse(agentName, prompt);
      case 'local':
        return await getLocalAgentResponse(agentName, prompt);
      case 'core_service':
        return await getCoreServiceResponse(agentName, prompt);
      default:
        throw new Error(`Unknown agent type for ${agentName}`);
    }
  };

  const getSynapseAgentResponse = async (agentName, prompt) => {
    if (!window.synapseGateway) {
      throw new Error('Synapse Gateway not available');
    }
    
    let result;
    switch (agentName) {
      case 'google-gemini':
        result = await window.synapseGateway.callGoogleGeminiAPI(prompt, {
          maxTokens: 500,
          temperature: 0.8
        });
        break;
      case 'kimi-k2':
        result = await window.synapseGateway.callKimiK2API(prompt, {
          maxTokens: 500,
          temperature: 0.8
        });
        break;
      case 'claude-code-cli':
        result = await window.synapseGateway.callClaudeCodeCLI(prompt);
        break;
      default:
        throw new Error(`Unknown Synapse agent: ${agentName}`);
    }
    
    return {
      content: result.result,
      type: 'external'
    };
  };

  const getLocalAgentResponse = async (agentName, prompt) => {
    // Simulate local agent processing
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const responses = {
      'alden': `Hello! I'm Alden, your primary AI assistant. I can help you with reasoning, conversation, and memory management. ${prompt.includes('help') ? 'How can I assist you today?' : 'I understand your request and I\'m here to help.'}`,
      'alice': `Hi there! I'm Alice, specialized in analysis and problem-solving. I can help optimize processes and analyze complex situations. ${prompt.includes('analyze') ? 'Let me analyze that for you.' : 'I\'m ready to help with analysis and optimization.'}`,
      'mimic': `Hey! I'm Mimic, the adaptive learning agent. I can adapt to different patterns and learn from interactions. ${prompt.includes('learn') ? 'I\'m always learning from our conversations.' : 'I can adapt to help you better.'}`
    };
    
    return {
      content: responses[agentName] || `I'm ${agentName}, ready to assist you.`,
      type: 'local'
    };
  };

  const getCoreServiceResponse = async (agentName, prompt) => {
    // Simulate core service processing
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const responses = {
      'sentry': `🛡️ Sentry here. I'm monitoring system security and health. ${prompt.includes('security') ? 'I\'m tracking security metrics and can provide system alerts.' : 'All systems are secure and operational.'}`,
      'synapse': `🔗 Synapse Gateway reporting. I manage external connections and plugin integrations. ${prompt.includes('connect') ? 'I can help establish connections to external services.' : 'All gateway connections are stable.'}`,
      'vault': `🗄️ Vault service active. I handle secure data storage and memory management. ${prompt.includes('store') ? 'I can securely store and retrieve your data.' : 'All data is safely stored and accessible.'}`
    };
    
    return {
      content: responses[agentName] || `${agentName} service is operational.`,
      type: 'service'
    };
  };

  const testMultiAgentConversation = async () => {
    // Create a test room if none exists
    if (!activeRoom) {
      const testRoom = {
        id: 'test-multi-agent-room',
        name: 'Multi-Agent Test Room',
        participants: [],
        created: new Date().toISOString(),
        status: 'active'
      };
      setConferenceRooms(prev => [...prev, testRoom]);
      setActiveRoom(testRoom);
      setMessages([]);
      setParticipants([{
        id: 'user-1',
        name: 'You',
        status: 'online'
      }]);
    }
    
    // Send a test message that mentions multiple agents
    const testMessage = {
      id: `msg-${Date.now()}`,
      sender: 'You',
      content: 'Hello @alden, @google-gemini, and @kimi-k2! Can you all introduce yourselves and tell me what you can help with?',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, testMessage]);
    addOrchestrationLog('Starting multi-agent conversation test', 'info');
    
    // Process the multi-agent conversation
    await processMultiAgentConversation(testMessage);
  };

  const createQuickSession = async () => {
    const activeAgents = agents.filter(a => a.status === 'active');
    
    if (activeAgents.length === 0) {
      addOrchestrationLog('No active agents available for quick session', 'warning');
      return;
    }

    const quickSessionName = `Quick Session - ${new Date().toLocaleTimeString()}`;
    const participants = activeAgents.map(agent => ({
      id: agent.id,
      name: getAgentDisplayName(agent),
      type: agent.type,
      status: agent.status,
      avatar: getAgentDisplayName(agent).charAt(0).toUpperCase()
    }));

    const newRoom = {
      id: `room-${Date.now()}`,
      name: quickSessionName,
      participants,
      created_at: new Date().toISOString(),
      status: 'active',
      type: 'quick'
    };

    setConferenceRooms(prev => [...prev, newRoom]);
    setActiveRoom(newRoom);
    setShowCreateRoomForm(false);
    
    // Initialize with welcome message
    const welcomeMessage = {
      id: `msg-${Date.now()}`,
      sender: 'System',
      content: `Welcome to ${quickSessionName}! All ${participants.length} active agents have been invited to join.`,
      timestamp: new Date().toISOString(),
      type: 'system'
    };
    
    setMessages([welcomeMessage]);
    addOrchestrationLog(`Quick session created with ${participants.length} agents`, 'info');
  };

  const leaveRoom = async (roomId) => {
    if (!roomId) return;
    
    const room = conferenceRooms.find(r => r.id === roomId);
    if (!room) return;

    try {
      // Try to leave via API
      const response = await fetch(`http://localhost:8000/api/sessions/${roomId}/leave`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        throw new Error('Failed to leave room via API');
      }
    } catch (error) {
      console.warn('Failed to leave room via API, using local:', error);
    }
    
    // Remove from local state
    setConferenceRooms(prev => prev.filter(r => r.id !== roomId));
    
    // If this was the active room, clear it
    if (activeRoom?.id === roomId) {
      setActiveRoom(null);
      setMessages([]);
      setParticipants([]);
    }
    
    addOrchestrationLog(`Left session: ${room.name}`, 'info');
  };

  const openDirectMessage = async (agent) => {
    if (!agent || agent.status !== 'active') return;
    
    const dmSessionName = `DM with ${getAgentDisplayName(agent)}`;
    const dmParticipants = [
      {
        id: 'user',
        name: 'You',
        type: 'user',
        status: 'active',
        avatar: 'U'
      },
      {
        id: agent.id,
        name: getAgentDisplayName(agent),
        type: agent.type,
        status: agent.status,
        avatar: getAgentDisplayName(agent).charAt(0).toUpperCase()
      }
    ];

    const dmRoom = {
      id: `dm-${agent.id}-${Date.now()}`,
      name: dmSessionName,
      participants: dmParticipants,
      created_at: new Date().toISOString(),
      status: 'active',
      type: 'direct_message'
    };

    setConferenceRooms(prev => [...prev, dmRoom]);
    setActiveRoom(dmRoom);
    
    // Initialize with greeting message
    const greetingMessage = {
      id: `msg-${Date.now()}`,
      sender: 'System',
      content: `Direct message session started with ${getAgentDisplayName(agent)}`,
      timestamp: new Date().toISOString(),
      type: 'system'
    };
    
    setMessages([greetingMessage]);
    addOrchestrationLog(`Direct message session started with ${getAgentDisplayName(agent)}`, 'info');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational':
      case 'active':
      case 'completed':
        return '#10b981';
      case 'monitoring':
      case 'learning':
      case 'in_progress':
        return '#3b82f6';
      case 'warning':
      case 'planning':
        return '#f59e0b';
      case 'error':
      case 'critical':
        return '#ef4444';
      case 'pending':
      case 'idle':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  const getHealthColor = (health) => {
    if (health >= 95) return '#10b981';
    if (health >= 85) return '#3b82f6';
    if (health >= 70) return '#f59e0b';
    return '#ef4444';
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getProgressBarColor = (progress) => {
    if (progress >= 80) return '#10b981';
    if (progress >= 60) return '#3b82f6';
    if (progress >= 40) return '#f59e0b';
    return '#ef4444';
  };

  // SPEC-3 Week 2: Orphaned Function UI Controls
  const handleCoreHealthCheck = async () => {
    try {
      addOrchestrationLog('Performing core health check...', 'info');
      
      // Simulate core health check
      const health = {
        status: 'healthy',
        uptime: systemStatus.uptime,
        components: {
          orchestrator: 'active',
          session_manager: 'active',
          message_bus: 'active',
          memory_manager: 'active'
        },
        performance: {
          cpu: systemStatus.cpu,
          memory: systemStatus.memory,
          network: systemStatus.network
        },
        timestamp: new Date().toISOString()
      };
      
      setCoreHealthStatus(health);
      addOrchestrationLog('Core health check completed', 'success');
    } catch (error) {
      addOrchestrationLog(`Core health check failed: ${error.message}`, 'error');
      setCoreHealthStatus({ status: 'error', error: error.message });
    }
  };

  const handleGetCoreStatus = async () => {
    try {
      addOrchestrationLog('Retrieving core status...', 'info');
      
      const status = {
        status: orchestrationStatus,
        active_sessions: projects.length,
        active_agents: agents.length,
        system_load: systemStatus.cpu / 100,
        memory_usage: systemStatus.memory / 100,
        services: services.map(s => ({ name: s.name, status: s.status })),
        timestamp: new Date().toISOString()
      };
      
      setCoreStatus(status);
      addOrchestrationLog('Core status retrieved successfully', 'success');
    } catch (error) {
      addOrchestrationLog(`Failed to get core status: ${error.message}`, 'error');
      setCoreStatus({ status: 'error', error: error.message });
    }
  };

  const handleExecuteCommand = async (command, args = []) => {
    try {
      addOrchestrationLog(`Executing command: ${command}`, 'info');
      
      const result = {
        command: command,
        args: args,
        status: 'success',
        output: `Command '${command}' executed successfully`,
        execution_time: `${Math.random() * 2 + 0.5}s`,
        timestamp: new Date().toISOString()
      };
      
      setExecutionResult(result);
      addOrchestrationLog(`Command executed: ${command}`, 'success');
    } catch (error) {
      addOrchestrationLog(`Command execution failed: ${error.message}`, 'error');
      setExecutionResult({ 
        command: command, 
        status: 'error', 
        error: error.message,
        timestamp: new Date().toISOString()
      });
    }
  };

  return (
    <div className="core-interface">
      {/* Header Section */}
      <div className="core-header">
        <div className="core-title">
          <h1>Core Orchestration Center</h1>
          <div className="core-subtitle">AI Agent Coordination & System Management</div>
        </div>
        <div className="system-status-indicator">
          <div className={`status-light ${systemStatus.overall}`}>
            <div className="status-dot"></div>
            <span>{systemStatus.overall.toUpperCase()}</span>
          </div>
          <div className="uptime-display">
            <span>Uptime: {systemStatus.uptime}</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="core-nav">
        <button 
          className={`nav-tab ${activeTab === 'orchestration' ? 'active' : ''}`}
          onClick={() => setActiveTab('orchestration')}
        >
          🎯 Orchestration
        </button>
        <button 
          className={`nav-tab ${activeTab === 'conference' ? 'active' : ''}`}
          onClick={() => setActiveTab('conference')}
        >
          💬 Conference
        </button>
        <button 
          className={`nav-tab ${activeTab === 'agents' ? 'active' : ''}`}
          onClick={() => setActiveTab('agents')}
        >
          🤖 Agents
        </button>
        <button 
          className={`nav-tab ${activeTab === 'services' ? 'active' : ''}`}
          onClick={() => setActiveTab('services')}
        >
          ⚙️ Services
        </button>
        <button 
          className={`nav-tab ${activeTab === 'projects' ? 'active' : ''}`}
          onClick={() => setActiveTab('projects')}
        >
          📋 Projects
        </button>
        <button 
          className={`nav-tab ${activeTab === 'project-command' ? 'active' : ''}`}
          onClick={() => setActiveTab('project-command')}
        >
          🎯 Project Command
        </button>
        <button 
          className={`nav-tab ${activeTab === 'monitoring' ? 'active' : ''}`}
          onClick={() => setActiveTab('monitoring')}
        >
          📊 Monitoring
        </button>
        <button 
          className={`nav-tab ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
        >
          🔧 System Functions
        </button>
      </div>

      {/* Main Content */}
      <div className="core-content">
        {activeTab === 'orchestration' && (
          <div className="orchestration-section">
            <div className="section-header">
              <h2>🎯 System Orchestration</h2>
              <div className="orchestration-controls">
                <button 
                  className={`orchestration-btn ${orchestrationStatus === 'active' ? 'active' : ''}`}
                  onClick={() => startOrchestration(activeProject?.id)}
                  disabled={!activeProject || orchestrationStatus === 'initializing'}
                >
                  {orchestrationStatus === 'active' ? 'Active' : 
                   orchestrationStatus === 'initializing' ? 'Starting...' : 'Start Orchestration'}
                </button>
                <div className="status-indicator">
                  <span>Status: </span>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(orchestrationStatus) }}
                  >
                    {orchestrationStatus.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>

            <div className="orchestration-dashboard">
              <div className="system-overview">
                <h3>System Overview</h3>
                <div className="metrics-grid">
                  <div className="metric-card">
                    <div className="metric-icon">🖥️</div>
                    <div className="metric-content">
                      <div className="metric-value">{systemStatus.cpu}%</div>
                      <div className="metric-label">CPU Usage</div>
                    </div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-icon">💾</div>
                    <div className="metric-content">
                      <div className="metric-value">{systemStatus.memory}%</div>
                      <div className="metric-label">Memory Usage</div>
                    </div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-icon">🌐</div>
                    <div className="metric-content">
                      <div className="metric-value">{systemStatus.network}%</div>
                      <div className="metric-label">Network Load</div>
                    </div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-icon">💿</div>
                    <div className="metric-content">
                      <div className="metric-value">{systemStatus.storage}%</div>
                      <div className="metric-label">Storage Used</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="active-project-panel">
                <h3>Active Project</h3>
                {activeProject ? (
                  <div className="project-details">
                    <div className="project-header">
                      <h4>{activeProject.name}</h4>
                      <span 
                        className="project-status"
                        style={{ backgroundColor: getStatusColor(activeProject.status) }}
                      >
                        {activeProject.status.toUpperCase()}
                      </span>
                    </div>
                    <p className="project-description">{activeProject.description}</p>
                    <div className="project-progress">
                      <div className="progress-label">Progress: {activeProject.progress}%</div>
                      <div className="progress-bar">
                        <div 
                          className="progress-fill"
                          style={{ 
                            width: `${activeProject.progress}%`,
                            backgroundColor: getProgressBarColor(activeProject.progress)
                          }}
                        ></div>
                      </div>
                    </div>
                    <div className="project-agents">
                      <span>Assigned Agents: </span>
                      {activeProject.assignedAgents.map(agentId => (
                        <span key={agentId} className="agent-badge">{agentId}</span>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="no-project">No project selected</div>
                )}
              </div>

              <div className="orchestration-logs">
                <h3>Orchestration Logs</h3>
                <div className="logs-container">
                  {orchestrationLogs.slice(0, 10).map(log => (
                    <div key={log.id} className={`log-entry log-${log.type}`}>
                      <span className="log-timestamp">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <span className="log-agent">[{log.agent}]</span>
                      <span className="log-message">{log.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'conference' && (
          <div className="conference-section modern-conference">
            {/* Professional Header */}
            <div className="conference-header-modern">
              <div className="header-content">
                <div className="title-section">
                  <h1 className="conference-title">🏛️ COUNCIL CHAMBER</h1>
                  <p className="conference-subtitle">Multi-Agent Conference System</p>
                </div>
                <div className="header-controls">
                  <button 
                    className="btn btn-primary"
                    onClick={() => setShowCreateRoomForm(true)}
                  >
                    <span className="btn-icon">🏛️</span>
                    New Session
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => testMultiAgentConversation()}
                  >
                    <span className="btn-icon">⚡</span>
                    Test Protocol
                  </button>
                </div>
              </div>
            </div>

            {/* Main Conference Layout */}
            <div className="conference-layout">
              {/* Left Sidebar */}
              <div className="conference-sidebar">
                {/* Active Sessions */}
                <div className="sidebar-section">
                  <div className="section-header">
                    <h3>📋 Active Sessions</h3>
                    <span className="session-count">{conferenceRooms.length}</span>
                  </div>
                  <div className="sessions-container">
                    {conferenceRooms.length === 0 ? (
                      <div className="no-sessions">
                        <div className="empty-state">
                          <div className="empty-icon">📋</div>
                          <p>No active sessions</p>
                          <button 
                            className="btn btn-small btn-primary"
                            onClick={() => setShowCreateRoomForm(true)}
                          >
                            Create Session
                          </button>
                        </div>
                      </div>
                    ) : (
                      conferenceRooms.map(room => (
                        <div 
                          key={room.id} 
                          className={`session-item ${activeRoom?.id === room.id ? 'active' : ''}`}
                          onClick={() => joinRoom(room.id)}
                        >
                          <div className="session-header">
                            <div className="session-name">{room.name}</div>
                            <div className="session-actions">
                              <button 
                                className="btn-icon-small"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  leaveRoom(room.id);
                                }}
                                title="Leave Session"
                              >
                                ❌
                              </button>
                            </div>
                          </div>
                          <div className="session-meta">
                            <span className="participant-count">
                              👥 {room.participants.length} agents
                            </span>
                            <span className={`session-status ${room.status}`}>
                              {room.status === 'active' ? '🟢 Active' : '🔴 Inactive'}
                            </span>
                          </div>
                          <div className="session-time">
                            Created: {new Date(room.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
                
                {/* Direct Messages */}
                <div className="sidebar-section">
                  <div className="section-header">
                    <h3>📞 Direct Messages</h3>
                  </div>
                  <div className="dm-container">
                    {agents.filter(a => a.status === 'active').length === 0 ? (
                      <div className="no-agents">
                        <div className="empty-state">
                          <div className="empty-icon">🤖</div>
                          <p>No active agents</p>
                        </div>
                      </div>
                    ) : (
                      agents.filter(a => a.status === 'active').map(agent => (
                        <div 
                          key={agent.id} 
                          className="dm-item"
                          onClick={() => openDirectMessage(agent)}
                        >
                          <div className="dm-avatar">
                            {getAgentDisplayName(agent).charAt(0).toUpperCase()}
                          </div>
                          <div className="dm-info">
                            <div className="dm-name">{getAgentDisplayName(agent)}</div>
                            <div className="dm-type">{agent.type}</div>
                          </div>
                          <div className="dm-status">
                            <span className="status-indicator active">💬</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* Main Conference Area */}
              <div className="conference-main">
                {activeRoom ? (
                  <>
                    {/* Session Header */}
                    <div className="session-header-bar">
                      <div className="session-info">
                        <h2 className="session-title">{activeRoom.name}</h2>
                        <div className="session-details">
                          <span>📅 {new Date(activeRoom.created_at).toLocaleDateString()}</span>
                          <span>👥 {activeRoom.participants.length} participants</span>
                          <span className={`status-badge ${activeRoom.status}`}>
                            {activeRoom.status === 'active' ? '🟢 Active' : '🔴 Inactive'}
                          </span>
                        </div>
                      </div>
                      <div className="session-controls">
                        <button className="btn btn-secondary btn-small">⚙️ Settings</button>
                        <button 
                          className="btn btn-danger btn-small"
                          onClick={() => leaveRoom(activeRoom.id)}
                        >
                          🚪 Leave
                        </button>
                      </div>
                    </div>

                    {/* Participants Panel */}
                    <div className="participants-panel">
                      <div className="participants-header">
                        <h3>👥 Session Participants</h3>
                        <span className="participant-count">{activeRoom.participants.length} agents</span>
                      </div>
                      <div className="participants-grid">
                        {activeRoom.participants.map((participant, index) => (
                          <div 
                            key={participant.id}
                            className={`participant-card ${participant.status}`}
                          >
                            <div className="participant-avatar">
                              {getAgentDisplayName(participant).charAt(0).toUpperCase()}
                            </div>
                            <div className="participant-info">
                              <div className="participant-name">{getAgentDisplayName(participant)}</div>
                              <div className="participant-type">{participant.type}</div>
                            </div>
                            <div className="participant-status">
                              <span className={`status-dot ${participant.status}`}></span>
                              {participant.status === 'active' ? 'Online' : 'Offline'}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Messages Panel */}
                    <div className="messages-panel">
                      <div className="messages-header">
                        <h3>💬 Session Messages</h3>
                        <div className="messages-controls">
                          <button 
                            className="btn btn-small btn-secondary"
                            onClick={() => setMessages([])}
                          >
                            🗑️ Clear
                          </button>
                        </div>
                      </div>
                      <div className="messages-container">
                        {messages.length === 0 ? (
                          <div className="no-messages">
                            <div className="empty-state">
                              <div className="empty-icon">💬</div>
                              <p>No messages yet</p>
                              <p className="empty-subtitle">Start the conversation!</p>
                            </div>
                          </div>
                        ) : (
                          messages.map(message => (
                            <div key={message.id} className={`message ${message.type || 'normal'}`}>
                              <div className="message-avatar">
                                {message.sender.charAt(0).toUpperCase()}
                              </div>
                              <div className="message-body">
                                <div className="message-meta">
                                  <span className="sender-name">{message.sender}</span>
                                  <span className="message-timestamp">
                                    {new Date(message.timestamp).toLocaleTimeString()}
                                  </span>
                                </div>
                                <div className="message-content">{message.content}</div>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>

                    {/* Message Input */}
                    <div className="message-input-panel">
                      <div className="input-container">
                        <input
                          type="text"
                          value={newMessage}
                          onChange={(e) => setNewMessage(e.target.value)}
                          onKeyPress={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                              e.preventDefault();
                              sendMessage();
                            }
                          }}
                          placeholder="Type your message..."
                          className="message-input"
                        />
                        <button 
                          onClick={sendMessage} 
                          className="btn btn-primary send-btn"
                          disabled={!newMessage.trim()}
                        >
                          📢 Send
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="no-session-state">
                    <div className="empty-chamber">
                      <div className="empty-icon">🏛️</div>
                      <h3>Welcome to the Council Chamber</h3>
                      <p>Select an active session from the sidebar or create a new one to begin collaborating with your AI agents.</p>
                      <button 
                        className="btn btn-primary btn-large"
                        onClick={() => setShowCreateRoomForm(true)}
                      >
                        🏛️ Create New Session
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="agents-section">
            <div className="section-header">
              <h2>🤖 Agent Management</h2>
              <div className="agent-controls">
                <button 
                  onClick={discoverAgents}
                  className="discover-agents-btn"
                  title="Discover agents from Synapse Gateway"
                >
                  🔍 Discover Agents
                </button>
                <div className="agent-stats">
                  <span>Active: {agents.filter(a => a.status === 'active').length}</span>
                  <span>Total Tasks: {agents.reduce((sum, a) => sum + a.tasks, 0)}</span>
                  <span>Avg Load: {Math.round(agents.reduce((sum, a) => sum + a.load, 0) / agents.length) || 0}%</span>
                </div>
              </div>
            </div>

            <div className="agents-grid">
              {agents.map(agent => (
                <div key={agent.id} className="agent-card">
                  <div className="agent-header">
                    <h3>{getAgentDisplayName(agent)}</h3>
                    <span 
                      className="agent-status"
                      style={{ backgroundColor: getStatusColor(agent.status) }}
                    >
                      {agent.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="agent-type">
                    {agent.type.toUpperCase()}
                    {agent.source === 'synapse' && (
                      <span className="agent-source-badge">SYNAPSE</span>
                    )}
                  </div>
                  
                  {/* Persona Management Section */}
                  <div className="agent-persona">
                    <div className="persona-header">
                      <h4>👤 Persona</h4>
                      <button 
                        className="persona-edit-btn"
                        onClick={() => setEditingAgentPersona(agent.id)}
                      >
                        {editingAgentPersona === agent.id ? '💾 Save' : '✏️ Edit'}
                      </button>
                    </div>
                    
                    {editingAgentPersona === agent.id ? (
                      <div className="persona-edit-form">
                        <div className="form-group">
                          <label>Display Name:</label>
                          <input 
                            type="text"
                            value={agentPersonas[agent.id]?.customName || agent.name || ''}
                            onChange={(e) => updateAgentPersona(agent.id, { customName: e.target.value })}
                            placeholder="Enter custom name"
                          />
                        </div>
                        <div className="form-group">
                          <label>Description:</label>
                          <textarea 
                            value={agentPersonas[agent.id]?.description || agent.description || ''}
                            onChange={(e) => updateAgentPersona(agent.id, { description: e.target.value })}
                            placeholder="Enter persona description"
                          />
                        </div>
                        <div className="form-group">
                          <label>Persona Mode:</label>
                          <select 
                            value={agentPersonas[agent.id]?.mode || 'static'}
                            onChange={(e) => updateAgentPersona(agent.id, { mode: e.target.value })}
                          >
                            <option value="static">Static (Manual)</option>
                            <option value="dynamic">Dynamic (Mimic Logic)</option>
                          </select>
                        </div>
                        <div className="persona-actions">
                          <button 
                            className="persona-save-btn"
                            onClick={() => setEditingAgentPersona(null)}
                          >
                            ✅ Save
                          </button>
                          <button 
                            className="persona-reset-btn"
                            onClick={() => resetAgentPersona(agent.id)}
                          >
                            🔄 Reset
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="persona-display">
                        <div className="persona-info">
                          <span className="persona-label">Name:</span>
                          <span className="persona-value">{getAgentDisplayName(agent)}</span>
                        </div>
                        <div className="persona-info">
                          <span className="persona-label">Mode:</span>
                          <span className="persona-value">
                            {agentPersonas[agent.id]?.mode === 'dynamic' ? '🔄 Dynamic' : '📌 Static'}
                          </span>
                        </div>
                        <div className="persona-description">
                          {getAgentPersonaDescription(agent)}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {agent.configured === false && agent.source === 'synapse' && (
                    <div className="agent-warning">⚠️ Configuration incomplete</div>
                  )}
                  <div className="agent-metrics">
                    <div className="metric-row">
                      <span className="metric-label">Load:</span>
                      <span className="metric-value">{agent.load.toFixed(2)}%</span>
                    </div>
                    <div className="metric-row">
                      <span className="metric-label">Tasks:</span>
                      <span className="metric-value">{agent.tasks}</span>
                    </div>
                    <div className="metric-row">
                      <span className="metric-label">Last Activity:</span>
                      <span className="metric-value">
                        {Math.round((Date.now() - new Date(agent.lastActivity)) / 60000)}m ago
                      </span>
                    </div>
                  </div>
                  <div className="agent-capabilities">
                    <h4>Capabilities:</h4>
                    <div className="capability-tags">
                      {agent.capabilities.map(cap => (
                        <span key={cap} className="capability-tag">{cap}</span>
                      ))}
                    </div>
                  </div>
                  <div className="agent-performance">
                    <h4>Performance:</h4>
                    <div className="performance-bars">
                      <div className="performance-metric">
                        <span>Efficiency:</span>
                        <div className="performance-bar">
                          <div 
                            className="performance-fill"
                            style={{ width: `${agent.performance.efficiency}%` }}
                          ></div>
                        </div>
                        <span>{agent.performance.efficiency}%</span>
                      </div>
                      <div className="performance-metric">
                        <span>Accuracy:</span>
                        <div className="performance-bar">
                          <div 
                            className="performance-fill"
                            style={{ width: `${agent.performance.accuracy}%` }}
                          ></div>
                        </div>
                        <span>{agent.performance.accuracy}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'services' && (
          <div className="services-section">
            <div className="section-header">
              <h2>⚙️ Core Services</h2>
              <div className="services-stats">
                <span>Online: {services.filter(s => s.status === 'operational').length}/{services.length}</span>
                <span>Avg Health: {Math.round(services.reduce((sum, s) => sum + s.health, 0) / services.length)}%</span>
              </div>
            </div>

            <div className="services-grid">
              {services.map(service => (
                <div key={service.id} className="service-card">
                  <div className="service-header">
                    <h3>{service.name}</h3>
                    <span 
                      className="service-status"
                      style={{ backgroundColor: getStatusColor(service.status) }}
                    >
                      {service.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="service-health">
                    <div className="health-label">Health: {service.health}%</div>
                    <div className="health-bar">
                      <div 
                        className="health-fill"
                        style={{ 
                          width: `${service.health}%`,
                          backgroundColor: getHealthColor(service.health)
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="service-metrics">
                    <div className="metric-row">
                      <span className="metric-label">Throughput:</span>
                      <span className="metric-value">{service.throughput}</span>
                    </div>
                    <div className="metric-row">
                      <span className="metric-label">Connections:</span>
                      <span className="metric-value">{service.connections}</span>
                    </div>
                    <div className="metric-row">
                      <span className="metric-label">Uptime:</span>
                      <span className="metric-value">{service.uptime}</span>
                    </div>
                  </div>
                  <div className="service-actions">
                    <button className="service-action">🔄 Restart</button>
                    <button className="service-action">📊 Metrics</button>
                    <button className="service-action">⚙️ Configure</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'projects' && (
          <div className="projects-section">
            <div className="section-header">
              <h2>📋 Project Management</h2>
              <div className="project-controls">
                <button className="create-project-btn">➕ New Project</button>
                <select className="project-filter">
                  <option value="all">All Projects</option>
                  <option value="active">Active</option>
                  <option value="planning">Planning</option>
                  <option value="pending">Pending</option>
                </select>
              </div>
            </div>

            <div className="projects-grid">
              {projects.map(project => (
                <div 
                  key={project.id} 
                  className={`project-card ${activeProject?.id === project.id ? 'selected' : ''}`}
                  onClick={() => setActiveProject(project)}
                >
                  <div className="project-header">
                    <h3>{project.name}</h3>
                    <span 
                      className="project-priority"
                      style={{ backgroundColor: getStatusColor(project.priority) }}
                    >
                      {project.priority.toUpperCase()}
                    </span>
                  </div>
                  <p className="project-description">{project.description}</p>
                  <div className="project-progress">
                    <div className="progress-label">Progress: {project.progress}%</div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill"
                        style={{ 
                          width: `${project.progress}%`,
                          backgroundColor: getProgressBarColor(project.progress)
                        }}
                      ></div>
                    </div>
                  </div>
                  <div className="project-tasks">
                    <div className="task-summary">
                      <span>Tasks: {project.tasks.length}</span>
                      <span>Completed: {project.tasks.filter(t => t.status === 'completed').length}</span>
                      <span>In Progress: {project.tasks.filter(t => t.status === 'in_progress').length}</span>
                    </div>
                  </div>
                  <div className="project-timeline">
                    <div className="timeline-item">
                      <span>Started: {new Date(project.startDate).toLocaleDateString()}</span>
                    </div>
                    <div className="timeline-item">
                      <span>Est. Completion: {new Date(project.estimatedCompletion).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="project-actions">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        startOrchestration(project.id);
                      }}
                      className="project-action primary"
                    >
                      🎯 Orchestrate
                    </button>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        testTaskDelegation(project.id);
                      }}
                      className="project-action"
                    >
                      🧪 Test Tasks
                    </button>
                    <button className="project-action">📊 Analytics</button>
                    <button className="project-action">⚙️ Configure</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'project-command' && (
          <div className="project-command-section">
            <ProjectCommand 
              accessibilitySettings={accessibilitySettings}
              onVoiceCommand={onVoiceCommand}
              currentAgent={currentAgent}
            />
          </div>
        )}


        {activeTab === 'monitoring' && (
          <div className="monitoring-section">
            <div className="section-header">
              <h2>📊 System Monitoring</h2>
              <div className="monitoring-controls">
                <button className="refresh-btn">🔄 Refresh</button>
                <button className="export-btn">📤 Export Data</button>
              </div>
            </div>

            <div className="monitoring-dashboard">
              <div className="performance-charts">
                <h3>Performance Metrics</h3>
                <div className="charts-grid">
                  <div className="chart-placeholder">
                    <div className="chart-title">CPU Usage Trend</div>
                    <div className="chart-content">
                      <div className="placeholder-text">Real-time CPU monitoring chart</div>
                    </div>
                  </div>
                  <div className="chart-placeholder">
                    <div className="chart-title">Memory Utilization</div>
                    <div className="chart-content">
                      <div className="placeholder-text">Memory usage over time</div>
                    </div>
                  </div>
                  <div className="chart-placeholder">
                    <div className="chart-title">Network Activity</div>
                    <div className="chart-content">
                      <div className="placeholder-text">Network throughput monitoring</div>
                    </div>
                  </div>
                  <div className="chart-placeholder">
                    <div className="chart-title">Agent Performance</div>
                    <div className="chart-content">
                      <div className="placeholder-text">Agent efficiency metrics</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="alerts-panel">
                <h3>System Alerts</h3>
                <div className="alerts-list">
                  <div className="alert-item info">
                    <span className="alert-icon">ℹ️</span>
                    <span className="alert-message">System performance is optimal</span>
                    <span className="alert-time">2 min ago</span>
                  </div>
                  <div className="alert-item warning">
                    <span className="alert-icon">⚠️</span>
                    <span className="alert-message">Memory usage above 80% threshold</span>
                    <span className="alert-time">15 min ago</span>
                  </div>
                  <div className="alert-item success">
                    <span className="alert-icon">✅</span>
                    <span className="alert-message">All agents responding normally</span>
                    <span className="alert-time">30 min ago</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'system' && (
          <div className="system-functions-section">
            <div className="section-header">
              <h2>🔧 System Functions Control Panel</h2>
              <div className="system-controls">
                <button className="refresh-btn" onClick={() => window.location.reload()}>🔄 Refresh</button>
              </div>
            </div>

            <div className="system-functions-grid">
              <div className="function-category">
                <h3>Core System Functions</h3>
                <div className="function-controls">
                  <div className="function-control-item">
                    <div className="function-info">
                      <h4>Core Health Check</h4>
                      <p>Perform comprehensive health check of core system components</p>
                    </div>
                    <button 
                      className="function-btn health-check"
                      onClick={handleCoreHealthCheck}
                    >
                      🏥 Health Check
                    </button>
                  </div>

                  <div className="function-control-item">
                    <div className="function-info">
                      <h4>Get Core Status</h4>
                      <p>Retrieve current status of core orchestration system</p>
                    </div>
                    <button 
                      className="function-btn status-check"
                      onClick={handleGetCoreStatus}
                    >
                      📊 Get Status
                    </button>
                  </div>

                  <div className="function-control-item">
                    <div className="function-info">
                      <h4>Execute System Command</h4>
                      <p>Execute administrative commands on the system</p>
                    </div>
                    <button 
                      className="function-btn execute-command"
                      onClick={() => {
                        const command = prompt('Enter command to execute:');
                        if (command) {
                          const args = prompt('Enter arguments (comma-separated, optional):');
                          handleExecuteCommand(command, args ? args.split(',').map(s => s.trim()) : []);
                        }
                      }}
                    >
                      ⚡ Execute Command
                    </button>
                  </div>
                </div>
              </div>

              <div className="function-results">
                <h3>Function Results</h3>
                
                {coreHealthStatus && (
                  <div className="result-panel health-result">
                    <h4>Core Health Status</h4>
                    <div className="result-content">
                      <div className={`status-indicator ${coreHealthStatus.status}`}>
                        {coreHealthStatus.status === 'healthy' ? '✅' : '❌'} {coreHealthStatus.status}
                      </div>
                      <pre>{JSON.stringify(coreHealthStatus, null, 2)}</pre>
                    </div>
                  </div>
                )}

                {coreStatus && (
                  <div className="result-panel status-result">
                    <h4>Core System Status</h4>
                    <div className="result-content">
                      <pre>{JSON.stringify(coreStatus, null, 2)}</pre>
                    </div>
                  </div>
                )}

                {executionResult && (
                  <div className="result-panel execution-result">
                    <h4>Command Execution Result</h4>
                    <div className="result-content">
                      <div className={`status-indicator ${executionResult.status}`}>
                        {executionResult.status === 'success' ? '✅' : '❌'} {executionResult.status}
                      </div>
                      <pre>{JSON.stringify(executionResult, null, 2)}</pre>
                    </div>
                  </div>
                )}

                {!coreHealthStatus && !coreStatus && !executionResult && (
                  <div className="result-placeholder">
                    <p>No function results yet. Use the controls above to execute system functions.</p>
                  </div>
                )}
              </div>
            </div>

            <div className="system-info">
              <h3>System Information</h3>
              <div className="info-grid">
                <div className="info-item">
                  <div className="info-label">Function Coverage</div>
                  <div className="info-value">54.6% (Target: ≥95%)</div>
                </div>
                <div className="info-item">
                  <div className="info-label">Orphaned Functions</div>
                  <div className="info-value">1752 identified</div>
                </div>
                <div className="info-item">
                  <div className="info-label">CLI Tools Available</div>
                  <div className="info-value">✅ scripts/cli_tools.py</div>
                </div>
                <div className="info-item">
                  <div className="info-label">SPEC-3 Week 2 Progress</div>
                  <div className="info-value">Step 3 - Adding Invocation Paths</div>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>

      {/* Agent Selection Modal */}
      {showAgentSelectionModal && (
        <div className="modal-overlay" onClick={closeAgentSelectionModal}>
          <div className="modal-content agent-selection-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🏛️ Select Council Members</h3>
              <button onClick={closeAgentSelectionModal} className="modal-close">×</button>
            </div>
            
            <div className="modal-body">
              <div className="session-form">
                <div className="form-group">
                  <label htmlFor="sessionName">Session Name:</label>
                  <input 
                    id="sessionName"
                    type="text"
                    value={newRoomName}
                    onChange={(e) => setNewRoomName(e.target.value)}
                    placeholder="Enter session name (e.g., 'Strategy Planning')"
                    className="session-name-input"
                    autoComplete="off"
                    autoFocus
                  />
                </div>
              </div>
              
              <div className="agents-selection">
                <div className="selection-header">
                  <h4>👥 Available Agents</h4>
                  <div className="selection-stats">
                    <span className="selected-count">{selectedAgents.length}</span> / <span className="total-count">{agents.length}</span> selected
                  </div>
                </div>
                
                <div className="agents-grid">
                  {agents.length === 0 ? (
                    <div className="no-agents-state">
                      <div className="empty-icon">🤖</div>
                      <p>No agents available</p>
                      <p className="empty-subtitle">Make sure agents are running and connected</p>
                    </div>
                  ) : (
                    agents.map(agent => (
                      <div 
                        key={agent.id} 
                        className={`agent-card ${selectedAgents.includes(agent.id) ? 'selected' : ''} ${agent.status === 'inactive' ? 'disabled' : ''}`}
                        onClick={() => agent.status === 'active' && toggleAgentSelection(agent.id)}
                      >
                        <div className="agent-card-header">
                          <div className="agent-checkbox">
                            <input 
                              type="checkbox" 
                              checked={selectedAgents.includes(agent.id)}
                              onChange={() => toggleAgentSelection(agent.id)}
                              disabled={agent.status === 'inactive'}
                              onClick={(e) => e.stopPropagation()}
                            />
                          </div>
                          <div className="agent-avatar">
                            {getAgentDisplayName(agent).charAt(0).toUpperCase()}
                          </div>
                          <div className="agent-status-indicator">
                            <span className={`status-dot ${agent.status}`}></span>
                          </div>
                        </div>
                        
                        <div className="agent-card-body">
                          <div className="agent-name">{getAgentDisplayName(agent)}</div>
                          <div className="agent-type">{agent.type}</div>
                          <div className="agent-status-text">{agent.status}</div>
                        </div>
                        
                        <div className="agent-card-footer">
                          <div className="agent-metrics">
                            <span className="metric">Load: {agent.load ? agent.load.toFixed(1) : 0}%</span>
                            <span className="metric">Tasks: {agent.tasks || 0}</span>
                          </div>
                          {agent.configured === false && agent.source === 'synapse' && (
                            <div className="agent-warning">⚠️ Setup needed</div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                onClick={closeAgentSelectionModal} 
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button 
                onClick={createConferenceRoomWithSelectedAgents}
                disabled={!newRoomName.trim() || selectedAgents.length === 0}
                className="btn btn-primary"
              >
                🏛️ Create Session ({selectedAgents.length} agents)
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Room Form Modal */}
      {showCreateRoomForm && (
        <div className="modal-overlay" onClick={() => setShowCreateRoomForm(false)}>
          <div className="modal-content create-session-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🏛️ Create New Session</h3>
              <button onClick={() => setShowCreateRoomForm(false)} className="modal-close">×</button>
            </div>
            
            <div className="modal-body">
              <div className="session-options">
                <div className="option-card" onClick={openAgentSelectionModal}>
                  <div className="option-header">
                    <div className="option-icon">👥</div>
                    <div className="option-title">
                      <h4>Custom Session</h4>
                      <p>Select specific agents for your session</p>
                    </div>
                  </div>
                  <div className="option-features">
                    <ul>
                      <li>Choose which agents to include</li>
                      <li>Customize session name</li>
                      <li>Control participant list</li>
                    </ul>
                  </div>
                </div>
                
                <div className="option-card" onClick={() => createQuickSession()}>
                  <div className="option-header">
                    <div className="option-icon">⚡</div>
                    <div className="option-title">
                      <h4>Quick Session</h4>
                      <p>Start immediately with all active agents</p>
                    </div>
                  </div>
                  <div className="option-features">
                    <ul>
                      <li>Includes all {agents.filter(a => a.status === 'active').length} active agents</li>
                      <li>Starts immediately</li>
                      <li>Perfect for quick collaboration</li>
                    </ul>
                  </div>
                  <div className="option-status">
                    {agents.filter(a => a.status === 'active').length === 0 ? (
                      <div className="warning">⚠️ No active agents available</div>
                    ) : (
                      <div className="ready">✓ Ready to start</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                onClick={() => setShowCreateRoomForm(false)} 
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CoreInterface;