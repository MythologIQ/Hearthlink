/**
 * E2E Context Retrieval Validation Sprint - Scenario Scripts
 * 
 * Four critical scenarios to validate the complete pipeline:
 * 1. Simple Fact Lookup - Context retrieval, inference, memory persistence
 * 2. Missing Context Fallback - Graceful handling of unknown topics
 * 3. Multi-Step Dialogue - Chain-of-thought conversation continuity  
 * 4. Agent Handoff - Cross-agent memory consistency and routing
 */

const fs = require('fs');
const path = require('path');

class E2EScenarioManager {
  constructor() {
    this.results = [];
    this.startTime = Date.now();
    this.performanceThreshold = 500; // 500ms max round-trip latency
  }

  // Utility: Record test result with timing
  recordResult(scenario, passed, latency, details) {
    this.results.push({
      scenario,
      passed,
      latency,
      details,
      timestamp: new Date().toISOString()
    });
    
    console.log(`${passed ? '✅' : '❌'} ${scenario}: ${latency}ms ${passed ? 'PASS' : 'FAIL'}`);
    if (details) console.log(`   Details: ${details}`);
  }

  // Generate final report
  generateReport() {
    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.passed).length;
    const avgLatency = this.results.reduce((sum, r) => sum + r.latency, 0) / totalTests;
    const maxLatency = Math.max(...this.results.map(r => r.latency));
    
    const report = {
      summary: {
        total_tests: totalTests,
        passed: passedTests,
        failed: totalTests - passedTests,
        pass_rate: ((passedTests / totalTests) * 100).toFixed(1) + '%',
        avg_latency_ms: Math.round(avgLatency),
        max_latency_ms: maxLatency,
        performance_threshold_ms: this.performanceThreshold,
        performance_violations: this.results.filter(r => r.latency > this.performanceThreshold).length
      },
      detailed_results: this.results,
      execution_time_ms: Date.now() - this.startTime
    };

    return report;
  }
}

// Scenario 1: Simple Fact Lookup
const scenario1_SimpleFactLookup = {
  name: "Simple Fact Lookup",
  description: "Query 'What is X?', check response correctness, verify new entry in Vault",
  
  async execute(page, apiClient) {
    const startTime = Date.now();
    
    try {
      // Step 1: Navigate to main interface
      await page.goto('http://localhost:3000');
      await page.waitForSelector('[data-testid="alden-interface"]', { timeout: 10000 });
      
      // Step 2: Click on Alden interface
      await page.click('[data-testid="alden-interface"]');
      await page.waitForSelector('.chat-input', { timeout: 5000 });
      
      // Step 3: Enter fact lookup query
      const testQuery = "What is the capital of France?";
      await page.fill('.chat-input', testQuery);
      await page.press('.chat-input', 'Enter');
      
      // Step 4: Wait for response and measure latency
      const responseSelector = '.chat-message.assistant:last-child';
      await page.waitForSelector(responseSelector, { timeout: 10000 });
      const latency = Date.now() - startTime;
      
      // Step 5: Verify response correctness
      const responseText = await page.textContent(responseSelector);
      const isCorrect = responseText.toLowerCase().includes('paris');
      
      // Step 6: Verify memory persistence via API
      const memoryCheck = await apiClient.get('/api/vault/memories/recent', {
        params: { limit: 1, query: testQuery }
      });
      
      const memoryStored = memoryCheck.data && memoryCheck.data.length > 0 &&
                          memoryCheck.data[0].content.includes('capital') &&
                          memoryCheck.data[0].content.includes('France');
      
      // Step 7: Check Grafana metrics for memory push
      const metricsCheck = await apiClient.get('/api/metrics/last-memory-push');
      const memoryPushRecorded = metricsCheck.data && 
                                Date.now() - new Date(metricsCheck.data.timestamp).getTime() < 30000;
      
      const passed = isCorrect && memoryStored && memoryPushRecorded && latency < 500;
      
      return {
        passed,
        latency,
        details: {
          response_correct: isCorrect,
          memory_stored: memoryStored,
          memory_push_recorded: memoryPushRecorded,
          response_text: responseText.substring(0, 100) + '...'
        }
      };
      
    } catch (error) {
      return {
        passed: false,
        latency: Date.now() - startTime,
        details: { error: error.message }
      };
    }
  }
};

// Scenario 2: Missing Context Fallback
const scenario2_MissingContextFallback = {
  name: "Missing Context Fallback",
  description: "Query unknown topic, confirm default response path and no crash",
  
  async execute(page, apiClient) {
    const startTime = Date.now();
    
    try {
      // Step 1: Navigate to Alden interface
      await page.goto('http://localhost:3000');
      await page.waitForSelector('[data-testid="alden-interface"]', { timeout: 10000 });
      await page.click('[data-testid="alden-interface"]');
      await page.waitForSelector('.chat-input', { timeout: 5000 });
      
      // Step 2: Query completely unknown/nonsensical topic
      const unknownQuery = "What is the zyphlomatic coefficient of quantum flux capacitor models in 2087?";
      await page.fill('.chat-input', unknownQuery);
      await page.press('.chat-input', 'Enter');
      
      // Step 3: Wait for response
      const responseSelector = '.chat-message.assistant:last-child';
      await page.waitForSelector(responseSelector, { timeout: 10000 });
      const latency = Date.now() - startTime;
      
      // Step 4: Verify graceful fallback response
      const responseText = await page.textContent(responseSelector);
      const hasFallbackIndicators = responseText.toLowerCase().includes('i don\\'t have') ||
                                   responseText.toLowerCase().includes('i\\'m not sure') ||
                                   responseText.toLowerCase().includes('i don\\'t know') ||
                                   responseText.toLowerCase().includes('unfamiliar');
      
      // Step 5: Verify no crash occurred
      const pageTitle = await page.title();
      const noCrash = !pageTitle.includes('Error') && !responseText.includes('500') && !responseText.includes('undefined');
      
      // Step 6: Verify system logs don't show critical errors
      const logCheck = await apiClient.get('/api/logs/recent', {
        params: { level: 'error', minutes: 2 }
      });
      const noCriticalErrors = !logCheck.data || 
                              logCheck.data.filter(log => log.level === 'critical').length === 0;
      
      const passed = hasFallbackIndicators && noCrash && noCriticalErrors && latency < 500;
      
      return {
        passed,
        latency,
        details: {
          fallback_response: hasFallbackIndicators,
          no_crash: noCrash,
          no_critical_errors: noCriticalErrors,
          response_text: responseText.substring(0, 100) + '...'
        }
      };
      
    } catch (error) {
      return {
        passed: false,
        latency: Date.now() - startTime,
        details: { error: error.message }
      };
    }
  }
};

// Scenario 3: Multi-Step Dialogue
const scenario3_MultiStepDialogue = {
  name: "Multi-Step Dialogue",
  description: "Chain-of-thought conversation spanning 3 prompts, ensure context carries forward",
  
  async execute(page, apiClient) {
    const overallStartTime = Date.now();
    const stepLatencies = [];
    
    try {
      // Step 1: Navigate to Alden interface
      await page.goto('http://localhost:3000');
      await page.waitForSelector('[data-testid="alden-interface"]', { timeout: 10000 });
      await page.click('[data-testid="alden-interface"]');
      await page.waitForSelector('.chat-input', { timeout: 5000 });
      
      // Multi-step conversation sequence
      const conversationSteps = [
        {
          query: "I'm planning a trip to Japan. What should I know about the culture?",
          expectedContext: ["japan", "culture", "trip"]
        },
        {
          query: "What about the best time to visit?",
          expectedContext: ["japan", "visit", "time", "season"]
        },
        {
          query: "And what are the must-see places there?",
          expectedContext: ["japan", "places", "tourist", "visit"]
        }
      ];
      
      let contextCarriedForward = true;
      let allResponsesValid = true;
      
      for (let i = 0; i < conversationSteps.length; i++) {
        const stepStartTime = Date.now();
        const step = conversationSteps[i];
        
        // Clear input and enter query
        await page.fill('.chat-input', '');
        await page.fill('.chat-input', step.query);
        await page.press('.chat-input', 'Enter');
        
        // Wait for response
        const responseSelector = `.chat-message.assistant:nth-last-child(${1})`;
        await page.waitForSelector(responseSelector, { timeout: 10000 });
        const stepLatency = Date.now() - stepStartTime;
        stepLatencies.push(stepLatency);
        
        // Verify response has context
        const responseText = await page.textContent(responseSelector);
        const hasExpectedContext = step.expectedContext.some(keyword => 
          responseText.toLowerCase().includes(keyword.toLowerCase())
        );
        
        if (!hasExpectedContext) {
          contextCarriedForward = false;
          allResponsesValid = false;
        }
        
        // Wait between steps
        await page.waitForTimeout(1000);
      }
      
      const totalLatency = Date.now() - overallStartTime;
      const avgStepLatency = stepLatencies.reduce((sum, l) => sum + l, 0) / stepLatencies.length;
      
      // Step 4: Verify conversation memory persistence
      const conversationCheck = await apiClient.get('/api/vault/conversations/recent', {
        params: { limit: 1 }
      });
      
      const conversationStored = conversationCheck.data && conversationCheck.data.length > 0 &&
                                conversationCheck.data[0].messages.length >= 6; // 3 user + 3 assistant
      
      const passed = contextCarriedForward && allResponsesValid && conversationStored && avgStepLatency < 500;
      
      return {
        passed,
        latency: totalLatency,
        details: {
          context_carried_forward: contextCarriedForward,
          all_responses_valid: allResponsesValid,
          conversation_stored: conversationStored,
          avg_step_latency_ms: Math.round(avgStepLatency),
          step_latencies_ms: stepLatencies
        }
      };
      
    } catch (error) {
      return {
        passed: false,
        latency: Date.now() - overallStartTime,
        details: { error: error.message }
      };
    }
  }
};

// Scenario 4: Agent Handoff
const scenario4_AgentHandoff = {
  name: "Agent Handoff",
  description: "Security query routed Alden→Sentry→Alden, verify memory consistency and persona responses",
  
  async execute(page, apiClient) {
    const startTime = Date.now();
    
    try {
      // Step 1: Navigate to Alden interface
      await page.goto('http://localhost:3000');
      await page.waitForSelector('[data-testid="alden-interface"]', { timeout: 10000 });
      await page.click('[data-testid="alden-interface"]');
      await page.waitForSelector('.chat-input', { timeout: 5000 });
      
      // Step 2: Trigger security-related query that should handoff to Sentry
      const securityQuery = "I'm concerned about potential security vulnerabilities in our MCP servers. Can you analyze the current threat level?";
      await page.fill('.chat-input', securityQuery);
      await page.press('.chat-input', 'Enter');
      
      // Step 3: Wait for initial Alden response (should indicate handoff)
      await page.waitForSelector('.chat-message.assistant:last-child', { timeout: 10000 });
      await page.waitForTimeout(2000); // Allow for handoff processing
      
      // Step 4: Look for Sentry response indicators
      const allMessages = await page.$$eval('.chat-message', messages => 
        messages.map(msg => ({
          role: msg.classList.contains('user') ? 'user' : 'assistant',
          content: msg.textContent,
          agent: msg.dataset.agent || 'unknown'
        }))
      );
      
      const sentryResponse = allMessages.find(msg => 
        msg.agent === 'sentry' || 
        msg.content.toLowerCase().includes('security analysis') ||
        msg.content.toLowerCase().includes('threat level')
      );
      
      // Step 5: Verify handoff occurred and response came back to Alden
      const aldenFinalResponse = allMessages.filter(msg => msg.role === 'assistant').pop();
      const handoffSuccessful = sentryResponse !== undefined;
      const returnedToAlden = aldenFinalResponse && (aldenFinalResponse.agent === 'alden' || 
                             aldenFinalResponse.content.includes('based on the security analysis'));
      
      // Step 6: Verify memory consistency across agents
      const memoryConsistencyCheck = await apiClient.get('/api/vault/cross-agent-memory', {
        params: { query: securityQuery, agents: ['alden', 'sentry'] }
      });
      
      const memoryConsistent = memoryConsistencyCheck.data && 
                              memoryConsistencyCheck.data.alden_memory &&
                              memoryConsistencyCheck.data.sentry_memory &&
                              memoryConsistencyCheck.data.consistency_score > 0.8;
      
      // Step 7: Check agent handoff metrics
      const handoffMetrics = await apiClient.get('/api/metrics/agent-handoffs/recent');
      const handoffRecorded = handoffMetrics.data && 
                             handoffMetrics.data.recent_handoffs &&
                             handoffMetrics.data.recent_handoffs.some(h => 
                               h.from_agent === 'alden' && h.to_agent === 'sentry'
                             );
      
      const latency = Date.now() - startTime;
      const passed = handoffSuccessful && returnedToAlden && memoryConsistent && handoffRecorded && latency < 1500; // Allow 1.5s for handoff
      
      return {
        passed,
        latency,
        details: {
          handoff_successful: handoffSuccessful,
          returned_to_alden: returnedToAlden,
          memory_consistent: memoryConsistent,
          handoff_recorded: handoffRecorded,
          total_messages: allMessages.length,
          agents_involved: [...new Set(allMessages.map(m => m.agent).filter(a => a !== 'unknown'))]
        }
      };
      
    } catch (error) {
      return {
        passed: false,
        latency: Date.now() - startTime,
        details: { error: error.message }
      };
    }
  }
};

// Export scenarios and manager
module.exports = {
  E2EScenarioManager,
  scenarios: {
    scenario1_SimpleFactLookup,
    scenario2_MissingContextFallback,
    scenario3_MultiStepDialogue,
    scenario4_AgentHandoff
  }
};

// Utility functions for scenario execution
const ScenarioUtils = {
  // Reset Vault state between tests
  async resetVaultState(apiClient) {
    try {
      await apiClient.post('/api/vault/test/reset', {
        preserve_system_memories: true,
        clear_conversations: true,
        reset_metrics: false
      });
      return true;
    } catch (error) {
      console.error('Failed to reset Vault state:', error.message);
      return false;
    }
  },

  // Seed randomness for deterministic tests
  seedTestData(apiClient) {
    const testSeed = process.env.E2E_TEST_SEED || '12345';
    return apiClient.post('/api/test/seed', { seed: testSeed });
  },

  // Wait for system readiness
  async waitForSystemReady(apiClient, timeout = 30000) {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      try {
        const healthCheck = await apiClient.get('/api/health/full');
        if (healthCheck.data && healthCheck.data.all_services_ready) {
          return true;
        }
      } catch (error) {
        // Continue waiting
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error('System not ready within timeout');
  },

  // Inject controlled faults for error testing
  async injectFault(apiClient, faultType, duration = 5000) {
    return apiClient.post('/api/test/inject-fault', {
      fault_type: faultType, // 'vault_unavailable', 'llm_timeout', 'memory_corruption'
      duration_ms: duration
    });
  },

  // Clear injected faults
  async clearFaults(apiClient) {
    return apiClient.post('/api/test/clear-faults');
  }
};

module.exports.ScenarioUtils = ScenarioUtils;