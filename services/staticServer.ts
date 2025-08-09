export {}
const http = require('http');
const path = require('path');
const fs = require('fs').promises;
const url = require('url');

let staticServer = null;

// Cache for file stats to avoid repeated fs calls
const statCache = new Map();
const CACHE_TTL = 5000; // 5 seconds

function getCachedStat(filePath) {
  const cached = statCache.get(filePath);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.stats;
  }
  return null;
}

function setCachedStat(filePath, stats) {
  statCache.set(filePath, {
    stats,
    timestamp: Date.now()
  });
}

async function checkFileExists(filePath) {
  try {
    const cached = getCachedStat(filePath);
    if (cached) return cached;
    
    const stats = await fs.stat(filePath);
    setCachedStat(filePath, stats);
    return stats;
  } catch {
    return null;
  }
}

// Lightweight static server with security and caching
function startStaticServer() {
  return new Promise((resolve, reject) => {
    const buildPath = path.join(__dirname, '..', 'build');
    const port = 3008;
    
    staticServer = http.createServer(async (req, res) => {
      try {
        const parsedUrl = url.parse(req.url);
        let filePath = path.join(buildPath, parsedUrl.pathname);
        
        // Security: Ensure the file is within the build directory
        const resolvedPath = path.resolve(filePath);
        const resolvedBuildPath = path.resolve(buildPath);
        
        if (!resolvedPath.startsWith(resolvedBuildPath)) {
          res.writeHead(403, { 'Content-Type': 'text/plain' });
          res.end('Forbidden');
          return;
        }
        
        // Check if file exists
        const stats = await checkFileExists(filePath);
        if (!stats) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('File not found');
          return;
        }
        
        // Handle directory requests
        if (stats.isDirectory()) {
          filePath = path.join(filePath, 'index.html');
          const indexStats = await checkFileExists(filePath);
          if (!indexStats) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('Index file not found');
            return;
          }
        }
        
        // Set appropriate content type
        const ext = path.extname(filePath).toLowerCase();
        const contentTypes = {
          '.html': 'text/html',
          '.css': 'text/css',
          '.js': 'application/javascript',
          '.json': 'application/json',
          '.png': 'image/png',
          '.jpg': 'image/jpeg',
          '.jpeg': 'image/jpeg',
          '.gif': 'image/gif',
          '.svg': 'image/svg+xml',
          '.ico': 'image/x-icon',
          '.woff': 'font/woff',
          '.woff2': 'font/woff2',
          '.ttf': 'font/ttf',
          '.eot': 'application/vnd.ms-fontobject'
        };
        
        const contentType = contentTypes[ext] || 'application/octet-stream';
        
        // Security headers
        res.setHeader('Content-Type', contentType);
        res.setHeader('X-Content-Type-Options', 'nosniff');
        res.setHeader('X-Frame-Options', 'DENY');
        res.setHeader('X-XSS-Protection', '1; mode=block');
        
        // Localhost-only when packaged
        const { app } = require('electron');
        if (app?.isPackaged) {
          res.setHeader('Access-Control-Allow-Origin', 'localhost');
        }
        
        // Stream the file
        const stream = fs.createReadStream(filePath);
        stream.pipe(res);
        
        stream.on('error', (error) => {
          console.error('Static server error:', error);
          if (!res.headersSent) {
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end('Internal server error');
          }
        });
        
      } catch (error) {
        console.error('Static server error:', error);
        if (!res.headersSent) {
          res.writeHead(500, { 'Content-Type': 'text/plain' });
          res.end('Internal server error');
        }
      }
    });
    
    staticServer.listen(port, '127.0.0.1', () => {
      resolve(port);
    });
    
    staticServer.on('error', (error) => {
      console.error('Static server failed to start:', error);
      reject(error);
    });
  });
}

function stopStaticServer() {
  if (staticServer) {
    staticServer.close();
    staticServer = null;
  }
}

module.exports = {
  startStaticServer,
  stopStaticServer
};export {}
