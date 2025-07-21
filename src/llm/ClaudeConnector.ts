/**
 * Claude Connector for Hearthlink
 * 
 * Routes Claude API requests through Synapse security gateway with comprehensive
 * token tracking, error handling, and vault storage integration.
 * 
 * This is the critical path connector until Phase 3 write-to-disk is enabled.
 */

import { log_agent_token_usage } from '../log_handling/agent_token_tracker';

interface ClaudeConfig {
  baseUrl: string;
  apiKey: string;
  model: string;
  maxTokens: number;
  temperature: number;
  timeout: number;
  maxRetries: number;
  retryDelay: number;
  vaultEnabled: boolean;
  synapseEndpoint: string;
}

interface ClaudeRequest {
  prompt: string;
  systemMessage?: string;
  temperature?: number;
  maxTokens?: number;
  agentId: string;
  module: string;
  requestId?: string;
  context?: Record<string, any>;
}

interface ClaudeResponse {
  content: string;
  model: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  responseTime: number;
  timestamp: string;
  requestId: string;
  finishReason: string;
}

interface ClaudeError {
  type: 'connection_error' | 'auth_error' | 'rate_limit' | 'timeout' | 'api_error' | 'vault_error';
  message: string;
  statusCode?: number;
  retryAfter?: number;
  requestId?: string;
}

export class ClaudeConnector {
  private config: ClaudeConfig;
  private requestQueue: Map<string, ClaudeRequest> = new Map();
  
  constructor(config: ClaudeConfig) {
    this.config = config;
    this.validateConfig();
  }

  private validateConfig(): void {
    if (!this.config.apiKey) {
      throw new Error('Claude API key is required');
    }
    if (!this.config.baseUrl) {
      throw new Error('Claude base URL is required');
    }
    if (!this.config.synapseEndpoint) {
      throw new Error('Synapse endpoint is required for secure routing');
    }
  }

  /**
   * Generate response from Claude via Synapse routing
   */
  async generate(request: ClaudeRequest): Promise<ClaudeResponse> {
    const startTime = Date.now();
    const requestId = request.requestId || this.generateRequestId();
    
    try {
      // Add to request queue for tracking
      this.requestQueue.set(requestId, { ...request, requestId });
      
      // Route through Synapse for security validation
      const synapseResponse = await this.routeThroughSynapse(request, requestId);
      
      // Make Claude API call
      const claudeResponse = await this.callClaudeAPI(synapseResponse.validatedRequest, requestId);
      
      // Calculate response metrics
      const responseTime = Date.now() - startTime;
      
      // Store completion to vault via Synapse
      if (this.config.vaultEnabled) {
        await this.storeToVault(claudeResponse, request, requestId);
      }
      
      // Track token usage
      await this.trackTokenUsage(request, claudeResponse, responseTime);
      
      // Remove from queue
      this.requestQueue.delete(requestId);
      
      return {
        content: claudeResponse.content[0].text,
        model: claudeResponse.model,
        usage: {
          promptTokens: claudeResponse.usage.input_tokens,
          completionTokens: claudeResponse.usage.output_tokens,
          totalTokens: claudeResponse.usage.input_tokens + claudeResponse.usage.output_tokens
        },
        responseTime,
        timestamp: new Date().toISOString(),
        requestId,
        finishReason: claudeResponse.stop_reason || 'stop'
      };
      
    } catch (error) {
      // Remove from queue on error
      this.requestQueue.delete(requestId);
      
      // Handle and log error
      const claudeError = this.handleError(error, requestId, request);
      await this.logError(claudeError, request);
      
      throw claudeError;
    }
  }

  /**
   * Route request through Synapse security gateway
   */
  private async routeThroughSynapse(request: ClaudeRequest, requestId: string): Promise<any> {
    const synapseUrl = `${this.config.synapseEndpoint}/api/claude/validate`;
    
    const payload = {
      agentId: request.agentId,
      module: request.module,
      requestId,
      prompt: request.prompt,
      systemMessage: request.systemMessage,
      context: request.context
    };
    
    const response = await fetch(synapseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Hearthlink-Agent': request.agentId,
        'X-Request-ID': requestId
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(this.config.timeout)
    });
    
