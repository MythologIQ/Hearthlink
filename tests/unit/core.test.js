const { describe, it, expect, beforeEach, afterEach } = require('@jest/globals');
const { setupCoreHandlers } = require('../../ipcHandlers/core');
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

describe('Core IPC Handlers', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    // Clean up any handlers that were set up
    ipcMain.handle.mockClear();
  });

  describe('setupCoreHandlers', () => {
    it('should register all core IPC handlers', () => {
      setupCoreHandlers();

      // Verify that all expected handlers are registered
      expect(ipcMain.handle).toHaveBeenCalledWith(
        'core-create-session',
        expect.any(Function)
      );
      expect(ipcMain.handle).toHaveBeenCalledWith(
        'core-get-session',
        expect.any(Function)
      );
      expect(ipcMain.handle).toHaveBeenCalledWith(
        'core-add-participant',
        expect.any(Function)
      );
      expect(ipcMain.handle).toHaveBeenCalledWith(
        'core-start-turn-taking',
        expect.any(Function)
      );
      expect(ipcMain.handle).toHaveBeenCalledWith(
        'core-advance-turn',
        expect.any(Function)
      );
    });
  });

  describe('core-create-session handler', () => {
    let createSessionHandler;

    beforeEach(() => {
      setupCoreHandlers();
      // Get the handler function for core-create-session
      const handleCall = ipcMain.handle.mock.calls.find(
        call => call[0] === 'core-create-session'
      );
      createSessionHandler = handleCall[1];
    });

    it('should create session successfully', async () => {
      const mockResponse = { success: true, sessionId: 'test-session-123' };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      const params = {
        userId: 'user123',
        topic: 'Test Session',
        participants: ['user1', 'user2']
      };

      const result = await createSessionHandler(event, params);

      expect(sendToPython).toHaveBeenCalledWith({
        id: expect.any(Number),
        type: 'core_create_session',
        payload: params
      });
      expect(result).toEqual(mockResponse);
    });

    it('should handle Python bridge errors', async () => {
      const error = new Error('Python backend not available');
      sendToPython.mockRejectedValue(error);

      const event = {};
      const params = {
        userId: 'user123',
        topic: 'Test Session',
        participants: ['user1', 'user2']
      };

      const result = await createSessionHandler(event, params);

      expect(result).toEqual({
        success: false,
        error: 'Python backend not available'
      });
    });

    it('should generate unique command IDs', async () => {
      const mockResponse = { success: true };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      const params = {
        userId: 'user123',
        topic: 'Test Session',
        participants: []
      };

      // Call handler twice
      await createSessionHandler(event, params);
      await createSessionHandler(event, params);

      // Verify that different IDs were generated
      const firstCall = sendToPython.mock.calls[0][0];
      const secondCall = sendToPython.mock.calls[1][0];
      
      expect(firstCall.id).not.toEqual(secondCall.id);
      expect(typeof firstCall.id).toBe('number');
      expect(typeof secondCall.id).toBe('number');
    });
  });

  describe('core-get-session handler', () => {
    let getSessionHandler;

    beforeEach(() => {
      setupCoreHandlers();
      const handleCall = ipcMain.handle.mock.calls.find(
        call => call[0] === 'core-get-session'
      );
      getSessionHandler = handleCall[1];
    });

    it('should retrieve session successfully', async () => {
      const mockSession = {
        success: true,
        data: {
          sessionId: 'test-session-123',
          userId: 'user123',
          topic: 'Test Session',
          participants: ['user1', 'user2'],
          status: 'active'
        }
      };
      sendToPython.mockResolvedValue(mockSession);

      const event = {};
      const sessionId = 'test-session-123';

      const result = await getSessionHandler(event, sessionId);

      expect(sendToPython).toHaveBeenCalledWith({
        id: expect.any(Number),
        type: 'core_get_session',
        payload: { sessionId }
      });
      expect(result).toEqual(mockSession);
    });

    it('should handle session not found', async () => {
      const mockResponse = { success: false, error: 'Session not found' };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      const sessionId = 'nonexistent-session';

      const result = await getSessionHandler(event, sessionId);

      expect(result).toEqual(mockResponse);
    });
  });

  describe('core-add-participant handler', () => {
    let addParticipantHandler;

    beforeEach(() => {
      setupCoreHandlers();
      const handleCall = ipcMain.handle.mock.calls.find(
        call => call[0] === 'core-add-participant'
      );
      addParticipantHandler = handleCall[1];
    });

    it('should add participant successfully', async () => {
      const mockResponse = { success: true };
      sendToPython.mockResolvedValue(mockResponse);

      const event = {};
      const params = {
        sessionId: 'test-session-123',
        userId: 'user123',
        participantData: {
          name: 'John Doe',
          role: 'participant'
        }
      };

      const result = await addParticipantHandler(event, params);

      expect(sendToPython).toHaveBeenCalledWith({
        id: expect.any(Number),
        type: 'core_add_participant',
        payload: params
      });
      expect(result).toEqual(mockResponse);
    });
  });
});