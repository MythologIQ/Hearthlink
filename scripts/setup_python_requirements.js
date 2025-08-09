#!/usr/bin/env node

/**
 * Python Requirements Setup Script
 * 
 * This script ensures Python dependencies are installed for Tauri builds.
 * It attempts to install requirements using pip/pip3 in a cross-platform manner.
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class PythonSetup {
    constructor() {
        this.projectRoot = path.resolve(__dirname, '..');
        this.requirementsFile = path.join(this.projectRoot, 'requirements_full.txt');
        this.fallbackRequirementsFile = path.join(this.projectRoot, 'requirements.txt');
    }

    findPython() {
        const pythonCandidates = ['python3', 'python', 'python.exe', 'python3.exe'];
        
        for (const candidate of pythonCandidates) {
            try {
                const version = execSync(`${candidate} --version`, { encoding: 'utf8', stdio: 'pipe' });
                if (version.includes('Python 3.')) {
                    console.log(`✅ Found Python: ${candidate} (${version.trim()})`);
                    return candidate;
                }
            } catch (error) {
                // Continue to next candidate
            }
        }
        
        throw new Error('Python 3.x not found. Please install Python 3.x and ensure it\'s in your PATH.');
    }

    findRequirementsFile() {
        if (fs.existsSync(this.requirementsFile)) {
            console.log(`📦 Using requirements file: ${this.requirementsFile}`);
            return this.requirementsFile;
        } else if (fs.existsSync(this.fallbackRequirementsFile)) {
            console.log(`📦 Using fallback requirements file: ${this.fallbackRequirementsFile}`);
            return this.fallbackRequirementsFile;
        } else {
            console.log('⚠️  No requirements.txt found, creating minimal requirements...');
            const minimalRequirements = [
                'fastapi>=0.104.0',
                'uvicorn>=0.24.0',
                'pydantic>=2.0.0',
                'requests>=2.31.0',
                'sqlite3' // Built-in to Python 3.x
            ].join('\n');
            
            fs.writeFileSync(this.fallbackRequirementsFile, minimalRequirements);
            return this.fallbackRequirementsFile;
        }
    }

    async installRequirements() {
        try {
            const python = this.findPython();
            const requirementsFile = this.findRequirementsFile();

            console.log('📦 Installing Python dependencies...');
            
            const installCommand = [python, '-m', 'pip', 'install', '-r', requirementsFile];
            
            return new Promise((resolve, reject) => {
                const process = spawn(installCommand[0], installCommand.slice(1), {
                    stdio: 'inherit',
                    cwd: this.projectRoot
                });

                process.on('close', (code) => {
                    if (code === 0) {
                        console.log('✅ Python dependencies installed successfully');
                        resolve();
                    } else {
                        console.error(`❌ Failed to install Python dependencies (exit code: ${code})`);
                        console.log('💡 Try manually running:');
                        console.log(`   ${installCommand.join(' ')}`);
                        reject(new Error(`pip install failed with code ${code}`));
                    }
                });

                process.on('error', (error) => {
                    console.error('❌ Error running pip install:', error.message);
                    reject(error);
                });
            });

        } catch (error) {
            console.error('❌ Setup failed:', error.message);
            throw error;
        }
    }

    async verifyInstallation() {
        console.log('🔍 Verifying Python installation...');
        
        try {
            const python = this.findPython();
            
            // Test core imports
            const testScript = `
import sys
import os
import json
import sqlite3
try:
    import fastapi
    import uvicorn
    import pydantic
    import requests
    print("✅ All core dependencies available")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    sys.exit(1)
`;

            execSync(`${python} -c "${testScript.replace(/\n/g, '; ')}"`, {
                stdio: 'inherit',
                cwd: this.projectRoot
            });

            console.log('✅ Python environment verified successfully');
            return true;
            
        } catch (error) {
            console.error('❌ Python environment verification failed');
            console.log('💡 Run "npm run python:install" to install missing dependencies');
            return false;
        }
    }
}

async function main() {
    const setup = new PythonSetup();
    
    try {
        await setup.installRequirements();
        await setup.verifyInstallation();
        console.log('🎉 Python setup completed successfully!');
        process.exit(0);
    } catch (error) {
        console.error('💥 Python setup failed:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { PythonSetup };