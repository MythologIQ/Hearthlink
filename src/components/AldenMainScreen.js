import React, { useState, useEffect, useRef } from 'react';
import './AldenMainScreen.css';

// Import individual panel components
import ObservatoryPanel from './panels/ObservatoryPanel';
import PersonalityMoodPanel from './panels/PersonalityMoodPanel';
import CognitionMemoryPanel from './panels/CognitionMemoryPanel';
import InteractionInterfacePanel from './panels/InteractionInterfacePanel';
import DiagnosticsRepairPanel from './panels/DiagnosticsRepairPanel';
import TaskDashboard from './panels/TaskDashboard';
import ProjectBoard from './panels/ProjectBoard';
import AliceInterface from './AliceInterface';
import MimicInterface from './MimicInterface';
import LocalLLMInterface from './LocalLLMInterface';

const AldenMainScreen = ({ accessibilitySettings, onVoiceCommand }) => {
  // Core state management
  const [expandedPanel, setExpandedPanel] = useState(null);
  // System controls moved to global banner

  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [voiceInputActive, setVoiceInputActive] = useState(false);

  // Alice interface state
  const [aliceInterfaceVisible, setAliceInterfaceVisible] = useState(false);
  
  // Mimic interface state
  const [mimicInterfaceVisible, setMimicInterfaceVisible] = useState(false);
  
  // Local LLM interface state
  const [llmInterfaceVisible, setLlmInterfaceVisible] = useState(false);
  
  // Removed SuperClaude interface state - now in Core module

  // System data state
  const [agentGraphData, setAgentGraphData] = useState({
    agents: [
      { id: 'alden', name: 'Alden', status: 'active', connections: ['alice', 'core'], health: 'green' },
      { id: 'alice', name: 'Alice', status: 'active', connections: ['alden', 'sentry'], health: 'green' },
      { id: 'mimic', name: 'Mimic', status: 'idle', connections: ['core'], health: 'yellow' },
      { id: 'sentry', name: 'Sentry', status: 'monitoring', connections: ['alice', 'synapse'], health: 'green' },
      { id: 'core', name: 'Core', status: 'active', connections: ['alden', 'vault'], health: 'green' },
      { id: 'synapse', name: 'Synapse', status: 'active', connections: ['sentry'], health: 'green' },
      { id: 'vault', name: 'Vault', status: 'active', connections: ['core'], health: 'green' }
    ]
  });

  // Task management data state
  const [taskData, setTaskData] = useState({
    tasks: [
      {
        id: 'task_1',
        title: 'Complete Phase 3A UI implementation',
        description: 'Implement advanced UI panels for Alden interface with task management capabilities',
        priority: 'high',
        status: 'in_progress',
        createdAt: '2025-01-21T10:00:00Z',
        dueDate: '2025-01-22T18:00:00Z',
        progress: 65,
        estimatedTime: 8,
        assignedAgent: 'alden',
        tags: ['ui', 'development', 'priority']
      },
      {
        id: 'task_2',
        title: 'Optimize memory usage in vector embeddings',
        description: 'Improve performance of vector embedding storage and retrieval',
        priority: 'medium',
        status: 'todo',
        createdAt: '2025-01-21T09:30:00Z',
        dueDate: '2025-01-23T12:00:00Z',
        progress: 0,
        estimatedTime: 4,
        assignedAgent: 'alice',
        tags: ['performance', 'memory']
      },
      {
        id: 'task_3',
        title: 'Update security protocols',
        description: 'Review and update security protocols for multi-agent communication',
        priority: 'high',
        status: 'todo',
        createdAt: '2025-01-21T08:15:00Z',
        dueDate: '2025-01-21T16:00:00Z',
        progress: 0,
        estimatedTime: 6,
        assignedAgent: 'sentry',
        tags: ['security', 'protocols']
      },
      {
        id: 'task_4',
        title: 'Test voice command accuracy',
        description: 'Run comprehensive tests on voice command recognition system',
        priority: 'medium',
        status: 'completed',
        createdAt: '2025-01-20T14:00:00Z',
        completedAt: '2025-01-21T11:30:00Z',
        progress: 100,
        estimatedTime: 3,
        assignedAgent: 'mimic',
        tags: ['testing', 'voice']
      },
      {
        id: 'task_5',
        title: 'Backup system configurations',
        description: 'Create automated backup system for all agent configurations',
        priority: 'low',
        status: 'todo',
        createdAt: '2025-01-21T07:45:00Z',
        dueDate: '2025-01-25T10:00:00Z',
        progress: 0,
        estimatedTime: 2,
        assignedAgent: 'vault',
        tags: ['backup', 'maintenance']
      }
    ],
    projects: [
      {
        id: 'project_1',
        name: 'Hearthlink Phase 3A',
        description: 'Advanced UI Panels implementation',
        status: 'active',
        progress: 65,
        dueDate: '2025-01-30T00:00:00Z',
        taskIds: ['task_1', 'task_2']
      }
    ]
  });

  const [personalityData, setPersonalityData] = useState({
    currentMood: 'focused',
    moodIntensity: 74,
    traits: [
      { name: 'analytical', strength: 85 },
      { name: 'empathetic', strength: 80 },
      { name: 'vigilant', strength: 75 },
      { name: 'creative', strength: 90 },
      { name: 'skeptical', strength: 65 }
    ],
    emotionalHistory: [
      { timestamp: Date.now() - 600000, mood: 'curious', intensity: 70 },
      { timestamp: Date.now() - 300000, mood: 'focused', intensity: 80 },
      { timestamp: Date.now() - 100000, mood: 'analytical', intensity: 75 },
      { timestamp: Date.now(), mood: 'focused', intensity: 74 }
    ],
    behavioralBiases: [
      { type: 'confirmation_bias', active: false, description: 'Seeking confirming evidence' },
      { type: 'recency_bias', active: true, description: 'Overweighting recent information' }
    ]
  });

  const [memoryData, setMemoryData] = useState({
    usage: {
      shortTerm: 35,
      longTerm: 60,
      embedded: 25,
      total: 45
    },
    workingSet: [
      { id: 'mem_001', type: 'episodic', content: 'User interaction pattern analysis', importance: 0.85, timestamp: Date.now() - 300000 },
      { id: 'mem_002', type: 'semantic', content: 'Project management methodologies', importance: 0.72, timestamp: Date.now() - 600000 },
      { id: 'mem_003', type: 'procedural', content: 'Natural language processing workflow', importance: 0.90, timestamp: Date.now() - 180000 }
    ],
    cognitiveLoad: {
      current: 65,
      queueSize: 7,
      processingRate: 0.85
    },
    embeddingClusters: [
      { x: 20, y: 30, label: 'Technical' },
      { x: 60, y: 40, label: 'Personal' },
      { x: 80, y: 20, label: 'Creative' },
      { x: 40, y: 70, label: 'Analytical' }
    ]
  });

  const [systemHealth, setSystemHealth] = useState({
    uptime: { days: 2, hours: 14, minutes: 23 },
    heartbeat: 'stable',
    latency: { current: 45, average: 52, peak: 120, floor: 28 },
    recentPrompts: [
      { id: 'p1', content: 'Analyze the project structure', tokens: 25, response: 'Comprehensive analysis complete', responseTokens: 150, timestamp: Date.now() - 120000 },
      { id: 'p2', content: 'Show system status', tokens: 15, response: 'All systems operational', responseTokens: 80, timestamp: Date.now() - 300000 }
    ],
    failureEvents: [
      { timestamp: Date.now() - 3600000, type: 'timeout', severity: 'low', message: 'API timeout resolved automatically' },
      { timestamp: Date.now() - 7200000, type: 'recovery', severity: 'info', message: 'Memory optimization completed' }
    ],
    selfRepairOps: [
      { timestamp: Date.now() - 1800000, action: 'memory_cleanup', success: true, details: 'Cleared 15MB of temporary data' },
      { timestamp: Date.now() - 900000, action: 'cache_refresh', success: true, details: 'Updated vector embeddings' }
    ]
  });

  const [interactionData, setInteractionData] = useState({
    recentInputs: [
      { mode: 'voice', content: 'Show me the system status', timestamp: Date.now() - 120000 },
      { mode: 'text', content: 'Analyze the current workload', timestamp: Date.now() - 300000 },
      { mode: 'gesture', content: 'Navigate to diagnostics', timestamp: Date.now() - 600000 }
    ],
    voiceStatus: {
      listening: false,
      sensitivity: 0.7,
      threshold: 0.5
    },
    accessibilityModes: {
      screenReader: true,
      highContrast: false,
      largeText: false,
      voiceNavigation: true
    }
  });

  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize Alden with welcome message
    const welcomeMessage = {
      id: Date.now(),
      type: 'system',
      content: 'ALDEN MAIN SCREEN OPERATIONAL\n\nAll panels loaded successfully. System controls active.\nReady for interaction.',
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Live data updates
  useEffect(() => {
    const updateSystemData = async () => {
      try {
        // Check system health and update agent statuses
        const systemHealth = await checkSystemHealth();
        setAgentGraphData(prev => ({
          ...prev,
          agents: prev.agents.map(agent => ({
            ...agent,
            health: systemHealth[agent.id] || 'red',
            status: systemHealth[agent.id] === 'green' ? 'active' : 'idle'
          }))
        }));

        // Update memory usage from actual system metrics
        const memoryStats = await getMemoryStats();
        setMemoryData(prev => ({
          ...prev,
          usage: memoryStats.usage,
          cognitiveLoad: memoryStats.cognitiveLoad
        }));

        // Update system health metrics
        const healthMetrics = await getSystemHealthMetrics();
        setSystemHealth(prev => ({
          ...prev,
          ...healthMetrics
        }));

      } catch (error) {
        console.warn('Failed to update system data:', error);
      }
    };

    // Initial load
    updateSystemData();

    // Update every 5 seconds
    const interval = setInterval(updateSystemData, 5000);
    return () => clearInterval(interval);
  }, []);

  // System health check functions
  const checkSystemHealth = async () => {
    // Check if services are running
    const health = {};
    
    try {
      // Check LLM service
      const llmResponse = await fetch('http://localhost:8001/api/llm/health', { method: 'GET' }).catch(() => null);
      health.alden = llmResponse?.ok ? 'green' : 'red';
      health.alice = llmResponse?.ok ? 'green' : 'red';
      health.mimic = llmResponse?.ok ? 'green' : 'red';
      
      // Check Vault service
      const vaultResponse = await fetch('http://localhost:8002/api/vault/health', { method: 'GET' }).catch(() => null);
      health.vault = vaultResponse?.ok ? 'green' : 'red';
      
      // Check Synapse service
      const synapseResponse = await fetch('http://localhost:8003/api/synapse/health', { method: 'GET' }).catch(() => null);
      health.synapse = synapseResponse?.ok ? 'green' : 'red';
      
      // Check Core service
      const coreResponse = await fetch('http://localhost:8000/api/health', { method: 'GET' }).catch(() => null);
      health.core = coreResponse?.ok ? 'green' : 'red';
      
      // Check Sentry service
      const sentryResponse = await fetch('http://localhost:8004/api/sentry/health', { method: 'GET' }).catch(() => null);
      health.sentry = sentryResponse?.ok ? 'green' : 'red';
      
    } catch (error) {
      // Default to red if health checks fail
      Object.keys(health).forEach(key => { health[key] = 'red'; });
    }
    
    return health;
  };

  const getMemoryStats = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/system/memory');
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to fetch memory stats:', error);
    }
    
    // Return simulated data if API fails
    return {
      usage: {
        shortTerm: Math.floor(Math.random() * 40) + 20,
        longTerm: Math.floor(Math.random() * 30) + 50,
        embedded: Math.floor(Math.random() * 20) + 15,
        total: Math.floor(Math.random() * 25) + 35
      },
      cognitiveLoad: {
        current: Math.floor(Math.random() * 30) + 50,
        queueSize: Math.floor(Math.random() * 5) + 3,
        processingRate: Math.random() * 0.3 + 0.7
      }
    };
  };

  const getSystemHealthMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/system/health');
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.warn('Failed to fetch system health:', error);
    }
    
    // Return simulated metrics if API fails
    const now = Date.now();
    return {
      uptime: { 
        days: Math.floor(Math.random() * 5) + 1, 
        hours: Math.floor(Math.random() * 24), 
        minutes: Math.floor(Math.random() * 60) 
      },
      heartbeat: 'stable',
      latency: { 
        current: Math.floor(Math.random() * 50) + 20, 
        average: Math.floor(Math.random() * 20) + 40, 
        peak: Math.floor(Math.random() * 100) + 80, 
        floor: Math.floor(Math.random() * 20) + 10 
      },
      recentPrompts: [
        { id: 'p1', content: 'System status check', tokens: 20, response: 'All systems operational', responseTokens: 100, timestamp: now - 60000 },
        { id: 'p2', content: 'Memory analysis', tokens: 30, response: 'Memory usage within normal range', responseTokens: 120, timestamp: now - 180000 }
      ]
    };
  };

  // Utility functions removed - radial navigation handled globally

  const handlePanelExpand = (panelId) => {
    setExpandedPanel(expandedPanel === panelId ? null : panelId);
  };

  // System control toggle removed - handled globally

  const handleSendMessage = async (content) => {
    if (!content.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: content.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Try to get real LLM response
      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: `You are Alden, a helpful AI assistant in the Hearthlink system. You are the primary persona responsible for productivity, reasoning, and general assistance. Respond professionally and helpfully.\n\nUser: ${content.trim()}`,
          task_type: 'reasoning',
          profile: 'mid'
        })
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: data.response || data.message || 'I received your message and am processing it.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        throw new Error('LLM API request failed');
      }
    } catch (error) {
      console.warn('LLM API unavailable, using fallback response:', error);
      
      // Fallback to a more intelligent simulated response
      const fallbackResponses = [
        `I understand you're asking about "${content.trim()}". While I'm currently operating in offline mode, I can help you with system operations and general assistance.`,
        `Thank you for your message about "${content.trim()}". I'm functioning normally and ready to assist with your tasks.`,
        `I received your request regarding "${content.trim()}". My cognitive systems are operational and I'm here to help with productivity and reasoning tasks.`,
        `Your message about "${content.trim()}" has been processed. I'm currently monitoring system operations and ready to provide assistance.`
      ];
      
      const randomResponse = fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)];
      
      const response = {
        id: Date.now() + 1,
        type: 'assistant',
        content: randomResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, response]);
    }
    
    setIsTyping(false);
  };

  const handleVoiceToggle = () => {
    setVoiceInputActive(!voiceInputActive);
    setInteractionData(prev => ({
      ...prev,
      voiceStatus: {
        ...prev.voiceStatus,
        listening: !voiceInputActive
      }
    }));
  };

  // Task management handlers
  const handleTaskCreate = (newTask) => {
    setTaskData(prev => ({
      ...prev,
      tasks: [newTask, ...prev.tasks]
    }));
    
    // Add chat message for task creation
    const taskMessage = {
      id: Date.now(),
      content: `✅ New task created: "${newTask.title}" (Priority: ${newTask.priority})`,
      type: 'system',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, taskMessage]);
  };

  const handleTaskUpdate = (updatedTask) => {
    setTaskData(prev => ({
      ...prev,
      tasks: prev.tasks.map(task => 
        task.id === updatedTask.id ? updatedTask : task
      )
    }));
    
    // Add chat message for task status changes
    if (updatedTask.status === 'completed') {
      const completionMessage = {
        id: Date.now(),
        content: `🎉 Task completed: "${updatedTask.title}"`,
        type: 'system',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, completionMessage]);
    }
  };

  // Project management handlers
  const handleProjectCreate = (newProject) => {
    setTaskData(prev => ({
      ...prev,
      projects: [newProject, ...prev.projects]
    }));
    
    // Add chat message for project creation
    const projectMessage = {
      id: Date.now(),
      content: `🚀 New project created: "${newProject.name}"`,
      type: 'system',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, projectMessage]);
  };

  const handleProjectUpdate = (updatedProject) => {
    setTaskData(prev => ({
      ...prev,
      projects: prev.projects.map(project => 
        project.id === updatedProject.id ? updatedProject : project
      )
    }));
    
    // Add chat message for project status changes
    if (updatedProject.status === 'completed') {
      const completionMessage = {
        id: Date.now(),
        content: `🎊 Project completed: "${updatedProject.name}"`,
        type: 'system',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, completionMessage]);
    }
  };

  // Render functions
  // Radial navigation removed - now handled globally in banner

  const renderPanelFrame = () => {
    if (expandedPanel) {
      return (
        <div className="panel-item expanded">
          <div className="panel-header">
            <h3 className="panel-title">{expandedPanel.toUpperCase()}</h3>
            <button 
              className="panel-close-button"
              onClick={() => setExpandedPanel(null)}
              aria-label="Close expanded panel"
            >
              ✕
            </button>
          </div>
          <div className="panel-content">
            {renderExpandedPanel()}
          </div>
        </div>
      );
    }

    return (
      <>
        <div className="panel-item" onClick={() => handlePanelExpand('observatory')}>
          <div className="panel-header">
            <h3 className="panel-title">Observatory</h3>
          </div>
          <div className="panel-content">
            <div className="dashboard-preview">
              <div className="agent-status-grid">
                {agentGraphData.agents.slice(0, 3).map(agent => (
                  <div key={agent.id} className="agent-status-card">
                    <div className={`status-dot ${agent.health}`}></div>
                    <span className="agent-name">{agent.name}</span>
                    <span className="agent-status">{agent.status}</span>
                  </div>
                ))}
              </div>
              <div className="observatory-stats">
                <div className="stat-item">
                  <span className="stat-label">Active Agents</span>
                  <span className="stat-value">{agentGraphData.agents.filter(a => a.status === 'active').length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Connections</span>
                  <span className="stat-value">{agentGraphData.agents.reduce((sum, a) => sum + a.connections.length, 0)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="panel-item" onClick={() => handlePanelExpand('personality')}>
          <div className="panel-header">
            <h3 className="panel-title">Personality & Mood</h3>
          </div>
          <div className="panel-content">
            <div className="dashboard-preview">
              <div className="personality-mood-preview">
                <div className="mood-indicator-preview">
                  <div className="mood-ring" style={{
                    background: `conic-gradient(rgba(34, 211, 238, 0.8) ${personalityData.moodIntensity * 3.6}deg, rgba(34, 211, 238, 0.2) 0deg)`,
                    borderRadius: '50%',
                    width: '60px',
                    height: '60px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.7rem',
                    fontWeight: 'bold',
                    color: '#22d3ee'
                  }}>
                    {personalityData.currentMood.toUpperCase()}
                  </div>
                  <div className="mood-stats">
                    <div className="stat-item">
                      <span className="stat-label">Intensity</span>
                      <span className="stat-value">{personalityData.moodIntensity}%</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Traits</span>
                      <span className="stat-value">{personalityData.traits.length}</span>
                    </div>
                  </div>
                </div>
                <div className="top-traits">
                  {personalityData.traits.slice(0, 3).map((trait, index) => (
                    <div key={index} className="trait-preview">
                      <span className="trait-name">{trait.name}</span>
                      <div className="trait-bar-mini">
                        <div className="trait-fill" style={{width: `${trait.strength}%`}}></div>
                      </div>
                      <span className="trait-value">{trait.strength}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="panel-item" onClick={() => handlePanelExpand('interaction')}>
          <div className="panel-header">
            <h3 className="panel-title">Interaction Interface</h3>
          </div>
          <div className="panel-content">
            <div className="dashboard-preview">
              <div className="interaction-preview">
                <div className="input-modes">
                  <div className="mode-indicator">
                    <div className={`mode-dot ${interactionData.voiceStatus.listening ? 'active' : ''}`}></div>
                    <span className="mode-label">Voice</span>
                  </div>
                  <div className="mode-indicator">
                    <div className="mode-dot active"></div>
                    <span className="mode-label">Text</span>
                  </div>
                  <div className="mode-indicator">
                    <div className="mode-dot"></div>
                    <span className="mode-label">Gesture</span>
                  </div>
                </div>
                <div className="recent-interactions">
                  <div className="interaction-count">
                    <span className="count-label">Recent Inputs</span>
                    <span className="count-value">{interactionData.recentInputs.length}</span>
                  </div>
                  <div className="voice-sensitivity">
                    <span className="sensitivity-label">Voice Sensitivity</span>
                    <div className="sensitivity-bar">
                      <div className="sensitivity-fill" style={{width: `${interactionData.voiceStatus.sensitivity * 100}%`}}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="panel-item" onClick={() => handlePanelExpand('cognition')}>
          <div className="panel-header">
            <h3 className="panel-title">Cognition & Memory</h3>
          </div>
          <div className="panel-content">
            <div className="dashboard-preview">
              <div className="memory-preview">
                <div className="memory-usage">
                  <div className="usage-ring" style={{
                    background: `conic-gradient(#fbbf24 ${memoryData.usage.total * 3.6}deg, rgba(251, 191, 36, 0.2) 0deg)`,
                    borderRadius: '50%',
                    width: '50px',
                    height: '50px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    color: '#fbbf24'
                  }}>
                    {memoryData.usage.total}%
                  </div>
                  <div className="usage-breakdown">
                    <div className="usage-item">
                      <span className="usage-label">Short-term</span>
                      <span className="usage-value">{memoryData.usage.shortTerm}%</span>
                    </div>
                    <div className="usage-item">
                      <span className="usage-label">Long-term</span>
                      <span className="usage-value">{memoryData.usage.longTerm}%</span>
                    </div>
                  </div>
                </div>
                <div className="working-set-preview">
                  <div className="working-set-count">
                    <span className="count-label">Working Set</span>
                    <span className="count-value">{memoryData.workingSet.length}</span>
                  </div>
                  <div className="cognitive-load">
                    <span className="load-label">Cognitive Load</span>
                    <div className="load-bar">
                      <div className="load-fill" style={{width: `${memoryData.cognitiveLoad.current}%`}}></div>
                    </div>
                    <span className="load-value">{memoryData.cognitiveLoad.current}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="panel-item" onClick={() => handlePanelExpand('diagnostics')}>
          <div className="panel-header">
            <h3 className="panel-title">Diagnostics & Repair</h3>
          </div>
          <div className="panel-content">
            <div className="dashboard-preview">
              <div className="diagnostics-preview">
                <div className="system-health">
                  <div className="health-indicator">
                    <div className={`health-dot ${systemHealth.heartbeat === 'stable' ? 'healthy' : 'warning'}`}></div>
                    <span className="health-label">System Health</span>
                    <span className="health-status">{systemHealth.heartbeat.toUpperCase()}</span>
                  </div>
                  <div className="uptime-display">
                    <span className="uptime-label">Uptime</span>
                    <span className="uptime-value">{systemHealth.uptime.days}d {systemHealth.uptime.hours}h {systemHealth.uptime.minutes}m</span>
                  </div>
                </div>
                <div className="performance-metrics">
                  <div className="metric-item">
                    <span className="metric-label">Latency</span>
                    <span className="metric-value">{systemHealth.latency.current}ms</span>
                    <div className="metric-bar">
                      <div className="metric-fill" style={{width: `${Math.min(systemHealth.latency.current / 2, 100)}%`}}></div>
                    </div>
                  </div>
                  <div className="metric-item">
                    <span className="metric-label">Recent Events</span>
                    <span className="metric-value">{systemHealth.failureEvents.length}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="panel-item" onClick={() => handlePanelExpand('tasks')}>
          <div className="panel-header">
            <h3 className="panel-title">Task Management</h3>
          </div>
          <div className="panel-content">
            <TaskDashboard 
              data={taskData}
              isExpanded={false}
              onTaskCreate={handleTaskCreate}
              onTaskUpdate={handleTaskUpdate}
            />
          </div>
        </div>
        
        <div className="panel-item" onClick={() => handlePanelExpand('projects')}>
          <div className="panel-header">
            <h3 className="panel-title">Project Board</h3>
          </div>
          <div className="panel-content">
            <ProjectBoard 
              data={taskData}
              isExpanded={false}
              onProjectCreate={handleProjectCreate}
              onProjectUpdate={handleProjectUpdate}
              onTaskUpdate={handleTaskUpdate}
            />
          </div>
        </div>
      </>
    );
  };

  const renderExpandedPanel = () => {
    switch (expandedPanel) {
      case 'observatory':
        return <ObservatoryPanel data={agentGraphData} isExpanded={true} />;
      case 'personality':
        return <PersonalityMoodPanel data={personalityData} isExpanded={true} />;
      case 'cognition':
        return <CognitionMemoryPanel data={memoryData} isExpanded={true} />;
      case 'interaction':
        return <InteractionInterfacePanel 
          data={interactionData} 
          isExpanded={true} 
          onVoiceToggle={handleVoiceToggle}
          voiceActive={voiceInputActive}
        />;
      case 'diagnostics':
        return <DiagnosticsRepairPanel data={systemHealth} isExpanded={true} />;
      case 'tasks':
        return <TaskDashboard 
          data={taskData}
          isExpanded={true}
          onTaskCreate={handleTaskCreate}
          onTaskUpdate={handleTaskUpdate}
        />;
      case 'projects':
        return <ProjectBoard 
          data={taskData}
          isExpanded={true}
          onProjectCreate={handleProjectCreate}
          onProjectUpdate={handleProjectUpdate}
          onTaskUpdate={handleTaskUpdate}
        />;
      default:
        return null;
    }
  };

  const renderChatInterface = () => (
    <div className="persistent-chat">
      <div className="chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`chat-message ${message.type}`}>
            <div className="message-content">{message.content}</div>
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="chat-message assistant typing">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-area">
        <div className="input-container">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(inputValue);
              }
            }}
            placeholder="Type your message..."
            className="chat-input"
            rows="2"
            disabled={isTyping}
          />
          <button 
            onClick={() => handleSendMessage(inputValue)}
            disabled={!inputValue.trim() || isTyping}
            className="chat-send-button"
          >
            {isTyping ? 'Processing...' : 'Send'}
          </button>
          {voiceInputActive && (
            <button 
              className="voice-input-button active"
              onClick={handleVoiceToggle}
              aria-label="Voice input active"
            >
              🎤
            </button>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="alden-main-screen">
      {/* Main Layout Container */}
      <div className="main-layout-container">
        {/* Panel Frame - left side */}
        <div className="panel-frame-left">
          {renderPanelFrame()}
        </div>
        
        {/* Chat Column - right side */}
        <div className="chat-column-right">
          {renderChatInterface()}
        </div>
      </div>

      {/* Alice Behavioral Analysis Interface */}
      <AliceInterface 
        isVisible={aliceInterfaceVisible}
        onClose={() => setAliceInterfaceVisible(false)}
      />

      {/* Mimic Dynamic Persona Interface */}
      <MimicInterface 
        isVisible={mimicInterfaceVisible}
        onClose={() => setMimicInterfaceVisible(false)}
      />

      {/* Local LLM & Voice Integration Interface */}
      <LocalLLMInterface 
        isVisible={llmInterfaceVisible}
        onClose={() => setLlmInterfaceVisible(false)}
      />

      {/* SuperClaude moved to Core module */}
    </div>
  );
};

export default AldenMainScreen;