/**
 * Async Error Handler Utility
 * Provides consistent error handling for async operations
 */

class AsyncErrorHandler {
    constructor(options = {}) {
        this.retryAttempts = options.retryAttempts || 3;
        this.retryDelay = options.retryDelay || 1000;
        this.onError = options.onError || this.defaultErrorHandler;
        this.onRetry = options.onRetry || this.defaultRetryHandler;
    }

    /**
     * Wrap async function with error handling and retry logic
     */
    async executeWithRetry(asyncFn, context = {}) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const result = await asyncFn();
                
                // Log successful retry if it wasn't the first attempt
                if (attempt > 1) {
                    console.info(`✅ Async operation succeeded on attempt ${attempt}`, {
                        context,
                        attempt,
                        timestamp: new Date().toISOString()
                    });
                }
                
                return result;
                
            } catch (error) {
                lastError = error;
                
                const errorInfo = {
                    error: error.message,
                    attempt,
                    maxAttempts: this.retryAttempts,
                    context,
                    timestamp: new Date().toISOString()
                };

                // Log the error
                console.error(`❌ Async operation failed (attempt ${attempt}/${this.retryAttempts})`, errorInfo);
                
                // Call error handler
                this.onError(error, errorInfo);
                
                // Don't retry on final attempt
                if (attempt === this.retryAttempts) {
                    break;
                }
                
                // Call retry handler
                this.onRetry(error, errorInfo);
                
                // Wait before retry with exponential backoff
                const delay = this.retryDelay * Math.pow(2, attempt - 1);
                await this.delay(delay);
            }
        }
        
        // All retries failed
        const finalError = new Error(`Async operation failed after ${this.retryAttempts} attempts: ${lastError.message}`);
        finalError.originalError = lastError;
        finalError.context = context;
        
        throw finalError;
    }

    /**
     * Wrap async function with timeout
     */
    async executeWithTimeout(asyncFn, timeoutMs = 10000, context = {}) {
        return new Promise(async (resolve, reject) => {
            const timeoutId = setTimeout(() => {
                const timeoutError = new Error(`Async operation timed out after ${timeoutMs}ms`);
                timeoutError.context = context;
                reject(timeoutError);
            }, timeoutMs);

            try {
                const result = await asyncFn();
                clearTimeout(timeoutId);
                resolve(result);
            } catch (error) {
                clearTimeout(timeoutId);
                reject(error);
            }
        });
    }

    /**
     * Execute async function with both retry and timeout
     */
    async executeWithGuards(asyncFn, options = {}) {
        const { timeout = 10000, context = {} } = options;
        
        return this.executeWithRetry(
            () => this.executeWithTimeout(asyncFn, timeout, context),
            context
        );
    }

    /**
     * Batch execute multiple async functions with error isolation
     */
    async executeBatch(asyncFunctions, options = {}) {
        const { failFast = false, context = {} } = options;
        const results = [];
        const errors = [];

        for (let i = 0; i < asyncFunctions.length; i++) {
            try {
                const result = await this.executeWithGuards(asyncFunctions[i], {
                    context: { ...context, batchIndex: i }
                });
                results.push({ index: i, success: true, result });
            } catch (error) {
                const errorInfo = { index: i, success: false, error };
                errors.push(errorInfo);
                results.push(errorInfo);

                if (failFast) {
                    throw new Error(`Batch execution failed at index ${i}: ${error.message}`);
                }
            }
        }

        return {
            results,
            errors,
            successCount: results.filter(r => r.success).length,
            errorCount: errors.length
        };
    }

    defaultErrorHandler(error, errorInfo) {
        // Store error in localStorage for debugging
        try {
            const errorLog = JSON.parse(localStorage.getItem('asyncErrors') || '[]');
            errorLog.push(errorInfo);
            localStorage.setItem('asyncErrors', JSON.stringify(errorLog.slice(-50))); // Keep last 50 errors
        } catch (e) {
            // Ignore localStorage errors
        }
    }

    defaultRetryHandler(error, errorInfo) {
        console.warn(`🔄 Retrying async operation...`, {
            nextAttempt: errorInfo.attempt + 1,
            error: error.message
        });
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Export singleton instance
export const asyncErrorHandler = new AsyncErrorHandler();

// Export class for custom instances
export default AsyncErrorHandler;

// Helper functions for common patterns
export const withRetry = (asyncFn, context) => {
    return asyncErrorHandler.executeWithRetry(asyncFn, context);
};

export const withTimeout = (asyncFn, timeout, context) => {
    return asyncErrorHandler.executeWithTimeout(asyncFn, timeout, context);
};

export const withGuards = (asyncFn, options) => {
    return asyncErrorHandler.executeWithGuards(asyncFn, options);
};

export const executeBatch = (asyncFunctions, options) => {
    return asyncErrorHandler.executeBatch(asyncFunctions, options);
};
