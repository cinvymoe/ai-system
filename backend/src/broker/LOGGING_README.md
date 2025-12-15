# Message Broker Logging Configuration

## Overview

The message broker includes comprehensive logging functionality that supports:
- Configurable log levels
- Structured logging (JSON format)
- File and console output
- Context-aware logging
- High-performance logging for high-frequency messages

## Requirements Implemented

- **Requirement 8.1**: Message publishing logs
- **Requirement 8.2**: Subscription registration logs
- **Requirement 8.3**: Error logs
- **Requirement 8.4**: Configurable log levels
- **Requirement 8.5**: Efficient logging for high-frequency messages

## Configuration

### Basic Configuration

```python
from broker import configure_broker_logging

# Configure with default settings (INFO level, console output)
configure_broker_logging(log_level="INFO")
```

### Advanced Configuration

```python
# Configure with structured logging (JSON format) and file output
configure_broker_logging(
    log_level="DEBUG",
    use_structured=True,
    log_file="/var/log/broker.log"
)
```

### Environment Variables

The logging system respects the `LOG_LEVEL` environment variable from `config.py`:

```bash
export LOG_LEVEL=DEBUG
```

## Log Levels

Supported log levels (from most to least verbose):
- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## Log Formats

### Simple Format (Human-Readable)

```
2024-12-09 10:08:18 - src.broker.broker - INFO - Published message abc123 of type direction_result
```

### Structured Format (JSON)

```json
{
  "timestamp": "2024-12-09T10:08:18.123456",
  "level": "INFO",
  "logger": "src.broker.broker",
  "message": "Published message abc123 of type direction_result",
  "module": "broker",
  "function": "publish",
  "line": 186,
  "message_id": "abc123",
  "message_type": "direction_result"
}
```

## Context Loggers

### Message Context Logger

Automatically includes message ID and type in all log entries:

```python
from broker import create_message_logger

logger = create_message_logger(
    message_id="msg_12345",
    message_type="direction_result"
)
logger.info("Processing message")
# Output includes message_id and message_type in context
```

### Subscriber Context Logger

Automatically includes subscriber ID in all log entries:

```python
from broker import create_subscriber_logger

logger = create_subscriber_logger(subscriber_id="sub_67890")
logger.info("Subscriber callback executed")
# Output includes subscriber_id in context
```

## Usage Examples

### In Application Startup

```python
from broker import configure_broker_logging
from config import settings

# Configure logging during application startup
configure_broker_logging(
    log_level=settings.LOG_LEVEL,
    use_structured=False,
    log_file=None
)
```

### In Custom Modules

```python
from broker import get_broker_logger

logger = get_broker_logger("my_module")
logger.info("Custom module initialized")
```

## Logged Events

### Message Publishing

- Message validation (success/failure)
- Message processing time
- Number of subscribers notified
- Validation errors

### Subscription Management

- Subscriber registration
- Subscriber unregistration
- Subscriber count per message type

### Error Handling

- Validation errors with details
- Database errors with retry attempts
- Subscriber callback failures (isolated)
- Exception stack traces

## Performance

The logging system is optimized for high-frequency message processing:
- Average logging overhead: < 1ms per message
- Tested with 100+ messages/second
- Non-blocking for subscriber callbacks
- Efficient structured logging

## File Rotation

When using file logging, logs are automatically rotated:
- Maximum file size: 10MB
- Backup count: 5 files
- Encoding: UTF-8

## Testing

Run the logging tests:

```bash
cd backend
python test_broker_logging.py
```

## Integration

The logging configuration is automatically initialized in `main.py` during application startup:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure broker logging
    configure_broker_logging(
        log_level=settings.LOG_LEVEL,
        use_structured=False,
        log_file=None
    )
    # ... rest of startup
```

## Troubleshooting

### No Logs Appearing

1. Check log level configuration
2. Verify logger name starts with `src.broker` or `broker`
3. Ensure logging is configured before creating broker instance

### Too Many Logs

1. Increase log level to `WARNING` or `ERROR`
2. Disable DEBUG logging in production

### Performance Issues

1. Use simple format instead of structured format
2. Increase log level to reduce log volume
3. Ensure file logging uses SSD storage
