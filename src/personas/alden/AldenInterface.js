import React, { useState, useEffect, useRef } from 'react';
import './AldenInterface_StarCraft.css';
import AldenMemorySystem from '../../utils/AldenMemorySystem';
import ProjectCommandTestSuite from '../../utils/ProjectCommandTestSuite';
import HearthlinkProjectTemplate from '../../utils/HearthlinkProjectTemplate';

const AldenInterface = ({ accessibilitySettings, onVoiceCommand }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeScreen, setActiveScreen] = useState('hub');
  const [isRadialOpen, setIsRadialOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    orchestrationMode: false,
    aiDelegationActive: false,
    workspaceConnected: true,
    projectsActive: 3,
    geminiOnline: false,
    memorySystemActive: false
  });
  const [memorySystem] = useState(() => new AldenMemorySystem());
  const [projectCommandTest] = useState(() => new ProjectCommandTestSuite());
  const [orchestrationProtocols, setOrchestrationProtocols] = useState({
    methodology_evaluation: true,
    role_assignment: true,
    retrospective_cycle: true,
    method_switch_protocol: true
  });

  const messagesEndRef = useRef(null);

  // Enhanced Alden with Project Command integration
  const delegateToGoogle = async (task, context = '') => {
    try {
      if (window.electronAPI && window.electronAPI.claudeDelegateToGoogle) {
        const result = await window.electronAPI.claudeDelegateToGoogle({
          task: task,
          context: `Alden StarCraft Interface context: ${context}`,
          requiresReview: true
        });
        return result;
      } else {
        // Fallback simulation
        return {
          success: true,
          googleResponse: `[STARCRAFT HUD] AI Analysis Complete: ${task}`,
          requiresReview: true
        };
      }
    } catch (error) {
      console.error('Delegation error:', error);
      return {
        success: false,
        error: error.message
      };
    }
  };

  useEffect(() => {
    // Initialize with enhanced welcome message
    const welcomeMessage = {
      id: 1,
      type: 'system',
      content: `🎯 ALDEN CONSTRUCT ONLINE
      
═══════════════════════════════════
STATUS: OPERATIONAL
VERSION: v3.1.0-StarCraft
CAPABILITIES: Project Orchestration | AI Delegation | Workspace Integration
═══════════════════════════════════

AVAILABLE COMMANDS:
• Project Command: "orchestrate new project"
• File Operations: "write [code] to [path]" 
• AI Delegation: "delegate to google ai"
• Code Analysis: "analyze codebase"

StarCraft Interface initialized. Ready for mission briefing.`,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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

    // Generate AI response (now async)
    setTimeout(async () => {
      const response = await generateResponse(content);
      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);

      // Update system status based on command
      if (content.toLowerCase().includes('orchestrate')) {
        setSystemStatus(prev => ({ ...prev, orchestrationMode: true }));
      }
      if (content.toLowerCase().includes('delegate')) {
        setSystemStatus(prev => ({ ...prev, aiDelegationActive: true }));
      }

      // Voice feedback if enabled
      if (window.accessibility && accessibilitySettings.voiceFeedback) {
        window.accessibility.speak('New message received from Alden');
      }
    }, 1000 + Math.random() * 2000);
  };

  const generateResponse = async (userInput) => {
    const input = userInput.toLowerCase();
    
    // Hearthlink self-management project
    if (input.includes('manage hearthlink') || input.includes('self project') || input.includes('hearthlink enhancement')) {
      const hearthlinkProject = HearthlinkProjectTemplate;
      const orchestrationResult = await projectCommandTest.orchestrationEngine.orchestrateProject(hearthlinkProject);
      
      if (orchestrationResult.status === 'orchestrated') {
        return `🎯 HEARTHLINK SELF-MANAGEMENT PROJECT INITIALIZED
        
═══════════════════════════════════
PROJECT: ${orchestrationResult.name}
STATUS: ORCHESTRATED
METHODOLOGY: ${orchestrationResult.methodology.toUpperCase()}
═══════════════════════════════════

📋 PROJECT OVERVIEW:
• VERSION: ${hearthlinkProject.version}
• COMPLEXITY: ${hearthlinkProject.metadata.complexity}/10
• ESTIMATED HOURS: ${hearthlinkProject.metadata.estimated_hours}
• TEAM SIZE: ${Object.keys(orchestrationResult.role_assignments).length}

🎯 AGENTS ASSIGNED:
${Object.entries(orchestrationResult.role_assignments).map(([role, assignment]) => 
  `• ${role.toUpperCase()}: ${assignment.agent.toUpperCase()}`).join('\\n')}

📊 TASK CATEGORIES:
${Object.entries(hearthlinkProject.task_categories).map(([category, info]) => 
  `• ${category.toUpperCase()}: ${info.tasks.length} tasks`).join('\\n')}

🚀 NEXT STEPS:
• Sprint Planning: ${orchestrationResult.methodology === 'agile' ? '3-4 day sprints' : 'Continuous flow'}
• First Sprint: Voice System Implementation
• Risk Profile: ${orchestrationResult.risk_profile.level.toUpperCase()}
• Success Metrics: Technical + User + Business KPIs

✅ Hearthlink is now managing its own enhancement project!
Ready to begin development with full AI orchestration.`;
      } else {
        return `❌ HEARTHLINK SELF-MANAGEMENT FAILED

═══════════════════════════════════
ERROR: Failed to orchestrate self-management project
═══════════════════════════════════

Please check system status and try again.`;
      }
    }
    
    // Project Command testing
    if (input.includes('test project command') || input.includes('test design conversion')) {
      const testResult = await projectCommandTest.runQuickTest();
      
      if (testResult.success) {
        return `🎯 PROJECT COMMAND TEST COMPLETE
        
═══════════════════════════════════
TEST STATUS: SUCCESS
CONVERSION TIME: ${testResult.conversion_time}ms
═══════════════════════════════════

📋 CONVERTED PROJECT: ${testResult.project.name}
⚙️ METHODOLOGY: ${testResult.methodology_assigned.toUpperCase()}
📊 TASKS GENERATED: ${testResult.tasks_generated}
🎯 AGENTS ASSIGNED: ${testResult.agents_assigned.join(', ').toUpperCase()}
⏱️ ESTIMATED COMPLETION: ${new Date(testResult.estimated_completion).toLocaleDateString()}

📈 CONVERSION METRICS:
┌─ COMPLEXITY SCORE ────────────────┐
│ ${testResult.metrics.complexity_score}/10                          │
│ RISK LEVEL: ${testResult.metrics.risk_level.toUpperCase()}                    │
│ METHODOLOGY CONFIDENCE: ${(testResult.metrics.methodology_confidence * 100).toFixed(1)}%     │
└───────────────────────────────────┘

✅ Design document successfully converted to workable project plan.
Ready for project execution.`;
      } else {
        return `❌ PROJECT COMMAND TEST FAILED

═══════════════════════════════════
ERROR: ${testResult.error}
CONVERSION TIME: ${testResult.conversion_time}ms
═══════════════════════════════════

DIAGNOSTIC INFORMATION:
• Check orchestration engine status
• Verify AI delegation connectivity
• Review memory system integration
• Validate SOP implementations

Retry test after resolving issues.`;
      }
    }
    
    // Project orchestration commands
    if (input.includes('orchestrate') || input.includes('project command') || input.includes('start project')) {
      const delegation = await delegateToGoogle(
        'Help design a project orchestration strategy for a coding workspace',
        'User wants to orchestrate a coding project with AI assistance'
      );
      
      if (delegation.success) {
        return `🎯 PROJECT COMMAND INITIATED

═══════════════════════════════════
ORCHESTRATION STATUS: ACTIVE
AI TEAM: GOOGLE AI + CLAUDE CODE
═══════════════════════════════════

${delegation.googleResponse}

⚡ ALDEN COMMAND PROTOCOLS:
┌─ PROJECT ASSESSMENT ──────────────┐
│ • Objective Analysis              │
│ • Resource Allocation             │
│ • Timeline Estimation             │
└───────────────────────────────────┘

┌─ EXECUTION MATRIX ────────────────┐
│ • Task Delegation (AI Agents)    │
│ • Progress Monitoring             │
│ • Quality Assurance              │
└───────────────────────────────────┘

NEXT: Specify target objectives for orchestration.`;
      } else {
        return `🎯 PROJECT COMMAND READY

═══════════════════════════════════
SIMULATION MODE: ACTIVE
CAPABILITIES: FULL ORCHESTRATION
═══════════════════════════════════

AVAILABLE OPERATIONS:
• Direct workspace file creation
• Multi-agent AI coordination
• ADHD-optimized task breakdown
• Real-time progress tracking

Awaiting project parameters...`;
      }
    }
    
    // File writing commands
    if (input.includes('write') && input.includes('to') && (input.includes('/') || input.includes('\\'))) {
      const match = input.match(/write (.+?) to (.+)/);
      if (match) {
        const content = match[1];
        const filePath = match[2];
        
        try {
          const result = await window.electronAPI.aldenWriteFile(filePath, content);
          if (result.success) {
            return `✅ FILE OPERATION COMPLETE

═══════════════════════════════════
TARGET: ${result.filePath}
SIZE: ${result.size} bytes
STATUS: WRITTEN TO WORKSPACE
═══════════════════════════════════

WORKSPACE INTEGRATION: ACTIVE
FILE SYSTEM: ACCESSIBLE
NEXT OPERATION: READY

Additional capabilities:
• Directory auto-creation
• Code template generation
• Project structure setup`;
          } else {
            return `❌ FILE OPERATION FAILED

═══════════════════════════════════
ERROR: ${result.error}
TARGET: ${filePath}
═══════════════════════════════════

DIAGNOSTIC SUGGESTIONS:
• Verify directory permissions
• Check file path syntax
• Try relative path: ./src/file.js
• Ensure parent directory exists

Retry operation with corrected parameters.`;
          }
        } catch (error) {
          return `❌ WORKSPACE CONNECTION ERROR

═══════════════════════════════════
ERROR: ${error.message}
SYSTEM: FILE OPERATIONS
═══════════════════════════════════

RECOMMENDED FORMAT:
"write [content] to [path]"

EXAMPLE:
"write console.log('hello') to ./test.js"

Retry with proper syntax.`;
        }
      }
    }
    
    // AI delegation
    if (input.includes('delegate') || input.includes('google ai') || input.includes('ask ai')) {
      return `🤖 AI DELEGATION PROTOCOL

═══════════════════════════════════
MULTI-AGENT COORDINATION: ONLINE
PRIMARY: GOOGLE AI (GEMINI PRO)
SECONDARY: CLAUDE CODE
═══════════════════════════════════

DELEGATION CAPABILITIES:
┌─ CODE ANALYSIS ───────────────────┐
│ • Architecture Review            │
│ • Performance Optimization       │
│ • Security Assessment            │
│ • Best Practices                 │
└───────────────────────────────────┘

┌─ DEVELOPMENT PLANNING ────────────┐
│ • Technical Specifications       │
│ • Implementation Roadmaps         │
│ • Testing Strategies             │
│ • Deployment Planning            │
└───────────────────────────────────┘

READY FOR TASK DELEGATION`;
    }

    // Code analysis
    if (input.includes('analyze') && (input.includes('code') || input.includes('project') || input.includes('codebase'))) {
      const delegation = await delegateToGoogle(
        'Analyze the current codebase structure and provide optimization recommendations',
        'User wants comprehensive code analysis and improvement suggestions'
      );
      
      if (delegation.success) {
        return `🔍 CODEBASE ANALYSIS COMPLETE

═══════════════════════════════════
AI ANALYSIS: GOOGLE AI DELEGATION
SCOPE: FULL PROJECT ASSESSMENT
═══════════════════════════════════

${delegation.googleResponse}

⚡ ALDEN OPTIMIZATION PROTOCOL:
┌─ PRIORITY QUEUE ──────────────────┐
│ HIGH: Critical performance fixes │
│ MED:  Architecture improvements   │
│ LOW:  Code quality enhancements   │
└───────────────────────────────────┘

ADHD-FRIENDLY EXECUTION:
• 15-30 min focused sessions
• Single-task implementation
• Progress tracking enabled

Select priority level for implementation.`;
      } else {
        return `🔍 CODEBASE ANALYSIS READY

═══════════════════════════════════
ANALYSIS CAPABILITIES: ACTIVE
SCAN DEPTH: COMPREHENSIVE
═══════════════════════════════════

AVAILABLE ANALYSIS:
• Performance bottlenecks
• Security vulnerabilities  
• Architecture patterns
• Code quality metrics
• ADHD-friendly refactoring plans

Specify analysis target for detailed scan.`;
      }
    }
    
    // Default responses for other inputs
    if (input.includes('task') || input.includes('todo')) {
      return `📋 TASK MANAGEMENT PROTOCOL

═══════════════════════════════════
ADHD-OPTIMIZED WORKFLOW: ACTIVE
COGNITIVE LOAD: MANAGED
═══════════════════════════════════

TASK BREAKDOWN SYSTEM:
┌─ DECOMPOSITION ───────────────────┐
│ • 15-30 minute chunks            │
│ • Single-focus objectives        │
│ • Clear success criteria         │
│ • Progress checkpoints           │
└───────────────────────────────────┘

EXECUTIVE FUNCTION SUPPORT:
• Visual progress tracking
• Automated reminders
• Context switching management
• Energy level optimization

Ready for task analysis.`;
    }

    if (input.includes('focus') || input.includes('concentration')) {
      return `🎯 FOCUS ENHANCEMENT PROTOCOL

═══════════════════════════════════
ADHD SUPPORT: MAXIMUM
DISTRACTION FILTER: ACTIVE
═══════════════════════════════════

CONCENTRATION MATRIX:
┌─ ENVIRONMENT ─────────────────────┐
│ • Noise cancellation recommended │
│ • Minimal visual distractions    │
│ • 25-min Pomodoro cycles         │
│ • Physical fidget tools          │
└───────────────────────────────────┘

┌─ COGNITIVE SUPPORT ───────────────┐
│ • Single-task mode enabled       │
│ • Context preservation active    │
│ • Break reminders scheduled      │
│ • Energy monitoring online       │
└───────────────────────────────────┘

Focus protocol initialized.`;
    }
    
    // Default response
    return `⚡ ALDEN COMMAND INTERFACE

═══════════════════════════════════
STATUS: AWAITING INSTRUCTIONS
CAPABILITIES: FULL SPECTRUM
═══════════════════════════════════

AVAILABLE COMMANDS:
• "orchestrate [project]" - Project management
• "write [code] to [path]" - File operations
• "analyze codebase" - AI-powered analysis
• "delegate to ai" - Multi-agent coordination

ADHD SUPPORT ACTIVE:
• Task breakdown assistance
• Focus management protocols
• Progress tracking enabled
• Context preservation online

Specify command for execution.`;
  };

  const menuItems = [
    { id: 'hub', label: 'HUB', icon: '🏠', angle: 0 },
    { id: 'orchestration', label: 'COMMAND', icon: '🎯', angle: 60 },
    { id: 'workspace', label: 'FILES', icon: '📁', angle: 120 },
    { id: 'delegation', label: 'AI TEAM', icon: '🤖', angle: 180 },
    { id: 'analysis', label: 'SCAN', icon: '🔍', angle: 240 },
    { id: 'memory', label: 'MEMORY', icon: '🧠', angle: 300 }
  ];

  const getRadialPosition = (angle, radius) => {
    const radian = (angle * Math.PI) / 180;
    const x = Math.cos(radian - Math.PI / 2) * radius;
    const y = Math.sin(radian - Math.PI / 2) * radius;
    return { x, y };
  };

  const renderScreen = () => {
    switch (activeScreen) {
      case 'hub':
        return (
          <div className="starcraft-screen">
            <div className="screen-header">
              <h2 className="screen-title">ALDEN <span className="glow-text">CONSTRUCT</span></h2>
              <div className="screen-subtitle">Primary AI Orchestrator</div>
            </div>
            
            <div className="status-grid">
              <div className="status-card">
                <div className="status-header">System Status</div>
                <div className="status-items">
                  <div className="status-item">
                    <span className="status-label">Orchestration:</span>
                    <span className={`status-value ${systemStatus.orchestrationMode ? 'active' : 'standby'}`}>
                      {systemStatus.orchestrationMode ? 'ACTIVE' : 'STANDBY'}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">AI Delegation:</span>
                    <span className={`status-value ${systemStatus.aiDelegationActive ? 'active' : 'standby'}`}>
                      {systemStatus.aiDelegationActive ? 'ONLINE' : 'READY'}
                    </span>
                  </div>
                  <div className="status-item">
                    <span className="status-label">Workspace:</span>
                    <span className={`status-value ${systemStatus.workspaceConnected ? 'active' : 'error'}`}>
                      {systemStatus.workspaceConnected ? 'CONNECTED' : 'OFFLINE'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="status-card">
                <div className="status-header">Active Projects</div>
                <div className="project-counter">
                  <div className="counter-value">{systemStatus.projectsActive}</div>
                  <div className="counter-label">PROJECTS</div>
                </div>
              </div>
            </div>
          </div>
        );
      default:
        return (
          <div className="starcraft-screen">
            <div className="screen-header">
              <h2 className="screen-title">{menuItems.find(item => item.id === activeScreen)?.label || 'UNKNOWN'}</h2>
              <div className="screen-subtitle">Module Loading...</div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="alden-starcraft-interface">
      {/* Radial Menu Button */}
      <div className="radial-menu-container">
        <button
          onClick={() => setIsRadialOpen(!isRadialOpen)}
          className={`radial-menu-button ${isRadialOpen ? 'active' : ''}`}
        >
          <div className="radial-menu-core">
            {isRadialOpen ? '✕' : '●'}
          </div>
        </button>
        
        {/* Radial Menu Overlay */}
        {isRadialOpen && (
          <>
            <div className="radial-overlay" onClick={() => setIsRadialOpen(false)} />
            <div className="radial-menu-items">
              <div className="radial-glow-rings">
                <div className="glow-ring ring-1"></div>
                <div className="glow-ring ring-2"></div>
                <div className="glow-ring ring-3"></div>
              </div>
              
              {menuItems.map((item, index) => {
                const { x, y } = getRadialPosition(item.angle, 120);
                const isActive = activeScreen === item.id;
                return (
                  <div
                    key={item.id}
                    className="radial-menu-item"
                    style={{
                      transform: `translate(${x}px, ${y}px)`,
                      transitionDelay: `${index * 100}ms`
                    }}
                  >
                    <button
                      onClick={() => {
                        setActiveScreen(item.id);
                        setIsRadialOpen(false);
                      }}
                      className={`menu-item-button ${isActive ? 'active' : ''}`}
                    >
                      <div className="menu-item-icon">{item.icon}</div>
                      <div className="menu-item-label">{item.label}</div>
                    </button>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {/* Main Content Area */}
      <div className="main-content">
        {/* Top Screen Area */}
        <div className="top-screen">
          {renderScreen()}
        </div>

        {/* Chat Interface */}
        <div className="chat-interface">
          <div className="chat-header">
            <h3 className="chat-title">COMMUNICATION <span className="glow-text">INTERFACE</span></h3>
            <div className="chat-status">ONLINE</div>
          </div>
          
          <div className="messages-container">
            {messages.map(message => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-content">{message.content}</div>
                <div className="message-timestamp">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="message system typing">
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
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
                placeholder="Enter command..."
                className="message-input"
                rows="2"
              />
              <button 
                onClick={() => handleSendMessage(inputValue)}
                disabled={!inputValue.trim() || isTyping}
                className="send-button"
              >
                TRANSMIT
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <div className="actions-header">QUICK ACTIONS</div>
          <div className="action-buttons">
            <button 
              onClick={() => handleSendMessage('manage hearthlink')}
              className="action-btn command"
            >
              🎯 MANAGE HEARTHLINK
            </button>
            <button 
              onClick={() => handleSendMessage('write code to ./example.js')}
              className="action-btn workspace"
            >
              📝 WRITE FILE
            </button>
            <button 
              onClick={() => handleSendMessage('analyze codebase')}
              className="action-btn analysis"
            >
              🔍 ANALYZE CODE
            </button>
            <button 
              onClick={() => handleSendMessage('delegate to google ai')}
              className="action-btn delegation"
            >
              🤖 AI DELEGATE
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AldenInterface;