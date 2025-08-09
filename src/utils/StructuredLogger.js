/**
 * Structured Logger Utility
 * Provides consistent structured logging across the application
 */

class StructuredLogger {
    constructor(options = {}) {
        this.serviceName = options.serviceName || 'hearthlink';
        this.version = options.version || '1.0.0';
        this.environment = options.environment || process.env.NODE_ENV || 'development';
        this.enableConsole = options.enableConsole !== false;
        this.enableStorage = options.enableStorage !== false;
        this.maxStoredLogs = options.maxStoredLogs || 1000;
    }

    /**
     * Create structured log entry
     */
    createLogEntry(level, message, metadata = {}) {
        return {
            timestamp: new Date().toISOString(),
            level: level.toUpperCase(),
            service: this.serviceName,
            version: this.version,
            environment: this.environment,
            message,
            metadata: {
                ...metadata,
                url: typeof window !== 'undefined' ? window.location.href : undefined,
                userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
                sessionId: this.getSessionId()
            },
            traceId: this.generateTraceId()
        };
    }

    /**
     * Log error with full context
     */
    error(message, error, metadata = {}) {
        const logEntry = this.createLogEntry('error', message, {
            ...metadata,
            error: {
                name: error?.name,
                message: error?.message,
                stack: error?.stack,
                code: error?.code
            }
        });

        this.outputLog(logEntry);
        this.storeLog(logEntry);
        
        // Send to error tracking service in production
        if (this.environment === 'production') {
            this.sendToErrorService(logEntry);
        }
    }

    /**
     * Log warning
     */
    warn(message, metadata = {}) {
        const logEntry = this.createLogEntry('warn', message, metadata);
        this.outputLog(logEntry);
        this.storeLog(logEntry);
    }

    /**
     * Log info
     */
    info(message, metadata = {}) {
        const logEntry = this.createLogEntry('info', message, metadata);
        this.outputLog(logEntry);
        this.storeLog(logEntry);
    }

    /**
     * Log debug (only in development)
     */
    debug(message, metadata = {}) {
        if (this.environment === 'development') {
            const logEntry = this.createLogEntry('debug', message, metadata);
            this.outputLog(logEntry);
            this.storeLog(logEntry);
        }
    }

    /**
     * Log performance metrics
     */
    performance(operation, duration, metadata = {}) {
        const logEntry = this.createLogEntry('info', `Performance: ${operation}`, {
            ...metadata,
            performance: {
                operation,
                duration,
                unit: 'ms'
            }
        });
        
        this.outputLog(logEntry);
        this.storeLog(logEntry);
    }

    /**
     * Log user action
     */
    userAction(action, metadata = {}) {
        const logEntry = this.createLogEntry('info', `User Action: ${action}`, {
            ...metadata,
            category: 'user_action',
            action
        });
        
        this.outputLog(logEntry);
        this.storeLog(logEntry);
    }

    /**
     * Output log to console
     */
    outputLog(logEntry) {
        if (!this.enableConsole) return;

        const { level, message, metadata } = logEntry;
        const style = this.getConsoleStyle(level);

        if (level === 'ERROR') {
            console.error(`${style}%s`, message, metadata);
        } else if (level === 'WARN') {
            console.warn(`${style}%s`, message, metadata);
        } else if (level === 'INFO') {
            console.info(`${style}%s`, message, metadata);
        } else {
            console.log(`${style}%s`, message, metadata);
        }
    }

    /**
     * Store log in localStorage
     */
    storeLog(logEntry) {
        if (!this.enableStorage) return;

        try {
            const existingLogs = JSON.parse(localStorage.getItem('structuredLogs') || '[]');
            existingLogs.push(logEntry);
            
            // Keep only recent logs
            const recentLogs = existingLogs.slice(-this.maxStoredLogs);
            localStorage.setItem('structuredLogs', JSON.stringify(recentLogs));
        } catch (e) {
            // Ignore localStorage errors
        }
    }

    /**
     * Send log to error tracking service
     */
    async sendToErrorService(logEntry) {
        try {
            // Example integration - replace with actual service
            /*
            await fetch('/api/logs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(logEntry)
            });
            */
        } catch (e) {
            // Silently fail - don't want logging to break the app
        }
    }

    /**
     * Get stored logs
     */
    getStoredLogs() {
        try {
            return JSON.parse(localStorage.getItem('structuredLogs') || '[]');
        } catch (e) {
            return [];
        }
    }

    /**
     * Clear stored logs
     */
    clearStoredLogs() {
        try {
            localStorage.removeItem('structuredLogs');
        } catch (e) {
            // Ignore errors
        }
    }

    /**
     * Generate unique trace ID
     */
    generateTraceId() {
        return `trace_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get or create session ID
     */
    getSessionId() {
        try {
            let sessionId = sessionStorage.getItem('logSessionId');
            if (!sessionId) {
                sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
                sessionStorage.setItem('logSessionId', sessionId);
            }
            return sessionId;
        } catch (e) {
            return 'unknown_session';
        }
    }

    /**
     * Get console styling for log level
     */
    getConsoleStyle(level) {
        const styles = {
            'ERROR': 'color: #dc3545; font-weight: bold;',
            'WARN': 'color: #ffc107; font-weight: bold;',
            'INFO': 'color: #007bff;',
            'DEBUG': 'color: #6c757d;'
        };
        return styles[level] || '';
    }
}

// Export singleton instance
export const logger = new StructuredLogger();

// Export class for custom instances
export default StructuredLogger;

// Helper functions
export const logError = (message, error, metadata) => logger.error(message, error, metadata);
export const logWarn = (message, metadata) => logger.warn(message, metadata);
export const logInfo = (message, metadata) => logger.info(message, metadata);
export const logDebug = (message, metadata) => logger.debug(message, metadata);
export const logPerformance = (operation, duration, metadata) => logger.performance(operation, duration, metadata);
export const logUserAction = (action, metadata) => logger.userAction(action, metadata);
