import React, { useState, useEffect, useRef } from 'react';
import './AldenMainScreen.css';
import aldenAPIService from '../services/AldenAPIService.js';

// Import individual panel components
import ObservatoryPanel from './panels/ObservatoryPanel';
import PersonalityMoodPanel from './panels/PersonalityMoodPanel';
import CognitionMemoryPanel from './panels/CognitionMemoryPanel';
import InteractionInterfacePanel from './panels/InteractionInterfacePanel';
import DiagnosticsRepairPanel from './panels/DiagnosticsRepairPanel';
import TaskDashboard from './panels/TaskDashboard';
import ProjectBoard from './panels/ProjectBoard';
import CalendarIntegration from './panels/CalendarIntegration';
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

  // Personal task and goal management data state
  const [taskData, setTaskData] = useState({
    tasks: [
      {
        id: 'task_1',
        title: 'Morning workout routine',
        description: '30-minute cardio session and strength training',
        priority: 'high',
        status: 'in_progress',
        createdAt: '2025-01-22T06:00:00Z',
        dueDate: '2025-01-22T08:00:00Z',
        progress: 45,
        estimatedTime: 1,
        category: 'health',
        tags: ['fitness', 'daily', 'wellness']
      },
      {
        id: 'task_2',
        title: 'Review quarterly financial goals',
        description: 'Check savings progress and investment portfolio performance',
        priority: 'medium',
        status: 'todo',
        createdAt: '2025-01-22T09:30:00Z',
        dueDate: '2025-01-23T17:00:00Z',
        progress: 0,
        estimatedTime: 2,
        category: 'finance',
        tags: ['planning', 'money', 'goals']
      },
      {
        id: 'task_3',
        title: 'Call mom for birthday planning',
        description: 'Discuss plans for mom\'s upcoming birthday celebration',
        priority: 'high',
        status: 'todo',
        createdAt: '2025-01-22T08:15:00Z',
        dueDate: '2025-01-22T19:00:00Z',
        progress: 0,
        estimatedTime: 0.5,
        category: 'family',
        tags: ['family', 'birthday', 'phone']
      },
      {
        id: 'task_4',
        title: 'Complete online course module',
        description: 'Finish Module 3: Advanced Communication Skills',
        priority: 'medium',
        status: 'completed',
        createdAt: '2025-01-21T14:00:00Z',
        completedAt: '2025-01-21T20:30:00Z',
        progress: 100,
        estimatedTime: 2,
        category: 'learning',
        tags: ['education', 'skills', 'professional']
      },
      {
        id: 'task_5',
        title: 'Organize home office desk',
        description: 'Declutter and reorganize workspace for better productivity',
        priority: 'low',
        status: 'todo',
        createdAt: '2025-01-22T07:45:00Z',
        dueDate: '2025-01-23T15:00:00Z',
        progress: 0,
        estimatedTime: 1.5,
        category: 'home',
        tags: ['organization', 'workspace', 'productivity']
      }
    ],
    goals: [
      {
        id: 'goal_1',
        name: 'Health & Fitness',
        description: 'Maintain consistent exercise routine and healthy eating habits',
        status: 'active',
        progress: 72,
        target: 'Exercise 4x per week, drink 8 glasses of water daily',
        dueDate: '2025-03-31T00:00:00Z',
        taskIds: ['task_1'],
        category: 'wellness'
      },
      {
        id: 'goal_2',
        name: 'Professional Development',
        description: 'Complete certification course and networking goals',
        status: 'active',
        progress: 45,
        target: 'Finish online certification by end of Q1',
        dueDate: '2025-03-31T00:00:00Z',
        taskIds: ['task_4'],
        category: 'career'
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
    // Initialize Alden API Service and welcome message
    const initializeAlden = async () => {
      try {
        await aldenAPIService.initialize();
        console.log('Alden API Service initialized successfully');
        
        const welcomeMessage = {
          id: Date.now(),
          type: 'system',
          content: `ALDEN MAIN SCREEN OPERATIONAL\n\nBackend Status: ${aldenAPIService.isAvailable() ? 'CONNECTED' : 'DISCONNECTED'}\nAll panels loaded successfully. System controls active.\nReady for interaction.`,
          timestamp: new Date()
        };
        setMessages([welcomeMessage]);
      } catch (error) {
        console.error('Failed to initialize Alden API Service:', error);
        const errorMessage = {
          id: Date.now(),
          type: 'system',
          content: `ALDEN MAIN SCREEN OPERATIONAL\n\nBackend Status: DISCONNECTED\nError: ${error.message}\nUI panels loaded. Backend connection failed.`,
          timestamp: new Date()
        };
        setMessages([errorMessage]);
      }
    };
    
    initializeAlden();
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
        console.warn('❌ System data update failed:', error.message);
        
        // Set default values when system monitoring is not available
        if (error.message.includes('Feature not implemented')) {
          // Keep existing static data rather than clearing it
          console.log('⚠️ Using static fallback data for system monitoring panels');
        }
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
      // Check Alden service (primary)
      const aldenHealthy = await aldenAPIService.checkHealth();
      health.alden = aldenHealthy ? 'green' : 'red';
      
      // Check other services with fallback defaults
      // Note: These endpoints may not be implemented yet
      const vaultResponse = await fetch('http://localhost:8002/api/vault/health', { method: 'GET' }).catch(() => null);
      health.vault = vaultResponse?.ok ? 'green' : 'yellow'; // Default to yellow if not available
      
      const synapseResponse = await fetch('http://localhost:8003/api/synapse/health', { method: 'GET' }).catch(() => null);
      health.synapse = synapseResponse?.ok ? 'green' : 'yellow';
      
      const coreResponse = await fetch('http://localhost:8000/api/health', { method: 'GET' }).catch(() => null);
      health.core = coreResponse?.ok ? 'green' : 'yellow';
      
      const sentryResponse = await fetch('http://localhost:8004/api/sentry/health', { method: 'GET' }).catch(() => null);
      health.sentry = sentryResponse?.ok ? 'green' : 'yellow';
      
      // Alice and Mimic status based on Alden availability (they share backend)
      health.alice = health.alden;
      health.mimic = health.alden;
      
    } catch (error) {
      console.warn('Health check failed:', error);
      // Default to yellow if health checks fail (services may not be fully implemented)
      health.alden = aldenAPIService.isAvailable() ? 'green' : 'red';
      health.alice = health.alden;
      health.mimic = health.alden;
      health.vault = 'yellow';
      health.synapse = 'yellow';
      health.core = 'yellow';
      health.sentry = 'yellow';
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
    
    // No simulations - throw clear error for unimplemented feature
    throw new Error('Feature not implemented: Real-time memory monitoring API not available. Memory statistics require backend system monitoring service.');
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
    
    // No simulations - throw clear error for unimplemented feature
    throw new Error('Feature not implemented: Real-time system health monitoring API not available. Health metrics require backend system monitoring service.');
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
      // Use Alden API Service for direct communication with Alden backend
      const result = await aldenAPIService.sendMessage(content.trim(), {
        interface: 'alden_main',
        timestamp: Date.now(),
        messageHistory: messages.slice(-5).map(msg => ({
          type: msg.type,
          content: msg.content,
          timestamp: msg.timestamp
        })) // Last 5 messages for context
      });
      
      // Display Alden's response
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: result.response || 'I received your message and am processing it.',
        timestamp: new Date(),
        metadata: result.metadata
      };
      setMessages(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      console.warn('Alden API Service unavailable:', error);
      
      // Enhanced fallback response
      const fallbackMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `I'm having trouble connecting to my backend service right now. This might be temporary - please try again in a moment. In the meantime, I can help you navigate the interface or provide general assistance with your tasks.`,
        timestamp: new Date(),
        fallback: true,
        error: error.message
      };
      setMessages(prev => [...prev, fallbackMessage]);
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

  // Handle confirmation responses (simplified for direct Alden communication)
  const handleConfirmation = async (confirmed, originalRequest) => {
    setIsTyping(true);
    
    try {
      const confirmationMessage = confirmed 
        ? `Yes, please proceed with: ${originalRequest}`
        : `No, please cancel: ${originalRequest}`;
        
      const result = await aldenAPIService.sendMessage(confirmationMessage, {
        interface: 'alden_main',
        isConfirmation: true,
        originalRequest: originalRequest,
        timestamp: Date.now()
      });
      
      const responseMessage = {
        id: Date.now(),
        type: 'assistant', 
        content: result.response,
        timestamp: new Date(),
        confirmationResult: true
      };
      setMessages(prev => [...prev, responseMessage]);
      
    } catch (error) {
      console.error('Confirmation processing failed:', error);
      const errorMessage = {
        id: Date.now(),
        type: 'assistant',
        content: confirmed 
          ? 'I apologize, but I encountered an issue processing that action.' 
          : 'Understood. I won\'t proceed with that action.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    
    setIsTyping(false);
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

  // Goal management handlers
  const handleGoalCreate = (newGoal) => {
    setTaskData(prev => ({
      ...prev,
      goals: [newGoal, ...prev.goals]
    }));
    
    // Add chat message for goal creation
    const goalMessage = {
      id: Date.now(),
      content: `🎯 New goal created: "${newGoal.name}"`,
      type: 'system',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, goalMessage]);
  };

  const handleGoalUpdate = (updatedGoal) => {
    setTaskData(prev => ({
      ...prev,
      goals: prev.goals.map(goal => 
        goal.id === updatedGoal.id ? updatedGoal : goal
      )
    }));
    
    // Add chat message for goal status changes
    if (updatedGoal.status === 'completed') {
      const completionMessage = {
        id: Date.now(),
        content: `🎊 Goal achieved: "${updatedGoal.name}"`,
        type: 'system',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, completionMessage]);
    }
  };

  // Calendar event handlers - connect to actual MCP calendar server
  const handleEventCreate = async (event) => {
    try {
      // Call MCP Gmail/Calendar server to create event
      const response = await fetch('http://localhost:8000/synapse/mcp/gmail-calendar-mcp/create_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Add system message
        const eventMessage = {
          id: Date.now(),
          content: `📅 Calendar event created: "${event.title}" on ${new Date(event.startDate).toLocaleDateString()}`,
          type: 'system',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, eventMessage]);
        
        return result;
      } else {
        throw new Error('Failed to create calendar event');
      }
    } catch (error) {
      console.error('Calendar event creation failed:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now(),
        content: `❌ Failed to create calendar event: ${error.message}`,
        type: 'error',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleEventUpdate = async (event) => {
    try {
      // Call MCP Gmail/Calendar server to update event
      const response = await fetch('http://localhost:8000/synapse/mcp/gmail-calendar-mcp/update_event', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Add system message
        const eventMessage = {
          id: Date.now(),
          content: `📅 Calendar event updated: "${event.title}"`,
          type: 'system',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, eventMessage]);
        
        return result;
      } else {
        throw new Error('Failed to update calendar event');
      }
    } catch (error) {
      console.error('Calendar event update failed:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now(),
        content: `❌ Failed to update calendar event: ${error.message}`,
        type: 'error',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleTaskSchedule = async (task, schedule) => {
    try {
      // Create a calendar event from the task
      const event = {
        title: `Task: ${task.title}`,
        description: task.description || '',
        startDate: schedule.startDate,
        endDate: schedule.endDate || new Date(new Date(schedule.startDate).getTime() + 60*60*1000), // 1 hour default
        location: schedule.location || '',
        attendees: schedule.attendees || []
      };
      
      const result = await handleEventCreate(event);
      
      if (result) {
        // Update task with calendar event ID
        const updatedTask = {
          ...task,
          calendarEventId: result.eventId,
          scheduledDate: schedule.startDate,
          status: 'scheduled'
        };
        
        await handleTaskUpdate(updatedTask);
        
        // Add system message
        const scheduleMessage = {
          id: Date.now(),
          content: `📅 Task "${task.title}" scheduled for ${new Date(schedule.startDate).toLocaleString()}`,
          type: 'system',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, scheduleMessage]);
      }
    } catch (error) {
      console.error('Task scheduling failed:', error);
      
      // Add error message
      const errorMessage = {
        id: Date.now(),
        content: `❌ Failed to schedule task: ${error.message}`,
        type: 'error',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
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
        
        <div className="panel-item" onClick={() => handlePanelExpand('goals')}>
          <div className="panel-header">
            <h3 className="panel-title">Goal Tracking</h3>
          </div>
          <div className="panel-content">
            <ProjectBoard 
              data={taskData}
              isExpanded={false}
              onGoalCreate={handleGoalCreate}
              onGoalUpdate={handleGoalUpdate}
              onTaskUpdate={handleTaskUpdate}
              mode="goals"
            />
          </div>
        </div>
        
        <div className="panel-item" onClick={() => handlePanelExpand('calendar')}>
          <div className="panel-header">
            <h3 className="panel-title">Calendar Integration</h3>
          </div>
          <div className="panel-content">
            <CalendarIntegration 
              data={taskData}
              isExpanded={false}
              onEventCreate={handleEventCreate}
              onEventUpdate={handleEventUpdate}
              onTaskSchedule={handleTaskSchedule}
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
        return <PersonalityMoodPanel isExpanded={true} />;
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
      case 'goals':
        return <ProjectBoard 
          data={taskData}
          isExpanded={true}
          onGoalCreate={handleGoalCreate}
          onGoalUpdate={handleGoalUpdate}
          onTaskUpdate={handleTaskUpdate}
          mode="goals"
        />;
      case 'calendar':
        return <CalendarIntegration 
          data={taskData}
          isExpanded={true}
          onEventCreate={handleEventCreate}
          onEventUpdate={handleEventUpdate}
          onTaskSchedule={handleTaskSchedule}
          mode="personal"
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
            {message.requiresConfirmation && (
              <div className="confirmation-buttons">
                <button 
                  className="confirm-btn yes"
                  onClick={() => handleConfirmation(true, message.originalRequest)}
                >
                  Yes, proceed
                </button>
                <button 
                  className="confirm-btn no"
                  onClick={() => handleConfirmation(false, message.originalRequest)}
                >
                  No, cancel
                </button>
              </div>
            )}
            <div className="message-timestamp">
              {message.timestamp.toLocaleTimeString()}
              {message.metadata && (
                <span className="message-source"> • via {message.metadata.source}</span>
              )}
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