import React, { useState, useEffect } from 'react';
import './InteractionInterfacePanel.css';

const InteractionInterfacePanel = ({ data, isExpanded, onExpand, onVoiceToggle, voiceActive }) => {
  const [inputStreamScroll, setInputStreamScroll] = useState(0);

  useEffect(() => {
    // Auto-scroll input stream
    const interval = setInterval(() => {
      setInputStreamScroll(prev => (prev + 1) % 100);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const getInputModeIcon = (mode) => {
    const icons = {
      voice: '🎤',
      text: '⌨️',
      gesture: '👆',
      touch: '👋'
    };
    return icons[mode] || '💬';
  };

  const getInputModeColor = (mode) => {
    const colors = {
      voice: '#ef4444',
      text: '#22d3ee',
      gesture: '#fbbf24',
      touch: '#10b981'
    };
    return colors[mode] || '#6b7280';
  };

  const getTimeDelta = (timestamp) => {
    const delta = Date.now() - timestamp;
    const minutes = Math.floor(delta / 60000);
    const seconds = Math.floor((delta % 60000) / 1000);
    return minutes > 0 ? `${minutes}m ${seconds}s ago` : `${seconds}s ago`;
  };

  const getAccessibilityModeStatus = (mode, active) => {
    return active ? 'ENABLED' : 'DISABLED';
  };

  const getAccessibilityModeColor = (active) => {
    return active ? '#10b981' : '#6b7280';
  };

  if (isExpanded) {
    return (
      <div className="interaction-interface-panel expanded">
        <div className="panel-header">
          <h2>Interaction Interface</h2>
          <div className="panel-subtitle">Communication clarity, accessibility, and input/output feedback</div>
        </div>

        <div className="interaction-expanded-content">
          <div className="input-stream-section">
            <h3>Input Stream Monitor</h3>
            <div className="input-stream-container expanded">
              {data.recentInputs.map((input, index) => (
                <div key={index} className={`input-bubble ${input.mode}`}>
                  <div className="input-header">
                    <span className="input-mode-icon">
                      {getInputModeIcon(input.mode)}
                    </span>
                    <span className={`input-mode-label ${input.mode}`}>
                      {input.mode.toUpperCase()}
                    </span>
                    <span className="input-timestamp">
                      {getTimeDelta(input.timestamp)}
                    </span>
                  </div>
                  <div className="input-content">
                    {input.content}
                  </div>
                  <div className="input-meta">
                    <span className="input-confidence">
                      Confidence: {Math.round(Math.random() * 40 + 60)}%
                    </span>
                    <span className="input-processing">
                      Processed: {Math.round(Math.random() * 100 + 50)}ms
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="voice-activation-section">
            <h3>Voice Interface Control</h3>
            <div className="voice-control-container">
              <div className="voice-activation-ring expanded">
                <div className={`voice-ring-outer ${voiceActive ? 'listening' : 'idle'}`}>
                  <div className="voice-ring-middle">
                    <div className="voice-ring-inner">
                      <button 
                        className={`voice-control-button ${voiceActive ? 'active' : 'inactive'}`}
                        onClick={onVoiceToggle}
                      >
                        {voiceActive ? '🎤' : '🔇'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="voice-settings">
                <div className="voice-setting-item">
                  <label>Sensitivity</label>
                  <div className="sensitivity-slider">
                    <input 
                      type="range" 
                      min="0" 
                      max="1" 
                      step="0.1" 
                      value={data.voiceStatus.sensitivity}
                      readOnly
                    />
                    <span className="sensitivity-value">
                      {Math.round(data.voiceStatus.sensitivity * 100)}%
                    </span>
                  </div>
                </div>
                
                <div className="voice-setting-item">
                  <label>Threshold</label>
                  <div className="threshold-indicator">
                    <div className="threshold-bar">
                      <div 
                        className="threshold-fill" 
                        style={{ width: `${data.voiceStatus.threshold * 100}%` }}
                      ></div>
                      <div className="threshold-marker"></div>
                    </div>
                    <span className="threshold-value">
                      {Math.round(data.voiceStatus.threshold * 100)}%
                    </span>
                  </div>
                </div>

                <div className="voice-status-indicators">
                  <div className={`status-indicator ${voiceActive ? 'active' : 'inactive'}`}>
                    <span className="status-dot"></span>
                    <span className="status-label">
                      {voiceActive ? 'LISTENING' : 'STANDBY'}
                    </span>
                  </div>
                  <div className="audio-level">
                    <span className="audio-label">Audio Level:</span>
                    <div className="audio-bars">
                      {[...Array(8)].map((_, i) => (
                        <div 
                          key={i} 
                          className={`audio-bar ${voiceActive && Math.random() > 0.3 ? 'active' : ''}`}
                          style={{ height: `${10 + i * 5}px` }}
                        ></div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="accessibility-section">
            <h3>Accessibility Pathways</h3>
            <div className="accessibility-grid expanded">
              {Object.entries(data.accessibilityModes).map(([mode, active]) => (
                <div key={mode} className={`accessibility-mode-card ${active ? 'enabled' : 'disabled'}`}>
                  <div className="mode-header">
                    <div className={`mode-indicator ${active ? 'active' : 'inactive'}`}></div>
                    <span className="mode-name">
                      {mode.replace(/([A-Z])/g, ' $1').toUpperCase()}
                    </span>
                  </div>
                  <div className="mode-status">
                    <span className={`status-text ${active ? 'enabled' : 'disabled'}`}>
                      {getAccessibilityModeStatus(mode, active)}
                    </span>
                  </div>
                  <div className="mode-description">
                    {getModeDescription(mode)}
                  </div>
                  <div className="mode-controls">
                    <button 
                      className={`mode-toggle ${active ? 'enabled' : 'disabled'}`}
                      onClick={() => toggleAccessibilityMode(mode)}
                    >
                      {active ? 'DISABLE' : 'ENABLE'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="feedback-section">
            <h3>System Feedback & Status</h3>
            <div className="feedback-container">
              <div className="feedback-metrics">
                <div className="metric-card">
                  <div className="metric-label">Response Time</div>
                  <div className="metric-value">145ms</div>
                  <div className="metric-trend up">↗ 12%</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Recognition Accuracy</div>
                  <div className="metric-value">94.8%</div>
                  <div className="metric-trend up">↗ 2.1%</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Error Rate</div>
                  <div className="metric-value">2.1%</div>
                  <div className="metric-trend down">↘ 0.8%</div>
                </div>
              </div>
              
              <div className="system-feedback">
                <div className="feedback-item success">
                  <span className="feedback-icon">✓</span>
                  <span className="feedback-message">Voice command processed successfully</span>
                  <span className="feedback-time">2s ago</span>
                </div>
                <div className="feedback-item info">
                  <span className="feedback-icon">ℹ</span>
                  <span className="feedback-message">Accessibility mode activated</span>
                  <span className="feedback-time">15s ago</span>
                </div>
                <div className="feedback-item warning">
                  <span className="feedback-icon">⚠</span>
                  <span className="feedback-message">Audio input level low</span>
                  <span className="feedback-time">45s ago</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="interaction-interface-panel compact" onClick={onExpand}>
      <div className="panel-header compact">
        <h3>Interaction</h3>
        <div className="expand-hint">Click to expand</div>
      </div>

      <div className="interaction-compact-content">
        <div className="compact-voice-ring">
          <div className={`voice-indicator ${voiceActive ? 'listening' : 'idle'}`}>
            <button 
              className="voice-button"
              onClick={(e) => {
                e.stopPropagation();
                onVoiceToggle();
              }}
            >
              {voiceActive ? '🎤' : '🔇'}
            </button>
          </div>
        </div>

        <div className="compact-input-stream">
          <div className="recent-inputs">
            {data.recentInputs.slice(0, 2).map((input, index) => (
              <div key={index} className={`input-item compact ${input.mode}`}>
                <span className="input-icon">
                  {getInputModeIcon(input.mode)}
                </span>
                <span className="input-preview">
                  {input.content.substring(0, 20)}...
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="compact-accessibility">
          <div className="accessibility-summary">
            <span className="summary-label">Accessible:</span>
            <span className="summary-count">
              {Object.values(data.accessibilityModes).filter(Boolean).length}/
              {Object.keys(data.accessibilityModes).length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  function getModeDescription(mode) {
    const descriptions = {
      screenReader: 'Voice output for visual elements',
      highContrast: 'Enhanced visual contrast',
      largeText: 'Increased text size for readability', 
      voiceNavigation: 'Navigate using voice commands'
    };
    return descriptions[mode] || 'Accessibility enhancement';
  }

  function toggleAccessibilityMode(mode) {
    // This would be handled by parent component
    console.log(`Toggle ${mode}`);
  }
};

export default InteractionInterfacePanel;