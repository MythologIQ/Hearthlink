#!/usr/bin/env node

const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Hearthlink Clean Startup Script');
console.log('===================================');
console.log();

// Function to check if port is available
function checkPort(port) {
    return new Promise((resolve) => {
        const net = require('net');
        const tester = net.createServer()
            .once('error', () => resolve(false))
            .once('listening', () => tester.once('close', () => resolve(true)).close())
            .listen(port, '127.0.0.1');
    });
}

// Function to find available port starting from a base port
async function findAvailablePort(basePort, maxAttempts = 10) {
    for (let i = 0; i < maxAttempts; i++) {
        const port = basePort + i;
        const available = await checkPort(port);
        if (available) {
            return port;
        }
    }
    throw new Error(`No available port found starting from ${basePort}`);
}

// Function to start process with better error handling
function startProcess(command, args, options = {}) {
    return new Promise((resolve, reject) => {
        console.log(`📦 Starting: ${command} ${args.join(' ')}`);
        
        const child = spawn(command, args, {
            stdio: 'inherit',
            shell: true,
            cwd: process.cwd(),
            ...options
        });

        child.on('error', (error) => {
            console.error(`❌ Failed to start ${command}:`, error.message);
            reject(error);
        });

        child.on('exit', (code) => {
            if (code === 0) {
                console.log(`✅ ${command} completed successfully`);
                resolve(code);
            } else {
                console.log(`⚠️  ${command} exited with code ${code}`);
                resolve(code);
            }
        });

        // Give the process a moment to start
        setTimeout(() => {
            if (!child.killed) {
                resolve(child);
            }
        }, 2000);
    });
}

async function main() {
    try {
        console.log('🔍 Checking port availability...');
        
        // Check critical ports
        const ports = [3000, 3001, 3008, 8000, 8001];
        const portStatus = {};
        
        for (const port of ports) {
            const available = await checkPort(port);
            portStatus[port] = available;
            console.log(`Port ${port}: ${available ? '🟢 Available' : '🔴 In Use'}`);
        }
        
        // Find available port for static server if 3001/3008 are taken
        let staticPort = 3001;
        if (!portStatus[3001]) {
            if (!portStatus[3008]) {
                staticPort = await findAvailablePort(3010);
                console.log(`📡 Using alternative static port: ${staticPort}`);
            } else {
                staticPort = 3008;
            }
        }
        
        console.log();
        console.log('🛠️  Starting Hearthlink services...');
        console.log();
        
        // Method 1: Try npm start (recommended)
        if (portStatus[3000]) {
            console.log('🎯 Method 1: Using npm start...');
            try {
                await startProcess('npm', ['start'], { timeout: 30000 });
            } catch (error) {
                console.log('⚠️  npm start failed, trying alternative method...');
                console.log();
                
                // Method 2: Start React dev server manually
                console.log('🎯 Method 2: Starting React dev server manually...');
                const reactServer = spawn('npm', ['run', 'start:react'], {
                    stdio: 'inherit',
                    shell: true,
                    detached: true
                });
                
                console.log('⏳ Waiting for React to start...');
                await new Promise(resolve => setTimeout(resolve, 5000));
                
                // Method 3: Start Electron
                console.log('🎯 Method 3: Starting Electron...');
                await startProcess('npm', ['run', 'start:electron']);
            }
        } else {
            console.log('❌ Port 3000 is in use. Please run the port cleanup script first:');
            console.log('   bash fix-port-conflict.sh');
            process.exit(1);
        }
        
    } catch (error) {
        console.error('❌ Startup failed:', error.message);
        console.log();
        console.log('🔧 Troubleshooting suggestions:');
        console.log('1. Run: bash fix-port-conflict.sh');
        console.log('2. Check: bash check-ports.sh');
        console.log('3. Manual start: npm run build && npm run start:electron');
        process.exit(1);
    }
}

// Handle cleanup on exit
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down Hearthlink...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down Hearthlink...');
    process.exit(0);
});

main().catch(console.error);