/**
 * SPEC-3 Week 3: Feedback UI End-to-End Tests
 * Comprehensive E2E tests for FeedbackButton component and bug reporting workflow
 */

const { test, expect } = require('@playwright/test');

test.describe('FeedbackButton Component', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to a page that has the FeedbackButton component
    await page.goto('/');
    
    // Wait for the feedback button to be visible
    await page.waitForSelector('.feedback-button', { timeout: 10000 });
  });

  test('should display feedback button', async ({ page }) => {
    // Check if feedback button is visible
    const feedbackButton = page.locator('.feedback-button');
    await expect(feedbackButton).toBeVisible();
    
    // Check button text and icon
    await expect(feedbackButton).toContainText('Feedback');
    
    // Check button styling
    await expect(feedbackButton).toHaveCSS('position', 'fixed');
  });

  test('should open modal when feedback button is clicked', async ({ page }) => {
    // Click the feedback button
    await page.click('.feedback-button');
    
    // Check if modal is opened
    const modal = page.locator('.feedback-modal-overlay');
    await expect(modal).toBeVisible();
    
    // Check modal title
    const modalTitle = page.locator('.feedback-modal-header h2');
    await expect(modalTitle).toContainText('Send Feedback');
    
    // Check form elements are present
    await expect(page.locator('input[name="category"]')).toBeVisible();
    await expect(page.locator('#title')).toBeVisible();
    await expect(page.locator('#description')).toBeVisible();
  });

  test('should close modal when close button is clicked', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    await expect(page.locator('.feedback-modal-overlay')).toBeVisible();
    
    // Click close button
    await page.click('.feedback-modal-close');
    
    // Check if modal is closed
    await expect(page.locator('.feedback-modal-overlay')).not.toBeVisible();
  });

  test('should close modal when clicking outside', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    await expect(page.locator('.feedback-modal-overlay')).toBeVisible();
    
    // Click outside the modal (on overlay)
    await page.click('.feedback-modal-overlay', { position: { x: 10, y: 10 } });
    
    // Check if modal is closed
    await expect(page.locator('.feedback-modal-overlay')).not.toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    
    // Try to submit without filling required fields
    await page.click('button[type="submit"]');
    
    // Check for validation errors
    const titleError = page.locator('.error-message').first();
    await expect(titleError).toBeVisible();
    await expect(titleError).toContainText('Title is required');
  });

  test('should show character counts', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    
    // Type in title field
    const titleInput = page.locator('#title');
    await titleInput.fill('Test title');
    
    // Check character count
    const titleCount = page.locator('small').filter({ hasText: '/200 characters' });
    await expect(titleCount).toContainText('10/200 characters');
    
    // Type in description field
    const descInput = page.locator('#description');
    await descInput.fill('Test description');
    
    // Check character count
    const descCount = page.locator('small').filter({ hasText: '/10,000 characters' });
    await expect(descCount).toContainText('16/10,000 characters');
  });

  test('should select different categories', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    
    // Test category selection
    const categories = ['bug', 'feature', 'UI', 'performance'];
    
    for (const category of categories) {
      const categoryOption = page.locator(`input[value="${category}"]`);
      await categoryOption.check();
      await expect(categoryOption).toBeChecked();
    }
  });

  test('should handle file attachments', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    
    // Create a test file
    const testFile = {
      name: 'test.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('Test file content')
    };
    
    // Set up file input
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles([testFile]);
    
    // Check if file appears in attachment list
    const attachmentItem = page.locator('.attachment-item');
    await expect(attachmentItem).toBeVisible();
    await expect(attachmentItem).toContainText('test.txt');
  });

  test('should remove attachments', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    
    // Add a file
    const testFile = {
      name: 'test.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('Test file content')
    };
    
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles([testFile]);
    
    // Wait for attachment to appear
    await expect(page.locator('.attachment-item')).toBeVisible();
    
    // Remove the attachment
    await page.click('.remove-attachment');
    
    // Check if attachment is removed
    await expect(page.locator('.attachment-item')).not.toBeVisible();
  });

  test('should submit feedback successfully', async ({ page }) => {
    // Mock the API response
    await page.route('/api/bugs', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          bug_id: 'BUG_20250801_123456_abc123',
          status: 'submitted',
          message: 'Bug report submitted successfully! Reference ID: BUG_20250801_123456_abc123',
          timestamp: new Date().toISOString()
        })
      });
    });
    
    // Open modal
    await page.click('.feedback-button');
    
    // Fill required fields
    await page.fill('#title', 'Test Bug Report');
    await page.fill('#description', 'This is a detailed description of the test bug report.');
    
    // Select category
    await page.check('input[value="bug"]');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for success message
    const successMessage = page.locator('.feedback-result-success');
    await expect(successMessage).toBeVisible();
    await expect(successMessage).toContainText('Bug report submitted successfully!');
    await expect(successMessage).toContainText('BUG_20250801_123456_abc123');
  });

  test('should handle submission errors', async ({ page }) => {
    // Mock API error response
    await page.route('/api/bugs', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Internal server error'
        })
      });
    });
    
    // Open modal
    await page.click('.feedback-button');
    
    // Fill required fields
    await page.fill('#title', 'Test Bug Report');
    await page.fill('#description', 'This is a test bug report.');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for error message
    const errorMessage = page.locator('.feedback-result-error');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText('Failed to submit feedback');
  });

  test('should show loading state during submission', async ({ page }) => {
    // Mock slow API response
    await page.route('/api/bugs', async (route) => {
      await new Promise(resolve => setTimeout(resolve, 2000)); // 2 second delay
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          bug_id: 'BUG_TEST',
          status: 'submitted',
          message: 'Success',
          timestamp: new Date().toISOString()
        })
      });
    });
    
    // Open modal
    await page.click('.feedback-button');
    
    // Fill form
    await page.fill('#title', 'Loading Test');
    await page.fill('#description', 'Testing loading state');
    
    // Submit form
    const submitButton = page.locator('button[type="submit"]');
    await submitButton.click();
    
    // Check loading state
    await expect(submitButton).toContainText('Submitting...');
    await expect(submitButton).toHaveAttribute('disabled');
    
    // Check for spinner
    const spinner = page.locator('.spinner');
    await expect(spinner).toBeVisible();
  });

  test('should validate file types and sizes', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    
    // Try to upload an invalid file type
    const invalidFile = {
      name: 'test.exe',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('Invalid file content')
    };
    
    // Mock window.alert to capture the message
    let alertMessage = '';
    await page.evaluate(() => {
      window.alert = (message) => {
        window.lastAlert = message;
      };
    });
    
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles([invalidFile]);
    
    // Check if alert was shown (this would need to be adapted based on actual implementation)
    const lastAlert = await page.evaluate(() => window.lastAlert);
    expect(lastAlert).toContain('unsupported type');
  });

  test('should auto-close modal after successful submission', async ({ page }) => {
    // Mock successful API response
    await page.route('/api/bugs', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          bug_id: 'BUG_AUTO_CLOSE_TEST',
          status: 'submitted',
          message: 'Success',
          timestamp: new Date().toISOString()
        })
      });
    });
    
    // Open modal
    await page.click('.feedback-button');
    
    // Fill and submit form
    await page.fill('#title', 'Auto Close Test');
    await page.fill('#description', 'Testing auto-close functionality');
    await page.click('button[type="submit"]');
    
    // Wait for success message
    await expect(page.locator('.feedback-result-success')).toBeVisible();
    
    // Wait for modal to auto-close (3 seconds as per implementation)
    await page.waitForTimeout(3500);
    await expect(page.locator('.feedback-modal-overlay')).not.toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check feedback button on mobile
    const feedbackButton = page.locator('.feedback-button');
    await expect(feedbackButton).toBeVisible();
    
    // Open modal
    await page.click('.feedback-button');
    
    // Check modal responsiveness
    const modal = page.locator('.feedback-modal');
    await expect(modal).toBeVisible();
    
    // Check if category grid stacks vertically on mobile
    const categoryGrid = page.locator('.category-grid');
    const gridColumnCount = await categoryGrid.evaluate(el => 
      window.getComputedStyle(el).gridTemplateColumns
    );
    
    // On mobile, should have single column
    expect(gridColumnCount).toBe('1fr');
  });

  test('should maintain form data when switching categories', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    
    // Fill title and description
    await page.fill('#title', 'Category Switch Test');
    await page.fill('#description', 'Testing if form data persists');
    
    // Select bug category
    await page.check('input[value="bug"]');
    
    // Switch to feature category
    await page.check('input[value="feature"]');
    
    // Check if form data is still there
    await expect(page.locator('#title')).toHaveValue('Category Switch Test');
    await expect(page.locator('#description')).toHaveValue('Testing if form data persists');
  });

  test('should reset form when modal is reopened', async ({ page }) => {
    // Open modal
    await page.click('.feedback-button');
    
    // Fill form
    await page.fill('#title', 'Form Reset Test');
    await page.fill('#description', 'This should be cleared');
    
    // Close modal
    await page.click('.feedback-modal-close');
    
    // Reopen modal
    await page.click('.feedback-button');
    
    // Check if form is reset
    await expect(page.locator('#title')).toHaveValue('');
    await expect(page.locator('#description')).toHaveValue('');
    await expect(page.locator('input[value="bug"]')).toBeChecked(); // Default category
  });
});

