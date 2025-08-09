#!/usr/bin/env node

/**
 * Launcher Validation Script
 * Tests all requirements from the validation checklist
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Hearthlink Launcher Validation Checklist\n');

// Test results tracking
const results = {
  core: {},
  functionality: {},
  integration: {},
  startup: {}
};

// Helper function to log results
function logResult(category, test, passed, details = '') {
  const status = passed ? '✅' : '❌';
  console.log(`${status} ${test}: ${passed ? 'PASSED' : 'FAILED'}`);
  if (details) {
    console.log(`   ${details}`);
  }
  results[category][test] = { passed, details };
  return passed;
}

// Core Requirements Tests
console.log('\n📋 Core Requirements:');

// Test 1: Check if main.js exists and is valid
try {
  const mainJsPath = path.join(__dirname, '..', 'main.js');
  const mainJsContent = fs.readFileSync(mainJsPath, 'utf8');
  const hasCreateWindow = mainJsContent.includes('createWindow');
  const hasElectronImports = mainJsContent.includes('require(\'electron\')');
  
  logResult('core', 'main.js exists and is valid', hasCreateWindow && hasElectronImports);
} catch (error) {
  logResult('core', 'main.js exists and is valid', false, error.message);
}

// Test 2: Check if package.json has correct scripts
try {
  const packageJsonPath = path.join(__dirname, '..', 'package.json');
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const hasStartScript = packageJson.scripts && packageJson.scripts.start;
  const hasBuildScript = packageJson.scripts && packageJson.scripts.build;
  
  logResult('core', 'package.json has correct scripts', hasStartScript && hasBuildScript);
} catch (error) {
  logResult('core', 'package.json has correct scripts', false, error.message);
}

// Test 3: Check if React app builds successfully
try {
  console.log('   Building React app...');
  execSync('npm run build', { cwd: path.join(__dirname, '..'), stdio: 'pipe' });
  const buildDir = path.join(__dirname, '..', 'build');
  const hasIndexHtml = fs.existsSync(path.join(buildDir, 'index.html'));
  const hasStaticDir = fs.existsSync(path.join(buildDir, 'static'));
  
  logResult('core', 'React app builds successfully', hasIndexHtml && hasStaticDir);
} catch (error) {
  logResult('core', 'React app builds successfully', false, error.message);
}

// Functionality Checks
console.log('\n🔧 Functionality Checks:');

// Test 4: Check if SynapseInterface component exists
try {
  const synapseInterfacePath = path.join(__dirname, '..', 'src', 'components', 'SynapseInterface.js');
  const synapseInterfaceExists = fs.existsSync(synapseInterfacePath);
  
  logResult('functionality', 'SynapseInterface component exists', synapseInterfaceExists);
} catch (error) {
  logResult('functionality', 'SynapseInterface component exists', false, error.message);
}

// Test 5: Check if SynapseInterface CSS exists
try {
  const synapseInterfaceCssPath = path.join(__dirname, '..', 'src', 'components', 'SynapseInterface.css');
  const synapseInterfaceCssExists = fs.existsSync(synapseInterfaceCssPath);
  
  logResult('functionality', 'SynapseInterface CSS exists', synapseInterfaceCssExists);
} catch (error) {
  logResult('functionality', 'SynapseInterface CSS exists', false, error.message);
}

// Test 6: Check if App.js includes Synapse interface
try {
  const appJsPath = path.join(__dirname, '..', 'src', 'App.js');
  const appJsContent = fs.readFileSync(appJsPath, 'utf8');
  const hasSynapseImport = appJsContent.includes('SynapseInterface');
  const hasSynapseButton = appJsContent.includes('synapse');
  
  logResult('functionality', 'App.js includes Synapse interface', hasSynapseImport && hasSynapseButton);
} catch (error) {
  logResult('functionality', 'App.js includes Synapse interface', false, error.message);
}

// Test 7: Check if VoiceInterface component exists
try {
  const voiceInterfacePath = path.join(__dirname, '..', 'src', 'components', 'VoiceInterface.js');
  const voiceInterfaceExists = fs.existsSync(voiceInterfacePath);
  
  logResult('functionality', 'VoiceInterface component exists', voiceInterfaceExists);
} catch (error) {
  logResult('functionality', 'VoiceInterface component exists', false, error.message);
}

// Test 8: Check if AccessibilityPanel component exists
try {
  const accessibilityPanelPath = path.join(__dirname, '..', 'src', 'components', 'AccessibilityPanel.js');
  const accessibilityPanelExists = fs.existsSync(accessibilityPanelPath);
  
  logResult('functionality', 'AccessibilityPanel component exists', accessibilityPanelExists);
} catch (error) {
  logResult('functionality', 'AccessibilityPanel component exists', false, error.message);
}

// Integration Hooks
console.log('\n🔗 Integration Hooks:');

// Test 9: Check if logs directory exists
try {
  const logsDir = path.join(__dirname, '..', 'logs');
  const logsDirExists = fs.existsSync(logsDir);
  
  logResult('integration', 'Logs directory exists', logsDirExists);
} catch (error) {
  logResult('integration', 'Logs directory exists', false, error.message);
}

// Test 10: Check if preload.js exists and has required APIs
try {
  const preloadPath = path.join(__dirname, '..', 'preload.js');
  const preloadContent = fs.readFileSync(preloadPath, 'utf8');
  const hasElectronAPI = preloadContent.includes('electronAPI');
  const hasVoiceCommands = preloadContent.includes('voiceCommands');
  const hasAccessibility = preloadContent.includes('accessibility');
  
  logResult('integration', 'preload.js has required APIs', hasElectronAPI && hasVoiceCommands && hasAccessibility);
} catch (error) {
  logResult('integration', 'preload.js has required APIs', false, error.message);
}

// Test 11: Check if assets directory has required images
try {
  const assetsDir = path.join(__dirname, '..', 'src', 'assets');
  const requiredImages = ['Alden.png', 'Alice.png', 'Core.png', 'Synapse.png', 'header-logo.png'];
  const existingImages = fs.readdirSync(assetsDir).filter(file => file.endsWith('.png'));
  const hasRequiredImages = requiredImages.every(img => existingImages.includes(img));
  
  logResult('integration', 'Assets directory has required images', hasRequiredImages, 
    `Found: ${existingImages.join(', ')}`);
} catch (error) {
  logResult('integration', 'Assets directory has required images', false, error.message);
}

// Startup Behavior
console.log('\n🚀 Startup Behavior:');

// Test 12: Check if main.js has proper security settings
try {
  const mainJsPath = path.join(__dirname, '..', 'main.js');
  const mainJsContent = fs.readFileSync(mainJsPath, 'utf8');
  const hasSecuritySettings = mainJsContent.includes('webSecurity: true') && 
                             mainJsContent.includes('contextIsolation: true') &&
                             mainJsContent.includes('nodeIntegration: false');
  
  logResult('startup', 'main.js has proper security settings', hasSecuritySettings);
} catch (error) {
  logResult('startup', 'main.js has proper security settings', false, error.message);
}

// Test 13: Check if main.js has error handling
try {
  const mainJsPath = path.join(__dirname, '..', 'main.js');
  const mainJsContent = fs.readFileSync(mainJsPath, 'utf8');
  const hasErrorHandling = mainJsContent.includes('uncaughtException') && 
                          mainJsContent.includes('unhandledRejection');
  
  logResult('startup', 'main.js has error handling', hasErrorHandling);
} catch (error) {
  logResult('startup', 'main.js has error handling', false, error.message);
}

// Test 14: Check if package.json has correct dependencies
try {
  const packageJsonPath = path.join(__dirname, '..', 'package.json');
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  const hasReact = packageJson.dependencies && packageJson.dependencies.react;
  const hasElectron = packageJson.dependencies && packageJson.dependencies.electron;
  const hasElectronBuilder = packageJson.dependencies && packageJson.dependencies['electron-builder'];
  
  logResult('startup', 'package.json has correct dependencies', hasReact && hasElectron && hasElectronBuilder);
} catch (error) {
  logResult('startup', 'package.json has correct dependencies', false, error.message);
}

// Test 15: Check if build directory structure is correct
try {
  const buildDir = path.join(__dirname, '..', 'build');
  if (fs.existsSync(buildDir)) {
    const buildFiles = fs.readdirSync(buildDir);
    const hasIndexHtml = buildFiles.includes('index.html');
    const hasStaticDir = fs.existsSync(path.join(buildDir, 'static'));
    
    logResult('startup', 'Build directory structure is correct', hasIndexHtml && hasStaticDir);
  } else {
    logResult('startup', 'Build directory structure is correct', false, 'Build directory does not exist');
  }
} catch (error) {
  logResult('startup', 'Build directory structure is correct', false, error.message);
}

// Summary
console.log('\n📊 Validation Summary:');

let totalTests = 0;
let passedTests = 0;

Object.keys(results).forEach(category => {
  console.log(`\n${category.toUpperCase()}:`);
  Object.keys(results[category]).forEach(test => {
    totalTests++;
    if (results[category][test].passed) {
      passedTests++;
    }
    const status = results[category][test].passed ? '✅' : '❌';
    console.log(`  ${status} ${test}`);
  });
});

const passRate = ((passedTests / totalTests) * 100).toFixed(1);
console.log(`\n🎯 Overall Pass Rate: ${passedTests}/${totalTests} (${passRate}%)`);

if (passedTests === totalTests) {
  console.log('\n🎉 All tests passed! Launcher is ready for use.');
  process.exit(0);
} else {
  console.log('\n⚠️  Some tests failed. Please review the issues above.');
  process.exit(1);
} 