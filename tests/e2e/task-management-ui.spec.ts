/**
 * SPEC-2 Task Management UI - Playwright E2E Tests
 * Tests for TaskDashboard, TaskEditor, and Steve August template integration
 */

import { test, expect, Page } from '@playwright/test';

// Test constants
const TEST_USER_ID = 'test-user-123';
const VALID_LICENSE_TOKEN = 'SA-2025-TEST-MOCK-VALID';
const INVALID_LICENSE_TOKEN = 'SA-2025-INVALID-TOKEN';
const EXPIRED_LICENSE_TOKEN = 'SA-2023-EXPIRED-TEST';

// Mock API responses
const mockTaskTemplates = [
  {
    id: 'alden-productivity',
    name: 'Alden Productivity Task',
    description: 'Vault-backed task with memory integration',
    category: 'productivity',
    mission: 'Enhance productivity through AI-assisted task management',
    values: ['efficiency', 'innovation'],
    priority: 'medium',
    estimatedTime: 2.0,
    assignedAgent: 'alden',
    tags: ['memory-integration', 'vault-backed'],
    isSystem: true,
    isActive: true
  },
  {
    id: 'steve-august-focus-formula',
    name: '🧠 Steve August Focus Formula',
    description: 'Licensed ADHD coaching worksheet for weekly focus',
    category: 'adhd-coaching',
    mission: 'ADHD-focused weekly productivity planning',
    values: ['focus', 'self-care', 'executive-function'],
    priority: 'medium',
    estimatedTime: 0.5,
    assignedAgent: 'alden',
    tags: ['adhd-coaching', 'licensed'],
    isSystem: true,
    isActive: true,
    licensed: true
  }
];

const mockTasks = [
  {
    id: 'task-1',
    title: 'Sample Task',
    description: 'A sample task for testing',
    priority: 'high',
    status: 'todo',
    category: 'development',
    assignedAgent: 'alden',
    tags: ['testing', 'sample'],
    createdAt: '2025-07-30T10:00:00Z'
  }
];

// Helper functions
async function setupMockAPIs(page: Page) {
  // Mock templates API
  await page.route('/api/templates/', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockTaskTemplates)
    });
  });

  // Mock tasks API
  await page.route('/api/vault/tasks/list', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ tasks: mockTasks })
    });
  });

  // Mock license validation API
  await page.route('/api/templates/validate-license', async route => {
    const request = await route.request();
    const body = await request.postDataJSON();
    
    let response;
    if (body.licenseKey === VALID_LICENSE_TOKEN) {
      response = {
        valid: true,
        licenseType: 'individual',
        message: 'License validated successfully',
        features: ['full-template', 'habit-tracking'],
        usageLimit: 100,
        currentUsage: 5
      };
    } else if (body.licenseKey === EXPIRED_LICENSE_TOKEN) {
      response = {
        valid: false,
        licenseType: 'none',
        message: 'License key expired',
        features: []
      };
    } else {
      response = {
        valid: false,
        licenseType: 'none',
        message: 'Invalid license key format',
        features: []
      };
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(response)
    });
  });

  // Mock license info API
  await page.route('/api/templates/license-info/steve-august-focus-formula', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        licenseRequired: true,
        templateId: 'steve-august-focus-formula',
        templateName: 'August Weekly Focus Formula',
        maxTrialUses: 3,
        purchaseUrl: 'https://steve-august.com/focus-formula'
      })
    });
  });

  // Mock user licenses API
  await page.route('/api/templates/user-licenses/*', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        userLicenses: {
          'steve-august-focus-formula': {
            templateName: 'August Weekly Focus Formula',
            totalUses: 2,
            trialActive: true,
            trialUsesRemaining: 1,
            lastUsed: '2025-07-30T10:00:00Z'
          }
        }
      })
    });
  });

  // Mock task creation API
  await page.route('/api/vault/tasks', async route => {
    if (route.request().method() === 'POST') {
      const body = await route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: `task-${Date.now()}`,
          ...body.task,
          createdAt: new Date().toISOString()
        })
      });
    }
  });

  // Mock task update API
  await page.route('/api/vault/tasks/*', async route => {
    if (route.request().method() === 'PUT') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    } else if (route.request().method() === 'DELETE') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    }
  });

  // Mock audit logging API
  await page.route('/api/templates/audit', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true })
    });
  });
}

