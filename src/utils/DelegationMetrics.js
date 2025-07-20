/**
 * Delegation Metrics Tracker
 * Monitors and analyzes AI-to-AI collaboration performance
 */

class DelegationMetrics {
  constructor() {
    this.sessions = new Map();
    this.globalMetrics = {
      totalDelegations: 0,
      averageResponseTime: 0,
      averageVerbosity: 0,
      averageQuality: 0,
      contextDriftEvents: 0,
      successRate: 0,
      startTime: Date.now()
    };
    
    // Quality assessment criteria
    this.qualityMetrics = {
      relevance: 0,        // How relevant is the response to the task
      completeness: 0,     // How complete is the response
      accuracy: 0,         // How accurate is the technical content
      actionability: 0,    // How actionable are the recommendations
      clarity: 0           // How clear and understandable is the response
    };
    
    // Context drift detection
    this.contextBaseline = null;
    this.contextDriftThreshold = 0.3; // 30% deviation threshold
    
    // Performance benchmarks
    this.benchmarks = {
      responseTime: {
        excellent: 2000,   // < 2 seconds
        good: 5000,        // < 5 seconds
        acceptable: 10000, // < 10 seconds
        poor: 15000        // > 15 seconds
      },
      verbosity: {
        terse: 500,        // < 500 characters
        concise: 1500,     // < 1500 characters
        detailed: 3000,    // < 3000 characters
        verbose: 5000      // > 5000 characters
      },
      quality: {
        excellent: 4.5,    // > 4.5/5
        good: 3.5,         // > 3.5/5
        acceptable: 2.5,   // > 2.5/5
        poor: 1.5          // < 1.5/5
      }
    };
  }

  /**
   * Start tracking a new delegation session
   */
  startSession(sessionId, taskData) {
    const session = {
      id: sessionId,
      task: taskData.task,
      context: taskData.context,
      startTime: Date.now(),
      endTime: null,
      responseTime: null,
      
      // Task characteristics
      taskComplexity: this.assessTaskComplexity(taskData.task),
      taskType: this.classifyTaskType(taskData.task),
      contextLength: taskData.context ? taskData.context.length : 0,
      
      // Response metrics
      responseLength: null,
      verbosityScore: null,
      qualityScore: null,
      contextDrift: null,
      
      // Success metrics
      success: null,
      errorType: null,
      implementationSuccess: null,
      
      // Content analysis
      keywordsMatched: null,
      technicalAccuracy: null,
      actionableItems: null,
      
      // Collaboration metrics
      clarificationNeeded: false,
      followUpRequired: false,
      satisfactionScore: null
    };
    
    this.sessions.set(sessionId, session);
    return session;
  }

  /**
   * Record the Google AI response and analyze it
   */
  recordResponse(sessionId, response, success = true, errorType = null) {
    const session = this.sessions.get(sessionId);
    if (!session) return null;
    
    const endTime = Date.now();
    const responseTime = endTime - session.startTime;
    
    // Update session metrics
    session.endTime = endTime;
    session.responseTime = responseTime;
    session.success = success;
    session.errorType = errorType;
    
    if (success && response) {
      session.responseLength = response.length;
      session.verbosityScore = this.calculateVerbosityScore(response);
      session.qualityScore = this.assessResponseQuality(session.task, response);
      session.contextDrift = this.detectContextDrift(session.context, response);
      session.keywordsMatched = this.analyzeKeywordMatching(session.task, response);
      session.technicalAccuracy = this.assessTechnicalAccuracy(response);
      session.actionableItems = this.extractActionableItems(response);
    }
    
    // Update global metrics
    this.updateGlobalMetrics(session);
    
    return this.generateSessionReport(session);
  }

  /**
   * Assess task complexity based on content analysis
   */
  assessTaskComplexity(task) {
    const complexityIndicators = {
      high: ['architecture', 'optimize', 'design', 'implement', 'integrate', 'security', 'performance'],
      medium: ['analyze', 'review', 'improve', 'enhance', 'modify', 'update'],
      low: ['explain', 'describe', 'list', 'show', 'tell', 'what', 'how']
    };
    
    const taskLower = task.toLowerCase();
    
    for (const [level, indicators] of Object.entries(complexityIndicators)) {
      if (indicators.some(indicator => taskLower.includes(indicator))) {
        return level;
      }
    }
    
    return 'medium'; // default
  }