    if (!response.ok) {
      throw new Error(`Synapse validation failed: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }

  /**
   * Make actual Claude API call
   */
  private async callClaudeAPI(validatedRequest: any, requestId: string): Promise<any> {
    const claudeUrl = `${this.config.baseUrl}/v1/messages`;
    
    const payload = {
      model: this.config.model,
      max_tokens: validatedRequest.maxTokens || this.config.maxTokens,
      temperature: validatedRequest.temperature || this.config.temperature,
      system: validatedRequest.systemMessage,
      messages: [
        {
          role: 'user',
          content: validatedRequest.prompt
        }
      ]
    };
    
    let lastError;
    
    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        const response = await fetch(claudeUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.config.apiKey}`,
            'X-API-Key': this.config.apiKey,
            'anthropic-version': '2023-06-01',
            'X-Request-ID': requestId
          },
          body: JSON.stringify(payload),
          signal: AbortSignal.timeout(this.config.timeout)
        });
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(`Claude API error: ${response.status} ${response.statusText} - ${JSON.stringify(errorData)}`);
        }
        
        return response.json();
        
      } catch (error) {
        lastError = error;
        
        if (attempt < this.config.maxRetries) {
          // Wait before retry with exponential backoff
          await new Promise(resolve => 
            setTimeout(resolve, this.config.retryDelay * Math.pow(2, attempt))
          );
        }
      }
    }
    
    throw lastError;
  }

  /**
   * Store Claude completion to Vault via Synapse
   */
  private async storeToVault(claudeResponse: any, request: ClaudeRequest, requestId: string): Promise<void> {
    try {
      const vaultUrl = `${this.config.synapseEndpoint}/api/vault/append`;
      
      const vaultPayload = {
        agentId: request.agentId,
        module: request.module,
        requestId,
        data: {
          prompt: request.prompt,
          response: claudeResponse.content[0].text,
          model: claudeResponse.model,
          usage: claudeResponse.usage,
          timestamp: new Date().toISOString()
        }
      };
      
      const response = await fetch(vaultUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Hearthlink-Agent': request.agentId,
          'X-Request-ID': requestId
        },
        body: JSON.stringify(vaultPayload)
      });
      
      if (!response.ok) {
        console.warn(`Failed to store to vault: ${response.status} ${response.statusText}`);
      }
      
    } catch (error) {
      console.warn('Vault storage failed:', error);
      // Don't throw - vault storage is non-critical for generation
    }
  }

  /**
   * Track token usage via agent token tracker
   */
  private async trackTokenUsage(request: ClaudeRequest, response: any, responseTime: number): Promise<void> {
    try {
      const totalTokens = response.usage.input_tokens + response.usage.output_tokens;
      
      await log_agent_token_usage(
        'claude',
        'claude',
        totalTokens,
        `Generated response: ${request.prompt.substring(0, 100)}...`,
        request.module,
        {
          operation_type: 'inference',
          request_id: request.requestId,
          prompt_tokens: response.usage.input_tokens,
          completion_tokens: response.usage.output_tokens,
          total_tokens: totalTokens,
          model_name: response.model,
          temperature: request.temperature || this.config.temperature,
          max_tokens: request.maxTokens || this.config.maxTokens,
          response_time_ms: responseTime,
          success: true
        }
      );
      
    } catch (error) {
      console.warn('Token tracking failed:', error);
      // Don't throw - token tracking is non-critical for generation
    }
  }

  /**
   * Handle and classify errors
   */
  private handleError(error: any, requestId: string, _request: ClaudeRequest): ClaudeError {
    let errorType: ClaudeError['type'] = 'api_error';
    let statusCode: number | undefined;
    let retryAfter: number | undefined;
    
    if (error.name === 'AbortError' || error.message?.includes('timeout')) {
      errorType = 'timeout';
    } else if (error.message?.includes('401') || error.message?.includes('unauthorized')) {
      errorType = 'auth_error';
      statusCode = 401;
    } else if (error.message?.includes('429') || error.message?.includes('rate limit')) {
      errorType = 'rate_limit';
      statusCode = 429;
      // Extract retry-after if available
      const retryMatch = error.message.match(/retry-after:\s*(\d+)/i);
      if (retryMatch) {
        retryAfter = parseInt(retryMatch[1]);
      }
    } else if (error.message?.includes('fetch') || error.message?.includes('network')) {
      errorType = 'connection_error';
    } else if (error.message?.includes('vault')) {
      errorType = 'vault_error';
    }
    
    const claudeError: ClaudeError = {
      type: errorType,
      message: error.message || 'Unknown error occurred',
      requestId
    };
    
    if (statusCode !== undefined) {
      claudeError.statusCode = statusCode;
    }
    
    if (retryAfter !== undefined) {
      claudeError.retryAfter = retryAfter;
    }
    
    return claudeError;
  }

  /**
   * Log error details
   */
  private async logError(error: ClaudeError, request: ClaudeRequest): Promise<void> {
    try {
      await log_agent_token_usage(
        'claude',
        'claude',
        0, // No tokens used on error
        `Error: ${request.prompt.substring(0, 100)}...`,
        request.module,
        {
          operation_type: 'inference',
          request_id: error.requestId,
          success: false,
          error_message: error.message,
          error_type: error.type,
          status_code: error.statusCode
        }
      );
    } catch (trackingError) {
      console.warn('Error tracking failed:', trackingError);
    }
  }

  /**
   * Generate unique request ID
   */
  private generateRequestId(): string {
    return `claude_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get current queue status
   */
  getQueueStatus(): { active: number; requests: string[] } {
    return {
      active: this.requestQueue.size,
      requests: Array.from(this.requestQueue.keys())
    };
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: 'healthy' | 'degraded' | 'unhealthy'; details: Record<string, any> }> {
    try {
      // Test Synapse connectivity
      const synapseResponse = await fetch(`${this.config.synapseEndpoint}/api/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000)
      });
      
      const synapseHealthy = synapseResponse.ok;
      
      // Test Claude API connectivity (simple ping)
      const claudeResponse = await fetch(`${this.config.baseUrl}/v1/models`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'anthropic-version': '2023-06-01'
        },
        signal: AbortSignal.timeout(5000)
      });
      
      const claudeHealthy = claudeResponse.ok;
      
      const queueSize = this.requestQueue.size;
      
      let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
      
      if (!synapseHealthy || !claudeHealthy) {
        status = 'unhealthy';
      } else if (queueSize > 10) {
        status = 'degraded';
      }
      
      return {
        status,
        details: {
          synapse: synapseHealthy,
          claude: claudeHealthy,
          queueSize,
          timestamp: new Date().toISOString()
        }
      };
      
    } catch (error) {
      return {
        status: 'unhealthy',
        details: {
          error: error instanceof Error ? error.message : 'Unknown error',
          timestamp: new Date().toISOString()
        }
      };
    }
  }
}

// Default configuration
export const DEFAULT_CLAUDE_CONFIG: ClaudeConfig = {
  baseUrl: 'https://api.anthropic.com',
  apiKey: process.env.REACT_APP_CLAUDE_API_KEY || '',
  model: 'claude-3-sonnet-20240229',
  maxTokens: 4096,
  temperature: 0.7,
  timeout: 30000,
  maxRetries: 3,
  retryDelay: 1000,
  vaultEnabled: true,
  synapseEndpoint: process.env.REACT_APP_SYNAPSE_ENDPOINT || 'http://localhost:8080'
};

// Factory function
export function createClaudeConnector(config?: Partial<ClaudeConfig>): ClaudeConnector {
  const finalConfig = { ...DEFAULT_CLAUDE_CONFIG, ...config };
  return new ClaudeConnector(finalConfig);
}

// Singleton instance for app-wide use
let _claudeConnector: ClaudeConnector | null = null;

export function getClaudeConnector(config?: Partial<ClaudeConfig>): ClaudeConnector {
  if (!_claudeConnector) {
    _claudeConnector = createClaudeConnector(config);
  }
  return _claudeConnector;
}