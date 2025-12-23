/**
 * Network Retry Utilities
 * Provides retry logic for network operations with exponential backoff
 */

export interface RetryOptions {
  maxAttempts?: number;
  baseDelay?: number;
  maxDelay?: number;
  backoffFactor?: number;
}

export interface RetryResult<T> {
  success: boolean;
  data?: T;
  error?: Error;
  attempts: number;
}

/**
 * Default retry options
 */
const DEFAULT_RETRY_OPTIONS: Required<RetryOptions> = {
  maxAttempts: 3,
  baseDelay: 1000, // 1 second
  maxDelay: 10000, // 10 seconds
  backoffFactor: 2
};

/**
 * Check if an error is retryable
 */
export function isRetryableError(error: Error): boolean {
  const message = error.message.toLowerCase();
  
  // Network errors that should be retried
  const retryablePatterns = [
    'network',
    'fetch',
    'timeout',
    'connection',
    'econnreset',
    'enotfound',
    'econnrefused',
    '500', // Server errors
    '502', // Bad Gateway
    '503', // Service Unavailable
    '504'  // Gateway Timeout
  ];
  
  return retryablePatterns.some(pattern => message.includes(pattern));
}

/**
 * Calculate delay for next retry attempt
 */
function calculateDelay(attempt: number, options: Required<RetryOptions>): number {
  const delay = options.baseDelay * Math.pow(options.backoffFactor, attempt - 1);
  return Math.min(delay, options.maxDelay);
}

/**
 * Sleep for specified milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Retry an async operation with exponential backoff
 */
export async function retryOperation<T>(
  operation: () => Promise<T>,
  options: RetryOptions = {}
): Promise<RetryResult<T>> {
  const opts = { ...DEFAULT_RETRY_OPTIONS, ...options };
  let lastError: Error | undefined;
  
  for (let attempt = 1; attempt <= opts.maxAttempts; attempt++) {
    try {
      const data = await operation();
      return {
        success: true,
        data,
        attempts: attempt
      };
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      // Don't retry if it's the last attempt or error is not retryable
      if (attempt === opts.maxAttempts || !isRetryableError(lastError)) {
        break;
      }
      
      // Wait before next attempt
      const delay = calculateDelay(attempt, opts);
      await sleep(delay);
    }
  }
  
  return {
    success: false,
    error: lastError || new Error('Operation failed'),
    attempts: opts.maxAttempts
  };
}

/**
 * Retry wrapper for zone save operations
 */
export async function retryZoneSave<T>(
  operation: () => Promise<T>,
  onRetry?: (attempt: number, error: Error) => void
): Promise<T> {
  const result = await retryOperation(operation, {
    maxAttempts: 3,
    baseDelay: 1000,
    maxDelay: 5000
  });
  
  if (!result.success) {
    // Call retry callback if provided
    if (onRetry && result.attempts > 1) {
      onRetry(result.attempts, result.error!);
    }
    throw result.error;
  }
  
  return result.data!;
}