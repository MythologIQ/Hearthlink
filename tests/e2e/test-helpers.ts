/**
 * Test Helper Utilities for SPEC-2 Task Management UI Tests
 */

import { Page, expect } from '@playwright/test';

// Test data constants
export const TEST_CONSTANTS = {
  USERS: {
    TEST_USER: 'test-user-123',
    ADMIN_USER: 'admin-user-456'
  },
  LICENSES: {
    VALID: 'SA-2025-TEST-MOCK-VALID',
    INVALID: 'SA-2025-INVALID-TOKEN',
    EXPIRED: 'SA-2023-EXPIRED-TEST',
    TRIAL: 'SA-2025-TRIAL-TOKEN'
  },
  TEMPLATES: {
    STEVE_AUGUST: 'steve-august-focus-formula',
    ALDEN_PRODUCTIVITY: 'alden-productivity',
    DEVELOPMENT_SPRINT: 'development-sprint'
  }
};

// Mock API responses
export const MOCK_RESPONSES = {
  validLicense: {
    valid: true,
    licenseType: 'individual',
    message: 'License validated successfully',
    features: ['full-template', 'habit-tracking', 'decision-support'],
    usageLimit: 100,
    currentUsage: 5
  },
  invalidLicense: {
    valid: false,
    licenseType: 'none',
    message: 'Invalid license key format',
    features: []
  },
  trialLicense: {
    valid: true,
    licenseType: 'trial',
    message: 'Trial access: 2 uses remaining',
    usageLimit: 3,
    currentUsage: 1,
    features: ['limited-template']
  },
  taskTemplates: [
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
  ],
  sampleTasks: [
    {
      id: 'task-1',
      title: 'Sample Development Task',
      description: 'A sample task for UI testing',
      priority: 'high',
      status: 'todo',
      category: 'development',
      assignedAgent: 'alden',
      tags: ['testing', 'ui', 'development'],
      estimatedTime: 3,
      createdAt: '2025-07-30T10:00:00Z',
      updatedAt: '2025-07-30T10:00:00Z'
    },
    {
      id: 'task-2',
      title: 'Weekly Focus Formula - Week of 2025-07-28',
      description: 'Steve August ADHD Weekly Focus Formula worksheet',
      priority: 'medium',
      status: 'in-progress',
      category: 'adhd-coaching',
      assignedAgent: 'alden',
      tags: ['steve-august', 'focus-formula', 'adhd-coaching'],
      template: 'steve-august-focus-formula',
      estimatedTime: 0.5,
      createdAt: '2025-07-28T09:00:00Z',
      updatedAt: '2025-07-30T08:30:00Z'
    }
  ]
};

// API Mocking Utilities
export class ApiMocker {
  constructor(private page: Page) {}

  async setupStandardMocks() {
    await this.mockTemplatesAPI();
    await this.mockTasksAPI();
    await this.mockLicenseAPI();
    await this.mockAuditAPI();
  }

