#!/usr/bin/env node

/**
 * Local Tauri Build Test Script
 * 
 * This script simulates the CI build process locally to help developers
 * identify issues before pushing to GitHub Actions.
 * 
 * Usage:
 *   node test-tauri-build.js [--debug] [--msi] [--nsis]
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const isDebug = args.includes('--debug');
const buildMsi = args.includes('--msi') || !args.includes('--nsis');
const buildNsis = args.includes('--nsis') || !args.includes('--msi');

console.log('🧪 Local Tauri Build Test');
console.log('========================\n');

// Helper functions
function runCommand(command, description) {
  console.log(`🔄 ${description}...`);
  try {
    const output = execSync(command, { 
      stdio: 'inherit', 
      cwd: process.cwd(),
      timeout: 300000 // 5 minutes timeout
    });
    console.log(`✅ ${description} completed\n`);
    return true;
  } catch (error) {
    console.error(`❌ ${description} failed:`, error.message);
    return false;
  }
}

function checkFile(filePath, description) {
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${description} found`);
    return true;
  } else {
    console.log(`❌ ${description} not found`);
    return false;
  }
}

function checkRequirements() {
  console.log('🔍 Checking Build Requirements...');
  
  const requirements = [
    { cmd: 'node --version', name: 'Node.js' },
    { cmd: 'npm --version', name: 'NPM' },
    { cmd: 'python --version', name: 'Python' },
    { cmd: 'cargo --version', name: 'Cargo (Rust)' },
    { cmd: 'tauri --version', name: 'Tauri CLI' }
  ];
  
  let allOk = true;
  
  requirements.forEach(req => {
    try {
      const version = execSync(req.cmd, { encoding: 'utf8', stdio: 'pipe' });
      console.log(`✅ ${req.name}: ${version.trim()}`);
    } catch (error) {
      console.log(`❌ ${req.name}: Not found or error`);
      allOk = false;
    }
  });
  
  console.log('');
  return allOk;
}

function main() {
  console.log('Build Configuration:');
  console.log(`- Debug Mode: ${isDebug ? 'ON' : 'OFF'}`);
  console.log(`- Build MSI: ${buildMsi ? 'YES' : 'NO'}`);
  console.log(`- Build NSIS: ${buildNsis ? 'YES' : 'NO'}`);
  console.log('');
  
  // Step 1: Check requirements
  if (!checkRequirements()) {
    console.error('❌ Some build requirements are missing. Please install them first.');
    process.exit(1);
  }
  
  // Step 2: Validate Tauri configuration
  console.log('🔍 Validating Configuration...');
  if (!runCommand('node validate-tauri-config.js', 'Configuration validation')) {
    console.error('❌ Configuration validation failed');
    process.exit(1);
  }
  
  // Step 3: Install dependencies
  if (!runCommand('npm ci', 'Installing NPM dependencies')) {
    console.error('❌ NPM dependency installation failed');
    process.exit(1);
  }
  
  // Step 4: Install Python dependencies
  if (checkFile('requirements.txt', 'requirements.txt')) {
    if (!runCommand('pip install -r requirements.txt', 'Installing Python dependencies')) {
      console.warn('⚠️ Python dependency installation failed - continuing anyway');
    }
  }
  
  // Step 5: Build React frontend
  if (!runCommand('npm run build', 'Building React frontend')) {
    console.error('❌ React build failed');
    process.exit(1);
  }
  
  // Verify build output
  if (!checkFile('build/index.html', 'React build output')) {
    console.error('❌ React build did not produce expected output');
    process.exit(1);
  }
  
  // Step 6: Test Tauri builds
  console.log('🏗️ Testing Tauri Builds...');
  
  const tauriBuildOptions = isDebug ? '--debug' : '';
  let buildSuccess = true;
  
  if (buildMsi) {
    console.log('Building MSI installer...');
    if (!runCommand(`tauri build ${tauriBuildOptions} --bundles msi`, 'MSI build')) {
      buildSuccess = false;
    }
  }
  
  if (buildNsis) {
    console.log('Building NSIS EXE installer...');
    if (!runCommand(`tauri build ${tauriBuildOptions} --bundles nsis`, 'NSIS EXE build')) {
      buildSuccess = false;
    }
  }
  
  // Step 7: Verify build artifacts
  console.log('🔍 Checking Build Artifacts...');
  
  const bundleDir = 'src-tauri/target/' + (isDebug ? 'debug' : 'release') + '/bundle';
  
  if (fs.existsSync(bundleDir)) {
    console.log('✅ Bundle directory found');
    
    if (buildMsi && fs.existsSync(path.join(bundleDir, 'msi'))) {
      console.log('✅ MSI bundle directory found');
      const msiFiles = fs.readdirSync(path.join(bundleDir, 'msi')).filter(f => f.endsWith('.msi'));
      console.log(`✅ MSI files: ${msiFiles.join(', ')}`);
    }
    
    if (buildNsis && fs.existsSync(path.join(bundleDir, 'nsis'))) {
      console.log('✅ NSIS bundle directory found');
      const exeFiles = fs.readdirSync(path.join(bundleDir, 'nsis')).filter(f => f.endsWith('.exe'));
      console.log(`✅ EXE files: ${exeFiles.join(', ')}`);
    }
  } else {
    console.log('❌ Bundle directory not found');
    buildSuccess = false;
  }
  
  // Final summary
  console.log('\n📊 Build Test Summary');
  console.log('====================');
  
  if (buildSuccess) {
    console.log('✅ All builds completed successfully!');
    console.log('📦 Your configuration is ready for GitHub Actions CI/CD');
    console.log('\nNext steps:');
    console.log('1. Commit your changes');
    console.log('2. Push to GitHub');
    console.log('3. Check the GitHub Actions workflow');
    process.exit(0);
  } else {
    console.log('❌ Some builds failed');
    console.log('🔧 Please fix the issues before pushing to GitHub');
    console.log('\nCommon fixes:');
    console.log('- Ensure all dependencies are installed');
    console.log('- Check Tauri configuration syntax');
    console.log('- Verify Python dependencies are correct');
    console.log('- Make sure icons directory exists with required files');
    process.exit(1);
  }
}

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
  console.log('\n⏹️ Build test interrupted by user');
  process.exit(1);
});

// Run the main function
main();