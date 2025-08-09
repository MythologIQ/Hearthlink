import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { 
            hasError: false, 
            error: null, 
            errorInfo: null,
            errorId: null 
        };
    }

    static getDerivedStateFromError(error) {
        // Update state so the next render will show the fallback UI
        return { 
            hasError: true,
            errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
    }

    componentDidCatch(error, errorInfo) {
        // Log error details
        this.setState({
            error: error,
            errorInfo: errorInfo
        });

        // Enhanced error reporting
        this.reportError(error, errorInfo);
    }

    reportError = (error, errorInfo) => {
        const errorReport = {
            errorId: this.state.errorId,
            message: error.message,
            stack: error.stack,
            componentStack: errorInfo.componentStack,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            props: Object.keys(this.props).reduce((acc, key) => {
                if (key !== 'children') {
                    acc[key] = this.props[key];
                }
                return acc;
            }, {})
        };

        // Log to console in development
        if (process.env.NODE_ENV === 'development') {
            console.error('Error Boundary caught an error:', errorReport);
        }

        // Send to error tracking service (implement as needed)
        this.sendErrorReport(errorReport);
    }

    sendErrorReport = async (errorReport) => {
        try {
            // Example: Send to logging service
            // await fetch('/api/errors', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(errorReport)
            // });
            
            // For now, store in localStorage for debugging
            const existingErrors = JSON.parse(localStorage.getItem('errorBoundaryLogs') || '[]');
            existingErrors.push(errorReport);
            
            // Keep only last 10 errors
            const recentErrors = existingErrors.slice(-10);
            localStorage.setItem('errorBoundaryLogs', JSON.stringify(recentErrors));
        } catch (e) {
            console.error('Failed to send error report:', e);
        }
    }

    handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
            errorId: null
        });
    }

    handleReload = () => {
        window.location.reload();
    }

    render() {
        if (this.state.hasError) {
            const { error, errorInfo, errorId } = this.state;
            const { fallback: FallbackComponent } = this.props;

            // Use custom fallback if provided
            if (FallbackComponent) {
                return (
                    <FallbackComponent 
                        error={error}
                        errorInfo={errorInfo}
                        onReset={this.handleReset}
                        onReload={this.handleReload}
                    />
                );
            }

            // Default error UI
            return (
                <div className="error-boundary">
                    <div className="error-boundary-content">
                        <h1>🚨 Something went wrong</h1>
                        <p>We're sorry, but something unexpected happened.</p>
                        
                        <div className="error-actions">
                            <button 
                                className="btn btn-primary" 
                                onClick={this.handleReset}
                            >
                                Try Again
                            </button>
                            <button 
                                className="btn btn-secondary" 
                                onClick={this.handleReload}
                            >
                                Reload Page
                            </button>
                        </div>

                        {process.env.NODE_ENV === 'development' && (
                            <details className="error-details">
                                <summary>Error Details (Development Only)</summary>
                                <div className="error-info">
                                    <p><strong>Error ID:</strong> {errorId}</p>
                                    <p><strong>Message:</strong> {error?.message}</p>
                                    <pre className="error-stack">
                                        {error?.stack}
                                    </pre>
                                    <pre className="error-component-stack">
                                        {errorInfo?.componentStack}
                                    </pre>
                                </div>
                            </details>
                        )}
                    </div>

                    <style jsx>{`
                        .error-boundary {
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                        }

                        .error-boundary-content {
                            background: white;
                            padding: 2rem;
                            border-radius: 12px;
                            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                            max-width: 600px;
                            text-align: center;
                        }

                        .error-actions {
                            margin: 1.5rem 0;
                            display: flex;
                            gap: 1rem;
                            justify-content: center;
                        }

                        .btn {
                            padding: 0.75rem 1.5rem;
                            border: none;
                            border-radius: 6px;
                            font-weight: 500;
                            cursor: pointer;
                            transition: all 0.2s;
                        }

                        .btn-primary {
                            background: #007bff;
                            color: white;
                        }

                        .btn-secondary {
                            background: #6c757d;
                            color: white;
                        }

                        .btn:hover {
                            transform: translateY(-1px);
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        }

                        .error-details {
                            margin-top: 1.5rem;
                            text-align: left;
                        }

                        .error-info {
                            margin-top: 1rem;
                        }

                        .error-stack, .error-component-stack {
                            background: #f8f9fa;
                            padding: 1rem;
                            border-radius: 4px;
                            font-size: 0.875rem;
                            overflow-x: auto;
                            margin: 0.5rem 0;
                        }
                    `}</style>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
