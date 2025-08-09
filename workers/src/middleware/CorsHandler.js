/**
 * CORS Handler for Hearthlink Workers API
 * 
 * Handles Cross-Origin Resource Sharing with proper security controls
 * and support for various client environments including Electron apps.
 */

export class CorsHandler {
  constructor(env) {
    this.env = env;
    this.allowedOrigins = this.parseAllowedOrigins(env.CORS_ORIGINS);
    this.allowedMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'];
    this.allowedHeaders = [
      'Authorization',
      'Content-Type',
      'X-Requested-With',
      'X-API-Key',
      'X-Client-Version',
      'Accept',
      'Origin',
      'User-Agent'
    ];
    this.exposedHeaders = [
      'X-RateLimit-Limit',
      'X-RateLimit-Remaining', 
      'X-RateLimit-Reset',
      'X-Request-ID',
      'X-Response-Time'
    ];
    this.maxAge = 86400; // 24 hours
  }

  /**
   * Parse allowed origins from environment variable
   */
  parseAllowedOrigins(corsOrigins) {
    if (!corsOrigins) {
      return ['*']; // Default to allow all in development
    }

    if (corsOrigins === '*') {
      return ['*'];
    }

    return corsOrigins.split(',').map(origin => origin.trim());
  }

  /**
   * Check if origin is allowed
   */
  isOriginAllowed(origin) {
    if (!origin) {
      return true; // Allow requests without origin (same-origin, mobile apps, etc.)
    }

    if (this.allowedOrigins.includes('*')) {
      return true;
    }

    // Exact match
    if (this.allowedOrigins.includes(origin)) {
      return true;
    }

    // Support for localhost with any port in development
    if (this.env.ENVIRONMENT === 'development') {
      const localhostPattern = /^https?:\/\/(localhost|127\.0\.0\.1|0\.0\.0\.0)(:\d+)?$/;
      if (localhostPattern.test(origin)) {
        return true;
      }

      // Support for file:// protocol (Electron apps)
      if (origin.startsWith('file://')) {
        return true;
      }
    }

    // Support for Electron apps (various protocols)
    const electronProtocols = ['app:', 'file:', 'electron:'];
    if (electronProtocols.some(protocol => origin.startsWith(protocol))) {
      return true;
    }

    return false;
  }

  /**
   * Handle CORS preflight requests
   */
  handlePreflight(request) {
    const origin = request.headers.get('Origin');
    const requestMethod = request.headers.get('Access-Control-Request-Method');
    const requestHeaders = request.headers.get('Access-Control-Request-Headers');

    // Check if origin is allowed
    if (!this.isOriginAllowed(origin)) {
      return new Response(null, {
        status: 403,
        statusText: 'Origin not allowed'
      });
    }

    // Check if method is allowed
    if (requestMethod && !this.allowedMethods.includes(requestMethod)) {
      return new Response(null, {
        status: 405,
        statusText: 'Method not allowed'
      });
    }

    const headers = new Headers();

    // Set CORS headers
    if (origin && this.isOriginAllowed(origin)) {
      headers.set('Access-Control-Allow-Origin', origin);
    } else if (this.allowedOrigins.includes('*')) {
      headers.set('Access-Control-Allow-Origin', '*');
    }

    headers.set('Access-Control-Allow-Methods', this.allowedMethods.join(', '));
    headers.set('Access-Control-Allow-Headers', this.allowedHeaders.join(', '));
    headers.set('Access-Control-Expose-Headers', this.exposedHeaders.join(', '));
    headers.set('Access-Control-Max-Age', this.maxAge.toString());
    headers.set('Access-Control-Allow-Credentials', 'true');

    // Security headers
    headers.set('Vary', 'Origin, Access-Control-Request-Method, Access-Control-Request-Headers');

    return new Response(null, {
      status: 200,
      headers
    });
  }

  /**
   * CORS middleware for all requests
   */
  middleware = (request) => {
    const origin = request.headers.get('Origin');

    // Add CORS headers to the request object for later use
    request.corsHeaders = this.getCorsHeaders(origin);
  };

  /**
   * Get CORS headers for response
   */
  getCorsHeaders(origin) {
    const headers = new Headers();

    // Set origin
    if (origin && this.isOriginAllowed(origin)) {
      headers.set('Access-Control-Allow-Origin', origin);
    } else if (this.allowedOrigins.includes('*')) {
      headers.set('Access-Control-Allow-Origin', '*');
    }

    // Set other CORS headers
    headers.set('Access-Control-Allow-Methods', this.allowedMethods.join(', '));
    headers.set('Access-Control-Allow-Headers', this.allowedHeaders.join(', '));
    headers.set('Access-Control-Expose-Headers', this.exposedHeaders.join(', '));
    headers.set('Access-Control-Allow-Credentials', 'true');

    // Security headers
    headers.set('Vary', 'Origin');

    return headers;
  }

