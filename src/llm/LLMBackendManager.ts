/**
 * LLM Backend Manager - Universal LLM Integration
 * 
 * Supports multiple LLM backends:
 * - Claude API (for users with API keys)
 * - Claude Code CLI (for Claude Code users like current setup)
 * - ChatGPT API (for OpenAI users)
 * - Local LLM (Ollama, LMStudio)
 * - Hearthlink API (reverse connection mode)
 */

import { log_agent_token_usage } from '../log_handling/agent_token_tracker';

export type LLMBackendType = 
  | 'claude-api' 
  | 'claude-code' 
  | 'chatgpt-api' 
  | 'local-llm' 
  | 'hearthlink-api'
  | 'kimi-k2';

export interface LLMRequest {
  prompt: string;
  systemMessage?: string;
  temperature?: number;
  maxTokens?: number;
  agentId: string;
  module: string;
  context?: Record<string, any>;
  tools?: any[];
  toolChoice?: 'auto' | 'none' | { type: 'function'; function: { name: string } };
  stream?: boolean;
  preferredBackend?: LLMBackendType;
}

export interface LLMResponse {
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
  backend: LLMBackendType;
  toolCalls?: any[];
  metadata?: Record<string, any>;
}

export interface BackendConfig {
  claude_api?: {
    apiKey: string;
    baseUrl?: string;
    model?: string;
  };
  claude_code?: {
    cliPath?: string;
    workingDir?: string;
  };
  chatgpt_api?: {
    apiKey: string;
    baseUrl?: string;
    model?: string;
    organization?: string;
  };
  local_llm?: {
    type: 'ollama' | 'lmstudio' | 'custom';
    baseUrl: string;
    model: string;
  };
  hearthlink_api?: {
    endpoint: string;
    apiKey: string;
    reverseConnection: boolean;
  };
  kimi_k2?: {
    apiKey: string;
    baseUrl?: string;
    model?: string;
    maxTokens?: number;
    temperature?: number;
    timeout?: number;
    retryAttempts?: number;
    enableCaching?: boolean;
    enableMetrics?: boolean;
  };
}

export class LLMBackendManager {
  private backends: Map<LLMBackendType, any> = new Map();
  private activeBackend: LLMBackendType;
  private config: BackendConfig;

  constructor(config: BackendConfig, defaultBackend: LLMBackendType = 'claude-code') {
    this.config = config;
    this.activeBackend = defaultBackend;
    this.initializeBackends();
  }

  /**
   * Initialize all configured backends
   */
  private async initializeBackends(): Promise<void> {
    // Claude API Backend
    if (this.config.claude_api?.apiKey) {
      const { ClaudeConnector } = await import('./ClaudeConnector');
      this.backends.set('claude-api', new ClaudeConnector({
        baseUrl: this.config.claude_api.baseUrl || 'https://api.anthropic.com',
        apiKey: this.config.claude_api.apiKey,
        model: this.config.claude_api.model || 'claude-3-sonnet-20240229',
        maxTokens: 4096,
        temperature: 0.7,
        timeout: 30000,
        maxRetries: 3,
        retryDelay: 1000,
        vaultEnabled: true,
        synapseEndpoint: 'http://localhost:8080'
      }));
    }

    // Claude Code CLI Backend
    this.backends.set('claude-code', new ClaudeCodeBackend(this.config.claude_code || {}));

    // ChatGPT API Backend  
    if (this.config.chatgpt_api?.apiKey) {
      this.backends.set('chatgpt-api', new ChatGPTBackend(this.config.chatgpt_api));
    }

    // Local LLM Backend
    if (this.config.local_llm?.baseUrl) {
      this.backends.set('local-llm', new LocalLLMBackend(this.config.local_llm));
    }

    // Hearthlink API Backend
    if (this.config.hearthlink_api?.endpoint) {
      this.backends.set('hearthlink-api', new HearthlinkAPIBackend(this.config.hearthlink_api));
    }

    // Kimi K2 Backend
    if (this.config.kimi_k2?.apiKey) {
      const { KimiK2Backend } = await import('./KimiK2Backend');
      this.backends.set('kimi-k2', new KimiK2Backend({
        ...this.config.kimi_k2,
        endpoint: (this.config.kimi_k2 as any).baseUrl || (this.config.kimi_k2 as any).endpoint || 'https://api.kimi.moonshot.cn'
      }));
    }
  }