  /**
   * Classify the type of task being delegated
   */
  classifyTaskType(task) {
    const taskTypes = {
      'code-generation': ['generate', 'create', 'write', 'build', 'implement'],
      'analysis': ['analyze', 'review', 'assess', 'evaluate', 'examine'],
      'optimization': ['optimize', 'improve', 'enhance', 'speed up', 'performance'],
      'architecture': ['design', 'architecture', 'structure', 'pattern', 'framework'],
      'debugging': ['debug', 'fix', 'error', 'problem', 'issue', 'bug'],
      'explanation': ['explain', 'describe', 'how', 'what', 'why', 'tell']
    };
    
    const taskLower = task.toLowerCase();
    
    for (const [type, keywords] of Object.entries(taskTypes)) {
      if (keywords.some(keyword => taskLower.includes(keyword))) {
        return type;
      }
    }
    
    return 'general';
  }

  /**
   * Calculate verbosity score based on response length and content density
   */
  calculateVerbosityScore(response) {
    const length = response.length;
    const sentences = response.split(/[.!?]+/).length;
    const words = response.split(/\s+/).length;
    const avgWordsPerSentence = words / sentences;
    
    // Normalize scores
    const lengthScore = this.normalizeToScale(length, 0, 5000, 1, 5);
    const densityScore = this.normalizeToScale(avgWordsPerSentence, 5, 25, 1, 5);
    
    return {
      overall: (lengthScore + densityScore) / 2,
      length: lengthScore,
      density: densityScore,
      characterCount: length,
      wordCount: words,
      sentenceCount: sentences,
      avgWordsPerSentence: avgWordsPerSentence
    };
  }

  /**
   * Assess response quality across multiple dimensions
   */
  assessResponseQuality(task, response) {
    const relevance = this.assessRelevance(task, response);
    const completeness = this.assessCompleteness(response);
    const accuracy = this.assessTechnicalAccuracy(response);
    const actionability = this.assessActionability(response);
    const clarity = this.assessClarity(response);
    
    return {
      overall: (relevance + completeness + accuracy + actionability + clarity) / 5,
      relevance,
      completeness,
      accuracy,
      actionability,
      clarity,
      breakdown: {
        relevance: `${relevance}/5`,
        completeness: `${completeness}/5`,
        accuracy: `${accuracy}/5`,
        actionability: `${actionability}/5`,
        clarity: `${clarity}/5`
      }
    };
  }

  /**
   * Detect context drift in the response
   */
  detectContextDrift(originalContext, response) {
    if (!originalContext) return { drift: 0, severity: 'none' };
    
    // Extract key terms from original context
    const contextKeywords = this.extractKeywords(originalContext);
    const responseKeywords = this.extractKeywords(response);
    
    // Calculate overlap
    const overlap = this.calculateKeywordOverlap(contextKeywords, responseKeywords);
    const drift = 1 - overlap;
    
    let severity = 'none';
    if (drift > 0.5) severity = 'high';
    else if (drift > 0.3) severity = 'medium';
    else if (drift > 0.1) severity = 'low';
    
    return {
      drift: drift,
      severity: severity,
      contextKeywords: contextKeywords.length,
      responseKeywords: responseKeywords.length,
      overlap: overlap,
      recommendation: this.getContextDriftRecommendation(drift)
    };
  }

  /**
   * Helper methods for quality assessment
   */
  assessRelevance(task, response) {
    const taskKeywords = this.extractKeywords(task);
    const responseKeywords = this.extractKeywords(response);
    const overlap = this.calculateKeywordOverlap(taskKeywords, responseKeywords);
    return this.normalizeToScale(overlap, 0, 1, 1, 5);
  }

  assessCompleteness(response) {
    const completenessIndicators = [
      'analysis', 'approach', 'implementation', 'details', 'risks', 'outcomes',
      'steps', 'process', 'solution', 'recommendation'
    ];
    
    const found = completenessIndicators.filter(indicator => 
      response.toLowerCase().includes(indicator)
    );
    
    return this.normalizeToScale(found.length, 0, completenessIndicators.length, 1, 5);
  }

  assessTechnicalAccuracy(response) {
    // This would ideally use more sophisticated analysis
    // For now, we'll use heuristics based on technical terms and structure
    const technicalTerms = [
      'function', 'class', 'method', 'variable', 'array', 'object',
      'database', 'api', 'endpoint', 'algorithm', 'optimization',
      'security', 'performance', 'scalability', 'architecture'
    ];
    
    const foundTerms = technicalTerms.filter(term => 
      response.toLowerCase().includes(term)
    );
    
    return this.normalizeToScale(foundTerms.length, 0, 10, 1, 5);
  }

