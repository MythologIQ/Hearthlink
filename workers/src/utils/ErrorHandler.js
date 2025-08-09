/**
 * Error Handler for Hearthlink Workers API
 * 
 * Centralized error handling with consistent response formats,
 * security considerations, and proper HTTP status codes.
 */

export class ErrorHandler {
  /**
   * Generic error response builder
   */
  static buildErrorResponse(status, error, message, details = null, debugMode = false) {
    const response = {
      success: false,
      error: {
        code: error,
        message: message,
        timestamp: new Date().toISOString()
      }
    };

    // Add details in debug mode or for client errors
    if (debugMode || status < 500) {
      if (details) {
        response.error.details = details;
      }
    }

    // Add request ID if available
    if (globalThis.requestId) {
      response.error.requestId = globalThis.requestId;
    }

    return new Response(JSON.stringify(response), {
      status: status,
      headers: {
        'Content-Type': 'application/json',
        'X-Error-Code': error
      }
    });
  }

  /**
   * 400 Bad Request
   */
  static badRequest(message = 'Bad Request', details = null) {
    return ErrorHandler.buildErrorResponse(
      400,
      'BAD_REQUEST',
      message,
      details
    );
  }

  /**
   * 401 Unauthorized
   */
  static unauthorized(message = 'Unauthorized', details = null) {
    return ErrorHandler.buildErrorResponse(
      401,
      'UNAUTHORIZED',
      message,
      details
    );
  }

  /**
   * 403 Forbidden
   */
  static forbidden(message = 'Forbidden', details = null) {
    return ErrorHandler.buildErrorResponse(
      403,
      'FORBIDDEN',
      message,
      details
    );
  }

  /**
   * 404 Not Found
   */
  static notFound(message = 'Not Found', details = null) {
    return ErrorHandler.buildErrorResponse(
      404,
      'NOT_FOUND',
      message,
      details
    );
  }

  /**
   * 405 Method Not Allowed
   */
  static methodNotAllowed(message = 'Method Not Allowed', allowedMethods = []) {
    const response = ErrorHandler.buildErrorResponse(
      405,
      'METHOD_NOT_ALLOWED',
      message,
      { allowedMethods }
    );

    // Add Allow header
    if (allowedMethods.length > 0) {
      response.headers.set('Allow', allowedMethods.join(', '));
    }

    return response;
  }

  /**
   * 409 Conflict
   */
  static conflict(message = 'Conflict', details = null) {
    return ErrorHandler.buildErrorResponse(
      409,
      'CONFLICT',
      message,
      details
    );
  }

  /**
   * 422 Unprocessable Entity
   */
  static unprocessableEntity(message = 'Unprocessable Entity', validationErrors = null) {
    return ErrorHandler.buildErrorResponse(
      422,
      'UNPROCESSABLE_ENTITY',
      message,
      validationErrors ? { validationErrors } : null
    );
  }

  /**
   * 429 Too Many Requests
   */
  static tooManyRequests(message = 'Too Many Requests', resetTime = null) {
    const response = ErrorHandler.buildErrorResponse(
      429,
      'TOO_MANY_REQUESTS',
      message,
      resetTime ? { resetTime } : null
    );

    // Add rate limit headers
    if (resetTime) {
      response.headers.set('Retry-After', Math.ceil((resetTime - Date.now()) / 1000).toString());
      response.headers.set('X-RateLimit-Reset', resetTime.toString());
    }

    return response;
  }

  /**
   * 500 Internal Server Error
   */
  static internal(error, debugMode = false) {
    let message = 'Internal Server Error';
    let details = null;

    if (debugMode && error) {
      message = error.message || message;
      details = {
        stack: error.stack,
        name: error.name
      };
    }

    // Log error for monitoring
    console.error('Internal Server Error:', error);

    return ErrorHandler.buildErrorResponse(
      500,
      'INTERNAL_SERVER_ERROR',
      message,
      details,
      debugMode
    );
  }

  /**
   * 502 Bad Gateway
   */
  static badGateway(message = 'Bad Gateway', upstreamError = null) {
    return ErrorHandler.buildErrorResponse(
      502,
      'BAD_GATEWAY',
      message,
      upstreamError ? { upstream: upstreamError } : null
    );
  }

  /**
   * 503 Service Unavailable
   */
  static serviceUnavailable(message = 'Service Unavailable', retryAfter = null) {
    const response = ErrorHandler.buildErrorResponse(
      503,
      'SERVICE_UNAVAILABLE',
      message,
      retryAfter ? { retryAfter } : null
    );

    if (retryAfter) {
      response.headers.set('Retry-After', retryAfter.toString());
    }

    return response;
  }

