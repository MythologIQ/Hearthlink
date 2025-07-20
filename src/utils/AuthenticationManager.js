/**
 * Comprehensive Authentication and Authorization System
 * 
 * Provides centralized authentication management, role-based access control,
 * session management, and security enforcement for all system components.
 */

import systemLogger, { info as logInfo, warn as logWarn, error as logError, securityEvent, createContext } from './SystemLogger';
import { AuthenticationError, SystemError, ValidationError } from './ErrorHandler';
import { get as getConfig, watch as watchConfig } from './ConfigManager';

// Authentication states
export const AUTH_STATES = {
  UNAUTHENTICATED: 'unauthenticated',
  AUTHENTICATING: 'authenticating',
  AUTHENTICATED: 'authenticated',
  TOKEN_EXPIRED: 'token_expired',
  LOCKED: 'locked',
  SUSPENDED: 'suspended'
};

// User roles and permissions
export const USER_ROLES = {
  ADMIN: 'admin',
  USER: 'user',
  AGENT: 'agent',
  VIEWER: 'viewer',
  SYSTEM: 'system'
};

export const PERMISSIONS = {
  // System permissions
  SYSTEM_ADMIN: 'system:admin',
  SYSTEM_CONFIG: 'system:config',
  SYSTEM_LOGS: 'system:logs',
  
  // Agent permissions
  AGENT_CREATE: 'agent:create',
  AGENT_DELETE: 'agent:delete',
  AGENT_MODIFY: 'agent:modify',
  AGENT_INTERACT: 'agent:interact',
  
  // Vault permissions
  VAULT_READ: 'vault:read',
  VAULT_WRITE: 'vault:write',
  VAULT_DELETE: 'vault:delete',
  VAULT_ADMIN: 'vault:admin',
  
  // Voice permissions
  VOICE_ACCESS: 'voice:access',
  VOICE_COMMAND: 'voice:command',
  VOICE_CONFIG: 'voice:config',
  
  // External API permissions
  API_EXTERNAL: 'api:external',
  API_WEBHOOK: 'api:webhook',
  API_BROWSER: 'api:browser',
  
  // UI permissions
  UI_ADMIN: 'ui:admin',
  UI_CONFIG: 'ui:config'
};

// Session types
export const SESSION_TYPES = {
  USER: 'user',
  AGENT: 'agent',
  SYSTEM: 'system',
  EXTERNAL: 'external'
};

class AuthenticationManager {
  constructor() {
    this.currentUser = null;
    this.sessions = new Map();
    this.authState = AUTH_STATES.UNAUTHENTICATED;
    this.rolePermissions = new Map();
    this.authProviders = new Map();
    this.sessionTimeouts = new Map();
    this.failedAttempts = new Map();
    this.context = createContext('auth-manager', 'security');
    
    this.initialize();
  }

  async initialize() {
    try {
      // Setup role-based permissions
      this.setupRolePermissions();
      
      // Initialize authentication providers
      this.initializeAuthProviders();
      
      // Setup session management
      this.setupSessionManagement();
      
      // Setup security monitoring
      this.setupSecurityMonitoring();
      
      // Load saved authentication state
      await this.loadAuthenticationState();
      
      logInfo('AuthenticationManager initialized successfully', {
        supportedRoles: Object.values(USER_ROLES),
        authProviders: Array.from(this.authProviders.keys())
      }, this.context);
      
    } catch (error) {
      logError('Failed to initialize AuthenticationManager', {
        error: error.message,
        stack: error.stack
      }, this.context);
      throw new SystemError('Authentication initialization failed', { originalError: error });
    }
  }

