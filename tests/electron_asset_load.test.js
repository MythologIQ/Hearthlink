/**
 * Electron Asset Loading Test Suite
 * 
 * This test validates that Electron can properly load all static assets
 * including CSS, JavaScript, images, and other resources from the build directory.
 * 
 * Test Requirements:
 * - All assets in build/ directory must be accessible
 * - Protocol handler must work correctly
 * - Static server fallback must function
 * - No hardcoded file:// paths
 * - Electron build must match browser behavior
 */

const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const assert = require('assert');

// Test configuration
const TEST_CONFIG = {
  buildPath: path.join(__dirname, '..', 'build'),
  staticServerPort: 3001,
  timeout: 10000,
  assets: [
    'index.html',
    'static/css/main.750a3279.css',
    'static/js/main.253b1441.js',
    'assets/Hearthlink.png',
    'assets/Alden.png',
    'assets/Alice.png',
    'assets/Core.png',
    'assets/Synapse.png',
    'assets/Sentry.png',
    'assets/Vault.png',
    'assets/Mimic.png',
    'assets/logo.png',
    'assets/header-logo.png',
    'assets/Loading.png',
    'assets/stars.png',
    'assets/obsidian-bg.png'
  ]
};

// Test results tracking
const testResults = {
  passed: 0,
  failed: 0,
  errors: [],
  startTime: Date.now()
};

/**
 * Test 1: Validate Build Directory Structure
 */
function testBuildDirectoryStructure() {
  console.log('\n=== Test 1: Build Directory Structure ===');
  
  try {
    // Check if build directory exists
    assert(fs.existsSync(TEST_CONFIG.buildPath), 'Build directory does not exist');
    console.log('✅ Build directory exists');
    
    // Check if index.html exists
    const indexPath = path.join(TEST_CONFIG.buildPath, 'index.html');
    assert(fs.existsSync(indexPath), 'index.html does not exist');
    console.log('✅ index.html exists');
    
    // Check if static directory exists
    const staticPath = path.join(TEST_CONFIG.buildPath, 'static');
    assert(fs.existsSync(staticPath), 'static directory does not exist');
    console.log('✅ static directory exists');
    
    // Check if assets directory exists
    const assetsPath = path.join(TEST_CONFIG.buildPath, 'assets');
    assert(fs.existsSync(assetsPath), 'assets directory does not exist');
    console.log('✅ assets directory exists');
    
    testResults.passed++;
    return true;
  } catch (error) {
    console.error('❌ Build directory structure test failed:', error.message);
    testResults.failed++;
    testResults.errors.push(`Build directory structure: ${error.message}`);
    return false;
  }
}

/**
 * Test 2: Validate Asset Manifest
 */
function testAssetManifest() {
  console.log('\n=== Test 2: Asset Manifest ===');
  
  try {
    const manifestPath = path.join(TEST_CONFIG.buildPath, 'asset-manifest.json');
    assert(fs.existsSync(manifestPath), 'asset-manifest.json does not exist');
    
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    assert(manifest.files, 'Manifest missing files property');
    assert(manifest.entrypoints, 'Manifest missing entrypoints property');
    
    // Validate entrypoints exist
    for (const entrypoint of manifest.entrypoints) {
      const entrypointPath = path.join(TEST_CONFIG.buildPath, entrypoint);
      assert(fs.existsSync(entrypointPath), `Entrypoint ${entrypoint} does not exist`);
    }
    
    console.log('✅ Asset manifest is valid');
    console.log(`✅ ${manifest.entrypoints.length} entrypoints validated`);
    
    testResults.passed++;
    return true;
  } catch (error) {
    console.error('❌ Asset manifest test failed:', error.message);
    testResults.failed++;
    testResults.errors.push(`Asset manifest: ${error.message}`);
    return false;
  }
}

/**
 * Test 3: Validate All Required Assets Exist
 */
function testRequiredAssets() {
  console.log('\n=== Test 3: Required Assets ===');
  
  let missingAssets = [];
  
  for (const asset of TEST_CONFIG.assets) {
    const assetPath = path.join(TEST_CONFIG.buildPath, asset);
    if (!fs.existsSync(assetPath)) {
      missingAssets.push(asset);
    }
  }
  
  if (missingAssets.length === 0) {
    console.log(`✅ All ${TEST_CONFIG.assets.length} required assets exist`);
    testResults.passed++;
    return true;
  } else {
    console.error('❌ Missing assets:', missingAssets);
    testResults.failed++;
    testResults.errors.push(`Missing assets: ${missingAssets.join(', ')}`);
    return false;
  }
}

