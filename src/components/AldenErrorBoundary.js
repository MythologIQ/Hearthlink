import React from 'react';

class AldenErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { 
            hasError: false,
            error: null,
            errorCount: 0
        };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        const errorCount = this.state.errorCount + 1;
        
        this.setState({
            error: error,
            errorCount: errorCount
        });

        // Log module-specific error
        console.error('Alden Module Error:', {
            module: 'Alden',
            component: 'AldenMainScreen',
            error: error.message,
            count: errorCount,
            timestamp: new Date().toISOString()
        });

        // Auto-recovery after first error
        if (errorCount === 1) {
            setTimeout(() => {
                this.handleAutoRecover();
            }, 3000);
        }
    }

    handleAutoRecover = () => {
        if (this.state.errorCount === 1) {
            this.setState({
                hasError: false,
                error: null
            });
        }
    }

    handleManualReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorCount: 0
        });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="alden-error-boundary">
                    <div className="module-error-content">
                        <h3>⚠️ Alden Module Error</h3>
                        <p>The Alden module encountered an error.</p>
                        
                        {this.state.errorCount === 1 && (
                            <div className="auto-recovery-notice">
                                🔄 Attempting automatic recovery in 3 seconds...
                            </div>
                        )}

                        {this.state.errorCount > 1 && (
                            <div className="manual-recovery">
                                <p>Multiple errors detected. Manual intervention required.</p>
                                <button 
                                    className="btn btn-primary"
                                    onClick={this.handleManualReset}
                                >
                                    Reset Alden Module
                                </button>
                            </div>
                        )}

                        <div className="error-stats">
                            Error Count: {this.state.errorCount}
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default AldenErrorBoundary;
