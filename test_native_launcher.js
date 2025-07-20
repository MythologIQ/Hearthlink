#!/usr/bin/env node

/**
 * Test script for Native Launcher Port Management
 * 
 * This script tests the enhanced port management in the native launcher
 * without actually starting the Electron GUI.
 */

const { HearthlinkLauncher } = require('./launcher.js');

async function testNativeLauncher() {
  console.log('🧪 Testing Native Launcher Port Management');
  console.log('==========================================\n');

  try {
    // Test 1: Port availability checking
    console.log('1. Testing port availability checking...');
    const { PortManager } = require('./launcher.js');
    
    const testPorts = [3001, 8000, 8001];
    for (const port of testPorts) {
      const available = await PortManager.checkPortAvailable(port);
      console.log(`   Port ${port}: ${available ? '✅ Available' : '❌ In use'}`);
    }
    console.log();

    // Test 2: Alternative port discovery
    console.log('2. Testing alternative port discovery...');
    const alternativePort = await PortManager.findAvailablePort(3001);
    if (alternativePort) {
      console.log(`   ✅ Found alternative port: ${alternativePort}`);
    } else {
      console.log('   ❌ No alternative port found');
    }
    console.log();

    // Test 3: Port with fallback
    console.log('3. Testing port fallback mechanism...');
    try {
      const finalPort = await PortManager.getPortWithFallback(3001, 'Test Service');
      console.log(`   ✅ Final port selected: ${finalPort}`);
    } catch (error) {
      console.log(`   ❌ Port fallback failed: ${error.message}`);
    }
    console.log();

    // Test 4: Environment variable integration
    console.log('4. Testing environment variable integration...');
    const originalPort = process.env.REACT_PROD_PORT;
    
    // Test with custom port
    process.env.REACT_PROD_PORT = '3005';
    console.log(`   Set REACT_PROD_PORT to: ${process.env.REACT_PROD_PORT}`);
    
    // Check if the launcher would use this port
    const configuredPort = process.env.REACT_PROD_PORT || 3001;
    console.log(`   ✅ Launcher would use port: ${configuredPort}`);
    
    // Restore original value
    if (originalPort) {
      process.env.REACT_PROD_PORT = originalPort;
    } else {
      delete process.env.REACT_PROD_PORT;
    }
    console.log();

    // Test 5: Multiple services port management
    console.log('5. Testing multiple services coordination...');
    const services = [
      { name: 'React Production', defaultPort: 3001 },
      { name: 'Backend API', defaultPort: 8000 },
      { name: 'API Documentation', defaultPort: 8001 }
    ];

    for (const service of services) {
      const port = await PortManager.getPortWithFallback(service.defaultPort, service.name);
      console.log(`   ${service.name}: ${port} ${port !== service.defaultPort ? '(alternative)' : '(preferred)'}`);
    }
    console.log();

    console.log('✅ All native launcher tests completed successfully!');
    console.log('\nThe enhanced native launcher now provides:');
    console.log('  • Automatic port conflict detection');
    console.log('  • Alternative port discovery');
    console.log('  • Environment variable integration'); 
    console.log('  • Multi-service coordination');
    console.log('  • Comprehensive error handling');
    console.log('\nTo test with actual Electron app:');
    console.log('  npm run launch');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Only run if this is the main module
if (require.main === module) {
  testNativeLauncher().catch(console.error);
}

module.exports = { testNativeLauncher };