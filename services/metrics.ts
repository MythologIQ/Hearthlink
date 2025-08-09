export {}
const fs = require('fs').promises;
const path = require('path');

// Token bucket rate limiter (better than O(n) array filtering)
class TokenBucketRateLimiter {
  maxTokens: number;
  tokens: number;
  refillRate: number;
  lastRefill: number;
  
  constructor(maxTokens = 60, refillRate = 1, refillInterval = 1000) {
    this.maxTokens = maxTokens;
    this.tokens = maxTokens;
    this.refillRate = refillRate;
    this.lastRefill = Date.now();
    
    // Automatically refill tokens
    setInterval(() => this.refill(), refillInterval);
  }
  
  refill() {
    const now = Date.now();
    const timePassed = now - this.lastRefill;
    const tokensToAdd = Math.floor(timePassed / 1000) * this.refillRate;
    
    this.tokens = Math.min(this.maxTokens, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }
  
  canMakeRequest() {
    this.refill();
    return this.tokens > 0;
  }
  
  addRequest() {
    if (this.canMakeRequest()) {
      this.tokens--;
      return true;
    }
    return false;
  }
  
  getWaitTime() {
    if (this.tokens > 0) return 0;
    return Math.ceil((1 - (this.tokens % 1)) * 1000);
  }
  
  getRemainingRequests() {
    this.refill();
    return this.tokens;
  }
}

// Delegation Metrics Tracking with async persistence
class DelegationMetricsTracker {
  sessions: Map<string, any>;
  globalMetrics: any;
  persistenceQueue: any[];
  isProcessingQueue: boolean;
  
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
    this.persistenceQueue = [];
    this.isProcessingQueue = false;
  }

  startSession(sessionId, taskData) {
    const session = {
      sessionId,
      taskData,
      startTime: Date.now(),
      delegations: [],
      status: 'active'
    };
    
    this.sessions.set(sessionId, session);
    this.queuePersistence('session_start', { sessionId, session });
    return session;
  }

  addDelegation(sessionId, delegationData) {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    const delegation = {
      id: Date.now(),
      timestamp: Date.now(),
      ...delegationData
    };

    session.delegations.push(delegation);
    this.globalMetrics.totalDelegations++;
    
    this.queuePersistence('delegation_add', { sessionId, delegation });
    return delegation;
  }

  endSession(sessionId, finalMetrics = {}) {
    const session = this.sessions.get(sessionId);
    if (!session) return null;

    session.endTime = Date.now();
    session.duration = session.endTime - session.startTime;
    session.status = 'completed';
    session.finalMetrics = finalMetrics;

    this.updateGlobalMetrics(session);
    this.queuePersistence('session_end', { sessionId, session });
    
    return session;
  }

  updateGlobalMetrics(session) {
    // Calculate averages based on all completed sessions
    const completedSessions = Array.from(this.sessions.values())
      .filter(s => s.status === 'completed');
    
    if (completedSessions.length === 0) return;

    // Recalculate global metrics
    const totalDelegations = completedSessions.reduce((sum, s) => sum + s.delegations.length, 0);
    const avgResponseTime = completedSessions.reduce((sum, s) => 
      sum + (s.finalMetrics?.responseTime || 0), 0) / completedSessions.length;
    
    this.globalMetrics = {
      ...this.globalMetrics,
      totalDelegations,
      averageResponseTime: avgResponseTime,
      successRate: completedSessions.filter(s => s.finalMetrics?.success).length / completedSessions.length
    };
  }

  // Async persistence queue to avoid blocking
  queuePersistence(operation, data) {
    this.persistenceQueue.push({ operation, data, timestamp: Date.now() });
    
    if (!this.isProcessingQueue) {
      this.processQueue();
    }
  }

  async processQueue() {
    if (this.isProcessingQueue) return;
    this.isProcessingQueue = true;

    while (this.persistenceQueue.length > 0) {
      const item = this.persistenceQueue.shift();
      try {
        await this.persistItem(item);
      } catch (error) {
        console.error('Failed to persist metrics:', error);
      }
    }

    this.isProcessingQueue = false;
  }

  async persistItem(item) {
    const userDataPath = path.join(__dirname, '..', 'userData');
    const metricsPath = path.join(userDataPath, 'delegation-metrics.json');
    
    try {
      // Read existing data
      let existingData: {
        sessions: Record<string, any>;
        globalMetrics: any;
        lastUpdated?: number;
      } = { sessions: {}, globalMetrics: this.globalMetrics };
      try {
        const content = await fs.readFile(metricsPath, 'utf8');
        existingData = JSON.parse(content);
      } catch (error) {
        // File doesn't exist yet, use defaults
      }

      // Update with new data
      switch (item.operation) {
        case 'session_start':
        case 'session_end':
          existingData.sessions[item.data.sessionId] = item.data.session;
          break;
        case 'delegation_add':
          if (existingData.sessions[item.data.sessionId]) {
            existingData.sessions[item.data.sessionId].delegations = 
              existingData.sessions[item.data.sessionId].delegations || [];
            existingData.sessions[item.data.sessionId].delegations.push(item.data.delegation);
          }
          break;
      }

      existingData.globalMetrics = this.globalMetrics;
      existingData.lastUpdated = Date.now();

      // Write back to file
      await fs.writeFile(metricsPath, JSON.stringify(existingData, null, 2));
      
      // Compress old data if file gets too large
      await this.compressOldData(metricsPath);
      
    } catch (error) {
      console.error('Error persisting metrics:', error);
    }
  }

  async compressOldData(metricsPath) {
    try {
      const stats = await fs.stat(metricsPath);
      const fileSizeMB = stats.size / (1024 * 1024);
      
      // If file is larger than 10MB, archive old sessions
      if (fileSizeMB > 10) {
        const content = await fs.readFile(metricsPath, 'utf8');
        const data = JSON.parse(content);
        
        const oneWeekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
        const recentSessions = {};
        const oldSessions = {};
        
        for (const [sessionId, session] of Object.entries(data.sessions)) {
          const typedSession = session as { startTime?: number };
          if (typedSession.startTime && typedSession.startTime > oneWeekAgo) {
            recentSessions[sessionId] = session;
          } else {
            oldSessions[sessionId] = session;
          }
        }
        
        // Archive old sessions
        if (Object.keys(oldSessions).length > 0) {
          const archivePath = path.join(path.dirname(metricsPath), 
            `delegation-metrics-archive-${Date.now()}.json.gz`);
          
          const zlib = require('zlib');
          const compressed = zlib.gzipSync(JSON.stringify(oldSessions));
          await fs.writeFile(archivePath, compressed);
        }
        
        // Keep only recent sessions
        data.sessions = recentSessions;
        await fs.writeFile(metricsPath, JSON.stringify(data, null, 2));
      }
    } catch (error) {
      console.error('Error compressing old metrics data:', error);
    }
  }

  getMetrics() {
    return {
      globalMetrics: this.globalMetrics,
      activeSessions: this.sessions.size,
      recentSessions: Array.from(this.sessions.values())
        .filter(s => s.startTime > Date.now() - (24 * 60 * 60 * 1000))
        .length
    };
  }
}

const googleRateLimiter = new TokenBucketRateLimiter(60, 1, 1000);
const delegationTracker = new DelegationMetricsTracker();

module.exports = {
  TokenBucketRateLimiter,
  DelegationMetricsTracker,
  googleRateLimiter,
  delegationTracker
};export {}
