const request = require('supertest');
const { MemorySyncService } = require('../index');

describe('Memory Sync Service', () => {
  let app;
  let service;

  beforeAll(async () => {
    // Mock Redis for testing
    jest.mock('redis', () => ({
      createClient: jest.fn(() => ({
        connect: jest.fn(),
        isReady: true,
        set: jest.fn(() => 'OK'),
        get: jest.fn(),
        del: jest.fn(),
        setEx: jest.fn(),
        on: jest.fn(),
        quit: jest.fn()
      }))
    }));

    service = new MemorySyncService();
    app = service.app;
    
    // Mock Redis client
    service.redisClient = {
      isReady: true,
      set: jest.fn(() => 'OK'),
      get: jest.fn(),
      del: jest.fn(),
      setEx: jest.fn()
    };
  });

  afterAll(async () => {
    if (service) {
      await service.shutdown();
    }
  });

  describe('Health Check', () => {
    test('should return health status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body).toHaveProperty('status', 'healthy');
      expect(response.body).toHaveProperty('uptime');
      expect(response.body).toHaveProperty('redis');
      expect(response.body).toHaveProperty('metrics');
    });
  });

  describe('Memory Sync', () => {
    test('should validate sync data', async () => {
      const invalidSyncData = {
        agentId: 'alden'
        // Missing memoryId and operation
      };

      const response = await request(app)
        .post('/api/sync-memory')
        .send(invalidSyncData)
        .expect(500);

      expect(response.body).toHaveProperty('error');
    });

    test('should process valid sync data', async () => {
      const validSyncData = {
        agentId: 'alden',
        memoryId: 'test-memory-1',
        operation: 'create',
        content: 'Test memory content',
        importance: 0.8
      };

      service.syncOperations = new Map();
      service.acquireMemoryLock = jest.fn(() => Promise.resolve(true));
      service.releaseMemoryLock = jest.fn();
      service.checkExistingSync = jest.fn(() => Promise.resolve(null));

      const response = await request(app)
        .post('/api/sync-memory')
        .send(validSyncData)
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('syncId');
    });

    test('should handle sync conflicts', async () => {
      const syncData = {
        agentId: 'alice',
        memoryId: 'conflict-memory',
        operation: 'update',
        content: 'Conflicting content'
      };

      const existingSync = {
        syncId: 'existing-sync',
        agentId: 'alden',
        memoryId: 'conflict-memory',
        status: 'processing'
      };

      service.checkExistingSync = jest.fn(() => Promise.resolve(existingSync));
      service.handleSyncConflict = jest.fn(() => Promise.resolve({
        success: false,
        conflictId: 'test-conflict',
        status: 'conflict_pending'
      }));

      const response = await request(app)
        .post('/api/sync-memory')
        .send(syncData)
        .expect(200);

      expect(service.handleSyncConflict).toHaveBeenCalled();
    });
  });

  describe('Conflict Resolution', () => {
    test('should resolve conflicts by agent priority', async () => {
      const syncOperations = [
        { agentId: 'alice', memoryId: 'test', syncId: 'sync1' },
        { agentId: 'sentry', memoryId: 'test', syncId: 'sync2' }
      ];

      service.processSyncOperation = jest.fn(() => Promise.resolve({ success: true }));

      const result = await service.resolveByAgentPriority(syncOperations);

      expect(result.success).toBe(true);
      expect(result.strategy).toBe('agent_priority');
      expect(result.winningOperation.agentId).toBe('sentry'); // Higher priority
    });

    test('should resolve conflicts by timestamp', async () => {
      const now = new Date();
      const earlier = new Date(now.getTime() - 1000);

      const syncOperations = [
        { agentId: 'alden', memoryId: 'test', syncId: 'sync1', timestamp: earlier.toISOString() },
        { agentId: 'alice', memoryId: 'test', syncId: 'sync2', timestamp: now.toISOString() }
      ];

      service.processSyncOperation = jest.fn(() => Promise.resolve({ success: true }));

      const result = await service.resolveByTimestamp(syncOperations);

      expect(result.success).toBe(true);
      expect(result.strategy).toBe('timestamp_latest');
      expect(result.winningOperation.syncId).toBe('sync2'); // More recent
    });
  });

  describe('Metrics', () => {
    test('should return metrics', async () => {
      const response = await request(app)
        .get('/api/metrics')
        .expect(200);

      expect(response.body).toHaveProperty('totalSyncs');
      expect(response.body).toHaveProperty('conflictsResolved');
      expect(response.body).toHaveProperty('agentOperations');
      expect(response.body).toHaveProperty('uptime');
    });
  });

  describe('Active Conflicts', () => {
    test('should return active conflicts', async () => {
      service.activeConflicts = new Map([
        ['conflict-1', {
          conflictId: 'conflict-1',
          memoryId: 'test-memory',
          agents: ['alden', 'alice'],
          status: 'pending',
          created: new Date().toISOString()
        }]
      ]);

      const response = await request(app)
        .get('/api/conflicts')
        .expect(200);

      expect(response.body).toHaveProperty('conflicts');
      expect(response.body.conflicts).toHaveLength(1);
      expect(response.body.total).toBe(1);
    });
  });

  describe('Force Sync', () => {
    test('should perform force sync', async () => {
      const forceData = {
        memoryId: 'urgent-memory',
        agentId: 'sentry',
        priority: true
      };

      service.handleMemorySync = jest.fn(() => Promise.resolve({
        success: true,
        syncId: 'force-sync-id'
      }));

      const response = await request(app)
        .post('/api/force-sync')
        .send(forceData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(service.handleMemorySync).toHaveBeenCalled();
    });
  });
});