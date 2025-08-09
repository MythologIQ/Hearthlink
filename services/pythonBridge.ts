export {}
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let pythonProcess = null;
let pythonReadyPromise = null;

// Validate Python executable path for security
function validatePythonPath(pythonPath) {
  if (!pythonPath || typeof pythonPath !== 'string') {
    throw new Error('Invalid Python path');
  }
  
  // Remove any command injection attempts
  const sanitized = pythonPath.replace(/[;&|`$(){}[\]]/g, '');
  
  // Use environment-based allowlist instead of hard-coded paths
  const envAllowedPaths = process.env.PYTHON_ALLOWED_PATHS?.split(';') || [];
  const defaultAllowedPaths = [
    'python',
    'python3',
    'python3.8',
    'python3.9',
    'python3.10',
    'python3.11',
    'python3.12',
    'python3.13'
  ];
  
  const allowedPythonPaths = [...defaultAllowedPaths, ...envAllowedPaths];
  
  // Check if it's a whitelisted name or verify with which/where
  const isAllowed = allowedPythonPaths.some(allowed => 
    sanitized === allowed || 
    (allowed.includes(path.sep) && sanitized.startsWith(allowed.substring(0, allowed.lastIndexOf(path.sep))))
  );
  
  if (!isAllowed && !path.isAbsolute(sanitized)) {
    throw new Error('Python path not in whitelist');
  }
  
  return sanitized;
}

// Start Python backend process with security validation
function startPythonBackend() {
  return new Promise((resolve, reject) => {
    try {
      const rawPythonPath = process.env.PYTHON_PATH || 'python';
      const pythonPath = validatePythonPath(rawPythonPath);
      const backendScript = path.join(__dirname, '..', 'src', 'main.py');
      
      // Verify backend script exists and is within project directory
      const projectDir = path.resolve(__dirname, '..');
      const scriptPath = path.resolve(backendScript);
      if (!scriptPath.startsWith(projectDir)) {
        throw new Error('Backend script path traversal blocked');
      }
      
      if (!fs.existsSync(backendScript)) {
        throw new Error('Backend script not found');
      }
      
      console.log('[SECURITY] Starting Python backend:', pythonPath, backendScript);
      
      pythonProcess = spawn(pythonPath, [backendScript, '--ipc'], {
        cwd: path.join(__dirname, '..'),
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { 
          ...process.env, 
          PYTHONPATH: path.join(__dirname, '..', 'src'),
          // Clear potentially dangerous environment variables
          LD_PRELOAD: undefined,
          LD_LIBRARY_PATH: undefined
        }
      });
    } catch (error) {
      console.error('[SECURITY] Python backend validation failed:', error.message);
      reject(error);
      return;
    }
    
    let initBuffer = '';
    
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      initBuffer += output;
      
      // Check for initialization complete signal
      if (initBuffer.includes('HEARTHLINK_READY')) {
        resolve(true);
      }
    });
    
    pythonProcess.stderr.on('data', (data) => {
      console.error('Python error:', data.toString());
    });
    
    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python backend:', error);
      reject(error);
    });
    
    pythonProcess.on('close', (code) => {
      pythonProcess = null;
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      if (!pythonProcess?.killed) {
        reject(new Error('Python backend startup timeout'));
      }
    }, 10000);
  });
}

function sendToPython(command) {
  return new Promise((resolve, reject) => {
    if (!pythonProcess) {
      reject(new Error('Python backend not running'));
      return;
    }
    
    const message = JSON.stringify(command) + '\n';
    pythonProcess.stdin.write(message);
    
    // Listen for response
    const timeout = setTimeout(() => {
      reject(new Error('Python backend response timeout'));
    }, 5000);
    
    const responseHandler = (data) => {
      try {
        const response = JSON.parse(data.toString());
        if (response.id === command.id) {
          clearTimeout(timeout);
          pythonProcess.stdout.removeListener('data', responseHandler);
          resolve(response);
        }
      } catch (error) {
        // Continue listening for valid JSON
      }
    };
    
    pythonProcess.stdout.on('data', responseHandler);
  });
}

function stopPythonBackend() {
  if (pythonProcess) {
    pythonProcess.kill();
    pythonProcess = null;
  }
}

function getPythonProcess() {
  return pythonProcess;
}

module.exports = {
  startPythonBackend,
  sendToPython,
  stopPythonBackend,
  getPythonProcess
};export {}
