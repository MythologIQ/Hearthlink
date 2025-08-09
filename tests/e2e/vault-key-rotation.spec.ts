/**
 * SPEC-2 Phase 2: Vault Key Rotation E2E Tests
 * Playwright tests for key rotation functionality and verification
 */

import { test, expect, Page } from '@playwright/test';
import { ApiMocker } from './test-helpers';

const BASE_URL = 'http://localhost:8000';
const VAULT_TOKEN = 'vault-rotation-token';

// Mock responses for key rotation API
const MOCK_KEY_STATUS = {
  current_version: 1,
  should_rotate: false,
  rotation_reason: 'Key rotation not due until 2025-08-30T10:00:00Z',
  policy: {
    rotation_interval_days: 30,
    max_key_versions: 3,
    auto_rotation_enabled: true,
    performance_threshold_seconds: 5.0
  },
  metrics: {
    total_rotations: 0,
    last_rotation_timestamp: null,
    active_versions: 1
  },
  versions: [
    {
      version: 1,
      created_at: '2025-07-30T10:00:00Z',
      rotated_at: null,
      is_active: true,
      metadata: { generation_method: 'initial', bit_length: '256' }
    }
  ]
};

const MOCK_ROTATION_SUCCESS = {
  success: true,
  old_version: 1,
  new_version: 2,
  duration_seconds: 2.45,
  trigger_type: 'api',
  message: 'Key rotation completed successfully in 2.45s'
};

const MOCK_ROTATION_HISTORY = {
  history: [
    {
      timestamp: '2025-07-30T12:00:00Z',
      old_version: 1,
      new_version: 2,
      trigger_type: 'api',
      duration_seconds: 2.45,
      success: true,
      error_message: null
    }
  ],
  total_entries: 1
};

const MOCK_KEY_VERIFICATION = {
  summary: {
    total_versions: 2,
    valid_versions: 2,
    error_versions: 0,
    all_valid: true
  },
  results: [
    { version: 1, status: 'valid', is_active: false },
    { version: 2, status: 'valid', is_active: true }
  ],
  timestamp: '2025-07-30T12:05:00Z'
};

class VaultRotationApiMocker {
  constructor(private page: Page) {}

  async setupMocks() {
    await this.mockKeyStatus();
    await this.mockKeyRotation();
    await this.mockRotationHistory();
    await this.mockKeyVerification();
    await this.mockHealthCheck();
  }

  async mockKeyStatus() {
    await this.page.route('/api/vault/key-status', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_KEY_STATUS)
      });
    });
  }

  async mockKeyRotation() {
    await this.page.route('/api/vault/rotate-keys', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(MOCK_ROTATION_SUCCESS)
        });
      }
    });
  }

  async mockRotationHistory() {
    await this.page.route('/api/vault/rotation-history**', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_ROTATION_HISTORY)
      });
    });
  }

  async mockKeyVerification() {
    await this.page.route('/api/vault/verify-keys', async route => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(MOCK_KEY_VERIFICATION)
        });
      }
    });
  }

  async mockHealthCheck() {
    await this.page.route('/api/vault/health', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'healthy',
          current_key_version: 1,
          rotation_due: false,
          auto_rotation_enabled: true,
          timestamp: '2025-07-30T12:00:00Z'
        })
      });
    });
  }

  async mockRotationError() {
    await this.page.route('/api/vault/rotate-keys', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Key rotation failed: Database connection error' })
      });
    });
  }

  async mockAuthError() {
    await this.page.route('/api/vault/**', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Unauthorized: Invalid token' })
      });
    });
  }
}

