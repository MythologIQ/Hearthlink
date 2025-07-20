/**
 * React Hook for Claude Connector Integration
 * 
 * Provides easy access to Claude API through Synapse routing with:
 * - Request state management
 * - Error handling and retry logic
 * - Token usage tracking
 * - Queue status monitoring
 */

import { useState, useCallback, useEffect } from 'react';
import { getClaudeConnector, ClaudeConnector } from '../llm/ClaudeConnector';
import LLMBackendManager, { LLMBackendType, BackendConfig } from '../llm/LLMBackendManager';

interface ClaudeRequest {
  prompt: string;
  systemMessage?: string;
  temperature?: number;
  maxTokens?: number;
  agentId: string;
  module: string;
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

interface ClaudeState {
  isLoading: boolean;
  response: ClaudeResponse | null;
  error: ClaudeError | null;
  requestId: string | null;
}

interface ClaudeConnectorHook {
  // State
  state: ClaudeState;
  
  // Actions
  generate: (request: ClaudeRequest) => Promise<ClaudeResponse>;
  reset: () => void;
  
  // Status
  queueStatus: { active: number; requests: string[] };
  healthStatus: { status: 'healthy' | 'degraded' | 'unhealthy'; details: Record<string, any> } | null;
  
  // Utilities
  isHealthy: boolean;
  canRetry: boolean;
}

export function useClaudeConnector(): ClaudeConnectorHook {
  const [connector] = useState<ClaudeConnector>(() => getClaudeConnector());
  const [state, setState] = useState<ClaudeState>({
    isLoading: false,
    response: null,
    error: null,
    requestId: null
  });
  const [queueStatus, setQueueStatus] = useState({ active: 0, requests: [] });
  const [healthStatus, setHealthStatus] = useState<{ status: 'healthy' | 'degraded' | 'unhealthy'; details: Record<string, any> } | null>(null);

  // Update queue status periodically
  useEffect(() => {
    const updateQueueStatus = () => {
      setQueueStatus(connector.getQueueStatus());
    };

    updateQueueStatus(); // Initial update
    const interval = setInterval(updateQueueStatus, 1000); // Update every second

    return () => clearInterval(interval);
  }, [connector]);

  // Health check on mount and periodically
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await connector.healthCheck();
        setHealthStatus(health);
      } catch (error) {
        setHealthStatus({
          status: 'unhealthy',
          details: { error: error.message, timestamp: new Date().toISOString() }
        });
      }
    };

    checkHealth(); // Initial check
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, [connector]);

  const generate = useCallback(async (request: ClaudeRequest): Promise<ClaudeResponse> => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
      response: null
    }));

    try {
      const response = await connector.generate(request);
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        response,
        requestId: response.requestId
      }));

      return response;
    } catch (error) {
      const claudeError = error as ClaudeError;
      
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: claudeError,
        requestId: claudeError.requestId || null
      }));

      throw error;
    }
  }, [connector]);

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      response: null,
      error: null,
      requestId: null
    });
  }, []);

  const isHealthy = healthStatus?.status === 'healthy';
  const canRetry = state.error?.type === 'timeout' || state.error?.type === 'connection_error';

  return {
    state,
    generate,
    reset,
    queueStatus,
    healthStatus,
    isHealthy,
    canRetry
  };
}

// Specialized hooks for common use cases

/**
 * Hook for simple Claude chat interactions
 */
export function useClaudeChat(agentId: string, module: string) {
  const claude = useClaudeConnector();
  
  const chat = useCallback(async (prompt: string, systemMessage?: string) => {
    return claude.generate({
      prompt,
      systemMessage,
      agentId,
      module,
      context: { type: 'chat' }
    });
  }, [claude, agentId, module]);
  
  return {
    ...claude,
    chat
  };
}

/**
 * Hook for code generation tasks
 */
export function useClaudeCodeGen(agentId: string, module: string) {
  const claude = useClaudeConnector();
  
  const generateCode = useCallback(async (
    prompt: string, 
    language: string = 'typescript',
    context?: string
  ) => {
    const systemMessage = `You are a code generation assistant. Generate clean, well-documented ${language} code. ${context ? `Context: ${context}` : ''}`;
    
    return claude.generate({
      prompt,
      systemMessage,
      agentId,
      module,
      temperature: 0.3, // Lower temperature for more deterministic code
      context: { type: 'code_generation', language }
    });
  }, [claude, agentId, module]);
  
  return {
    ...claude,
    generateCode
  };
}

/**
 * Hook for analysis and reasoning tasks
 */
export function useClaudeAnalysis(agentId: string, module: string) {
  const claude = useClaudeConnector();
  
  const analyze = useCallback(async (
    data: string,
    analysisType: string = 'general',
    instructions?: string
  ) => {
    const systemMessage = `You are an analysis assistant specializing in ${analysisType} analysis. Provide clear, structured insights. ${instructions ? `Instructions: ${instructions}` : ''}`;
    
    return claude.generate({
      prompt: data,
      systemMessage,
      agentId,
      module,
      temperature: 0.5, // Balanced temperature for analysis
      context: { type: 'analysis', analysisType }
    });
  }, [claude, agentId, module]);
  
  return {
    ...claude,
    analyze
  };
}

/**
 * Hook for document processing tasks
 */
export function useClaudeDocumentProcessor(agentId: string, module: string) {
  const claude = useClaudeConnector();
  
  const processDocument = useCallback(async (
    document: string,
    task: 'summarize' | 'extract' | 'translate' | 'rewrite',
    options?: Record<string, any>
  ) => {
    let systemMessage = '';
    let prompt = '';
    
    switch (task) {
      case 'summarize':
        systemMessage = 'You are a document summarization assistant. Create concise, accurate summaries that capture key points.';
        prompt = `Please summarize the following document:\n\n${document}`;
        break;
      case 'extract':
        systemMessage = 'You are a data extraction assistant. Extract specific information as requested.';
        prompt = `Extract ${options?.extractType || 'key information'} from:\n\n${document}`;
        break;
      case 'translate':
        systemMessage = `You are a translation assistant. Translate accurately to ${options?.targetLanguage || 'English'}.`;
        prompt = `Translate the following to ${options?.targetLanguage || 'English'}:\n\n${document}`;
        break;
      case 'rewrite':
        systemMessage = `You are a writing assistant. Rewrite content in ${options?.style || 'a clear and professional'} style.`;
        prompt = `Rewrite the following in ${options?.style || 'a clear and professional'} style:\n\n${document}`;
        break;
    }
    
    return claude.generate({
      prompt,
      systemMessage,
      agentId,
      module,
      temperature: 0.4,
      context: { type: 'document_processing', task, options }
    });
  }, [claude, agentId, module]);
  
  return {
    ...claude,
    processDocument
  };
}

export default useClaudeConnector;