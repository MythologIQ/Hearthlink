/**
 * Rate Limiter for Hearthlink Workers API
 * 
 * Implements sliding window rate limiting with IP and user-based limits
 * to prevent abuse and ensure fair usage of the API.
 */

import { ErrorHandler } from '../utils/ErrorHandler.js';

export class RateLimiter {
  constructor(env) {
    this.env = env;
    this.defaultLimit = parseInt(env.RATE_LIMIT_PER_MINUTE) || 100;
    this.windowSize = 60 * 1000; // 1 minute in milliseconds
  }

  /**
   * Rate limiting middleware
   */
  middleware = async (request) => {
    try {
      const clientId = this.getClientId(request);
      const endpoint = this.getEndpoint(request);
      
      // Get rate limit configuration for this endpoint
      const limit = this.getEndpointLimit(endpoint);
      
      // Check rate limit
      const allowed = await this.isAllowed(clientId, endpoint, limit);
      
      if (!allowed.success) {
        return ErrorHandler.tooManyRequests(
          'Rate limit exceeded', 
          allowed.resetTime
        );
      }

      // Add rate limit headers to response
      request.rateLimitInfo = {
        limit: limit,
        remaining: allowed.remaining,
        resetTime: allowed.resetTime
      };

    } catch (error) {
      // Don't block requests if rate limiting fails
      console.error('Rate limiting error:', error);
    }
  };

  /**
   * Check if request is allowed based on rate limits
   */
  async isAllowed(clientId, endpoint, limit) {
    const now = Date.now();
    const windowStart = now - this.windowSize;
    const key = `ratelimit:${clientId}:${endpoint}`;
    
    // Get current request count from KV
    const data = await this.env.RATE_LIMITS.get(key);
    let requests = data ? JSON.parse(data) : [];
    
    // Remove requests outside the current window
    requests = requests.filter(timestamp => timestamp > windowStart);
    
    // Check if limit exceeded
    if (requests.length >= limit) {
      const oldestRequest = Math.min(...requests);
      const resetTime = oldestRequest + this.windowSize;
      
      return {
        success: false,
        remaining: 0,
        resetTime: resetTime
      };
    }

    // Add current request
    requests.push(now);
    
    // Store updated requests with TTL
    await this.env.RATE_LIMITS.put(
      key, 
      JSON.stringify(requests),
      { expirationTtl: Math.ceil(this.windowSize / 1000) }
    );

    return {
      success: true,
      remaining: limit - requests.length,
      resetTime: now + this.windowSize
    };
  }

  /**
   * Get client identifier for rate limiting
   */
  getClientId(request) {
    // Use user ID if authenticated, otherwise use IP address
    if (request.user && request.user.id) {
      return `user:${request.user.id}`;
    }
    
    // Get IP address from various headers
    const ip = request.headers.get('CF-Connecting-IP') || 
               request.headers.get('X-Forwarded-For') ||
               request.headers.get('X-Real-IP') ||
               '127.0.0.1';
    
    return `ip:${ip.split(',')[0].trim()}`;
  }

  /**
   * Get normalized endpoint for rate limiting
   */
  getEndpoint(request) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // Normalize paths with IDs to group similar endpoints
    const normalizedPath = path
      .replace(/\/api\/v\d+/, '') // Remove API version
      .replace(/\/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, '/:id') // UUID
      .replace(/\/\d+/g, '/:id') // Numeric IDs
      .replace(/\/[a-zA-Z0-9_-]{20,}/g, '/:id'); // Long alphanumeric IDs

    return `${request.method}:${normalizedPath}`;
  }

  /**
   * Get rate limit for specific endpoint
   */
  getEndpointLimit(endpoint) {
    // Different limits for different endpoints
    const endpointLimits = {
      'POST:/auth/login': 10, // Stricter limit for login attempts
      'POST:/auth/refresh': 20,
      'GET:/health': 1000, // Higher limit for health checks
      'GET:/status': 1000,
      'POST:/agents/:id/query': 50, // Moderate limit for AI queries
      'GET:/memory/:id/search': 100,
      'POST:/memory/:id': 30,
      'GET:/system/metrics': 200,
      'POST:/files/upload': 10, // Strict limit for file uploads
    };

    return endpointLimits[endpoint] || this.defaultLimit;
  }

  /**
   * Add rate limit headers to response
   */
  static addHeaders(response, rateLimitInfo) {
    if (!rateLimitInfo) return response;

    const headers = new Headers(response.headers);
    headers.set('X-RateLimit-Limit', rateLimitInfo.limit.toString());
    headers.set('X-RateLimit-Remaining', rateLimitInfo.remaining.toString());
    headers.set('X-RateLimit-Reset', rateLimitInfo.resetTime.toString());

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers
    });
  }

  /**
   * Cleanup expired rate limit data
   */
  static async cleanup(env) {
    try {
      // KV automatically expires keys based on TTL, so no manual cleanup needed
      // This method exists for potential future custom cleanup logic
      console.log('Rate limit cleanup completed');
    } catch (error) {
      console.error('Rate limit cleanup failed:', error);
    }
  }

  /**
   * Get current rate limit status for a client
   */
  async getStatus(clientId, endpoint) {
    const limit = this.getEndpointLimit(endpoint);
    const key = `ratelimit:${clientId}:${endpoint}`;
    
    const data = await this.env.RATE_LIMITS.get(key);
    const requests = data ? JSON.parse(data) : [];
    
    const now = Date.now();
    const windowStart = now - this.windowSize;
    const validRequests = requests.filter(timestamp => timestamp > windowStart);
    
    return {
      limit: limit,
      used: validRequests.length,
      remaining: limit - validRequests.length,
      resetTime: now + this.windowSize
    };
  }

  /**
   * Whitelist IP or user from rate limiting
   */
  async whitelist(identifier, duration = 24 * 60 * 60 * 1000) {
    const key = `whitelist:${identifier}`;
    await this.env.RATE_LIMITS.put(key, 'true', {
      expirationTtl: Math.ceil(duration / 1000)
    });
  }

  /**
   * Check if identifier is whitelisted
   */
  async isWhitelisted(identifier) {
    const key = `whitelist:${identifier}`;
    const whitelisted = await this.env.RATE_LIMITS.get(key);
    return whitelisted === 'true';
  }

  /**
   * Block IP or user temporarily
   */
  async block(identifier, duration = 60 * 60 * 1000) {
    const key = `blocked:${identifier}`;
    await this.env.RATE_LIMITS.put(key, 'true', {
      expirationTtl: Math.ceil(duration / 1000)
    });
  }

  /**
   * Check if identifier is blocked
   */
  async isBlocked(identifier) {
    const key = `blocked:${identifier}`;
    const blocked = await this.env.RATE_LIMITS.get(key);
    return blocked === 'true';
  }

  /**
   * Enhanced middleware with whitelist/blacklist support
   */
  enhancedMiddleware = async (request) => {
    try {
      const clientId = this.getClientId(request);
      
      // Check if blocked
      if (await this.isBlocked(clientId)) {
        return ErrorHandler.forbidden('Client is temporarily blocked');
      }
      
      // Check if whitelisted
      if (await this.isWhitelisted(clientId)) {
        return; // Skip rate limiting for whitelisted clients
      }
      
      // Apply normal rate limiting
      return this.middleware(request);
      
    } catch (error) {
      console.error('Enhanced rate limiting error:', error);
    }
  };
}