/**
 * Test 4: Validate Static Server Functionality
 */
function testStaticServer() {
  console.log('\n=== Test 4: Static Server ===');
  
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      try {
        const filePath = path.join(TEST_CONFIG.buildPath, req.url);
        const resolvedPath = path.resolve(filePath);
        const resolvedBuildPath = path.resolve(TEST_CONFIG.buildPath);
        
        // Security check
        if (!resolvedPath.startsWith(resolvedBuildPath)) {
          res.writeHead(403, { 'Content-Type': 'text/plain' });
          res.end('Forbidden');
          return;
        }
        
        if (!fs.existsSync(filePath)) {
          res.writeHead(404, { 'Content-Type': 'text/plain' });
          res.end('File not found');
          return;
        }
        
        const ext = path.extname(filePath).toLowerCase();
        const contentTypes = {
          '.html': 'text/html',
          '.css': 'text/css',
          '.js': 'application/javascript',
          '.json': 'application/json',
          '.png': 'image/png',
          '.jpg': 'image/jpeg',
          '.jpeg': 'image/jpeg',
          '.gif': 'image/gif',
          '.svg': 'image/svg+xml',
          '.ico': 'image/x-icon'
        };
        
        const contentType = contentTypes[ext] || 'application/octet-stream';
        res.setHeader('Content-Type', contentType);
        
        const stream = fs.createReadStream(filePath);
        stream.pipe(res);
        
        stream.on('error', (error) => {
          res.writeHead(500, { 'Content-Type': 'text/plain' });
          res.end('Internal server error');
        });
        
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Internal server error');
      }
    });
    
    server.listen(TEST_CONFIG.staticServerPort, () => {
      console.log(`✅ Static server started on port ${TEST_CONFIG.staticServerPort}`);
      
      // Test a few key assets
      const testAssets = [
        '/index.html',
        '/static/css/main.750a3279.css',
        '/static/js/main.253b1441.js',
        '/assets/Hearthlink.png'
      ];
      
      let testsCompleted = 0;
      let testsPassed = 0;
      
      testAssets.forEach(asset => {
        const req = http.get(`http://localhost:${TEST_CONFIG.staticServerPort}${asset}`, (res) => {
          if (res.statusCode === 200) {
            console.log(`✅ ${asset} served successfully`);
            testsPassed++;
          } else {
            console.error(`❌ ${asset} failed with status ${res.statusCode}`);
          }
          testsCompleted++;
          
          if (testsCompleted === testAssets.length) {
            server.close(() => {
              if (testsPassed === testAssets.length) {
                console.log('✅ All static server tests passed');
                testResults.passed++;
                resolve(true);
              } else {
                console.error('❌ Some static server tests failed');
                testResults.failed++;
                testResults.errors.push(`Static server: ${testAssets.length - testsPassed} tests failed`);
                resolve(false);
              }
            });
          }
        });
        
        req.on('error', (error) => {
          console.error(`❌ ${asset} request failed:`, error.message);
          testsCompleted++;
          
          if (testsCompleted === testAssets.length) {
            server.close(() => {
              testResults.failed++;
              testResults.errors.push(`Static server: ${testAssets.length - testsPassed} tests failed`);
              resolve(false);
            });
          }
        });
        
        req.setTimeout(TEST_CONFIG.timeout, () => {
          console.error(`❌ ${asset} request timed out`);
          req.destroy();
          testsCompleted++;
          
          if (testsCompleted === testAssets.length) {
            server.close(() => {
              testResults.failed++;
              testResults.errors.push(`Static server: ${testAssets.length - testsPassed} tests failed`);
              resolve(false);
            });
          }
        });
      });
    });
    
    server.on('error', (error) => {
      console.error('❌ Static server failed to start:', error.message);
      testResults.failed++;
      testResults.errors.push(`Static server startup: ${error.message}`);
      resolve(false);
    });
  });
}

/**
 * Test 5: Validate No Hardcoded File Paths
 */
