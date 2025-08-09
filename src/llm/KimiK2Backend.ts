// src/llm/KimiK2Backend.ts
import { KimiK2Connector, KimiK2Config, KimiK2Request, KimiK2Response } from './KimiK2Connector'
import { LLMBackend, LLMRequest, LLMResponse } from './LLMBackend'

export class KimiK2Backend implements LLMBackend {
  private connector: KimiK2Connector
  private config: KimiK2Config
  private isInitialized = false

  constructor(config: KimiK2Config) {
    this.config = config
    this.connector = new KimiK2Connector(config)
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) return
    
    // Test connectivity
    const isHealthy = await this.connector.ping()
    if (!isHealthy) {
      console.warn('KimiK2Backend: Initial health check failed, but continuing...')
    }
    
    this.isInitialized = true
  }

  async process(request: LLMRequest): Promise<LLMResponse> {
    await this.initialize()
    
    const startTime = Date.now()
    
    const kimiRequest: KimiK2Request = {
      prompt: request.prompt,
      systemMessage: request.systemMessage,
      agentId: request.agentId,
      module: request.module,
      temperature: request.temperature,
      maxTokens: request.maxTokens
    }

    const response = await this.connector.call(kimiRequest)
    const responseTime = Date.now() - startTime
    
    return {
      content: response.text,
      model: 'moonshot-v1-8k',
      usage: {
        promptTokens: response.usage?.promptTokens || 0,
        completionTokens: response.usage?.completionTokens || 0,
        totalTokens: response.usage?.totalTokens || response.tokensUsed
      },
      responseTime,
      timestamp: new Date().toISOString(),
      requestId: Math.random().toString(36).substring(2),
      finishReason: 'stop',
      backend: 'kimi-k2' as const
    }
  }

  async isAvailable(): Promise<boolean> {
    try {
      return await this.connector.ping()
    } catch {
      return false
    }
  }

  async getCapabilities(): Promise<string[]> {
    return [
      'text-generation',
      'conversation',
      'chinese-language',
      'english-language',
      'reasoning',
      'analysis'
    ]
  }

  async getModelInfo(): Promise<any> {
    return {
      name: 'Kimi K2 (Moonshot)',
      provider: 'Moonshot AI',
      model: 'moonshot-v1-8k',
      contextLength: 8192,
      supportedLanguages: ['zh', 'en'],
      capabilities: await this.getCapabilities()
    }
  }

  async getUsageStats(): Promise<any> {
    return {
      provider: 'kimi-k2',
      endpoint: this.config.endpoint,
      status: await this.isAvailable() ? 'online' : 'offline',
      lastHealthCheck: new Date().toISOString()
    }
  }

  async estimateCost(request: LLMRequest): Promise<number> {
    // Moonshot pricing (estimated)
    const inputTokens = this.estimateTokens(request.prompt || '')
    const outputTokens = request.maxTokens || 1024
    
    // Moonshot pricing: ~$0.012 per 1K tokens
    const costPer1K = 0.012
    const totalTokens = inputTokens + outputTokens
    return (totalTokens / 1000) * costPer1K
  }

  private estimateTokens(text: string): number {
    // Rough estimation: ~4 characters per token for mixed language content
    return Math.ceil(text.length / 4)
  }

  async health(): Promise<{ status: string; details?: any }> {
    try {
      const isHealthy = await this.connector.ping()
      return {
        status: isHealthy ? 'healthy' : 'unhealthy',
        details: {
          endpoint: this.config.endpoint,
          lastCheck: new Date().toISOString(),
          initialized: this.isInitialized
        }
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        details: {
          error: error.message,
          endpoint: this.config.endpoint,
          lastCheck: new Date().toISOString()
        }
      }
    }
  }
}