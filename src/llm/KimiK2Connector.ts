// src/llm/KimiK2Connector.ts
export {}

export interface KimiK2Request {
  prompt: string
  systemMessage?: string
  agentId: string
  module: string
  context?: Record<string, any>
  tools?: any[]
  toolChoice?: 'auto' | 'none'
  temperature?: number
  maxTokens?: number
}

export interface KimiK2Config {
  apiKey: string
  endpoint: string
  timeoutMs?: number
}

export interface KimiK2Response {
  text: string
  tokensUsed: number
  usage?: {
    totalTokens: number
    promptTokens: number
    completionTokens: number
    total_tokens: number
    prompt_tokens: number
  }
}

export class KimiK2Connector {
  private config: KimiK2Config
  private baseHeaders: Record<string, string>

  constructor(config: KimiK2Config) {
    this.config = config
    this.baseHeaders = {
      'Authorization': `Bearer ${config.apiKey}`,
      'Content-Type': 'application/json',
      'User-Agent': 'Hearthlink/1.3.0'
    }
  }

  async call(request: KimiK2Request): Promise<KimiK2Response> {
    try {
      const requestBody = {
        model: 'moonshot-v1-8k', // Default Kimi model
        messages: [
          ...(request.systemMessage ? [{ role: 'system', content: request.systemMessage }] : []),
          { role: 'user', content: request.prompt }
        ],
        temperature: request.temperature || 0.7,
        max_tokens: request.maxTokens || 2048,
        stream: false
      }

      const response = await fetch(this.config.endpoint + '/v1/chat/completions', {
        method: 'POST',
        headers: this.baseHeaders,
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(this.config.timeoutMs || 30000)
      })

      if (!response.ok) {
        throw new Error(`Kimi API error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      
      const usage = data.usage || {}
      const responseText = data.choices?.[0]?.message?.content || 'No response'

      return {
        text: responseText,
        tokensUsed: usage.total_tokens || 0,
        usage: {
          totalTokens: usage.total_tokens || 0,
          promptTokens: usage.prompt_tokens || 0,
          completionTokens: usage.completion_tokens || 0,
          total_tokens: usage.total_tokens || 0,
          prompt_tokens: usage.prompt_tokens || 0
        }
      }
    } catch (error) {
      console.error('KimiK2Connector error:', error)
      throw new Error(`KimiK2 API call failed: ${error.message}`)
    }
  }

  async ping(): Promise<boolean> {
    try {
      const response = await this.call({
        prompt: 'ping',
        agentId: 'health',
        module: 'health'
      })
      return response.text.length > 0
    } catch {
      return false
    }
  }
}