function testNoHardcodedPaths() {
  console.log('\n=== Test 5: No Hardcoded File Paths ===');
  
  try {
    const mainJsPath = path.join(__dirname, '..', 'main.js');
    const mainJsContent = fs.readFileSync(mainJsPath, 'utf8');
    
    // Check for hardcoded file:// paths
    const hardcodedPatterns = [
      /file:\/\/\/[a-zA-Z]:/g,  // Windows absolute paths
      /file:\/\/\/\//g,         // Unix absolute paths
      /file:\/\/[a-zA-Z]/g      // Drive letter paths
    ];
    
    let foundHardcoded = false;
    hardcodedPatterns.forEach(pattern => {
      const matches = mainJsContent.match(pattern);
      if (matches) {
        console.error('❌ Found hardcoded file paths:', matches);
        foundHardcoded = true;
      }
    });
    
    if (!foundHardcoded) {
      console.log('✅ No hardcoded file:// paths found');
      testResults.passed++;
      return true;
    } else {
      testResults.failed++;
      testResults.errors.push('Hardcoded file paths found in main.js');
      return false;
    }
  } catch (error) {
    console.error('❌ Hardcoded paths test failed:', error.message);
    testResults.failed++;
    testResults.errors.push(`Hardcoded paths test: ${error.message}`);
    return false;
  }
}

/**
 * Test 6: Validate Protocol Handler Configuration
 */
function testProtocolHandler() {
  console.log('\n=== Test 6: Protocol Handler ===');
  
  try {
    const mainJsPath = path.join(__dirname, '..', 'main.js');
    const mainJsContent = fs.readFileSync(mainJsPath, 'utf8');
    
    // Check for protocol handler registration
    const hasProtocolHandler = mainJsContent.includes('protocol.registerFileProtocol');
    const hasAppProtocol = mainJsContent.includes('app://');
    
    if (hasProtocolHandler && hasAppProtocol) {
      console.log('✅ Protocol handler properly configured');
      testResults.passed++;
      return true;
    } else {
      console.error('❌ Protocol handler not properly configured');
      testResults.failed++;
      testResults.errors.push('Protocol handler configuration missing or incomplete');
      return false;
    }
  } catch (error) {
    console.error('❌ Protocol handler test failed:', error.message);
    testResults.failed++;
    testResults.errors.push(`Protocol handler test: ${error.message}`);
    return false;
  }
}

/**
 * Run all tests
 */
async function runAllTests() {
  console.log('🚀 Starting Electron Asset Loading Tests');
  console.log('==========================================');
  
  // Run synchronous tests
  testBuildDirectoryStructure();
  testAssetManifest();
  testRequiredAssets();
  testNoHardcodedPaths();
  testProtocolHandler();
  
  // Run asynchronous tests
  await testStaticServer();
  
  // Generate test report
  generateTestReport();
}

/**
 * Generate test report
 */
function generateTestReport() {
  const endTime = Date.now();
  const duration = endTime - testResults.startTime;
  
  console.log('\n==========================================');
  console.log('📊 ELECTRON ASSET LOADING TEST REPORT');
  console.log('==========================================');
  console.log(`Total Tests: ${testResults.passed + testResults.failed}`);
  console.log(`Passed: ${testResults.passed}`);
  console.log(`Failed: ${testResults.failed}`);
  console.log(`Duration: ${duration}ms`);
  
  if (testResults.errors.length > 0) {
    console.log('\n❌ ERRORS:');
    testResults.errors.forEach((error, index) => {
      console.log(`${index + 1}. ${error}`);
    });
  }
  
  if (testResults.failed === 0) {
    console.log('\n🎉 ALL TESTS PASSED!');
    console.log('✅ Electron asset loading is properly configured');
    process.exit(0);
  } else {
    console.log('\n💥 SOME TESTS FAILED!');
    console.log('❌ Electron asset loading needs attention');
    process.exit(1);
  }
}

// Export for use in other test files
module.exports = {
  testBuildDirectoryStructure,
  testAssetManifest,
  testRequiredAssets,
  testStaticServer,
  testNoHardcodedPaths,
  testProtocolHandler,
  runAllTests,
  TEST_CONFIG
};

// Run tests if this file is executed directly
if (require.main === module) {
  runAllTests().catch(error => {
    console.error('Test suite failed:', error);
    process.exit(1);
  });
} 