  /**
   * Add CORS headers to response
   */
  static addCorsHeaders(response, corsHeaders) {
    if (!corsHeaders) return response;

    const headers = new Headers(response.headers);

    // Add all CORS headers
    for (const [key, value] of corsHeaders.entries()) {
      headers.set(key, value);
    }

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers
    });
  }

  /**
   * Security-focused CORS for production
   */
  getStrictCorsHeaders(origin) {
    const headers = new Headers();

    // Only allow specific origins in production
    if (this.env.ENVIRONMENT === 'production') {
      if (origin && this.allowedOrigins.includes(origin)) {
        headers.set('Access-Control-Allow-Origin', origin);
      }
      // No wildcard in production
    } else {
      // More permissive in development
      if (origin && this.isOriginAllowed(origin)) {
        headers.set('Access-Control-Allow-Origin', origin);
      } else if (this.allowedOrigins.includes('*')) {
        headers.set('Access-Control-Allow-Origin', '*');
      }
    }

    headers.set('Access-Control-Allow-Methods', this.allowedMethods.join(', '));
    headers.set('Access-Control-Allow-Headers', this.allowedHeaders.join(', '));
    headers.set('Access-Control-Expose-Headers', this.exposedHeaders.join(', '));
    headers.set('Access-Control-Allow-Credentials', 'true');

    // Additional security headers
    headers.set('Vary', 'Origin, Access-Control-Request-Method, Access-Control-Request-Headers');
    headers.set('X-Content-Type-Options', 'nosniff');
    headers.set('X-Frame-Options', 'DENY');

    return headers;
  }

  /**
   * Enhanced middleware with security checks
   */
  securityMiddleware = (request) => {
    const origin = request.headers.get('Origin');
    const userAgent = request.headers.get('User-Agent');

    // Log suspicious requests
    if (origin && !this.isOriginAllowed(origin)) {
      console.warn(`Blocked request from unauthorized origin: ${origin}`, {
        userAgent,
        ip: request.headers.get('CF-Connecting-IP'),
        url: request.url
      });
    }

    // Check for common attack patterns
    if (this.detectSuspiciousActivity(request)) {
      console.warn('Suspicious activity detected', {
        origin,
        userAgent,
        ip: request.headers.get('CF-Connecting-IP'),
        url: request.url
      });
    }

    // Add security-focused CORS headers
    request.corsHeaders = this.getStrictCorsHeaders(origin);
  };

  /**
   * Detect suspicious activity patterns
   */
  detectSuspiciousActivity(request) {
    const userAgent = request.headers.get('User-Agent') || '';
    const referer = request.headers.get('Referer') || '';

    // Check for common bot patterns
    const botPatterns = [
      /bot/i,
      /crawler/i,
      /spider/i,
      /scraper/i,
      /scanner/i
    ];

    if (botPatterns.some(pattern => pattern.test(userAgent))) {
      return true;
    }

    // Check for suspicious referers
    const suspiciousReferers = [
      /malware/i,
      /phishing/i,
      /attack/i
    ];

    if (suspiciousReferers.some(pattern => pattern.test(referer))) {
      return true;
    }

    return false;
  }

  /**
   * CORS configuration for WebSocket upgrades
   */
  getWebSocketCorsHeaders(origin) {
    const headers = new Headers();

    if (origin && this.isOriginAllowed(origin)) {
      headers.set('Access-Control-Allow-Origin', origin);
      headers.set('Access-Control-Allow-Credentials', 'true');
    }

    return headers;
  }

  /**
   * Handle CORS for file uploads
   */
  getFileUploadCorsHeaders(origin) {
    const headers = this.getCorsHeaders(origin);
    
    // Add specific headers for file uploads
    headers.set('Access-Control-Allow-Headers', [
      ...this.allowedHeaders,
      'Content-Length',
      'Content-Range',
      'Content-Disposition'
    ].join(', '));

    return headers;
  }

  /**
   * Validate request against CORS policy
   */
  validateRequest(request) {
    const origin = request.headers.get('Origin');
    const method = request.method;

    // Check origin
    if (origin && !this.isOriginAllowed(origin)) {
      return {
        valid: false,
        reason: 'Origin not allowed',
        origin
      };
    }

    // Check method
    if (!this.allowedMethods.includes(method)) {
      return {
        valid: false,
        reason: 'Method not allowed',
        method
      };
    }

    return { valid: true };
  }

  /**
   * Create CORS error response
   */
  createCorsErrorResponse(validation) {
    return new Response(JSON.stringify({
      success: false,
      error: {
        code: 'CORS_ERROR',
        message: validation.reason,
        details: validation
      }
    }), {
      status: 403,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'null'
      }
    });
  }
}