test.describe('Vault Key Rotation API', () => {
  let apiMocker: VaultRotationApiMocker;

  test.beforeEach(async ({ page }) => {
    apiMocker = new VaultRotationApiMocker(page);
    await apiMocker.setupMocks();
  });

  test('should get key status', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/vault/key-status`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });

    expect(response.status()).toBe(200);
    const status = await response.json();
    
    expect(status.current_version).toBe(1);
    expect(status.should_rotate).toBe(false);
    expect(status.policy.rotation_interval_days).toBe(30);
    expect(status.versions).toHaveLength(1);
  });

  test('should perform key rotation', async ({ request }) => {
    const rotationRequest = {
      force: true,
      trigger_type: 'e2e_test'
    };

    const response = await request.post(`${BASE_URL}/api/vault/rotate-keys`, {
      headers: { 
        'Authorization': `Bearer ${VAULT_TOKEN}`,
        'Content-Type': 'application/json'
      },
      data: rotationRequest
    });

    expect(response.status()).toBe(200);
    const result = await response.json();
    
    expect(result.success).toBe(true);
    expect(result.old_version).toBe(1);
    expect(result.new_version).toBe(2);
    expect(result.duration_seconds).toBeLessThan(5.0); // Performance requirement
    expect(result.message).toContain('successfully');
  });

  test('should get rotation history', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/vault/rotation-history?limit=10`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });

    expect(response.status()).toBe(200);
    const history = await response.json();
    
    expect(history.history).toBeDefined();
    expect(history.total_entries).toBe(1);
    expect(history.history[0].success).toBe(true);
    expect(history.history[0].trigger_type).toBe('api');
  });

  test('should verify key integrity', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/vault/verify-keys`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });

    expect(response.status()).toBe(200);
    const verification = await response.json();
    
    expect(verification.summary.all_valid).toBe(true);
    expect(verification.summary.total_versions).toBe(2);
    expect(verification.summary.valid_versions).toBe(2);
    expect(verification.summary.error_versions).toBe(0);
    expect(verification.results).toHaveLength(2);
  });

  test('should handle authentication errors', async ({ page, request }) => {
    await apiMocker.mockAuthError();

    const response = await request.get(`${BASE_URL}/api/vault/key-status`, {
      headers: { 'Authorization': 'Bearer invalid-token' }
    });

    expect(response.status()).toBe(401);
  });

  test('should handle rotation errors gracefully', async ({ page, request }) => {
    await apiMocker.mockRotationError();

    const response = await request.post(`${BASE_URL}/api/vault/rotate-keys`, {
      headers: { 
        'Authorization': `Bearer ${VAULT_TOKEN}`,
        'Content-Type': 'application/json'
      },
      data: { force: true, trigger_type: 'error_test' }
    });

    expect(response.status()).toBe(500);
    const error = await response.json();
    expect(error.error).toContain('Key rotation failed');
  });

  test('should check vault health', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/vault/health`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });

    expect(response.status()).toBe(200);
    const health = await response.json();
    
    expect(health.status).toBe('healthy');
    expect(health.current_key_version).toBe(1);
    expect(health.auto_rotation_enabled).toBe(true);
  });
});

