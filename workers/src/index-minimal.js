/**
 * Hearthlink Workers API - Minimal Test Version
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 200, headers: corsHeaders });
    }

    // JSON response helper
    function jsonResponse(data, status = 200) {
      return new Response(JSON.stringify(data, null, 2), {
        status,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders,
        },
      });
    }

    // Route handling
    const path = url.pathname;

    // Health check
    if (path === '/api/v1/health') {
      return jsonResponse({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'Hearthlink Workers API',
        version: '1.0.0',
        environment: env.ENVIRONMENT || 'development',
        worker_url: request.url
      });
    }

    // API info
    if (path === '/api/v1/info') {
      return jsonResponse({
        service: 'Hearthlink Workers API',
        version: '1.0.0',
        description: 'Secure, globally distributed REST API for Hearthlink AI orchestration',
        deployment: 'Cloudflare Workers',
        endpoints: [
          'GET /api/v1/health - Health check',
          'GET /api/v1/info - API information'
        ]
      });
    }

    // Root
    if (path === '/' || path === '') {
      return jsonResponse({
        message: 'Welcome to Hearthlink Workers API',
        version: '1.0.0',
        status: 'operational',
        documentation: '/api/v1/info',
        health: '/api/v1/health'
      });
    }

    // 404
    return jsonResponse({
      error: 'Not Found',
      message: 'The requested endpoint does not exist',
      path: path,
      available: ['/', '/api/v1/health', '/api/v1/info']
    }, 404);
  },
};