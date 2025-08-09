/**
 * E2E Tauri App Automation - Context Retrieval Validation
 * 
 * Playwright automation script that:
 * 1. Launches the Tauri app
 * 2. Executes all four scenario scripts
 * 3. Captures response text, UI indicators, and Grafana metrics
 * 4. Validates complete pipeline functionality
 */

const { test, expect } = require('@playwright/test');
const axios = require('axios');
const { E2EScenarioManager, scenarios, ScenarioUtils } = require('../scenarios/scenario-scripts');

// Test configuration
const CONFIG = {
  TAURI_APP_URL: process.env.TAURI_APP_URL || 'http://localhost:3000',
  API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8002',
  PERFORMANCE_THRESHOLD_MS: 500,
  HANDOFF_THRESHOLD_MS: 1500,
  TEST_TIMEOUT_MS: 60000
};

// Create API client
const apiClient = axios.create({
  baseURL: CONFIG.API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.E2E_TEST_TOKEN || 'test-token-12345'}`
  }
});

// Add request/response interceptors for debugging
apiClient.interceptors.request.use(request => {
  console.log(`🔵 API Request: ${request.method?.toUpperCase()} ${request.url}`);
  return request;
});

apiClient.interceptors.response.use(
  response => {
    console.log(`🟢 API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  error => {
    console.log(`🔴 API Error: ${error.response?.status || 'NETWORK'} ${error.config?.url}`);
    return Promise.reject(error);
  }
);

test.describe('E2E Context Retrieval Validation Sprint', () => {
  let scenarioManager;

  test.beforeAll(async () => {
    console.log('🚀 Starting E2E Context Retrieval Validation Sprint');
    scenarioManager = new E2EScenarioManager();

    // Wait for system readiness
    console.log('⏳ Waiting for system readiness...');
    await ScenarioUtils.waitForSystemReady(apiClient);
    
    // Seed test data for deterministic results
    console.log('🌱 Seeding test data...');
    await ScenarioUtils.seedTestData(apiClient);
    
    console.log('✅ System ready for E2E testing');
  });

  test.beforeEach(async ({ page }) => {
    // Reset Vault state between tests
    const resetSuccess = await ScenarioUtils.resetVaultState(apiClient);
    if (!resetSuccess) {
      console.warn('⚠️ Failed to reset Vault state - tests may be affected');
    }

    // Clear any injected faults
    await ScenarioUtils.clearFaults(apiClient);

    // Set up page error handling
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log(`🔴 Browser Error: ${msg.text()}`);
      }
    });

    page.on('pageerror', error => {
      console.log(`🔴 Page Error: ${error.message}`);
    });

    // Set longer timeout for E2E tests
    test.setTimeout(CONFIG.TEST_TIMEOUT_MS);
  });

  test.afterEach(async () => {
    // Clear any faults that might have been injected
    await ScenarioUtils.clearFaults(apiClient);
  });

  test('Scenario 1: Simple Fact Lookup - Context Retrieval & Memory Persistence', async ({ page }) => {
    console.log('\n📝 Executing Scenario 1: Simple Fact Lookup');
    
    const result = await scenarios.scenario1_SimpleFactLookup.execute(page, apiClient);
    
    scenarioManager.recordResult(
      'Simple Fact Lookup',
      result.passed,
      result.latency,
      JSON.stringify(result.details)
    );

    // Playwright assertions
    expect(result.passed).toBe(true);
    expect(result.latency).toBeLessThan(CONFIG.PERFORMANCE_THRESHOLD_MS);
    expect(result.details.response_correct).toBe(true);
    expect(result.details.memory_stored).toBe(true);
    expect(result.details.memory_push_recorded).toBe(true);

    console.log(`✅ Scenario 1 completed: ${result.latency}ms`);
  });

  test('Scenario 2: Missing Context Fallback - Graceful Error Handling', async ({ page }) => {
    console.log('\n🔍 Executing Scenario 2: Missing Context Fallback');
    
    const result = await scenarios.scenario2_MissingContextFallback.execute(page, apiClient);
    
    scenarioManager.recordResult(
      'Missing Context Fallback',
      result.passed,
      result.latency,
      JSON.stringify(result.details)
    );

    // Playwright assertions
    expect(result.passed).toBe(true);
    expect(result.latency).toBeLessThan(CONFIG.PERFORMANCE_THRESHOLD_MS);
    expect(result.details.fallback_response).toBe(true);
    expect(result.details.no_crash).toBe(true);
    expect(result.details.no_critical_errors).toBe(true);

    console.log(`✅ Scenario 2 completed: ${result.latency}ms`);
  });

  test('Scenario 3: Multi-Step Dialogue - Chain-of-Thought Continuity', async ({ page }) => {
    console.log('\n💭 Executing Scenario 3: Multi-Step Dialogue');
    
    const result = await scenarios.scenario3_MultiStepDialogue.execute(page, apiClient);
    
    scenarioManager.recordResult(
      'Multi-Step Dialogue',
      result.passed,
      result.latency,
      JSON.stringify(result.details)
    );

    // Playwright assertions
    expect(result.passed).toBe(true);
    expect(result.details.context_carried_forward).toBe(true);
    expect(result.details.all_responses_valid).toBe(true);
    expect(result.details.conversation_stored).toBe(true);
    expect(result.details.avg_step_latency_ms).toBeLessThan(CONFIG.PERFORMANCE_THRESHOLD_MS);

    console.log(`✅ Scenario 3 completed: ${result.latency}ms (avg step: ${result.details.avg_step_latency_ms}ms)`);
  });

  test('Scenario 4: Agent Handoff - Cross-Agent Memory Consistency', async ({ page }) => {
    console.log('\n🔄 Executing Scenario 4: Agent Handoff');
    
    const result = await scenarios.scenario4_AgentHandoff.execute(page, apiClient);
    
    scenarioManager.recordResult(
      'Agent Handoff',
      result.passed,
      result.latency,
      JSON.stringify(result.details)
    );

    // Playwright assertions for agent handoff (allow higher latency)
    expect(result.passed).toBe(true);
    expect(result.latency).toBeLessThan(CONFIG.HANDOFF_THRESHOLD_MS);
    expect(result.details.handoff_successful).toBe(true);
    expect(result.details.returned_to_alden).toBe(true);
    expect(result.details.memory_consistent).toBe(true);
    expect(result.details.handoff_recorded).toBe(true);

    console.log(`✅ Scenario 4 completed: ${result.latency}ms`);
    console.log(`   Agents involved: ${result.details.agents_involved.join(', ')}`);
  });

  test('Error Path Validation: Vault Failure Handling', async ({ page }) => {
    console.log('\n⚠️ Testing Error Path: Vault Failure');
    
    // Inject Vault unavailable fault
    await ScenarioUtils.injectFault(apiClient, 'vault_unavailable', 10000);
    
    try {
      const startTime = Date.now();
      
      // Navigate to Alden interface
      await page.goto(CONFIG.TAURI_APP_URL);
      await page.waitForSelector('[data-testid="alden-interface"]', { timeout: 10000 });
      await page.click('[data-testid="alden-interface"]');
      await page.waitForSelector('.chat-input', { timeout: 5000 });
      
      // Send query during Vault failure
      await page.fill('.chat-input', 'What is the current weather?');
      await page.press('.chat-input', 'Enter');
      
      // Wait for response
      await page.waitForSelector('.chat-message.assistant:last-child', { timeout: 15000 });
      const responseText = await page.textContent('.chat-message.assistant:last-child');
      
      const latency = Date.now() - startTime;
      
      // Verify graceful fallback
      const gracefulFallback = responseText.includes('currently unavailable') ||
                              responseText.includes('temporary issue') ||
                              responseText.includes('please try again') ||
                              !responseText.includes('undefined') && !responseText.includes('500');
      
      scenarioManager.recordResult(
        'Vault Failure Handling',
        gracefulFallback,
        latency,
        `Response: ${responseText.substring(0, 100)}...`
      );

      expect(gracefulFallback).toBe(true);
      console.log(`✅ Vault failure handled gracefully: ${latency}ms`);
      
    } finally {
      // Clear the fault
      await ScenarioUtils.clearFaults(apiClient);
    }
  });

  test('Error Path Validation: LLM Timeout Handling', async ({ page }) => {
    console.log('\n⏰ Testing Error Path: LLM Timeout');
    
    // Inject LLM timeout fault
    await ScenarioUtils.injectFault(apiClient, 'llm_timeout', 8000);
    
    try {
      const startTime = Date.now();
      
      // Navigate to Alden interface
      await page.goto(CONFIG.TAURI_APP_URL);
      await page.waitForSelector('[data-testid="alden-interface"]', { timeout: 10000 });
      await page.click('[data-testid="alden-interface"]');
      await page.waitForSelector('.chat-input', { timeout: 5000 });
      
      // Send query during LLM timeout
      await page.fill('.chat-input', 'Explain quantum computing principles');
      await page.press('.chat-input', 'Enter');
      
      // Wait for timeout response
      await page.waitForSelector('.chat-message.assistant:last-child', { timeout: 20000 });
      const responseText = await page.textContent('.chat-message.assistant:last-child');
      
      const latency = Date.now() - startTime;
      
      // Verify timeout handling
      const timeoutHandled = responseText.includes('taking longer than expected') ||
                            responseText.includes('timeout') ||
                            responseText.includes('please try again') ||
                            (!responseText.includes('undefined') && latency < 15000);
      
      scenarioManager.recordResult(
        'LLM Timeout Handling',
        timeoutHandled,
        latency,
        `Response: ${responseText.substring(0, 100)}...`
      );

      expect(timeoutHandled).toBe(true);
      console.log(`✅ LLM timeout handled gracefully: ${latency}ms`);
      
    } finally {
      // Clear the fault
      await ScenarioUtils.clearFaults(apiClient);
    }
  });

  test('Performance Validation: Concurrent Query Handling', async ({ page }) => {
    console.log('\n🏃 Testing Performance: Concurrent Queries');
    
    const startTime = Date.now();
    const concurrentQueries = [
      'What is artificial intelligence?',
      'How does machine learning work?',
      'Explain neural networks'
    ];
    
    // Navigate to Alden interface
    await page.goto(CONFIG.TAURI_APP_URL);
    await page.waitForSelector('[data-testid="alden-interface"]', { timeout: 10000 });
    await page.click('[data-testid="alden-interface"]');
    await page.waitForSelector('.chat-input', { timeout: 5000 });
    
    // Send queries rapidly
    for (const query of concurrentQueries) {
      await page.fill('.chat-input', query);
      await page.press('.chat-input', 'Enter');
      await page.waitForTimeout(500); // Small delay between queries
    }
    
    // Wait for all responses
    await page.waitForSelector(`.chat-message.assistant:nth-last-child(1)`, { timeout: 15000 });
    
    const totalLatency = Date.now() - startTime;
    const avgLatency = totalLatency / concurrentQueries.length;
    
    // Check that all queries got responses
    const messageCount = await page.$$eval('.chat-message.assistant', messages => messages.length);
    const allQueriesAnswered = messageCount >= concurrentQueries.length;
    
    const performancePass = allQueriesAnswered && avgLatency < CONFIG.PERFORMANCE_THRESHOLD_MS * 1.5; // Allow 1.5x threshold for concurrent
    
    scenarioManager.recordResult(
      'Concurrent Query Handling',
      performancePass,
      totalLatency,
      `Avg latency: ${Math.round(avgLatency)}ms, Messages: ${messageCount}`
    );

    expect(performancePass).toBe(true);
    console.log(`✅ Concurrent queries handled: ${totalLatency}ms total, ${Math.round(avgLatency)}ms avg`);
  });

  test.afterAll(async () => {
    console.log('\n📊 Generating E2E Test Report...');
    
    const report = scenarioManager.generateReport();
    
    // Write detailed report to file
    const reportPath = 'tests/e2e/reports/e2e-validation-report.json';
    require('fs').writeFileSync(reportPath, JSON.stringify(report, null, 2));
    
    // Log summary to console
    console.log('\n' + '='.repeat(60));
    console.log('🎯 E2E CONTEXT RETRIEVAL VALIDATION SUMMARY');
    console.log('='.repeat(60));
    console.log(`📊 Tests: ${report.summary.total_tests} total, ${report.summary.passed} passed, ${report.summary.failed} failed`);
    console.log(`📈 Pass Rate: ${report.summary.pass_rate}`);
    console.log(`⏱️  Average Latency: ${report.summary.avg_latency_ms}ms`);
    console.log(`🚀 Max Latency: ${report.summary.max_latency_ms}ms`);
    console.log(`⚡ Performance Violations: ${report.summary.performance_violations}/${report.summary.total_tests}`);
    console.log(`🕐 Total Execution Time: ${Math.round(report.execution_time_ms / 1000)}s`);
    
    if (report.summary.failed > 0) {
      console.log('\n❌ FAILED TESTS:');
      report.detailed_results
        .filter(r => !r.passed)
        .forEach(r => {
          console.log(`   - ${r.scenario}: ${r.latency}ms`);
          console.log(`     Details: ${r.details}`);
        });
    }
    
    if (report.summary.performance_violations > 0) {
      console.log('\n⚠️ PERFORMANCE VIOLATIONS:');
      report.detailed_results
        .filter(r => r.latency > CONFIG.PERFORMANCE_THRESHOLD_MS)
        .forEach(r => {
          console.log(`   - ${r.scenario}: ${r.latency}ms (threshold: ${CONFIG.PERFORMANCE_THRESHOLD_MS}ms)`);
        });
    }
    
    console.log('='.repeat(60));
    
    // Set exit code based on results
    if (report.summary.failed > 0) {
      process.exitCode = 1;
      console.log('❌ E2E Validation FAILED - Build should fail');
    } else {
      console.log('✅ E2E Validation PASSED - All scenarios successful');
    }
    
    console.log(`📄 Detailed report saved to: ${reportPath}`);
  });
});

// Custom test utilities
test.extend({
  // Custom fixture for API testing
  apiClient: async ({}, use) => {
    await use(apiClient);
  },
  
  // Custom fixture for Grafana metrics validation
  grafanaMetrics: async ({}, use) => {
    const grafanaClient = axios.create({
      baseURL: process.env.GRAFANA_URL || 'http://localhost:3000',
      headers: {
        'Authorization': `Bearer ${process.env.GRAFANA_API_KEY || 'test-key'}`
      }
    });
    
    const metricsHelper = {
      async getLastMemoryPush() {
        try {
          const response = await grafanaClient.get('/api/datasources/proxy/1/api/v1/query', {
            params: { query: 'memory_push_timestamp_seconds' }
          });
          return response.data;
        } catch (error) {
          console.warn('Failed to get Grafana metrics:', error.message);
          return null;
        }
      }
    };
    
    await use(metricsHelper);
  }
});