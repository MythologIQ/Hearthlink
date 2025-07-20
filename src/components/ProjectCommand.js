import React, { useState, useEffect } from 'react';
import './ProjectCommand.css';
import taskDelegationService from '../services/TaskDelegationService';

const ProjectCommand = ({ accessibilitySettings, onVoiceCommand, currentAgent }) => {
  const [activeView, setActiveView] = useState('dashboard');
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [methodologyData, setMethodologyData] = useState({
    current: 'agile',
    confidence: 85,
    recommendations: []
  });
  
  // Task delegation state
  const [delegatedTasks, setDelegatedTasks] = useState([]);
  const [serviceStatus, setServiceStatus] = useState({});
  const [taskHistory, setTaskHistory] = useState([]);
  const [pendingTasks, setPendingTasks] = useState([
    {
      id: 'task-001',
      name: 'Implement backend DELETE endpoints',
      priority: 'high',
      type: 'code_generation',
      description: 'Add DELETE endpoints for user management in backend API',
      recommended_service: 'claude-code',
      context: { language: 'python', framework: 'flask' }
    },
    {
      id: 'task-002', 
      name: 'Research ChatGPT Custom Actions requirements',
      priority: 'medium',
      type: 'research',
      description: 'Investigate requirements for implementing ChatGPT Custom Actions',
      recommended_service: 'google-ai',
      context: { research_type: 'technical_requirements' }
    },
    {
      id: 'task-003',
      name: 'Optimize database queries in user service',
      priority: 'medium',
      type: 'code_optimization',
      description: 'Review and optimize slow database queries in user management service',
      recommended_service: 'claude-code',
      context: { file_path: 'src/api/user_service.py', optimization_type: 'performance' }
    }
  ]);

  // Available methodologies with their characteristics
  const methodologies = [
    { 
      id: 'agile', 
      name: 'Agile/Scrum', 
      complexity: 'Medium',
      risk: 'Low',
      effort: 'Medium',
      description: 'Iterative development with regular sprints and reviews'
    },
    { 
      id: 'kanban', 
      name: 'Kanban', 
      complexity: 'Low',
      risk: 'Low',
      effort: 'Low',
      description: 'Continuous flow with WIP limits and visual boards'
    },
    { 
      id: 'waterfall', 
      name: 'Waterfall', 
      complexity: 'High',
      risk: 'High',
      effort: 'High',
      description: 'Sequential phases with detailed planning and documentation'
    },
    { 
      id: 'scrumban', 
      name: 'Scrumban', 
      complexity: 'Medium',
      risk: 'Medium',
      effort: 'Medium',
      description: 'Hybrid approach combining Scrum and Kanban elements'
    },
    { 
      id: 'lean', 
      name: 'Lean', 
      complexity: 'Medium',
      risk: 'Medium',
      effort: 'Low',
      description: 'Waste reduction and continuous improvement focused'
    },
    { 
      id: 'prince2', 
      name: 'PRINCE2', 
      complexity: 'High',
      risk: 'Low',
      effort: 'High',
      description: 'Process-driven with defined roles and stage gates'
    }
  ];

  // Initialize component and check service status
  useEffect(() => {
    const sampleProjects = [
      {
        id: 'HEARTHLINK-001',
        name: 'Core AI Integration',
        methodology: 'agile',
        status: 'active',
        priority: 'high',
        lead_agent: 'Alden',
        start_date: '2025-07-11',
        completion: 75,
        risk_level: 'moderate',
        team_size: 3,
        sprint_length: 14
      },
      {
        id: 'HEARTHLINK-002',
        name: 'Project Command Implementation',
        methodology: 'scrumban',
        status: 'active',
        priority: 'high',
        lead_agent: 'Alden',
        start_date: '2025-07-11',
        completion: 60,
        risk_level: 'low',
        team_size: 2,
        sprint_length: 7
      }
    ];
    
    setProjects(sampleProjects);
    setSelectedProject(sampleProjects[0]);
    
    // Check service status
    updateServiceStatus();
    
    // Set up periodic status checks
    const statusInterval = setInterval(updateServiceStatus, 30000);
    
    return () => clearInterval(statusInterval);
  }, []);
  
  // Update service status
  const updateServiceStatus = async () => {
    try {
      const status = await taskDelegationService.getServiceStatus();
      setServiceStatus(status);
    } catch (error) {
      console.error('Failed to update service status:', error);
    }
  };
  
  // Handle task delegation
  const handleTaskDelegation = async (taskId, approved) => {
    const task = pendingTasks.find(t => t.id === taskId);
    if (!task) return;
    
    if (approved) {
      try {
        const result = await taskDelegationService.delegateTask(
          task.type,
          task.description,
          task.context
        );
        
        // Add to task history
        const completedTask = {
          ...task,
          ...result,
          timestamp: new Date().toISOString(),
          status: result.success ? 'completed' : 'failed'
        };
        
        setTaskHistory(prev => [completedTask, ...prev]);
        setDelegatedTasks(prev => [...prev, completedTask]);
        
        // Remove from pending tasks
        setPendingTasks(prev => prev.filter(t => t.id !== taskId));
        
        console.log(`Task ${taskId} delegated:`, result);
      } catch (error) {
        console.error(`Failed to delegate task ${taskId}:`, error);
      }
    } else {
      // Remove from pending tasks
      setPendingTasks(prev => prev.filter(t => t.id !== taskId));
    }
  };
  
  // Handle task reassignment
  const handleTaskReassignment = async (taskId, newService) => {
    const task = pendingTasks.find(t => t.id === taskId);
    if (!task) return;
    
    const updatedTask = { ...task, recommended_service: newService };
    setPendingTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
  };
  
  // Generate new task
  const generateTask = async (description, taskType = 'ai_response') => {
    const newTask = {
      id: `task-${Date.now()}`,
      name: description,
      priority: 'medium',
      type: taskType,
      description: description,
      recommended_service: 'google-ai',
      context: { generated: true }
    };
    
    setPendingTasks(prev => [newTask, ...prev]);
  };

  const handleMethodologyEvaluation = () => {
    // Trigger methodology evaluation SOP
    const evaluation = {
      triggered_by: 'user_request',
      timestamp: new Date().toISOString(),
      agent: currentAgent,
      status: 'initiated'
    };
    
    console.log('Methodology evaluation triggered:', evaluation);
    
    // Simulate evaluation process
    setTimeout(() => {
      setMethodologyData(prev => ({
        ...prev,
        recommendations: [
          { methodology: 'agile', score: 92, rationale: 'High team collaboration, moderate complexity' },
          { methodology: 'kanban', score: 88, rationale: 'Continuous flow suitable for current workload' },
          { methodology: 'scrumban', score: 85, rationale: 'Hybrid approach for mixed requirements' }
        ]
      }));
    }, 2000);
  };

  const handleMethodSwitch = (methodologyId) => {
    // Implement Method Switch Protocol SOP
    const switchRequest = {
      from: methodologyData.current,
      to: methodologyId,
      timestamp: new Date().toISOString(),
      agent: currentAgent,
      rationale: 'User initiated switch'
    };
    
    console.log('Method switch requested:', switchRequest);
    
    // Update methodology
    setMethodologyData(prev => ({
      ...prev,
      current: methodologyId,
      confidence: 95 // New methodology starts with high confidence
    }));
    
    // Update selected project
    if (selectedProject) {
      setSelectedProject(prev => ({
        ...prev,
        methodology: methodologyId
      }));
    }
  };

  const renderDashboard = () => (
    <div className="project-dashboard">
      <div className="dashboard-header">
        <h3>Project Command Dashboard</h3>
        <div className="dashboard-stats">
          <div className="stat-card">
            <div className="stat-value">{projects.length}</div>
            <div className="stat-label">Active Projects</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{methodologyData.confidence}%</div>
            <div className="stat-label">Methodology Confidence</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{projects.filter(p => p.priority === 'high').length}</div>
            <div className="stat-label">High Priority</div>
          </div>
        </div>
      </div>
      
      <div className="projects-grid">
        {projects.map(project => (
          <div 
            key={project.id} 
            className={`project-card ${selectedProject?.id === project.id ? 'selected' : ''}`}
            onClick={() => setSelectedProject(project)}
          >
            <div className="project-header">
              <h4>{project.name}</h4>
              <span className={`status ${project.status}`}>{project.status.toUpperCase()}</span>
            </div>
            <div className="project-details">
              <div className="detail-row">
                <span>Methodology:</span>
                <span className="methodology-tag">{project.methodology.toUpperCase()}</span>
              </div>
              <div className="detail-row">
                <span>Lead Agent:</span>
                <span>{project.lead_agent}</span>
              </div>
              <div className="detail-row">
                <span>Priority:</span>
                <span className={`priority ${project.priority}`}>{project.priority.toUpperCase()}</span>
              </div>
            </div>
            <div className="progress-section">
              <div className="progress-label">Completion: {project.completion}%</div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${project.completion}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderMethodologySelector = () => (
    <div className="methodology-selector">
      <div className="selector-header">
        <h3>Methodology Evaluation</h3>
        <button 
          className="evaluate-btn"
          onClick={handleMethodologyEvaluation}
        >
          🔄 Evaluate Methodologies
        </button>
      </div>
      
      <div className="current-methodology">
        <h4>Current Methodology</h4>
        <div className="methodology-card current">
          <div className="methodology-info">
            <span className="methodology-name">
              {methodologies.find(m => m.id === methodologyData.current)?.name}
            </span>
            <span className="confidence-badge">
              {methodologyData.confidence}% Confidence
            </span>
          </div>
          <div className="methodology-description">
            {methodologies.find(m => m.id === methodologyData.current)?.description}
          </div>
        </div>
      </div>
      
      {methodologyData.recommendations.length > 0 && (
        <div className="recommendations">
          <h4>Recommendations</h4>
          <div className="methodology-grid">
            {methodologyData.recommendations.map(rec => {
              const methodology = methodologies.find(m => m.id === rec.methodology);
              return (
                <div key={rec.methodology} className="methodology-card recommendation">
                  <div className="methodology-header">
                    <span className="methodology-name">{methodology.name}</span>
                    <span className="score-badge">{rec.score}% Match</span>
                  </div>
                  <div className="methodology-meta">
                    <span className={`complexity ${methodology.complexity.toLowerCase()}`}>
                      {methodology.complexity} Complexity
                    </span>
                    <span className={`risk ${methodology.risk.toLowerCase()}`}>
                      {methodology.risk} Risk
                    </span>
                    <span className={`effort ${methodology.effort.toLowerCase()}`}>
                      {methodology.effort} Effort
                    </span>
                  </div>
                  <div className="methodology-description">
                    {methodology.description}
                  </div>
                  <div className="rationale">
                    <strong>Rationale:</strong> {rec.rationale}
                  </div>
                  <button 
                    className="switch-btn"
                    onClick={() => handleMethodSwitch(rec.methodology)}
                  >
                    Switch to {methodology.name}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );

  const renderRetrospective = () => (
    <div className="retrospective-panel">
      <h3>Retrospective & Learning</h3>
      <div className="retrospective-content">
        <div className="retrospective-section">
          <h4>Recent Learnings</h4>
          <div className="learning-items">
            <div className="learning-item">
              <div className="learning-header">
                <span className="learning-type">Methodology Switch</span>
                <span className="learning-date">2025-07-10</span>
              </div>
              <div className="learning-content">
                Switched from Waterfall to Agile for Core AI Integration project. 
                Result: 20% increase in delivery velocity, improved team collaboration.
              </div>
            </div>
            <div className="learning-item">
              <div className="learning-header">
                <span className="learning-type">Risk Mitigation</span>
                <span className="learning-date">2025-07-09</span>
              </div>
              <div className="learning-content">
                Implemented daily standups for high-risk tasks. 
                Result: Early detection of 3 critical blockers, prevented 2-day delay.
              </div>
            </div>
          </div>
        </div>
        
        <div className="retrospective-section">
          <h4>Performance Metrics</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-value">85%</div>
              <div className="metric-label">Sprint Completion Rate</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">2.3</div>
              <div className="metric-label">Avg Velocity (Story Points/Day)</div>
            </div>
            <div className="metric-card">
              <div className="metric-value">12</div>
              <div className="metric-label">Blockers Resolved</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAIDelegation = () => (
    <div className="ai-delegation-panel">
      <div className="delegation-header">
        <h3>🤖 AI Task Delegation</h3>
        <p>Automatically delegate tasks to AI agents based on expertise and availability</p>
        <button className="refresh-btn" onClick={updateServiceStatus}>
          🔄 Refresh Status
        </button>
      </div>
      
      <div className="delegation-content">
        <div className="delegation-section">
          <h4>Available AI Agents</h4>
          <div className="agents-grid">
            <div className={`agent-card ${serviceStatus['claude-code']?.available ? 'active' : ''}`}>
              <div className="agent-info">
                <span className="agent-name">Claude Code</span>
                <span className={`agent-status ${serviceStatus['claude-code']?.available ? 'online' : 'offline'}`}>
                  ● {serviceStatus['claude-code']?.available ? 'ONLINE' : 'OFFLINE'}
                </span>
              </div>
              <div className="agent-expertise">
                <span className="expertise-tag">Code Generation</span>
                <span className="expertise-tag">Debugging</span>
                <span className="expertise-tag">Refactoring</span>
                <span className="expertise-tag">Analysis</span>
              </div>
              <div className="agent-workload">
                <span>Current Load: 45%</span>
                <div className="workload-bar">
                  <div className="workload-fill" style={{ width: '45%' }}></div>
                </div>
              </div>
            </div>
            
            <div className={`agent-card ${serviceStatus['google-ai']?.available ? 'active' : ''}`}>
              <div className="agent-info">
                <span className="agent-name">Google Gemini</span>
                <span className={`agent-status ${serviceStatus['google-ai']?.available ? 'online' : 'offline'}`}>
                  ● {serviceStatus['google-ai']?.available ? 'ONLINE' : 'OFFLINE'}
                </span>
              </div>
              <div className="agent-expertise">
                <span className="expertise-tag">Analysis</span>
                <span className="expertise-tag">Documentation</span>
                <span className="expertise-tag">Research</span>
                <span className="expertise-tag">Chat</span>
              </div>
              <div className="agent-workload">
                <span>Current Load: 60%</span>
                <div className="workload-bar">
                  <div className="workload-fill" style={{ width: '60%' }}></div>
                </div>
              </div>
            </div>
            
            <div className={`agent-card ${serviceStatus['ollama']?.available ? 'active' : ''}`}>
              <div className="agent-info">
                <span className="agent-name">Ollama LLM</span>
                <span className={`agent-status ${serviceStatus['ollama']?.available ? 'online' : 'offline'}`}>
                  ● {serviceStatus['ollama']?.available ? 'ONLINE' : 'OFFLINE'}
                </span>
              </div>
              <div className="agent-expertise">
                <span className="expertise-tag">Local Processing</span>
                <span className="expertise-tag">Chat</span>
                <span className="expertise-tag">Generation</span>
              </div>
              <div className="agent-workload">
                <span>Current Load: 15%</span>
                <div className="workload-bar">
                  <div className="workload-fill" style={{ width: '15%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="delegation-section">
          <h4>Pending Delegations ({pendingTasks.length})</h4>
          <div className="delegations-list">
            {pendingTasks.map(task => (
              <div key={task.id} className="delegation-item">
                <div className="task-info">
                  <span className="task-name">{task.name}</span>
                  <span className={`task-priority ${task.priority}`}>{task.priority.toUpperCase()} PRIORITY</span>
                </div>
                <div className="delegation-details">
                  <span className="recommended-agent">Recommended: {task.recommended_service}</span>
                  <span className="delegation-reason">Type: {task.type}</span>
                </div>
                <div className="delegation-actions">
                  <button 
                    className="approve-btn"
                    onClick={() => handleTaskDelegation(task.id, true)}
                  >
                    ✓ Approve
                  </button>
                  <button 
                    className="reject-btn"
                    onClick={() => handleTaskDelegation(task.id, false)}
                  >
                    ✗ Reject
                  </button>
                  <select 
                    className="reassign-select"
                    value={task.recommended_service}
                    onChange={(e) => handleTaskReassignment(task.id, e.target.value)}
                  >
                    <option value="claude-code">Claude Code</option>
                    <option value="google-ai">Google AI</option>
                    <option value="ollama">Ollama</option>
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="delegation-section">
          <h4>Task History ({taskHistory.length})</h4>
          <div className="task-history-list">
            {taskHistory.slice(0, 5).map(task => (
              <div key={task.id} className="history-item">
                <div className="task-info">
                  <span className="task-name">{task.name}</span>
                  <span className={`task-status ${task.status}`}>{task.status.toUpperCase()}</span>
                </div>
                <div className="task-details">
                  <span>Service: {task.service_used}</span>
                  <span>Time: {new Date(task.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="delegation-section">
          <h4>Quick Task Generator</h4>
          <div className="task-generator">
            <input 
              type="text"
              placeholder="Describe a task to delegate..."
              onKeyPress={(e) => {
                if (e.key === 'Enter' && e.target.value.trim()) {
                  generateTask(e.target.value.trim());
                  e.target.value = '';
                }
              }}
            />
            <select onChange={(e) => {
              const taskType = e.target.value;
              e.target.value = '';
            }}>
              <option value="">Select task type...</option>
              <option value="code_generation">Code Generation</option>
              <option value="code_analysis">Code Analysis</option>
              <option value="research">Research</option>
              <option value="documentation">Documentation</option>
              <option value="debugging">Debugging</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="project-command">
      <div className="project-command-header">
        <h2>PROJECT COMMAND</h2>
        <div className="module-subtitle">AI-Orchestrated Project Management</div>
        <div className="authority-badge">
          <span className="agent-tag">Authorized: Alden</span>
          <span className="agent-tag">Executor: {currentAgent}</span>
        </div>
      </div>
      
      <div className="project-command-nav">
        <button 
          className={`nav-btn ${activeView === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveView('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={`nav-btn ${activeView === 'methodology' ? 'active' : ''}`}
          onClick={() => setActiveView('methodology')}
        >
          🎯 Methodology
        </button>
        <button 
          className={`nav-btn ${activeView === 'retrospective' ? 'active' : ''}`}
          onClick={() => setActiveView('retrospective')}
        >
          📈 Retrospective
        </button>
        <button 
          className={`nav-btn ${activeView === 'delegation' ? 'active' : ''}`}
          onClick={() => setActiveView('delegation')}
        >
          🤖 AI Delegation
        </button>
      </div>
      
      <div className="project-command-content">
        {activeView === 'dashboard' && renderDashboard()}
        {activeView === 'methodology' && renderMethodologySelector()}
        {activeView === 'retrospective' && renderRetrospective()}
        {activeView === 'delegation' && renderAIDelegation()}
      </div>
    </div>
  );
};

export default ProjectCommand;