export class BaseError extends Error {
  public readonly name: string;
  public readonly code: string;
  public readonly statusCode: number;
  public readonly details?: any;
  public readonly timestamp: string;

  constructor(message: string, code: string, statusCode: number = 500, details?: any) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    this.timestamp = new Date().toISOString();
    
    // Ensure the stack trace points to the actual error location
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON(): any {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
      details: this.details,
      timestamp: this.timestamp,
      stack: this.stack
    };
  }
}

export class APIError extends BaseError {
  constructor(message: string, statusCode: number = 500, details?: any) {
    super(message, 'API_ERROR', statusCode, details);
  }
}

export class SecurityError extends BaseError {
  constructor(message: string, details?: any) {
    super(message, 'SECURITY_ERROR', 403, details);
  }
}

export class RateLimitError extends BaseError {
  public readonly retryAfter?: number;

  constructor(message: string, retryAfter?: string | number, details?: any) {
    super(message, 'RATE_LIMIT_ERROR', 429, details);
    
    if (retryAfter) {
      this.retryAfter = typeof retryAfter === 'string' ? parseInt(retryAfter, 10) : retryAfter;
    }
  }
}

export class ValidationError extends BaseError {
  constructor(message: string, details?: any) {
    super(message, 'VALIDATION_ERROR', 400, details);
  }
}

export class TimeoutError extends BaseError {
  constructor(message: string, timeout: number, details?: any) {
    super(message, 'TIMEOUT_ERROR', 408, { timeout, ...details });
  }
}

export class ConfigurationError extends BaseError {
  constructor(message: string, details?: any) {
    super(message, 'CONFIGURATION_ERROR', 500, details);
  }
}

export class ConnectionError extends BaseError {
  constructor(message: string, details?: any) {
    super(message, 'CONNECTION_ERROR', 503, details);
  }
}

export class TokenLimitError extends BaseError {
  constructor(message: string, limit: number, requested: number, details?: any) {
    super(message, 'TOKEN_LIMIT_ERROR', 400, { limit, requested, ...details });
  }
}

export class ModelNotAvailableError extends BaseError {
  constructor(message: string, model: string, details?: any) {
    super(message, 'MODEL_NOT_AVAILABLE', 503, { model, ...details });
  }
}

export class ToolCallError extends BaseError {
  public readonly toolName: string;
  public readonly toolArgs: any;

  constructor(message: string, toolName: string, toolArgs: any, details?: any) {
    super(message, 'TOOL_CALL_ERROR', 500, { toolName, toolArgs, ...details });
    this.toolName = toolName;
    this.toolArgs = toolArgs;
  }
}

export class ToolCallSecurityError extends BaseError {
  constructor(message: string, details?: any) {
    super(message, 'TOOL_CALL_SECURITY_ERROR', 403, details);
  }
}

export class VaultError extends BaseError {
  constructor(message: string, operation: string, details?: any) {
    super(message, 'VAULT_ERROR', 500, { operation, ...details });
  }
}

export class CircuitBreakerError extends BaseError {
  constructor(message: string, state: string, details?: any) {
    super(message, 'CIRCUIT_BREAKER_ERROR', 503, { state, ...details });
  }
}

// Error handler utility
export class ErrorHandler {
  static handle(error: Error): BaseError {
    if (error instanceof BaseError) {
      return error;
    }

    // Handle fetch errors
    if (error.name === 'AbortError') {
      return new TimeoutError('Request timed out', 30000);
    }

    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return new ConnectionError('Network connection failed', { originalError: error.message });
    }

    // Handle JSON parsing errors
    if (error instanceof SyntaxError && error.message.includes('JSON')) {
      return new APIError('Invalid JSON response', 502, { originalError: error.message });
    }

    // Default to generic API error
    return new APIError(error.message || 'Unknown error occurred', 500, { originalError: error });
  }

  static isRetryable(error: Error): boolean {
    if (error instanceof BaseError) {
      return [
        'TIMEOUT_ERROR',
        'CONNECTION_ERROR',
        'RATE_LIMIT_ERROR'
      ].includes(error.code) || (error.statusCode >= 500 && error.statusCode < 600);
    }

    return false;
  }

  static getRetryDelay(error: Error, attempt: number): number {
    if (error instanceof RateLimitError && error.retryAfter) {
      return error.retryAfter * 1000; // Convert to milliseconds
    }

    // Exponential backoff with jitter
    const baseDelay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s, 8s, etc.
    const jitter = Math.random() * 0.1 * baseDelay; // Add up to 10% jitter
    return Math.min(baseDelay + jitter, 60000); // Cap at 60 seconds
  }
}

// Error logging utility
export class ErrorLogger {
  static log(error: Error, context?: any): void {
    const errorData = {
      error: error instanceof BaseError ? error.toJSON() : {
        name: error.name,
        message: error.message,
        stack: error.stack
      },
      context,
      timestamp: new Date().toISOString()
    };

    console.error('Error logged:', errorData);
    
    // In production, this would send to your logging service
    // e.g., Sentry, LogRocket, etc.
  }
}