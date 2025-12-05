# Data Collector Module

A comprehensive, interface-based data collection, processing, and storage framework for Python applications.

## Overview

The Data Collector Module provides a set of well-defined interfaces for building robust data pipelines. It follows the dependency inversion principle, allowing you to implement custom data sources, processors, and storage backends while maintaining a consistent architecture.

## Features

- **Three-Layer Architecture**: Separation of concerns between collection, processing, and storage
- **Async/Await Support**: Built for high-performance asynchronous operations
- **Interface-Based Design**: Easy to extend and test with dependency injection
- **Event System**: Built-in event emitter for monitoring and notifications
- **Error Handling**: Structured error handling with categorization and context
- **Task Tracking**: Track asynchronous operations with progress updates
- **Mock Implementations**: Complete set of mocks for testing

## Quick Start

```python
import asyncio
from collectors.mocks import MockDataSource, MockProcessor, MockStorageBackend

async def main():
    # Create components
    source = MockDataSource(source_id="sensor_001", data=b"temperature:25.5")
    processor = MockProcessor(name="normalizer")
    storage = MockStorageBackend(backend_id="main_db")
    
    # Connect
    await source.connect()
    await storage.connect()
    
    # Collect data
    data = await source.collect()
    print(f"Collected: {data.raw_data.decode()}")
    
    # Process data
    result = await processor.process({"raw": data.raw_data.decode()})
    print(f"Processed: {result.processed_data}")
    
    # Store data
    location = await storage.store(result.processed_data)
    print(f"Stored at: {location.path}")
    
    # Cleanup
    await source.disconnect()
    await storage.disconnect()

asyncio.run(main())
```

## Architecture

```
┌─────────────────────────────────────────┐
│       Data Collection Layer             │
│  - IDataSource                          │
│  - IMetadataParser                      │
│  - ICollectionManager                   │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│       Data Processing Layer             │
│  - IProcessor                           │
│  - IPipeline                            │
│  - IProcessingManager                   │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│       Data Storage Layer                │
│  - IStorageBackend                      │
│  - IStorageManager                      │
└─────────────────────────────────────────┘
```

## Core Interfaces

### Data Collection Layer

- **IDataSource**: Interface for data sources (sensors, APIs, databases)
- **IMetadataParser**: Interface for parsing and validating metadata
- **ICollectionManager**: Interface for managing data sources and collection tasks

### Data Processing Layer

- **IProcessor**: Interface for data processors (validation, transformation, enrichment)
- **IPipeline**: Interface for processing pipelines (sequential processor execution)
- **IProcessingManager**: Interface for managing processors and pipelines

### Data Storage Layer

- **IStorageBackend**: Interface for storage backends (databases, file systems, cloud storage)
- **IStorageManager**: Interface for managing storage backends and operations

### Cross-Cutting Interfaces

- **IErrorHandler**: Interface for error handling
- **IEventEmitter**: Interface for event-driven architecture
- **ITaskTracker**: Interface for tracking asynchronous operations

## Documentation

- **[API Documentation](API_DOCUMENTATION.md)**: Complete API reference with examples
- **[Integration Guide](INTEGRATION_GUIDE.md)**: Step-by-step integration instructions
- **[Usage Examples](examples.py)**: Runnable code examples
- **[Design Document](../../../.kiro/specs/data-collector-interfaces/design.md)**: Architecture and design decisions
- **[Requirements](../../../.kiro/specs/data-collector-interfaces/requirements.md)**: Functional requirements

## Installation

The module is part of the backend package:

```bash
cd backend
pip install -e .
```

## Usage Examples

### Example 1: Basic Data Collection

```python
from collectors.mocks import MockDataSource

async def collect_data():
    source = MockDataSource(source_id="sensor_001", data=b"data")
    await source.connect()
    
    data = await source.collect()
    print(f"Source: {data.source_id}")
    print(f"Data: {data.raw_data}")
    print(f"Timestamp: {data.timestamp}")
    
    await source.disconnect()
```

### Example 2: Processing Pipeline

```python
from collectors.mocks import MockProcessor

async def process_data():
    validator = MockProcessor(name="validator")
    transformer = MockProcessor(name="transformer")
    
    input_data = {"value": 42}
    
    # Step 1: Validate
    result1 = await validator.process(input_data)
    
    # Step 2: Transform
    if result1.success:
        result2 = await transformer.process(result1.processed_data)
        print(f"Final: {result2.processed_data}")
```

### Example 3: Complete Pipeline

```python
from collectors.mocks import (
    MockDataSource,
    MockProcessor,
    MockStorageBackend,
)

async def complete_pipeline():
    # Setup
    source = MockDataSource(source_id="sensor", data=b"temp:25.5")
    processor = MockProcessor(name="normalizer")
    storage = MockStorageBackend(backend_id="db")
    
    await source.connect()
    await storage.connect()
    
    try:
        # Collect
        data = await source.collect()
        
        # Process
        result = await processor.process({
            "raw": data.raw_data.decode(),
            "timestamp": data.timestamp.isoformat()
        })
        
        # Store
        if result.success:
            location = await storage.store(result.processed_data)
            print(f"Success! Stored at: {location.path}")
    finally:
        await source.disconnect()
        await storage.disconnect()
```

### Example 4: Event Monitoring

