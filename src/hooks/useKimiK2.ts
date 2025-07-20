import { useState, useCallback, useRef } from 'react';
import { KimiK2Request, KimiK2Response } from '../llm/KimiK2Connector';

export interface UseKimiK2Options {
  baseUrl?: string;
  timeout?: number;
  retryAttempts?: number;
  onError?: (error: Error) => void;
  onSuccess?: (response: KimiK2Response) => void;
}

export interface UseKimiK2Result {
  sendRequest: (request: KimiK2Request) => Promise<KimiK2Response>;
  isLoading: boolean;
  error: string | null;
  response: KimiK2Response | null;
  cancel: () => void;
  reset: () => void;
  stats: {
    totalRequests: number;
    successfulRequests: number;
    failedRequests: number;
    totalTokens: number;
    totalCost: number;
  };
}

export const useKimiK2 = (options: UseKimiK2Options = {}): UseKimiK2Result => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<KimiK2Response | null>(null);
  const [stats, setStats] = useState({
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    totalTokens: 0,
    totalCost: 0
  });

  const abortControllerRef = useRef<AbortController | null>(null);

  const sendRequest = useCallback(async (request: KimiK2Request): Promise<KimiK2Response> => {
    // Cancel any existing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setError(null);
    
    // Update stats
    setStats(prev => ({
      ...prev,
      totalRequests: prev.totalRequests + 1
    }));

    try {
      const response = await fetch(options.baseUrl || '/api/llm/kimi-k2', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.message || response.statusText}`);
      }

      const data: KimiK2Response = await response.json();
      
      // Update stats
      setStats(prev => ({
        ...prev,
        successfulRequests: prev.successfulRequests + 1,
        totalTokens: prev.totalTokens + data.usage.totalTokens,
        totalCost: prev.totalCost + (data.usage.promptTokens * 0.00057 + data.usage.completionTokens * 0.0023) / 1000
      }));

      setResponse(data);
      
      // Call success callback if provided
      if (options.onSuccess) {
        options.onSuccess(data);
      }
      
      return data;

    } catch (err) {
      if (err.name === 'AbortError') {
        // Request was cancelled, don't update error state
        return Promise.reject(err);
      }

      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      
      // Update stats
      setStats(prev => ({
        ...prev,
        failedRequests: prev.failedRequests + 1
      }));

      // Call error callback if provided
      if (options.onError) {
        options.onError(err instanceof Error ? err : new Error(errorMessage));
      }

      throw err;
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [options]);

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsLoading(false);
  }, []);

  const reset = useCallback(() => {
    cancel();
    setError(null);
    setResponse(null);
    setStats({
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      totalTokens: 0,
      totalCost: 0
    });
  }, [cancel]);

  return {
    sendRequest,
    isLoading,
    error,
    response,
    cancel,
    reset,
    stats
  };
};

// Specialized hooks for different use cases
export const useKimiK2Chat = (options: UseKimiK2Options = {}) => {
  const base = useKimiK2(options);
  
  const sendChatMessage = useCallback(async (
    message: string,
    agentId: string,
    systemMessage?: string,
    context?: Record<string, any>
  ): Promise<KimiK2Response> => {
    const request: KimiK2Request = {
      prompt: message,
      systemMessage,
      agentId,
      module: 'chat',
      context,
      temperature: 0.7,
      maxTokens: 4096
    };

    return base.sendRequest(request);
  }, [base]);

  return {
    ...base,
    sendChatMessage
  };
};

export const useKimiK2CodeGen = (options: UseKimiK2Options = {}) => {
  const base = useKimiK2(options);
  
  const generateCode = useCallback(async (
    prompt: string,
    agentId: string,
    language?: string,
    context?: Record<string, any>
  ): Promise<KimiK2Response> => {
    const systemMessage = `You are a skilled software developer. Generate high-quality, well-commented code${language ? ` in ${language}` : ''}. Focus on best practices, error handling, and maintainability.`;
    
    const request: KimiK2Request = {
      prompt,
      systemMessage,
      agentId,
      module: 'code-generation',
      context: { ...context, language },
      temperature: 0.3, // Lower temperature for more consistent code generation
      maxTokens: 8192
    };

    return base.sendRequest(request);
  }, [base]);

  return {
    ...base,
    generateCode
  };
};

export const useKimiK2Agentic = (options: UseKimiK2Options = {}) => {
  const base = useKimiK2(options);
  
  const executeAgenticTask = useCallback(async (
    task: string,
    agentId: string,
    tools?: any[],
    context?: Record<string, any>
  ): Promise<KimiK2Response> => {
    const systemMessage = `You are an advanced AI agent capable of autonomous task execution. Break down complex tasks into steps and execute them systematically. Use available tools when appropriate.`;
    
    const request: KimiK2Request = {
      prompt: task,
      systemMessage,
      agentId,
      module: 'agentic',
      context,
      tools,
      toolChoice: 'auto',
      temperature: 0.6,
      maxTokens: 8192
    };

    return base.sendRequest(request);
  }, [base]);

  return {
    ...base,
    executeAgenticTask
  };
};

export const useKimiK2LongContext = (options: UseKimiK2Options = {}) => {
  const base = useKimiK2(options);
  
  const processLongContext = useCallback(async (
    query: string,
    documents: string[],
    agentId: string,
    context?: Record<string, any>
  ): Promise<KimiK2Response> => {
    const systemMessage = `You have access to extensive context documents. Use them to provide comprehensive and accurate responses. Reference specific information from the documents when relevant.`;
    
    const combinedPrompt = `Context Documents:\n${documents.join('\n\n')}\n\nQuery: ${query}`;
    
    const request: KimiK2Request = {
      prompt: combinedPrompt,
      systemMessage,
      agentId,
      module: 'long-context',
      context: { ...context, documentCount: documents.length },
      temperature: 0.5,
      maxTokens: 8192
    };

    return base.sendRequest(request);
  }, [base]);

  return {
    ...base,
    processLongContext
  };
};

export const useKimiK2Analysis = (options: UseKimiK2Options = {}) => {
  const base = useKimiK2(options);
  
  const analyzeContent = useCallback(async (
    content: string,
    analysisType: 'sentiment' | 'technical' | 'business' | 'creative' | 'general',
    agentId: string,
    context?: Record<string, any>
  ): Promise<KimiK2Response> => {
    const systemMessages = {
      sentiment: 'You are an expert in sentiment analysis. Analyze the emotional tone, opinions, and attitudes expressed in the given content.',
      technical: 'You are a technical analyst. Examine the technical aspects, quality, and implementation details of the given content.',
      business: 'You are a business analyst. Evaluate the business implications, opportunities, and strategic aspects of the given content.',
      creative: 'You are a creative analyst. Assess the creative elements, originality, and artistic aspects of the given content.',
      general: 'You are a skilled analyst. Provide comprehensive analysis and insights about the given content.'
    };
    
    const request: KimiK2Request = {
      prompt: content,
      systemMessage: systemMessages[analysisType],
      agentId,
      module: 'analysis',
      context: { ...context, analysisType },
      temperature: 0.4,
      maxTokens: 6144
    };

    return base.sendRequest(request);
  }, [base]);

  return {
    ...base,
    analyzeContent
  };
};