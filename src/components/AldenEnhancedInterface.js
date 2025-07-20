import React, { useState, useEffect, useRef } from 'react';
import './AldenInterface_StarCraft.css';
import Dashboard from './Dashboard';

const AldenEnhancedInterface = ({ accessibilitySettings, onVoiceCommand }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [systemStatus, setSystemStatus] = useState({
    llm_available: false,
    database_available: false,
    vector_db_available: false,
    knowledge_graph_available: false,
    backend_healthy: false
  });
  const [activeScreen, setActiveScreen] = useState('hub');
  const [isRadialOpen, setIsRadialOpen] = useState(false);
  const [activeSubmenu, setActiveSubmenu] = useState(null);
  const [relevantMemories, setRelevantMemories] = useState([]);
  
  const messagesEndRef = useRef(null);
  const BACKEND_URL = process.env.REACT_APP_ALDEN_BACKEND_URL || 'http://localhost:8888';

  // Initialize connection and check backend status
  useEffect(() => {
    checkBackendStatus();
    initializeAlden();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/status`);
      if (response.ok) {
        const status = await response.json();
        setSystemStatus(status);
        setIsConnected(true);
      } else {
        setIsConnected(false);
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
      setIsConnected(false);
    }
  };

  const initializeAlden = async () => {
    const welcomeMessage = {
      id: 1,
      type: 'system',
      content: `🎯 ALDEN ENHANCED CONSTRUCT ONLINE
      
═══════════════════════════════════
STATUS: ${isConnected ? 'CONNECTED' : 'OFFLINE'}
VERSION: v4.0.0-Enhanced
CAPABILITIES: ${isConnected ? 'Full LLM + RAG + Knowledge Graph' : 'Limited Offline Mode'}
SESSION: ${sessionId}
═══════════════════════════════════

${isConnected ? 
`🧠 MEMORY SYSTEMS:
• Episodic Memory: Active
• Semantic Memory: Active  
• Procedural Memory: Active
• Knowledge Graph: ${systemStatus.knowledge_graph_available ? 'Online' : 'Offline'}
• Vector Database: ${systemStatus.vector_db_available ? 'Online' : 'Offline'}

🤖 LLM INTEGRATION:
• Local LLM: ${systemStatus.llm_available ? 'Available' : 'Unavailable'}
• RAG Pipeline: ${systemStatus.vector_db_available ? 'Active' : 'Inactive'}
• Context Awareness: Enhanced

Ready for natural language interaction with persistent memory.` :
`⚠️ OFFLINE MODE:
• Backend connection failed
• Using cached responses
• Limited functionality
• Memory not persistent

Please check backend connection and try again.`}`,
      timestamp: new Date(),
      memories: []
    };
    
    setMessages([welcomeMessage]);
    
    // Check backend status periodically
    const statusInterval = setInterval(checkBackendStatus, 30000); // Every 30 seconds
    return () => clearInterval(statusInterval);
  };

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
      let response;
      let memories = [];

      if (isConnected) {
        // Send to real backend
        const backendResponse = await fetch(`${BACKEND_URL}/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: content.trim(),
            session_id: sessionId,
            user_id: 'default-user-001',
            include_memory: true
          })
        });

        if (backendResponse.ok) {
          const data = await backendResponse.json();
          response = data.response;
          memories = data.relevant_memories || [];
          setRelevantMemories(memories);
          
          // Update system status with real backend data
          if (data.metadata) {
            setSystemStatus(prev => ({
              ...prev,
              llm_available: true,
              database_available: true,
              backend_healthy: true
            }));
          }
        } else {
          response = "Backend error occurred. Please try again.";
        }
      } else {
        // Fallback responses
        response = generateFallbackResponse(content);
      }

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response,
        timestamp: new Date(),
        memories: memories
      };

      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);

      // Voice feedback if enabled
      if (window.accessibility && accessibilitySettings.voiceFeedback) {
        window.accessibility.speak('New message received from Alden');
      }

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'system',
        content: `❌ CONNECTION ERROR
        
═══════════════════════════════════
ERROR: ${error.message}
TIMESTAMP: ${new Date().toISOString()}
═══════════════════════════════════

Please check your internet connection and backend status.`,
        timestamp: new Date(),
        memories: []
      };
      
      setMessages(prev => [...prev, errorMessage]);
      setIsTyping(false);
    }
  };

  const generateFallbackResponse = (input) => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('status') || lowerInput.includes('health')) {
      return `🔧 SYSTEM STATUS - OFFLINE MODE

═══════════════════════════════════
BACKEND CONNECTION: FAILED
DATABASE SYSTEMS: UNAVAILABLE
LLM INTEGRATION: OFFLINE
MEMORY PERSISTENCE: DISABLED
═══════════════════════════════════

To enable full functionality:
1. Start the Alden backend server
2. Ensure databases are running
3. Refresh this interface

Current capabilities are limited to cached responses.`;
    }
    
    if (lowerInput.includes('memory') || lowerInput.includes('remember')) {
      return `🧠 MEMORY SYSTEMS - OFFLINE

═══════════════════════════════════
EPISODIC MEMORY: Not Available
SEMANTIC MEMORY: Not Available
PROCEDURAL MEMORY: Not Available
KNOWLEDGE GRAPH: Not Available
═══════════════════════════════════

Memory systems require backend connection with:
• PostgreSQL for structured data
• Neo4j for knowledge graphs
• Qdrant for vector storage
• Redis for session management

Please restore backend connection for memory capabilities.`;
    }
    
    return `🤖 ALDEN OFFLINE MODE

═══════════════════════════════════
LIMITED FUNCTIONALITY ACTIVE
REAL-TIME LLM: UNAVAILABLE
PERSISTENT MEMORY: DISABLED
═══════════════════════════════════

I'm currently running in offline mode with limited capabilities.

To access my full AI features including:
• Natural language understanding
• Persistent memory and learning
• Knowledge graph integration
• Context-aware responses
• RAG-enhanced generation

Please ensure the backend is running and databases are connected.

Would you like me to help you with basic system diagnostics?`;
  };

  const mainMenuItems = [
    { 
      id: 'core-ops', 
      label: 'Core Ops', 
      icon: '⚙️', 
      angle: 0,
      submenu: [
        { id: 'hub', label: 'HUB', icon: '🏠' },
        { id: 'dashboard', label: 'DASHBOARD', icon: '📊' },
        { id: 'settings', label: 'SETTINGS', icon: '⚙️' }
      ]
    },
    { 
      id: 'personality', 
      label: 'Personality', 
      icon: '🧠', 
      angle: 72,
      submenu: [
        { id: 'traits', label: 'TRAITS', icon: '🎭' },
        { id: 'adaptation', label: 'ADAPTATION', icon: '🔄' },
        { id: 'learning', label: 'LEARNING', icon: '🎓' }
      ]
    },
    { 
      id: 'observatory', 
      label: 'Observatory', 
      icon: '🔭', 
      angle: 144,
      submenu: [
        { id: 'monitoring', label: 'MONITORING', icon: '📡' },
        { id: 'analysis', label: 'ANALYSIS', icon: '🔍' },
        { id: 'insights', label: 'INSIGHTS', icon: '💡' }
      ]
    },
    { 
      id: 'system', 
      label: 'System', 
      icon: '💻', 
      angle: 216,
      submenu: [
        { id: 'memory', label: 'MEMORY', icon: '🧠' },
        { id: 'knowledge', label: 'KNOWLEDGE', icon: '📚' },
        { id: 'diagnostics', label: 'DIAGNOSTICS', icon: '🔧' }
      ]
    },
    { 
      id: 'identity', 
      label: 'Identity', 
      icon: '👤', 
      angle: 288,
      submenu: [
        { id: 'profile', label: 'PROFILE', icon: '📋' },
        { id: 'preferences', label: 'PREFERENCES', icon: '⚙️' },
        { id: 'history', label: 'HISTORY', icon: '📜' }
      ]
    }
  ];

  const getRadialPosition = (angle, radius) => {
    const radian = (angle * Math.PI) / 180;
    const x = Math.cos(radian - Math.PI / 2) * radius;
    const y = Math.sin(radian - Math.PI / 2) * radius;
    return { x, y };
  };

  const renderConnectionStatus = () => (
    <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
      <div className="status-indicator">
        <div className={`status-dot ${isConnected ? 'online' : 'offline'}`}></div>
        <span>{isConnected ? 'CONNECTED' : 'OFFLINE'}</span>
      </div>
      {isConnected && (
        <div className="backend-status">
          <div className="status-grid">
            <div className={`status-item ${systemStatus.llm_available ? 'active' : 'inactive'}`}>
              LLM: {systemStatus.llm_available ? 'ON' : 'OFF'}
            </div>
            <div className={`status-item ${systemStatus.database_available ? 'active' : 'inactive'}`}>
              DB: {systemStatus.database_available ? 'ON' : 'OFF'}
            </div>
            <div className={`status-item ${systemStatus.vector_db_available ? 'active' : 'inactive'}`}>
              VDB: {systemStatus.vector_db_available ? 'ON' : 'OFF'}
            </div>
            <div className={`status-item ${systemStatus.knowledge_graph_available ? 'active' : 'inactive'}`}>
              KG: {systemStatus.knowledge_graph_available ? 'ON' : 'OFF'}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderMemoryPanel = () => (
    <div className="memory-panel">
      <h4>RELEVANT MEMORIES</h4>
      {relevantMemories.length > 0 ? (
        <div className="memory-items">
          {relevantMemories.map((memory, index) => (
            <div key={index} className="memory-item">
              <div className="memory-type">{memory.slice_type?.toUpperCase()}</div>
              <div className="memory-content">{memory.content}</div>
              <div className="memory-meta">
                <span className="memory-importance">
                  Importance: {(memory.importance * 100).toFixed(1)}%
                </span>
                <span className="memory-time">
                  {new Date(memory.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-memories">No relevant memories for current context</div>
      )}
    </div>
  );

  const renderScreen = () => {
    switch (activeScreen) {
      case 'hub':
        return (
          <div className="starcraft-screen">
            <div className="screen-header">
              <h2 className="screen-title">ALDEN'S <span className="glow-text">HUB</span></h2>
              <div className="screen-subtitle">ACTIVE OPERATIONAL COUNT</div>
            </div>
            
            {renderConnectionStatus()}
            
            {/* Observatory Section inspired by design mockups */}
            <div className="observatory-section">
              <h3 className="section-title">Observatory</h3>
              <div className="observatory-grid">
                <div className="observatory-card primary">
                  <div className="card-header">CORE PERSONALITY SNAPSHOT</div>
                  <div className="personality-ring">
                    <div className="ring-center">
                      <span className="personality-score">85%</span>
                      <span className="personality-label">Efficacy</span>
                    </div>
                  </div>
                  <div className="trait-breakdown">
                    <div className="trait-item">
                      <span>Conscientiousness</span>
                      <div className="trait-bar">
                        <div className="trait-fill" style={{width: '85%'}}></div>
                      </div>
                    </div>
                    <div className="trait-item">
                      <span>Empathy</span>
                      <div className="trait-bar">
                        <div className="trait-fill" style={{width: '80%'}}></div>
                      </div>
                    </div>
                    <div className="trait-item">
                      <span>Curiosity</span>
                      <div className="trait-bar">
                        <div className="trait-fill" style={{width: '90%'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="observatory-card">
                  <div className="card-header">PRIORITY ALERTS</div>
                  <div className="alert-item">
                    <div className="alert-dot green"></div>
                    <span>System diagnostics clean</span>
                  </div>
                  <div className="alert-item">
                    <div className="alert-dot blue"></div>
                    <span>Memory persistence active</span>
                  </div>
                  <div className="alert-item">
                    <div className="alert-dot green"></div>
                    <span>Learning algorithms operational</span>
                  </div>
                </div>
                
                <div className="observatory-card">
                  <div className="card-header">KEY GOAL STATUS</div>
                  <div className="goal-item">
                    <span>Expand knowledge base</span>
                    <div className="goal-progress">
                      <div className="progress-fill" style={{width: '60%'}}></div>
                    </div>
                  </div>
                  <div className="goal-item">
                    <span>Enhance response quality</span>
                    <div className="goal-progress">
                      <div className="progress-fill" style={{width: '85%'}}></div>
                    </div>
                  </div>
                  <div className="goal-item">
                    <span>Build trust relationship</span>
                    <div className="goal-progress">
                      <div className="progress-fill" style={{width: '75%'}}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="capabilities-grid">
              <div className="capability-card active">
                <div className="capability-icon">🧠</div>
                <div className="capability-name">Memory Systems</div>
                <div className="capability-status">
                  {isConnected ? 'Active' : 'Offline'}
                </div>
                <div className="capability-detail">
                  {relevantMemories.length} memories stored
                </div>
              </div>
              
              <div className="capability-card active">
                <div className="capability-icon">🤖</div>
                <div className="capability-name">LLM Integration</div>
                <div className="capability-status">
                  {systemStatus.llm_available ? 'Available' : 'Unavailable'}
                </div>
                <div className="capability-detail">
                  Real-time processing
                </div>
              </div>
              
              <div className="capability-card">
                <div className="capability-icon">📊</div>
                <div className="capability-name">Analytics Engine</div>
                <div className="capability-status">
                  {systemStatus.database_available ? 'Online' : 'Offline'}
                </div>
                <div className="capability-detail">
                  SQLite database active
                </div>
              </div>
              
              <div className="capability-card">
                <div className="capability-icon">🔍</div>
                <div className="capability-name">Search & Recall</div>
                <div className="capability-status">
                  {isConnected ? 'Active' : 'Inactive'}
                </div>
                <div className="capability-detail">
                  Context-aware retrieval
                </div>
              </div>
            </div>
          </div>
        );
      
      case 'dashboard':
        return (
          <div className="starcraft-screen dashboard-screen">
            <Dashboard 
              accessibilitySettings={accessibilitySettings}
              onVoiceCommand={onVoiceCommand}
              currentAgent="alden"
            />
          </div>
        );
      
      case 'memory':
        return (
          <div className="starcraft-screen">
            <div className="screen-header">
              <h2 className="screen-title">MEMORY <span className="glow-text">SYSTEMS</span></h2>
              <div className="screen-subtitle">Persistent Learning & Knowledge</div>
            </div>
            {renderMemoryPanel()}
          </div>
        );
      
      default:
        return (
          <div className="starcraft-screen">
            <div className="screen-header">
              <h2 className="screen-title">{menuItems.find(item => item.id === activeScreen)?.label || 'UNKNOWN'}</h2>
              <div className="screen-subtitle">Module Under Development</div>
            </div>
            <div className="development-notice">
              <p>This module is currently under development.</p>
              <p>Full functionality will be available in a future update.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="alden-starcraft-interface">
      {/* Radial Menu - PROPERLY POSITIONED */}
      <div className={`radial-menu-container ${isRadialOpen ? 'open' : ''}`}>
        <button
          onClick={() => setIsRadialOpen(!isRadialOpen)}
          className={`radial-menu-button ${isRadialOpen ? 'active' : ''}`}
        >
          <div className="radial-menu-core">
            {isRadialOpen ? '✕' : '●'}
          </div>
        </button>
        
{isRadialOpen && (
          <>
            <div className="radial-overlay" onClick={() => {
              setIsRadialOpen(false);
              setActiveSubmenu(null);
            }} />
            <div className="radial-menu-items">
              <div className="radial-glow-rings">
                <div className="glow-ring ring-1"></div>
                <div className="glow-ring ring-2"></div>
                <div className="glow-ring ring-3"></div>
              </div>
              
              {/* Main Menu Items */}
              {!activeSubmenu && mainMenuItems.map((item, index) => {
                const { x, y } = getRadialPosition(item.angle, 80);
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
                      onClick={() => setActiveSubmenu(item.id)}
                      className="menu-item-button"
                    >
                      <div className="menu-item-icon">{item.icon}</div>
                      <div className="menu-item-label">{item.label}</div>
                    </button>
                  </div>
                );
              })}
              
              {/* Submenu Items */}
              {activeSubmenu && (() => {
                const parentMenu = mainMenuItems.find(m => m.id === activeSubmenu);
                return (
                  <>
                    {/* Back Button */}
                    <div
                      className="radial-menu-item"
                      style={{
                        transform: `translate(0px, 0px)`
                      }}
                    >
                      <button
                        onClick={() => setActiveSubmenu(null)}
                        className="menu-item-button back-button"
                      >
                        <div className="menu-item-icon">←</div>
                        <div className="menu-item-label">BACK</div>
                      </button>
                    </div>
                    
                    {/* Submenu Items */}
                    {parentMenu?.submenu.map((subItem, index) => {
                      const { x, y } = getRadialPosition(index * (360 / parentMenu.submenu.length), 80);
                      const isActive = activeScreen === subItem.id;
                      return (
                        <div
                          key={subItem.id}
                          className="radial-menu-item"
                          style={{
                            transform: `translate(${x}px, ${y}px)`,
                            transitionDelay: `${index * 100}ms`
                          }}
                        >
                          <button
                            onClick={() => {
                              setActiveScreen(subItem.id);
                              setIsRadialOpen(false);
                              setActiveSubmenu(null);
                            }}
                            className={`menu-item-button ${isActive ? 'active' : ''}`}
                          >
                            <div className="menu-item-icon">{subItem.icon}</div>
                            <div className="menu-item-label">{subItem.label}</div>
                          </button>
                        </div>
                      );
                    })}
                  </>
                );
              })()}
            </div>
          </>
        )}
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Top Screen */}
        <div className="top-screen">
          {renderScreen()}
        </div>

        {/* Chat Interface */}
        <div className="chat-interface">
          <div className="chat-header">
            <h3 className="chat-title">ENHANCED <span className="glow-text">INTERFACE</span></h3>
            <div className={`chat-status ${isConnected ? 'online' : 'offline'}`}>
              {isConnected ? 'ONLINE' : 'OFFLINE'}
            </div>
          </div>
          
          <div className="messages-container">
            {messages.map(message => (
              <div key={message.id} className={`message ${message.type}`}>
                <div className="message-content">{message.content}</div>
                <div className="message-timestamp">
                  {message.timestamp.toLocaleTimeString()}
                </div>
                {message.memories && message.memories.length > 0 && (
                  <div className="message-memories">
                    <small>Referenced {message.memories.length} memory slice(s)</small>
                  </div>
                )}
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
                placeholder={isConnected ? "Ask me anything..." : "Backend offline - limited functionality"}
                className="message-input"
                rows="2"
                disabled={isTyping}
              />
              <button 
                onClick={() => handleSendMessage(inputValue)}
                disabled={!inputValue.trim() || isTyping}
                className="send-button"
              >
                {isTyping ? 'PROCESSING...' : 'TRANSMIT'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AldenEnhancedInterface;