  async mockTemplatesAPI() {
    await this.page.route('/api/templates/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_RESPONSES.taskTemplates)
      });
    });
  }

  async mockTasksAPI() {
    // List tasks
    await this.page.route('/api/vault/tasks/list', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ tasks: MOCK_RESPONSES.sampleTasks })
      });
    });

    // Create task
    await this.page.route('/api/vault/tasks', async route => {
      if (route.request().method() === 'POST') {
        const body = await route.request().postDataJSON();
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: `task-${Date.now()}`,
            ...body.task,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          })
        });
      }
    });

    // Update task
    await this.page.route('/api/vault/tasks/*', async route => {
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
  }

  async mockLicenseAPI(licenseResponse: 'valid' | 'invalid' | 'trial' = 'valid') {
    // License validation
    await this.page.route('/api/templates/validate-license', async route => {
      const body = await route.request().postDataJSON();
      let response;
      
      if (body.licenseKey === TEST_CONSTANTS.LICENSES.VALID) {
        response = MOCK_RESPONSES.validLicense;
      } else if (body.licenseKey === TEST_CONSTANTS.LICENSES.TRIAL) {
        response = MOCK_RESPONSES.trialLicense;
      } else {
        response = MOCK_RESPONSES.invalidLicense;
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response)
      });
    });

    // License info
    await this.page.route('/api/templates/license-info/*', async route => {
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

    // User licenses
    await this.page.route('/api/templates/user-licenses/*', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          userLicenses: {
            'steve-august-focus-formula': {
              templateName: 'August Weekly Focus Formula',
              totalUses: 2,
              trialActive: licenseResponse === 'trial',
              trialUsesRemaining: licenseResponse === 'trial' ? 1 : 0,
              lastUsed: '2025-07-30T10:00:00Z'
            }
          }
        })
      });
    });

    // Start trial
    await this.page.route('/api/templates/start-trial', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Trial started successfully',
          trialDays: 7,
          trialUsesRemaining: 3,
          purchaseUrl: 'https://steve-august.com/focus-formula'
        })
      });
    });

    // Record usage
    await this.page.route('/api/templates/record-usage', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Usage recorded successfully',
          currentUsage: 3
        })
      });
    });
  }

  async mockAuditAPI() {
    await this.page.route('/api/templates/audit', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true })
      });
    });
  }

  async mockApiError(endpoint: string, status: number = 500) {
    await this.page.route(endpoint, async route => {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
  }
}

// Page Navigation Utilities
export class NavigationHelper {
  constructor(private page: Page) {}

  async goToTaskDashboard(userId: string = TEST_CONSTANTS.USERS.TEST_USER, licenseToken?: string) {
    const params = new URLSearchParams({ userId });
    if (licenseToken) {
      params.set('focusFormulaLicenseToken', licenseToken);
    }
    
    await this.page.goto(`/task-dashboard?${params.toString()}`);
    await this.page.waitForLoadState('networkidle');
  }

  async waitForTaskDashboardLoad() {
    await expect(this.page.locator('h1')).toContainText('Task Management Dashboard');
    await expect(this.page.locator('.tab-navigation')).toBeVisible();
  }

  async switchToTemplatesTab() {
    await this.page.locator('.tab-button').last().click();
    await expect(this.page.locator('.tab-button.active')).toContainText('Templates');
  }

  async switchToTasksTab() {
    await this.page.locator('.tab-button').first().click();
    await expect(this.page.locator('.tab-button.active')).toContainText('Tasks');
  }
}

// Form Interaction Utilities
export class FormHelper {
  constructor(private page: Page) {}

  async openTaskEditor() {
    await this.page.locator('.create-button').click();
    await expect(this.page.locator('.task-editor-modal')).toBeVisible();
  }

  async fillBasicTaskInfo(title: string, description: string, mission?: string) {
    await this.page.locator('#title').fill(title);
    await this.page.locator('#description').fill(description);
    if (mission) {
      await this.page.locator('#mission').fill(mission);
    }
  }

  async fillSteveAugustBasicInfo(weekOf: string) {
    await this.page.locator('#weekOf').fill(weekOf);
  }

  async selectCategory(category: string) {
    await this.page.locator('#category').selectOption(category);
  }

  async selectPriority(priority: 'high' | 'medium' | 'low') {
    await this.page.locator(`.priority-btn.${priority}`).click();
  }

  async goToNextStep() {
    await this.page.locator('.nav-btn.primary').click();
  }

  async goToPreviousStep() {
    await this.page.locator('.nav-btn.secondary').click();
  }

  async saveTask() {
    await this.page.locator('.nav-btn.primary').click();
  }

  async fillSteveAugustStep3(magneticNorth: string, vision?: string, values?: string) {
    await this.page.locator('#magneticNorth').fill(magneticNorth);
    if (vision) {
      await this.page.locator('#steveVision').fill(vision);
    }
    if (values) {
      await this.page.locator('#steveValues').fill(values);
    }
  }

  async addBrainDumpOption(goal: string, rock: string, nextStep: string) {
    const optionInputs = this.page.locator('.brain-dump-item').last().locator('.form-input');
    await optionInputs.nth(0).fill(goal);
    await optionInputs.nth(1).fill(rock);
    await optionInputs.nth(2).fill(nextStep);
  }

  async checkHabitDay(day: string) {
    await this.page.locator(`.habit-day:has-text("${day}") input[type="checkbox"]`).check();
  }

  async fillDailyPriority(day: string, priority: string) {
    await this.page.locator(`.daily-priority:has-text("${day}") .form-input`).fill(priority);
  }
}

// Assertion Utilities
export class AssertionHelper {
  constructor(private page: Page) {}

  async verifyTaskCard(title: string, options?: {
    description?: string;
    priority?: string;
    status?: string;
    agent?: string;
    template?: string;
  }) {
    const taskCard = this.page.locator('.task-card', { hasText: title });
    await expect(taskCard).toBeVisible();
    
    if (options?.description) {
      await expect(taskCard.locator('.task-description')).toContainText(options.description);
    }
    
    if (options?.priority) {
      await expect(taskCard.locator(`.priority-badge`)).toContainText(options.priority);
    }
    
    if (options?.status) {
      await expect(taskCard.locator(`.status-badge`)).toContainText(options.status);
    }
    
    if (options?.agent) {
      await expect(taskCard.locator('.task-agent')).toContainText(options.agent);
    }

    if (options?.template === 'steve-august-focus-formula') {
      await expect(taskCard.locator('.credit-link')).toBeVisible();
      await expect(taskCard.locator('.credit-link')).toContainText('Steve August');
    }
  }

  async verifyTemplateCard(name: string, options?: {
    description?: string;
    licensed?: boolean;
    category?: string;
  }) {
    const templateCard = this.page.locator('.template-card', { hasText: name });
    await expect(templateCard).toBeVisible();
    
    if (options?.description) {
      await expect(templateCard.locator('.template-description')).toContainText(options.description);
    }
    
    if (options?.licensed) {
      await expect(templateCard.locator('.licensed-badge')).toBeVisible();
      await expect(templateCard.locator('.credit-link')).toBeVisible();
    }
    
    if (options?.category) {
      await expect(templateCard.locator('.template-category')).toContainText(options.category);
    }
  }

  async verifyLicenseStatus(status: 'valid' | 'invalid', message?: string) {
    const licenseStatus = this.page.locator('.license-status');
    await expect(licenseStatus).toBeVisible();
    await expect(licenseStatus).toHaveClass(new RegExp(`license-status.*${status}`));
    
    if (message) {
      await expect(licenseStatus).toContainText(message);
    }
  }

  async verifyFormValidationError(field: string, message: string) {
    const errorMessage = this.page.locator(`.error-message:has-text("${message}")`);
    await expect(errorMessage).toBeVisible();
  }

  async verifyStepIndicator(activeStep: number, totalSteps: number = 4) {
    await expect(this.page.locator('.step-indicator')).toHaveCount(totalSteps);
    await expect(this.page.locator('.step-indicator.active')).toHaveCount(activeStep);
  }

  async verifySteveAugustCredit() {
    await expect(this.page.locator('.credit-link')).toBeVisible();
    await expect(this.page.locator('.credit-link')).toHaveAttribute('href', 'https://steve-august.com');
    await expect(this.page.locator('.credit-link')).toContainText('Steve August – ADHD Coaching');
  }

  async verifyOptimisticUpdate(action: 'create' | 'update' | 'delete', taskTitle?: string) {
    switch (action) {
      case 'create':
        if (taskTitle) {
          // Task should appear immediately
          await expect(this.page.locator('.task-card', { hasText: taskTitle })).toBeVisible();
        }
        break;
      case 'update':
        if (taskTitle) {
          // Updated task should show new data immediately
          await expect(this.page.locator('.task-title', { hasText: taskTitle })).toBeVisible();
        }
        break;
      case 'delete':
        if (taskTitle) {
          // Task should disappear immediately
          await expect(this.page.locator('.task-card', { hasText: taskTitle })).toHaveCount(0);
        }
        break;
    }
  }
}

// Test Data Generators
export class TestDataGenerator {
  static generateTaskData(overrides?: Partial<any>) {
    return {
      title: `Test Task ${Date.now()}`,
      description: 'Generated test task description',
      priority: 'medium',
      estimatedTime: 2,
      category: 'testing',
      assignedAgent: 'alden',
      mission: 'Test mission statement',
      values: ['testing', 'quality'],
      tags: ['test', 'generated'],
      memoryTags: ['test-data'],
      ...overrides
    };
  }

  static generateSteveAugustData(overrides?: Partial<any>) {
    return {
      weekOf: '2025-08-01',
      twoHourWorkdayPriorities: ['Focus on important tasks'],
      brainDumpOptions: [
        { goal: 'Complete project', rock: 'Time constraints', smallestNextStep: 'Write outline' }
      ],
      magneticNorth: 'Focus on high-impact work',
      mission: 'Achieve weekly productivity goals',
      vision: 'Complete all priority tasks successfully',
      values: 'Focus, efficiency, self-care',
      selfCareHabitTracker: {
        habitName: 'Morning meditation',
        targetFrequency: 'daily',
        weekly: { Mon: true, Tue: true, Wed: false, Thu: false, Fri: false, Sat: false, Sun: false },
        notes: 'Focus on breathing'
      },
      daily2HRPriorities: {
        Monday: 'Project planning',
        Tuesday: 'Core development',
        Wednesday: 'Testing and review',
        Thursday: 'Documentation',
        Friday: 'Final polish'
      },
      decisions: [
        { decision: 'Choose technology stack', deadline: '2025-08-03', options: ['React', 'Vue'], criteria: 'Team expertise' }
      ],
      ...overrides
    };
  }
}

// Performance Testing Utilities
export class PerformanceHelper {
  constructor(private page: Page) {}

  async measurePageLoad() {
    const startTime = Date.now();
    await this.page.waitForLoadState('networkidle');
    return Date.now() - startTime;
  }

  async measureApiResponse(url: string) {
    const startTime = Date.now();
    const response = await this.page.request.get(url);
    const endTime = Date.now();
    
    return {
      responseTime: endTime - startTime,
      status: response.status(),
      ok: response.ok()
    };
  }

  async measureFormSubmission() {
    const startTime = Date.now();
    await this.page.locator('.nav-btn.primary').click();
    await this.page.waitForSelector('.success-message, .error-summary');
    return Date.now() - startTime;
  }
}

export { TEST_CONSTANTS, MOCK_RESPONSES, ApiMocker, NavigationHelper, FormHelper, AssertionHelper, TestDataGenerator, PerformanceHelper };