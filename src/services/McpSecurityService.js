/**
 * MCP Security Service
 * 
 * Comprehensive security monitoring and protection system for Model Context Protocol (MCP) servers.
 * Addresses critical vulnerabilities identified in cybersecurity research:
 * 
 * - CVE-2025-49596: RCE vulnerability in MCP Inspector
 * - Command injection vulnerabilities
 * - Prompt injection attacks
 * - OAuth token security issues
 * - Malicious server detection
 * - Protocol integrity validation
 */

class McpSecurityService {
  constructor() {
    this.securityEvents = [];
    this.threatPatterns = {
      commandInjection: [
        /os\.system\([^)]*\)/g,
        /subprocess\.call\([^)]*\)/g,
        /exec\([^)]*\)/g,
        /eval\([^)]*\)/g,
        /system\([^)]*\)/g,
        /shell_exec\([^)]*\)/g,
        /popen\([^)]*\)/g,
        /Runtime\.getRuntime\(\)\.exec\([^)]*\)/g
      ],
      promptInjection: [
        /ignore\s+previous\s+instructions/i,
        /forget\s+everything\s+above/i,
        /you\s+are\s+now\s+a\s+different\s+ai/i,
        /system:\s*override/i,
        /jailbreak/i,
        /pretend\s+you\s+are/i,
        /act\s+as\s+if\s+you\s+are/i,
        /role:\s*admin/i,
        /\[INST\]/i,
        /\<\|im_start\|\>/i,
        /\<system\>/i,
        /assistant:\s*\(/i
      ],
      maliciousPayloads: [
        /\$\{.*\}/g, // Template injection
        /\<script\>/i, // XSS
        /javascript:/i, // JavaScript protocol
        /vbscript:/i, // VBScript protocol
        /data:.*base64/i, // Base64 data URLs
        /\.\.\//g, // Directory traversal
        /\/etc\/passwd/i, // System file access
        /cmd\.exe/i, // Windows command execution
        /powershell/i, // PowerShell execution
        /bash\s+-c/i // Bash command execution
      ]
    };
    
    this.vulnerableVersions = {
      'mcp-inspector': ['<0.14.1'],
      'claude-mcp': ['<1.0.0'],
      'anthropic-mcp': ['<2.0.0']
    };
    
    this.securityConfig = {
      realTimeMonitoring: true,
      quarantineEnabled: true,
      autoBlockThreats: true,
      logAllActivity: true,
      strictValidation: true,
      tokenRotationEnabled: true,
      integrityChecksEnabled: true
    };
    
    this.monitoringActive = false;
    this.quarantinedServers = new Set();
    this.trustedServers = new Set();
    this.sessionTokens = new Map();
    this.mcpConnections = new Map();
    
    this.initializeSecurityService();
  }

  // Initialize the security service
  async initializeSecurityService() {
    try {
      // Load security configuration
      await this.loadSecurityConfig();
      
      // Initialize monitoring
      if (this.securityConfig.realTimeMonitoring) {
        this.startRealTimeMonitoring();
      }
      
      // Validate existing MCP connections
      await this.validateExistingConnections();
      
      // Set up integrity checks
      if (this.securityConfig.integrityChecksEnabled) {
        this.scheduleIntegrityChecks();
      }
      
      this.logSecurityEvent('security_service_initialized', 'MCP Security Service initialized successfully', 'info');
      
    } catch (error) {
      this.logSecurityEvent('initialization_error', `Failed to initialize MCP Security Service: ${error.message}`, 'critical');
      throw error;
    }
  }

  // Start real-time monitoring
  startRealTimeMonitoring() {
    if (this.monitoringActive) return;
    
    this.monitoringActive = true;
    
    // Monitor MCP communications every 1 second
    this.monitoringInterval = setInterval(() => {
      this.monitorMcpCommunications();
    }, 1000);
    
    // Perform security scans every 30 seconds
    this.scanInterval = setInterval(() => {
      this.performSecurityScan();
    }, 30000);
    
    // Rotate session tokens every 5 minutes
    if (this.securityConfig.tokenRotationEnabled) {
      this.tokenRotationInterval = setInterval(() => {
        this.rotateSessionTokens();
      }, 300000);
    }
    
    this.logSecurityEvent('monitoring_started', 'Real-time MCP security monitoring started', 'info');
  }

  // Stop real-time monitoring
  stopRealTimeMonitoring() {
    this.monitoringActive = false;
    
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    
    if (this.scanInterval) {
      clearInterval(this.scanInterval);
      this.scanInterval = null;
    }
    
    if (this.tokenRotationInterval) {
      clearInterval(this.tokenRotationInterval);
      this.tokenRotationInterval = null;
    }
    
    this.logSecurityEvent('monitoring_stopped', 'Real-time MCP security monitoring stopped', 'info');
  }

  // Validate MCP server before connection
  async validateMcpServer(serverInfo) {
    const { name, version, url, capabilities } = serverInfo;
    const securityReport = {
      serverName: name,
      version,
      url,
      vulnerabilities: [],
      threats: [],
      recommendations: [],
      trustLevel: 'unknown',
      allowConnection: false
    };

    try {
      // Check for known vulnerable versions
      const vulnerableVersions = this.vulnerableVersions[name.toLowerCase()];
      if (vulnerableVersions) {
        const isVulnerable = this.checkVersionVulnerability(version, vulnerableVersions);
        if (isVulnerable) {
          securityReport.vulnerabilities.push({
            type: 'vulnerable_version',
            severity: 'critical',
            description: `Server ${name} version ${version} contains known security vulnerabilities`,
            recommendation: 'Update to latest secure version immediately'
          });
        }
      }

      // Check server URL for suspicious patterns
      if (this.containsMaliciousPatterns(url)) {
        securityReport.threats.push({
          type: 'malicious_url',
          severity: 'high',
          description: `Server URL contains suspicious patterns: ${url}`,
          recommendation: 'Verify server authenticity before connecting'
        });
      }

      // Validate server capabilities
      if (capabilities && Array.isArray(capabilities)) {
        const suspiciousCapabilities = capabilities.filter(cap => 
          cap.includes('exec') || cap.includes('system') || cap.includes('shell')
        );
        
        if (suspiciousCapabilities.length > 0) {
          securityReport.threats.push({
            type: 'suspicious_capabilities',
            severity: 'medium',
            description: `Server declares suspicious capabilities: ${suspiciousCapabilities.join(', ')}`,
            recommendation: 'Review server capabilities and limit permissions'
          });
        }
      }

      // Check if server is in trusted list
      if (this.trustedServers.has(name)) {
        securityReport.trustLevel = 'trusted';
      } else if (this.quarantinedServers.has(name)) {
        securityReport.trustLevel = 'quarantined';
        securityReport.allowConnection = false;
        securityReport.recommendations.push('Server is quarantined due to previous security violations');
      }

      // Make final connection decision
      if (securityReport.vulnerabilities.length === 0 && 
          securityReport.threats.length === 0 && 
          securityReport.trustLevel !== 'quarantined') {
        securityReport.allowConnection = true;
        securityReport.trustLevel = securityReport.trustLevel === 'trusted' ? 'trusted' : 'verified';
      }

      this.logSecurityEvent('server_validation_completed', 
        `MCP server ${name} validation completed. Trust level: ${securityReport.trustLevel}`, 
        securityReport.allowConnection ? 'info' : 'warning'
      );

      return securityReport;

    } catch (error) {
      this.logSecurityEvent('server_validation_error', 
        `Failed to validate MCP server ${name}: ${error.message}`, 
        'error'
      );
      
      securityReport.vulnerabilities.push({
        type: 'validation_error',
        severity: 'high',
        description: `Server validation failed: ${error.message}`,
        recommendation: 'Manual security review required'
      });
      
      return securityReport;
    }
  }

  // Monitor MCP communications for threats
  monitorMcpCommunications() {
    if (!this.monitoringActive) return;

    try {
      // Get active MCP connections
      const connections = Array.from(this.mcpConnections.values());
      
      connections.forEach(connection => {
        // Check for command injection in recent messages
        if (connection.recentMessages) {
          connection.recentMessages.forEach(message => {
            if (this.detectCommandInjection(message.content)) {
              this.handleThreatDetected('command_injection', connection, message);
            }
            
            if (this.detectPromptInjection(message.content)) {
              this.handleThreatDetected('prompt_injection', connection, message);
            }
          });
        }
        
        // Check session token validity
        if (connection.sessionToken) {
          const tokenValid = this.validateSessionToken(connection.sessionToken);
          if (!tokenValid) {
            this.handleThreatDetected('invalid_session_token', connection);
          }
        }
        
        // Monitor for suspicious activity patterns
        if (connection.activityLog) {
          const suspiciousActivity = this.detectSuspiciousActivity(connection.activityLog);
          if (suspiciousActivity) {
            this.handleThreatDetected('suspicious_activity', connection, suspiciousActivity);
          }
        }
      });

    } catch (error) {
      this.logSecurityEvent('monitoring_error', 
        `Error during MCP communication monitoring: ${error.message}`, 
        'error'
      );
    }
  }

  // Detect command injection attempts
  detectCommandInjection(content) {
    if (!content || typeof content !== 'string') return false;
    
    return this.threatPatterns.commandInjection.some(pattern => pattern.test(content));
  }

  // Detect prompt injection attempts
  detectPromptInjection(content) {
    if (!content || typeof content !== 'string') return false;
    
    return this.threatPatterns.promptInjection.some(pattern => pattern.test(content));
  }

  // Detect malicious patterns
  containsMaliciousPatterns(content) {
    if (!content || typeof content !== 'string') return false;
    
    return this.threatPatterns.maliciousPayloads.some(pattern => pattern.test(content));
  }

  // Handle detected threats
  handleThreatDetected(threatType, connection, details = null) {
    const threat = {
      type: threatType,
      timestamp: new Date().toISOString(),
      connection: connection.id,
      serverName: connection.serverName,
      details: details,
      severity: this.getThreatSeverity(threatType),
      action: 'detected'
    };

    this.logSecurityEvent('threat_detected', 
      `${threatType} detected on MCP connection ${connection.id}`, 
      threat.severity
    );

    // Auto-block if configured
    if (this.securityConfig.autoBlockThreats) {
      this.blockThreat(threat, connection);
    }

    // Quarantine server if multiple threats detected
    if (this.shouldQuarantineServer(connection.serverName)) {
      this.quarantineServer(connection.serverName);
    }

    return threat;
  }

  // Block detected threat
  blockThreat(threat, connection) {
    try {
      // Block the specific action
      if (threat.details && threat.details.messageId) {
        // Block message from being processed
        this.blockMessage(threat.details.messageId);
      }
      
      // Log blocking action
      this.logSecurityEvent('threat_blocked', 
        `${threat.type} blocked on connection ${connection.id}`, 
        'info'
      );
      
      threat.action = 'blocked';
      
      // Notify user if critical
      if (threat.severity === 'critical') {
        this.notifyUserOfCriticalThreat(threat);
      }
      
    } catch (error) {
      this.logSecurityEvent('blocking_error', 
        `Failed to block threat: ${error.message}`, 
        'error'
      );
    }
  }

  // Quarantine MCP server
  quarantineServer(serverName) {
    this.quarantinedServers.add(serverName);
    this.trustedServers.delete(serverName);
    
    // Disconnect all connections from quarantined server
    this.mcpConnections.forEach((connection, id) => {
      if (connection.serverName === serverName) {
        this.disconnectMcpServer(id);
      }
    });
    
    this.logSecurityEvent('server_quarantined', 
      `MCP server ${serverName} quarantined due to security violations`, 
      'warning'
    );
  }

  // Perform comprehensive security scan
  async performSecurityScan() {
    try {
      const scanResults = {
        timestamp: new Date().toISOString(),
        connections: this.mcpConnections.size,
        vulnerabilities: [],
        threats: [],
        quarantinedServers: Array.from(this.quarantinedServers),
        trustedServers: Array.from(this.trustedServers),
        securityScore: 100
      };

      // Scan all active connections
      for (const [id, connection] of this.mcpConnections) {
        const connectionScan = await this.scanMcpConnection(connection);
        scanResults.vulnerabilities.push(...connectionScan.vulnerabilities);
        scanResults.threats.push(...connectionScan.threats);
      }

      // Calculate security score
      scanResults.securityScore = this.calculateSecurityScore(scanResults);

      // Store scan results
      this.lastSecurityScan = scanResults;

      this.logSecurityEvent('security_scan_completed', 
        `Security scan completed. Found ${scanResults.vulnerabilities.length} vulnerabilities, ${scanResults.threats.length} threats`, 
        scanResults.vulnerabilities.length > 0 ? 'warning' : 'info'
      );

      return scanResults;

    } catch (error) {
      this.logSecurityEvent('security_scan_error', 
        `Security scan failed: ${error.message}`, 
        'error'
      );
      throw error;
    }
  }

  // Scan individual MCP connection
  async scanMcpConnection(connection) {
    const scan = {
      connectionId: connection.id,
      serverName: connection.serverName,
      vulnerabilities: [],
      threats: []
    };

    try {
      // Check for session token security
      if (!connection.sessionToken || !this.validateSessionToken(connection.sessionToken)) {
        scan.vulnerabilities.push({
          type: 'weak_session_token',
          severity: 'medium',
          description: 'Connection lacks secure session token',
          recommendation: 'Implement secure session token authentication'
        });
      }

      // Check for CSRF protection
      if (!connection.csrfProtection) {
        scan.vulnerabilities.push({
          type: 'no_csrf_protection',
          severity: 'high',
          description: 'Connection lacks CSRF protection',
          recommendation: 'Implement CSRF token validation'
        });
      }

      // Check for origin validation
      if (!connection.originValidation) {
        scan.vulnerabilities.push({
          type: 'no_origin_validation',
          severity: 'high',
          description: 'Connection lacks origin validation',
          recommendation: 'Implement origin header validation'
        });
      }

      // Check for suspicious activity
      if (connection.activityLog) {
        const suspiciousPatterns = this.analyzeSuspiciousActivity(connection.activityLog);
        suspiciousPatterns.forEach(pattern => {
          scan.threats.push({
            type: 'suspicious_pattern',
            severity: 'medium',
            description: `Suspicious activity pattern detected: ${pattern.type}`,
            details: pattern
          });
        });
      }

    } catch (error) {
      scan.vulnerabilities.push({
        type: 'scan_error',
        severity: 'low',
        description: `Failed to scan connection: ${error.message}`,
        recommendation: 'Manual security review required'
      });
    }

    return scan;
  }

  // Validate session token
  validateSessionToken(token) {
    if (!token || typeof token !== 'string') return false;
    
    try {
      // Check token format (should be cryptographically secure)
      if (token.length < 32) return false;
      
      // Check if token is in valid tokens map
      const tokenData = this.sessionTokens.get(token);
      if (!tokenData) return false;
      
      // Check if token has expired
      if (Date.now() > tokenData.expires) {
        this.sessionTokens.delete(token);
        return false;
      }
      
      return true;
      
    } catch (error) {
      return false;
    }
  }

  // Generate secure session token
  generateSessionToken(connectionId) {
    const token = this.generateSecureToken();
    const expiresAt = Date.now() + (60 * 60 * 1000); // 1 hour
    
    this.sessionTokens.set(token, {
      connectionId,
      created: Date.now(),
      expires: expiresAt
    });
    
    return token;
  }

  // Rotate session tokens
  rotateSessionTokens() {
    const expiredTokens = [];
    
    this.sessionTokens.forEach((tokenData, token) => {
      if (Date.now() > tokenData.expires) {
        expiredTokens.push(token);
      }
    });
    
    expiredTokens.forEach(token => {
      this.sessionTokens.delete(token);
    });
    
    this.logSecurityEvent('token_rotation', 
      `Rotated ${expiredTokens.length} expired session tokens`, 
      'info'
    );
  }

  // Generate cryptographically secure token
  generateSecureToken() {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  // Get threat severity level
  getThreatSeverity(threatType) {
    const severityMap = {
      'command_injection': 'critical',
      'prompt_injection': 'high',
      'malicious_payload': 'high',
      'suspicious_activity': 'medium',
      'invalid_session_token': 'medium',
      'weak_authentication': 'medium',
      'unauthorized_access': 'high'
    };
    
    return severityMap[threatType] || 'low';
  }

  // Calculate overall security score
  calculateSecurityScore(scanResults) {
    let score = 100;
    
    // Deduct points for vulnerabilities
    scanResults.vulnerabilities.forEach(vuln => {
      switch (vuln.severity) {
        case 'critical': score -= 25; break;
        case 'high': score -= 15; break;
        case 'medium': score -= 10; break;
        case 'low': score -= 5; break;
      }
    });
    
    // Deduct points for threats
    scanResults.threats.forEach(threat => {
      switch (threat.severity) {
        case 'critical': score -= 20; break;
        case 'high': score -= 10; break;
        case 'medium': score -= 5; break;
        case 'low': score -= 2; break;
      }
    });
    
    // Bonus for security measures
    if (this.securityConfig.realTimeMonitoring) score += 5;
    if (this.securityConfig.autoBlockThreats) score += 5;
    if (this.securityConfig.tokenRotationEnabled) score += 3;
    if (this.securityConfig.integrityChecksEnabled) score += 3;
    
    return Math.max(0, Math.min(100, score));
  }

  // Log security events
  logSecurityEvent(eventType, message, severity = 'info') {
    const event = {
      id: `mcp-sec-${Date.now()}`,
      timestamp: new Date().toISOString(),
      type: eventType,
      message,
      severity,
      service: 'mcp-security'
    };
    
    this.securityEvents.push(event);
    
    // Keep only last 1000 events
    if (this.securityEvents.length > 1000) {
      this.securityEvents = this.securityEvents.slice(-1000);
    }
    
    // Log to console for debugging
    console.log(`[MCP Security] ${severity.toUpperCase()}: ${message}`);
    
    // Store in localStorage for persistence
    try {
      localStorage.setItem('mcpSecurityEvents', JSON.stringify(this.securityEvents.slice(-100)));
    } catch (error) {
      console.warn('Failed to store security events:', error);
    }
  }

  // Get security events
  getSecurityEvents(limit = 50) {
    return this.securityEvents.slice(-limit).reverse();
  }

  // Get security status
  getSecurityStatus() {
    return {
      monitoringActive: this.monitoringActive,
      activeConnections: this.mcpConnections.size,
      quarantinedServers: Array.from(this.quarantinedServers),
      trustedServers: Array.from(this.trustedServers),
      lastScan: this.lastSecurityScan,
      securityScore: this.lastSecurityScan ? this.lastSecurityScan.securityScore : 0,
      eventsCount: this.securityEvents.length
    };
  }

  // Emergency kill switch
  emergencyKillSwitch() {
    this.logSecurityEvent('emergency_kill_switch', 
      'Emergency kill switch activated - terminating all MCP connections', 
      'critical'
    );
    
    // Disconnect all MCP servers
    this.mcpConnections.forEach((connection, id) => {
      this.disconnectMcpServer(id);
    });
    
    // Clear all session tokens
    this.sessionTokens.clear();
    
    // Stop monitoring
    this.stopRealTimeMonitoring();
    
    // Clear trusted servers
    this.trustedServers.clear();
    
    return {
      success: true,
      message: 'Emergency kill switch activated',
      timestamp: new Date().toISOString()
    };
  }

  // Disconnect MCP server
  disconnectMcpServer(connectionId) {
    const connection = this.mcpConnections.get(connectionId);
    if (connection) {
      this.mcpConnections.delete(connectionId);
      
      // Revoke session token
      if (connection.sessionToken) {
        this.sessionTokens.delete(connection.sessionToken);
      }
      
      this.logSecurityEvent('server_disconnected', 
        `MCP server ${connection.serverName} disconnected`, 
        'info'
      );
    }
  }

  // Load security configuration
  async loadSecurityConfig() {
    try {
      const saved = localStorage.getItem('mcpSecurityConfig');
      if (saved) {
        const config = JSON.parse(saved);
        this.securityConfig = { ...this.securityConfig, ...config };
      }
    } catch (error) {
      console.warn('Failed to load MCP security config:', error);
    }
  }

  // Save security configuration
  async saveSecurityConfig() {
    try {
      localStorage.setItem('mcpSecurityConfig', JSON.stringify(this.securityConfig));
      this.logSecurityEvent('config_saved', 'MCP security configuration saved', 'info');
    } catch (error) {
      this.logSecurityEvent('config_save_error', `Failed to save security config: ${error.message}`, 'error');
    }
  }

  // Cleanup on service shutdown
  shutdown() {
    this.stopRealTimeMonitoring();
    this.mcpConnections.clear();
    this.sessionTokens.clear();
    this.logSecurityEvent('service_shutdown', 'MCP Security Service shutdown', 'info');
  }
}

// Export singleton instance
const mcpSecurityService = new McpSecurityService();
export default mcpSecurityService;