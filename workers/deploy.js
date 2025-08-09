#!/usr/bin/env node

/**
 * Hearthlink Workers Deployment Script
 * 
 * Automated deployment and configuration for Cloudflare Workers API
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Hearthlink Workers API Deployment');
console.log('=====================================\n');

// Configuration
const ENVIRONMENTS = ['development', 'staging', 'production'];
const REQUIRED_SECRETS = [
  'JWT_SECRET',
  'REFRESH_TOKEN_SECRET',
  'HEARTHLINK_BACKEND_URL',
  'ENCRYPTION_KEY'
];

/**
 * Execute command with proper error handling
 */
function runCommand(command, description) {
  console.log(`🔧 ${description}...`);
  try {
    const result = execSync(command, { encoding: 'utf8', stdio: 'inherit' });
    console.log(`✅ ${description} completed\n`);
    return result;
  } catch (error) {
    console.error(`❌ ${description} failed:`, error.message);
    process.exit(1);
  }
}

/**
 * Check if wrangler.toml exists
 */
function checkConfiguration() {
  if (!fs.existsSync('wrangler.toml')) {
    console.log('❌ wrangler.toml not found!');
    console.log('📋 Please copy wrangler.example.toml to wrangler.toml and configure:');
    console.log('   - account_id: Your Cloudflare account ID');
    console.log('   - KV namespace IDs (run: npm run kv:create)');
    console.log('   - Any custom domain routes\n');
    process.exit(1);
  }
  console.log('✅ Configuration file found\n');
}

/**
 * Create KV namespaces if they don't exist
 */
function setupKVNamespaces() {
  console.log('🗄️  Setting up KV namespaces...');
  
  const namespaces = ['SESSIONS', 'CACHE', 'RATE_LIMITS'];
  
  namespaces.forEach(namespace => {
    try {
      console.log(`   Creating ${namespace} namespace...`);
      execSync(`wrangler kv:namespace create ${namespace}`, { stdio: 'inherit' });
      execSync(`wrangler kv:namespace create ${namespace} --preview`, { stdio: 'inherit' });
    } catch (error) {
      console.log(`   ℹ️  ${namespace} namespace may already exist`);
    }
  });
  
  console.log('\n📝 Make sure to update wrangler.toml with the KV namespace IDs shown above!\n');
}

/**
 * Set up secrets
 */
function setupSecrets(environment = '') {
  console.log(`🔐 Setting up secrets${environment ? ` for ${environment}` : ''}...`);
  
  REQUIRED_SECRETS.forEach(secret => {
    const envFlag = environment ? `--env ${environment}` : '';
    console.log(`   Setting ${secret}...`);
    console.log(`   Run: wrangler secret put ${secret} ${envFlag}`);
  });
  
  console.log('\n⚠️  You\'ll need to manually set each secret using the commands above.\n');
}

/**
 * Deploy to specific environment
 */
function deploy(environment) {
  const envFlag = environment ? `--env ${environment}` : '';
  const deployCommand = `wrangler deploy ${envFlag}`;
  
  runCommand(deployCommand, `Deploying to ${environment || 'development'}`);
  
  console.log(`🎉 Deployment to ${environment || 'development'} completed!`);
  
  if (environment === 'production') {
    console.log('\n🌍 Your Hearthlink Workers API is now live globally!');
  }
}

/**
 * Main deployment flow
 */
function main() {
  const environment = process.argv[2];
  
  if (environment && !ENVIRONMENTS.includes(environment)) {
    console.log(`❌ Invalid environment: ${environment}`);
    console.log(`   Valid options: ${ENVIRONMENTS.join(', ')}`);
    process.exit(1);
  }
  
  // Pre-deployment checks
  checkConfiguration();
  
  // Setup flow
  if (process.argv.includes('--setup')) {
    console.log('🔧 Running first-time setup...\n');
    setupKVNamespaces();
    setupSecrets(environment);
    console.log('✅ Setup completed! Now run deploy again without --setup flag.');
    return;
  }
  
  // Deployment flow
  runCommand('npm run lint', 'Running linter');
  runCommand('npm run test', 'Running tests');
  
  deploy(environment);
  
  console.log('\n📊 Post-deployment verification:');
  console.log('   - Check Workers dashboard for logs');
  console.log('   - Test API endpoints');  
  console.log('   - Monitor performance metrics\n');
}

// Handle command line arguments
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log('Hearthlink Workers Deployment Script\n');
  console.log('Usage:');
  console.log('  node deploy.js [environment] [options]\n');
  console.log('Environments:');
  console.log('  development  - Deploy to dev environment');
  console.log('  staging      - Deploy to staging environment');
  console.log('  production   - Deploy to production environment\n');
  console.log('Options:');
  console.log('  --setup      - Run first-time setup (KV namespaces, secrets)');
  console.log('  --help, -h   - Show this help message\n');
  console.log('Examples:');
  console.log('  node deploy.js --setup                  # First-time setup');
  console.log('  node deploy.js development              # Deploy to dev');
  console.log('  node deploy.js production               # Deploy to prod');
  process.exit(0);
}

main();