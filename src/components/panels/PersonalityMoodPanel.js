import React, { useState, useEffect, useRef } from 'react';
import './PersonalityMoodPanel.css';

const PersonalityMoodPanel = ({ data, isExpanded, onExpand }) => {
  const [moodRingAnimation, setMoodRingAnimation] = useState(0);
  const canvasRef = useRef(null);

  useEffect(() => {
    // Animate mood ring based on intensity
    const interval = setInterval(() => {
      setMoodRingAnimation(prev => (prev + 1) % 360);
    }, 50);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (canvasRef.current && isExpanded) {
      drawMoodRing();
    }
  }, [data, moodRingAnimation, isExpanded]);

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

    // Draw mood intensity ring
    const intensityAngle = (data.moodIntensity / 100) * 2 * Math.PI;
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, getMoodColor(data.currentMood, 0.8));
    gradient.addColorStop(1, getMoodColor(data.currentMood, 1.0));

    ctx.strokeStyle = gradient;
    ctx.lineWidth = 8;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, intensityAngle - Math.PI / 2);
    ctx.stroke();

    // Draw pulsing light effects
    const pulseRadius = radius + Math.sin(moodRingAnimation * 0.1) * 5;
    const pulseGradient = ctx.createRadialGradient(centerX, centerY, radius - 5, centerX, centerY, pulseRadius);
    pulseGradient.addColorStop(0, getMoodColor(data.currentMood, 0.3));
    pulseGradient.addColorStop(1, getMoodColor(data.currentMood, 0.0));

    ctx.strokeStyle = pulseGradient;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(centerX, centerY, pulseRadius, 0, 2 * Math.PI);
    ctx.stroke();

    // Draw mood keyword in center
    ctx.fillStyle = getMoodColor(data.currentMood, 1.0);
    ctx.font = 'bold 24px Orbitron';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(data.currentMood.toUpperCase(), centerX, centerY - 10);

    // Draw intensity percentage
    ctx.fillStyle = 'rgba(34, 211, 238, 0.8)';
    ctx.font = '16px Orbitron';
    ctx.fillText(`${data.moodIntensity}%`, centerX, centerY + 20);
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

  if (isExpanded) {
    return (
      <div className="personality-mood-panel expanded">
        <div className="panel-header">
          <h2>Personality & Mood Analysis</h2>
          <div className="panel-subtitle">Real-time emotional state and behavioral characteristics</div>
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
                    <span className="mood-value" style={{color: getMoodColor(data.currentMood)}}>{data.currentMood.toUpperCase()}</span>
                  </div>
                  <div className="mood-intensity">
                    <span className="intensity-label">Intensity:</span>
                    <span className="intensity-value">{data.moodIntensity}/100</span>
                  </div>
                  <div className="mood-duration">
                    <span className="duration-label">Duration:</span>
                    <span className="duration-value">
                      {data.emotionalHistory.length > 0 && 
                        getTimeDelta(data.emotionalHistory[data.emotionalHistory.length - 1].timestamp)
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="emotional-history-section">
            <h3>Emotional Timeline</h3>
            <div className="emotional-timeline expanded">
              {data.emotionalHistory.map((entry, index) => (
                <div key={index} className="timeline-entry">
                  <div className="timeline-dot" style={{backgroundColor: getMoodColor(entry.mood)}}></div>
                  <div className="timeline-content">
                    <div className="timeline-mood">{entry.mood.toUpperCase()}</div>
                    <div className="timeline-intensity">{entry.intensity}%</div>
                    <div className="timeline-time">{getTimeDelta(entry.timestamp)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="traits-section">
            <h3>Personality Trait Profile</h3>
            <div className="traits-grid expanded">
              {data.traits.map((trait, index) => (
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
              ))}
            </div>
          </div>

          <div className="behavioral-bias-section">
            <h3>Behavioral Bias Monitor</h3>
            <div className="bias-list expanded">
              {data.behavioralBiases.map((bias, index) => (
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
              ))}
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
              background: `conic-gradient(${getMoodColor(data.currentMood)} ${data.moodIntensity * 3.6}deg, rgba(34, 211, 238, 0.2) 0deg)`
            }}
          >
            <div className="mood-center">
              <div className="mood-text">{data.currentMood.toUpperCase()}</div>
              <div className="mood-percentage">{data.moodIntensity}%</div>
            </div>
          </div>
        </div>

        <div className="compact-traits">
          <div className="traits-list">
            {data.traits.slice(0, 3).map((trait, index) => (
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
            ))}
          </div>
        </div>

        <div className="compact-status">
          <div className="status-indicators">
            <div className="status-item">
              <span className="status-label">Biases Active:</span>
              <span className="status-value">
                {data.behavioralBiases.filter(b => b.active).length}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Mood Changes:</span>
              <span className="status-value">{data.emotionalHistory.length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonalityMoodPanel;