#!/usr/bin/env node
/**
 * Force React Fix - Aggressive approach
 * Uses multiple fallback strategies to get React working
 */

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class ForceReactFix {
    constructor() {
        this.testPorts = [3015, 3016, 3017, 3018, 3019, 3020, 3021, 3022];
        this.logFile = 'force_react_fix.log';
    }

    log(message) {
        const timestamp = new Date().toISOString();
        const logEntry = `[${timestamp}] ${message}`;
        console.log(logEntry);
        fs.appendFileSync(this.logFile, logEntry + '\n');
    }

    async findWorkingPort() {
        this.log('Finding a working port for React...');
        
        for (const port of this.testPorts) {
            const isAvailable = await this.testPort(port);
            if (isAvailable) {
                this.log(`Found working port: ${port}`);
                return port;
            }
        }
        
        throw new Error('No available ports found');
    }

    testPort(port) {
        return new Promise((resolve) => {
            const server = require('net').createServer();
            
            server.listen(port, () => {
                server.close(() => {
                    this.log(`Port ${port} is available`);
                    resolve(true);
                });
            });
            
            server.on('error', () => {
                this.log(`Port ${port} is in use`);
                resolve(false);
            });
        });
    }

    async updateEnvironmentFiles(port) {
        // Update .env.development
        const envContent = `PORT=${port}\nBROWSER=none\nGENERATE_SOURCEMAP=false\n`;
        fs.writeFileSync('.env.development', envContent);
        this.log(`Updated .env.development with port ${port}`);

        // Update .env.local if it exists
        if (fs.existsSync('.env.local')) {
            fs.writeFileSync('.env.local', envContent);
            this.log('Updated .env.local');
        }

        // Create .env if it doesn't exist
        fs.writeFileSync('.env', envContent);
        this.log('Updated .env');
    }

    async createSimpleStartScript(port) {
        const startScript = `#!/usr/bin/env node
/**
 * Simple React Start Script
 * Starts React on a specific port with fallback handling
 */

const { spawn } = require('child_process');

console.log('🚀 Starting React on port ${port}...');

const reactProcess = spawn('npx', ['react-scripts', 'start'], {
    env: {
        ...process.env,
        PORT: '${port}',
        BROWSER: 'none',
        GENERATE_SOURCEMAP: 'false'
    },
    stdio: 'inherit'
});

reactProcess.on('exit', (code) => {
    console.log(\`React process exited with code \${code}\`);
});

process.on('SIGINT', () => {
    console.log('\\n🛑 Stopping React...');
    reactProcess.kill();
    process.exit(0);
});
`;

        fs.writeFileSync('start-react-simple.js', startScript);
        fs.chmodSync('start-react-simple.js', '755');
        this.log(`Created simple start script for port ${port}`);
    }

    async updatePackageJsonScripts(port) {
        const packageJsonPath = 'package.json';
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        
        packageJson.scripts = {
            ...packageJson.scripts,
            'start:react-fixed': `cross-env PORT=${port} BROWSER=none react-scripts start`,
            'start:react-simple': `node start-react-simple.js`,
            'dev:fixed': `concurrently "npm run start:react-fixed" "sleep 8 && npm run start:electron"`
        };
        
        fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
        this.log(`Updated package.json with fixed scripts for port ${port}`);
    }

    async testReactOnPort(port) {
        this.log(`Testing React startup on port ${port}...`);
        
        return new Promise((resolve) => {
            const reactProcess = spawn('npm', ['run', 'start:react-fixed'], {
                stdio: ['ignore', 'pipe', 'pipe'],
                env: { ...process.env, PORT: port }
            });
            
            let success = false;
            let output = '';
            
            const timeout = setTimeout(() => {
                if (!success) {
                    reactProcess.kill();
                    this.log(`React test on port ${port} timed out`);
                    resolve(false);
                }
            }, 45000); // 45 second timeout
            
            reactProcess.stdout.on('data', (data) => {
                const text = data.toString();
                output += text;
                
                // Look for success indicators
                if (text.includes('webpack compiled') || 
                    text.includes('Compiled successfully') ||
                    text.includes('Local:') ||
                    text.includes(`localhost:${port}`) ||
                    text.includes('You can now view')) {
                    success = true;
                    clearTimeout(timeout);
                    reactProcess.kill();
                    this.log(`✅ React successfully started on port ${port}!`);
                    resolve(true);
                }
            });
            
            reactProcess.stderr.on('data', (data) => {
                output += data.toString();
            });
            
            reactProcess.on('exit', (code) => {
                clearTimeout(timeout);
                if (!success) {
                    this.log(`React test failed with exit code ${code}`);
                    this.log(`Output: ${output}`);
                    resolve(false);
                }
            });
        });
    }

    async buildFallback() {
        this.log('Building React app as fallback...');
        
        return new Promise((resolve) => {
            const buildProcess = spawn('npm', ['run', 'build'], {
                stdio: 'inherit'
            });
            
            buildProcess.on('exit', (code) => {
                if (code === 0) {
                    this.log('✅ React build successful');
                    resolve(true);
                } else {
                    this.log('❌ React build failed');
                    resolve(false);
                }
            });
        });
    }

    async createElectronWithBuild() {
        // Update main.js to use build directory
        const mainJsPath = 'main.js';
        let mainJsContent = fs.readFileSync(mainJsPath, 'utf8');
        
        // Add build directory fallback
        const buildFallbackCode = `
// Force use build directory
const isDev = false; // Force production mode
const indexPath = path.join(__dirname, 'build', 'index.html');
`;
        
        // Insert after imports
        const lines = mainJsContent.split('\n');
        const importEndIndex = lines.findIndex(line => 
            line.includes('require(') && !line.includes('//') && lines.indexOf(line) > 5
        );
        
        if (importEndIndex > -1) {
            lines.splice(importEndIndex + 1, 0, buildFallbackCode);
            fs.writeFileSync(mainJsPath, lines.join('\n'));
            this.log('Updated main.js to use build directory');
        }
    }

    async run() {
        this.log('🔄 Force React Fix - Starting aggressive repair...');
        this.log('=' * 60);
        
        try {
            // Strategy 1: Find a working port and test React
            const workingPort = await this.findWorkingPort();
            await this.updateEnvironmentFiles(workingPort);
            await this.updatePackageJsonScripts(workingPort);
            await this.createSimpleStartScript(workingPort);
            
            const reactWorks = await this.testReactOnPort(workingPort);
            
            if (reactWorks) {
                this.log('🎉 SUCCESS: React is now working!');
                this.log(`🚀 Start React with: npm run start:react-fixed`);
                this.log(`🚀 Start full app with: npm run dev:fixed`);
                this.log(`🌐 React URL: http://localhost:${workingPort}`);
                return { success: true, port: workingPort, strategy: 'port_fix' };
            }
            
            // Strategy 2: Build and use static files
            this.log('React dev server failed, trying build approach...');
            const buildSuccess = await this.buildFallback();
            
            if (buildSuccess) {
                await this.createElectronWithBuild();
                this.log('🎉 SUCCESS: Using built React files!');
                this.log(`🚀 Start app with: npm start (uses build directory)`);
                return { success: true, strategy: 'build_fallback' };
            }
            
            // Strategy 3: Last resort instructions
            this.log('All automated fixes failed. Manual intervention required.');
            this.log('🔧 Manual fix options:');
            this.log('1. Try: npx create-react-app temp-app && cp -r temp-app/public/* public/');
            this.log('2. Try: rm -rf node_modules && npm install');
            this.log('3. Try: npm run build && npm start');
            this.log('4. Check WSL/Windows file permissions');
            
            return { success: false, strategy: 'manual_required' };
            
        } catch (error) {
            this.log(`❌ Force fix failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }
}

// Run if called directly
if (require.main === module) {
    const fixer = new ForceReactFix();
    fixer.run().then(result => {
        if (result.success) {
            console.log('\n🎉 React fix completed successfully!');
            process.exit(0);
        } else {
            console.log('\n⚠️ React fix requires manual intervention');
            process.exit(1);
        }
    });
}

module.exports = ForceReactFix;