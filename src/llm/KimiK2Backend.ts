import { KimiK2Connector, KimiK2Config, KimiK2Request, KimiK2Response } from './KimiK2Connector';
import { LLMBackend, LLMRequest, LLMResponse } from './LLMBackend';
import { ConfigManager } from '../config/ConfigManager';
import { MetricsCollector } from '../monitoring/MetricsCollector';

export class KimiK2Backend implements LLMBackend {
  private connector: KimiK2Connector;
  private config: KimiK2Config;
  private metrics: MetricsCollector;
  private isInitialized: boolean = false;

  constructor() {
    this.metrics = new MetricsCollector('kimi-k2');
    this.initialize();
  }

  private async initialize(): Promise<void> {
    try {
      // Load configuration
      const configManager = new ConfigManager();
      const llmConfig = await configManager.loadConfig('llm_backends');
      const kimiConfig = llmConfig.backends.kimi_k2;

      if (!kimiConfig.enabled) {
        throw new Error('Kimi K2 backend is disabled in configuration');
      }

      // Build configuration
      this.config = {
        apiKey: process.env.KIMI_K2_API_KEY || '',
        baseUrl: process.env.KIMI_K2_BASE_URL || 'https://openrouter.ai/api/v1',
        model: process.env.KIMI_K2_MODEL || 'moonshotai/kimi-k2',
        maxTokens: kimiConfig.max_tokens || 8192,
        temperature: kimiConfig.temperature || 0.7,
        timeout: kimiConfig.timeout || 30000,
        retryAttempts: kimiConfig.retry_attempts || 3,
        enableCaching: kimiConfig.enable_caching !== false,
        enableMetrics: kimiConfig.enable_metrics !== false
      };

      // Validate configuration
      if (!this.config.apiKey) {
        throw new Error('KIMI_K2_API_KEY environment variable is required');
      }

      // Initialize connector
      this.connector = new KimiK2Connector(this.config);

      // Test connection
      const healthCheck = await this.connector.healthCheck();
      if (healthCheck.status !== 'healthy') {
        throw new Error(`Kimi K2 health check failed: ${healthCheck.details?.error}`);
      }

      this.isInitialized = true;
      console.log('Kimi K2 backend initialized successfully');

    } catch (error) {
      console.error('Failed to initialize Kimi K2 backend:', error);
      throw error;
    }
  }

  async process(request: LLMRequest): Promise<LLMResponse> {
    if (!this.isInitialized) {
      throw new Error('Kimi K2 backend not initialized');
    }

    const startTime = Date.now();
    this.metrics.increment('requests_total');

    try {
      // Convert generic LLM request to Kimi K2 request
      const kimiRequest = this.convertRequest(request);

      // Make the API call
      const kimiResponse = await this.connector.chat(kimiRequest);

      // Convert response back to generic format
      const genericResponse = this.convertResponse(kimiResponse);

      // Track metrics
      this.metrics.histogram('request_duration', Date.now() - startTime);
      this.metrics.increment('requests_success');
      this.metrics.histogram('tokens_prompt', genericResponse.usage.promptTokens);
      this.metrics.histogram('tokens_completion', genericResponse.usage.completionTokens);

      return genericResponse;

    } catch (error) {
      this.metrics.increment('requests_failed');
      this.metrics.increment('errors_total', { error_type: error.constructor.name });
      
      console.error('Kimi K2 backend request failed:', error);
      throw error;
    }
  }

  private convertRequest(request: LLMRequest): KimiK2Request {
    return {
      prompt: request.prompt,
      systemMessage: request.systemMessage,
      temperature: request.temperature,
      maxTokens: request.maxTokens,
      agentId: request.agentId,
      module: request.module,
      context: request.context,
      tools: request.tools,
      toolChoice: request.toolChoice,
      stream: request.stream,
      preferredBackend: 'kimi-k2'
    };
  }

  private convertResponse(response: KimiK2Response): LLMResponse {
    return {
      content: response.content,
      model: response.model,
      usage: response.usage,
      responseTime: response.responseTime,
      timestamp: response.timestamp,
      requestId: response.requestId,
      finishReason: response.finishReason,
      backend: 'kimi-k2',
      toolCalls: response.toolCalls,
      metadata: response.metadata
    };
  }

