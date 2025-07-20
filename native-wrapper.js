#!/usr/bin/env node

/**
 * Hearthlink Native Wrapper
 * 
 * A persistent native application wrapper that manages the Electron app lifecycle
 * and provides system tray integration for Hearthlink.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

class HearthlinkNativeWrapper {
    constructor() {
        this.electronProcess = null;
        this.isRunning = false;
        this.restartCount = 0;
        this.maxRestarts = 5;
        this.logFile = path.join(__dirname, 'userData', 'logs', 'native-wrapper.log');
        this.pidFile = path.join(__dirname, 'userData', 'native-wrapper.pid');
        
        this.ensureDirectories();
        this.setupSignalHandlers();
        this.writePidFile();
    }

    ensureDirectories() {
        const logDir = path.dirname(this.logFile);
        if (!fs.existsSync(logDir)) {
            fs.mkdirSync(logDir, { recursive: true });
        }
        
        const pidDir = path.dirname(this.pidFile);
        if (!fs.existsSync(pidDir)) {
            fs.mkdirSync(pidDir, { recursive: true });
        }
    }

    log(level, message, meta = {}) {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            message,
            pid: process.pid,
            ...meta
        };
        
        const logLine = JSON.stringify(logEntry) + '\n';
        
        // Console output
        console.log(`[${timestamp}] ${level.toUpperCase()}: ${message}`);
        
        // File output
        try {
            fs.appendFileSync(this.logFile, logLine);
        } catch (error) {
            console.error('Failed to write to log file:', error.message);
        }
    }

    info(message, meta) { this.log('info', message, meta); }
    warn(message, meta) { this.log('warn', message, meta); }
    error(message, meta) { this.log('error', message, meta); }

    writePidFile() {
        try {
            fs.writeFileSync(this.pidFile, process.pid.toString());
        } catch (error) {
            this.error('Failed to write PID file', { error: error.message });
        }
    }

    cleanupPidFile() {
        try {
            if (fs.existsSync(this.pidFile)) {
                fs.unlinkSync(this.pidFile);
            }
        } catch (error) {
            this.error('Failed to cleanup PID file', { error: error.message });
        }
    }

    setupSignalHandlers() {
        process.on('SIGINT', () => {
            this.info('Received SIGINT, shutting down gracefully...');
            this.shutdown();
        });

        process.on('SIGTERM', () => {
            this.info('Received SIGTERM, shutting down gracefully...');
            this.shutdown();
        });

        process.on('exit', () => {
            this.cleanupPidFile();
        });
    }

    async startElectronApp() {
        if (this.isRunning) {
            this.warn('Electron app is already running');
            return;
        }

        try {
            this.info('Starting Electron application...');
            
            let spawnOptions = {
                cwd: __dirname,
                stdio: ['pipe', 'pipe', 'pipe'],
                detached: false
            };

            let electronCmd, electronArgs;
            
            if (os.platform() === 'win32') {
                electronCmd = 'cmd';
                electronArgs = ['/c', 'npm', 'run', 'launch'];
                spawnOptions.shell = true;
            } else {
                electronCmd = 'npm';
                electronArgs = ['run', 'launch'];
            }
            
            this.electronProcess = spawn(electronCmd, electronArgs, spawnOptions);

            this.isRunning = true;
            this.restartCount = 0;

            this.electronProcess.stdout.on('data', (data) => {
                this.info('Electron stdout', { data: data.toString().trim() });
            });

            this.electronProcess.stderr.on('data', (data) => {
                this.error('Electron stderr', { data: data.toString().trim() });
            });

            this.electronProcess.on('exit', (code, signal) => {
                this.isRunning = false;
                this.info('Electron process exited', { code, signal });
                
                if (code !== 0 && this.restartCount < this.maxRestarts) {
                    this.warn(`Electron crashed, attempting restart ${this.restartCount + 1}/${this.maxRestarts}`);
                    this.restartCount++;
                    setTimeout(() => this.startElectronApp(), 5000);
                } else if (this.restartCount >= this.maxRestarts) {
                    this.error('Maximum restart attempts reached, stopping automatic restarts');
                }
            });

            this.electronProcess.on('error', (error) => {
                this.isRunning = false;
                this.error('Failed to start Electron process', { error: error.message });
                
                // Try fallback method
                this.tryFallbackLaunch();
            });

            this.info('Electron application started successfully', { pid: this.electronProcess.pid });
        } catch (error) {
            this.isRunning = false;
            this.error('Failed to start Electron application', { error: error.message });
            
            // Try fallback method
            this.tryFallbackLaunch();
        }
    }

    async tryFallbackLaunch() {
        this.info('Attempting fallback launch method...');
        
        try {
            let spawnOptions = {
                cwd: __dirname,
                stdio: ['pipe', 'pipe', 'pipe'],
                detached: false
            };

            let electronCmd, electronArgs;
            
            if (os.platform() === 'win32') {
                // Try direct electron execution on Windows
                electronCmd = 'npx';
                electronArgs = ['electron', 'launcher.js'];
                spawnOptions.shell = true;
            } else {
                // Try direct electron execution on Unix
                electronCmd = 'npx';
                electronArgs = ['electron', 'launcher.js'];
            }
            
            this.electronProcess = spawn(electronCmd, electronArgs, spawnOptions);
            this.isRunning = true;
            this.restartCount = 0;

            this.electronProcess.stdout.on('data', (data) => {
                this.info('Electron fallback stdout', { data: data.toString().trim() });
            });

            this.electronProcess.stderr.on('data', (data) => {
                this.error('Electron fallback stderr', { data: data.toString().trim() });
            });

            this.electronProcess.on('exit', (code, signal) => {
                this.isRunning = false;
                this.info('Electron fallback process exited', { code, signal });
            });

            this.electronProcess.on('error', (error) => {
                this.isRunning = false;
                this.error('Fallback launch also failed', { error: error.message });
            });

            this.info('Fallback launch successful', { pid: this.electronProcess.pid });
        } catch (error) {
            this.error('Fallback launch failed', { error: error.message });
        }
    }

    async stopElectronApp() {
        if (!this.isRunning || !this.electronProcess) {
            this.warn('Electron app is not running');
            return;
        }

        try {
            this.info('Stopping Electron application...');
            
            if (os.platform() === 'win32') {
                // On Windows, kill the process tree
                try {
                    spawn('taskkill', ['/pid', this.electronProcess.pid, '/t', '/f'], { 
                        stdio: 'ignore',
                        shell: true 
                    });
                } catch (killError) {
                    this.warn('Failed to use taskkill, trying process.kill', { error: killError.message });
                    this.electronProcess.kill('SIGTERM');
                }
            } else {
                // On Unix-like systems, send SIGTERM
                this.electronProcess.kill('SIGTERM');
            }

            // Wait for graceful shutdown
            setTimeout(() => {
                if (this.isRunning && this.electronProcess) {
                    this.warn('Force killing Electron process');
                    try {
                        this.electronProcess.kill('SIGKILL');
                    } catch (killError) {
                        this.warn('Failed to force kill process', { error: killError.message });
                    }
                }
            }, 5000);

            this.isRunning = false;
            this.info('Electron application stopped successfully');
        } catch (error) {
            this.error('Failed to stop Electron application', { error: error.message });
        }
    }

    async restartElectronApp() {
        this.info('Restarting Electron application...');
        await this.stopElectronApp();
        setTimeout(() => this.startElectronApp(), 2000);
    }

    getStatus() {
        return {
            isRunning: this.isRunning,
            pid: this.electronProcess?.pid || null,
            restartCount: this.restartCount,
            uptime: this.isRunning ? Date.now() - this.startTime : 0
        };
    }

    async shutdown() {
        this.info('Shutting down native wrapper...');
        
        if (this.isRunning) {
            await this.stopElectronApp();
        }
        
        this.cleanupPidFile();
        this.info('Native wrapper shutdown completed');
        process.exit(0);
    }

    async start() {
        this.info('Starting Hearthlink Native Wrapper', { 
            version: '1.3.0',
            platform: os.platform(),
            arch: os.arch(),
            nodeVersion: process.version
        });

        this.startTime = Date.now();
        
        // Auto-start Electron app
        await this.startElectronApp();
        
        // Keep the wrapper running
        this.info('Native wrapper is running and monitoring Electron app...');
        this.info('Press Ctrl+C to shutdown gracefully');
        
        // Keep alive
        setInterval(() => {
            // Health check every 30 seconds
            if (this.isRunning && this.electronProcess) {
                try {
                    // Check if process is still alive
                    process.kill(this.electronProcess.pid, 0);
                } catch (error) {
                    this.warn('Electron process appears to be dead, restarting...');
                    this.isRunning = false;
                    this.startElectronApp();
                }
            }
        }, 30000);
    }
}

// CLI Interface
if (require.main === module) {
    const wrapper = new HearthlinkNativeWrapper();
    
    const args = process.argv.slice(2);
    const command = args[0];
    
    switch (command) {
        case 'start':
            wrapper.start();
            break;
        case 'stop':
            // TODO: Implement stop command to communicate with running wrapper
            console.log('Stop command not implemented yet');
            break;
        case 'restart':
            // TODO: Implement restart command
            console.log('Restart command not implemented yet');
            break;
        case 'status':
            // TODO: Implement status command
            console.log('Status command not implemented yet');
            break;
        default:
            console.log(`
Hearthlink Native Wrapper v1.3.0

Usage: node native-wrapper.js [command]

Commands:
  start    Start the native wrapper and Electron app
  stop     Stop the native wrapper and Electron app
  restart  Restart the Electron app
  status   Show current status

If no command is provided, 'start' will be used by default.
`);
            if (!command) {
                wrapper.start();
            }
    }
}

module.exports = HearthlinkNativeWrapper;