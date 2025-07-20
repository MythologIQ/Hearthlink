import React, { useState, useEffect, useRef } from 'react';
import './MimicInterface.css';

const MimicInterface = ({ isVisible, onClose }) => {
  // Core state management
  const [activeTab, setActiveTab] = useState('personas');
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Persona creation state
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createFormData, setCreateFormData] = useState({
    role: '',
    description: '',
    context: {},
    traits: {
      focus: 50,
      creativity: 50,
      precision: 50,
      humor: 25,
      empathy: 50,
      assertiveness: 50,
      adaptability: 50,
      collaboration: 50
    },
    tags: []
  });
  
  // Performance analytics state
  const [analytics, setAnalytics] = useState(null);
  const [performanceHistory, setPerformanceHistory] = useState([]);
  
  // Persona forking/merging state
  const [showForkForm, setShowForkForm] = useState(false);
  const [showMergeForm, setShowMergeForm] = useState(false);
  const [forkData, setForkData] = useState({
    sourcePersonaId: '',
    newRole: '',
    modifications: {}
  });
  
  // Plugin management state
  const [availablePlugins, setAvailablePlugins] = useState([]);
  const [selectedPlugins, setSelectedPlugins] = useState([]);
  
  // Knowledge management state
  const [knowledgeBase, setKnowledgeBase] = useState([]);
  const [showKnowledgeForm, setShowKnowledgeForm] = useState(false);
  const [knowledgeFormData, setKnowledgeFormData] = useState({
    content: '',
    tags: [],
    relevanceScore: 0.5
  });

  const canvasRef = useRef(null);

  useEffect(() => {
    if (isVisible) {
      fetchPersonas();
      fetchAvailablePlugins();
    }
  }, [isVisible]);

  useEffect(() => {
    if (selectedPersona && activeTab === 'analytics') {
      fetchPersonaAnalytics();
    }
  }, [selectedPersona, activeTab]);

  const fetchPersonas = async () => {
    setIsLoading(true);
    try {
      // Mock data for now - in real implementation would call API
      const mockPersonas = [
        {
          persona_id: 'mimic-001',
          persona_name: 'Dr. Research',
          role: 'researcher',
          description: 'Advanced research and analysis specialist',
          status: 'active',
          performance_tier: 'excellent',
          sessions_completed: 25,
          average_score: 92,
          active_plugins: 3,
          knowledge_items: 15,
          created_at: '2025-01-10T10:00:00Z',
          last_updated: '2025-01-13T15:30:00Z'
        },
        {
          persona_id: 'mimic-002',
          persona_name: 'Creative Writer',
          role: 'creative_writer',
          description: 'Specialized in storytelling and creative content',
          status: 'active',
          performance_tier: 'stable',
          sessions_completed: 18,
          average_score: 87,
          active_plugins: 2,
          knowledge_items: 8,
          created_at: '2025-01-08T14:20:00Z',
          last_updated: '2025-01-13T12:15:00Z'
        },
        {
          persona_id: 'mimic-003',
          persona_name: 'Strategy Guide',
          role: 'consultant',
          description: 'Business strategy and optimization expert',
          status: 'beta',
          performance_tier: 'beta',
          sessions_completed: 12,
          average_score: 78,
          active_plugins: 1,
          knowledge_items: 5,
          created_at: '2025-01-12T09:45:00Z',
          last_updated: '2025-01-13T11:00:00Z'
        }
      ];
      setPersonas(mockPersonas);
      if (!selectedPersona && mockPersonas.length > 0) {
        setSelectedPersona(mockPersonas[0]);
      }
    } catch (error) {
      setError('Failed to fetch personas');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchPersonaAnalytics = async () => {
    if (!selectedPersona) return;
    
    try {
      // Mock analytics data
      const mockAnalytics = {
        persona_id: selectedPersona.persona_id,
        persona_name: selectedPersona.persona_name,
        role: selectedPersona.role,
        status: selectedPersona.status,
        growth_stats: {
          sessions_completed: selectedPersona.sessions_completed,
          unique_tasks: 15,
          repeat_tasks: 10,
          usage_streak: 7,
          total_usage_time: 45.5,
          growth_rate: 0.12
        },
        total_sessions: selectedPersona.sessions_completed,
        average_score: selectedPersona.average_score,
        success_rate: 0.92,
        performance_trend: [78, 82, 85, 88, 90, 87, 92, 89, 94, 92],
        top_topics: [
          { topic: 'research_analysis', score: 0.95 },
          { topic: 'data_analytics', score: 0.88 },
          { topic: 'problem_solving', score: 0.82 }
        ],
        knowledge_coverage: 0.75,
        active_plugins: selectedPersona.active_plugins,
        plugin_performance_impact: 0.15,
        recommendations: [
          'Continue focusing on research tasks to maintain excellence',
          'Consider expanding knowledge base in emerging domains',
          'Strong performance suggests readiness for complex challenges'
        ],
        growth_opportunities: [
          'Specialize further in current high-performing areas',
          'Explore cross-domain knowledge integration',
          'Consider mentoring newer personas'
        ]
      };
      setAnalytics(mockAnalytics);
    } catch (error) {
      setError('Failed to fetch analytics');
    }
  };

  const fetchAvailablePlugins = async () => {
    try {
      // Mock plugin data
      const mockPlugins = [
        {
          plugin_id: 'research-tools',
          name: 'Advanced Research Tools',
          version: '1.2.0',
          description: 'Enhanced research capabilities with data analysis',
          permissions: ['data_access', 'api_calls'],
          performance_impact: 0.2
        },
        {
          plugin_id: 'creative-enhancer',
          name: 'Creative Writing Enhancer',
          version: '1.0.5',
          description: 'Advanced creative writing and storytelling tools',
          permissions: ['content_generation'],
          performance_impact: 0.1
        },
        {
          plugin_id: 'analytics-pro',
          name: 'Analytics Professional',
          version: '2.1.0',
          description: 'Professional-grade analytics and visualization',
          permissions: ['data_analysis', 'visualization'],
          performance_impact: 0.15
        }
      ];
      setAvailablePlugins(mockPlugins);
    } catch (error) {
      setError('Failed to fetch plugins');
    }
  };

  const createPersona = async () => {
    setIsLoading(true);
    try {
      // Mock persona creation
      const newPersona = {
        persona_id: `mimic-${Date.now()}`,
        persona_name: createFormData.role.charAt(0).toUpperCase() + createFormData.role.slice(1) + ' Expert',
        role: createFormData.role,
        description: createFormData.description,
        status: 'draft',
        performance_tier: 'unstable',
        sessions_completed: 0,
        average_score: 0,
        active_plugins: 0,
        knowledge_items: 0,
        created_at: new Date().toISOString(),
        last_updated: new Date().toISOString()
      };
      
      setPersonas(prev => [...prev, newPersona]);
      setShowCreateForm(false);
      setCreateFormData({
        role: '',
        description: '',
        context: {},
        traits: {
          focus: 50,
          creativity: 50,
          precision: 50,
          humor: 25,
          empathy: 50,
          assertiveness: 50,
          adaptability: 50,
          collaboration: 50
        },
        tags: []
      });
    } catch (error) {
      setError('Failed to create persona');
    } finally {
      setIsLoading(false);
    }
  };

  const forkPersona = async () => {
    if (!forkData.sourcePersonaId || !forkData.newRole) return;
    
    setIsLoading(true);
    try {
      const sourcePersona = personas.find(p => p.persona_id === forkData.sourcePersonaId);
      const forkedPersona = {
        ...sourcePersona,
        persona_id: `mimic-fork-${Date.now()}`,
        persona_name: `Forked ${sourcePersona.persona_name}`,
        role: forkData.newRole,
        status: 'forked',
        performance_tier: 'beta',
        sessions_completed: 0,
        created_at: new Date().toISOString(),
        last_updated: new Date().toISOString()
      };
      
      setPersonas(prev => [...prev, forkedPersona]);
      setShowForkForm(false);
      setForkData({ sourcePersonaId: '', newRole: '', modifications: {} });
    } catch (error) {
      setError('Failed to fork persona');
    } finally {
      setIsLoading(false);
    }
  };

  const renderPersonaCard = (persona) => (
    <div 
      key={persona.persona_id}
      className={`persona-card ${selectedPersona?.persona_id === persona.persona_id ? 'selected' : ''}`}
      onClick={() => setSelectedPersona(persona)}
    >
      <div className="persona-header">
        <h3>{persona.persona_name}</h3>
        <span className={`status-badge ${persona.status}`}>{persona.status}</span>
      </div>
      <div className="persona-role">{persona.role}</div>
      <div className="persona-description">{persona.description}</div>
      <div className="persona-stats">
        <div className="stat">
          <span className="stat-label">Tier:</span>
          <span className={`stat-value tier-${persona.performance_tier}`}>
            {persona.performance_tier}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">Sessions:</span>
          <span className="stat-value">{persona.sessions_completed}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Score:</span>
          <span className="stat-value">{persona.average_score}%</span>
        </div>
      </div>
      <div className="persona-footer">
        <span className="last-updated">
          Updated: {new Date(persona.last_updated).toLocaleDateString()}
        </span>
      </div>
    </div>
  );

  const renderPerformanceChart = () => {
    const canvas = canvasRef.current;
    if (!canvas || !analytics) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, width, height);

    // Draw performance trend
    const trend = analytics.performance_trend;
    if (trend.length > 1) {
      const maxScore = Math.max(...trend);
      const minScore = Math.min(...trend);
      const scoreRange = maxScore - minScore || 1;

      ctx.strokeStyle = '#22d3ee';
      ctx.lineWidth = 2;
      ctx.beginPath();

      for (let i = 0; i < trend.length; i++) {
        const x = (i / (trend.length - 1)) * (width - 40) + 20;
        const y = height - 20 - ((trend[i] - minScore) / scoreRange) * (height - 40);
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();

      // Draw points
      ctx.fillStyle = '#22d3ee';
      for (let i = 0; i < trend.length; i++) {
        const x = (i / (trend.length - 1)) * (width - 40) + 20;
        const y = height - 20 - ((trend[i] - minScore) / scoreRange) * (height - 40);
        
        ctx.beginPath();
        ctx.arc(x, y, 3, 0, 2 * Math.PI);
        ctx.fill();
      }
    }
  };

  useEffect(() => {
    if (activeTab === 'analytics' && analytics) {
      renderPerformanceChart();
    }
  }, [activeTab, analytics]);

  const renderPersonasTab = () => (
    <div className="mimic-tab-content">
      <div className="personas-header">
        <h3>Dynamic Personas</h3>
        <button 
          className="create-persona-btn"
          onClick={() => setShowCreateForm(true)}
        >
          + Create Persona
        </button>
      </div>
      
      <div className="personas-grid">
        {personas.map(renderPersonaCard)}
      </div>

      {showCreateForm && (
        <div className="modal-overlay">
          <div className="create-form-modal">
            <h3>Create New Persona</h3>
            <div className="form-group">
              <label>Role</label>
              <input
                type="text"
                value={createFormData.role}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, role: e.target.value }))}
                placeholder="e.g., researcher, creative_writer, analyst"
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={createFormData.description}
                onChange={(e) => setCreateFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe the persona's purpose and capabilities"
              />
            </div>
            <div className="traits-section">
              <h4>Core Traits</h4>
              <div className="traits-grid">
                {Object.entries(createFormData.traits).map(([trait, value]) => (
                  <div key={trait} className="trait-slider">
                    <label>{trait.charAt(0).toUpperCase() + trait.slice(1)}</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={value}
                      onChange={(e) => setCreateFormData(prev => ({
                        ...prev,
                        traits: { ...prev.traits, [trait]: parseInt(e.target.value) }
                      }))}
                    />
                    <span>{value}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="form-actions">
              <button onClick={() => setShowCreateForm(false)}>Cancel</button>
              <button onClick={createPersona} disabled={!createFormData.role}>
                Create Persona
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderAnalyticsTab = () => (
    <div className="mimic-tab-content">
      {selectedPersona ? (
        <div className="analytics-content">
          <div className="analytics-header">
            <h3>{selectedPersona.persona_name} Analytics</h3>
            <span className={`tier-badge ${selectedPersona.performance_tier}`}>
              {selectedPersona.performance_tier.toUpperCase()}
            </span>
          </div>

          {analytics && (
            <>
              <div className="analytics-overview">
                <div className="metric-card">
                  <h4>Sessions Completed</h4>
                  <div className="metric-value">{analytics.total_sessions}</div>
                </div>
                <div className="metric-card">
                  <h4>Average Score</h4>
                  <div className="metric-value">{analytics.average_score}%</div>
                </div>
                <div className="metric-card">
                  <h4>Success Rate</h4>
                  <div className="metric-value">{(analytics.success_rate * 100).toFixed(1)}%</div>
                </div>
                <div className="metric-card">
                  <h4>Usage Streak</h4>
                  <div className="metric-value">{analytics.growth_stats.usage_streak} days</div>
                </div>
              </div>

              <div className="performance-chart-section">
                <h4>Performance Trend</h4>
                <canvas 
                  ref={canvasRef}
                  width={600}
                  height={200}
                  className="performance-chart"
                />
              </div>

              <div className="analytics-details">
                <div className="top-topics">
                  <h4>Top Knowledge Areas</h4>
                  {analytics.top_topics.map((topic, index) => (
                    <div key={index} className="topic-item">
                      <span className="topic-name">{topic.topic.replace(/_/g, ' ')}</span>
                      <div className="topic-score-bar">
                        <div 
                          className="topic-score-fill"
                          style={{ width: `${topic.score * 100}%` }}
                        />
                      </div>
                      <span className="topic-score">{(topic.score * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>

                <div className="recommendations">
                  <h4>Recommendations</h4>
                  <ul>
                    {analytics.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>

                <div className="growth-opportunities">
                  <h4>Growth Opportunities</h4>
                  <ul>
                    {analytics.growth_opportunities.map((opp, index) => (
                      <li key={index}>{opp}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </>
          )}
        </div>
      ) : (
        <div className="no-selection">
          <p>Select a persona to view analytics</p>
        </div>
      )}
    </div>
  );

  const renderManagementTab = () => (
    <div className="mimic-tab-content">
      <div className="management-sections">
        <div className="management-section">
          <h3>Persona Operations</h3>
          <div className="operation-buttons">
            <button 
              onClick={() => setShowForkForm(true)}
              disabled={!selectedPersona}
            >
              Fork Persona
            </button>
            <button 
              onClick={() => setShowMergeForm(true)}
              disabled={personas.length < 2}
            >
              Merge Personas
            </button>
            <button disabled={!selectedPersona}>
              Export Persona
            </button>
            <button>
              Import Persona
            </button>
          </div>
        </div>

        <div className="management-section">
          <h3>Plugin Management</h3>
          <div className="plugins-list">
            {availablePlugins.map(plugin => (
              <div key={plugin.plugin_id} className="plugin-item">
                <div className="plugin-info">
                  <h4>{plugin.name}</h4>
                  <p>{plugin.description}</p>
                  <span className="plugin-version">v{plugin.version}</span>
                </div>
                <button 
                  className={`plugin-toggle ${selectedPlugins.includes(plugin.plugin_id) ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedPlugins(prev => 
                      prev.includes(plugin.plugin_id)
                        ? prev.filter(id => id !== plugin.plugin_id)
                        : [...prev, plugin.plugin_id]
                    );
                  }}
                >
                  {selectedPlugins.includes(plugin.plugin_id) ? 'Remove' : 'Add'}
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="management-section">
          <h3>Knowledge Base</h3>
          <button 
            className="add-knowledge-btn"
            onClick={() => setShowKnowledgeForm(true)}
          >
            + Add Knowledge
          </button>
          <div className="knowledge-list">
            {knowledgeBase.map((knowledge, index) => (
              <div key={index} className="knowledge-item">
                <div className="knowledge-content">{knowledge.summary}</div>
                <div className="knowledge-meta">
                  <span className="relevance-score">
                    Relevance: {(knowledge.relevance_score * 100).toFixed(0)}%
                  </span>
                  <div className="knowledge-tags">
                    {knowledge.tags.map((tag, i) => (
                      <span key={i} className="tag">{tag}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {showForkForm && (
        <div className="modal-overlay">
          <div className="fork-form-modal">
            <h3>Fork Persona</h3>
            <div className="form-group">
              <label>Source Persona</label>
              <select
                value={forkData.sourcePersonaId}
                onChange={(e) => setForkData(prev => ({ ...prev, sourcePersonaId: e.target.value }))}
              >
                <option value="">Select persona to fork</option>
                {personas.map(persona => (
                  <option key={persona.persona_id} value={persona.persona_id}>
                    {persona.persona_name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>New Role</label>
              <input
                type="text"
                value={forkData.newRole}
                onChange={(e) => setForkData(prev => ({ ...prev, newRole: e.target.value }))}
                placeholder="New role for forked persona"
              />
            </div>
            <div className="form-actions">
              <button onClick={() => setShowForkForm(false)}>Cancel</button>
              <button onClick={forkPersona} disabled={!forkData.sourcePersonaId || !forkData.newRole}>
                Fork Persona
              </button>
            </div>
          </div>
        </div>
      )}

      {showKnowledgeForm && (
        <div className="modal-overlay">
          <div className="knowledge-form-modal">
            <h3>Add Knowledge</h3>
            <div className="form-group">
              <label>Content</label>
              <textarea
                value={knowledgeFormData.content}
                onChange={(e) => setKnowledgeFormData(prev => ({ ...prev, content: e.target.value }))}
                placeholder="Knowledge content or summary"
              />
            </div>
            <div className="form-group">
              <label>Relevance Score</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={knowledgeFormData.relevanceScore}
                onChange={(e) => setKnowledgeFormData(prev => ({ ...prev, relevanceScore: parseFloat(e.target.value) }))}
              />
              <span>{(knowledgeFormData.relevanceScore * 100).toFixed(0)}%</span>
            </div>
            <div className="form-actions">
              <button onClick={() => setShowKnowledgeForm(false)}>Cancel</button>
              <button 
                onClick={() => {
                  setKnowledgeBase(prev => [...prev, {
                    doc_id: `doc-${Date.now()}`,
                    summary: knowledgeFormData.content,
                    relevance_score: knowledgeFormData.relevanceScore,
                    tags: knowledgeFormData.tags,
                    created_at: new Date().toISOString()
                  }]);
                  setShowKnowledgeForm(false);
                  setKnowledgeFormData({ content: '', tags: [], relevanceScore: 0.5 });
                }}
                disabled={!knowledgeFormData.content}
              >
                Add Knowledge
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (!isVisible) return null;

  return (
    <div className="mimic-interface-overlay">
      <div className="mimic-interface">
        <div className="mimic-header">
          <div className="header-title">
            <h2>MIMIC - Dynamic Persona Engine</h2>
            <span className="module-status online">OPERATIONAL</span>
          </div>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="mimic-navigation">
          <button 
            className={`nav-tab ${activeTab === 'personas' ? 'active' : ''}`}
            onClick={() => setActiveTab('personas')}
          >
            Personas
          </button>
          <button 
            className={`nav-tab ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            Analytics
          </button>
          <button 
            className={`nav-tab ${activeTab === 'management' ? 'active' : ''}`}
            onClick={() => setActiveTab('management')}
          >
            Management
          </button>
        </div>

        <div className="mimic-content">
          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}
          
          {isLoading && (
            <div className="loading-overlay">
              <div className="loading-spinner"></div>
              <span>Processing...</span>
            </div>
          )}

          {activeTab === 'personas' && renderPersonasTab()}
          {activeTab === 'analytics' && renderAnalyticsTab()}
          {activeTab === 'management' && renderManagementTab()}
        </div>

        <div className="mimic-footer">
          <div className="system-status">
            <span className="status-indicator online"></span>
            <span>Mimic Engine Online</span>
          </div>
          <div className="persona-count">
            {personas.length} Active Personas
          </div>
        </div>
      </div>
    </div>
  );
};

export default MimicInterface;