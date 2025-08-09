// Global test setup

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

// Mock environment variables
process.env.NODE_ENV = 'test';
process.env.ELECTRON_IS_DEV = 'false';

// Mock fetch for Node.js environments
if (!global.fetch) {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
      blob: () => Promise.resolve(new Blob())
    })
  );
}

// Mock crypto for secure random generation
if (!global.crypto) {
  global.crypto = {
    getRandomValues: jest.fn((arr) => {
      for (let i = 0; i < arr.length; i++) {
        arr[i] = Math.floor(Math.random() * 256);
      }
      return arr;
    })
  };
}

// Mock timers for consistent testing
jest.useFakeTimers('modern');

// Global test utilities
global.testHelpers = {
  // Create a mock IPC event
  createMockIpcEvent: () => ({
    reply: jest.fn(),
    sender: {
      send: jest.fn()
    }
  }),
  
  // Create mock session data
  createMockSession: (overrides = {}) => ({
    sessionId: 'test-session-123',
    userId: 'test-user-456',
    topic: 'Test Session Topic',
    participants: ['user1', 'user2'],
    status: 'active',
    createdAt: new Date().toISOString(),
    ...overrides
  }),
  
  // Create mock persona memory data
  createMockPersonaMemory: (overrides = {}) => ({
    personaId: 'alden',
    userId: 'test-user-456',
    memory: {
      preferences: { theme: 'dark', language: 'en' },
      interactions: ['greeting', 'task_completion'],
      lastAccessed: new Date().toISOString()
    },
    ...overrides
  }),
  
  // Create mock plugin data
  createMockPlugin: (overrides = {}) => ({
    pluginId: 'test-plugin',
    name: 'Test Plugin',
    version: '1.0.0',
    description: 'A test plugin for unit testing',
    permissions: ['read', 'write'],
    ...overrides
  }),
  
  // Wait for async operations
  waitFor: async (fn, timeout = 5000) => {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      try {
        const result = await fn();
        if (result) return result;
      } catch (error) {
        // Continue trying
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error(`waitFor timeout after ${timeout}ms`);
  },
  
  // Simulate user delay
  simulateDelay: (ms = 100) => new Promise(resolve => setTimeout(resolve, ms))
};

// Custom matchers
expect.extend({
  toBeValidSession(received) {
    const requiredFields = ['sessionId', 'userId', 'topic', 'participants', 'status'];
    const hasAllFields = requiredFields.every(field => 
      received && typeof received === 'object' && field in received
    );
    
    if (hasAllFields) {
      return {
        message: () => `expected ${JSON.stringify(received)} not to be a valid session`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${JSON.stringify(received)} to be a valid session with fields: ${requiredFields.join(', ')}`,
        pass: false
      };
    }
  },
  
  toBeValidApiResponse(received) {
    const hasSuccessField = received && typeof received === 'object' && 'success' in received;
    const hasValidStructure = hasSuccessField && (
      (received.success === true) ||
      (received.success === false && 'error' in received)
    );
    
    if (hasValidStructure) {
      return {
        message: () => `expected ${JSON.stringify(received)} not to be a valid API response`,
        pass: true
      };
    } else {
      return {
        message: () => `expected ${JSON.stringify(received)} to be a valid API response with 'success' field and optional 'error' or 'data' fields`,
        pass: false
      };
    }
  }
});

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
  jest.clearAllTimers();
  jest.restoreAllMocks();
});

// Global cleanup
afterAll(() => {
  jest.restoreAllMocks();
  jest.useRealTimers();
});