  assessActionability(response) {
    const actionableIndicators = [
      'implement', 'create', 'add', 'modify', 'update', 'configure',
      'install', 'setup', 'run', 'execute', 'test', 'deploy',
      'step 1', 'step 2', 'first', 'then', 'next', 'finally'
    ];
    
    const found = actionableIndicators.filter(indicator => 
      response.toLowerCase().includes(indicator)
    );
    
    return this.normalizeToScale(found.length, 0, 8, 1, 5);
  }

  assessClarity(response) {
    const sentences = response.split(/[.!?]+/).length;
    const words = response.split(/\s+/).length;
    const avgWordsPerSentence = words / sentences;
    
    // Optimal range: 10-20 words per sentence
    const clarityScore = avgWordsPerSentence < 10 ? 3 : 
                        avgWordsPerSentence <= 20 ? 5 : 
                        avgWordsPerSentence <= 30 ? 4 : 2;
    
    return clarityScore;
  }

  /**
   * Extract actionable items from the response
   */
  extractActionableItems(response) {
    const actionPatterns = [
      /\d+\.\s*(.+?)(?=\n|\d+\.|$)/g,  // Numbered lists
      /[-•]\s*(.+?)(?=\n|[-•]|$)/g,    // Bullet points
      /implement\s+(.+?)(?=\n|\.)/gi,   // Implementation steps
      /create\s+(.+?)(?=\n|\.)/gi,      // Creation tasks
      /add\s+(.+?)(?=\n|\.)/gi,         // Addition tasks
    ];
    
    const items = [];
    actionPatterns.forEach(pattern => {
      const matches = response.matchAll(pattern);
      for (const match of matches) {
        if (match[1] && match[1].trim().length > 10) {
          items.push(match[1].trim());
        }
      }
    });
    
    return {
      count: items.length,
      items: items.slice(0, 10), // Limit to top 10
      density: items.length / (response.length / 1000) // Items per 1000 chars
    };
  }

  /**
   * Generate performance recommendations based on metrics
   */
  generateRecommendations(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) return null;
    
    const recommendations = [];
    
    // Response time recommendations
    if (session.responseTime > this.benchmarks.responseTime.poor) {
      recommendations.push({
        type: 'performance',
        severity: 'high',
        issue: 'Slow response time',
        recommendation: 'Consider breaking down complex tasks into smaller, more focused requests'
      });
    }
    
    // Verbosity recommendations
    if (session.verbosityScore && session.verbosityScore.overall > 4) {
      recommendations.push({
        type: 'verbosity',
        severity: 'medium',
        issue: 'Response too verbose',
        recommendation: 'Add constraints to request more concise responses'
      });
    }
    
    // Quality recommendations
    if (session.qualityScore && session.qualityScore.overall < 3) {
      recommendations.push({
        type: 'quality',
        severity: 'high',
        issue: 'Low quality response',
        recommendation: 'Provide more specific context and clearer task definition'
      });
    }
    
    // Context drift recommendations
    if (session.contextDrift && session.contextDrift.severity === 'high') {
      recommendations.push({
        type: 'context',
        severity: 'high',
        issue: 'High context drift detected',
        recommendation: 'Refine the task description to better align with the intended context'
      });
    }
    
