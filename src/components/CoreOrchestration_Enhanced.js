import React, { useState, useEffect } from 'react';
import './CoreOrchestration_Enhanced.css';

const CoreOrchestration = ({ accessibilitySettings, onVoiceCommand, currentAgent }) => {
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [orchestrationStatus, setOrchestrationStatus] = useState('standby');
  const [systemLogs, setSystemLogs] = useState([]);
  const [aiAgents, setAiAgents] = useState({
    alden: { status: 'online', load: 25, tasks: 3 },
    google: { status: 'ready', load: 0, tasks: 0 },
    claude: { status: 'active', load: 60, tasks: 8 },
    synapse: { status: 'online', load: 15, tasks: 2 }
  });
  const [projectCommand, setProjectCommand] = useState({
    active: false,
    currentMethodology: 'agile',
    riskProfile: 'medium',
    delegation: []
  });

  useEffect(() => {
    initializeProjects();
    startSystemMonitoring();
  }, []);

  const initializeProjects = () => {
    const initialProjects = [
      {
        id: 'hearthlink-core',
        name: 'Hearthlink Core Enhancement',
        description: 'Advanced AI orchestration and StarCraft HUD integration',
        status: 'active',
        priority: 'critical',
        progress: 85,
        methodology: 'agile',
        tasks: [
          { id: 1, name: 'StarCraft UI Implementation', status: 'completed', assignee: 'claude', priority: 'high' },
          { id: 2, name: 'Memory System Integration', status: 'in_progress', assignee: 'alden', priority: 'high' },
          { id: 3, name: 'AI Delegation Framework', status: 'completed', assignee: 'google', priority: 'high' },
          { id: 4, name: 'Project Command Protocol', status: 'in_progress', assignee: 'alden', priority: 'critical' },
          { id: 5, name: 'Synapse Gateway Enhancement', status: 'pending', assignee: 'synapse', priority: 'medium' }
        ],
        agents: ['alden', 'claude', 'google', 'synapse'],
        timeline: { start: '2025-07-11', estimated_completion: '2025-07-12' },
        resources: { cpu: 65, memory: 45, network: 30 },
        metrics: { velocity: 8.5, quality: 0.92, blockers: 1 }
      },
      {
        id: 'workspace-automation',
        name: 'Workspace Automation Suite',
        description: 'Direct file operations and project structure generation',
        status: 'planning',
        priority: 'high',
        progress: 25,
        methodology: 'kanban',
        tasks: [
          { id: 1, name: 'File System Integration', status: 'completed', assignee: 'alden', priority: 'high' },
          { id: 2, name: 'Template Generation Engine', status: 'pending', assignee: 'claude', priority: 'medium' },
          { id: 3, name: 'Code Quality Automation', status: 'pending', assignee: 'google', priority: 'medium' },
          { id: 4, name: 'Deployment Pipeline', status: 'pending', assignee: 'synapse', priority: 'low' }
        ],
        agents: ['alden', 'claude', 'google'],
        timeline: { start: '2025-07-12', estimated_completion: '2025-07-15' },
        resources: { cpu: 40, memory: 30, network: 50 },
        metrics: { velocity: 6.2, quality: 0.88, blockers: 0 }
      },
      {
        id: 'memory-optimization',
        name: 'AI Memory & Learning System',
        description: 'Advanced memory consolidation and learning algorithms',
        status: 'research',
        priority: 'medium',
        progress: 60,
        methodology: 'research',
        tasks: [
          { id: 1, name: 'Episodic Memory Framework', status: 'completed', assignee: 'alden', priority: 'high' },
          { id: 2, name: 'Semantic Knowledge Base', status: 'in_progress', assignee: 'alden', priority: 'high' },
          { id: 3, name: 'Procedural Learning Engine', status: 'in_progress', assignee: 'google', priority: 'medium' },
          { id: 4, name: 'Memory Consolidation Protocol', status: 'completed', assignee: 'claude', priority: 'medium' }
        ],
        agents: ['alden', 'google', 'claude'],
        timeline: { start: '2025-07-10', estimated_completion: '2025-07-14' },
        resources: { cpu: 55, memory: 70, network: 20 },
        metrics: { velocity: 7.8, quality: 0.95, blockers: 2 }
      }
    ];

    setProjects(initialProjects);
    setActiveProject(initialProjects[0]);
  };

  const startSystemMonitoring = () => {
    // Real-time system monitoring
    const monitoringInterval = setInterval(() => {
      updateSystemStatus();
      checkProjectHealth();
      updateAgentStatus();
    }, 5000);

    return () => clearInterval(monitoringInterval);
  };

  const addSystemLog = (message, type = 'info', source = 'CORE') => {
    const logEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      message,
      type,
      source
    };
    setSystemLogs(prev => [logEntry, ...prev].slice(0, 100));
  };

  const initiateProjectCommand = async (projectId) => {
    setProjectCommand(prev => ({ ...prev, active: true }));
    setOrchestrationStatus('orchestrating');
    
    addSystemLog(`PROJECT COMMAND INITIATED: ${projectId}`, 'command', 'PROJECT');
    
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    try {
      // Methodology evaluation
      addSystemLog('Evaluating optimal methodology...', 'info', 'METHODOLOGY');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Risk assessment
      addSystemLog('Assessing project risk profile...', 'info', 'RISK');
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Agent delegation
      addSystemLog('Delegating tasks to AI agents...', 'info', 'DELEGATION');
      for (const agent of project.agents) {
        await delegateToAgent(agent, project);
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      // Start execution monitoring
      addSystemLog('Execution monitoring activated', 'success', 'MONITOR');
      setOrchestrationStatus('monitoring');
      
      // Update project status
      const updatedProjects = projects.map(p => 
        p.id === projectId 
          ? { ...p, status: 'executing', last_orchestrated: new Date().toISOString() }
          : p
      );
      setProjects(updatedProjects);
      
    } catch (error) {
      addSystemLog(`Orchestration failed: ${error.message}`, 'error', 'CORE');
      setOrchestrationStatus('error');
    }
  };

  const delegateToAgent = async (agentName, project) => {
    const agentTasks = project.tasks.filter(task => task.assignee === agentName);
    
    if (agentTasks.length > 0) {
      addSystemLog(`Delegating ${agentTasks.length} tasks to ${agentName.toUpperCase()}`, 'info', agentName.toUpperCase());
      
      // Simulate agent response
      setAiAgents(prev => ({
        ...prev,
        [agentName]: {
          ...prev[agentName],
          status: 'active',
          load: Math.min(prev[agentName].load + (agentTasks.length * 10), 100),
          tasks: prev[agentName].tasks + agentTasks.length
        }
      }));
      
      // Update delegation tracking
      setProjectCommand(prev => ({
        ...prev,
        delegation: [...prev.delegation, {
          agent: agentName,
          tasks: agentTasks.length,
          timestamp: new Date().toISOString()
        }]
      }));
    }
  };

  const executeTask = async (projectId, taskId) => {
    addSystemLog(`Executing task ${taskId} in project ${projectId}`, 'info', 'EXECUTOR');
    
    const updatedProjects = projects.map(project => 
      project.id === projectId 
        ? {
            ...project,
            tasks: project.tasks.map(task => 
              task.id === taskId 
                ? { ...task, status: 'in_progress', started_at: new Date().toISOString() }
                : task
            )
          }
        : project
    );
    setProjects(updatedProjects);
    
    // Simulate task execution
    setTimeout(() => {
      const finalProjects = projects.map(project => 
        project.id === projectId 
          ? {
              ...project,
              tasks: project.tasks.map(task => 
                task.id === taskId 
                  ? { ...task, status: 'completed', completed_at: new Date().toISOString() }
                  : task
              )
            }
          : project
      );
      setProjects(finalProjects);
      addSystemLog(`Task ${taskId} completed successfully`, 'success', 'EXECUTOR');
    }, 3000 + Math.random() * 5000);
  };

  const updateSystemStatus = () => {
    // Simulate real-time status updates
    const activeProjects = projects.filter(p => p.status === 'active' || p.status === 'executing').length;
    const totalTasks = projects.reduce((sum, p) => sum + p.tasks.length, 0);
    const completedTasks = projects.reduce((sum, p) => sum + p.tasks.filter(t => t.status === 'completed').length, 0);
    
    if (Math.random() < 0.1) { // 10% chance to add status update
      addSystemLog(`System Status: ${activeProjects} active projects, ${completedTasks}/${totalTasks} tasks completed`, 'info', 'STATUS');
    }
  };

  const checkProjectHealth = () => {
    projects.forEach(project => {
      const blockers = project.tasks.filter(t => t.status === 'blocked').length;
      if (blockers > 0 && Math.random() < 0.05) { // 5% chance to report blockers
        addSystemLog(`Project ${project.name}: ${blockers} blocked tasks detected`, 'warning', 'HEALTH');
      }
    });
  };

  const updateAgentStatus = () => {
    // Simulate agent load changes
    setAiAgents(prev => {
      const updated = { ...prev };
      Object.keys(updated).forEach(agent => {
        if (updated[agent].status === 'active' && Math.random() < 0.2) {
          updated[agent].load = Math.max(0, updated[agent].load - Math.random() * 5);
        }
      });
      return updated;
    });
  };

  const getStatusColor = (status) => {
    const statusColors = {
      'completed': '#00ff88',
      'active': '#00ccff',
      'executing': '#ffaa00',
      'in_progress': '#ffaa00',
      'planning': '#aa88ff',
      'research': '#ff6699',
      'pending': '#888888',
      'blocked': '#ff4444',
      'error': '#ff0000'
    };
    return statusColors[status] || '#888888';
  };

  const getPriorityColor = (priority) => {
    const priorityColors = {
      'critical': '#ff0000',
      'high': '#ff6600',
      'medium': '#ffaa00',
      'low': '#88cc00'
    };
    return priorityColors[priority] || '#888888';
  };

  const getAgentStatusColor = (status) => {
    const agentColors = {
      'online': '#00ff88',
      'active': '#00ccff',
      'ready': '#88cc00',
      'busy': '#ffaa00',
      'offline': '#ff4444'
    };
    return agentColors[status] || '#888888';
  };

  return (
    <div className="core-orchestration-enhanced">
      {/* Header */}
      <div className="core-header">
        <div className="header-title">
          <h1>CORE <span className="glow-text">ORCHESTRATION</span></h1>
          <div className="header-subtitle">Advanced Project Command Center</div>
        </div>
        <div className="system-status">
          <div className="status-indicator">
            <span className="status-label">STATUS:</span>
            <span className={`status-value status-${orchestrationStatus}`}>
              {orchestrationStatus.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Main Dashboard */}
      <div className="dashboard-grid">
        {/* Project Overview */}
        <div className="dashboard-section projects-section">
          <div className="section-header">
            <h2>🎯 ACTIVE PROJECTS</h2>
            <div className="project-stats">
              {projects.length} Projects | {projects.filter(p => p.status === 'active').length} Active
            </div>
          </div>
          
          <div className="projects-grid">
            {projects.map(project => (
              <div 
                key={project.id} 
                className={`project-card ${activeProject?.id === project.id ? 'active' : ''}`}
                onClick={() => setActiveProject(project)}
              >
                <div className="project-header">
                  <div className="project-name">{project.name}</div>
                  <div className="project-status" style={{ color: getStatusColor(project.status) }}>
                    {project.status.toUpperCase()}
                  </div>
                </div>
                
                <div className="project-description">{project.description}</div>
                
                <div className="project-metrics">
                  <div className="metric">
                    <span className="metric-label">Progress:</span>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${project.progress}%` }}
                      ></div>
                    </div>
                    <span className="metric-value">{project.progress}%</span>
                  </div>
                  
                  <div className="metric">
                    <span className="metric-label">Priority:</span>
                    <span 
                      className="metric-value" 
                      style={{ color: getPriorityColor(project.priority) }}
                    >
                      {project.priority.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="metric">
                    <span className="metric-label">Methodology:</span>
                    <span className="metric-value">{project.methodology.toUpperCase()}</span>
                  </div>
                </div>
                
                <div className="project-agents">
                  <span className="agents-label">Agents:</span>
                  {project.agents.map(agent => (
                    <span key={agent} className="agent-badge" style={{ color: getAgentStatusColor(aiAgents[agent]?.status) }}>
                      {agent.toUpperCase()}
                    </span>
                  ))}
                </div>
                
                <div className="project-actions">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      initiateProjectCommand(project.id);
                    }}
                    disabled={orchestrationStatus === 'orchestrating'}
                    className="orchestrate-btn"
                  >
                    {orchestrationStatus === 'orchestrating' ? 'ORCHESTRATING...' : 'INITIATE COMMAND'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* AI Agents Status */}
        <div className="dashboard-section agents-section">
          <div className="section-header">
            <h2>🤖 AI AGENTS</h2>
            <div className="agents-stats">
              {Object.values(aiAgents).filter(a => a.status === 'online' || a.status === 'active').length} Online
            </div>
          </div>
          
          <div className="agents-grid">
            {Object.entries(aiAgents).map(([agentName, agent]) => (
              <div key={agentName} className="agent-card">
                <div className="agent-header">
                  <div className="agent-name">{agentName.toUpperCase()}</div>
                  <div className="agent-status" style={{ color: getAgentStatusColor(agent.status) }}>
                    ● {agent.status.toUpperCase()}
                  </div>
                </div>
                
                <div className="agent-metrics">
                  <div className="agent-metric">
                    <span className="metric-label">Load:</span>
                    <div className="load-bar">
                      <div 
                        className="load-fill" 
                        style={{ 
                          width: `${agent.load}%`,
                          backgroundColor: agent.load > 80 ? '#ff4444' : agent.load > 50 ? '#ffaa00' : '#00ff88'
                        }}
                      ></div>
                    </div>
                    <span className="metric-value">{agent.load}%</span>
                  </div>
                  
                  <div className="agent-metric">
                    <span className="metric-label">Tasks:</span>
                    <span className="metric-value">{agent.tasks}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Active Project Details */}
        {activeProject && (
          <div className="dashboard-section project-details-section">
            <div className="section-header">
              <h2>📋 PROJECT DETAILS</h2>
              <div className="project-name">{activeProject.name}</div>
            </div>
            
            <div className="project-details">
              <div className="tasks-list">
                <div className="tasks-header">
                  <span>Task</span>
                  <span>Assignee</span>
                  <span>Priority</span>
                  <span>Status</span>
                  <span>Actions</span>
                </div>
                
                {activeProject.tasks.map(task => (
                  <div key={task.id} className="task-row">
                    <span className="task-name">{task.name}</span>
                    <span className="task-assignee" style={{ color: getAgentStatusColor(aiAgents[task.assignee]?.status) }}>
                      {task.assignee.toUpperCase()}
                    </span>
                    <span className="task-priority" style={{ color: getPriorityColor(task.priority) }}>
                      {task.priority.toUpperCase()}
                    </span>
                    <span className="task-status" style={{ color: getStatusColor(task.status) }}>
                      {task.status.toUpperCase()}
                    </span>
                    <div className="task-actions">
                      {task.status === 'pending' && (
                        <button 
                          onClick={() => executeTask(activeProject.id, task.id)}
                          className="execute-btn"
                        >
                          EXECUTE
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* System Logs */}
        <div className="dashboard-section logs-section">
          <div className="section-header">
            <h2>📡 SYSTEM LOGS</h2>
            <div className="logs-stats">
              {systemLogs.length} Entries
            </div>
          </div>
          
          <div className="logs-container">
            {systemLogs.map(log => (
              <div key={log.id} className={`log-entry log-${log.type}`}>
                <span className="log-timestamp">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </span>
                <span className="log-source">[{log.source}]</span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoreOrchestration;