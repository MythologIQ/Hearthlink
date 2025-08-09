/**
 * Alden API Service
 * Handles communication with the Alden backend running on port 8888
 */
class AldenAPIService {
  constructor() {
    this.baseURL = 'http://localhost:8888';
    this.healthCheckInterval = null;
    this.isHealthy = false;
  }

  /**
   * Initialize the service and start health monitoring
   */
  async initialize() {
    await this.checkHealth();
    this.startHealthMonitoring();
    return this;
  }

  /**
   * Check if Alden backend is healthy
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const healthData = await response.json();
        this.isHealthy = healthData.status === 'healthy';
        return this.isHealthy;
      } else {
        this.isHealthy = false;
        return false;
      }
    } catch (error) {
      console.warn('Alden health check failed:', error.message);
      this.isHealthy = false;
      return false;
    }
  }

  /**
   * Start periodic health monitoring
   */
  startHealthMonitoring(intervalMs = 30000) {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }

    this.healthCheckInterval = setInterval(async () => {
      await this.checkHealth();
    }, intervalMs);
  }

  /**
   * Stop health monitoring
   */
  stopHealthMonitoring() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }
  }

  /**
   * Send a message to Alden and get a response
   */
  async sendMessage(message, context = {}) {
    if (!this.isHealthy) {
      await this.checkHealth();
      if (!this.isHealthy) {
        throw new Error('Alden backend is not available');
      }
    }

    try {
      const response = await fetch(`${this.baseURL}/conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: message,
          context: context,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.status === 'success') {
        return {
          response: data.response,
          status: 'success',
          timestamp: new Date(),
          metadata: data.metadata || {}
        };
      } else {
        throw new Error(data.error || 'Unknown error from Alden backend');
      }
    } catch (error) {
      console.error('Failed to send message to Alden:', error);
      throw new Error(`Alden communication failed: ${error.message}`);
    }
  }

  /**
   * Get Alden's current status and system information
   */
  async getStatus() {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        return await response.json();
      } else {
        throw new Error(`Status check failed: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Failed to get Alden status:', error);
      throw error;
    }
  }

  /**
   * Get conversation history (if supported by backend)
   */
  async getConversationHistory(limit = 10) {
    try {
      const response = await fetch(`${this.baseURL}/conversation/history?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        return await response.json();
      } else if (response.status === 404) {
        // Endpoint not implemented yet
        return { history: [], total: 0 };
      } else {
        throw new Error(`History fetch failed: ${response.statusText}`);
      }
    } catch (error) {
      console.warn('Failed to get conversation history:', error);
      return { history: [], total: 0 };
    }
  }

  /**
   * Check if the service is available
   */
  isAvailable() {
    return this.isHealthy;
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.stopHealthMonitoring();
  }
}

// Create singleton instance
const aldenAPIService = new AldenAPIService();

// Auto-initialize when imported
aldenAPIService.initialize().catch(error => {
  console.warn('Alden API Service initialization failed:', error.message);
});

export default aldenAPIService;