  /**
   * Generate response using active backend
   */
  async generate(request: LLMRequest): Promise<LLMResponse> {
    // Use preferred backend if specified and available
    const targetBackend = request.preferredBackend || this.activeBackend;
    let backend = this.backends.get(targetBackend);
    
    if (!backend) {
      // Fall back to active backend if preferred is not available
      backend = this.backends.get(this.activeBackend);
      if (!backend) {
        throw new Error(`Backend ${this.activeBackend} not available`);
      }
    }

    const startTime = Date.now();
    
    try {
      const response = await backend.generate ? backend.generate(request) : backend.process(request);
      
      // Add backend info to response
      response.backend = targetBackend;
      response.responseTime = Date.now() - startTime;
      response.timestamp = new Date().toISOString();
      
      // Track token usage
      await this.trackTokenUsage(request, response);
      
      return response;
      
    } catch (error) {
      // Try fallback to Kimi K2 if primary backend fails and it's available
      if (targetBackend !== 'kimi-k2' && this.backends.has('kimi-k2')) {
        try {
          const fallbackBackend = this.backends.get('kimi-k2');
          const fallbackResponse = await fallbackBackend.process(request);
          
          fallbackResponse.backend = 'kimi-k2';
          fallbackResponse.responseTime = Date.now() - startTime;
          fallbackResponse.timestamp = new Date().toISOString();
          fallbackResponse.metadata = { 
            ...fallbackResponse.metadata, 
            fallbackUsed: true, 
            originalBackend: targetBackend 
          };
          
          await this.trackTokenUsage(request, fallbackResponse);
          return fallbackResponse;
          
        } catch (fallbackError) {
          console.warn('Fallback to Kimi K2 also failed:', fallbackError);
        }
      }
      
      // Track failed request
      await this.trackTokenUsage(request, null, error.message);
      throw error;
    }
  }

  /**
   * Switch active backend
   */
  switchBackend(backend: LLMBackendType): void {
    if (!this.backends.has(backend)) {
      throw new Error(`Backend ${backend} not configured or available`);
    }
    this.activeBackend = backend;
  }

  /**
   * Get available backends
   */
  getAvailableBackends(): LLMBackendType[] {
    return Array.from(this.backends.keys());
  }

  /**
   * Get current backend status
   */
  async getBackendStatus(): Promise<Record<LLMBackendType, { available: boolean; healthy: boolean; details?: any }>> {
    const status: any = {};
    
    for (const [type, backend] of this.backends) {
      try {
        const health = await backend.healthCheck?.() || { status: 'unknown' };
        status[type] = {
          available: true,
          healthy: health.status === 'healthy',
          details: health
        };
      } catch (error) {
        status[type] = {
          available: true,
          healthy: false,
          details: { error: error.message }
        };
      }
    }

    return status;
  }

  /**
   * Track token usage
   */
  private async trackTokenUsage(request: LLMRequest, response: LLMResponse | null, error?: string): Promise<void> {
    try {
      const totalTokens = response?.usage.totalTokens || 0;
      
      await log_agent_token_usage(
        this.activeBackend,
        this.activeBackend,
        totalTokens,
        `${this.activeBackend}: ${request.prompt.substring(0, 100)}...`,
        request.module,
        {
          operation_type: 'inference',
          request_id: response?.requestId || `${Date.now()}`,
          prompt_tokens: response?.usage.promptTokens || 0,
          completion_tokens: response?.usage.completionTokens || 0,
          total_tokens: totalTokens,
          model_name: response?.model || 'unknown',
          backend: this.activeBackend,
          success: !error,
          error_message: error
        }
      );
    } catch (trackingError) {
      console.warn('Token tracking failed:', trackingError);
    }
  }
}

/**
 * Claude Code CLI Backend
 */
class ClaudeCodeBackend {
  private config: any;

  constructor(config: any) {
    this.config = config;
  }

  async generate(request: LLMRequest): Promise<Partial<LLMResponse>> {
    // For Claude Code users, this could:
    // 1. Write prompt to temp file
    // 2. Execute `claude` CLI command
    // 3. Parse response
    // 4. Return formatted result

    console.log('🔮 Claude Code Backend: Request received');
    console.log(`📝 Prompt: ${request.prompt.substring(0, 100)}...`);
    
    // Simulated response for now - in real implementation this would
    // execute CLI commands or provide alternative integration
    return {
      content: `Claude Code Backend Response:\n\nReceived prompt: "${request.prompt}"\n\nThis would be processed through Claude Code CLI integration.`,
      model: 'claude-code-cli',
      usage: {
        promptTokens: Math.floor(request.prompt.length / 4),
        completionTokens: 50,
        totalTokens: Math.floor(request.prompt.length / 4) + 50
      },
      requestId: `claude-code-${Date.now()}`,
      finishReason: 'stop'
    };
  }

  async healthCheck() {
    return { status: 'healthy', details: 'Claude Code CLI integration' };
  }
}

/**
 * ChatGPT API Backend
 */
class ChatGPTBackend {
  private config: any;

  constructor(config: any) {
    this.config = config;
  }

  async generate(request: LLMRequest): Promise<Partial<LLMResponse>> {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.config.model || 'gpt-4',
        messages: [
          ...(request.systemMessage ? [{ role: 'system', content: request.systemMessage }] : []),
          { role: 'user', content: request.prompt }
        ],
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 4096
      })
    });

    if (!response.ok) {
      throw new Error(`ChatGPT API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      content: data.choices[0].message.content,
      model: data.model,
      usage: {
        promptTokens: data.usage.prompt_tokens,
        completionTokens: data.usage.completion_tokens,
        totalTokens: data.usage.total_tokens
      },
      requestId: `chatgpt-${Date.now()}`,
      finishReason: data.choices[0].finish_reason
    };
  }

  async healthCheck() {
    try {
      const response = await fetch('https://api.openai.com/v1/models', {
        headers: { 'Authorization': `Bearer ${this.config.apiKey}` }
      });
      return { status: response.ok ? 'healthy' : 'unhealthy' };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }
}

/**
 * Local LLM Backend (Ollama/LMStudio)
 */
class LocalLLMBackend {
  private config: any;

  constructor(config: any) {
    this.config = config;
  }

  async generate(request: LLMRequest): Promise<Partial<LLMResponse>> {
    const endpoint = this.config.type === 'ollama' ? '/api/generate' : '/v1/chat/completions';
    const url = `${this.config.baseUrl}${endpoint}`;

    let payload: any;
    
    if (this.config.type === 'ollama') {
      payload = {
        model: this.config.model,
        prompt: request.prompt,
        system: request.systemMessage,
        options: {
          temperature: request.temperature || 0.7,
          num_predict: request.maxTokens || 4096
        }
      };
    } else {
      // LMStudio/OpenAI compatible
      payload = {
        model: this.config.model,
        messages: [
          ...(request.systemMessage ? [{ role: 'system', content: request.systemMessage }] : []),
          { role: 'user', content: request.prompt }
        ],
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 4096
      };
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Local LLM error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    if (this.config.type === 'ollama') {
      return {
        content: data.response,
        model: this.config.model,
        usage: {
          promptTokens: data.prompt_eval_count || 0,
          completionTokens: data.eval_count || 0,
          totalTokens: (data.prompt_eval_count || 0) + (data.eval_count || 0)
        },
        requestId: `local-${Date.now()}`,
        finishReason: data.done ? 'stop' : 'length'
      };
    } else {
      return {
        content: data.choices[0].message.content,
        model: data.model,
        usage: {
          promptTokens: data.usage?.prompt_tokens || 0,
          completionTokens: data.usage?.completion_tokens || 0,
          totalTokens: data.usage?.total_tokens || 0
        },
        requestId: `local-${Date.now()}`,
        finishReason: data.choices[0].finish_reason
      };
    }
  }

  async healthCheck() {
    try {
      const healthUrl = this.config.type === 'ollama' ? 
        `${this.config.baseUrl}/api/tags` : 
        `${this.config.baseUrl}/v1/models`;
      
      const response = await fetch(healthUrl);
      return { status: response.ok ? 'healthy' : 'unhealthy' };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }
}

/**
 * Hearthlink API Backend (Reverse Connection)
 */
class HearthlinkAPIBackend {
  private config: any;

  constructor(config: any) {
    this.config = config;
  }

  async generate(request: LLMRequest): Promise<Partial<LLMResponse>> {
    const response = await fetch(`${this.config.endpoint}/api/generate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: request.prompt,
        system_message: request.systemMessage,
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 4096,
        agent_id: request.agentId,
        module: request.module,
        reverse_connection: this.config.reverseConnection
      })
    });

    if (!response.ok) {
      throw new Error(`Hearthlink API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    return {
      content: data.content,
      model: data.model || 'hearthlink-api',
      usage: data.usage || {
        promptTokens: 0,
        completionTokens: 0,
        totalTokens: 0
      },
      requestId: data.request_id || `hearthlink-${Date.now()}`,
      finishReason: data.finish_reason || 'stop'
    };
  }

  async healthCheck() {
    try {
      const response = await fetch(`${this.config.endpoint}/api/health`);
      return { status: response.ok ? 'healthy' : 'unhealthy' };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }
}

export default LLMBackendManager;