  setupRolePermissions() {
    // Admin permissions (full access)
    this.rolePermissions.set(USER_ROLES.ADMIN, new Set([
      PERMISSIONS.SYSTEM_ADMIN,
      PERMISSIONS.SYSTEM_CONFIG,
      PERMISSIONS.SYSTEM_LOGS,
      PERMISSIONS.AGENT_CREATE,
      PERMISSIONS.AGENT_DELETE,
      PERMISSIONS.AGENT_MODIFY,
      PERMISSIONS.AGENT_INTERACT,
      PERMISSIONS.VAULT_READ,
      PERMISSIONS.VAULT_WRITE,
      PERMISSIONS.VAULT_DELETE,
      PERMISSIONS.VAULT_ADMIN,
      PERMISSIONS.VOICE_ACCESS,
      PERMISSIONS.VOICE_COMMAND,
      PERMISSIONS.VOICE_CONFIG,
      PERMISSIONS.API_EXTERNAL,
      PERMISSIONS.API_WEBHOOK,
      PERMISSIONS.API_BROWSER,
      PERMISSIONS.UI_ADMIN,
      PERMISSIONS.UI_CONFIG
    ]));

    // User permissions (standard user access)
    this.rolePermissions.set(USER_ROLES.USER, new Set([
      PERMISSIONS.AGENT_INTERACT,
      PERMISSIONS.VAULT_READ,
      PERMISSIONS.VAULT_WRITE,
      PERMISSIONS.VOICE_ACCESS,
      PERMISSIONS.VOICE_COMMAND,
      PERMISSIONS.API_BROWSER
    ]));

    // Agent permissions (for AI agent operations)
    this.rolePermissions.set(USER_ROLES.AGENT, new Set([
      PERMISSIONS.AGENT_INTERACT,
      PERMISSIONS.VAULT_READ,
      PERMISSIONS.API_EXTERNAL,
      PERMISSIONS.API_WEBHOOK,
      PERMISSIONS.API_BROWSER
    ]));

    // Viewer permissions (read-only access)
    this.rolePermissions.set(USER_ROLES.VIEWER, new Set([
      PERMISSIONS.VAULT_READ,
      PERMISSIONS.VOICE_ACCESS
    ]));

    // System permissions (for system operations)
    this.rolePermissions.set(USER_ROLES.SYSTEM, new Set([
      PERMISSIONS.SYSTEM_LOGS,
      PERMISSIONS.AGENT_MODIFY,
      PERMISSIONS.VAULT_READ,
      PERMISSIONS.VAULT_WRITE
    ]));
  }

  initializeAuthProviders() {
    // Local authentication provider
    this.authProviders.set('local', {
      authenticate: this.authenticateLocal.bind(this),
      validate: this.validateLocalSession.bind(this),
      logout: this.logoutLocal.bind(this)
    });

    // Token-based authentication
    this.authProviders.set('token', {
      authenticate: this.authenticateToken.bind(this),
      validate: this.validateTokenSession.bind(this),
      logout: this.logoutToken.bind(this)
    });

    // System authentication (for internal operations)
    this.authProviders.set('system', {
      authenticate: this.authenticateSystem.bind(this),
      validate: this.validateSystemSession.bind(this),
      logout: this.logoutSystem.bind(this)
    });
  }

  setupSessionManagement() {
    const sessionTimeout = getConfig('security.sessionTimeout', 3600000); // 1 hour default
    
    // Setup session cleanup interval
    setInterval(() => {
      this.cleanupExpiredSessions();
    }, 300000); // Check every 5 minutes

    // Watch for configuration changes
    watchConfig('security.sessionTimeout', (newTimeout) => {
      logInfo('Session timeout updated', { 
        oldTimeout: sessionTimeout, 
        newTimeout 
      }, this.context);
    });
  }

  setupSecurityMonitoring() {
    // Monitor failed authentication attempts
    this.maxFailedAttempts = getConfig('security.maxFailedAttempts', 5);
    this.lockoutDuration = getConfig('security.lockoutDuration', 900000); // 15 minutes
    
    // Setup automatic lockout cleanup
    setInterval(() => {
      this.cleanupFailedAttempts();
    }, 60000); // Check every minute
  }

  async loadAuthenticationState() {
    try {
      // In a real implementation, this would load from secure storage
      const savedState = localStorage.getItem('hearthlink_auth_state');
      if (savedState) {
        const authData = JSON.parse(savedState);
        
        // Validate and restore session if valid
        if (authData.sessionId && authData.expiresAt > Date.now()) {
          await this.restoreSession(authData);
        } else {
          // Clear expired state
          localStorage.removeItem('hearthlink_auth_state');
        }
      }
    } catch (error) {
      logWarn('Failed to load authentication state', {
        error: error.message
      }, this.context);
    }
  }

  async authenticate(provider, credentials) {
    const authContext = createContext('authentication', 'security', {
      provider,
      userId: credentials.userId || credentials.username
    });

    try {
      this.authState = AUTH_STATES.AUTHENTICATING;
      
      // Check for account lockout
      if (this.isAccountLocked(credentials.userId || credentials.username)) {
        throw new AuthenticationError('Account is locked due to failed attempts', {
          lockoutExpires: this.getFailedAttemptData(credentials.userId || credentials.username).lockoutExpires
        });
      }

      const authProvider = this.authProviders.get(provider);
      if (!authProvider) {
        throw new AuthenticationError(`Authentication provider '${provider}' not found`);
      }

      // Perform authentication
      const authResult = await authProvider.authenticate(credentials);
      
      if (authResult.success) {
        // Clear failed attempts on successful authentication
        this.clearFailedAttempts(credentials.userId || credentials.username);
        
        // Create session
        const session = await this.createSession(authResult.user, provider);
        
        // Update authentication state
        this.currentUser = authResult.user;
        this.authState = AUTH_STATES.AUTHENTICATED;
        
        // Save authentication state
        await this.saveAuthenticationState(session);
        
        securityEvent('authentication_success', {
          userId: authResult.user.id,
          provider,
          sessionId: session.id
        }, authContext);
        
        logInfo('User authenticated successfully', {
          userId: authResult.user.id,
          role: authResult.user.role,
          provider,
          sessionId: session.id
        }, authContext);
        
        // Emit authentication event
        window.dispatchEvent(new CustomEvent('userAuthenticated', {
          detail: { user: authResult.user, session }
        }));
        
        return { success: true, user: authResult.user, session };
        
      } else {
        // Record failed attempt
        this.recordFailedAttempt(credentials.userId || credentials.username);
        
        securityEvent('authentication_failed', {
          userId: credentials.userId || credentials.username,
          provider,
          reason: authResult.error
        }, authContext);
        
        throw new AuthenticationError(authResult.error || 'Authentication failed');
      }
      
    } catch (error) {
      this.authState = AUTH_STATES.UNAUTHENTICATED;
      
      if (!(error instanceof AuthenticationError)) {
        logError('Authentication error', {
          error: error.message,
          stack: error.stack
        }, authContext);
      }
      
      throw error;
    }
  }

  async authenticateLocal(credentials) {
    // Local authentication implementation
    const { username, password } = credentials;
    
    // In a real implementation, this would validate against a secure database
    const users = getConfig('authentication.localUsers', {});
    const user = users[username];
    
    if (!user) {
      return { success: false, error: 'Invalid username or password' };
    }
    
    // Simple password validation (in production, use proper hashing)
    if (user.password !== password) {
      return { success: false, error: 'Invalid username or password' };
    }
    
    return {
      success: true,
      user: {
        id: user.id || username,
        username,
        role: user.role || USER_ROLES.USER,
        permissions: this.rolePermissions.get(user.role || USER_ROLES.USER),
        profile: user.profile || {}
      }
    };
  }

  async authenticateToken(credentials) {
    // Token-based authentication implementation
    const { token } = credentials;
    
    try {
      // In a real implementation, this would validate JWT or similar
      const tokenData = this.parseToken(token);
      
      if (tokenData.exp < Date.now() / 1000) {
        return { success: false, error: 'Token expired' };
      }
      
      return {
        success: true,
        user: {
          id: tokenData.sub,
          username: tokenData.username,
          role: tokenData.role || USER_ROLES.USER,
          permissions: this.rolePermissions.get(tokenData.role || USER_ROLES.USER),
          profile: tokenData.profile || {}
        }
      };
      
    } catch (error) {
      return { success: false, error: 'Invalid token' };
    }
  }

  async authenticateSystem(credentials) {
    // System authentication for internal operations
    const { systemKey, component } = credentials;
    
    const validSystemKey = getConfig('security.systemKey');
    if (!validSystemKey || systemKey !== validSystemKey) {
      return { success: false, error: 'Invalid system key' };
    }
    
    return {
      success: true,
      user: {
        id: `system:${component}`,
        username: 'system',
        role: USER_ROLES.SYSTEM,
        permissions: this.rolePermissions.get(USER_ROLES.SYSTEM),
        profile: { component }
      }
    };
  }

  async createSession(user, provider) {
    const sessionId = this.generateSessionId();
    const expiresAt = Date.now() + getConfig('security.sessionTimeout', 3600000);
    
    const session = {
      id: sessionId,
      userId: user.id,
      user,
      provider,
      type: SESSION_TYPES.USER,
      createdAt: Date.now(),
      expiresAt,
      lastActivityAt: Date.now(),
      ipAddress: this.getClientIP(),
      userAgent: navigator.userAgent
    };
    
    this.sessions.set(sessionId, session);
    
    // Setup session timeout
    this.sessionTimeouts.set(sessionId, setTimeout(() => {
      this.expireSession(sessionId);
    }, expiresAt - Date.now()));
    
    return session;
  }

