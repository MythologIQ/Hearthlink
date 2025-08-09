/**
 * Hearthlink Workers API - Simplified Version
 * 
 * Minimal working API for quick deployment and testing
 */

import { Router } from 'itty-router';

// Initialize router
const router = Router();

// CORS headers
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// Helper to create JSON responses with CORS
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders,
    },
  });
}

// Handle CORS preflight requests
router.options('*', () => new Response(null, { status: 200, headers: corsHeaders }));

// Health check endpoint
router.get('/api/v1/health', () => {
  return jsonResponse({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'Hearthlink Workers API',
    version: '1.0.0',
    environment: 'development'
  });
});

// Basic info endpoint
router.get('/api/v1/info', () => {
  return jsonResponse({
    service: 'Hearthlink Workers API',
    version: '1.0.0',
    description: 'Secure, globally distributed REST API for Hearthlink AI orchestration',
    endpoints: [
      'GET /api/v1/health - Health check',
      'GET /api/v1/info - API information',
      'GET /api/v1/agents - List available agents',
      'POST /api/v1/auth/login - User authentication'
    ]
  });
});

// List agents endpoint  
router.get('/api/v1/agents', () => {
  return jsonResponse({
    agents: [
      {
        id: 'alden',
        name: 'ALDEN',
        description: 'Primary AI assistant and productivity companion',
        status: 'available',
        capabilities: ['conversation', 'task-management', 'productivity']
      },
      {
        id: 'alice',
        name: 'ALICE', 
        description: 'Cognitive-behavioral analysis agent',
        status: 'available',
        capabilities: ['analysis', 'behavioral-insights', 'recommendations']
      },
      {
        id: 'superclaude',
        name: 'SuperClaude',
        description: 'Advanced Claude integration with enhanced capabilities',
        status: 'available', 
        capabilities: ['advanced-reasoning', 'code-analysis', 'research']
      }
    ],
    total: 3,
    timestamp: new Date().toISOString()
  });
});

// Basic authentication endpoint (mock for now)
router.post('/api/v1/auth/login', async (request) => {
  try {
    const body = await request.json();
    const { username, password } = body;
    
    // Mock authentication - replace with real auth
    if (username && password) {
      return jsonResponse({
        success: true,
        message: 'Authentication successful',
        token: 'mock-jwt-token-' + Date.now(),
        user: {
          id: 'user_' + Date.now(),
          username: username,
          role: 'user'
        },
        expiresIn: '24h'
      });
    } else {
      return jsonResponse({
        success: false,
        message: 'Username and password required'
      }, 400);
    }
  } catch (error) {
    return jsonResponse({
      success: false,
      message: 'Invalid request body'
    }, 400);
  }
});

// Root endpoint
router.get('/', () => {
  return jsonResponse({
    message: 'Welcome to Hearthlink Workers API',
    version: '1.0.0',
    documentation: '/api/v1/info',
    health: '/api/v1/health'
  });
});

// 404 handler
router.all('*', () => {
  return jsonResponse({
    error: 'Not Found',
    message: 'The requested endpoint does not exist',
    available_endpoints: ['/api/v1/health', '/api/v1/info', '/api/v1/agents']
  }, 404);
});

// Main worker handler
export default {
  async fetch(request, env, ctx) {
    try {
      return await router.handle(request, env, ctx);
    } catch (error) {
      console.error('Worker error:', error);
      return jsonResponse({
        error: 'Internal Server Error',
        message: 'An unexpected error occurred',
        timestamp: new Date().toISOString()
      }, 500);
    }
  },
};