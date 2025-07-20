import React, { useState, useEffect } from 'react';
import './ConferenceSystem.css';

const ConferenceSystem = () => {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [sessionTopic, setSessionTopic] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [googleResponse, setGoogleResponse] = useState('');
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // Available AI personas
  const availablePersonas = [
    { id: 'alden', name: 'Alden', type: 'persona', role: 'Executive Function Partner' },
    { id: 'alice', name: 'Alice', type: 'persona', role: 'Behavioral Analysis' },
    { id: 'mimic', name: 'Mimic', type: 'persona', role: 'Dynamic Persona' },
    { id: 'sentry', name: 'Sentry', type: 'persona', role: 'Security & Compliance' }
  ];

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      // For now, use mock data since we need to implement session listing
      const mockSessions = [];
      setSessions(mockSessions);
    } catch (err) {
      setError('Failed to load sessions');
      console.error('Error loading sessions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const createSession = async () => {
    if (!sessionTopic.trim()) {
      setError('Please enter a session topic');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const userId = 'user-001'; // TODO: Get from auth context
      const response = await window.electronAPI.createSession(
        userId,
        sessionTopic,
        participants
      );

      if (response.success) {
        const newSession = {
          sessionId: response.data.sessionId,
          topic: sessionTopic,
          participants: participants,
          status: 'active',
          createdAt: new Date().toISOString()
        };

        setSessions([...sessions, newSession]);
        setActiveSession(newSession);
        setSessionTopic('');
        setParticipants([]);
      } else {
        setError(`Failed to create session: ${response.error}`);
      }
    } catch (err) {
      setError('Failed to create session');
      console.error('Error creating session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const askGoogleAPI = async () => {
    if (!sessionTopic.trim()) {
      setError('Please enter a topic to ask Google AI');
      return;
    }

    try {
      setIsGoogleLoading(true);
      setError(null);
      setGoogleResponse('');

      const message = `Please provide insights about: ${sessionTopic}`;
      const response = await window.electronAPI.googleApiCall(message);

      if (response.success) {
        setGoogleResponse(response.response);
      } else {
        setError(`Google API Error: ${response.error}`);
      }
    } catch (err) {
      setError('Failed to connect to Google API');
      console.error('Error calling Google API:', err);
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const addParticipant = (persona) => {
    if (!participants.find(p => p.id === persona.id)) {
      setParticipants([...participants, persona]);
    }
  };

  const removeParticipant = (personaId) => {
    setParticipants(participants.filter(p => p.id !== personaId));
  };

  const startTurnTaking = async (sessionId) => {
    try {
      setIsLoading(true);
      const userId = 'user-001';
      const turnOrder = participants.map(p => p.id);

      const response = await window.electronAPI.startTurnTaking(
        sessionId,
        userId,
        turnOrder
      );

      if (response.success) {
        // Update session status
        setSessions(sessions.map(s => 
          s.sessionId === sessionId 
            ? { ...s, turnTakingActive: true, currentTurn: turnOrder[0] }
            : s
        ));
        
        if (activeSession?.sessionId === sessionId) {
          setActiveSession({
            ...activeSession,
            turnTakingActive: true,
            currentTurn: turnOrder[0]
          });
        }
      } else {
        setError(`Failed to start turn-taking: ${response.error}`);
      }
    } catch (err) {
      setError('Failed to start turn-taking');
      console.error('Error starting turn-taking:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const advanceTurn = async (sessionId) => {
    try {
      setIsLoading(true);
      const userId = 'user-001';

      const response = await window.electronAPI.advanceTurn(sessionId, userId);

      if (response.success) {
        const nextParticipant = response.data.nextParticipant;
        
        // Update session with next participant
        setSessions(sessions.map(s => 
          s.sessionId === sessionId 
            ? { ...s, currentTurn: nextParticipant }
            : s
        ));
        
        if (activeSession?.sessionId === sessionId) {
          setActiveSession({
            ...activeSession,
            currentTurn: nextParticipant
          });
        }
      } else {
        setError(`Failed to advance turn: ${response.error}`);
      }
    } catch (err) {
      setError('Failed to advance turn');
      console.error('Error advancing turn:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadSessionDetails = async (sessionId) => {
    try {
      setIsLoading(true);
      const response = await window.electronAPI.getSession(sessionId);

      if (response.success) {
        setActiveSession(response.data);
      } else {
        setError(`Failed to load session: ${response.error}`);
      }
    } catch (err) {
      setError('Failed to load session details');
      console.error('Error loading session details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="conference-system">
      <div className="conference-header">
        <h2>Multi-Agent Conference System</h2>
        {error && <div className="error-message">{error}</div>}
      </div>

      <div className="conference-content">
        {/* Session Creation */}
        <div className="session-creation">
          <h3>Create New Session</h3>
          <div className="session-form">
            <input
              type="text"
              placeholder="Enter session topic..."
              value={sessionTopic}
              onChange={(e) => setSessionTopic(e.target.value)}
              className="topic-input"
            />
            
            <div className="participant-selection">
              <h4>Select Participants</h4>
              <div className="available-personas">
                {availablePersonas.map(persona => (
                  <div 
                    key={persona.id} 
                    className={`persona-card ${participants.find(p => p.id === persona.id) ? 'selected' : ''}`}
                    onClick={() => addParticipant(persona)}
                  >
                    <div className="persona-name">{persona.name}</div>
                    <div className="persona-role">{persona.role}</div>
                  </div>
                ))}
              </div>
              
              {participants.length > 0 && (
                <div className="selected-participants">
                  <h5>Selected Participants:</h5>
                  {participants.map(participant => (
                    <div key={participant.id} className="selected-participant">
                      <span>{participant.name}</span>
                      <button 
                        onClick={() => removeParticipant(participant.id)}
                        className="remove-btn"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button 
              onClick={createSession}
              disabled={isLoading || !sessionTopic.trim() || participants.length === 0}
              className="create-session-btn"
            >
              {isLoading ? 'Creating...' : 'Create Session'}
            </button>
          </div>
        </div>

        {/* Google API Integration */}
        <div className="google-api-section">
          <h3>Ask Google AI</h3>
          <div className="google-api-form">
            <button 
              onClick={askGoogleAPI}
              disabled={isGoogleLoading || !sessionTopic.trim()}
              className="google-api-btn"
            >
              {isGoogleLoading ? 'Asking Google AI...' : 'Ask Google AI about this topic'}
            </button>
            
            {googleResponse && (
              <div className="google-response">
                <h4>Google AI Response:</h4>
                <div className="response-text">{googleResponse}</div>
              </div>
            )}
          </div>
        </div>

        {/* Active Sessions */}
        <div className="active-sessions">
          <h3>Active Sessions</h3>
          {sessions.length === 0 ? (
            <p>No active sessions</p>
          ) : (
            <div className="sessions-list">
              {sessions.map(session => (
                <div 
                  key={session.sessionId} 
                  className={`session-card ${activeSession?.sessionId === session.sessionId ? 'active' : ''}`}
                  onClick={() => loadSessionDetails(session.sessionId)}
                >
                  <div className="session-topic">{session.topic}</div>
                  <div className="session-info">
                    <span>Participants: {session.participants.length}</span>
                    <span>Status: {session.status}</span>
                    {session.currentTurn && (
                      <span>Current Turn: {session.currentTurn}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Session Details */}
        {activeSession && (
          <div className="session-details">
            <h3>Session: {activeSession.topic}</h3>
            <div className="session-controls">
              {!activeSession.turnTakingActive ? (
                <button 
                  onClick={() => startTurnTaking(activeSession.sessionId)}
                  disabled={isLoading}
                  className="start-turn-btn"
                >
                  Start Turn-Taking
                </button>
              ) : (
                <div className="turn-controls">
                  <div className="current-turn">
                    Current Turn: {activeSession.currentTurn || 'None'}
                  </div>
                  <button 
                    onClick={() => advanceTurn(activeSession.sessionId)}
                    disabled={isLoading}
                    className="advance-turn-btn"
                  >
                    Advance Turn
                  </button>
                </div>
              )}
            </div>

            <div className="session-participants">
              <h4>Participants</h4>
              {activeSession.participants && activeSession.participants.map(participant => (
                <div 
                  key={participant.id} 
                  className={`participant-item ${activeSession.currentTurn === participant.id ? 'current-turn' : ''}`}
                >
                  <span className="participant-name">{participant.name}</span>
                  <span className="participant-role">{participant.role}</span>
                  {activeSession.currentTurn === participant.id && (
                    <span className="turn-indicator">●</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConferenceSystem;