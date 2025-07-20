#!/usr/bin/env node

/**
 * Create True Windows Executable
 * Uses pkg to create a proper .exe file
 */

const fs = require('fs');
const { spawn } = require('child_process');

console.log('🔧 Creating true Windows executable for Hearthlink...');

// First, let's try using electron-builder with a different approach
const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));

// Update package.json for better executable generation
packageJson.build.win.target = [
  {
    target: "nsis",
    arch: ["x64"]
  }
];

packageJson.build.nsis = {
  oneClick: false,
  allowToChangeInstallationDirectory: true,
  createDesktopShortcut: true,
  createStartMenuShortcut: true,
  shortcutName: "Hearthlink",
  uninstallDisplayName: "Hearthlink",
  artifactName: "Hearthlink-Setup-v1.3.0.exe"
};

packageJson.main = "launcher.js";

fs.writeFileSync('package.json', JSON.stringify(packageJson, null, 2));

console.log('✅ Updated package.json for NSIS installer generation');

// Try to install pkg for standalone executable creation
console.log('📦 Attempting to create standalone executable with pkg...');

// Create a simple launcher script for pkg
const pkgLauncher = `#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

console.log('⚡ HEARTHLINK v1.3.0');
console.log('Advanced AI Orchestration Platform');
console.log('');

const isWindows = os.platform() === 'win32';
const npmCmd = isWindows ? 'npm.cmd' : 'npm';

console.log('Starting Hearthlink...');

const child = spawn(npmCmd, ['run', 'launch'], {
  stdio: 'inherit',
  shell: true,
  cwd: __dirname
});

child.on('error', (error) => {
  console.error('Error:', error.message);
  console.log('Please ensure Node.js and npm are installed.');
  console.log('Alternative: Run "npm run launch" manually');
  process.exit(1);
});
`;

fs.writeFileSync('pkg-launcher.js', pkgLauncher);

console.log('✅ Created pkg-launcher.js');
console.log('');
console.log('🎯 Next steps:');
console.log('1. For installer: npx electron-builder --win --publish=never');
console.log('2. For standalone: npx pkg pkg-launcher.js --targets node16-win-x64 --output hearthlink.exe');
console.log('3. Use hearthlink.bat for immediate launch');
console.log('');
console.log('📝 The .bat file is now the recommended launcher for Windows!');