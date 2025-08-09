// src/llm/GeminiConnector.ts
// Google Gemini API Connector with model selection capability

export interface GeminiRequest {
  prompt: string
  systemMessage?: string
  agentId: string
  module: string
  context?: Record<string, any>
  temperature?: number
  maxTokens?: number
  model?: 'flash' | 'pro' | 'flash-8b' | 'pro-latest'
}

export interface GeminiConfig {
  apiKey: string
  model?: 'flash' | 'pro' | 'flash-8b' | 'pro-latest'
  timeoutMs?: number
}

export interface GeminiResponse {
  text: string
  tokensUsed: number
  model: string
  usage?: {
    totalTokens: number
    promptTokens: number
    completionTokens: number
  }
}

export class GeminiConnector {
  private config: GeminiConfig
  private baseUrl: string = 'https://generativelanguage.googleapis.com'
  private modelMap = {
    'flash': 'gemini-1.5-flash',
    'pro': 'gemini-1.5-pro',
    'flash-8b': 'gemini-1.5-flash-8b', 
    'pro-latest': 'gemini-1.5-pro-latest'
  }

  constructor(config: GeminiConfig) {
    this.config = config
    if (!config.apiKey) {
      throw new Error('Gemini API key is required')
    }
  }

  async call(request: GeminiRequest): Promise<GeminiResponse> {
    try {
      // Model selection with fallback to config default, then flash
      const modelKey = request.model || this.config.model || 'flash'
      const modelName = this.modelMap[modelKey]
      
      if (!modelName) {
        throw new Error(`Invalid Gemini model: ${modelKey}. Available: flash, pro, flash-8b, pro-latest`)
      }

      const requestBody = {
        contents: [
          {
            parts: [
              ...(request.systemMessage ? [{ text: `System: ${request.systemMessage}\n\n` }] : []),
              { text: request.prompt }
            ]
          }
        ],
        generationConfig: {
          temperature: request.temperature || 0.7,
          maxOutputTokens: request.maxTokens || 2048,
          topP: 0.9,
          topK: 40
        }
      }

      const url = `${this.baseUrl}/v1beta/models/${modelName}:generateContent?key=${this.config.apiKey}`

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'Hearthlink/1.3.0'
        },
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(this.config.timeoutMs || 30000)
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Gemini API error: ${response.status} ${response.statusText} - ${errorText}`)
      }

      const data = await response.json()
      
      if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
        throw new Error('Invalid Gemini API response structure')
      }

      const candidate = data.candidates[0]
      const responseText = candidate.content.parts.map(part => part.text).join('')
      
      // Extract usage information if available
      const usage = data.usageMetadata || {}

      return {
        text: responseText,
        tokensUsed: usage.totalTokenCount || 0,
        model: modelName,
        usage: {
          totalTokens: usage.totalTokenCount || 0,
          promptTokens: usage.promptTokenCount || 0,
          completionTokens: usage.candidatesTokenCount || 0
        }
      }
    } catch (error) {
      console.error('GeminiConnector error:', error)
      throw new Error(`Gemini API call failed: ${error.message}`)
    }
  }

  async ping(): Promise<boolean> {
    try {
      const response = await this.call({
        prompt: 'Say "pong" to confirm connectivity',
        agentId: 'health',
        module: 'health',
        maxTokens: 10
      })
      return response.text.toLowerCase().includes('pong')
    } catch {
      return false
    }
  }

  /**
   * Test all available models to check which ones are accessible
   */
  async testAllModels(): Promise<Record<string, boolean>> {
    const results: Record<string, boolean> = {}
    
    for (const [key, modelName] of Object.entries(this.modelMap)) {
      try {
        const response = await this.call({
          prompt: 'Test',
          agentId: 'test',
          module: 'test',
          model: key as any,
          maxTokens: 5
        })
        results[key] = response.text.length > 0
      } catch (error) {
        console.warn(`Model ${key} (${modelName}) test failed:`, error.message)
        results[key] = false
      }
    }
    
    return results
  }

  /**
   * Get recommended model based on use case
   */
  getRecommendedModel(useCase: 'speed' | 'quality' | 'balanced'): string {
    switch (useCase) {
      case 'speed':
        return 'flash' // Fastest, most cost-effective
      case 'quality':
        return 'pro' // Best reasoning and complex tasks
      case 'balanced':
      default:
        return 'flash' // Good balance for most applications
    }
  }

  /**
   * Switch the default model for this connector instance
   */
  setDefaultModel(model: 'flash' | 'pro' | 'flash-8b' | 'pro-latest'): void {
    if (!this.modelMap[model]) {
      throw new Error(`Invalid model: ${model}`)
    }
    this.config.model = model
  }
}