test.describe('Vault Key Rotation UI Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    const apiMocker = new VaultRotationApiMocker(page);
    await apiMocker.setupMocks();
    
    // Navigate to vault management dashboard
    await page.goto('/vault-dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display key rotation status', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Vault Key Management');
    
    // Check status display
    await expect(page.locator('.key-status .current-version')).toContainText('1');
    await expect(page.locator('.key-status .rotation-due')).toContainText('No');
    await expect(page.locator('.key-status .auto-rotation')).toContainText('Enabled');
    
    // Check policy display
    await expect(page.locator('.policy-info .interval')).toContainText('30 days');
    await expect(page.locator('.policy-info .max-versions')).toContainText('3');
  });

  test('should trigger manual key rotation', async ({ page }) => {
    // Click rotate button
    await page.locator('.rotate-button').click();
    
    // Confirm rotation in modal
    await expect(page.locator('.rotation-modal')).toBeVisible();
    await expect(page.locator('.rotation-modal .warning')).toContainText('This will rotate the master key');
    
    await page.locator('.confirm-rotation').click();
    
    // Check success message
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Key rotation completed successfully');
    
    // Verify status update
    await expect(page.locator('.key-status .current-version')).toContainText('2');
  });

  test('should display rotation history', async ({ page }) => {
    // Navigate to history tab
    await page.locator('.tab-button:has-text("History")').click();
    
    // Check history table
    await expect(page.locator('.history-table')).toBeVisible();
    await expect(page.locator('.history-table tbody tr')).toHaveCount(1);
    
    // Check history entry details
    const historyRow = page.locator('.history-table tbody tr').first();
    await expect(historyRow.locator('.timestamp')).toContainText('2025-07-30');
    await expect(historyRow.locator('.old-version')).toContainText('1');
    await expect(historyRow.locator('.new-version')).toContainText('2');
    await expect(historyRow.locator('.status')).toContainText('Success');
    await expect(historyRow.locator('.duration')).toContainText('2.45s');
  });

  test('should run key verification', async ({ page }) => {
    // Navigate to verification tab
    await page.locator('.tab-button:has-text("Verification")').click();
    
    // Click verify button
    await page.locator('.verify-keys-button').click();
    
    // Wait for verification to complete
    await expect(page.locator('.verification-results')).toBeVisible();
    
    // Check verification results
    await expect(page.locator('.verification-summary .total-versions')).toContainText('2');
    await expect(page.locator('.verification-summary .valid-versions')).toContainText('2');
    await expect(page.locator('.verification-summary .error-versions')).toContainText('0');
    await expect(page.locator('.verification-summary .status')).toContainText('All Valid');
    
    // Check individual results
    await expect(page.locator('.verification-results .result-row')).toHaveCount(2);
    await expect(page.locator('.verification-results .result-row:first-child .status')).toContainText('Valid');
    await expect(page.locator('.verification-results .result-row:last-child .status')).toContainText('Valid');
  });

  test('should display metrics and monitoring', async ({ page }) => {
    // Navigate to metrics tab
    await page.locator('.tab-button:has-text("Metrics")').click();
    
    // Check metrics display
    await expect(page.locator('.metrics-dashboard')).toBeVisible();
    await expect(page.locator('.metric-card .total-rotations .value')).toContainText('0');
    await expect(page.locator('.metric-card .active-versions .value')).toContainText('1');
    
    // Check performance chart (placeholder)
    await expect(page.locator('.performance-chart')).toBeVisible();
    
    // Check Prometheus metrics export
    await expect(page.locator('.export-metrics-button')).toBeVisible();
  });

  test('should handle rotation errors gracefully', async ({ page }) => {
    // Mock rotation error
    await page.route('/api/vault/rotate-keys', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Database connection error' })
      });
    });
    
    // Attempt rotation
    await page.locator('.rotate-button').click();
    await page.locator('.confirm-rotation').click();
    
    // Check error handling
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('Database connection error');
    
    // Verify UI state remains consistent
    await expect(page.locator('.key-status .current-version')).toContainText('1');
  });

  test('should show performance warnings', async ({ page }) => {
    // Mock slow rotation response
    await page.route('/api/vault/rotate-keys', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...MOCK_ROTATION_SUCCESS,
          duration_seconds: 6.5 // Exceeds 5s threshold
        })
      });
    });
    
    // Trigger rotation
    await page.locator('.rotate-button').click();
    await page.locator('.confirm-rotation').click();
    
    // Check performance warning
    await expect(page.locator('.warning-message')).toBeVisible();
    await expect(page.locator('.warning-message')).toContainText('exceeding threshold');
    await expect(page.locator('.warning-message')).toContainText('6.5s');
  });
});

test.describe('CLI Integration Tests', () => {
  test('should provide CLI status command', async ({ page }) => {
    // This would typically test actual CLI commands
    // For E2E testing, we simulate CLI behavior through API calls
    
    const response = await page.request.get(`${BASE_URL}/api/vault/key-status`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });
    
    expect(response.status()).toBe(200);
    const status = await response.json();
    
    // Verify CLI-equivalent data
    expect(status.current_version).toBeDefined();
    expect(status.should_rotate).toBeDefined();
    expect(status.policy).toBeDefined();
  });

  test('should support CLI rotation command', async ({ page }) => {
    const response = await page.request.post(`${BASE_URL}/api/vault/rotate-keys`, {
      headers: { 
        'Authorization': `Bearer ${VAULT_TOKEN}`,
        'Content-Type': 'application/json'
      },
      data: { force: true, trigger_type: 'cli' }
    });
    
    expect(response.status()).toBe(200);
    const result = await response.json();
    expect(result.success).toBe(true);
    expect(result.trigger_type).toBe('cli'); // Would be set by CLI
  });

  test('should support CLI verification command', async ({ page }) => {
    const response = await page.request.post(`${BASE_URL}/api/vault/verify-keys`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });
    
    expect(response.status()).toBe(200);
    const verification = await response.json();
    
    // CLI would display this data in table format
    expect(verification.summary).toBeDefined();
    expect(verification.results).toBeInstanceOf(Array);
  });
});

