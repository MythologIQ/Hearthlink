const { describe, it, expect, beforeEach, afterEach } = require('@jest/globals');
const { setupVaultHandlers } = require('../../ipcHandlers/vault');
const { ipcMain } = require('electron');

// Mock electron
jest.mock('electron', () => ({
  ipcMain: {
    handle: jest.fn(),
    removeHandler: jest.fn()
  }
}));

// Mock Python bridge
jest.mock('../../services/pythonBridge', () => ({
  sendToPython: jest.fn()
}));

const { sendToPython } = require('../../services/pythonBridge');

describe('Vault IPC Handlers', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    ipcMain.handle.mockClear();
  });

  describe('setupVaultHandlers', () => {
    it('should register all vault IPC handlers', () => {
      setupVaultHandlers();

      expect(ipcMain.handle).toHaveBeenCalledWith(
        'vault-get-persona-memory',
        expect.any(Function)
      );
      expect(ipcMain.handle).toHaveBeenCalledWith(
        'vault-update-persona-memory',
        expect.any(Function)
      );
    });
  });

  describe('vault-get-persona-memory handler', () => {
    let getPersonaMemoryHandler;

    beforeEach(() => {
      setupVaultHandlers();
      const handleCall = ipcMain.handle.mock.calls.find(
        call => call[0] === 'vault-get-persona-memory'
      );
      getPersonaMemoryHandler = handleCall[1];
    });

    it('should retrieve persona memory successfully', async () => {
      const mockMemory = {
        success: true,
        data: {
          personaId: 'alden',
          userId: 'user123',
          memory: {
            preferences: { theme: 'dark', language: 'en' },
            interactions: ['greeting', 'task_completion'],
            lastAccessed: '2025-01-20T10:00:00Z'
          }
        }
      };
      sendToPython.mockResolvedValue(mockMemory);

      const event = {};
      const params = {
        personaId: 'alden',
        userId: 'user123'
      };

      const result = await getPersonaMemoryHandler(event, params);

      expect(sendToPython).toHaveBeenCalledWith({
        id: expect.any(Number),
        type: 'vault_get_persona_memory',
        payload: params
      });
      expect(result).toEqual(mockMemory);
    });

    it('should handle persona not found', async () => {
      const mockResponse = { success: false, error: 'Persona memory not found' };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      const params = {
        personaId: 'nonexistent-persona',
        userId: 'user123'
      };

      const result = await getPersonaMemoryHandler(event, params);

      expect(result).toEqual(mockResponse);
    });

    it('should handle Python bridge errors', async () => {
      const error = new Error('Vault service unavailable');
      sendToPython.mockRejectedValue(error);

      const event = {};
      const params = {
        personaId: 'alden',
        userId: 'user123'
      };

      const result = await getPersonaMemoryHandler(event, params);

      expect(result).toEqual({
        success: false,
        error: 'Vault service unavailable'
      });
    });
  });

  describe('vault-update-persona-memory handler', () => {
    let updatePersonaMemoryHandler;

    beforeEach(() => {
      setupVaultHandlers();
      const handleCall = ipcMain.handle.mock.calls.find(
        call => call[0] === 'vault-update-persona-memory'
      );
      updatePersonaMemoryHandler = handleCall[1];
    });

    it('should update persona memory successfully', async () => {
      const mockResponse = { success: true };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      const params = {
        personaId: 'alden',
        userId: 'user123',
        data: {
          preferences: { theme: 'light', notifications: true },
          newInteraction: 'file_management',
          timestamp: '2025-01-20T11:00:00Z'
        }
      };

      const result = await updatePersonaMemoryHandler(event, params);

      expect(sendToPython).toHaveBeenCalledWith({
        id: expect.any(Number),
        type: 'vault_update_persona_memory',
        payload: params
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle validation errors', async () => {
      const mockResponse = { 
        success: false, 
        error: 'Invalid data format' 
      };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      const params = {
        personaId: 'alden',
        userId: 'user123',
        data: null // Invalid data
      };

      const result = await updatePersonaMemoryHandler(event, params);

      expect(result).toEqual(mockResponse);
    });

    it('should handle large data payloads', async () => {
      const mockResponse = { success: true };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      const largeData = {
        interactions: new Array(1000).fill('interaction'),
        longHistory: 'x'.repeat(10000),
        complexObject: {
          nested: {
            deeply: {
              structured: {
                data: Array.from({ length: 100 }, (_, i) => ({
                  id: i,
                  value: `item_${i}`,
                  metadata: { created: new Date().toISOString() }
                }))
              }
            }
          }
        }
      };

      const params = {
        personaId: 'alden',
        userId: 'user123',
        data: largeData
      };

      const result = await updatePersonaMemoryHandler(event, params);

      expect(sendToPython).toHaveBeenCalledWith({
        id: expect.any(Number),
        type: 'vault_update_persona_memory',
        payload: params
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('security and data integrity', () => {
    let getPersonaMemoryHandler;
    let updatePersonaMemoryHandler;

    beforeEach(() => {
      setupVaultHandlers();
      const getCall = ipcMain.handle.mock.calls.find(
        call => call[0] === 'vault-get-persona-memory'
      );
      const updateCall = ipcMain.handle.mock.calls.find(
        call => call[0] === 'vault-update-persona-memory'
      );
      getPersonaMemoryHandler = getCall[1];
      updatePersonaMemoryHandler = updateCall[1];
    });

    it('should isolate user data by userId', async () => {
      const mockResponse1 = { success: true, data: { memory: 'user1_data' } };
      const mockResponse2 = { success: true, data: { memory: 'user2_data' } };
      
      sendToPython
        .mockResolvedValueOnce(mockResponse1)
        .mockResolvedValueOnce(mockResponse2);

      const event = {};
      
      // Request data for user1
      await getPersonaMemoryHandler(event, {
        personaId: 'alden',
        userId: 'user1'
      });

      // Request data for user2
      await getPersonaMemoryHandler(event, {
        personaId: 'alden',
        userId: 'user2'
      });

      // Verify separate calls were made for each user
      expect(sendToPython).toHaveBeenCalledTimes(2);
      expect(sendToPython.mock.calls[0][0].payload.userId).toBe('user1');
      expect(sendToPython.mock.calls[1][0].payload.userId).toBe('user2');
    });

    it('should handle concurrent memory operations', async () => {
      const mockResponse = { success: true };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      
      // Make multiple concurrent requests
      const promises = [
        getPersonaMemoryHandler(event, { personaId: 'alden', userId: 'user1' }),
        updatePersonaMemoryHandler(event, { 
          personaId: 'alden', 
          userId: 'user1', 
          data: { test: 'data1' } 
        }),
        getPersonaMemoryHandler(event, { personaId: 'alice', userId: 'user2' }),
        updatePersonaMemoryHandler(event, { 
          personaId: 'alice', 
          userId: 'user2', 
          data: { test: 'data2' } 
        })
      ];

      const results = await Promise.all(promises);

      // All operations should succeed
      results.forEach(result => {
        expect(result.success).toBe(true);
      });

      // Verify all calls were made
      expect(sendToPython).toHaveBeenCalledTimes(4);
    });
  });
});