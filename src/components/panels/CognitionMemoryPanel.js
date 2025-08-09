import React, { useState, useEffect, useRef } from 'react';
import './CognitionMemoryPanel.css';

const CognitionMemoryPanel = ({ data, isExpanded, onExpand }) => {
  const [memoryVisualization, setMemoryVisualization] = useState('donut');
  const [realMemoryData, setRealMemoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const canvasRef = useRef(null);
  const embeddingCanvasRef = useRef(null);

  useEffect(() => {
    // Fetch real memory data from Alden API
    const fetchMemoryData = async () => {
      setLoading(true);
      try {
        const memoryEndpoints = [
          'http://localhost:8080/memory', // Current Alden backend
          'http://localhost:8080/api/memory', // Alternative Alden API path
          'http://localhost:8002/api/alden/memory', // Core API proxy
        ];

        let memoryData = null;
        
        for (const endpoint of memoryEndpoints) {
          try {
            const response = await fetch(endpoint);
            if (response.ok) {
              const data = await response.json();
              memoryData = data;
              break;
            }
          } catch (endpointError) {
            console.log(`Memory endpoint ${endpoint} not available:`, endpointError.message);
            continue;
          }
        }

        if (memoryData) {
          setRealMemoryData(memoryData);
          setError(null);
        } else {
          throw new Error('No memory API endpoints available');
        }

      } catch (error) {
        console.error('Failed to fetch real memory data:', error);
        setError(error.message);
        // Use fallback - no simulated data, just indicate real data unavailable
        setRealMemoryData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchMemoryData();
    
    // Refresh memory data every 15 seconds
    const interval = setInterval(fetchMemoryData, 15000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (canvasRef.current) {
      drawMemoryVisualization();
    }
    if (embeddingCanvasRef.current && isExpanded) {
      drawEmbeddingMap();
    }
  }, [realMemoryData, memoryVisualization, isExpanded]);

  const drawMemoryVisualization = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 10;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Use real data or fallback values
    const currentData = realMemoryData || {
      usage: { shortTerm: 0, longTerm: 0, embedded: 0, total: 0 }
    };

    if (memoryVisualization === 'donut') {
      // Draw donut chart for memory usage
      const total = currentData.usage.shortTerm + currentData.usage.longTerm + currentData.usage.embedded;
      let currentAngle = -Math.PI / 2;

      // Short-term memory
      const shortTermAngle = (currentData.usage.shortTerm / 100) * 2 * Math.PI;
      ctx.fillStyle = 'rgba(34, 211, 238, 0.8)';
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + shortTermAngle);
      ctx.arc(centerX, centerY, radius * 0.6, currentAngle + shortTermAngle, currentAngle, true);
      ctx.fill();
      currentAngle += shortTermAngle;

      // Long-term memory
      const longTermAngle = (currentData.usage.longTerm / 100) * 2 * Math.PI;
      ctx.fillStyle = 'rgba(16, 185, 129, 0.8)';
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + longTermAngle);
      ctx.arc(centerX, centerY, radius * 0.6, currentAngle + longTermAngle, currentAngle, true);
      ctx.fill();
      currentAngle += longTermAngle;

      // Embedded memory
      const embeddedAngle = (currentData.usage.embedded / 100) * 2 * Math.PI;
      ctx.fillStyle = 'rgba(251, 191, 36, 0.8)';
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + embeddedAngle);
      ctx.arc(centerX, centerY, radius * 0.6, currentAngle + embeddedAngle, currentAngle, true);
      ctx.fill();

      // Center text
      ctx.fillStyle = '#22d3ee';
      ctx.font = 'bold 16px Orbitron';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(`${currentData.usage.total}%`, centerX, centerY - 5);
      ctx.font = '10px Orbitron';
      ctx.fillText(realMemoryData ? 'REAL' : 'LOADING', centerX, centerY + 10);
    }
  };

  const drawEmbeddingMap = () => {
    const canvas = embeddingCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    // Clear canvas with dark background
    ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = 'rgba(34, 211, 238, 0.1)';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 20) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 20) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Use real data or fallback values
    const currentData = realMemoryData || {
      embeddingClusters: [
        { x: 30, y: 40, label: "Loading" },
        { x: 70, y: 60, label: "System" }
      ]
    };

    // Draw embedding clusters
    currentData.embeddingClusters.forEach((cluster, index) => {
      const x = (cluster.x / 100) * canvas.width;
      const y = (cluster.y / 100) * canvas.height;
      
      // Draw cluster circle with glow effect
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, 20);
      gradient.addColorStop(0, `hsla(${index * 60}, 70%, 60%, 0.8)`);
      gradient.addColorStop(1, `hsla(${index * 60}, 70%, 60%, 0.1)`);
      
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, 15, 0, 2 * Math.PI);
      ctx.fill();
      
      // Draw cluster border
      ctx.strokeStyle = `hsl(${index * 60}, 70%, 60%)`;
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Draw label
      ctx.fillStyle = '#22d3ee';
      ctx.font = '10px Orbitron';
      ctx.textAlign = 'center';
      ctx.fillText(cluster.label.toUpperCase(), x, y - 25);
    });
  };

  const getMemoryTypeIcon = (type) => {
    const icons = {
      episodic: '📅',
      semantic: '📚',
      procedural: '⚙️'
    };
    return icons[type] || '🧠';
  };

  const getTimeDelta = (timestamp) => {
    const delta = Date.now() - timestamp;
    const minutes = Math.floor(delta / 60000);
    const hours = Math.floor(delta / 3600000);
    if (hours > 0) return `${hours}h ${Math.floor((delta % 3600000) / 60000)}m ago`;
    return minutes > 0 ? `${minutes}m ago` : 'Just now';
  };

  const getImportanceColor = (importance) => {
    if (importance >= 0.8) return '#ef4444'; // Red for critical
    if (importance >= 0.6) return '#fbbf24'; // Yellow for important
    if (importance >= 0.4) return '#22d3ee'; // Cyan for moderate
    return '#6b7280'; // Gray for low
  };

  const getCognitiveLoadColor = (load) => {
    if (load >= 80) return '#ef4444';
    if (load >= 60) return '#fbbf24';
    if (load >= 40) return '#22d3ee';
    return '#10b981';
  };

  // Use real data instead of simulated props data
  const displayData = realMemoryData || {
    usage: { shortTerm: 0, longTerm: 0, embedded: 0, total: 0 },
    workingSet: [],
    cognitiveLoad: { current: 0, queueSize: 0, processingRate: 0 },
    embeddingClusters: []
  };

  if (isExpanded) {
    return (
      <div className="cognition-memory-panel expanded">
        <div className="panel-header">
          <h2>Cognition & Memory Systems</h2>
          <div className="panel-subtitle">
            {realMemoryData ? 
              `Real-time data from ${realMemoryData.source || 'Alden Memory System'}` : 
              'Connecting to memory monitoring system...'}
          </div>
          {loading && <div className="loading-indicator">Fetching real memory data...</div>}
          {error && <div className="error-indicator">Real API unavailable: {error}</div>}
        </div>

        <div className="cognition-expanded-content">
          <div className="memory-usage-section">
            <h3>Memory Usage Analysis</h3>
            <div className="memory-visualization-container">
              <div className="visualization-controls">
                <button
                  className={memoryVisualization === 'donut' ? 'active' : ''}
                  onClick={() => setMemoryVisualization('donut')}
                >
                  Donut Chart
                </button>
                <button
                  className={memoryVisualization === 'bars' ? 'active' : ''}
                  onClick={() => setMemoryVisualization('bars')}
                >
                  Bar Chart
                </button>
              </div>
              <canvas 
                ref={canvasRef} 
                className="memory-usage-canvas expanded"
                width="300"
                height="200"
              />
              <div className="memory-legend">
                <div className="legend-item">
                  <span className="legend-color short-term"></span>
                  <span>Short-term: {displayData.usage.shortTerm}%</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color long-term"></span>
                  <span>Long-term: {displayData.usage.longTerm}%</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color embedded"></span>
                  <span>Embedded: {displayData.usage.embedded}%</span>
                </div>
              </div>
            </div>
          </div>

          <div className="working-set-section">
            <h3>Current Working Set</h3>
            <div className="working-set-list expanded">
              {displayData.workingSet && displayData.workingSet.length > 0 ? (
                displayData.workingSet.map((memory, index) => (
                  <div key={memory.id} className="memory-item expanded">
                    <div className="memory-header">
                      <span className="memory-type-icon">
                        {getMemoryTypeIcon(memory.type)}
                      </span>
                      <span className={`memory-type ${memory.type}`}>
                        {memory.type.toUpperCase()}
                      </span>
                      <div
                        className="memory-importance"
                        style={{ backgroundColor: getImportanceColor(memory.importance) }}
                      >
                        {Math.round(memory.importance * 100)}%
                      </div>
                    </div>
                    <div className="memory-content">{memory.content}</div>
                    <div className="memory-meta">
                      <span className="memory-timestamp">
                        {getTimeDelta(memory.timestamp)}
                      </span>
                      <span className="memory-id">ID: {memory.id}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="memory-item expanded">
                  <div className="memory-header">
                    <span className="memory-type-icon">🧠</span>
                    <span className="memory-type system">REAL-TIME MONITORING</span>
                    <div className="memory-importance" style={{ backgroundColor: '#22d3ee' }}>
                      {realMemoryData ? 'Active' : 'Connecting'}
                    </div>
                  </div>
                  <div className="memory-content">
                    {realMemoryData ? 'No memory items in working set' : 'Waiting for memory data...'}
                  </div>
                  <div className="memory-meta">
                    <span className="memory-timestamp">Now</span>
                    <span className="memory-id">Source: Real memory system</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="cognitive-load-section">
            <h3>Cognitive Load Monitor</h3>
            <div className="cognitive-load-display">
              <div className="load-meter">
                <div className="load-bar">
                  <div 
                    className="load-fill" 
                    style={{
                      width: `${displayData.cognitiveLoad.current}%`,
                      backgroundColor: getCognitiveLoadColor(displayData.cognitiveLoad.current)
                    }}
                  ></div>
                  <div className="load-burst" style={{
                    left: `${displayData.cognitiveLoad.current}%`,
                    opacity: displayData.cognitiveLoad.current > 70 ? 1 : 0
                  }}></div>
                </div>
                <div className="load-labels">
                  <span className="load-current">{displayData.cognitiveLoad.current}%</span>
                  <span className="load-status">
                    {displayData.cognitiveLoad.current > 80 ? 'HIGH STRAIN' :
                     displayData.cognitiveLoad.current > 60 ? 'MODERATE' :
                     displayData.cognitiveLoad.current > 40 ? 'NORMAL' : 'LOW USAGE'}
                  </span>
                </div>
              </div>
              <div className="load-metrics">
                <div className="metric-item">
                  <span className="metric-label">Queue Size:</span>
                  <span className="metric-value">{displayData.cognitiveLoad.queueSize}</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Processing Rate:</span>
                  <span className="metric-value">{(displayData.cognitiveLoad.processingRate * 100).toFixed(1)}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Efficiency:</span>
                  <span className="metric-value">
                    {displayData.cognitiveLoad.current > 0 ? 
                      Math.round((displayData.cognitiveLoad.processingRate / (displayData.cognitiveLoad.current / 100)) * 100) : 0
                    }%
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="embedding-map-section">
            <h3>Vector Embedding Space</h3>
            <div className="embedding-container">
              <canvas 
                ref={embeddingCanvasRef} 
                className="embedding-map-canvas"
                width="400"
                height="250"
              />
              <div className="embedding-info">
                <div className="embedding-stats">
                  <div className="stat-item">
                    <span className="stat-label">Active Clusters:</span>
                    <span className="stat-value">{displayData.embeddingClusters.length}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Dimensionality:</span>
                    <span className="stat-value">768</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Similarity Threshold:</span>
                    <span className="stat-value">0.85</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="cognition-memory-panel compact" onClick={onExpand}>
      <div className="panel-header compact">
        <h3>Cognition & Memory</h3>
        <div className="expand-hint">Click to expand</div>
      </div>

      <div className="cognition-compact-content">
        <div className="compact-memory-usage">
          <canvas 
            ref={canvasRef} 
            className="memory-usage-canvas compact"
            width="120"
            height="80"
          />
        </div>

        <div className="compact-metrics">
          <div className="metric-row">
            <span className="metric-label">Cognitive Load:</span>
            <span 
              className="metric-value"
              style={{ color: getCognitiveLoadColor(displayData.cognitiveLoad.current) }}
            >
              {displayData.cognitiveLoad.current}%
            </span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Working Set:</span>
            <span className="metric-value">{displayData.workingSet.length} items</span>
          </div>
          <div className="metric-row">
            <span className="metric-label">Queue Size:</span>
            <span className="metric-value">{displayData.cognitiveLoad.queueSize}</span>
          </div>
        </div>

        <div className="compact-recent-memory">
          <div className="recent-memory-item">
            <span className="memory-type-indicator">
              {displayData.workingSet[0] ? getMemoryTypeIcon(displayData.workingSet[0].type) : '🧠'}
            </span>
            <span className="memory-preview">
              {displayData.workingSet[0] ? 
                `${displayData.workingSet[0].content.substring(0, 30)}...` : 
                realMemoryData ? 'No active memories' : 'Loading...'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CognitionMemoryPanel;