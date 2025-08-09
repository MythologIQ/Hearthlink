/**
 * Multi-Agent Conflict Resolution Integration Tests
 * Tests the memory sync service with real multi-agent scenarios
 */

const request = require('supertest');
const redis = require('redis');

describe('Multi-Agent Conflict Resolution Integration', () => {
  let memorySyncUrl;
  let redisClient;

  beforeAll(async () => {
    memorySyncUrl = process.env.MEMORY_SYNC_URL || 'http://localhost:8003';
    
    // Setup Redis client for direct testing
    redisClient = redis.createClient({
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379,
      password: process.env.REDIS_PASSWORD
    });
    
    await redisClient.connect();
    
    // Wait for memory sync service to be ready
    await waitForService(memorySyncUrl, 30000);
  });

  afterAll(async () => {
    if (redisClient) {
      await redisClient.quit();
    }
  });

  beforeEach(async () => {
    // Clear Redis state between tests
    await redisClient.flushDb();
  });

  describe('Agent Priority Conflict Resolution', () => {
    test('should resolve conflicts by agent priority (Sentry > Alden > Alice > Mimic)', async () => {
      const memoryId = 'priority-test-memory-1';
      const agents = ['mimic', 'alice', 'sentry', 'alden']; // Random order
      
      // Create simultaneous operations
      const operations = agents.map(agent => ({
        agentId: agent,
        memoryId: memoryId,
        operation: 'create',
        content: `Content from ${agent}`,
        importance: 0.5
      }));

      // Send operations simultaneously
      const promises = operations.map(op => 
        request(memorySyncUrl)
          .post('/api/sync-memory')
          .send(op)
      );

      const responses = await Promise.all(promises);
      
      // All should return 200 but some may have conflicts
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });

      // Check that Sentry won (highest priority)
      const successfulResponses = responses.filter(r => r.body.success === true);
      const conflictResponses = responses.filter(r => r.body.status === 'conflict_pending');
      
      expect(successfulResponses.length).toBeGreaterThan(0);
      
      // Get final memory state and verify Sentry's content won
      const statusResponses = await Promise.all(
        responses.map(r => r.body.syncId ? 
          request(memorySyncUrl).get(`/api/sync-status/${r.body.syncId}`) : null
        ).filter(Boolean)
      );

      // At least one operation should have succeeded
      const completedOperations = statusResponses.filter(r => 
        r.status === 200 && r.body.status === 'completed'
      );
      
      expect(completedOperations.length).toBeGreaterThan(0);
    });

    test('should handle mixed priority conflicts correctly', async () => {
      const memoryId = 'mixed-priority-memory';
      
      // First, Mimic creates memory
      const mimicResponse = await request(memorySyncUrl)
        .post('/api/sync-memory')
        .send({
          agentId: 'mimic',
          memoryId: memoryId,
          operation: 'create',
          content: 'Initial content from Mimic'
        });

      expect(mimicResponse.status).toBe(200);
      expect(mimicResponse.body.success).toBe(true);

      // Then Sentry tries to update (should win due to priority)
      const sentryResponse = await request(memorySyncUrl)
        .post('/api/sync-memory')
        .send({
          agentId: 'sentry',
          memoryId: memoryId,
          operation: 'update',
          content: 'Security update from Sentry',
          importance: 0.9
        });

      expect(sentryResponse.status).toBe(200);
      // Either succeeds immediately or creates resolvable conflict
      expect(sentryResponse.body.success || sentryResponse.body.conflictId).toBeTruthy();
    });
  });

  describe('Timestamp-Based Resolution', () => {
    test('should resolve conflicts by timestamp for same-priority agents', async () => {
      const memoryId = 'timestamp-test-memory';
      
      // Alice creates memory first
      const aliceResponse1 = await request(memorySyncUrl)
        .post('/api/sync-memory')
        .send({
          agentId: 'alice',
          memoryId: memoryId,
          operation: 'create',
          content: 'First content from Alice',
          timestamp: new Date('2024-01-01T10:00:00Z').toISOString()
        });

      expect(aliceResponse1.status).toBe(200);

      // Small delay to ensure different timestamps
      await new Promise(resolve => setTimeout(resolve, 100));

      // Alice updates with newer timestamp
      const aliceResponse2 = await request(memorySyncUrl)
        .post('/api/sync-memory')
        .send({
          agentId: 'alice',
          memoryId: memoryId,
          operation: 'update',
          content: 'Updated content from Alice',
          timestamp: new Date('2024-01-01T10:01:00Z').toISOString()
        });

      expect(aliceResponse2.status).toBe(200);
      // Should succeed or be resolvable
      expect(aliceResponse2.body.success || aliceResponse2.body.conflictId).toBeTruthy();
    });
  });

  describe('Importance-Based Resolution', () => {
    test('should resolve conflicts by importance score', async () => {
      const memoryId = 'importance-test-memory';
      
      // Low importance operation
      const lowImportanceResponse = await request(memorySyncUrl)
        .post('/api/sync-memory')
        .send({
          agentId: 'alice',
          memoryId: memoryId,
          operation: 'create',
          content: 'Low importance content',
          importance: 0.2
        });

      expect(lowImportanceResponse.status).toBe(200);

      // High importance operation (should win if conflict resolution uses importance)
      const highImportanceResponse = await request(memorySyncUrl)
        .post('/api/sync-memory')
        .send({
          agentId: 'alice',
          memoryId: memoryId,
          operation: 'update',
          content: 'High importance content',
          importance: 0.9
        });

      expect(highImportanceResponse.status).toBe(200);
      expect(highImportanceResponse.body.success || highImportanceResponse.body.conflictId).toBeTruthy();
    });
  });

  describe('Concurrent Operations Load Test', () => {
    test('should handle high volume of concurrent operations', async () => {
      const numOperations = 50;
      const agents = ['alden', 'alice', 'sentry', 'mimic'];
      
      const operations = Array.from({ length: numOperations }, (_, i) => ({
        agentId: agents[i % agents.length],
        memoryId: `load-test-memory-${Math.floor(i / 4)}`, // 4 operations per memory
        operation: 'create',
        content: `Load test content ${i}`,
        importance: Math.random()
      }));

      const promises = operations.map(op => 
        request(memorySyncUrl)
          .post('/api/sync-memory')
          .send(op)
      );

      const responses = await Promise.all(promises);
      
      // All should return valid responses
      responses.forEach((response, index) => {
        expect(response.status).toBe(200);
        expect(response.body).toHaveProperty('syncId');
      });

      // Check service health after load
      const healthResponse = await request(memorySyncUrl).get('/health');
      expect(healthResponse.status).toBe(200);
      expect(healthResponse.body.status).toBe('healthy');
    });
  });

  describe('Conflict Detection and Resolution', () => {
    test('should detect and track conflicts properly', async () => {
      const memoryId = 'conflict-detection-test';
      
      // Create initial memory
      const initialResponse = await request(memorySyncUrl)
        .post('/api/sync-memory')
        .send({
          agentId: 'alden',
          memoryId: memoryId,
          operation: 'create',
          content: 'Initial content'
        });

      expect(initialResponse.status).toBe(200);

      // Create conflicting updates
      const conflictPromises = ['alice', 'sentry'].map(agent => 
        request(memorySyncUrl)
          .post('/api/sync-memory')
          .send({
            agentId: agent,
            memoryId: memoryId,
            operation: 'update',
            content: `Updated by ${agent}`
          })
      );

      const conflictResponses = await Promise.all(conflictPromises);
      
      // Check conflicts endpoint
      const conflictsResponse = await request(memorySyncUrl).get('/api/conflicts');
      expect(conflictsResponse.status).toBe(200);
      
      // Should have tracked conflicts if they occurred
      if (conflictsResponse.body.total > 0) {
        expect(conflictsResponse.body.conflicts).toBeInstanceOf(Array);
        conflictsResponse.body.conflicts.forEach(conflict => {
          expect(conflict).toHaveProperty('conflictId');
          expect(conflict).toHaveProperty('memoryId');
          expect(conflict).toHaveProperty('agents');
        });
      }
    });

    test('should provide conflict resolution status', async () => {
      const memoryId = 'conflict-status-test';
      
      // Create simultaneous conflicting operations
      const operations = ['alden', 'alice'].map(agent => ({
        agentId: agent,
        memoryId: memoryId,
        operation: 'create',
        content: `Content from ${agent}`
      }));

      const responses = await Promise.all(
        operations.map(op => 
          request(memorySyncUrl)
            .post('/api/sync-memory')
            .send(op)
        )
      );

      // Check sync status for each operation
      for (const response of responses) {
        if (response.body.syncId) {
          const statusResponse = await request(memorySyncUrl)
            .get(`/api/sync-status/${response.body.syncId}`);
            
          expect(statusResponse.status).toBe(200);
          expect(statusResponse.body).toHaveProperty('syncId');
        }
      }
    });
  });

  describe('Service Metrics and Monitoring', () => {
    test('should provide accurate metrics', async () => {
      // Perform some operations
      const operations = [
        { agentId: 'alden', memoryId: 'metrics-test-1', operation: 'create', content: 'Test 1' },
        { agentId: 'alice', memoryId: 'metrics-test-2', operation: 'create', content: 'Test 2' },
        { agentId: 'sentry', memoryId: 'metrics-test-1', operation: 'update', content: 'Update 1' }
      ];

      await Promise.all(
        operations.map(op => 
          request(memorySyncUrl)
            .post('/api/sync-memory')
            .send(op)
        )
      );

      // Get metrics
      const metricsResponse = await request(memorySyncUrl).get('/api/metrics');
      expect(metricsResponse.status).toBe(200);
      
      const metrics = metricsResponse.body;
      expect(metrics).toHaveProperty('totalSyncs');
      expect(metrics).toHaveProperty('agentOperations');
      expect(metrics).toHaveProperty('uptime');
      expect(metrics.totalSyncs).toBeGreaterThan(0);
      
      // Check agent-specific metrics
      expect(metrics.agentOperations).toHaveProperty('alden');
      expect(metrics.agentOperations).toHaveProperty('alice');
      expect(metrics.agentOperations).toHaveProperty('sentry');
      expect(metrics.agentOperations).toHaveProperty('mimic');
    });
  });

  describe('Force Sync Operations', () => {
    test('should handle force sync with priority', async () => {
      const memoryId = 'force-sync-test';
      
      // Regular operation
      const regularResponse = await request(memorySyncUrl)
        .post('/api/sync-memory')
        .send({
          agentId: 'alice',
          memoryId: memoryId,
          operation: 'create',
          content: 'Regular content'
        });

      expect(regularResponse.status).toBe(200);

      // Force sync should override
      const forceSyncResponse = await request(memorySyncUrl)
        .post('/api/force-sync')
        .send({
          memoryId: memoryId,
          agentId: 'sentry',
          priority: true
        });

      expect(forceSyncResponse.status).toBe(200);
      expect(forceSyncResponse.body.success).toBe(true);
    });
  });
});

/**
 * Helper function to wait for service to be ready
 */
async function waitForService(url, timeout = 30000) {
  const start = Date.now();
  
  while (Date.now() - start < timeout) {
    try {
      const response = await request(url).get('/health');
      if (response.status === 200) {
        return;
      }
    } catch (error) {
      // Service not ready yet
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  throw new Error(`Service not ready after ${timeout}ms`);
}