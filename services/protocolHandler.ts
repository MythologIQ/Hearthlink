const { protocol } = require('electron');
const path = require('path');
const fs = require('fs').promises;

// Cache for file existence checks
const existsCache = new Map();
const CACHE_TTL = 5000; // 5 seconds

function getCachedExists(filePath) {
  const cached = existsCache.get(filePath);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.exists;
  }
  return null;
}

function setCachedExists(filePath, exists) {
  existsCache.set(filePath, {
    exists,
    timestamp: Date.now()
  });
}

async function checkFileExists(filePath) {
  const cached = getCachedExists(filePath);
  if (cached !== null) return cached;
  
  try {
    await fs.access(filePath);
    setCachedExists(filePath, true);
    return true;
  } catch {
    setCachedExists(filePath, false);
    return false;
  }
}

// Protocol handler for serving static files
function setupProtocolHandler() {
  protocol.registerFileProtocol('app', async (request, callback) => {
    try {
      const url = request.url.substr(6); // Remove 'app://' prefix
      const filePath = path.normalize(path.join(__dirname, '..', 'build', url));
      
      // Security: Ensure the file is within the build directory
      const buildPath = path.resolve(path.join(__dirname, '..', 'build'));
      const resolvedPath = path.resolve(filePath);
      
      if (!resolvedPath.startsWith(buildPath)) {
        console.error('Security violation: Attempted to access file outside build directory:', filePath);
        callback({ error: 403 });
        return;
      }
      
      // Check if file exists with caching
      const exists = await checkFileExists(filePath);
      if (!exists) {
        console.error('File not found:', filePath);
        callback({ error: 404 });
        return;
      }
      
      callback({ path: filePath });
    } catch (error) {
      console.error('Protocol handler error:', error);
      callback({ error: 500 });
    }
  });
}

module.exports = {
  setupProtocolHandler
};