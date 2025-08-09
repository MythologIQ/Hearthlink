/**
 * SPEC-2 Memory Debug Panel - Alden Memory Slice Inspector
 * 
 * Dashboard widget to inspect Alden's memory slices and sync status
 * Provides real-time insights into:
 * - Memory slice distribution and health
 * - Cross-agent synchronization status
 * - Task memory integration status
 * - Vault storage utilization
 */

import React, { useState, useEffect, useRef } from 'react';
import './MemoryDebugPanel.css';

const MemoryDebugPanel = ({ isActive = true, refreshInterval = 5000 }) => {
  const [memoryData, setMemoryData] = useState({
    slices: [],
    syncStatus: {},
    vaultStats: {},
    aldenMemory: {},
    totalMemories: 0,
    lastUpdated: null
  });
  
  const [selectedSlice, setSelectedSlice] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // overview, slices, sync, vault
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  const intervalRef = useRef(null);
  const wsRef = useRef(null);

  // Fetch memory debug data
  const fetchMemoryData = async () => {
    if (!isActive) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Parallel fetch of memory data
      const [slicesResponse, syncResponse, vaultResponse, aldenResponse] = await Promise.all([
        fetch('/api/debug/memory/slices', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        }),
        fetch('/api/debug/memory/sync-status', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        }),
        fetch('/api/debug/vault/stats', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        }),
        fetch('/api/debug/alden/memory', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('hearthlink_token')}`
          }
        })
      ]);

      const slicesData = slicesResponse.ok ? await slicesResponse.json() : { slices: [] };
      const syncData = syncResponse.ok ? await syncResponse.json() : { syncStatus: {} };
      const vaultData = vaultResponse.ok ? await vaultResponse.json() : { stats: {} };
      const aldenData = aldenResponse.ok ? await aldenResponse.json() : { memory: {} };

      setMemoryData({
        slices: slicesData.slices || [],
        syncStatus: syncData.syncStatus || {},
        vaultStats: vaultData.stats || {},
        aldenMemory: aldenData.memory || {},
        totalMemories: slicesData.totalMemories || 0,
        lastUpdated: new Date().toISOString()
      });

    } catch (err) {
      console.error('Failed to fetch memory data:', err);
      setError('Failed to load memory debug data');
    } finally {
      setIsLoading(false);
    }
  };

  // Setup WebSocket for real-time updates
  const setupWebSocket = () => {
    if (!isActive || wsRef.current) return;

    try {
      const wsUrl = `ws://localhost:8002/ws/debug/memory`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('Memory debug WebSocket connected');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const update = JSON.parse(event.data);
          
          setMemoryData(prev => {
            const updated = { ...prev };
            
            if (update.type === 'memory_slice_update') {
              const sliceIndex = updated.slices.findIndex(s => s.id === update.slice.id);
              if (sliceIndex >= 0) {
                updated.slices[sliceIndex] = { ...updated.slices[sliceIndex], ...update.slice };
              } else {
                updated.slices.push(update.slice);
              }
            } else if (update.type === 'sync_status_update') {
              updated.syncStatus = { ...updated.syncStatus, ...update.syncStatus };
            } else if (update.type === 'vault_stats_update') {
              updated.vaultStats = { ...updated.vaultStats, ...update.stats };
            }
            
            updated.lastUpdated = new Date().toISOString();
            return updated;
          });
        } catch (err) {
          console.error('Failed to process WebSocket message:', err);
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('Memory debug WebSocket error:', error);
      };

      wsRef.current.onclose = () => {
        console.log('Memory debug WebSocket disconnected');
        wsRef.current = null;
        
        // Attempt to reconnect after delay
        if (isActive) {
          setTimeout(setupWebSocket, 5000);
        }
      };

    } catch (err) {
      console.error('Failed to setup WebSocket:', err);
    }
  };

  // Setup polling and WebSocket
  useEffect(() => {
    if (!isActive) {
      // Cleanup when inactive
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    // Initial fetch
    fetchMemoryData();

    // Setup real-time updates
    setupWebSocket();

    // Setup polling as fallback
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchMemoryData, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isActive, autoRefresh, refreshInterval]);

  // Calculate memory health score
  const calculateHealthScore = () => {
    if (!memoryData.slices.length) return 0;
    
    const healthySlices = memoryData.slices.filter(slice => 
      slice.status === 'healthy' && slice.syncStatus === 'synced'
    ).length;
    
    return Math.round((healthySlices / memoryData.slices.length) * 100);
  };

  // Get sync status summary
  const getSyncSummary = () => {
    const agents = Object.keys(memoryData.syncStatus);
    const syncedAgents = agents.filter(agent => 
      memoryData.syncStatus[agent]?.status === 'synced'
    ).length;
    
    return {
      total: agents.length,
      synced: syncedAgents,
      percentage: agents.length > 0 ? Math.round((syncedAgents / agents.length) * 100) : 0
    };
  };

  // Format memory size
  const formatMemorySize = (bytes) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Never';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  // Render memory slice details
  const renderSliceDetails = (slice) => (
    <div className="slice-details" key={slice.id}>
      <div className="slice-header">
        <h4>{slice.name}</h4>
        <div className={`slice-status ${slice.status}`}>
          {slice.status}
        </div>
      </div>
      
      <div className="slice-metrics">
        <div className="metric">
          <label>Size:</label>
          <span>{formatMemorySize(slice.size)}</span>
        </div>
        <div className="metric">
          <label>Entries:</label>
          <span>{slice.entryCount || 0}</span>
        </div>
        <div className="metric">
          <label>Last Access:</label>
          <span>{formatTimestamp(slice.lastAccess)}</span>
        </div>
        <div className="metric">
          <label>Sync Status:</label>
          <span className={`sync-status ${slice.syncStatus}`}>
            {slice.syncStatus}
          </span>
        </div>
      </div>
      
      {slice.tags && slice.tags.length > 0 && (
        <div className="slice-tags">
          <label>Tags:</label>
          <div className="tags">
            {slice.tags.map(tag => (
              <span key={tag} className="tag">{tag}</span>
            ))}
          </div>
        </div>
      )}
      
      {slice.errors && slice.errors.length > 0 && (
        <div className="slice-errors">
          <label>Errors:</label>
          <ul>
            {slice.errors.map((error, idx) => (
              <li key={idx} className="error">{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  if (!isActive) {
    return (
      <div className="memory-debug-panel inactive">
        <div className="inactive-message">
          Memory Debug Panel - Inactive
        </div>
      </div>
    );
  }

  const healthScore = calculateHealthScore();
  const syncSummary = getSyncSummary();

  return (
    <div className="memory-debug-panel">
      <div className="panel-header">
        <div className="title-section">
          <h3>🧠 Alden Memory Debug</h3>
          <div className="last-updated">
            Last Updated: {formatTimestamp(memoryData.lastUpdated)}
          </div>
        </div>
        
        <div className="controls">
          <button
            className={`refresh-btn ${isLoading ? 'loading' : ''}`}
            onClick={fetchMemoryData}
            disabled={isLoading}
          >
            {isLoading ? '🔄' : '↻'} Refresh
          </button>
          
          <label className="auto-refresh">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto Refresh
          </label>
        </div>
      </div>

      <div className="view-mode-tabs">
        {['overview', 'slices', 'sync', 'vault'].map(mode => (
          <button
            key={mode}
            className={`tab ${viewMode === mode ? 'active' : ''}`}
            onClick={() => setViewMode(mode)}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </button>
        ))}
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="panel-content">
        {viewMode === 'overview' && (
          <div className="overview-view">
            <div className="overview-stats">
              <div className="stat-card health">
                <div className="stat-icon">💚</div>
                <div className="stat-content">
                  <div className="stat-value">{healthScore}%</div>
                  <div className="stat-label">Memory Health</div>
                </div>
              </div>
              
              <div className="stat-card memories">
                <div className="stat-icon">🗃️</div>
                <div className="stat-content">
                  <div className="stat-value">{memoryData.totalMemories}</div>
                  <div className="stat-label">Total Memories</div>
                </div>
              </div>
              
              <div className="stat-card sync">
                <div className="stat-icon">🔄</div>
                <div className="stat-content">
                  <div className="stat-value">{syncSummary.percentage}%</div>
                  <div className="stat-label">Sync Status</div>
                </div>
              </div>
              
              <div className="stat-card vault">
                <div className="stat-icon">🔒</div>
                <div className="stat-content">
                  <div className="stat-value">
                    {formatMemorySize(memoryData.vaultStats.totalSize)}
                  </div>
                  <div className="stat-label">Vault Usage</div>
                </div>
              </div>
            </div>

            <div className="quick-insights">
              <h4>Quick Insights</h4>
              <div className="insights-list">
                <div className="insight">
                  <span className="insight-icon">📊</span>
                  <span>{memoryData.slices.length} memory slices active</span>
                </div>
                <div className="insight">
                  <span className="insight-icon">🎯</span>
                  <span>{syncSummary.synced}/{syncSummary.total} agents synchronized</span>
                </div>
                <div className="insight">
                  <span className="insight-icon">⚡</span>
                  <span>
                    {memoryData.slices.filter(s => s.status === 'healthy').length} healthy slices
                  </span>
                </div>
                {memoryData.slices.some(s => s.errors?.length > 0) && (
                  <div className="insight warning">
                    <span className="insight-icon">⚠️</span>
                    <span>
                      {memoryData.slices.filter(s => s.errors?.length > 0).length} slices with errors
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {viewMode === 'slices' && (
          <div className="slices-view">
            <div className="slices-header">
              <h4>Memory Slices ({memoryData.slices.length})</h4>
              <div className="slice-filters">
                <button
                  className={selectedSlice === null ? 'active' : ''}
                  onClick={() => setSelectedSlice(null)}
                >
                  All
                </button>
                <button
                  className={selectedSlice === 'healthy' ? 'active' : ''}
                  onClick={() => setSelectedSlice('healthy')}
                >
                  Healthy
                </button>
                <button
                  className={selectedSlice === 'error' ? 'active' : ''}
                  onClick={() => setSelectedSlice('error')}
                >
                  Errors
                </button>
              </div>
            </div>
            
            <div className="slices-list">
              {memoryData.slices
                .filter(slice => {
                  if (selectedSlice === null) return true;
                  if (selectedSlice === 'healthy') return slice.status === 'healthy';
                  if (selectedSlice === 'error') return slice.errors?.length > 0;
                  return true;
                })
                .map(slice => renderSliceDetails(slice))}
            </div>
          </div>
        )}

        {viewMode === 'sync' && (
          <div className="sync-view">
            <h4>Agent Synchronization Status</h4>
            <div className="sync-agents">
              {Object.entries(memoryData.syncStatus).map(([agent, status]) => (
                <div key={agent} className="agent-sync-card">
                  <div className="agent-header">
                    <div className="agent-name">{agent}</div>
                    <div className={`sync-indicator ${status.status}`}>
                      {status.status}
                    </div>
                  </div>
                  
                  <div className="sync-details">
                    <div className="sync-metric">
                      <label>Last Sync:</label>
                      <span>{formatTimestamp(status.lastSync)}</span>
                    </div>
                    <div className="sync-metric">
                      <label>Pending Changes:</label>
                      <span>{status.pendingChanges || 0}</span>
                    </div>
                    <div className="sync-metric">
                      <label>Conflicts:</label>
                      <span className={status.conflicts > 0 ? 'error' : ''}>
                        {status.conflicts || 0}
                      </span>
                    </div>
                  </div>
                  
                  {status.errors && status.errors.length > 0 && (
                    <div className="sync-errors">
                      <label>Sync Errors:</label>
                      <ul>
                        {status.errors.map((error, idx) => (
                          <li key={idx}>{error}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {viewMode === 'vault' && (
          <div className="vault-view">
            <h4>Vault Storage Statistics</h4>
            <div className="vault-stats">
              <div className="vault-stat">
                <label>Total Size:</label>
                <span>{formatMemorySize(memoryData.vaultStats.totalSize)}</span>
              </div>
              <div className="vault-stat">
                <label>Total Files:</label>
                <span>{memoryData.vaultStats.totalFiles || 0}</span>
              </div>
              <div className="vault-stat">
                <label>Encrypted Files:</label>
                <span>{memoryData.vaultStats.encryptedFiles || 0}</span>
              </div>
              <div className="vault-stat">
                <label>Compression Ratio:</label>
                <span>{(memoryData.vaultStats.compressionRatio || 1).toFixed(2)}x</span>
              </div>
            </div>
            
            {memoryData.vaultStats.topPaths && (
              <div className="vault-paths">
                <h5>Top Storage Paths</h5>
                <div className="paths-list">
                  {memoryData.vaultStats.topPaths.map((pathData, idx) => (
                    <div key={idx} className="path-item">
                      <div className="path-name">{pathData.path}</div>
                      <div className="path-size">{formatMemorySize(pathData.size)}</div>
                      <div className="path-files">{pathData.files} files</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MemoryDebugPanel;