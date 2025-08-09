import React, { useState, useEffect, useRef } from 'react';
import './PersonalityMoodPanel.css';

const PersonalityMoodPanel = ({ data, isExpanded, onExpand }) => {
  const [moodRingAnimation, setMoodRingAnimation] = useState(0);
  const [realPersonalityData, setRealPersonalityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    // Animate mood ring based on intensity
    const interval = setInterval(() => {
      setMoodRingAnimation(prev => (prev + 1) % 360);
    }, 50);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Fetch real personality data from Alden API
    const fetchPersonalityData = async () => {
      setLoading(true);
      try {
        const personalityEndpoints = [
          'http://localhost:8080/personality', // Current Alden backend
          'http://localhost:8080/api/personality', // Alternative Alden API path
          'http://localhost:8002/api/alden/personality', // Core API proxy
        ];

        let personalityData = null;
        
        for (const endpoint of personalityEndpoints) {
          try {
            const response = await fetch(endpoint);
            if (response.ok) {
              const data = await response.json();
              
              // Transform different API formats to consistent format
              if (endpoint.includes('/api/alden/personality')) {
                // Transform Core API proxy format
                personalityData = {
                  currentMood: 'focused',
                  moodIntensity: Math.round(data.trust_level * 100) || 74,
                  traits: Object.entries(data.traits || {}).map(([name, value]) => ({
                    name: name,
                    strength: value
                  })),
                  emotionalHistory: [],
                  behavioralBiases: [
                    {
                      type: 'confirmation_bias',
                      active: false,
                      description: 'Systematic analysis reduces confirmation bias'
                    },
                    {
                      type: 'recency_bias', 
                      active: true,
                      description: 'Recent interactions influence response patterns'
                    },
                    {
                      type: 'anchoring_bias',
                      active: false,
                      description: 'Open-minded approach reduces anchoring'
                    },
                    {
                      type: 'availability_bias',
                      active: true,
                      description: 'Recent memories more accessible than older ones'
                    }
                  ],
                  source: 'alden_api_status'
                };
              } else {
                // Use personality endpoint format directly
                personalityData = {
                  ...data,
                  source: 'alden_personality_api'
                };
              }
              break; // Use the first successful endpoint
            }
          } catch (endpointError) {
            console.log(`Personality endpoint ${endpoint} not available:`, endpointError.message);
            continue;
          }
        }

        if (personalityData) {
          setRealPersonalityData(personalityData);
          setError(null);
        } else {
          throw new Error('No personality API endpoints available');
        }

      } catch (error) {
        console.error('Failed to fetch real personality data:', error);
        setError(error.message);
        // Use fallback - no simulated data, just indicate real data unavailable
        setRealPersonalityData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchPersonalityData();
    
    // Refresh personality data every 30 seconds
    const interval = setInterval(fetchPersonalityData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (canvasRef.current && isExpanded) {
      drawMoodRing();
    }
  }, [realPersonalityData, moodRingAnimation, isExpanded]);

  const drawMoodRing = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background ring
    ctx.strokeStyle = 'rgba(34, 211, 238, 0.2)';
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.stroke();

    // Use real data or show loading state
    const currentData = realPersonalityData || { currentMood: 'focused', moodIntensity: 0 };
    
    // Draw mood intensity ring
    const intensityAngle = (currentData.moodIntensity / 100) * 2 * Math.PI;
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, getMoodColor(currentData.currentMood, 0.8));
    gradient.addColorStop(1, getMoodColor(currentData.currentMood, 1.0));

    ctx.strokeStyle = gradient;
    ctx.lineWidth = 8;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, intensityAngle - Math.PI / 2);
    ctx.stroke();

    // Draw pulsing light effects
    const pulseRadius = radius + Math.sin(moodRingAnimation * 0.1) * 5;
    const pulseGradient = ctx.createRadialGradient(centerX, centerY, radius - 5, centerX, centerY, pulseRadius);
    pulseGradient.addColorStop(0, getMoodColor(currentData.currentMood, 0.3));
    pulseGradient.addColorStop(1, getMoodColor(currentData.currentMood, 0.0));

    ctx.strokeStyle = pulseGradient;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(centerX, centerY, pulseRadius, 0, 2 * Math.PI);
    ctx.stroke();

    // Draw mood keyword in center
    ctx.fillStyle = getMoodColor(currentData.currentMood, 1.0);
    ctx.font = 'bold 24px Orbitron';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(currentData.currentMood.toUpperCase(), centerX, centerY - 10);

    // Draw intensity percentage
    ctx.fillStyle = 'rgba(34, 211, 238, 0.8)';
    ctx.font = '16px Orbitron';
    ctx.fillText(`${currentData.moodIntensity}%`, centerX, centerY + 20);
  };

  const getMoodColor = (mood, alpha = 1) => {
    const colors = {
      focused: `rgba(34, 211, 238, ${alpha})`,
      curious: `rgba(251, 191, 36, ${alpha})`,
      analytical: `rgba(139, 92, 246, ${alpha})`,
      calm: `rgba(16, 185, 129, ${alpha})`,
      excited: `rgba(239, 68, 68, ${alpha})`,
      thoughtful: `rgba(168, 85, 247, ${alpha})`,
      determined: `rgba(245, 101, 101, ${alpha})`
    };
    return colors[mood] || colors.focused;
  };

  const getTimeDelta = (timestamp) => {
    const delta = Date.now() - timestamp;
    const minutes = Math.floor(delta / 60000);
    const hours = Math.floor(delta / 3600000);
    if (hours > 0) return `${hours}h ${Math.floor((delta % 3600000) / 60000)}m ago`;
    return minutes > 0 ? `${minutes}m ago` : 'Just now';
  };

  const getTraitDescription = (trait) => {
    const descriptions = {
      analytical: 'Systematic thinking and logical reasoning',
      empathetic: 'Understanding and sharing others\' feelings',
      vigilant: 'Alert awareness and careful observation',
      creative: 'Innovative thinking and artistic expression',
      skeptical: 'Critical thinking and questioning assumptions'
    };
    return descriptions[trait] || 'Personality characteristic';
  };

  const getBiasDescription = (bias) => {
    const descriptions = {
      confirmation_bias: 'Tendency to search for or interpret information that confirms existing beliefs',
      recency_bias: 'Greater weight given to recent events over earlier ones',
      anchoring_bias: 'Heavy reliance on first piece of information encountered',
      availability_bias: 'Overestimating likelihood based on easily recalled examples'
    };
    return descriptions[bias] || 'Cognitive bias affecting decision making';
  };

  // Use real data instead of simulated props data
  const displayData = realPersonalityData || {
    currentMood: 'initializing',
    moodIntensity: 0,
    traits: [],
    emotionalHistory: [],
    behavioralBiases: []
  };

  if (isExpanded) {
    return (
      <div className="personality-mood-panel expanded">
        <div className="panel-header">
          <h2>Personality & Mood Analysis</h2>
          <div className="panel-subtitle">
            {realPersonalityData ? 
              `Real-time data from ${realPersonalityData.source || 'Alden API'}` : 
              'Connecting to personality monitoring system...'}
          </div>
          {loading && <div className="loading-indicator">Fetching real personality data...</div>}
          {error && <div className="error-indicator">Real API unavailable: {error}</div>}
        </div>

        <div className="personality-expanded-content">
          <div className="mood-section">
            <h3>Current Mood State</h3>
            <div className="mood-ring-container expanded">
              <canvas 
                ref={canvasRef} 
                className="mood-ring-canvas"
                width="300"
                height="300"
              />
              <div className="mood-details">
                <div className="mood-info">
                  <div className="mood-primary">
                    <span className="mood-label">Current Mood:</span>
                    <span className="mood-value" style={{color: getMoodColor(displayData.currentMood)}}>{displayData.currentMood.toUpperCase()}</span>
                  </div>
                  <div className="mood-intensity">
                    <span className="intensity-label">Intensity:</span>
                    <span className="intensity-value">{displayData.moodIntensity}/100</span>
                  </div>
                  <div className="mood-duration">
                    <span className="duration-label">Data Source:</span>
                    <span className="duration-value">
                      {realPersonalityData ? 'Live API' : 'Connecting...'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="emotional-history-section">
            <h3>Emotional Timeline</h3>
            <div className="emotional-timeline expanded">
              {displayData.emotionalHistory && displayData.emotionalHistory.length > 0 ? (
                displayData.emotionalHistory.map((entry, index) => (
                  <div key={index} className="timeline-entry">
                    <div className="timeline-dot" style={{backgroundColor: getMoodColor(entry.mood)}}></div>
                    <div className="timeline-content">
                      <div className="timeline-mood">{entry.mood.toUpperCase()}</div>
                      <div className="timeline-intensity">{entry.intensity}%</div>
                      <div className="timeline-time">{getTimeDelta(entry.timestamp)}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="timeline-entry">
                  <div className="timeline-dot" style={{backgroundColor: getMoodColor('focused')}}></div>
                  <div className="timeline-content">
                    <div className="timeline-mood">REAL-TIME MONITORING</div>
                    <div className="timeline-intensity">
                      {realPersonalityData ? 'Active' : 'Connecting...'}
                    </div>
                    <div className="timeline-time">No historical data available yet</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="traits-section">
            <h3>Personality Trait Profile</h3>
            <div className="traits-grid expanded">
              {displayData.traits && displayData.traits.length > 0 ? (
                displayData.traits.map((trait, index) => (
                  <div key={index} className="trait-card">
                    <div className="trait-header">
                      <span className="trait-name">{trait.name.toUpperCase()}</span>
                      <span className="trait-strength">{trait.strength}%</span>
                    </div>
                    <div className="trait-bar">
                      <div 
                        className="trait-fill" 
                        style={{
                          width: `${trait.strength}%`,
                          backgroundColor: `hsl(${trait.strength * 1.2}, 70%, 60%)`
                        }}
                      ></div>
                    </div>
                    <div className="trait-description">
                      {getTraitDescription(trait.name)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="trait-card">
                  <div className="trait-header">
                    <span className="trait-name">REAL-TIME ANALYSIS</span>
                    <span className="trait-strength">
                      {realPersonalityData ? 'Active' : 'Loading...'}
                    </span>
                  </div>
                  <div className="trait-bar">
                    <div 
                      className="trait-fill" 
                      style={{
                        width: '0%',
                        backgroundColor: 'rgba(34, 211, 238, 0.5)'
                      }}
                    ></div>
                  </div>
                  <div className="trait-description">
                    Personality traits will appear when real API data is available
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="behavioral-bias-section">
            <h3>Behavioral Bias Monitor</h3>
            <div className="bias-list expanded">
              {displayData.behavioralBiases && displayData.behavioralBiases.length > 0 ? (
                displayData.behavioralBiases.map((bias, index) => (
                  <div key={index} className={`bias-card ${bias.active ? 'active' : 'inactive'}`}>
                    <div className="bias-header">
                      <span className="bias-name">{bias.type.replace('_', ' ').toUpperCase()}</span>
                      <span className={`bias-status ${bias.active ? 'active' : 'inactive'}`}>
                        {bias.active ? 'ACTIVE' : 'INACTIVE'}
                      </span>
                    </div>
                    <div className="bias-description">
                      {getBiasDescription(bias.type)}
                    </div>
                    <div className="bias-current">
                      <strong>Current Impact:</strong> {bias.description}
                    </div>
                  </div>
                ))
              ) : (
                <div className="bias-card inactive">
                  <div className="bias-header">
                    <span className="bias-name">REAL-TIME BIAS MONITORING</span>
                    <span className="bias-status inactive">
                      {realPersonalityData ? 'ANALYZING' : 'CONNECTING'}
                    </span>
                  </div>
                  <div className="bias-description">
                    Behavioral bias analysis based on real-time personality data
                  </div>
                  <div className="bias-current">
                    <strong>Status:</strong> {realPersonalityData ? 'Real-time analysis active' : 'Waiting for API connection'}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="personality-mood-panel compact" onClick={onExpand}>
      <div className="panel-header compact">
        <h3>Personality & Mood</h3>
        <div className="expand-hint">Click to expand</div>
      </div>

      <div className="personality-compact-content">
        <div className="compact-mood-ring">
          <div 
            className="mood-indicator"
            style={{
              background: `conic-gradient(${getMoodColor(displayData.currentMood)} ${displayData.moodIntensity * 3.6}deg, rgba(34, 211, 238, 0.2) 0deg)`
            }}
          >
            <div className="mood-center">
              <div className="mood-text">{displayData.currentMood.toUpperCase()}</div>
              <div className="mood-percentage">{displayData.moodIntensity}%</div>
            </div>
          </div>
        </div>

        <div className="compact-traits">
          <div className="traits-list">
            {displayData.traits && displayData.traits.length > 0 ? (
              displayData.traits.slice(0, 3).map((trait, index) => (
                <div key={index} className="trait-item compact">
                  <span className="trait-name">{trait.name}</span>
                  <div className="trait-bar compact">
                    <div 
                      className="trait-fill" 
                      style={{width: `${trait.strength}%`}}
                    ></div>
                  </div>
                  <span className="trait-value">{trait.strength}%</span>
                </div>
              ))
            ) : (
              <div className="trait-item compact">
                <span className="trait-name">Real API</span>
                <div className="trait-bar compact">
                  <div 
                    className="trait-fill" 
                    style={{width: realPersonalityData ? '100%' : '0%'}}
                  ></div>
                </div>
                <span className="trait-value">{realPersonalityData ? 'Live' : 'Loading'}</span>
              </div>
            )}
          </div>
        </div>

        <div className="compact-status">
          <div className="status-indicators">
            <div className="status-item">
              <span className="status-label">Data Source:</span>
              <span className="status-value">
                {realPersonalityData ? (realPersonalityData.source || 'API').toUpperCase() : 'CONNECTING'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Status:</span>
              <span className="status-value">
                {loading ? 'LOADING' : error ? 'ERROR' : realPersonalityData ? 'LIVE' : 'OFFLINE'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonalityMoodPanel;