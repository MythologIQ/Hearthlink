import React, { useState, useEffect, useRef } from 'react';
import './SuperClaudeInterface.css';

const SuperClaudeInterface = ({ isVisible, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [reasoning_mode, setReasoningMode] = useState('balanced');
  const [tools_enabled, setToolsEnabled] = useState([]);
  const [session_id, setSessionId] = useState(null);
  const [connection_status, setConnectionStatus] = useState('disconnected');
  const [backend_mode, setBackendMode] = useState('claude_code_cli');
  const messagesEndRef = useRef(null);

  const reasoning_modes = [
    { mode: 'fast', label: 'Fast', description: 'Quick responses' },
    { mode: 'balanced', label: 'Balanced', description: 'Optimal balance' },
    { mode: 'deep', label: 'Deep', description: 'Thorough analysis' },
    { mode: 'creative', label: 'Creative', description: 'Creative exploration' }
  ];

  const available_tools = [
    { id: 'code_interpreter', label: 'Code Interpreter', icon: '💻' },
    { id: 'file_manager', label: 'File Manager', icon: '📁' },
    { id: 'data_analysis', label: 'Data Analysis', icon: '📊' },
    { id: 'web_search', label: 'Web Search', icon: '🔍' }
  ];

  useEffect(() => {
    if (isVisible) {
      initializeSession();
      checkConnectionStatus();
    }
  }, [isVisible]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeSession = async () => {
    try {
      const response = await fetch('http://localhost:8005/api/superclaude/session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reasoning_mode,
          tools_enabled,
          backend_preference: backend_mode
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setConnectionStatus('connected');
        addSystemMessage(`SuperClaude session initialized (${data.backend_used})`);
      } else {
        setConnectionStatus('error');
        addSystemMessage('Failed to initialize SuperClaude session');
      }
    } catch (error) {
      setConnectionStatus('error');
      addSystemMessage(`Connection error: ${error.message}`);
    }
  };

  const checkConnectionStatus = async () => {
    try {
      const response = await fetch('http://localhost:8005/api/superclaude/status');
      const data = await response.json();
      setConnectionStatus(data.status);
      setBackendMode(data.current_backend);
    } catch (error) {
      setConnectionStatus('error');
    }
  };

  const addSystemMessage = (content) => {
    const message = {
      id: Date.now(),
      type: 'system',
      content,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, message]);
  };

  const addUserMessage = (content) => {
    const message = {
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date().toLocaleTimeString(),
      reasoning_mode,
      tools_enabled: [...tools_enabled]
    };
    setMessages(prev => [...prev, message]);
  };

  const addAssistantMessage = (content, metadata = {}) => {
    const message = {
      id: Date.now(),
      type: 'assistant',
      content,
      timestamp: new Date().toLocaleTimeString(),
      metadata
    };
    setMessages(prev => [...prev, message]);
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading || !session_id) return;

    const userMessage = inputValue;
    addUserMessage(userMessage);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8005/api/superclaude/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id,
          message: userMessage,
          reasoning_mode,
          tools_enabled,
          context: {
            hearthlink_ecosystem: true,
            alice_insights: true,
            mimic_personas: true
          }
        })
      });

      if (response.ok) {
        const data = await response.json();
        addAssistantMessage(data.response, {
          reasoning_chain: data.reasoning_chain,
          tools_used: data.tools_used,
          backend_used: data.backend_used,
          response_time: data.response_time,
          token_usage: data.token_usage
        });
      } else {
        const error = await response.json();
        addSystemMessage(`Error: ${error.message}`);
      }
    } catch (error) {
      addSystemMessage(`Request failed: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleTool = (toolId) => {
    setToolsEnabled(prev =>
      prev.includes(toolId)
        ? prev.filter(id => id !== toolId)
        : [...prev, toolId]
    );
  };

  const clearConversation = () => {
    setMessages([]);
    initializeSession();
  };

  if (!isVisible) return null;

  return (
    <div className="superclaude-overlay">
      <div className="superclaude-modal">
        <div className="superclaude-header">
          <div className="header-left">
            <h2>🧠 SuperClaude Advanced AI</h2>
            <div className={`connection-status ${connection_status}`}>
              <span className="status-dot"></span>
              <span className="status-text">
                {connection_status === 'connected' && `Connected (${backend_mode})`}
                {connection_status === 'disconnected' && 'Disconnected'}
                {connection_status === 'error' && 'Connection Error'}
              </span>
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="superclaude-controls">
          <div className="reasoning-modes">
            <label>Reasoning Mode:</label>
            <select 
              value={reasoning_mode} 
              onChange={(e) => setReasoningMode(e.target.value)}
              disabled={isLoading}
            >
              {reasoning_modes.map(mode => (
                <option key={mode.mode} value={mode.mode}>
                  {mode.label} - {mode.description}
                </option>
              ))}
            </select>
          </div>

          <div className="tools-section">
            <label>Tools:</label>
            <div className="tools-grid">
              {available_tools.map(tool => (
                <button
                  key={tool.id}
                  className={`tool-btn ${tools_enabled.includes(tool.id) ? 'active' : ''}`}
                  onClick={() => toggleTool(tool.id)}
                  disabled={isLoading}
                  title={tool.label}
                >
                  {tool.icon} {tool.label}
                </button>
              ))}
            </div>
          </div>

          <div className="session-controls">
            <button 
              className="clear-btn"
              onClick={clearConversation}
              disabled={isLoading}
            >
              🗑️ Clear
            </button>
            <button 
              className="reconnect-btn"
              onClick={initializeSession}
              disabled={isLoading}
            >
              🔄 Reconnect
            </button>
          </div>
        </div>

        <div className="superclaude-messages">
          {messages.map(message => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-header">
                <span className="message-type">
                  {message.type === 'user' && '👤 You'}
                  {message.type === 'assistant' && '🧠 SuperClaude'}
                  {message.type === 'system' && '⚙️ System'}
                </span>
                <span className="message-time">{message.timestamp}</span>
                {message.reasoning_mode && (
                  <span className="reasoning-mode-badge">{message.reasoning_mode}</span>
                )}
              </div>
              <div className="message-content">
                {message.content}
              </div>
              {message.metadata && (
                <div className="message-metadata">
                  {message.metadata.reasoning_chain && (
                    <div className="reasoning-chain">
                      <strong>Reasoning:</strong> {message.metadata.reasoning_chain}
                    </div>
                  )}
                  {message.metadata.tools_used && message.metadata.tools_used.length > 0 && (
                    <div className="tools-used">
                      <strong>Tools Used:</strong> {message.metadata.tools_used.join(', ')}
                    </div>
                  )}
                  {message.metadata.token_usage && (
                    <div className="token-usage">
                      <strong>Tokens:</strong> {message.metadata.token_usage.total}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="superclaude-input">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask SuperClaude anything... (Shift+Enter for new line)"
            disabled={isLoading || connection_status !== 'connected'}
            rows="3"
          />
          <button 
            className="send-btn"
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim() || connection_status !== 'connected'}
          >
            {isLoading ? '⏳' : '🚀'} Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default SuperClaudeInterface;