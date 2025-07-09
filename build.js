const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Starting Hearthlink Desktop Build Process...\n');

// Check if we're in the right directory
if (!fs.existsSync('package.json')) {
  console.error('❌ Error: package.json not found. Please run this script from the project root.');
  process.exit(1);
}

// Create necessary directories
const dirs = ['build', 'dist', 'dist/windows'];
dirs.forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    console.log(`📁 Created directory: ${dir}`);
  }
});

// Copy assets to public directory
const assetsDir = 'src/assets';
const publicAssetsDir = 'public/assets';

if (fs.existsSync(assetsDir)) {
  if (!fs.existsSync(publicAssetsDir)) {
    fs.mkdirSync(publicAssetsDir, { recursive: true });
  }
  
  // Copy assets
  const copyAssets = (src, dest) => {
    if (fs.existsSync(src)) {
      if (fs.lstatSync(src).isDirectory()) {
        if (!fs.existsSync(dest)) {
          fs.mkdirSync(dest, { recursive: true });
        }
        fs.readdirSync(src).forEach(file => {
          copyAssets(path.join(src, file), path.join(dest, file));
        });
      } else {
        fs.copyFileSync(src, dest);
      }
    }
  };
  
  copyAssets(assetsDir, publicAssetsDir);
  console.log('📦 Copied assets to public directory');
}

// Create voice directory if it doesn't exist
const voiceDir = 'voice';
if (!fs.existsSync(voiceDir)) {
  fs.mkdirSync(voiceDir, { recursive: true });
  fs.writeFileSync(path.join(voiceDir, 'README.md'), '# Voice Assets\n\nThis directory contains voice-related assets for the Hearthlink application.\n');
  console.log('📁 Created voice directory');
}

// Install dependencies if needed
console.log('\n📦 Installing dependencies...');
try {
  execSync('npm install', { stdio: 'inherit' });
  console.log('✅ Dependencies installed successfully');
} catch (error) {
  console.error('❌ Error installing dependencies:', error.message);
  process.exit(1);
}

// Build React app
console.log('\n🔨 Building React application...');
try {
  execSync('npm run build', { stdio: 'inherit' });
  console.log('✅ React app built successfully');
} catch (error) {
  console.error('❌ Error building React app:', error.message);
  process.exit(1);
}

// Build Electron app
console.log('\n⚡ Building Electron application...');
try {
  execSync('npm run dist-msi', { stdio: 'inherit' });
  console.log('✅ Electron app built successfully');
} catch (error) {
  console.error('❌ Error building Electron app:', error.message);
  process.exit(1);
}

// Check if MSI was created
const msiPath = 'dist/windows/HearthlinkSetup-v1.1.0.msi';
if (fs.existsSync(msiPath)) {
  const stats = fs.statSync(msiPath);
  const fileSizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
  
  console.log('\n🎉 Build completed successfully!');
  console.log(`📦 MSI Package: ${msiPath}`);
  console.log(`📏 File size: ${fileSizeInMB} MB`);
  console.log('\n📋 Package includes:');
  console.log('  ✅ React application (Alden + Dashboard)');
  console.log('  ✅ Voice interface and accessibility tools');
  console.log('  ✅ Documentation (docs/public/)');
  console.log('  ✅ License and README files');
  console.log('  ✅ SBOM and security information');
  console.log('  ✅ Electron runtime');
  console.log('\n🚀 Ready for distribution!');
} else {
  console.error('❌ Error: MSI package not found at expected location');
  process.exit(1);
}

console.log('\n📝 Build Summary:');
console.log('  • Architecture: x64');
console.log('  • Target: Windows 10+');
console.log('  • Package format: MSI');
console.log('  • Installer: HearthlinkSetup-v1.1.0.msi');
console.log('  • Output directory: dist/windows/');
console.log('\n✨ Build process completed!'); 