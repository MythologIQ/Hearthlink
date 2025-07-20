#!/usr/bin/env node

/**
 * Cross-Platform Hearthlink Launcher
 * Detects environment and uses appropriate launch strategy
 */

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Security: Input validation for process arguments
function validateCommand(cmd) {
  if (!cmd || typeof cmd !== 'string') {
    throw new Error('Invalid command');
  }
  // Remove dangerous characters
  return cmd.replace(/[;&|`$()]/g, '');
}

// Environment detection
function detectEnvironment() {
  const platform = process.platform;
  const isWSL = fs.existsSync('/proc/version') && 
                fs.readFileSync('/proc/version', 'utf8').toLowerCase().includes('microsoft');
  
  return {
    platform,
    isWSL,
    isWindows: platform === 'win32' || isWSL,
    isLinux: platform === 'linux' && !isWSL,
    isMacOS: platform === 'darwin'
  };
}

// Cross-platform command execution
function executeCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const env = detectEnvironment();
    let actualCommand = command;
    let actualArgs = args;
    
    // Adjust command for environment
    if (env.isWSL && command.endsWith('.bat')) {
      actualCommand = 'cmd.exe';
      actualArgs = ['/c', command, ...args];
    } else if (env.isWindows && !command.includes('.')) {
      actualCommand = command + '.cmd';
    }
    
    console.log(`[LAUNCHER] Environment: ${JSON.stringify(env)}`);
    console.log(`[LAUNCHER] Executing: ${actualCommand} ${actualArgs.join(' ')}`);
    
    const child = spawn(actualCommand, actualArgs, {
      stdio: 'inherit',
      shell: env.isWindows,
      ...options
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve(code);
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });
    
    child.on('error', reject);
  });
}

// Main launcher logic
async function launch() {
  try {
    console.log('========================================');
    console.log('HEARTHLINK CROSS-PLATFORM LAUNCHER');
    console.log('========================================');
    
    const env = detectEnvironment();
    const projectDir = __dirname;
    
    console.log(`[LAUNCHER] Detected environment: ${env.platform} (WSL: ${env.isWSL})`);
    console.log(`[LAUNCHER] Project directory: ${projectDir}`);
    
    // Check if build exists
    const buildPath = path.join(projectDir, 'build');
    const packageJsonPath = path.join(projectDir, 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
      throw new Error('package.json not found. Are you in the project directory?');
    }
    
    // Strategy 1: Try npm run launch (if not in problematic WSL->Windows npm scenario)
    if (!env.isWSL) {
      console.log('[LAUNCHER] Attempting npm run launch...');
      try {
        await executeCommand('npm', ['run', 'launch'], { cwd: projectDir });
        console.log('[LAUNCHER] ✅ Success with npm run launch');
        return;
      } catch (error) {
        console.log(`[LAUNCHER] npm run launch failed: ${error.message}`);
      }
    }
    
    // Strategy 2: Direct build and launch
    console.log('[LAUNCHER] Attempting direct build and launch...');
    
    if (!fs.existsSync(buildPath)) {
      console.log('[LAUNCHER] Build directory missing, running build...');
      try {
        if (env.isWSL) {
          // Use Windows npm from WSL
          await executeCommand('cmd.exe', ['/c', 'npm', 'run', 'build'], { cwd: projectDir });
        } else {
          await executeCommand('npm', ['run', 'build'], { cwd: projectDir });
        }
      } catch (buildError) {
        console.log(`[LAUNCHER] Build failed: ${buildError.message}`);
      }
    }
    
    // Strategy 3: Emergency file protocol launch
    console.log('[LAUNCHER] Attempting emergency file protocol launch...');
    
    if (fs.existsSync(path.join(buildPath, 'index.html'))) {
      const fileUrl = `file://${path.resolve(buildPath, 'index.html')}`;
      console.log(`[LAUNCHER] Opening: ${fileUrl}`);
      
      if (env.isWindows || env.isWSL) {
        await executeCommand('cmd.exe', ['/c', 'start', '""', fileUrl]);
      } else if (env.isMacOS) {
        await executeCommand('open', [fileUrl]);
      } else {
        await executeCommand('xdg-open', [fileUrl]);
      }
      
      console.log('[LAUNCHER] ✅ Launched via file protocol');
      return;
    }
    
    // Strategy 4: Fallback test page
    console.log('[LAUNCHER] Attempting fallback test page...');
    const testPath = path.join(projectDir, 'public', 'test.html');
    
    if (fs.existsSync(testPath)) {
      const testUrl = `file://${path.resolve(testPath)}`;
      console.log(`[LAUNCHER] Opening test page: ${testUrl}`);
      
      if (env.isWindows || env.isWSL) {
        await executeCommand('cmd.exe', ['/c', 'start', '""', testUrl]);
      } else if (env.isMacOS) {
        await executeCommand('open', [testUrl]);
      } else {
        await executeCommand('xdg-open', [testUrl]);
      }
      
      console.log('[LAUNCHER] ✅ Launched fallback test page');
      return;
    }
    
    throw new Error('All launch strategies failed');
    
  } catch (error) {
    console.error('[LAUNCHER] ❌ Launch failed:', error.message);
    
    // Provide troubleshooting information
    console.log('\n[TROUBLESHOOTING] Suggestions:');
    console.log('1. Run "npm install" to ensure dependencies are installed');
    console.log('2. Run "npm run build" to create the build directory');
    console.log('3. Check that you have the correct permissions');
    console.log('4. Try running from Windows Command Prompt instead of WSL');
    
    process.exit(1);
  }
}

// CLI interface
if (require.main === module) {
  launch().catch(console.error);
}

module.exports = { launch, detectEnvironment, executeCommand };