#!/usr/bin/env node

/**
 * Hearthlink Native Wrapper Status Checker
 * 
 * Simple utility to check if the native wrapper is running
 */

const fs = require('fs');
const path = require('path');

const pidFile = path.join(__dirname, 'userData', 'native-wrapper.pid');
const logFile = path.join(__dirname, 'userData', 'logs', 'native-wrapper.log');

function checkWrapperStatus() {
    console.log('🔍 Checking Hearthlink Native Wrapper Status...\n');
    
    // Check if PID file exists
    if (!fs.existsSync(pidFile)) {
        console.log('❌ Native wrapper is not running (no PID file found)');
        return false;
    }
    
    // Read PID
    let pid;
    try {
        pid = parseInt(fs.readFileSync(pidFile, 'utf8').trim());
    } catch (error) {
        console.log('❌ Failed to read PID file:', error.message);
        return false;
    }
    
    // Check if process is running
    try {
        process.kill(pid, 0); // Signal 0 checks if process exists
        console.log('✅ Native wrapper is running');
        console.log(`   PID: ${pid}`);
        
        // Check log file for recent activity
        if (fs.existsSync(logFile)) {
            const stats = fs.statSync(logFile);
            const lastModified = stats.mtime;
            const now = new Date();
            const timeDiff = now - lastModified;
            
            console.log(`   Log file last updated: ${lastModified.toLocaleString()}`);
            
            if (timeDiff < 60000) { // Less than 1 minute ago
                console.log('✅ Wrapper appears to be actively running');
            } else {
                console.log('⚠️  Wrapper may be idle (no recent log activity)');
            }
            
            // Show last few log entries
            try {
                const logContent = fs.readFileSync(logFile, 'utf8');
                const lines = logContent.split('\n').filter(line => line.trim());
                const recentLines = lines.slice(-5);
                
                console.log('\n📋 Recent log entries:');
                recentLines.forEach(line => {
                    if (line.trim()) {
                        try {
                            const logEntry = JSON.parse(line);
                            console.log(`   ${logEntry.timestamp} [${logEntry.level.toUpperCase()}] ${logEntry.message}`);
                        } catch (parseError) {
                            console.log(`   ${line}`);
                        }
                    }
                });
            } catch (logError) {
                console.log('⚠️  Could not read recent log entries');
            }
        } else {
            console.log('⚠️  Log file not found');
        }
        
        return true;
    } catch (error) {
        console.log('❌ Native wrapper process is not running');
        console.log(`   PID ${pid} not found`);
        
        // Clean up stale PID file
        try {
            fs.unlinkSync(pidFile);
            console.log('🧹 Cleaned up stale PID file');
        } catch (cleanupError) {
            console.log('⚠️  Failed to cleanup PID file');
        }
        
        return false;
    }
}

function showUsage() {
    console.log(`
Hearthlink Native Wrapper Status Checker

Usage: node check-native-status.js

This tool checks if the native wrapper is currently running and shows
recent activity from the log files.
`);
}

// Main execution
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.includes('--help') || args.includes('-h')) {
        showUsage();
        process.exit(0);
    }
    
    const isRunning = checkWrapperStatus();
    process.exit(isRunning ? 0 : 1);
}

module.exports = checkWrapperStatus;