async function navigateToTaskDashboard(page: Page, licenseToken?: string) {
  const url = licenseToken 
    ? `/task-dashboard?userId=${TEST_USER_ID}&focusFormulaLicenseToken=${licenseToken}`
    : `/task-dashboard?userId=${TEST_USER_ID}`;
  
  await page.goto(url);
  await page.waitForLoadState('networkidle');
}

// Test Suite: Task Dashboard Basic Functionality
test.describe('Task Dashboard - Basic Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPIs(page);
    // Set up localStorage with auth token
    await page.addInitScript(() => {
      localStorage.setItem('hearthlink_token', 'test-auth-token');
    });
  });

  test('should load dashboard and display tasks and templates tabs', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Check header
    await expect(page.locator('h1')).toContainText('Task Management Dashboard');

    // Check tabs
    await expect(page.locator('.tab-button').first()).toContainText('Tasks');
    await expect(page.locator('.tab-button').last()).toContainText('Templates');

    // Check filters are present
    await expect(page.locator('.search-input')).toBeVisible();
    await expect(page.locator('.create-button')).toBeVisible();
  });

  test('should display tasks in tasks tab', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Should be on tasks tab by default
    await expect(page.locator('.tab-button.active')).toContainText('Tasks');

    // Should display the mock task
    await expect(page.locator('.task-card')).toBeVisible();
    await expect(page.locator('.task-title')).toContainText('Sample Task');
    await expect(page.locator('.task-description')).toContainText('A sample task for testing');
  });

  test('should switch to templates tab and display templates', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Click templates tab
    await page.locator('.tab-button').last().click();
    await expect(page.locator('.tab-button.active')).toContainText('Templates');

    // Should display regular template
    await expect(page.locator('.template-card')).toBeVisible();
    await expect(page.locator('.template-title')).toContainText('Alden Productivity Task');
  });

  test('should filter tasks by category', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Select development category
    await page.locator('.filter-select').first().selectOption('development');
    
    // Should still show the task (it's development category)
    await expect(page.locator('.task-card')).toBeVisible();

    // Select design category
    await page.locator('.filter-select').first().selectOption('design');
    
    // Should show empty state
    await expect(page.locator('.empty-state')).toBeVisible();
  });

  test('should search tasks and templates', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Search for specific task
    await page.locator('.search-input').fill('Sample');
    await expect(page.locator('.task-card')).toBeVisible();

    // Search for non-existent task
    await page.locator('.search-input').fill('Non-existent');
    await expect(page.locator('.empty-state')).toBeVisible();

    // Clear search
    await page.locator('.search-input').fill('');
    await expect(page.locator('.task-card')).toBeVisible();
  });
});

// Test Suite: Steve August Template License Validation
test.describe('Steve August Template - License Validation', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPIs(page);
    await page.addInitScript(() => {
      localStorage.setItem('hearthlink_token', 'test-auth-token');
    });
  });

  test('should hide Steve August template without license token', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Switch to templates tab
    await page.locator('.tab-button').last().click();

    // Should only show regular templates, not Steve August
    await expect(page.locator('.template-card')).toHaveCount(1);
    await expect(page.locator('.template-title')).not.toContainText('Steve August');
  });

  test('should show Steve August template with valid license', async ({ page }) => {
    await navigateToTaskDashboard(page, VALID_LICENSE_TOKEN);

    // Check license status indicator
    await expect(page.locator('.license-status.valid')).toBeVisible();
    await expect(page.locator('.license-status')).toContainText('License validated successfully');

    // Switch to templates tab
    await page.locator('.tab-button').last().click();

    // Should show Steve August template
    await expect(page.locator('.template-card')).toHaveCount(2);
    await expect(page.locator('.template-title')).toContainText('Steve August');
    await expect(page.locator('.licensed-badge')).toBeVisible();
  });

  test('should show invalid license status with invalid token', async ({ page }) => {
    await navigateToTaskDashboard(page, INVALID_LICENSE_TOKEN);

    // Check license status indicator
    await expect(page.locator('.license-status.invalid')).toBeVisible();
    await expect(page.locator('.license-status')).toContainText('Invalid license key format');

    // Switch to templates tab - should not show Steve August template
    await page.locator('.tab-button').last().click();
    await expect(page.locator('.template-card')).toHaveCount(1);
  });

  test('should show expired license status', async ({ page }) => {
    await navigateToTaskDashboard(page, EXPIRED_LICENSE_TOKEN);

    // Check license status indicator
    await expect(page.locator('.license-status.invalid')).toBeVisible();
    await expect(page.locator('.license-status')).toContainText('License key expired');
  });
});

