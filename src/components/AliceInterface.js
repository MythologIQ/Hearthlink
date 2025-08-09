/**
 * Alice Behavioral Analysis Agent Interface
 * 
 * Comprehensive behavioral analysis system for understanding user communication patterns,
 * emotional states, and providing context-aware coaching recommendations.
 */

import React, { useState, useEffect, useRef } from 'react';
import { 
  info as logInfo, 
  warn as logWarn, 
  agentAction, 
  createContext 
} from '../utils/SystemLogger';
import { handleError } from '../utils/ErrorHandler';
import { call, sendToModule, on, off } from '../utils/APIManager';
import { recordMetric } from '../utils/HealthMonitor';
import './AliceInterface.css';

const AliceInterface = ({ isVisible, onClose }) => {
  // Core state management
  const [behavioralProfile, setBehavioralProfile] = useState(null);
  const [analysisData, setAnalysisData] = useState({
    communication: {
      cadence: 0,
      formality_level: 3,
      sentiment_baseline: 0,
      preferred_interaction_style: 'balanced'
    },
    patterns: {
      peak_productivity_hours: [],
      stress_indicators: [],
      motivation_triggers: [],
      cognitive_distortions: []
    },
    context: {
      current_session: null,
      conversation_depth: 0,
      topic_switches: 0,
      engagement_level: 0.5
    },
    coaching: {
      recommendations: [],
      effectiveness_score: 0,
      adaptation_suggestions: []
    }
  });

  const [realTimeAnalysis, setRealTimeAnalysis] = useState({
    currentMood: 'neutral',
    stressLevel: 0,
    engagementScore: 0.5,
    communicationEffectiveness: 0.7,
    cognitiveLoad: 'normal'
  });

  const [contextHistory, setContextHistory] = useState([]);
  const [coachingInsights, setCoachingInsights] = useState([]);
  const [activeView, setActiveView] = useState('overview');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Canvas refs for visualizations
  const moodCanvasRef = useRef(null);
  const patternCanvasRef = useRef(null);
  const contextCanvasRef = useRef(null);

  // Component context
  const context = createContext('alice-interface', 'agent');

  useEffect(() => {
    if (isVisible) {
      initializeAlice();
      setupEventListeners();
    }

    return () => {
      cleanupEventListeners();
    };
  }, [isVisible]);

  useEffect(() => {
    if (isVisible && analysisData) {
      drawVisualizations();
    }
  }, [analysisData, realTimeAnalysis, activeView]);

  // Initialization
  const initializeAlice = async () => {
    try {
      logInfo('Initializing Alice Behavioral Analysis Agent', {}, context);

      // Load existing behavioral profile
      const savedProfile = await loadBehavioralProfile();
      if (savedProfile) {
        setBehavioralProfile(savedProfile);
        setAnalysisData(savedProfile.analysisData || analysisData);
      }

      // Start real-time analysis
      await startRealTimeAnalysis();

      // Load recent context history
      const recentContext = await loadContextHistory();
      setContextHistory(recentContext);

      agentAction('alice', 'interface_initialized', {
        profileExists: !!savedProfile,
        contextItems: recentContext.length
      }, context);

    } catch (error) {
      handleError(error, { component: 'alice-interface', action: 'initialize' });
    }
  };

  const setupEventListeners = () => {
    // Listen for user interactions to analyze
    on('userInteraction', handleUserInteraction);
    on('conversationUpdate', handleConversationUpdate);
    on('agentResponse', handleAgentResponse);
    on('systemEvent', handleSystemEvent);
  };

  const cleanupEventListeners = () => {
    off('userInteraction', handleUserInteraction);
    off('conversationUpdate', handleConversationUpdate);
    off('agentResponse', handleAgentResponse);
    off('systemEvent', handleSystemEvent);
  };

  // Behavioral Analysis Engine
  const analyzeCommunicationPattern = (interaction) => {
    const analysis = {
      wordCount: interaction.content?.split(' ').length || 0,
      avgWordsPerMinute: calculateCadence(interaction),
      sentimentScore: analyzeSentiment(interaction.content),
      formalityLevel: analyzeFormalityLevel(interaction.content),
      complexityScore: analyzeComplexity(interaction.content),
      emotionalMarkers: extractEmotionalMarkers(interaction.content)
    };

    return analysis;
  };

  const calculateCadence = (interaction) => {
    const wordCount = interaction.content?.split(' ').length || 0;
    const timespan = interaction.duration || 30000; // Default 30 seconds
    return (wordCount / (timespan / 60000)); // Words per minute
  };

  const analyzeSentiment = (content) => {
    // Simplified sentiment analysis (in production, use more sophisticated NLP)
    const positiveWords = ['good', 'great', 'excellent', 'love', 'amazing', 'wonderful', 'fantastic'];
    const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'horrible', 'disappointing', 'frustrating'];
    
    const words = content?.toLowerCase().split(' ') || [];
    let score = 0;

    words.forEach(word => {
      if (positiveWords.includes(word)) score += 1;
      if (negativeWords.includes(word)) score -= 1;
    });

    return Math.max(-1, Math.min(1, score / words.length));
  };

  const analyzeFormalityLevel = (content) => {
    // Analyze formality indicators
    const formalIndicators = ['please', 'thank you', 'would you', 'could you', 'I would appreciate'];
    const informalIndicators = ['hey', 'gonna', 'wanna', 'yeah', 'ok', 'cool'];
    
    const text = content?.toLowerCase() || '';
    let formalCount = 0;
    let informalCount = 0;

    formalIndicators.forEach(indicator => {
      if (text.includes(indicator)) formalCount++;
    });

    informalIndicators.forEach(indicator => {
      if (text.includes(indicator)) informalCount++;
    });

    // Return scale of 1-5 (1 = very informal, 5 = very formal)
    if (formalCount > informalCount) return Math.min(5, 3 + formalCount);
    if (informalCount > formalCount) return Math.max(1, 3 - informalCount);
    return 3; // Neutral
  };

  const analyzeComplexity = (content) => {
    if (!content) return 0;
    
    const sentences = content.split(/[.!?]+/).filter(s => s.trim());
    const totalWords = content.split(' ').length;
    const avgWordsPerSentence = totalWords / sentences.length;
    
    // Complexity score based on sentence length and vocabulary
    return Math.min(1, avgWordsPerSentence / 20);
  };

  const extractEmotionalMarkers = (content) => {
    const emotionKeywords = {
      stress: ['stressed', 'overwhelmed', 'pressure', 'deadline', 'urgent', 'panic'],
      excitement: ['excited', 'thrilled', 'amazing', 'fantastic', 'awesome'],
      frustration: ['frustrated', 'annoyed', 'irritated', 'stuck', 'confused'],
      satisfaction: ['satisfied', 'accomplished', 'pleased', 'proud', 'successful']
    };

    const detected = {};
    const words = content?.toLowerCase().split(' ') || [];

    Object.entries(emotionKeywords).forEach(([emotion, keywords]) => {
      const matches = keywords.filter(keyword => words.includes(keyword));
      if (matches.length > 0) {
        detected[emotion] = matches.length;
      }
    });

    return detected;
  };

  // Context Analysis
  const analyzeConversationContext = (conversation) => {
    return {
      topicSwitches: detectTopicSwitches(conversation),
      conversationDepth: calculateConversationDepth(conversation),
      engagementLevel: calculateEngagementLevel(conversation),
      contextCoherence: analyzeContextCoherence(conversation)
    };
  };

  const detectTopicSwitches = (conversation) => {
    // Simplified topic detection
    const messages = conversation.messages || [];
    let switches = 0;
    let currentTopic = null;

    messages.forEach(message => {
      const messageTopic = extractPrimaryTopic(message.content);
      if (currentTopic && messageTopic !== currentTopic) {
        switches++;
      }
      currentTopic = messageTopic;
    });

    return switches;
  };

  const extractPrimaryTopic = (content) => {
    // Simplified topic extraction
    const topicKeywords = {
      work: ['work', 'job', 'project', 'meeting', 'deadline', 'task'],
      personal: ['family', 'friend', 'relationship', 'home', 'personal'],
      technical: ['code', 'programming', 'software', 'system', 'technical', 'bug'],
      planning: ['plan', 'schedule', 'organize', 'prepare', 'future', 'goal']
    };

    const words = content?.toLowerCase().split(' ') || [];
    let maxMatches = 0;
    let primaryTopic = 'general';

    Object.entries(topicKeywords).forEach(([topic, keywords]) => {
      const matches = keywords.filter(keyword => words.includes(keyword)).length;
      if (matches > maxMatches) {
        maxMatches = matches;
        primaryTopic = topic;
      }
    });

    return primaryTopic;
  };

  const calculateConversationDepth = (conversation) => {
    const messages = conversation.messages || [];
    const avgMessageLength = messages.reduce((sum, msg) => sum + (msg.content?.length || 0), 0) / messages.length;
    const followUpRatio = messages.filter(msg => msg.isFollowUp).length / messages.length;
    
    return Math.min(1, (avgMessageLength / 100) * (followUpRatio + 0.5));
  };

  const calculateEngagementLevel = (conversation) => {
    const messages = conversation.messages || [];
    const userMessages = messages.filter(msg => msg.sender === 'user');
    const responseTime = calculateAvgResponseTime(userMessages);
    const questionRatio = userMessages.filter(msg => msg.content?.includes('?')).length / userMessages.length;
    
    // Higher engagement = faster responses + more questions
    const responseScore = Math.max(0, 1 - (responseTime / 30000)); // 30 seconds baseline
    const questionScore = questionRatio;
    
    return (responseScore + questionScore) / 2;
  };

  const calculateAvgResponseTime = (messages) => {
    if (messages.length < 2) return 0;
    
    let totalTime = 0;
    for (let i = 1; i < messages.length; i++) {
      totalTime += messages[i].timestamp - messages[i-1].timestamp;
    }
    
    return totalTime / (messages.length - 1);
  };

  const analyzeContextCoherence = (conversation) => {
    // Analyze how well the conversation flows and maintains context
    const messages = conversation.messages || [];
    let coherenceScore = 1.0;
    
    for (let i = 1; i < messages.length; i++) {
      const prev = messages[i-1];
      const current = messages[i];
      
      // Check for abrupt topic changes without transitions
      if (extractPrimaryTopic(prev.content) !== extractPrimaryTopic(current.content)) {
        const hasTransition = hasTransitionLanguage(current.content);
        if (!hasTransition) {
          coherenceScore -= 0.1;
        }
      }
    }
    
    return Math.max(0, coherenceScore);
  };

  const hasTransitionLanguage = (content) => {
    const transitions = ['by the way', 'speaking of', 'on another note', 'changing topics', 'also', 'additionally'];
    const text = content?.toLowerCase() || '';
    return transitions.some(transition => text.includes(transition));
  };

  // Coaching System
  const generateCoachingRecommendations = (profile, currentAnalysis) => {
    const recommendations = [];

    // Communication effectiveness recommendations
    if (currentAnalysis.communicationEffectiveness < 0.6) {
      recommendations.push({
        type: 'communication',
        priority: 'high',
        title: 'Improve Communication Clarity',
        description: 'Consider breaking down complex requests into smaller, more specific questions.',
        actionable: true,
        implementation: 'Try using bullet points or numbered lists for multi-part requests.'
      });
    }

    // Stress level recommendations
    if (currentAnalysis.stressLevel > 0.7) {
      recommendations.push({
        type: 'wellness',
        priority: 'high',
        title: 'Stress Management',
        description: 'High stress levels detected. Consider taking breaks or simplifying current tasks.',
        actionable: true,
        implementation: 'Use the Pomodoro technique: 25 minutes focused work, 5 minute break.'
      });
    }

    // Engagement recommendations
    if (currentAnalysis.engagementScore < 0.4) {
      recommendations.push({
        type: 'engagement',
        priority: 'medium',
        title: 'Increase Interaction Depth',
        description: 'Consider asking more detailed questions to get better assistance.',
        actionable: true,
        implementation: 'Add context about your goals and constraints when asking for help.'
      });
    }

    // Cognitive load recommendations
    if (currentAnalysis.cognitiveLoad === 'high') {
      recommendations.push({
        type: 'cognitive',
        priority: 'high',
        title: 'Reduce Cognitive Load',
        description: 'Current cognitive load is high. Consider focusing on one task at a time.',
        actionable: true,
        implementation: 'Use task prioritization: urgent/important matrix to focus efforts.'
      });
    }

    return recommendations;
  };

  const calculateEffectivenessScore = (profile, recommendations) => {
    // Calculate how effective previous recommendations have been
    const implementedRecs = recommendations.filter(rec => rec.implemented);
    const improvementScore = implementedRecs.reduce((sum, rec) => sum + (rec.improvement || 0), 0);
    
    return implementedRecs.length > 0 ? improvementScore / implementedRecs.length : 0.5;
  };

  // Event Handlers
  const handleUserInteraction = async (event) => {
    try {
      setIsAnalyzing(true);
      
      const interaction = event.detail;
      const communicationAnalysis = analyzeCommunicationPattern(interaction);
      
      // Update real-time analysis
      setRealTimeAnalysis(prev => ({
        ...prev,
        currentMood: communicationAnalysis.sentimentScore > 0.2 ? 'positive' : 
                    communicationAnalysis.sentimentScore < -0.2 ? 'negative' : 'neutral',
        stressLevel: Math.max(0, Math.min(1, Object.keys(communicationAnalysis.emotionalMarkers).includes('stress') ? 0.8 : 0.3)),
        engagementScore: Math.min(1, prev.engagementScore + 0.1),
        communicationEffectiveness: (prev.communicationEffectiveness + communicationAnalysis.complexityScore) / 2
      }));

      // Update behavioral profile
      updateBehavioralProfile(communicationAnalysis);
      
      // Generate coaching insights
      const insights = generateCoachingRecommendations(behavioralProfile, realTimeAnalysis);
      setCoachingInsights(insights);

      recordMetric('alice.interaction_analyzed', 1);
      
    } catch (error) {
      handleError(error, { component: 'alice-interface', action: 'analyze_interaction' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleConversationUpdate = async (event) => {
    try {
      const conversation = event.detail;
      const contextAnalysis = analyzeConversationContext(conversation);
      
      // Update context history
      const newContextItem = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        conversation_id: conversation.id,
        analysis: contextAnalysis,
        summary: generateContextSummary(conversation)
      };
      
      setContextHistory(prev => [newContextItem, ...prev.slice(0, 49)]); // Keep last 50 items
      
      // Update analysis data
      setAnalysisData(prev => ({
        ...prev,
        context: {
          ...prev.context,
          current_session: conversation.id,
          conversation_depth: contextAnalysis.conversationDepth,
          topic_switches: contextAnalysis.topicSwitches,
          engagement_level: contextAnalysis.engagementLevel
        }
      }));

    } catch (error) {
      handleError(error, { component: 'alice-interface', action: 'update_conversation' });
    }
  };

  const handleAgentResponse = (event) => {
    // Analyze agent response effectiveness
    const response = event.detail;
    // Update coaching effectiveness metrics based on user reaction
  };

  const handleSystemEvent = (event) => {
    // Handle system-wide events that might affect behavioral analysis
    const systemEvent = event.detail;
    if (systemEvent.type === 'user_stress_detected') {
      setRealTimeAnalysis(prev => ({
        ...prev,
        stressLevel: Math.min(1, prev.stressLevel + 0.2)
      }));
    }
  };

  // Utility Functions
  const updateBehavioralProfile = (analysis) => {
    setBehavioralProfile(prev => {
      const updated = {
        ...prev,
        communication: {
          ...prev?.communication,
          cadence: (prev?.communication?.cadence || 0) * 0.9 + analysis.avgWordsPerMinute * 0.1,
          formality_level: (prev?.communication?.formality_level || 3) * 0.9 + analysis.formalityLevel * 0.1,
          sentiment_baseline: (prev?.communication?.sentiment_baseline || 0) * 0.9 + analysis.sentimentScore * 0.1
        },
        lastUpdated: new Date().toISOString()
      };
      
      // Save to local storage
      saveBehavioralProfile(updated);
      return updated;
    });
  };

  const generateContextSummary = (conversation) => {
    const messages = conversation.messages || [];
    const topics = messages.map(msg => extractPrimaryTopic(msg.content));
    const uniqueTopics = [...new Set(topics)];
    
    return {
      messageCount: messages.length,
      primaryTopics: uniqueTopics,
      duration: conversation.duration,
      userParticipation: messages.filter(msg => msg.sender === 'user').length / messages.length
    };
  };

  // Data Persistence
  const saveBehavioralProfile = async (profile) => {
    try {
      localStorage.setItem('hearthlink_alice_profile', JSON.stringify(profile));
      agentAction('alice', 'profile_saved', { profileSize: JSON.stringify(profile).length }, context);
    } catch (error) {
      handleError(error, { component: 'alice-interface', action: 'save_profile' });
    }
  };

  const loadBehavioralProfile = async () => {
    try {
      const saved = localStorage.getItem('hearthlink_alice_profile');
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      handleError(error, { component: 'alice-interface', action: 'load_profile' });
      return null;
    }
  };

  const loadContextHistory = async () => {
    try {
      const saved = localStorage.getItem('hearthlink_alice_context');
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      return [];
    }
  };

  const startRealTimeAnalysis = async () => {
    // Initialize real-time behavioral monitoring
    setIsAnalyzing(true);
    
    // Simulate real-time updates (in production, this would be more sophisticated)
    const interval = setInterval(() => {
      setRealTimeAnalysis(prev => ({
        ...prev,
        stressLevel: Math.max(0, prev.stressLevel - 0.01), // Gradual stress reduction
        engagementScore: Math.max(0.2, prev.engagementScore - 0.005) // Gradual engagement decay
      }));
    }, 5000);

    return () => clearInterval(interval);
  };

  // Visualization Functions
  const drawVisualizations = () => {
    drawMoodVisualization();
    drawPatternVisualization();
    drawContextVisualization();
  };

  const drawMoodVisualization = () => {
    const canvas = moodCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw mood ring
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20;

    // Mood colors
    const moodColors = {
      positive: '#10b981',
      neutral: '#22d3ee',
      negative: '#ef4444'
    };

    const moodColor = moodColors[realTimeAnalysis.currentMood] || moodColors.neutral;

    // Draw outer ring
    ctx.strokeStyle = moodColor;
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.stroke();

    // Draw stress indicator
    const stressAngle = realTimeAnalysis.stressLevel * 2 * Math.PI;
    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius - 15, -Math.PI / 2, -Math.PI / 2 + stressAngle);
    ctx.stroke();

    // Draw center text
    ctx.fillStyle = moodColor;
    ctx.font = 'bold 14px Orbitron';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(realTimeAnalysis.currentMood.toUpperCase(), centerX, centerY);
  };

  const drawPatternVisualization = () => {
    const canvas = patternCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw communication pattern over time
    const data = [
      analysisData.communication.cadence,
      analysisData.communication.formality_level * 20,
      (analysisData.communication.sentiment_baseline + 1) * 50,
      realTimeAnalysis.engagementScore * 100
    ];

    const labels = ['Cadence', 'Formality', 'Sentiment', 'Engagement'];
    const colors = ['#22d3ee', '#10b981', '#fbbf24', '#ef4444'];

    // Draw bars
    const barWidth = canvas.width / data.length - 10;
    const maxHeight = canvas.height - 40;

    data.forEach((value, index) => {
      const height = (value / 100) * maxHeight;
      const x = index * (barWidth + 10) + 5;
      const y = canvas.height - height - 20;

      // Draw bar
      ctx.fillStyle = colors[index];
      ctx.fillRect(x, y, barWidth, height);

      // Draw label
      ctx.fillStyle = '#ffffff';
      ctx.font = '10px Orbitron';
      ctx.textAlign = 'center';
      ctx.fillText(labels[index], x + barWidth / 2, canvas.height - 5);

      // Draw value
      ctx.fillText(Math.round(value), x + barWidth / 2, y - 5);
    });
  };

  const drawContextVisualization = () => {
    const canvas = contextCanvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw context flow timeline
    const contexts = contextHistory.slice(0, 10);
    if (contexts.length === 0) return;

    const pointSpacing = canvas.width / (contexts.length + 1);
    const baseY = canvas.height / 2;

    contexts.forEach((context, index) => {
      const x = (index + 1) * pointSpacing;
      const intensity = context.analysis.engagementLevel;
      const y = baseY - (intensity - 0.5) * 50;

      // Draw connection line
      if (index > 0) {
        const prevX = index * pointSpacing;
        const prevContext = contexts[index - 1];
        const prevY = baseY - (prevContext.analysis.engagementLevel - 0.5) * 50;

        ctx.strokeStyle = 'rgba(34, 211, 238, 0.5)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(prevX, prevY);
        ctx.lineTo(x, y);
        ctx.stroke();
      }

      // Draw point
      ctx.fillStyle = `hsl(${intensity * 120}, 70%, 60%)`;
      ctx.beginPath();
      ctx.arc(x, y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  // Render Methods
  const renderOverview = () => (
    <div className="alice-overview">
      <div className="behavior-summary">
        <h3>Behavioral Profile Summary</h3>
        <div className="profile-metrics">
          <div className="metric-card">
            <span className="metric-label">Communication Style</span>
            <span className="metric-value">
              {analysisData.communication.preferred_interaction_style}
            </span>
          </div>
          <div className="metric-card">
            <span className="metric-label">Avg Cadence</span>
            <span className="metric-value">
              {Math.round(analysisData.communication.cadence)} WPM
            </span>
          </div>
          <div className="metric-card">
            <span className="metric-label">Formality Level</span>
            <span className="metric-value">
              {Math.round(analysisData.communication.formality_level)}/5
            </span>
          </div>
          <div className="metric-card">
            <span className="metric-label">Sentiment Baseline</span>
            <span className="metric-value">
              {analysisData.communication.sentiment_baseline > 0 ? 'Positive' :
               analysisData.communication.sentiment_baseline < 0 ? 'Negative' : 'Neutral'}
            </span>
          </div>
        </div>
      </div>

      <div className="real-time-analysis">
        <h3>Real-Time Analysis</h3>
        <div className="mood-ring-container">
          <canvas 
            ref={moodCanvasRef}
            className="mood-visualization"
            width="150"
            height="150"
          />
          <div className="mood-indicators">
            <div className={`indicator ${realTimeAnalysis.currentMood}`}>
              Mood: {realTimeAnalysis.currentMood}
            </div>
            <div className="indicator stress">
              Stress: {Math.round(realTimeAnalysis.stressLevel * 100)}%
            </div>
            <div className="indicator engagement">
              Engagement: {Math.round(realTimeAnalysis.engagementScore * 100)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAnalysis = () => (
    <div className="alice-analysis">
      <div className="pattern-analysis">
        <h3>Communication Patterns</h3>
        <canvas 
          ref={patternCanvasRef}
          className="pattern-visualization"
          width="400"
          height="200"
        />
      </div>

      <div className="context-analysis">
        <h3>Context Flow</h3>
        <canvas 
          ref={contextCanvasRef}
          className="context-visualization"
          width="400"
          height="150"
        />
        <div className="context-metrics">
          <div className="context-metric">
            <span>Topic Switches:</span>
            <span>{analysisData.context.topic_switches}</span>
          </div>
          <div className="context-metric">
            <span>Conversation Depth:</span>
            <span>{Math.round(analysisData.context.conversation_depth * 100)}%</span>
          </div>
          <div className="context-metric">
            <span>Coherence Score:</span>
            <span>{Math.round(analysisData.context.engagement_level * 100)}%</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCoaching = () => (
    <div className="alice-coaching">
      <div className="coaching-header">
        <h3>Behavioral Coaching Insights</h3>
        <div className="effectiveness-score">
          Effectiveness: {Math.round(analysisData.coaching.effectiveness_score * 100)}%
        </div>
      </div>

      <div className="recommendations-list">
        {coachingInsights.map((insight, index) => (
          <div key={index} className={`recommendation ${insight.priority}`}>
            <div className="recommendation-header">
              <span className="recommendation-type">{insight.type}</span>
              <span className={`priority-badge ${insight.priority}`}>
                {insight.priority}
              </span>
            </div>
            <h4>{insight.title}</h4>
            <p>{insight.description}</p>
            {insight.implementation && (
              <div className="implementation-suggestion">
                <strong>How to implement:</strong> {insight.implementation}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  if (!isVisible) return null;

  return (
    <div className="alice-interface">
      <div className="alice-header">
        <div className="alice-title">
          <h1>Alice - Behavioral Analysis Agent</h1>
          <div className="alice-subtitle">
            Understanding patterns, enhancing communication, providing insights
          </div>
        </div>
        <div className="alice-status">
          <div className={`status-indicator ${isAnalyzing ? 'analyzing' : 'ready'}`}>
            {isAnalyzing ? 'Analyzing...' : 'Ready'}
          </div>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
      </div>

      <div className="alice-navigation">
        <button 
          className={activeView === 'overview' ? 'active' : ''}
          onClick={() => setActiveView('overview')}
        >
          Overview
        </button>
        <button 
          className={activeView === 'analysis' ? 'active' : ''}
          onClick={() => setActiveView('analysis')}
        >
          Analysis
        </button>
        <button 
          className={activeView === 'coaching' ? 'active' : ''}
          onClick={() => setActiveView('coaching')}
        >
          Coaching
        </button>
      </div>

      <div className="alice-content">
        {activeView === 'overview' && renderOverview()}
        {activeView === 'analysis' && renderAnalysis()}
        {activeView === 'coaching' && renderCoaching()}
      </div>
    </div>
  );
};

export default AliceInterface;