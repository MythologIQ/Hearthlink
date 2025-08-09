/**
 * Error Recovery Service
 * Provides automatic error recovery mechanisms
 */

class ErrorRecoveryService {
    constructor() {
        this.recoveryStrategies = new Map();
        this.recoveryAttempts = new Map();
        this.maxRecoveryAttempts = 3;
        this.isRecovering = false;
        
        this.initializeDefaultStrategies();
    }

    /**
     * Initialize default recovery strategies
     */
    initializeDefaultStrategies() {
        // Network error recovery
        this.registerStrategy('NetworkError', async (error, context) => {
            console.log('🔄 Attempting network error recovery...');
            
            // Wait for network connectivity
            await this.waitForConnectivity();
            
            // Retry the failed operation
            if (context.retryFunction) {
                return await context.retryFunction();
            }
        });

        // State corruption recovery
        this.registerStrategy('StateError', async (error, context) => {
            console.log('🔄 Attempting state recovery...');
            
            // Reset application state to safe defaults
            this.resetApplicationState();
            
            // Reload critical data
            await this.reloadCriticalData();
        });

        // UI component recovery
        this.registerStrategy('ComponentError', async (error, context) => {
            console.log('🔄 Attempting component recovery...');
            
            // Force re-render of affected component
            if (context.componentRef && context.componentRef.forceUpdate) {
                context.componentRef.forceUpdate();
            }
            
            // Clear component-specific caches
            this.clearComponentCaches(context.componentName);
        });

        // Memory error recovery
        this.registerStrategy('MemoryError', async (error, context) => {
            console.log('🔄 Attempting memory recovery...');
            
            // Clear non-essential caches
            this.clearNonEssentialCaches();
            
            // Trigger garbage collection if available
            if (window.gc) {
                window.gc();
            }
            
            // Reduce memory-intensive operations
            this.reduceMemoryOperations();
        });
    }

    /**
     * Register a recovery strategy
     */
    registerStrategy(errorType, recoveryFunction) {
        this.recoveryStrategies.set(errorType, recoveryFunction);
    }

    /**
     * Attempt to recover from an error
     */
    async attemptRecovery(error, context = {}) {
        if (this.isRecovering) {
            console.warn('⚠️ Recovery already in progress, skipping...');
            return false;
        }

        const errorType = this.classifyError(error);
        const strategy = this.recoveryStrategies.get(errorType);
        
        if (!strategy) {
            console.warn(`⚠️ No recovery strategy for error type: ${errorType}`);
            return false;
        }

        const attemptKey = `${errorType}_${context.source || 'unknown'}`;
        const currentAttempts = this.recoveryAttempts.get(attemptKey) || 0;
        
        if (currentAttempts >= this.maxRecoveryAttempts) {
            console.error(`❌ Max recovery attempts exceeded for ${errorType}`);
            return false;
        }

        this.isRecovering = true;
        this.recoveryAttempts.set(attemptKey, currentAttempts + 1);

        try {
            console.log(`🔄 Starting recovery attempt ${currentAttempts + 1}/${this.maxRecoveryAttempts} for ${errorType}`);
            
            await strategy(error, context);
            
            console.log(`✅ Recovery successful for ${errorType}`);
            this.recoveryAttempts.delete(attemptKey); // Reset counter on success
            return true;
            
        } catch (recoveryError) {
            console.error(`❌ Recovery failed for ${errorType}:`, recoveryError);
            return false;
        } finally {
            this.isRecovering = false;
        }
    }

    /**
     * Classify error type for recovery strategy selection
     */
    classifyError(error) {
        const message = error.message || '';
        const name = error.name || '';
        
        if (message.includes('network') || message.includes('fetch') || name === 'NetworkError') {
            return 'NetworkError';
        }
        
        if (message.includes('state') || message.includes('undefined') || name === 'TypeError') {
            return 'StateError';
        }
        
        if (message.includes('Component') || message.includes('render')) {
            return 'ComponentError';
        }
        
        if (message.includes('memory') || message.includes('heap')) {
            return 'MemoryError';
        }
        
        return 'GenericError';
    }

    /**
     * Wait for network connectivity
     */
    async waitForConnectivity(maxWait = 10000) {
        return new Promise((resolve) => {
            const checkConnectivity = () => {
                if (navigator.onLine) {
                    resolve();
                } else {
                    setTimeout(checkConnectivity, 1000);
                }
            };
            
            checkConnectivity();
            
            // Timeout after maxWait
            setTimeout(resolve, maxWait);
        });
    }

    /**
     * Reset application state to safe defaults
     */
    resetApplicationState() {
        try {
            // Clear potentially corrupted state
            if (typeof window !== 'undefined') {
                // Clear session storage except for essential items
                const essentialKeys = ['logSessionId', 'authToken'];
                const sessionKeys = Object.keys(sessionStorage);
                
                sessionKeys.forEach(key => {
                    if (!essentialKeys.includes(key)) {
                        sessionStorage.removeItem(key);
                    }
                });
            }
        } catch (e) {
            console.warn('Failed to reset application state:', e);
        }
    }

    /**
     * Reload critical data
     */
    async reloadCriticalData() {
        try {
            // Trigger reload of critical application data
            if (window.hearthlink && window.hearthlink.reloadCriticalData) {
                await window.hearthlink.reloadCriticalData();
            }
        } catch (e) {
            console.warn('Failed to reload critical data:', e);
        }
    }

    /**
     * Clear component-specific caches
     */
    clearComponentCaches(componentName) {
        try {
            // Clear component-specific caches
            if (componentName && window.componentCaches) {
                delete window.componentCaches[componentName];
            }
        } catch (e) {
            console.warn('Failed to clear component caches:', e);
        }
    }

    /**
     * Clear non-essential caches
     */
    clearNonEssentialCaches() {
        try {
            // Clear various caches to free memory
            if (window.caches) {
                window.caches.keys().then(names => {
                    names.forEach(name => {
                        if (!name.includes('essential')) {
                            window.caches.delete(name);
                        }
                    });
                });
            }
        } catch (e) {
            console.warn('Failed to clear caches:', e);
        }
    }

    /**
     * Reduce memory-intensive operations
     */
    reduceMemoryOperations() {
        try {
            // Signal to reduce memory usage
            if (window.hearthlink && window.hearthlink.reduceMemoryUsage) {
                window.hearthlink.reduceMemoryUsage();
            }
        } catch (e) {
            console.warn('Failed to reduce memory operations:', e);
        }
    }

    /**
     * Get recovery statistics
     */
    getRecoveryStats() {
        return {
            strategiesRegistered: this.recoveryStrategies.size,
            activeAttempts: this.recoveryAttempts.size,
            isRecovering: this.isRecovering,
            maxAttempts: this.maxRecoveryAttempts
        };
    }

    /**
     * Reset recovery state
     */
    resetRecoveryState() {
        this.recoveryAttempts.clear();
        this.isRecovering = false;
    }
}

// Export singleton instance
export const errorRecoveryService = new ErrorRecoveryService();

// Export class for custom instances
export default ErrorRecoveryService;
