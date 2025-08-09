import React, { useState, useEffect } from 'react';
import './CoreOrchestration.css';
import ProjectCommand from './ProjectCommand';
import ConferenceSystem from './ConferenceSystem';

const CoreOrchestration = ({ accessibilitySettings, onVoiceCommand, currentAgent }) => {
  const [activeSubModule, setActiveSubModule] = useState('orchestration');
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [orchestrationStatus, setOrchestrationStatus] = useState('idle');
  const [logs, setLogs] = useState([]);

  // Initialize with sample projects
  useEffect(() => {
    const sampleProjects = [
      {
        id: 'hearthlink-core',
        name: 'Hearthlink Core Enhancement',
        description: 'Enhance core functionality with AI delegation and metrics',
        status: 'active',
        priority: 'high',
        tasks: [
          { id: 1, name: 'Complete AI delegation system', status: 'completed', priority: 'high' },
          { id: 2, name: 'Implement metrics persistence', status: 'completed', priority: 'high' },
          { id: 3, name: 'Add error handling', status: 'completed', priority: 'medium' },
          { id: 4, name: 'Create simulation mode', status: 'completed', priority: 'medium' },
          { id: 5, name: 'Enable production deployment', status: 'pending', priority: 'high' }
        ],
        agents: ['claude-code', 'google-api', 'synapse-gateway'],
        lastActivity: new Date().toISOString()
      },
      {
        id: 'synapse-integration',
        name: 'Synapse Gateway Integration',
        description: 'Complete integration with external AI systems',
        status: 'ready',
        priority: 'high',
        tasks: [
          { id: 1, name: 'Configure API endpoints', status: 'ready', priority: 'high' },
          { id: 2, name: 'Set up rate limiting', status: 'ready', priority: 'high' },
          { id: 3, name: 'Add security layers', status: 'ready', priority: 'medium' },
          { id: 4, name: 'Test integration', status: 'ready', priority: 'medium' }
        ],
        agents: ['synapse-gateway', 'claude-code'],
        lastActivity: new Date().toISOString()
      },
      {
        id: 'ui-optimization',
        name: 'UI/UX Optimization',
        description: 'Improve user interface and accessibility',
        status: 'pending',
        priority: 'medium',
        tasks: [
          { id: 1, name: 'Enhance metrics display', status: 'pending', priority: 'medium' },
          { id: 2, name: 'Add responsive design', status: 'pending', priority: 'low' },
          { id: 3, name: 'Improve accessibility', status: 'pending', priority: 'medium' }
        ],
        agents: ['claude-code'],
        lastActivity: new Date().toISOString()
      }
    ];

    setProjects(sampleProjects);
    setActiveProject(sampleProjects[0]);
  }, []);

  const addLog = (message, type = 'info') => {
    const logEntry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      message,
      type
    };
    setLogs(prev => [logEntry, ...prev].slice(0, 100)); // Keep last 100 logs
  };

  const startOrchestration = async (projectId) => {
    setOrchestrationStatus('running');
    addLog(`Starting orchestration for project: ${projectId}`, 'info');
    
    const project = projects.find(p => p.id === projectId);
    if (!project) {
      addLog(`Project ${projectId} not found`, 'error');
      setOrchestrationStatus('error');
      return;
    }

    try {
      // Simulate orchestration process
      addLog(`Initializing agents: ${project.agents.join(', ')}`, 'info');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addLog(`Analyzing project requirements...`, 'info');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addLog(`Delegating tasks to appropriate agents...`, 'info');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update project status
      const updatedProjects = projects.map(p => 
        p.id === projectId 
          ? { ...p, status: 'active', lastActivity: new Date().toISOString() }
          : p
      );
      setProjects(updatedProjects);
      
      addLog(`Orchestration completed successfully for ${project.name}`, 'success');
      setOrchestrationStatus('completed');
      
    } catch (error) {
      addLog(`Orchestration failed: ${error.message}`, 'error');
      setOrchestrationStatus('error');
    }
  };

  const delegateTask = async (projectId, taskId) => {
    addLog(`Delegating task ${taskId} from project ${projectId}`, 'info');
    
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    const task = project.tasks.find(t => t.id === taskId);
    if (!task) return;

    // Simulate task delegation
    try {
      addLog(`Analyzing task: ${task.name}`, 'info');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      addLog(`Selecting optimal agent for task...`, 'info');
      await new Promise(resolve => setTimeout(resolve, 500));
      
      addLog(`Executing task delegation...`, 'info');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update task status
      const updatedProjects = projects.map(p => 
        p.id === projectId 
          ? {
              ...p,
              tasks: p.tasks.map(t => 
                t.id === taskId 
                  ? { ...t, status: 'in_progress' }
                  : t
              )
            }
          : p
      );
      setProjects(updatedProjects);
      
      addLog(`Task "${task.name}" delegated successfully`, 'success');
      
    } catch (error) {
      addLog(`Task delegation failed: ${error.message}`, 'error');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#28a745';
      case 'active': return '#007bff';
      case 'in_progress': return '#ffc107';
      case 'ready': return '#17a2b8';
      case 'pending': return '#6c757d';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getTaskStats = (tasks) => {
    const total = tasks.length;
    const completed = tasks.filter(t => t.status === 'completed').length;
    const inProgress = tasks.filter(t => t.status === 'in_progress').length;
    const pending = tasks.filter(t => t.status === 'pending' || t.status === 'ready').length;
    
    return { total, completed, inProgress, pending };
  };

  const renderSubModuleNav = () => (
    <div className="sub-module-nav">
      <button 
        className={`sub-nav-btn ${activeSubModule === 'orchestration' ? 'active' : ''}`}
        onClick={() => setActiveSubModule('orchestration')}
      >
        🎯 Orchestration
      </button>
      <button 
        className={`sub-nav-btn ${activeSubModule === 'project-command' ? 'active' : ''}`}
        onClick={() => setActiveSubModule('project-command')}
      >
        📋 Project Command
      </button>
      <button 
        className={`sub-nav-btn ${activeSubModule === 'conference' ? 'active' : ''}`}
        onClick={() => setActiveSubModule('conference')}
      >
        🎪 Conference
      </button>
    </div>
  );

  return (
    <div className="core-orchestration">
      <div className="orchestration-header">
        <h2>CORE ORCHESTRATION CENTER</h2>
        <div className="module-subtitle">AI-Powered Project Management & Coordination</div>
      </div>
      
      {renderSubModuleNav()}
      
      <div className="sub-module-content">
        {activeSubModule === 'orchestration' && (
          <div className="orchestration-main">
            <div className="section-header">
              <h3>🎯 Orchestration Dashboard</h3>
              <p>Manage and orchestrate AI-powered coding initiatives</p>
            </div>

      <div className="orchestration-dashboard">
        {/* Project Overview */}
        <div className="dashboard-section">
          <h3>📊 Project Overview</h3>
          <div className="project-grid">
            {projects.map(project => {
              const stats = getTaskStats(project.tasks);
              return (
                <div 
                  key={project.id} 
                  className={`project-card ${activeProject?.id === project.id ? 'active' : ''}`}
                  onClick={() => setActiveProject(project)}
                >
                  <div className="project-header">
                    <h4>{project.name}</h4>
                    <span 
                      className="project-status"
                      style={{ backgroundColor: getStatusColor(project.status) }}
                    >
                      {project.status}
                    </span>
                  </div>
                  <p className="project-description">{project.description}</p>
                  <div className="project-stats">
                    <div className="stat">
                      <span className="stat-label">Total Tasks:</span>
                      <span className="stat-value">{stats.total}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Completed:</span>
                      <span className="stat-value">{stats.completed}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">In Progress:</span>
                      <span className="stat-value">{stats.inProgress}</span>
                    </div>
                  </div>
                  <div className="project-agents">
                    <strong>Agents:</strong> {project.agents.join(', ')}
                  </div>
                  <div className="project-actions">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        startOrchestration(project.id);
                      }}
                      disabled={orchestrationStatus === 'running'}
                      className="orchestrate-btn"
                    >
                      {orchestrationStatus === 'running' ? 'Running...' : 'Start Orchestration'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Active Project Details */}
        {activeProject && (
          <div className="dashboard-section">
            <h3>📋 Active Project: {activeProject.name}</h3>
            <div className="project-details">
              <div className="task-list">
                <h4>Tasks</h4>
                {activeProject.tasks.map(task => (
                  <div key={task.id} className="task-item">
                    <div className="task-info">
                      <span className="task-name">{task.name}</span>
                      <span 
                        className="task-status"
                        style={{ backgroundColor: getStatusColor(task.status) }}
                      >
                        {task.status}
                      </span>
                      <span className={`task-priority priority-${task.priority}`}>
                        {task.priority}
                      </span>
                    </div>
                    <div className="task-actions">
                      <button 
                        onClick={() => delegateTask(activeProject.id, task.id)}
                        disabled={task.status === 'completed' || orchestrationStatus === 'running'}
                        className="delegate-btn"
                      >
                        Delegate
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Orchestration Status */}
        <div className="dashboard-section">
          <h3>🔄 Orchestration Status</h3>
          <div className="status-panel">
            <div className="status-indicator">
              <span className="status-label">Current Status:</span>
              <span 
                className="status-value"
                style={{ backgroundColor: getStatusColor(orchestrationStatus) }}
              >
                {orchestrationStatus}
              </span>
            </div>
            <div className="status-info">
              <p>
                The orchestration system coordinates AI agents to complete coding tasks efficiently.
                Select a project and click "Start Orchestration" to begin automated task delegation.
              </p>
            </div>
          </div>
        </div>

        {/* Activity Logs */}
        <div className="dashboard-section">
          <h3>📝 Activity Logs</h3>
          <div className="logs-container">
            {logs.length === 0 ? (
              <div className="no-logs">No activity logs yet. Start orchestration to see logs.</div>
            ) : (
              logs.map(log => (
                <div key={log.id} className={`log-entry log-${log.type}`}>
                  <span className="log-timestamp">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="log-message">{log.message}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
          </div>
        )}
        
        {activeSubModule === 'project-command' && (
          <ProjectCommand 
            accessibilitySettings={accessibilitySettings}
            onVoiceCommand={onVoiceCommand}
            currentAgent={currentAgent}
          />
        )}
        
        {activeSubModule === 'conference' && (
          <ConferenceSystem 
            accessibilitySettings={accessibilitySettings}
            onVoiceCommand={onVoiceCommand}
            currentAgent={currentAgent}
          />
        )}
      </div>
    </div>
  );
};

export default CoreOrchestration;