  async restoreSession(authData) {
    try {
      const session = this.sessions.get(authData.sessionId);
      if (session && session.expiresAt > Date.now()) {
        this.currentUser = session.user;
        this.authState = AUTH_STATES.AUTHENTICATED;
        
        logInfo('Session restored', {
          userId: session.userId,
          sessionId: session.id
        }, this.context);
        
        return session;
      }
    } catch (error) {
      logWarn('Failed to restore session', {
        error: error.message
      }, this.context);
    }
    
    return null;
  }

  async saveAuthenticationState(session) {
    try {
      const authState = {
        sessionId: session.id,
        userId: session.userId,
        expiresAt: session.expiresAt
      };
      
      localStorage.setItem('hearthlink_auth_state', JSON.stringify(authState));
    } catch (error) {
      logWarn('Failed to save authentication state', {
        error: error.message
      }, this.context);
    }
  }

  hasPermission(permission, user = null) {
    const currentUser = user || this.currentUser;
    if (!currentUser || !currentUser.permissions) {
      return false;
    }
    
    return currentUser.permissions.has(permission);
  }

  checkPermission(permission, user = null) {
    if (!this.hasPermission(permission, user)) {
      const currentUser = user || this.currentUser;
      const context = createContext('permission-check', 'security', {
        userId: currentUser?.id,
        permission
      });
      
      securityEvent('permission_denied', {
        userId: currentUser?.id,
        permission,
        userRole: currentUser?.role
      }, context);
      
      throw new AuthenticationError(`Permission denied: ${permission}`, {
        permission,
        userRole: currentUser?.role,
        userId: currentUser?.id
      });
    }
    
    return true;
  }

  async logout(sessionId = null) {
    const targetSessionId = sessionId || this.getCurrentSessionId();
    const session = this.sessions.get(targetSessionId);
    
    if (session) {
      const logoutContext = createContext('logout', 'security', {
        userId: session.userId,
        sessionId: targetSessionId
      });
      
      // Clear session timeout
      if (this.sessionTimeouts.has(targetSessionId)) {
        clearTimeout(this.sessionTimeouts.get(targetSessionId));
        this.sessionTimeouts.delete(targetSessionId);
      }
      
      // Remove session
      this.sessions.delete(targetSessionId);
      
      // Call provider logout
      const provider = this.authProviders.get(session.provider);
      if (provider && provider.logout) {
        await provider.logout(session);
      }
      
      // Update state if current session
      if (targetSessionId === this.getCurrentSessionId()) {
        this.currentUser = null;
        this.authState = AUTH_STATES.UNAUTHENTICATED;
        localStorage.removeItem('hearthlink_auth_state');
      }
      
      securityEvent('logout', {
        userId: session.userId,
        sessionId: targetSessionId
      }, logoutContext);
      
      logInfo('User logged out', {
        userId: session.userId,
        sessionId: targetSessionId
      }, logoutContext);
      
      // Emit logout event
      window.dispatchEvent(new CustomEvent('userLoggedOut', {
        detail: { userId: session.userId, sessionId: targetSessionId }
      }));
    }
  }

  getCurrentSessionId() {
    // In a real implementation, this would get the current session ID
    const authState = localStorage.getItem('hearthlink_auth_state');
    if (authState) {
      try {
        return JSON.parse(authState).sessionId;
      } catch (error) {
        return null;
      }
    }
    return null;
  }

  validateSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (!session) {
      return { valid: false, reason: 'session_not_found' };
    }
    
    if (session.expiresAt <= Date.now()) {
      this.expireSession(sessionId);
      return { valid: false, reason: 'session_expired' };
    }
    
    // Update last activity
    session.lastActivityAt = Date.now();
    