  /**
   * 504 Gateway Timeout
   */
  static gatewayTimeout(message = 'Gateway Timeout', timeout = null) {
    return ErrorHandler.buildErrorResponse(
      504,
      'GATEWAY_TIMEOUT',
      message,
      timeout ? { timeout } : null
    );
  }

  /**
   * Handle specific error types
   */
  static handleError(error, debugMode = false) {
    // JWT verification errors
    if (error.name === 'JWTExpired') {
      return ErrorHandler.unauthorized('Token expired');
    }

    if (error.name === 'JWTInvalid') {
      return ErrorHandler.unauthorized('Invalid token');
    }

    // Validation errors
    if (error.name === 'ValidationError') {
      return ErrorHandler.unprocessableEntity(
        'Validation failed',
        error.details || error.message
      );
    }

    // Rate limiting errors
    if (error.name === 'RateLimitError') {
      return ErrorHandler.tooManyRequests(
        error.message,
        error.resetTime
      );
    }

    // Network/timeout errors
    if (error.name === 'TimeoutError') {
      return ErrorHandler.gatewayTimeout('Request timeout');
    }

    if (error.name === 'NetworkError') {
      return ErrorHandler.badGateway('Network error');
    }

    // Default to internal server error
    return ErrorHandler.internal(error, debugMode);
  }

  /**
   * Validation error helper
   */
  static validationError(field, message, value = null) {
    return ErrorHandler.unprocessableEntity('Validation failed', [{
      field,
      message,
      value
    }]);
  }

  /**
   * Multiple validation errors
   */
  static multipleValidationErrors(errors) {
    return ErrorHandler.unprocessableEntity(
      'Multiple validation errors',
      errors.map(error => ({
        field: error.field,
        message: error.message,
        value: error.value
      }))
    );
  }

  /**
   * Authentication error with specific reason
   */
  static authenticationError(reason, details = null) {
    const messages = {
      'invalid_credentials': 'Invalid username or password',
      'account_locked': 'Account is temporarily locked',
      'account_disabled': 'Account has been disabled',
      'token_expired': 'Authentication token has expired',
      'token_invalid': 'Authentication token is invalid',
      'session_expired': 'Session has expired',
      'mfa_required': 'Multi-factor authentication required'
    };

    return ErrorHandler.unauthorized(
      messages[reason] || 'Authentication failed',
      details
    );
  }

  /**
   * Authorization error with specific reason
   */
  static authorizationError(reason, requiredPermission = null) {
    const messages = {
      'insufficient_permissions': 'Insufficient permissions',
      'role_required': 'Specific role required',
      'resource_access_denied': 'Access to resource denied',
      'action_not_allowed': 'Action not allowed'
    };

    const details = requiredPermission ? { requiredPermission } : null;

    return ErrorHandler.forbidden(
      messages[reason] || 'Access denied',
      details
    );
  }

  /**
   * API error with custom error code
   */
  static apiError(status, errorCode, message, details = null) {
    return ErrorHandler.buildErrorResponse(
      status,
      errorCode,
      message,
      details
    );
  }

  /**
   * Handle async errors
   */
  static async handleAsync(fn, debugMode = false) {
    try {
      return await fn();
    } catch (error) {
      return ErrorHandler.handleError(error, debugMode);
    }
  }

  /**
   * Middleware wrapper for error handling
   */
  static wrap(handler, debugMode = false) {
    return async (...args) => {
      try {
        return await handler(...args);
      } catch (error) {
        return ErrorHandler.handleError(error, debugMode);
      }
    };
  }

  /**
   * Log error for monitoring
   */
  static logError(error, request = null, extra = {}) {
    const logData = {
      timestamp: new Date().toISOString(),
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      },
      ...extra
    };

    if (request) {
      logData.request = {
        method: request.method,
        url: request.url,
        headers: Object.fromEntries(request.headers.entries()),
        userAgent: request.headers.get('User-Agent'),
        ip: request.headers.get('CF-Connecting-IP')
      };
    }

    console.error('API Error:', JSON.stringify(logData, null, 2));
  }

  /**
   * Create error from HTTP response
   */
  static fromResponse(response, context = null) {
    const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
    error.name = 'HTTPError';
    error.status = response.status;
    error.context = context;
    return error;
  }

  /**
   * Security headers for error responses
   */
  static addSecurityHeaders(response) {
    const headers = new Headers(response.headers);
    
    headers.set('X-Content-Type-Options', 'nosniff');
    headers.set('X-Frame-Options', 'DENY');
    headers.set('X-XSS-Protection', '1; mode=block');
    headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers
    });
  }
}