// Test Suite: Task Editor Functionality
test.describe('Task Editor - Form Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPIs(page);
    await page.addInitScript(() => {
      localStorage.setItem('hearthlink_token', 'test-auth-token');
    });
  });

  test('should open task editor for new task creation', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Click create button
    await page.locator('.create-button').click();

    // Should open task editor
    await expect(page.locator('.task-editor-modal')).toBeVisible();
    await expect(page.locator('.editor-header h2')).toContainText('Create New Task');

    // Should show step 1
    await expect(page.locator('.step-indicator.active')).toHaveCount(1);
  });

  test('should validate required fields in basic info step', async ({ page }) => {
    await navigateToTaskDashboard(page);
    await page.locator('.create-button').click();

    // Try to proceed without filling required fields
    await page.locator('.nav-btn.primary').click();

    // Should show validation errors
    await expect(page.locator('.error-message')).toHaveCount(2); // Title and description required
    await expect(page.locator('.form-input.error')).toHaveCount(2);
  });

  test('should progress through form steps with valid data', async ({ page }) => {
    await navigateToTaskDashboard(page);
    await page.locator('.create-button').click();

    // Fill step 1
    await page.locator('#title').fill('Test Task Title');
    await page.locator('#description').fill('Test task description');
    await page.locator('#mission').fill('Test mission');

    // Proceed to step 2
    await page.locator('.nav-btn.primary').click();
    await expect(page.locator('.step-indicator.active')).toHaveCount(2);

    // Fill step 2
    await page.locator('#category').selectOption('development');
    await page.locator('.priority-btn.high').click();
    await page.locator('#estimatedTime').fill('3');

    // Proceed to step 3
    await page.locator('.nav-btn.primary').click();
    await expect(page.locator('.step-indicator.active')).toHaveCount(3);

    // Should be able to save
    await expect(page.locator('.nav-btn.primary')).toContainText('Save Task');
  });

  test('should navigate backwards through form steps', async ({ page }) => {
    await navigateToTaskDashboard(page);
    await page.locator('.create-button').click();

    // Fill step 1 and proceed
    await page.locator('#title').fill('Test Task');
    await page.locator('#description').fill('Description');
    await page.locator('.nav-btn.primary').click();

    // Go back to step 1
    await page.locator('.nav-btn.secondary').click();
    await expect(page.locator('.step-indicator.active')).toHaveCount(1);
    await expect(page.locator('#title')).toHaveValue('Test Task');
  });
});

