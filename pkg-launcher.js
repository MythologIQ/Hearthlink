#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

console.log('⚡ HEARTHLINK v1.3.0');
console.log('Advanced AI Orchestration Platform');
console.log('');

const isWindows = os.platform() === 'win32';
const npmCmd = isWindows ? 'npm.cmd' : 'npm';

console.log('Starting Hearthlink...');

const child = spawn(npmCmd, ['run', 'launch'], {
  stdio: 'inherit',
  shell: true,
  cwd: __dirname
});

child.on('error', (error) => {
  console.error('Error:', error.message);
  console.log('Please ensure Node.js and npm are installed.');
  console.log('Alternative: Run "npm run launch" manually');
  process.exit(1);
});
