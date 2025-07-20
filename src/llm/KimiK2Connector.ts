import { CircuitBreaker } from '../utils/CircuitBreaker';
import { TokenTracker } from '../monitoring/TokenTracker';
import { Vault } from '../vault/vault';
import { SecurityError, RateLimitError, APIError } from '../utils/errors';

export interface KimiK2Config {
  apiKey: string;
  baseUrl: string;
  model: string;
  maxTokens: number;
  temperature: number;
  timeout: number;
  retryAttempts: number;
  enableCaching: boolean;
  enableMetrics: boolean;
}

export interface Tool {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: Record<string, any>;
  };
}

export interface ToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

export interface KimiK2Request {
  prompt: string;
  systemMessage?: string;
  temperature?: number;
  maxTokens?: number;
  agentId: string;
  module: string;
  context?: Record<string, any>;
  tools?: Tool[];
  toolChoice?: 'auto' | 'none' | { type: 'function'; function: { name: string } };
  stream?: boolean;
  preferredBackend?: string;
}

export interface KimiK2Response {
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
  finishReason: 'stop' | 'length' | 'tool_calls';
  backend: string;
  toolCalls?: ToolCall[];
  metadata?: Record<string, any>;
}

export interface SecurityValidationResult {
  approved: boolean;
  reason?: string;
  details?: Record<string, any>;
}

export class KimiK2Connector {
  private config: KimiK2Config;
  private circuitBreaker: CircuitBreaker;
  private tokenTracker: TokenTracker;
  private vault: Vault;
  private cache: Map<string, { response: KimiK2Response; timestamp: number }>;
  private readonly CACHE_TTL = 300000; // 5 minutes