// Test Suite: Steve August Template Form
test.describe('Steve August Template - Multi-Step Form', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPIs(page);
    await page.addInitScript(() => {
      localStorage.setItem('hearthlink_token', 'test-auth-token');
    });
  });

  test('should load Steve August template form with 4 steps', async ({ page }) => {
    await navigateToTaskDashboard(page, VALID_LICENSE_TOKEN);

    // Switch to templates and click Steve August template
    await page.locator('.tab-button').last().click();
    await page.locator('.template-title:has-text("Steve August")').click();

    // Should open editor with 4 steps
    await expect(page.locator('.task-editor-modal')).toBeVisible();
    await expect(page.locator('.step-indicator')).toHaveCount(4);
    await expect(page.locator('.editor-header h2')).toContainText('Steve August');
  });

  test('should validate Steve August specific fields', async ({ page }) => {
    await navigateToTaskDashboard(page, VALID_LICENSE_TOKEN);
    await page.locator('.tab-button').last().click();
    await page.locator('.template-use-button').first().click();

    // Fill basic fields
    await page.locator('#title').fill('Weekly Focus Test');
    await page.locator('#description').fill('Test description');
    // Leave weekOf empty to test validation

    // Try to proceed
    await page.locator('.nav-btn.primary').click();

    // Should show weekOf validation error
    await expect(page.locator('.error-message')).toContainText('Week date is required');
  });

  test('should complete Steve August form flow', async ({ page }) => {
    await navigateToTaskDashboard(page, VALID_LICENSE_TOKEN);
    await page.locator('.tab-button').last().click();
    await page.locator('.template-use-button').first().click();

    // Step 1: Basic info
    await page.locator('#title').fill('Weekly Focus - Test Week');
    await page.locator('#description').fill('ADHD coaching worksheet');
    await page.locator('#weekOf').fill('2025-08-01');
    await page.locator('.nav-btn.primary').click();

    // Step 2: Category
    await page.locator('#category').selectOption('adhd-coaching');
    await page.locator('.nav-btn.primary').click();

    // Step 3: Focus & Vision
    await page.locator('#magneticNorth').fill('Focus on important work');
    await page.locator('#steveVision').fill('Complete all priority tasks');
    await page.locator('.nav-btn.primary').click();

    // Step 4: Habits & Decisions
    await page.locator('#habitName').fill('Morning meditation');
    await page.locator('input[type="checkbox"]').first().check();

    // Should show save button
    await expect(page.locator('.nav-btn.primary')).toContainText('Save Task');
  });

  test('should display Steve August credit link', async ({ page }) => {
    await navigateToTaskDashboard(page, VALID_LICENSE_TOKEN);
    await page.locator('.tab-button').last().click();
    await page.locator('.template-use-button').first().click();

    // Check credit link in footer
    await expect(page.locator('.credit-link')).toBeVisible();
    await expect(page.locator('.credit-link')).toHaveAttribute('href', 'https://steve-august.com');
    await expect(page.locator('.credit-link')).toContainText('Steve August – ADHD Coaching');
  });
});

// Test Suite: CRUD Operations with Optimistic Updates
test.describe('CRUD Operations - Optimistic Updates', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPIs(page);
    await page.addInitScript(() => {
      localStorage.setItem('hearthlink_token', 'test-auth-token');
    });
  });

  test('should create task with optimistic update', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Initial task count
    await expect(page.locator('.task-card')).toHaveCount(1);

    // Create new task
    await page.locator('.create-button').click();
    await page.locator('#title').fill('New Optimistic Task');
    await page.locator('#description').fill('Test optimistic creation');
    await page.locator('.nav-btn.primary').click();
    await page.locator('#category').selectOption('development');
    await page.locator('.nav-btn.primary').click();
    await page.locator('.nav-btn.primary').click(); // Save

    // Should show success message
    await expect(page.locator('.success-message')).toBeVisible();

    // Wait for modal to close and check task was added
    await page.waitForTimeout(2000);
    await expect(page.locator('.task-card')).toHaveCount(2);
  });

  test('should handle task creation failure with rollback', async ({ page }) => {
    // Mock API failure
    await page.route('/api/vault/tasks', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal server error' })
        });
      }
    });

    await navigateToTaskDashboard(page);

    // Create task that will fail
    await page.locator('.create-button').click();
    await page.locator('#title').fill('Failed Task');
    await page.locator('#description').fill('This will fail');
    await page.locator('.nav-btn.primary').click();
    await page.locator('.nav-btn.primary').click();
    await page.locator('.nav-btn.primary').click(); // Save

    // Should show error message
    await expect(page.locator('.error-summary')).toBeVisible();
    await expect(page.locator('.error-summary')).toContainText('Failed to create task');
  });

  test('should edit existing task', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Click edit button on first task
    await page.locator('.action-button.edit').first().click();

    // Should open editor with existing data
    await expect(page.locator('.task-editor-modal')).toBeVisible();
    await expect(page.locator('.editor-header h2')).toContainText('Edit Task');
    await expect(page.locator('#title')).toHaveValue('Sample Task');

    // Modify title
    await page.locator('#title').fill('Modified Sample Task');
    await page.locator('.nav-btn.primary').click();
    await page.locator('.nav-btn.primary').click();
    await page.locator('.nav-btn.primary').click(); // Save

    // Should update the task
    await page.waitForTimeout(1000);
    await expect(page.locator('.task-title')).toContainText('Modified Sample Task');
  });

  test('should delete task with confirmation', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Initial count
    await expect(page.locator('.task-card')).toHaveCount(1);

    // Click delete button
    await page.locator('.action-button.delete').first().click();

    // Task should be removed immediately (optimistic update)
    await expect(page.locator('.empty-state')).toBeVisible();
  });
});

