#!/usr/bin/env node

/**
 * Integration Test Script for Hearthlink IPC Bridge
 * 
 * This script tests the communication between Electron and Python backend
 * to ensure all IPC handlers are working correctly.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class IntegrationTester {
  constructor() {
    this.pythonProcess = null;
    this.testResults = [];
  }

  log(message) {
    console.log(`[TEST] ${message}`);
  }

  error(message) {
    console.error(`[ERROR] ${message}`);
  }

  async startPythonBackend() {
    return new Promise((resolve, reject) => {
      const pythonPath = process.env.PYTHON_PATH || 'python';
      const backendScript = path.join(__dirname, 'src', 'main.py');
      
      this.log('Starting Python backend for testing...');
      
      this.pythonProcess = spawn(pythonPath, [backendScript, '--ipc'], {
        cwd: __dirname,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONPATH: path.join(__dirname, 'src') }
      });
      
      let initBuffer = '';
      
      this.pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        initBuffer += output;
        
        if (initBuffer.includes('HEARTHLINK_READY')) {
          this.log('Python backend ready for testing');
          resolve(true);
        }
      });
      
      this.pythonProcess.stderr.on('data', (data) => {
        this.error(`Python stderr: ${data.toString()}`);
      });
      
      this.pythonProcess.on('error', (error) => {
        this.error(`Failed to start Python backend: ${error.message}`);
        reject(error);
      });
      
      // Timeout after 10 seconds
      setTimeout(() => {
        if (!this.pythonProcess?.killed) {
          this.error('Python backend startup timeout');
          reject(new Error('Python backend startup timeout'));
        }
      }, 10000);
    });
  }

  async sendCommand(command) {
    return new Promise((resolve, reject) => {
      if (!this.pythonProcess) {
        reject(new Error('Python backend not running'));
        return;
      }
      
      const message = JSON.stringify(command) + '\n';
      this.pythonProcess.stdin.write(message);
      
      const timeout = setTimeout(() => {
        reject(new Error('Command timeout'));
      }, 5000);
      
      const responseHandler = (data) => {
        try {
          const lines = data.toString().split('\n');
          for (const line of lines) {
            if (line.trim()) {
              const response = JSON.parse(line);
              if (response.id === command.id) {
                clearTimeout(timeout);
                this.pythonProcess.stdout.removeListener('data', responseHandler);
                resolve(response);
                return;
              }
            }
          }
        } catch (error) {
          // Continue listening for valid JSON
        }
      };
      
      this.pythonProcess.stdout.on('data', responseHandler);
    });
  }

  async testVoiceCommand() {
    this.log('Testing voice command...');
    
    const command = {
      id: Date.now(),
      type: 'voice_command',
      payload: { command: 'Hello, this is a test voice command' }
    };
    
    try {
      const response = await this.sendCommand(command);
      
      if (response.success && response.data) {
        this.log('✓ Voice command test passed');
        this.testResults.push({ test: 'voice_command', passed: true });
      } else {
        this.error('✗ Voice command test failed: ' + JSON.stringify(response));
        this.testResults.push({ test: 'voice_command', passed: false, error: response.error });
      }
    } catch (error) {
      this.error('✗ Voice command test failed: ' + error.message);
      this.testResults.push({ test: 'voice_command', passed: false, error: error.message });
    }
  }

  async testCoreSession() {
    this.log('Testing Core session creation...');
    
    const command = {
      id: Date.now(),
      type: 'core_create_session',
      payload: {
        userId: 'test-user-001',
        topic: 'Test Conference Session',
        participants: [
          { id: 'alden', name: 'Alden', type: 'persona', role: 'Executive Function' },
          { id: 'alice', name: 'Alice', type: 'persona', role: 'Behavioral Analysis' }
        ]
      }
    };
    
    try {
      const response = await this.sendCommand(command);
      
      if (response.success && response.data && response.data.sessionId) {
        this.log('✓ Core session creation test passed');
        this.testResults.push({ test: 'core_create_session', passed: true, sessionId: response.data.sessionId });
        return response.data.sessionId;
      } else {
        this.error('✗ Core session creation test failed: ' + JSON.stringify(response));
        this.testResults.push({ test: 'core_create_session', passed: false, error: response.error });
        return null;
      }
    } catch (error) {
      this.error('✗ Core session creation test failed: ' + error.message);
      this.testResults.push({ test: 'core_create_session', passed: false, error: error.message });
      return null;
    }
  }

  async testGetSession(sessionId) {
    if (!sessionId) {
      this.log('Skipping get session test - no session ID');
      return;
    }
    
    this.log('Testing Core session retrieval...');
    
    const command = {
      id: Date.now(),
      type: 'core_get_session',
      payload: { sessionId: sessionId }
    };
    
    try {
      const response = await this.sendCommand(command);
      
      if (response.success && response.data && response.data.session_id) {
        this.log('✓ Core session retrieval test passed');
        this.testResults.push({ test: 'core_get_session', passed: true });
      } else {
        this.error('✗ Core session retrieval test failed: ' + JSON.stringify(response));
        this.testResults.push({ test: 'core_get_session', passed: false, error: response.error });
      }
    } catch (error) {
      this.error('✗ Core session retrieval test failed: ' + error.message);
      this.testResults.push({ test: 'core_get_session', passed: false, error: error.message });
    }
  }

  async testSynapseListPlugins() {
    this.log('Testing Synapse plugin listing...');
    
    const command = {
      id: Date.now(),
      type: 'synapse_list_plugins',
      payload: {}
    };
    
    try {
      const response = await this.sendCommand(command);
      
      if (response.success && response.data && response.data.plugins) {
        this.log('✓ Synapse plugin listing test passed');
        this.testResults.push({ test: 'synapse_list_plugins', passed: true });
      } else {
        this.error('✗ Synapse plugin listing test failed: ' + JSON.stringify(response));
        this.testResults.push({ test: 'synapse_list_plugins', passed: false, error: response.error });
      }
    } catch (error) {
      this.error('✗ Synapse plugin listing test failed: ' + error.message);
      this.testResults.push({ test: 'synapse_list_plugins', passed: false, error: error.message });
    }
  }

  async testInvalidCommand() {
    this.log('Testing invalid command handling...');
    
    const command = {
      id: Date.now(),
      type: 'invalid_command_type',
      payload: {}
    };
    
    try {
      const response = await this.sendCommand(command);
      
      if (!response.success && response.error && response.error.includes('Unknown command type')) {
        this.log('✓ Invalid command handling test passed');
        this.testResults.push({ test: 'invalid_command', passed: true });
      } else {
        this.error('✗ Invalid command handling test failed: ' + JSON.stringify(response));
        this.testResults.push({ test: 'invalid_command', passed: false, error: 'Should have failed' });
      }
    } catch (error) {
      this.error('✗ Invalid command handling test failed: ' + error.message);
      this.testResults.push({ test: 'invalid_command', passed: false, error: error.message });
    }
  }

  async runAllTests() {
    this.log('Starting integration tests...');
    
    try {
      // Start Python backend
      await this.startPythonBackend();
      
      // Run tests
      await this.testVoiceCommand();
      const sessionId = await this.testCoreSession();
      await this.testGetSession(sessionId);
      await this.testSynapseListPlugins();
      await this.testInvalidCommand();
      
      // Report results
      this.generateReport();
      
    } catch (error) {
      this.error('Test suite failed: ' + error.message);
    } finally {
      // Cleanup
      if (this.pythonProcess) {
        this.pythonProcess.kill();
      }
    }
  }

  generateReport() {
    this.log('=== Test Results ===');
    
    const passed = this.testResults.filter(r => r.passed).length;
    const total = this.testResults.length;
    
    this.testResults.forEach(result => {
      const status = result.passed ? '✓ PASS' : '✗ FAIL';
      const error = result.error ? ` (${result.error})` : '';
      this.log(`${status}: ${result.test}${error}`);
    });
    
    this.log(`\nSummary: ${passed}/${total} tests passed`);
    
    if (passed === total) {
      this.log('🎉 All tests passed! Integration is working correctly.');
    } else {
      this.error(`❌ ${total - passed} tests failed. Check the errors above.`);
    }
    
    // Save results to file
    const reportPath = path.join(__dirname, 'test_results.json');
    fs.writeFileSync(reportPath, JSON.stringify({
      timestamp: new Date().toISOString(),
      summary: { passed, total },
      results: this.testResults
    }, null, 2));
    
    this.log(`Test results saved to: ${reportPath}`);
  }
}

// Run tests if this script is executed directly
if (require.main === module) {
  const tester = new IntegrationTester();
  tester.runAllTests().catch(error => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}

module.exports = IntegrationTester;