test.describe('FeedbackButton Integration', () => {
  test('should include page context in submission', async ({ page }) => {
    let capturedRequest;
    
    // Capture the API request
    await page.route('/api/bugs', async (route) => {
      capturedRequest = route.request();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          bug_id: 'BUG_CONTEXT_TEST',
          status: 'submitted',
          message: 'Success',
          timestamp: new Date().toISOString()
        })
      });
    });
    
    // Navigate to a specific page
    await page.goto('/#/core');
    
    // Open modal and submit
    await page.click('.feedback-button');
    await page.fill('#title', 'Context Test');
    await page.fill('#description', 'Testing page context inclusion');
    await page.click('button[type="submit"]');
    
    // Wait for request to be made
    await page.waitForResponse('/api/bugs');
    
    // Check if page context was included
    const formData = await capturedRequest.postData();
    expect(formData).toContain('#/core'); // URL should be included in page_ctx
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate network error
    await page.route('/api/bugs', async (route) => {
      await route.abort('internetdisconnected');
    });
    
    // Open modal and submit
    await page.click('.feedback-button');
    await page.fill('#title', 'Network Error Test');
    await page.fill('#description', 'Testing network error handling');
    await page.click('button[type="submit"]');
    
    // Check for error message
    const errorMessage = page.locator('.feedback-result-error');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText('Failed to submit feedback');
  });
});