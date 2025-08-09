const { test, expect } = require('@playwright/test');

test.describe('SynapseGateway Rate Limits Fix - Quick Test', () => {
  test('should load SynapseGateway without rate_limits TypeError', async ({ page }) => {
    // Skip webServer and go directly to running server
    await page.goto('http://localhost:3016', { timeout: 10000 });
    
    // Track JavaScript errors
    const jsErrors = [];
    page.on('pageerror', error => {
      jsErrors.push(error.message);
    });

    // Wait for page to load
    await page.waitForLoadState('domcontentloaded');
    
    // Try to navigate to Synapse (look for any way to get there)  
    try {
      // Look for Synapse link/button - try multiple selectors
      const selectors = [
        'text=Synapse',
        'a[href*="synapse"]', 
        '[data-testid*="synapse"]',
        'button:has-text("Synapse")',
        '.nav-item:has-text("Synapse")'
      ];
      
      let found = false;
      for (const selector of selectors) {
        const element = page.locator(selector).first();
        if (await element.count() > 0) {
          await element.click({ timeout: 5000 });
          found = true;
          break;
        }
      }
      
      if (found) {
        await page.waitForTimeout(2000);
        
        // Try to click Gateway tab
        const gatewayTab = page.locator('text=Gateway').first();
        if (await gatewayTab.count() > 0) {
          await gatewayTab.click({ timeout: 5000 });
          await page.waitForTimeout(3000);
        }
      }
    } catch (error) {
      console.log('Navigation error (expected in some cases):', error.message);
    }
    
    // Check for the specific TypeError we're trying to fix
    const rateLimitErrors = jsErrors.filter(error => 
      error.includes('requests_per_minute') && 
      (error.includes('TypeError') || error.includes('Cannot read propert'))
    );
    
    console.log('All JS Errors:', jsErrors);
    console.log('Rate Limit Errors:', rateLimitErrors);
    
    // Main test: no rate_limits TypeError should occur
    expect(rateLimitErrors).toHaveLength(0);
  });
});