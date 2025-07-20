import React, { useState, useEffect } from 'react';
import './ClaudeGoogleDelegation.css';

const ClaudeGoogleDelegation = () => {
  const [task, setTask] = useState('');
  const [context, setContext] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [delegationResult, setDelegationResult] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [error, setError] = useState(null);
  const [delegationMetrics, setDelegationMetrics] = useState(null);

  // Load API status and metrics on component mount
  useEffect(() => {
    loadApiStatus();
    loadDelegationMetrics();
    // Refresh status every 30 seconds
    const interval = setInterval(() => {
      loadApiStatus();
      loadDelegationMetrics();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadApiStatus = async () => {
    try {
      const status = await window.electronAPI.googleApiStatus();
      setApiStatus(status.rateLimitInfo);
    } catch (err) {
      console.error('Error loading API status:', err);
    }
  };

  const loadDelegationMetrics = async () => {
    try {
      const metrics = await window.electronAPI.getDelegationMetrics();
      if (metrics.success) {
        setDelegationMetrics(metrics);
      }
    } catch (err) {
      console.error('Error loading delegation metrics:', err);
    }
  };

  const delegateTask = async () => {
    if (!task.trim()) {
      setError('Please enter a task to delegate');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setDelegationResult(null);

      const taskData = {
        task: task.trim(),
        context: context.trim() || undefined,
        requiresReview: true
      };

      const result = await window.electronAPI.claudeDelegateToGoogle(taskData);

      if (result.success) {
        setDelegationResult(result);
        setApiStatus(result.rateLimitInfo);
        // Refresh metrics after successful delegation
        loadDelegationMetrics();
      } else {
        if (result.rateLimited) {
          setError(`Rate limit exceeded. Please wait ${Math.ceil(result.waitTime / 1000)} seconds before next request.`);
        } else {
          setError(`Delegation failed: ${result.error}`);
        }
      }
    } catch (err) {
      setError('Failed to delegate task');
      console.error('Error delegating task:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setDelegationResult(null);
    setError(null);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="claude-google-delegation">
      <div className="delegation-header">
        <h2>🤖 Claude ↔ Google AI Task Delegation</h2>
        <p>Delegate tasks from Claude Code to Google AI for analysis and recommendations</p>
      </div>

      {/* API Status */}
      {apiStatus && (
        <div className="api-status">
          <h3>API Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Remaining Requests:</span>
              <span className={`status-value ${apiStatus.remaining < 10 ? 'warning' : ''}`}>
                {apiStatus.remaining}/{apiStatus.maxRequests}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Can Make Request:</span>
              <span className={`status-value ${apiStatus.canMakeRequest ? 'success' : 'error'}`}>
                {apiStatus.canMakeRequest ? 'Yes' : 'No'}
              </span>
            </div>
            {apiStatus.waitTime > 0 && (
              <div className="status-item">
                <span className="status-label">Wait Time:</span>
                <span className="status-value warning">
                  {Math.ceil(apiStatus.waitTime / 1000)}s
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Delegation Metrics */}
      {delegationMetrics && (
        <div className="delegation-metrics">
          <h3>📊 Delegation Performance Metrics</h3>
          
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-label">Total Delegations</div>
              <div className="metric-value">{delegationMetrics.globalMetrics.totalDelegations}</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Success Rate</div>
              <div className="metric-value">{(delegationMetrics.globalMetrics.successRate * 100).toFixed(1)}%</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Avg Response Time</div>
              <div className="metric-value">{delegationMetrics.globalMetrics.averageResponseTime.toFixed(0)}ms</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Avg Quality Score</div>
              <div className="metric-value">{delegationMetrics.globalMetrics.averageQuality.toFixed(1)}/5</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Context Drift Rate</div>
              <div className="metric-value">{(delegationMetrics.globalMetrics.contextDriftRate * 100).toFixed(1)}%</div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Active Sessions</div>
              <div className="metric-value">{delegationMetrics.globalMetrics.sessionsActive}</div>
            </div>
          </div>

          {/* Recent Sessions */}
          {delegationMetrics.recentSessions && delegationMetrics.recentSessions.length > 0 && (
            <div className="recent-sessions">
              <h4>Recent Delegation Sessions</h4>
              <div className="sessions-table">
                <div className="sessions-header">
                  <span>Task</span>
                  <span>Type</span>
                  <span>Response Time</span>
                  <span>Quality</span>
                  <span>Context Drift</span>
                  <span>Status</span>
                </div>
                {delegationMetrics.recentSessions.slice(0, 5).map(session => (
                  <div key={session.id} className="session-row">
                    <span className="task-preview" title={session.task}>
                      {session.task.substring(0, 40)}...
                    </span>
                    <span className="task-type">{session.taskType}</span>
                    <span className="response-time">
                      {session.responseTime ? `${session.responseTime}ms` : 'N/A'}
                    </span>
                    <span className="quality-score">
                      {session.qualityScore ? `${session.qualityScore.toFixed(1)}/5` : 'N/A'}
                    </span>
                    <span className={`context-drift ${session.contextDrift || 'none'}`}>
                      {session.contextDrift || 'none'}
                    </span>
                    <span className={`status ${session.success ? 'success' : 'failed'}`}>
                      {session.success ? '✅' : '❌'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Task Input */}
      <div className="task-input-section">
        <h3>Task Delegation</h3>
        
        <div className="input-group">
          <label htmlFor="task">Task to Delegate:</label>
          <textarea
            id="task"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Enter the task you want to delegate to Google AI..."
            rows={3}
            className="task-input"
          />
        </div>

        <div className="input-group">
          <label htmlFor="context">Additional Context (Optional):</label>
          <textarea
            id="context"
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Provide any additional context that might help with the task..."
            rows={2}
            className="context-input"
          />
        </div>

        <div className="button-group">
          <button 
            onClick={delegateTask}
            disabled={isLoading || !task.trim() || (apiStatus && !apiStatus.canMakeRequest)}
            className="delegate-btn"
          >
            {isLoading ? 'Delegating Task...' : 'Delegate to Google AI'}
          </button>
          
          {delegationResult && (
            <button onClick={clearResults} className="clear-btn">
              Clear Results
            </button>
          )}
          
          <button onClick={loadApiStatus} className="refresh-status-btn">
            Refresh Status
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-section">
          <h3>⚠️ Error</h3>
          <div className="error-message">{error}</div>
        </div>
      )}

      {/* Delegation Results */}
      {delegationResult && (
        <div className="delegation-results">
          <h3>📋 Delegation Results</h3>
          
          <div className="result-meta">
            <div className="meta-item">
              <strong>Task:</strong> {delegationResult.task}
            </div>
            <div className="meta-item">
              <strong>Delegated At:</strong> {formatTimestamp(delegationResult.delegatedAt)}
            </div>
            <div className="meta-item">
              <strong>Requires Review:</strong> 
              <span className={delegationResult.requiresReview ? 'review-required' : 'review-not-required'}>
                {delegationResult.requiresReview ? 'Yes' : 'No'}
              </span>
            </div>
          </div>

          <div className="google-response-section">
            <h4>🤖 Google AI Response:</h4>
            <div className="google-response">
              {delegationResult.googleResponse}
            </div>
          </div>

          {delegationResult.requiresReview && (
            <div className="review-section">
              <h4>👨‍💻 Claude Code Review</h4>
              <div className="review-placeholder">
                <p><em>This is where Claude Code would review the Google AI response and provide implementation guidance.</em></p>
                <p><strong>Next Steps:</strong></p>
                <ul>
                  <li>Analyze the Google AI recommendations</li>
                  <li>Validate the approach against project requirements</li>
                  <li>Implement the suggested solutions</li>
                  <li>Test and validate the implementation</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Example Tasks */}
      <div className="example-tasks">
        <h3>💡 Example Tasks</h3>
        <div className="example-grid">
          <button 
            onClick={() => setTask('Analyze the current Hearthlink architecture and suggest performance optimizations')}
            className="example-btn"
          >
            Performance Analysis
          </button>
          <button 
            onClick={() => setTask('Design a robust error handling strategy for multi-agent communication')}
            className="example-btn"
          >
            Error Handling Design
          </button>
          <button 
            onClick={() => setTask('Recommend security best practices for external API integration')}
            className="example-btn"
          >
            Security Recommendations
          </button>
          <button 
            onClick={() => setTask('Suggest UI/UX improvements for the Conference System interface')}
            className="example-btn"
          >
            UI/UX Analysis
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClaudeGoogleDelegation;