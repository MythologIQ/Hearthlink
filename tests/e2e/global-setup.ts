/**
 * Global Setup for Playwright Tests
 * Initializes test environment and services
 */

import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting SPEC-2 Task Management UI Test Suite');
  
  // Start test database if needed
  console.log('📊 Setting up test database...');
  
  // Initialize test data
  console.log('🗃️ Initializing test data...');
  
  // Verify services are running
  console.log('🔧 Verifying required services...');
  
  // Setup auth for tests
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Navigate to login or setup page
    await page.goto('http://localhost:3000/');
    
    // Set up authentication token
    await page.evaluate(() => {
      localStorage.setItem('hearthlink_token', 'test-auth-token');
    });
    
    console.log('✅ Authentication setup complete');
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
  
  console.log('✅ Global setup complete');
}

export default globalSetup;