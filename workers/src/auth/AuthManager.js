/**
 * Authentication Manager for Hearthlink Workers API
 * 
 * Handles JWT tokens, session management, and user authentication
 * with integration to the main Hearthlink authentication system.
 */

import { SignJWT, jwtVerify } from 'jose';
import bcrypt from 'bcryptjs';
import { ErrorHandler } from '../utils/ErrorHandler.js';

export class AuthManager {
  constructor(env) {
    this.env = env;
    this.jwtSecret = new TextEncoder().encode(env.JWT_SECRET || 'fallback-secret-key');
    this.sessionTTL = 24 * 60 * 60 * 1000; // 24 hours
    this.refreshTTL = 7 * 24 * 60 * 60 * 1000; // 7 days
  }

  /**
   * Middleware to validate authentication for protected routes
   */
  middleware = async (request) => {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // Skip auth for public endpoints
    const publicPaths = ['/health', '/status', '/auth/login', '/auth/refresh'];
    if (publicPaths.some(p => path.endsWith(p))) {
      return; // Continue to next middleware
    }

    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return ErrorHandler.unauthorized('Missing or invalid authorization header');
    }

    const token = authHeader.substring(7);
    
    try {
      const payload = await this.verifyToken(token);
      
      // Check if session is still valid
      const sessionData = await this.env.SESSIONS.get(payload.sessionId);
      if (!sessionData) {
        return ErrorHandler.unauthorized('Session expired or invalid');
      }

      const session = JSON.parse(sessionData);
      if (session.expiresAt < Date.now()) {
        await this.env.SESSIONS.delete(payload.sessionId);
        return ErrorHandler.unauthorized('Session expired');
      }

      // Update last accessed time
      session.lastAccessed = Date.now();
      await this.env.SESSIONS.put(payload.sessionId, JSON.stringify(session), {
        expirationTtl: this.sessionTTL / 1000
      });

      // Attach user info to request
      request.user = {
        id: payload.userId,
        email: payload.email,
        roles: payload.roles || [],
        sessionId: payload.sessionId
      };

    } catch (error) {
      return ErrorHandler.unauthorized('Invalid token');
    }
  };

  /**
   * Login endpoint - authenticate user and create session
   */
  login = async (request) => {
    try {
      const { email, password, deviceInfo } = await request.json();

      if (!email || !password) {
        return ErrorHandler.badRequest('Email and password are required');
      }

      // In a real implementation, this would validate against your user database
      // For now, we'll use a simple validation system
      const user = await this.validateUser(email, password);
      if (!user) {
        return ErrorHandler.unauthorized('Invalid credentials');
      }

      // Generate session ID
      const sessionId = crypto.randomUUID();
      
      // Create session data
      const sessionData = {
        userId: user.id,
        email: user.email,
        roles: user.roles,
        deviceInfo: deviceInfo || {},
        createdAt: Date.now(),
        lastAccessed: Date.now(),
        expiresAt: Date.now() + this.sessionTTL
      };

      // Store session in KV
      await this.env.SESSIONS.put(sessionId, JSON.stringify(sessionData), {
        expirationTtl: this.sessionTTL / 1000
      });

      // Generate JWT tokens
      const accessToken = await this.generateToken({
        userId: user.id,
        email: user.email,
        roles: user.roles,
        sessionId
      }, '1h');

      const refreshToken = await this.generateToken({
        userId: user.id,
        sessionId,
        type: 'refresh'
      }, '7d');

      return new Response(JSON.stringify({
        success: true,
        data: {
          accessToken,
          refreshToken,
          user: {
            id: user.id,
            email: user.email,
            roles: user.roles
          },
          expiresAt: sessionData.expiresAt
        }
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Set-Cookie': `refreshToken=${refreshToken}; HttpOnly; Secure; SameSite=Strict; Max-Age=${this.refreshTTL / 1000}`
        }
      });

    } catch (error) {
      return ErrorHandler.internal(error, this.env.DEBUG_MODE);
    }
  };

  /**
   * Logout endpoint - invalidate session and tokens
   */
  logout = async (request) => {
    try {
      const sessionId = request.user?.sessionId;
      
      if (sessionId) {
        await this.env.SESSIONS.delete(sessionId);
      }

      return new Response(JSON.stringify({
        success: true,
        message: 'Logged out successfully'
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Set-Cookie': 'refreshToken=; HttpOnly; Secure; SameSite=Strict; Max-Age=0'
        }
      });

    } catch (error) {
      return ErrorHandler.internal(error, this.env.DEBUG_MODE);
    }
  };

  /**
   * Refresh token endpoint - generate new access token
   */
  refresh = async (request) => {
    try {
      // Get refresh token from cookie or Authorization header
      let refreshToken = this.getCookieValue(request, 'refreshToken');
      
      if (!refreshToken) {
        const authHeader = request.headers.get('Authorization');
        if (authHeader && authHeader.startsWith('Bearer ')) {
          refreshToken = authHeader.substring(7);
        }
      }

      if (!refreshToken) {
        return ErrorHandler.unauthorized('Refresh token required');
      }

      const payload = await this.verifyToken(refreshToken);
      
      if (payload.type !== 'refresh') {
        return ErrorHandler.unauthorized('Invalid refresh token');
      }

      // Check if session still exists
      const sessionData = await this.env.SESSIONS.get(payload.sessionId);
      if (!sessionData) {
        return ErrorHandler.unauthorized('Session expired');
      }

      const session = JSON.parse(sessionData);
      
      // Generate new access token
      const accessToken = await this.generateToken({
        userId: session.userId,
        email: session.email,
        roles: session.roles,
        sessionId: payload.sessionId
      }, '1h');

      return new Response(JSON.stringify({
        success: true,
        data: {
          accessToken,
          expiresAt: Date.now() + (60 * 60 * 1000) // 1 hour
        }
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return ErrorHandler.unauthorized('Invalid refresh token');
    }
  };

  /**
   * Validate token endpoint - check if token is valid
   */
  validate = async (request) => {
    try {
      return new Response(JSON.stringify({
        success: true,
        valid: true,
        user: request.user
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return ErrorHandler.internal(error, this.env.DEBUG_MODE);
    }
  };

  /**
   * Generate JWT token
   */
  async generateToken(payload, expiresIn) {
    const jwt = await new SignJWT(payload)
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime(expiresIn)
      .setIssuer('hearthlink-workers-api')
      .setAudience('hearthlink-client')
      .sign(this.jwtSecret);

    return jwt;
  }

  /**
   * Verify JWT token
   */
  async verifyToken(token) {
    const { payload } = await jwtVerify(token, this.jwtSecret, {
      issuer: 'hearthlink-workers-api',
      audience: 'hearthlink-client'
    });

    return payload;
  }

  /**
   * Validate user credentials
   * In a real implementation, this would query your user database
   */
  async validateUser(email, password) {
    // Demo users for testing
    const demoUsers = [
      {
        id: '1',
        email: 'admin@hearthlink.ai',
        passwordHash: await bcrypt.hash('admin123', 10),
        roles: ['admin', 'user']
      },
      {
        id: '2', 
        email: 'user@hearthlink.ai',
        passwordHash: await bcrypt.hash('user123', 10),
        roles: ['user']
      }
    ];

    const user = demoUsers.find(u => u.email === email);
    if (!user) return null;

    const isValid = await bcrypt.compare(password, user.passwordHash);
    if (!isValid) return null;

    return {
      id: user.id,
      email: user.email,
      roles: user.roles
    };
  }

  /**
   * Get cookie value from request
   */
  getCookieValue(request, name) {
    const cookies = request.headers.get('Cookie');
    if (!cookies) return null;

    const cookieMatch = cookies.match(new RegExp(`${name}=([^;]+)`));
    return cookieMatch ? cookieMatch[1] : null;
  }

  /**
   * Check if user has required role
   */
  hasRole(user, role) {
    return user.roles && user.roles.includes(role);
  }

  /**
   * Require specific role middleware
   */
  requireRole(role) {
    return (request) => {
      if (!request.user || !this.hasRole(request.user, role)) {
        return ErrorHandler.forbidden(`Requires ${role} role`);
      }
    };
  }
}