    return recommendations;
  }

  /**
   * Generate comprehensive session report
   */
  generateSessionReport(session) {
    const recommendations = this.generateRecommendations(session.id);
    
    return {
      sessionId: session.id,
      timestamp: new Date().toISOString(),
      performance: {
        responseTime: session.responseTime,
        responseTimeRating: this.rateResponseTime(session.responseTime),
        success: session.success,
        errorType: session.errorType
      },
      verbosity: {
        score: session.verbosityScore,
        rating: this.rateVerbosity(session.verbosityScore?.overall),
        characterCount: session.responseLength
      },
      quality: {
        score: session.qualityScore,
        rating: this.rateQuality(session.qualityScore?.overall),
        breakdown: session.qualityScore?.breakdown
      },
      context: {
        drift: session.contextDrift,
        taskComplexity: session.taskComplexity,
        taskType: session.taskType
      },
      actionability: {
        items: session.actionableItems,
        technicalAccuracy: session.technicalAccuracy
      },
      recommendations: recommendations,
      summary: this.generateSummary(session)
    };
  }

  /**
   * Helper methods
   */
  normalizeToScale(value, min, max, scaleMin, scaleMax) {
    const normalized = Math.max(Math.min(value, max), min);
    return scaleMin + (normalized - min) * (scaleMax - scaleMin) / (max - min);
  }

  extractKeywords(text) {
    return text.toLowerCase()
      .replace(/[^\w\s]/g, '')
      .split(/\s+/)
      .filter(word => word.length > 3)
      .filter(word => !['this', 'that', 'with', 'from', 'they', 'have', 'will', 'been', 'were'].includes(word));
  }

  calculateKeywordOverlap(keywords1, keywords2) {
    const set1 = new Set(keywords1);
    const set2 = new Set(keywords2);
    const intersection = new Set([...set1].filter(x => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    return intersection.size / union.size;
  }

  rateResponseTime(responseTime) {
    if (responseTime < this.benchmarks.responseTime.excellent) return 'excellent';
    if (responseTime < this.benchmarks.responseTime.good) return 'good';
    if (responseTime < this.benchmarks.responseTime.acceptable) return 'acceptable';
    return 'poor';
  }

  rateVerbosity(score) {
    if (score < 2) return 'terse';
    if (score < 3) return 'concise';
    if (score < 4) return 'detailed';
    return 'verbose';
  }

  rateQuality(score) {
    if (score > this.benchmarks.quality.excellent) return 'excellent';
    if (score > this.benchmarks.quality.good) return 'good';
    if (score > this.benchmarks.quality.acceptable) return 'acceptable';
    return 'poor';
  }

  getContextDriftRecommendation(drift) {
    if (drift > 0.5) return 'High context drift detected. Consider rephrasing the task with more specific context.';
    if (drift > 0.3) return 'Moderate context drift. Task could benefit from clearer context definition.';
    if (drift > 0.1) return 'Minor context drift. Response is mostly aligned with context.';
    return 'Good context alignment. Response stays on topic.';
  }

  generateSummary(session) {
    const timeRating = this.rateResponseTime(session.responseTime);
    const qualityRating = this.rateQuality(session.qualityScore?.overall);
    const verbosityRating = this.rateVerbosity(session.verbosityScore?.overall);
    
    return {
      overall: session.success ? 'successful' : 'failed',
      responseTime: `${session.responseTime}ms (${timeRating})`,
      quality: `${session.qualityScore?.overall.toFixed(1)}/5 (${qualityRating})`,
      verbosity: `${verbosityRating}`,
      contextDrift: session.contextDrift?.severity || 'none',
      actionableItems: session.actionableItems?.count || 0,
      taskComplexity: session.taskComplexity
    };
  }

  /**
   * Update global metrics
   */
  updateGlobalMetrics(session) {
    this.globalMetrics.totalDelegations++;
    
    if (session.success) {
      const total = this.globalMetrics.totalDelegations;
      this.globalMetrics.averageResponseTime = 
        (this.globalMetrics.averageResponseTime * (total - 1) + session.responseTime) / total;
      
      if (session.verbosityScore) {
        this.globalMetrics.averageVerbosity = 
          (this.globalMetrics.averageVerbosity * (total - 1) + session.verbosityScore.overall) / total;
      }
      
      if (session.qualityScore) {
        this.globalMetrics.averageQuality = 
          (this.globalMetrics.averageQuality * (total - 1) + session.qualityScore.overall) / total;
      }
      
      if (session.contextDrift && session.contextDrift.severity !== 'none') {
        this.globalMetrics.contextDriftEvents++;
      }
    }
    
    const successfulSessions = Array.from(this.sessions.values()).filter(s => s.success).length;
    this.globalMetrics.successRate = successfulSessions / this.globalMetrics.totalDelegations;
  }

  /**
   * Get global performance metrics
   */
  getGlobalMetrics() {
    const uptime = Date.now() - this.globalMetrics.startTime;
    
    return {
      ...this.globalMetrics,
      uptime: uptime,
      uptimeFormatted: this.formatUptime(uptime),
      sessionsActive: this.sessions.size,
      averageResponseTimeFormatted: `${this.globalMetrics.averageResponseTime.toFixed(0)}ms`,
      successRateFormatted: `${(this.globalMetrics.successRate * 100).toFixed(1)}%`,
      contextDriftRate: this.globalMetrics.contextDriftEvents / this.globalMetrics.totalDelegations
    };
  }

  formatUptime(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }

  /**
   * Export metrics for analysis
   */
  exportMetrics() {
    return {
      global: this.getGlobalMetrics(),
      sessions: Array.from(this.sessions.entries()).map(([id, session]) => ({
        id,
        ...session
      })),
      exportedAt: new Date().toISOString()
    };
  }
}

export default DelegationMetrics;