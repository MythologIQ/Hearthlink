#!/usr/bin/env node

/**
 * Alternative Portable Executable Creator
 * Creates a simple executable package for Hearthlink
 */

const fs = require('fs');
const path = require('path');

console.log('🚀 Creating Hearthlink Portable Executable...');

// Create a self-contained executable script
const executableContent = `#!/usr/bin/env node

/**
 * Hearthlink Portable Executable v1.3.0
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

// Launch the main application
const isWindows = os.platform() === 'win32';
const nodeCmd = isWindows ? 'node.exe' : 'node';
const launcherPath = path.join(appDir, 'launcher.js');

// Check if launcher exists
if (!require('fs').existsSync(launcherPath)) {
  console.error('❌ Error: launcher.js not found in', appDir);
  console.log('Please ensure all Hearthlink files are in the same directory as this executable.');
  process.exit(1);
}

console.log('✅ Starting Hearthlink launcher...');

const child = spawn(nodeCmd, [launcherPath], {
  stdio: 'inherit',
  cwd: appDir
});

child.on('error', (error) => {
  console.error('❌ Error starting Hearthlink:', error.message);
  console.log('Please ensure Node.js is installed on your system.');
  process.exit(1);
});

child.on('exit', (code) => {
  console.log(\`Hearthlink exited with code \${code}\`);
  process.exit(code);
});
`;

// Write the portable executable
const executablePath = path.join(__dirname, 'hearthlink.exe');
fs.writeFileSync(executablePath, executableContent);

console.log('✅ Portable executable created: hearthlink.exe');

// Create a batch file for Windows users
const batchContent = `@echo off
title Hearthlink - Advanced AI Orchestration Platform
echo ⚡ HEARTHLINK v1.3.0
echo Advanced AI Orchestration Platform
echo.
echo Starting application...
node "%~dp0launcher.js"
pause`;

fs.writeFileSync(path.join(__dirname, 'hearthlink.bat'), batchContent);

console.log('✅ Windows batch file created: hearthlink.bat');

// Create a shell script for Unix-like systems  
const shellContent = `#!/bin/bash
echo "⚡ HEARTHLINK v1.3.0"
echo "Advanced AI Orchestration Platform"
echo ""
echo "Starting application..."
DIR="$(cd "$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
node "$DIR/launcher.js"`;

fs.writeFileSync(path.join(__dirname, 'hearthlink.sh'), shellContent);

console.log('✅ Unix shell script created: hearthlink.sh');

console.log('');
console.log('🎉 Hearthlink executable package created successfully!');
console.log('');
console.log('📂 Files created:');
console.log('   • hearthlink.exe   (Node.js executable)');
console.log('   • hearthlink.bat   (Windows batch file)');
console.log('   • hearthlink.sh    (Unix shell script)');
console.log('');
console.log('🚀 To run Hearthlink:');
console.log('   Windows: double-click hearthlink.bat or run "node hearthlink.exe"');
console.log('   Linux/Mac: ./hearthlink.sh or node hearthlink.exe');
console.log('');
console.log('✅ Hearthlink is ready to launch!');