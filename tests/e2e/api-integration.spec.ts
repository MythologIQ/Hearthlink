/**
 * SPEC-2 API Integration Tests
 * Tests for CRUD operations, audit logging, and license validation APIs
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:8000'; // Python backend URL
const TEST_USER_ID = 'test-user-123';
const VALID_LICENSE_TOKEN = 'SA-2025-TEST-MOCK-VALID';

// Test Suite: Template CRUD API
test.describe('Template CRUD API', () => {
  test('should fetch task templates', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/templates/`, {
      headers: {
        'Authorization': 'Bearer test-auth-token'
      }
    });

    expect(response.status()).toBe(200);
    const templates = await response.json();
    expect(Array.isArray(templates)).toBe(true);
    
    // Should include Steve August template
    const steveAugustTemplate = templates.find((t: any) => t.id === 'steve-august-focus-formula');
    expect(steveAugustTemplate).toBeDefined();
    expect(steveAugustTemplate.name).toContain('Steve August');
  });

  test('should validate license for protected template', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/templates/validate-license`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: {
        templateId: 'steve-august-focus-formula',
        licenseKey: VALID_LICENSE_TOKEN,
        userId: TEST_USER_ID
      }
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.valid).toBe(true);
    expect(result.templateId).toBe('steve-august-focus-formula');
    expect(result.features).toContain('full-template');
  });

  test('should reject invalid license', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/templates/validate-license`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: {
        templateId: 'steve-august-focus-formula',
        licenseKey: 'INVALID-LICENSE-KEY',
        userId: TEST_USER_ID
      }
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.valid).toBe(false);
    expect(result.message).toContain('Invalid');
  });

  test('should start trial for licensed template', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/templates/start-trial`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: {
        templateId: 'steve-august-focus-formula',
        userId: `trial-${Date.now()}`,
        email: 'test@example.com'
      }
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.message).toContain('Trial started');
    expect(result.trialUsesRemaining).toBeGreaterThan(0);
  });

  test('should record template usage', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/templates/record-usage`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: {
        templateId: 'steve-august-focus-formula',
        licenseKey: VALID_LICENSE_TOKEN,
        userId: TEST_USER_ID,
        action: 'create_task'
      }
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.message).toContain('recorded successfully');
  });
});

// Test Suite: Vault CRUD API
test.describe('Vault CRUD API', () => {
  let createdTaskId: string;

  test('should create task in vault', async ({ request }) => {
    const taskData = {
      task: {
        title: 'API Test Task',
        description: 'Task created via API test',
        priority: 'high',
        estimatedTime: 2,
        category: 'testing',
        assignedAgent: 'alden',
        mission: 'Test API functionality',
        values: ['testing', 'quality'],
        tags: ['api-test'],
        template: null,
        memoryTags: ['api-test', 'vault-integration']
      },
      vaultPath: `tasks/test/${Date.now()}`,
      encrypted: true,
      auditLog: {
        operation: 'CREATE',
        entityType: 'task',
        userId: TEST_USER_ID,
        timestamp: new Date().toISOString()
      }
    };

    const response = await request.post(`${BASE_URL}/api/vault/tasks`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: taskData
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.id).toBeDefined();
    expect(result.vaultPath).toBeDefined();
    
    createdTaskId = result.id;
  });

  test('should retrieve task from vault', async ({ request }) => {
    if (!createdTaskId) {
      test.skip('No task ID available from previous test');
    }

    const response = await request.get(`${BASE_URL}/api/vault/tasks/${createdTaskId}`, {
      headers: {
        'Authorization': 'Bearer test-auth-token'
      }
    });

    expect(response.status()).toBe(200);
    const task = await response.json();
    expect(task.title).toBe('API Test Task');
    expect(task.encrypted).toBe(true);
  });

  test('should update task in vault', async ({ request }) => {
    if (!createdTaskId) {
      test.skip('No task ID available from previous test');
    }

    const updateData = {
      task: {
        title: 'Updated API Test Task',
        description: 'Updated via API test',
        status: 'in-progress'
      },
      auditLog: {
        operation: 'UPDATE',
        entityType: 'task',
        entityId: createdTaskId,
        userId: TEST_USER_ID,
        timestamp: new Date().toISOString(),
        changes: { title: 'Updated API Test Task', status: 'in-progress' }
      }
    };

    const response = await request.put(`${BASE_URL}/api/vault/tasks/${createdTaskId}`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: updateData
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.success).toBe(true);
  });

  test('should list tasks from vault', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/vault/tasks/list`, {
      headers: {
        'Authorization': 'Bearer test-auth-token'
      }
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.tasks).toBeDefined();
    expect(Array.isArray(result.tasks)).toBe(true);
  });

  test('should delete task from vault', async ({ request }) => {
    if (!createdTaskId) {
      test.skip('No task ID available from previous test');
    }

    const response = await request.delete(`${BASE_URL}/api/vault/tasks/${createdTaskId}`, {
      headers: {
        'Authorization': 'Bearer test-auth-token'
      }
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.success).toBe(true);
  });
});

// Test Suite: Audit Logging API
test.describe('Audit Logging API', () => {
  test('should log audit entries', async ({ request }) => {
    const auditEntry = {
      operation: 'CREATE',
      entityType: 'task',
      entityId: `test-entity-${Date.now()}`,
      userId: TEST_USER_ID,
      timestamp: new Date().toISOString(),
      metadata: {
        title: 'Test Task',
        category: 'testing',
        template: null
      }
    };

    const response = await request.post(`${BASE_URL}/api/templates/audit`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: auditEntry
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.success).toBe(true);
  });

  test('should retrieve audit logs', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/templates/audit/user/${TEST_USER_ID}`, {
      headers: {
        'Authorization': 'Bearer test-auth-token'
      }
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.auditLogs).toBeDefined();
    expect(Array.isArray(result.auditLogs)).toBe(true);
  });
});

// Test Suite: Error Handling
test.describe('API Error Handling', () => {
  test('should handle invalid authentication', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/templates/`, {
      headers: {
        'Authorization': 'Bearer invalid-token'
      }
    });

    expect(response.status()).toBe(401);
  });

  test('should handle missing required fields', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/vault/tasks`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: {
        // Missing required task data
        vaultPath: 'test/path'
      }
    });

    expect(response.status()).toBe(422); // Validation error
  });

  test('should handle non-existent resources', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/vault/tasks/non-existent-id`, {
      headers: {
        'Authorization': 'Bearer test-auth-token'
      }
    });

    expect(response.status()).toBe(404);
  });

  test('should handle invalid license format', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/templates/validate-license`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: {
        templateId: 'steve-august-focus-formula',
        licenseKey: 'invalid-format',
        userId: TEST_USER_ID
      }
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.valid).toBe(false);
    expect(result.message).toContain('Invalid license key format');
  });
});

// Test Suite: Performance and Concurrency
test.describe('API Performance', () => {
  test('should handle concurrent requests', async ({ request }) => {
    const promises = Array.from({ length: 10 }, (_, i) =>
      request.get(`${BASE_URL}/api/templates/`, {
        headers: {
          'Authorization': 'Bearer test-auth-token'
        }
      })
    );

    const responses = await Promise.all(promises);
    
    for (const response of responses) {
      expect(response.status()).toBe(200);
    }
  });

  test('should respond within acceptable time limits', async ({ request }) => {
    const startTime = Date.now();
    
    const response = await request.get(`${BASE_URL}/api/templates/`, {
      headers: {
        'Authorization': 'Bearer test-auth-token'
      }
    });

    const responseTime = Date.now() - startTime;
    
    expect(response.status()).toBe(200);
    expect(responseTime).toBeLessThan(5000); // 5 seconds max
  });

  test('should handle large payload', async ({ request }) => {
    const largeTask = {
      task: {
        title: 'Large Task',
        description: 'A'.repeat(10000), // Large description
        priority: 'medium',
        estimatedTime: 1,
        category: 'testing',
        assignedAgent: 'alden',
        tags: Array.from({ length: 100 }, (_, i) => `tag-${i}`),
        memoryTags: Array.from({ length: 50 }, (_, i) => `memory-tag-${i}`)
      },
      vaultPath: `tasks/large/${Date.now()}`,
      encrypted: true
    };

    const response = await request.post(`${BASE_URL}/api/vault/tasks`, {
      headers: {
        'Authorization': 'Bearer test-auth-token',
        'Content-Type': 'application/json'
      },
      data: largeTask
    });

    expect(response.status()).toBe(200);
  });
});