```python
from collectors.mocks import MockEventEmitter
from collectors.enums import EventType
from collectors.models import SystemEvent
from datetime import datetime

async def monitor_events():
    emitter = MockEventEmitter()
    
    # Subscribe to events
    async def on_event(event: SystemEvent):
        print(f"Event: {event.event_type.value}")
    
    sub_id = await emitter.subscribe(
        EventType.COLLECTION_COMPLETE,
        on_event
    )
    
    # Emit event
    await emitter.emit(SystemEvent(
        event_type=EventType.COLLECTION_COMPLETE,
        timestamp=datetime.now(),
        source="collector",
        data={"items": 100}
    ))
    
    await emitter.unsubscribe(sub_id)
```

### Example 5: Error Handling

```python
from collectors.mocks import MockErrorHandler
from collectors.models import ErrorInfo
from collectors.enums import ErrorType
from datetime import datetime

async def handle_errors():
    handler = MockErrorHandler()
    
    error = ErrorInfo(
        error_type=ErrorType.VALIDATION,
        timestamp=datetime.now(),
        layer_name="processing",
        operation="validate",
        message="Invalid data format",
        details={"expected": "dict", "got": "str"},
        is_critical=False
    )
    
    if handler.can_handle(error.error_type):
        await handler.handle_error(error)
        print("Error handled successfully")
```

## Running Examples

Run all examples:

```bash
cd backend
python -m collectors.examples
```

Run specific example:

```python
import asyncio
from collectors.examples import example_basic_collection

asyncio.run(example_basic_collection())
```

## Testing

The module includes comprehensive mock implementations for testing:

```python
from collectors.mocks import (
    MockDataSource,
    MockMetadataParser,
    MockProcessor,
    MockStorageBackend,
    MockErrorHandler,
    MockEventEmitter,
    MockTaskTracker,
)
```

Run tests:

```bash
cd backend
pytest tests/test_mocks.py
```

## Implementing Custom Components

### Custom Data Source

```python
from collectors.interfaces import IDataSource
from collectors.models import CollectedData
from datetime import datetime

class MyDataSource(IDataSource):
    async def connect(self) -> None:
        # Connect to your data source
        pass
    
    async def disconnect(self) -> None:
        # Disconnect from your data source
        pass
    
    async def collect(self) -> CollectedData:
        # Collect data
        return CollectedData(
            source_id=self.get_source_id(),
            timestamp=datetime.now(),
            data_format="custom",
            collection_method="custom_method",
            raw_data=b"your_data",
            metadata={}
        )
    
    async def collect_stream(self):
        # Stream data
        while True:
            yield await self.collect()
    
    def get_source_id(self) -> str:
        return "my_source"
```

### Custom Processor

```python
from collectors.interfaces import IProcessor
from collectors.models import ProcessingResult
from datetime import datetime

class MyProcessor(IProcessor):
    async def process(self, data) -> ProcessingResult:
        start = datetime.now()
        
        try:
            # Process your data
            processed = {"processed": True, "data": data}
            
            return ProcessingResult(
                success=True,
                processed_data=processed,
                error=None,
                processing_time=(datetime.now() - start).total_seconds()
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                processed_data=None,
                error=str(e),
                processing_time=(datetime.now() - start).total_seconds()
            )
    
    def get_processor_name(self) -> str:
        return "my_processor"
    
    def validate_input(self, data) -> bool:
        return data is not None
```

### Custom Storage Backend

```python
from collectors.interfaces import IStorageBackend
from collectors.models import StorageLocation, QueryCriteria
from datetime import datetime
import uuid

class MyStorageBackend(IStorageBackend):
    async def connect(self) -> None:
        # Connect to storage
        pass
    
    async def disconnect(self) -> None:
        # Disconnect from storage
        pass
    
    async def store(self, data) -> StorageLocation:
        # Store data
        location_id = str(uuid.uuid4())
        
        return StorageLocation(
            backend_id=self.get_backend_id(),
            location_id=location_id,
            path=f"/storage/{location_id}",
            created_at=datetime.now()
        )
    
    async def query(self, criteria: QueryCriteria):
        # Query data
        return []
    
    async def delete(self, location_id: str) -> None:
        # Delete data
        pass
    
    def get_backend_id(self) -> str:
        return "my_storage"
```

## Data Models

The module provides comprehensive data models:

- **CollectedData**: Raw data with metadata
- **ParsedMetadata**: Parsed and validated metadata
- **ProcessingResult**: Result of processing operation
- **StorageLocation**: Location of stored data
- **ErrorInfo**: Structured error information
- **SystemEvent**: System event for monitoring
- **TaskInfo**: Asynchronous task information

See [API Documentation](API_DOCUMENTATION.md) for complete model definitions.

## Enumerations

- **CollectionStatus**: IDLE, RUNNING, PAUSED, STOPPED, ERROR
- **TaskStatus**: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
- **EventType**: COLLECTION_START, COLLECTION_COMPLETE, PROCESSING_START, etc.
- **ErrorType**: CONFIGURATION, CONNECTION, VALIDATION, PROCESSING, STORAGE

## Best Practices

1. **Always use async/await** for I/O operations
2. **Always disconnect** from sources and backends in finally blocks
3. **Validate configurations** before registering components
4. **Use events** for monitoring and notifications
5. **Handle errors gracefully** with structured error information
6. **Add logging** for production deployments
7. **Write tests** using mock implementations

## Contributing

When implementing new components:

1. Implement the appropriate interface
2. Add comprehensive docstrings
3. Include type hints
4. Write unit tests
5. Update documentation

## License

See the main project LICENSE file.

## Support

- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Integration Guide**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Examples**: [examples.py](examples.py)
- **Design Document**: [design.md](../../../.kiro/specs/data-collector-interfaces/design.md)

## Version

Version 1.0.0 - Initial release

## Authors

Data Collector Module Development Team
