#!/usr/bin/env node
/**
 * React Startup Fix Script
 * 
 * Comprehensive solution for React startup issues including:
 * - Port conflict resolution
 * - Process cleanup
 * - Environment setup
 * - Fallback port management
 */

const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class ReactStartupFixer {
    constructor() {
        this.defaultPorts = {
            react: 3005,
            static: 3008,
            electron: 3000
        };
        this.fallbackPorts = {
            react: [3006, 3007, 3009, 3010],
            static: [3011, 3012, 3013, 3014]
        };
        this.logFile = path.join(__dirname, 'react_startup_fix.log');
    }

    log(message, level = 'INFO') {
        const timestamp = new Date().toISOString();
        const logEntry = `[${timestamp}] ${level}: ${message}\n`;
        console.log(`${level}: ${message}`);
        
        try {
            fs.appendFileSync(this.logFile, logEntry);
        } catch (error) {
            console.warn('Could not write to log file:', error.message);
        }
    }

    async findAvailablePort(basePort, fallbackPorts = []) {
        const portsToTry = [basePort, ...fallbackPorts];
        
        for (const port of portsToTry) {
            const isAvailable = await this.checkPortAvailable(port);
            if (isAvailable) {
                this.log(`Found available port: ${port}`);
                return port;
            }
        }
        
        throw new Error(`No available ports found from: ${portsToTry.join(', ')}`);
    }

    checkPortAvailable(port) {
        return new Promise((resolve) => {
            const server = require('net').createServer();
            
            server.listen(port, () => {
                server.close(() => resolve(true));
            });
            
            server.on('error', () => resolve(false));
        });
    }

    async killProcessOnPort(port) {
        return new Promise((resolve) => {
            // Try multiple methods to kill process on port
            const commands = [
                `fuser -k ${port}/tcp`,
                `lsof -ti:${port} | xargs kill -9`,
                `pkill -f "PORT=${port}"`,
                `pkill -f ":${port}"`
            ];
            
            let commandsCompleted = 0;
            
            commands.forEach(cmd => {
                exec(cmd, (error) => {
                    commandsCompleted++;
                    if (error) {
                        this.log(`Command failed (expected): ${cmd}`, 'DEBUG');
                    } else {
                        this.log(`Successfully killed process on port ${port}`, 'INFO');
                    }
                    
                    if (commandsCompleted === commands.length) {
                        resolve();
                    }
                });
            });
            
            // Timeout after 5 seconds
            setTimeout(() => {
                if (commandsCompleted < commands.length) {
                    this.log(`Port cleanup timeout for port ${port}`, 'WARNING');
                    resolve();
                }
            }, 5000);
        });
    }

    async cleanupConflictingProcesses() {
        this.log('Cleaning up conflicting processes...');
        
        const portsToClean = [
            this.defaultPorts.react,
            this.defaultPorts.static,
            this.defaultPorts.electron,
            ...this.fallbackPorts.react,
            ...this.fallbackPorts.static
        ];
        
        // Kill React development servers
        const reactCleanupCommands = [
            'pkill -f "react-scripts"',
            'pkill -f "webpack-dev-server"',
            'pkill -f "cross-env PORT="',
            'pkill -f "concurrently"'
        ];
        
        for (const cmd of reactCleanupCommands) {
            await new Promise(resolve => {
                exec(cmd, (error) => {
                    if (!error) {
                        this.log(`Cleaned up: ${cmd}`);
                    }
                    resolve();
                });
            });
        }
        
        // Clean up ports
        for (const port of portsToClean) {
            await this.killProcessOnPort(port);
        }
        
        // Wait for cleanup to complete
        await new Promise(resolve => setTimeout(resolve, 2000));
    }

    async updatePackageJsonPorts(reactPort, staticPort) {
        const packageJsonPath = path.join(__dirname, 'package.json');
        
        try {
            const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
            
            // Update scripts with new ports
            packageJson.scripts = {
                ...packageJson.scripts,
                'start:react': `cross-env PORT=${reactPort} react-scripts start`,
                'start:static': `node -e "const express = require('express'); const app = express(); app.use(express.static('build')); app.listen(${staticPort}, () => console.log('Static server on port ${staticPort}'));"`,
                'dev': `concurrently "npm run start:react" "npx wait-on http://localhost:${reactPort} && npm run start:electron"`,
                'dev:enhanced': `concurrently "npm run start:react" "npx wait-on http://localhost:${reactPort} && npm run start:electron" "node start-hearthlink-clean.js"`
            };
            
            fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
            this.log(`Updated package.json with React port ${reactPort} and static port ${staticPort}`);
            
        } catch (error) {
            this.log(`Failed to update package.json: ${error.message}`, 'ERROR');
            throw error;
        }
    }

    async updateMainJsConfig(staticPort) {
        const mainJsPath = path.join(__dirname, 'main.js');
        
        try {
            let mainJsContent = fs.readFileSync(mainJsPath, 'utf8');
            
            // Update static server port references
            mainJsContent = mainJsContent.replace(
                /const STATIC_SERVER_PORT = \d+/g,
                `const STATIC_SERVER_PORT = ${staticPort}`
            );
            
            mainJsContent = mainJsContent.replace(
                /localhost:\d+/g,
                `localhost:${staticPort}`
            );
            
            fs.writeFileSync(mainJsPath, mainJsContent);
            this.log(`Updated main.js with static port ${staticPort}`);
            
        } catch (error) {
            this.log(`Failed to update main.js: ${error.message}`, 'ERROR');
        }
    }

    async createEnvironmentFile(reactPort, staticPort) {
        const envContent = `
# React Development Configuration
PORT=${reactPort}
BROWSER=none
GENERATE_SOURCEMAP=false
FAST_REFRESH=true

# Static Server Configuration  
STATIC_PORT=${staticPort}

# Development Settings
NODE_ENV=development
REACT_APP_STATIC_URL=http://localhost:${staticPort}
REACT_APP_API_URL=http://localhost:8000

# Disable automatic browser opening
BROWSER=none
`;
        
        const envPath = path.join(__dirname, '.env.development');
        fs.writeFileSync(envPath, envContent.trim());
        this.log(`Created .env.development with ports React:${reactPort}, Static:${staticPort}`);
    }

    async testReactStartup(reactPort) {
        this.log('Testing React startup...');
        
        return new Promise((resolve) => {
            const reactProcess = spawn('npm', ['run', 'start:react'], {
                stdio: ['ignore', 'pipe', 'pipe'],
                env: { ...process.env, PORT: reactPort }
            });
            
            let startupSuccess = false;
            let startupOutput = '';
            
            const timeout = setTimeout(() => {
                if (!startupSuccess) {
                    reactProcess.kill();
                    this.log('React startup test timed out', 'ERROR');
                    resolve(false);
                }
            }, 30000);
            
            reactProcess.stdout.on('data', (data) => {
                const output = data.toString();
                startupOutput += output;
                
                if (output.includes('webpack compiled') || 
                    output.includes('Compiled successfully') ||
                    output.includes('Local:') ||
                    output.includes(`localhost:${reactPort}`)) {
                    startupSuccess = true;
                    clearTimeout(timeout);
                    reactProcess.kill();
                    this.log('React startup test successful!');
                    resolve(true);
                }
            });
            
            reactProcess.stderr.on('data', (data) => {
                const error = data.toString();
                startupOutput += error;
                
                if (error.includes('Something is already running') ||
                    error.includes('EADDRINUSE')) {
                    clearTimeout(timeout);
                    reactProcess.kill();
                    this.log(`React startup failed - port conflict: ${error}`, 'ERROR');
                    resolve(false);
                }
            });
            
            reactProcess.on('exit', (code) => {
                if (!startupSuccess) {
                    this.log(`React process exited with code ${code}`, 'WARNING');
                    this.log(`Startup output: ${startupOutput}`, 'DEBUG');
                    clearTimeout(timeout);
                    resolve(false);
                }
            });
        });
    }

    async fixReactStartup() {
        this.log('🔄 Starting React Startup Fix Process');
        this.log('=' * 50);
        
        try {
            // Step 1: Clean up conflicting processes
            await this.cleanupConflictingProcesses();
            
            // Step 2: Find available ports
            this.log('Finding available ports...');
            const reactPort = await this.findAvailablePort(
                this.defaultPorts.react, 
                this.fallbackPorts.react
            );
            
            const staticPort = await this.findAvailablePort(
                this.defaultPorts.static,
                this.fallbackPorts.static
            );
            
            // Step 3: Update configuration files
            await this.updatePackageJsonPorts(reactPort, staticPort);
            await this.updateMainJsConfig(staticPort);
            await this.createEnvironmentFile(reactPort, staticPort);
            
            // Step 4: Test React startup
            this.log('Testing React startup with new configuration...');
            const startupSuccess = await this.testReactStartup(reactPort);
            
            if (startupSuccess) {
                this.log('✅ React Startup Fix: SUCCESS!');
                this.log(`🚀 React will run on: http://localhost:${reactPort}`);
                this.log(`📁 Static files on: http://localhost:${staticPort}`);
                this.log('');
                this.log('You can now run:');
                this.log('  npm run dev          - Start React + Electron');
                this.log('  npm run dev:enhanced - Start with all services');
                this.log('  npm run start:react  - Start React only');
                
                return { success: true, reactPort, staticPort };
            } else {
                throw new Error('React startup test failed');
            }
            
        } catch (error) {
            this.log(`❌ React Startup Fix Failed: ${error.message}`, 'ERROR');
            
            // Provide fallback solutions
            this.log('🔧 Fallback solutions:', 'INFO');
            this.log('1. Run: npm run build && npm start', 'INFO');
            this.log('2. Try: npx kill-port 3005 && npm run dev', 'INFO');
            this.log('3. Manual: Change PORT in .env to a different value', 'INFO');
            
            return { success: false, error: error.message };
        }
    }

    async createServiceHealthChecker() {
        const healthCheckerContent = `#!/usr/bin/env node
/**
 * Service Health Checker
 * Monitors React and other services for health status
 */

const http = require('http');

class ServiceHealthChecker {
    constructor() {
        this.services = {
            react: { port: ${this.defaultPorts.react}, name: 'React Development Server' },
            static: { port: ${this.defaultPorts.static}, name: 'Static File Server' },
            core: { port: 8000, name: 'Core API' },
            llm: { port: 8001, name: 'Local LLM API' }
        };
    }

    async checkService(name, port) {
        return new Promise((resolve) => {
            const req = http.request({
                hostname: 'localhost',
                port: port,
                path: '/',
                method: 'GET',
                timeout: 2000
            }, (res) => {
                resolve({ 
                    name, 
                    port, 
                    status: 'healthy', 
                    statusCode: res.statusCode 
                });
            });

            req.on('error', () => {
                resolve({ 
                    name, 
                    port, 
                    status: 'unhealthy', 
                    error: 'Connection failed' 
                });
            });

            req.on('timeout', () => {
                req.destroy();
                resolve({ 
                    name, 
                    port, 
                    status: 'timeout', 
                    error: 'Request timeout' 
                });
            });

            req.end();
        });
    }

    async checkAllServices() {
        console.log('🔍 Checking service health...');
        console.log('================================');
        
        const results = await Promise.all(
            Object.entries(this.services).map(([key, service]) => 
                this.checkService(service.name, service.port)
            )
        );

        results.forEach(result => {
            const statusIcon = result.status === 'healthy' ? '✅' : '❌';
            console.log(\`\${statusIcon} \${result.name} (:\${result.port}) - \${result.status}\`);
        });

        const healthyCount = results.filter(r => r.status === 'healthy').length;
        console.log(\`\\n📊 Health Summary: \${healthyCount}/\${results.length} services healthy\`);
        
        return results;
    }
}

if (require.main === module) {
    const checker = new ServiceHealthChecker();
    checker.checkAllServices();
}

module.exports = ServiceHealthChecker;
`;

        const healthCheckerPath = path.join(__dirname, 'check-service-health.js');
        fs.writeFileSync(healthCheckerPath, healthCheckerContent);
        fs.chmodSync(healthCheckerPath, '755');
        this.log('Created service health checker: check-service-health.js');
    }
}

// Run the fix if called directly
if (require.main === module) {
    const fixer = new ReactStartupFixer();
    
    fixer.fixReactStartup().then(result => {
        if (result.success) {
            console.log('\n🎉 React startup issues resolved!');
            process.exit(0);
        } else {
            console.log('\n⚠️ React startup fix completed with issues');
            process.exit(1);
        }
    }).catch(error => {
        console.error('\n💥 React startup fix failed:', error.message);
        process.exit(1);
    });
}

module.exports = ReactStartupFixer;