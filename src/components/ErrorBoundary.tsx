/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree and displays fallback UI
 * Requirements: Error handling scenarios for component failures
 */

import React, { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  resetOnPropsChange?: boolean;
  resetKeys?: Array<string | number>;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
  errorId: string;
}

/**
 * Generic Error Boundary for catching component errors
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  private resetTimeoutId: number | null = null;

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorId: `error-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log the error
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });

    // Call the onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps) {
    const { resetOnPropsChange, resetKeys } = this.props;
    const { hasError } = this.state;

    // Reset error state if resetKeys have changed
    if (hasError && resetOnPropsChange && resetKeys) {
      const prevResetKeys = prevProps.resetKeys || [];
      const hasResetKeyChanged = resetKeys.some((key, index) => {
        const prevKey = prevResetKeys[index];
        return key !== prevKey;
      });
      
      if (hasResetKeyChanged) {
        this.resetErrorBoundary();
      }
    }
  }

  componentWillUnmount() {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }
  }

  resetErrorBoundary = () => {
    if (this.resetTimeoutId) {
      clearTimeout(this.resetTimeoutId);
    }

    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    });
  };

  handleRetry = () => {
    this.resetErrorBoundary();
  };

  handleAutoRetry = () => {
    // Auto-retry after 3 seconds
    this.resetTimeoutId = window.setTimeout(() => {
      this.resetErrorBoundary();
    }, 3000);
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6 text-center">
          <AlertTriangle className="size-12 mx-auto mb-4 text-red-500" />
          <h3 className="text-red-400 text-lg font-semibold mb-2">Something went wrong</h3>
          <p className="text-red-300 text-sm mb-4">
            An unexpected error occurred in this component.
          </p>
          
          {/* Error details in development */}
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details className="text-left bg-red-950/50 rounded p-3 mb-4 text-xs">
              <summary className="cursor-pointer text-red-400 font-medium mb-2">
                Error Details (Development)
              </summary>
              <div className="text-red-300 font-mono whitespace-pre-wrap">
                <strong>Error:</strong> {this.state.error.message}
                {this.state.error.stack && (
                  <>
                    <br />
                    <strong>Stack:</strong>
                    <br />
                    {this.state.error.stack}
                  </>
                )}
                {this.state.errorInfo && (
                  <>
                    <br />
                    <strong>Component Stack:</strong>
                    <br />
                    {this.state.errorInfo.componentStack}
                  </>
                )}
              </div>
            </details>
          )}

          <div className="flex gap-2 justify-center">
            <button
              onClick={this.handleRetry}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              <RefreshCw className="size-4" />
              Try Again
            </button>
            <button
              onClick={this.handleAutoRetry}
              className="px-4 py-2 bg-red-600/50 hover:bg-red-600/70 text-red-200 rounded-lg transition-colors"
            >
              Auto-retry in 3s
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * Zone-specific Error Boundary with specialized error handling
 */
interface ZoneErrorBoundaryProps {
  children: ReactNode;
  onZoneError?: (error: Error) => void;
  cameraId?: string;
}

export function ZoneErrorBoundary({ children, onZoneError, cameraId }: ZoneErrorBoundaryProps) {
  const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
    // Log zone-specific error
    console.error('Zone management error:', {
      error: error.message,
      cameraId,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString()
    });

    // Call zone error handler
    if (onZoneError) {
      onZoneError(error);
    }
  };

  const fallbackUI = (
    <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-6 text-center">
      <AlertTriangle className="size-10 mx-auto mb-3 text-orange-500" />
      <h4 className="text-orange-400 text-base font-medium mb-2">Zone Management Error</h4>
      <p className="text-orange-300 text-sm mb-4">
        There was an error with the zone management system. 
        {cameraId && ` Camera: ${cameraId}`}
      </p>
      <p className="text-orange-400 text-xs">
        Please try refreshing the page or contact support if the problem persists.
      </p>
    </div>
  );

  return (
    <ErrorBoundary
      fallback={fallbackUI}
      onError={handleError}
      resetOnPropsChange={true}
      resetKeys={cameraId ? [cameraId] : []}
    >
      {children}
    </ErrorBoundary>
  );
}

/**
 * Canvas-specific Error Boundary for drawing operations
 */
interface CanvasErrorBoundaryProps {
  children: ReactNode;
  onCanvasError?: (error: Error) => void;
}

export function CanvasErrorBoundary({ children, onCanvasError }: CanvasErrorBoundaryProps) {
  const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
    // Log canvas-specific error
    console.error('Canvas drawing error:', {
      error: error.message,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString()
    });

    if (onCanvasError) {
      onCanvasError(error);
    }
  };

  const fallbackUI = (
    <div className="bg-slate-800 border border-slate-600 rounded-lg p-8 text-center">
      <AlertTriangle className="size-8 mx-auto mb-3 text-yellow-500" />
      <h4 className="text-slate-200 text-base font-medium mb-2">Drawing Canvas Error</h4>
      <p className="text-slate-400 text-sm">
        The zone drawing canvas encountered an error and cannot be displayed.
      </p>
    </div>
  );

  return (
    <ErrorBoundary
      fallback={fallbackUI}
      onError={handleError}
    >
      {children}
    </ErrorBoundary>
  );
}

/**
 * Hook for using error boundary functionality in functional components
 */
export function useErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  const handleError = React.useCallback((error: Error) => {
    setError(error);
  }, []);

  // Throw error to be caught by error boundary
  if (error) {
    throw error;
  }

  return { handleError, resetError };
}