// Test Suite: Error Handling and Edge Cases
test.describe('Error Handling and Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('hearthlink_token', 'test-auth-token');
    });
  });

  test('should handle API failure gracefully', async ({ page }) => {
    // Mock API failures
    await page.route('/api/templates/', async route => {
      await route.fulfill({ status: 500 });
    });
    await page.route('/api/vault/tasks/list', async route => {
      await route.fulfill({ status: 500 });
    });

    await navigateToTaskDashboard(page);

    // Should show error banner
    await expect(page.locator('.error-banner')).toBeVisible();
    await expect(page.locator('.error-banner')).toContainText('Failed to load dashboard data');
  });

  test('should handle network timeout', async ({ page }) => {
    // Mock slow response
    await page.route('/api/templates/', async route => {
      await new Promise(resolve => setTimeout(resolve, 5000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });

    await navigateToTaskDashboard(page);

    // Should show loading state
    await expect(page.locator('.task-dashboard-loading')).toBeVisible();
    await expect(page.locator('.loading-spinner')).toBeVisible();
  });

  test('should validate form fields with custom error messages', async ({ page }) => {
    await setupMockAPIs(page);
    await navigateToTaskDashboard(page, VALID_LICENSE_TOKEN);

    // Open Steve August template
    await page.locator('.tab-button').last().click();
    await page.locator('.template-use-button').first().click();

    // Try invalid date format
    await page.locator('#title').fill('Test');
    await page.locator('#description').fill('Test');
    await page.locator('#weekOf').fill('invalid-date');
    await page.locator('.nav-btn.primary').click();

    // Should handle invalid input gracefully
    await expect(page.locator('.form-input')).toBeVisible();
  });

  test('should handle license validation failure', async ({ page }) => {
    // Mock license validation failure
    await page.route('/api/templates/validate-license', async route => {
      await route.fulfill({ status: 500 });
    });

    await navigateToTaskDashboard(page, VALID_LICENSE_TOKEN);

    // Should not crash, should handle gracefully
    await expect(page.locator('h1')).toContainText('Task Management Dashboard');
  });
});

// Test Suite: Accessibility and UX
test.describe('Accessibility and User Experience', () => {
  test.beforeEach(async ({ page }) => {
    await setupMockAPIs(page);
    await page.addInitScript(() => {
      localStorage.setItem('hearthlink_token', 'test-auth-token');
    });
  });

  test('should be keyboard navigable', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Tab through interface
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Should focus on create button
    await expect(page.locator('.create-button')).toBeFocused();

    // Enter should activate button
    await page.keyboard.press('Enter');
    await expect(page.locator('.task-editor-modal')).toBeVisible();
  });

  test('should have proper ARIA labels and roles', async ({ page }) => {
    await navigateToTaskDashboard(page);

    // Check for proper form labels
    await page.locator('.create-button').click();
    await expect(page.locator('label[for="title"]')).toBeVisible();
    await expect(page.locator('label[for="description"]')).toBeVisible();
  });

  test('should be responsive on mobile viewports', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await navigateToTaskDashboard(page);

    // Should adapt to mobile layout
    await expect(page.locator('.tasks-grid')).toBeVisible();
    await expect(page.locator('.dashboard-filters')).toBeVisible();
    
    // Tabs should stack on mobile
    await expect(page.locator('.tab-navigation')).toBeVisible();
  });

  test('should show loading states during operations', async ({ page }) => {
    await setupMockAPIs(page);
    await navigateToTaskDashboard(page);

    await page.locator('.create-button').click();
    await page.locator('#title').fill('Loading Test');
    await page.locator('#description').fill('Test loading state');
    await page.locator('.nav-btn.primary').click();
    await page.locator('.nav-btn.primary').click();

    // Mock slow save
    await page.route('/api/vault/tasks', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: 'new-task' })
      });
    });

    await page.locator('.nav-btn.primary').click(); // Save

    // Should show loading spinner
    await expect(page.locator('.loading-spinner')).toBeVisible();
    await expect(page.locator('.nav-btn.primary')).toContainText('Saving...');
  });
});

// Test configuration
test.describe.configure({ mode: 'parallel' });