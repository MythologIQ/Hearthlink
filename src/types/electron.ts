// Type definitions for Electron IPC API

export interface VoiceCommandResponse {
  command: string;
  response?: {
    success: boolean;
    action: string;
    response: string;
  };
  error?: string;
  timestamp: number;
}

export interface SessionData {
  userId: string;
  topic: string;
  participants: string[];
}

export interface ParticipantData {
  [key: string]: unknown;
}

export interface PersonaMemoryData {
  [key: string]: unknown;
}

export interface PluginPayload {
  [key: string]: unknown;
}

export interface AccessibilityUpdate {
  feature: string;
  enabled: boolean;
}

// API response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

// Electron API interface exposed to renderer
export interface ElectronAPI {
  // App information
  getAppVersion(): Promise<string>;
  getAppPath(): Promise<string>;
  getResourcePath(resourcePath: string): Promise<string>;
  
  // Documentation
  readDocumentation(docPath: string): Promise<ApiResponse<string>>;
  
  // External interactions
  openExternal(url: string): Promise<ApiResponse<void>>;
  
  // Voice commands
  sendVoiceCommand(command: string): Promise<ApiResponse<unknown>>;
  onVoiceCommandResponse(callback: (data: VoiceCommandResponse) => void): void;
  
  // Core session management
  createSession(userId: string, topic: string, participants: string[]): Promise<ApiResponse<unknown>>;
  getSession(sessionId: string): Promise<ApiResponse<unknown>>;
  addParticipant(sessionId: string, userId: string, participantData: ParticipantData): Promise<ApiResponse<unknown>>;
  startTurnTaking(sessionId: string, userId: string, turnOrder: string[]): Promise<ApiResponse<unknown>>;
  advanceTurn(sessionId: string, userId: string): Promise<ApiResponse<unknown>>;
  
  // Vault operations
  getPersonaMemory(personaId: string, userId: string): Promise<ApiResponse<PersonaMemoryData>>;
  updatePersonaMemory(personaId: string, userId: string, data: PersonaMemoryData): Promise<ApiResponse<void>>;
  
  // Synapse plugin operations
  executePlugin(pluginId: string, payload: PluginPayload, userId: string): Promise<ApiResponse<unknown>>;
  listPlugins(): Promise<ApiResponse<unknown[]>>;
  
  // Accessibility
  toggleAccessibility(feature: string): Promise<ApiResponse<{ feature: string; enabled: boolean }>>;
  onAccessibilityUpdate(callback: (data: AccessibilityUpdate) => void): void;
  
  // Menu events
  onNewSession(callback: () => void): void;
  onOpenUserGuide(callback: () => void): void;
  onOpenAccessibilityGuide(callback: () => void): void;
  onOpenTroubleshooting(callback: () => void): void;
  
  // Cleanup
  removeAllListeners(channel: string): void;
}

// Process information exposed to renderer
export interface ProcessInfo {
  env: {
    NODE_ENV?: string;
    ELECTRON_IS_DEV?: boolean;
  };
  platform: NodeJS.Platform;
  arch: string;
}

// Accessibility utilities
export interface AccessibilityAPI {
  speak(text: string, options?: {
    rate?: number;
    pitch?: number;
    volume?: number;
  }): void;
  setHighContrast(enabled: boolean): void;
  setFontSize(size: string): void;
  focusElement(selector: string): void;
  setupKeyboardNavigation(): void;
}

// Voice command utilities
export interface VoiceCommandAPI {
  initSpeechRecognition(): any | null;
  processCommand(command: string): boolean;
}

// Notification utilities
export interface NotificationAPI {
  show(title: string, body: string, options?: NotificationOptions): Notification | null;
  requestPermission(): Promise<NotificationPermission>;
}

// Security utilities
export interface SecurityAPI {
  getNonce(): string | null;
  validateOrigin(origin: string): boolean;
  getChannelVersion(): string;
}

// Global types for window object
declare global {
  interface Window {
    electronAPI: ElectronAPI;
    process: ProcessInfo;
    accessibility: AccessibilityAPI;
    voiceCommands: VoiceCommandAPI;
    notifications: NotificationAPI;
    security: SecurityAPI;
  }
}