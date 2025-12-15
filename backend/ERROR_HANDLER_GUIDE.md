# Error Handler Implementation Guide

## Overview

The ErrorHandler class provides centralized error handling for the Message Broker system, implementing robust error recovery strategies for validation errors, database errors, and subscriber errors.

## Features

### 1. Validation Error Handling

Handles message validation failures by logging detailed error information without retrying.

**Requirements Addressed:**
- Requirements 2.4: Handle publishing failures gracefully
- Requirements 3.5: Handle invalid angle data and log errors
- Requirements 8.3: Record error logs

**Usage:**
```python
from broker import MessageBroker, ErrorHandler

broker = MessageBroker.get_instance()
error_handler = broker.get_error_handler()

# Validation errors are automatically handled during publish
result = broker.publish("direction_result", {
    "invalid": "data"  # Missing required fields
})

if not result.success:
    print(f"Validation failed: {result.errors}")
```

### 2. Database Error Handling with Retry

Implements exponential backoff retry strategy for database operations with caching fallback.

**Features:**
- Automatic retry with exponential backoff
- Configurable retry count and delay
- Cache mechanism for fallback
- Detailed logging of retry attempts

**Requirements Addressed:**
- Requirements 8.3: Record error logs
- Retry mechanism with exponential backoff
- Degraded mode with cached results

**Usage:**
```python
from broker.errors import ErrorHandler

error_handler = ErrorHandler()

def query_database():
    # Your database operation
    return db.query(Camera).all()

# Handle with automatic retry
result = error_handler.handle_database_error(
    operation=query_database,
    operation_name="get_all_cameras",
    error=Exception("Connection failed"),
    max_retries=3,
    initial_delay=0.1
)

if result is None:
    print("All retries failed, using fallback")
```

### 3. Subscriber Error Isolation

Ensures that errors in one subscriber callback don't affect other subscribers.

**Requirements Addressed:**
- Requirements 9.5: Subscriber error isolation
- Requirements 8.3: Record error logs

**Usage:**
```python
# Subscriber errors are automatically isolated
def my_callback(message):
    raise Exception("Oops!")  # Won't affect other subscribers

broker.subscribe("direction_result", my_callback)

# Other subscribers will still receive messages
result = broker.publish("direction_result", {"command": "forward"})
print(f"Notified {result.subscribers_notified} subscribers")
```

## Architecture

### ErrorHandler Class

```python
class ErrorHandler:
    """
    Centralized error handling for the Message Broker
    
    Attributes:
        _logger: Logger instance for error recording
        _cache: Simple cache for database query results
    """
    
    def handle_validation_error(message, error):
        """Log validation errors without retry"""
        
    def handle_database_error(operation, operation_name, error, max_retries=3):
        """Retry database operations with exponential backoff"""
        
    def handle_subscriber_error(subscriber_id, error, message_id=None):
        """Log subscriber errors without affecting others"""
```

### Integration Points

1. **MessageBroker**: Uses ErrorHandler for validation and subscriber errors
2. **CameraMapper**: Uses ErrorHandler for database query retries
3. **Handlers**: Validation errors are passed to ErrorHandler

## Error Recovery Strategies

### 1. Validation Errors
- **Strategy**: Reject immediately, no retry
- **Logging**: Detailed error with message ID and validation failures
- **Return**: PublishResult with success=False and error list

### 2. Database Errors
- **Strategy**: Retry with exponential backoff
- **Retry Count**: Default 3 attempts
- **Backoff**: initial_delay * (2 ^ attempt)
- **Fallback**: Return cached result or None
- **Logging**: Each retry attempt and final outcome

### 3. Subscriber Errors
- **Strategy**: Isolate and continue
- **Logging**: Error with subscriber ID and message ID
- **Impact**: Other subscribers still receive the message

## Testing

### Test Coverage

1. **Validation Error Handling**
   - Invalid direction messages
   - Invalid angle messages
   - Missing required fields

2. **Database Error Handling**
   - Flaky operations (succeed after retry)
   - Permanent failures (all retries fail)
   - Cache mechanism

3. **Subscriber Error Isolation**
   - Multiple subscribers with one failing
   - Verify all subscribers are called
   - Verify successful subscribers receive messages

### Running Tests

```bash
# Test ErrorHandler implementation
cd backend
python test_error_handler.py

# Test broker subscription (includes error isolation)
python test_broker_subscription.py
```

## Configuration

### Retry Configuration

```python
# Default configuration
max_retries = 3
initial_delay = 0.1  # seconds

# Custom configuration
result = error_handler.handle_database_error(
    operation=my_operation,
    operation_name="custom_query",
    error=e,
    max_retries=5,        # More retries
    initial_delay=0.2     # Longer initial delay
)
```

