#!/usr/bin/env node

/**
 * Tauri Setup Verification Script
 * 
 * Verifies that all required tools and dependencies are properly installed
 * for Hearthlink Tauri native development and building.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class TauriVerifier {
    constructor() {
        this.projectRoot = path.resolve(__dirname, '..');
        this.checks = [];
        this.warnings = [];
        this.errors = [];
    }

    log(message, type = 'info') {
        const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
        const prefix = {
            info: '💡',
            success: '✅', 
            warning: '⚠️',
            error: '❌'
        }[type];
        
        console.log(`[${timestamp}] ${prefix} ${message}`);
        
        if (type === 'warning') this.warnings.push(message);
        if (type === 'error') this.errors.push(message);
    }

    async runCheck(name, checkFn) {
        try {
            this.log(`Checking ${name}...`);
            await checkFn();
            this.log(`${name} - OK`, 'success');
            this.checks.push({ name, status: 'ok' });
        } catch (error) {
            this.log(`${name} - ${error.message}`, 'error');
            this.checks.push({ name, status: 'error', error: error.message });
        }
    }

    checkCommand(command, expectedPattern, errorMessage) {
        try {
            const output = execSync(command, { encoding: 'utf8', stdio: 'pipe' });
            if (expectedPattern && !expectedPattern.test(output)) {
                throw new Error(`${errorMessage}: ${output.trim()}`);
            }
            return output.trim();
        } catch (error) {
            throw new Error(`${errorMessage}: ${error.message}`);
        }
    }

    async checkPython() {
        const pythonCommands = ['python', 'python3'];
        let pythonFound = false;
        
        for (const cmd of pythonCommands) {
            try {
                const version = this.checkCommand(`${cmd} --version`, /Python 3\.\d+/, null);
                this.log(`Found ${cmd}: ${version}`);
                pythonFound = true;
                
                // Check pip
                this.checkCommand(`${cmd} -m pip --version`, /pip/, `${cmd} pip not available`);
                break;
            } catch (error) {
                // Continue to next command
            }
        }
        
        if (!pythonFound) {
            throw new Error('Python 3.x not found. Install Python 3.11+ and ensure it\'s in PATH');
        }
    }

    async checkNode() {
        const nodeVersion = this.checkCommand('node --version', /v\d+\.\d+\.\d+/, 'Node.js not found');
        const npmVersion = this.checkCommand('npm --version', /\d+\.\d+\.\d+/, 'npm not found');
        
        this.log(`Node.js: ${nodeVersion}, npm: ${npmVersion}`);
        
        const majorVersion = parseInt(nodeVersion.replace('v', '').split('.')[0]);
        if (majorVersion < 18) {
            this.log('Node.js version should be 18+ for best compatibility', 'warning');
        }
    }

    async checkRust() {
        const cargoVersion = this.checkCommand('cargo --version', /cargo/, 'Rust/Cargo not found');
        const rustcVersion = this.checkCommand('rustc --version', /rustc/, 'Rust compiler not found');
        
        this.log(`Cargo: ${cargoVersion}`);
        this.log(`Rustc: ${rustcVersion}`);
    }

    async checkTauriCLI() {
        try {
            const tauriVersion = this.checkCommand('cargo tauri --version', /tauri-cli/, 'Tauri CLI not found');
            this.log(`Tauri CLI: ${tauriVersion}`);
        } catch (error) {
            this.log('Installing Tauri CLI...', 'info');
            try {
                execSync('cargo install tauri-cli', { stdio: 'inherit' });
                const tauriVersion = this.checkCommand('cargo tauri --version', /tauri-cli/, 'Tauri CLI installation failed');
                this.log(`Tauri CLI installed: ${tauriVersion}`, 'success');
            } catch (installError) {
                throw new Error('Failed to install Tauri CLI: ' + installError.message);
            }
        }
    }

    async checkProjectFiles() {
        const requiredFiles = [
            'src-tauri/Cargo.toml',
            'src-tauri/tauri.conf.json', 
            'src-tauri/src/main.rs',
            'package.json',
            'src/main.py'
        ];

        for (const file of requiredFiles) {
            const fullPath = path.join(this.projectRoot, file);
            if (!fs.existsSync(fullPath)) {
                throw new Error(`Required file missing: ${file}`);
            }
        }

        this.log(`All required project files present`);
    }

    async checkPythonDependencies() {
        const pythonCommands = ['python', 'python3'];
        let dependenciesOk = false;
        
        for (const cmd of pythonCommands) {
            try {
                const testScript = `
import sys
import os
import json
try:
    import fastapi
    import uvicorn
    import pydantic
    import requests
    print("OK")
    sys.exit(0)
except ImportError as e:
    print(f"MISSING: {e}")
    sys.exit(1)
`;
                const result = execSync(`${cmd} -c "${testScript.replace(/\n/g, '; ')}"`, { 
                    encoding: 'utf8', 
                    stdio: 'pipe' 
                });
                
                if (result.includes('OK')) {
                    dependenciesOk = true;
                    this.log('Python dependencies available');
                    break;
                } else {
                    this.log(`Python dependency check failed: ${result}`, 'warning');
                }
            } catch (error) {
                // Continue to next command
            }
        }
        
        if (!dependenciesOk) {
            this.log('Installing Python dependencies...', 'info');
            try {
                const { PythonSetup } = require('./setup_python_requirements.js');
                const setup = new PythonSetup();
                await setup.installRequirements();
                this.log('Python dependencies installed', 'success');
            } catch (error) {
                throw new Error('Failed to install Python dependencies: ' + error.message);
            }
        }
    }

    async checkWindowsBuildTools() {
        if (process.platform !== 'win32') {
            this.log('Not on Windows, skipping build tools check');
            return;
        }

        try {
            // Check for Visual Studio or Build Tools
            const vcvarsPath = [
                'C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvars64.bat',
                'C:\\Program Files\\Microsoft Visual Studio\\2019\\Community\\VC\\Auxiliary\\Build\\vcvars64.bat',
                'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat'
            ].find(path => fs.existsSync(path));

            if (vcvarsPath) {
                this.log(`Found Visual Studio Build Tools: ${vcvarsPath}`);
            } else {
                this.log('Visual Studio Build Tools not found. May cause build issues on Windows', 'warning');
            }
        } catch (error) {
            this.log('Could not verify Windows build tools', 'warning');
        }
    }

    async checkPortAvailability() {
        const ports = [3005, 8000, 8001, 8002, 8888];
        const net = require('net');
        
        for (const port of ports) {
            try {
                await new Promise((resolve, reject) => {
                    const server = net.createServer();
                    server.listen(port, '127.0.0.1', () => {
                        server.close();
                        resolve();
                    });
                    server.on('error', () => {
                        reject(new Error(`Port ${port} is in use`));
                    });
                });
            } catch (error) {
                this.log(`Port ${port} may be in use (this is OK if services are running)`, 'warning');
            }
        }
    }

    async runAllChecks() {
        this.log('🔍 Starting Tauri setup verification...\n');

        await this.runCheck('Python 3.x', () => this.checkPython());
        await this.runCheck('Node.js & npm', () => this.checkNode());
        await this.runCheck('Rust & Cargo', () => this.checkRust());
        await this.runCheck('Tauri CLI', () => this.checkTauriCLI());
        await this.runCheck('Project Files', () => this.checkProjectFiles());
        await this.runCheck('Python Dependencies', () => this.checkPythonDependencies());
        await this.runCheck('Windows Build Tools', () => this.checkWindowsBuildTools());
        await this.runCheck('Port Availability', () => this.checkPortAvailability());

        this.printSummary();
    }

    printSummary() {
        console.log('\n' + '='.repeat(60));
        console.log('📊 VERIFICATION SUMMARY');
        console.log('='.repeat(60));

        const passed = this.checks.filter(c => c.status === 'ok').length;
        const failed = this.checks.filter(c => c.status === 'error').length;

        console.log(`✅ Passed: ${passed}`);
        console.log(`❌ Failed: ${failed}`);
        console.log(`⚠️  Warnings: ${this.warnings.length}`);

        if (failed === 0) {
            console.log('\n🎉 All checks passed! Ready to build Tauri app.');
            console.log('\nNext steps:');
            console.log('  npm run tauri:dev      # Development mode');
            console.log('  npm run tauri:build    # Production build');
        } else {
            console.log('\n💥 Some checks failed. Please fix the issues above.');
            this.checks.filter(c => c.status === 'error').forEach(check => {
                console.log(`   ❌ ${check.name}: ${check.error}`);
            });
        }

        if (this.warnings.length > 0) {
            console.log('\n⚠️  Warnings:');
            this.warnings.forEach(warning => {
                console.log(`   • ${warning}`);
            });
        }
    }
}

async function main() {
    const verifier = new TauriVerifier();
    
    try {
        await verifier.runAllChecks();
        process.exit(verifier.errors.length > 0 ? 1 : 0);
    } catch (error) {
        console.error('💥 Verification failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { TauriVerifier };