    return { valid: true, session };
  }

  expireSession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session) {
      securityEvent('session_expired', {
        userId: session.userId,
        sessionId
      }, this.context);
      
      this.logout(sessionId);
    }
  }

  cleanupExpiredSessions() {
    const now = Date.now();
    const expiredSessions = [];
    
    for (const [sessionId, session] of this.sessions.entries()) {
      if (session.expiresAt <= now) {
        expiredSessions.push(sessionId);
      }
    }
    
    expiredSessions.forEach(sessionId => {
      this.expireSession(sessionId);
    });
    
    if (expiredSessions.length > 0) {
      logInfo('Cleaned up expired sessions', {
        count: expiredSessions.length
      }, this.context);
    }
  }

  recordFailedAttempt(userId) {
    const now = Date.now();
    const attemptData = this.failedAttempts.get(userId) || {
      count: 0,
      firstAttempt: now,
      lastAttempt: now,
      lockoutExpires: null
    };
    
    attemptData.count++;
    attemptData.lastAttempt = now;
    
    if (attemptData.count >= this.maxFailedAttempts) {
      attemptData.lockoutExpires = now + this.lockoutDuration;
      
      securityEvent('account_locked', {
        userId,
        failedAttempts: attemptData.count,
        lockoutExpires: attemptData.lockoutExpires
      }, this.context);
    }
    
    this.failedAttempts.set(userId, attemptData);
  }

  isAccountLocked(userId) {
    const attemptData = this.failedAttempts.get(userId);
    return attemptData && attemptData.lockoutExpires && attemptData.lockoutExpires > Date.now();
  }

  getFailedAttemptData(userId) {
    return this.failedAttempts.get(userId) || null;
  }

  clearFailedAttempts(userId) {
    this.failedAttempts.delete(userId);
  }

  cleanupFailedAttempts() {
    const now = Date.now();
    const toRemove = [];
    
    for (const [userId, attemptData] of this.failedAttempts.entries()) {
      if (attemptData.lockoutExpires && attemptData.lockoutExpires <= now) {
        toRemove.push(userId);
      }
    }
    
    toRemove.forEach(userId => {
      this.clearFailedAttempts(userId);
      securityEvent('lockout_expired', { userId }, this.context);
    });
  }

  // Utility methods
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  parseToken(token) {
    // Simple token parsing (in production, use proper JWT library)
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid token format');
      }
      
      const payload = JSON.parse(atob(parts[1]));
      return payload;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  getClientIP() {
    // In a real implementation, this would get the actual client IP
    return '127.0.0.1';
  }

  // Validation methods for different providers
  async validateLocalSession(session) {
    return this.validateSession(session.id);
  }

  async validateTokenSession(session) {
    return this.validateSession(session.id);
  }

  async validateSystemSession(session) {
    return this.validateSession(session.id);
  }

  // Logout methods for different providers
  async logoutLocal(session) {
    // Local logout cleanup
    return true;
  }

  async logoutToken(session) {
    // Token logout cleanup
    return true;
  }

  async logoutSystem(session) {
    // System logout cleanup
    return true;
  }

  // Public API methods
  isAuthenticated() {
    return this.authState === AUTH_STATES.AUTHENTICATED && this.currentUser !== null;
  }

  getCurrentUser() {
    return this.currentUser;
  }

  getAuthState() {
    return this.authState;
  }

  getSessions() {
    return Array.from(this.sessions.values());
  }

  getAuthenticationStats() {
    const now = Date.now();
    const recentSessions = this.getSessions().filter(s => 
      now - s.createdAt < 3600000 // Last hour
    );
    
    return {
      totalSessions: this.sessions.size,
      recentSessions: recentSessions.length,
      currentUser: this.currentUser,
      authState: this.authState,
      failedAttempts: this.failedAttempts.size,
      lockedAccounts: Array.from(this.failedAttempts.entries())
        .filter(([, data]) => data.lockoutExpires && data.lockoutExpires > now)
        .length
    };
  }
}

// Create singleton instance
const authenticationManager = new AuthenticationManager();

// Export convenience functions
export const authenticate = (provider, credentials) => authenticationManager.authenticate(provider, credentials);
export const logout = (sessionId) => authenticationManager.logout(sessionId);
export const hasPermission = (permission, user) => authenticationManager.hasPermission(permission, user);
export const checkPermission = (permission, user) => authenticationManager.checkPermission(permission, user);
export const isAuthenticated = () => authenticationManager.isAuthenticated();
export const getCurrentUser = () => authenticationManager.getCurrentUser();
export const getAuthState = () => authenticationManager.getAuthState();
export const validateSession = (sessionId) => authenticationManager.validateSession(sessionId);
export const getAuthStats = () => authenticationManager.getAuthenticationStats();

export default authenticationManager;