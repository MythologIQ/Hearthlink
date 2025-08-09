import { LLMRequest, LLMResponse } from './LLMBackendManager';

export { LLMRequest, LLMResponse };

export interface LLMBackend {
  /**
   * Process an LLM request and return a response
   */
  process(request: LLMRequest): Promise<LLMResponse>;

  /**
   * Check if the backend is available
   */
  isAvailable(): Promise<boolean>;

  /**
   * Get the capabilities of this backend
   */
  getCapabilities(): Promise<string[]>;

  /**
   * Get information about the model
   */
  getModelInfo(): Promise<any>;

  /**
   * Get usage statistics
   */
  getUsageStats(): Promise<any>;

  /**
   * Estimate the cost of a request
   */
  estimateCost(request: LLMRequest): Promise<number>;

  /**
   * Warm up the backend (optional)
   */
  warmUp?(): Promise<void>;

  /**
   * Shut down the backend (optional)
   */
  shutdown?(): Promise<void>;

  /**
   * Health check
   */
  healthCheck?(): Promise<{ status: 'healthy' | 'unhealthy'; details?: any }>;
}