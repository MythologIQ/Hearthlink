/**
 * Hearthlink Cloudflare Workers API
 * 
 * Secure, globally distributed REST API for the Hearthlink AI orchestration platform.
 * Provides edge computing capabilities with authentication, rate limiting, and caching.
 */

import { Router } from 'itty-router';
import { AuthManager } from './auth/AuthManager.js';
import { RateLimiter } from './security/RateLimiter.js';
import { AgentHandler } from './handlers/AgentHandler.js';
import { MemoryHandler } from './handlers/MemoryHandler.js';
import { SessionHandler } from './handlers/SessionHandler.js';
import { SystemHandler } from './handlers/SystemHandler.js';
import { WebSocketHandler } from './handlers/WebSocketHandler.js';
import { CorsHandler } from './middleware/CorsHandler.js';
import { Logger } from './utils/Logger.js';
import { ErrorHandler } from './utils/ErrorHandler.js';

// Initialize router with base path
const router = Router({ base: '/api/v1' });

/**
 * Main request handler for Cloudflare Workers
 */
export default {
  async fetch(request, env, ctx) {
    const logger = new Logger(env);
    
    try {
      // Initialize services
      const authManager = new AuthManager(env);
      const rateLimiter = new RateLimiter(env);
      const corsHandler = new CorsHandler(env);
      
      // Handle CORS preflight requests
      if (request.method === 'OPTIONS') {
        return corsHandler.handlePreflight(request);
      }

      // Apply CORS headers to all responses
      const response = await router
        .all('*', corsHandler.middleware)
        .all('*', rateLimiter.middleware)
        .all('*', authManager.middleware)
        .all('*', (request) => {
          request.env = env;
          request.ctx = ctx;
          request.logger = logger;
        })
        
        // Health check endpoint (no auth required)
        .get('/health', SystemHandler.health)
        .get('/status', SystemHandler.status)
        
        // Authentication endpoints
        .post('/auth/login', authManager.login)
        .post('/auth/logout', authManager.logout)
        .post('/auth/refresh', authManager.refresh)
        .get('/auth/validate', authManager.validate)
        
        // Agent management endpoints
        .get('/agents', AgentHandler.list)
        .get('/agents/:agentId', AgentHandler.get)
        .post('/agents/:agentId/query', AgentHandler.query)
        .patch('/agents/:agentId/config', AgentHandler.updateConfig)
        .get('/agents/:agentId/status', AgentHandler.getStatus)
        .post('/agents/:agentId/reset', AgentHandler.reset)
        
        // Memory management endpoints
        .post('/memory/:agentId/search', MemoryHandler.search)
        .post('/memory/:agentId', MemoryHandler.create)
        .get('/memory/:agentId/:memoryId', MemoryHandler.get)
        .put('/memory/:agentId/:memoryId', MemoryHandler.update)
        .delete('/memory/:agentId/:memoryId', MemoryHandler.delete)
        .get('/memory/:agentId/stats', MemoryHandler.getStats)
        .post('/memory/:agentId/export', MemoryHandler.export)
        .post('/memory/:agentId/import', MemoryHandler.import)
        
        // Session management endpoints
        .post('/sessions', SessionHandler.create)
        .get('/sessions', SessionHandler.list)
        .get('/sessions/:sessionId', SessionHandler.get)
        .patch('/sessions/:sessionId', SessionHandler.update)
        .delete('/sessions/:sessionId', SessionHandler.delete)
        .post('/sessions/:sessionId/end', SessionHandler.end)
        
        // System management endpoints
        .get('/system/metrics', SystemHandler.metrics)
        .get('/system/config', SystemHandler.getConfig)
        .patch('/system/config', SystemHandler.updateConfig)
        .get('/system/logs', SystemHandler.getLogs)
        .post('/system/backup', SystemHandler.backup)
        .post('/system/restore', SystemHandler.restore)
        
        // Security and audit endpoints
        .get('/security/audit', SystemHandler.getAuditLogs)
        .get('/security/sessions', SystemHandler.getActiveSessions)
        .post('/security/revoke/:sessionId', SystemHandler.revokeSession)
        
        // WebSocket upgrade endpoint
        .get('/ws', WebSocketHandler.upgrade)
        
        // File operations (if R2 is enabled)
        .post('/files/upload', SystemHandler.uploadFile)
        .get('/files/:fileId', SystemHandler.downloadFile)
        .delete('/files/:fileId', SystemHandler.deleteFile)
        
        // Catch-all for 404s
        .all('*', () => ErrorHandler.notFound())
        
        .handle(request);

      // Log request details
      await logger.logRequest(request, response);
      
      return response;
      
    } catch (error) {
      await logger.logError(error, request);
      return ErrorHandler.internal(error, env.DEBUG_MODE);
    }
  },

  /**
   * Scheduled event handler for maintenance tasks
   */
  async scheduled(event, env, ctx) {
    const logger = new Logger(env);
    
    try {
      // Cleanup expired sessions
      await SessionHandler.cleanupExpired(env);
      
      // Cleanup rate limit counters
      await RateLimiter.cleanup(env);
      
      // Cleanup old logs (if enabled)
      if (env.LOG_RETENTION_DAYS) {
        await logger.cleanup(env.LOG_RETENTION_DAYS);
      }
      
      console.log('Scheduled maintenance completed successfully');
      
    } catch (error) {
      await logger.logError(error);
      console.error('Scheduled maintenance failed:', error.message);
    }
  }
};

/**
 * Durable Object for session management
 */
export class SessionManager {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.sessions = new Map();
  }

  async fetch(request) {
    const url = new URL(request.url);
    const sessionId = url.searchParams.get('sessionId');
    
    switch (request.method) {
      case 'GET':
        return new Response(JSON.stringify(this.sessions.get(sessionId) || null), {
          headers: { 'Content-Type': 'application/json' }
        });
        
      case 'POST':
        const sessionData = await request.json();
        this.sessions.set(sessionId, {
          ...sessionData,
          lastAccessed: Date.now()
        });
        return new Response(JSON.stringify({ success: true }), {
          headers: { 'Content-Type': 'application/json' }
        });
        
      case 'DELETE':
        this.sessions.delete(sessionId);
        return new Response(JSON.stringify({ success: true }), {
          headers: { 'Content-Type': 'application/json' }
        });
        
      default:
        return new Response('Method not allowed', { status: 405 });
    }
  }
}

/**
 * Durable Object for WebSocket connections
 */
export class WebSocketHandler {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.connections = new Set();
  }

  async fetch(request) {
    if (request.headers.get('Upgrade') !== 'websocket') {
      return new Response('Expected websocket', { status: 400 });
    }

    const [client, server] = Object.values(new WebSocketPair());
    
    server.accept();
    this.connections.add(server);
    
    server.addEventListener('message', async (event) => {
      try {
        const data = JSON.parse(event.data);
        await this.handleMessage(server, data);
      } catch (error) {
        server.send(JSON.stringify({ 
          type: 'error', 
          message: 'Invalid message format' 
        }));
      }
    });
    
    server.addEventListener('close', () => {
      this.connections.delete(server);
    });
    
    return new Response(null, {
      status: 101,
      webSocket: client
    });
  }

  async handleMessage(connection, data) {
    switch (data.type) {
      case 'ping':
        connection.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
        break;
        
      case 'subscribe':
        // Handle subscription to specific channels
        connection.send(JSON.stringify({ 
          type: 'subscribed', 
          channel: data.channel 
        }));
        break;
        
      case 'unsubscribe':
        // Handle unsubscription
        connection.send(JSON.stringify({ 
          type: 'unsubscribed', 
          channel: data.channel 
        }));
        break;
        
      default:
        connection.send(JSON.stringify({ 
          type: 'error', 
          message: 'Unknown message type' 
        }));
    }
  }

  broadcast(message) {
    const data = JSON.stringify(message);
    for (const connection of this.connections) {
      try {
        connection.send(data);
      } catch (error) {
        this.connections.delete(connection);
      }
    }
  }
}