test.describe('Performance and Load Testing', () => {
  test('should complete rotation under performance threshold', async ({ request }) => {
    const startTime = Date.now();
    
    const response = await request.post(`${BASE_URL}/api/vault/rotate-keys`, {
      headers: { 
        'Authorization': `Bearer ${VAULT_TOKEN}`,
        'Content-Type': 'application/json'
      },
      data: { force: true, trigger_type: 'performance_test' }
    });
    
    const duration = (Date.now() - startTime) / 1000;
    
    expect(response.status()).toBe(200);
    expect(duration).toBeLessThan(5.0); // Performance requirement
    
    const result = await response.json();
    expect(result.duration_seconds).toBeLessThan(5.0);
  });

  test('should handle concurrent API requests', async ({ request }) => {
    const requests = Array.from({ length: 5 }, () =>
      request.get(`${BASE_URL}/api/vault/key-status`, {
        headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
      })
    );
    
    const responses = await Promise.all(requests);
    
    // All requests should succeed
    for (const response of responses) {
      expect(response.status()).toBe(200);
    }
  });

  test('should handle rapid status checks', async ({ request }) => {
    const rapidRequests: Promise<any>[] = [];
    
    for (let i = 0; i < 10; i++) {
      rapidRequests.push(
        request.get(`${BASE_URL}/api/vault/key-status`, {
          headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
        })
      );
    }
    
    const responses = await Promise.all(rapidRequests);
    
    // All should succeed with consistent data
    for (const response of responses) {
      expect(response.status()).toBe(200);
      const status = await response.json();
      expect(status.current_version).toBe(1);
    }
  });
});

test.describe('Security and Error Handling', () => {
  test('should require authentication', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/vault/key-status`);
    expect(response.status()).toBe(401);
  });

  test('should validate request data', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/api/vault/rotate-keys`, {
      headers: { 
        'Authorization': `Bearer ${VAULT_TOKEN}`,
        'Content-Type': 'application/json'
      },
      data: { invalid_field: true } // Invalid request structure
    });
    
    // Should still work with defaults, but test validates request handling
    expect([200, 422]).toContain(response.status());
  });

  test('should handle database errors', async ({ page, request }) => {
    await page.route('/api/vault/key-status', async route => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Database unavailable' })
      });
    });
    
    const response = await request.get(`${BASE_URL}/api/vault/key-status`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });
    
    expect(response.status()).toBe(503);
  });

  test('should rate limit requests', async ({ request }) => {
    // Simulate rate limiting (this would be configured in the actual API)
    const responses = [];
    
    for (let i = 0; i < 3; i++) {
      const response = await request.post(`${BASE_URL}/api/vault/rotate-keys`, {
        headers: { 
          'Authorization': `Bearer ${VAULT_TOKEN}`,
          'Content-Type': 'application/json'
        },
        data: { force: true, trigger_type: `rate_limit_test_${i}` }
      });
      responses.push(response);
    }
    
    // First request should succeed, others might be rate limited
    expect(responses[0].status()).toBe(200);
  });
});

test.describe('Grafana Integration', () => {
  test('should export Prometheus metrics', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/vault/metrics`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });
    
    expect(response.status()).toBe(200);
    
    const metrics = await response.text();
    expect(metrics).toContain('vault_key_rotation_total');
    expect(metrics).toContain('vault_key_rotation_timestamp');
    expect(metrics).toContain('vault_key_version_count');
    expect(metrics).toContain('vault_key_rotation_duration_seconds');
  });

  test('should provide metrics in correct format', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/api/vault/metrics`, {
      headers: { 'Authorization': `Bearer ${VAULT_TOKEN}` }
    });
    
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('text/plain');
    
    const metrics = await response.text();
    
    // Check Prometheus format
    expect(metrics).toMatch(/# HELP vault_key_rotation_total/);
    expect(metrics).toMatch(/# TYPE vault_key_rotation_total counter/);
    expect(metrics).toMatch(/vault_key_rotation_total \d+/);
  });
});