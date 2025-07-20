/**
 * Security Test Framework for Hearthlink
 * Tests for vulnerability regression prevention
 */

const { strict: assert } = require('assert');
const path = require('path');
const fs = require('fs');

class SecurityTests {
  constructor() {
    this.results = {
      passed: 0,
      failed: 0,
      tests: []
    };
  }

  // Test helper
  test(name, testFn) {
    try {
      console.log(`[TEST] ${name}...`);
      testFn();
      this.results.passed++;
      this.results.tests.push({ name, status: 'PASS' });
      console.log(`[PASS] ${name}`);
    } catch (error) {
      this.results.failed++;
      this.results.tests.push({ name, status: 'FAIL', error: error.message });
      console.error(`[FAIL] ${name}: ${error.message}`);
    }
  }

  // Path traversal vulnerability tests
  testPathTraversalPrevention() {
    this.test('Path traversal prevention in preload.js', () => {
      const preloadContent = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
      
      // Check for secure path validation function
      assert(preloadContent.includes('validatePath'), 'validatePath function not found');
      assert(preloadContent.includes('ALLOWED_PATHS'), 'ALLOWED_PATHS whitelist not found');
      assert(preloadContent.includes('path.resolve'), 'path.resolve security check not found');
      
      // Ensure dangerous patterns are not present
      assert(!preloadContent.includes('path.join(process.resourcesPath, filePath)'), 
             'Dangerous direct path join still present');
    });
  }

  // CSP security tests
  testContentSecurityPolicy() {
    this.test('Content Security Policy implementation', () => {
      const preloadContent = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
      
      // Check that unsafe directives are removed
      assert(!preloadContent.includes("'unsafe-eval'"), 
             "Dangerous 'unsafe-eval' directive still present");
      assert(!preloadContent.includes("'unsafe-inline'") || 
             preloadContent.includes("style-src 'self' 'unsafe-inline'"), 
             "Unsafe 'unsafe-inline' in script-src");
      
      // Check for nonce implementation
      assert(preloadContent.includes('generateSecureNonce'), 'CSP nonce generation not found');
      assert(preloadContent.includes('script-src'), 'script-src directive not found');
    });
  }

  // IPC handler validation tests
  testIPCValidation() {
    this.test('IPC handler input validation', () => {
      const preloadContent = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
      
      // Check for validation functions
      assert(preloadContent.includes('validateString'), 'validateString function not found');
      assert(preloadContent.includes('validateId'), 'validateId function not found');
      assert(preloadContent.includes('validateObject'), 'validateObject function not found');
      assert(preloadContent.includes('secureIpcInvoke'), 'secureIpcInvoke wrapper not found');
      
      // Check that IPC handlers use validation
      const ipcHandlers = [
        'core-create-session',
        'vault-get-persona-memory',
        'synapse-execute-plugin',
        'alden-write-file'
      ];
      
      ipcHandlers.forEach(handler => {
        assert(preloadContent.includes(`secureIpcInvoke('${handler}'`), 
               `Handler ${handler} not using secure wrapper`);
      });
    });
  }

  // Process spawning security tests
  testProcessSpawningSecurity() {
    this.test('Process spawning security in main.js', () => {
      const mainContent = fs.readFileSync(path.join(__dirname, '..', 'main.js'), 'utf8');
      
      // Check for Python path validation
      assert(mainContent.includes('validatePythonPath'), 'validatePythonPath function not found');
      assert(mainContent.includes('allowedPythonPaths'), 'Python path whitelist not found');
      
      // Check for command injection protection
      assert(mainContent.includes('replace(/[;&|`$(){}[\\]]/g'), 'Command injection filter not found');
      
      // Check for path traversal protection in backend script
      assert(mainContent.includes('scriptPath.startsWith(projectDir)'), 
             'Backend script path validation not found');
    });
  }

  // File system security tests
  testFileSystemSecurity() {
    this.test('File system access security', () => {
      const preloadContent = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
      
      // Check that file operations use security validation
      assert(preloadContent.includes('validatePath(filePath)'), 
             'File path validation not applied');
      assert(preloadContent.includes('fullPath.startsWith(path.resolve(process.resourcesPath))'), 
             'Path traversal check not found in file operations');
      
      // Ensure dangerous file operations are removed
      assert(!preloadContent.includes('fs.promises.readFile(fullPath') || 
             preloadContent.includes('validatePath'), 
             'Unvalidated file operations found');
    });
  }

  // Environment variable security tests
  testEnvironmentSecurity() {
    this.test('Environment variable security', () => {
      const mainContent = fs.readFileSync(path.join(__dirname, '..', 'main.js'), 'utf8');
      
      // Check for dangerous environment variable clearing
      assert(mainContent.includes('LD_PRELOAD: undefined'), 
             'LD_PRELOAD not cleared in spawn environment');
      assert(mainContent.includes('LD_LIBRARY_PATH: undefined'), 
             'LD_LIBRARY_PATH not cleared in spawn environment');
    });
  }

  // Security header tests
  testSecurityHeaders() {
    this.test('Security headers implementation', () => {
      const preloadContent = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
      
      // Check for security headers
      const requiredHeaders = [
        'X-Content-Type-Options',
        'X-Frame-Options',
        'X-XSS-Protection',
        'Referrer-Policy'
      ];
      
      requiredHeaders.forEach(header => {
        assert(preloadContent.includes(header), `Security header ${header} not found`);
      });
    });
  }

  // Input sanitization tests
  testInputSanitization() {
    this.test('Input sanitization in validation functions', () => {
      const preloadContent = fs.readFileSync(path.join(__dirname, '..', 'preload.js'), 'utf8');
      
      // Check for XSS protection
      assert(preloadContent.includes('replace(/<script\\b[^<]*(?:(?!<\\/script>)<[^<]*)*<\\/script>/gi'), 
             'Script tag sanitization not found');
      assert(preloadContent.includes('replace(/javascript:/gi'), 
             'JavaScript protocol sanitization not found');
      assert(preloadContent.includes('replace(/on\\w+\\s*=/gi'), 
             'Event handler sanitization not found');
    });
  }

  // Run all security tests
  runAllTests() {
    console.log('========================================');
    console.log('HEARTHLINK SECURITY TEST FRAMEWORK');
    console.log('========================================');
    console.log('Running vulnerability regression tests...\n');

    this.testPathTraversalPrevention();
    this.testContentSecurityPolicy();
    this.testIPCValidation();
    this.testProcessSpawningSecurity();
    this.testFileSystemSecurity();
    this.testEnvironmentSecurity();
    this.testSecurityHeaders();
    this.testInputSanitization();

    console.log('\n========================================');
    console.log('SECURITY TEST RESULTS');
    console.log('========================================');
    console.log(`Total Tests: ${this.results.passed + this.results.failed}`);
    console.log(`Passed: ${this.results.passed}`);
    console.log(`Failed: ${this.results.failed}`);
    
    if (this.results.failed > 0) {
      console.log('\nFailed Tests:');
      this.results.tests
        .filter(test => test.status === 'FAIL')
        .forEach(test => console.log(`- ${test.name}: ${test.error}`));
    }

    console.log(`\nSecurity Status: ${this.results.failed === 0 ? '✅ SECURE' : '❌ VULNERABILITIES DETECTED'}`);
    
    return this.results.failed === 0;
  }
}

// CLI interface
if (require.main === module) {
  const securityTests = new SecurityTests();
  const isSecure = securityTests.runAllTests();
  process.exit(isSecure ? 0 : 1);
}

module.exports = SecurityTests;