  constructor(config: KimiK2Config) {
    this.config = config;
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 5,
      resetTimeout: 30000,
      timeout: config.timeout || 30000
    });
    this.tokenTracker = new TokenTracker('kimi-k2');
    this.vault = new Vault();
    this.cache = new Map();
  }

  async chat(request: KimiK2Request): Promise<KimiK2Response> {
    const requestId = this.generateRequestId();
    const startTime = Date.now();

    try {
      // Check cache first
      if (this.config.enableCaching && !request.tools) {
        const cacheKey = this.generateCacheKey(request);
        const cached = this.getFromCache(cacheKey);
        if (cached) {
          return cached;
        }
      }

      // Execute through circuit breaker
      const response = await this.circuitBreaker.execute(async () => {
        // Validate request through Synapse security gateway
        const validationResult = await this.validateRequest(request);
        if (!validationResult.approved) {
          throw new SecurityError(validationResult.reason || 'Request blocked by security policy');
        }

        // Prepare OpenAI-compatible request
        const openAIRequest = this.formatOpenAIRequest(request);

        // Make API call
        const apiResponse = await this.makeAPICall(openAIRequest);

        // Format response
        const formattedResponse = this.formatResponse(apiResponse, startTime, requestId);

        // Cache successful response
        if (this.config.enableCaching && !request.tools) {
          const cacheKey = this.generateCacheKey(request);
          this.setCache(cacheKey, formattedResponse);
        }

        return formattedResponse;
      });

      // Store interaction in Vault
      await this.vault.storeInteraction(request, response);

      // Track usage metrics
      if (this.config.enableMetrics) {
        this.tokenTracker.trackUsage(response.usage);
      }

      return response;

    } catch (error) {
      await this.handleError(error, request, requestId);
      throw error;
    }
  }

  private async validateRequest(request: KimiK2Request): Promise<SecurityValidationResult> {
    try {
      // Content safety check
      const contentSafe = await this.checkContentSafety(request.prompt);
      if (!contentSafe) {
        return {
          approved: false,
          reason: 'Content safety violation detected'
        };
      }

      // Token limit check
      const estimatedTokens = this.estimateTokens(request.prompt);
      if (estimatedTokens > this.config.maxTokens) {
        return {
          approved: false,
          reason: 'Token limit exceeded',
          details: { estimated: estimatedTokens, limit: this.config.maxTokens }
        };
      }

      // Tool calling permission check
      if (request.tools && request.tools.length > 0) {
        const toolsAllowed = await this.checkToolPermissions(request.tools, request.agentId);
        if (!toolsAllowed) {
          return {
            approved: false,
            reason: 'Tool calling not permitted for this agent'
          };
        }
      }

      // Rate limiting check
      const rateLimitOk = await this.checkRateLimit(request.agentId);
      if (!rateLimitOk) {
        return {
          approved: false,
          reason: 'Rate limit exceeded'
        };
      }

      return { approved: true };

    } catch (error) {
      console.error('Security validation error:', error);
      return {
        approved: false,
        reason: 'Security validation failed'
      };
    }
  }

  private formatOpenAIRequest(request: KimiK2Request): any {
    const messages = [];
    
    if (request.systemMessage) {
      messages.push({
        role: 'system',
        content: request.systemMessage
      });
    }

    messages.push({
      role: 'user',
      content: request.prompt
    });

    const openAIRequest: any = {
      model: this.config.model,
      messages: messages,
      temperature: (request.temperature || this.config.temperature) * 0.6, // Kimi K2 temperature mapping
      max_tokens: request.maxTokens || this.config.maxTokens,
      stream: request.stream || false
    };

    // Add tool calling if specified
    if (request.tools && request.tools.length > 0) {
      openAIRequest.tools = request.tools;
      openAIRequest.tool_choice = request.toolChoice || 'auto';
    }

    return openAIRequest;
  }

  private async makeAPICall(request: any): Promise<any> {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.config.apiKey}`,
      'HTTP-Referer': 'https://hearthlink.ai',
      'X-Title': 'Hearthlink AI Orchestration'
    };

    const response = await fetch(this.config.baseUrl + '/chat/completions', {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
      signal: AbortSignal.timeout(this.config.timeout)
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      if (response.status === 401) {
        throw new APIError('Authentication failed', 401, errorData);
      } else if (response.status === 429) {
        throw new RateLimitError('Rate limit exceeded', response.headers.get('retry-after'));
      } else {
        throw new APIError(`API request failed: ${response.status}`, response.status, errorData);
      }
    }

    return await response.json();
  }

  private formatResponse(apiResponse: any, startTime: number, requestId: string): KimiK2Response {
    const responseTime = Date.now() - startTime;
    const choice = apiResponse.choices[0];
    const usage = apiResponse.usage;

    const response: KimiK2Response = {
      content: choice.message.content || '',
      model: apiResponse.model,
      usage: {
        promptTokens: usage.prompt_tokens,
        completionTokens: usage.completion_tokens,
        totalTokens: usage.total_tokens
      },
      responseTime,
      timestamp: new Date().toISOString(),
      requestId,
      finishReason: choice.finish_reason,
      backend: 'kimi-k2'
    };

    // Add tool calls if present
    if (choice.message.tool_calls) {
      response.toolCalls = choice.message.tool_calls.map((toolCall: any) => ({
        id: toolCall.id,
        type: 'function',
        function: {
          name: toolCall.function.name,
          arguments: toolCall.function.arguments
        }
      }));
    }

    return response;
  }

  private async handleError(error: Error, request: KimiK2Request, requestId: string): Promise<void> {
    const errorLog = {
      error: error.message,
      type: error.constructor.name,
      request: {
        agentId: request.agentId,
        module: request.module,
        hasTools: !!(request.tools && request.tools.length > 0)
      },
      requestId,
      timestamp: new Date().toISOString()
    };

    // Log error to Vault
    await this.vault.logError(errorLog);

    // Track error metrics
    if (this.config.enableMetrics) {
      this.tokenTracker.trackError(error);
    }

    console.error('KimiK2Connector error:', errorLog);
  }

  // Cache management methods
  private generateCacheKey(request: KimiK2Request): string {
    const keyData = {
      prompt: request.prompt,
      systemMessage: request.systemMessage,
      temperature: request.temperature,
      maxTokens: request.maxTokens,
      agentId: request.agentId
    };
    return Buffer.from(JSON.stringify(keyData)).toString('base64');
  }

  private getFromCache(key: string): KimiK2Response | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.CACHE_TTL) {
      return cached.response;
    }
    if (cached) {
      this.cache.delete(key);
    }
    return null;
  }

  private setCache(key: string, response: KimiK2Response): void {
    this.cache.set(key, {
      response,
      timestamp: Date.now()
    });
  }

  // Utility methods
  private generateRequestId(): string {
    return `kimi-k2-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private estimateTokens(text: string): number {
    // Rough token estimation: ~4 characters per token
    return Math.ceil(text.length / 4);
  }

  private async checkContentSafety(content: string): Promise<boolean> {
    // Implement content safety check
    // This would integrate with your content filtering system
    return true; // Placeholder
  }

  private async checkToolPermissions(tools: Tool[], agentId: string): Promise<boolean> {
    // Implement tool permission checking
    // This would check against your permission system
    return true; // Placeholder
  }

  private async checkRateLimit(agentId: string): Promise<boolean> {
    // Implement rate limiting check
    // This would check against your rate limiting system
    return true; // Placeholder
  }

  // Health check method
  async healthCheck(): Promise<{ status: 'healthy' | 'unhealthy'; details?: any }> {
    try {
      const testRequest: KimiK2Request = {
        prompt: 'Health check',
        agentId: 'health-check',
        module: 'health',
        maxTokens: 10,
        temperature: 0.1
      };

      const response = await this.chat(testRequest);
      
      return {
        status: 'healthy',
        details: {
          responseTime: response.responseTime,
          model: response.model,
          timestamp: response.timestamp
        }
      };

    } catch (error) {
      return {
        status: 'unhealthy',
        details: {
          error: error.message,
          timestamp: new Date().toISOString()
        }
      };
    }
  }

  // Cleanup method
  cleanup(): void {
    this.cache.clear();
    this.circuitBreaker.reset();
  }
}