  async isAvailable(): Promise<boolean> {
    if (!this.isInitialized) {
      return false;
    }

    try {
      const healthCheck = await this.connector.healthCheck();
      return healthCheck.status === 'healthy';
    } catch (error) {
      return false;
    }
  }

  async getCapabilities(): Promise<string[]> {
    return [
      'text_generation',
      'code_generation',
      'reasoning',
      'tool_calling',
      'agentic_workflows',
      'long_context',
      'multi_step_tasks'
    ];
  }

  async getModelInfo(): Promise<any> {
    return {
      name: 'Kimi K2',
      provider: 'Moonshot AI',
      version: '1.0',
      contextWindow: 128000,
      maxOutputTokens: 8192,
      supportedFeatures: [
        'tool_calling',
        'streaming',
        'long_context',
        'code_generation',
        'reasoning',
        'agentic_workflows'
      ],
      pricing: {
        input: 0.00057, // per 1K tokens
        output: 0.0023  // per 1K tokens
      }
    };
  }

  async getUsageStats(): Promise<any> {
    return {
      totalRequests: this.metrics.getCounter('requests_total'),
      successfulRequests: this.metrics.getCounter('requests_success'),
      failedRequests: this.metrics.getCounter('requests_failed'),
      averageResponseTime: this.metrics.getHistogramAverage('request_duration'),
      totalTokensPrompt: this.metrics.getHistogramSum('tokens_prompt'),
      totalTokensCompletion: this.metrics.getHistogramSum('tokens_completion')
    };
  }

  async estimateCost(request: LLMRequest): Promise<number> {
    const modelInfo = await this.getModelInfo();
    const estimatedPromptTokens = Math.ceil(request.prompt.length / 4);
    const estimatedCompletionTokens = request.maxTokens || 1000;

    const inputCost = (estimatedPromptTokens / 1000) * modelInfo.pricing.input;
    const outputCost = (estimatedCompletionTokens / 1000) * modelInfo.pricing.output;

    return inputCost + outputCost;
  }

  async warmUp(): Promise<void> {
    if (!this.isInitialized) {
      await this.initialize();
    }

    // Make a test request to warm up the connection
    const testRequest: LLMRequest = {
      prompt: 'Warm up request',
      agentId: 'warm-up',
      module: 'system',
      maxTokens: 10,
      temperature: 0.1
    };

    try {
      await this.process(testRequest);
      console.log('Kimi K2 backend warmed up successfully');
    } catch (error) {
      console.warn('Kimi K2 backend warm up failed:', error);
    }
  }

  async shutdown(): Promise<void> {
    if (this.connector) {
      this.connector.cleanup();
    }
    this.isInitialized = false;
    console.log('Kimi K2 backend shut down');
  }

  // Advanced features specific to Kimi K2
  async executeAgenticWorkflow(workflow: any): Promise<any> {
    if (!this.isInitialized) {
      throw new Error('Kimi K2 backend not initialized');
    }

    const request: KimiK2Request = {
      prompt: workflow.prompt,
      systemMessage: workflow.systemMessage || 'You are an advanced AI agent capable of autonomous task execution.',
      agentId: workflow.agentId,
      module: workflow.module,
      tools: workflow.tools,
      toolChoice: 'auto',
      maxTokens: workflow.maxTokens || 4096,
      temperature: workflow.temperature || 0.7
    };

    const response = await this.connector.chat(request);
    return response;
  }

  async processWithLongContext(request: LLMRequest & { documents?: string[] }): Promise<LLMResponse> {
    if (!this.isInitialized) {
      throw new Error('Kimi K2 backend not initialized');
    }

    // Combine documents with the prompt for long context processing
    let extendedPrompt = request.prompt;
    if (request.documents && request.documents.length > 0) {
      extendedPrompt = `Context Documents:\n${request.documents.join('\n\n')}\n\nQuery: ${request.prompt}`;
    }

    const kimiRequest: KimiK2Request = {
      ...this.convertRequest(request),
      prompt: extendedPrompt,
      maxTokens: Math.min(request.maxTokens || 8192, 8192), // Respect model limits
      systemMessage: request.systemMessage || 'You have access to extensive context. Use it to provide comprehensive and accurate responses.'
    };

    const kimiResponse = await this.connector.chat(kimiRequest);
    return this.convertResponse(kimiResponse);
  }
}