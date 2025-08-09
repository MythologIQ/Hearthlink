#!/usr/bin/env node

/**
 * Hearthlink Portable Launcher v1.3.0
 * Advanced AI Orchestration Platform
 */

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

console.log('⚡ HEARTHLINK v1.3.0');
console.log('Advanced AI Orchestration Platform');
console.log('Starting application...');

// Get the directory where this executable is located
const appDir = path.dirname(process.execPath || __dirname);

// Launch using npm run launch for proper Electron integration
const isWindows = os.platform() === 'win32';
const npmCmd = isWindows ? 'npm.cmd' : 'npm';

console.log('✅ Starting Hearthlink with enhanced port management...');

const child = spawn(npmCmd, ['run', 'launch'], {
  stdio: 'inherit',
  cwd: appDir,
  shell: true
});

child.on('error', (error) => {
  console.error('❌ Error starting Hearthlink:', error.message);
  console.log('Please ensure Node.js and npm are installed on your system.');
  console.log('Alternative: Try running "npm run launch" manually');
  process.exit(1);
});

child.on('exit', (code) => {
  console.log(`Hearthlink exited with code ${code}`);
  process.exit(code);
});