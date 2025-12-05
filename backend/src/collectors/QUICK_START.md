# Data Collector Module - Quick Start Guide

Get started with the Data Collector Module in 5 minutes!

## Installation

```bash
cd backend
pip install -e .
```

## Your First Pipeline

Create a file `my_pipeline.py`:

```python
import asyncio
from collectors.mocks import MockDataSource, MockProcessor, MockStorageBackend

async def main():
    # 1. Create components
    source = MockDataSource(source_id="sensor_001", data=b"temperature:25.5")
    processor = MockProcessor(name="normalizer")
    storage = MockStorageBackend(backend_id="main_db")
    
    # 2. Connect to source and storage
    await source.connect()
    await storage.connect()
    
    try:
        # 3. Collect data
        data = await source.collect()
        print(f"✓ Collected: {data.raw_data.decode()}")
        
        # 4. Process data
        result = await processor.process({
            "raw": data.raw_data.decode(),
            "timestamp": data.timestamp.isoformat()
        })
        print(f"✓ Processed: {result.processed_data}")
        
        # 5. Store data
        location = await storage.store(result.processed_data)
        print(f"✓ Stored at: {location.path}")
        
    finally:
        # 6. Cleanup
        await source.disconnect()
        await storage.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python my_pipeline.py
```

Output:
```
✓ Collected: temperature:25.5
✓ Processed: {'raw': 'temperature:25.5', 'timestamp': '2025-12-04T10:30:00', 'processed_by_normalizer': True}
✓ Stored at: /mock/main_db/abc-123-def-456
```

## Run Built-in Examples

The module includes 8 complete examples:

```bash
cd backend
python -m collectors.examples
```

Or run a specific example:

```python
import asyncio
from collectors.examples import example_basic_collection

asyncio.run(example_basic_collection())
```

## Available Examples

1. **Basic Data Collection** - Simple data collection from a source
2. **Stream Data Collection** - Collecting streaming data
3. **Data Processing Pipeline** - Multi-step data processing
4. **Data Storage** - Storing and querying data
5. **Error Handling** - Handling errors with error handlers
6. **Event System** - Using events for monitoring
7. **Complete End-to-End Pipeline** - Full pipeline with all components
8. **Custom Data Source** - Implementing a custom data source

## Next Steps

### Learn More

- **[README](README.md)** - Module overview and features
- **[API Documentation](API_DOCUMENTATION.md)** - Complete API reference
- **[Integration Guide](INTEGRATION_GUIDE.md)** - Detailed integration instructions
- **[Examples](examples.py)** - All runnable examples

### Implement Your Own Components

1. **Custom Data Source** - Connect to your data source (API, sensor, database)
2. **Custom Processor** - Add your data transformation logic
3. **Custom Storage** - Store to your preferred backend

See the [Integration Guide](INTEGRATION_GUIDE.md) for step-by-step instructions.

### Test Your Implementation

Use the provided mock implementations for testing:

```python
from collectors.mocks import (
    MockDataSource,
    MockProcessor,
    MockStorageBackend,
    MockErrorHandler,
    MockEventEmitter,
)
```

## Common Patterns

### Pattern 1: Simple Collect-Store

```python
async def simple():
    source = MockDataSource(source_id="sensor", data=b"data")
    storage = MockStorageBackend(backend_id="db")
    
    await source.connect()
    await storage.connect()
    
    data = await source.collect()
    location = await storage.store({"data": data.raw_data.decode()})
    
    await source.disconnect()
    await storage.disconnect()
```

### Pattern 2: Collect-Process-Store

```python
async def with_processing():
    source = MockDataSource(source_id="sensor", data=b"data")
    processor = MockProcessor(name="validator")
    storage = MockStorageBackend(backend_id="db")
    
    await source.connect()
    await storage.connect()
    
    data = await source.collect()
    result = await processor.process({"raw": data.raw_data.decode()})
    
    if result.success:
        location = await storage.store(result.processed_data)
    
    await source.disconnect()
    await storage.disconnect()
```

### Pattern 3: With Error Handling

```python
from collectors.mocks import MockErrorHandler
from collectors.models import ErrorInfo
from collectors.enums import ErrorType
from datetime import datetime

async def with_errors():
    source = MockDataSource(source_id="sensor", data=b"data")
    storage = MockStorageBackend(backend_id="db")
    error_handler = MockErrorHandler()
    
    await source.connect()
    await storage.connect()
    
    try:
        data = await source.collect()
        location = await storage.store({"data": data.raw_data.decode()})
    except Exception as e:
        error = ErrorInfo(
            error_type=ErrorType.STORAGE,
            timestamp=datetime.now(),
            layer_name="storage",
            operation="store",
            message=str(e),
            details={},
            is_critical=True
        )
        await error_handler.handle_error(error)
    finally:
        await source.disconnect()
        await storage.disconnect()
```

### Pattern 4: With Event Monitoring

```python
from collectors.mocks import MockEventEmitter
from collectors.models import SystemEvent
from collectors.enums import EventType
from datetime import datetime

async def with_events():
    source = MockDataSource(source_id="sensor", data=b"data")
    storage = MockStorageBackend(backend_id="db")
    emitter = MockEventEmitter()
    
    # Subscribe to events
    async def on_event(event):
        print(f"Event: {event.event_type.value}")
    
    await emitter.subscribe(EventType.COLLECTION_COMPLETE, on_event)
    
    await source.connect()
    await storage.connect()
    
    data = await source.collect()
    await emitter.emit(SystemEvent(
        event_type=EventType.COLLECTION_COMPLETE,
        timestamp=datetime.now(),
        source="pipeline",
        data={"source_id": data.source_id}
    ))
    
    location = await storage.store({"data": data.raw_data.decode()})
    
    await source.disconnect()
    await storage.disconnect()
```

## Key Concepts

### Interfaces

The module provides interfaces for:
- **IDataSource** - Data collection
- **IProcessor** - Data processing
- **IStorageBackend** - Data storage
- **IErrorHandler** - Error handling
- **IEventEmitter** - Event system

### Data Models

Key data models:
- **CollectedData** - Raw data with metadata
- **ProcessingResult** - Processing output
- **StorageLocation** - Storage location info
- **ErrorInfo** - Error information
- **SystemEvent** - System events

### Async/Await

All I/O operations are asynchronous:

```python
# Always use await
await source.connect()
data = await source.collect()
await source.disconnect()
```

## Tips

1. **Always disconnect** - Use try/finally blocks
2. **Handle errors** - Use structured error handling
3. **Monitor with events** - Subscribe to system events
4. **Test with mocks** - Use provided mock implementations
5. **Add logging** - Use Python's logging module

## Getting Help

- Check [API Documentation](API_DOCUMENTATION.md) for detailed API reference
- Read [Integration Guide](INTEGRATION_GUIDE.md) for implementation details
- Review [examples.py](examples.py) for complete examples
- See design document at `.kiro/specs/data-collector-interfaces/design.md`

## What's Next?

1. Run the built-in examples
2. Implement your custom data source
3. Add your processing logic
4. Connect to your storage backend
5. Add monitoring and error handling
6. Deploy to production

Happy coding! 🚀