### Logging Configuration

The ErrorHandler uses structured logging with extra context:

```python
logger.error(
    "Validation failed for message {message_id}",
    extra={
        "message_id": message.message_id,
        "message_type": message.type,
        "errors": error.errors,
        "warnings": error.warnings
    }
)
```

## Cache Management

### Cache Behavior

- Successful database operations are automatically cached
- Cache key is the operation name
- Cache is used as fallback when all retries fail

### Cache Operations

```python
# Clear cache manually
error_handler.clear_cache()

# Cache is automatically populated on success
result = error_handler.handle_database_error(...)
# Result is now cached

# On failure, cached result is returned
result = error_handler.handle_database_error(...)
# Returns cached result if available
```

## Best Practices

### 1. Use Descriptive Operation Names

```python
# Good
error_handler.handle_database_error(
    operation=query_func,
    operation_name="get_cameras_by_direction(forward)",
    error=e
)

# Bad
error_handler.handle_database_error(
    operation=query_func,
    operation_name="query",
    error=e
)
```

### 2. Handle None Results

```python
result = error_handler.handle_database_error(...)

if result is None:
    # All retries failed and no cache available
    # Implement fallback logic
    return []
```

### 3. Don't Catch ErrorHandler Exceptions

The ErrorHandler logs errors but doesn't raise exceptions for:
- Validation errors (returns PublishResult)
- Database errors (returns None or cached result)
- Subscriber errors (logs and continues)

### 4. Monitor Logs

Watch for patterns in error logs:
- Frequent validation errors → Check data sources
- Frequent database retries → Check database health
- Frequent subscriber errors → Check subscriber implementations

## Examples

### Example 1: Custom Database Operation

```python
from broker.errors import ErrorHandler

error_handler = ErrorHandler()

def complex_query():
    # Your complex database operation
    db = get_session()
    try:
        result = db.query(Camera).join(AngleRange).filter(...).all()
        return result
    finally:
        db.close()

# Handle with retry
cameras = error_handler.handle_database_error(
    operation=complex_query,
    operation_name="complex_camera_query",
    error=Exception("Initial failure")
)

if cameras is None:
    cameras = []  # Fallback to empty list
```

### Example 2: Validation in Custom Handler

```python
from broker.handlers import MessageTypeHandler
from broker.models import ValidationResult

class CustomHandler(MessageTypeHandler):
    def validate(self, data):
        errors = []
        
        if 'required_field' not in data:
            errors.append("Missing required_field")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )
    
    # ErrorHandler will automatically handle validation failures
```

### Example 3: Subscriber with Error Handling

```python
def robust_subscriber(message):
    try:
        # Your processing logic
        process_message(message)
    except Exception as e:
        # Log locally if needed
        logger.warning(f"Processing failed: {e}")
        # Re-raise to let ErrorHandler log it
        raise

# ErrorHandler will isolate this subscriber's errors
broker.subscribe("direction_result", robust_subscriber)
```

## Troubleshooting

### Issue: Too Many Retries

**Symptom**: Database operations taking too long

**Solution**: Reduce max_retries or increase initial_delay
```python
result = error_handler.handle_database_error(
    operation=query,
    operation_name="query",
    error=e,
    max_retries=2,  # Fewer retries
    initial_delay=0.05  # Shorter delay
)
```

### Issue: Cache Growing Too Large

**Symptom**: Memory usage increasing

**Solution**: Periodically clear cache
```python
# Clear cache after processing batch
error_handler.clear_cache()
```

### Issue: Validation Errors Not Logged

**Symptom**: Missing validation error logs

**Solution**: Check logger configuration
```python
import logging
logging.basicConfig(level=logging.ERROR)
```

## Related Documentation

- [Broker Implementation Summary](BROKER_IMPLEMENTATION_SUMMARY.md)
- [Subscription Notification Guide](SUBSCRIPTION_NOTIFICATION_GUIDE.md)
- [Handler Verification](HANDLER_VERIFICATION.md)

## Requirements Traceability

| Requirement | Implementation | Test Coverage |
|-------------|----------------|---------------|
| 2.4 | handle_validation_error | test_validation_error_handling |
| 3.5 | handle_validation_error | test_validation_error_handling |
| 8.3 | All error handlers | All tests |
| 9.5 | handle_subscriber_error | test_subscriber_error_handling |

## Summary

The ErrorHandler provides robust error handling with:
- ✅ Validation error logging
- ✅ Database retry with exponential backoff
- ✅ Subscriber error isolation
- ✅ Cache-based fallback
- ✅ Structured logging
- ✅ Thread-safe operations
