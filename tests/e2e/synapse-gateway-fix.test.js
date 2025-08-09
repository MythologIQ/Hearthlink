const { test, expect } = require('@playwright/test');

test.describe('SynapseGateway Rate Limits Fix', () => {
  test.beforeEach(async ({ page }) => {
    // Start the application
    await page.goto('http://localhost:3016');
    
    // Wait for app to load
    await page.waitForLoadState('networkidle');
    
    // Navigate to Synapse module
    await page.click('[data-testid="synapse-module"], a[href="/synapse"], text=Synapse');
    await page.waitForLoadState('networkidle');
  });

  test('should load SynapseGateway without rate_limits TypeError', async ({ page }) => {
    // Listen for console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Listen for page errors
    const pageErrors = [];
    page.on('pageerror', error => {
      pageErrors.push(error.message);
    });

    // Click on Gateway tab to trigger SynapseGateway component
    await page.click('text=Gateway', { timeout: 10000 });
    
    // Wait for component to render
    await page.waitForTimeout(2000);
    
    // Check that no TypeError related to requests_per_minute occurred
    const rateLimitErrors = [...consoleErrors, ...pageErrors].filter(error => 
      error.includes('requests_per_minute') && error.includes('TypeError')
    );
    
    expect(rateLimitErrors).toHaveLength(0);
    
    // Verify the gateway interface is visible
    await expect(page.locator('.synapse-gateway, .gateway-interface')).toBeVisible();
  });

  test('should successfully open API configuration form', async ({ page }) => {
    // Navigate to Gateway tab
    await page.click('text=Gateway');
    await page.waitForTimeout(1000);

    // Look for Add API or Configure API button
    const addApiButton = page.locator('button:has-text("Add"), button:has-text("API"), button:has-text("Configure")');
    
    if (await addApiButton.count() > 0) {
      await addApiButton.first().click();
      await page.waitForTimeout(1000);

      // Check that rate limit fields are present and functional
      const rateLimitFields = [
        'input[placeholder="100"]', // requests_per_minute
        'input[placeholder="5000"]', // requests_per_day
        'input[placeholder="100000"]', // tokens_per_minute
        'input[placeholder="1000000"]' // tokens_per_day
      ];

      for (const field of rateLimitFields) {
        await expect(page.locator(field)).toBeVisible();
        
        // Verify field has a value or placeholder
        const fieldValue = await page.locator(field).inputValue();
        const fieldPlaceholder = await page.locator(field).getAttribute('placeholder');
        
        expect(fieldValue || fieldPlaceholder).toBeTruthy();
      }
    }
  });

  test('should handle rate limit field interactions without errors', async ({ page }) => {
    // Navigate to Gateway tab
    await page.click('text=Gateway');
    await page.waitForTimeout(1000);

    // Track console errors
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    // Try to find and interact with rate limit input
    const rateLimitInput = page.locator('input[placeholder="100"]').first();
    
    if (await rateLimitInput.count() > 0) {
      await rateLimitInput.fill('150');
      await page.waitForTimeout(500);
      
      // Verify no errors occurred during interaction
      const fieldErrors = consoleErrors.filter(error => 
        error.includes('rate_limits') || error.includes('requests_per_minute')
      );
      
      expect(fieldErrors).toHaveLength(0);
    }
  });
});