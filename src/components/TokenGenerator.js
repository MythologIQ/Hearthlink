import React, { useState, useEffect } from 'react';

const TokenGenerator = () => {
  const [agents, setAgents] = useState([]);
  const [tokens, setTokens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newAgent, setNewAgent] = useState({
    name: '',
    description: '',
    capabilities: ['file_write', 'ipc_communication', 'api_access'],
    apiKey: '',
    apiProvider: 'none'
  });
  const [selectedAgent, setSelectedAgent] = useState('');
  const [generatedToken, setGeneratedToken] = useState(null);

  const API_BASE = 'http://192.168.0.29:8080/api';

  useEffect(() => {
    loadAgents();
    loadTokens();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await fetch(`${API_BASE}/agents`);
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (error) {
      console.error('Failed to load agents:', error);
    }
  };

  const loadTokens = async () => {
    try {
      const response = await fetch(`${API_BASE}/tokens`);
      const data = await response.json();
      setTokens(data.tokens || []);
    } catch (error) {
      console.error('Failed to load tokens:', error);
    }
  };

  const createAgent = async () => {
    if (!newAgent.name.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newAgent.name,
          description: newAgent.description,
          capabilities: newAgent.capabilities,
          config: { 
            version: '1.0.0', 
            created_via: 'ui',
            api_provider: newAgent.apiProvider,
            has_api_key: newAgent.apiKey.length > 0
          },
          api_key: newAgent.apiKey // Will be encrypted by backend
        })
      });
      
      if (response.ok) {
        const agent = await response.json();
        setAgents([...agents, agent]);
        setSelectedAgent(agent.id);
        setNewAgent({ 
          name: '', 
          description: '', 
          capabilities: ['file_write', 'ipc_communication', 'api_access'],
          apiKey: '',
          apiProvider: 'none'
        });
        console.log('Agent created:', agent);
      }
    } catch (error) {
      console.error('Failed to create agent:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateToken = async () => {
    if (!selectedAgent) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/agents/${selectedAgent}/tokens`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          permissions: { read: true, write: true, execute: true },
          expires_days: 30
        })
      });
      
      if (response.ok) {
        const tokenData = await response.json();
        setGeneratedToken(tokenData);
        loadTokens(); // Refresh tokens list
        console.log('Token generated:', tokenData);
      }
    } catch (error) {
      console.error('Failed to generate token:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      alert('Token copied to clipboard!');
    });
  };

  const deleteAgent = async (agentId, agentName) => {
    if (!window.confirm(`Are you sure you want to delete agent "${agentName}"? This will also revoke all its tokens.`)) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/agents/${agentId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setAgents(agents.filter(agent => agent.id !== agentId));
        setTokens(tokens.filter(token => token.agent_id !== agentId));
        if (selectedAgent === agentId) {
          setSelectedAgent('');
        }
        console.log('Agent deleted:', agentId);
      } else {
        const error = await response.text();
        alert(`Failed to delete agent: ${error}`);
      }
    } catch (error) {
      console.error('Failed to delete agent:', error);
      alert('Failed to delete agent. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const revokeToken = async (tokenId) => {
    if (!window.confirm('Are you sure you want to revoke this token? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/tokens/${tokenId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setTokens(tokens.filter(token => token.token_id !== tokenId));
        console.log('Token revoked:', tokenId);
      } else {
        const error = await response.text();
        alert(`Failed to revoke token: ${error}`);
      }
    } catch (error) {
      console.error('Failed to revoke token:', error);
      alert('Failed to revoke token. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      padding: '20px',
      backgroundColor: '#0d1b2a',
      color: '#e0e6ed',
      minHeight: '100vh',
      fontFamily: 'Orbitron, monospace',
      overflowY: 'auto',
      boxSizing: 'border-box'
    }}>
      <h1 style={{ color: '#22d3ee', textAlign: 'center', marginBottom: '10px' }}>
        🔑 INCOMING API MANAGEMENT
      </h1>
      <p style={{ color: '#94a3b8', textAlign: 'center', marginBottom: '20px', fontSize: '14px' }}>
        Manage tokens for external services to call YOUR Hearthlink API
      </p>

      {/* API Direction Clarification */}
      <div style={{
        backgroundColor: '#1e293b',
        padding: '15px',
        borderRadius: '8px',
        marginBottom: '20px',
        border: '1px solid #64748b'
      }}>
        <h3 style={{ color: '#64748b', marginBottom: '10px', fontSize: '16px' }}>📍 API Direction Clarification</h3>
        <div style={{ fontSize: '14px', lineHeight: '1.5' }}>
          <div style={{ marginBottom: '8px' }}>
            <strong style={{ color: '#22d3ee' }}>This page (Incoming):</strong> <span style={{ color: '#e2e8f0' }}>Create tokens for external services to call your Hearthlink API</span>
          </div>
          <div>
            <strong style={{ color: '#fbbf24' }}>Outgoing API Management:</strong> <span style={{ color: '#e2e8f0' }}>Use Synapse Gateway to configure your API keys for calling external services</span>
          </div>
        </div>
      </div>

      {/* Instructions Section */}
      <div style={{
        backgroundColor: '#2d5a2d',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px',
        border: '2px solid #4ade80'
      }}>
        <h2 style={{ color: '#4ade80', marginBottom: '15px' }}>📖 How to Connect External Services</h2>
        
        <div style={{ marginBottom: '15px' }}>
          <h3 style={{ color: '#4ade80', fontSize: '16px', marginBottom: '10px' }}>🌐 Public API Endpoint:</h3>
          <div style={{
            backgroundColor: '#0d1b2a',
            padding: '10px',
            borderRadius: '4px',
            fontFamily: 'monospace',
            fontSize: '14px',
            border: '1px solid #4ade80'
          }}>
            <strong>https://your-domain.com/api</strong> (configure your public domain)
            <br />
            <span style={{ color: '#94a3b8' }}>Current local: http://192.168.0.29:8080/api</span>
          </div>
        </div>

        <div style={{ marginBottom: '15px' }}>
          <h3 style={{ color: '#4ade80', fontSize: '16px', marginBottom: '10px' }}>🔑 For ChatGPT/External AI:</h3>
          <ol style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
            <li>Create an Agent below (e.g., "ChatGPT Assistant")</li>
            <li>Generate an API Token for that agent</li>
            <li>Copy the token and use in your requests:</li>
          </ol>
          <div style={{
            backgroundColor: '#0d1b2a',
            padding: '10px',
            borderRadius: '4px',
            fontFamily: 'monospace',
            fontSize: '12px',
            marginTop: '10px',
            border: '1px solid #4ade80'
          }}>
            <strong>Authorization:</strong> Bearer YOUR_TOKEN_HERE<br />
            <strong>Content-Type:</strong> application/json<br /><br />
            <strong>Available Endpoints:</strong><br />
            • POST /api/agents - Create agent<br />
            • GET /api/agents - List agents<br />
            • POST /api/agents/&lt;id&gt;/tokens - Generate token<br />
            • POST /api/auth/verify - Verify token<br />
            • POST /api/execute - Execute commands
          </div>
        </div>

        <div style={{
          backgroundColor: '#5b2d2d',
          padding: '15px',
          borderRadius: '4px',
          border: '1px solid #ef4444'
        }}>
          <strong style={{ color: '#ef4444' }}>⚠️ Public Access Setup (Only if needed):</strong><br />
          <div style={{ fontSize: '13px', color: '#fee2e2', marginTop: '8px', lineHeight: '1.4' }}>
            <strong>You DON'T need this for:</strong><br />
            • Making calls TO external APIs (Gemini, OpenAI)<br />
            • Local desktop app usage<br />
            • Development and testing<br /><br />
            
            <strong>You ONLY need this for:</strong><br />
            • External services calling INTO your API<br />
            • ChatGPT custom actions connecting to you<br />
            • Web/mobile apps accessing your API<br /><br />
            
            <strong>If needed:</strong> Consider cloud hosting instead of exposing your home network
          </div>
        </div>
      </div>

      {/* Create Agent Section */}
      <div style={{
        backgroundColor: '#1e3a5f',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px',
        border: '1px solid #22d3ee'
      }}>
        <h2 style={{ color: '#22d3ee', marginBottom: '15px' }}>📋 Step 1: Create Agent Profile</h2>
        <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '15px' }}>
          Create a named profile to represent an external service (e.g., "ChatGPT", "My Bot", "Web App")
        </p>
        
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>Service/Agent Name:</label>
          <input
            type="text"
            value={newAgent.name}
            onChange={(e) => setNewAgent({...newAgent, name: e.target.value})}
            placeholder="e.g., My Project Agent"
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: '#0d1b2a',
              border: '1px solid #22d3ee',
              borderRadius: '4px',
              color: '#e0e6ed'
            }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>Description:</label>
          <input
            type="text"
            value={newAgent.description}
            onChange={(e) => setNewAgent({...newAgent, description: e.target.value})}
            placeholder="Agent description (optional)"
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: '#0d1b2a',
              border: '1px solid #22d3ee',
              borderRadius: '4px',
              color: '#e0e6ed'
            }}
          />
        </div>

        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>API Provider:</label>
          <select
            value={newAgent.apiProvider}
            onChange={(e) => setNewAgent({...newAgent, apiProvider: e.target.value})}
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: '#0d1b2a',
              border: '1px solid #22d3ee',
              borderRadius: '4px',
              color: '#e0e6ed'
            }}
          >
            <option value="none">No API Key Required</option>
            <option value="openai">OpenAI (GPT)</option>
            <option value="google">Google Gemini</option>
            <option value="anthropic">Anthropic Claude</option>
            <option value="custom">Custom API</option>
          </select>
        </div>

        {newAgent.apiProvider !== 'none' && (
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>
              🔐 API Key (Encrypted Storage):
            </label>
            <input
              type="password"
              value={newAgent.apiKey}
              onChange={(e) => setNewAgent({...newAgent, apiKey: e.target.value})}
              placeholder="Enter API key (will be encrypted)"
              style={{
                width: '100%',
                padding: '10px',
                backgroundColor: '#0d1b2a',
                border: '1px solid #fbbf24',
                borderRadius: '4px',
                color: '#e0e6ed',
                fontFamily: 'monospace'
              }}
            />
            <div style={{ 
              fontSize: '12px', 
              color: '#fbbf24', 
              marginTop: '5px',
              display: 'flex',
              alignItems: 'center',
              gap: '5px'
            }}>
              🔒 API keys are encrypted before storage and never displayed in plain text
            </div>
          </div>
        )}

        <button
          onClick={createAgent}
          disabled={loading || !newAgent.name.trim()}
          style={{
            padding: '10px 20px',
            backgroundColor: '#22d3ee',
            color: '#0d1b2a',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Creating...' : '✨ Create Agent'}
        </button>
      </div>

      {/* Existing Agents Management */}
      <div style={{
        backgroundColor: '#1e3a5f',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px',
        border: '1px solid #22d3ee'
      }}>
        <h2 style={{ color: '#22d3ee', marginBottom: '15px' }}>👥 Manage Agent Profiles</h2>
        <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '15px' }}>
          Existing agent profiles and their configurations
        </p>
        
        {agents.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>No agents created yet.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #22d3ee' }}>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Agent Name</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Description</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>API Provider</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Created</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {agents.map(agent => (
                  <tr key={agent.id} style={{ borderBottom: '1px solid #374151' }}>
                    <td style={{ padding: '10px', fontWeight: 'bold' }}>{agent.name}</td>
                    <td style={{ padding: '10px', color: '#94a3b8' }}>
                      {agent.description || 'No description'}
                    </td>
                    <td style={{ padding: '10px' }}>
                      <span style={{ 
                        color: agent.config?.api_provider && agent.config.api_provider !== 'none' ? '#4ade80' : '#94a3b8',
                        fontSize: '12px'
                      }}>
                        {agent.config?.api_provider === 'none' || !agent.config?.api_provider 
                          ? 'None' 
                          : agent.config.api_provider.charAt(0).toUpperCase() + agent.config.api_provider.slice(1)
                        }
                        {agent.config?.has_api_key && ' 🔐'}
                      </span>
                    </td>
                    <td style={{ padding: '10px', fontSize: '12px', color: '#94a3b8' }}>
                      {new Date(agent.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '10px' }}>
                      <button
                        onClick={() => deleteAgent(agent.id, agent.name)}
                        disabled={loading}
                        style={{
                          padding: '5px 10px',
                          backgroundColor: '#ef4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}
                      >
                        🗑️ DELETE
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Generate Token Section */}
      <div style={{
        backgroundColor: '#1e3a5f',
        padding: '20px',
        borderRadius: '8px',
        marginBottom: '20px',
        border: '1px solid #22d3ee'
      }}>
        <h2 style={{ color: '#22d3ee', marginBottom: '15px' }}>🎫 Step 2: Generate Access Token</h2>
        <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '15px' }}>
          Generate a Bearer token for the selected agent to authenticate API requests
        </p>
        
        <div style={{ marginBottom: '15px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>Select Agent:</label>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: '#0d1b2a',
              border: '1px solid #22d3ee',
              borderRadius: '4px',
              color: '#e0e6ed'
            }}
          >
            <option value="">-- Select an agent --</option>
            {agents.map(agent => (
              <option key={agent.id} value={agent.id}>
                {agent.name} ({agent.id.substring(0, 8)}...)
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={generateToken}
          disabled={loading || !selectedAgent}
          style={{
            padding: '10px 20px',
            backgroundColor: '#22d3ee',
            color: '#0d1b2a',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Generating...' : '🔑 Generate Token'}
        </button>
      </div>

      {/* Generated Token Display */}
      {generatedToken && (
        <div style={{
          backgroundColor: '#2d5a2d',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '2px solid #4ade80'
        }}>
          <h2 style={{ color: '#4ade80', marginBottom: '15px' }}>✅ Token Generated Successfully!</h2>
          
          <div style={{ marginBottom: '10px' }}>
            <strong>🏷️ Reference ID:</strong> {generatedToken.token_id.substring(0, 12)}...
          </div>
          <div style={{ marginBottom: '10px' }}>
            <strong>🤖 Agent Profile:</strong> {agents.find(a => a.id === generatedToken.agent_id)?.name || generatedToken.agent_id.substring(0, 8)}
          </div>
          <div style={{ marginBottom: '15px' }}>
            <strong>⏰ Valid Until:</strong> {new Date(generatedToken.expires_at).toLocaleDateString()} ({Math.ceil((new Date(generatedToken.expires_at) - new Date()) / (1000 * 60 * 60 * 24))} days)
          </div>
          
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', color: '#4ade80', fontWeight: 'bold' }}>
              🔑 Bearer Token (Copy this for your API requests):
            </label>
            <div style={{
              backgroundColor: '#0d1b2a',
              padding: '15px',
              borderRadius: '4px',
              border: '1px solid #4ade80',
              wordBreak: 'break-all',
              fontFamily: 'monospace',
              fontSize: '12px'
            }}>
              {generatedToken.token}
            </div>
          </div>

          <div style={{
            backgroundColor: '#1e293b',
            padding: '10px',
            borderRadius: '4px',
            marginBottom: '15px',
            border: '1px solid #64748b',
            fontSize: '12px'
          }}>
            <strong>📝 Usage Example:</strong><br />
            <code style={{ color: '#22d3ee' }}>
              curl -H "Authorization: Bearer {generatedToken.token.substring(0, 20)}..." \\<br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;-H "Content-Type: application/json" \\<br />
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;https://your-domain.com/api/auth/verify
            </code>
          </div>
          
          <button
            onClick={() => copyToClipboard(generatedToken.token)}
            style={{
              padding: '8px 16px',
              backgroundColor: '#4ade80',
              color: '#0d1b2a',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
          >
            📋 Copy Token
          </button>
          
          <div style={{ marginTop: '10px', fontSize: '12px', color: '#94a3b8' }}>
            ⚠️ Save this token securely - it won't be shown again!
          </div>
        </div>
      )}

      {/* Existing Tokens */}
      <div style={{
        backgroundColor: '#1e3a5f',
        padding: '20px',
        borderRadius: '8px',
        border: '1px solid #22d3ee'
      }}>
        <h2 style={{ color: '#22d3ee', marginBottom: '15px' }}>📋 Active Access Tokens</h2>
        <p style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '15px' }}>
          Current tokens in use by agents (tokens are only shown when first generated)
        </p>
        
        {tokens.length === 0 ? (
          <p style={{ color: '#94a3b8' }}>No tokens generated yet.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #22d3ee' }}>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Agent</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Token ID</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Created</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Expires</th>
                  <th style={{ padding: '10px', textAlign: 'left', color: '#22d3ee' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tokens.map(token => (
                  <tr key={token.token_id} style={{ borderBottom: '1px solid #374151' }}>
                    <td style={{ padding: '10px' }}>{token.agent_name}</td>
                    <td style={{ padding: '10px', fontFamily: 'monospace', fontSize: '12px' }}>
                      {token.token_id.substring(0, 20)}...
                    </td>
                    <td style={{ padding: '10px' }}>
                      {new Date(token.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '10px' }}>
                      {new Date(token.expires_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '10px' }}>
                      <button
                        onClick={() => revokeToken(token.token_id)}
                        disabled={loading}
                        style={{
                          padding: '5px 10px',
                          backgroundColor: '#ef4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}
                      >
                        🔐 REVOKE
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* API Status */}
      <div style={{
        marginTop: '20px',
        padding: '15px',
        backgroundColor: '#064e3b',
        borderRadius: '8px',
        border: '1px solid #10b981'
      }}>
        <h3 style={{ color: '#10b981', marginBottom: '10px' }}>🌐 API Status</h3>
        <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.5' }}>
          <strong>Development:</strong> <span style={{ color: '#10b981' }}>✅ Online</span><br />
          <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>http://192.168.0.29:8080/api</span><br />
          <strong>Production:</strong> <span style={{ color: '#94a3b8' }}>Configure your domain</span><br />
          <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>https://your-domain.com/api</span>
        </p>
      </div>
    </div>
  );
};

export default TokenGenerator;