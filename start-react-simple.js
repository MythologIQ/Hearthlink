#!/usr/bin/env node
/**
 * Simple React Start Script
 * Starts React on a specific port with fallback handling
 */

const { spawn } = require('child_process');

console.log('🚀 Starting React on port 3015...');

const reactProcess = spawn('npx', ['react-scripts', 'start'], {
    env: {
        ...process.env,
        PORT: '3015',
        BROWSER: 'none',
        GENERATE_SOURCEMAP: 'false'
    },
    stdio: 'inherit'
});

reactProcess.on('exit', (code) => {
    console.log(`React process exited with code ${code}`);
});

process.on('SIGINT', () => {
    console.log('\n🛑 Stopping React...');
    reactProcess.kill();
    process.exit(0);
});
