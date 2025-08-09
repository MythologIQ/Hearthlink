import React, { useState, useEffect } from 'react';
import './VaultInterface.css';

const VaultInterface = ({ accessibilitySettings, onVoiceCommand, currentAgent }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [vaultStats, setVaultStats] = useState({
    totalMemories: 0,
    personaMemories: 0,
    communalMemories: 0,
    storageUsed: 0,
    lastBackup: null,
    integrityStatus: 'verified'
  });
  const [memories, setMemories] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize vault connection and load data
    initializeVault();
    const interval = setInterval(refreshVaultStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const initializeVault = async () => {
    try {
      // Check vault service connection
      const healthResponse = await fetch('http://localhost:8001/api/vault/health');
      setIsConnected(healthResponse.ok);
      
      if (healthResponse.ok) {
        await refreshVaultStats();
        await loadMemories();
        await loadAuditLog();
      }
    } catch (error) {
      console.error('Failed to initialize vault:', error);
      setIsConnected(false);
    }
  };

  const refreshVaultStats = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/vault/stats');
      if (response.ok) {
        const stats = await response.json();
        setVaultStats(stats);
      }
    } catch (error) {
      console.error('Failed to refresh vault stats:', error);
    }
  };

  const loadMemories = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/vault/memories');
      if (response.ok) {
        const memoriesData = await response.json();
        setMemories(memoriesData.memories || []);
      }
    } catch (error) {
      console.error('Failed to load memories:', error);
    }
  };

  const loadAuditLog = async () => {
    try {
      const response = await fetch('http://localhost:8001/api/vault/audit-log');
      if (response.ok) {
        const auditData = await response.json();
        setAuditLog(auditData.audit_log || []);
      }
    } catch (error) {
      console.error('Failed to load audit log:', error);
    }
  };

  const handleMemorySelect = (memory) => {
    setSelectedMemory(memory);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'memories') {
      loadMemories();
    } else if (tab === 'audit') {
      loadAuditLog();
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const filteredMemories = memories.filter(memory =>
    memory.id?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    memory.content?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    memory.memory_type?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    memory.persona_id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified': return '#10b981';
      case 'warning': return '#f59e0b';
      case 'error': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getMemoryTypeIcon = (type) => {
    switch (type) {
      case 'persona': return '👤';
      case 'communal': return '🌐';
      case 'knowledge': return '📚';
      case 'conversation': return '💬';
      case 'skill': return '⚡';
      case 'episodic': return '📖';
      case 'semantic': return '🧠';
      default: return '📄';
    }
  };

  return (
    <div className="vault-interface">
      {/* Header Section */}
      <div className="vault-header">
        <div className="vault-title">
          <h1>Vault Repository</h1>
          <div className="vault-subtitle">Memory & Knowledge Storage System</div>
        </div>
        <div className="vault-status">
          <div className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            <div className="status-dot"></div>
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
          <div className={`integrity-status ${vaultStats.integrityStatus}`}>
            <span>Integrity: {vaultStats.integrityStatus.toUpperCase()}</span>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="vault-nav">
        <button 
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => handleTabChange('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`nav-tab ${activeTab === 'memories' ? 'active' : ''}`}
          onClick={() => handleTabChange('memories')}
        >
          🧠 Memories
        </button>
        <button 
          className={`nav-tab ${activeTab === 'knowledge' ? 'active' : ''}`}
          onClick={() => handleTabChange('knowledge')}
        >
          📚 Knowledge Graph
        </button>
        <button 
          className={`nav-tab ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => handleTabChange('audit')}
        >
          📋 Audit Log
        </button>
        <button 
          className={`nav-tab ${activeTab === 'admin' ? 'active' : ''}`}
          onClick={() => handleTabChange('admin')}
        >
          ⚙️ Administration
        </button>
      </div>

      {/* Main Content */}
      <div className="vault-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon">🧠</div>
                <div className="stat-content">
                  <div className="stat-value">{vaultStats.totalMemories}</div>
                  <div className="stat-label">Total Memories</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">👤</div>
                <div className="stat-content">
                  <div className="stat-value">{vaultStats.personaMemories}</div>
                  <div className="stat-label">Persona Memories</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">🌐</div>
                <div className="stat-content">
                  <div className="stat-value">{vaultStats.communalMemories}</div>
                  <div className="stat-label">Communal Memories</div>
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon">💾</div>
                <div className="stat-content">
                  <div className="stat-value">{formatFileSize(vaultStats.storageUsed)}</div>
                  <div className="stat-label">Storage Used</div>
                </div>
              </div>
            </div>

            <div className="overview-panels">
              <div className="recent-activity-panel">
                <h3>Recent Activity</h3>
                <div className="activity-list">
                  {auditLog.slice(0, 5).map((entry, index) => (
                    <div key={index} className="activity-item">
                      <div className="activity-icon">
                        {entry.level === 'info' ? 'ℹ️' : 
                         entry.level === 'error' ? '❌' : 
                         entry.level === 'warning' ? '⚠️' : '👁️'}
                      </div>
                      <div className="activity-content">
                        <div className="activity-action">{entry.level.toUpperCase()}</div>
                        <div className="activity-details">{entry.message}</div>
                        <div className="activity-time">{formatTimestamp(entry.timestamp)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="system-health-panel">
                <h3>System Health</h3>
                <div className="health-indicators">
                  <div className="health-indicator">
                    <div className="indicator-label">Data Integrity</div>
                    <div className="indicator-value">
                      <div 
                        className="indicator-dot" 
                        style={{ backgroundColor: getStatusColor(vaultStats.integrityStatus) }}
                      ></div>
                      <span>{vaultStats.integrityStatus.toUpperCase()}</span>
                    </div>
                  </div>
                  <div className="health-indicator">
                    <div className="indicator-label">Last Backup</div>
                    <div className="indicator-value">
                      {vaultStats.lastBackup ? formatTimestamp(vaultStats.lastBackup) : 'Never'}
                    </div>
                  </div>
                  <div className="health-indicator">
                    <div className="indicator-label">Encryption</div>
                    <div className="indicator-value">
                      <div className="indicator-dot" style={{ backgroundColor: '#10b981' }}></div>
                      <span>AES-256</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'memories' && (
          <div className="memories-section">
            <div className="memories-toolbar">
              <div className="search-container">
                <input
                  type="text"
                  placeholder="Search memories..."
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="search-input"
                />
                <button className="search-button">🔍</button>
              </div>
              <div className="memory-actions">
                <button className="action-button primary">➕ New Memory</button>
                <button className="action-button">📤 Export</button>
                <button className="action-button">📥 Import</button>
              </div>
            </div>

            <div className="memories-content">
              <div className="memories-list">
                {filteredMemories.map((memory, index) => (
                  <div 
                    key={memory.id || index} 
                    className={`memory-item ${selectedMemory?.id === memory.id ? 'selected' : ''}`}
                    onClick={() => handleMemorySelect(memory)}
                  >
                    <div className="memory-icon">
                      {getMemoryTypeIcon(memory.memory_type)}
                    </div>
                    <div className="memory-content">
                      <div className="memory-title">{memory.id || `Memory ${index + 1}`}</div>
                      <div className="memory-meta">
                        <span className="memory-type">{memory.memory_type}</span>
                        <span className="memory-persona">{memory.persona_id || 'System'}</span>
                        <span className="memory-date">{formatTimestamp(memory.created_at)}</span>
                      </div>
                      <div className="memory-preview">
                        {memory.content ? memory.content.substring(0, 100) + '...' : 'No content available'}
                      </div>
                    </div>
                    <div className="memory-actions">
                      <button className="memory-action">👁️</button>
                      <button className="memory-action">✏️</button>
                      <button className="memory-action">🗑️</button>
                    </div>
                  </div>
                ))}
              </div>

              {selectedMemory && (
                <div className="memory-details">
                  <div className="details-header">
                    <h3>{selectedMemory.id}</h3>
                    <button className="close-details" onClick={() => setSelectedMemory(null)}>✕</button>
                  </div>
                  <div className="details-content">
                    <div className="detail-section">
                      <h4>Metadata</h4>
                      <div className="metadata-grid">
                        <div className="metadata-item">
                          <span className="metadata-label">Type:</span>
                          <span className="metadata-value">{selectedMemory.memory_type}</span>
                        </div>
                        <div className="metadata-item">
                          <span className="metadata-label">Persona:</span>
                          <span className="metadata-value">{selectedMemory.persona_id || 'System'}</span>
                        </div>
                        <div className="metadata-item">
                          <span className="metadata-label">Importance:</span>
                          <span className="metadata-value">{selectedMemory.importance}/1.0</span>
                        </div>
                        <div className="metadata-item">
                          <span className="metadata-label">Created:</span>
                          <span className="metadata-value">{formatTimestamp(selectedMemory.created_at)}</span>
                        </div>
                      </div>
                    </div>
                    <div className="detail-section">
                      <h4>Content</h4>
                      <div className="content-preview">
                        {selectedMemory.content || 'No content available'}
                      </div>
                    </div>
                    {selectedMemory.metadata && Object.keys(selectedMemory.metadata).length > 0 && (
                      <div className="detail-section">
                        <h4>Additional Metadata</h4>
                        <div className="metadata-grid">
                          {Object.entries(selectedMemory.metadata).map(([key, value]) => (
                            <div key={key} className="metadata-item">
                              <span className="metadata-label">{key}:</span>
                              <span className="metadata-value">{JSON.stringify(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'knowledge' && (
          <div className="knowledge-section">
            <div className="knowledge-visualization">
              <h3>Knowledge Graph Visualization</h3>
              <div className="graph-container">
                <div className="graph-placeholder">
                  <div className="placeholder-content">
                    <div className="placeholder-icon">🕸️</div>
                    <div className="placeholder-text">Knowledge Graph Visualization</div>
                    <div className="placeholder-subtext">Interactive Neo4j knowledge mapping coming soon</div>
                  </div>
                </div>
              </div>
            </div>
            <div className="knowledge-controls">
              <button className="graph-control">🔍 Zoom In</button>
              <button className="graph-control">🔍 Zoom Out</button>
              <button className="graph-control">🎯 Center View</button>
              <button className="graph-control">🔄 Refresh Graph</button>
            </div>
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="audit-section">
            <div className="audit-toolbar">
              <div className="audit-filters">
                <select className="filter-select">
                  <option value="">All Actions</option>
                  <option value="create">Create</option>
                  <option value="read">Read</option>
                  <option value="update">Update</option>
                  <option value="delete">Delete</option>
                </select>
                <select className="filter-select">
                  <option value="">All Agents</option>
                  <option value="alden">Alden</option>
                  <option value="alice">Alice</option>
                  <option value="mimic">Mimic</option>
                  <option value="sentry">Sentry</option>
                </select>
              </div>
              <button className="export-audit">📤 Export Log</button>
            </div>
            <div className="audit-log">
              <div className="log-header">
                <div className="log-column">Timestamp</div>
                <div className="log-column">Level</div>
                <div className="log-column">Component</div>
                <div className="log-column">Message</div>
              </div>
              <div className="log-entries">
                {auditLog.map((entry, index) => (
                  <div key={index} className="log-entry">
                    <div className="log-cell">{formatTimestamp(entry.timestamp)}</div>
                    <div className="log-cell">
                      <span className={`level-badge ${entry.level}`}>{entry.level.toUpperCase()}</span>
                    </div>
                    <div className="log-cell">{entry.component}</div>
                    <div className="log-cell">{entry.message}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'admin' && (
          <div className="admin-section">
            <div className="admin-panels">
              <div className="admin-panel">
                <h3>Backup & Recovery</h3>
                <div className="admin-actions">
                  <button className="admin-button primary">🔄 Create Backup</button>
                  <button className="admin-button">📥 Restore Backup</button>
                  <button className="admin-button">📋 Backup History</button>
                </div>
              </div>
              <div className="admin-panel">
                <h3>Data Management</h3>
                <div className="admin-actions">
                  <button className="admin-button">🔍 Verify Integrity</button>
                  <button className="admin-button">🧹 Clean Orphaned Data</button>
                  <button className="admin-button">📊 Rebuild Indexes</button>
                </div>
              </div>
              <div className="admin-panel">
                <h3>Security</h3>
                <div className="admin-actions">
                  <button className="admin-button">🔑 Rotate Encryption Keys</button>
                  <button className="admin-button">👥 Manage Access</button>
                  <button className="admin-button">🛡️ Security Audit</button>
                </div>
              </div>
              <div className="admin-panel">
                <h3>Performance</h3>
                <div className="admin-actions">
                  <button className="admin-button">⚡ Optimize Storage</button>
                  <button className="admin-button">🗜️ Compress Archives</button>
                  <button className="admin-button">📈 Performance Report</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VaultInterface;