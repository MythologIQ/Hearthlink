import React from 'react';

class SystemFunctionsBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { 
            hasError: false, 
            error: null,
            lastFailedAction: null,
            retryCount: 0
        };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({
            error: error,
            lastFailedAction: this.props.lastAction || 'unknown'
        });

        // Log system function errors specifically
        console.error('System Functions Error:', {
            error: error.message,
            action: this.props.lastAction,
            stack: error.stack,
            timestamp: new Date().toISOString()
        });
    }

    handleRetry = () => {
        const newRetryCount = this.state.retryCount + 1;
        
        this.setState({
            hasError: false,
            error: null,
            retryCount: newRetryCount
        });

        // Call retry callback if provided
        if (this.props.onRetry) {
            this.props.onRetry(this.state.lastFailedAction, newRetryCount);
        }
    }

    handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            lastFailedAction: null,
            retryCount: 0
        });

        if (this.props.onReset) {
            this.props.onReset();
        }
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="system-functions-error">
                    <div className="error-content">
                        <h3>🔧 System Function Error</h3>
                        <p>A system function encountered an error and needs attention.</p>
                        
                        {this.state.lastFailedAction && (
                            <div className="error-context">
                                <strong>Failed Action:</strong> {this.state.lastFailedAction}
                            </div>
                        )}

                        <div className="error-actions">
                            <button 
                                className="btn btn-primary"
                                onClick={this.handleRetry}
                                disabled={this.state.retryCount >= 3}
                            >
                                {this.state.retryCount >= 3 ? 'Max Retries Reached' : `Retry (${this.state.retryCount}/3)`}
                            </button>
                            <button 
                                className="btn btn-secondary"
                                onClick={this.handleReset}
                            >
                                Reset Functions
                            </button>
                        </div>

                        {process.env.NODE_ENV === 'development' && (
                            <details className="error-details">
                                <summary>Technical Details</summary>
                                <pre>{this.state.error?.message}\n{this.state.error?.stack}</pre>
                            </details>
                        )}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default SystemFunctionsBoundary;
